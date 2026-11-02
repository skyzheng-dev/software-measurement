# [Working Title] Toward Generalizable Automated Software Size Measurement with Language Models

**Author:** Sky Zheng, Undergraduate Researcher
**Advisor:** Dr. Ekincan Ufuktepe
**Institution:** University of Missouri, Columbia
**Draft version:** 0.12 · **Last updated:** 2026-11-01

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

As a first exploratory step toward these goals, this work examines whether COSMIC functional size and Chidamber and Kemerer (CK) object-oriented metrics can be computed together within one toolchain (Section 2.4). The hypothesis is that structural code metrics, which do not depend on an organization's writing style, may serve as complementary signals for size models that must generalize across organizations.

**Selected problem (2026-11-01, provisional pending advisor confirmation):** The code-based model of prior work [2] reads a function only as a token sequence. It is least accurate on Entry (67.0%) and Exit (73.1%), the movements that cross the boundary between the software and its users, and it was evaluated only on random splits of a single pooled dataset. This project asks whether explicit structural information about the code, namely program dependence graphs (PDGs) extracted with Joern and static metrics computed with SciTools Understand, improves CodeBERT's COSMIC size estimates, and whether any improvement persists when the model is tested on projects it has not seen during training (G1).

### 1.3 Research Questions

Provisional (2026-11-01), pending advisor confirmation:

- **RQ1:** Does augmenting CodeBERT with structural features (PDG-derived features from Joern and static metrics from Understand) improve exact-match accuracy, MMRE, and PRED(30) for COSMIC Entry, Exit, Read, Write, and total CFP on Python functions, compared with CodeBERT on code text alone?
- **RQ2:** Does any such improvement persist, or grow, under a project-held-out evaluation in which test functions come from repositories not seen during training, compared with the random split used in prior work [2]?
- **RQ3:** Which structural features contribute most to each data-movement type? [TBD: confirm whether RQ3 is in scope.]

_Other candidate directions are listed in `RESEARCH_CONTEXT.md` Section 6._

### 1.4 Contributions

Planned (provisional):

- A comparison of text-only and structure-augmented CodeBERT models for COSMIC measurement from Python code, using the publicly released labeled dataset of [2].
- A project-held-out evaluation of code-based COSMIC measurement, which prior work has not reported.
- A reproducible pipeline that extracts per-function PDG features (Joern) and static metrics (Understand) from Python code.
- [TBD]

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

Existing work leaves open several questions. This paper targets two of them (2026-11-01, provisional): (a) code-based COSMIC models [2] use code only as text and have not been combined with explicit structural program representations, and (b) code-based models have been evaluated only on random splits, so their accuracy on code from unseen projects is unknown. This second gap is the code-side counterpart of the cross-organization failure observed for requirements in [3]. Other open questions (the amount of organizational data needed, cross-language measurement, few-shot LLM baselines, joint prediction of E/X/R/W, a shared benchmark) are left for future work. Section 2.4 adds a further gap: **no tool combines functional size (COSMIC) with structural metrics (CK)**, and code-based COSMIC automation is still language-specific and mostly limited to Java and C.

---

## 3. Methodology

### 3.1 Research Design

**Decision (2026-10-17):** Python is the first target language. This allows direct comparison with the prior code-based study [2] and reuse of its manually labeled CodeSearchNet functions. It also fills the gap that no open-source CK tool covers Python (Section 2.4.1). Java is a likely second language. The planned toolchain is SciTools Understand (CK metrics through `und metrics` and the Python API). Understand (Build 1265, macOS arm64) was installed on 2026-10-17, along with the Understand for VS Code extension (v1.1.6); the `und`, `userver`, and `upython` command-line tools are available. A license was activated on 2026-11-01 (valid until 2027-10-26); a test run of `und metrics` on a sample Python file produced both file-level and function-level metrics (e.g., line counts and cyclomatic complexity per function). Joern 4.0.665 [23] was installed on 2026-10-25 to obtain per-method program dependence graphs (PDGs) from source code; its Python frontend (`pysrc2cpg`) was verified on a sample function, producing data- and control-dependence edges together with parameter, call, and return nodes that are candidate signals for COSMIC Entry, Read, Write, and Exit movements. **Decision (2026-11-01, provisional pending advisor confirmation):** PDG-derived features and Understand metrics will be used as model inputs alongside CodeBERT (strategy 3 in Section 2.4.3), addressing RQ1 to RQ3 (Section 1.3). The planned design is: (i) reproduce the text-only CodeBERT baseline of [2] on its released data; (ii) extract per-function structural features; (iii) compare text-only and structure-augmented models under a random split and a project-held-out split. The baseline follows the protocol of [2] (5-fold cross-validation, 5 epochs per fold, as implemented in [24]). To isolate the effect of the structural features, both the text-only and the structure-augmented models receive the same version of the code text; the restored source (Section 3.2) is used for feature extraction. [TBD: feature set, fusion architecture, split procedure]

### 3.2 Datasets

**Primary dataset (identified 2026-11-01):** the COSMIC-labeled Python functions of [2], released by the authors in the public `CodeSizeBERT` repository under the MIT license [24] as `data/code_cosmic.csv`. It contains 1,787 functions with columns `code`, `docstring`, `entry`, `read`, `write`, `exit`, and `cfp`. A MicroM-labeled companion file (`data/code_microm.csv`) is also included. The repository's `stats/acc.csv` reports exact-match accuracies (Entry 0.6704, Read 0.9138, Write 0.8763, Exit 0.7314, CFP 0.4924) that match the figures in [2], which supports that this is the dataset used there. No author contact is needed to obtain it.

Label distribution (computed from `code_cosmic.csv`): mean Entry 0.98, Read 0.13, Write 0.24, Exit 0.89, CFP 2.24 per function. CFP ranges from 0 to 7, with a median of 2. There are no duplicate `code` entries.

Two properties of the released data affect this project's design:

1. **Indentation is not preserved.** In almost all functions (1,778 of 1,787), every line after the signature has the same indentation, so block structure is lost. Only 343 of 1,787 functions parse as valid Python with `ast.parse`. Because Joern and Understand both need syntactically valid code, the original source must be recovered, for example by matching each function to its CodeSearchNet [7] record, which also gives the original formatting.
2. **No project identifier is included.** The project-held-out split (RQ2) needs each function's source repository. CodeSearchNet records include the repository name and file path, so the matching in (1) would also supply this.

**Data repair (2026-11-01).** Each labeled function was matched back to its CodeSearchNet [7] record (Hugging Face `code-search-net/code_search_net`, revision `bd0cf26`, 457,461 Python functions across the train, validation, and test partitions). The pipeline is in `scripts/01_download.py` (pinned downloads), `scripts/02_match_codesearchnet.py` (matching), and `scripts/03_report_repair.py` (summary table and figures in `figures/data_repair/`). Matching uses the code with all whitespace removed as a key. On the CodeSearchNet side the key is built from the code tokens (which exclude the docstring) with comment tokens dropped, because the released code has no comments. If no key matches exactly, the most similar CodeSearchNet function with the same signature (or, failing that, the same bare name) is taken, with similarity computed after removing triple-quoted strings from both sides. A function is kept (*usable*) when the match is exact, or fuzzy with similarity ≥ 0.80, and the restored source parses as Python 3.

| | COSMIC | MicroM |
|---|---|---|
| Labeled functions | 1,787 | 2,126 |
| Exact match | 1,674 | 1,959 |
| Fuzzy match | 113 | 167 |
| No match | 0 | 0 |
| Parses as Python 3, as released | 343 (19%) | 2,069 (97%) |
| Parses as Python 3, restored | 1,767 (99%) | 2,108 (99%) |
| **Usable** | **1,766 (98.8%)** | **2,108 (99.2%)** |
| Distinct repositories (usable) | 950 | 1,373 |
| Largest number of functions from one repository | 66 | 48 |

Source: `figures/data_repair/summary.csv`. Figures: `figures/data_repair/fig1_match_outcome.png` (match outcome), `fig2_valid_python.png` (valid Python before and after), `fig3_cosmic_labels.png` (COSMIC label distribution in the usable set), and `fig4_functions_per_repo.png` (functions per repository).

Of the 21 excluded COSMIC functions, 20 are matched but do not parse as Python 3; in 19 of them the restored source shows Python 2 syntax (e.g., `print` statements, `except X, e`). The remaining one (`run_instances`, similarity 0.04) was checked by hand: the match is correct, but the labeled copy kept most of a 27,000-character docstring and the function body is only `pass`. All fuzzy matches with similarity below 0.90 were inspected; their differences were single-quoted docstrings or garbled non-ASCII text, not differing code.

The repair also revealed how the released text was preprocessed, which matters for interpreting the baseline of [2]:

- **All triple-quoted strings were removed, not only docstrings.** Multi-line string literals in the function body, including embedded SQL queries, are missing (e.g., `query = """SELECT ..."""` became `query =`). Such strings can carry evidence for Read and Write movements that the text-only model never saw.
- **Comment removal truncated some strings.** Text after a `#` was dropped even inside string literals (e.g., a character set ending `...!@#$%^&*` became `...!@`).
- **Only the COSMIC file had its indentation flattened;** the MicroM file keeps it (97% parse as released).
- The released MicroM file has 2,126 functions, one fewer than the 2,127 reported in [2].
- Most repositories contribute one labeled function (638 of 950 for COSMIC; Figure `fig4`), so a project-held-out split is feasible, although a few repositories (up to 66 functions) must be kept within a single fold.

[TBD: train/validation/test splits.] An earlier repository by the same author, `codebert-ssm` [25], contains CodeSearchNet-derived files (`codesearchnet_manual.csv`, `codesearchnet_auto.csv`) that appear to belong to the earlier study [21]; it has not been examined in detail.

### 3.3 Models and Baselines

**Text-only CodeBERT baseline (reproduction of [2]).** `scripts/04_baseline_codebert.py` ports the authors' `cross_pred.py` [24] and keeps its protocol: `microsoft/codebert-base` [6] with a single-output regression head and MSE loss, one model per movement type (Entry, Exit, Read, Write), AdamW (learning rate 2×10⁻⁵, no weight decay, no learning-rate schedule), batch size 32, maximum input length 512 tokens, 5 epochs, and seed 42. The input is the released `code` text. Evaluation is 5-fold cross-validation over the authors' shuffled file, split in order into five contiguous folds, with a fresh model trained for each fold. For each fold, the epoch with the lowest MSE on the test fold supplies the predictions. Predictions are rounded to integers before scoring, and total CFP is the sum of the four rounded movement predictions (`scripts/05_report_baseline.py`, following the authors' `sum_preds.py` and `calculate_metrics.py`).

The port differs from the original only in ways that do not change the model's computation: it runs on Apple MPS rather than CUDA; each batch of 32 is accumulated from four micro-batches of 8 to fit in 16 GB of memory; each micro-batch is padded to its longest input (at most 512 tokens) rather than always to 512, with padding masked as before; and seeds are reset per fold (42 + fold index) so an interrupted run can resume. Exact numerical agreement with [2] is not expected, because GPU kernels and random-number streams differ across hardware.

The upstream protocol selects each fold's epoch by its MSE on that same test fold, so test data influence model selection and the reported accuracy is optimistically biased. To measure this bias, the predictions of every epoch are stored, and results are also reported for a rule fixed in advance (always the last epoch, *epoch5*).

The baseline is run on two sets: *released* (all 1,787 functions, the reproduction) and *usable* (the 1,766 functions whose source could be restored, Section 3.2), which will be the evaluation set for the structure-augmented models.

[TBD: structure-augmented models.]

### 3.4 Training and Experimental Setup

[TBD: hyperparameters, hardware, random seeds.] Software versions: SciTools Understand Build 1265; Joern 4.0.665 on OpenJDK 21.0.13 (Homebrew); Matplotlib 3.11.2 for figures; the CodeBERT checkpoint is `microsoft/codebert-base` from the Hugging Face Hub; Understand for VS Code extension v1.1.6. Python 3.12.12 environment managed with uv (dependencies pinned in `pyproject.toml` and `uv.lock`): PyTorch 2.14.1 (Apple Metal/MPS backend), Transformers 5.20.1, Datasets 5.1.0, scikit-learn 1.9.1, pandas 3.0.6, NumPy 2.5.4, Radon 6.0.1, and Lizard 1.24.1. Hardware: Apple M3, 16 GB RAM. [TBD: remaining software versions]

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

- **Internal validity:** [TBD] Restoring the original formatting of the released functions (Section 3.2) could introduce mismatches between a label and the code it was assigned to. 94% of COSMIC matches are exact; the 113 fuzzy matches were accepted at similarity ≥ 0.80 and the weakest were inspected by hand, but not every fuzzy match was checked individually. Excluding Python 2 functions (Section 3.2) slightly changes the dataset relative to [2], so baseline figures are compared on both the full released set and the usable subset.
- **External validity:** [TBD] The project-held-out split uses open-source repositories as a stand-in for organizations. Variation between open-source projects may be smaller or different in kind than variation between companies, so results for unseen projects may not transfer to unseen organizations (G1).
- **Construct validity:** [TBD]
- **Conclusion validity:** [TBD] The baseline protocol of [2] selects each fold's epoch using the test fold (Section 3.3), which biases reported accuracy upward; results under a fixed epoch are reported alongside it.

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
23. F. Yamaguchi, N. Golde, D. Arp, K. Rieck, "Modeling and Discovering Vulnerabilities with Code Property Graphs," _IEEE Symposium on Security and Privacy_, 2014. Tool: Joern, https://github.com/joernio/joern
24. S. Tenekeci, CodeSizeBERT: Automating Software Size Measurement from Code Using Language Models (code and data for [2]), MIT license. https://github.com/smtnkc/CodeSizeBERT (accessed 2026-11-01)
25. S. Tenekeci, codebert-ssm: CodeBERT for CFP size measurement. https://github.com/smtnkc/codebert-ssm (accessed 2026-11-01)

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
| 2026-10-25 | 0.7     | Recorded installation of Joern 4.0.665 (with OpenJDK 21) for PDG extraction in Sections 3.1 and 3.4; added ref 23. |
| 2026-11-01 | 0.8     | Recorded activation of the SciTools Understand license and a successful test metrics run in Section 3.1. |
| 2026-11-01 | 0.9     | Selected the provisional research problem and RQ1 to RQ3 (structure-augmented CodeBERT; project-held-out evaluation) in Sections 1.2 to 1.4 and 2.5. Recorded the public CodeSizeBERT dataset of [2] and its formatting and project-ID limitations in Sections 3.1, 3.2, and 6. Added refs 24 and 25. |
| 2026-11-01 | 0.10    | Specified the baseline protocol and the same-code-text control for the model comparison (Section 3.1); added the projects-as-proxy-for-organizations limitation (Section 6). |
| 2026-11-01 | 0.11    | Recorded the data repair (matching to CodeSearchNet): procedure, match and usable counts, four figures in `figures/data_repair/`, and preprocessing artifacts found in the released data (Section 3.2); updated Sections 3.4 and 6. |
| 2026-11-01 | 0.12    | Described the text-only CodeBERT baseline reproduction (protocol, deviations, the test-fold epoch-selection issue) in Section 3.3; added notes to Sections 3.4 and 6. |
