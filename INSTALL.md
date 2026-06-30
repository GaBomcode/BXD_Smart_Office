# Install BXD Smart Office V1.0 LTS

## Requirements

- Windows 10/11
- Python 3.12+
- Offline wheelhouse or pre-downloaded dependencies for production installs

## Source Install

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m database.init_db
python -m pytest -q
python -m streamlit run app/main.py
```

## Packaged Install

1. Build with `build_release.ps1`.
2. Copy `dist\BXD-Smart-Office\` to the target machine.
3. Run `verify_release.py` once on the target source folder or run the packaged executable.
4. Keep `database\`, `logs\`, `backups\`, `documents\`, and `workspace\` beside the executable.

The application is offline-first. It does not require internet or cloud AI.
