# Contributing

Document ID: HWI4U-CONTRIBUTING · Version: 3 · 2026-10-20

[FR-043/045/047 · 0.19.0 TEST · Foundations / Grundlagen / Alapok](docs/FOUNDATIONS.en.md)

Use a branch or code fork, not a shared writable inventory. Each contributor uses a separate private workspace and disposable fictional devices. Keep the original UUIDs when migrating existing data. Never commit runtime data, photos/manuals, invoices, logs with secrets, real account details, or private project documents. Ignore rules are a convenience, not a substitute for inspecting staged content and history.

```sh
git switch -c feature/descriptive-name
QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests
python tools/check_distribution.py
```

The test suite creates disposable SQLite databases; tests must not open a developer's inventory. Linux offscreen tests are configured for pull requests and pushes in `.github/workflows/tests.yml`; a workflow file is not proof that remote CI passed. Check the actual run. Windows/mobile support needs separate platform tests before claiming support. Some older tests can emit non-failing unclosed-connection ResourceWarnings; report new warnings rather than hiding failures.

Create a pull request describing problem, resulting behavior and validation. Update matching English/German/Hungarian documents (same ID/version/date). Never use a chat as the only specification. Keep document links relative. No generated proprietary assets are required.

Database changes: append one uniquely numbered migration after the highest existing schema version; do not edit released migrations. Coordinate numbering when branches overlap. Update fresh schema, version checks, export version, fixtures as needed and tests. Test old-row preservation, invalid inputs, pending writers, rollback and full-backup restore on copies. Do not reset a user's database or treat unknown values as deletions.

```sh
python manage.py publish --workspace /absolute/private/workspace
python manage.py test --workspace /absolute/private/workspace
python manage.py promote --workspace /absolute/private/workspace
```

Publish stages changed source into the generated workspace, validates an immutable TEST release and keeps production pinned. Do not edit generated workspace source: local modifications are detected to prevent overwriting them. Review TEST including unsaved Save/Discard/Keep editing behavior; promotion opens an explicit acceptance dialog and never copies test records to production. An initial empty installation selects its first validated release for both channels; this is not an update to an existing inventory. Only exact reviewed code is accepted for subsequent production changes.

[Setup](README.en.md) · [Recovery](docs/RECOVERY.en.md)

[Platform checks / Plattformprüfung / Platformteszt](docs/DESKTOP.en.md)
