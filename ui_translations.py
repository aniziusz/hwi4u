"""English source text → German / Hungarian; user data is never translated."""
TEXT={}
def add(en,de,hu):TEXT[en]=(de,hu)
for line in '''Hardware inventory|Hardwareinventar|Hardverleltár
Local device records • dates, lifecycle and condition|Lokale Gerätedaten • Daten, Lebenszyklus und Zustand|Helyi eszközadatok • dátumok, életciklus és állapot
New device|Neues Gerät|Új eszköz
Refresh|Aktualisieren|Frissítés
Full backup|Vollständige Sicherung|Teljes mentés
Manage types|Typen verwalten|Típusok kezelése
Filter group|Gruppe filtern|Csoportszűrő
All groups|Alle Gruppen|Minden csoport
All types|Alle Typen|Minden típus
Unknown|Unbekannt|Ismeretlen
unknown|unbekannt|ismeretlen
none|keine|nincs
recorded below|unten erfasst|alább rögzítve
Name|Name|Név
Group|Gruppe|Csoport
Type|Typ|Típus
State|Status|Életciklusállapot
Condition|Zustand|Fizikai állapot
Edit device|Gerät bearbeiten|Eszköz szerkesztése
Device ID *|Gerätekennung *|Eszközazonosító *
Name *|Name *|Név *
Information source *|Informationsquelle *|Információ forrása *
Information source|Informationsquelle|Információ forrása
Type group|Typgruppe|Típuscsoport
Device type|Gerätetyp|Eszköztípus
Unknown / choose a type|Unbekannt / Typ wählen|Ismeretlen / válassz típust
Purchase date|Kaufdatum|Vásárlás dátuma
Installation date|Inbetriebnahmedatum|Üzembe helyezés dátuma
Scrapped date|Entsorgungsdatum|Selejtezés dátuma
Purchase price|Kaufpreis|Vételár
Currency|Währung|Pénznem
Current state|Aktueller Lebenszyklusstatus|Jelenlegi életciklusállapot
Physical condition|Physischer Zustand|Jelenlegi fizikai állapot
Known|Bekannt|Ismert
Save device|Gerät speichern|Eszköz mentése
Cancel changes|Änderungen verwerfen|Módosítások elvetése
Device photos|Gerätefotos|Eszközfotók
Add photo…|Foto hinzufügen…|Fotó hozzáadása…
Open image|Bild öffnen|Kép megnyitása
Detach|Zuordnung entfernen|Leválasztás
Connection interfaces|Verbindungsschnittstellen|Csatlakozási interfészek
Communication protocols|Kommunikationsprotokolle|Kommunikációs protokollok
Supported capabilities|Unterstützte Fähigkeiten|Támogatott képességek
Currently in use|Derzeit verwendet|Jelenleg használt
Choice|Auswahl|Választás
Supported|Unterstützt|Támogatott
In use|Verwendet|Használt
Assessment date|Bewertungsdatum|Értékelés dátuma
Manage connection choices…|Verbindungsauswahl verwalten…|Kapcsolati választék kezelése…
Manage connection choices|Verbindungsauswahl verwalten|Kapcsolati választék kezelése
New choice|Neue Auswahl|Új választási érték
Save choice|Auswahl speichern|Választási érték mentése
Lowercase choice name|Auswahlname in Kleinbuchstaben|Kisbetűs választási név
Manage device types|Gerätetypen verwalten|Eszköztípusok kezelése
Type name *|Typname *|Típusnév *
Group *|Gruppe *|Csoport *
New type|Neuer Typ|Új típus
Save type|Typ speichern|Típus mentése
Close|Schließen|Bezárás
Save|Speichern|Mentés
Cancel|Abbrechen|Mégse
Yes|Ja|Igen
No|Nein|Nem
Discard|Verwerfen|Elvetés
OK|OK|OK
Open|Öffnen|Megnyitás
Unsaved changes|Ungespeicherte Änderungen|Nem mentett módosítások
Discard your unsaved changes?|Ungespeicherte Änderungen verwerfen?|Elveted a nem mentett módosításokat?
Unsaved changes cancelled.|Ungespeicherte Änderungen verworfen.|A nem mentett módosítások elvetve.
Device list and types refreshed.|Geräteliste und Typen aktualisiert.|Eszközlista és típusok frissítve.
Device types updated. Select a device to assign its type.|Gerätetypen aktualisiert. Gerät zur Typzuweisung auswählen.|Eszköztípusok frissítve. Válassz eszközt a besoroláshoz.
Connection choices updated.|Verbindungsauswahl aktualisiert.|Kapcsolati választék frissítve.
Could not save|Speichern fehlgeschlagen|Sikertelen mentés
Could not save type|Typ konnte nicht gespeichert werden|A típus nem menthető
Could not save choice|Auswahl konnte nicht gespeichert werden|A választási érték nem menthető
Cannot open inventory|Inventar kann nicht geöffnet werden|A leltár nem nyitható meg
Save changes first|Zuerst Änderungen speichern|Először mentsd a változásokat
Update shared type|Gemeinsamen Typ ändern|Közös típus módosítása
Rename shared choice|Gemeinsame Auswahl umbenennen|Közös választási érték átnevezése
Rename or move this type for all devices that use it?|Diesen Typ für alle zugeordneten Geräte umbenennen oder verschieben?|Átnevezed vagy átcsoportosítod ezt a típust minden érintett eszköznél?
Update this choice for every assigned device?|Diese Auswahl für alle zugeordneten Geräte ändern?|Módosítod ezt a választási értéket minden érintett eszköznél?
Choose device photo|Gerätefoto auswählen|Eszközfotó kiválasztása
Photo details|Fotoangaben|Fotó adatai
Description (optional)|Beschreibung (optional)|Leírás (opcionális)
Detach photo|Fotozuordnung entfernen|Fotó leválasztása
Save full inventory backup|Vollständige Inventarsicherung speichern|Teljes leltármentés mentése
ZIP archive (*.zip)|ZIP-Archiv (*.zip)|ZIP-archívum (*.zip)
Images (*.jpg *.jpeg *.png)|Bilder (*.jpg *.jpeg *.png)|Képek (*.jpg *.jpeg *.png)
Save a device before attaching photos.|Vor dem Anhängen von Fotos ein Gerät speichern.|Fotó csatolása előtt mentsd az eszközt.
Save or cancel device changes before adding a photo.|Geräteänderungen vor dem Anhängen speichern oder verwerfen.|Fotó hozzáadása előtt mentsd vagy vesd el az eszközváltozásokat.
Save or cancel device changes before detaching a photo.|Geräteänderungen vor dem Entfernen speichern oder verwerfen.|Fotó leválasztása előtt mentsd vagy vesd el az eszközváltozásokat.
Save or cancel device changes before backing up.|Geräteänderungen vor der Sicherung speichern oder verwerfen.|Mentéskészítés előtt mentsd vagy vesd el az eszközváltozásokat.
Could not open the original image.|Originalbild konnte nicht geöffnet werden.|Az eredeti kép nem nyitható meg.
Original photo is missing or changed. Restore it from a full backup.|Originalfoto fehlt oder wurde verändert. Aus vollständiger Sicherung wiederherstellen.|Az eredeti fotó hiányzik vagy megváltozott. Állítsd vissza teljes mentésből.
Photo detached; files retained for older backups.|Fotozuordnung entfernt; Dateien für ältere Sicherungen behalten.|Fotó leválasztva; fájlok régebbi mentésekhez megmaradtak.
Photo copied and attached. Use Full backup to include database and photos in one archive.|Foto kopiert und angehängt. Vollständige Sicherung enthält Datenbank und Fotos zusammen.|Fotó másolva és csatolva. A Teljes mentés adatbázist és fotókat együtt tartalmaz.
Saved {0}. Pre-save backup: {1}|{0} gespeichert. Vorherige Sicherung: {1}|{0} mentve. Előzetes mentés: {1}
Verified full backup saved: {0}|Geprüfte vollständige Sicherung gespeichert: {0}|Ellenőrzött teljes mentés elkészült: {0}
Photo list unavailable: {0}|Fotoliste nicht verfügbar: {0}|Fotólista nem érhető el: {0}
Original image • {0}|Originalbild • {0}|Eredeti kép • {0}
{0} is required.|{0} ist erforderlich.|{0} megadása kötelező.
Device id|Gerätekennung|Eszközazonosító
Source|Quelle|Forrás
Source: |Quelle: |Forrás: 
Stored value: |Gespeicherter Wert: |Tárolt érték: 
Info|Info|Információ
Language|Sprache|Nyelv
About Hardware inventory…|Über Hardwareinventar…|A Hardverleltár névjegye…
Open user guide|Benutzeranleitung öffnen|Útmutató megnyitása
About Hardware inventory|Über Hardwareinventar|A Hardverleltár névjegye
Application version|Programmversion|Alkalmazásverzió
Release date|Versionsdatum|Kiadás dátuma
Database schema|Datenbankschema|Adatbázisséma
Database location|Datenbankpfad|Adatbázis helye
Photo folder|Fotoordner|Fotómappa
License|Lizenz|Licenc
Local, offline hardware inventory|Lokales Offline-Hardwareinventar|Helyi, offline hardverleltár
No network service or cloud account is required.|Kein Netzwerkdienst oder Cloud-Konto erforderlich.|Nem szükséges hálózati szolgáltatás vagy felhőfiók.
Features|Funktionen|Funkciók
Devices, dates, types, connection assessments and local photo attachments.|Geräte, Daten, Typen, Verbindungsbewertungen und lokale Fotoanhänge.|Eszközök, dátumok, típusok, kapcsolati értékelések és helyi fotómellékletek.
Full backup includes the database and attached photos. Automatic snapshots contain only the database.|Vollständige Sicherung enthält Datenbank und Fotos. Automatische Sicherungen enthalten nur die Datenbank.|A Teljes mentés adatbázist és fotókat tartalmaz. Az automatikus pillanatképek csak adatbázist mentenek.
Shared catalogue values and your entries remain unchanged when switching language.|Gemeinsame Katalogwerte und eigene Eingaben bleiben beim Sprachwechsel unverändert.|A közös katalógusértékek és saját adatok nyelvváltáskor változatlanok.
Created for your local home-infrastructure inventory. No independent product certification is claimed.|Für das lokale Heiminfrastruktur-Inventar erstellt. Keine unabhängige Produktzertifizierung behauptet.|Helyi otthoni infrastruktúra leltározására készült. Nincs állított független terméktanúsítás.
Could not open guide|Anleitung konnte nicht geöffnet werden|Az útmutató nem nyitható meg
Could not save language preference|Spracheinstellung konnte nicht gespeichert werden|A nyelvi beállítás nem menthető
Choose a unique ID; format is still manual|Eindeutige Kennung wählen; noch manuelle Vergabe|Adj egyedi azonosítót; a képzés még kézi
For example: device label or invoice filename|Zum Beispiel: Typenschild oder Rechnungsdatei|Például: adattábla vagy számlafájlnév
Unknown — or amount such as 129.90|Unbekannt — oder Betrag wie 129.90|Ismeretlen — vagy összeg, például 129.90
For example: front view or device label|Zum Beispiel: Vorderansicht oder Typenschild|Például: elölnézet vagy adattábla
For example: my photograph, 2026-10-18|Zum Beispiel: eigenes Foto, 2026-10-18|Például: saját fénykép, 2026-10-18
Search devices, types, interfaces or protocols…|Geräte, Typen, Schnittstellen oder Protokolle suchen…|Eszköz, típus, interfész vagy protokoll keresése…
Source required for known capabilities or known none|Quelle für bekannte Fähigkeiten oder bekannte Abwesenheit erforderlich|Ismert képesség vagy igazolt hiány esetén forrás kötelező
Choose a currency or type a three-letter uppercase code. Blank means unknown.|Währung wählen oder dreistelligen Großbuchstabencode eingeben. Leer bedeutet unbekannt.|Válassz pénznemet vagy írj három nagybetűs kódot. Üres: ismeretlen.
Choose a device type for this group, or choose Unknown / choose a type to leave classification unknown.|Gerätetyp für diese Gruppe wählen oder Unbekannt / Typ wählen für unbekannte Klassifikation.|Válassz típust a csoporthoz vagy Ismeretlen / válassz típust az ismeretlen besoroláshoz.
Database busy. Finish or cancel changes in DB Browser, close it, and try again.|Datenbank belegt. Änderungen in DB Browser abschließen/verwerfen, schließen und erneut versuchen.|Az adatbázis foglalt. Mentsd/vesd el a DB Browser módosításait, zárd be, és próbáld újra.
Choose a valid device type.|Gültigen Gerätetyp wählen.|Válassz érvényes eszköztípust.
That device ID already exists. Choose another ID.|Diese Gerätekennung existiert bereits. Andere Kennung wählen.|Ez az eszközazonosító már létezik. Válassz másikat.
Existing device IDs cannot be changed in this form.|Bestehende Gerätekennungen sind hier nicht änderbar.|Meglévő eszközazonosító itt nem változtatható.
This device changed outside the form. Cancel and refresh before editing again.|Gerät wurde außerhalb geändert. Verwerfen und vor erneutem Bearbeiten aktualisieren.|Az eszköz kívülről változott. Vesd el és frissítsd új szerkesztés előtt.
Connectivity changed outside the form. Cancel and refresh before editing again.|Verbindungsdaten wurden außerhalb geändert. Verwerfen und aktualisieren.|A kapcsolati adatok kívülről változtak. Vesd el és frissítsd új szerkesztés előtt.
Enter both purchase price and currency, or leave both unknown.|Kaufpreis und Währung zusammen angeben oder beide unbekannt lassen.|Árat és pénznemet együtt adj meg, vagy mindkettő legyen ismeretlen.
Price: use a non-negative amount with a decimal point, for example 129.90.|Preis: nichtnegativen Betrag mit Dezimalpunkt eingeben, z. B. 129.90.|Ár: nem negatív összeg tizedesponttal, például 129.90.
Currency: use three uppercase letters, for example EUR or HUF.|Währung: drei Großbuchstaben, z. B. EUR oder HUF.|Pénznem: három nagybetű, például EUR vagy HUF.
Device ID: use letters, digits, dots, underscores or hyphens; begin with a letter or digit.|Gerätekennung: Buchstaben, Ziffern, Punkt, Unter-/Bindestrich; Beginn mit Buchstabe/Ziffer.|Azonosító: betű, szám, pont, aláhúzás vagy kötőjel; betűvel/számmal kezdődjön.
Photo information source is required.|Quelle für das Foto erforderlich.|Fotóforrás megadása kötelező.
Choose a JPEG or PNG file up to 25 MiB.|JPEG/PNG-Datei bis 25 MiB wählen.|Válassz legfeljebb 25 MiB JPEG/PNG fájlt.
Supported photo formats: JPEG and PNG.|Unterstützte Fotoformate: JPEG und PNG.|Támogatott fotóformátum: JPEG és PNG.
Choose an image up to 16 megapixels; export a smaller copy if needed.|Bild bis 16 Megapixel wählen, gegebenenfalls kleinere Kopie exportieren.|Legfeljebb 16 megapixeles kép; szükség esetén kisebb másolatot exportálj.
Both type name and group are required.|Typname und Gruppe erforderlich.|Típusnév és csoport kötelező.
A choice name is required.|Auswahlname erforderlich.|Választási név megadása kötelező.
Type changed outside this dialog; reopen it.|Typ wurde außerhalb geändert; Dialog erneut öffnen.|A típus kívülről változott; nyisd újra az ablakot.
Choice changed outside the dialog; reopen it.|Auswahl wurde außerhalb geändert; Dialog erneut öffnen.|A választási érték kívülről változott; nyisd újra az ablakot.
Choose unknown, none or recorded for connectivity status.|Verbindungsstatus unbekannt, keine oder erfasst wählen.|Kapcsolati állapot: ismeretlen, nincs vagy rögzített.
An in-use choice must also be marked supported.|Verwendete Auswahl muss auch unterstützt sein.|Használt választásnak támogatottnak is kell lennie.
No supported capabilities means no capabilities in use.|Ohne unterstützte Fähigkeiten keine verwendeten Fähigkeiten.|Ha nincs támogatott képesség, használt képesség sem lehet.
Connectivity assessment date must be a valid calendar date.|Bewertungsdatum muss ein gültiges Kalenderdatum sein.|Az értékelés dátuma érvényes naptári dátum legyen.
Unsupported schema version|Nicht unterstützte Schemaversion|Nem támogatott sémaverzió
'''.splitlines():
    if line:en,de,hu=line.split('|');add(en,de,hu)
add('Add types or rename/move an existing type. Changes apply to every device using that type. Names are stored in lowercase.','Typen ergänzen oder umbenennen/verschieben. Änderungen gelten für alle zugeordneten Geräte. Namen werden kleingeschrieben.','Típus felvétele, átnevezése vagy átcsoportosítása. Minden hozzárendelt eszközt érint. A nevek kisbetűsek.')
add('Renaming a shared choice updates every device using it. No interface-to-protocol compatibility is inferred.','Umbenennen ändert die Auswahl für alle Geräte. Keine Schnittstellen-/Protokollkompatibilität wird abgeleitet.','Közös érték átnevezése minden érintett eszközt frissít. Nem következtetünk interfész/protokoll-kompatibilitásra.')
add('Choose recorded below to tick multiple choices. In use implies supported. Recorded choices need not be an exhaustive capability list.','Unten erfasst wählen, um mehrere Werte anzukreuzen. Verwendet bedeutet unterstützt. Die Liste muss nicht vollständig sein.','Több jelöléshez válaszd az alább rögzítve állapotot. Használt egyben támogatott. A lista nem feltétlen teljes.')
add('Uncheck Known to keep a date unknown. No date is saved automatically.\n* Required fields. Group follows the selected type; choose a type to save a classification.\nExisting IDs stay fixed; components and facts use the existing tool.','Bekannt abwählen für unbekannte Daten; kein Datum wird automatisch gespeichert.\n* Pflichtfelder. Gruppe folgt dem gewählten Typ.\nKennungen bleiben fest; Komponenten/Angaben über vorhandenes Werkzeug.','Kapcsold ki az Ismert jelölést ismeretlen dátumhoz; nincs automatikus dátummentés.\n* Kötelező mezők. A csoportot a kiválasztott típus határozza meg.\nAzonosító rögzített; alkatrészek/egyedi adatok a meglévő eszközzel.')
add('JPEG / PNG • up to 25 MiB and 16 megapixels. Attachments save immediately. Double-click to open.','JPEG / PNG • bis 25 MiB und 16 Megapixel. Anhänge werden sofort gespeichert. Doppelklick zum Öffnen.','JPEG / PNG • legfeljebb 25 MiB és 16 megapixel. Melléklet azonnal mentődik. Dupla kattintással megnyitás.')
add('Remove this attachment from the device? Files remain on disk to support older backups.','Fotozuordnung entfernen? Dateien bleiben für ältere Sicherungen erhalten.','Leválasztod ezt a fotót? Fájlok régebbi mentésekhez megmaradnak.')
add('Application version, data location, license and backup information.','Programmversion, Speicherorte, Lizenz und Sicherungshinweise.','Verzió, adattárolási hely, licenc és mentési információk.')
add('Information source is required for {0} connectivity.','Informationsquelle für {0}-Verbindungen erforderlich.','A(z) {0} kapcsolati részhez forrás szükséges.')
add('{0}: choose a valid calendar date.','{0}: gültiges Kalenderdatum wählen.','{0}: válassz érvényes naptári dátumot.')
add('{0}: recorded needs at least one {1} choice; unknown/none must have no choices.','{0}: Erfasst benötigt mindestens eine Auswahl für {1}; unbekannt/keine dürfen keine Auswahl haben.','{0}: rögzítve esetén legalább egy {1} választás kell; ismeretlen/nincs mellett nem lehet jelölés.')
add('Unknown {0} choice; refresh the lists.','Unbekannte Auswahl für {0}; Listen aktualisieren.','Ismeretlen {0} érték; frissítsd a listát.')
add('interface','Schnittstelle','interfész')
add('protocol','Protokoll','protokoll')
add('supported','unterstützt','támogatott')
add('in use','verwendet','használt')
add('Could not save thumbnail','Vorschaubild konnte nicht gespeichert werden','A bélyegkép nem menthető')
add('Could not decode this image: {0}','Bild konnte nicht dekodiert werden: {0}','A kép nem dekódolható: {0}')
add('Source image changed while importing; please retry.','Quelldatei während Import verändert; erneut versuchen.','A forráskép import közben megváltozott; próbáld újra.')
add('Duplicate connectivity selection.','Doppelte Verbindungsauswahl.','Ismételt kapcsolati választás.')
for line in '''awaiting installation|wartet auf Installation|telepítésre vár
in use|in Betrieb|használatban
spare|Reserve|tartalék
in storage|eingelagert|raktáron
under assessment|in Prüfung|vizsgálat alatt
under repair|in Reparatur|javítás alatt
retired|außer Betrieb genommen|használatból kivonva
sold|verkauft|eladva
given away|verschenkt|elajándékozva
returned|zurückgegeben|visszaadva
lost|verloren|elveszett
stolen|gestohlen|ellopták
scrapped|entsorgt|leselejtezve
working|funktionsfähig|működő
partially working|teilweise funktionsfähig|részben működő
faulty|defekt|hibás
untested|ungeprüft|nem tesztelt'''.splitlines():
    en,de,hu=line.split('|');add(en,de.lower(),hu)
for line in '''Software|Software|Szoftver
Operating system|Betriebssystem|Operációs rendszer
OS family|Betriebssystemfamilie|OS-család
OS name / distribution|Betriebssystemname / Distribution|OS neve / disztribúció
OS version|Betriebssystemversion|OS-verzió
Firmware|Firmware|Firmware
Firmware version|Firmwareversion|Firmware-verzió
Checked on|Geprüft am|Ellenőrzés dátuma
not applicable|nicht zutreffend|nem alkalmazható
recorded|erfasst|rögzítve
For example: arch linux, debian or proxmox ve|Zum Beispiel: arch linux, debian oder proxmox ve|Például: arch linux, debian vagy proxmox ve
Exact installed version, if known|Genaue installierte Version, falls bekannt|Pontos telepített verzió, ha ismert
Exact installed firmware version, if known|Genaue installierte Firmwareversion, falls bekannt|Pontos telepített firmware-verzió, ha ismert
For example: system settings, command output or management interface|Zum Beispiel: Systemeinstellungen, Befehlsausgabe oder Verwaltungsoberfläche|Például: rendszerbeállítás, parancskimenet vagy kezelőfelület
One current OS per device. Unknown is different from not applicable. Firmware can be recorded independently.|Ein aktuelles Betriebssystem pro Gerät. Unbekannt ist nicht nicht zutreffend. Firmware separat erfassbar.|Eszközönként egy jelenlegi OS. Ismeretlen nem azonos a nem alkalmazhatóval. Firmware külön rögzíthető.
Current operating system and firmware assessments, with evidence and checked date.|Aktuelles Betriebssystem und Firmware mit Quelle und Prüfdatum.|Jelenlegi operációs rendszer és firmware, forrással és ellenőrzési dátummal.
Search devices, software, interfaces or protocols…|Geräte, Software, Schnittstellen oder Protokolle suchen…|Eszköz, szoftver, interfész vagy protokoll keresése…
Choose unknown, not applicable or recorded for software status.|Softwarestatus unbekannt, nicht zutreffend oder erfasst wählen.|Szoftverállapot: ismeretlen, nem alkalmazható vagy rögzítve.
Recorded OS needs a family or OS name.|Erfasstes Betriebssystem benötigt Familie oder Namen.|Rögzített OS-hez család vagy OS-név kell.
Choose a valid OS family.|Gültige Betriebssystemfamilie wählen.|Válassz érvényes OS-családot.
Unknown or not applicable OS cannot have OS details.|Unbekanntes/nicht zutreffendes Betriebssystem darf keine Details enthalten.|Ismeretlen/nem alkalmazható OS nem tartalmazhat OS-részleteket.
Recorded firmware needs a version.|Erfasste Firmware benötigt eine Version.|Rögzített firmware-hez verzió kell.
Unknown or not applicable firmware cannot have a version.|Unbekannte/nicht zutreffende Firmware darf keine Version enthalten.|Ismeretlen/nem alkalmazható firmware nem tartalmazhat verziót.
Information source is required for known software or not applicable status.|Quelle für bekannte Software oder nicht zutreffenden Status erforderlich.|Ismert szoftverhez vagy nem alkalmazható állapothoz forrás kötelező.
Software checked date must be a valid calendar date.|Software-Prüfdatum muss gültiges Kalenderdatum sein.|Szoftverellenőrzés dátuma érvényes naptári dátum legyen.
Software changed outside the form. Cancel and refresh before editing again.|Software wurde außerhalb geändert. Verwerfen und vor Bearbeitung aktualisieren.|A szoftveradat kívülről változott. Vesd el és frissítsd új szerkesztés előtt.'''.splitlines():
    en,de,hu=line.split('|');add(en,de,hu)
for line in '''Manuals and references|Handbücher und Verweise|Kézikönyvek és hivatkozások
Manual folder|Handbuchordner|Kézikönyvmappa
Add reference…|Verweis hinzufügen…|Hivatkozás hozzáadása…
Edit reference…|Verweis bearbeiten…|Hivatkozás szerkesztése…
Open reference|Verweis öffnen|Hivatkozás megnyitása
Detach reference|Verweis entfernen|Hivatkozás leválasztása
Add manual reference|Handbuchverweis hinzufügen|Kézikönyvhivatkozás hozzáadása
Edit manual reference|Handbuchverweis bearbeiten|Kézikönyvhivatkozás szerkesztése
Reference kind|Verweisart|Hivatkozás típusa
Online link|Online-Link|Online hivatkozás
Local PDF|Lokale PDF|Helyi PDF
Title *|Titel *|Cím *
Online URL|Online-URL|Online URL
Language code|Sprachcode|Nyelvkód
Edition / version|Ausgabe / Version|Kiadás / verzió
Applicable model|Passendes Modell|Érintett modell
Notes|Notizen|Megjegyzés
Local file|Lokale Datei|Helyi fájl
Choose PDF…|PDF auswählen…|PDF kiválasztása…
Choose local manual|Lokales Handbuch auswählen|Helyi kézikönyv kiválasztása
PDF documents (*.pdf)|PDF-Dokumente (*.pdf)|PDF-dokumentumok (*.pdf)
Save a device before adding references.|Vor dem Hinzufügen von Verweisen ein Gerät speichern.|Hivatkozás hozzáadása előtt mentsd az eszközt.
Multiple online links or local PDFs. References save immediately. Double-click to open.|Mehrere Online-Links/lokale PDFs. Verweise sofort gespeichert. Doppelklick öffnet.|Több online link vagy helyi PDF. Hivatkozás azonnal mentődik. Dupla kattintás megnyitja.
References save immediately. Online links are opened only on request; no document is downloaded automatically. Local PDFs are copied into managed storage.|Verweise sofort gespeichert. Links nur auf Anforderung geöffnet, keine automatischen Downloads. Lokale PDFs werden kopiert.|Hivatkozás azonnal mentődik. Link csak kérésre nyílik, nincs automatikus letöltés. Helyi PDF kezelt tárolóba másolódik.
Manual reference saved. Full backup includes attached local PDFs.|Handbuchverweis gespeichert. Vollständige Sicherung enthält lokale PDFs.|Kézikönyvhivatkozás mentve. Teljes mentés a csatolt helyi PDF-eket is tartalmazza.
Manual reference saved.|Handbuchverweis gespeichert.|Kézikönyvhivatkozás mentve.
Could not save manual reference|Handbuchverweis konnte nicht gespeichert werden|Kézikönyvhivatkozás nem menthető
Save or cancel device changes before editing manual references.|Geräteänderungen vor dem Bearbeiten von Verweisen speichern/verwerfen.|Kézikönyvhivatkozás szerkesztése előtt mentsd/vesd el az eszközváltozásokat.
Detach manual reference|Handbuchverweis entfernen|Kézikönyvhivatkozás leválasztása
Remove this reference? Managed local files remain for older backups.|Verweis entfernen? Lokale Dateien bleiben für ältere Sicherungen erhalten.|Leválasztod a hivatkozást? Kezelt helyi fájl régi mentésekhez megmarad.
Reference detached; managed files retained.|Verweis entfernt; verwaltete Dateien bleiben.|Hivatkozás leválasztva; kezelt fájlok megmaradtak.
Manual file is missing or changed. Restore it from a full backup.|Handbuchdatei fehlt/verändert. Aus vollständiger Sicherung wiederherstellen.|Kézikönyvfájl hiányzik vagy változott. Állítsd vissza teljes mentésből.
Could not open the reference. Check your browser or PDF file association.|Verweis nicht geöffnet. Browser/PDF-Dateizuordnung prüfen.|Hivatkozás nem nyitható. Ellenőrizd a böngésző/PDF-fájltársítást.
Manual title and information source are required.|Handbuchtitel und Quelle erforderlich.|Kézikönyvcím és forrás kötelező.
Enter a complete HTTP or HTTPS URL without spaces.|Vollständige HTTP-/HTTPS-URL ohne Leerzeichen eingeben.|Teljes HTTP/HTTPS URL szóköz nélkül szükséges.
Use an HTTP or HTTPS URL with a host and without embedded credentials.|HTTP-/HTTPS-URL mit Host ohne eingebettete Zugangsdaten verwenden.|HTTP/HTTPS URL gazdanévvel, beágyazott hitelesítő adatok nélkül.
Use a language code such as en, de, hu or en-GB; leave unknown blank.|Sprachcode wie en, de, hu, en-GB; unbekannt leer lassen.|Nyelvkód pl. en, de, hu vagy en-GB; ismeretlen üresen.
Choose an online link or local PDF.|Online-Link oder lokale PDF wählen.|Online link vagy helyi PDF választása.
An online reference needs a URL.|Online-Verweis benötigt URL.|Online hivatkozáshoz URL kell.
Choose a local PDF file.|Lokale PDF-Datei wählen.|Válassz helyi PDF-fájlt.
Choose a PDF file up to 100 MiB.|PDF-Datei bis 100 MiB wählen.|Legfeljebb 100 MiB PDF-fájl választható.
This file does not have a PDF header.|Datei hat keinen PDF-Kopf.|A fájlnak nincs PDF-fejléce.
Manual changed during import; please retry.|Handbuch während Import geändert; erneut versuchen.|Kézikönyv import közben megváltozott; próbáld újra.
Manual reference changed outside this dialog; refresh and try again.|Handbuchverweis außerhalb geändert; aktualisieren und erneut versuchen.|Kézikönyvhivatkozás kívülről változott; frissítsd és próbáld újra.
en, de, hu, fr…; leave blank if unknown|en, de, hu, fr…; unbekannt leer lassen|en, de, hu, fr…; ismeretlen üresen
Exact document edition or version, if known|Genaue Ausgabe/Version, falls bekannt|Pontos dokumentumkiadás/verzió, ha ismert
Model(s) this document applies to, if known|Passende Modelle, falls bekannt|Érintett modell(ek), ha ismertek
For example: manufacturer website or document supplied with the device|Zum Beispiel: Herstellerwebsite oder mitgeliefertes Dokument|Például: gyártói weboldal vagy eszközhöz kapott dokumentum
Full backup includes the database, attached photos and local manuals. Automatic snapshots contain only the database.|Vollständige Sicherung enthält Datenbank, Fotos und lokale Handbücher. Automatische Sicherungen enthalten nur Datenbank.|Teljes mentés adatbázist, fotókat és helyi kézikönyveket tartalmaz. Automatikus pillanatkép csak adatbázist ment.'''.splitlines():
    en,de,hu=line.split('|');add(en,de,hu)

add('Generated automatically when saved','Beim Speichern automatisch erzeugt','Mentéskor automatikusan létrejön')
add('Example: backup-server-office-01','Beispiel: backup-server-office-01','Példa: backup-server-office-01')
add('That device name already exists. Add a distinguishing location or number.','Dieser Gerätename existiert bereits. Einen unterscheidenden Ort oder eine Nummer ergänzen.','Ez az eszköznév már létezik. Adj hozzá megkülönböztető helyet vagy sorszámot.')

add('Short ID','Kurz-ID','Rövid azonosító')
add('Stable short label for this inventory. The full ID remains the permanent reference.','Dauerhafte Kurzkennung dieses Inventars. Die vollständige ID bleibt die technische Referenz.','Állandó rövid leltári címke. A teljes ID marad a technikai hivatkozás.')
add('Recommended source; missing information warns but does not block saving','Quelle empfohlen; fehlende Angabe warnt, verhindert Speichern nicht','Forrás javasolt; hiánya figyelmeztet, de nem akadályozza a mentést')
add('Warning: connectivity source is missing. Saving is allowed.','Warnung: Verbindungsquelle fehlt. Speichern ist möglich.','Figyelem: kapcsolati forrás hiányzik. Mentés engedélyezett.')
add('Save your changes before continuing?','Änderungen vor dem Fortfahren speichern?','Mented a változásokat a folytatás előtt?')

add('Find installed versions…','Installierte Versionen finden…','Telepített verziók megkeresése…')
add('Installed OS and firmware versions','Installierte Betriebssystem- und Firmwareversionen','Telepített OS- és firmware-verziók')
add('For pfSense, open Dashboard → System Information: Version shows pfSense and its underlying FreeBSD version. BIOS may show the installed BIOS vendor/version/date. If absent, read it in BIOS setup. Choose Firmware: recorded to enter the exact installed BIOS/UEFI version. A manufacturer download is not proof of the installed version. SSD firmware needs a reading from that disk. Leave unavailable values unknown.','In pfSense Dashboard → System Information öffnen: Version zeigt pfSense und die FreeBSD-Basisversion. BIOS kann Hersteller/Version/Datum des installierten BIOS anzeigen. Falls nicht, im BIOS-Setup ablesen. Firmware: erfasst wählen, um die genaue installierte BIOS-/UEFI-Version einzutragen. Herstellerdownload beweist keine installierte Version. SSD-Firmware am Laufwerk ablesen. Fehlende Werte unbekannt lassen.','pfSense: Dashboard → System Information. Version alatt pfSense és az alap FreeBSD verziója látható. BIOS megmutathatja a telepített BIOS gyártóját/verzióját/dátumát; ha nem, a BIOS-beállításban olvasd le. Firmware: rögzítve választással írd be a tényleges BIOS/UEFI-verziót. Gyártói letöltés nem bizonyít telepített verziót. SSD-firmware az adott lemezről olvasható le. Hiányzó érték maradjon ismeretlen.')

add('Apply update','Update anwenden','Frissítés alkalmazása')
add('Save or discard edits, then restart into the tested update. A database write lock defers migration.','Änderungen speichern/verwerfen, dann getestetes Update neu starten. Eine Datenbank-Schreibsperre verschiebt die Migration.','Változások mentése/eldobása, majd újraindítás az ellenőrzött frissítéssel. Adatbázis-írászár halasztja a migrációt.')
add('Update deferred. Finish open database transactions, then retry Apply update.','Update verschoben. Offene Datenbanktransaktionen abschließen, dann Update anwenden erneut versuchen.','Frissítés halasztva. Fejezd be a nyitott adatbázis-tranzakciókat, majd próbáld újra a Frissítés alkalmazását.')
add('Finish the current dialog','Aktuellen Dialog abschließen','Fejezd be az aktuális párbeszédablakot')
add('Save or cancel the open dialog before applying the update.','Offenen Dialog vor Update speichern oder abbrechen.','Frissítés előtt mentsd vagy szakítsd meg a nyitott párbeszédablakot.')

add('Check for local updates','Lokale Updates prüfen','Helyi frissítések keresése')
add('Use launch-desktop.sh for managed updates.','Für verwaltete Updates launch-desktop.sh verwenden.','Kezelt frissítéshez a launch-desktop.sh indítót használd.')
add('No newer published local release.','Keine neuere veröffentlichte lokale Version.','Nincs újabb közzétett helyi kiadás.')
add('A tested local update is ready. Use Apply update when convenient.','Ein getestetes lokales Update ist bereit. Bei Gelegenheit Update anwenden wählen.','Ellenőrzött helyi frissítés kész. Alkalmas időben válaszd a Frissítés alkalmazását.')

add('Type code','Typcode','Típuskód')
add('Two-letter code; automatic if blank','Zweistelliger Buchstabencode; leer = automatisch','Kétbetűs kód; üresen automatikus')
add('Choose an unused two-letter uppercase type code.','Unbenutzten Typcode aus zwei Großbuchstaben wählen.','Válassz még nem használt két nagybetűs típuskódot.')
add('No unused two-letter type code remains.','Kein freier zweistelliger Typcode mehr vorhanden.','Nincs több szabad kétbetűs típuskód.')
add('Two-letter type code and five random digits. Reclassification gives a new label; old labels still resolve to this full ID.','Zwei Typbuchstaben und fünf Zufallsziffern. Neue Klassifikation erzeugt neues Kürzel; alte Kürzel verweisen weiter auf dieselbe vollständige ID.','Két típuskódbetű és öt véletlen számjegy. Átsorolás új címkét ad; régi címke továbbra is a teljes ID-ra mutat.')

for row in '''Network identity|Netzwerkidentität|Hálózati azonosítók
Hostname|Hostname|Gépnév
Unknown, or actual hostname / FQDN|Unbekannt oder tatsächlicher Hostname / FQDN|Ismeretlen vagy tényleges gépnév / FQDN
Interface / port|Schnittstelle / Port|Interfész / port
MAC address|MAC-Adresse|MAC-cím
IP addresses|IP-Adressen|IP-címek
Add interface|Schnittstelle hinzufügen|Interfész hozzáadása
Remove interface|Schnittstelle entfernen|Interfész eltávolítása
Recommended: device settings or your observation|Empfohlen: Geräteeinstellungen oder eigene Beobachtung|Javasolt: eszközbeállítás vagy saját megfigyelés
Observed on|Beobachtet am|Megfigyelés dátuma
Evidence status|Belegstatus|Bizonyíték állapota
user_reported|Nutzerangabe|felhasználói közlés
verified|geprüft|ellenőrzött
uncertain|unsicher|bizonytalan
No duplicate name found.|Kein doppelter Name gefunden.|Nem találtunk azonos nevet.
Name must be at most 100 characters.|Name darf höchstens 100 Zeichen lang sein.|A név legfeljebb 100 karakter lehet.
Name cannot contain control characters or line breaks.|Name darf keine Steuerzeichen oder Zeilenumbrüche enthalten.|A név nem tartalmazhat vezérlőkaraktert vagy sortörést.
Name check is unavailable; Save will validate again.|Namensprüfung nicht verfügbar; Speichern prüft erneut.|Névellenőrzés nem elérhető; mentéskor ismét ellenőrizzük.
Network details changed outside the form. Cancel and refresh before editing again.|Netzwerkdaten wurden außerhalb geändert. Abbrechen und neu laden.|Hálózati adatok kívülről változtak. Mégse, majd frissítés szükséges.
Warning: network information source is missing. Saving unverified details is allowed.|Warnung: Netzwerkquelle fehlt. Ungeprüfte Angaben dürfen gespeichert werden.|Figyelem: hálózati forrás hiányzik. Nem ellenőrzött adat menthető.
Verified network details need an evidence source and observation date.|Geprüfte Netzwerkangaben brauchen Quelle und Beobachtungsdatum.|Ellenőrzött hálózati adathoz forrás és megfigyelési dátum kell.
Each interface needs a label of 1–100 characters, for example igc0 or WAN.|Jede Schnittstelle braucht 1–100 Zeichen als Bezeichnung, etwa igc0 oder WAN.|Minden interfésznek 1–100 karakteres címke kell, például igc0 vagy WAN.
Interface labels must be unique within this device.|Schnittstellenbezeichnungen müssen im Gerät eindeutig sein.|Interfészcímke az eszközön belül egyedi legyen.
Do not repeat an IP address within the same interface.|IP-Adresse innerhalb einer Schnittstelle nicht doppelt eintragen.|Egy interfészen belül ne ismételd az IP-címet.
MAC address cannot be all zeros or the broadcast address.|MAC-Adresse darf weder nur Nullen noch Broadcastadresse sein.|MAC-cím nem lehet csupa nulla vagy szórási cím.
Enter IP addresses in an interface row, not in Hostname.|IP-Adressen in Schnittstellenzeile, nicht unter Hostname eintragen.|IP-címet interfészsorba írj, ne a gépnévhez.
Hostname: use valid DNS labels with letters, digits and hyphens.|Hostname: gültige DNS-Teile mit Buchstaben, Ziffern und Bindestrichen verwenden.|Gépnév: érvényes DNS-részek betűkkel, számokkal és kötőjellel.
MAC address: enter six hexadecimal octets, for example 02:00:00:00:00:01, or leave unknown blank.|MAC-Adresse: sechs hexadezimale Oktette, etwa 02:00:00:00:00:01; unbekannt leer lassen.|MAC-cím: hat hexadecimális oktett, például 02:00:00:00:00:01; ismeretlennél üres.
Enter a valid IPv4/IPv6 address, optionally with /prefix; the interface row identifies its scope.|Gültige IPv4-/IPv6-Adresse, optional /Präfix; Schnittstellenzeile bestimmt den Geltungsbereich.|Érvényes IPv4/IPv6-cím, opcionális /prefix; hatókört az interfészsor adja.
Choose a valid network evidence status.|Gültigen Netzwerk-Belegstatus wählen.|Válassz érvényes hálózati bizonyítékállapotot.
Network observation date must be a valid calendar date.|Netzwerk-Beobachtungsdatum muss gültig sein.|Hálózati megfigyelési dátum érvényes naptári dátum legyen.
Invalid or repeated network interface identity.|Ungültige oder doppelte Schnittstellenkennung.|Érvénytelen vagy ismételt interfészazonosító.'''.splitlines():
    add(*row.split('|'))
add('Separate from the descriptive inventory name. DNS labels use letters, digits and hyphens; IDNs are stored as ASCII IDNA. No DNS lookup is performed.','Vom beschreibenden Inventarnamen getrennt. DNS-Teile nutzen Buchstaben, Ziffern, Bindestriche; IDN wird als ASCII-IDNA gespeichert. Keine DNS-Abfrage.','A leíró leltárnévtől különálló. DNS-részek betű/szám/kötőjel; IDN ASCII-IDNA formában tárolva. Nincs DNS-lekérdezés.')
add('One row per interface, for example igc0 or WAN. MAC may be unknown. Enter multiple IPv4/IPv6 addresses separated by commas; optional /prefix is allowed. Same IP on different interfaces is allowed.','Eine Zeile pro Schnittstelle, etwa igc0 oder WAN. MAC darf unbekannt sein. Mehrere IPv4-/IPv6-Adressen mit Komma, optional /Präfix. Gleiche IP auf verschiedenen Schnittstellen erlaubt.','Interfészenként egy sor, például igc0 vagy WAN. MAC lehet ismeretlen. Több IPv4/IPv6-cím vesszővel, opcionális /prefix. Más interfészeken azonos IP megengedett.')
add('Verified means you checked the actual values; it requires a source and observation date. Saving does not independently verify the device.','Geprüft bedeutet tatsächliche Werte geprüft; Quelle und Datum erforderlich. Speichern prüft das Gerät nicht selbst.','Ellenőrzött: tényleges értékeket ellenőrizted, forrás és dátum szükséges. Mentés nem ellenőrzi önállóan az eszközt.')
add('Optional values stay unknown. Network edits save with Save device; previous saved assessments remain in the observation history.','Optionale Werte bleiben unbekannt. Netzwerkänderungen mit Gerät speichern sichern; frühere Bewertungen bleiben im Beobachtungsverlauf.','Opcionális adat ismeretlen marad. Hálózati szerkesztés Eszköz mentésével rögzül; korábbi mentett értékelés megmarad az előzményekben.')

# HWI4U 0.8: clear actions, compact sections and purchase location.
for line in '''hardware inventory database client|Hardwareinventar-Datenbankclient|hardverleltár-adatbáziskliens
About HWI4U|Über HWI4U|A HWI4U névjegye
About HWI4U…|Über HWI4U…|A HWI4U névjegye…
Purchased at|Gekauft bei|Vásárlás helye
Shop, marketplace or seller. Optional text; spelling suggestions never change it automatically.|Shop, Marktplatz oder Verkäufer. Optionaler Text; Schreibvorschläge ändern ihn niemals automatisch.|Bolt, piactér vagy eladó. Nem kötelező; a helyesírási javaslat nem módosítja automatikusan.
Suggested spelling: |Schreibvorschlag: |Javasolt írásmód: 
Use suggested spelling|Schreibvorschlag übernehmen|Javasolt írásmód használata
Save changes|Änderungen speichern|Módosítások mentése
Discard unsaved changes|Ungespeicherte Änderungen verwerfen|Nem mentett módosítások elvetése
Keep editing|Weiter bearbeiten|Szerkesztés folytatása
Save writes the form to the database. Discard leaves the saved database record unchanged. Keep editing returns to the form.|Speichern schreibt das Formular in die Datenbank. Verwerfen lässt den gespeicherten Datensatz unverändert. Weiter bearbeiten kehrt zum Formular zurück.|A mentés az adatbázisba írja az űrlapot. Az elvetés nem módosítja a mentett rekordot. A szerkesztés folytatása visszatér az űrlaphoz.
Write these device changes to the database, then continue.|Diese Geräteänderungen in die Datenbank schreiben und fortfahren.|Az eszköz módosításainak mentése az adatbázisba, majd továbblépés.
Ignore changes in this form. Do not delete the saved device.|Änderungen in diesem Formular ignorieren. Das gespeicherte Gerät wird nicht gelöscht.|Az űrlap módosításainak elvetése. A mentett eszköz nem törlődik.
Return to the form without saving or discarding changes.|Zum Formular zurückkehren, ohne Änderungen zu speichern oder zu verwerfen.|Visszatérés az űrlaphoz mentés és elvetés nélkül.
Delete device…|Gerät löschen…|Eszköz törlése…
Delete device|Gerät löschen|Eszköz törlése
Select a saved device first.|Zuerst ein gespeichertes Gerät auswählen.|Előbb válassz egy mentett eszközt.
Delete this device?|Dieses Gerät löschen?|Törlöd ezt az eszközt?
Keep device|Gerät behalten|Eszköz megtartása
Device deleted. Full backup: |Gerät gelöscht. Vollständige Sicherung: |Eszköz törölve. Teljes mentés: 
A verified full backup is required. Device facts, attachments, network details and assembly links will be removed from current records. Other devices remain. A deletion history and reserved IDs are retained; local attachment files remain on disk.|Eine geprüfte vollständige Sicherung ist erforderlich. Gerätefakten, Anhänge, Netzwerkdaten und Baugruppenverknüpfungen werden aus den aktuellen Datensätzen entfernt. Andere Geräte bleiben erhalten. Löschhistorie und reservierte Kennungen sowie lokale Anhangdateien bleiben erhalten.|Ellenőrzött teljes mentés szükséges. Az eszköz adatai, mellékletei, hálózati adatai és szerelési kapcsolatai törlődnek az aktuális rekordokból. Más eszközök megmaradnak. A törlési előzmény, a fenntartott azonosítók és a helyi mellékletfájlok megmaradnak.'''.splitlines():
    en,de,hu=line.split('|');add(en,de,hu)

for line in '''TEST ENVIRONMENT — changes affect only the test copy.|TESTUMGEBUNG — Änderungen betreffen nur die Testkopie.|TESZTKÖRNYEZET — a módosítások csak a tesztmásolatot érintik.
Environment|Umgebung|Környezet
Refresh test data|Testdaten erneuern|Tesztadatok frissítése
Accept tested release|Getestete Version freigeben|Tesztelt kiadás elfogadása
Working…|Wird ausgeführt…|Folyamatban…
Completed: |Abgeschlossen: |Elkészült: 
Close|Schließen|Bezárás
Refresh test data from production? Current test edits will be replaced by a new copy. The previous test copy is retained. Production is unchanged. Finish the TEST session first.|Testdaten aus der Produktion erneuern? Aktuelle Teständerungen werden durch eine neue Kopie ersetzt. Die vorherige Testkopie bleibt erhalten. Produktion bleibt unverändert. Zuerst die TEST-Sitzung beenden.|Frissíted a tesztadatokat az éles rendszerből? A jelenlegi tesztmódosításokat új másolat váltja fel. A korábbi tesztmásolat megmarad. Az éles rendszer változatlan. Előbb fejezd be a TESZT munkamenetet.
Accept this tested release for production? Only software and migrations are promoted. Test records are never copied back. Production applies the update through Apply update.|Diese getestete Version für die Produktion freigeben? Nur Software und Migrationen werden übernommen. Testdatensätze werden niemals zurückkopiert. Produktion übernimmt das Update über Update anwenden.|Elfogadod ezt a tesztelt kiadást az éles rendszerhez? Csak a szoftver és a migrációk kerülnek át. Tesztrekordok soha nem másolódnak vissza. Az éles rendszerben a Frissítés alkalmazása telepíti a frissítést.'''.splitlines():
    en,de,hu=line.split('|');add(en,de,hu)

for line in '''Open production client|Produktivclient öffnen|Éles kliens megnyitása
Open test client|Testclient öffnen|Tesztkliens megnyitása
Open the other client in a separate window. Unsaved edits stay in this window; no data is copied.|Anderen Client in einem separaten Fenster öffnen. Ungespeicherte Eingaben bleiben hier; keine Daten werden kopiert.|A másik kliens megnyitása külön ablakban. A nem mentett bevitel itt marad; adat nem másolódik.
Could not open client|Client konnte nicht geöffnet werden|A kliens nem nyitható meg
Could not open the other client.|Der andere Client konnte nicht geöffnet werden.|A másik kliens nem nyitható meg.
The other client opened in a separate window. Unsaved changes remain here.|Der andere Client wurde in einem separaten Fenster geöffnet. Ungespeicherte Änderungen bleiben hier.|A másik kliens külön ablakban megnyílt. A nem mentett módosítások itt maradnak.'''.splitlines():
    en,de,hu=line.split('|');add(en,de,hu)

add('Abort','Abbrechen','Megszakítás')
add('Postpone this update. Keep the current client and all unsaved edits.','Dieses Update aufschieben. Aktuellen Client und alle ungespeicherten Eingaben behalten.','A frissítés elhalasztása. Az aktuális kliens és minden nem mentett bevitel megmarad.')
add('Update postponed. Your unsaved changes are kept.','Update aufgeschoben. Ihre ungespeicherten Änderungen bleiben erhalten.','A frissítés elhalasztva. A nem mentett módosítások megmaradnak.')

for line in '''Sources and evidence|Quellen und Belege|Források és bizonyítékok
Information source / notes|Informationsquelle / Notizen|Információforrás / megjegyzések
No sources selected|Keine Quellen ausgewählt|Nincs kiválasztott forrás
Choose sources…|Quellen auswählen…|Források kiválasztása…
Select several existing sources or add evidence. Source assignments save together with this device.|Mehrere vorhandene Quellen wählen oder Belege ergänzen. Zuordnungen werden mit dem Gerät gespeichert.|Válassz több meglévő forrást vagy adj hozzá bizonyítékot. A hozzárendelések az eszközzel együtt mentődnek.
Website|Webseite|Weboldal
Document (PDF)|Dokument (PDF)|Dokumentum (PDF)
Photo|Foto|Fénykép
Observation|Beobachtung|Megfigyelés
Source observation|Quellenbeobachtung|Forrásmegfigyelés
Add source|Quelle hinzufügen|Forrás hozzáadása
Revise source|Quelle überarbeiten|Forrás módosított változata
Source kind|Quellenart|Forrás típusa
Observation / notes|Beobachtung / Notizen|Megfigyelés / megjegyzések
Origin / provenance|Herkunft|Eredet
Observed / accessed on|Beobachtet / abgerufen am|Megfigyelés / hozzáférés dátuma
Verification status|Prüfstatus|Ellenőrzési állapot
Choose source file…|Quelldatei auswählen…|Forrásfájl kiválasztása…
Choose source file|Quelldatei auswählen|Forrásfájl kiválasztása
Could not save source|Quelle konnte nicht gespeichert werden|A forrás nem menthető
Could not open source|Quelle konnte nicht geöffnet werden|A forrás nem nyitható meg
Search source titles, URLs or observations…|Quellentitel, URLs oder Beobachtungen suchen…|Forráscímek, URL-ek vagy megfigyelések keresése…
Add source…|Quelle hinzufügen…|Forrás hozzáadása…
Reuse manual/photo…|Anleitung/Foto wiederverwenden…|Útmutató/fotó újrafelhasználása…
Revise source…|Quelle überarbeiten…|Forrás módosított változata…
Open source|Quelle öffnen|Forrás megnyitása
Revision|Überarbeitung|Módosított változat
Reuse an existing manual or photo|Vorhandene Anleitung oder Foto wiederverwenden|Meglévő útmutató vagy fotó újrafelhasználása
Existing managed files are reused without copying. Source verification and observation date stay unknown until supplied.|Vorhandene verwaltete Dateien werden ohne Kopieren genutzt. Quellenprüfung und Beobachtungsdatum bleiben bis zur Angabe unbekannt.|A meglévő kezelt fájlok másolás nélkül használódnak. Ellenőrzés és megfigyelési dátum megadásig ismeretlen.
Who supplied this source, or where it came from. A source does not independently verify a device or its installed state.|Wer diese Quelle lieferte oder woher sie stammt. Eine Quelle bestätigt nicht automatisch ein Gerät oder seinen Installationszustand.|Ki adta vagy honnan származik a forrás. Egy forrás nem igazol automatikusan eszközt vagy telepített állapotot.
Actual observation or access date. Leave unknown if unavailable; no date is filled automatically.|Tatsächliches Beobachtungs-/Abrufdatum. Unbekannt lassen, falls nicht verfügbar; kein automatisches Datum.|Tényleges megfigyelési/hozzáférési dátum. Hiányában maradjon ismeretlen; nincs automatikus dátum.
Verified means you checked this source and requires a date. It does not automatically verify linked device assessments.|Geprüft bedeutet, dass Sie die Quelle geprüft haben; Datum erforderlich. Verknüpfte Gerätebewertungen werden nicht automatisch bestätigt.|Az ellenőrzött azt jelenti, hogy ellenőrizted a forrást; dátum kell. Nem igazolja automatikusan a kapcsolt eszközértékeléseket.
Library entries save immediately. Revisions create a new entry; old sources and existing assignments remain unchanged. Assignments save with Save device.|Bibliothekseinträge werden sofort gespeichert. Überarbeitungen erzeugen neue Einträge; alte Quellen/Zuordnungen bleiben. Zuordnungen mit Gerät speichern.|A forrástári bejegyzések azonnal mentődnek. Módosítás új bejegyzést hoz létre; régiek és hozzárendelések megmaradnak. Hozzárendelés az Eszköz mentése művelettel mentődik.
Tick sources for this section. Untick to remove an assignment. New/revised library entries save immediately; assignments apply only with Save device.|Quellen für diesen Bereich ankreuzen, zum Entfernen abwählen. Neue/überarbeitete Einträge sofort gespeichert; Zuordnungen erst mit Gerät speichern.|Jelöld a rész forrásait; jelölés törlésével a hozzárendelést veszed le. Új/módosított forrás azonnal mentődik, hozzárendelés csak az Eszköz mentése művelettel.'''.splitlines():
    en,de,hu=line.split('|');add(en,de,hu)
add('Selected sources:','Ausgewählte Quellen:','Kiválasztott források:')
for line in '''A source title of 1–200 characters is required.|Ein Quellentitel mit 1–200 Zeichen ist erforderlich.|1–200 karakteres forráscím szükséges.
Choose a valid source kind.|Gültige Quellenart wählen.|Válassz érvényes forrástípust.
Choose a valid source verification status.|Gültigen Quellen-Prüfstatus wählen.|Válassz érvényes forrásellenőrzési állapotot.
Choose a valid source observation or access date.|Gültiges Beobachtungs-/Abrufdatum wählen.|Válassz érvényes megfigyelési/hozzáférési dátumot.
A verified source needs an observation or access date.|Eine geprüfte Quelle benötigt ein Beobachtungs-/Abrufdatum.|Ellenőrzött forráshoz megfigyelési/hozzáférési dátum kell.
Write the observation or preserved source text.|Beobachtung oder bewahrten Quellentext eingeben.|Írd le a megfigyelést vagy a megőrzött forrásszöveget.
Choose a local source file.|Lokale Quelldatei auswählen.|Válassz helyi forrásfájlt.
Choose a valid JPEG/PNG photo up to 16 megapixels.|Gültiges JPEG-/PNG-Foto bis 16 Megapixel wählen.|Válassz érvényes JPEG/PNG-fotót legfeljebb 16 megapixelig.
Source file is missing or changed.|Quelldatei fehlt oder wurde verändert.|A forrásfájl hiányzik vagy megváltozott.
Could not open the selected source.|Ausgewählte Quelle konnte nicht geöffnet werden.|A kiválasztott forrás nem nyitható meg.
A selected source no longer exists; reopen the source selector.|Ausgewählte Quelle existiert nicht mehr; Quellenauswahl erneut öffnen.|A kiválasztott forrás már nem létezik; nyisd újra a választót.
Source assignments changed outside the form. Cancel and refresh before editing again.|Quellenzuordnungen wurden außerhalb des Formulars geändert. Abbrechen und vor weiterer Bearbeitung aktualisieren.|A forráshozzárendelések másutt megváltoztak. Vond vissza és frissíts új szerkesztés előtt.
Choose each source only once per section.|Jede Quelle pro Bereich nur einmal wählen.|Minden forrást csak egyszer válassz részenként.
Source file changed during import; retry.|Quelldatei wurde beim Import verändert; erneut versuchen.|A forrásfájl importáláskor megváltozott; próbáld újra.'''.splitlines():
    en,de,hu=line.split('|');add(en,de,hu)
add('Save source','Quelle speichern','Forrás mentése')
add('Use selected sources','Ausgewählte Quellen verwenden','Kiválasztott források használata')
add('Reuse selected reference','Ausgewählten Verweis wiederverwenden','Kiválasztott hivatkozás újrafelhasználása')
add('Uncertain','Unsicher','Bizonytalan')
add('User reported','Vom Nutzer berichtet','Felhasználói közlés')
add('Verified','Geprüft','Ellenőrzött')
add('Preserved source text','Bewahrter Quellentext','Megőrzött forrásszöveg')
add('Source text','Quellentext','Forrásszöveg')

# FR-019/020: deliberate editing and sourced topology.
for line in '''Network connections…|Netzwerkverbindungen…|Hálózati kapcsolatok…
Network connections|Netzwerkverbindungen|Hálózati kapcsolatok
Add connection|Verbindung hinzufügen|Kapcsolat hozzáadása
Edit connection|Verbindung bearbeiten|Kapcsolat szerkesztése
Add connection…|Verbindung hinzufügen…|Kapcsolat hozzáadása…
Edit connection…|Verbindung bearbeiten…|Kapcsolat szerkesztése…
Remove connection…|Verbindung entfernen…|Kapcsolat eltávolítása…
Remove connection|Verbindung entfernen|Kapcsolat eltávolítása
Save connection|Verbindung speichern|Kapcsolat mentése
Endpoint A|Endpunkt A|A végpont
Endpoint B|Endpunkt B|B végpont
Choose a saved interface|Gespeicherte Schnittstelle wählen|Válassz mentett interfészt
Choose a connection medium|Verbindungsmedium wählen|Válassz kapcsolati közeget
Connection medium|Verbindungsmedium|Kapcsolati közeg
Connection state|Verbindungsstatus|Kapcsolat állapota
Link rate (Mbit/s)|Verbindungsrate (Mbit/s)|Kapcsolati sebesség (Mbit/s)
Planned|Geplant|Tervezett
Observed|Beobachtet|Megfigyelt
Retired|Stillgelegt|Megszüntetett
Fiber|Glasfaser|Optikai szál
Other|Sonstige|Egyéb
Notes|Notizen|Megjegyzések
Unknown — leave blank|Unbekannt — leer lassen|Ismeretlen — hagyd üresen
Missing connection evidence|Verbindungsbeleg fehlt|Hiányzó kapcsolati bizonyíték
Could not save connection|Verbindung nicht gespeichert|A kapcsolat mentése sikertelen
No evidence source is selected. Save this unverified connection anyway?|Keine Belegquelle gewählt. Diese ungeprüfte Verbindung trotzdem speichern?|Nincs kiválasztott forrás. Mégis mented ezt az ellenőrizetlen kapcsolatot?
Remove this connection record? Devices stay unchanged; connection history is retained.|Diesen Verbindungseintrag entfernen? Geräte bleiben unverändert; Verbindungshistorie bleibt erhalten.|Eltávolítod ezt a kapcsolatrekordot? Az eszközök változatlanok, a kapcsolattörténet megmarad.
Save or cancel device changes before editing network connections.|Geräteänderungen vor dem Bearbeiten der Netzwerkverbindungen speichern oder verwerfen.|Hálózati kapcsolatok szerkesztése előtt mentsd vagy vond vissza az eszköz módosításait.
Save actual interfaces in Network identity first. Unknown MAC/IP addresses may remain blank.|Zuerst tatsächliche Schnittstellen unter Netzwerkidentität speichern. Unbekannte MAC-/IP-Adressen dürfen leer bleiben.|Először mentsd a tényleges interfészeket a Hálózati azonosítók alatt. Ismeretlen MAC-/IP-címek üresek maradhatnak.
Observed means reported at a date, not currently online. Planned links are not installed links.|Beobachtet bedeutet zu einem Zeitpunkt gemeldet, nicht gerade online. Geplante Verbindungen sind nicht installiert.|A megfigyelt állapot egy időpontra vonatkozó jelentés, nem jelenlegi online állapot. A tervezett kapcsolat nincs telepítve.
Observed or planned link rate in Mbit/s, not measured throughput. Describe its meaning in Notes.|Beobachtete oder geplante Verbindungsrate in Mbit/s, kein gemessener Datendurchsatz. Bedeutung unter Notizen beschreiben.|Megfigyelt vagy tervezett kapcsolati sebesség Mbit/s egységben, nem mért adatátvitel. Jelentését a Megjegyzésekben írd le.
Save connection commits this record immediately. Cancel leaves the record unchanged. Library entries created in the chooser save separately. Missing evidence warns; Verified requires evidence and a date.|Verbindung speichern übernimmt diesen Eintrag sofort. Abbrechen lässt ihn unverändert. In der Auswahl erstellte Quellen werden separat gespeichert. Fehlende Belege erzeugen eine Warnung; Geprüft erfordert Beleg und Datum.|A Kapcsolat mentése azonnal menti a rekordot. A Mégse változatlanul hagyja. A választóban létrehozott források külön mentődnek. Hiányzó bizonyíték figyelmeztetést ad; az Ellenőrzött állapothoz bizonyíték és dátum kell.
Recorded topology, not a live network scan. Save device changes before opening this list. Double-click a connection to edit.|Dokumentierte Topologie, kein Live-Netzwerkscan. Geräteänderungen vor dem Öffnen speichern. Verbindung zum Bearbeiten doppelt anklicken.|Dokumentált topológia, nem élő hálózatfelderítés. A lista megnyitása előtt mentsd az eszköz módosításait. Szerkesztéshez kattints duplán a kapcsolatra.
Choose two different saved interfaces.|Zwei unterschiedliche gespeicherte Schnittstellen wählen.|Válassz két különböző mentett interfészt.
Choose interfaces on two different saved devices.|Schnittstellen zweier unterschiedlicher gespeicherter Geräte wählen.|Válassz interfészeket két különböző mentett eszközön.
Choose a connection medium.|Verbindungsmedium wählen.|Válassz kapcsolati közeget.
Choose a connection state.|Verbindungsstatus wählen.|Válassz kapcsolati állapotot.
Connection notes and dates must be text.|Verbindungsnotizen und Daten müssen Text sein.|A kapcsolat megjegyzései és dátumai szövegek legyenek.
Speed must be a positive number in Mbit/s, or blank.|Geschwindigkeit muss eine positive Zahl in Mbit/s oder leer sein.|A sebesség pozitív szám legyen Mbit/s egységben, vagy üres.
Choose existing evidence entries.|Vorhandene Belege wählen.|Válassz létező bizonyítékokat.
Verified connections need evidence and an observation date.|Geprüfte Verbindungen benötigen Beleg und Beobachtungsdatum.|Ellenőrzött kapcsolathoz bizonyíték és megfigyelési dátum kell.
Connection needs normalization.|Verbindung muss normalisiert werden.|A kapcsolat normalizálást igényel.
This connection changed. Close and reopen the connection list.|Diese Verbindung wurde geändert. Verbindungsliste schließen und erneut öffnen.|Ez a kapcsolat megváltozott. Zárd be és nyisd újra a kapcsolatok listáját.
This pair of interfaces already has a connection record.|Für dieses Schnittstellenpaar besteht bereits ein Verbindungseintrag.|Ehhez az interfészpárhoz már létezik kapcsolatrekord.
Remove the connection records before removing this interface.|Vor dem Entfernen dieser Schnittstelle die Verbindungseinträge entfernen.|Az interfész eltávolítása előtt távolítsd el a kapcsolatrekordokat.
Remove the connection records before deleting this device.|Vor dem Löschen dieses Geräts die Verbindungseinträge entfernen.|Az eszköz törlése előtt távolítsd el a kapcsolatrekordokat.
Interface identity belongs to another device.|Schnittstellenkennung gehört zu einem anderen Gerät.|Az interfészazonosító másik eszközhöz tartozik.'''.splitlines():
    en,de,hu=line.split('|');add(en,de,hu)

add('Library entries save immediately. Revisions create a new entry; old sources and existing assignments remain unchanged. Assignments save with the parent form.','Quellen werden sofort gespeichert. Revisionen erzeugen einen neuen Eintrag; alte Quellen und Zuordnungen bleiben erhalten. Zuordnungen werden mit dem übergeordneten Formular gespeichert.','A források azonnal mentődnek. A javítás új bejegyzést hoz létre; a régi források és hozzárendelések megmaradnak. A hozzárendelések a szülőűrlappal mentődnek.')
add('Tick sources for this section. Untick to remove an assignment. New/revised library entries save immediately; assignments apply only when the parent form is saved.','Quellen für diesen Abschnitt markieren; zum Entfernen der Zuordnung abwählen. Neue/revidierte Quellen werden sofort gespeichert; Zuordnungen erst mit dem übergeordneten Formular.','Jelöld a szakasz forrásait; a jelölés törlése megszünteti a hozzárendelést. Új/javított forrás azonnal mentődik; hozzárendelés csak a szülőűrlap mentésekor.')
add('Select several existing sources or add evidence. Source assignments save together with the parent form.','Mehrere Quellen wählen oder Belege hinzufügen. Zuordnungen werden mit dem übergeordneten Formular gespeichert.','Válassz több forrást vagy adj hozzá bizonyítékot. A hozzárendelések a szülőűrlappal mentődnek.')

add('Location','Standort','Elhelyezkedés')
add('Location: use a single line of text, up to 200 characters.','Standort: eine Textzeile mit höchstens 200 Zeichen.','Elhelyezkedés: egyetlen sor, legfeljebb 200 karakter.')
add('Optional physical location, for example building / room / rack / shelf. Unicode allowed; maximum 200 characters. Leave unknown blank. This is not a network address or purchased-at value.','Optionaler physischer Standort, z. B. Gebäude / Raum / Rack / Regal. Unicode erlaubt; höchstens 200 Zeichen. Unbekanntes leer lassen. Keine Netzwerkadresse und kein Kaufort.','Opcionális fizikai hely, például épület / helyiség / rack / polc. Unicode megengedett; legfeljebb 200 karakter. Ismeretlen maradjon üres. Nem hálózati cím és nem vásárlási hely.')
add('Type to find an existing choice…','Tippen, um vorhandene Auswahl zu finden…','Írj be egy meglévő lehetőség kereséséhez…')
add('Device location','Gerätestandort','Eszköz elhelyezkedése')
add('Basement','Keller','Pince')
add('Ground floor','Erdgeschoss','Földszint')
add('First floor','Erstes Obergeschoss','Első emelet')
add('Attic','Dachgeschoss','Tetőtér')
add('Where is this device?','Wo befindet sich dieses Gerät?','Hol található ez az eszköz?')
add('Guided location…','Standort geführt eingeben…','Vezetett helymegadás…')
add('Location status','Standortstatus','Helyadat állapota')
add('Recorded location','Standort angegeben','Megadott hely')
add('Not applicable / portable','Nicht zutreffend / tragbar','Nem alkalmazható / hordozható')
add('Current form values','Aktuelle Formularwerte','Jelenlegi űrlapértékek')
add('New location…','Neuer Standort…','Új hely…')
add('Reuse an existing location','Vorhandenen Standort verwenden','Meglévő hely újrafelhasználása')
add('Building / site','Gebäude / Standort','Épület / telephely')
add('Floor / storey','Geschoss / Etage','Szint / emelet')
add('Room','Raum','Helyiség')
add('Position / wall','Position / Wand','Pozíció / fal')
add('Mounting height (m)','Montagehöhe (m)','Szerelési magasság (m)')
add('Height reference','Höhenbezug','Magassági referencia')
add('Choose a height reference','Höhenbezug wählen','Válassz magassági referenciát')
add('Above finished floor','Über Fertigfußboden','Kész padlószint felett')
add('Above ground level','Über Gelände','Talajszint felett')
add('Other height reference','Anderer Höhenbezug','Más magassági referencia')
add('Address and additional notes (optional)','Adresse und weitere Hinweise (optional)','Cím és további megjegyzések (opcionális)')
add('Country','Land','Ország')
add('Postal code','Postleitzahl','Irányítószám')
add('City','Ort / Stadt','Település')
add('Street','Straße','Utca')
add('House number','Hausnummer','Házszám')
add('Placement notes','Platzierungshinweise','Elhelyezési megjegyzések')
add('Location preview','Standortvorschau','Helyadat előnézete')
add('Use location','Standort übernehmen','Helyadat használata')
add('Placement belongs to this device. Other devices are unchanged. Use location returns to the device form; Save device writes to the database.','Die Platzierung gehört zu diesem Gerät. Andere Geräte bleiben unverändert. Standort übernehmen führt zum Geräteformular zurück; Gerät speichern schreibt in die Datenbank.','Az elhelyezés ehhez az eszközhöz tartozik. Más eszköz nem változik. A Helyadat használata visszatér az űrlapra; az Eszköz mentése ír az adatbázisba.')
add('Location details need attention.','Standortangaben prüfen.','Ellenőrizd a helyadatokat.')
add('Location fields must be single-line text.','Standortfelder müssen einzeiliger Text sein.','A helymezők egysoros szöveget fogadnak el.')
add('Location fields must contain at most 200 characters.','Standortfelder dürfen höchstens 200 Zeichen enthalten.','A helymezők legfeljebb 200 karaktert tartalmazhatnak.')
add('Choose a valid location status.','Gültigen Standortstatus wählen.','Válassz érvényes helyállapotot.')
add('Height: enter a number from 0 to 10000 metres, using a comma or point.','Höhe: Zahl zwischen 0 und 10000 Metern mit Komma oder Punkt eingeben.','Magasság: 0 és 10000 méter közötti számot adj meg, vesszővel vagy ponttal.')
add('Choose a height reference.','Höhenbezug wählen.','Válassz magassági referenciát.')
add('Describe the other height reference in placement notes.','Anderen Höhenbezug in den Platzierungshinweisen beschreiben.','Írd le a másik magassági referenciát az elhelyezési megjegyzésekben.')
add('Unknown or not applicable locations must have no structured details.','Unbekannte oder nicht zutreffende Standorte dürfen keine strukturierten Angaben haben.','Ismeretlen vagy nem alkalmazható helyhez nem tartozhat strukturált adat.')
add('Enter at least one location detail, or choose Unknown.','Mindestens eine Standortangabe eingeben oder Unbekannt wählen.','Adj meg legalább egy helyadatot, vagy válaszd az Ismeretlen lehetőséget.')
add('Location changed outside the form. Cancel and refresh before editing again.','Standort wurde außerhalb des Formulars geändert. Abbrechen und vor erneutem Bearbeiten aktualisieren.','A helyadat az űrlapon kívül módosult. Vond vissza és frissítsd új szerkesztés előtt.')
add('Optional building or site. Reuse a saved place or enter a new one.','Optionales Gebäude oder Standort. Gespeicherten Ort verwenden oder neuen eingeben.','Opcionális épület vagy telephely. Használj mentett helyet vagy adj meg újat.')
add('Optional floor label, for example basement, ground floor or first floor.','Optionale Geschossbezeichnung, z. B. Keller, Erdgeschoss oder Obergeschoss.','Opcionális szintnév, például pince, földszint vagy első emelet.')
add('Optional room. All hierarchy levels can be left out when irrelevant.','Optionaler Raum. Unzutreffende Hierarchieebenen können entfallen.','Opcionális helyiség. A nem szükséges hierarchiaszintek elhagyhatók.')
add('Position for this device only, for example northwest wall or rack shelf.','Position nur für dieses Gerät, z. B. Nordwestwand oder Rackboden.','Csak ezen eszköz pozíciója, például északnyugati fal vagy rackpolc.')
add('Optional height in metres, from 0 to 10000. Both 1.8 and 1,8 are accepted. State the reference level.','Optionale Höhe in Metern von 0 bis 10000. 1.8 und 1,8 sind zulässig. Bezugsebene angeben.','Opcionális magasság méterben 0 és 10000 között. Az 1.8 és 1,8 egyaránt elfogadott. Add meg a referenciaszintet.')
add('Optional placement details. Describe the reference here when choosing Other height reference.','Optionale Platzierungshinweise. Bei Anderem Höhenbezug hier den Bezug beschreiben.','Opcionális elhelyezési adatok. Más magassági referencia választásakor itt írd le a referenciát.')
add('Optional single-line Unicode text, maximum 200 characters.','Optionaler einzeiliger Unicode-Text, höchstens 200 Zeichen.','Opcionális egysoros Unicode-szöveg, legfeljebb 200 karakter.')
add('Height is independent of floor labels and X/Y position. Choose the actual reference level.','Höhe ist unabhängig von Geschossnamen und X/Y-Position. Tatsächliche Bezugsebene wählen.','A magasság független a szintnévtől és X/Y pozíciótól. Válaszd a tényleges referenciaszintet.')
add('Reuse the address, building, floor and room. Precise placement is specific to this device. Existing places are never renamed here.','Adresse, Gebäude, Geschoss und Raum wiederverwenden. Genaue Position gilt nur für dieses Gerät. Vorhandene Orte werden hier nicht umbenannt.','Cím, épület, szint és helyiség újrafelhasználása. A pontos pozíció csak erre az eszközre vonatkozik. Meglévő hely itt nem nevezhető át.')
add('Validate and return these pending details to the device form. Save device is still required.','Ausstehende Angaben prüfen und ins Geräteformular übernehmen. Gerät speichern ist weiterhin erforderlich.','Ellenőrizd és vidd vissza a függő adatokat az eszközűrlapra. Az Eszköz mentése még szükséges.')
add('Keep the location values from before this dialog.','Standortwerte von vor diesem Dialog behalten.','A párbeszédablak előtti helyadatok megtartása.')
add('Choose or reuse a place, then enter device-specific position and mounting height. Existing location text is preserved.','Ort wählen oder wiederverwenden, dann gerätespezifische Position und Montagehöhe eingeben. Vorhandener Standorttext bleibt erhalten.','Válassz vagy használj újra helyet, majd add meg az eszköz pozícióját és magasságát. A meglévő helyszöveg megmarad.')
add('Type part of a name, then choose a matching result. Typing alone does not apply a filter or create a new choice. Choose All groups or All types to reset.','Namensteil tippen und Treffer wählen. Tippen allein aktiviert keinen Filter und erstellt keinen Eintrag. Zum Zurücksetzen Alle Gruppen oder Alle Typen wählen.','Írd be a név részletét, majd válassz találatot. A gépelés önmagában nem alkalmaz szűrőt és nem hoz létre új elemet. Visszaállításhoz Minden csoport vagy Minden típus.')

add('Location text / additional description','Standorttext / zusätzliche Beschreibung','Helyszöveg / további leírás')
add('Structured location','Strukturierter Standort','Strukturált helyadat')
