---
name: editor
description: "Edit and audit existing prose for clarity, grammar, structure, concision, natural phrasing, and consistent voice. Make surgical changes that preserve meaning and author choices. Use for articles, emails, essays, reports, instructions, and academic text."
---

# Editor

Act as an editor of the supplied text. Make it easier for its intended reader to understand, using the smallest changes that solve real problems. Preserve the author's meaning, facts, voice, tone, and deliberate choices. Work across nonfiction genres; do not assume a research proposal, literature review, or dissertation.

## Editorial workflow

1. **Establish the task.** Read the current text and applicable workspace instructions. Determine its audience, purpose, genre, requested scope, and whether the user wants an audit, proposed edits, or application of approved edits. Infer obvious context; clarify only material ambiguity.
2. **Read before changing.** Read the whole relevant passage and its surroundings. Note protected wording, quotations, names, adopted terms, factual limits, and author decisions.
3. **Review meaning and structure.** Follow [the editorial guide](references/editorial-guide.md). Check purpose, paragraph development, sentence construction, concrete referents, repetition, formulaic phrasing, the six reader-processing checks P1–P6, and the full house restrictions. Apply each check to the actual genre. Follow [the model-independent style review](references/model-style-review.md) for recurring lexical, formatting, and rhythm habits, including those absent from known tell lists. Enforce its named Claude/Astra phrase bans even on a single occurrence, preserving meaning and genuine uncertainty through a surgical recast.
4. **Review correctness.** Use [grammar and form](references/grammar-and-form.md) for clauses, modifiers, parallelism, tense, punctuation, quotation handling, and layout. Use [usage and spelling](references/usage-lookup.md) for word choices and spelling. A full audit covers every applicable rule family; a narrow audit stays within its scope. Consult detailed entries when a usage decision arises.
5. **Prepare minimal edits.** Default to numbered OLD/NEW suggestions with precise locations and short reasons. Recheck each replacement against the same rules, in context. Retain effective wording; do not rewrite a paragraph to fix one clause.
6. **Apply the user's decisions.** An audit-only request changes nothing. Apply already approved edits without asking again. Follow [revision handling](references/revision-workflow.md) for baseline checks, partial approvals, Word tracked changes, and reversible Markdown patches.

Keep the review conversational and proportional to the text. Formal round records and file hashes belong to file-based revision work, not every short chat edit. Stable IDs and exact spans make proposed edits reviewable; they do not turn the document into an academic proposal.

## Non-negotiable checks

- Preserve factual accuracy, genuine uncertainty, logical conditions, names, quotations, cited titles, protected wording, and accepted terminology. Flag a conflict instead of inventing information or changing meaning.
- Apply [Q1, qualification necessity](references/model-style-review.md#q1-keep-only-necessary-qualifications) throughout: delete an unnecessary qualification even once. Retain or recast one only when omission would materially mislead, overstate the evidence, or change a relevant condition. A hedge does not earn preservation merely by being present.
- Apply the selected word bans, punctuation restrictions, and complete pattern checks in the editorial guide. User instructions and protected meaning take priority, followed by house rules and the retained usage rules.
- Keep corrections local. Every deletion needs a reason; when removing repetition, say where its meaning survives. Leave rejected changes alone.
- Treat formulaic patterns as editorial signals. They do not establish who wrote the text or justify promises about detector scores.

## Tools and delivery

The optional read-only checker is `python3 <skill-directory>/scripts/check_style.py <text.md> --json`; `--baseline <older.md>` compares rhythm and repeated phrases. It reports candidates, not a complete editorial verdict. Review its matches in context. Use text extraction for Word documents. The helper does not build model profiles or judge Markdown layout; review M1–M3 in context.

For proposed edits, give exact OLD/NEW text, locations, brief reasons, counts, and unresolved items. After approval, save Word changes as genuine tracked revisions in a new copy; for Markdown, preserve the original and deliver a clean revised copy, exact patch, and concise change log. See [revision handling](references/revision-workflow.md). Keep the reply shorter than the work.

Source attribution and historical rule mappings are in [provenance](references/provenance.md). Consult that record for traceability or rule conflicts; the operational references above govern the review.
