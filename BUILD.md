# Build BXD Smart Office V1.0 LTS

## Windows Build

Run from the repository root:

```powershell
.\build_release.ps1
```

The script cleans old build artifacts, creates a PyInstaller one-folder build, attempts a one-file build unless `-SkipOneFile` is passed, and runs release verification.

## Batch Wrapper

```cmd
build_windows.bat
```

## Clean Only

```powershell
.\clean_build.ps1
```

## Verify Only

```powershell
python verify_release.py
```

## Bundled Assets

The build includes:

- `app`
- `core`
- `database` schema and migrations
- `models`
- `modules`
- `repositories`
- `services`
- `templates`
- `static`

Runtime data is written beside the executable, not inside the PyInstaller temporary extraction folder.
