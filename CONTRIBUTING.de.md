# Mitarbeit

Document ID: HWI4U-CONTRIBUTING · Version: 2 · 2026-10-20

[Windows initialization repair · 0.13.1 / schema 21](docs/WINDOWS-FIX.de.md)

Branch/Code-Fork mit eigenem privatem Arbeitsbereich und fiktiven Wegwerfgeräten, keine gemeinsame beschreibbare Inventardatei. UUIDs bei Migration erhalten. Keine Laufzeitdaten, Anhänge, Rechnungen, geheimen Logs/Kontodaten oder privaten Projektdokumente committen. Ignore ersetzt keine Prüfung von Index/Verlauf.

```sh
git switch -c feature/descriptive-name
QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests
python tools/check_distribution.py
```

Tests nutzen Wegwerfdatenbanken, niemals Nutzerinventar. Linux-Offscreen-CI für Push/Pull Request in `.github/workflows/tests.yml`; Datei beweist keinen erfolgreichen Remote-Lauf. Tatsächlichen Lauf prüfen. Windows/Mobil gesondert testen. Ältere Tests können nicht-fehlschlagende Verbindungs-ResourceWarnings melden; neue Warnungen untersuchen, Fehler nicht verstecken.

Pull Request beschreibt Problem, Verhalten, Prüfung. EN/DE/HU mit gleicher ID/Version/Datum aktualisieren, relative Links, Spezifikation nicht nur im Chat. Keine proprietären Assets nötig.

Datenbankänderung: nächste eindeutige Migrationsnummer, freigegebene Migrationen nicht bearbeiten. Nummern über Branches koordinieren. Frisches Schema, Versions-/Exportprüfung, Fixtures/Tests anpassen. Erhalt alter Daten, ungültige Eingaben, offene Schreiber, Rollback und Vollwiederherstellung auf Kopien prüfen. Keine Datenbank zurücksetzen; unbekannt bedeutet nicht löschen.

```sh
python manage.py publish --workspace /absoluter/privater/arbeitsbereich
python manage.py test --workspace /absoluter/privater/arbeitsbereich
python manage.py promote --workspace /absoluter/privater/arbeitsbereich
```

Publish überträgt Quelle in erzeugten Arbeitsbereich, prüft unveränderlichen TEST-Kandidaten, Produktion bleibt fixiert. Generierte Quellen nicht bearbeiten: Änderungen werden zum Schutz erkannt. TEST samt ungespeicherten Änderungen prüfen. Promote öffnet bewusste Freigabe, kopiert keine Testdaten. Nur frische leere Installation wählt erste geprüfte Version für beide Kanäle; bestehendes Inventar erhält keine automatische Freigabe.

[Setup](README.de.md) · [Wiederherstellung](docs/RECOVERY.de.md)
