# Kilima Locations — Complete Reference

> Updated 2026-03-23. Reflects the 7-level hierarchy, BN1 locations, and harmonic system.
> For the generic engine, see `gigagen_location_system.md`.
> For factions, see `kilima_factions.md`.
> For the JSON data, see `locations.json`.

---

## Location Hierarchy (7 levels)

| Level | Name | Tonic logic | Description |
|-------|------|-------------|-------------|
| 1 | World | Fixed by narrative arc | The totality. Changes between BN1, BN2, etc. |
| 2 | Territory | Derived | Physical space. Media or gambling of lower levels. |
| 3 | Region | Seeded in Chronica | Kilima, Last Road, Golden Cage, The Train. |
| 4 | Area | Seeded in Chronica | Capitol, Agora, Pobla 2, Wall, Net. Contains zone_tags (districts/barrios/sections). |
| 5 | Location | Mix fixed/seeded | The harmonic entity. Has note, faction control, modal influence. Enters Life Pack. |
| 6 | Room | Fixed by nature/use | Operational position. A studio is always a studio. |
| 7 | Locker | Fixed by content | Movable between rooms. Physical container for items. |

Every level has a tonic note. The harmonic affinity between any two entities is always note vs note, regardless of level. The octave/level is organization, not resonance.

---

## Full Hierarchy

```
World (level 1 — fixed by arc)
└── Territory (level 2 — derived)
    ├── Kilima (level 3 — seeded)
    │   ├── Capitol (level 4 — seeded)
    │   │   zone_tags: 7 districts (Morecuri, Nuve Este, Terramar, Triple Sur, Santo Norte, Oeste Auron, Neotown)
    │   │   ├── The Tower (level 5 — seeded) — Agency SL
    │   │   │   └── Meeting Room (level 6)
    │   │   ├── The Cathedral (level 5 — seeded) — Cult Order
    │   │   │   └── Main Hall (level 6)
    │   │   ├── The Central Station (level 5 — seeded) — Kilima Lines
    │   │   │   └── Platform 04 (level 6)
    │   │   └── The Avenue (level 5 — seeded) — neutral
    │   │       └── Cabin 04 (level 6)
    │   │
    │   ├── Agora (level 4 — seeded)
    │   │   zone_tags: 13 barrios (12 ministerios Union Corp + Levi-Montalcini outsider)
    │   │   barrio names: Culture, Education, Energy, Defense, Katalin Kariko, Structures,
    │   │                  Systems, Interior, Memory, Materials, Engineering, Exterior, Levi-Montalcini
    │   │   ├── The Headquarters (level 5 — seeded) — Union Corp
    │   │   │   └── Interior Office (level 6)
    │   │   ├── The Nest (level 5 — seeded, barrio: Katalin Kariko fixed) — Amparo Foundation
    │   │   │   └── Operating Room (level 6)
    │   │   └── The Recess (level 5 — A# fixed, barrio: Levi-Montalcini fixed) — Anti Group
    │   │       ├── Studio (level 6)
    │   │       └── Rooftop (level 6)
    │   │
    │   ├── Pobla 2 (level 4 — seeded)
    │   │   zone_tags: 8 sections (N, NE, E, SE, S, SW, W, NW)
    │   │   ├── The Backdoor (level 5 — F# fixed) — Backdoor
    │   │   │   └── Hub (level 6)
    │   │   ├── The Cave (level 5 — B fixed) — Anti Group
    │   │   │   ├── Entrance (level 6)
    │   │   │   ├── Assembly (level 6)
    │   │   │   └── Daycare (level 6)
    │   │   ├── The Workshop (level 5 — D# fixed) — Anti Group / Red Fist Dragons
    │   │   │   ├── Garage (level 6)
    │   │   │   │   └── Chest 04 (level 7 — locker, Zapas Viejas de Kive)
    │   │   │   └── Living Room (level 6)
    │   │   └── The Cemetery (level 5 — seeded) — none
    │   │       └── Sector 07 (level 6)
    │   │
    │   ├── Wall (level 4 — seeded) — Guard Force
    │   │   ├── The First Wall (level 5 — seeded) — Guard Force
    │   │   │   └── Checkpoint (level 6)
    │   │   └── The Second Wall (level 5 — seeded) — Guard Force
    │   │       └── Checkpoint (level 6)
    │   │
    │   └── Net (level 4 — seeded)
    │       ├── The Plaza (level 5 — seeded) — neutral
    │       │   └── Stage (level 6)
    │       └── The Limbo (level 5 — seeded) — none
    │           └── Lobby (level 6)
    │
    ├── Last Road (level 3 — seeded)
    │   └── The Oasis Suspiro (level 5 — seeded) — Anti Group / Dust Parade
    │       └── Cafe (level 6)
    │
    ├── Golden Cage (level 3 — seeded)
    │   ├── Plaza (level 6 — room of Golden Cage directly)
    │   ├── Port (level 6 — room of Golden Cage directly)
    │   ├── The Library (level 5 — seeded) — Bohemian Academy
    │   └── The Mortuary (level 5 — seeded) — none
    │       └── Belongings Room (level 6)
    │           └── Locker 05 (level 7 — locker, pertenencias de Len)
    │
    └── The Train (level 3 — seeded)
        └── Wagon 04 (level 6 — room of The Train directly)
```

---

## BN1 Locations (operational)

Only locations where characters physically are during the 62-hour BN1 timeline.

### Fixed tonic (4 locations)

| Location | Tonic | Region | Faction | Why fixed |
|----------|-------|--------|---------|-----------|
| The Workshop | D# | Pobla 2 | Anti Group / Red Fist Dragons | Kive's base |
| The Backdoor | F# | Pobla 2 | Backdoor | Dev's territory |
| The Cave | B | Pobla 2 | Anti Group / Direnis Cell | Freya's base, group converges |
| The Recess | A# | Agora | Anti Group / artistas | Cris territory, fiesta interrumpida |

### Seeded tonic (13 locations)

| Location | Region | Faction | BN1 relevance |
|----------|--------|---------|---------------|
| The Tower | Capitol | Agency SL | Luka works here |
| The Cathedral | Capitol | Cult Order | Occultist funeral, Len initiated |
| The Central Station | Capitol | Kilima Lines | Kive + Yeri arrive, split |
| The Avenue | Capitol | neutral | Net cabins, Kive meets Agency SL, Dev finds him |
| The Headquarters | Agora | Union Corp | Saarah + Cris flee H18 |
| The Nest | Agora | Amparo Foundation | Nora, group hides |
| The Cemetery | Pobla 2 | none | Robot junkyard, Dev passes through |
| The First Wall | Wall | Guard Force | Capitol-Agora border |
| The Second Wall | Wall | Guard Force | Agora-Pobla 2 border |
| The Plaza | Net | neutral | Virtual funeral |
| The Limbo | Net | none | Len exists here, Brais transferred |
| The Oasis Suspiro | Last Road | Anti Group / Dust Parade | Kive + Yeri pass through |
| The Library | Golden Cage | Bohemian Academy | Pau, Grand Library |
| The Mortuary | Golden Cage | none | Len's belongings post-incineration |

---

## Zone Tags

Zone tags are geographic labels within areas. They are not operational levels — they provide context.

### Capitol — 7 districts (planetary names)

| District | Reference |
|----------|-----------|
| Morecuri | Mercury |
| Nuve Este | Venus |
| Terramar | Mars |
| Triple Sur | Jupiter |
| Santo Norte | Saturn |
| Oeste Auron | Uranus |
| Neotown | Neptune |

Assignment: seeded. Each location in Capitol gets a random district per seed.

### Agora — 13 barrios (12 ministries + 1 outsider)

| Barrio | Ministry / Role | Notes |
|--------|----------------|-------|
| Culture | Culture ministry | Name TBD (woman who revolutionized the field) |
| Education | Education ministry | Name TBD |
| Energy | Energy ministry | Name TBD |
| Defense | Defense ministry | Name TBD |
| Katalin Kariko | Biotechnology ministry | Fixed: The Nest is here |
| Structures | Structures ministry | Name TBD |
| Systems | Systems ministry | Name TBD |
| Interior | Interior ministry | Name TBD |
| Memory | Memory ministry | Name TBD |
| Materials | Materials ministry | Name TBD |
| Engineering | Engineering ministry | Name TBD |
| Exterior | Exterior ministry | Name TBD |
| Levi-Montalcini | Outsider (not Union Corp) | Fixed: The Recess is here. Artistic quarter. |

Assignment: seeded, except The Nest (Katalin Kariko) and The Recess (Levi-Montalcini) which are fixed.

Future: all barrio names will be renamed to women who revolutionized each sector.

### Pobla 2 — 8 sections (compass rose)

| Section |
|---------|
| N |
| NE |
| E |
| SE |
| S |
| SW |
| W |
| NW |

Assignment: seeded.

---

## Character Starting Positions (H00)

| Character | Note | Starting location | Region |
|-----------|------|-------------------|--------|
| Kive (REB) | D# | Golden Cage | Golden Cage |
| Len (ORP) | E | The Limbo | Net |
| Dev (HCK) | F# | The Cave | Pobla 2 |
| Saarah (LEA) | G | Capitol | Capitol |
| Cris (CRE) | A# | Agora | Agora |
| Brais (INN) | G# | Golden Cage | Golden Cage |
| Ali (LOV) | F | Agora | Agora |
| Pau (JES) | C# | Golden Cage | Golden Cage |
| Luka (HER) | D | Capitol | Capitol |
| Yeri (EXP) | A | Golden Cage | Golden Cage |
| Nora (CAR) | C | Golden Cage | Golden Cage |
| Freya (DEI) | B | The Cave | Pobla 2 |

---

## Harmonic System

Every location at every level has a tonic note. The harmonic affinity between a character and a location is calculated with the universal function: `harmonic_affinity(character_note, location_note) → float`.

The octave/level does not affect the calculation. D# against A# is always a perfect fifth, whether comparing a character to a region or to a room.

The parent tree does not affect the base calculation either. A possible future enhancement: compute a weighted average of intervals up the parent chain for a "general comfort index". Not blocking.

Location tonics are **not access gates**. Any character can be in any location regardless of harmonic affinity. The affinity is an emotional indicator — how the character feels there — not a mechanical restriction. Access is controlled by factions, objects, and skills.

---

## Naming Conventions

- Level 5 locations always carry the determiner "The" (The Tower, The Recess, The Cave).
- Room names with numbers use zero-padded format (Platform 04, Cabin 04, Wagon 04, Sector 07).
- Locker names use zero-padded format (Locker 05, Chest 04).
- Region and area names have no determiner (Capitol, Agora, Pobla 2, Golden Cage).
- Language is English as standard, with creative exceptions for lore (Pobla 2, Oasis Suspiro, Levi-Montalcini, Katalin Kariko).

### Nomenclature changes from previous documentation

| Before | Now | Reason |
|--------|-----|--------|
| La Capital | Capitol | English standard |
| La Ciudad | Agora | Proper name |
| El Poblado | Pobla 2 | Proper name |
| The Cage / La Jaula | Golden Cage | Avoid confusion with "cave" |
| La Sede | The Headquarters | English standard |
| El Forno (location) | The Recess (location) + Levi-Montalcini (barrio) | Separated location from barrio. Forno becomes character name. |
| El Taller | The Workshop | English standard with "The" |
| La Catedral | The Cathedral | English standard with "The" |
| La Biblioteca | The Library | English standard with "The" |
| The Road | Last Road | Renamed |
| — | The Avenue | New location |
| — | The Central Station | New location |
| — | The Cemetery | New location |
| — | The Plaza | New virtual location |
| — | The Recess | New location (abandoned school, artists) |
| — | The Mortuary | New location |

---

## Future Locations (not operational in BN1)

Documented in lore, will be implemented when needed.

### Capitol
The Table, La Junta, El Jardin Real, The Clinic, The Coliseum, The Server, The Academy, The Rotation

### Agora
The Church, Lujuria, El Rancho, The Zone, Los Pisos

### Pobla 2
Los Bloques, The Port, El Desguace, Los Servidores, La Colina

### Cave (additional rooms)
El Comedor, La Enfermeria, El Aula, Sala de Maquinas, Centro de Mando

### Golden Cage
El Museo, El Parque

### Last Road
Los Amarres, La Escuela Militar, La Urbanizacion, El Zepelin

### Net
The Void, The Infrared, El Crucero, El Estadio, El Cole, El Jardin, El Launcher, El Refugio

### Space
The Colony (lunar prison, Guard Force / Moon Soldiers), The Frontier (luxury station, Union Corp)

### Earth
La Selva, El Copo, La Brecha, Las Tres Islas, Atlantis, La Flota
