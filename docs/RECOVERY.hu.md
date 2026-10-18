# Mentés és visszaállítás

Document ID: HWI4U-RECOVERY · Version: 1 · 2026-10-18

Privát adat Git-en kívüli munkaterületen. GitHub forráskezelés, nem leltármentés. Teljes munkaterület (adatbázis, photos/manuals/sources, .runtime, beállítás, forrásmásolat) független mentése és Git-klón/bundle szükséges. Azonos lemez nem független. Konzisztens fájlrendszerpillanatkép vagy írók bezárása fájlmásolás előtt; élő SQLite-ot ne másoljunk gondatlanul. Kódoláshoz nem kell bezárni.

GUI teljes mentés: ellenőrzött ZIP adatbázissal, hivatkozott fájllal és MANIFEST.json-nal; automatikus .sqlite3 fájlok nélkül. Forráscommit/kiadás-ID megőrzése mentés mellett. Régi runtime megmaradjon; migráció nem fordítható vissza egyszerű régi kóddal.

```sh
python tools/verify_bundle.py /utvonal/mentes.zip /uj/ures/visszaallitasi/konyvtar
python inventory.py --db /uj/ures/visszaallitasi/konyvtar/hardware.sqlite3 check
```

Ellenőrző hiányzó/extra/veszélyes tagot vagy hibás hash-t elutasít; csak új könyvtárba bont. Második parancshoz azonos séma kell (itt 21); régebbi mentéshez előbb megfelelő forrás/runtime, majd másolaton kezelt migráció. user_version nem manipulálható. ZIP adat, nem inicializált manage.py-munkaterület.

Szokásos helyreállítás: teljes konzisztens munkaterületmentés ÚJ helyre, marker/forrás/runtime megőrzésével; `python manage.py run --workspace /uj/visszaallitott/munkaterulet` annak rögzített éles verzióját futtatja. Integritás/hash ellenőrzése, eredeti ne íródjon felül. Ha csak adat-ZIP van, ellenőrzött kibontás és megfelelő forrás megőrzése, kifejezett adatátvételi terv; automatikus ZIP-adoptálás nincs ebben a kiadásban.

Sikertelen publikálásnál éles mutató megmarad. Forrásjavítás, teszt, újrapublikálás. Függő tranzakció befejezése és újrapróbálás; másik szerkesztőt ne állítsunk le, ellenőrzést ne kapcsoljunk ki. Hibás migráció rollback, teljes előmentés megmarad. Összetartozó teljes adat/runtime visszaállítása régi kód új sémán futtatása helyett. [Telepítés](../README.hu.md) · [Fejlesztés](../CONTRIBUTING.hu.md)
