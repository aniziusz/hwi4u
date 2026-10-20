# Funkciókövetés és dokumentációkarbantartás

Document ID: HWI4U-WIKI-TRACKING · Version: 1 · 2026-10-20

**Feature list** minden FR kereshető táblája, **Work board** a nyitott munka. Mezők: FR ID, cím, állapot, fajta (Feature/Bug/Process), opcionális prioritás/célverzió, felelős/címke. Nincs kitalált prioritás/vállalás. Állapot: Backlog, Ready, In progress, Review, Done, Duplicate. Issue-szám nem FR-ID. Kész funkció Done lehet main-be még nem egyesített forráság esetén is; forrás/CI ellenőrzendő kódválasztás előtt.

Egy issue FR-enként; pontosításkor újrahasználni. FR-ID címben/törzsben marad, terjedelem issue-ban, implementáló PR hivatkozva, ellenőrzés után Review, elfogadott mérföldkő után Done. Duplikátum saját ID-val/indokkal, történet nem újraszámozott. Meglévő issue eredeti szövege/története megőrzendő. Metaadat export és helyi EN/DE/HU dokumentáció kapcsolódó munka során frissítendő; nincs háttérszinkron.

Wiki ellenőrzött nyilvános útmutató tükre forrásverzióval. Szerkeszthető Markdown-/Git-másolat offline marad, privát anyag külön. Feltöltött adatbázis/számla/privát rajz/fotó/cím/titok/helyi útvonal nem publikálható. ID/verzió/dátum nyelvek között egyezik. Jövőbeli frissítés ellenőrzött publikálás, más módosítását nem írja felül automatikusan; előbb letöltés és ütközéskezelés. Külső oldalhoz hálózat kell, ha nincs külön mentve; nincs teljes offline állományígéret.

Hordozható visszaállításhoz forrás/wiki Git-klón és projektmező/elem/issuetörzs JSON-export. Markdown/JSON GitHub/AI-fiók nélkül olvasható. Helyi másolat nem független mentés; külön helyre mentendő. Tracker metaadat, nem privát eszközfájl-mentés. Titok nem kerül mezőbe.
