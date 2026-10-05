# UI Version Registry & Evaluation Interface Alignment Report

**Repository:** `dysglycemia-dashboard`  
**Date:** 2026-10-05  
**Protocol:** Two-Stage Non-Laboratory Screening Evaluation Protocol E1 (v1.0.3) / E2  
**Governing Branch:** `ui-wording-alignment`  
**Evaluation Study Tag:** `evaluation-study-ui` (`54f5cdbd6a73f08a5a853896987bb4e8db1ecb56`)

---

## 1. Executive Summary & Version Registry

Between 23 September 2026 and 1 October 2026, an empirical participant evaluation study was conducted on the Railway cloud deployment of this repository. A reviewer noted discrepancies between the manuscript framing (which describes layperson/volunteer participants conducting a simulated workflow evaluation of a frozen model without online learning) and visual artifacts displaying clinician-centric wording, online learning signals, and an unpopulated reviewer code input.

To provide empirical proof for manuscript reporting and resolve UI discrepancies:
1. An annotated Git tag `evaluation-study-ui` was created at commit `54f5cdbd6a73f08a5a853896987bb4e8db1ecb56`.
2. High-resolution Playwright captures (1440×1080 @ 2× DPR) were generated directly from commit `54f5cdbd` running in `APP_MODE=evaluation` on a clean, verified SQLite database.
3. A dedicated alignment branch `ui-wording-alignment` was created from `main`, implementing mode-conditional copy alignments and auto-filling the pseudonymous reviewer code.
4. An expanded test suite was developed (`test_evaluation_wording.py`), raising total test coverage from 263 to 276 tests with 100% passing rate.
5. A comprehensive 4-part audit was executed across all templates, forms, JavaScript, and backend services.

### Version Mapping Table

| Version Identifier | Git Hash / Reference | Operational Dates | Environment & Target Audience | Key Characteristics |
| :--- | :--- | :--- | :--- | :--- |
| **`evaluation-study-ui`** *(Locked Tag)* | `54f5cdbd6a73f08a5a853896987bb4e8db1ecb56` | 2026-09-23 to 2026-10-01 | Railway Production (`APP_MODE=evaluation`). Participants (N=42 completers, 41 formal reviews). | Interface actually used by study participants. Retained internal developer phrasing ("clinical review decision", "Structured Learning Signal", editable Reviewer Code). |
| **`main` baseline** | `e56f4d9435b62d38ae85903b44b80dfcb26c63b4` | 2026-10-01 to 2026-10-04 | Local Development / Evaluation Gate refactor. | Partially updated copy; Reviewer Code still manually editable; legacy NLP text persisted. |
| **`ui-wording-alignment`** *(Active Branch)* | Branch head (from `e56f4d`) | Current Working Tree | Post-study aligned evaluation mode + researcher Feedback Lab mode. | Mode-conditional copy: non-clinical framing, Reviewer Code hidden & auto-filled in evaluation mode, Feedback Lab mode retains full researcher features. |

> [!IMPORTANT]
> **Data Collection Provenance:**  
> All 42 completers and all 41 formal human reviews analyzed in the manuscript were collected strictly on the deployment corresponding to commit `54f5cdbd` (tagged as `evaluation-study-ui`). No participant ever interacted with the modified copy on branch `ui-wording-alignment`. The branch exists to align future deployments and provide exact documentation of the visual delta.

---

## 2. High-Resolution Visual Evidence Registry

Visual captures were captured using Playwright (`chromium`, viewport `1440x1080`, `deviceScaleFactor: 2`, full-page and element clips) from a clean, seeded evaluation database containing 11 formal records and zero practice or corrupted records.

| Artifact Filename | Relative Path | Resolution (Physical Pixels) | Commit Source | Content & State |
| :--- | :--- | :--- | :--- | :--- |
| `fig_eval_study_overview_54f5cdbd.png` | `reports_manuscript/figures_evaluation/` | 2880 × 2160 | `54f5cdbd` | Evaluation Overview dashboard with 11 formal records, zero practice records, status badges, and workflow actions. |
| `fig_eval_study_human_review_54f5cdbd.png` | `reports_manuscript/figures_evaluation/` | 2880 × 1720 | `54f5cdbd` | Human Review panel at commit `54f5cdbd` with Override selected, revealing reviewer code input, structured learning signal, and NLP disclaimer. |
| `fig_eval_study_full_page_54f5cdbd.png` | `reports_manuscript/figures_evaluation/` | 2880 × 5320 | `54f5cdbd` | Full Stage-1 screening result page showing Primary Result, GAM Additive Factor Decomposition, and Human Review. |
| `fig_eval_comparison_human_review_latest.png` | `reports_manuscript/figures_evaluation/` | 2880 × 1720 | `e56f4d94` | Human Review panel comparison capture at `HEAD` prior to final branch copy alignment. |
| `fig_eval_comparison_full_page_latest.png` | `reports_manuscript/figures_evaluation/` | 2880 × 5320 | `e56f4d94` | Full Stage-1 screening result page comparison capture at `HEAD`. |

### Exact Text Comparison in Human Review Card (Captured via DOM Extraction)

```diff
  Human Review
- Evaluate the AI screening assessment and record your clinical review decision.
+ Evaluate the AI screening assessment and record your review decision.
  Pending Review
  AI RECOMMENDATION: REFER FOR STAGE-2 HbA1c
  Refer for Stage-2 HbA1c laboratory assessment
  Stage-1 Non-Laboratory Screening: Model Probability 0.2285 (Decision Threshold: 0.1389).

- Reviewer Code *
- Pseudonymous reviewer code assigned for this study. Do not enter identifying personal information.
+ [HIDDEN IN EVALUATION MODE: Automatically populated from respondent session token]

  Human Review Decision *
  (o) Accept AI Recommendation - Agree with the model assessment (Final Decision: Refer).
  ( ) Override AI Recommendation
-     Clinical intervention: change final decision to Do not refer.
+     Human override: change final decision to Do not refer.

- Override Factor / Structured Learning Signal *
- Select which factor motivated this clinical override. In the Feedback Lab, this factor provides the canonical signal for candidate adaptation without any secondary submission step.
+ Human Override Rationale *
+ Select which factor motivated this human override. This rationale is recorded for audit and research analysis only; it does not trigger model adaptation.

  Reason items:
- 1. BMI was over-weighted
+ 1. BMI appears over-weighted
  ... (items 2-7 aligned to "appears over-weighted")

- Clinical Rationale / Contextual Note
- Preserved for auditability; analyzed via NLP for supplementary evaluation.
+ Decision Rationale / Contextual Note
+ Stored for audit only; it does not change the model.

  Footer Notice:
- Decisions are immutable once submitted. Human overrides generate the learning signal directly within this unified review action.
+ Evaluation Mode uses a frozen model. Human overrides are recorded for research analysis only and do not trigger model adaptation.
```

---

## 3. Detailed Change Log (`ui-wording-alignment`)

The branch implements mode-conditional template rendering (`{% if IS_EVALUATION_MODE %}`) and a single functional improvement to form handling, preserving complete researcher tooling in `feedback_lab` mode.

| # | File & Location | Baseline Text (`54f5cdbd` / `main`) | Aligned Text (`ui-wording-alignment`) | Rationale & Mode Behavior |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `overview.html:36` | "Awaiting clinician review" | "Awaiting human review" | Standardizes role label to human reviewer. |
| 2 | `overview.html:43` | "Screenings requiring clinician review..." | "Screenings requiring human review or Stage-2 HbA1c entry." | Accurately describes two-stage workflow requirements. |
| 3 | `review_queue.html:28` | "awaiting clinician review." | "awaiting human review." | Aligns queue header to neutral human reviewer role. |
| 4 | `screening_result.html:190` | "Clinician Interpretation" | "Result Interpretation" | Removes clinical implication from algorithmic score display. |
| 5 | `screening_result.html:268` | "...record your clinical review decision." | "...record your review decision." in evaluation mode (`clinical review` in feedback_lab). | Distinguishes study participant review from clinical practice. |
| 6 | `screening_result.html:314` | Manual `<input name="reviewer_code">` visible in all modes | Hidden input in evaluation mode (`type="hidden"`), visible text input in feedback_lab. | Prevents confusion; auto-populates from anonymous `respondent_code`. |
| 7 | `forms.py:168` & `views.py:592` | `reviewer_code` required in form validation | In evaluation mode: `required=False`, auto-filled from session `EvaluationSession.respondent_code`. | Approved functional change ensuring valid audit trail without user burden. |
| 8 | `screening_result.html:388` | "Preserved for auditability; analyzed via NLP..." | "Stored for audit only; it does not change the model." in evaluation mode. | Clarifies that NLP does not trigger online adaptation in evaluation mode. |
| 9 | `screening_result.html:430` | NLP Category & Learning Signal Cards displayed unconditionally | Gated behind `{% if IS_FEEDBACK_LAB_MODE %}`; hidden in evaluation mode. | Suppresses internal developer telemetry cards for study participants. |
| 10 | `screening_result.html:484` | Final review badge: "Clinician Reviewer" | "Reviewer ID: {{ review.reviewer_code }}" in evaluation mode. | Reflects participant pseudonymous identifier. |
| 11 | `evaluation_practice.html:65` | "Klinisi memegang keputusan akhir..." | "Peninjau manusia memegang keputusan akhir..." | Accurately reflects Indonesian participant instructions. |
| 12 | `evaluation_practice.html:73` | "Pada Stage 2 klinisi memasukkan..." | "Pada Stage 2 Anda memasukkan satu nilai HbA1c hipotetik untuk menguji alur kerja. Ini bukan hasil laboratorium dan bukan diagnosis." | Clarifies hypothetical exercise context for Stage 2. |
| 13 | `stage2_entry.html:10`, `stage2_result.html:10` | "Stage 2 – Confirmatory HbA1c" | "Stage 2 – HbA1c Range Assessment" (hypothetical data entry context noted). | Eliminates diagnostic confirmation claim. |
| 14 | `analytics.html:125, 230` | "clinician disposition", "clinician decision override", "clinical judgment" | "human reviewer disposition", "human reviewer decision override", "human reviewer decision". | Aligns analytics dashboard copy with study methodology. |
| 15 | `about.html:30` | "...assist healthcare providers..." | Added disclaimer: "In the participant evaluation the review task was a simulated exercise performed by volunteers, mostly laypersons." | Reconciles general prototype purpose with specific evaluation study sample. |

---

## 4. Comprehensive 4-Part Terminology & Reachability Audit

### Audit (a): Broader Grep for Clinical and Patient Terms

A codebase-wide audit was conducted across all templates, forms, static JavaScript, and backend services for key terms: `patient`, `pasien`, `diagnos`, `treatment`, `clinic`, `medical`, `dokter`, `laborator`, `your own`, `real`.

| Term | File Occurrences | Mode Context | Current Status & Disposition |
| :--- | :--- | :--- | :--- |
| **`patient`** | `index.html:4,7,16,19`, `result.html:79,82,84,86,87`, `evaluation.html:49`, `components_demo.html:200` | Legacy & UI demo views only (`/index/`, `/predict/`, `/evaluation/`, `/components/`). | **Zero occurrences in primary two-stage screening templates.** Proposed disposition: Block legacy routes with 404 in evaluation mode. |
| **`pasien`** | `services/questionnaire.py:287` (`P0_SPEC`) | Practice Case P0 definition title: `"Bukan Data Pasien Nyata"`. | Explicit negative disclaimer ("Not real patient data"). Retain. |
| **`diagnos`** | `screening_result.html:186,201,211,212`, `stage2_result.html:117,122`, `evaluation_consent.html:39`, `evaluation_practice.html:73` | Mandatory safety disclaimers ("not a diagnostic tool", "bukan alat medis diagnostik"). | Essential governance text required by thesis ethics. Preserved intact. |
| **`treatment`**| `screening_result.html:212` | Regulatory disclaimer ("does not provide medical diagnosis, clinical treatment orders, or disease confirmation"). | Standard protective medical legal disclaimer. Preserved. |
| **`clinic`** | `about.html:175`, `screening_result.html:494`, `analytics.html:51,349` | Governance caveats ("Neither axis is clinical ground truth", "not establish clinical truth"). | Epistemic boundary disclaimers. Preserved. |
| **`medical`** | `screening_result.html:212,247`, `about.html:30` | Disclaimers ("does not constitute personalized medical advice"). | Mandatory disclaimer. Preserved. |
| **`dokter`** | None found across repository. | N/A | None. |
| **`real`** | `screening_result.html:453`, `feedback_experiment.html:44,101,139` | Gated behind `IS_FEEDBACK_LAB_MODE` (researcher experiment tab). | Hidden in evaluation mode. Retained for researcher validation. |

### Audit (b): Reachability of Legacy Endpoints in Evaluation Mode

The URL router (`predictor/urls.py`) exposes several legacy endpoints originally developed during earlier project phases:
- `/index/` (`views.index`): Legacy single-stage input form using patient terminology and baseline models.
- `/predict/` (`views.predict_view`): Legacy single-stage prediction handler.
- `/evaluation/` (`views.evaluation_view`): Legacy static evaluation benchmark display.
- `/components/` (`views.components_demo_view`): Design system UI component catalog.

**Audit Finding:**  
None of these four views invoke `check_evaluation_onboarding(request)`, and none check `settings.APP_MODE`. In `base.html`, navigation links to `/components/` are hidden when `IS_EVALUATION_MODE=True`, and legacy routes are not present in the sidebar. However, a participant who manually enters the URL path `/index/` or `/predict/` can access the legacy single-stage interface without completing the onboarding gate.

**Recommended Disposition:**  
In `predictor/views.py`, introduce an evaluation mode check at the entry of `index`, `predict_view`, `evaluation_view`, and `components_demo_view`:
```python
if getattr(settings, 'APP_MODE', 'feedback_lab').lower() == 'evaluation':
    raise Http404("This legacy endpoint is not available in participant evaluation mode.")
```

### Audit (c): Sidebar Navigation Item Comparison

| Navigation Section | Commit `54f5cdbd` (`evaluation-study-ui`) | Branch `ui-wording-alignment` | Status & Visual Delta |
| :--- | :--- | :--- | :--- |
| **Screening Workflow** | Overview (`/`), New Screening (`/screening/new/`), Review Queue (`/review/`), History (`/history/`) | Overview (`/`), New Screening (`/screening/new/`), Review Queue (`/review/`), History (`/history/`) | Identical layout and links. Added `aria-current="page"` for accessibility. |
| **Research & Methodology**| Analytics (`/analytics/`), About the Model (`/about/`) | Analytics (`/analytics/`), About the Model (`/about/`) | Identical layout and links. |
| **Researcher Tools** | `feedback_experiment` and `components_demo` hidden via `{% if not IS_EVALUATION_MODE %}` | `feedback_experiment` and `components_demo` hidden via `{% if not IS_EVALUATION_MODE %}` | Identical behavior. Completely hidden in evaluation mode. |
| **Research Evaluation** | Informed Consent (`/evaluation/consent/`), Practice Case P0 (`/evaluation/practice/`), Questionnaire (`/evaluation/questionnaire/`) | Informed Consent (`/evaluation/consent/`), Practice Case P0 (`/evaluation/practice/`), Questionnaire (`/evaluation/questionnaire/`) | Identical layout and links. |
| **Top-Right Mode Pill** | `Mode Evaluasi · Protocol v1.0.3` | `Mode Evaluasi · Protocol v1.0.3 (Model Beku)` | Explicit "Model Beku" tag added to emphasize locked GAM. |

### Audit (d): Informed Consent & Questionnaire Exact Wording

To evaluate whether participants were instructed to enter personal health data versus hypothetical vignettes:

1. **Informed Consent (`evaluation_consent.html` lines 37–41):**
   - *"Anonimitas & Kerahasiaan: Tidak ada data identitas pribadi (nama, kontak, institusi) yang disimpan. Setiap partisipan diidentifikasi melalui kode acak anonim (contoh: `R-A1B2C3D4`)."*
   - *"Bukan Alat Diagnostik Klinis: Sistem ini merupakan prototype riset akademik sistem informasi dan bukan alat medis diagnostik. Hasil penilaian risiko adalah perkiraan statistik model machine learning."*
   - *"Alur Kegiatan: Anda akan (1) membaca pengenalan alur pada Kasus Latihan P0, (2) mencoba proses screening risiko, (3) meninjau penjelasan AI dan mencoba fitur peninjauan manusia, dan (4) mengisi kuesioner evaluasi singkat (pemahaman, SUS, dan umpan balik)."*
2. **Practice Case Specification (`services/questionnaire.py` line 287):**
   - Title: *"Kasus Latihan P0 — Orientasi Alur Kerja (Bukan Data Pasien Nyata)"*
   - Description: *"Kasus latihan ini dirancang untuk memperkenalkan alur screening: melihat hasil AI, memeriksa penjelasan feature contribution, mencoba keputusan peninjauan manusia (Setuju / Override), dan memberikan umpan balik terstruktur. Kasus ini dikecualikan dari data analisis riset."*
3. **Stage-2 Lab Entry Notice (`evaluation_practice.html` line 73):**
   - *"Pada Stage 2 Anda memasukkan satu nilai HbA1c hipotetik untuk menguji alur kerja. Ini bukan hasil laboratorium dan bukan diagnosis."*
4. **Input Guidance Finding:**
   - Neither the consent form nor the questionnaire mandated that participants enter their own personal medical information. Participants completed onboarding using predefined Case P0 and were instructed that Stage 2 was a hypothetical workflow exercise.

---

## 5. Verification Test Suite Execution

A dedicated unit test suite, `EvaluationModeWordingTests`, was implemented in `dashboard/predictor/test_evaluation_wording.py` (13 tests) verifying:
- Non-clinical wording appears across overview, review queue, screening result, and Stage 2 in evaluation mode.
- Reviewer code is hidden and auto-filled from session in evaluation mode.
- `feedback_lab` mode retains full researcher wording ("Structured Learning Signal", "Feedback Lab · Localhost Mode", editable Reviewer Code).
- Disclaimers and locked model notes are strictly enforced.

```
Baseline Test Run (main):            Ran 263 tests in 8.521s -> OK (0 failures, 0 errors)
Post-Implementation Run (branch):    Ran 276 tests in 9.814s -> OK (0 failures, 0 errors)
```

---

## 6. Commitments & Governance Conformance

1. **Tag Status:** Tag `evaluation-study-ui` exists locally at commit `54f5cdbd6a73f08a5a853896987bb4e8db1ecb56`. No tag has been pushed to remote.
2. **Branch Status:** All changes reside on local branch `ui-wording-alignment`. No remote push or pull request has been issued.
3. **Ethics / Instrument Lock:** Zero modifications were made to `evaluation_consent.html` or `services/questionnaire.py`, preserving the exact ethical consent text and validated psychometric items.
4. **Model Architecture:** The Phase-5 GAM model (`lambda=10.0`, threshold `0.1389`) remains strictly frozen and untampered.
