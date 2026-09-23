# Railway Persistent Volume Configuration Guide for Evaluation Mode
**Protocol E1 / E2 Participant Data Preservation**

---

## 1. Executive Summary & Critical Risk Assessment

In Railway deployments, container filesystems are **ephemeral** by default. Any deployment, build restart, container crash, or manual restart recreates the container image from scratch, wiping all files not mounted on a **Persistent Volume**.

If `db_evaluation.sqlite3` is located inside the application's local root (`/app/dashboard/db_evaluation.sqlite3` or relative path), **ALL participant research data (evaluation respondents, completed sessions, event logs, questionnaire responses, screening records, and human review decisions) will be PERMANENTLY DESTROYED upon redeployment or container restart.**

This guide outlines the mandatory steps to configure a persistent volume on Railway and direct SQLite to store `db_evaluation.sqlite3` on that persistent volume.

---

## 2. Railway Volume Setup Instructions

### Step 1: Create a Persistent Volume in Railway
1. Navigate to your project dashboard on [Railway.app](https://railway.app).
2. Select your web service card (the Django deployment running `APP_MODE=evaluation`).
3. In the service settings menu, click the **Volumes** tab.
4. Click **+ Add Volume**.
5. Configure the volume parameters:
   - **Mount Path**: `/data`
   - **Volume Name**: `evaluation-data` (or default generated name)
6. Click **Add**. Railway will provision and attach the volume to your service.

### Step 2: Configure Environment Variables
Navigate to the **Variables** tab of the service and configure:

| Variable Name | Required Value | Description |
| :--- | :--- | :--- |
| `APP_MODE` | `evaluation` | Enforces participant workflow isolation |
| `DB_NAME` | `/data/db_evaluation.sqlite3` | Directs SQLite to the persistent mount path |
| `RESEARCHER_ACCESS_KEY` | *(Set a secure 32+ char key)* | Protects `/evaluation/analytics/` and `/evaluation/export/` |
| `DJANGO_SETTINGS_MODULE` | `dashboard.settings` | Django settings entry point |

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
