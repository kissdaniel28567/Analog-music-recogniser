---
title: Felhasználói eset diagram
---
```plantuml
@startuml

left to right direction

actor "Zenehallgató" as ZH

rectangle "Intelligens Lemezlejátszó Rendszer" {
    usecase "Zenehallgatás és azonosítás" as UC1
    usecase "Lejátszási statisztikák megtekintése" as UC2
    usecase "Rendszerdiagnosztika ellenőrzése" as UC3
    usecase "Zene streamelése hálózaton" as UC4
    usecase "Dalszöveg megtekintése" as UC5
    usecase "Rendszer beállítása" as UC6
    
    ' Az automatikus alfolyamatok logikailag elkülönítve, de a rendszeren belül
    usecase "Zeneszám lekérdezése API-ból" as UC1_1
    usecase "Zene scrobbelése Last.fm-re" as UC1_2
    usecase "Metaadatok lekérdezése" as UC1_3
}

actor "Lemezlejátszó" as LL
actor "Zenefelismerő Szolgáltatás" as ZFS
actor "Last.fm Szolgáltatás" as LFM
actor "Dalszöveg Adatbázis" as DA
actor "Metaadat Adatbázis" as MA

ZH --> UC1
ZH --> UC2
ZH --> UC3
ZH --> UC6
LL --> UC1 : audio jelet ad

UC1 .> UC1_1 : <<include>>
UC1 .> UC1_2 : <<include>>
UC1 .> UC1_3 : <<include>>

UC4 .> UC1 : <<extend>>
UC5 .> UC1 : <<extend>>

UC1_1 --> ZFS
UC1_2 --> LFM
UC1_3 --> MA
UC5 --> DA

@enduml
