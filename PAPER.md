# [Working Title] Toward Generalizable Automated Software Size Measurement with Language Models

**Author:** Sky Zheng, Undergraduate Researcher
**Advisor:** Dr. Ekincan Ufuktepe
**Institution:** University of Missouri, Columbia
**Draft version:** 0.6 · **Last updated:** 2026-10-17

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

Automated size measurement with language models is technically feasible, but current models **do not generalize** to organizations whose data they were not trained on (see Section 2.3). Prior work is also limited to a few languages: Python for source code, and English and Turkish for requirements.

This project has two goals. Both are **provisional** and may be revised as the work progresses:

- **G1 (Cross-organization generalization):** Develop a software size measurement tool that can be trained on data from many sources, not one company's data, and that measures size as accurately as possible for any software organization.
- **G2 (Language coverage):** Extend automated measurement beyond Python, English, and Turkish to other programming languages and natural languages.

As a first exploratory step toward these goals, this work examines whether COSMIC functional size and Chidamber and Kemerer (CK) object-oriented metrics can be computed together within one toolchain (Section 2.4). The hypothesis is that structural code metrics, which do not depend on an organization's writing style, may serve as complementary signals for size models that must generalize across organizations. [TBD: refine into the specific problem this project tackles.]

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

The research group of Ünlü, Tenekeci, Demirörs, and colleagues at the Izmir Institute of Technology has studied this problem in several steps. Early exploratory studies fine-tuned BERT and BERT_SE on user stories, reaching 72.8% and 74.4% accuracy for total COSMIC size [22]. They also fine-tuned CodeBERT on 4,800 Python and 1,100 C# functions [21]. Three later studies form the basis of this project:

1. **Requirements-based measurement with domain-adapted models** [1]. SE-BERT (English) and SE-BERTurk (Turkish) were pre-trained on software-engineering corpora and fine-tuned, as regressors, on a proprietary, multilingual, organization-specific requirements dataset labeled with COSMIC and MicroM by domain experts. SE-BERTurk improved exact-match accuracy from 65.7% to 69.3% over BERTurk, and SE-BERT improved it from 66.9% to 68.2% over BERT. Both also outperformed the earlier domain-adapted baselines BERT_SE and RE-BERT.

2. **Code-based measurement** [2]. CodeBERT was fine-tuned on Python functions from CodeSearchNet, manually labeled with COSMIC (1,787 functions) and MicroM (2,127 functions), with multiple data movements allowed per function. Per-movement exact-match accuracy was 67.0% (Entry), 73.1% (Exit), 87.6% (Write), and 91.4% (Read). MicroM event-type accuracy reached 81.5%. Accuracy for the aggregated total was lower: 49.2% for CFP (NMAE 0.273) and 44.1% for MicroM (NMAE 0.29). The study was exploratory and limited to open-source Python.

3. **Industrial evaluation** [3]. BERT and SE-BERT were evaluated on requirements from two organizations, an industrial automation company (Case 1) and a global technology company focused on aviation (Case 2), under three settings: generic (trained and tested on a heterogeneous dataset from 26 open-source specifications, publicly released as SSMB), external (the generic model applied to organization data), and internal (trained and tested on organization data). The generic models reached PRED(30) ≈ 0.85 at sentence level (0.63 at use-case level). In external evaluation, PRED(30) for total COSMIC fell to 0.1129 (Case 1) and 0.1240 (Case 2), with MMRE above 0.50. Organization-specific training lowered MMRE by up to 65% (0.5268 → 0.1821). In external evaluation, SE-BERT showed no clear advantage over BERT, which the authors read as domain misalignment outweighing domain-adaptive pre-training. In a zero-shot pre-evaluation with COSMIC/MicroM background supplied in the prompt (633 heterogeneous use cases), the best GPT model (o4-mini-high) reached a CFP PRED(30) of 0.2164, versus 0.6382 for SE-BERT, a gap of more than 3x.

### 2.4 Tool Support for COSMIC and CK Metrics

A tool survey (October 2026) found **no existing tool, IDE, or plugin that computes both COSMIC functional size and CK metrics**. The two families of metrics are supported by separate tools.

#### 2.4.1 CK Metrics
The CK suite [8] measures the design structure of object-oriented code at the class level:

| Metric | Name | Captures |
|---|---|---|
| WMC | Weighted Methods per Class | Class complexity (often the sum of method cyclomatic complexities) |
| DIT | Depth of Inheritance Tree | How deep a class sits in the inheritance hierarchy |
| NOC | Number of Children | Number of direct subclasses |
| CBO | Coupling Between Objects | Number of other classes a class depends on |
| RFC | Response For a Class | Methods that can run in response to a message to the class |
| LCOM | Lack of Cohesion in Methods | How weakly a class's methods share its fields |

Because CK metrics are defined from source structure alone, they can be computed fully automatically. The main tools are:

- **SciTools Understand** [9]: commercial, with a free renewable educational license for students and teachers [10]. Analyzes 17+ languages, including Java, C, C++, C#, and Python. It provides CK metrics (e.g., `CountClassCoupled` for CBO, `MaxInheritanceTree` for DIT, `PercentLackOfCohesion` for LCOM) and a Python API that supports **custom metric plugins**. Which metrics are available varies by language.
- **Analizo** [11]: open source (GPL-3.0). Supports C, C++, Java, and C#, and computes CK-style metrics including CBO, RFC, and LCOM4.
- **CK** (Aniche) [12]: open source (Apache 2.0), Java only. Analyzes source code without compiling it and outputs class-, method-, and variable-level CSV files. Beyond CK, it reports LOC, fan-in/fan-out, TCC/LCC, and counts of loops, returns, and similar constructs. Its README notes that its original LCOM implementation is unreliable and recommends the normalized LCOM*.
- **CKJM-extended** [13]: open source, Java only. Computes 19 metrics from compiled bytecode.

No well-maintained open-source tool computing the full CK suite for **Python** was found.

A known caveat is that different tools implement the "same" metric differently, so values (especially LCOM) can only be compared when computed by the same tool and definition [14].

#### 2.4.2 Automated COSMIC Measurement
COSMIC needs the user's view of functionality: *functional processes* triggered by functional users, *data groups*, and the boundary between the software and its users. Source code does not state these directly, so automation from code relies on language- or framework-specific mapping rules. Most automation work is academic [15]. A survey of 336 FSM specialists found automated FSM from code "important but challenging," with COSMIC the preferred method to automate [15].

| Tool | Input | Approach | Reported result |
|---|---|---|---|
| COSMIC Solver (Tarhan et al.) [16] | Running Java business application | AspectJ captures functional execution traces as textual UML sequence diagrams, which are tagged with E/X/R/W and counted by a Calculator component | 77% convergence with manual counts; the trace component missed some objects of interest and double-tagged others |
| JavaCFP (Chamkha et al.) [15] | Java source code | NetBeans plugin that tracks implemented functionality against requirements | not available in the sources reviewed |
| CFP4J (Sahab et al.) [15] | Java Spring Web MVC applications | Mapping rules from framework constructs to data movements; described as openly accessible | public repository not located |
| Regex-based tool (Moulla et al.) [17] | C source code | Regular-expression rules mapping I/O and storage calls to data movements | prototype |
| CosmiCode [18] | Arduino code | Regular expressions and NLP, with an ML extension | 98.28% (rules) and 88.9% (ML) in initial tests |
| x86 / ARM / MIPS prototypes [15] | Assembly code | Instruction-level mapping rules | prototypes |
| ScopeMaster [19] | Textual requirements and user stories | Proprietary NLP | vendor-reported >85% agreement with experts |
| cosmic-sizing-tool [20] | Manual entry | Web application for recording COSMIC measurements | not automated |

No code-based COSMIC tool was found for Python, C#, or JavaScript. The language-model approach in Section 2.3 is therefore the only code-based COSMIC method reported for Python.

#### 2.4.3 Ways to Combine Them
COSMIC and CK measure different things: *how much functionality* versus *how the code is structured*. They also use different units. COSMIC counts per functional process, which in code usually maps to an entry-point method such as a controller action, handler, or command. CK metrics are per class. Combining them requires aligning these units, either by mapping functional processes to methods and adding method-level structural metrics, or by summing COSMIC counts up to the class or module level. Four candidate combination strategies are considered:

1. **Single-platform pipeline:** Compute CK metrics in Understand and implement COSMIC data-movement detection as an Understand metric plugin (rule-based or model-backed). One parser serves all languages, which keeps metrics consistent across languages.
2. **Multi-tool pipeline:** Run open-source CK tools (Analizo, CK) alongside COSMIC labels or model predictions, and join the outputs by class or method. This is free but needs per-tool adapters and brings in cross-tool metric inconsistency.
3. **Feature fusion for size prediction:** Use CK and other structural metrics as extra features next to code embeddings (e.g., CodeBERT) in the size model, and test whether they improve cross-organization accuracy (G1).
4. **Domain-shift characterization:** Use CK metric distributions to describe how organizations' codebases differ, for example to select or weight training data from similar organizations.

### 2.5 Research Gap

Existing work leaves open: [TBD: pick the gap(s) this paper targets, e.g. how much organizational data is needed, cross-language code measurement, few-shot LLM baselines, joint prediction of E/X/R/W, a public benchmark.] Section 2.4 adds a further gap: **no tool combines functional size (COSMIC) with structural metrics (CK)**, and code-based COSMIC automation is still language-specific and mostly limited to Java and C.

---

## 3. Methodology

### 3.1 Research Design

**Decision (2026-10-17):** Python is the first target language. This allows direct comparison with the prior code-based study [2] and reuse of its manually labeled CodeSearchNet functions. It also fills the gap that no open-source CK tool covers Python (Section 2.4.1). Java is a likely second language. The planned toolchain is SciTools Understand (CK metrics through `und metrics` and the Python API), pending an educational license. Understand (Build 1265, macOS arm64) was installed on 2026-10-17, along with the Understand for VS Code extension (v1.1.6); the `und`, `userver`, and `upython` command-line tools are available. A license has not yet been obtained. [TBD: rest of design]

### 3.2 Datasets

[TBD: source, size, labeling procedure, label distribution, train/validation/test splits. Link to data in repo.]

### 3.3 Models and Baselines

[TBD]

### 3.4 Training and Experimental Setup

[TBD: hyperparameters, hardware, random seeds.] Software versions: SciTools Understand Build 1265; Understand for VS Code extension v1.1.6. Python 3.12.12 environment managed with uv (dependencies pinned in `pyproject.toml` and `uv.lock`): PyTorch 2.14.1 (Apple Metal/MPS backend), Transformers 5.20.1, Datasets 5.1.0, scikit-learn 1.9.1, pandas 3.0.6, NumPy 2.5.4, Radon 6.0.1, and Lizard 1.24.1. Hardware: Apple M3, 16 GB RAM. [TBD: remaining software versions]

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

> Numbers in Section 2.3 were checked against the full texts of [1], [2], [3], [21], and [22] on 2026-10-17. Local copies are in `papers/` (gitignored and confidential; do not commit or redistribute).

1. S. Tenekeci, H. Ünlü, B. Keçeci, M. E. İncir, O. Demirörs, "Automated software size measurement using multilingual domain-adapted language models," _Turkish Journal of Electrical Engineering and Computer Sciences_, 34(2), 234–247, 2026. DOI: 10.55730/1300-0632.4172. Open access: https://journals.tubitak.gov.tr/elektrik/vol34/iss2/5/
2. S. Tenekeci, H. Ünlü, B. A. Gül, D. Keleş, M. Küçük, O. Demirörs, "Automating software size measurement from Python code using language models," _Automated Software Engineering_, 33, 19, 2026. DOI: 10.1007/s10515-025-00571-z
3. H. Ünlü, S. Tenekeci, D. E. Kennouche, O. Demirörs, "Automating software size measurement with language models: Insights from industrial case studies," _Journal of Systems and Software_, 231, 112638, 2026. DOI: 10.1016/j.jss.2025.112638. Dataset: https://github.com/smtnkc/SSMB
4. COSMIC Measurement Manual / ISO/IEC 19761. [TBD: exact version]
5. Devlin et al., "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding," NAACL 2019.
6. Feng et al., "CodeBERT: A Pre-Trained Model for Programming and Natural Languages," Findings of EMNLP 2020.
7. Husain et al., "CodeSearchNet Challenge: Evaluating the State of Semantic Code Search," arXiv:1909.09436, 2019.
8. S. R. Chidamber and C. F. Kemerer, "A Metrics Suite for Object Oriented Design," _IEEE Transactions on Software Engineering_, 20(6), 1994.
9. SciTools, Understand: metrics documentation. https://docs.scitools.com/help/metrics/metrics-overview.html
10. SciTools, Educational license. https://docs.scitools.com/help/licensing/educational-license.html
11. Analizo: an extensible multi-language source code analysis and visualization toolkit. https://github.com/analizo/analizo
12. M. Aniche, CK: Java code metrics calculator. https://github.com/mauricioaniche/ck
13. M. Jureczko, CKJM-extended. https://github.com/mjureczko/CKJM-extended
14. "Evaluation of Software Product Quality Metrics," arXiv:2009.01557, 2020.
15. D. K. Moulla, A. A. Kitikil, E. Mnkandla, H. Soubra, A. Abran, "Functional Size Measurement for X86 Assembly Programs," IWSM-Mensura 2023, CEUR-WS Vol-3543. https://ceur-ws.org/Vol-3543/paper3.pdf
16. A. Tarhan et al., "COSMIC Solver: A Tool for Functional Sizing of Java Business Applications," _Balkan Journal of Electrical & Computer Engineering_, 6(1), 2018. https://dergipark.org.tr/en/download/article-file/435554
17. D. K. Moulla et al., "Automated COSMIC Function Points Measurement for C Program Using Regular Expressions," IWSM-Mensura 2022, CEUR-WS Vol-3272. https://ceur-ws.org/Vol-3272/IWSM-MENSURA22_paper4.pdf
18. "CosmiCode: Automated COSMIC Measurement Tool for Arduino Using RegEx and NLP," Springer, 2025. https://link.springer.com/chapter/10.1007/978-3-031-82377-0_26
19. ScopeMaster: automated COSMIC measurement from requirements. https://cosmic-sizing.org/publications/automated-software-estimation-with-scopemaster/
20. cosmic-sizing-tool. https://github.com/cosmic-sizing-tool/cosmic-sizing-tool
21. S. Tenekeci, H. Ünlü, E. Dikenelli, U. Selçuk, G. Kılınç Soylu, O. Demirörs, "Predicting Software Size and Effort from Code Using Natural Language Processing," IWSM-Mensura 2024, CEUR-WS Vol-3852. https://ceur-ws.org/Vol-3852/paper1.pdf
22. H. Ünlü, S. Tenekeci, C. Çiftçi, İ. B. Oral, T. Atalay, T. Hacaloğlu, B. Musaoğlu, O. Demirörs, "Predicting Software Functional Size Using Natural Language Processing: An Exploratory Case Study," _50th Euromicro SEAA_, pp. 188–193, IEEE, 2024. DOI: 10.1109/SEAA64295.2024.00036

---

## Appendix

[TBD: extra tables, labeling guidelines, prompt templates, hyperparameter grids.]

---

## Revision History

| Date       | Version | Change                                                                                                                                            |
| ---------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-10-17 | 0.1     | Created paper skeleton. Wrote Introduction motivation and Background/Related Work (Section 2) from the summary of the prior three-stage research. |
| 2026-10-17 | 0.2     | Added provisional goals G1 (cross-organization generalization) and G2 (language coverage) to Section 1.2. Added Section 2.4 (tool survey for COSMIC and CK metrics, and candidate ways to combine them). Renumbered Research Gap to 2.5. Added references 8 to 20. |
| 2026-10-17 | 0.3     | Filled in full citations for the three prior papers (refs 1 to 3). Added two related earlier papers by the same group (refs 21, 22). Recorded the decision to start with Python (Section 3.1). |
| 2026-10-17 | 0.4     | Checked Section 2.3 against the full-text PDFs and corrected it: exact accuracy figures, dataset sizes (1,787 / 2,127), the PRED(30) baseline (≈0.85 sentence level, 0.63 use-case level), and details of the GPT comparison. Fixed the author list for ref 2 (Tenekeci is first author; Küçük), filled in volume/article numbers, and added the SSMB dataset link. Completed refs 21 and 22. |
| 2026-10-17 | 0.5     | Recorded installation of SciTools Understand (Build 1265) and its VS Code extension (v1.1.6) in Sections 3.1 and 3.5; license still pending. |
| 2026-10-17 | 0.6     | Recorded the Python 3.12 environment (uv), library versions, and hardware in Section 3.5. |
