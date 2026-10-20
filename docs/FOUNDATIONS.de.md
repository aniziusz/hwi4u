# Zuverlässige Grundlagen — 0.19.0 TEST

Document ID: HWI4U-FOUNDATIONS · Version: 1 · 2026-10-20

FR-043, FR-045 und FR-047. Kandidat; Produktivabnahme separat. Kein Schemawechsel (25), keine TEST-Datenaktualisierung, kein Inventar hochgeladen. Laufende Clients bleiben bis Update/Neustart auf ihrer Version.

## Gerätenachweise

Quelleneingabe und Quellenbereich tragen * und erläutern: Quellentext ODER mindestens eine Gerätequelle wählen. Inline-Hinweis aktualisiert sich. Fehlt beides, verhindert Speichern die Änderung und führt in Schnell-/Vollfenster-Editor zum Nachweis. Nur für OS/Netzwerk/Verbindungen gewählte Quellen genügen nicht. Bestehende Netzwerk-/Verbindungswarnungen und Anforderungen verifizierter Bewertungen bleiben. Kein doppelter Text nötig; Speichern/Verwerfen und Quellenverlauf unverändert.

## Sprachen pflegen

locales/en.json, de.json, hu.json enthalten 725 migrierte Meldungen einschließlich Menüs, Beschriftungen, Hilfe, Tooltips, Auswahl, Dialogen, Validierung und Statusvorlagen. JSON passt zur vorhandenen Live-Übersetzung und benötigt weder zusätzliche Laufzeit noch Compiler; deshalb statt Qt TS/gettext PO gewählt. Keine automatische Übersetzung, kein Hot-Reload oder Übersetzer-GUI.

Englisch: stabile IDs (ui.0001 usw.), unveränderlicher source-Suchalias, bearbeitbarer text und context für Übersetzer. IDs nie umnummerieren/wiederverwenden, source bei Wortlautänderungen erhalten. Übersetzungen: gleiche ID, text und source_sha256 des englischen Anzeigetextes. Geändertes Englisch macht alte Übersetzungen veraltet; Text und Hash nach Prüfung aktualisieren. Fehlende/leere/veraltete oder unpassende Übersetzung fällt auf aktuelles Englisch zurück. Platzhalter müssen genau übereinstimmen; Tastenkürzel (&), Satzzeichen und vorgesehenes Markup erhalten. Markup bleibt Anwendungseigentum, keine Benutzer-HTML. Format 1 unterstützt keine Pluralarrays; bei künftigem Bedarf zuerst eine unterstützte Plural-API entwerfen.

language, name und qt_locale bestimmen neue Sprachmenüeinträge und Kalender-Locale beim nächsten Start. Im Quellordner:

```sh
python tools/catalogues.py
python tools/catalogues.py --new-language fr --name Français --qt-locale fr_FR
```

Der zweite Befehl erstellt ausschließlich eine neue unvollständige fr.json. Leere Texte fallen auf Englisch zurück. Mit en.json Kontext vergleichen, IDs/englische Hashes erhalten. Fehlerhafte Sprachdateien werden ausgeschlossen; Prüfbefehl zeigt Diagnosen. Bei beschädigtem Englisch bleiben wörtliche englische Beschriftungen ohne Kataloghilfe benutzbar: veröffentlichte Datei wiederherstellen und prüfen. Ungültige/fehlende Spracheinstellung fällt auf Englisch zurück. Inventardaten unverändert. Kataloge sind Teil von Quell-ZIP und Release-Hash; Wortlautänderung braucht neues geprüftes Release, keine Änderung unveränderlicher installierter Releases.

Datenbankwerte/Benutzereingaben bleiben Daten. Sprachwechsel schreibt keine Datensätze um. EN/DE/HU-Dokumente separat pflegen; ungespeicherte Eingaben, Datumslocale, Kürzel, Platzhalter und Dialoge prüfen. Kompatibilitäts-Pythonmodule enthalten keinen separat gepflegten Wortlaut.

## Gemessene Validierung und sichere Wiederverwendung

Nach überschaubarer Änderung gezielt prüfen; vor abschließender Regression kompatiblen Kandidaten einfrieren. Privates Nachweisverzeichnis außerhalb öffentlicher Commits wählen:

```sh
python tools/validate.py --evidence /absolute/private/evidence --pattern test_foundations.py
python tools/validate.py --evidence /absolute/private/evidence
python tools/validate.py --evidence /absolute/private/evidence --fresh
```

Gezielte Prüfungen erfassen Dauer/Rückgabecode und gelten nie als Release-Nachweis. Vollprüfung erfasst Testzahl, verstrichene Sekunden, Ausgabehash, Quell-/Test-/Katalog-/Abhängigkeitsmanifeste, Pythonprogramm/-version, tatsächliche Qt-/Moduldateihashes, OS/Architektur, SQLite und Umgebungsdigest. Keine Umgebungswerte speichern. Lokaler Zufallsschlüssel authentifiziert Nachweise per HMAC; Signatur und Ausgabeprotokoll werden geprüft. Andere Quellen/Umgebung/Abhängigkeiten, fehlende/ungültige Signatur, geändertes Protokoll, Fehler oder null Tests verlangen neue Prüfung. Eingaben nach Lauf erneut prüfen; --fresh erzwingt Lauf. Fehler liefert Fehlerstatus.

Veröffentlichung und Übernahme nutzen private .runtime/validation. Nur vollständiger Fingerabdruckgleichstand erlaubt Wiederverwendung, nicht Versionsnummer/Commit allein. Lokales Bestehen ersetzt weder native Plattform-CI, Distributionskontrolle, Migration/Sicherung, Start des TEST-Kandidaten noch ausdrückliche Produktivabnahme. Release vor Produktivauswahl erneut prüfen. Kein automatisches Promoten. Fehlender Schlüssel/Nachweis führt neuem Lauf; beschädigter Schlüssel zu erklärtem Fehler. Lokale Nachweise sind keine unabhängige Sicherung.

HMAC schützt gegen beschädigte/bearbeitete Nachweise, nicht gegen bösartige Prozesse mit gleichen Benutzerrechten und Schlüsselzugriff. Schlüssel/Logs privat halten, .runtime nicht in Git/Artefakte hochladen. Verdächtige Nachweise erhalten, neues leeres privates Verzeichnis wählen, frisch prüfen. Keine Releases/Daten zum Umgehen löschen. Verschiedene Umgebungen teilen kein Vertrauen. CI misst einmal je Kandidat; Plattform-Smoke/Packaging separat.

Originalschätzung und tatsächliche Dauer, Wiederholungen/Fehler, Benutzer-/externe Wartezeit und Wiederverwendung dokumentieren. Aktiver Aufwand unbekannt, wenn nicht separat gemessen. Nur vergleichbare Läufe vergleichen; kein universeller Beschleunigungsfaktor oder Umrechnung von Kontingent in Arbeitszeit. [Beitragsablauf](../CONTRIBUTING.de.md).
