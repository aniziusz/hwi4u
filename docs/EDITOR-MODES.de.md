# Basis/Details und geschützte Bearbeitung — 0.20.0 TEST

Document ID: HWI4U-EDITOR-MODES · Version: 1 · 2026-10-20

FR-050/053/052/044/046. Benutzer wählte Basis/Details und klassische Menüs links. Nur TEST-Kandidat, Produktivabnahme separat. Schema 25 und gespeicherte Datensätze unverändert; keine neue Abhängigkeit, Migration oder TEST-Aktualisierung.

## Basis und Details

Jedes Fenster startet mit Basis: Kurz-ID, Name, Hersteller/Modell, Typ/Gruppe, Standort mit strukturiertem Ortseditor, Lebenszyklusstatus, physischer Zustand und Gerätenachweis. Name/Nachweis behalten Pflichtregeln; anderes darf unbekannt bleiben. Typgruppe folgt gespeichertem Typ. Generierte IDs schreibgeschützt.

Details ergänzt vollständige ID, Seriennummer, Rollen/Modellvorschläge, Kauf/Installation/Entsorgung, Software, Netzwerkidentität, Schnittstellen/Protokolle, Lifecycle/Garantie, Fotos/Referenzen. Details funktioniert auch im Anzeigemodus. Initiale Feldauswahl aus gewählter Vorschau, keine benutzerkonfigurierbaren Prioritäten oder neuer Assistent. Auswahl bleibt innerhalb des Fensters erhalten; neues Fenster/Neustart beginnt Basis. Umschalten speichert/löscht/lädt nichts neu. Große Ansicht behält adaptive Kacheln, Baum und Hervorhebung; versteckte Bereiche belegen kein Rasterfeld. Listenpräferenzen unverändert.

## Anzeigen und Bearbeiten

Gespeicherte Geräte öffnen in beiden Ansichten geschützt. Gerät bearbeiten aktiviert Änderungen. Schreibgeschützter Text bleibt kopierbar; Quellen ansehen, Fotos/Handbücher/Links öffnen bleibt in Details möglich. Quellenansicht kann im Anzeigemodus nichts anlegen/revidieren/zuordnen. Lifecycle-/Ortseditor und Anhangänderungen erfordern Bearbeitung. Das verhindert Versehen, ist keine Authentifizierung, Verschlüsselung oder Datenbank-Zugriffskontrolle. Externe Werkzeuge und ausdrückliche gemeinsame Katalogpflege bleiben getrennte Fähigkeiten.

Neue Geräte sind bearbeitbar. Erfolgreiches Speichern oder Verwerfen führt zur Anzeige. Fehlgeschlagene Speicherung erhält Eingaben und Bearbeitungsmodus; relevante versteckte Details werden sichtbar/fokussiert. Gerätenachweis: Text ODER ausgewählte Gerätequellen. Gemeinsame Validierung, Konfliktprüfung, Sicherungen/UUIDs bleiben; Änderungen anderer Fenster überschreiben keine Entwürfe.

Änderungen speichern/verwerfen erscheinen genau einmal unten rechts außerhalb des Scrollbereichs, nur während Bearbeitung. Gerät bearbeiten steht bei Basis/Details. Menübefehle verwenden dieselben Operationen. Strg+S (macOS Plattformstandard Command) speichert nur im Bearbeitungsmodus. Escape startet Verwerfen; bei Eingaben bleibt Speichern/Verwerfen/Weiter bearbeiten als ausdrückliche Bestätigung. Kein stiller Entwurfsverlust. Schließen/Updates erhalten Schutz. Löschen braucht Bestätigung/geprüfte Sicherung.

Fotos/Handbücher und neue Quellenbibliothekseinträge behalten sofortiges Speichern im jeweiligen Dialog: Geräte-Verwerfen macht bereits gespeicherte Anhänge/Quellen nicht rückgängig. Quellenzuordnungen bleiben bis Geräte-Speichern ausstehend. Bestehende Hinweise erläutern Grenzen. Gemeinsame Typ-/Verbindungskataloge sind ausdrückliche Werkzeuge mit Bestätigung und geräteübergreifenden Auswirkungen; Anzeige ist keine globale Schreibsperre.

## Lifecycle aufklappen

Schnellansicht: Lifecycle-Daten als tastaturbedienbarer Pfeil, zunächst geschlossen wie Netzwerk/Software. In Details öffnen. Ausblenden erhält Daten, Quellen, Warnungen/Entwürfe. Textlicher Prüfhinweis im Header und Basis-/Detailstatus zeigen Warnungen weiter an. Große Ansicht behält Lifecycle-Kachel/Baumeintrag mit demselben Editor wie andere Netzwerk-/Softwarekacheln, keine doppelten Formulare.

## Klassische Menüs

Datei, Bearbeiten, Ansicht, Werkzeuge, Hilfe links; kein Ribbon. Native macOS-About/Quit-Platzierung bleibt.

| Menü | Operationen |
|---|---|
| Datei | Neues Gerät, Speichern, Vollsicherung, Beenden |
| Bearbeiten | Gerät bearbeiten, Verwerfen, Löschen |
| Ansicht | Basis/Details, Suche, Filter, Spalten, Gruppierung, Filter löschen, Aktualisieren |
| Werkzeuge | Typen, Verbindungsauswahl, Netzwerkverbindungen, anderer Client, Sprache |
| Hilfe | Über, Anleitung, lokale Updates |

Standard-Qt-Kürzel für Speichern/Neu/Suchen/Aktualisieren/Hilfe/Beenden; Strg+E für Bearbeiten, Escape für Verwerfen. Große Fenster deaktivieren Listenaktionen, da die Liste im Hauptfenster bleibt. Kein nicht implementierter Excel-/Undo-Befehl. Updatekontrollen und TEST-/Produktivkennzeichnung bleiben. Neue Texte in externen EN/DE/HU-Katalogen (742 Einträge); Sprachwechsel erhält Entwürfe, Modi und Quellen.

## Prüfung und Wiederherstellung

TEST per Apply update oder normalem Neustart laden. Exakten Kandidaten vor Übernahme prüfen: gespeichertes Gerät geschützt, Bearbeiten, Feld ändern, Basis/Details wechseln, Speichern/Verwerfen; Seriennummer/Kaufdaten, Lifecycle und Sprachmenüs prüfen. Referenz ohne Bearbeitung öffnen. Unveränderliches vorheriges TEST 0.19.0 und Produktiv 0.18.0 bleiben vorhanden, Release-Verzeichnisse nicht bearbeiten. [Wiederherstellung](RECOVERY.de.md) · [Grundlagen](FOUNDATIONS.de.md) · [Arbeitsbereich](WORKSPACE.de.md).
