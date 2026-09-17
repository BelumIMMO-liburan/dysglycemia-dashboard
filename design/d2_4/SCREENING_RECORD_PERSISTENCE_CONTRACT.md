# Screening Record Persistence Contract: Data Architecture & Immutability Specification

**Document Version:** 1.0  
**Phase:** D2.4  
**Status:** Frozen & Approved  
**Governing Skill:** `research-governance`  

---

## 1. Purpose & Architectural Principles

This document formalizes the persistence contract for Stage-1 non-laboratory dysglycemia screening records. It defines the database schema, data types, provenance tracking, and strict immutability guarantees.

### Core Architectural Mandate
> **"Future Human Review records must not overwrite original AI screening outputs."**

The `ScreeningRecord` entity represents the immutable historical truth of what the AI model evaluated at the time of the screening intake. When human review and clinical override capabilities are introduced in subsequent phases, they will reside in distinct relational entities referencing `ScreeningRecord.id`, preserving the AI output as unalterable evidentiary provenance.

---

## 2. Schema Specification: `ScreeningRecord`

**Database Table:** `predictor_screeningrecord`  
**Django Model:** `predictor.models.ScreeningRecord`  

| Column Name | Django Field Type | Null / Blank | Constraints / Choices | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `UUIDField` | `False / False` | `primary_key=True`, default=`uuid.uuid4` | Anonymous, non-sequential unique identifier. |
| `age` | `PositiveSmallIntegerField` | `False / False` | Range: $[18, 80]$ | Chronological age in years (top-coded at 80). |
| `sex` | `CharField(max_length=10)` | `False / False` | `[('male', 'Male'), ('female', 'Female')]` | Biological sex as recorded in protocol. |
| `bmi` | `DecimalField(4, 1)` | `False / False` | Range: $[11.1, 69.9]$ | Body Mass Index in $\text{kg/m}^2$. |
| `waist_cm` | `DecimalField(4, 1)` | `False / False` | Range: $[60.0, 187.0]$ | Waist circumference in centimeters. |
| `hypertension_history` | `CharField(max_length=5)` | `False / False` | `[('yes', 'Yes'), ('no', 'No')]` | Doctor-diagnosed hypertension history. |
| `smoking_history` | `CharField(max_length=5)` | `False / False` | `[('yes', 'Yes'), ('no', 'No')]` | Smoked $\ge 100$ cigarettes in lifetime. |
| `sedentary_minutes_day` | `PositiveSmallIntegerField`| `False / False` | Range: $[0, 1200]$ | Typical daily sitting/reclining time (min/day). |
| `screening_probability` | `FloatField` | `False / False` | IEEE 754 64-bit float $[0.0, 1.0]$ | Non-laboratory probability from GAM `predict_mu`. |
| `ai_referral_recommended`| `BooleanField` | `False / False` | `True` iff `prob >= 0.1389` | Binary referral decision at locked threshold. |
| `decision_threshold` | `DecimalField(6, 4)` | `False / False` | Default: `0.1389` | Locked research operating point threshold. |
| `model_name` | `CharField(max_length=100)`| `False / False` | Default: `"Phase-5 GAM (λ=10.0, Splines=10)"` | Canonical architecture descriptor. |
| `model_sha256` | `CharField(max_length=64)` | `False / False` | Length: 64 hex characters | SHA-256 checksum of `gam_final.pkl`. |
| `preprocessor_sha256` | `CharField(max_length=64)` | `False / False` | Length: 64 hex characters | SHA-256 checksum of `preprocessor.pkl`. |
| `input_schema_version`| `CharField(max_length=20)` | `False / False` | Default: `"1.0"` | Version of the Stage-1 input schema. |
| `created_at` | `DateTimeField` | `False / False` | `auto_now_add=True` | UTC timestamp of record creation. |
| `idempotency_token` | `CharField(max_length=64)` | `True / True` | `unique=True` | Session token preventing duplicate records. |

---

## 3. Human-Readable Input Semantics

To ensure auditability, transparency, and clinical understandability, inputs are persisted in their canonical semantic forms:
- `sex`: Stored as `"male"` or `"female"` (never internal factor indices `1.0` / `0.0`).
- `hypertension_history`: Stored as `"yes"` or `"no"` (never internal floats `1.0` / `0.0`).
- `smoking_history`: Stored as `"yes"` or `"no"` (never internal floats `1.0` / `0.0`).
- Continuous variables: Stored in natural clinical units (`years`, `kg/m²`, `cm`, `min/day`), never as standardized z-scores.

---

## 4. Full Precision vs. Formatted Probability

- **Database Storage:** Stored as a 64-bit floating point number in `screening_probability` preserving exact mathematical precision from PyGAM.
- **Threshold Comparison:** The decision `ai_referral_recommended` is computed prior to database write using the unrounded probability:
  $$\text{ai\_referral\_recommended} = (\hat{p} \ge 0.1389)$$
- **User Presentation:** Formatted as a single-decimal percentage (e.g., `21.6%` or `3.6%`). This string formatting is purely visual and is never used for comparison.

---

## 5. Result Creation Lifecycle & Transactions

1. **Revalidation:** Client POST data is bound to `Stage1ScreeningForm` and server-side validated again.
2. **Idempotency Check:** If `idempotency_token` exists in the database, the transaction is skipped, and the client is immediately redirected to the existing result.
3. **Inference Execution:** `screening_inference.predict_screening()` evaluates the validated dictionary. If an error occurs, execution halts, rendering an error alert with **zero database modifications**.
4. **Atomic Persistence:** Persistence occurs inside `transaction.atomic()`. Any database write failure triggers an immediate rollback and returns a safe, neutral error to the user.
5. **Post-Redirect-Get:** On successful persistence, a `302 Found` redirect is issued to `/screening/<uuid>/result/`.

---

## 6. Privacy & Data Minimization

In compliance with medical research ethics and privacy standards:
1. **Anonymous Identity:** Screening records use randomly generated UUIDv4 keys. No sequential IDs are exposed.
2. **No PII:** No names, national identity numbers, medical record numbers, dates of birth, phone numbers, or addresses are stored in `ScreeningRecord`.
3. **No Unnecessary Internals:** Scaled feature matrices, spline basis terms, temporary numpy arrays, and raw model weights are not persisted.
