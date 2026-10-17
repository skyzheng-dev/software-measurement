# Research Context: Automated Software Size Measurement

> **Purpose of this file:** Give any future session (human or AI) the background needed to continue this project without re-explaining it.
> **Last updated:** 2026-10-17

---

## 1. About this project

- **Who:** An undergraduate researcher studying **software measurement**: how we work out the worth of software and how it can be measured.
- **Starting point:** The researcher was given an existing body of work (three papers from one research group) that looks at **automating software size measurement with language models**. The goal is to **build on that work**.
- **Status:** Early stage. So far the prior work has been understood and summarized (below). No new experiments, code, or datasets have been produced in this repo yet.
- **Caveat:** Everything in Section 3 comes from a **summary** of the papers, not from the full texts. Exact numbers, author names, and venues should be checked against the original PDFs before they are cited. (Add the PDFs or full citations to this repo when available. See Section 7.)

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
- **Method:** Built **SE-BERT** (English) and **SE-BERTurk** (Turkish) by further pre-training on large software-related corpora. Fine-tuned them on **one real company's requirements dataset**, labeled with COSMIC and MicroM.
- **Result:** Domain adaptation helps, most of all for Turkish. **SE-BERTurk scored about 69% exact-match accuracy vs. 65.7% for plain BERTurk.**
- **Limitation:** Proof of concept on a single organization's data.

### Stage 2: Measuring size from source code (Automated Software Engineering paper)
- **Question:** Can size be measured from **code** when there are no written requirements (common in agile teams)?
- **Method:** **CodeBERT** on **Python functions from CodeSearchNet**. About **1,800 to 2,100 functions** were labeled by hand with COSMIC and MicroM values.
- **Results:**
  - Up to **91% per-movement accuracy**.
  - Aggregated whole-function exact accuracy was lower: **~49% (COSMIC)** and **~44% (MicroM)**.
- **Methodological contribution:** Compared with the group's earlier, rougher attempt, this one used **fully manual, expert-verified labels** and allowed **multiple data movements per function**. That is more realistic and harder.
- **Limitations:** Described as exploratory and preliminary. Python only, open-source only, not tested on industrial codebases.

### Stage 3: Real industrial deployment (Journal of Systems & Software paper). The most important stage.
- **Question:** Do these models hold up in real companies?
- **Data:** Real requirement documents from **two organizations**: an industrial automation firm and a large tech/aviation company.
- **Models:** BERT and SE-BERT, compared against **GPT-4o, GPT-o3, and GPT-o4-mini-high (zero-shot)**.
- **Three scenarios:**
  1. **Generic model:** trained on a mix of requirements from **26 open-source projects**.
  2. **External evaluation:** the generic model applied unchanged to a new company's requirements.
  3. **Internal evaluation:** a model trained on **one company's own requirements**.
- **Results:**
  - **Generic models fail in the real world.** In external evaluation, PRED(30) fell **below 20%** in some cases, against about **85%** in controlled lab settings.
  - **Organization-specific training restores accuracy.** MMRE improved by **up to 65% (0.53 to 0.18)** when moving from generic to organization-specific training.
  - **Fine-tuned BERT models beat zero-shot GPT models by about 3x in accuracy.** For this structured task, a small fine-tuned model still wins over large general LLMs.

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

## 7. To add to this repo (TODO)

- [ ] Full citations (authors, year, venue, DOI) for all three papers
- [ ] PDFs or notes from reading the full texts (check the numbers in Section 3)
- [ ] Links to the group's public GitHub datasets/code and the AI-Estimator tool
- [ ] The chosen research question and plan, once decided
- [ ] Advisor guidance, deadlines, and deliverables
