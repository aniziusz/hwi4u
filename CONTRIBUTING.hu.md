# Közreműködés

Document ID: HWI4U-CONTRIBUTING · Version: 6 · 2026-10-21

[Windows offline EXE-telepítő · 0.21.1 TEST](docs/WINDOWS-INSTALLER.hu.md)

[Névjavaslatok és újrahasználható címkék — 0.21.0 TEST](docs/NAMES-TAGS.hu.md)

[FR-050/053/052/044/046 · 0.20.0 TEST · Basic/Details · View/Edit](docs/EDITOR-MODES.hu.md)

[FR-043/045/047 · 0.19.0 TEST · Foundations / Grundlagen / Alapok](docs/FOUNDATIONS.hu.md)

Branch/kódfork saját privát munkaterülettel és fiktív eldobható adatokkal; ne közösen írható leltárfájl. Migráció őrizze az UUID-ket. Futási adat, melléklet, számla, titkos napló/fiókadat és privát projektdokumentum nem commitolható. Ignore nem helyettesít staging/történet-ellenőrzést.

```sh
git switch -c feature/descriptive-name
QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests
python tools/check_distribution.py
```

Tesztek eldobható adatbázisokkal, soha valódi leltárral. Linux offscreen CI push/pull request esetén `.github/workflows/tests.yml`; fájl megléte nem igazol sikeres távoli futást. Tényleges eredmény ellenőrizendő. Windows/mobil külön tesztelendő. Régebbi teszt nem hibát okozó nyitottkapcsolat-ResourceWarningot adhat; új jelzést vizsgálj, hibát ne rejts el.

Pull request: probléma, viselkedés, ellenőrzés. EN/DE/HU azonos ID/verzió/dátummal, relatív linkkel; specifikáció ne csak chatben legyen. Proprietáris anyag nem szükséges.

Adatbázis: következő egyedi migrációszám, kiadott migráció nem módosul. Ágak között számozásegyeztetés. Friss séma, verzió/export, fixture/teszt frissítése. Régi adatmegőrzés, hibás bevitel, nyitott írás, rollback és teljes visszaállítás másolaton tesztelendő. Adatbázist ne nullázzunk; ismeretlen nem törlés.

```sh
python manage.py publish --workspace /abszolut/privat/munkaterulet
python manage.py test --workspace /abszolut/privat/munkaterulet
python manage.py promote --workspace /abszolut/privat/munkaterulet
```

Publish forrást visz a generált munkaterületre, változatlan TEST-kiadást ellenőriz, éles marad rögzítve. Generált forrást ne szerkessz: eltérés észlelve a felülírás elkerülésére. TEST ellenőrzése függő módosításokkal együtt. Promote kifejezett jóváhagyás, nem másol tesztadatot. Csak új üres telepítés első ellenőrzött verziója kerül mindkét csatornára; meglévő leltár frissítését nem fogadja el automatikusan.

[Telepítés](README.hu.md) · [Visszaállítás](docs/RECOVERY.hu.md)

[Platform checks / Plattformprüfung / Platformteszt](docs/DESKTOP.hu.md)
