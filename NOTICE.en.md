# License, provenance and dependencies

Document ID: HWI4U-NOTICE · Version: 2 · 2026-10-21

[Windows offline EXE installer · 0.21.1 TEST](docs/WINDOWS-INSTALLER.en.md)

Original HWI4U Python/SQL/tools/tests and public documentation are distributed under the MIT license in LICENSE, retaining the contributor copyright notice. The earlier component-specific LICENSE-desktop.txt is retained as a compatible notice explicitly covering original source, schema, migrations, tests and documentation. No inventory data or third-party dependency is relicensed.

Runtime dependency: PySide6/Qt 6.11.2, installed separately via requirements.txt, not bundled in this repository. Qt for Python documents community LGPL/GPL and commercial options: https://doc.qt.io/qtforpython-6/ . Preserve the dependency's own notices/conditions. The Git repository remains source-only. The0.21.1 installer bundles CPython and the unmodified Qt Essentials/shiboken runtime with dependency notices and replaceable shared libraries; see the installer guide for exact source/license links. Python/SQLite/Git retain their own licenses.

The shareable source was selected from application code, generated schema/migrations and fictional tests. No vendor images, PDFs, order receipts, populated databases, private documentation or chat history are distributed. The schema includes generic device-type/protocol lookup names, not owned-device observations. Network examples in tests are fictional; no external integrations are contacted by tests. Maintainers must review future contributions for provenance and permission.

GitHub Actions configuration references official checkout/setup-python actions; those dependencies are not vendored. Sources reviewed 2026-10-18: https://github.com/actions/checkout , https://github.com/actions/setup-python , https://pypi.org/project/PySide6/6.11.2/ . External evidence pages/assets are not saved locally; this notice is not a complete offline third-party license archive. [README](README.en.md)
