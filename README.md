# Editor

An agent skill for editing existing prose with small, traceable changes that preserve meaning, facts, voice, and author choices.

Use it for articles, emails, essays, reports, instructions, and academic writing. It reviews clarity, grammar, structure, concision, natural phrasing, repetition, and readability.

## Install

Install through the Agent Skills CLI:

```sh
npx skills add https://github.com/Khilo65/editor --skill editor
```

The repository keeps `SKILL.md` at its root for compatible skill installers. In Codex, invoke the installed skill as `$editor`.

## Use

```text
Use $editor to audit this text without changing it.

Use $editor to suggest the smallest edits that improve clarity and flow.

Apply the approved edits with tracked changes in the Word document.
```

The editor defaults to numbered OLD/NEW suggestions. It applies approved changes only, preserves rejected wording, and checks the current source before applying edits. Word revisions use native tracked changes. Markdown revisions preserve the original and include a clean copy, exact patch, and concise change log.

## Editorial checks

- Preserve facts, uncertainty, logical conditions, quotations, names, protected wording, and accepted terminology.
- Review sentence and paragraph construction, grammar, punctuation, usage, spelling, and clear referents.
- Flag empty rhetorical templates, vague abstractions, and redundant summaries.
- Remove unnecessary qualifications even once. Keep or recast a limit only when omission would mislead, overstate evidence, or change a relevant condition; apply [Q1](references/model-style-review.md#q1-keep-only-necessary-qualifications).
- Review recurring vocabulary, formatting, and rhythm across models, using observed text and suitable reference samples; recheck for habits introduced by repairs.
- Check helpful clause markers, embedded clauses, distant related words, opaque noun strings, improvised verbs, strained personification, and compressed invented labels.

This is an opinionated house style. It requires active voice in new prose and proposed replacements, permits useful repetition, and enforces specific word, punctuation, and usage preferences, including the [named Claude/Astra phrase bans](references/model-style-review.md#mandatory-claude-and-astra-phrase-bans). Those phrases require a local recast even once; preserve meaning and genuine uncertainty. Protected text has explicit exceptions. Adapt the editorial guide if your preferences differ.

## Optional checker

The Python helper uses only the standard library and reads UTF-8 Markdown or plain text:

```sh
python3 scripts/check_style.py draft.md --json
python3 scripts/check_style.py revised.md --baseline original.md --json
```

It reports candidates and descriptive sentence statistics. It does not apply edits, certify style compliance, determine authorship, or syntactically detect the six reader-processing checks. Those checks require contextual editorial review. The helper also flags the named mandatory phrase bans, subject to protected-text and scope checks. Those checks do not make an applicable ban optional. The report lists Q1 and completion of phrase review as manual requirements, including when no regex matches. Model profiles and Markdown layout require contextual review; the helper does not infer them.

## Guide structure

- [Skill workflow](SKILL.md)
- [Editorial review](references/editorial-guide.md)
- [Style habits across models](references/model-style-review.md)
- [Grammar and form](references/grammar-and-form.md)
- [Usage and spelling](references/usage-lookup.md)
- [Revision handling](references/revision-workflow.md)
- [Sources and rule provenance](references/provenance.md)

## Sources

The guidance synthesizes writing principles from William Strunk Jr.'s *The Elements of Style*, revised by Chris Hong, author-supplied editorial preferences, and contextual applications of [Clark, Martin, and Mahowald's readability study](https://arxiv.org/abs/2610.29162). [Graphite's AI Tells research](https://graphite.io/five-percent/research/ai-tells) also informs the contextual review of recurring habits; detailed Markdown checks are editorial extensions. [Book-to-skill](https://github.com/virgiliojr94/book-to-skill) supported the extraction and conversion workflow.

The repository contains operational instructions and original examples. It excludes the source PDFs, raw extractions, private drafts, and local test artifacts. The study motivates contextual checks; it does not validate this checklist through a new human comprehension experiment.
