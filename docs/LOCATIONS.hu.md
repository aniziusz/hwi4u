# Vezetett eszközelhelyezés

Document ID: HWI4U-LOCATIONS · Version: 1 · 2026-10-18

FR-025, forrás 0.14.0/22-es séma, TEST-ellenőrzésre jelölt. Élesítés külön jóváhagyással. A Guided form készült el; rajzimport, automatikus alaprajzválasztás, X/Y-kalibrálás és grafikus jelölő későbbi szakasz. DXF-hez minta és megerősített egység/origó szükséges; CAD-támogatás nem igazolt.

1. Válaszd ki az eszközt, a további helyszöveg alatt nyisd meg a **Vezetett helymegadás…** ablakot.
2. Válassz Megadott hely, Ismeretlen vagy Nem alkalmazható / hordozható állapotot. Hordozhatóság nem következik a típusból.
3. Használj meglévő helyet, vagy adj meg opcionális épületet/telephelyet, szintet/emeletet és helyiséget. Új hely törli az ablak mezőit. Újrafelhasználás címet/épületet/szintet/helyiséget másol, a pozíciót, magasságot és megjegyzéseket törli, hogy régi pozíció ne kerüljön véletlenül új helyiséghez.
4. Add meg az eszköz pozícióját/falát, opcionális magasságát méterben, referenciával. `1,8` és `1.8` elfogadott; 0–10000 m. Magasság mellett kész padlószint, talajszint vagy más referencia szükséges; utóbbit megjegyzésben írd le. Magasság nélkül nincs referencia. Minden szövegmező egysoros Unicode, legfeljebb 200 karakter.
5. Nyisd le a **Cím és további megjegyzések (opcionális)** részt: ország, irányítószám, település, utca, házszám, megjegyzés. Nincs kötelező hierarchiaszint; polcleírás önmagában elegendő. Ellenőrizd az összetett előnézetet.
6. **Helyadat használata** ellenőriz és a függő adatokat visszaadja az eszközűrlapnak. **Eszköz mentése** minden módosítást atomikusan ír, ellenőrzött előzetes mentés után. Mégse az ablakban megtartja a korábbi értékeket; az eszközűrlap visszavonása a szokásos nem mentett változások ablakát használja. Megnyitás/visszavonás nem hoz létre helyet.

Egy eszköz módosítása nem nevez át közös helyet és nem helyez át más eszközt. A helyek változtathatatlan pillanatképek; pontosan egyező kanonikus mezők újrahasználhatók. Más érték csak eszközmentéskor hoz létre másik helyet. Nem használt helyek megmaradnak; globális átnevezés/törlés nincs. Szabad szintnevek nem kényszerítenek számozást. Javaslatok az ablak nyelvét követik, tárolt érték szó szerint megmarad. Felhasználói adat nem függetlenül igazolt mérés.

A 022 migráció megőrzi a `devices.location` szövegét feldolgozás nélkül. **Helyszöveg / további leírás** néven külön szerkeszthető, továbbra is legfeljebb 200 karakter; mentéskor a szokásos szóközellenőrzés érvényes. Az új strukturált állapot kezdetben Ismeretlen akkor is, ha régi szöveg van. Nincs csendes felülírás. Keresés mindkettőben. JSON-/SQL-/CSV-exportban `location_places`, `device_locations`, `device_location_history`; külső exportprofil még terv. Történetben előző/új strukturált érték, UTC-idő, `user_entry` forrás és `user_reported` ellenőrzés. Eszköztörlés után megmarad; törlési mentés/történet tartalmazza az elhelyezést. Stabil eszközazonosítók és más adatok megmaradnak.

Repository-munkaterület: `python manage.py publish --workspace /abszolut/privat/munkaterulet`, majd `python manage.py test --workspace /abszolut/privat/munkaterulet`. TEST-ben Frissítés alkalmazása vagy bezárva szokásos indítás. A kezelt frissítő ellenőrzött teljes mentés után, írási foglalás alatt végzi a 21→22 migrációt; foglalt író halasztást, hiba visszagörgetést okoz. Nincs kikényszerített bezárás vagy kézi élő SQL. Új adatbázist ne nyiss régi klienssel. Éles verzió csak a pontos jelölt jóváhagyásával változzon; TEST-rekordot ne másolj élesbe. [Visszaállítás](RECOVERY.hu.md): nincs sémavisszalépés; korábbi teljes mentést új mappába, megfelelő régi klienssel állíts vissza, újabb fájlokat tartsd meg ellenőrzésre.

Ellenőrzés: `QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests`. Céltesztek: magasság, helyújrahasználat/izoláció, elavult mentés, mentési hiba, függő adat/Mégse/nyelv, keresés, 21→22 adatmegőrzés, változtathatatlan történet és teljes visszaállítás. Offscreen-Qt Linux-ellenőrzés, nem Windows-/mobiligazolás vagy éles telepítés. Forrást és privát adatot függetlenül ments; ugyanazon lemez nem elegendő.

[Útmutató](../GUIDE.hu.md) · [English](LOCATIONS.en.md) · [Deutsch](LOCATIONS.de.md)
