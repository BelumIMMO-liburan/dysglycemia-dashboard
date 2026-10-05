# UI Version Registry & Evaluation Interface Alignment Report

**Repository:** `dysglycemia-dashboard`  
**Date:** 2026-10-05  
**Protocol:** Two-Stage Non-Laboratory Screening Evaluation Protocol E1 (v1.0.3) / E2  
**Governing Branch:** `ui-wording-alignment`  
**Evaluation Study Tag:** `evaluation-study-ui` (`54f5cdbd6a73f08a5a853896987bb4e8db1ecb56`)  
**Tagger Identity:** `Daymbroo <felikjavier123@gmail.com>` (1791139775 +0700)

---

## 1. Executive Summary & Version Registry

Between 23 September 2026 and 1 October 2026, an empirical participant evaluation study was conducted on the Railway cloud deployment of this repository. A reviewer noted discrepancies between the manuscript framing (which describes layperson/volunteer participants conducting a simulated workflow evaluation of a frozen model without online learning) and visual artifacts displaying clinician-centric wording, online learning signals, and an unpopulated reviewer code input.

To provide empirical proof for manuscript reporting and resolve UI discrepancies:
1. An annotated Git tag `evaluation-study-ui` was created at commit `54f5cdbd6a73f08a5a853896987bb4e8db1ecb56` (signed by `Daymbroo <felikjavier123@gmail.com>`).
2. High-resolution Playwright captures (1440×1080 @ 2× DPR) were generated directly from commit `54f5cdbd` running in `APP_MODE=evaluation` on a clean, verified SQLite database.
3. A dedicated alignment branch `ui-wording-alignment` was created from `main`, implementing mode-conditional copy alignments, gating researcher feedback mechanisms behind `feedback_lab` mode, and auto-filling the pseudonymous reviewer code.
4. An expanded test suite was developed (`test_evaluation_wording.py`), raising total test coverage from 263 to 276 tests with 100% passing rate.
5. All old strings were mechanically verified against `git show 54f5cdbd:<path>` with zero unverified strings.
6. A `.gitattributes` file was added with `*.pkl binary` to safeguard serialized model weights.

### Version Mapping Table

| Version Identifier | Git Hash / Reference | Operational Dates | Environment & Target Audience | Key Characteristics |
| :--- | :--- | :--- | :--- | :--- |
| **`evaluation-study-ui`** *(Locked Tag)* | `54f5cdbd6a73f08a5a853896987bb4e8db1ecb56` | 2026-09-23 to 2026-10-01 | Railway Production (`APP_MODE=evaluation`). Participants (N=42 completers, 41 formal reviews). | Interface actually used by study participants. Retained internal developer phrasing ("clinical review decision", "Structured Learning Signal", editable Reviewer Code). Middle-dot `·` in Stage-2 titles. |
| **`main` baseline** | `6644bb48` / `e56f4d94` | 2026-10-01 to 2026-10-04 | Local Development / Feedback Lab refactor. | Added Feedback Lab direction-aware taxonomy, similar prior cases, and candidate adaptation preview in `screening_result.html`. |
| **`ui-wording-alignment`** *(Active Branch)* | `b0c1b6f` (from `e56f4d`) | Current Working Tree | Post-study aligned evaluation mode + researcher Feedback Lab mode. | Mode-conditional copy: non-clinical framing, Reviewer Code hidden & auto-filled in evaluation mode; Feedback Lab mode retains full researcher features; `(Model Beku)` badge suffix reverted; About page updated with simulated non-expert notice. |

> [!IMPORTANT]
> **Data Collection Provenance:**  
> All 42 completers and all 41 formal human reviews analyzed in the manuscript were collected strictly on the deployment corresponding to commit `54f5cdbd` (tagged as `evaluation-study-ui`). No participant ever interacted with the modified copy on branch `ui-wording-alignment`. The branch exists to align future deployments and provide exact documentation of the visual delta.

---

## 2. Separate Lineage: Commit `54f5cdbd` vs `main` (`6644bb48`) vs `ui-wording-alignment`

To maintain complete transparency for peer review, changes in this repository follow two distinct phases:

### Phase A: What changed between `54f5cdbd` and `main` (`6644bb48`)
Between the evaluation deployment (`54f5cdbd`) and `main` (`6644bb48`), work focused entirely on developing the researcher-facing **Feedback Lab** mechanism:
1. **Single Template Modified:** Only `dashboard/predictor/templates/predictor/screening_result.html` was modified in `main` to introduce Feedback Lab controls (two-step signal selection, direction-aware feedback taxonomy, similar prior cases accordion, and candidate adaptation preview).
2. **Zero Template Changes Elsewhere:** Templates `about.html`, `analytics.html`, `evaluation_practice.html`, `overview.html`, `review_queue.html`, `stage2_entry.html`, `stage2_result.html`, `stage2_review.html`, and `base.html` were **100% identical** between `54f5cdbd` and `main` (`git diff` returned 0 changes).
3. **Backend Models & Services:** Added `0012_humanfeedback_direction_aware_signal.py`, `feedback_taxonomy.py`, `feedback_learning.py`, and test suites for direction-aware signals (`test_direction_aware_taxonomy.py`).

### Phase B: What changed between `main` (`6644bb48`) and `ui-wording-alignment` (`b0c1b6f`)
Branch `ui-wording-alignment` addressed reviewer concerns regarding layperson evaluation framing:
1. **Mode-Conditional Gating:** Added `{% if IS_EVALUATION_MODE %}` / `{% if IS_FEEDBACK_LAB_MODE %}` guards. The entire Feedback Lab learning signal and adaptation card in `screening_result.html` is strictly gated behind `{% if IS_FEEDBACK_LAB_MODE and human_feedback %}`, completely hiding learning loops from evaluation participants.
2. **Non-Clinical Copy:** Replaced clinician wording with neutral "human review" across overview, review queue, screening result, and analytics.
3. **Reviewer Code Auto-Linking:** In evaluation mode, `reviewer_code` is hidden from the UI and automatically linked to the participant's anonymous `respondent_code`.
4. **Stage-2 Non-Diagnostic Framing:** Clarified Stage-2 as a hypothetical data-entry exercise to test ADA 2026 range categorization, rather than a diagnostic laboratory confirmatory claim.
5. **Badge Suffix Reversion:** Reverted `(Model Beku)` badge suffix in `base.html` so the evaluation badge reads `Mode Evaluasi · Protocol {{ EVALUATION_PROTOCOL_VERSION }}` verbatim.
6. **About Page Notice Alignment:** Replaced the prototype notice sentence in `about.html` (in evaluation mode only) with the approved 3-sentence non-diagnostic and simulated volunteer evaluation disclaimer.

---

## 3. High-Resolution Visual Evidence Registry

Visual captures were captured using Playwright (`chromium`, viewport `1440x1080`, `deviceScaleFactor: 2`, full-page and element clips) from a clean, seeded evaluation database containing 11 formal records and zero practice or corrupted records.

| Artifact Filename | Relative Path | Resolution (Physical Pixels) | Commit Source | Content & State |
| :--- | :--- | :--- | :--- | :--- |
| `fig_eval_study_overview_54f5cdbd.png` | `reports_manuscript/figures_evaluation/` | 2880 × 2160 | `54f5cdbd` | Evaluation Overview dashboard with 11 formal records, zero practice records, status badges, and workflow actions. |
| `fig_eval_study_human_review_54f5cdbd.png` | `reports_manuscript/figures_evaluation/` | 2880 × 1720 | `54f5cdbd` | Human Review panel at commit `54f5cdbd` with Override selected, revealing reviewer code input, structured learning signal, and NLP disclaimer. |
| `fig_eval_study_full_page_54f5cdbd.png` | `reports_manuscript/figures_evaluation/` | 2880 × 5320 | `54f5cdbd` | Full Stage-1 screening result page showing Primary Result, GAM Additive Factor Decomposition, and Human Review. |
| `fig_eval_comparison_human_review_latest.png` | `reports_manuscript/figures_evaluation/` | 2880 × 1720 | `e56f4d94` | Human Review panel comparison capture at `HEAD` prior to final branch copy alignment. |
| `fig_eval_comparison_full_page_latest.png` | `reports_manuscript/figures_evaluation/` | 2880 × 5320 | `e56f4d94` | Full Stage-1 screening result page comparison capture at `HEAD`. |

---

## 4. Mechanical Wording Audit & Discrepancy Reconciliation

Every historical string was mechanically verified against `git show 54f5cdbd:<path>`. Discrepancies between earlier manual summaries and verbatim source code at `54f5cdbd` have been resolved:

| # | File & Location at `54f5cdbd` | Verbatim Old String at `54f5cdbd` | Branch String (`ui-wording-alignment`) | Verification & Reconciled Discrepancy |
| :- | :--- | :--- | :--- | :--- |
| 1 | `evaluation_practice.html:65` | `Tenaga kesehatan memegang kendali penuh: menerima rekomendasi atau melakukan Override dengan alasan klinis terstruktur.` | `Peninjau manusia memegang keputusan akhir: menerima rekomendasi atau melakukan Override dengan alasan terstruktur.` | **VERIFIED:** Earlier summary incorrectly cited `"Klinisi memegang keputusan akhir..."`. Verbatim text at `54f5cdbd` confirmed. |
| 2 | `evaluation_practice.html:73` | `Kasus terindikasi dirujuk untuk pemeriksaan biomarker HbA1c standar guna konfirmasi klinis diagnostik.` | `Pada Stage 2 Anda memasukkan satu nilai HbA1c hipotetik untuk menguji alur kerja. Ini bukan hasil laboratorium dan bukan diagnosis.` | **VERIFIED:** Earlier summary incorrectly cited `"Pada Stage 2 klinisi memasukkan..."`. Verbatim text at `54f5cdbd` confirmed. |
| 3 | `analytics.html:596` | `<td>Concordance between AI recommendation and clinician disposition. <strong>Never called AI accuracy.</strong></td>` | `<td>Concordance between AI recommendation and human reviewer disposition. <strong>Never called AI accuracy.</strong></td>` | **VERIFIED:** Full table cell sentence confirmed (earlier summary reported partial phrase `"clinician disposition"`). |
| 4 | `analytics.html:602` | `<td>Frequency of clinician decision override. <strong>Never called AI error rate or mistake.</strong></td>` | `<td>Frequency of human reviewer decision override. <strong>Never called AI error rate or mistake.</strong></td>` | **VERIFIED:** Full table cell sentence confirmed (earlier summary reported partial phrase `"clinician decision override"`). |
| 5 | `analytics.html:608` | `<td>Proportion of reviewed cases ultimately authorized by human clinical judgment for Stage 2.</td>` | `<td>Proportion of reviewed cases ultimately authorized by human reviewer decision for Stage 2.</td>` | **VERIFIED:** Full table cell sentence confirmed (earlier summary reported partial phrase `"human clinical judgment"`). |
| 6 | `app.js:2` | ` * Dysglycemia Screening Clinical Decision Support (CDSS)` | ` * Dysglycemia Screening Research Decision Support` | **VERIFIED:** Verbatim text is inside a top-level JavaScript comment block (`/** ... */`) and does **not** appear in the rendered DOM. |
| 7 | `stage2_entry.html:3, 14` | `Stage 2 · HbA1c Laboratory Assessment` (uses middle dot `\u00b7`) | `Stage 2 – HbA1c Range Assessment` (uses en-dash `\u2013`) | **VERIFIED:** Verbatim old text at `54f5cdbd` used middle dot `·` (`\u00b7`), not en-dash. |
| 8 | `stage2_result.html:3, 14` | `Stage 2 · HbA1c Laboratory Assessment` (uses middle dot `\u00b7`) | `Stage 2 – HbA1c Range Assessment` (uses en-dash `\u2013`) | **VERIFIED:** Verbatim old text at `54f5cdbd` used middle dot `·` (`\u00b7`), not en-dash. |
| 9 | `stage2_review.html:16` | `<h1 class="ui-page-title">Review Stage-2 Laboratory Measurement</h1>` | `<h1 class="ui-page-title">{% if IS_EVALUATION_MODE %}Review Stage-2 HbA1c Entry{% else %}Review Stage-2 Laboratory Measurement{% endif %}</h1>` | **VERIFIED:** Earlier summary misidentified line as `Stage 2 · HbA1c Laboratory Assessment`; verbatim old at `54f5cdbd` was `Review Stage-2 Laboratory Measurement`. |
| 10 | `about.html:30` | `This dashboard is an academic research prototype and is <strong>not a medical diagnostic tool</strong>. It is designed to assist healthcare providers by prioritizing non-laboratory community screening cases for Stage-2 laboratory confirmatory evaluation.` | `{% if IS_EVALUATION_MODE %}This dashboard is an academic research prototype and is not a medical diagnostic tool. It is designed to prioritize non-laboratory community screening cases for possible Stage-2 laboratory evaluation, and to study how non-expert users understand the model's output and explanations. In the participant evaluation, the review task was a simulated exercise performed by volunteers, mostly laypersons.{% else %}...{% endif %}` | **VERIFIED:** Full 2-sentence alert body replaced in evaluation mode with approved 3-sentence non-diagnostic/simulated volunteer evaluation disclaimer. |
| 11 | `screening_result.html:815` | `Reviewer Code <span style="color: hsl(var(--destructive));">*</span>` | `{% if IS_FEEDBACK_LAB_MODE %}...{% endif %}` | **VERIFIED:** Input group hidden in evaluation mode; auto-populated from session respondent code. |
| 12 | `screening_result.html:884` | `Override Factor / Structured Learning Signal <span style="color: hsl(var(--destructive));">*</span>` | `{% if IS_FEEDBACK_LAB_MODE %}Structured Learning Signal *{% else %}Human Override Rationale *{% endif %}` | **VERIFIED:** Verbatim text at `54f5cdbd` included HTML span. |
| 13 | `screening_result.html:556` | `{% if human_feedback %}` | `{% if IS_FEEDBACK_LAB_MODE and human_feedback %}` | **VERIFIED:** Secondary feedback learning signal card completely hidden in evaluation mode. |

---

## 5. Comprehensive 4-Part Terminology & Reachability Audit

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

**Recommended Disposition (Proposed Patch):**  
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
| **Top-Right Mode Pill** | `Mode Evaluasi · Protocol v1.0.3` | `Mode Evaluasi · Protocol v1.0.3` | Identical text. Suffix `(Model Beku)` reverted to maintain exact visual parity. |

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

## 6. Verification Test Suite Execution

A dedicated unit test suite, `EvaluationModeWordingTests`, was implemented in `dashboard/predictor/test_evaluation_wording.py` (13 tests) verifying:
- Non-clinical wording appears across overview, review queue, screening result, and Stage 2 in evaluation mode.
- Reviewer code is hidden and auto-filled from session in evaluation mode.
- Feedback Lab mode retains full researcher wording ("Structured Learning Signal", editable Reviewer Code).
- **Absence Checks:** Explicitly tests absence of prohibited terms: `"learning loop"`, `"adaptation layers"`, `"Check Similar Prior Cases"`, `"Eligible for Adaptation"` in evaluation mode.
- **Presence Checks:** Explicitly tests presence of required finalized review summary items (`"Recommendation Overridden"`, `"No referral recommended..."`, `"Override Reason"`, `"Reviewer ID"`, rationale text).

```
Test Run (predictor):  Ran 276 tests in 10.312s -> OK (0 failures, 0 errors)
```

---

## 7. Commitments & Governance Conformance

1. **Tag Status:** Tag `evaluation-study-ui` exists locally at commit `54f5cdbd6a73f08a5a853896987bb4e8db1ecb56`. Tagger: `Daymbroo <felikjavier123@gmail.com>`. No tag has been pushed to remote.
2. **Branch Status:** All changes reside on local branch `ui-wording-alignment`. No remote push or pull request has been issued.
3. **Ethics / Instrument Lock:** Zero modifications were made to `evaluation_consent.html` or `services/questionnaire.py`, preserving the exact ethical consent text and validated psychometric items.
4. **Model Architecture:** The Phase-5 GAM model (`lambda=10.0`, threshold `0.1389`) remains strictly frozen and untampered.
