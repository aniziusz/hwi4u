# Windows, Apple Silicon és nagy eszközszerkesztő

Document ID: HWI4U-DESKTOP · Version: 1 · 2026-10-18

0.15.0 forrásjelölt, 22-es séma változatlan. FR-012: Windows 11 x64; FR-029: natív Apple Silicon (M1 és későbbi), macOS 14-től. Intel Mac, Windows ARM, iOS/Android nincs a csomagban. Automatikus teszt nem felhasználói átvétel: CI-cél Windows Server 2025 x64, macOS 14 ARM64, Ubuntu 24.04. Egy futtató nem igazol minden PC/MacBook, kijelző vagy rendszerbeállítást. Aktuális bizonyíték a PR-ban; célgépen első telepítés/asztali integráció és felhasználói ellenőrzés még szükséges.

## Telepítés és indítás

**Forráskliens-csomag**, nem beépített Pythont tartalmazó EXE, aláírt telepítő vagy notarizált Mac-alkalmazás. Python 3.14 [python.org](https://www.python.org/downloads/) forrásból, első alkalommal internet a rögzített FOSS PySide6-hoz, írható helyi telepítési mappa szükséges. A `.venv` virtuális környezet elkülöníti Python-függőségeket; rendszertelepítés nem változik. A telepítési mappát ne mozgasd/töröld. Jelenlegi mentéskiadáshoz hardlinket támogató helyi fájlrendszer, például NTFS/APFS kell; felhős/hálózati/FAT-adatmappa nem minősített. Független mentés kell; szokásos ZIP nincs titkosítva.

**Windows:** `hwi4u-source-client.zip` kibontása állandó felhasználói mappába. `py -3.14 --version` ellenőrzése; szükség esetén Python 3.14 indítóval telepítendő. **Install HWI4U.cmd** dupla kattintás, majd **Start HWI4U.cmd** vagy **Start HWI4U TEST.cmd**. UTF-8 és `.venv\Scripts\python.exe`. Adat `%LOCALAPPDATA%\HWI4U` alatt, TEST külön. Konzol megmutatja a hibát; HWI4U nem kér rendszergazdajogot.

**Apple Silicon:** natív ARM64 Python 3.14 és natív Terminal, nem Rosetta/Intel-interpreter. Állandó mappába bontás, **Install HWI4U.command** megnyitása. Elveszett futtatási jog esetén mappában `chmod +x "Install HWI4U.command"`, majd `./"Install HWI4U.command"`. Létrejön **HWI4U.app** és **HWI4U TEST.app**; dupla kattintás vagy Dockba helyezés. Helyi indító a `.venv` környezethez, nem önálló bináris; csak az app mozgatása elrontja a hivatkozást. macOS külön jóváhagyást kérhet letöltött programhoz; rendszervédelmet ne kapcsold ki. Adat `~/Library/Application Support/HWI4U` alatt, TEST külön.

Meglévő érvényes munkaterület nem nullázódik: újratelepítés csak TEST-forrást publikál, éles rögzített marad. Ismeretlen meglévő adatmappa felülírás nélkül megállít. Első telepítés üres leltárt hoz létre, GitHubról nem tölt adatbázist. Meglévő leltár ellenőrzött **Teljes mentéssel**, mellékletekkel, új mappába ellenőrzött visszaállítással vihető át, nem nyitott SQLite-fájl másolásával. [Visszaállítás](RECOVERY.hu.md). `manage.py init` meglévő mappát elutasít; generált fájlokat ne cserélj kényszerített átvételhez. Közös szerkesztés/offline szinkron továbbra is FR-014.

Technikailag: Macen `python3 install_desktop.py`, Windowson `py -3.14 install_desktop.py`. `--skip-pip` csak már pontos függőségekkel rendelkező `.venv` esetén, nem offline csomag. Hibadiagnosztikát tartsd meg, újrapróbáláshoz privát adatot ne törölj. Régi telepítés/forrás és ellenőrzött mentés maradjon elfogadásig; új csomag külön környezet, meglévő venv ne legyen átnevezve.

## Nagy szerkesztő

Bal oldali mentett sor dupla kattintása maximált ablakot nyit lista nélkül; gyorsszerkesztő megmarad. Ismételt dupla kattintás a teljes eszköz-ID alapján meglévő ablakot aktiválja. Minden tulajdonság, hely, kép/hivatkozás, ellenőrzés és mentés azonos űrlapot/store-t használ. Új eszköz/listaszűrő rejtett; Frissítés ugyanazt az eszközt tartja. Mentés frissíti a tiszta másik nézetet; függő adat megmarad, elavult mentés elutasítva. Visszavonás/Frissítés újratölt. Másik nézetből törölt eszköz tiszta nagy űrlapja letiltódik, nem lesz új eszköz. Azonnal mentő melléklet/forrás megőrzi szabályait.

Nagy ablak bezárása saját módosításait ellenőrzi. Főablak bezárása, **Kilépés a HWI4U-ból** vagy **Frissítés alkalmazása** minden eszközablakot ellenőriz. Mentés/Elvetés/Folytatás változatlan; Folytatás megakadályozza bezárást/újraindítást. Nyelvváltás mindkét űrlapot megőrzi. Nincs új sémamigráció; régebbi séma a korábbi kezelten frissül.

## Ellenőrzés és csomag

`python -m venv .venv`, benne `requirements.txt` telepítése. `QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests` (Windows: változó előzetes beállítása). `python tools/native_smoke.py --output dist/smoke`: Cocoa/Windows-Qt, Linuxon offscreen; kizárólag ideiglenes fiktív adat. Munkaterület, nagy/gyors nézet, nyelv, teljes visszaállítás és Unicode-export ellenőrzése; architektúra/backend és fiktív képek rögzítése. `python tools/package_source.py --output dist/hwi4u-source-client.zip`: cél nem létezhet; csak engedélyezett forrás/dokumentum/teszt, futtatási jog/sorvégek megtartva, nincs privát adat, terv, kép, venv vagy runtime. GitHub-artifact 14 nap után lejár; forrás és független mentés helyben megőrzendő. Aláírás/notarizáció és önálló bináris telepítő későbbi feladat.

[Útmutató](../GUIDE.hu.md) · [Telepítés](../README.hu.md) · [English](DESKTOP.en.md) · [Deutsch](DESKTOP.de.md)
