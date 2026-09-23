"""
Evaluation Research Data Export Service (Protocol E1 v1.0.3 / E2).

Generates a complete, de-identified research data export package as a ZIP archive:
evaluation_export_<timestamp>.zip

Contains:
1. respondents.csv
2. sessions.csv
3. events.csv
4. screening.csv (all screening runs with is_practice flag explicitly preserved)
5. human_review.csv
6. stage2.csv
7. questionnaire.csv
8. manifest.json (row counts, file sizes, and SHA-256 checksums)
9. README.txt (comprehensive codebook, data dictionary, and linkage guide)

DATA PRIVACY GUARANTEES:
- Zero passwords, session cookies, CSRF tokens, SECRET_KEY, or server secrets.
- Zero participant PII (names, emails, student IDs, IP addresses).
- 0 database writes, 0 ML inference, 0 model evaluations, 0 learning triggers.
"""

import csv
import hashlib
import io
import json
import zipfile
from datetime import datetime
from typing import Tuple, Dict, Any

from django.conf import settings
from django.utils import timezone

from ..models import (
    EvaluationRespondent,
    EvaluationSession,
    EvaluationEvent,
    QuestionnaireResponse,
    ScreeningRecord,
    HumanReview,
    Stage2Assessment,
)


def _compute_sha256(content: bytes) -> str:
    """Compute SHA-256 checksum for binary content."""
    h = hashlib.sha256()
    h.update(content)
    return h.hexdigest()


def generate_evaluation_export_zip() -> Tuple[bytes, str, Dict[str, Any]]:
    """
    Builds the complete in-memory ZIP archive for research data export.
    Returns:
        (zip_bytes, filename, manifest_dict)
    """
    timestamp_str = timezone.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"evaluation_export_{timestamp_str}.zip"

    manifest: Dict[str, Any] = {
        "export_identifier": f"EVAL_EXPORT_{timestamp_str}",
        "generated_at_utc": timezone.now().isoformat(),
        "app_version": getattr(settings, "APP_VERSION", "v1.0.3"),
        "protocol_version": getattr(settings, "EVALUATION_PROTOCOL_VERSION", "E1-v1.0.3"),
        "app_mode": getattr(settings, "APP_MODE", "evaluation"),
        "database_engine": settings.DATABASES["default"]["ENGINE"],
        "files": {},
    }

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        # =====================================================================
        # 1. respondents.csv
        # =====================================================================
        resp_buf = io.StringIO()
        resp_writer = csv.writer(resp_buf)
        resp_writer.writerow([
            "respondent_id",
            "respondent_code",
            "age_group",
            "education_level",
            "technical_background",
            "health_background",
            "consent_given",
            "consent_timestamp",
            "created_at",
        ])
        resp_count = 0
        for r in EvaluationRespondent.objects.all().order_by("created_at"):
            resp_writer.writerow([
                str(r.id),
                r.respondent_code,
                r.age_group,
                r.education_level,
                r.technical_background,
                r.health_background,
                1 if r.consent_given else 0,
                r.consent_timestamp.isoformat() if r.consent_timestamp else "",
                r.created_at.isoformat() if r.created_at else "",
            ])
            resp_count += 1

        resp_bytes = resp_buf.getvalue().encode("utf-8")
        zf.writestr("respondents.csv", resp_bytes)
        manifest["files"]["respondents.csv"] = {
            "rows": resp_count,
            "bytes": len(resp_bytes),
            "sha256": _compute_sha256(resp_bytes),
        }

        # =====================================================================
        # 2. sessions.csv
        # =====================================================================
        sess_buf = io.StringIO()
        sess_writer = csv.writer(sess_buf)
        sess_writer.writerow([
            "session_id",
            "respondent_id",
            "respondent_code",
            "status",
            "practice_completed",
            "questionnaire_completed",
            "is_excluded",
            "exclusion_reason",
            "exclusion_notes",
            "excluded_at",
            "app_version",
            "model_version",
            "started_at",
            "completed_at",
        ])
        sess_count = 0
        for s in EvaluationSession.objects.select_related("respondent").order_by("started_at"):
            sess_writer.writerow([
                str(s.id),
                str(s.respondent_id),
                s.respondent.respondent_code,
                s.status,
                1 if s.practice_completed else 0,
                1 if s.questionnaire_completed else 0,
                1 if s.is_excluded else 0,
                s.exclusion_reason or "",
                s.exclusion_notes or "",
                s.excluded_at.isoformat() if s.excluded_at else "",
                s.app_version,
                s.model_version,
                s.started_at.isoformat() if s.started_at else "",
                s.completed_at.isoformat() if s.completed_at else "",
            ])
            sess_count += 1

        sess_bytes = sess_buf.getvalue().encode("utf-8")
        zf.writestr("sessions.csv", sess_bytes)
        manifest["files"]["sessions.csv"] = {
            "rows": sess_count,
            "bytes": len(sess_bytes),
            "sha256": _compute_sha256(sess_bytes),
        }

        # =====================================================================
        # 3. events.csv
        # =====================================================================
        ev_buf = io.StringIO()
        ev_writer = csv.writer(ev_buf)
        ev_writer.writerow([
            "event_id",
            "session_id",
            "respondent_id",
            "respondent_code",
            "event_name",
            "event_data_json",
            "timestamp",
        ])
        ev_count = 0
        for ev in EvaluationEvent.objects.select_related("session__respondent").order_by("timestamp"):
            ev_writer.writerow([
                str(ev.id),
                str(ev.session_id),
                str(ev.session.respondent_id),
                ev.session.respondent.respondent_code,
                ev.event_name,
                json.dumps(ev.event_data or {}, ensure_ascii=False),
                ev.timestamp.isoformat() if ev.timestamp else "",
            ])
            ev_count += 1

        ev_bytes = ev_buf.getvalue().encode("utf-8")
        zf.writestr("events.csv", ev_bytes)
        manifest["files"]["events.csv"] = {
            "rows": ev_count,
            "bytes": len(ev_bytes),
            "sha256": _compute_sha256(ev_bytes),
        }

        # =====================================================================
        # 4. screening.csv
        # =====================================================================
        scr_buf = io.StringIO()
        scr_writer = csv.writer(scr_buf)
        scr_writer.writerow([
            "screening_id",
            "session_id",
            "respondent_id",
            "is_practice",
            "age",
            "sex",
            "bmi",
            "waist_cm",
            "hypertension_history",
            "smoking_history",
            "sedentary_minutes_day",
            "screening_probability",
            "ai_referral_recommended",
            "decision_threshold",
            "model_name",
            "model_sha256",
            "preprocessor_sha256",
            "input_schema_version",
            "idempotency_token",
            "created_at",
        ])
        scr_count = 0
        for sc in ScreeningRecord.objects.select_related("evaluation_session__respondent").order_by("created_at"):
            session_id = str(sc.evaluation_session_id) if sc.evaluation_session_id else ""
            resp_id = str(sc.evaluation_session.respondent_id) if (sc.evaluation_session and sc.evaluation_session.respondent_id) else ""
            scr_writer.writerow([
                str(sc.id),
                session_id,
                resp_id,
                1 if sc.is_practice else 0,
                sc.age,
                sc.sex,
                str(sc.bmi),
                str(sc.waist_cm),
                sc.hypertension_history,
                sc.smoking_history,
                sc.sedentary_minutes_day,
                round(sc.screening_probability, 6),
                1 if sc.ai_referral_recommended else 0,
                str(sc.decision_threshold),
                sc.model_name,
                sc.model_sha256,
                sc.preprocessor_sha256,
                sc.input_schema_version,
                sc.idempotency_token or "",
                sc.created_at.isoformat() if sc.created_at else "",
            ])
            scr_count += 1

        scr_bytes = scr_buf.getvalue().encode("utf-8")
        zf.writestr("screening.csv", scr_bytes)
        manifest["files"]["screening.csv"] = {
            "rows": scr_count,
            "bytes": len(scr_bytes),
            "sha256": _compute_sha256(scr_bytes),
        }

        # =====================================================================
        # 5. human_review.csv
        # =====================================================================
        rev_buf = io.StringIO()
        rev_writer = csv.writer(rev_buf)
        rev_writer.writerow([
            "human_review_id",
            "screening_id",
            "session_id",
            "respondent_id",
            "reviewer_code",
            "review_action",
            "final_referral_recommended",
            "override_reason_code",
            "override_note",
            "created_at",
        ])
        rev_count = 0
        for hr in HumanReview.objects.select_related("screening_record__evaluation_session__respondent").order_by("created_at"):
            sc = hr.screening_record
            sess = sc.evaluation_session if sc else None
            sess_id = str(sess.id) if sess else ""
            resp_id = str(sess.respondent_id) if sess else ""
            rev_writer.writerow([
                str(hr.id),
                str(hr.screening_record_id),
                sess_id,
                resp_id,
                hr.reviewer_code,
                hr.review_action,
                1 if hr.final_referral_recommended else 0,
                hr.override_reason_code or "",
                hr.override_note or "",
                hr.created_at.isoformat() if hr.created_at else "",
            ])
            rev_count += 1

        rev_bytes = rev_buf.getvalue().encode("utf-8")
        zf.writestr("human_review.csv", rev_bytes)
        manifest["files"]["human_review.csv"] = {
            "rows": rev_count,
            "bytes": len(rev_bytes),
            "sha256": _compute_sha256(rev_bytes),
        }

        # =====================================================================
        # 6. stage2.csv
        # =====================================================================
        s2_buf = io.StringIO()
        s2_writer = csv.writer(s2_buf)
        s2_writer.writerow([
            "stage2_id",
            "human_review_id",
            "screening_id",
            "session_id",
            "respondent_id",
            "hba1c_percent",
            "laboratory_range",
            "range_rule_version",
            "entry_method",
            "created_at",
        ])
        s2_count = 0
        for s2 in Stage2Assessment.objects.select_related("human_review__screening_record__evaluation_session__respondent").order_by("created_at"):
            hr = s2.human_review
            sc = hr.screening_record if hr else None
            sess = sc.evaluation_session if sc else None
            sess_id = str(sess.id) if sess else ""
            resp_id = str(sess.respondent_id) if sess else ""
            s2_writer.writerow([
                str(s2.id),
                str(s2.human_review_id),
                str(sc.id) if sc else "",
                sess_id,
                resp_id,
                str(s2.hba1c_percent),
                s2.laboratory_range,
                s2.range_rule_version,
                s2.entry_method,
                s2.created_at.isoformat() if s2.created_at else "",
            ])
            s2_count += 1

        s2_bytes = s2_buf.getvalue().encode("utf-8")
        zf.writestr("stage2.csv", s2_bytes)
        manifest["files"]["stage2.csv"] = {
            "rows": s2_count,
            "bytes": len(s2_bytes),
            "sha256": _compute_sha256(s2_bytes),
        }

        # =====================================================================
        # 7. questionnaire.csv
        # =====================================================================
        q_buf = io.StringIO()
        q_writer = csv.writer(q_buf)
        q_writer.writerow([
            "questionnaire_id",
            "respondent_id",
            "session_id",
            "respondent_code",
            "c1_answer",
            "c2_answer",
            "c3_answer",
            "c4_answer",
            "c5_answer",
            "c6_answer",
            "c7_answer",
            "c8_answer",
            "comprehension_score",
            "comprehension_pct",
            "sus_1",
            "sus_2",
            "sus_3",
            "sus_4",
            "sus_5",
            "sus_6",
            "sus_7",
            "sus_8",
            "sus_9",
            "sus_10",
            "sus_score",
            "clarity_1",
            "clarity_2",
            "clarity_3",
            "clarity_4",
            "clarity_5",
            "open_1",
            "open_2",
            "open_3",
            "app_version",
            "model_version",
            "submitted_at",
        ])
        q_count = 0
        for qr in QuestionnaireResponse.objects.select_related("respondent", "session").order_by("submitted_at"):
            q_writer.writerow([
                str(qr.id),
                str(qr.respondent_id),
                str(qr.session_id),
                qr.respondent.respondent_code,
                qr.c1_answer,
                qr.c2_answer,
                qr.c3_answer,
                qr.c4_answer,
                qr.c5_answer,
                qr.c6_answer,
                qr.c7_answer,
                qr.c8_answer,
                qr.comprehension_score,
                qr.comprehension_pct,
                qr.sus_1,
                qr.sus_2,
                qr.sus_3,
                qr.sus_4,
                qr.sus_5,
                qr.sus_6,
                qr.sus_7,
                qr.sus_8,
                qr.sus_9,
                qr.sus_10,
                qr.sus_score,
                qr.clarity_1,
                qr.clarity_2,
                qr.clarity_3,
                qr.clarity_4,
                qr.clarity_5,
                qr.open_1 or "",
                qr.open_2 or "",
                qr.open_3 or "",
                qr.app_version,
                qr.model_version,
                qr.submitted_at.isoformat() if qr.submitted_at else "",
            ])
            q_count += 1

        q_bytes = q_buf.getvalue().encode("utf-8")
        zf.writestr("questionnaire.csv", q_bytes)
        manifest["files"]["questionnaire.csv"] = {
            "rows": q_count,
            "bytes": len(q_bytes),
            "sha256": _compute_sha256(q_bytes),
        }

        # =====================================================================
        # 8. manifest.json
        # =====================================================================
        manifest["files_count"] = len(manifest["files"])
        manifest_bytes = json.dumps(manifest, indent=2, ensure_ascii=False).encode("utf-8")
        zf.writestr("manifest.json", manifest_bytes)

        # =====================================================================
        # 9. README.txt
        # =====================================================================
        readme_text = f"""================================================================================
DYSGLYCEMIA CLINICAL SCREENING DASHBOARD
PARTICIPANT EVALUATION RESEARCH DATA EXPORT PACKAGE
================================================================================

Export Identifier : {manifest['export_identifier']}
Generated UTC     : {manifest['generated_at_utc']}
Protocol Acuan    : {manifest['protocol_version']}
Aplikasi / Model  : {manifest['app_version']} / GAM-v1 (Frozen Threshold = 0.1389)

--------------------------------------------------------------------------------
1. STRUKTUR & RELASI DATASET
--------------------------------------------------------------------------------
Paket ini berisi 7 file CSV ternormalisasi yang saling terhubung secara deterministik:

EvaluationRespondent (respondents.csv)
      │
      └──< 1-to-N >── EvaluationSession (sessions.csv)
                            ├──< 1-to-N >── EvaluationEvent (events.csv)
                            ├──< 1-to-N >── ScreeningRecord (screening.csv)
                            │                     └──< 1-to-1 >── HumanReview (human_review.csv)
                            │                                           └──< 1-to-1 >── Stage2Assessment (stage2.csv)
                            └──< 1-to-1 >── QuestionnaireResponse (questionnaire.csv)

Kunci Penghubung (Linkage Keys):
- respondent_id : UUIDv4 unik responden anonim.
- session_id    : UUIDv4 unik sesi evaluasi partisipan.
- screening_id  : UUIDv4 unik kasus skrining Stage-1.
- human_review_id: UUIDv4 unik ulasan klinisi/manusia.

--------------------------------------------------------------------------------
2. DAFTAR FILE & JUMLAH BARIS
--------------------------------------------------------------------------------
1. respondents.csv     : {resp_count} baris (Profil demografi teranonimisasi & timestamp persetujuan)
2. sessions.csv        : {sess_count} baris (Status sesi, durasi, bendera selesai, & audit pembatalan)
3. events.csv          : {ev_count} baris (Log peristiwa milestone alur evaluasi)
4. screening.csv       : {scr_count} baris (Semua kasus skrining Stage-1 termasuk bendera is_practice)
5. human_review.csv    : {rev_count} baris (Keputusan human review, kode alasan override, & catatan)
6. stage2.csv          : {s2_count} baris (Hasil konfirmasi laboratorium HbA1c & kategori rentang)
7. questionnaire.csv   : {q_count} baris (Respons kuesioner 4 bagian: C1-C8, SUS, DQ1-DQ5, OQ1-OQ3)
8. manifest.json       : Metadata ekspor & checksum SHA-256 untuk verifikasi integritas file.

--------------------------------------------------------------------------------
3. TATA KELOLA KASUS LATIHAN (P0)
--------------------------------------------------------------------------------
Kasus orientasi P0 disimpan di screening.csv dengan atribut:
  is_practice = 1
Untuk analisis skrining penelitian riil, filter data menggunakan:
  is_practice == 0

--------------------------------------------------------------------------------
4. DEFINISI RESPONDEN VALID (E1 Protocol §6.1 & §6.2)
--------------------------------------------------------------------------------
Responden dihitung sebagai VALID dalam laporan akhir apabila memenuhi kriteria:
1. Memberikan persetujuan tertulis (consent_given = 1).
2. Menyelesaikan seluruh instrumen kuesioner digital (questionnaire_completed = 1).
3. Tidak dibatalkan pasca-studi akibat kegagalan teknis fatal, galat prosedur moderator,
   atau pelanggaran kriteria eligibilitas (is_excluded = 0).

Aturan Etis Mutlak (§6.2):
Sesi TIDAK BOLEH dibatalkan atau dihapus hanya karena skor SUS rendah, jumlah eror tinggi,
atau umpan balik kualitatif kurang memuaskan.

--------------------------------------------------------------------------------
5. PERLINDUNGAN PRIVASI DATA
--------------------------------------------------------------------------------
Dataset ini sepenuhnya bebas dari:
- Nama lengkap, email, nomor identitas (NIM/NIK), atau alamat IP.
- Cookie sesi browser, token CSRF, kata sandi, dan secret keys.
================================================================================
"""
        zf.writestr("README.txt", readme_text.encode("utf-8"))

    zip_buffer.seek(0)
    return zip_buffer.getvalue(), zip_filename, manifest
