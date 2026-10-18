# CLI

Document ID: HWI4U-CLI · Version: 1 · 2026-10-18

CLI examples use a disposable database, not a live production inventory. For old-schema data use the matching pinned release; do not run new source against an older database. `--help` lists all operations, including sourced facts and dated component installations. JSON/SQL exports are portable data; database-only snapshots do not contain attachments.

```sh
python inventory.py --help
python inventory.py --db /absolute/new/demo.sqlite3 init
python inventory.py --db /absolute/new/demo.sqlite3 add-device --name example-device --source "FICTIONAL DEMONSTRATION"
python inventory.py --db /absolute/new/demo.sqlite3 list
python inventory.py --db /absolute/new/demo.sqlite3 check
python inventory.py --db /absolute/new/demo.sqlite3 export --directory /absolute/new/export-directory
python inventory.py --db /absolute/new/demo.sqlite3 backup-bundle --output /absolute/new/full-backup.zip
```

[README](../README.en.md)
