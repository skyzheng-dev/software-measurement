# Research Context: Automated Software Size Measurement

> **Purpose of this file:** Give any future session (human or AI) the background needed to continue this project without re-explaining it.
> **Last updated:** 2026-10-17

---

## 1. About this project

- **Who:** An undergraduate researcher studying **software measurement**: how we work out the worth of software and how it can be measured.
- **Starting point:** The researcher was given an existing body of work (three papers from one research group) that looks at **automating software size measurement with language models**. The goal is to **build on that work**.
- **Status:** Early stage. The prior work has been summarized (below), and a tool survey of COSMIC and CK metrics is done (Section 7). No experiments, code, or datasets exist in this repo yet. **The user asked that nothing be implemented until they say so.**
- **Current goals (provisional, may change):**
  - **G1:** A size measurement tool that can be trained on data from many sources, not one company, and works as accurately as possible for *any* software firm.
  - **G2:** Go beyond Python (code) and English/Turkish (requirements) to other languages.
- **Formal write-up:** `PAPER.md` (living research paper; see the update rules in `CLAUDE.md`).
- **Sources:** The numbers in Section 3 were **checked against the full-text PDFs** on 2026-10-17. The PDFs are in `papers/`, which is gitignored because two of them are confidential or paywalled. **Never commit or publish them.**

---

## 2. Key concepts and glossary

| Term | Meaning |
|---|---|
| **Software size** | A measure of how much functionality a piece of software delivers. It is the base input for estimating **cost, effort, and schedule**. |
| **Functional Size Measurement (FSM)** | Measuring size from the functionality a user sees, not from lines of code. |
| **COSMIC** | A standardized FSM method (ISO/IEC 19761). It counts **data movements** of four kinds: **Entry (E)**, **Exit (X)**, **Read (R)**, **Write (W)**. Each movement is 1 COSMIC Function Point (CFP). |
| **MicroM** | A newer size metric created by the same research group. It is used alongside COSMIC as a label in their datasets. |
| **Data movement** | One unit of data crossing a boundary (user to software, software to storage, and so on). A single function or requirement can contain several. |
| **BERT** | A transformer language model. Here it is fine-tuned to output a size value instead of a human counting it. |
| **SE-BERT / SE-BERTurk** | The group's domain-adapted models: BERT (English) and BERTurk (Turkish) given extra pre-training on large software-engineering text corpora. |
| **CodeBERT** | A BERT variant pre-trained on both source code and natural language. |
| **CodeSearchNet** | A public corpus of open-source GitHub functions with docstrings. The Python subset was used in Stage 2. |
| **Domain adaptation** | Further pre-training a general model on text from a specific field before fine-tuning it. |
| **Fine-tuning** | Training a pre-trained model on a labeled, task-specific dataset. |
| **Zero-shot** | Asking a model to do a task with no task-specific training or examples. |
| **MMRE** | Mean Magnitude of Relative Error. **Lower is better.** |
| **PRED(30)** | The share of predictions within 30% of the actual value. **Higher is better.** |
| **Per-movement vs. aggregated accuracy** | Per-movement: is each E/X/R/W count right on its own? Aggregated: is the *total* size of the function exactly right? Aggregated is the harder test. |

---

## 3. Summary of the prior research (three stages)

**Overall goal of the group:** Measure software size **automatically**, with no need for trained human experts. Manual measurement is slow and expensive, and it needs certified specialists that most companies don't have.

**Core bet:** Use BERT-style models to read **requirements text** or **source code** and output a size number.

### Stage 1: Domain-adapted models on requirements (TUBITAK paper)
- **Question:** Does a domain-adapted model read requirements better than a general one?
- **Method:** Built **SE-BERT** (English) and **SE-BERTurk** (Turkish) by further pre-training on large software-engineering corpora (Stack Overflow, GitHub, Jira, project documentation). Fine-tuned them on a **proprietary, multilingual (Turkish + English), organization-specific requirements dataset**, labeled with COSMIC and MicroM by domain experts. The task is framed as **regression**.
- **Result:** Domain adaptation helps, most of all for Turkish. **SE-BERTurk: 65.7% → 69.3%** exact-match accuracy over BERTurk. **SE-BERT: 66.9% → 68.2%** over BERT. Both also beat the earlier domain-adapted baselines BERT_SE and RE-BERT.
- **Limitation:** The dataset comes from a limited number of organizations.
- **Also in this paper:** the AI-Estimator prototype (by Bilgi Grubu: https://www.bg.com.tr/wp/en/projects/#AI-ESTIMATOR).

### Stage 2: Measuring size from source code (Automated Software Engineering paper)
- **Question:** Can size be measured from **code** when there are no written requirements (common in agile teams)?
- **Method:** **CodeBERT** on **Python functions from CodeSearchNet**. Candidate functions were found by keyword filtering, then labeled by hand: **1,787 functions with COSMIC** and **2,127 with MicroM**.
- **Results (exact-match accuracy):**
  - COSMIC per movement: **Entry 67.0%, Read 91.4%, Write 87.6%, Exit 73.1%**. Total CFP: **49.2%** (NMAE 0.273).
  - MicroM per event type: **Interaction 80.2%, Communication 81.5%, Process 50.9%**. Total MicroM: **44.1%** (NMAE 0.29).
- **Data availability:** "provided within the manuscript". No GitHub link was found in the paper.
- **Methodological contribution:** Compared with the group's earlier, rougher attempt, this one used **fully manual, expert-verified labels** and allowed **multiple data movements per function**. That is more realistic and harder.
- **Limitations:** Described as exploratory and preliminary. Python only, open-source only, not tested on industrial codebases.

### Stage 3: Real industrial deployment (Journal of Systems & Software paper). The most important stage.
- **Question:** Do these models hold up in real companies?
- **Data:** Real requirement documents from **two organizations**, measured by experienced analysts:
  - **Case 1:** an industrial automation firm (25+ years, 100+ staff).
  - **Case 2:** a global tech company focused on aviation (2,500+ staff).
  - The heterogeneous dataset is public at **https://github.com/smtnkc/SSMB**.
- **Models:** BERT and SE-BERT, evaluated at both use-case level and sentence level.
- **GPT comparison:** GPT-4o, o3, and o4-mini-high were tested **zero-shot with COSMIC/MicroM background given in the prompt**, as a pre-evaluation on the heterogeneous use-case dataset (633 samples) only.
- **Three scenarios:**
  1. **Generic model:** trained on a mix of requirements from **26 open-source projects**.
  2. **External evaluation:** the generic model applied unchanged to a new company's requirements.
  3. **Internal evaluation:** a model trained on **one company's own requirements**.
- **Results:**
  - **Generic models fail in the real world.** In external evaluation, total-COSMIC PRED(30) was **0.1129 (Case 1)** and **0.1240 (Case 2)**, with MMRE above 0.50. The same generic models scored PRED(30) **≈0.85 at sentence level** (CFP 0.8591, MicroM 0.8478) and **≈0.63 at use-case level** when tested on data like their training data.
  - **Organization-specific training restores accuracy.** MMRE improved by **up to 65% (0.5268 → 0.1821)**. SE-BERT beat BERT by up to 7% on organization-specific data (0.1948 → 0.1821).
  - **Fine-tuned BERT models beat zero-shot GPT models by more than 3x.** CFP PRED(30) was 0.6382 for SE-BERT vs. 0.2164 for o4-mini-high, the best GPT model; GPT-4o scored 0.0964. For MicroM it was 0.6408 vs. 0.2104.
  - **Domain misalignment outweighs domain adaptation.** In external evaluation, SE-BERT showed no clear advantage over BERT.

### Summary table

| Stage | Question | Tool | Key takeaway |
|---|---|---|---|
| 1 | Can domain-adapted BERT measure size from requirements? | SE-BERT / SE-BERTurk | Yes. A modest gain over plain BERT, largest for Turkish. |
| 2 | Can we skip requirements and measure size from code? | CodeBERT | Yes, with "acceptable" accuracy. Promising but exploratory. |
| 3 | Does this hold up in real companies? | BERT, SE-BERT, GPT comparison | Only when the model is trained on that organization's own data. Generic models generalize poorly. |

---

## 4. The big-picture conclusion

- Automating size measurement is **technically feasible** (Stages 1 and 2).
- The sobering finding is that it is **not yet generalizable** (Stage 3). It becomes reliable only when tuned to a specific company's writing style and codebase.
- So the practical strategy is **"each company fine-tunes its own small model,"** not "one universal model for everyone."
- The key factor is **a modest amount of labeled data from the organization that will use the tool**, not a bigger or smarter architecture.

---

## 5. The group's stated future directions

1. **Practical tooling:** A prototype called **AI-Estimator** lets companies use the public pre-trained models or fine-tune their own on historical project data.
2. **Organization-specific fine-tuning** as the main lever for real-world accuracy.
3. **Wider scope:** More programming languages (beyond Python), more natural languages (beyond English and Turkish), more industries, and especially **safety-critical and embedded systems**, where current results may not hold.
4. **Multi-task learning:** Predict all size components (E/X/R/W) **jointly** rather than with separate models. Separate models ignore correlations, for example between Read and Write.
5. **Multi-modal learning:** Combine **code + text + diagrams (UML, BPMN)**.
6. **Public benchmarks:** There is no shared standard dataset, which makes fair comparison hard. The group has released its datasets and code on GitHub as a first step.

---

## 6. Open gaps that could become this project's contribution

These are candidate directions drawn from the limitations above. **None has been chosen yet.**

- **Stage 2 on another language:** Repeat the code-based approach on Java, C, JavaScript, and so on, or on non-open-source/industrial code.
- **How much organizational data is enough?** A learning-curve study: how many labeled requirements from a company are needed to close the generic-to-specific gap?
- **Few-shot or fine-tuned LLMs vs. BERT:** Stage 3 tested GPT models only zero-shot. Few-shot prompting, retrieval of similar labeled examples, or fine-tuning small open LLMs could change the result.
- **Joint (multi-task) prediction** of E/X/R/W compared with independent models.
- **Domain adaptation for transfer:** Can light adaptation (a small amount of unlabeled company text) recover accuracy without new labels?
- **Benchmark building:** Merge or standardize the public datasets into one shared benchmark with fixed splits and metrics.
- **Linking size to "worth":** Connect predicted size to effort, cost, or value estimates, which is the wider research interest.

---

## 7. Tool survey: COSMIC + CK metrics (2026-10-17)

Full details and citations are in `PAPER.md` Section 2.4.

- **No single tool, IDE, or plugin computes both COSMIC and CK.**
- **CK tools:** SciTools Understand (commercial, free educational license, 17+ languages, Python plugin API), Analizo (free; C/C++/Java/C#), CK by Aniche (free; Java source), CKJM-extended (free; Java bytecode). No good open-source CK tool for Python. Different tools compute the same metric differently.
- **COSMIC from code:** Only academic prototypes, mostly Java (COSMIC Solver at 77% agreement with manual counts, JavaCFP, CFP4J) and C (regex), plus Arduino and assembly. Nothing for Python, C#, or JS. ScopeMaster (commercial) works from requirements text, not code.
- **Ways to combine (none chosen yet):** (1) Understand plus a custom COSMIC plugin, (2) open-source CK tools joined with COSMIC labels or predictions, (3) CK metrics as extra features next to CodeBERT embeddings to test cross-organization generalization (G1), (4) CK distributions to describe how companies' codebases differ.
- **Main obstacle:** Unit mismatch. COSMIC counts per *functional process* (≈ an entry-point method); CK metrics are per *class*.

## 8. To add to this repo (TODO)

- [x] Full citations for all three papers (in `PAPER.md` References 1 to 3). The group is **Ünlü, Tenekeci, Demirörs et al.** (Izmir Institute of Technology).
  - TUBITAK: DOI 10.55730/1300-0632.4172 (open access)
  - ASE: DOI 10.1007/s10515-025-00571-z
  - JSS: DOI 10.1016/j.jss.2025.112638
- [x] All five PDFs are in `papers/` (gitignored), named `Year_FirstAuthor_Venue_Topic.pdf`. The number in brackets is the paper's number in the `PAPER.md` reference list:
  - `2024_Unlu_SEAA_...` = [22]
  - `2024_Tenekeci_IWSM_...` = [21]
  - `2026_Tenekeci_TJEECS_...` = [1] (Stage 1)
  - `2026_Tenekeci_ASE_...` = [2] (Stage 2)
  - `2026_Unlu_JSS_...` = [3] (Stage 3)

  The numbers in Section 3 are checked. Also there: IWSM 2024 (CodeBERT on Python + **C#**) and SEAA 2024 (BERT on user stories).
- [ ] Read IWSM 2024 in depth, since its C# dataset is relevant to G2.
- [x] Decision: **Python is the first language** (2026-10-17). Understand license still pending (user will apply later).
- [ ] Links to the group's public GitHub datasets/code and the AI-Estimator tool
- [ ] The chosen research question and plan, once decided
- [ ] Advisor guidance, deadlines, and deliverables
