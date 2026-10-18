# CLI

Document ID: HWI4U-CLI · Version: 1 · 2026-10-18

CLI-példa eldobható adatbázison, nem élő leltáron. Régi sémához megfelelő rögzített kód. --help a tény/alkatrészműveleteket is mutatja. JSON/SQL hordozható, adatbázismásolat melléklet nélkül.

```sh
python inventory.py --help
python inventory.py --db /absolute/new/demo.sqlite3 init
python inventory.py --db /absolute/new/demo.sqlite3 add-device --name example-device --source "FICTIONAL DEMONSTRATION"
python inventory.py --db /absolute/new/demo.sqlite3 list
python inventory.py --db /absolute/new/demo.sqlite3 check
python inventory.py --db /absolute/new/demo.sqlite3 export --directory /absolute/new/export-directory
python inventory.py --db /absolute/new/demo.sqlite3 backup-bundle --output /absolute/new/full-backup.zip
```

[README](../README.hu.md)
