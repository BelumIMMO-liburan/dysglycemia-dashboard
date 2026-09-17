# Phase D2.2 Validation Audit Report
**Phase:** D2.2 — Stage-1 Non-Laboratory Screening Form  
**Audit Scope:** Server-side validation rules, development-domain range enforcement, missing value rejection, and sentinel handling.  
**Date:** September 4, 2026  
**Status:** ALL 12 VALIDATION TEST SUITES PASSED (100% COMPLIANT)

---

## 1. Validation Authority & Domain Boundaries

The validation bounds are grounded strictly in the **development partition** ($N = 3,232$) documented in [`FINAL_MODEL_SPECIFICATION_LOCKED.md`](file:///c:/Users/Felix/Documents/Skripsi/nhanes_feasibility_2021_2023/lock_phase4_2/FINAL_MODEL_SPECIFICATION_LOCKED.md) Section 3.2. 

The application strictly forbids silent extrapolation beyond the model's supported research domain. Missing values are never imputed.

---

## 2. Exhaustive Boundary & Rule Matrix

| Field | Expected Type | Min Bound | Max Bound | Allowed Step | Sentinel Codes Rejected | Validation Rule & Error Copy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `age` | Integer | 18 | 80 | 1 year | None | $18 \le \text{age} \le 80$. "Age is below/above the model-supported research range." |
| `sex` | Categorical | N/A | N/A | N/A | None | Strict membership in `['male', 'female']`. "Select a valid choice (Male or Female)." |
| `bmi` | Float | 11.1 | 69.9 | 0.1 | None | $11.1 \le \text{bmi} \le 69.9$, rounded to 1 decimal. "BMI is outside the range supported by the research model." |
| `waist_cm` | Float | 60.0 | 187.0 | 0.1 | None | $60.0 \le \text{waist} \le 187.0$, rounded to 1 decimal. "Waist circumference is outside the range supported by the research model." |
| `hypertension_history` | Categorical | N/A | N/A | N/A | None | Strict membership in `['yes', 'no']`. "Select a valid choice (Yes or No)." |
| `smoking_history` | Categorical | N/A | N/A | N/A | None | Strict membership in `['yes', 'no']`. "Select a valid choice (Yes or No)." |
| `sedentary_minutes_day` | Integer | 0 | 1200 | 1 min/day | `7777`, `9999` | $0 \le \text{sedentary} \le 1200$. Explicit rejection of NHANES sentinel missing codes `7777` (refused) and `9999` (don't know). |

---

## 3. Automated Test Execution Results

All test cases were executed via Django test runner (`python manage.py test predictor`):

```
Creating test database for alias 'default'...
............
----------------------------------------------------------------------
Ran 12 tests in 0.056s

OK
Destroying test database for alias 'default'...
Found 12 test(s).
System check identified no issues (0 silenced).
```

### Detailed Test Coverage Breakdown

1. **`test_valid_payload_passes`**: Confirmed complete valid payload (`age=52, sex=male, bmi=28.4, waist_cm=98.5, hypertension_history=yes, smoking_history=no, sedentary_minutes_day=480`) passes validation and generates sanitized summary with formatted units.
2. **`test_all_fields_are_required`**: Confirmed empty submission triggers exactly 7 field errors.
3. **`test_age_boundaries`**: Tested lower bound (17 rejected, 18 accepted) and upper bound (80 accepted, 81 rejected).
4. **`test_sex_choices`**: Tested `'female'` accepted, unmodeled `'other'` rejected.
5. **`test_bmi_boundaries`**: Tested lower bound (11.0 rejected, 11.1 accepted) and upper bound (69.9 accepted, 70.0 rejected).
6. **`test_waist_boundaries`**: Tested lower bound (59.9 rejected, 60.0 accepted) and upper bound (187.0 accepted, 187.1 rejected).
7. **`test_hypertension_history_choices`**: Tested `'no'` accepted, unapproved strings rejected.
8. **`test_smoking_history_choices`**: Tested `'yes'` accepted, unapproved strings rejected.
9. **`test_sedentary_minutes_boundaries_and_sentinels`**: Tested 0 accepted, 1200 accepted, negative rejected, 1201 rejected, and sentinel codes `7777` & `9999` explicitly rejected.
10. **`test_get_new_screening_page`**: Tested GET returns HTTP 200, semantic form title, all 7 field labels, units, and buttons.
11. **`test_valid_post_renders_input_review_state`**: Tested POST renders Input Review State without creating any database rows (`Prediction.objects.count() == 0`) and without calculating any probability score.
12. **`test_invalid_post_renders_error_summary_and_field_errors`**: Tested POST with errors renders top-level `#error-summary`, sets `aria-invalid="true"`, and preserves valid inputs.

---

## 4. Client-Side vs Server-Side Validation Synergy

1. **HTML5 Constraints:** `min`, `max`, `step`, and `required` attributes are set on numeric input elements for immediate browser feedback.
2. **Authoritative Server-Side Validation:** The form contains `novalidate` to ensure all submissions pass through Django's `Stage1ScreeningForm` server-side clean methods. Client-side tampering cannot bypass bounds.
3. **Preservation of Valid Data:** When validation errors occur, previously entered valid field values are preserved in the form inputs so the user never re-enters correct parameters.
