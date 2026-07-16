# Final Exam Reviewer Conversion Specification

## Agent Role

The conversion agent produces a faithful Markdown representation of `final-exam_reviewer.pdf`. It preserves the source's wording, order, choices, summaries, answer explanations, mathematical symbols, grammar productions, and automata notation. It performs conversion and extraction work only; it does not act as an editor, tutor, fact-checker, or diagram author.

## Prerequisites

- The unchanged source file `final-exam_reviewer.pdf` must be available.
- `uvx` must be available for an isolated MarkItDown environment.
- MarkItDown must be invoked as `uvx --from "markitdown[pdf]" markitdown`.
- PyMuPDF may be used only to inventory and render PDF pages, compare ambiguous extraction against the source, and extract embedded appendix images.
- The agent must be able to write `final-exam_reviewer.md` and `final-exam_reviewer_assets/`.

## Exact Workflow

1. Record the source filename and confirm that the PDF has 39 pages.
2. Run MarkItDown as the sole text converter:

   ```powershell
   uvx --from "markitdown[pdf]" markitdown "final-exam_reviewer.pdf" -o "tmp\pdfs\final-exam_reviewer.raw.md"
   ```

3. Do not replace MarkItDown with Docling, OCR, PyMuPDF text extraction, or any other text converter. PyMuPDF text or rendering may be consulted only to verify and resolve an extraction ambiguity; the deliverable remains a cleanup of the MarkItDown conversion.
4. Clean the MarkItDown output without changing academic content. Normalize headings, lists, whitespace, line wrapping, repeated running headers and footers, sparse table artifacts, and duplicated question numbers created by extraction.
5. Compare the cleaned content with pages 1–36 of the PDF. Verify question order, four choices per question, section order, all answer explanations, symbols, productions, subscripts, and transition notation. Resolve ambiguous glyphs by viewing the PDF, never by inference.
6. With PyMuPDF, enumerate the embedded images on pages 37–39. Extract them in page order as PNG files:

   - `final-exam_reviewer_assets/page-37-image-1.png` through `page-37-image-3.png`
   - `final-exam_reviewer_assets/page-38-image-1.png` through `page-38-image-3.png`
   - `final-exam_reviewer_assets/page-39-image-1.png` through `page-39-image-2.png`

7. Add an appendix to `final-exam_reviewer.md` containing relative Markdown image links in the same page and image order. Do not transcribe, summarize, or interpret the diagrams.
8. Run all acceptance checks before treating either Markdown file as publishable.

## Permitted Cleanup

- Normalize document and section headings to Markdown heading levels.
- Convert question choices and answer explanations into consistent Markdown blocks.
- Remove repeated page headers, footers, and page numbers.
- Remove Markdown table scaffolding introduced by PDF layout detection.
- Remove duplicated question numbers such as `1. 1.` when the duplication is clearly an extraction artifact.
- Join broken line wraps and repair source-confirmed word splits or merges.
- Restore source-confirmed spacing, set-builder bars, union bars, subscripts, superscripts, and other notation displaced by extraction.
- Normalize excess blank lines and trailing whitespace.

## Prohibited Behavior

- Do not summarize, paraphrase, rewrite, simplify, expand, or correct the academic content.
- Do not reorder questions, choices, sections, answer explanations, pages, or appendix images.
- Do not invent missing text, image descriptions, captions, examples, answers, or diagrams.
- Do not use OCR or another converter as a silent fallback.
- Do not replace unclear symbols based on subject-matter expectations; compare them with the PDF.
- Do not alter the source PDF.
- Do not publish a partial conversion.

## Failure Handling and Stop Conditions

Stop without publishing partial deliverables if any of these conditions occurs:

- MarkItDown cannot run or returns an incomplete conversion.
- Text from any of pages 1–36 is substantially missing.
- The page count is not 39.
- The expected image count is not exactly eight, distributed 3/3/2 across pages 37–39.
- Any appendix image cannot be extracted or decoded as PNG.
- Question numbering, choice coverage, answer-key coverage, section ordering, or mathematical notation cannot be verified.
- A relative appendix link does not resolve.

Report the failure and retain intermediate files only for diagnosis. Do not silently switch conversion methods.

## Acceptance Criteria

- `final-exam_reviewer.md` contains the full cleaned text from pages 1–36.
- Questions 1–200 appear once, in order, with choices A–D exactly once per question.
- Answer explanations 1–200 appear once and in order.
- All topical-summary, practice-test, and answer-key sections appear in source order.
- Unicode mathematical notation, grammar productions, and automata notation match the PDF after source comparison.
- No repeated running headers, page footers, replacement characters, duplicated question numbers, broken choice markers, or malformed Markdown remain.
- Pages 37–39 are represented by exactly eight relative image references in 3/3/2 order.
- Exactly eight required PNG assets exist, decode successfully, and have nonzero dimensions.
- Every relative Markdown asset path resolves from `final-exam_reviewer.md`.
- `final-exam_reviewer.pdf` remains unchanged.

## Known Limits

- Markdown preserves semantic content, not the PDF's exact pagination, typography, columns, colors, or visual layout.
- Appendix diagrams remain images. They are not searchable, transcribed, captioned, or interpreted.
- Mathematical notation is kept as extracted Unicode where possible. When PDF positioning carries meaning that plain extraction loses, the agent may restore a source-confirmed plain-text or Markdown equivalent.
- MarkItDown's PDF layout detection may emit sparse tables, displaced superscripts, or merged words; only source-confirmed cleanup is allowed.
- Installation is isolated through `uvx`; no global Python environment is modified.
