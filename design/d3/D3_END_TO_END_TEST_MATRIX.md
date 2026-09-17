# D3 End-to-End Test Matrix & Verification Scenarios

**Status:** ALL SCENARIOS VERIFIED AND PASSING  
**Execution Environment:** Django Automated Test Runner (`PhaseD3SystemAuditTests`)  
**Total Scenarios Tested:** 8 Core Lifecycle Paths (A–H)

---

## 1. Scenario Execution Matrix

| Scenario ID | Test Name | Intake Profile | AI Signal | Review Action | Final Human Decision | Stage 2 Action | Stage 2 Range | Final Lifecycle State | Invariant Audit | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SCENARIO A** | `test_scenario_a_refer_accept_stage2_normal` | 55yo Male, BMI 31.2, HTN Yes, SMK Yes | Refer (p ≥ 0.1389) | Accept | Refer | Enters 5.4% | `normal_range` | `completed_stage2` | GAM output immutable; Review concordance recorded; Stage2 linked | **PASSED** |
| **SCENARIO B** | `test_scenario_b_refer_accept_stage2_prediabetes` | 55yo Male, BMI 31.2, HTN Yes, SMK Yes | Refer (p ≥ 0.1389) | Accept | Refer | Enters 6.1% | `prediabetes_range` | `completed_stage2` | GAM output immutable; Stage2 categorization verified | **PASSED** |
| **SCENARIO C** | `test_scenario_c_refer_override_no_refer_stage2_blocked` | 55yo Male, BMI 31.2, HTN Yes, SMK Yes | Refer (p ≥ 0.1389) | Override | Do Not Refer | Attempted | BLOCKED | `reviewed_no_referral` | AI recommendation preserved; Rationale captured; Stage2 inaccessible | **PASSED** |
| **SCENARIO D** | `test_scenario_d_no_refer_accept_stage2_blocked` | 24yo Female, BMI 21.0, HTN No, SMK No | Do Not Refer (p < 0.1389) | Accept | Do Not Refer | Attempted | BLOCKED | `reviewed_no_referral` | Final decision concordant; Stage2 ineligible | **PASSED** |
| **SCENARIO E** | `test_scenario_e_no_refer_override_refer_stage2_diabetes` | 24yo Female, BMI 21.0, HTN No, SMK No | Do Not Refer (p < 0.1389) | Override | Refer | Enters 7.2% | `diabetes_range` | `completed_stage2` | Override permits Stage2; AI recommendation unaltered; Diabetes-range derived | **PASSED** |
| **SCENARIO F** | `test_scenario_f_explanation_failure_preserves_screening_blocks_review` | High-risk input | Refer | Attempted | BLOCKED | Ineligible | N/A | `explanation_unavailable` | ScreeningRecord preserved; Explanation status `failed`; Human review blocked | **PASSED** |
| **SCENARIO G** | `test_scenario_g_inference_failure_halts_persistence` | Invalid / corrupted model | HALTED | Ineligible | Ineligible | Ineligible | N/A | None (0 persisted) | Zero records written; Clean atomic abort | **PASSED** |
| **SCENARIO H** | `test_scenario_h_stage2_invalid_input_halts_persistence` | Normal refer flow | Refer | Accept | Refer | Enters 1.0% | REJECTED | `pending_stage2` | Out-of-bounds input rejected; Zero Stage2Assessment persisted | **PASSED** |

---

## 2. Invariants Formally Verified

Across all eight scenarios, the automated test suite verified the following strict system invariants:

1. **Immutability of Stage-1 Intake:** `ScreeningRecord` inputs and AI outputs (`screening_probability`, `ai_referral_recommended`) never change after creation.
2. **Deterministic Explanation Association:** Every generated `ScreeningExplanation` links to exactly one `ScreeningRecord` and reproduces model probability within `1e-10` link-scale tolerance.
3. **Zero Reinference on Review:** Finalizing a human review (Accept or Override) executes 0 GAM inferences and 0 preprocessor transformations.
4. **Authoritative Server Derivation:** Review decisions and laboratory ranges cannot be injected or modified by the browser client.
5. **Selective Verification Barrier:** Stage-2 laboratory assessment is accessible if and only if the final human referral decision is `Refer`. Cases with final decision `Do Not Refer` cannot submit laboratory assessments.
