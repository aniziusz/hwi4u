# Windows, Apple Silicon und großes Gerätefenster

Document ID: HWI4U-DESKTOP · Version: 1 · 2026-10-18

Quellkandidat 0.15.0, Schema 22 unverändert. FR-012: Windows 11 x64; FR-029: natives Apple Silicon (M1 und später), macOS ab 14. Intel-Macs, Windows ARM, iOS/Android nicht enthalten. Automatiktests sind keine Nutzerabnahme: CI-Ziele Windows Server 2025 x64, macOS 14 ARM64, Ubuntu 24.04. Ein Runner bestätigt nicht jeden PC/MacBook, Bildschirm oder Systemstand. Aktuelle Nachweise im Pull Request; Erstinstallation/Desktopintegration und Nutzerprüfung am Zielgerät bleiben erforderlich.

## Installation und Start

**Quellclient-Paket**, kein eingebettetes Python-EXE, signierter Installer oder notarisiertes Mac-Programm. Python 3.14 von [python.org](https://www.python.org/downloads/), Internet für die erste Installation der festgelegten FOSS-PySide6-Abhängigkeit und ein beschreibbarer lokaler Installationsordner erforderlich. Die virtuelle Umgebung `.venv` isoliert Python-Abhängigkeiten; Systempakete bleiben. Installationsordner nicht verschieben/löschen. Lokales Dateisystem mit Hardlinks, etwa NTFS/APFS, für derzeitige Sicherungsveröffentlichung; Cloud-/Netz-/FAT-Datenordner nicht qualifiziert. Unabhängige Sicherungen nötig, normale ZIPs nicht verschlüsselt.

**Windows:** `hwi4u-source-client.zip` in dauerhaften Nutzerordner entpacken. `py -3.14 --version` prüfen; gegebenenfalls Python 3.14 mit Launcher installieren. **Install HWI4U.cmd** doppelt anklicken, danach **Start HWI4U.cmd** oder **Start HWI4U TEST.cmd**. UTF-8 und `.venv\Scripts\python.exe`. Daten unter `%LOCALAPPDATA%\HWI4U`, TEST separat. Konsole zeigt Fehler; HWI4U fordert keine Administratorrechte.

**Apple Silicon:** natives ARM64-Python 3.14 und natives Terminal, kein Rosetta/Intel-Interpreter. Dauerhaft entpacken, **Install HWI4U.command** öffnen. Bei verlorener Ausführungsberechtigung im Ordner `chmod +x "Install HWI4U.command"`, danach `./"Install HWI4U.command"`. Erzeugt **HWI4U.app** und **HWI4U TEST.app** daneben; doppelklicken oder ins Dock legen. Lokale Starter mit Verweis auf `.venv`, keine eigenständigen Binärpakete; nur die App verschieben bricht den Verweis. macOS kann ausdrückliche Zustimmung zu Downloads verlangen; Systemsicherheit nicht abschalten. Daten unter `~/Library/Application Support/HWI4U`, TEST separat.

Vorhandene gültige Arbeitsbereiche werden nicht zurückgesetzt: Neuinstallation veröffentlicht nur TEST-Quellstand, Produktion bleibt angeheftet. Unbekannter vorhandener Datenordner stoppt ohne Überschreiben. Ersteinrichtung erzeugt leeres Inventar, lädt keine Datenbank von GitHub. Vorhandenes Inventar nur mit geprüfter **Vollsicherung** samt Anhängen und überprüfter Wiederherstellung in neuem Ordner übertragen, keine offene SQLite-Datei kopieren. [Wiederherstellung](RECOVERY.de.md). `manage.py init` lehnt vorhandene Ordner ab; generierte Dateien nicht zur erzwungenen Übernahme ersetzen. Gemeinsames Bearbeiten/Offline-Abgleich bleibt FR-014.

Technisch: `python3 install_desktop.py` am Mac, `py -3.14 install_desktop.py` unter Windows. `--skip-pip` nur bei exakt bestückter bestehender `.venv`, kein Offline-Paket. Fehlerdiagnosen behalten, keine privaten Daten zum Wiederholen löschen. Ältere Installation/Quelle und geprüfte Vollsicherung bis Abnahme behalten; neue Pakete erhalten eigene Umgebung, venv nicht umbenennen.

## Gerätefenster

Gespeicherte Zeile links doppelklicken: maximiertes Fenster ohne Liste, Schnelleditor bleibt. Erneuter Doppelklick fokussiert dasselbe Fenster anhand voller Geräte-ID. Alle Eigenschaften, Standort, Bilder/Verweise, Prüfung und Sicherung verwenden dasselbe Formular/Store. Neues Gerät und Listenfilter verborgen; Aktualisieren behält Gerät. Speichern aktualisiert saubere Gegenansicht; offene Änderungen bleiben, veraltetes Speichern wird abgewiesen. Abbrechen/Aktualisieren lädt neu. Nach externer Löschung wird sauberes großes Formular deaktiviert statt zum Neugerätformular zu werden. Sofort speichernde Anhänge/Quellen behalten ihre Regeln.

Großes Fenster schließen prüft seine Änderungen. Hauptfenster schließen, **HWI4U beenden** oder **Update anwenden** prüft alle Gerätefenster. Speichern/Verwerfen/Weiterbearbeiten gelten unverändert; Weiterbearbeiten verhindert Schließen/Neustart. Sprachwechsel erhält beide Formulare. Keine zusätzliche Schemamigration; ältere Schemata durchlaufen bestehende Migrationen.

## Prüfung und Paket

`python -m venv .venv`, darin `requirements.txt` installieren. `QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests` (Windows: Variable vorher setzen). `python tools/native_smoke.py --output dist/smoke`: Cocoa/Windows-Qt, Linux offscreen; ausschließlich temporäre fiktive Daten. Prüft Arbeitsbereich, große/kleine Ansicht, Sprache, Vollwiederherstellung und Unicode-Export; protokolliert Architektur/Backend und synthetische Bilder. `python tools/package_source.py --output dist/hwi4u-source-client.zip`: Ziel darf nicht existieren; ausschließlich erlaubte Quellen/Dokumente/Tests mit Skriptrechten/Zeilenenden, keine privaten Daten, Pläne, Bilder, venv oder Runtime. GitHub-Artefakte verfallen nach 14 Tagen; Quelle und unabhängige Sicherung lokal erhalten. Signierung/Notarisierung und eigenständiger Binärinstaller bleiben später.

[Anleitung](../GUIDE.de.md) · [Setup](../README.de.md) · [English](DESKTOP.en.md) · [Magyar](DESKTOP.hu.md)
