# Railway Persistent Database Configuration Guide (PostgreSQL & Persistent Volumes)
**Protocol E1 / E2 Participant Data Preservation**

---

## 1. Executive Summary & Critical Risk Assessment

In Railway deployments, container filesystems are **ephemeral** by default. Any deployment, build restart, container crash, or manual restart recreates the container image from scratch, wiping all files not stored on a persistent service or mounted on a volume.

By connecting to **Railway PostgreSQL** (or using a Persistent Volume mount), **participant research data (evaluation respondents, completed sessions, event logs, questionnaire responses, screening records, and human review decisions) is fully preserved across restarts and redeployments.**

---

## 2. Railway PostgreSQL Setup (Recommended)

When you create a PostgreSQL service / database in your Railway project:

1. Railway automatically provisions a managed PostgreSQL instance with persistent storage.
2. In your Django service, link the PostgreSQL database or ensure the variable `DATABASE_URL` is available:
   - Railway typically sets `DATABASE_URL` automatically if both services are in the same project.
   - If not automatically linked, go to your Django service **Variables** tab $\to$ **New Variable** $\to$ **Add Reference** $\to$ select `DATABASE_URL` from the Postgres service.
3. The Django application's `dashboard/dashboard/settings.py` automatically detects `DATABASE_URL` using `dj-database-url` and connects to PostgreSQL.
4. On deployment, `Procfile` runs `python dashboard/manage.py migrate`, automatically applying all 11 schema migrations to PostgreSQL.

### Step 3: Verify Automated Path Resolution
The Django settings file (`dashboard/dashboard/settings.py`) has been updated to automatically detect absolute paths:
```python
db_path = Path(raw_db_name)
if not db_path.is_absolute():
    db_path = BASE_DIR / db_path

# Ensure parent directory exists for volume mounts
try:
    db_path.parent.mkdir(parents=True, exist_ok=True)
except Exception:
    pass
```
When `DB_NAME=/data/db_evaluation.sqlite3` is set, Django recognizes it as an absolute path, creates `/data` if needed, and binds the SQLite backend to `/data/db_evaluation.sqlite3`.

---

## 3. Persistent vs Ephemeral SQLite Path Comparison

| Property | Ephemeral (Default / Unconfigured) | Persistent (Volume Mounted) |
| :--- | :--- | :--- |
| **Path** | `./db_evaluation.sqlite3` (`BASE_DIR / DB_NAME`) | `/data/db_evaluation.sqlite3` |
| **Storage Medium** | Container root overlayfs | Attached Railway block volume (`/data`) |
| **Survives App Restart** | ❌ NO (Container killed = data erased) | ✅ YES |
| **Survives Git Push / Redeploy**| ❌ NO (New build image replaces old) | ✅ YES (Volume reattached to new container) |
| **Survives Crash / Out-of-Memory**| ❌ NO | ✅ YES |
| **Audit & Research Safety** | 🚨 FATAL VIOLATION (Loss of human trials) | 🛡️ SECURE (Preserves all trials) |

---

## 4. Deploy & Verification Procedures

### Verifying Volume Mount and Database File via Railway CLI
Using the Railway CLI on your local terminal:

```bash
# 1. Open an interactive shell inside the running Railway container
railway run bash

# 2. Check that the /data volume mount exists and is writable
ls -ld /data
touch /data/.volume_test && rm /data/.volume_test && echo "Volume is writable"

# 3. Check current database file location and size
ls -lh /data/db_evaluation.sqlite3

# 4. Check migration status on the persistent database
python dashboard/manage.py showmigrations

# 5. Verify participant record count
python dashboard/manage.py shell -c "
from predictor.models import EvaluationRespondent, EvaluationSession, QuestionnaireResponse
print('Respondents:', EvaluationRespondent.objects.count())
print('Sessions:', EvaluationSession.objects.count())
print('Responses:', QuestionnaireResponse.objects.count())
"
```

---

## 5. Automated / Manual Backup Protocol

To guarantee zero data loss even in the event of cloud provider incidents, conduct regular snapshots:

### Manual Backup Download via Export Endpoint
Researchers can download the complete atomic data dump at any time by visiting:
```
https://your-domain.up.railway.app/evaluation/export/?key=YOUR_RESEARCHER_ACCESS_KEY
```
This returns `evaluation_export_<timestamp>.zip` containing all 7 CSV files, SHA-256 manifest, and documentation.

### Direct SQLite Backup via CLI
```bash
# From local terminal with railway CLI linked
railway run sqlite3 /data/db_evaluation.sqlite3 ".backup '/tmp/backup.sqlite3'"
# Copy out or upload to secure researcher storage
```

### Pre-Evaluation Checklist
Before admitting clinical participants:
- [ ] Railway Persistent Volume mounted at `/data`.
- [ ] `DB_NAME=/data/db_evaluation.sqlite3` confirmed in Railway service variables.
- [ ] `RESEARCHER_ACCESS_KEY` set to strong random string.
- [ ] Run test deployment or restart to confirm test participant record remains intact across restart.
