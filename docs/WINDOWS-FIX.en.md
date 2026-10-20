# Windows initialization repair

Document ID: HWI4U-WINDOWS-FIX · Version: 1 · 2026-10-20

This is a focused **0.13.1 / schema 21** repair based on main revision 30befe1. It does not import the later 0.21.0 TEST features or upgrade a newer inventory. Main previously contained 0.13.0, despite the wiki describing newer development branches. Use the fix/windows-init branch until reviewed and merged; a main ZIP does not contain this fix before merge. No migration/schema constraint is changed. Keep UUIDs, source metadata and TEST/production separation.

## Diagnosis and changes

User-reported Windows run: Python 3.14.8, PySide6/shiboken6 6.11.2, 121 tests, one failure and five errors. The supplied transcript is private evidence and is not published. Code inspection confirms: (1) a SQLite transaction context does not close its connection; tests now combine explicit closing with the original commit/rollback scope, before temporary-directory cleanup; (2) connection setup could raise on a busy schema read before the caller entered closing; inventory.connect closes on every failed setup; (3) a fixture stored native Windows separators in a managed relative path; it now uses as_posix, matching production import paths and unchanged CHECK rules; (4) Qt image readers retained source/managed file handles during exception cleanup; explicit QFile/finally scopes now close them in PhotoStore and SourceStore; (5) the name test guessed a 300 ms delay for a 200 ms Qt debounce. It now observes the actual timeout with QSignalSpy and processes events until that signal, with a failure deadline, retaining the duplicate-name assertion and real validation. No test or assertion is disabled; SQL constraints remain unchanged.

The original FOREIGN KEY failure is expected for a missing device; cleanup must preserve that error rather than replace it with WinError32. New tests retain the error traceback while immediately deleting files/checking closed connections. The About query also closes its connection if reading fails.

## Fonts and warnings

The transcript's QFontDatabase Cannot find font directory warning belongs to the offscreen test plugin, not proof that native Windows rendering is broken. Child-test configuration uses the existing WINDIR/Fonts directory if present and no explicit QT_QPA_FONTDIR is set. No fonts are copied, downloaded or redistributed; native desktop launches keep the Windows Qt backend. Missing directories remain visible warnings rather than being suppressed. Existing explicit font configuration is respected. Offscreen propagateSizeHints/raise/keyboard-grab capability messages are recorded as test-plugin limitations, not SQLite failures. ResourceWarnings about unclosed databases are defects: the diagnostic runner records them and fails if any remain after deferred Qt deletion and garbage collection. This does not hide warnings or weaken assertions.

## New isolated Windows setup

Prerequisites: Windows x64; Python 3.14.8 selected via py -3.14, not a different global python (the report also showed Python 3.15.0); internet for dependencies/source; existing Windows fonts for offscreen tests. A virtual environment isolates dependencies. The initial setup runs the complete suite before selecting an empty workspace; it refuses existing directories. Keep C:/INSTALL/hwi4u-main and LOCALAPPDATA/HWI4U-Test unchanged for diagnosis. Do not rerun init against that partially created directory or delete it merely to bypass the error. No personal inventory is imported into the new workspace.

```powershell
# Download the fix into a NEW source folder; keep the failed installation.
$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$zip = Join-Path $env:TEMP "hwi4u-windows-fix-$stamp.zip"
$destination = "C:\INSTALL\HWI4U-Windows-Fix-$stamp"
if (Test-Path $destination) { throw 'Choose a new source destination.' }
Invoke-WebRequest 'https://github.com/aniziusz/hwi4u/archive/refs/heads/fix/windows-init.zip' -OutFile $zip
Expand-Archive -LiteralPath $zip -DestinationPath $destination
$source = (Get-ChildItem -LiteralPath $destination -Directory | Select-Object -First 1).FullName
Set-Location $source
py -3.14 -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
.\.venv\Scripts\python.exe -c "import sys, PySide6, shiboken6; print(sys.version); print(PySide6.__version__, shiboken6.__version__)"
$workspace = Join-Path $env:LOCALAPPDATA "HWI4U-Windows-Fixed-$stamp"
if (Test-Path $workspace) { throw 'Choose a new workspace.' }
.\.venv\Scripts\python.exe manage.py init --workspace $workspace
if ($LASTEXITCODE -ne 0) { throw 'Initialization failed; retain this folder and inspect the error.' }
.\.venv\Scripts\python.exe manage.py test --workspace $workspace
```

The exact tested commit and CI run are provided in the repair pull request/project record. The branch download above can move; use the commit ZIP from the pull request for a fixed snapshot. Verify Python/PySide6 versions before initialization. PowerShell activation is unnecessary: explicit .venv/Scripts/python.exe avoids execution-policy changes and global interpreter confusion. Later sessions must use the saved source and workspace paths, not generate a new workspace each time:

```powershell
Set-Location 'C:\INSTALL\<new source folder>'
.\.venv\Scripts\python.exe manage.py test --workspace '<saved workspace path>'
```

## Reproduce verification and recovery

```powershell
.\.venv\Scripts\python.exe tools/windows_regressions.py --phase targeted --output dist/checks
.\.venv\Scripts\python.exe tools/windows_regressions.py --phase full --output dist/checks
.\.venv\Scripts\python.exe tools/windows_startup_smoke.py --output dist/startup
```

The first command executes all six reported tests plus five new lifetime/font checks. The full suite contains 126 tests (original 121 retained). Reports record actual Python/Qt, errors/failures/skips, ResourceWarnings and Qt messages. CI runs these in order on Windows2025 x64 and Ubuntu24.04 using Python3.14.8/Qt6.11.2. A configured workflow alone is not a pass claim; actual run results are recorded in the pull request. Linux local tests use Python3.14.7 separately. Startup smoke creates another new fictional workspace through manage.py init with its full test gate. On Windows it launches the actual manage.py test supervisor, verifies a visible native TEST window belonging only to that process tree and the matching launch receipt, captures it, closes it normally with WM_CLOSE and checks exit0. On failure only that test process tree is cleaned up. Linux uses the initialized dataset and offscreen TEST form; it does not claim native Windows verification.

The user's failed directory was not accessed remotely or removed. CI/temp workspaces contain no user records. A GitHub-hosted Windows runner is distinct from the user's physical PC; its exact OS/display differences remain a qualification limit. Local manual review is still required. No newer-schema database may be opened with this schema21 repair. Recover existing inventories with compatible software and checked full backup bundles into a new directory; never overwrite them with this fresh schema. Source/docs/reports are ordinary editable files; local copies are not independent backups. Screenshots contain only fictional empty data. The private transcript stays out of Git and wiki.

[Setup](../README.en.md) · [Recovery](RECOVERY.en.md) · [Contributing](../CONTRIBUTING.en.md)
