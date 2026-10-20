# Reparatur der Windows-Initialisierung

Document ID: HWI4U-WINDOWS-FIX · Version: 1 · 2026-10-20

Gezielte Reparatur **0.13.1 / Schema21**, basierend auf main 30befe1. Sie übernimmt keine späteren 0.21.0-TEST-Funktionen und aktualisiert kein neueres Inventar. Main enthielt 0.13.0, obwohl das Wiki neuere Entwicklungszweige beschreibt. Bis Prüfung/Merge fix/windows-init verwenden; ein main-ZIP enthält vorher keine Korrektur. Keine Migration oder Schemaeinschränkung geändert. UUIDs, Nachweise und TEST/Produktiv-Trennung bleiben.

## Diagnose und Änderungen

Benutzerprotokoll: Windows, Python3.14.8, PySide6/shiboken6 6.11.2,121 Tests, ein Fehlschlag/fünf Fehler. Privates Protokoll wird nicht veröffentlicht. Codeprüfung bestätigt: (1) SQLite-Transaktionskontext schließt die Verbindung nicht; Tests kombinieren jetzt ausdrückliches Schließen mit dem bisherigen Commit/Rollback-Kontext vor Temp-Verzeichnisbereinigung. (2) Verbindungsaufbau konnte bei gesperrtem Schemalesen vor Eintritt in closing fehlschlagen; inventory.connect schließt bei jedem Aufbaufehler. (3) Testdaten speicherten Windows-Trennzeichen im verwalteten relativen Pfad; jetzt as_posix wie bei echten Importen, unveränderte CHECK-Regeln. (4) Qt-Bildleser hielten Original/Kopie während Fehlerbereinigung offen; ausdrückliche QFile/finally-Bereiche schließen in PhotoStore und SourceStore. (5) Namenstest schätzte300ms für200ms Qt-Verzögerung. Jetzt wartet QSignalSpy ereignisgesteuert auf das tatsächliche Timeout, mit Fehlerfrist; Duplikat-Assertion und echte Validierung bleiben. Kein Test/Assertion deaktiviert, SQL-Regeln nicht gelockert.

FOREIGN KEY bei fehlendem Gerät bleibt der erwartete Fehler. Bereinigung darf ihn nicht durch WinError32 ersetzen. Neue Tests halten den Fehler-Traceback noch fest, während Dateien sofort gelöscht/geschlossene Verbindungen geprüft werden. Auch die About-Abfrage schließt bei Lesefehlern.

## Schriften und Warnungen

QFontDatabase Cannot find font directory betrifft im Protokoll das Offscreen-Testplugin und beweist keinen Fehler nativer Windows-Darstellung. Kind-Testprozesse verwenden vorhandenes WINDIR/Fonts, sofern vorhanden und QT_QPA_FONTDIR nicht ausdrücklich gesetzt. Keine Schriften kopiert, heruntergeladen oder verteilt; normale Oberfläche behält natives Windows-Qt. Fehlende Ordner bleiben sichtbare Warnung, keine Unterdrückung. Eigene Schriftkonfiguration bleibt erhalten. Offscreen-Hinweise zu propagateSizeHints/raise/Tastaturzugriff werden als Plugin-Grenzen aufgezeichnet, nicht als Datenbankfehler. ResourceWarnings zu ungeschlossenen Datenbanken sind Fehler: Diagnoseablauf zeichnet sie auf und scheitert, falls nach aufgeschobener Qt-Löschung/Garbage Collection welche verbleiben. Warnungen werden nicht versteckt, Assertions nicht geschwächt.

## Neue isolierte Windows-Einrichtung

Voraussetzungen: Windowsx64, Python3.14.8 über py -3.14, nicht anderes globales python (Protokoll zeigte auch3.15.0), Internet für Quellcode/Abhängigkeiten, vorhandene Windows-Schriften für Offscreen. Virtuelle Umgebung isoliert Abhängigkeiten. Init prüft die vollständige Suite vor Auswahl eines leeren Arbeitsbereichs und verweigert bestehende Ordner. C:/INSTALL/hwi4u-main und LOCALAPPDATA/HWI4U-Test zur Diagnose unverändert lassen. Init dort nicht wiederholen und Ordner nicht nur zur Fehlerumgehung löschen. Keine persönlichen Inventardaten werden importiert.

```powershell
# Download the fix into a NEW source folder; keep the failed installation.
$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$zip = Join-Path $env:TEMP "hwi4u-windows-fix-$stamp.zip"
$destination = "C:\INSTALL\HWI4U-Windows-Fix-$stamp"
if (Test-Path $destination) { throw 'Choose a new source destination.' }
Invoke-WebRequest 'https://github.com/aniziusz/hwi4u/archive/refs/heads/fix/windows-init.zip' -OutFile $zip
Expand-Archive -LiteralPath $zip -DestinationPath $destination
$source = (Get-ChildItem -LiteralPath $destination -Directory | Select-Object -First 1).FullName
Set-Location $source
py -3.14 -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
.\.venv\Scripts\python.exe -c "import sys, PySide6, shiboken6; print(sys.version); print(PySide6.__version__, shiboken6.__version__)"
$workspace = Join-Path $env:LOCALAPPDATA "HWI4U-Windows-Fixed-$stamp"
if (Test-Path $workspace) { throw 'Choose a new workspace.' }
.\.venv\Scripts\python.exe manage.py init --workspace $workspace
if ($LASTEXITCODE -ne 0) { throw 'Initialization failed; retain this folder and inspect the error.' }
.\.venv\Scripts\python.exe manage.py test --workspace $workspace
```

Exakter geprüfter Commit/CI-Lauf stehen im Reparatur-PR/Projektprotokoll. Branch-Download kann sich ändern; Commit-ZIP im PR ist ein fester Stand. Python/PySide6 vor Init prüfen. Keine PowerShell-Aktivierung nötig: ausdrücklicher .venv/Scripts/python.exe-Pfad vermeidet Ausführungsrichtlinienänderung und falschen globalen Interpreter. Später gespeicherte Pfade verwenden, nicht jedes Mal einen neuen Arbeitsbereich erzeugen:

```powershell
Set-Location 'C:\INSTALL\<neuer Quellordner>'
.\.venv\Scripts\python.exe manage.py test --workspace '<gespeicherter Arbeitsbereich>'
```

## Prüfung wiederholen und Wiederherstellung

```powershell
.\.venv\Scripts\python.exe tools/windows_regressions.py --phase targeted --output dist/checks
.\.venv\Scripts\python.exe tools/windows_regressions.py --phase full --output dist/checks
.\.venv\Scripts\python.exe tools/windows_startup_smoke.py --output dist/startup
```

Erster Befehl führt alle sechs gemeldeten Tests plus fünf neue Lebensdauer-/Schriftprüfungen aus. Vollsuite enthält126 Tests, alle121 ursprünglichen erhalten. Berichte enthalten tatsächliches Python/Qt, Fehler/Fehlschläge/übersprungene Tests, ResourceWarnings/Qt-Meldungen. CI führt dies in dieser Reihenfolge auf Windows2025x64 und Ubuntu24.04 mit Python3.14.8/Qt6.11.2 aus. Workflow allein ist kein Erfolgsnachweis; wirkliche Ergebnisse stehen im PR. Lokaler Linux-Lauf nutzt separat Python3.14.7. Startprüfung erstellt weiteren fiktiven Arbeitsbereich über manage.py init samt voller Prüfschranke. Windows startet tatsächlich manage.py test/verwalteten Supervisor, prüft sichtbares natives TEST-Fenster nur dieses Prozessbaums und passendes Startprotokoll, erstellt Bild, schließt regulär per WM_CLOSE und prüft Exit0. Bei Fehlern wird nur dieser Test-Prozessbaum bereinigt. Linux verwendet initialisierten TEST-Datensatz/Offscreen-Formular, keine behauptete native Windows-Prüfung.

Fehlgeschlagener Benutzerordner wurde nicht ferngeöffnet oder entfernt. CI-/Temp-Ordner enthalten keine Benutzerdaten. GitHub-Windows-Rechner ist nicht der physische Benutzer-PC; genaue Betriebssystem-/Anzeigeunterschiede bleiben Prüfgrenzen. Lokale manuelle Prüfung bleibt nötig. Neuere Datenbankschemata nie mit diesem Schema21-Fix öffnen. Bestehende Inventare mit kompatibler Software/geprüftem Vollbundle in neues Verzeichnis wiederherstellen; nie mit leerem Schema überschreiben. Quellen/Anleitungen/Berichte sind normale bearbeitbare Dateien; lokale Kopien keine unabhängigen Backups. Bilder enthalten nur fiktive leere Daten. Privates Protokoll bleibt außerhalb von Git/Wiki.

[Setup](../README.de.md) · [Recovery](RECOVERY.de.md) · [Contributing](../CONTRIBUTING.de.md)
