# [Working Title] Toward Generalizable Automated Software Size Measurement with Language Models

**Author:** Sky Zheng, Undergraduate Researcher
**Advisor:** Dr. Ekincan Ufuktepe
**Institution:** University of Missouri, Columbia
**Draft version:** 0.1 · **Last updated:** 2026-10-17

> **Status:** Living draft. Sections marked `[TBD]` are not written yet. Every update to the project (papers read, decisions made, experiments run, results) goes into the matching section below and gets an entry in the **Revision History** at the end.

---

## Abstract

[TBD: write once the research question and results exist. Target length is 150 to 250 words: problem, gap, approach, key result, implication.]

_Placeholder framing:_ Software size underpins cost, effort, and schedule estimation, but measuring it by hand with methods such as COSMIC is slow and needs trained experts. Earlier work has shown that fine-tuned BERT-style models can estimate size from requirements and source code. However, these models generalize poorly across organizations unless they are trained on each organization's own data. This project builds on that work by [TBD: contribution].

**Keywords:** software measurement, functional size measurement, COSMIC, effort estimation, BERT, language models, transfer learning

---

## 1. Introduction

### 1.1 Motivation

Estimating what software is worth, and how much effort it takes to build, starts with knowing how _big_ it is. Functional size measurement (FSM) methods such as COSMIC (ISO/IEC 19761) give a standardized way to quantify size, and that size feeds cost, effort, and schedule models. In practice, manual FSM is expensive, slow, and depends on certified specialists that most organizations don't have. As a result it is rarely done.

### 1.2 Problem Statement

Automated size measurement with language models is technically feasible, but current models **do not generalize** to organizations whose data they were not trained on (see Section 2.3). [TBD: refine into the specific problem this project tackles.]

### 1.3 Research Questions

- **RQ1:** [TBD]
- **RQ2:** [TBD]
- **RQ3:** [TBD]

_Candidate directions are listed in `RESEARCH_CONTEXT.md` Section 6._

### 1.4 Contributions

[TBD: bullet list of what this work adds.]

### 1.5 Paper Organization

Section 2 reviews background and related work. Section 3 describes the methodology. Section 4 presents results. Section 5 discusses implications. Section 6 covers threats to validity. Section 7 concludes.

---

## 2. Background and Related Work

### 2.1 Functional Size Measurement

**COSMIC** measures size by counting _data movements_ of four kinds: **Entry (E)**, **Exit (X)**, **Read (R)**, and **Write (W)**. Each movement counts as one COSMIC Function Point (CFP). **MicroM** is a newer size metric proposed by the research group whose work this project extends. [TBD: add a formal description of MicroM and a citation.]

### 2.2 Language Models for Software Engineering

BERT-style transformer models can be adapted to a field by further pre-training on text from that field (_domain adaptation_), then _fine-tuned_ on labeled task data. Relevant variants include SE-BERT / SE-BERTurk (pre-trained on software-engineering text) and CodeBERT (pre-trained on code plus natural language).

### 2.3 Prior Work on Automated Size Measurement

A single research group has studied this problem in three stages [TBD: citations]:

1. **Requirements-based measurement with domain-adapted models** [TUBITAK paper, TBD cite]. SE-BERT and SE-BERTurk were fine-tuned on one company's requirements labeled with COSMIC and MicroM. SE-BERTurk reached about 69% exact-match accuracy vs. 65.7% for plain BERTurk. This showed a modest benefit from domain adaptation, but on a single organization's data.

2. **Code-based measurement** [Automated Software Engineering paper, TBD cite]. CodeBERT was applied to about 1,800 to 2,100 manually labeled Python functions from CodeSearchNet, with multiple data movements allowed per function. It reached up to 91% per-movement accuracy, but whole-function exact accuracy was only about 49% (COSMIC) and 44% (MicroM). The study was exploratory: Python only, open-source only.

3. **Industrial evaluation** [Journal of Systems & Software paper, TBD cite]. BERT and SE-BERT were evaluated on requirements from two companies (industrial automation; tech/aviation) under three settings: a generic model trained on 26 open-source projects, the same generic model applied to a new organization (external), and organization-specific training (internal). Generic models collapsed in the external setting (PRED(30) below 20% in some cases, vs. about 85% in the lab). Organization-specific training improved MMRE by up to 65% (0.53 to 0.18). Fine-tuned models beat zero-shot GPT-4o, GPT-o3, and GPT-o4-mini-high by about 3x in accuracy.

### 2.4 Research Gap

Existing work leaves open: [TBD: pick the gap(s) this paper targets, e.g. how much organizational data is needed, cross-language code measurement, few-shot LLM baselines, joint prediction of E/X/R/W, a public benchmark.]

---

## 3. Methodology

### 3.1 Research Design

[TBD]

### 3.2 Datasets

[TBD: source, size, labeling procedure, label distribution, train/validation/test splits. Link to data in repo.]

### 3.3 Models and Baselines

[TBD]

### 3.4 Training and Experimental Setup

[TBD: hyperparameters, hardware, random seeds, software versions.]

### 3.5 Evaluation Metrics

Planned to match prior work so results can be compared:

- **MMRE:** Mean Magnitude of Relative Error (lower is better)
- **PRED(30):** share of predictions within 30% of the actual value (higher is better)
- **Exact-match accuracy:** per movement and aggregated per function/requirement
- [TBD: any extra metrics]

---

## 4. Results

[TBD: one subsection per RQ. Report tables/figures with exact numbers and link to the scripts or notebooks that produced them.]

### 4.1 RQ1

[TBD]

### 4.2 RQ2

[TBD]

---

## 5. Discussion

[TBD: interpret results, compare with prior work in Section 2.3, give practical implications for organizations adopting automated measurement.]

---

## 6. Threats to Validity

- **Internal validity:** [TBD]
- **External validity:** [TBD]
- **Construct validity:** [TBD]
- **Conclusion validity:** [TBD]

---

## 7. Conclusion and Future Work

[TBD]

---

## References

> Fill in full citations (authors, year, title, venue, DOI). Numbers cited in Section 2.3 come from a summary and must be checked against the original papers.

1. [TBD] SE-BERT / SE-BERTurk for COSMIC and MicroM measurement from requirements. _TUBITAK-related publication._
2. [TBD] CodeBERT-based software size measurement from Python source code. _Automated Software Engineering._
3. [TBD] Industrial evaluation of BERT-based size measurement across organizations. _Journal of Systems and Software._
4. COSMIC Measurement Manual / ISO/IEC 19761. [TBD: exact version]
5. Devlin et al., "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding," NAACL 2019.
6. Feng et al., "CodeBERT: A Pre-Trained Model for Programming and Natural Languages," Findings of EMNLP 2020.
7. Husain et al., "CodeSearchNet Challenge: Evaluating the State of Semantic Code Search," arXiv:1909.09436, 2019.

---

## Appendix

[TBD: extra tables, labeling guidelines, prompt templates, hyperparameter grids.]

---

## Revision History

| Date       | Version | Change                                                                                                                                            |
| ---------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-17 | 0.1     | Created paper skeleton. Wrote Introduction motivation and Background/Related Work (Section 2) from the summary of the prior three-stage research. |
