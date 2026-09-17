# Phase D2.7 Database Architecture & Migration Audit Report

**Phase:** D2.7  
**Auditor:** Antigravity  
**Database Engine:** SQLite 3 (Django ORM 5.x)  
**Status:** PASSED & VERIFIED  
**Governing Skill:** `research-governance`  

---

## 1. Migration Specification: `0005_humanreview_override_note_and_more.py`

Django migration `predictor/migrations/0005_humanreview_override_note_and_more.py` was generated and applied to the database.

### Operations Applied:
1. `AddField(model_name='humanreview', name='override_note', field=models.TextField(blank=True, max_length=500, null=True))`
2. `AddField(model_name='humanreview', name='override_reason_code', field=models.CharField(blank=True, max_length=64, null=True))`
3. `AlterField(model_name='humanreview', name='final_referral_recommended', field=models.BooleanField(help_text='Final referral decision derived server-side'))`
4. `AlterField(model_name='humanreview', name='review_action', field=models.CharField(choices=[('accepted', 'Accepted Recommendation'), ('overridden', 'Overridden Recommendation')], max_length=20))`
5. `AlterField(model_name='humanreview', name='screening_record', field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='human_review', to='predictor.screeningrecord'))`

---

## 2. Updated Table Schema: `predictor_humanreview`

```sql
CREATE TABLE "predictor_humanreview" (
    "id" char(32) NOT NULL PRIMARY KEY,
    "reviewer_code" varchar(32) NOT NULL,
    "review_action" varchar(20) NOT NULL,
    "final_referral_recommended" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "screening_record_id" char(32) NOT NULL UNIQUE REFERENCES "predictor_screeningrecord" ("id") DEFERRABLE INITIALLY DEFERRED,
    "override_note" text NULL,
    "override_reason_code" varchar(64) NULL
);
```

---

## 3. Audit of Schema Constraints & Invariants

| Constraint / Invariant | Implementation Mechanism | Verification Result |
| :--- | :--- | :--- |
| **No Implicit Default Action** | Removed `default='accepted'` from `review_action`. Must be explicitly declared. | **VERIFIED:** Attempting to create without `review_action` fails. |
| **Backward Compatibility** | Existing D2.6 rows retain `review_action='accepted'`, with `override_note=NULL` and `override_reason_code=NULL`. | **VERIFIED:** 54 existing tests passed without schema errors. |
| **Single Review per Screening** | `UNIQUE` constraint on `screening_record_id` (`OneToOneField`). | **VERIFIED:** Duplicate submissions blocked. |
| **Deletion Protection** | `on_delete=models.PROTECT` on `screening_record`. | **VERIFIED:** Cannot delete reviewed screening records. |
| **Reason Code Validation** | Dynamic branch-specific choice checking in Form and Model `clean()`. | **VERIFIED:** Cross-branch reasons rejected. |
| **Mandatory Note for "Other"** | Enforced in Form and Model `clean()`. | **VERIFIED:** Empty note rejected when code is `'other'`. |

---

## 4. Isolation of Legacy Prototype Models

- The legacy `predictor_override` and `predictor_prediction` tables remain completely isolated from the active screening and review pipeline.
- `HumanReview` does not import, foreign-key, or interact with `Override`.
- No legacy migrations or schemas were mutated.
