# Namensvorschläge und Tags

Document ID: HWI4U-NAMES-TAGS · Version: 1 · 2026-10-20

FR-042 und FR-051 · 0.21.0 TEST · Schema 26. Regeln vom Benutzer am 2026-10-20 bestätigt. Produktiv bleibt 0.18.0. Der Benutzer hat 0.20.0 TEST akzeptiert; dies übernimmt weder diesen neuen Kandidaten noch TEST-Daten. Ältere Anleitungsteile behalten ihren Versionsbezug; dieses Dokument ist für Namen/Tags aktuell.

## Namensvorschläge

Bei bestehenden Geräten Gerät bearbeiten wählen. In Basis oder Details Hersteller, Modell und/oder Gerätetyp eingeben. Namensvorschlag zeigt **Hersteller Modell — Gerätetyp**, ohne fehlende Teile. Ohne Eingaben gibt es keinen Vorschlag; Hersteller, Modell oder Hardwarefakten werden nicht erfunden. **Vorschlag übernehmen** ersetzt den Namen im ungespeicherten Formular; danach bleibt er frei bearbeitbar. Bestehende/ausgefüllte Namen ändern sich nie automatisch. Vorschauänderungen allein gelten nicht als Geräteänderung. Änderungen speichern übernimmt, Änderungen verwerfen stellt den gespeicherten Namen wieder her. Schnell- und Vollfenster verwenden dieselben Felder.

Vorschläge behalten Groß-/Kleinschreibung und Unicode. Leerzeichen werden vereinheitlicht, nichtdruckbare Steuer-/Zeilenumbruchzeichen aus der Vorschau entfernt; maximal 100 Zeichen. Doppelte Namen erhalten (2), (3) usw.; der Grundtext wird für den Zusatz gekürzt. Vergleich über vorhandene Unicode-NFKC-, Casefold- und Leerzeichennormalisierung; das bearbeitete Gerät ist ausgeschlossen. Beim Übernehmen werden aktuelle gespeicherte Namen erneut geprüft; die abschließende Transaktion verhindert konkurrierende Duplikate. Der Zusatz ist keine reservierte Zählung. Name, UUID, zufällige Kurz-ID, Hostname und Seriennummer bleiben getrennt. IDs/Hostname werden nicht ausgefüllt oder geändert. Lange Vorschläge können gekürzt sein; vor Speichern prüfen.

## Wiederverwendbare Tags

Die optionale Tag-Auswahl ist in Basis und Details, im Vollfenster unter Allgemein. Vorhandene Bezeichnungen wählen oder Tag hinzufügen, mehrere anhaken und Anwenden. Neue Tags/Zuordnungen bleiben bis Änderungen speichern ungespeichert. Abbrechen im Auswahldialog oder Verwerfen im Geräteformular verwirft neue Eingaben. Öffnen allein erzeugt nichts. Tags ersetzen weder Gerätetyp noch Funktionsrollen, Standort, Zustand oder bestätigte Eigenschaften. Keine Vorgaben oder automatischen Zuordnungen.

Bezeichnungen haben 1–50 druckbare Unicode-Zeichen in einer Zeile. Zusätzliche/äußere Leerzeichen werden vereinheitlicht/entfernt. Anzeige verwendet NFC, Eindeutigkeit NFKC, Casefold und vereinheitlichte Leerzeichen. Bei gleichwertigen Tags bleibt die vorhandene Schreibweise. Gleichwertige Mehrfachauswahl wird einmal gespeichert. Stabile Katalog-UUIDs verbinden Geräte/Tags. Abwählen entfernt nur die Zuordnung dieses Geräts; weder Bezeichnung noch andere Geräte ändern sich. Gemeinsames Umbenennen, Zusammenführen und Kataloglöschen sind zurückgestellt. Unbenutzte Tags bleiben verfügbar. Unveränderliche Zuordnungshistorie enthält IDs/Bezeichnungen und user_entry/user_reported; dies bestätigt keine sachliche Eigenschaft. Ansichtsmodus schützt vor Änderungen. Sprachwechsel erhält Bezeichnungen/ungespeicherte Auswahl; gespeicherte Tags werden nicht übersetzt.

Links über Ansicht → Spalten Tags einblenden. Im Spaltenkopffilter reicht **eines der gewählten Tags**; andere Spaltenfilter werden mit **UND** verknüpft. Textsuche berücksichtigt Tags auch bei ausgeblendeter Spalte. Die bestehende Auswahl Unbekannt steht hier für keine Tag-Zuordnung, nicht für das Fehlen einer sachlichen Eigenschaft. Tag-Gruppierung ist in dieser Version nicht enthalten. Spaltenreihenfolge, Breiten und Filter bleiben; neue Spalte zunächst ausgeblendet.

## Speicherung, Export und sichere Aktualisierung

Schema 26 ergänzt tag_choices, device_tags und unveränderliche device_tag_history. Migration 026 weist bestehenden Geräten keine Tags zu und erhält UUIDs, Kurz-IDs, Nachweise und andere Werte. Katalogerstellung, Zuordnung und Geräteänderungen teilen sich eine Schreibtransaktion samt geprüftem Vorab-Backup. Veraltete Zuordnungen verhindern das Speichern, Formular bleibt erhalten. CLI-/Geräteänderungen ohne tags erhalten Zuordnungen. Gerätelöschung behält Katalog/Tag-Historie und nimmt Tag-IDs/Historie in den Lösch-Snapshot auf; vorher geprüftes Vollbackup.

Vollbackup/Wiederherstellung enthält alle Tag-Tabellen. `inventory.py export --directory /neuer/export/ordner` enthält Katalog, Zuordnungen und Historie in JSON/SQL; `inventory.py show --device DEVICE_ID` zeigt Tag-Bezeichnungen. Vor dem Befehl `--db /absolut/privat/hardware.sqlite3` angeben und inventory.py der gewählten kompatiblen unveränderlichen Version verwenden. Kein XLSX-/Zielexport; FR-048/023/027 bleiben getrennt. Neueren Quell-CLI nie mit älterem Produktivschema starten.

TEST regulär starten oder Aktualisierung anwenden wählen. Laufender Altclient bleibt gebunden; Updater migriert 25→26 unter Schreibreservierung nach geprüftem Vollbundle. Sperren verschieben sicher; blockierende Transaktion beenden, erneut versuchen. Codierung/Veröffentlichung migriert keine geöffnete Inventardatei und aktualisiert TEST-Daten nicht aus Produktiv. Produktivübernahme braucht ausdrückliche Abnahme des exakten Kandidaten. Wiederherstellung: Vorab-Vollbundle in neues Verzeichnis mit kompatiblem 0.20.0-/Schema-25-Code zurückspielen; nie ältere Software auf die aktualisierte Datenbank richten. Lokale Snapshots sind keine unabhängigen Backups.

## Prüfung und Voraussetzungen

Vorhandene Namensregeln, Identifikationsfelder, Mehrfach-Spaltenfilter, Ansicht/Bearbeiten und verwaltete Backups/Migrationen sind bestätigte Code-Voraussetzungen. Keine neue Abhängigkeit oder Infrastruktur nötig. Fiktive Tests prüfen fehlende/lange/Unicode-/doppelte Namen, ausdrückliches Übernehmen, Eingaben/Sprachen, Normalisierung/Wiederverwendung, Historie, Konflikte, Backupfehler-Atomarität, Filter/Suche, Lösch-Snapshots, JSON/SQL/Vollwiederherstellung, geordnete Migration, Sperren und Rollback. Aktuelle Ausführungs-/Plattformnachweise stehen im privaten Projektprotokoll und Pull Request; Benutzerabnahme bleibt getrennt. Code, SQL, JSON und Anleitung sind offline lesbar; Abhängigkeiten/verlinkte Webseiten sind kein Offline-Installationspaket.

[Guide](../GUIDE.de.md) · [Editor modes](EDITOR-MODES.de.md) · [Recovery](RECOVERY.de.md)
