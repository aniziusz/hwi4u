# Geführter Gerätestandort

Document ID: HWI4U-LOCATIONS · Version: 1 · 2026-10-18

FR-025, Quelle 0.14.0/Schema 22, Kandidat zur TEST-Prüfung. Produktion gesondert freigeben. Implementiert ist Guided form; Zeichnungsimport, automatische Grundrisswahl, X/Y-Kalibrierung und grafische Marker bleiben eine spätere Stufe. DXF erfordert eine Beispieldatei mit bestätigter Einheit/Ursprung; keine CAD-Unterstützung behauptet.

1. Gerät auswählen, unter dem zusätzlichen Standorttext **Standort geführt eingeben…** öffnen.
2. Standort angegeben, Unbekannt oder Nicht zutreffend / tragbar wählen. Tragbarkeit wird nicht vom Gerätetyp abgeleitet.
3. Vorhandenen Ort wiederverwenden oder optional Gebäude/Standort, Geschoss/Etage und Raum eingeben. Neuer Standort leert Dialogfelder. Wiederverwendung kopiert Adresse/Gebäude/Geschoss/Raum und leert Position, Höhe und Hinweise, damit keine alte Position versehentlich einem anderen Raum zugewiesen wird.
4. Gerätespezifische Position/Wand, optionale Höhe in Metern und Höhenbezug eingeben. `1,8` und `1.8` zulässig; 0 bis 10000 m. Mit Höhe Fertigfußboden, Gelände oder anderer Bezug mit Beschreibung in Hinweisen wählen. Ohne Höhe kein Bezug. Jedes Textfeld erlaubt eine Unicode-Zeile mit höchstens 200 Zeichen.
5. **Adresse und weitere Hinweise (optional)** aufklappen: Land, Postleitzahl, Ort/Stadt, Straße, Hausnummer, Platzierungshinweise. Keine Ebene ist Pflicht; eine Regalbeschreibung allein genügt. Zusammengesetzte Vorschau prüfen.
6. **Standort übernehmen** prüft und übergibt ungespeicherte Werte ins Geräteformular. **Gerät speichern** schreibt alle Änderungen atomar nach geprüfter Sicherung. Abbrechen im Dialog erhält frühere Werte; Abbrechen im Geräteformular verwendet den normalen Ungespeichert-Dialog. Öffnen/Abbrechen legt keine Orte an.

Änderungen eines Geräts benennen keinen gemeinsamen Ort um und bewegen keine anderen Geräte. Orte sind unveränderliche Momentaufnahmen; exakt gleiche kanonische Feldwerte werden wiederverwendet. Andere Werte erzeugen erst beim Gerätespeichern einen neuen Ort. Unbenutzte Orte bleiben; globale Umbenennung/Löschung nicht enthalten. Freie Geschossnamen erzwingen kein Nummernsystem. Vorschläge folgen der Dialogsprache, gespeicherte Werte bleiben wörtlich. Nutzerangaben sind keine unabhängig verifizierten Messungen.

Migration 022 erhält `devices.location` ohne Zerlegung. Als **Standorttext / zusätzliche Beschreibung** separat editierbar, weiterhin höchstens 200 Zeichen; normale Leerzeichenprüfung beim Gerätespeichern gilt. Neuer strukturierter Status zunächst Unbekannt, auch bei vorhandenem Alttext. Keine stille gegenseitige Ersetzung. Suche umfasst beides. JSON-/SQL-/CSV-Export enthält `location_places`, `device_locations`, `device_location_history`; externe Exportprofile bleiben geplant. Historie enthält vorherige/neue strukturierte Werte, UTC-Zeit, Quelle `user_entry`, Prüfstatus `user_reported`. Bleibt bei Gerätelöschung erhalten; Löschsicherung/-historie enthält Platzierung. Stabile Geräte-IDs und andere Daten bleiben erhalten.

Repository-Arbeitsbereich: `python manage.py publish --workspace /absoluter/privater/arbeitsbereich`, dann `python manage.py test --workspace /absoluter/privater/arbeitsbereich`. TEST mit Update anwenden aktualisieren oder geschlossen normal starten. Verwalteter Updater migriert 21→22 nach geprüfter Vollsicherung unter Schreibreservierung; belegte Schreiber verschieben, Fehler rollen zurück. Kein erzwungenes Schließen und kein manuelles Live-SQL. Neue Datenbank nicht mit altem Client öffnen. Produktion bis zur exakten Kandidatenfreigabe unverändert lassen; keine TEST-Datensätze kopieren. [Wiederherstellung](RECOVERY.de.md): kein Schema-Downgrade; frühere Vollsicherung in neuem Ordner mit passender früherer Version wiederherstellen, neuere Dateien zur Prüfung erhalten.

Prüfung: `QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests`. Zieltests: Höhenvalidierung, Wiederverwendung/Isolation, veraltetes Speichern, Sicherungsfehler, ungespeichert/Abbrechen/Sprache, Suche, 21→22-Datenerhalt, unveränderliche Historie und Vollwiederherstellung. Offscreen-Qt ist Linux-Prüfung, kein Windows-/Mobilnachweis oder Produktionsdeployment. Quellen und private Daten unabhängig sichern; gleiche Festplatte genügt nicht.

[Anleitung](../GUIDE.de.md) · [English](LOCATIONS.en.md) · [Magyar](LOCATIONS.hu.md)
