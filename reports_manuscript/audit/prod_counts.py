#!/usr/bin/env python3
"""
Read-Only Evaluation Database Production Audit Script
Protocol E1 v1.0.3 / Thesis Mechanism & Governance Verification

PURPOSE:
Audits production database counts to verify whether any online adaptation,
feedback-learning, or unassociated screening records occurred during the
participant evaluation study window (23 September 2026 – 1 October 2026).

STRICT SAFETY CONSTRAINTS:
1. READ-ONLY: Executes only SELECT / COUNT queries. Zero modifications or writes.
2. AGGREGATE COUNTS ONLY: Outputs numbers only. Never prints participant codes,
   free-text rationales, or identifying metadata.
3. FAIL-SAFE: Can be run standalone via `python prod_counts.py` against any
   Django-configured PostgreSQL or SQLite database.
"""

import os
import sys
from datetime import datetime, timezone

# Setup Django environment if not already loaded
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dashboard_dir = os.path.join(base_dir, "dashboard")
if dashboard_dir not in sys.path:
    sys.path.insert(0, dashboard_dir)
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

if not os.environ.get("DJANGO_SETTINGS_MODULE"):
    os.environ["DJANGO_SETTINGS_MODULE"] = "dashboard.settings"
os.environ.setdefault("APP_MODE", "evaluation")

try:
    import django
    django.setup()
except Exception as e:
    sys.exit(f"Error initializing Django: {e}")

from django.db.models import Count, Q
from predictor.models import (
    ScreeningRecord,
    HumanReview,
    HumanFeedback,
    Stage2Assessment,
    SimilarCaseComparison,
    ControlledFeedbackExperiment,
    ModelVersion,
)

def run_audit():
    from django.db import connection
    db_dict = connection.settings_dict
    engine = db_dict.get('ENGINE', '')
    host = db_dict.get('HOST', '') or '(local/none)'
    port = db_dict.get('PORT', '') or '(default)'
    raw_name = db_dict.get('NAME', '')
    is_sqlite = 'sqlite' in engine.lower()
    db_name = os.path.basename(str(raw_name)) if is_sqlite else str(raw_name)

    print("=" * 78)
    print("PARTICIPANT EVALUATION DATABASE AUDIT — AGGREGATE PRODUCTION COUNTS ONLY")
    print("=" * 78)
    print(f"Timestamp of execution (UTC) : {datetime.now(timezone.utc).isoformat()}")
    print("Study Evaluation Window      : 2026-09-23 00:00:00 UTC to 2026-10-01 23:59:59 UTC")
    print("-" * 78)
    print(f"Database Engine              : {engine}")
    print(f"Database Host                : {host}")
    print(f"Database Port                : {port}")
    print(f"Database Name                : {db_name}")
    print("-" * 78)

    if is_sqlite:
        print("\n" + "!" * 78)
        print("WARNING: LOCAL SQLITE - NOT PRODUCTION; zeros here are meaningless")
        print("!" * 78)
        if "--allow-sqlite" not in sys.argv:
            print("Refusing to run on SQLite without explicit flag.")
            print("Pass --allow-sqlite to inspect local test/development database.")
            print("!" * 78 + "\n")
            sys.exit(2)
        else:
            print("(--allow-sqlite flag detected: proceeding with local inspection)\n")

    window_start = datetime(2026, 9, 23, 0, 0, 0, tzinfo=timezone.utc)
    window_end = datetime(2026, 10, 1, 23, 59, 59, tzinfo=timezone.utc)

    # -------------------------------------------------------------------------
    # 0. Sanity Counts (Screenings, Reviews, Stage-2 Rows in Study Window)
    # -------------------------------------------------------------------------
    # EXPLANATION:
    # Baseline activity volume of participants throughout the 42-participant evaluation.
    # Ensures the database contains real workflow activity within the window.
    # -------------------------------------------------------------------------
    screenings_in_window = ScreeningRecord.objects.filter(
        created_at__gte=window_start,
        created_at__lte=window_end
    ).count()
    reviews_in_window = HumanReview.objects.filter(
        created_at__gte=window_start,
        created_at__lte=window_end
    ).count()
    stage2_in_window = Stage2Assessment.objects.filter(
        created_at__gte=window_start,
        created_at__lte=window_end
    ).count()

    print("\n[0] Sanity Counts in Study Window (23 Sep – 1 Oct 2026):")
    print(f"    - Total ScreeningRecord rows in window              : {screenings_in_window}")
    print(f"    - Total HumanReview rows in window                  : {reviews_in_window}")
    print(f"    - Total Stage2Assessment rows in window             : {stage2_in_window}")
    print("    * Study Export Benchmark: ScreeningRecord 87, HumanReview 55, Stage2Assessment 17")
    if screenings_in_window == 87 and reviews_in_window == 55 and stage2_in_window == 17:
        verdict = "MATCHES EXPORT"
    else:
        verdict = "DOES NOT MATCH EXPORT - wrong database, wrong window, or later activity"
    print(f"    * Verdict: {verdict}")
    print("    * Significance: Establishes base volume of participant workflow cases during the evaluation.")

    # -------------------------------------------------------------------------
    # 1. SimilarCaseComparison rows created during study window
    # -------------------------------------------------------------------------
    # EXPLANATION:
    # SimilarCaseComparison records before/after counterfactual evaluations of
    # Case B using the candidate residual adaptation layer. In pure participant
    # evaluation mode, this service should NEVER execute because the model is frozen.
    # Expected Count in Production Evaluation: 0
    # -------------------------------------------------------------------------
    sim_cases_total = SimilarCaseComparison.objects.count()
    sim_cases_window = SimilarCaseComparison.objects.filter(
        created_at__gte=window_start,
        created_at__lte=window_end
    ).count()

    print("\n[1] SimilarCaseComparison (Controlled Adaptation Comparisons):")
    print(f"    - Created within study window (23 Sep – 1 Oct 2026) : {sim_cases_window}")
    print(f"    - Total in database across all time                 : {sim_cases_total}")
    print("    * Significance: Proves whether candidate adaptation comparison was executed.")

    # -------------------------------------------------------------------------
    # 2. Adapted Prediction / Candidate Model rows created during study window
    # -------------------------------------------------------------------------
    # EXPLANATION:
    # ModelVersion records candidate model adaptations produced by FeedbackLearningBatch.
    # In pure participant evaluation mode, no candidate models should be created or active.
    # Expected Count in Production Evaluation: 0 candidate versions created/active.
    # -------------------------------------------------------------------------
    candidate_versions_window = ModelVersion.objects.filter(
        version_type='candidate',
        created_at__gte=window_start,
        created_at__lte=window_end
    ).count()

    active_candidate_versions = ModelVersion.objects.filter(
        version_type='candidate',
        is_active=True
    ).count()

    controlled_exps_window = ControlledFeedbackExperiment.objects.filter(
        created_at__gte=window_start,
        created_at__lte=window_end
    ).count() if hasattr(ControlledFeedbackExperiment, 'created_at') else ControlledFeedbackExperiment.objects.count()

    print("\n[2] Adapted Model Versions & Controlled Experiments:")
    print(f"    - Candidate ModelVersions created in study window   : {candidate_versions_window}")
    print(f"    - Candidate ModelVersions currently active          : {active_candidate_versions}")
    print(f"    - ControlledFeedbackExperiment instances in window  : {controlled_exps_window}")
    print("    * Significance: Proves frozen GAM remained the sole active model in evaluation.")

    # -------------------------------------------------------------------------
    # 3. HumanFeedback by learning_status and is_eligible_for_learning
    # -------------------------------------------------------------------------
    # EXPLANATION:
    # Tracks the governance state of structured feedback signals captured during
    # human review. Shows how many feedback records were marked eligible for learning
    # versus excluded/pending, and whether any were ingested into a learning batch.
    # Expected Count in Production Evaluation: 0 ingested into learning batches ('included').
    # -------------------------------------------------------------------------
    feedback_qs = HumanFeedback.objects.all()
    feedback_window_qs = feedback_qs.filter(
        created_at__gte=window_start,
        created_at__lte=window_end
    )

    print("\n[3] HumanFeedback Records by Learning Status & Eligibility:")
    print(f"    - Total HumanFeedback records in window             : {feedback_window_qs.count()}")
    
    # Breakdown by distinct learning_status values from the data
    status_counts = (
        feedback_window_qs.values('learning_status')
        .annotate(total=Count('id'))
        .order_by('learning_status')
    )
    if status_counts:
        for item in status_counts:
            st = str(item['learning_status'])
            cnt = item['total']
            print(f"      * learning_status = '{st:<12}'             : {cnt}")
    else:
        print("      * (no HumanFeedback records found in study window)")

    # Breakdown by eligibility
    eligible_count = feedback_window_qs.filter(is_eligible_for_learning=True).count()
    ineligible_count = feedback_window_qs.filter(is_eligible_for_learning=False).count()
    print(f"      * is_eligible_for_learning = True                 : {eligible_count}")
    print(f"      * is_eligible_for_learning = False                : {ineligible_count}")
    print("    * Significance: Confirms feedback signals were logged for audit without triggering batches.")

    # -------------------------------------------------------------------------
    # 4. Number of Human Reviews with non-empty free-text rationale
    # -------------------------------------------------------------------------
    # EXPLANATION:
    # Counts how many participants utilized the optional free-text rationale field
    # when submitting an override decision, versus structured factor only.
    # Zero text snippets are displayed to ensure privacy.
    # -------------------------------------------------------------------------
    reviews_window = HumanReview.objects.filter(
        created_at__gte=window_start,
        created_at__lte=window_end
    )
    total_reviews_window = reviews_window.count()
    override_reviews_window = reviews_window.filter(review_action='overridden').count()
    
    # Free-text override_note in HumanReview and feedback_text in HumanFeedback
    reviews_with_note = reviews_window.filter(
        ~Q(override_note__isnull=True) & ~Q(override_note__exact='')
    ).count()

    feedback_with_text = feedback_window_qs.filter(
        ~Q(feedback_text__isnull=True) & ~Q(feedback_text__exact='')
    ).count()

    print("\n[4] Free-Text Override Notes & Contextual Feedback (Counts Only):")
    print(f"    - Total HumanReview records in window               : {total_reviews_window}")
    print(f"    - HumanReview records with review_action='overridden': {override_reviews_window}")
    print(f"    - Reviews with non-empty free-text override_note    : {reviews_with_note}")
    print(f"    - Feedback records with non-empty feedback_text     : {feedback_with_text}")
    print("    * Significance: Quantifies the volume of qualitative commentary provided by participants.")

    # -------------------------------------------------------------------------
    # 5. Number of ScreeningRecord rows without evaluation_session
    # -------------------------------------------------------------------------
    # EXPLANATION:
    # Counts ScreeningRecord entities created without an associated EvaluationSession.
    # In a fully scoped protocol, all evaluation participant screenings belong to a session.
    # Records without evaluation_session indicate unassociated/orphaned screenings or
    # screenings created via legacy / development endpoints.
    # -------------------------------------------------------------------------
    screenings_window = ScreeningRecord.objects.filter(
        created_at__gte=window_start,
        created_at__lte=window_end
    )
    total_screenings_window = screenings_window.count()
    unassociated_screenings_window = screenings_window.filter(
        evaluation_session__isnull=True
    ).count()
    associated_screenings_window = screenings_window.filter(
        evaluation_session__isnull=False
    ).count()

    total_screenings_all = ScreeningRecord.objects.count()
    unassociated_screenings_all = ScreeningRecord.objects.filter(
        evaluation_session__isnull=True
    ).count()

    print("\n[5] ScreeningRecord Session Association & Scoping Audit:")
    print(f"    - Total ScreeningRecords in window                  : {total_screenings_window}")
    print(f"    - Screenings WITH evaluation_session in window      : {associated_screenings_window}")
    print(f"    - Screenings WITHOUT evaluation_session in window   : {unassociated_screenings_window}")
    print(f"    - Total unassociated Screenings across all time     : {unassociated_screenings_all} / {total_screenings_all}")
    print("    * Significance: Measures scoping fidelity and presence of untracked participant intake.")

    print("\n" + "=" * 78)
    print("AUDIT SCRIPT EXECUTION COMPLETE — ZERO IDENTIFIERS PRINTED")
    print("=" * 78)

if __name__ == '__main__':
    run_audit()
