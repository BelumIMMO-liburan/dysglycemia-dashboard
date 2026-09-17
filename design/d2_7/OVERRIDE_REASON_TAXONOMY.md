# Structured Override Rationale Taxonomy Specification

**Document Version:** 1.0  
**Phase:** D2.7  
**Status:** Frozen & Approved  
**Governing Skill:** `research-governance` (Highest Precedence)  

---

## 1. Overview & Research Scope

This taxonomy specifies the structured rationale categories available during the Human Override workflow. 

### Critical Interpretation Notice:
> **"These categories describe reviewer interaction rationale within a research decision-support framework. They are structured audit categories, NOT clinically validated medical diagnostic categories, and do NOT establish biological truth."**

To maintain clean research telemetry, reasons are strictly branch-sensitive: categories applicable when overriding towards non-referral are differentiated from categories applicable when overriding towards referral.

---

## 2. Branch 1: AI Recommends REFER $\longrightarrow$ Human Overrides to DO NOT REFER

Applicable when the frozen GAM produced an elevated screening signal ($\hat{p} \ge 0.1389$), but the reviewer decides that diagnostic Stage-2 HbA1c referral is unnecessary at this time.

| Reason Code | Display Label | Definition | Interpretation Limitation | Note Required? |
| :--- | :--- | :--- | :--- | :--- |
| `additional_context_reduces_concern` | "Additional context supports not referring at this time" | The reviewer has access to recent prior laboratory results (e.g. normal fasting plasma glucose within past 3 months) or verified physical fitness profiles that reduce suspicion of underlying dysglycemia. | Does not invalidate the statistical model's evaluation of the 7 Stage-1 non-laboratory predictors. | Optional (max 500 chars) |
| `input_quality_concern` | "Concern about the quality or accuracy of one or more screening inputs" | The reviewer suspects measurement error, transcription error, or atypical confounding in one or more Stage-1 inputs (e.g. self-reported sedentary time or anthropometric waist circumference). | Does not alter the persisted baseline input values in `ScreeningRecord`. | Optional (max 500 chars) |
| `repeat_assessment_preferred` | "Repeat or additional assessment is preferred before referral" | The reviewer elects to schedule a follow-up non-laboratory screening or clinic visit before ordering venous blood draw procedures. | Does not guarantee that risk will remain low in subsequent evaluations. | Optional (max 500 chars) |
| `other` | "Other reason" | A distinct contextual factor not captured by the pre-defined categories. | Cannot be selected without textual justification. | **MANDATORY** (1–500 chars) |

---

## 3. Branch 2: AI Recommends DO NOT REFER $\longrightarrow$ Human Overrides to REFER

Applicable when the frozen GAM produced a lower screening signal ($\hat{p} < 0.1389$), but the reviewer decides that diagnostic Stage-2 HbA1c referral is warranted.

| Reason Code | Display Label | Definition | Interpretation Limitation | Note Required? |
| :--- | :--- | :--- | :--- | :--- |
| `additional_context_increases_concern` | "Additional context supports referral" | The reviewer notes clinical indicators beyond the 7 Stage-1 predictors, such as strong first-degree family history of diabetes, symptoms of polyuria/polydipsia, or history of gestational diabetes. | Does not modify the Stage-1 model feature set or retrain coefficients. | Optional (max 500 chars) |
| `input_quality_concern` | "Concern about the quality or accuracy of one or more screening inputs" | The reviewer suspects an input was underreported (e.g., patient underreporting sedentary sitting hours or BMI measurement ambiguity). | Does not alter the persisted baseline input values in `ScreeningRecord`. | Optional (max 500 chars) |
| `precautionary_referral` | "Referral is preferred as a precaution" | The reviewer chooses a defensive clinical screening approach for an individual near the decision boundary or exhibiting border-zone characteristics. | Does not imply model classification error; reflects clinical risk aversion. | Optional (max 500 chars) |
| `other` | "Other reason" | A distinct contextual factor not captured by the pre-defined categories. | Cannot be selected without textual justification. | **MANDATORY** (1–500 chars) |

---

## 4. Branch Validation Enforcement Matrix

| Submitted Reason Code | Permitted for REFER $\to$ NO REFER | Permitted for NO REFER $\to$ REFER | Server Enforcement |
| :--- | :---: | :---: | :--- |
| `additional_context_reduces_concern` | **YES** | NO | Form & Model Validation Error if submitted on NO REFER branch. |
| `additional_context_increases_concern`| NO | **YES** | Form & Model Validation Error if submitted on REFER branch. |
| `repeat_assessment_preferred` | **YES** | NO | Form & Model Validation Error if submitted on NO REFER branch. |
| `precautionary_referral` | NO | **YES** | Form & Model Validation Error if submitted on REFER branch. |
| `input_quality_concern` | **YES** | **YES** | Permitted on both branches. |
| `other` | **YES** | **YES** | Permitted on both branches, strictly requires non-empty `override_note`. |

---

## 5. Rationale Note Guidelines & Boundary Rules

1. **Maximum Length:** Enforced at 500 characters.
2. **Contextual Scope:** Rationale notes provide brief contextual clarification. They are **not** clinical progress notes, EHR chart extracts, or diagnostic justifications.
3. **No PII:** Reviewers are instructed never to include patient names, clinician names, dates of birth, or identification numbers.
