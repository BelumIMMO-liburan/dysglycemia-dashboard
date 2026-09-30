"""
Management command to idempotently seed approved Feedback Lab research records
into the production Feedback Lab database.

GOVERNANCE & SAFETY:
- Executes ONLY when APP_MODE == 'feedback_lab'.
- Atomic transaction: rolls back completely on any failure.
- Strictly idempotent: never overwrites or mutates existing identical records.
- Preserves all UUIDs, timestamps, stored probabilities, and deltas without modification.
- Contains ZERO participant evaluation data and ZERO user credentials.
- Executes runtime verification of canonical Case B response under RA-v3 post-seed.
"""

import json
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.core import serializers
from django.db import transaction
from django.conf import settings

from predictor.services.feedback_learning import (
    CONTROLLED_CASE_B_DATA,
    verify_no_final_test_leakage,
)
from predictor.services.adapted_inference import predict_adapted
from predictor.models import (
    ModelVersion,
    ControlledFeedbackExperiment,
    FeedbackLearningBatch,
    SimilarCaseComparison,
    HumanFeedback,
    HumanReview,
    ScreeningExplanation,
    ScreeningRecord,
)


class Command(BaseCommand):
    help = "Seed verified Feedback Lab research data into production database (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-if-wrong-mode",
            action="store_true",
            help="If APP_MODE is not 'feedback_lab', exit cleanly with status 0 instead of raising error.",
        )
        parser.add_argument(
            "--fixture",
            type=str,
            default=None,
            help="Custom path to seed JSON fixture.",
        )

    def handle(self, *args, **options):
        current_mode = getattr(settings, "APP_MODE", "evaluation")
        skip_if_wrong = options["skip_if_wrong_mode"]

        if current_mode != "feedback_lab":
            msg = (
                f"Refusing to seed Feedback Lab research data: APP_MODE is '{current_mode}' "
                f"(expected 'feedback_lab')."
            )
            if skip_if_wrong:
                self.stdout.write(self.style.WARNING(f"[SEED SKIP] {msg}"))
                return
            else:
                raise CommandError(f"[FAIL-CLOSED] {msg}")

        fixture_path = options["fixture"]
        if fixture_path:
            p = Path(fixture_path)
        else:
            p = Path(__file__).resolve().parent.parent.parent / "fixtures" / "feedback_lab_production_seed.json"

        if not p.is_file():
            raise CommandError(f"Seed fixture not found at: {p}")

        self.stdout.write(self.style.NOTICE(f"Loading Feedback Lab seed from: {p}"))

        with open(p, "r", encoding="utf-8") as f:
            fixture_json = f.read()

        deserialized_objects = list(serializers.deserialize("json", fixture_json))
        total_in_fixture = len(deserialized_objects)

        created_counts = {}
        existing_counts = {}

        with transaction.atomic():
            for obj in deserialized_objects:
                model_cls = obj.object.__class__
                model_name = model_cls.__name__
                pk = obj.object.pk

                if model_cls.objects.filter(pk=pk).exists():
                    existing_counts[model_name] = existing_counts.get(model_name, 0) + 1
                else:
                    obj.save()
                    created_counts[model_name] = created_counts.get(model_name, 0) + 1

        self.stdout.write(self.style.SUCCESS(f"Seeding completed successfully. Total objects in fixture: {total_in_fixture}"))
        self.stdout.write("Created records:")
        for m, count in sorted(created_counts.items()):
            self.stdout.write(f"  + {m}: {count}")
        if not created_counts:
            self.stdout.write("  (No new records created; all existed)")

        self.stdout.write("Existing pre-seed records preserved:")
        for m, count in sorted(existing_counts.items()):
            self.stdout.write(f"  = {m}: {count}")

        # Post-Seed Verification Pass
        self.stdout.write("\nRunning post-seed verification checks...")

        # 1. ModelVersion check
        active_version = ModelVersion.objects.filter(is_active=True).first()
        if not active_version or active_version.version_label != "RA-v3":
            raise CommandError(f"Post-seed check failed: Active ModelVersion is {active_version}, expected RA-v3.")
        self.stdout.write(self.style.SUCCESS(f"  [PASS] Active ModelVersion: {active_version.version_label}"))

        # 2. Canonical Case B reproduction under RA-v3
        res = predict_adapted(CONTROLLED_CASE_B_DATA)
        p0 = round(res.baseline_probability, 6)
        p_prime = round(res.adapted_probability, 6)
        delta_p = round(res.delta_probability, 6)

        expected_p0 = 0.311198
        expected_p_prime = 0.270523
        expected_delta_p = -0.040675

        if p0 != expected_p0 or p_prime != expected_p_prime or delta_p != expected_delta_p:
            raise CommandError(
                f"Post-seed check failed: Case B response (P0={p0}, P'={p_prime}, delta={delta_p}) "
                f"does not match expected (P0={expected_p0}, P'={expected_p_prime}, delta={expected_delta_p})."
            )
        self.stdout.write(self.style.SUCCESS(
            f"  [PASS] Canonical Case B: P0={p0:.6f}, P'={p_prime:.6f}, delta={delta_p:+.6f}"
        ))

        # 3. Final-test leakage verification
        leak_ok, leak_msg = verify_no_final_test_leakage(HumanFeedback.objects.all())
        if not leak_ok:
            raise CommandError(f"Post-seed check failed: {leak_msg}")
        self.stdout.write(self.style.SUCCESS(f"  [PASS] Final-test leakage: {leak_msg}"))

        self.stdout.write(self.style.SUCCESS("\n[SUCCESS] Feedback Lab production seed is complete and verified."))
