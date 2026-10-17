# software-measurement

Undergraduate research project on software measurement (automated software size estimation with language models), building on prior work by another research group.

Full background, glossary, prior findings, and open directions:

@RESEARCH_CONTEXT.md

## Confidentiality

`papers/` holds the source PDFs. Some are confidential or paywalled. The folder is gitignored: never commit, upload, publish, or quote large passages from these files outside this machine.

## Documentation rules (always follow)

`PAPER.md` is the project's living documentation, written as a research paper. Whenever a session makes progress, update it **in the same session**:

- **New paper read / citation found:** update Section 2 (Related Work) and References.
- **Research question or gap chosen:** update Sections 1.2 to 1.4 and 2.4.
- **Dataset, model, or experiment design decided:** update Section 3 (Methodology).
- **Experiment run:** record exact numbers in Section 4 (Results) and link to the code/notebook that produced them. Never invent or estimate results.
- **Interpretation or limitation noticed:** update Section 5 (Discussion) or 6 (Threats to Validity).
- **Every change:** add a row to the Revision History table (date, bumped version, one-line summary).

Write in formal academic prose. Leave `[TBD]` markers in place for anything not yet known rather than filling them with guesses.

Also keep `RESEARCH_CONTEXT.md` in sync: it is the quick-reference briefing, and `PAPER.md` is the formal write-up.
