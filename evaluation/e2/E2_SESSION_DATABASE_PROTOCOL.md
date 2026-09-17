# Session Database Isolation & Archival Protocol (Phase E2)
## Operational Protocol for Per-Participant SQLite State Management

**Document Identifier:** `E2-SESSION-DB-PROTOCOL-V1.0`  
**Evaluation Phase:** `E2` (Pilot Instrument Package & Operationalization)  
**Governing Protocol:** `v1.0.3` (`E1-PROTOCOL-2026-V1.0.3`)  
**Package Version:** `1.0`  
**Date:** 2026-09-05  

---

## 1. Context & Isolation Mandate

In the formal evaluation protocol, every participant executes the exact same standardized synthetic task scenarios:
- Task 1: Non-laboratory screening intake for `CASE-ALPHA`.
- Task 2: Inspection of `CASE-ALPHA` explanation and factors.
- Task 3: Guided human review (Accept) for `CASE-ALPHA`.
- Task 4: Screening intake and human override for `CASE-BETA`.
- Task 5: Stage-2 HbA1c laboratory assessment for `CASE-ALPHA`.
- Task 6: Screening History and audit trail inspection for `CASE-BETA`.

### Critical State Isolation Problem:
If multiple participants share a cumulative database, Participant 2 would see Participant 1's completed screenings in the Screening History table (`/history/`) and Review Queue (`/review-queue/`). This would:
1. Spoil the outcome of Task 6 before the participant performs it.
2. Violate the standardized zero-state experimental controls established in Phase E1.
3. Expose prior participants' timestamps, reviewer codes, and override notes.

### Mandatory Operational Solution:
**Strict Per-Participant Database Isolation:**
Every evaluation session begins with a pristine zero-state database cloned from [`db_session_template.sqlite3`](file:///c:/Users/Felix/Documents/Skripsi/evaluation/e2/runtime/db_session_template.sqlite3). Following session completion, the active database is frozen, archived under the participant code, hashed via SHA-256, and verified prior to restoring a fresh template.

```
+----------------------------------------------------------------------------------------------------+
|                                PER-PARTICIPANT ISOLATION LIFECYCLE                                 |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|   [ Pristine Template ]                                                                            |
|   evaluation/e2/runtime/db_session_template.sqlite3                                                |
|            │                                                                                       |
|            ▼ (Copy before session)                                                                 |
|   [ Active Session DB ]                                                                            |
|   dashboard/db_study.sqlite3 ──► (Verify 0 records) ──► Participant runs Tasks 1–6                 |
|            │                                                                                       |
|            ▼ (Freeze & Copy post-session)                                                          |
|   [ Session Archive ]                                                                              |
|   evaluation/e2/archives/{participant_code}_dashboard.sqlite3                                      |
|            │                                                                                       |
|            ├───► Compute & verify SHA-256 hash                                                     |
|            ├───► Validate relational row counts (Alpha completed, Beta pending)                    |
|            └───► Log entry in evaluation/e2/templates/session_manifest.csv                         |
|                                                                                                    |
|            ▼ (Restore fresh template)                                                              |
|   [ Active Session DB Reset ]                                                                      |
|   dashboard/db_study.sqlite3 (Ready for next participant)                                          |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Zero-State Database Template Specification

The canonical session template is located at:
`evaluation/e2/runtime/db_session_template.sqlite3`

### Invariant Properties:
1. **Migrations Current:** Synced to migration head `predictor.0006_stage2assessment`.
2. **Domain Row Counts Strictly Zero:**
   - `ScreeningRecord` count = **0**
   - `ScreeningExplanation` count = **0**
   - `HumanReview` count = **0**
   - `Stage2Assessment` count = **0**
3. **No Synthetic QA Rows:** Contains zero legacy or demo screening records.

---

## 3. Step-by-Step Session Execution Procedure

### Stage A: Pre-Session Setup (Before Welcoming Participant)

1. **Verify Environment Mode:**  
   Ensure Django runs in study mode (`APP_DATA_MODE=study`), which directs all database I/O to `db_study.sqlite3`.
2. **Verify Software Release Integrity:**  
   Confirm that all 144 automated unit/integration tests pass and the 4 protected artifact hashes match baseline.
3. **Clone Pristine Template:**  
   Copy `evaluation/e2/runtime/db_session_template.sqlite3` to `dashboard/db_study.sqlite3`.
4. **Execute Zero-Count Verification:**  
   Execute the verification query to confirm that all 4 domain tables contain exactly 0 rows:
   ```bash
   py -3.10 -c "
   import sqlite3
   conn = sqlite3.connect('dashboard/db_study.sqlite3')
   cur = conn.cursor()
   for t in ['predictor_screeningrecord', 'predictor_screeningexplanation', 'predictor_humanreview', 'predictor_stage2assessment']:
       cur.execute(f'SELECT count(*) FROM {t}')
       assert cur.fetchone()[0] == 0, f'Non-zero rows in {t}'
   conn.close()
   print('ZERO-STATE VERIFIED')
   "
   ```
5. **Launch Application:**  
   Start local development server: `py -3.10 manage.py runserver` (with `APP_DATA_MODE=study`).
6. **Assign Participant Code:**  
   Prepare physical participant code card (e.g., `PILOT001`).

---

### Stage B: Post-Session Archival (Immediately Following Debriefing)

1. **Stop / Quiesce Local Server:**  
   Terminate server process (`Ctrl+C`) to guarantee all SQLite write locks and journal files are flushed.
2. **Copy to Archive Vault:**  
   Copy `dashboard/db_study.sqlite3` to:
   `evaluation/e2/archives/{participant_code}_dashboard.sqlite3`
   *(Example: `evaluation/e2/archives/PILOT001_dashboard.sqlite3`)*
3. **Compute SHA-256 Digest:**  
   Compute the cryptographic hash of the archived SQLite file:
   ```bash
   certutil -hashfile evaluation/e2/archives/{participant_code}_dashboard.sqlite3 SHA256
   ```
4. **Relational Completeness & Integrity Audit:**  
   Execute an automated check on the archived file to verify expected task completion:
   - `ScreeningRecord` count = **2**
   - `ScreeningExplanation` count = **2**
   - `HumanReview` count = **2** (`reviewer_code == participant_code`)
     - One `accepted` (`CASE-ALPHA`)
     - One `overridden` (`CASE-BETA`, reason: `precautionary_referral`)
   - `Stage2Assessment` count = **1** (`CASE-ALPHA` only, range: `prediabetes_range`)
   - `CASE-BETA` lifecycle status = `pending_stage2`
5. **Log Session Manifest Record:**  
   Append a row to `evaluation/e2/templates/session_manifest.csv` with the participant code, archive path, SHA-256 hash, and completion status.
6. **Fresh Template Restoration:**  
   Restore `evaluation/e2/runtime/db_session_template.sqlite3` over `dashboard/db_study.sqlite3` so that no traces of the completed session remain for the next participant.
7. **Prohibition on Overwriting:**  
   Never overwrite an existing session archive file. If an archive file already exists with that code, halt immediately to investigate identifier collision.
