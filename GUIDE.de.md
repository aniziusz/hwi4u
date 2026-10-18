# Anleitung

Document ID: HWI4U-GUIDE · Version: 5 · 2026-10-19

Aktuelle 0.16.1-Listensteuerung, Rollen und großes Layout ersetzen ältere Beschreibungen unten. [Aktuelle Anleitung](docs/WORKSPACE.de.md). FR-034 ist Duplikat vorhandener Suche, keine eigene Umsetzung.

README lesen, neuen privaten Arbeitsbereich initialisieren. Produktion: manage.py run, TEST: manage.py test. Daten getrennt, kein automatischer Abgleich. manage.py refresh-test nur bewusst: Bestätigung und ältere Kopien bleiben. Gleichzeitiges Bearbeiten desselben Datensatzes vermeiden; veraltetes Speichern wird abgewiesen.

Neues Gerät: eindeutiger beschreibender Name und Quellnotizen/gewählte Gerätequelle. UUID sowie Kurzkennung aus zwei Buchstaben/fünf Ziffern automatisch. Unicode-Namen max. 100 Zeichen; Groß-/Kleinschreibung/zusätzliche Leerzeichen unterscheiden keine Duplikate. Typ bestimmt Gruppe. Status ist Lebenszyklus, kein Onlinezustand. Unbekannte Daten nicht als Bekannt markieren; bekannte mit Kalender. Standorttext optional einzeilig, max. 200 Unicode-Zeichen. Geführte Eingabe ergänzt wiederverwendbare Orte und gerätespezifische Position; siehe Standortanleitung. Preis/Währung zusammen. Kaufort/Verkäufer getrennt vom Standort; Schreibvorschlag ändert nichts automatisch.

Gerät speichern sichert vorher geprüfte Datenbankkopie und übernimmt Formular. Abbrechen stellt gespeicherten Stand wieder her. Ungespeichert: Speichern, Ungespeichertes verwerfen, Weiterbearbeiten. Verwerfen löscht keine gespeicherten Daten. Löschen nur bestätigt mit Vollsicherung; Kennungen/Historie bleiben reserviert, andere Geräte erhalten. Verknüpfte Ports/Geräte erfordern zuerst ausdrückliches Entfernen der Verbindungen. Baugruppen/Fakten per CLI; kein entsprechender GUI-Editor.

Netzwerkidentität aufklappen: optional Hostname, tatsächliche Schnittstellen/MAC und mehrere IPv4/IPv6. Kein DNS-/DHCP-Schreiben oder Erkennen. Software, Schnittstellen, Protokolle aufklappbar; unterstützt/in Benutzung getrennt. Fähigkeit beweist keine Verbindung. Fehlende ungeprüfte Quellen warnen; geprüfte Angaben benötigen Belege/Datum. Neueste Herstellerfirmware beweist keine Installation. Typ erzeugt keine geprüften Fakten.

Netzwerkverbindung zwischen gespeicherten Ports verschiedener Geräte: Medium, geplant/beobachtet/stillgelegt, Rate optional, Quellen. Sofort gespeichert mit Historie, kein Live-Diagramm. Mehrfachverbindungen/WLAN-Zuordnung dokumentierbar. Quellenbibliothek wiederverwendbar; neue/revidierte Quelle sofort gespeichert, Zuordnung erst mit übergeordnetem Formular. Alte Quellen und Quelltexte erhalten. Öffnen ausdrücklich, kein automatischer Download. PDFs/Bilder außerhalb SQLite.

Suche umfasst Standort/IDs/Software/Netzwerte. Gruppen-/Typfilter: Teilwort tippen, Treffer wählen; Alle setzt zurück. Geschlossene Auswahl-/Datums-/Zahlenfelder ignorieren Mausradänderung und scrollen Formular. Geöffnete Listen/Kalender und Tastatur bleiben. Hoverhilfe/Info zeigen Bedeutung, Pfade, Version. Sprachwechsel erhält offene Werte; Nutzerdaten nicht übersetzen.

Vollsicherung: geprüfte ZIP mit Datenbank und referenzierten Bildern/Handbüchern/Quellen. Automatische Datenbankkopie ohne Dateien. Unabhängig sichern, Wiederherstellung beachten. Update anwenden schützt offene Änderungen und startet getesteten Kandidaten; Abbrechen verschiebt Meldung ohne Datenverlust. Veröffentlichung und Produktionsfreigabe getrennt. KeePass-/OPNsense-/HA-Abgleich nicht implementiert.

[Setup](README.de.md) · [Wiederherstellung](docs/RECOVERY.de.md) · [CLI](docs/CLI.de.md)

[FR-025 · Guided location / Standort / Helyadat](docs/LOCATIONS.de.md)

[FR-028 · FR-012 · FR-029](docs/DESKTOP.de.md)


[FR-030/031/032/033/035 · 0.16.1 · TEST](docs/WORKSPACE.de.md)
