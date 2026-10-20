# Névjavaslatok és címkék

Document ID: HWI4U-NAMES-TAGS · Version: 1 · 2026-10-20

FR-042 és FR-051 · 0.21.0 TEST · 26-os séma. A szabályokat a felhasználó 2026-10-20-án jóváhagyta. Az éles változat 0.18.0 marad. A felhasználó elfogadta a 0.20.0 TEST-et; ez nem jelenti az új jelölt vagy a TEST-adatok éles átvételét. A régebbi útmutatórészek megtartják verziójukat; a nevek/címkék aktuális leírása ez a dokumentum.

## Névjavaslatok

Meglévő eszköznél válassza az Eszköz szerkesztése műveletet. Alap vagy Részletek nézetben adja meg a gyártót, a modellt és/vagy az eszköztípust. A Névjavaslat mintája **gyártó modell — eszköztípus**, a hiányzó részek nélkül. Bemenet nélkül nincs javaslat; gyártót, modellt vagy hardvertényt nem talál ki. A **Javaslat alkalmazása** lecseréli a nevet a még nem mentett űrlapon; utána szabadon szerkeszthető. Meglévő/kitöltött név nem módosul automatikusan. Az előnézet változása önmagában nem számít eszközmódosításnak. Mentés véglegesít, elvetés visszaállítja a mentett nevet. A gyors- és teljes ablak ugyanazokat a mezőket használja.

A javaslat megőrzi a kis-/nagybetűket és Unicode-ot. Egységesíti a szóközöket, eltávolítja a nem nyomtatható vezérlő-/sortörésjeleket az előnézetből, és betartja a 100 karakteres határt. Ütközésnél (2), (3) stb. utótagot kap; az alapszöveg az utótaghoz rövidül. Az összehasonlítás a meglévő Unicode NFKC-, casefold- és szóköz-normalizálást használja; a szerkesztett eszköz kimarad. Alkalmazáskor újra ellenőrzi az aktuális mentett neveket; a végső tranzakció az egyidejű ütközést is tiltja. Az utótag javaslat, nem lefoglalt számláló. A leíró név különbözik a UUID-től, véletlen rövid azonosítótól, gépnévtől és sorozatszámtól. Azonosítókat/gépnevet nem tölt ki és nem módosít. Hosszú javaslat rövidülhet; mentés előtt ellenőrizze.

## Újrahasználható címkék

Az opcionális Címkék választó Alap és Részletek nézetben is elérhető, a teljes ablak Általános részén. Válasszon meglévő neveket vagy Címke hozzáadását, jelöljön többet, majd Alkalmazás. Új címkék és hozzárendelések az eszköz mentéséig függőben maradnak; a választó megszakítása vagy az eszközmódosítások elvetése eldobja az új bevitelt. Megnyitás önmagában nem hoz létre semmit. Címke nem helyettesíti az eszköztípust, funkcionális szerepet, helyet, állapotot vagy igazolt tulajdonságot. Nincs kezdő szókészlet vagy automatikus hozzárendelés.

A név egy sorban 1–50 nyomtatható Unicode-karakter lehet. A többlet- és szélső szóközök összevonódnak/eltűnnek. Megjelenítés NFC, egyediség NFKC, casefold és összevont szóközök alapján. Egyenértékű meglévő címkénél a mentett írásmód marad. Egyenértékű többszörös kijelölés egyszer mentődik. Stabil katalógus-UUID-k kapcsolják az eszközöket a címkékhez. Kijelölés megszüntetése csak az adott eszköz hozzárendelését törli, a címkét és más eszközöket nem érinti. Közös átnevezés, összevonás és katalógustörlés későbbre halasztva. Nem használt címke továbbra is elérhető. A változtathatatlan hozzárendelési előzmény ID-t/nevet és user_entry/user_reported eredetet őriz; tényállítást nem igazol. Megtekintésben nincs módosítás. Nyelvváltás megőrzi a neveket és a függő kijelölést; mentett címkéket nem fordít.

Bal oldalt Nézet → Oszlopok alatt kapcsolja be a Címkék oszlopot. Fejlécszűrőben **bármelyik választott címke** elég, a többi oszlopszűrővel **ÉS** kapcsolatban. A szövegkeresés rejtett oszlopnál is tartalmazza a címkéket. A meglévő Ismeretlen választás itt címke-hozzárendelés hiányát jelenti, nem valamely ténybeli tulajdonság hiányát. Címkék szerinti csoportosítás ebben a változatban nincs. Oszlopsorrend, szélesség és szűrő megmarad; az új oszlop kezdetben rejtett.

## Tárolás, export és biztonságos frissítés

A 26-os séma tag_choices, device_tags és változtathatatlan device_tag_history táblákat ad hozzá. A 026-os migráció meglévő eszközökhöz nem rendel címkét; megőrzi a UUID-ket, rövid azonosítókat, bizonyítékokat és egyéb adatokat. Katalóguslétrehozás, hozzárendelés és eszközmódosítás közös írási tranzakcióban, ellenőrzött előzetes mentéssel történik. Elavult címke-hozzárendelés megakadályozza a mentést, az űrlap megmarad. A tags nélküli CLI-/eszközfrissítés megtartja a hozzárendeléseket. Eszköztörléskor a katalógus és címkeelőzmény megmarad, a törlési pillanatkép tartalmazza a címke-ID-ket/előzményt; előtte ellenőrzött teljes mentés készül.

Teljes mentés/visszaállítás minden címketáblát tartalmaz. Az `inventory.py export --directory /uj/export/mappa` JSON/SQL formában katalógust, hozzárendelést és előzményt is visz; `inventory.py show --device DEVICE_ID` címkeneveket mutat. A parancs elé tegye a `--db /abszolut/privat/hardware.sqlite3` opciót, a választott kompatibilis, változtathatatlan kiadás inventory.py fájljával. Nincs új XLSX-/célrendszerexport; FR-048/023/027 külön marad. Új forrás CLI-t ne indítson régebbi éles sémán.

Indítsa TEST-et rendesen, vagy válassza a Frissítés alkalmazását. Futó régi kliens kötött marad; a frissítő ellenőrzött teljes csomag után, írásfoglalás alatt végzi a 25→26 migrációt. Zárolás biztonságosan halaszt; fejezze be a blokkoló tranzakciót, majd próbálja újra. Kódolás/publikálás nem migrálja a nyitott adatbázist és nem frissíti TEST-et éles adatokból. Éles átvételhez a pontos tesztelt jelölt kifejezett elfogadása kell. Helyreállítás: a frissítés előtti teljes csomagot új mappába állítsa vissza kompatibilis 0.20.0/25-ös kóddal; régebbi kódot ne irányítson frissített adatbázisra. Helyi pillanatkép nem független mentés.

## Ellenőrzés és előfeltételek

A meglévő névszabályok, azonosítómezők, többválasztós fejlécszűrők, Megtekintés/Szerkesztés és kezelt mentések/migrációk igazolt kódbeli előfeltételek. Nem kell új függőség vagy infrastruktúraprojekt. Fiktív tesztek: hiányzó/hosszú/Unicode/ütköző nevek, szándékos alkalmazás, függő adatok/nyelvek, normalizálás/újrahasználat, előzmény, ütközés, mentési hiba atomisága, szűrő/keresés, törlési pillanatkép, JSON/SQL/teljes visszaállítás, sorrendi migráció, zárolás és visszagörgetés. Az aktuális végrehajtási/platformbizonyíték a privát projektbejegyzésből és pull requestből érhető el; külön a felhasználói elfogadástól. Kód, SQL, JSON és útmutató offline olvasható; függőségek és linkelt oldalak nem alkotnak offline telepítőcsomagot.

[Guide](../GUIDE.hu.md) · [Editor modes](EDITOR-MODES.hu.md) · [Recovery](RECOVERY.hu.md)
