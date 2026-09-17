# Existing Application Architecture Audit

**Phase:** D1 — Design Foundation  
**Target Repository:** `dashboard/` (`c:\Users\Felix\Documents\Skripsi\dashboard`)  
**Audit Date:** 2026-09-04  
**Auditor:** Antigravity Research Agent  

---

## 1. Executive Summary

This audit establishes the baseline technical architecture of the existing dashboard implementation in `dashboard/`. The current codebase is an early proof-of-concept developed prior to the completion of the canonical Phase-2/3 NHANES data engineering and Phase-4/5 Generalized Additive Model (GAM) research evaluation. Consequently, the existing application relies on deprecated Kaggle models, obsolete 8-feature schemas (which incorrectly include laboratory markers in non-laboratory screening), uncalibrated threshold sliders, and diagnostic terminology that directly contradicts the frozen research methodology.

---

## 2. Backend Architecture

### 2.1 Runtime & Framework
- **Python Runtime:** Python 3.10.11 (located at `C:\Users\Felix\AppData\Local\Programs\Python\Python310\python.exe`)
- **Django Version:** Django 5.2.12 (`django-admin startproject` baseline)
- **WSGI / ASGI:** Standard Django WSGI (`dashboard/wsgi.py`) and ASGI (`dashboard/asgi.py`) modules present.
- **Database:** SQLite 3 (`BASE_DIR / 'db.sqlite3'`) configured as `'default'`.

### 2.2 Installed Applications
Defined in `dashboard/settings.py` (`INSTALLED_APPS`):
- `django.contrib.admin`
- `django.contrib.auth`
- `django.contrib.contenttypes`
- `django.contrib.sessions`
- `django.contrib.messages`
- `django.contrib.staticfiles`
- `predictor` (primary custom application)

### 2.3 Authentication & Authorization
- Django Auth middleware is active in `settings.py`.
- **Finding:** No authentication or role-based access control (RBAC) is enforced on `predictor` views. All views (`index`, `predict_view`, `prediction_detail_view`, `override_view`, `history_view`, `evaluation_view`, `analytics_view`) are publicly accessible without login.
- `/admin/` is mapped in `dashboard/urls.py` but linked via external target `_blank`.

### 2.4 Data Models (`predictor/models.py`)
The existing database schema consists of two models:

#### Model 1: `Prediction`
| Field | Type | Description in Code | Identified Defect / Conflict |
| :--- | :--- | :--- | :--- |
| `timestamp` | `DateTimeField(auto_now_add=True)` | Record creation timestamp | None |
| `patient_data` | `JSONField` | JSON object with 8 keys: `gender`, `age`, `hypertension`, `heart_disease`, `smoking`, `bmi`, `HbA1c`, `glucose` | **P0 Flaw:** Retains obsolete Kaggle features. Includes laboratory markers (`HbA1c`, `glucose`) in non-laboratory Stage-1 screening. |
| `model_used` | `CharField(max_length=100)` | Model name (e.g., 'DLNN Baseline', 'DLNN + Focal Loss') | **P0 Flaw:** Promotes user-selectable models and deprecated DLNNs. |
| `prediction` | `IntegerField` | Binary prediction: 0 = Not Diabetic, 1 = Diabetic | **P1 Flaw:** Uses diagnostic disease language ("Diabetic") rather than screening risk signal. |
| `confidence` | `FloatField` | Model probability (0.0 to 1.0) | Misnamed: represents raw probability for positive class or (1 - prob) for negative class. |
| `threshold` | `FloatField(default=0.5)` | Classification threshold | **P0 Flaw:** Allows dynamic/arbitrary threshold (default 0.50) instead of frozen 0.1389. |
| `shap_values` | `JSONField(null=True, blank=True)` | Feature SHAP values | Derived from KernelExplainer on obsolete model. |
| `is_reviewed` | `BooleanField(default=False)` | Doctor review flag | Binary flag; lacks multi-stage tracking. |

#### Model 2: `Override`
| Field | Type | Description in Code | Identified Defect / Conflict |
| :--- | :--- | :--- | :--- |
| `prediction` | `ForeignKey(Prediction)` | Target prediction relationship | Cascade delete on prediction deletion. |
| `timestamp` | `DateTimeField(auto_now_add=True)` | Override submission timestamp | None |
| `doctor_name` | `CharField(max_length=200)` | Reviewer name | Free-form string; no user account or role validation. |
| `decision` | `CharField(choices=[('accept', 'Accept'), ('reject', 'Reject')])` | Doctor's review choice | Restrictive binary accept/reject. |
| `override_value` | `IntegerField(null=True, blank=True)` | Corrected prediction (0 or 1) | **P0 Flaw:** Overturns biological disease status (`0 if pred == 1 else 1`) instead of modifying referral recommendation. |
| `reason` | `TextField(blank=True)` | Clinical reason for override | Free text; not enforced deterministically. |
| `flagged_features` | `JSONField(null=True, blank=True)` | List of disputed features | Unstructured list of feature names. |

### 2.5 View Layer & Endpoints (`predictor/views.py`, `predictor/urls.py`)
- `''` (`predictor:index`): Renders patient form with model selection dropdown and threshold input.
- `'predict/'` (`predictor:predict`): Processes form POST, executes model inference via `model_loader.predict()`, attempts SHAP explanation, persists `Prediction`, redirects to detail.
- `'prediction/<int:pk>/'` (`predictor:prediction_detail`): Shows result card, confidence meter, "dynamic multi-model consensus" badge (DLNN vs GAM), SHAP bar chart, patient summary, and override submission form.
- `'override/'` (`predictor:override`): Processes override POST, computes `override_value = 0 if prediction.prediction == 1 else 1`, marks `is_reviewed = True`, redirects to history.
- `'history/'` (`predictor:history`): Displays paginated/filtered table of all predictions and overrides.
- `'evaluation/'` (`predictor:evaluation`): Reads deprecated `models/results.csv` and renders Kaggle model benchmark comparison table.
- `'analytics/'` (`predictor:analytics`): Aggregates model usage, override rate, and flagged features. Contains mathematical denominator bug.

---

## 3. Frontend Architecture

### 3.1 Template Architecture
- Location: `dashboard/predictor/templates/predictor/`
- Inheritance: Standard Django template inheritance via `{% extends "predictor/base.html" %}`.
- Templates present:
  - `base.html`: Shell containing sidebar, topbar, theme-toggle script, messages, and content block.
  - `index.html`: Two-column grid with patient input form and sidebar statistics card.
  - `result.html`: Two-column layout with 3-tier risk card, consensus badge, patient summary, SHAP canvas, and override form.
  - `history.html`: Table displaying historical records with status filter tabs.
  - `evaluation.html`: Comparative evaluation metrics table and best-performer highlights.
  - `analytics.html`: Chart.js visualizations for model usage, override rate, and flagged features.

### 3.2 Styling & Design Tokens
- **Framework:** 100% Custom Vanilla CSS (`dashboard/predictor/static/predictor/css/style.css`, 1,256 lines).
- **Bootstrap Presence:** None.
- **Tailwind Presence:** None.
- **Theme Support:** Dark/Light mode implemented via CSS Custom Properties on `:root` and `[data-theme="dark"]` / `[data-theme="light"]`, controlled by inline JavaScript and `localStorage`.
- **Aesthetic Direction:** Heavy glassmorphism (`backdrop-filter: blur(12px)`, `rgba(...)` background cards, multi-color vibrant gradient accents `--gradient-risk`, `--gradient-safe`, `--gradient-primary`, saturated red/green/blue).
- **Typography:** Google Font `Inter` (`wght@300;400;500;600;700;800`).
- **Icons:** Raw Unicode emojis throughout HTML templates (`🔬`, `📋`, `🏆`, `📊`, `⚙️`, `🌙`, `🚨`, `⚠️`, `✅`, `👨‍⚕️`, `⚖️`).

### 3.3 Client-Side Logic & Libraries
- **JavaScript:** Custom vanilla script (`static/predictor/js/main.js`) handling sidebar toggle, theme switching, dynamic threshold display, and override form expansion.
- **Charting Library:** Chart.js v4.4.0 loaded via CDN (`https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js`).
- **Frameworks:** No React, Vue, HTMX, or Alpine.js is present.

---

## 4. Machine Learning Integration Architecture

### 4.1 Model Loading (`predictor/model_loader.py`)
- Models Directory: Points to obsolete `Skripsi/models/` instead of canonical `nhanes_feasibility_2021_2023/models_phase5/`.
- Model Registry: Contains six deprecated models (`DLNN Baseline`, `DLNN + Class Weights`, `DLNN + SMOTE`, `DLNN + Focal Loss`, `DLNN + SMOTE + Focal Loss`, and a rudimentary `GAM`).
- Scaler Loading: Loads obsolete `scaler_A.pkl` and `scaler_recall_improvement.pkl`.
- Feature Schema: Hardcoded to 8 Kaggle features (`gender`, `age`, `hypertension`, `heart_disease`, `smoking`, `bmi`, `HbA1c`, `glucose`).

### 4.2 Inference Logic
- Method: `predict(model_name, features_dict, threshold=0.5)`
- Scaling: Applies `scaler.transform()` to input array.
- Thresholding: Evaluates `probability >= threshold` dynamically, defaulting to 0.50.

### 4.3 Explainability (`predictor/shap_explainer.py`)
- Approach: `shap.KernelExplainer` wrapping Keras/sklearn models.
- Background Data: Samples 100 rows on the fly from `Skripsi/clean_dataset.csv` (Kaggle dataset).
- Fault Tolerance: Hardcoded zero fallback (`shap_values: 0.0 for all features`) with fallback base value `0.5` upon exception.

---

## 5. Architectural Assessment for Redesign

1. **Backend Soundness:** The Django 5.2 application structure is clean, standard, and robust. It provides a reliable foundation for serving server-rendered templates, managing database transactions, and executing Python-native ML inference.
2. **Decoupling Requirement:** The frontend view logic and database models are currently tightly coupled to Kaggle dataset features and diagnostic assumptions. These require refactoring to support the two-stage NHANES non-laboratory protocol.
3. **No External Framework Debt:** Because the application does not currently rely on React, Vue, or complex build pipelines, adopting a shadcn/ui-inspired design system within Django templates can be achieved without introducing heavy Node.js dependencies.
