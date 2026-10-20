# Windows-inicializálás javítása

Document ID: HWI4U-WINDOWS-FIX · Version: 1 · 2026-10-20

Célzott **0.13.1 /21-es séma** javítás a main30befe1 alapján. Nem veszi át a későbbi0.21.0 TEST-funkciókat és nem frissít újabb leltárt. Main0.13.0-t tartalmazott, bár a wiki újabb fejlesztési ágakat ír le. Ellenőrzés/összeolvasztásig fix/windows-init ág használandó; előtte a main-ZIP nem tartalmazza. Nincs migráció-/sémakorlát-változás. UUID-k, forrásadatok és TEST/éles elválasztás megmarad.

## Diagnózis és változások

Felhasználói Windows-napló: Python3.14.8, PySide6/shiboken6 6.11.2,121 teszt, egy sikertelen állítás/öt hiba. Privát napló nem kerül publikálásra. Kódvizsgálat: (1) SQLite-tranzakciós környezet nem zárja a kapcsolatot; tesztek most explicit zárást és eredeti commit/rollback környezetet használnak az ideiglenes mappa takarítása előtt. (2) Kapcsolatfelépítés zárolt sémaolvasáskor a closing belépése előtt hibázhatott; inventory.connect minden felépítési hibánál zár. (3) Tesztadat Windows-elválasztót mentett a kezelt relatív útba; most as_posix, a valódi importtal azonos, változatlan CHECK-feltételek mellett. (4) Qt-képolvasók hibatakarításkor nyitva tartották az eredeti/másolt fájlt; QFile/finally környezet explicit zár PhotoStore és SourceStore esetén. (5) Névteszt300ms-t találgatott200ms Qt-késleltetéshez; most QSignalSpy a tényleges timeout jelet és eseményfeldolgozást várja hibahatáridővel. Duplikátumállítás és valódi validálás marad. Nincs letiltott teszt/állítás, lazított SQL-feltétel.

Hiányzó eszköznél FOREIGN KEY a várt hiba; takarítás nem cserélheti WinError32-re. Új tesztek megtartják a hiba visszakövetését, miközben azonnal törölnek fájlt/ellenőrzik a lezárt kapcsolatot. Névjegy lekérdezése olvasási hibánál is zár.

## Betűk és figyelmeztetések

A QFontDatabase Cannot find font directory a naplóban az offscreen tesztpluginhoz tartozik; nem bizonyít natív Windows-megjelenítési hibát. Gyermek tesztfolyamat meglévő WINDIR/Fonts mappát használ, ha van és QT_QPA_FONTDIR nincs kifejezetten megadva. Nem másol, tölt le vagy terjeszt betűfájlt; normál felület natív Windows-Qt marad. Hiányzó mappa figyelmeztetése látható marad; egyéni beállítás megmarad. Offscreen propagateSizeHints/raise/billentyűzet-üzenetek pluginhatárként naplózódnak, nem adatbázishibaként. Lezáratlan adatbázis ResourceWarning hibának számít: diagnosztika rögzíti, és meghiúsul, ha halasztott Qt-törlés/szemétgyűjtés után marad. Nincs figyelmeztetés-elrejtés vagy gyengített állítás.

## Új, elkülönített Windows-telepítés

Előfeltétel: Windowsx64, py -3.14 által választott Python3.14.8, nem más globális python (naplóban3.15.0 is volt), internet forráshoz/függőségekhez, meglévő Windows-betűk offscreen teszthez. Virtuális környezet elkülöníti a függőségeket. Init teljes tesztsorozatot futtat üres munkatér kiválasztása előtt, meglévő mappát elutasít. C:/INSTALL/hwi4u-main és LOCALAPPDATA/HWI4U-Test maradjon változatlan diagnózishoz; ne indítsa újra ott az init-et, ne törölje hibamegkerüléshez. Személyes leltáradatot nem importál.

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

Pontos tesztelt commit/CI-futás a javító PR-ban/projektbejegyzésben. Ágletöltés változhat; PR commit-ZIP rögzített állapot. Python/PySide6 ellenőrzendő init előtt. PowerShell-aktiválás nem kell: explicit .venv/Scripts/python.exe út elkerüli végrehajtási házirend és globális értelmező tévesztését. Később a mentett útvonalakat használja, ne mindig új munkateret hozzon létre:

```powershell
Set-Location 'C:\INSTALL\<uj forrasmappa>'
.\.venv\Scripts\python.exe manage.py test --workspace '<mentett munkater utvonala>'
```

## Ellenőrzés ismétlése és helyreállítás

```powershell
.\.venv\Scripts\python.exe tools/windows_regressions.py --phase targeted --output dist/checks
.\.venv\Scripts\python.exe tools/windows_regressions.py --phase full --output dist/checks
.\.venv\Scripts\python.exe tools/windows_startup_smoke.py --output dist/startup
```

Első parancs mind a hat jelentett tesztet és öt új élettartam-/betűtesztet futtatja. Teljes sor126 tesztet tartalmaz, eredeti121 megmarad. Jelentés: tényleges Python/Qt, hibák/sikertelen/kihagyott tesztek, ResourceWarnings/Qt-üzenetek. CI sorrendben Windows2025x64 és Ubuntu24.04 rendszeren Python3.14.8/Qt6.11.2-vel futtat. Beállított workflow nem sikerbizonyíték; tényleges eredmény PR-ban. Helyi Linux külön Python3.14.7-et használ. Indításpróba új fiktív munkateret készít manage.py init-tel és teljes tesztkapuval. Windowson tényleges manage.py test/kezelt felügyelő indul; csak e folyamatfa látható natív TEST-ablakát és megfelelő indítási nyugtáját ellenőrzi, képet készít, WM_CLOSE-zal rendesen bezár és exit0-t ellenőriz. Hibánál csak e tesztfolyamatfa takarítódik. Linux inicializált TEST-adatokat/offscreen űrlapot használ, nem állít natív Windows-próbát.

Felhasználói sikertelen mappa nem volt távolról megnyitva/törölve. CI/temp mappák nem tartalmaznak felhasználói adatokat. GitHub Windows-gép nem a felhasználó fizikai PC-je; pontos OS-/kijelzőkülönbség ellenőrzési korlát marad. Helyi kézi ellenőrzés szükséges. Újabb sémájú adatbázist ne nyisson e21-es javítással. Meglévő leltár kompatibilis szoftverrel/ellenőrzött teljes csomagból új mappába állítandó vissza; üres séma sosem írja felül. Forrás/útmutató/jelentés hagyományos szerkeszthető fájl; helyi másolat nem független mentés. Képek csak fiktív üres adatot tartalmaznak. Privát napló nem kerül Gitbe/wikibe.

[Setup](../README.hu.md) · [Recovery](RECOVERY.hu.md) · [Contributing](../CONTRIBUTING.hu.md)
