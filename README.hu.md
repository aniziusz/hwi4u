# HWI4U

Document ID: HWI4U-README · Version: 3 · 2026-10-20

## Dokumentáció és funkciókövetés

[Wiki](https://github.com/aniziusz/hwi4u/wiki/Home-hu) · [Feature requests](https://github.com/aniziusz/hwi4u/wiki/Feature-requests-hu) · [Projects table/board](https://github.com/users/aniziusz/projects/1) · [Offline tracking guide](docs/TRACKING.hu.md)

Wiki és nyilvános funkciókövetés. A wiki a 0.18.0 forrást dokumentálja; ez az ág régebbi kódot tartalmazhat. A hivatkozott forrásverziót használja; dokumentáció nem frissíti a kódot.

**Hardware inventory database client** — helyi Python/Qt alkalmazás SQLite-tal, EN/DE/HU-felülettel. Forrásverzió **0.13.0**, séma **21**. Használatához felhőfiók nem szükséges.

Eszközök, Unicode-név, generált UUID/rövid ID, dátum/vásárlás/hely, csoport/típus, életciklus/állapot, OS/firmware, interfész/MAC/IP, kapcsolatok és források rögzítése. Kép/PDF külön kezelt fájl. Nincs automatikus felderítés/igazolás; ismeretlen adat ismeretlen marad.

Repository: kód, séma, migráció, fiktív tesztadat és nyilvános dokumentáció; nincs kitöltött leltár, melléklet, személyes projekttörténet vagy titok. Üres adatbázis schema.sql-ből; saját adat forráskönyvtáron kívül. Kitöltött adatbázis nem Git-fork.

Linuxon disztribúciós Qt-rendszerkönyvtár kell. Ubuntu-CI tesztek előtt libegl1, libopengl0 és libxkbcommon0 települ; nem pip-csomag. Más disztribúció megfelelő csomagjai szükségesek.

## Linux gyorsindítás

Tesztelt referencia: Python 3.14.7, SQLite 3.53.4, PySide6/Qt 6.11.2, Git 2.55.0. Más verzió/platform nincs minősítve. Előzetes Windows-fájl nem igazol támogatást; Android/iOS nincs megvalósítva.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py init
python manage.py run
```

Virtuális környezet különíti el a függőségeket. init üres éles és független TEST-másolatot hoz létre az adatkönyvtárban (Linux: `$XDG_DATA_HOME/hwi4u`, különben `~/.local/share/hwi4u`). Első kiadás előtt elkülönített teszt; létező célkönyvtárat elutasít. Saját új hely: minden parancshoz `--workspace /abszolut/utvonal/forrason/kivul`. Nincs meglévő adatimport/felülírás. Sikertelen inicializálás diagnosztikai könyvtára megmarad; ellenőrzés után másik üres cél választható.

```sh
python manage.py test
python manage.py publish
```

Kiadás TEST-ben ellenőrizendő, majd tudatos éles jóváhagyás. Publikálás nem másol tesztrekordot élesbe. [Útmutató](GUIDE.hu.md), [Közreműködés](CONTRIBUTING.hu.md), [Visszaállítás](docs/RECOVERY.hu.md), [Terv](FEATURES.hu.md), [Licenc](NOTICE.hu.md). manage.py a repository belépési pontja; .sh/.cmd generált munkaterülethez/kompatibilitáshoz marad.

Markdown/Python/SQL normál programmal offline olvasható. Függőségtelepítés/GitHub hálózatot igényel. Külső referenciák nem archiváltak; nincs teljes offline függőség-/bináriscsomag. Helyi adat nem független mentés; forrás és privát munkaterület külön mentendő.

[English](README.en.md) · [Deutsch](README.de.md)
