# Modellvorschläge und Lebenszyklusdaten

Document ID: HWI4U-LIFECYCLE · Version: 1 · 2026-10-19

FR-037/038/039 · Quelle 0.18.0 · Schema 25 · Zuerst TEST. Produktiv erst nach bewusster Abnahme. Modellprofile starten leer; kein privates Inventar, Online-Katalog oder automatisches Scraping enthalten. Migration leitet keine Werte ab und ändert keine IDs/Klassifikationen.

## Sechs getrennte Eigenschaften

**Lebenszyklusdaten** im Schnellformular oder als eigene Kachel öffnen. Unbekannte Eigenschaften stehen als Unbekannt in der Liste. Doppelklick oder Hinzufügen/Bearbeiten. Entfernen bereitet eine Löschung vor; **Gerät speichern** schreibt das Formular, Änderungen abbrechen stellt den gespeicherten Stand wieder her. Die Quellenbibliothek speichert weiterhin sofort, Zuordnungen und Lebenszyklusdaten erst mit dem Gerät. Änderungen/Leeren erzeugen Historien-Snapshots; Export enthält sie, ein eigener Historienbetrachter fehlt.

- Markteinführungsdatum: Hersteller-Marktstart des exakten Modells/Variante, nicht Komponentenstart oder bloße Ankündigung.
- Ende Firmware-Sicherheitsupdates: Anbieter, Produkt und Firmwareversion/Supportzweig, etwa BIOS/UEFI oder SSD-Firmware.
- Ende OS-Sicherheitsupdates: Anbieter, installiertes OS/Distribution und Version/Supportzweig; Basis-OS ersetzt nicht die Distributionsrichtlinie.
- Ende Hardware-Service: konkrete Reparatur-/Austausch-/Ersatzteil-/Servicezusage und Region.
- Produktionsende: Herstellung des Modells endet; weder Verkaufs- noch Supportende.
- Garantieablauf: individuelles Gerät/Kauf/Vertrag, kein gemeinsamer Modelltermin.

Mehrere Beobachtungen je Eigenschaft erlauben mehrere Softwareeinträge und Widersprüche. Anbieter/Produkt, gegebenenfalls Version, Variante/Region/Umfang, Quellen, tatsächliches Beobachtungs-/Abrufdatum, Prüfstatus und Hinweise erfassen. Unbekannt bleibt leer statt heute; das Standarddatum des Editors wird erst bei ausdrücklicher Übernahme gespeichert. Marktstart/Produktion benötigen Hersteller und exaktes Modell als Anbieter/Produkt, Software benötigt Anbieter/Produkt/Version, Hardware-Service/Garantie einen klaren Umfang. Keine pauschalen Laufzeiten ableiten. Bei gemeinsamem OS-/Firmwareimage dieselben Belege verwenden, keine künstlichen Fristen erfinden.

Exakter Tag mit Kalender, Monat (`2025-06`), Quartal (`2025-Q2`), Jahr (`2025`) sind möglich. Passende Präzision wählen; keinen Tag erfinden. Geprüfte Beobachtungen benötigen ein Beobachtungsdatum und geprüfte datierte Quellen. Quellenprüfung bestätigt nicht automatisch die Gültigkeit für das eigene Gerät. Ungeprüfte Angaben dürfen ohne Quelle mit Warnung gespeichert werden. Websites benötigen Netzwerk; für Offline-Nachweise Text erhalten oder PDF importieren. Keine Zusage, alle externen Quellen seien lokal gespeichert.

## Kaufdatumsprüfung

Frühester Kauf: **Marktstart minus ein Kalenderjahr**, einschließlich Grenze; 29. Februar wird auf 28. Februar des vorherigen Nichtschaltjahrs begrenzt. Marktstart 2025-06-15 erlaubt Kauf ab 2024-06-15. Monat/Quartal/Jahr bilden Intervalle: beide Grenzen ein Kalenderjahr zurück; davor Sperre, im unsicheren Grenzbereich Warnung, ab letzter Grenze bestanden. Für `2014-Q2`: vor 2013-04-01 gesperrt, 2013-04-01 bis 2013-06-29 Warnung, ab 2013-06-30 bestanden. Dies beweist keinen frühen Verkauf.

Sperre nur bei geprüfter passender Marktstart-Evidenz. Unterschiedliche Intervalle, ungeprüfte/fehlende Angaben oder Anbieter-/Produktabweichung von Gerätehersteller/-modell warnen. Nur Marktstart bestimmt diese Regel; Käufe nach Produktions-/Supportende bleiben möglich. Keine automatische Datumskorrektur. Alte Konflikte bleiben bei unabhängigen Bearbeitungen editierbar; neue/geänderte Kaufdaten, Lebenszyklusdaten oder Hersteller/Modell müssen die Regel erfüllen. Warnungen prüfen. Exakter Abgleich ignoriert Großschreibung und normalisiert Unicode/Leerzeichen; keine geratenen Aliase oder Regionen.

## Wiederverwendbare Modellprofile

1. Hersteller/Modell eingeben, Typ/Gruppe, Rollen und Lebenszyklusdaten anhand Belegen prüfen; Gerätequellen auswählen.
2. **Modellvorschläge… → Aktuelle Werte als Modellprofil speichern…**; Variante/Region/Hardwarerevision und Nachweise/Gültigkeit beschreiben. Bibliothek speichert sofort mit vollständiger Sicherung, unabhängig vom Abbrechen des Geräteformulars. Ausgewählte Variante kann nach Bestätigung als unveränderliche Revision gespeichert werden. Alte Profile/Quellen und vorhandene Geräte bleiben erhalten.
3. Bei exaktem Hersteller-/Modelltreffer Variante auswählen, Gruppe/Typ/Rollen/Daten/Quellen-IDs/Hinweise prüfen, Prüfbestätigung ankreuzen und übernehmen. Keine automatische Variantenauswahl.
4. Übernahme ändert nur das Formular: ersetzt Typ/Gruppe, Rollen und Nicht-Garantie-Lebenszyklusdaten, behält Gerätegarantie, ergänzt Quellenzuordnung. Prüfen und Gerät speichern oder abbrechen. Veraltete Revision/falsches Modell wird abgelehnt. Beworbene Fähigkeiten beweisen keine Nutzung; Rollen nur als geprüfte Vorschläge speichern.

Kein unscharfer Abgleich, automatische Aliaswahl, Onlinesuche, Hintergrundsync oder rückwirkende Geräteänderung. Manuelle Klassifikation/Softwarekonfiguration bleiben. Revisionen ändern keine bereits kopierten Termine. Seriennummern, individuelle Garantie und installierte Softwareeinstellungen werden nicht geteilt. Bei unklarer Gültigkeit abbrechen und klären. Ein primärer Typ, mehrere Rollen.

## Aktualisierung und Wiederherstellung

Verwaltetes TEST-Update oder normaler TEST-Start: geprüftes unveränderliches Paket und vollständige Sicherung vor transaktionaler Migration 24→25; ältere Schemata folgen der Kette. Programmierung braucht kein Schließen laufender gepinnter Clients; Sperren verschieben Migration sicher. Keine laufende Datenbank ersetzen oder hinter altem Client migrieren. Neue Tabellen: device_lifecycle, device_lifecycle_history, model_profiles. JSON/SQL und vollständige Pakete erhalten Daten/Profile/Quellen/Historie und verwaltete Dateien. Alte Sicherung in neues Verzeichnis mit passender älterer Software zurückspielen; ältere Software niemals auf Schema 25 richten. [Wiederherstellung](RECOVERY.de.md). Lokale Kopien sind keine unabhängige Sicherung; Dokumentation/Daten unabhängig sichern.

Automatische Tests nutzen fiktive Daten: Tages-/Intervall-/Schaltjahrgrenzen, unbekannte/widersprüchliche/falsche Modelle, Software-/Umfangsmetadaten, geprüfte Quellen, Konflikte, Sicherungsfehler, Profilrevisionen/Varianten, Übernahme/Abbrechen, Garantieerhalt, Migration 24, Löschhistorie und Export/Wiederherstellung. Plattformtests und Benutzerabnahme separat; Quellverfügbarkeit qualifiziert keine physische Plattform. [Anleitung](../GUIDE.de.md).
