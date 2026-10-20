# Megbízható alapok — 0.19.0 TEST

Document ID: HWI4U-FOUNDATIONS · Version: 1 · 2026-10-20

FR-043, FR-045 és FR-047. Jelölt; éles elfogadás külön. Séma változatlan (25), nincs TEST-adatfrissítés vagy leltárfeltöltés. Futó kliensek frissítésig/újraindításig régi verzión maradnak.

## Eszközforrás

Forrásmező és forrásterület * jelöléssel: forrásszöveg VAGY legalább egy eszközforrás. Helyi üzenet bevitelkor/frissítéskor változik. Mindkettő hiánya mentést megakadályoz és a forráshoz vezet a gyors/teljes szerkesztőben. Csak OS/hálózat/kapcsolat szakaszban választott forrás nem elegendő. Hálózati/kapcsolati figyelmeztetések és igazolt értékelések követelményei változatlanok. Nem kell duplán szöveget írni. Mentés/elvetés és forrástörténet marad.

## Nyelvek karbantartása

locales/en.json, de.json, hu.json 725 áthelyezett üzenettel: menük, feliratok, segítség, tippek, választások, párbeszédek, ellenőrzési és állapotsablonok. JSON illeszkedik az élő fordításhoz, standard könyvtárral, új futtató/fordító nélkül; ezért választva Qt TS/gettext PO helyett. Nem automatikus fordítás, élő újratöltés vagy fordítói GUI.

Angol bejegyzés: stabil ID (ui.0001 stb.), változatlan source keresési név, szerkeszthető text és fordítói context. ID-ket nem szabad újraszámozni/újrahasználni; szövegváltoztatáskor source marad. Fordítások: azonos ID, text és angol megjelenítési szöveg source_sha256 értéke. Angol változás elavulttá teszi fordítást: átnézés után szöveg/hash frissítendő. Hiányzó/üres/elavult/hibás fordítás jelenlegi angolra esik vissza. Helyőrzők pontosan egyezzenek; gyorsbillentyűjel (&), írásjelek és alkalmazási jelölés megőrzendő, nem felhasználói HTML. Format 1 nem támogat többes-szám tömböket; szükség esetén előbb támogatott API tervezendő.

language, name, qt_locale alapján új nyelv menüje és naptárbeállítása következő induláskor felismerhető. Forrásmappában:

```sh
python tools/catalogues.py
python tools/catalogues.py --new-language fr --name Français --qt-locale fr_FR
```

Második parancs kizárólag új, hiányos fr.json-t hoz létre. Üres szöveg angolra esik vissza. Kontextus en.json-ban; ID/angol hash megtartandó. Hibás nyelvfájl kizárva, ellenőrző diagnózist ad. Sérült angolnál szó szerinti angol feliratok katalógustippek nélkül használhatók: kiadott fájl visszaállítása és ellenőrzése. Hiányzó/hibás nyelvbeállítás angolra áll. Leltáradat nem változik. Katalógusok forrás-ZIP/release hash részei; szövegváltoztatáshoz új ellenőrzött kiadás kell, változatlan telepített release nem szerkeszthető.

Adatbázisérték és felhasználói szöveg adat marad, nyelvváltás nem írja át. EN/DE/HU útmutatók külön fájlok. Függő bevitel, dátumnyelv, gyorsbillentyűk, helyőrzők és párbeszédek ellenőrizendők. Kompatibilitási Pythonmodulban nincs külön karbantartandó szólista.

## Mért ellenőrzés és biztonságos újrafelhasználás

Kis módosítás után célzott vizsgálat; végső regresszió előtt jelölt rögzítése. Privát bizonyítékmappa, nyilvános commiton kívül:

```sh
python tools/validate.py --evidence /absolute/private/evidence --pattern test_foundations.py
python tools/validate.py --evidence /absolute/private/evidence
python tools/validate.py --evidence /absolute/private/evidence --fresh
```

Célzott eredmény időt/visszatérési kódot mér, sosem kiadási igazolás. Teljes futás tesztszámot, eltelt másodpercet, kimenethasht, forrás/teszt/katalógus/függőség jegyzéket, Pythonprogramot/verziót, tényleges Qt/modulfájlhasheket, OS/architektúrát, SQLite-ot és környezetdigestet rögzít. Környezeti érték nem tárolódik. Helyi véletlen kulcs HMAC-aláírást készít; eredmény és kimenetnapló integritása ellenőrzött. Változó forrás/környezet/függőség, hiányzó/hibás aláírás, módosult napló, hiba vagy nulla teszt új futást kíván. Futás végén bemenet újraellenőrzött; --fresh mindig újrafuttat. Hiba hibakóddal tér vissza.

Publikálás/élesítés privát .runtime/validation bizonyítékot használ. Teljes bemeneti ujjlenyomat egyezése kell, nem csupán verzió/commit. Helyi siker nem helyettesít natív platform-CI-t, csomagellenőrzést, migrációt/mentést, TEST-jelölt elindítását vagy kifejezett éles elfogadást. Éles kiválasztás előtt release újraellenőrzött. Nincs automatikus élesítés. Hiányzó kulcs/bizonyíték új futást eredményez; sérült kulcs külön hiba. Helyi eredmény nem független biztonsági mentés.

HMAC sérült/szerkesztett bizonyíték ellen véd, nem azonos felhasználói joggal és kulccsal rendelkező rosszindulatú folyamat ellen. Kulcsok/naplók privátak; .runtime nem tölthető Gitbe/artefaktumba. Gyanús eredményt őrizzük meg, új üres privát mappával friss vizsgálat. Ne töröljünk release/adatfájlt ellenőrzés megkerülésére. Külön környezetek nem osztanak bizalmat. CI jelöltenként egyszer mér; platform-smoke/csomagolás külön.

Eredeti becslés, tényleges eltelt idő, hibák/ismétlés, felhasználói/külső várakozás és újrafelhasználás rögzítendő. Aktív munka ismeretlen külön mérés nélkül. Csak hasonló futások hasonlíthatók; nincs univerzális gyorsulás vagy keretszázalékból munkaidő. [Közreműködési folyamat](../CONTRIBUTING.hu.md).
