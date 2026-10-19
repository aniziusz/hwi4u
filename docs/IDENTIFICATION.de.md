# Hardware-Identifikationsfelder

Document ID: HWI4U-IDENTIFICATION · Version: 1 · 2026-10-19

HWI4U 0.17.0 / Schema 24 — FR-036. Hersteller, Modell und Seriennummer sind optionale Unicode-Textfelder. In dieser Reihenfolge direkt über Standorttext im Schnelleditor. Im großen Editor dieselben Felder vor Standort in **Hardware und Standort**, mit entsprechendem Baumeintrag. Vorhandenes Speichern/Verwerfen, Sprachwechsel und Konfliktschutz gelten.

Unbekannt leer lassen, als NULL gespeichert. Maximal 200 druckbare einzeilige Zeichen pro Feld. Äußere Leerzeichen entfernt, Groß-/Kleinschreibung, führende Nullen und innere Leerzeichen erhalten. Seriennummer ist Text: `0007aB` bleibt exakt. Keine globale Eindeutigkeit: Hersteller können Nummern wiederverwenden oder Nummer unbekannt. Hersteller/Marke und Modellname/-code getrennt von beschreibendem Gerätenamen und primärem Typ. Nutzerangaben, nicht automatisch verifiziert.

Gerätesuche umfasst alle drei auch bei ausgeblendeten Spalten. Spalten… zeigt sie; Kopffilter filtern. Hersteller/Modell zusätzlich gruppierbar. Bestehende Spaltenreihenfolge, Breiten, Gruppen und Filter bei Einstellungsupgrade erhalten; neue Spalten hinten ausgeblendet. JSON-/SQL-Export und Sicherung/Wiederherstellung erhalten Texte. Keine Änderung an UUID/Kurz-ID/Rollen/Klassifikation/Standort.

Migration 024 ergänzt nullable Spalten, leitet nichts aus Namen/Rechnungen/Referenzen ab. Bestehende Geräte bleiben leer. Managed TEST-Update/normaler TEST-Start sichert vollständig vor 23→24; Zeilen/IDs bleiben. Nicht hinter laufendem Client migrieren, veröffentlichte Migration ändern, gefüllte DB ersetzen oder alten Client auf 24 richten. Produktion bleibt bis expliziter Abnahme fest. Rollback: geprüfte vorherige Vollsicherung in neues Verzeichnis, kompatible alte Version gemäß Wiederherstellung. Lokale Kopie ist keine unabhängige Sicherung.

Fiktive Tests: alte Zeilen/IDs/NULL, exakte Seriennummer, Leer-/Längen-/Steuerzeichenprüfung, Sicherungsfehler/Konflikte, Feldreihenfolge beider Editoren, Sprachen/Suche, bestehende Ansichten. Native Probe prüft führende Null nach Vollwiederherstellung. Gesamttests/Plattformbelege im Review; Nutzerabnahme getrennt. Beispiele füllen keine echten Gerätefelder.

[Anleitung](../GUIDE.de.md) · [Liste/Arbeitsbereich](WORKSPACE.de.md) · [Wiederherstellung](RECOVERY.de.md)
