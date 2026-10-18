# Sicherung und Wiederherstellung

Document ID: HWI4U-RECOVERY · Version: 1 · 2026-10-18

Private Daten im Arbeitsbereich außerhalb Git. GitHub sichert Quellen, kein Inventar. Unabhängige Sicherung des gesamten Arbeitsbereichs (Datenbank, photos/manuals/sources, .runtime, Einstellungen, Quellkopie) und Git-Klon/Bundle behalten. Gleicher Datenträger nicht unabhängig. Konsistente Dateisystemsicherung oder Schreiber vor Dateikopie schließen; SQLite nicht unbedacht live kopieren. Zum Programmieren nicht schließen.

GUI-Vollsicherung erzeugt geprüfte ZIP mit Datenbank, referenzierten Dateien und MANIFEST.json; automatische .sqlite3 ohne Dateien. Quellcommit/Release-ID mit Sicherung aufbewahren. Alte Laufzeitversionen erhalten; Migration nicht einfach durch ältere Quelle rückgängig.

```sh
python tools/verify_bundle.py /pfad/sicherung.zip /neues/leeres/wiederherstellungsverzeichnis
python inventory.py --db /neues/leeres/wiederherstellungsverzeichnis/hardware.sqlite3 check
```

Prüfer weist fehlende/zusätzliche/unsichere Elemente und falsche Hashes ab, entpackt nur neues Verzeichnis. Zweiter Aufruf braucht passendes Schema (hier 21); ältere Sicherung zunächst mit passender Quelle/Laufzeit, dann verwaltet auf Kopie migrieren. user_version nicht manipulieren. ZIP ist Daten, kein initialisierter manage.py-Arbeitsbereich.

Normal: konsistente ganze Arbeitsbereichssicherung an NEUEM Pfad samt Markern/Quellen/Laufzeiten wiederherstellen; `python manage.py run --workspace /neuer/wiederhergestellter/arbeitsbereich` verwendet dessen fixierte Produktionsversion. Integrität/Dateihashes prüfen, Original nicht überschreiben. Bei nur Daten-ZIP geprüfte Extraktion/passende Quelle erhalten und explizite Datenübernahme planen; automatische ZIP-Übernahme nicht enthalten.

Fehlende Veröffentlichung lässt Produktionszeiger unverändert. Quelle korrigieren, testen, erneut veröffentlichen. Offene Transaktionen beenden und Migration erneut versuchen, keine fremden Prozesse töten/Prüfungen abschalten. Fehlmigration rollt zurück, Vollvorsicherung bleibt. Vollständigen zusammenpassenden Daten-/Laufzeitstand wiederherstellen statt alten Code auf neues Schema anzuwenden. [Setup](../README.de.md) · [Entwicklung](../CONTRIBUTING.de.md)
