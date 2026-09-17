# Stage-2 HbA1c Reference Lock & Clinical Boundary Specification

## 1. Authoritative Reference Sources

### Primary Reference
- **Organization:** American Diabetes Association (ADA)
- **Document:** *Standards of Care in Diabetes — 2026*
- **Section:** Section 2: "Diagnosis and Classification of Diabetes"
- **Criteria for the Diagnosis of Diabetes:** Table 2.2 / Table 2.5 (A1C Criteria)

### Secondary Cross-Check Reference
- **Organization:** National Institute of Diabetes and Digestive and Kidney Diseases (NIDDK), National Institutes of Health (NIH)
- **Guidance:** *The A1C Test & Diabetes* (Clinical Information and Diagnostic Standards)
- **Consensus:** Concordant with ADA cut-points (<5.7%, 5.7%–6.4%, ≥6.5%).

---

## 2. Frozen Reference Rule Identifier

```
RULE_VERSION = "ADA_2026_A1C_RANGE_V1"
```

- Every `Stage2Assessment` persistent record stores this immutable version identifier.
- Rule definitions must NOT be changed retroactively. If future clinical standards are updated in application evolutions, a new version identifier must be defined (e.g., `ADA_2027_A1C_RANGE_V2`), preserving historical records under their creation-time rule.

---

## 3. Frozen Laboratory Range Rules (Nonpregnant Individuals)

For nonpregnant individuals, the prototype locks the following deterministic boundaries using exact Decimal arithmetic:

| Internal Code | User-Facing Category Label | HbA1c Percentage Range | Rule Definition |
| :--- | :--- | :--- | :--- |
| `normal_range` | **Normal-range** | $\text{HbA1c} < 5.7\%$ | `hba1c < Decimal("5.7")` |
| `prediabetes_range` | **Prediabetes-range** | $5.7\% \le \text{HbA1c} < 6.5\%$ | `Decimal("5.7") <= hba1c < Decimal("6.5")` |
| `diabetes_range` | **Diabetes-range** | $\text{HbA1c} \ge 6.5\%$ | `hba1c >= Decimal("6.5")` |

### Exact Decimal Boundary Test Targets
- `5.69%` $\to$ `normal_range`
- `5.70%` $\to$ `prediabetes_range`
- `6.49%` $\to$ `prediabetes_range`
- `6.50%` $\to$ `diabetes_range`
- `5.7%` $\to$ `prediabetes_range`
- `6.5%` $\to$ `diabetes_range`

No boundary gaps exist. Values are never rounded prior to range categorization.

---

## 4. Epistemic Separation: Laboratory Range vs. Clinical Diagnosis

> [!IMPORTANT]
> **Essential Epistemic Boundary:**
> While these quantitative thresholds correspond to clinical diagnostic cut-points within the ADA Standards of Care, this research prototype presents them **strictly as Laboratory Range Categories**, NOT as automated clinical diagnoses.

### Authoritative Diagnostic Confirmation Requirement
As specified by the ADA Standards of Care (2026):
> *"In the absence of unequivocal hyperglycemia (e.g., hyperglycemic crisis or classic symptoms of hyperglycemia and a random plasma glucose ≥200 mg/dL), diagnosis requires two abnormal test results from the same sample or in two separate test samples."*

The research prototype collects **only an entered HbA1c percentage** and does **not** assess clinical symptoms, random glucose, or repeat testing. Therefore:
1. The application **does not evaluate whether confirmatory testing criteria have been met**.
2. The application **never assigns an automated diagnosis** (e.g., no `confirmed_diabetes` or `diagnosis` database fields).
3. The user interface explicitly pairs all range presentations with standard clinical context warnings.

---

## 5. Methodological & Laboratory Limitations

As documented by ADA and NIDDK:
1. **NGSP Certification:** A1C should be measured using a method certified by the National Glycohemoglobin Standardization Program (NGSP) and standardized to the Diabetes Control and Complications Trial (DCCT) reference assay.
2. **Clinical Factors Influencing A1C:** Conditions that alter red blood cell turnover (e.g., sickle cell trait/disease, hemoglobinopathies, hemodialysis, recent blood transfusion, erythropoietin therapy, iron-deficiency anemia, pregnancy) can falsely elevate or depress HbA1c independent of ambient glycemia.
3. **Prototype Scope:** The prototype does not model these clinical hematologic covariates; it strictly categorizes the entered numerical value and provides transparent guidance regarding this limitation.

---

## 6. Input Domain Safety Bounds

- Minimum acceptable value: `2.00%` (Mathematical and practical lower bound)
- Maximum acceptable value: `25.00%` (Mathematical and practical upper bound)
- Data format: Decimal with 2 decimal places (`DecimalField(max_digits=4, decimal_places=2)`)
- Classification: Positive, finite Decimal values only.
- Safety Rationale: These bounds are enforced for **mathematical input safety and data validation**, not as unsupported claims of absolute physiological impossibility.
