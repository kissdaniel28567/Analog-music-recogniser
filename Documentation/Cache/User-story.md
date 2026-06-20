# User Story diagrammok 

Az alábbi dokumentum a projekt legfontosabb funkcióit írja le Gherkin szintaxis segítségével. A scenariók két fő csoportra vannak bontva: a rendszer belső működését leíró funkciókra és a felhasználói felületen végzett konkrét interakciókra.

## Rendszerfunkciók (Backend Viselkedés)

### Zene Sikeres Azonosítása
**Scenario:** A rendszer megtalálja a zenét és frissíti a felületet.
```gherkin
Given a rendszer "Figyelés" állapotban van és a lemezjátszón elindul egy dal
When a rendszer sikeresen azonosítja a zeneszámot
Then a felületen megjelenik az előadó és a számcím
And egy lejátszást szimbolizáló animáció elindul a képernyőn
```

### Last.fm Integráció
**Scenario:** Lejátszott dal automatikus naplózása (scrobbling).
```gherkin
Given a zenehallgató beállította a Last.fm fiókját a rendszerben
And a rendszer sikeresen felismert egy dalt
When a dal lejátszása eléri a scrobble-hez szükséges pontot (pl. a dal fele)
Then a dal megjelenik a felhasználó Last.fm profiljának előzményeiben
```

### Szinkronizált Dalszöveg
**Scenario:** Dalszöveg megjelenítése a felismert dalhoz.
```gherkin
Given a rendszer sikeresen felismert egy dalt
And a dalhoz létezik elérhető dalszöveg egy külső szolgáltatónál
When a zenehallgató a lejátszó felületét nézi
Then a felületen megjelenik a dal aktuális sora kiemelve, szinkronban a zenével
```

### Tűkopás Figyelés
**Scenario:** Figyelmeztetés a tű közelgő cseréjéről.
```gherkin
Given a rendszer naplózza a lejátszási időt, és a tű becsült élettartama 1000 óra
And a lejátszott órák száma elérte a 995 órát
When a zenehallgató elindít egy új lemezt
Then a webes felületen egy jól látható figyelmeztetés jelenik meg a tű közelgő cseréjéről
```

### Lemezállapot Diagnosztika
**Scenario:** Karcolás észlelése a lemezen.
```gherkin
Given a zenehallgató egy lemezt játszik le
When az audiojelben a rendszer egy karcolásra utaló, hirtelen zajt (kattogást) észlel
Then a felhasználói felületen egy ideiglenes vizuális jelzés (pl. ikon) jelenik meg, ami a lemezhibára utal
```

### Hálózati Audio Streaming
**Scenario:** Zenehallgatás másik eszközön a hálózaton keresztül.
```gherkin
Given a lemezjátszón szól a zene
When a zenehallgató egy másik eszközön (pl. telefon) megnyitja a rendszer streaming URL-jét
Then az eszközön hallhatóvá válik a lemezjátszó által lejátszott zene valós időben
```

## Felhasználói Felület Interakciók (Frontend Viselkedés)

### Dalszöveg Megtekintése
**Scenario:** A felhasználó a dalszövegre kíváncsi.
```gherkin
Given egy azonosított zeneszám szól a lemezjátszón
When a felhasználó megnyomja a "Dalszöveg" gombot
Then a képernyő fő részén megjelenik a dal szövege
```

### Statisztikák Megtekintése
**Scenario:** A felhasználó megnézi a hallgatási statisztikáit.
```gherkin
Given a felhasználó a főoldalon van
When a felhasználó megnyomja a "Statisztikák" menüpontot
Then a felület átvált a statisztikai nézetre, ahol a legtöbbet hallgatott előadók láthatók
```

### Rendszerállapot Ellenőrzése
**Scenario:** A felhasználó ellenőrzi a tű állapotát.
```gherkin
Given a rendszer fut
When a felhasználó a "Diagnosztika" vagy "Beállítások" oldalra navigál
Then a képernyőn megjelenik egy mutató, ami a tű becsült elhasználtságát mutatja százalékban
```

### Sikertelen Azonosítás
**Scenario:** A rendszer nem ismeri fel a zenét.
```gherkin
Given a rendszer "Figyelés" állapotban van, de egy ismeretlen zene szól
When letelik az azonosítási időkorlát
Then a felületen egy "A zeneszám nem felismerhető" üzenet jelenik meg
```