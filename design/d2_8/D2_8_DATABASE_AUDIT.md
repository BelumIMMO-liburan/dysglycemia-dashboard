# Phase D2.8 Database & Migration Audit

## 1. Migration Overview
- **Migration Identifier:** `predictor.0006_stage2assessment`
- **File Path:** `dashboard/predictor/migrations/0006_stage2assessment.py`
- **Dependency:** `predictor.0005_humanreview_override_note_and_more`
- **Operations:** `CreateModel(name='Stage2Assessment')`

---

## 2. Table Definition: `predictor_stage2assessment`

| Column Name | SQL Datatype | Nullable | Default | Description / Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `char(32)` / `UUID` | No | `uuid.uuid4` | Primary key |
| `human_review_id` | `char(32)` / `UUID` | No | None | Foreign Key referencing `predictor_humanreview(id)`, `UNIQUE` (OneToOne), `ON DELETE PROTECT` |
| `hba1c_percent` | `decimal(4, 2)` | No | None | Numerical laboratory measurement percentage |
| `laboratory_range` | `varchar(32)` | No | None | Categorical range code (`normal_range`, `prediabetes_range`, `diabetes_range`) |
| `range_rule_version` | `varchar(64)` | No | `'ADA_2026_A1C_RANGE_V1'` | Frozen reference standard identifier |
| `entry_method` | `varchar(20)` | No | `'manual'` | Provenance entry method |
| `created_at` | `datetime` | No | `auto_now_add` | Confirmation timestamp |

---

## 3. Relational Integrity & Cascades
- **Parent Table:** `predictor_humanreview`
- **Constraint:** `OneToOneField` creates a `UNIQUE` index on `human_review_id`.
- **Deletion Behavior:** `on_delete=models.PROTECT`. If an authorized reviewer or researcher attempts to delete a `HumanReview` that has an associated `Stage2Assessment`, the database raises `ProtectedError` to prevent silent audit trail destruction.

---

## 4. Invariant Checks
1. `human_review_id` is unique: Verified via unit test `test_one_to_one_relation_enforced`.
2. Prohibited fields absent: Verified via unit test `test_prohibited_fields_absent`.
3. Non-null constraints enforced across all essential fields.
4. Schema migrations execute cleanly: `python manage.py check` reports 0 silenced issues.
