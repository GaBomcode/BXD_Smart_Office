from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "database"
DB_PATH = DATA_DIR / "bxd_smart_office.db"
LOG_DIR = BASE_DIR / "logs"
UPLOAD_DIR = BASE_DIR / "workspace" / "uploads" / "evidence"
EXPORT_DIR = BASE_DIR / "workspace" / "exports"
BACKUP_DIR = BASE_DIR / "backups"
DOCUMENT_DIR = BASE_DIR / "documents"
DOCUMENT_TEMPLATE_DIR = DOCUMENT_DIR / "templates"
DOCUMENT_DRAFT_DIR = DOCUMENT_DIR / "drafts"
DOCUMENT_EXPORT_DIR = DOCUMENT_DIR / "exports"
WORKSPACE_DIR = BASE_DIR / "workspace"
ATTACHMENT_DIR = WORKSPACE_DIR / "attachments"
CACHE_DIR = WORKSPACE_DIR / "cache"
TEMP_DIR = WORKSPACE_DIR / "temp"

for path in [
    DATA_DIR,
    LOG_DIR,
    UPLOAD_DIR,
    EXPORT_DIR,
    BACKUP_DIR,
    DOCUMENT_TEMPLATE_DIR,
    DOCUMENT_DRAFT_DIR,
    DOCUMENT_EXPORT_DIR,
    ATTACHMENT_DIR,
    CACHE_DIR,
    TEMP_DIR,
]:
    path.mkdir(parents=True, exist_ok=True)
