# Phase D2.6 Database Architecture & Schema Audit Report

**Phase:** D2.6  
**Auditor:** Antigravity  
**Database Engine:** SQLite 3 (Django ORM 5.x)  
**Status:** PASSED  
**Governing Skill:** `research-governance`  

---

## 1. Schema Definition & Field Verification

Migration `predictor/migrations/0004_humanreview.py` was generated and executed against the database. The resulting schema for `predictor_humanreview` is:

```sql
CREATE TABLE "predictor_humanreview" (
    "id" char(32) NOT NULL PRIMARY KEY,
    "reviewer_code" varchar(32) NOT NULL,
    "review_action" varchar(20) NOT NULL,
    "final_referral_recommended" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "screening_record_id" char(32) NOT NULL UNIQUE REFERENCES "predictor_screeningrecord" ("id") DEFERRABLE INITIALLY DEFERRED
);
```

### Field-by-Field Audit

| Field | SQLite Type | Nullable | Unique | Constraints & Semantics |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `char(32)` (UUID hex) | `NOT NULL` | `PRIMARY KEY` | Cryptographically random UUIDv4. |
| `screening_record_id` | `char(32)` (UUID hex) | `NOT NULL` | `UNIQUE` | `OneToOneField` with `on_delete=models.PROTECT`. Guarantees exactly one review per screening. |
| `reviewer_code` | `varchar(32)` | `NOT NULL` | No | Anonymous, non-PII reviewer code validated by regex `^[a-zA-Z0-9_-]+$`. |
| `review_action` | `varchar(20)` | `NOT NULL` | No | Stored value: `'accepted'`. Overrides deferred to D2.7. |
| `final_referral_recommended` | `bool` | `NOT NULL` | No | Stored value derived server-side from `screening_record.ai_referral_recommended`. |
| `created_at` | `datetime` | `NOT NULL` | No | UTC creation timestamp (`auto_now_add=True`). |

---

## 2. Relational Integrity & Constraint Verification

1. **One-to-One Strictness:**
   - The `UNIQUE` constraint on `screening_record_id` ensures that a screening record can never have more than one `HumanReview` row in the database.
   - Tested by automated test `test_repeated_post_does_not_duplicate_review_row`.
2. **Deletion Protection (`on_delete=models.PROTECT`):**
   - Attempting to delete a `ScreeningRecord` that has a linked `HumanReview` raises a `django.db.models.deletion.ProtectedError`.
   - Tested by automated test `test_protected_deletion_on_screening_record`.
3. **Foreign Key Integrity:**
   - References `predictor_screeningrecord.id` with referential integrity enforced.
   - Verified that orphaned `HumanReview` rows cannot be inserted.

---

## 3. Audit of Legacy Entities (`predictor_override` & `predictor_prediction`)

Prior to Phase D2.0, the prototype contained legacy models `Prediction` and `Override`:

```python
# Legacy models in predictor/models.py
class Prediction(models.Model):
    # Old integer ID, unverified float inputs
    pass

class Override(models.Model):
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE)
    doctor_name = models.CharField(max_length=100)  # PII VIOLATION
    override_value = models.IntegerField()          # Class flipping violation
    reason = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
```

### Forensic Classification:
- **Class C: LEGACY — DO NOT USE / Class D: ARCHIVE LATER**
- **Defects of Legacy Entity:**
  1. **PII Storage:** Stored unredacted clinician names (`doctor_name`), violating privacy guidelines.
  2. **Non-Unique Foreign Key:** Used `ForeignKey` instead of `OneToOneField`, allowing arbitrary multiple conflicting overrides on the same prediction.
  3. **Class Flipping Semantics:** Stored `override_value = 0 or 1`, implying biological ground-truth flipping rather than research protocol referral decision.
  4. **Cascade Deletion:** Used `on_delete=CASCADE`, destroying audit history if a prediction was removed.
- **Architectural Isolation:**
  - `HumanReview` does not import, reference, or interact with `Override` or `Prediction`.
  - The new clinical review pipeline operates exclusively on `ScreeningRecord` and `ScreeningExplanation`.
  - Legacy models remain unreferenced and dormant.

---

## 4. Performance & Index Analysis

- `predictor_humanreview.id`: Primary key B-tree index (lookup $O(1)$).
- `predictor_humanreview.screening_record_id`: Unique B-tree index, providing immediate $O(1)$ relational retrieval when rendering `screening_result_view`.
- Zero table scans or N+1 query patterns are introduced by the review integration.
