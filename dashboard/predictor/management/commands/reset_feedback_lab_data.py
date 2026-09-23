"""
Management command to safely reset Feedback Lab experimental data in db.sqlite3.

SAFETY GUARANTEES:
1. Strictly restricted to 'db.sqlite3' (Feedback Lab database).
2. Rejects execution if active database is 'db_evaluation.sqlite3'.
3. Rejects execution if APP_MODE is 'evaluation'.
4. Requires affirmative confirmation flag (--confirm) to prevent accidental execution.
5. Verifies and guarantees db_evaluation.sqlite3 and all frozen ML artifacts remain 100% untouched.
"""

import os
import hashlib
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction
from django.contrib.sessions.models import Session
from predictor.models import (
    Prediction,
    Override,
    ScreeningRecord,
    ScreeningExplanation,
    HumanReview,
    Stage2Assessment,
    ModelVersion,
    HumanFeedback,
    FeedbackLearningBatch,
    SimilarCaseComparison,
    ControlledFeedbackExperiment,
    EvaluationRespondent,
    EvaluationSession,
    EvaluationEvent,
    QuestionnaireResponse,
)


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    if not file_path.exists():
        return ""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


class Command(BaseCommand):
    help = "Safely reset Feedback Lab experimental data in db.sqlite3 (all experiment records = 0)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm",
            action="store_true",
            dest="confirm",
            help="Affirmative confirmation required to execute reset.",
        )

    def handle(self, *args, **options):
        # 1. Inspect active database and application mode
        db_path = Path(settings.DATABASES["default"]["NAME"]).resolve()
        db_filename = db_path.name
        app_mode = getattr(settings, "APP_MODE", "feedback_lab").lower()

        self.stdout.write(f"Active database: {db_filename} ({db_path})")
        self.stdout.write(f"Active APP_MODE: {app_mode}")

        # 2. Strict Safety Guard: Never allow reset on db_evaluation.sqlite3
        if "db_evaluation.sqlite3" == db_filename:
            raise CommandError(
                "CRITICAL ABORT: Active database is 'db_evaluation.sqlite3' (Participant Evaluation database). "
                "This command is strictly restricted to 'db.sqlite3' (Feedback Lab). "
                "Set APP_MODE=feedback_lab before running this command."
            )

        if "db.sqlite3" != db_filename:
            raise CommandError(
                f"CRITICAL ABORT: Target database must be 'db.sqlite3', but got '{db_filename}'."
            )

        if app_mode == "evaluation":
            raise CommandError(
                "CRITICAL ABORT: APP_MODE is set to 'evaluation'. "
                "Set APP_MODE=feedback_lab before running this command."
            )

        # 3. Snapshot db_evaluation.sqlite3 hash before reset
        eval_db_path = db_path.parent / "db_evaluation.sqlite3"
        eval_hash_before = compute_sha256(eval_db_path) if eval_db_path.exists() else None

        # 4. Confirmation requirement
        if not options.get("confirm"):
            self.stdout.write(
                self.style.WARNING(
                    "Dry-run safety check: Add --confirm to execute the deletion of all Feedback Lab experimental data in db.sqlite3."
                )
            )
            return

        # 5. Capture pre-reset row counts
        pre_counts = {
            "ScreeningRecord": ScreeningRecord.objects.count(),
            "ScreeningExplanation": ScreeningExplanation.objects.count(),
            "HumanReview": HumanReview.objects.count(),
            "Stage2Assessment": Stage2Assessment.objects.count(),
            "HumanFeedback": HumanFeedback.objects.count(),
            "FeedbackLearningBatch": FeedbackLearningBatch.objects.count(),
            "SimilarCaseComparison": SimilarCaseComparison.objects.count(),
            "ControlledFeedbackExperiment": ControlledFeedbackExperiment.objects.count(),
            "ModelVersion": ModelVersion.objects.count(),
            "Prediction (legacy)": Prediction.objects.count(),
            "Override (legacy)": Override.objects.count(),
            "EvaluationRespondent": EvaluationRespondent.objects.count(),
            "EvaluationSession": EvaluationSession.objects.count(),
            "EvaluationEvent": EvaluationEvent.objects.count(),
            "QuestionnaireResponse": QuestionnaireResponse.objects.count(),
            "Session": Session.objects.count(),
        }

        # 6. Perform atomic reset in db.sqlite3
        with transaction.atomic():
            ControlledFeedbackExperiment.objects.all().delete()
            SimilarCaseComparison.objects.all().delete()
            FeedbackLearningBatch.objects.all().delete()
            HumanFeedback.objects.all().delete()
            ModelVersion.objects.all().delete()
            Stage2Assessment.objects.all().delete()
            HumanReview.objects.all().delete()
            ScreeningExplanation.objects.all().delete()
            ScreeningRecord.objects.all().delete()
            Override.objects.all().delete()
            Prediction.objects.all().delete()
            EvaluationRespondent.objects.all().delete()
            EvaluationSession.objects.all().delete()
            EvaluationEvent.objects.all().delete()
            QuestionnaireResponse.objects.all().delete()
            Session.objects.all().delete()

        # 7. Clean up generated candidate adaptation files
        repo_root = db_path.parent.parent
        adaptations_dir = repo_root / "models" / "adaptations"
        cleared_adaptations = 0
        if adaptations_dir.exists():
            for pkl in adaptations_dir.glob("*.pkl"):
                try:
                    pkl.unlink()
                    cleared_adaptations += 1
                except Exception as e:
                    self.stdout.write(f"Warning removing {pkl}: {e}")

        # Seed fresh baseline GAM-v1
        from predictor.services.model_versioning import ensure_baseline_version
        ensure_baseline_version()

        # 8. Verify post-reset counts
        post_counts = {
            "ScreeningRecord": ScreeningRecord.objects.count(),
            "ScreeningExplanation": ScreeningExplanation.objects.count(),
            "HumanReview": HumanReview.objects.count(),
            "Stage2Assessment": Stage2Assessment.objects.count(),
            "HumanFeedback": HumanFeedback.objects.count(),
            "FeedbackLearningBatch": FeedbackLearningBatch.objects.count(),
            "SimilarCaseComparison": SimilarCaseComparison.objects.count(),
            "ControlledFeedbackExperiment": ControlledFeedbackExperiment.objects.count(),
            "ModelVersion": ModelVersion.objects.count(),
            "Prediction (legacy)": Prediction.objects.count(),
            "Override (legacy)": Override.objects.count(),
            "EvaluationRespondent": EvaluationRespondent.objects.count(),
            "EvaluationSession": EvaluationSession.objects.count(),
            "EvaluationEvent": EvaluationEvent.objects.count(),
            "QuestionnaireResponse": QuestionnaireResponse.objects.count(),
            "Session": Session.objects.count(),
        }

        # 9. Verify db_evaluation.sqlite3 was completely untouched
        eval_hash_after = compute_sha256(eval_db_path) if eval_db_path.exists() else None
        eval_untouched = (eval_hash_before == eval_hash_after)

        # 10. Verify frozen ML artifacts integrity
        gam_path = repo_root / "nhanes_feasibility_2021_2023" / "models_phase5" / "gam_final.pkl"
        prep_path = repo_root / "nhanes_feasibility_2021_2023" / "models_phase5" / "preprocessor.pkl"
        expected_gam_hash = "204a94ff072ef4f1edecebf5a643738c006bbf010f3817b4bb798d3ea6fef41d"
        expected_prep_hash = "6e56a01993a4a6971eb62c82699c49da6f31a3acec2a1169e07862409f42824d"

        current_gam_hash = compute_sha256(gam_path)
        current_prep_hash = compute_sha256(prep_path)

        gam_intact = (current_gam_hash == expected_gam_hash)
        prep_intact = (current_prep_hash == expected_prep_hash)

        # 11. Output results
        self.stdout.write(self.style.SUCCESS("\n=================================================="))
        self.stdout.write(self.style.SUCCESS("FEEDBACK LAB DATABASE RESET SUMMARY"))
        self.stdout.write(self.style.SUCCESS("=================================================="))
        self.stdout.write(f"Target Database: {db_filename}")
        self.stdout.write(f"Candidate Adaptations Removed: {cleared_adaptations}")
        self.stdout.write("\nTable Row Counts:")
        for table, pre_val in pre_counts.items():
            post_val = post_counts[table]
            self.stdout.write(f"  - {table}: {pre_val} -> {post_val}")

        self.stdout.write(f"\ndb_evaluation.sqlite3 Untouched: {eval_untouched}")
        if eval_hash_before:
            self.stdout.write(f"  SHA-256 Before: {eval_hash_before}")
            self.stdout.write(f"  SHA-256 After:  {eval_hash_after}")

        self.stdout.write(f"\nFrozen ML Artifacts:")
        self.stdout.write(f"  gam_final.pkl Intact:    {gam_intact} ({current_gam_hash[:16]}...)")
        self.stdout.write(f"  preprocessor.pkl Intact: {prep_intact} ({current_prep_hash[:16]}...)")

        all_zero_except_baseline = all(
            v == 0 for k, v in post_counts.items() if k != "ModelVersion"
        ) and (post_counts["ModelVersion"] <= 1)

        if all_zero_except_baseline and eval_untouched and gam_intact and prep_intact:
            self.stdout.write(
                self.style.SUCCESS("\n[SUCCESS] Feedback Lab database cleanly reset. Baseline GAM-v1 ready.")
            )
        else:
            raise CommandError("Post-reset validation check failed.")
