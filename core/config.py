from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "database"
DB_PATH = DATA_DIR / "bxd_smart_office.db"
LOG_DIR = BASE_DIR / "logs"
UPLOAD_DIR = BASE_DIR / "workspace" / "uploads" / "evidence"
EXPORT_DIR = BASE_DIR / "workspace" / "exports"
BACKUP_DIR = BASE_DIR / "backups"

for path in [DATA_DIR, LOG_DIR, UPLOAD_DIR, EXPORT_DIR, BACKUP_DIR]:
    path.mkdir(parents=True, exist_ok=True)
