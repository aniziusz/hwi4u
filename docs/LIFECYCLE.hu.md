# Modelljavaslatok és életciklusdátumok

Document ID: HWI4U-LIFECYCLE · Version: 1 · 2026-10-19

FR-037/038/039 · Forrás 0.18.0 · Séma 25 · Először TEST. Élesítés csak tudatos elfogadás után. A modellkatalógus üresen indul; nincs privát leltár, online katalógus vagy automatikus adatgyűjtés. Migráció nem talál ki értékeket és nem módosít azonosítót/besorolást.

## Hat külön tulajdonság

Az **Életciklusdátumok** a gyorsűrlapon és külön csempén elérhető. Ismeretlen tulajdonság Ismeretlenként látszik. Dupla kattintás vagy Hozzáadás/Szerkesztés. Eltávolítás csak előkészít; **Eszköz mentése** rögzít, Elvetés visszaállít. Forráskönyvtár továbbra is azonnal ment; életciklusadat/forráshozzárendelés a szülőűrlappal. Módosítás/törlés történeti pillanatképet őriz; export tartalmazza, külön történetnéző nincs.

- Piaci megjelenés: gyártói bevezetés a pontos modellhez/változathoz, nem alkatrész vagy puszta bejelentés.
- Firmware biztonsági támogatás vége: szolgáltató, termék, firmware-verzió/támogatási ág, például BIOS/UEFI vagy SSD-firmware.
- OS biztonsági támogatás vége: szolgáltató, telepített OS/disztribúció, verzió/ág; alap-OS nem helyettesíti a disztribúció szabályát.
- Hardverszerviz-támogatás vége: konkrét javítás/csere/alkatrész/szervizígéret és régió.
- Gyártás vége: modell gyártásának vége; nem értékesítési/támogatási vég.
- Garancialejárat: egyedi készülék/vásárlás/szerződés, nem megosztott modelldátum.

Tulajdonságonként több megfigyelés lehetséges több szoftverhez és ellentmondásokhoz. Szolgáltató/termék, szükség szerint verzió, változat/régió/hatókör, forrás, valódi megfigyelési/lekérdezési dátum, ellenőrzési állapot és megjegyzés. Ismeretlen üres marad, nem mai dátum; szerkesztő alapdátuma csak kifejezett használatkor mentődik. Megjelenés/gyártás gyártót és pontos modellt kér szolgáltató/termékként; szoftver szolgáltatót/terméket/verziót; hardverszerviz/garancia hatókört. Nincs kitalált támogatási idő. Közös OS-/firmware-képnél azonos bizonyíték használható mesterséges határidők nélkül.

Pontos nap naptárral, hónap (`2025-06`), negyedév (`2025-Q2`) és év (`2025`) támogatott. Válassza a pontosságot; nincs kitalált nap. Ellenőrzött megfigyeléshez dátum és ellenőrzött dátumozott forrás kell. Forrásellenőrzés nem igazolja automatikusan a saját eszközre alkalmazhatóságot. Nem ellenőrzött adat forrás nélkül figyelmeztetéssel menthető. Webhelyhez hálózat kell; offline bizonyítékhoz szöveg vagy importált PDF. Nem állítjuk, hogy minden külső forrás helyben mentett.

## Vásárlási dátum

Legkorábbi vásárlás: **megjelenés mínusz egy naptári év**, határnapot beleértve; február 29. az előző nem szökőév február 28-ára kerül. 2025-06-15 megjelenésnél 2024-06-15-től elfogadható. Hónap/negyedév/év intervallum: mindkét határ egy évvel korábbra; előtte tiltás, bizonytalan határsávban figyelmeztetés, utolsó határtól megfelel. `2014-Q2`: 2013-04-01 előtt tiltás, 2013-04-01–2013-06-29 figyelmeztetés, 2013-06-30-tól megfelel. Ez nem bizonyít tényleges korai eladást.

Tiltás csak ellenőrzött, illeszkedő megjelenési bizonyítéknál. Eltérő intervallum, nem ellenőrzött/hiányzó adat vagy gyártó/modell eltérés figyelmeztet. Csak megjelenés számít; gyártás/támogatás vége utáni vásárlás megengedett. Nincs automatikus javítás. Régi ütközés független szerkesztésnél megtartható; új/módosult vásárlás, életciklus vagy gyártó/modell ellenőrzendő. Figyelmeztetést át kell tekinteni. Pontos egyezés kis-/nagybetűtől független, Unicode/szóköz normalizált; nincs talált álnév vagy régió.

## Újrahasználható modellprofil

1. Gyártó/modell, típus/csoport, szerepek és életciklusadatok ellenőrzése bizonyítékból; eszközforrások kijelölése.
2. **Modelljavaslatok… → Jelenlegi értékek mentése modellprofilként…**; változat/régió/hardverrevízió és bizonyíték/érvényesség megadása. Könyvtár azonnal ment teljes mentéssel, eszközűrlap elvetése nem vonja vissza. Kiválasztott változat megerősítéssel új változtathatatlan felülvizsgálatként menthető. Régi profil/forrás és eszköz változatlan.
3. Pontos gyártó-/modellegyezésnél változatot választani, csoport/típus/szerep/dátum/forrásazonosító/megjegyzés áttekintése, jelölőnégyzet és Alkalmazás. Változat automatikusan nem választódik.
4. Alkalmazás csak űrlapot módosít: típus/csoport, szerepek és nem garanciális életciklus cserélődik, egyedi garancia megmarad, eszközforrások bővülnek. Eszköz mentése vagy Elvetés. Elavult felülvizsgálat/modellhiba visszautasítva. Hirdetett képesség nem igazolja a használatot; szerep csak áttekintett javaslat.

Nincs közelítő egyezés, automatikus álnév, online keresés, háttérszinkron vagy visszamenőleges eszközfrissítés. Kézi besorolás/szoftverbeállítás megmarad. Felülvizsgálat nem írja át a már másolt dátumokat. Sorozatszám, egyedi garancia és telepített szoftverbeállítás nem megosztott. Bizonytalan érvényességnél megszakítás és vizsgálat. Egy elsődleges típus, több szerep.

## Frissítés és visszaállítás

Kezelt TEST-frissítés vagy szokásos TEST-indítás: ellenőrzött változtathatatlan kiadás és teljes mentés a tranzakciós 24→25 migráció előtt; régebbi sémák rendezett láncon. Fejlesztéshez futó rögzített kliens bezárása nem kell; zárolás biztonságosan halaszt. Nyitott adatbázist nem cserélünk, régi kliens mögött nem migrálunk. Új táblák: device_lifecycle, device_lifecycle_history, model_profiles. JSON/SQL és teljes csomag megőrzi adatokat/profilokat/forrásokat/történetet, kezelt fájlokat is. Korábbi teljes mentés új könyvtárba, kompatibilis régi szoftverrel; régi szoftver nem használhat 25-ös sémát. [Visszaállítás](RECOVERY.hu.md). Helyi másolat nem független mentés; dokumentáció/adatok függetlenül mentendők.

Fiktív adatos tesztek: nap-/intervallum-/szökőévhatárok, ismeretlen/ellentmondó/hibás modell, szoftver-/hatóköradat, ellenőrzött források, ütközés, mentéshiba, profilverzió/változat, elfogadás/elvetés, garancia, 24-es migráció, törlési történet, export/visszaállítás. Platformteszt és felhasználói elfogadás külön; forrás megléte nem fizikai platformminősítés. [Útmutató](../GUIDE.hu.md).
