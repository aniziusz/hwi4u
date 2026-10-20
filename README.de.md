# HWI4U

Document ID: HWI4U-README · Version: 4 · 2026-10-20

[Windows initialization repair · 0.13.1 / schema 21](docs/WINDOWS-FIX.de.md)

## Dokumentation und Featureverwaltung

[Wiki](https://github.com/aniziusz/hwi4u/wiki/Home-de) · [Feature requests](https://github.com/aniziusz/hwi4u/wiki/Feature-requests-de) · [Projects table/board](https://github.com/users/aniziusz/projects/1) · [Offline tracking guide](docs/TRACKING.de.md)

Wiki und öffentliche Featureverwaltung. Wiki beschreibt den Quellstand 0.18.0; dieser Branch kann älteren Anwendungscode enthalten. Verlinkte Quellrevision verwenden; Dokumentation aktualisiert keinen Code.

**Hardware inventory database client** — lokale Python/Qt-Anwendung mit SQLite und EN/DE/HU-Oberfläche. Quellversion **0.13.1**, Schema **21**. Nutzung ohne Cloudkonto.

Geräte, Unicode-Namen, generierte UUID/Kurzkennungen, Daten/Kauf/Standort, Gruppen/Typen, Lebenszyklus/Zustand, OS/Firmware, Schnittstellen/MAC/IP, Verbindungen und Quellen erfassen. Fotos/PDFs separate verwaltete Dateien. Angaben werden nicht automatisch erkannt/geprüft; Unbekanntes bleibt unbekannt.

Repository enthält Code, Schema, Migrationen, fiktive Testdaten und öffentliche Anleitung, keine befüllte Inventardatenbank, Anhänge, persönliche Projekthistorie oder Geheimnisse. Leere Datenbank aus schema.sql erzeugen; private Daten außerhalb des Quellordners. Befüllte Datenbank ist kein Git-Fork.

Linux benötigt Qt-Systembibliotheken der Distribution. Ubuntu-CI installiert libegl1, libopengl0 und libxkbcommon0 vor Tests; keine pip-Pakete. Andere Distributionen bieten entsprechende Pakete.

## Linux-Schnellstart

Geprüfte Referenz: Python 3.14.7, SQLite 3.53.4, PySide6/Qt 6.11.2, Git 2.55.0. Andere Versionen/Plattformen nicht qualifiziert. Vorläufige Windows-Dateien belegen keine Unterstützung; Android/iOS nicht implementiert.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py init
python manage.py run
```

Virtuelle Umgebung isoliert Abhängigkeiten. init erzeugt leere Produktion und unabhängige TEST-Kopie im Datenordner (Linux: `$XDG_DATA_HOME/hwi4u`, sonst `~/.local/share/hwi4u`). Isolierte Tests vor erster Freigabe; vorhandene Ordner abgewiesen. Eigener neuer Pfad: `--workspace /absoluter/pfad/ausserhalb/quellen` bei jedem Aufruf. Keine vorhandenen Daten importiert/überschrieben. Fehlgeschlagene Initialisierung erhält Diagnoseordner; nach Prüfung neuen leeren Zielpfad verwenden.

```sh
python manage.py test
python manage.py publish
```

Kandidaten in TEST prüfen, dann bewusst Produktion freigeben. Veröffentlichung kopiert keine Testdatensätze. [Anleitung](GUIDE.de.md), [Mitarbeit](CONTRIBUTING.de.md), [Wiederherstellung](docs/RECOVERY.de.md), [Plan](FEATURES.de.md), [Lizenz](NOTICE.de.md). manage.py ist Repository-Einstieg; .sh/.cmd bleiben für erzeugte Arbeitsbereiche/Kompatibilität.

Markdown/Python/SQL offline mit normalen Werkzeugen lesbar. Abhängigkeitsinstallation/GitHub benötigen Netzwerk. Externe Referenzen nicht archiviert, kein vollständiges Offlinepaket/Binärpaket. Lokale Dateien sind keine unabhängige Sicherung; Quellcode/private Daten separat sichern.

[English](README.en.md) · [Magyar](README.hu.md)
