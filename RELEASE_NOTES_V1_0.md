# BXD Smart Office V1.0.0 LTS Release Notes

## Release

V1.0.0 LTS is the offline production release candidate for BXD Smart Office.

## Included

- Dashboard, profile, task, workspace and audit workflows.
- Document template and draft workflow with DOCX export.
- Document Library indexing and full-text Knowledge handoff.
- Chunk, embedding, vector index, citation and AI Search workflows.
- AI Draft final validation before export.
- Advisory Report Engine with evidence-backed recommendations and human approval.
- Windows packaging scripts and release verification.

## Offline Guarantee

The release is designed for SQLite and local files. No cloud API, chatbot, assistant, agent or internet dependency is required for core workflows.

## Verification

Required release commands:

```powershell
python -m database.init_db
python -m pytest -q
python verify_release.py
```

## Packaging

Windows packaging is automated by:

- `build_windows.bat`
- `build_release.ps1`
- `clean_build.ps1`
- `verify_release.py`
