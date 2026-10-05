# UI Version Registry & Evaluation Interface Alignment Report

**Repository:** `dysglycemia-dashboard`  
**Date:** 2026-10-05  
**Protocol:** Two-Stage Non-Laboratory Screening Evaluation Protocol E1 (v1.0.3) / E2  
**Governing Branch:** `ui-wording-alignment`  
**Evaluation Study Tag:** `evaluation-study-ui` (`54f5cdbd6a73f08a5a853896987bb4e8db1ecb56`)  
**Tagger Identity:** `Daymbroo` (1791139775 +0700)

---

## 1. Executive Summary & Version Registry

Between 23 September 2026 and 1 October 2026, an empirical participant evaluation study was conducted on the Railway cloud deployment of this repository. A reviewer noted discrepancies between the manuscript framing (which describes layperson/volunteer participants conducting a simulated workflow evaluation of a frozen model without online learning) and visual artifacts displaying clinician-centric wording, online learning signals, and an unpopulated reviewer code input.

To provide empirical proof for manuscript reporting and resolve UI discrepancies:
1. An annotated Git tag `evaluation-study-ui` was created at commit `54f5cdbd6a73f08a5a853896987bb4e8db1ecb56` (tagged by `Daymbroo`).
2. High-resolution Playwright captures (1440×1080 @ 2× DPR, 24 captures documented in `capture_report_v2.json`) were generated directly from commit `54f5cdbd` and branch `ui-wording-alignment` running in `APP_MODE=evaluation` on a clean, verified SQLite database.
3. A dedicated alignment branch `ui-wording-alignment` was created from `main`, implementing mode-conditional copy alignments, gating researcher feedback mechanisms behind `feedback_lab` mode, auto-filling the pseudonymous reviewer code, blocking legacy endpoints with 404 for participants, and enforcing strict session scoping.
4. An expanded test suite was developed (`test_evaluation_mode.py`, `test_evaluation_wording.py`), raising total test coverage from 263 to 284 tests with 100% passing rate.
5. All old strings were mechanically verified against `git show 54f5cdbd:<path>` with zero unverified strings.
6. A `.gitattributes` file was added with `*.pkl binary` to safeguard serialized model weights.

### Version Mapping Table

| Version Identifier | Git Hash / Reference | Operational Dates | Environment & Target Audience | Key Characteristics |
| :--- | :--- | :--- | :--- | :--- |
| **`evaluation-study-ui`** *(Locked Tag)* | `54f5cdbd6a73f08a5a853896987bb4e8db1ecb56` | 2026-09-23 to 2026-10-01 | Railway Production (`APP_MODE=evaluation`). Participants (N=42 completers, 41 formal reviews). | Interface actually used by study participants. Retained internal developer phrasing ("clinical review decision", "Structured Learning Signal", editable Reviewer Code). Middle-dot `·` in Stage-2 titles. |
| **`main` baseline** | `6644bb48` / `e56f4d94` | 2026-10-01 to 2026-10-04 | Local Development / Feedback Lab refactor. | Added Feedback Lab direction-aware taxonomy, similar prior cases, and candidate adaptation preview in `screening_result.html`. |
| **`ui-wording-alignment`** *(Active Branch)* | `9b5a8e2` (from `e56f4d`) | Current Working Tree | Post-study aligned evaluation mode + researcher Feedback Lab mode. | Mode-conditional copy: non-clinical framing, Reviewer Code hidden & auto-filled in evaluation mode; Feedback Lab mode retains full researcher features; `(Model Beku)` badge suffix reverted; About page updated with simulated non-expert notice; legacy endpoints return 404; active participant session scoping enforced. |

> [!IMPORTANT]
> **Data Collection Provenance:**  
> All 42 completers and all 41 formal human reviews analyzed in the manuscript were collected strictly on the deployment corresponding to commit `54f5cdbd` (tagged as `evaluation-study-ui`). No participant ever interacted with the modified copy on branch `ui-wording-alignment`. The branch exists to align future deployments and provide exact documentation of the visual delta.

---

## 2. Separate Lineage: Commit `54f5cdbd` vs `main` (`6644bb48`) vs `ui-wording-alignment`

To maintain complete transparency for peer review, changes in this repository follow two distinct phases:

### Phase A: What changed between `54f5cdbd` and `main` (`6644bb48`)
Between the evaluation deployment (`54f5cdbd`) and `main` (`6644bb48`), work focused entirely on developing the researcher-facing **Feedback Lab** mechanism:
1. **Templates Modified:** `screening_result.html` was modified in `main` to introduce Feedback Lab controls (two-step signal selection, direction-aware feedback taxonomy, similar prior cases accordion, and candidate adaptation preview), and `components_demo.html` received design system demonstration updates.
2. **Forms & Views Extended:** `forms.py` was extended to include Feedback Lab forms (`UnifiedHumanReviewForm`, `HumanFeedbackForm`, `ControlledExperimentForm`), and `views.py` added endpoints for the Feedback Lab experiment, controlled adaptation, and similar case comparison (`feedback_experiment_view`, `run_comparison_view`, etc.).
3. **Backend Models & Services:** Added `0012_humanfeedback_direction_aware_signal.py`, `feedback_taxonomy.py`, `feedback_learning.py`, and test suites for direction-aware signals (`test_direction_aware_taxonomy.py`, `test_feedback_mechanism_validation.py`).
4. **Other Templates Unchanged:** Templates `about.html`, `analytics.html`, `evaluation_practice.html`, `overview.html`, `review_queue.html`, `stage2_entry.html`, `stage2_result.html`, `stage2_review.html`, and `base.html` were **100% identical** between `54f5cdbd` and `main` (`git diff` returned 0 changes across these files).

### Phase B: What changed between `main` (`6644bb48`) and `ui-wording-alignment` (`9b5a8e2`)
Branch `ui-wording-alignment` addressed reviewer concerns regarding layperson evaluation framing:
1. **Mode-Conditional Gating:** Added `{% if IS_EVALUATION_MODE %}` / `{% if IS_FEEDBACK_LAB_MODE %}` guards. The entire Feedback Lab learning signal and adaptation card in `screening_result.html` is strictly gated behind `{% if IS_FEEDBACK_LAB_MODE and human_feedback %}`, completely hiding learning loops from evaluation participants.
2. **Non-Clinical Copy:** Replaced clinician wording with neutral "human review" across overview, review queue, screening result, and analytics.
3. **Reviewer Code Auto-Linking:** In evaluation mode, `reviewer_code` is hidden from the UI and automatically linked to the participant's anonymous `respondent_code`.
4. **Stage-2 Non-Diagnostic Framing:** Clarified Stage-2 as a hypothetical data-entry exercise to test ADA 2026 range categorization, rather than a diagnostic laboratory confirmatory claim.
5. **Badge Suffix Reversion:** Reverted `(Model Beku)` badge suffix in `base.html` so the evaluation badge reads `Mode Evaluasi · Protocol {{ EVALUATION_PROTOCOL_VERSION }}` verbatim.
6. **About Page Notice Alignment:** Replaced the prototype notice sentence in `about.html` (in evaluation mode only) with the approved 3-sentence non-diagnostic and simulated volunteer evaluation disclaimer.
7. **Legacy Endpoint Blocking:** Added 404 blocking in evaluation mode for legacy single-stage endpoints (`/index/`, `/predict/`, `/evaluation/`, `/components/`) with staff exemption.
8. **Participant Session Scoping:** Added `_is_eval_participant`, `_scoped`, and `_require_own_record` helpers to restrict evaluation participants strictly to records belonging to their own session across overview, review queue, analytics, screening result, human reviews, Stage-2 entry, review, and confirm routes.

---

## 3. High-Resolution Visual Evidence Registry

Visual captures were captured using Playwright (`chromium`, viewport `1440x1080`, `deviceScaleFactor: 2`, full-page and element clips) from a clean, seeded evaluation database containing 11 formal records and zero practice or corrupted records.

A comprehensive set of **24 new captures** across both lineages is maintained in `reports_manuscript/figures_evaluation/` and mechanically indexed in `reports_manuscript/figures_evaluation/capture_report_v2.json`:

### 12 Captures from Study Version Commit `54f5cdbd`:
1. `fig_p3_e_consent_54f5cdbd.png`: Informed Consent and participant demographic intake.
2. `fig_p3_d_practice_54f5cdbd.png`: Practice Case P0 onboarding workflow.
3. `fig_p3_f_new_screening_54f5cdbd.png`: Stage-1 Non-Laboratory Screening input form.
4. `fig_p3_g_review_queue_54f5cdbd.png`: Actionable review queue with pending cases.
5. `fig_p3_a_finalized_review_54f5cdbd.png`: Finalized Review Result showing Feedback Loop card and NLP confidence score.
6. `fig_p3_c_override_panel_54f5cdbd.png`: Human Override Dialog showing Reviewer Code input and Structured Learning Signal.
7. `fig_p3_b_stage2_54f5cdbd.png`: Stage-2 HbA1c Laboratory Assessment entry form.
8. `fig_p3_h_about_54f5cdbd.png`: About the Model methodology page.
9. `fig_p3_i_analytics_54f5cdbd.png`: Research Analytics & Human-AI Decision Flow metrics.
10. `fig_p3_j_history_54f5cdbd.png`: Screening History Ledger.
11. `fig_p3_k_questionnaire_54f5cdbd.png`: Evaluation Questionnaire (4-part psychometric instrument).
12. `fig_p3_l_overview_54f5cdbd.png`: Primary Overview dashboard with 11 formal records.

### 12 Parallel Captures from Branch `ui-wording-alignment`:
13–24. Corresponding pages (`fig_p4_e_consent_aligned.png` through `fig_p4_l_overview_aligned.png`) demonstrating mode-conditional copy alignment, hidden reviewer code, hidden learning loops, and non-clinical framing.

Full DOM extracts and per-page keyword audits are documented in `capture_report_v2.json`.

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
| **`patient`** | `index.html:4,7,16,19`, `result.html:79,82,84,86,87`, `evaluation.html:49`, `components_demo.html:200` | Legacy & UI demo views only (`/index/`, `/predict/`, `/evaluation/`, `/components/`). | **Zero occurrences in primary two-stage screening templates.** Blocked with 404 in evaluation mode. |
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
In `commit 54f5cdbd`, none of these four views checked `settings.APP_MODE`. In `base.html`, navigation links were hidden in the sidebar, but manual URL navigation could access them.

**Resolution Implemented:**  
In `predictor/views.py`, helper `_block_in_evaluation_mode(request)` was introduced at the entry of `index`, `predict_view`, `evaluation_view`, and `components_demo_view`, raising `Http404` for evaluation participants while exempting authenticated staff.

### Audit (c): Sidebar Navigation Item Comparison

| Navigation Section | Commit `54f5cdbd` (`evaluation-study-ui`) | Branch `ui-wording-alignment` | Status & Visual Delta |
| :--- | :--- | :--- | :--- |
| **Screening Workflow** | Overview (`/`), New Screening (`/screening/new/`), Review Queue (`/review/`), History (`/history/`) | Overview (`/`), New Screening (`/screening/new/`), Review Queue (`/review/`), History (`/history/`) | Identical layout and links. Added `aria-current="page"` for accessibility. |
| **Research & Methodology**| Analytics (`/analytics/`), About the Model (`/about/`) | Analytics (`/analytics/`), About the Model (`/about/`) | Identical layout and links. |
| **Researcher Tools** | `feedback_experiment` and `components_demo` hidden via `{% if not IS_EVALUATION_MODE %}` | `feedback_experiment` and `components_demo` hidden via `{% if not IS_EVALUATION_MODE %}` | Identical behavior. Completely hidden in evaluation mode. |
| **Research Evaluation** | Informed Consent (`/evaluation/consent/`), Practice Case P0 (`/evaluation/practice/`), Questionnaire (`/evaluation/questionnaire/`) | Informed Consent (`/evaluation/consent/`), Practice Case P0 (`/evaluation/practice/`), Questionnaire (`/evaluation/questionnaire/`) | Identical layout and links. |
| **Top-Right Mode Pill** | `Mode Evaluasi · Protocol v1.0.3` | `Mode Evaluasi · Protocol v1.0.3` | Identical text. Suffix `(Model Beku)` reverted to maintain exact visual parity. |

### Audit (d): Informed Consent, Practice Flow, and Stage-2 Verbatim Wording Comparison

To rigorously evaluate what text study participants actually read during the 23 September – 1 October 2026 evaluation versus post-study alignments on branch `ui-wording-alignment`:

| Workflow Phase & Artifact | Study Version Text (`54f5cdbd` — What 42 Participants Saw) | Branch Only (`ui-wording-alignment`) |
| :--- | :--- | :--- |
| **Informed Consent**<br>`evaluation_consent.html:37–41` | • *"Anonimitas & Kerahasiaan: Tidak ada data identitas pribadi (nama, kontak, institusi) yang disimpan. Setiap partisipan diidentifikasi melalui kode acak anonim (contoh: `R-A1B2C3D4`)."*<br>• *"Bukan Alat Diagnostik Klinis: Sistem ini merupakan prototype riset akademik sistem informasi dan bukan alat medis diagnostik. Hasil penilaian risiko adalah perkiraan statistik model machine learning."*<br>• *"Alur Kegiatan: Anda akan (1) membaca pengenalan alur pada Kasus Latihan P0, (2) mencoba proses screening risiko, (3) meninjau penjelasan AI dan mencoba fitur peninjauan manusia, dan (4) mengisi kuesioner evaluasi singkat (pemahaman, SUS, dan umpan balik)."* | *(Identical — locked ethical instrument, 0 changes)* |
| **Practice Case P0 Specification**<br>`services/questionnaire.py:287` | • Title: *"Kasus Latihan P0 — Orientasi Alur Kerja (Bukan Data Pasien Nyata)"*<br>• Description: *"Kasus latihan ini dirancang untuk memperkenalkan alur screening: melihat hasil AI, memeriksa penjelasan feature contribution, mencoba keputusan peninjauan manusia (Setuju / Override), dan memberikan umpan balik terstruktur. Kasus ini dikecualikan dari data analisis riset."* | *(Identical — locked psychometric instrument, 0 changes)* |
| **Practice Step 3 (Human Review)**<br>`evaluation_practice.html:65` | *"Tenaga kesehatan memegang kendali penuh: menerima rekomendasi atau melakukan Override dengan alasan klinis terstruktur."* | *"Peninjau manusia memegang keputusan akhir: menerima rekomendasi atau melakukan Override dengan alasan terstruktur."* |
| **Practice Step 4 (Stage 2)**<br>`evaluation_practice.html:73` | *"Kasus terindikasi dirujuk untuk pemeriksaan biomarker HbA1c standar guna konfirmasi klinis diagnostik."* | *"Pada Stage 2 Anda memasukkan satu nilai HbA1c hipotetik untuk menguji alur kerja. Ini bukan hasil laboratorium dan bukan diagnosis."* |
| **Stage-2 Page Title & Breadcrumb**<br>`stage2_entry.html:3, 14`<br>`stage2_result.html:3, 14` | `Stage 2 · HbA1c Laboratory Assessment` | `Stage 2 – HbA1c Range Assessment` |
| **Stage-2 Entry Card Heading & Subtitle**<br>`stage2_entry.html:187, 190` | • Heading: `Enter HbA1c Measurement`<br>• Subtitle: `Laboratory measurement in percent (%). Values are categorized according to ADA Standards of Care (2026).` | • Heading: `Enter HbA1c Range Value`<br>• Subtitle: `Enter numeric HbA1c value to test range categorization according to ADA Standards of Care (2026).` |
| **Stage-2 Review Page Heading**<br>`stage2_review.html:16` | `<h1 class="ui-page-title">Review Stage-2 Laboratory Measurement</h1>` | `<h1 class="ui-page-title">{% if IS_EVALUATION_MODE %}Review Stage-2 HbA1c Entry{% else %}Review Stage-2 Laboratory Measurement{% endif %}</h1>` |
| **Stage-2 Result Card Heading**<br>`stage2_result.html:76` | `Stage-2 Laboratory Assessment Result` | `Stage-2 Range Categorization Result` |

**Input Guidance & Evidence Finding:**  
Neither the consent form nor the questionnaire mandated that participants enter their own personal medical information. Participants completed onboarding using predefined Case P0 and non-laboratory screening inputs. In the study version (`54f5cdbd`), Stage 2 was framed in the practice onboarding text using standard referral language (`"Kasus terindikasi dirujuk untuk pemeriksaan biomarker HbA1c standar guna konfirmasi klinis diagnostik"`) and on the Stage-2 pages as `"Laboratory Assessment"` / `"Laboratory measurement"`. Explicit disclaimers characterizing Stage 2 as hypothetical data entry (`"memasukkan satu nilai HbA1c hipotetik"`, `"Range Assessment"`) are present in branch `ui-wording-alignment` only.

---

## 6. Verification Test Suite Execution

A dedicated unit test suite, `EvaluationModeWordingTests`, and comprehensive mode tests (`test_evaluation_mode.py`, `test_direction_aware_taxonomy.py`) verify:
- Non-clinical wording appears across overview, review queue, screening result, and Stage 2 in evaluation mode.
- Reviewer code is hidden and auto-filled from session in evaluation mode.
- Feedback Lab mode retains full researcher wording ("Structured Learning Signal", editable Reviewer Code).
- **Absence Checks:** Explicitly tests absence of prohibited terms: `"learning loop"`, `"adaptation layers"`, `"Check Similar Prior Cases"`, `"Eligible for Adaptation"` in evaluation mode.
- **Presence Checks:** Explicitly tests presence of required finalized review summary items (`"Recommendation Overridden"`, `"No referral recommended..."`, `"Override Reason"`, `"Reviewer ID"`, rationale/note text).
- **Legacy Endpoint Blocking:** Asserts 404 for unauthenticated participants accessing legacy single-stage endpoints in evaluation mode; 200 for staff; 200 in feedback_lab mode.
- **Participant Scoping:** With `Client(enforce_csrf_checks=True)`, session A cannot GET session B's results, cannot POST reviews or Stage-2 assessments for B (asserting 404 and zero row mutations), and sees only own counts in overview, review queue, and analytics.

```
Test Run (predictor):  Ran 284 tests in 11.840s -> OK (0 failures, 0 errors)
```

---

## 7. Commitments & Governance Conformance

1. **Tag Status:** Tag `evaluation-study-ui` exists locally at commit `54f5cdbd6a73f08a5a853896987bb4e8db1ecb56`. Tagger: `Daymbroo`. No tag has been pushed to remote.
2. **Branch Status:** All changes reside on local branch `ui-wording-alignment`. No remote push or pull request has been issued.
3. **Ethics / Instrument Lock:** Zero modifications were made to `evaluation_consent.html` or `services/questionnaire.py`, preserving the exact ethical consent text and validated psychometric items.
4. **Model Architecture:** The Phase-5 GAM model (`lambda=10.0`, threshold `0.1389`) remains strictly frozen and untampered.
