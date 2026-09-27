# Dysglycemia Screening Decision Dashboard

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![Tests](https://img.shields.io/badge/Tests-224%20Passing-brightgreen.svg)]()
[![Notebooks](https://img.shields.io/badge/CRISP--DM%20Notebooks-9%20Passing-brightgreen.svg)]()
[![Model Baseline](https://img.shields.io/badge/GAM--v1-Frozen%20Locked-orange.svg)]()

> **"Decision Dashboard berbasis Explainable AI dan Human Override dengan Pendekatan Two-Stage Screening untuk Risiko Disglikemia"**

An academic research prototype and clinical decision-support system for non-laboratory screening of unrecognized dysglycemia ($\text{HbA1c} \ge 5.7\%$) in adults aged $\ge 18$ without previously diagnosed diabetes or prediabetes, developed using the NHANES 2021–2023 population cohort.

---

## 1. Key Research Specifications & Baseline

- **Primary Screening Model:** Generalized Additive Model (`LogisticGAM`) with cubic splines on continuous features and factor terms on categorical features.
  - Intercept ($\beta_0$): `-0.729147`
  - SHA-256 Model Hash: `204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d`
  - SHA-256 Preprocessor Hash: `6e56a01993a4a6971eb62c82699c49da6f31a3acec2a1169e07862409f42824d`
- **Locked Operating Point:** Decision threshold $\tau = 0.1389$ (calibrated strictly on the $N=3,232$ Development Cohort to satisfy a $\ge 90\%$ clinical sensitivity floor).
- **Held-Out Confirmatory Test Performance ($N=812$):**
  - Sensitivity: **86.39%** (95% Bootstrap CI: 81.19% – 90.96%)
  - Specificity: **42.51%** (95% Bootstrap CI: 38.57% – 46.37%)
  - ROC-AUC: **0.7277** (95% Bootstrap CI: 0.6875 – 0.7656)
  - PR-AUC: **0.4503** (95% Bootstrap CI: 0.3843 – 0.5210)
  - Brier Score: **0.1587** (95% Bootstrap CI: 0.1438 – 0.1729)

---

## 2. Dual-Mode Architecture

The prototype operates under a **Single-Codebase, Dual-Mode Architecture** controlled by the `APP_MODE` environment variable:

```
+-----------------------------------------------------------------------------------+
|                                  SINGLE CODEBASE                                  |
+-----------------------------------------+-----------------------------------------+
|        APP_MODE=evaluation             |         APP_MODE=feedback_lab          |
|        (Public / Railway Hosted)        |         (Localhost Researcher)          |
+-----------------------------------------+-----------------------------------------+
| * Isolated Database: db_evaluation      | * Research Database: db.sqlite3         |
| * Participant Onboarding & Study Flow   | * Full Researcher Administration Suite  |
| * Informed Consent & Demographics       | * Review Queue, History, Analytics      |
| * Practice Case P0 Guided Tour          | * Case A -> Feedback Learning Pipeline  |
| * 4-Part Evaluation Questionnaire       | * 8-D Residual Adaptation Training      |
|   - 8 Comprehension items (C1-C8)       | * 13 Automated Technical Checks         |
|   - 10 Indonesian SUS items (S1-S10)    | * Case B Comparative Inference          |
|   - 5 Dashboard Clarity items (DQ1-DQ5) | * Zero Final-Test Leakage Enforcement   |
|   - 3 Qualitative Feedback items        | * Candidate Activation & Rollback       |
| * Researcher routes: 403 Forbidden      | * Full Auditability & Dual Outputs      |
| * Participant feedback EXCLUDED from    |                                         |
|   learning loops                        |                                         |
+-----------------------------------------+-----------------------------------------+
```

---

## 3. Directory Layout

```text
dysglycemia-dashboard/
├── .env.example                     # Environment configuration template
├── .gitignore                       # Clean ignore rules (no secrets/databases/caches)
├── Procfile                         # Production deployment process definition
├── runtime.txt                      # Python runtime specification (3.10.12)
├── requirements.txt                 # Complete project dependencies
├── README.md                        # This project documentation
├── CRISP_DM_NOTEBOOKS/              # 9 Official CRISP-DM methodology notebooks
│   ├── 00_README_CRISP_DM.ipynb
│   ├── 01_BUSINESS_UNDERSTANDING.ipynb
│   ├── 02_DATA_UNDERSTANDING.ipynb
│   ├── 03_DATA_PREPARATION.ipynb
│   ├── 04_MODELING.ipynb
│   ├── 05_THRESHOLD_SELECTION.ipynb
│   ├── 06_FINAL_EVALUATION.ipynb
│   ├── 07_XAI_HUMAN_REVIEW.ipynb     # Feedback loop & adaptation demonstration
│   ├── 08_STAGE2_USER_EVALUATION.ipynb
│   └── VALIDATION_REPORT.md
├── dashboard/                       # Django Web Application
│   ├── dashboard/                   # Project settings, URLs, WSGI
│   ├── predictor/                   # Core application: models, views, forms, services
│   │   ├── services/                # Inference, SHAP explanations, feedback learning
│   │   ├── templates/               # Responsive HTML5 templates (shadcn-inspired)
│   │   ├── static/                  # Static assets and CSS
│   │   └── migrations/              # Database migration history (0001 - 0008)
│   └── manage.py
├── docs/                            # Architectural specifications and notices
├── nhanes_feasibility_2021_2023/    # Research assets, splits, and locked models
│   ├── lock_phase4_2/               # Cryptographic locks & model specifications
│   ├── models_phase5/               # gam_final.pkl, preprocessor.pkl
│   ├── predictions_phase5/          # Confirmatory test predictions
│   └── processed/                   # analytic_expanded_complete.parquet
└── notebooks/                       # Automated notebook builders & validation runner
```

---

## 4. Getting Started

### Prerequisites
- Python 3.10.x
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/BelumIMMO-liburan/dysglycemia-dashboard.git
   cd dysglycemia-dashboard
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # On Windows (PowerShell):
   .\.venv\Scripts\Activate.ps1
   # On Linux/macOS:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database migrations:**
   ```bash
   python dashboard/manage.py migrate
   ```

---

## 5. Running the Application

### Option A: Evaluation Mode (Participant-Facing Study)
Simulates or runs the Railway-hosted clinical evaluation flow:
```bash
# Windows PowerShell
$env:APP_MODE="evaluation"
python dashboard/manage.py runserver

# Linux / macOS
export APP_MODE=evaluation
python dashboard/manage.py runserver
```
Visit: `http://127.0.0.1:8000/evaluation/consent/`

### Option B: Feedback Lab Mode (Researcher / Adaptation Experiment)
Enables researcher controls, model adaptation training, and comparative inference:
```bash
# Windows PowerShell
$env:APP_MODE="feedback_lab"
python dashboard/manage.py runserver

# Linux / macOS
export APP_MODE=feedback_lab
python dashboard/manage.py runserver
```
Visit: `http://127.0.0.1:8000/feedback/experiment/`

---

## 6. Testing & Validation

### Automated Django Test Suite
Execute the full unit and integration test suite (224 tests covering clinical inference, SHAP explanations, feedback adaptation, validation checks, database isolation guards, and evaluation mode protections):
```bash
python dashboard/manage.py test predictor -v2
```

### CRISP-DM Notebook Validation
Verify that all 9 CRISP-DM notebooks execute cleanly and match locked research reports:
```bash
python notebooks/validate_crisp_dm_notebooks.py
```

---

## 7. Production Deployment (e.g., Railway)

1. Connect this GitHub repository to Railway.
2. Configure Environment Variables in the Railway Dashboard:
   ```env
   APP_MODE=evaluation
   SECRET_KEY=<your-secure-random-key>
   DEBUG=False
   ALLOWED_HOSTS=.railway.app,localhost,127.0.0.1
   CSRF_TRUSTED_ORIGINS=https://*.railway.app
   ```
3. The deployment automatically utilizes `Procfile` to run database migrations and launch the Gunicorn WSGI server:
   ```bash
   python dashboard/manage.py migrate && gunicorn --chdir dashboard dashboard.wsgi:application --bind 0.0.0.0:$PORT
   ```

---

## 8. Safe Evaluation Data Reset

To reset evaluation participant data during dry-runs without endangering research evidence:
```bash
$env:APP_MODE="evaluation"
python dashboard/manage.py reset_evaluation_data --confirm
```
*Note: This command strictly operates on `db_evaluation.sqlite3` and will abort if connected to `db.sqlite3`.*

---

## 9. License & Governance

This software is developed for academic research purposes under the thesis project:
*Decision Dashboard berbasis Explainable AI dan Human Override dengan Pendekatan Two-Stage Screening untuk Risiko Disglikemia.*

- All clinical risk predictions are investigational and intended solely as pre-screening decision support.
- Frozen baseline models and threshold configurations are permanently locked against post-hoc manipulation.
