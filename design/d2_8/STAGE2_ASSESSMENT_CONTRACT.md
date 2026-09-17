# Stage-2 HbA1c Assessment Contract — Data Specification & Governance Rules

## 1. Domain Purpose & Philosophy
The `Stage2Assessment` entity completes the research prototype's two-stage screening cascade:
$$\text{Stage-1 Non-Lab Screening} \longrightarrow \text{Frozen GAM Result} \longrightarrow \text{GAM-Native Explanation} \longrightarrow \text{Human Review} \longrightarrow \text{Final Human Referral Decision} \longrightarrow \text{If Refer: Stage-2 HbA1c Laboratory Assessment} \longrightarrow \text{Laboratory Range}$$

### Epistemic Declaration
> **Stage2Assessment records an entered HbA1c value and its laboratory-range classification. It does not represent an automated clinical diagnosis.**

Stage 2 is **NOT** a machine learning model, executes zero GAM inference calls, zero preprocessing calls, and zero XAI calculations. It deterministically categorizes an entered percentage into an authoritative laboratory range category.

---

## 2. Eligibility & Workflow Gates
Stage 2 entry and persistence are governed by strict prerequisite constraints:
1. `ScreeningRecord` exists and is immutable.
2. `ScreeningExplanation` is generated with verified additive fidelity.
3. `HumanReview` is finalized (exists and is immutable).
4. `HumanReview.final_referral_recommended == True`.

### Decision Permutations
| AI Recommendation | Human Review Action | Final Human Decision | Stage-2 Eligibility |
| :--- | :--- | :--- | :--- |
| **Refer** | **Accepted** | **Refer** | **Eligible** (Authorized) |
| **No Refer** | **Overridden** | **Refer** | **Eligible** (Authorized) |
| **Refer** | **Overridden** | **Do Not Refer** | **Blocked** (Unavailable) |
| **No Refer** | **Accepted** | **Do Not Refer** | **Blocked** (Unavailable) |

If `final_referral_recommended == False`, Stage-2 UI entry points are omitted, and direct route access triggers a workflow-safe redirect to `screening_result` with an explanatory notice.

---

## 3. Entity Specification: `Stage2Assessment`

### Relational Architecture
- `human_review`: `OneToOneField(HumanReview, on_delete=models.PROTECT, related_name='stage2_assessment')`
  - *Rationale:* Stage 2 occurs strictly as a consequence of the finalized human referral decision. Attaching to `HumanReview` guarantees complete auditability of the authorizing decision.

### Schema Fields
| Field Name | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUIDField` | Primary key, default `uuid.uuid4`, editable=False | Unique anonymous identifier |
| `human_review` | `OneToOneField` | `on_delete=PROTECT`, `related_name='stage2_assessment'` | Authorizing human review record |
| `hba1c_percent` | `DecimalField` | `max_digits=4, decimal_places=2` | Validated HbA1c percentage |
| `laboratory_range` | `CharField` | `max_length=32`, choices: `normal_range`, `prediabetes_range`, `diabetes_range` | Server-derived laboratory range category |
| `range_rule_version` | `CharField` | `max_length=64`, default `ADA_2026_A1C_RANGE_V1` | Stamped reference rule version |
| `entry_method` | `CharField` | `max_length=20`, default `'manual'` | Provenance entry method |
| `created_at` | `DateTimeField` | `auto_now_add=True` | Timestamp of confirmation |

### Prohibited Fields
The following fields are strictly prohibited from `Stage2Assessment`:
- `diagnosis`
- `diabetes_status`
- `confirmed_diabetes`
- `disease_truth`
- `AI_stage2_probability`
- `second_model_prediction`

---

## 4. Range Boundaries & Exact Decimal Arithmetic

Classification is performed using Python's `Decimal` module to prevent floating-point representation drift:

```python
NORMAL_THRESHOLD = Decimal("5.7")
DIABETES_THRESHOLD = Decimal("6.5")

if hba1c < NORMAL_THRESHOLD:
    range_code = "normal_range"
elif hba1c < DIABETES_THRESHOLD:
    range_code = "prediabetes_range"
else:
    range_code = "diabetes_range"
```

### Boundary Verification Targets
- `5.69%` $\to$ `normal_range`
- `5.70%` $\to$ `prediabetes_range`
- `6.49%` $\to$ `prediabetes_range`
- `6.50%` $\to$ `diabetes_range`
- Exact `5.7%` $\to$ `prediabetes_range`
- Exact `6.5%` $\to$ `diabetes_range`

---

## 5. Input Safety & Anti-Tampering Rules

### Mathematical Input Bounds
- Minimum: `2.00%`
- Maximum: `25.00%`
- Must be positive, finite Decimal number.
- Floats, strings, NaN, infinity, and negative numbers are rejected with `HbA1cValidationError`.

### Server-Derived Authority
- The browser must **never** submit an authoritative `laboratory_range` or `range_rule_version`.
- Any client attempts to submit `laboratory_range`, `range_rule_version`, `diagnosis`, or `confirmed_diabetes` are discarded. The server independently derives the category from the validated Decimal value using `classify_hba1c_range()`.

---

## 6. Two-Step Review Pattern & Immutability
To protect against accidental user keystrokes:
1. **Entry Step:** Reviewer enters numeric HbA1c value $\to$ POST to `/stage2/`.
2. **Review Step:** Server validates value and derives preliminary range $\to$ renders review state displaying entered value, category, an `[Edit]` button, and a `[Confirm Laboratory Result]` button. No persistence occurs at this step.
3. **Confirmation Step:** Reviewer clicks confirm $\to$ POST to `/stage2/confirm/` $\to$ revalidates server-side and atomically creates `Stage2Assessment`.
4. **Post-Confirmation Immutability:** Once confirmed, `Stage2Assessment` is permanently read-only in the UI. No editing or deletion controls are presented. Double submissions idempotently redirect to the completed result.
