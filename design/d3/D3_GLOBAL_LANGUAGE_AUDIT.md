# D3 Global Clinical & Research Language Audit

**Audit Date:** 2026-09-05  
**Audited Directory:** `dashboard/predictor/templates/` & `dashboard/predictor/services/`  
**Standard:** Research Governance & Non-Diagnostic Framing (Skill: `research-governance`)

---

## 1. Compliance Audit of Clinical & Diagnostic Terminology

A full text search across all active templates and services was conducted to verify that no active screen makes ungrounded clinical, diagnostic, or population claims:

| Target Query | Search Findings | Governance Evaluation | Status |
| :--- | :--- | :--- | :--- |
| `diagnosis` / `diagnosed` | Found in disclaimers: *"This screening result is not a diagnosis"*, *"does not provide medical diagnosis"*; and as predictor definition: *"Self-reported diagnosis of hypertension"* | All occurrences explicitly disclaim automated diagnosis or define NHANES self-reported survey variables. Zero diagnostic claims made. | **PASSED** |
| `patient has diabetes` | 0 occurrences found in active templates | Replaced by calibrated referral recommendation language. | **PASSED** |
| `positive for diabetes` | 0 occurrences found in active templates | Replaced by elevated screening signal terminology. | **PASSED** |
| `negative for diabetes` | 0 occurrences found in active templates | Replaced by lower screening signal terminology. | **PASSED** |
| `AI correct` / `AI incorrect` | 0 occurrences found in active templates | Replaced by descriptive decision concordance (`Human–AI agreement` / `Human–AI disagreement`). | **PASSED** |
| `doctor corrected` | 0 occurrences found in active templates | Replaced by auditable `Human Override` terminology with structured rationale. | **PASSED** |
| `clinical truth` / `ground truth` | Found in explicit governance notices: *"Neither establishes biological ground truth"*, *"Neither axis is clinical ground truth"* | Used exclusively as defensive disclaimers to prevent users from conflating agreement with diagnostic accuracy. | **PASSED** |
| `future diabetes risk` | 0 occurrences found in active templates | Correctly framed as cross-sectional screening probability of unrecognized dysglycemia at intake. | **PASSED** |
| `clinical optimum` | 0 occurrences found in active templates | Operating threshold framed purely as development-derived statistical operating point. | **PASSED** |
| `validated for Indonesia` | 0 occurrences in affirmative context. `about.html` Section 4 explicitly states: *"The model was developed... using US NHANES 2021–August 2023 survey data. It is not validated for Indonesia..."* | Generalizability boundary is fully and prominently declared. | **PASSED** |
| `nationally representative` | Framed strictly in reference to US NHANES survey design; never asserted as representative of Indonesia or study participants. | Correctly contextualized. | **PASSED** |
| `13.9% sensitivity` | 0 occurrences of this error. Threshold is accurately stated as `0.1389`; held-out confirmatory sensitivity is correctly stated as `86.39%`. | Accurate scientific reporting. | **PASSED** |

---

## 2. Approved Standard Lexicon Enforcement

All active views, badges, titles, and copy enforce the locked approved vocabulary:

- **Prototype Identity:** *"Research Prototype — Not a Diagnostic Tool"*
- **Stage-1 Engine:** *"Stage-1 Non-Laboratory Screening"*
- **Model Output:** *"Screening Probability"* and *"Elevated / Lower Screening Signal"*
- **AI Recommendation:** *"AI Referral Recommendation (Refer / Do Not Refer)"*
- **Human Actions:** *"Human Review"*, *"Accepted Recommendation"*, *"Human Override"*
- **Final Determination:** *"Final Human Referral Decision"*
- **Stage-2 Confirmatory:** *"Stage-2 HbA1c Laboratory Assessment"*
- **Laboratory Categories:** *"HbA1c Laboratory Range (Normal-range / Prediabetes-range / Diabetes-range)"*
- **Agreement Metrics:** *"Human–AI Agreement Rate"* and *"Human Override Rate"*
