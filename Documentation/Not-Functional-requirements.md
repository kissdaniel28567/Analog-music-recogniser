## Nem-funkcionális Követelmények

### Teljesítmény (Performance)
*   **Zenefelismerési idő:** A rendszernek a zene kezdetétől számítva legfeljebb 15 másodpercen belül azonosítania kell a dalt.
*   **Erőforrás-használat:** A Raspberry Pi átlagos CPU terhelése a program futása közben nem haladhatja meg a 75%-ot.
*   **Felhasználói felület válaszideje:** A webes felületen végzett műveletekre (pl. gombnyomás) a vizuális visszajelzésnek 200 ezredmásodpercen belül meg kell történnie.
*   **Audio streaming késleltetése:** A hálózati audio stream késleltetése a valós idejű hanghoz képest nem lehet több, mint 500 ms.

### Megbízhatóság (Reliability)
*   **Stabilitás:** A rendszernek képesnek kell lennie legalább 24 órás folyamatos, újraindítás nélküli működésre.
*   **Hibatűrés:** Külső API szolgáltatás (pl. Last.fm) elérhetetlensége esetén a program nem állhat le, a sikertelen kérést naplóznia kell.
*   **Adatkonzisztencia:** A lejátszási statisztikáknak meg kell maradniuk a program hirtelen leállása vagy újraindítása esetén is.

### Használhatóság (Usability)
*   **Első beállítás:** A rendszer alapvető beállításait (pl. Last.fm összekötés) egy új felhasználónak 5 percen belül, különösebb útmutató nélkül el kell tudnia végezni.
*   **Reszponzivitás:** A webes felületnek egyaránt használhatónak és esztétikusnak kell lennie asztali számítógépen és mobiltelefonon is.
*   **Visszajelzés:** A rendszernek minden fontos állapotváltozásról (pl. zene keresése, API hiba) egyértelmű vizuális visszajelzést kell adnia.

### Karbantarthatóság (Maintainability)
*   **Kódminőség:** A forráskódnak jól strukturáltnak, olvashatónak és megfelelően kommentezettnek kell lennie.
*   **Modularitás:** Az alkalmazás komponenseit (audiofeldolgozás, API kliensek, webes felület) logikailag szét kell választani a könnyebb fejleszthetőség érdekében.

### Biztonság (Security)
*   **API kulcsok kezelése:** A külső szolgáltatásokhoz tartozó API kulcsokat és egyéb érzékeny adatokat nem szabad a forráskódban tárolni, azokat környezeti változókból vagy biztonságos konfigurációs fájlból kell betölteni.
*   **Hálózati hozzáférés:** A webes felület alapértelmezetten csak a helyi hálózatról érhető el.