# Review and revision handling

## Read and select the mode

Read the whole document or the whole requested part before diagnosing it. Include relevant notes, table cells, headings, and citations. Do not claim a complete audit of text you could not read. Ask only when the authoritative version or intended scope cannot be resolved safely.

Default to proposals. An audit-only request produces findings and counts without editing. A proposal request produces exact OLD/NEW items and preserves the source. Apply an existing approval without asking for it again. Mixed requests can approve some items, reject others, and ask for revised proposals; maintain their separate statuses. An exploratory question authorizes an answer, not a document change.

## Record proposed edits

For a file-based round, record its absolute source path, SHA-256 hash, date, scope, and round number in a concise companion proposal record. Use the document's existing organization; do not create a research-project administration system. In chat-only work, keep this information in the conversation. Do not modify the source or create administrative files during an explicit no-file-writes request.

Number items in document order with stable IDs such as R1-1. Each item includes the reliable location, exact OLD text, complete NEW text, rule IDs, and a one-line reason. Use lines for Markdown and text; use section, paragraph number, table cell, or anchored quote for Word. Cite page numbers only after verifying pagination. Group repeated findings by named pattern without losing stable item IDs or document order. Explain the overall repair strategy once.

State the most consequential issue, totals, protected flags, unverified factual additions, and open decisions. Check every NEW span against the full rule set before proposing it. A deletion needs a reason. For repetition, give the location where the point still lives. For a gratuitous qualification, apply [Q1](model-style-review.md#q1-keep-only-necessary-qualifications); do not relocate or recast an unnecessary caveat merely to preserve its wording. A necessary condition or genuine uncertainty must survive accurately. Propose new facts only after checking them or clearly flagging them for verification before use.

When the user requests the full list, include every pending OLD/NEW item. Never silently substitute a revised proposal for an approved one. Interpret voice-transcription names from context and flag any material uncertainty.

## Approval and baseline drift

Record each item as pending, approved, approved as revised, rejected, withdrawn, superseded, or applied. “Keep the old version” means do not change it. A pointed question about a proposal needs an answer, not an inferred approval. An ambiguous response does not authorize changing that item; apply clearly approved independent items and keep the ambiguous item pending.

Before applying, reread and hash the live source. When the baseline differs, map approved spans onto the current version using exact text plus contextual anchors. Report items the author's revisions superseded. If an OLD span is missing, duplicated without a unique anchor, or overlaps another conflicting item, keep it pending and explain the conflict. Do not use a global replacement or guess at the intended occurrence.

Prepare a new output copy; preserve the original and earlier rounds. Never overwrite an existing revised artifact. Do not rewrite a whole paragraph to apply one approved clause. Re-read every changed sentence and its paragraph for grammar, duplication, referents, citations, unintended factual changes, mandatory phrase bans, and Q1 qualification necessity. Check that applied counts match approved applicable items. Preserve deliberate typos or grammar when the user instructs you to keep them.

## Markdown review package

After approval, deliver `<stem>_edited.md`, `<stem>_edits.patch`, and `<stem>_changes.md`, using a new round suffix if those names exist. Keep the source byte-identical, including its line-ending convention. The revised file is clean text, without inline editorial markers.

Make a unified diff against the exact baseline. Use stable relative patch paths `a/<source-basename>` and `b/<source-basename>`, and record those paths in the log; the clean deliverable can have a different filename. Include enough context to locate every change. Do not present an approximate prose comparison as an exact patch. Handle the final newline faithfully, including a valid no-newline marker if needed.

The numbered log contains each applied item's OLD/NEW text, rule/reason, location, statuses of skipped items, original and revised hashes, and the filenames. Verify the patch in an isolated copy of the baseline using an actual patch applicator. Forward application must reproduce the revised bytes; reverse application must recover the baseline bytes. Do not test the patch by applying it to the author's live file. If a diff tool changes line endings or cannot round-trip the text, fix the patch or report the limitation before delivery.

## Word tracked changes

Read the available document-editing guidance and use the environment's resolved document runtime for DOCX work. If no document tooling is available, inspect OOXML directly using suitable ZIP/XML tools. Do not claim native tracking from colored text or a clean rewrite. The bundled `add_tracked_replacements.py` helper handles only a single text node and can lose formatting on inserted/deleted text; it is not sufficient for general multi-run replacements.

Save a new `<stem>_edited.docx`, with a round suffix on collision, and a concise companion change log. Use **Codex** as the new revision author, current timestamps, and noncolliding revision IDs. Preserve pre-existing revision authors, IDs, dates, comments, relationships, styles, numbering, notes, headers, footers, fields, links, images, and unrelated ZIP parts.

For an ordinary approved replacement across formatting runs:

1. Read the current visible text with pending insertions included and deleted text excluded. Locate the approved span within its paragraph/cell and map characters back to the underlying `w:r` and `w:t` elements.
2. Split only the boundary runs at the approved offsets, preserving `w:rPr` and necessary `xml:space`. Leave unaffected runs and nontext nodes in place. Do not assign `paragraph.text` or rebuild the whole paragraph.
3. Wrap removed run fragments in `w:del` and convert their text nodes to `w:delText`. Insert the replacement as `w:ins` with proper run properties. Inherit the first affected run's formatting for plain replacement wording; retain separate styling on surviving names and equivalent styled spans. If the intended new styling is ambiguous, flag it instead of flattening the text.
4. Enable `w:trackRevisions` in settings and preserve schema ordering and package wiring. If a settings part must be added, add its relationship and content-type entry too. Insertions, deletions, and structural edits need their actual OOXML revision structures.
5. Do not nest revisions illegally, accept or reject other reviewers' changes, or delete comment/field boundaries to fit a replacement. Preserve unrelated pending changes. When an approved edit overlaps an older revision or complex field, use a verified revision-aware operation or flag the overlap for a concrete decision. Do not silently flatten it. A new edit inside this same round's insertion can fold into that insertion; record the fact.

Paragraph removals, table-row deletions, hyperlink-spanning changes, equations, and note/header edits need format-appropriate operations, not ordinary text-run replacement. Track structural deletions where applicable. A limitation in one item does not authorize an untracked rewrite of the file.

## Verification and delivery

For Word, inspect the revision XML and validate the package. Compute two projections for only the newly added revisions, retaining all older revision states. Accepting the new revisions must yield precisely the approved current text; rejecting them must recover the baseline current text. Check unaffected parts and formatting. Render and visually inspect the saved result using the available document workflow. If rendering is unavailable, state that visual QA was not completed; do not label it verified. Keep test projections separate from the tracked deliverable.

For both formats, reread changed passages, check references affected by edits, compare source hashes to confirm preservation, and reopen/hash outputs to confirm the writes. If an output write failed, retain the source and stage a new file rather than claiming success. Review any unresolved bans in protected text as exceptions.

The applied record gives full OLD/NEW for each applied item, before/after hashes, applied and skipped counts, author decisions, flags, and requested word/page counts. Update only records the actual task requires; do not create master ledgers or regenerate unrelated file formats by default. Report the result concisely. Never promise an unsupported AI-detector outcome.
