# Phase D2.7 Preflight Governance Corrections Audit

**Document Version:** 1.0  
**Phase:** D2.7 Preflight  
**Date:** 2026-09-04  
**Governing Skill:** `research-governance` (Highest Precedence)  

---

## 1. Overview & Purpose

Prior to expanding the Human Review foundation into the Human Override workflow, an audit of Phase D2.6 identified two documentation and schema items requiring precision hardening:
1. Reviewer Code Language & PII Claims.
2. Review Action Default & Choices.

Neither of these corrections expands scope; they ensure strict adherence to research governance and reproducibility standards.

---

## 2. Correction A: Reviewer Code Language & Privacy Semantics

### Finding:
In Phase D2.6 documentation, certain passages claimed that the reviewer-code validation regex (`^[a-zA-Z0-9_-]+$`) "rejects personal names" or "ensures no personal names are entered." 

### Corrective Standard:
An alphanumeric character regex restricts input syntax and disallows spaces, punctuation, or script injection. It **cannot and does not** prove whether a submitted string (e.g. `JOHN`, `SMITH1`, `FELIX`) is a person's name or not. The system must not claim automated PII detection.

### Standardized Guidance & Instruction:
- **System Description:**
  > *"The system requests a pseudonymous reviewer code and does not require personally identifying information."*
- **Reviewer-Study User Instructions:**
  > *"Use the reviewer code assigned for this study. Do not enter your name or other identifying information."*
- **Implementation:**
  - Form and template helper text have been updated to reflect this precise instruction.
  - All documentation claims attributing PII filtering to regular expression validation are formally retracted and superseded by this specification.

---

## 3. Correction B: Review Action Choices & Removal of Implicit Default

### Finding:
In `predictor/models.py` (Phase D2.6), `HumanReview.review_action` was declared with `default='accepted'`.

```python
# D2.6 Model Definition
review_action = models.CharField(
    max_length=20,
    choices=ACTION_CHOICES,
    default='accepted',
    help_text="Reviewer action: for Phase D2.6, strictly 'accepted'"
)
```

### Risk:
An implicit default allows unpopulated or missing review actions to silently become `"accepted"` without explicit programmatic intent.

### Corrective Standard:
1. Remove `default='accepted'`.
2. Explicitly define choices:
   ```python
   REVIEW_ACTION_CHOICES = [
       ('accepted', 'Accepted Recommendation'),
       ('overridden', 'Overridden Recommendation'),
   ]
   ```
3. Ensure no record can be instantiated without explicitly declaring whether the action is `'accepted'` or `'overridden'`.
4. Existing D2.6 database records with `'accepted'` remain valid and uncorrupted.
5. Apply this change in migration `0005_humanreview_override_fields.py`.
