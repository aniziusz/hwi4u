# CLI

Document ID: HWI4U-CLI · Version: 1 · 2026-10-18

CLI-Beispiele verwenden Wegwerfdatenbank, keine Live-Produktion. Bei altem Schema passende fixierte Quelle verwenden. --help zeigt Fakten-/Komponentenbefehle. JSON/SQL portabel, Datenbanksicherung ohne Anhänge.

```sh
python inventory.py --help
python inventory.py --db /absolute/new/demo.sqlite3 init
python inventory.py --db /absolute/new/demo.sqlite3 add-device --name example-device --source "FICTIONAL DEMONSTRATION"
python inventory.py --db /absolute/new/demo.sqlite3 list
python inventory.py --db /absolute/new/demo.sqlite3 check
python inventory.py --db /absolute/new/demo.sqlite3 export --directory /absolute/new/export-directory
python inventory.py --db /absolute/new/demo.sqlite3 backup-bundle --output /absolute/new/full-backup.zip
```

[README](../README.de.md)
