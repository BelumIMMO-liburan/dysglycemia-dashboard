# Phase D2.9 Medical Language & Epistemic Governance Audit

## 1. Compliance Mandate
The Research Governance skill (`research-governance`) enforces strict linguistic and epistemic boundaries on all dashboard interfaces. The system is an investigational decision-support screening prototype evaluated on NHANES data; it is **NOT** a certified diagnostic medical device.

---

## 2. Terminology Evaluation Matrix

| Category | Permitted Terminology | Strictly Prohibited Terminology | Audit Findings | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Model Output** | "Screening signal", "Elevated signal", "Lower signal", "Calculated probability" | "Diagnosis", "Diagnostic prediction", "Positive diabetes", "Negative diabetes" | Zero prohibited terms in queue/history templates. | **PASS** |
| **Recommendation** | "AI referral recommendation", "Refer for Stage-2 HbA1c", "Do not refer" | "Doctor prescription", "Definitive action", "Clinical truth", "Certainty" | Permitted referral language used uniformly. | **PASS** |
| **Human Review** | "Human guided review", "Accepted recommendation", "Overridden recommendation" | "AI correct", "AI incorrect", "Doctor corrected AI", "Ground truth verification" | Strict decision-concordance language maintained. | **PASS** |
| **Laboratory Stage** | "Stage-2 HbA1c laboratory assessment", "HbA1c laboratory range", "Normal-range", "Prediabetes-range", "Diabetes-range" | "Blood test diagnosis", "Confirmed disease", "Diabetic patient" | Persisted laboratory ranges with `-range` suffix used strictly. | **PASS** |
| **Lifecycle State** | "Workflow status", "Review status", "Stage-2 status" | "Clinical status", "Patient condition", "Disease progression" | Describes application workflow exclusively. | **PASS** |

---

## 3. Automated Script Audit Results
An automated case-insensitive grep scan across `dashboard/predictor/templates/predictor/` for prohibited phrases (`diagnosis`, `patient disease`, `positive diabetes`, `negative diabetes`, `AI correct`, `AI incorrect`, `doctor corrected`, `clinical truth`) confirmed **0 matches** in active Phase D2.9 files.
