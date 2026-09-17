# D3 Legacy Route & Dead Code Path Audit

**Audit Date:** 2026-09-05  
**Objective:** Verify that legacy workflows from Phase D1 cannot participate in, contaminate, or be reached from the formal two-stage screening study workflow.

---

## 1. Global Route Classification

Every route registered in `dashboard/predictor/urls.py` was evaluated and classified into one of four governance tiers:

| Route Path | View Function | Classification | Justification / Protection Status |
| :--- | :--- | :--- | :--- |
| `/` | `overview_view` | **PRODUCTION-RESEARCH ACTIVE** | Main orientation shell (Phase D2.1/D2.9). Read-only. |
| `/screening/new/` | `new_screening_view` | **PRODUCTION-RESEARCH ACTIVE** | Stage-1 participant intake form (Phase D2.2). |
| `/screening/run/` | `run_screening_view` | **PRODUCTION-RESEARCH ACTIVE** | Authoritative model inference & GAM XAI persistence (Phase D2.3–D2.5). POST-only. |
| `/screening/<uuid>/result/` | `screening_result_view` | **PRODUCTION-RESEARCH ACTIVE** | Screening result & GAM-native XAI visualization (Phase D2.4/D2.5). Read-only. |
| `/screening/<uuid>/review/accept/` | `accept_review_view` | **PRODUCTION-RESEARCH ACTIVE** | Human review acceptance endpoint (Phase D2.6). POST-only. |
| `/screening/<uuid>/review/override/` | `override_review_view` | **PRODUCTION-RESEARCH ACTIVE** | Human review override endpoint (Phase D2.7). POST-only. |
| `/screening/<uuid>/stage2/` | `stage2_view` | **PRODUCTION-RESEARCH ACTIVE** | Stage-2 HbA1c entry & result presentation (Phase D2.8). |
| `/screening/<uuid>/stage2/confirm/` | `stage2_confirm_view` | **PRODUCTION-RESEARCH ACTIVE** | Stage-2 persistence endpoint (Phase D2.8). POST-only. |
| `/review/` | `review_queue_view` | **PRODUCTION-RESEARCH ACTIVE** | Operational task queue for pending reviews (Phase D2.9). Read-only. |
| `/history/` | `history_view` | **PRODUCTION-RESEARCH ACTIVE** | Auditable screening history table (Phase D2.9). Read-only. |
| `/analytics/` | `analytics_view` | **PRODUCTION-RESEARCH ACTIVE** | Aggregate research workflow metrics & transition matrix (Phase D2.10). Read-only. |
| `/about/` | `about_model_view` | **PRODUCTION-RESEARCH ACTIVE** | Model specification, held-out evaluation & governance caveats. Read-only. |
| `/components/` | `components_demo_view` | **DEVELOPMENT ONLY** | Design system component demo. **Isolated:** suppressed from sidebar and mobile navigation in `study` mode. |
| `/index/` | `index` | **DEAD CODE / QUARANTINED** | Legacy D1 multi-model intake. Omitted from all navigation and templates. |
| `/predict/` | `predict_view` | **DEAD CODE / QUARANTINED** | Legacy D1 unvalidated DLNN endpoint. Zero calls from active templates. |
| `/prediction/<int:pk>/` | `prediction_detail_view` | **DEAD CODE / QUARANTINED** | Legacy D1 integer-keyed prediction view. Omitted from navigation. |
| `/override/` | `override_view` | **DEAD CODE / QUARANTINED** | Legacy D1 unvalidated doctor override table. Omitted from navigation. |
| `/evaluation/` | `evaluation_view` | **DEAD CODE / QUARANTINED** | Legacy D1 confusion matrix calculator. Omitted from navigation. |

---

## 2. Model & Explainer Isolation

1. **Legacy DLNN & Focal Loss Models:** The legacy `Prediction` and `Override` models (integer PKs, `doctor_name`, `confidence`) remain in database schema only for non-destructive migration history. No active screening route queries, creates, or renders records from these tables.
2. **SHAP KernelExplainer Isolation:** The legacy file `shap_explainer.py` is never called by the Stage-1 workflow. The active workflow strictly executes `screening_explanation.py` (GAM-native additive decomposition on the log-odds scale).
3. **Multi-Model / Slider Quarantine:** No user-facing threshold slider or model selection drop-down exists in any active template. The operating model is locked to `gam_final.pkl` and threshold `0.1389`.
