# Hardverazonosító mezők

Document ID: HWI4U-IDENTIFICATION · Version: 1 · 2026-10-19

HWI4U 0.17.0 / 24-es séma — FR-036. Gyártó, Modell, Sorozatszám opcionális Unicode szövegmező. Ebben a sorrendben közvetlenül a Hely szövegmező fölött a gyorsszerkesztőben. Nagy szerkesztőben ugyanazok a vezérlők a **Hardver és hely** csempén, helyadatok fölött és megfelelő faelemmel. Meglévő Mentés/Elvetés, nyelv- és ütközésvédelem érvényes.

Ismeretlenül üres, NULL-ként mentődik. Mezőnként max. 200 nyomtatható egysoros karakter. Szélső szóköz eltávolítva, kis-/nagybetű, kezdő nullák és belső szóköz megmarad. Sorozatszám szöveg: `0007aB` pontosan megmarad. Nincs globális egyediség; gyártók számai átfedhetnek/ismeretlenek lehetnek. Gyártó/márka és modellnév/kód külön leíró eszköznévtől és elsődleges típustól. Felhasználói adat, nem automatikusan igazolt.

Eszközkereső mindháromra keres rejtett oszlopnál is. Oszlopok… megjeleníti, fejlécszűrő szűri; Gyártó/Modell csoportszint is lehet. Meglévő sorrend, szélesség, csoport és szűrő megőrzött beállításfrissítésnél; új oszlopok végén rejtve. JSON/SQL-export és mentés/helyreállítás pontos szöveget őriz. UUID/rövid ID/szerep/besorolás/helyadat változatlan.

024 migráció nullable oszlopot ad, névből/számlából/hivatkozásból nem következtet. Meglévő eszközök üresek maradnak. Kezelt TEST-frissítés/normál TEST-indítás teljes mentést készít 23→24 előtt, sor/ID marad. Futó kliens mögött ne migráljon, kiadott migrációt ne írjon át, feltöltött DB-t ne cseréljen, régi klienst 24-esre ne irányítson. Éles külön átvételig rögzített. Visszaállítás: ellenőrzött korábbi teljes mentés új mappába, megfelelő régi verzió az útmutató szerint. Helyi másolat nem független mentés.

Fiktív tesztek: régi sor/ID/NULL, pontos sorozatszám, üres/hossz/vezérlőkarakter ellenőrzés, mentési hiba/ütközés, mindkét mezősorrend, nyelvek/keresés, korábbi nézetbeállítás. Natív próba kezdő nullát is ellenőriz teljes helyreállítás után. Teljes/platform bizonyíték review-ban; felhasználói átvétel külön. Példák nem töltenek ki valódi eszközt.

[Útmutató](../GUIDE.hu.md) · [Lista/munkaterület](WORKSPACE.hu.md) · [Helyreállítás](RECOVERY.hu.md)
