#!/usr/bin/env python3
"""Read-only editorial candidate finder. Not an authorship detector or style verdict."""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import statistics
import sys

# Explicit families avoid substring stemming. 'distinction' is deliberately absent:
# academic-writing-editor B3 calls that match a false positive. This finite inventory
# covers common inflections/derivations; an editor must check unfamiliar derivatives.
LEXICAL_FAMILIES = {
    'claim': 'claim claims claimed claiming claimant claimants claimable unclaimed reclaim reclaims reclaimed reclaiming',
    'reveal': 'reveal reveals revealed revealing revealingly unrevealed revelation revelations revelatory',
    'appear': 'appear appears appeared appearing appearance appearances apparent apparently reappear reappears reappeared reappearing reappearance',
    'examine': 'examine examines examined examining examiner examiners examination examinations unexamined re-examine re-examines re-examined re-examining re-examination re-examinations reexamine reexamines reexamined reexamining reexamination reexaminations',
    'emerge': 'emerge emerges emerged emerging emergence emergences emergent emergently',
    'remain': 'remain remains remained remaining remainder remainders',
    'while': 'while whilst meanwhile awhile',
    'rather': 'rather',
    'durable': 'durable durability durably nondurable non-durable',
    'distinguish': 'distinguish distinguishes distinguished distinguishing distinguishable distinguishably indistinguishable indistinguishably',
    'identify': 'identify identifies identified identifying identification identifications identifiable identifiably unidentified unidentifiable misidentify misidentifies misidentified misidentifying misidentification re-identify re-identifies re-identified re-identifying re-identification reidentify reidentifies reidentified reidentifying reidentification',
    'distinct': 'distinct distinctly distinctness distinctive distinctively distinctiveness indistinct indistinctly indistinctness',
    'concern': 'concern concerns concerned concerning unconcern unconcerned unconcernedly',
    'asks': 'ask asks asked asking asker askers',
    'beyond': 'beyond',
    'quiet': 'quiet quiets quieted quieting quieter quietest quietly quietness disquiet disquiets disquieted disquieting disquietude',
    'establish': 'establish establishes established establishing establishment establishments re-establish re-establishes re-established re-establishing re-establishment reestablish reestablishes reestablished reestablishing reestablishment',
}
ALL_PURPOSE_FAMILIES = {
    'supply': 'supply supplies supplied supplying',
    'provide': 'provide provides provided providing provision provisions',
    'offer': 'offer offers offered offering offerings',
    'assess': 'assess assesses assessed assessing assessment assessments',
    'record': 'record records recorded recording recordings',
}
WORDS = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)?(?:[-‐‑][A-Za-z]+)*")
MANUAL_CHECKS = [
    'A3.1 gap formula', 'A3.2 numbered setups', 'A3.3 unsupported rankings',
    'A3.4 artificial missing-information openers', 'A3.5 throat-clearing',
    'A3.6 templated section openings', 'A10.1 defensive caveats',
    'A10.2 stamp sentences', 'A10.3 all-purpose verbs', 'A10.4 repeated openers',
    'A10.5 trailing contrasts', 'A10.6 stacked conditionals',
    'A10.7 either/not-just/glue openings', 'A10.8 numbered/caveat templates',
    'A10.9 parallel rhetorical templates', 'A10.10 polished one-liners',
    'A10.11 jargon replacing substance', 'A10.12 vague relations',
    'A10.13 stock academic phrases', 'A11 actor/object/antecedent clarity',
    'A12 meaning-preserving redundancy cuts and authorial rhythm',
    'P1 helpful optional clause markers',
    'P2 embedded clauses and distant related words',
    'P3 opaque noun strings',
    'P4 improvised noun-to-verb conversions',
    'P5 strained personification and subject-verb fit',
    'P6 unfamiliar compressed labels',
]


def mask_nonprose(text: str) -> str:
    """Mask fenced/inline code and leading YAML without changing offsets."""
    chars = list(text)
    fence = None
    yaml_end = None
    lines = text.splitlines(keepends=True)
    if lines and lines[0].strip() == '---':
        for i, line in enumerate(lines[1:], 1):
            if line.strip() in {'---', '...'}:
                yaml_end = i
                break
    offset = 0
    for index, line in enumerate(lines):
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        fenced_line = fence is not None or marker is not None
        if marker:
            symbol = marker.group(1)[0]
            width = len(marker.group(1))
            if fence is None:
                fence = (symbol, width)
            elif symbol == fence[0] and width >= fence[1]:
                fence = None
        if fenced_line or (yaml_end is not None and index <= yaml_end):
            for pos in range(offset, offset + len(line)):
                if chars[pos] != '\n':
                    chars[pos] = ' '
        offset += len(line)
    masked = ''.join(chars)
    for match in re.finditer(r'(`+)([^`\n]*?)\1', masked):
        for pos in range(match.start(), match.end()):
            chars[pos] = ' '
    return ''.join(chars)


def sentence_spans(prose: str) -> list[tuple[int, int, list[re.Match]]]:
    """Approximate boundaries, not a linguistic parser; preserve positions."""
    spans = []
    start = 0
    for match in re.finditer(r'[.!?]+["”\')]*\s+|\n\s*\n', prose):
        end = match.start() + len(match.group().rstrip())
        words = list(WORDS.finditer(prose, start, end))
        if words:
            spans.append((start, end, words))
        start = match.end()
    words = list(WORDS.finditer(prose, start))
    if words:
        spans.append((start, len(prose), words))
    return spans


def stats(prose: str) -> dict:
    lengths = [len(words) for _, _, words in sentence_spans(prose)]
    return {
        'sentence_count': len(lengths), 'word_count': len(list(WORDS.finditer(prose))),
        'lengths': lengths, 'mean': round(statistics.mean(lengths), 3) if lengths else 0,
        'population_sd': round(statistics.pstdev(lengths), 3) if lengths else 0,
        'minimum': min(lengths, default=0), 'maximum': max(lengths, default=0),
        'interpretation': 'Descriptive estimates only. No target, score, or pass/fail threshold.',
    }


def trigram_locations(prose: str) -> dict:
    result = defaultdict(list)
    for _, _, matches in sentence_spans(prose):
        for index in range(len(matches) - 2):
            group = matches[index:index + 3]
            key = ' '.join(m.group().casefold() for m in group)
            result[key].append((group[0].start(), group[-1].end()))
    return result


def analyze(text: str, baseline: str | None = None) -> dict:
    prose = mask_nonprose(text)
    findings = []

    def add(rule: str, start: int, end: int, message: str):
        line = text.count('\n', 0, start) + 1
        col = start - text.rfind('\n', 0, start)
        line_start = text.rfind('\n', 0, start) + 1
        line_end = text.find('\n', end)
        if line_end < 0:
            line_end = len(text)
        findings.append({'rule': rule, 'line': line, 'column': col,
                         'text': text[start:end], 'snippet': text[line_start:line_end],
                         'message': message, 'requires_context': True})

    lexical = {word: family for family, words in LEXICAL_FAMILIES.items() for word in words.split()}
    filler = {word: family for family, words in ALL_PURPOSE_FAMILIES.items() for word in words.split()}
    mere = []
    for match in WORDS.finditer(prose):
        token = match.group().casefold().replace('‐', '-').replace('‑', '-')
        token = re.sub(r"['’]s$", '', token)
        if token in lexical:
            add('A1.lexical.' + lexical[token], *match.span(), 'House-ban candidate; check quotation, cited title, proper-name, and adopted-text exemptions.')
        if token in filler:
            add('A10.3.all-purpose.' + filler[token], *match.span(), 'Check whether this verb names an action or serves as filler; nouns and precise uses may be valid.')
        if token in {'mere', 'merely', 'merest'}:
            mere.append(match)
    if len(mere) > 1:
        for match in mere:
            add('A1.habitual-merely', *match.span(), f'{len(mere)} mere/merely variants; review recurrence in context. An isolated instance is acceptable.')

    patterns = [
        ('A1.central-argument', r'\bthe\s+central\s+argument\s+of\b', 'State the argument directly.'),
        ('A1.rather-than', r'\brather\s+than\b', 'State the positive substance; preserve meaningful distinctions.'),
        ('A1.leaves-open', r'\b(?:leave[sd]?|left)\b[^.!?\n]{0,100}\b(?:open|unexplained|unanswered)\b', 'Check the forbidden leaves-open family; literal physical uses may be valid.'),
        ('A1.section-reference', r'\b(?:section\s+\d+(?:\.\d+)*|as\s+defined\s+in\s+the\s+\w+\s+section)\b', 'Replace running-prose section references with the substantive referent.'),
        ('A1.negative-contrast', r'\bnot\b[^.!?\n]{0,100}\bbut\b', 'Check formulaic not-X-but-Y contrast without deleting real negation.'),
        ('A10.1.defensive', r'\b(?:alone\s+does\s+not|cannot\s+stand\s+in\s+for|does\s+not\s+by\s+itself|cannot\s+be\s+(?:answered|determined))\b', 'State the evidence needed or what the source tells us; retain uncertainty.'),
        ('A10.5.trailing-contrast', r',\s+not\b[^.!?\n]*', 'Check whether the trailing contrast answers a real objection.'),
        ('A10.13.stock', r'\b(?:sheds?\s+light\s+on|speaks?\s+to|in\s+its\s+own\s+right)\b', 'Check whether the phrase carries content.'),
        ('A10.12.vague-relation', r'\b(?:pointed\s+in\s+different\s+directions|the\s+two)\b', 'Name the referents and their relationship when unclear.'),
        ('A1.passive-candidate', r'\b(?:am|is|are|was|were|be|been|being)\s+(?:(?:not|\w+ly)\s+)*(?:[A-Za-z]+ed|taken|given|shown|known|written|chosen|seen|made|built|brought|found|kept|told|read|sent|won|held|lost|paid)\b', 'Heuristic only; adjectives and other valid phrases can match. Name the actor in new text, never invent one.'),
    ]
    for rule, pattern, message in patterns:
        for match in re.finditer(pattern, prose, re.I):
            add(rule, *match.span(), message)

    for match in re.finditer('—', prose):
        add('A1.em-dash', *match.span(), 'House punctuation ban; rebuild the sentence.')
    url_spans = [m.span() for m in re.finditer(r'\b(?:[a-z][a-z0-9+.-]*://|mailto:)\S+', prose, re.I)]
    offset = 0
    references = False
    for line in prose.splitlines(keepends=True):
        heading = re.match(r'^\s{0,3}#{1,6}\s+', line)
        if heading:
            references = bool(re.search(r'\b(?:references|bibliography|works cited)\b', line, re.I))
        for match in re.finditer(':', line):
            pos = offset + match.start()
            if heading or references or any(a <= pos < b for a, b in url_spans):
                continue
            if pos > 0 and pos + 1 < len(prose) and prose[pos-1].isdigit() and prose[pos+1].isdigit():
                continue
            # Citation page locators (Smith 2020: 12) are not clause joiners.
            before = prose[max(0, pos-80):pos]
            after = prose[pos+1:pos+25]
            if re.search(r'\([^()\n]*\b\d{4}[a-z]?\s*$', before) and re.match(r'\s*\d', after):
                continue
            add('A1.colon-candidate', pos, pos+1, 'Review only clause-joining colons in running prose/table cells; headings, reference entries, and cited titles are exempt.')
        offset += len(line)

    sentences = sentence_spans(prose)
    openers = defaultdict(list)
    for _, _, words in sentences:
        start = words[0].start()
        key = tuple(w.group().casefold() for w in words[:2])
        openers[key].append((start, words[min(1, len(words)-1)].end()))
        first = words[0].group().casefold()
        if first in {'either', 'however', 'therefore', 'moreover', 'thus'} or key == ('not', 'just'):
            add('A10.7.glue-opener', start, words[min(1, len(words)-1)].end(), 'Review stock opening in context; an isolated useful transition can be valid.')
        if first in {'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'neither'}:
            add('A3.2.numbered-setup', start, words[min(1, len(words)-1)].end(), 'Review numbered setup or caveat template, not a count alone.')
    for key, locations in openers.items():
        if len(locations) >= 2:
            for start, end in locations:
                add('A10.4.repeated-opener', start, end, f'Opening {" ".join(key)!r} recurs {len(locations)} times; compare rhetorical structure.')
    for first, second in zip(sentences, sentences[1:]):
        if all(item[2][0].group().casefold() == 'if' for item in (first, second)):
            add('A10.6.stacked-conditionals', first[2][0].start(), second[2][0].end(), 'Adjacent If openings; vary the explanatory move without changing conditions.')

    baseline_prose = mask_nonprose(baseline) if baseline is not None else None
    base_trigrams = trigram_locations(baseline_prose) if baseline_prose is not None else {}
    repeated = []
    for phrase, locations in trigram_locations(prose).items():
        if len(locations) >= 2:
            repeated.append({'phrase': phrase, 'count': len(locations),
                             'baseline_count': len(base_trigrams.get(phrase, [])),
                             'newly_repeated': baseline is not None and len(base_trigrams.get(phrase, [])) < 2,
                             'locations': [{'line': text.count('\n', 0, a)+1,
                                            'column': a-text.rfind('\n', 0, a)} for a, _ in locations]})
    result = {'sha256': hashlib.sha256(text.encode('utf-8')).hexdigest(),
              'findings': sorted(findings, key=lambda x: (x['line'], x['column'], x['rule'])),
              'sentence_statistics': stats(prose), 'repeated_trigrams': repeated,
              'limits': [
                  'All matches are candidates requiring human/editorial context, including quoted or protected wording.',
                  'Finite lexical families cannot enumerate every derivation; the editor must check unfamiliar forms.',
                  'Sentence boundaries and passive forms are heuristic; numbers are descriptive, not stylistic targets.',
                  'No authorship inference, automatic edits, or complete-style-pass verdict.',
                  'All contextual checks below still require a full-document reading even when a related heuristic matched.',
                  'P1-P6 are manual reader-processing checks; this helper does not syntactically detect them.',
              ], 'manual_checks_required': MANUAL_CHECKS}
    if baseline is not None:
        result['baseline_sha256'] = hashlib.sha256(baseline.encode('utf-8')).hexdigest()
        result['baseline_sentence_statistics'] = stats(baseline_prose)
    return result


def read_source(path: Path) -> str:
    if path.suffix.casefold() not in {'.md', '.txt', '.markdown'}:
        raise ValueError('Input must be a UTF-8 Markdown or plain-text file.')
    # newline="" keeps CRLF untouched for accurate file fingerprinting.
    with path.open('r', encoding='utf-8', newline='') as stream:
        return stream.read()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--json', action='store_true', help='Print structured JSON to stdout.')
    parser.add_argument('--baseline', type=Path, help='Compare descriptive rhythm and repetition with an earlier file.')
    args = parser.parse_args()
    try:
        report = analyze(read_source(args.input), read_source(args.baseline) if args.baseline else None)
    except (OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        for item in report['findings']:
            print(f"{item['line']}:{item['column']} [{item['rule']}] {item['text']!r}\n  {item['message']}")
        print(f"Candidates: {len(report['findings'])}; repeated trigrams: {len(report['repeated_trigrams'])}")
        print(json.dumps(report['sentence_statistics'], ensure_ascii=False))
        print('Read-only candidate finder. Full contextual review is still required; no authorship verdict.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
