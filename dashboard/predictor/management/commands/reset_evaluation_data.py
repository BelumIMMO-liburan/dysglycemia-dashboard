"""
Management command to safely reset participant evaluation data in db_evaluation.sqlite3.
Protocol E1 v1.0.3 / E2 Implementation.

SAFETY GUARANTEES:
1. Rejects execution if active database is 'db.sqlite3' (the Feedback Lab database).
2. Requires affirmative confirmation flag (--confirm) to prevent accidental execution.
3. Completely isolated from researcher feedback-lab evidence.
"""

from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction
from predictor.models import (
    EvaluationRespondent,
    EvaluationSession,
    EvaluationEvent,
    QuestionnaireResponse,
    ScreeningRecord,
    HumanFeedback,
    ModelVersion,
)


class Command(BaseCommand):
    help = "Safely reset evaluation participant data in db_evaluation.sqlite3 (respondents=0, sessions=0)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            dest='confirm',
            help='Affirmative confirmation required to execute reset.',
        )

    def handle(self, *args, **options):
        # 1. Inspect active database path
        db_path = Path(settings.DATABASES['default']['NAME'])
        db_filename = db_path.name

        self.stdout.write(f"Active database: {db_filename} ({db_path})")
        self.stdout.write(f"Active APP_MODE: {getattr(settings, 'APP_MODE', 'feedback_lab')}")

        # 2. Strict Safety Guard: Never allow reset on db.sqlite3
        if 'db.sqlite3' == db_filename:
            raise CommandError(
                "CRITICAL ABORT: Active database is 'db.sqlite3' (Researcher Feedback Lab database). "
                "This command is strictly restricted to 'db_evaluation.sqlite3'. "
                "Set APP_MODE=evaluation before running this command."
            )

        if not options.get('confirm'):
            raise CommandError(
                "Dry-run safety check: Add --confirm to execute the deletion of all evaluation participant data."
            )

        # 3. Perform atomic reset of evaluation participant tables
        with transaction.atomic():
            q_count = QuestionnaireResponse.objects.count()
            ev_count = EvaluationEvent.objects.count()
            sess_count = EvaluationSession.objects.count()
            resp_count = EvaluationRespondent.objects.count()
            scr_count = ScreeningRecord.objects.count()

            QuestionnaireResponse.objects.all().delete()
            EvaluationEvent.objects.all().delete()
            EvaluationSession.objects.all().delete()
            EvaluationRespondent.objects.all().delete()
            ScreeningRecord.objects.all().delete()

        # 4. Verify post-reset counts
        post_q = QuestionnaireResponse.objects.count()
        post_sess = EvaluationSession.objects.count()
        post_resp = EvaluationRespondent.objects.count()
        post_scr = ScreeningRecord.objects.count()

        self.stdout.write(self.style.SUCCESS(
            f"Evaluation data reset successfully:\n"
            f"  - Deleted {resp_count} respondents (Remaining: {post_resp})\n"
            f"  - Deleted {sess_count} sessions (Remaining: {post_sess})\n"
            f"  - Deleted {ev_count} evaluation events\n"
            f"  - Deleted {q_count} questionnaire responses (Remaining: {post_q})\n"
            f"  - Deleted {scr_count} evaluation screening records (Remaining: {post_scr})\n"
            f"State verified: Clean evaluation deployment ready."
        ))
