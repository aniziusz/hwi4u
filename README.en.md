# HWI4U

Document ID: HWI4U-README · Version: 8 · 2026-10-19

[FR-037/038/039 · 0.18.0 TEST · Lifecycle / Lebenszyklus / Életciklus](docs/LIFECYCLE.en.md)

[FR-036 · Manufacturer / Model / Serial number · 0.18.0 TEST](docs/IDENTIFICATION.en.md)

**Hardware inventory database client** — a local Python/Qt application using SQLite, with English, German and Hungarian UI. Source release **0.18.0**, database schema **24**. No cloud account is required to use the application.

Record devices, Unicode names, generated UUIDs and short labels, dates, purchase details, physical location, device groups/types, lifecycle/condition, operating system/firmware, interfaces, MAC/IP identities, connection records and sourced evidence. Photos/PDFs remain separate managed files. Evidence is user-provided; the program does not discover hardware or automatically verify claims. Unknown values remain unknown.

This repository contains code, schema, migrations, fictional test fixtures and public documentation. It contains no populated inventory, attached assets, personal project history or credentials. An empty database is generated from `schema.sql`; each user keeps their own data outside this source folder. A populated database is not a Git fork.

Linux needs the Qt system libraries supplied by your distribution. The Ubuntu CI runner installs libegl1, libopengl0 and libxkbcommon0 before tests; these are system libraries, not pip packages. Other Linux distributions provide equivalent packages.

## Quick start on Linux

Reference tested environment: Python 3.14.7, SQLite 3.53.4, PySide6/Qt 6.11.2. Git 2.55.0 was used for source checks. Windows x64 and Apple Silicon macOS installation and validation are described in the desktop guide. CI evidence is distinct from end-user platform acceptance. Android/iOS clients are not implemented.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py init
python manage.py run
```

The virtual environment isolates Python dependencies. `init` creates an empty production inventory and an independent TEST copy in the platform data directory (Linux: `$XDG_DATA_HOME/hwi4u`, or `~/.local/share/hwi4u`). It runs isolated tests before preparing the first release and refuses existing directories. To choose a new location, add `--workspace /absolute/path/outside/source` to every command. No existing database is imported or overwritten. Failed initialization retains its folder for diagnosis; choose a new empty target after reviewing the failure.

```sh
python manage.py test
python manage.py publish
```

Use TEST for edits and review a candidate before accepting it for production. Publishing code does not copy test records to production. See [guide](GUIDE.en.md), [contributing](CONTRIBUTING.en.md), [recovery](docs/RECOVERY.en.md), [roadmap](FEATURES.en.md) and [license/dependencies](NOTICE.en.md). `manage.py` is the supported repository entry point; the low-level `.sh/.cmd` launchers are retained for generated workspaces/compatibility.

Source files are editable Markdown/Python/SQL and can be read offline using ordinary tools. Dependency installation and GitHub collaboration require network access. External references are not archived here. Local files are not an independent backup; include source and private workspace in separate backup plans. No complete offline dependency bundle or binary distribution is supplied.

[Deutsch](README.de.md) · [Magyar](README.hu.md)

[FR-025 · 0.18.0 · TEST](docs/LOCATIONS.en.md)

[FR-012 / FR-028 / FR-029 · 0.18.0 · TEST](docs/DESKTOP.en.md)


[FR-030/031/032/033/035 · 0.18.0 · TEST](docs/WORKSPACE.en.md)
