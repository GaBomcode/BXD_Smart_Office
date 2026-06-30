# Deployment Checklist V1.0 LTS

## Before Build

- Confirm `APP_VERSION` is `1.0.0`.
- Run `python -m database.init_db`.
- Run `python -m pytest -q`.
- Confirm `verify_release.py` passes.

## Build

- Run `.\build_release.ps1`.
- Confirm `dist\BXD-Smart-Office\BXD-Smart-Office.exe` exists.
- If one-file build is enabled, confirm `dist\BXD-Smart-Office.exe` exists.

## Target Machine

- Copy the one-folder build to the offline machine.
- Start the app.
- Confirm database, logs, backups, exports and workspace folders are created.
- Index a small document folder.
- Create or open a workspace.
- Validate an AI Draft before export.
- Generate an advisory report and approve it for export readiness.

## Release Gate

Release is approved only when:

- Clean build succeeds.
- Release verification passes.
- Regression suite passes.
- No cloud API or internet dependency is required.
