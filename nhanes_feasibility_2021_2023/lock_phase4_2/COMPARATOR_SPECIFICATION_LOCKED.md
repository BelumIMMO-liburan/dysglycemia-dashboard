# Comparator Specification Lock Amendment (Phase 4.2A)

**Document Status:** **FROZEN & IMMUTABLE**  
**Protocol Phase:** Phase 4.2A Comparator and Final Evaluation Protocol Lock Amendment  
**Final Test Status:** **LOCKED — ZERO ACCESS PERMITTED**  
**Date Locked:** 2026-09-02  

---

## 1. Re-Affirmation of Primary Screening Model (No Change)

The primary final screening model specification established in [FINAL_MODEL_SPECIFICATION_LOCKED.md](file:///c:/Users/Felix/Documents/Skripsi/nhanes_feasibility_2021_2023/lock_phase4_2/FINAL_MODEL_SPECIFICATION_LOCKED.md) remains **100% immutable and unchanged**:
- **Model Family:** Generalized Additive Model (GAM) with binomial logit link (`pygam.LogisticGAM`).
- **Dataset / Population:** `EXPANDED_COMMON` ($N = 4,044$; Development $N = 3,232$; Final Test $N = 812$).
- **Predictors ($k = 7$):** `age`, `sex`, `bmi`, `hypertension_history`, `smoking_history`, `waist_cm`, `sedentary_minutes_day`.
- **Hyperparameters:** `n_splines = 10`, `lambda = 10.0` (continuous variables modeled with cubic P-splines; binary features modeled with factor terms).
- **Frozen Pre-Specified Research Decision Threshold:** **`0.1389`** (derived from 90% sensitivity floor on development OOF).

---

## 2. Locked Statistical Baseline Comparator: Logistic Regression

The exact statistical baseline configuration selected during Phase 4.1 development evaluation is frozen with the following immutable parameters:

### 2.1 Estimator & Algorithm Specification
- **Estimator Class:** `sklearn.linear_model.LogisticRegression`
- **Penalty:** L2 regularization (`penalty="l2"`)
- **Regularization Strength ($C$):** `C = 0.1` (inverse regularization parameter)
- **Optimization Solver:** `solver="lbfgs"`
- **Maximum Iterations:** `max_iter = 1000`
- **Convergence Tolerance:** `tol = 1e-4`
- **Class Weight:** `class_weight = None` (unweighted likelihood)
- **Intercept:** `fit_intercept = True`
- **Random Seed:** `random_state = 42`

### 2.2 Predictor Order & Preprocessing Pipeline
- **Predictor Order ($k = 7$):**
  1. `age` (continuous)
  2. `sex` (binary indicator)
  3. `bmi` (continuous)
  4. `hypertension_history` (binary indicator)
  5. `smoking_history` (binary indicator)
  6. `waist_cm` (continuous)
  7. `sedentary_minutes_day` (continuous)
- **Categorical Mappings:**
  - `sex`: `1.0 (Male) -> 1.0`, `2.0 (Female) -> 0.0`
  - `hypertension_history`: `1.0 (Yes) -> 1.0`, `2.0 (No) -> 0.0`
  - `smoking_history`: `1.0 (Yes, ≥100 cigarettes lifetime) -> 1.0`, `2.0 (No) -> 0.0`
- **Continuous Preprocessing:**
  - Standard scaling: $z = (x - \mu) / \sigma$ using `sklearn.preprocessing.StandardScaler`.
  - **Strict Isolation:** The scaler is fitted **strictly on the $N = 3,232$ development participants only**. The fitted scaler will transform the final test partition ($N = 812$) without re-estimation.

### 2.3 Frozen Development-Derived Operating Threshold
- **Pre-Specified Research Operating Point:** 90% Sensitivity Floor
- **Frozen Decision Threshold:** **`0.1389`**
  - Development OOF Baseline at this threshold: **90.23% Sensitivity**, **41.65% Specificity**, **31.73% PPV**, **93.41% NPV**, **65.72% Referral Fraction**, **3.15 HbA1c tests per dysglycemia case detected**.

---

## 3. Locked Complex Non-Linear Comparator: Deep Learning Neural Network (DLNN)

The exact deep learning neural network configuration selected during Phase 4.1 development evaluation (`DLNN_16_8_drop0.0`) is frozen with the following immutable parameters:

### 3.1 Network Architecture & Hyperparameters
- **Implementation Framework:** TensorFlow 2.x / Keras (`tf.keras.Sequential`)
- **Input Dimension:** 7 features (`layers.Input(shape=(7,))`)
- **Hidden Layer 1:** `layers.Dense(16, activation="relu", name="dense_1")`
- **Dropout Layer 1:** None (`dropout_rate = 0.0`)
- **Hidden Layer 2:** `layers.Dense(8, activation="relu", name="dense_2")`
- **Dropout Layer 2:** None (`dropout_rate = 0.0`)
- **Output Layer:** `layers.Dense(1, activation="sigmoid", name="output")`
- **Loss Function:** Binary cross-entropy (`loss="binary_crossentropy"`)
- **Optimizer:** Adam (`tf.keras.optimizers.Adam(learning_rate=0.001)`)
- **Training Batch Size:** `batch_size = 32`
- **Maximum Training Epochs:** `epochs = 200`
- **Early Stopping Configuration:**
  - `monitor = "val_loss"`
  - `patience = 15`
  - `restore_best_weights = True`
  - `verbose = 0`

### 3.2 Internal Validation Split Procedure (Strict Development Isolation)
- **Procedure:** An internal stratified validation split is created exclusively from the $N = 3,232$ development partition using `sklearn.model_selection.train_test_split`:
  - `test_size = 0.15` ($15\%$ internal validation, $N = 485$; $85\%$ internal sub-training, $N = 2,747$)
  - `random_state = 42`
  - `stratify = y_development`
- **Strict Prohibition:** **Final-test data MUST NOT be used for early stopping, internal validation, hyperparameter tuning, scaling, calibration, or threshold selection.**

### 3.3 Deterministic Execution & Random Seeds
- Environment settings enforced before TensorFlow initialization:
  - `os.environ["PYTHONHASHSEED"] = "42"`
  - `os.environ["TF_DETERMINISTIC_OPS"] = "1"`
  - `os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"`
  - `random.seed(42)`
  - `np.random.seed(42)`
  - `tf.random.set_seed(42)`
  - Model initialization seed: `tf.keras.utils.set_random_seed(42)`

### 3.4 Frozen Development-Derived Operating Threshold
- **Pre-Specified Research Operating Point:** 90% Sensitivity Floor
- **Frozen Decision Threshold:** **`0.1419`**
  - Development OOF Baseline at this threshold: **90.09% Sensitivity**, **41.93% Specificity**, **31.81% PPV**, **93.37% NPV**, **65.47% Referral Fraction**, **3.14 HbA1c tests per dysglycemia case detected**.

---

## 4. Summary of Frozen Model Triad

| Parameter / Attribute | Primary Screening Model (GAM) | Statistical Baseline (Logistic Reg.) | Complex Comparator (DLNN) |
|:---|:---|:---|:---|
| **Model Family** | Generalized Additive Model | L2 Logistic Regression | Feedforward Neural Network |
| **Winning Configuration** | `GAM_splines10_lam10.0` | `L2_C0.1` | `DLNN_16_8_drop0.0` |
| **Architecture / Estimator** | `pygam.LogisticGAM` | `sklearn.linear_model.LogisticRegression` | `Keras Sequential(Dense 16 -> Dense 8 -> Sigmoid)` |
| **Key Regularization / Hyperparam** | `n_splines=10, lam=10.0` | `C=0.1, penalty="l2", solver="lbfgs"` | `Adam(lr=0.001), patience=15, epochs=200` |
| **Input Features ($k$)** | 7 non-lab inputs | 7 non-lab inputs | 7 non-lab inputs |
| **Development Training Sample** | $N = 3,232$ | $N = 3,232$ | $N = 3,232$ ($15\%$ internal val for early stop) |
| **Frozen Decision Threshold** | **`0.1389`** | **`0.1389`** | **`0.1419`** |
| **Pre-Specified Operating Point** | $\ge 90\%$ Sensitivity Floor | $\ge 90\%$ Sensitivity Floor | $\ge 90\%$ Sensitivity Floor |
| **Dev Baseline Referral Rate** | 65.25% | 65.72% | 65.47% |
| **Dev Baseline Specificity** | 42.25% | 41.65% | 41.93% |
| **Dev Baseline Tests per Case** | 3.13 | 3.15 | 3.14 |

---

## 5. Verification Verdict

All comparator architectures, implementations, hyperparameter values, preprocessing pipelines, random seeds, and operating decision thresholds are **reconstructed 100% exactly from Phase 4 and Phase 4.1 development code**. No parameters have been guessed or altered.

---

**COMPARATOR SPECIFICATIONS FROZEN — IMMUTABLE PRE-TEST SPECIFICATION**
