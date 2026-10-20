# Alap/részletes nézet és védett szerkesztés — 0.20.0 TEST

Document ID: HWI4U-EDITOR-MODES · Version: 1 · 2026-10-20

FR-050/053/052/044/046. Felhasználó az Alap/részletes nézetet és bal oldali klasszikus menüket választotta. Csak TEST-jelölt, éles elfogadás külön. Séma 25/adatok változatlanok; nincs új függőség, migráció vagy TEST-adatfrissítés.

## Alap és részletes

Új ablak Alap nézettel indul: rövid ID, név, gyártó/modell, típus/csoport, hely strukturált szerkesztővel, életciklusállapot, fizikai állapot és eszközforrás. Név/forrás kötelezősége marad, más lehet ismeretlen. Típuscsoport mentéskor típusból származik. Generált ID nem szerkeszthető.

Részletek: teljes ID, sorozatszám, szerepek/modelljavaslatok, vásárlás/telepítés/selejtezés, szoftver, hálózat, interfészek/protokollok, életciklus/garancia, fotók/hivatkozások. Megtekintéskor is elérhető. Kiválasztott előnézet kezdeti mezőosztása, nem személyre szabható prioritás vagy új varázsló. Ablakon belül választás megmarad; új ablak/újraindítás Alap. Váltás nem ment/töröl/tölt újra. Nagy nézetben alkalmazkodó csempék, fa és kiemelés marad; rejtett szakasz nem foglal rácshelyet. Listabeállítások változatlanok.

## Megtekintés és szerkesztés

Meglévő rekord mindkét nézetben védett. Eszköz szerkesztése engedélyezi a változtatást. Csak olvasható szöveg másolható; forrásnézés, fotó/kézikönyv/link megnyitása Részletekben marad. Megtekintési forrásablak nem hozhat létre/revideálhat/rendelhet forrást. Életciklus-/helyszerkesztés és mellékletmódosítás szerkesztési módot kíván. Véletlen módosítás ellen véd, nem hitelesítés, titkosítás vagy adatbázis-jogosultság. Külső eszközök és kifejezett közös katalóguskarbantartás külön képesség.

Új eszköz szerkeszthető. Sikeres mentés/elvetés megtekintésre tér vissza. Hibás mentés megtartja bevitelt és szerkesztést; érintett rejtett részlet látható/fókuszált lesz. Eszközforrás: szöveg VAGY választott eszközforrás. Ellenőrzések, ütközésvédelem, mentések/UUID-k közösek; másik ablak nem írja felül a függő módosítást.

Mentés/elvetés egyszer jelenik meg jobb alsó sarokban, görgetésen kívül, csak szerkesztéskor. Eszköz szerkesztése az Alap/Részletek állapota mellett. Menük azonos műveleteket hívnak. Ctrl+S (macOS rendszerstandard Command) csak szerkesztéskor ment. Escape elvetést kezdeményez; bevitelnél Mentés/Elvetés/Szerkesztés folytatása megerősítés marad. Nincs csendes adatvesztés. Bezárás/frissítés védelem marad. Törlés külön megerősítést/ellenőrzött mentést kíván.

Fotók/kézikönyvek és új forráskönyvtár-elemek a saját párbeszédben azonnal mentődnek. Eszközmódosítások elvetése nem vonja vissza már mentett mellékletet/forrást. Forráshozzárendelések eszközmentésig függőek. Meglévő tippek jelzik a határokat. Közös típus-/kapcsolatkatalógusok kifejezett Eszközök-műveletek, megerősítéssel és több eszközre hatással; Megtekintés nem globális adatbázis-zár.

## Életciklus kibontása

Gyorsnézet: életciklus billentyűzettel is nyitható nyílgomb, kezdetben csukva, mint hálózat/szoftver. Részletekben nyitható. Rejtés értéket, forrást, figyelmeztetést, bevitelt megtart. Fejléc ellenőrzést jelző szövege és Alap/Részletek állapota tovább jelzi a figyelmeztetést. Nagy ablakban megmarad életciklus-csempe/fa ugyanazzal a szerkesztővel, mint hálózat/szoftver; nincs másolt űrlap.

## Klasszikus menük

Fájl, Szerkesztés, Nézet, Eszközök, Súgó balra; nincs szalagmenü. Natív macOS Névjegy/Kilépés-elhelyezés marad.

| Menü | Műveletek |
|---|---|
| Fájl | Új eszköz, Mentés, Teljes mentés, Kilépés |
| Szerkesztés | Eszköz szerkesztése, Elvetés, Törlés |
| Nézet | Alap/Részletek, Keresés, Szűrők, Oszlopok, Csoportosítás, Szűrők törlése, Frissítés |
| Eszközök | Típusok, Kapcsolatválaszték, Hálózati kapcsolatok, Másik kliens, Nyelv |
| Súgó | Névjegy, Útmutató, Helyi frissítések |

Qt-standard gyorsbillentyűk mentés/új/keresés/frissítés/súgó/kilépés; Ctrl+E szerkesztés, Escape elvetés. Nagy ablakban listaműveletek letiltva, lista főablakban marad. Nincs nem megvalósított Excel/visszavonás parancs. Frissítés és TEST/éles jelzés marad. Új szövegek külső EN/DE/HU-katalógusban (742 bejegyzés); nyelvváltás megtartja bevitelt, módot és forrásokat.

## Ellenőrzés és helyreállítás

TEST Apply update vagy normál újraindítás. Pontos jelölt átnézése élesítés előtt: meglévő rekord védett; szerkesztés, mezőmódosítás, Alap/Részletek váltás, mentés/elvetés. Sorozatszám/vásárlás, életciklus és nyelvek ellenőrzése; hivatkozás megnyitása szerkesztés nélkül. Korábbi változatlan TEST 0.19.0 és éles 0.18.0 megmarad; release-mappát nem szerkesztünk. [Helyreállítás](RECOVERY.hu.md) · [Alapok](FOUNDATIONS.hu.md) · [Munkaterület](WORKSPACE.hu.md).
