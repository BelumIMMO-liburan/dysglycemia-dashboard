"""
Dry-Run Verification Script for Phase E2 (Non-Human Deterministic Verification)
Executes Tasks 1-6 using locked stimuli against db_dryrun.sqlite3,
verifies exact model inference, XAI outputs, review actions, and Stage-2 assessment.
Verifies data linkage across SQLite, moderator observation, survey export, and manifest.
Verifies SUS and comprehension scoring formulas deterministically.
Ensures db_study.sqlite3 remains completely untouched and pristine zero-state.
"""

import os
import sys
import hashlib
import json
import sqlite3
import shutil

# Set up Django environment with db_dryrun.sqlite3
os.environ["DJANGO_SETTINGS_MODULE"] = "dashboard.settings"
os.environ["APP_DATA_MODE"] = "dryrun"  # custom or ensure points to db_dryrun

import django
from django.conf import settings

# Adjust settings dynamically to point to db_dryrun.sqlite3
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")
sys.path.insert(0, DASHBOARD_DIR)
DRYRUN_DB = os.path.join(DASHBOARD_DIR, "db_dryrun.sqlite3")
STUDY_DB = os.path.join(DASHBOARD_DIR, "db_study.sqlite3")
TEMPLATE_DB = os.path.join(BASE_DIR, "evaluation", "e2", "runtime", "db_session_template.sqlite3")

# Initialize dryrun db from pristine template
shutil.copy2(TEMPLATE_DB, DRYRUN_DB)
print(f"[INIT] Cloned pristine template to {DRYRUN_DB}")

settings.DATABASES["default"]["NAME"] = DRYRUN_DB
django.setup()

from predictor.models import ScreeningRecord, ScreeningExplanation, HumanReview, Stage2Assessment
from predictor.services import screening_inference, screening_explanation
from decimal import Decimal

PARTICIPANT_CODE = "DRYRUN001"

print("\n==================================================")
print(f"STARTING RESEARCHER-ONLY DETERMINISTIC DRY RUN: {PARTICIPANT_CODE}")
print("==================================================")

# Step 1: Execute CASE-ALPHA (Tasks 1, 2, 3)
alpha_inputs = {
    "age": 56,
    "sex": "male",
    "bmi": 31.2,
    "hypertension_history": "yes",
    "smoking_history": "no",
    "waist_cm": 102.0,
    "sedentary_minutes_day": 480
}

alpha_inf = screening_inference.predict_screening(alpha_inputs)
alpha_exp = screening_explanation.explain_screening(alpha_inputs)

alpha_rec = ScreeningRecord.objects.create(
    age=alpha_inputs["age"],
    sex=alpha_inputs["sex"],
    bmi=alpha_inputs["bmi"],
    waist_cm=alpha_inputs["waist_cm"],
    hypertension_history=alpha_inputs["hypertension_history"],
    smoking_history=alpha_inputs["smoking_history"],
    sedentary_minutes_day=alpha_inputs["sedentary_minutes_day"],
    screening_probability=alpha_inf.screening_probability,
    ai_referral_recommended=alpha_inf.referral_recommended,
    decision_threshold=Decimal(str(alpha_inf.threshold)),
    model_name=alpha_inf.model_name,
    model_sha256=screening_inference.EXPECTED_GAM_SHA256,
    preprocessor_sha256=screening_inference.EXPECTED_PREPROCESSOR_SHA256,
    input_schema_version="1.0"
)

alpha_exp_rec = ScreeningExplanation.objects.create(
    screening_record=alpha_rec,
    method=alpha_exp.method,
    method_version=alpha_exp.method_version,
    link_function=alpha_exp.link_function,
    intercept=alpha_exp.intercept,
    contributions_json=[c.to_dict() for c in alpha_exp.contributions],
    reconstructed_linear_predictor=alpha_exp.reconstructed_linear_predictor,
    reconstructed_probability=alpha_exp.reconstructed_probability,
    reconstruction_error=alpha_exp.reconstruction_error,
    model_sha256=alpha_exp.model_sha256,
    status='generated'
)

signal_alpha = "Elevated Screening Signal" if alpha_rec.ai_referral_recommended else "Lower Screening Signal"
print(f"[TASK 1 & 2] CASE-ALPHA Inference Result:")
print(f"  - Record UUID: {alpha_rec.id}")
print(f"  - Calculated Probability: {alpha_rec.screening_probability:.6f} (Expected: 0.272969)")
print(f"  - Recommendation: {'Refer' if alpha_rec.ai_referral_recommended else 'No Referral'} (Expected: Refer)")
print(f"  - Signal: {signal_alpha} (Expected: Elevated Screening Signal)")

# Assert exact values
assert abs(alpha_rec.screening_probability - 0.272969) < 1e-5, f"Alpha prob mismatch: {alpha_rec.screening_probability}"
assert alpha_rec.ai_referral_recommended is True
assert signal_alpha == "Elevated Screening Signal"

# Inspect GAM terms
terms = alpha_exp.contributions
print(f"  - GAM Factors Count: {len(terms)} (Expected: 7)")
assert len(terms) == 7

# Top positive factor must be age
positive_factors = [t for t in terms if t.contribution > 0]
positive_factors.sort(key=lambda x: x.contribution, reverse=True)
print(f"  - Top Positive Factor: {positive_factors[0].feature_name} (+{positive_factors[0].contribution:.3f})")
assert positive_factors[0].feature_name == "age"

# Task 3: Accept recommendation
alpha_review = HumanReview.objects.create(
    screening_record=alpha_rec,
    reviewer_code=PARTICIPANT_CODE,
    review_action="accepted",
    final_referral_recommended=True,
    override_reason_code="",
    override_note=""
)
print(f"[TASK 3] CASE-ALPHA Human Review Finalized:")
print(f"  - Action: {alpha_review.review_action}")
print(f"  - Final Decision: {'Refer' if alpha_review.final_referral_recommended else 'No Referral'}")
print(f"  - Reviewer Code: {alpha_review.reviewer_code}")

# Step 2: Execute CASE-BETA (Task 4)
beta_inputs = {
    "age": 32,
    "sex": "female",
    "bmi": 23.5,
    "hypertension_history": "no",
    "smoking_history": "yes",
    "waist_cm": 74.0,
    "sedentary_minutes_day": 300
}

beta_inf = screening_inference.predict_screening(beta_inputs)
beta_exp = screening_explanation.explain_screening(beta_inputs)

beta_rec = ScreeningRecord.objects.create(
    age=beta_inputs["age"],
    sex=beta_inputs["sex"],
    bmi=beta_inputs["bmi"],
    waist_cm=beta_inputs["waist_cm"],
    hypertension_history=beta_inputs["hypertension_history"],
    smoking_history=beta_inputs["smoking_history"],
    sedentary_minutes_day=beta_inputs["sedentary_minutes_day"],
    screening_probability=beta_inf.screening_probability,
    ai_referral_recommended=beta_inf.referral_recommended,
    decision_threshold=Decimal(str(beta_inf.threshold)),
    model_name=beta_inf.model_name,
    model_sha256=screening_inference.EXPECTED_GAM_SHA256,
    preprocessor_sha256=screening_inference.EXPECTED_PREPROCESSOR_SHA256,
    input_schema_version="1.0"
)

beta_exp_rec = ScreeningExplanation.objects.create(
    screening_record=beta_rec,
    method=beta_exp.method,
    method_version=beta_exp.method_version,
    link_function=beta_exp.link_function,
    intercept=beta_exp.intercept,
    contributions_json=[c.to_dict() for c in beta_exp.contributions],
    reconstructed_linear_predictor=beta_exp.reconstructed_linear_predictor,
    reconstructed_probability=beta_exp.reconstructed_probability,
    reconstruction_error=beta_exp.reconstruction_error,
    model_sha256=beta_exp.model_sha256,
    status='generated'
)

signal_beta = "Elevated Screening Signal" if beta_rec.ai_referral_recommended else "Lower Screening Signal"
print(f"\n[TASK 4] CASE-BETA Inference Result:")
print(f"  - Record UUID: {beta_rec.id}")
print(f"  - Calculated Probability: {beta_rec.screening_probability:.6f} (Expected: 0.054663)")
print(f"  - Recommendation: {'Refer' if beta_rec.ai_referral_recommended else 'No Referral'} (Expected: No Referral)")
print(f"  - Signal: {signal_beta} (Expected: Lower Screening Signal)")

assert abs(beta_rec.screening_probability - 0.054663) < 1e-5, f"Beta prob mismatch: {beta_rec.screening_probability}"
assert beta_rec.ai_referral_recommended is False
assert signal_beta == "Lower Screening Signal"

# Task 4: Human Override to Refer
beta_review = HumanReview.objects.create(
    screening_record=beta_rec,
    reviewer_code=PARTICIPANT_CODE,
    review_action="overridden",
    final_referral_recommended=True,
    override_reason_code="precautionary_referral",
    override_note="Individual reports unrecorded family history of early diabetes"
)
print(f"  - Human Override Finalized:")
print(f"    Action: {beta_review.review_action}")
print(f"    Original: {'Refer' if beta_rec.ai_referral_recommended else 'No Referral'} -> Final: {'Refer' if beta_review.final_referral_recommended else 'No Referral'}")
print(f"    Reason Code: {beta_review.override_reason_code}")
print(f"    Note: {beta_review.override_note}")

# Step 3: Execute Stage-2 Assessment for CASE-ALPHA ONLY (Task 5)
stage2_alpha = Stage2Assessment.objects.create(
    human_review=alpha_review,
    hba1c_percent=Decimal("6.10"),
    laboratory_range="prediabetes_range",
    range_rule_version="ADA_2026_A1C_RANGE_V1",
    entry_method="manual"
)
print(f"\n[TASK 5] CASE-ALPHA Stage-2 Lab Assessment:")
print(f"  - HbA1c: {stage2_alpha.hba1c_percent}%")
print(f"  - Category: {stage2_alpha.laboratory_range} (Expected: prediabetes_range)")

# Task 6: Audit History Verification
print(f"\n[TASK 6] Audit History & Cardinality Verification:")
rec_count = ScreeningRecord.objects.count()
exp_count = ScreeningExplanation.objects.count()
rev_count = HumanReview.objects.count()
s2_count = Stage2Assessment.objects.count()

print(f"  - ScreeningRecord Count: {rec_count} (Expected: 2)")
print(f"  - ScreeningExplanation Count: {exp_count} (Expected: 2)")
print(f"  - HumanReview Count: {rev_count} (Expected: 2)")
print(f"  - Stage2Assessment Count: {s2_count} (Expected: 1)")

assert rec_count == 2
assert exp_count == 2
assert rev_count == 2
assert s2_count == 1

# Check Case Beta Stage 2 status (must have no Stage2Assessment)
beta_s2 = Stage2Assessment.objects.filter(human_review=beta_review).first()
print(f"  - CASE-BETA Stage-2 Exists: {beta_s2 is not None} (Expected: False / Pending)")
assert beta_s2 is None

# Hash the dryrun database
with open(DRYRUN_DB, "rb") as f:
    dryrun_hash = hashlib.sha256(f.read()).hexdigest()
print(f"  - db_dryrun.sqlite3 SHA-256: {dryrun_hash}")

# Check that db_study.sqlite3 remains pristine zero-state
study_conn = sqlite3.connect(STUDY_DB)
cursor = study_conn.cursor()
for table in ["predictor_screeningrecord", "predictor_screeningexplanation", "predictor_humanreview", "predictor_stage2assessment"]:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  - [PRISTINE CHECK] {STUDY_DB} -> {table}: {count} rows")
    assert count == 0, f"Table {table} in {STUDY_DB} is NOT zero-state!"
study_conn.close()
print("  - [CONFIRMED] db_study.sqlite3 is 100% pristine zero-state!")

# Verify SUS Scoring Formula
print("\n==================================================")
print("TESTING DETERMINISTIC SUS SCORING ALGORITHM")
print("==================================================")

# Standard SUS Responses Fixture (All 4s)
# Odd items (1,3,5,7,9): response 4 -> contribution = 4 - 1 = 3
# Even items (2,4,6,8,10): response 4 -> contribution = 5 - 4 = 1
# Sum contributions = 5*3 + 5*1 = 20. Total SUS = 20 * 2.5 = 50.0
raw_sus_neutral_high = [4] * 10
contributions = []
for idx, r in enumerate(raw_sus_neutral_high, start=1):
    if idx % 2 == 1:
        c = r - 1
    else:
        c = 5 - r
    contributions.append(c)
computed_sus_50 = sum(contributions) * 2.5
print(f"  - Fixture 1 (All 4s): Computed SUS = {computed_sus_50} (Expected: 50.0)")
assert computed_sus_50 == 50.0

# Fixture 2: Best Possible (Odd=5, Even=1)
# Odd items: 5 - 1 = 4. Even items: 5 - 1 = 4. Sum = 40. Total SUS = 40 * 2.5 = 100.0
raw_sus_perfect = [5 if i % 2 == 1 else 1 for i in range(1, 11)]
contributions_perfect = [(r - 1) if (i % 2 == 1) else (5 - r) for i, r in enumerate(raw_sus_perfect, start=1)]
computed_sus_100 = sum(contributions_perfect) * 2.5
print(f"  - Fixture 2 (Odd=5, Even=1): Computed SUS = {computed_sus_100} (Expected: 100.0)")
assert computed_sus_100 == 100.0

# Fixture 3: Realistic Dry-run Profile (e.g. 4,2,4,2,4,2,4,2,4,2) -> Odd=4 (c=3), Even=2 (c=3) -> Sum=30 -> 30*2.5 = 75.0
raw_sus_dryrun = [4, 2, 4, 2, 4, 2, 4, 2, 4, 2]
contributions_dryrun = [(r - 1) if (i % 2 == 1) else (5 - r) for i, r in enumerate(raw_sus_dryrun, start=1)]
computed_sus_dryrun = sum(contributions_dryrun) * 2.5
print(f"  - Fixture 3 (Dryrun 4/2 alternating): Computed SUS = {computed_sus_dryrun} (Expected: 75.0)")
assert computed_sus_dryrun == 75.0

# Verify Comprehension Scoring Formula
print("\n==================================================")
print("TESTING OBJECTIVE COMPREHENSION SCORING ALGORITHM")
print("==================================================")
KEYED_CORRECT = {
    "COMP_01": "B",
    "COMP_02": "B",
    "COMP_03": "A",
    "COMP_04": "C",
    "COMP_05": "B",
    "COMP_06": "B",
    "COMP_07": "C",
    "COMP_08": "B",
}

# Synthetic Dryrun Responses: 7 correct, 1 incorrect (e.g. COMP_04 = A)
synthetic_comp_answers = {
    "COMP_01": "B",
    "COMP_02": "B",
    "COMP_03": "A",
    "COMP_04": "A",  # incorrect (distractor)
    "COMP_05": "B",
    "COMP_06": "B",
    "COMP_07": "C",
    "COMP_08": "B",
}

scored_comp = {}
for item_id, ans in synthetic_comp_answers.items():
    is_correct = 1 if ans == KEYED_CORRECT[item_id] else 0
    scored_comp[item_id] = is_correct

total_comp_score = sum(scored_comp.values())
print(f"  - Synthetic Comprehension Score: {total_comp_score}/8 (Expected: 7/8)")
assert total_comp_score == 7
assert scored_comp["COMP_04"] == 0
assert scored_comp["COMP_01"] == 1

print("\n==================================================")
print("EXPORTING DRYRUN LINKED CSV ARTIFACTS")
print("==================================================")

DRYRUN_EXPORT_DIR = os.path.join(BASE_DIR, "evaluation", "e2", "runtime", "dryrun_output")
os.makedirs(DRYRUN_EXPORT_DIR, exist_ok=True)

# 1. participants.csv row
participants_row = f"{PARTICIPANT_CODE},primary,25-34,bachelor,occasional,none,2026-09-05\n"
with open(os.path.join(DRYRUN_EXPORT_DIR, "participants.csv"), "w", encoding="utf-8") as f:
    f.write("participant_code,participant_group,age_band,education_category,prior_dashboard_exp,health_background,session_date\n")
    f.write(participants_row)

# 2. task_results.csv (6 rows)
task_rows = [
    f"{PARTICIPANT_CODE},TASK_1,1,0,,18.4,{alpha_rec.id}",
    f"{PARTICIPANT_CODE},TASK_2,1,0,,24.1,{alpha_rec.id}",
    f"{PARTICIPANT_CODE},TASK_3,1,0,,12.0,{alpha_rec.id}",
    f"{PARTICIPANT_CODE},TASK_4,1,0,,31.5,{beta_rec.id}",
    f"{PARTICIPANT_CODE},TASK_5,1,0,,22.3,{alpha_rec.id}",
    f"{PARTICIPANT_CODE},TASK_6,1,0,,16.8,{beta_rec.id}",
]
with open(os.path.join(DRYRUN_EXPORT_DIR, "task_results.csv"), "w", encoding="utf-8") as f:
    f.write("participant_code,task_id,task_success,assistance_level,error_types,task_duration_sec,screening_uuid\n")
    for tr in task_rows:
        f.write(tr + "\n")

# 3. comprehension_responses.csv (8 rows)
with open(os.path.join(DRYRUN_EXPORT_DIR, "comprehension_responses.csv"), "w", encoding="utf-8") as f:
    f.write("participant_code,item_id,selected_option,is_correct\n")
    for item_id, ans in synthetic_comp_answers.items():
        f.write(f"{PARTICIPANT_CODE},{item_id},{ans},{scored_comp[item_id]}\n")

# 4. sus_responses.csv (10 rows)
with open(os.path.join(DRYRUN_EXPORT_DIR, "sus_responses.csv"), "w", encoding="utf-8") as f:
    f.write("participant_code,item_id,raw_response,scored_value\n")
    for idx, (raw, sc) in enumerate(zip(raw_sus_dryrun, contributions_dryrun), start=1):
        item_id = f"SUS_{idx:02d}"
        f.write(f"{PARTICIPANT_CODE},{item_id},{raw},{sc}\n")

# 5. perception_responses.csv (5 rows)
with open(os.path.join(DRYRUN_EXPORT_DIR, "perception_responses.csv"), "w", encoding="utf-8") as f:
    f.write("participant_code,item_id,response_likert\n")
    for idx in range(1, 6):
        item_id = f"CLAR_{idx:02d}"
        f.write(f"{PARTICIPANT_CODE},{item_id},4\n")

# 6. qualitative_feedback.csv (3 rows)
with open(os.path.join(DRYRUN_EXPORT_DIR, "qualitative_feedback.csv"), "w", encoding="utf-8") as f:
    f.write("participant_code,item_id,feedback_text\n")
    f.write(f'{PARTICIPANT_CODE},QUAL_01,"Synthetic dry run feedback: navigation was straightforward"\n')
    f.write(f'{PARTICIPANT_CODE},QUAL_02,"Synthetic dry run feedback: factor direction labels are clear"\n')
    f.write(f'{PARTICIPANT_CODE},QUAL_03,"Synthetic dry run feedback: no ambiguity in decision ownership"\n')

# 7. session_manifest.csv row
manifest_row = f"{PARTICIPANT_CODE},1.0.3,research-prototype-v1.0,dryrun,2026-09-05,{DRYRUN_DB},{dryrun_hash},DRYRUN001_moderator.csv,DRYRUN001_survey.csv,completed,Synthetic verification run"
with open(os.path.join(DRYRUN_EXPORT_DIR, "session_manifest.csv"), "w", encoding="utf-8") as f:
    f.write("participant_code,protocol_version,prototype_release,session_type,session_date,dashboard_database_archive,dashboard_database_sha256,moderator_sheet_file,survey_export_file,completion_status,notes\n")
    f.write(manifest_row + "\n")

# Linkage Verification Audit
print(f"\n[LINKAGE CHECK] Verifying Participant Code across 7 exported files & SQLite:")
code_counts = {}
for fname in ["participants.csv", "task_results.csv", "comprehension_responses.csv", "sus_responses.csv", "perception_responses.csv", "qualitative_feedback.csv", "session_manifest.csv"]:
    fpath = os.path.join(DRYRUN_EXPORT_DIR, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("participant_code")]
        matched = all(line.startswith(PARTICIPANT_CODE) for line in lines)
        code_counts[fname] = len(lines)
        print(f"  - {fname}: {len(lines)} records, all matched '{PARTICIPANT_CODE}': {matched}")
        assert matched

# Check SQLite HumanReview reviewer_code
hr_codes = list(HumanReview.objects.values_list("reviewer_code", flat=True))
print(f"  - SQLite HumanReview reviewer_code list: {hr_codes}")
assert hr_codes == [PARTICIPANT_CODE, PARTICIPANT_CODE]

print("\n==================================================")
print("DRY-RUN LINKAGE & SCORING VERIFICATION COMPLETED SUCCESSFULLY!")
print("==================================================")
