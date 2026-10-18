# Felhasználói útmutató

Document ID: HWI4U-GUIDE · Version: 2 · 2026-10-18

README után új privát munkaterület inicializálása. Éles: manage.py run, TEST: manage.py test. Külön adatok, nincs automatikus szinkron. manage.py refresh-test tudatos művelet: megerősítés, régebbi másolatok megőrzése. Ugyanazon rekord párhuzamos szerkesztését kerüld; elavult mentést elutasít.

Új eszköz: egyedi leíró név és forrásjegyzet/választott eszközforrás. UUID és két betű/öt szám rövid ID automatikus. Unicode-név max. 100 karakter; betűméret/extra szóköz nem különböztet meg duplikációt. Típus határozza a csoportot. Állapot életciklus, nem online jelzés. Ismeretlen dátum Ismert nélkül, ismerthez naptár. Helyszöveg opcionális egy sor, max. 200 Unicode-karakter. Vezetett megadás újrahasználható helyekkel és eszközpozícióval; lásd a helyadat-útmutatót. Ár/pénznem együtt. Vásárlási hely/eladó külön a fizikai helytől; helyesírási javaslat nem ír át automatikusan.

Eszköz mentése ellenőrzött előzetes adatbázismásolat után ment. Mégse visszaállítja a mentett űrlapot. Függő változás: Mentés, Nem mentett változások elvetése, Szerkesztés folytatása. Elvetés nem töröl mentett adatot. Törlés megerősítéssel és teljes mentéssel; ID/történet megmarad, más eszköz nem sérül. Kapcsolt port/eszköz előtt kifejezetten távolítsd el kapcsolatait. Összeállítás/tény CLI-n kezelhető; nincs GUI-szerkesztőjük.

Hálózati azonosítók lenyitható: opcionális gépnév, tényleges interfész/MAC, több IPv4/IPv6. Nincs DNS-/DHCP-beállítás vagy felderítés. Szoftver/interfész/protokoll szintén lenyitható; támogatott/használt külön. Képesség nem bizonyít kapcsolatot. Hiányzó ellenőrizetlen forrás figyelmeztet; ellenőrzötthöz bizonyíték/dátum kell. Legújabb gyártói firmware nem bizonyít telepítést. Típus nem generál igazolt tényt.

Hálózati kapcsolat két külön eszköz mentett portja között: közeg, tervezett/megfigyelt/megszüntetett állapot, opcionális sebesség/forrás. Azonnali mentés történettel, nem élő ábra. Több kapcsolat/Wi-Fi-hozzárendelés dokumentálható. Forráskönyvtár újrahasználható; létrehozás/javítás azonnal mentődik, hozzárendelés csak a szülőűrlappal. Régi forrás/szöveg megmarad. Kifejezett megnyitás, nincs automatikus letöltés. PDF/kép SQLite-on kívül.

Keresésben hely/ID/szoftver/hálózati adat is. Csoport-/típusszűrő: részlet gépelése, találat választása; Minden visszaállít. Zárt lista/dátum/szám nem változik görgőtől, helyette űrlap görget. Nyitott lista/naptár és billentyűzet használható. Hover/Info: jelentés, útvonal, verzió. Nyelvváltás megőrzi függő adatot; felhasználói értéket nem fordít.

Teljes mentés: ellenőrzött ZIP adatbázissal és hivatkozott képpel/kézikönyvvel/forrással. Automatikus adatbázismásolat nem tartalmaz fájlt. Független mentés és visszaállítási útmutató szükséges. Frissítés alkalmazása védi függő módosítást, tesztelt verzióba indít; Megszakítás elhalaszt, nem veszít adatot. Publikálás/éles jóváhagyás külön. KeePass-/OPNsense-/HA-szinkron nincs megvalósítva.

[Telepítés](README.hu.md) · [Visszaállítás](docs/RECOVERY.hu.md) · [CLI](docs/CLI.hu.md)

[FR-025 · Guided location / Standort / Helyadat](docs/LOCATIONS.hu.md)
