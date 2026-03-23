# Roadmap — Factions & Locations Rework

> Prerequisito antes de LP-0. Dejar el terreno limpio para el renombrado y el Life Pack.
> Updated 2026-03-23 with all session decisions.

---

## Estado actual

### Facciones
- `kilima_factions.md` está actualizado con nomenclatura nueva (macro-faction/faction), 10 macro-facciones, bases corregidas.
- `factions.json` ACTUALIZADO (FL-0 + migración): estructura split con `macro_factions[]` + `factions[]`. 10 macro-facciones, 35 facciones. Loader reconstruye formato embebido al cargar.
- Hot Forno (cell de Anti Group) eliminada. Cris empieza sin facción — se une a Anti Group durante BN1 en The Cave.
- Anti Group tiene 3 cells: Direnis Cell, Red Fist Dragons, Dust Parade.

### Locations
- `kilima_locations.md` reescrito con la jerarquía de 7 niveles completa.
- `locations.json` reescrito desde cero con 55 entries (world, territory, 4 regions, 5 areas, 17 locations, 24 rooms, 2 lockers).
- 4 locations con tonic fixed (Workshop D#, Backdoor F#, Cave B, Recess A#), resto seeded.
- Zone tags definidos: Capitol 7 distritos, Agora 13 barrios (12 ministerios + Levi-Montalcini), Pobla 2 8 secciones (rosa de los vientos).

### Relations
- `relations.json` actualizado: 3 relaciones macro-faction→location eliminadas, 7 relaciones faction→location añadidas (nivel correcto). 30 relaciones total.

### Characters
- `characters.json` actualizado: location IDs corregidos (loc.cage → golden_cage, loc.capital → capitol, loc.city → agora). Cris tiene current_faction_id: null.

---

## FL-0: Rework completo de factions.json — DONE

**Objetivo:** Separar macro-facciones de facciones como entidades distintas. Estructura limpia para LP-0.

### Estructura nueva del JSON

```json
{
  "macro_factions": [
    {
      "id": "mfac.anti_group",
      "name": "Anti Group",
      "mode": "phrygian",
      "intervals": [1, 2, 2, 2, 1, 2, 2],
      "note_count": 7,
      "scale_family": "greek",
      "tags": [...],
      "description": "..."
    }
  ],
  "factions": [
    {
      "id": "fac.direnis_cell",
      "macro_faction_id": "mfac.anti_group",
      "name": "Direnis Cell",
      "root_note": "B",
      "leader_id": "kilima_in12_deity",
      "base_location_id": "loc.cave",
      "tags": [...],
      "description": "..."
    }
  ]
}
```

### Datos confirmados para las facciones

**Anti Group (Phrygian) — 3 factions:**

| ID | Name | Root note | Leader | Base |
|----|------|-----------|--------|------|
| fac.direnis_cell | Direnis Cell | B | Freya (kilima_in12_deity) | loc.cave |
| fac.red_fist_dragons | Red Fist Dragons | D# | Kive (kilima_in12_rebel) | loc.workshop |
| fac.dust_parade | Dust Parade | A | Yeri (kilima_in12_explorer) | loc.oasis |

**Union Corp (Ionian) — 12 factions (ministries):**

| ID | Name | Root note | Leader | Type | Agora barrio |
|----|------|-----------|--------|------|-------------|
| fac.uc_culture | Culture | C | TBD | simulated | TBD (woman name) |
| fac.uc_education | Education | C# | TBD | real | TBD |
| fac.uc_energy | Energy | D | TBD | real | TBD |
| fac.uc_defense | Defense | D# | TBD | real | TBD |
| fac.uc_biotech | Biotechnology | E | TBD | real | Katalin Kariko |
| fac.uc_structures | Structures | F | TBD | real | TBD |
| fac.uc_systems | Systems | F# | TBD | real | TBD |
| fac.uc_interior | Interior | G | Saarah (kilima_in12_leader) | simulated | TBD |
| fac.uc_memory | Memory | G# | TBD | simulated | TBD |
| fac.uc_materials | Materials | A | TBD | simulated | TBD |
| fac.uc_engineering | Engineering | A# | TBD | simulated | TBD |
| fac.uc_exterior | Exterior | B | TBD | simulated | TBD |

**Agency SL (Aeolian) — 5 factions:**

| ID | Name | Root note | Leader | Base |
|----|------|-----------|--------|------|
| fac.master_council | Master Council | D | Luka (kilima_in12_hero) — deserts | loc.tower |
| fac.contracts_bureau | Contracts Bureau | null | TBD | null |
| fac.intelligence | Intelligence Department | null | TBD | null |
| fac.marketing | Marketing Division | null | TBD | null |
| fac.net_service | Net Service | null | TBD (Ali is member) | null |

**Amparo Foundation (Lydian) — 4 factions:**

| ID | Name | Root note | Leader | Base |
|----|------|-----------|--------|------|
| fac.vital_care | Vital Care | null | TBD (Nora is member) | loc.nest (probable) |
| fac.open_breath | Open Breath | null | TBD | null |
| fac.ground_zero | Ground Zero | null | TBD | null |
| fac.amparo_refuge | (name TBD) | null | TBD | null |

**Bohemian Academy (Mixolydian) — 4 factions:**

| ID | Name | Root note | Leader | Base |
|----|------|-----------|--------|------|
| fac.grand_library | Grand Library | C# | TBD (Pau is member) | loc.library |
| fac.open_forum | Open Forum | null | TBD | null |
| fac.natural_sciences | Natural Sciences Circle | null | TBD | null |
| fac.arts_collective | Arts Collective | null | TBD | null |

**Cult Order (Locrian) — 2 factions (+2 in review):**

| ID | Name | Root note | Leader | Base |
|----|------|-----------|--------|------|
| fac.high_clergy | High Clergy | null | TBD | loc.cathedral (probable) |
| fac.lower_chapel | Lower Chapel | null | TBD | null |

**Guard Force (Dorian) — 4 factions:**

| ID | Name | Root note | Leader | Base |
|----|------|-----------|--------|------|
| fac.wall_command | Wall Command | null | TBD | loc.first_wall (probable) |
| fac.moon_soldiers | Moon Soldiers | null | TBD | null |
| fac.arena_corps | Arena Corps | null | TBD (Brais is member) | null |
| fac.road_patrol | Road Patrol | null | TBD | null |

**Backdoor (Whole tone) — 0 factions (Dev solo):**

Backdoor is both macro-faction and faction. Single entity. `fac.backdoor`, root_note F#, leader Dev, base loc.backdoor.

**Kilima Lines (Pentatonic major) — 0 factions TBD**

Base: loc.central_station.

**Kilima Mail (Pentatonic minor) — 0 factions TBD**

Base: null (no level 5 location assigned).

### Tasks

- [x] Create new JSON structure with `macro_factions` and `factions` as separate arrays
- [x] Populate all macro-factions (10) with mode, intervals, scale_family
- [x] Populate all confirmed factions with root_note, leader_id, base_location_id
- [x] Mark factions with TBD leaders as `leader_id: null, root_note: null`
- [x] Add `ministry_type: "real" | "simulated"` to Union Corp factions
- [x] Add `agora_barrio` field to Union Corp factions
- [x] Remove the old `subdivisions` array from each faction entry
- [x] Validate: every base_location_id points to a level 5 location in locations.json

**Criterio de éxito:** `len(json["macro_factions"]) == 10`. `len(json["factions"]) >= 34`. Every faction with a confirmed leader has root_note == leader's archetype note.

---

## FL-1: Locations — DONE

Already completed in this session. `locations.json` rewritten with 55 entries, 7 levels. No further work needed.

---

## FL-2: Asignar notas a locations — SIMPLIFIED

Only 4 locations are fixed. All others are seeded in Chronica. FL-2 is done — the `tonic_type: "seeded"` fields are already set. Actual note assignment happens at runtime in Chronica layer.

---

## FL-3: Validación cruzada factions ↔ locations — DONE

**Objetivo:** Verify coherence after FL-0 completes.

- [x] Every faction with base_location_id → that location exists in locations.json at level 5
- [x] Every faction root_note matches its leader's archetype note (where leader is assigned)
- [x] No faction points to a region or area as base (must be level 5 location)
- [x] Relations of kind `based_in` all point faction → level 5 location
- [x] Character current_faction_id matches a valid faction ID in the new structure
- [x] Add test: `test_faction_location_integrity.py` — 6 tests: counts, bases at level 5, root notes, based_in, no member_of→macro

**Criterio de éxito:** 0 inconsistencies. Validation script passed.

---

## FL-4: Update relations.json for new faction IDs — DONE

**Objetivo:** Once FL-0 creates new faction IDs, update relations.json to match.

Changes made:
- `kilima_in12_rebel → fac.anti_group` → `kilima_in12_rebel → fac.red_fist_dragons`
- `kilima_in12_hero → fac.agency` → `kilima_in12_hero → fac.master_council`
- `kilima_in12_innocent → fac.guard` → `kilima_in12_innocent → fac.arena_corps`
- `kilima_in12_deity → fac.anti_group (leader_of)` → `kilima_in12_deity → fac.direnis_cell (leader_of)`
- `kilima_in12_hacker → fac.anti_group (former_friend)` → `kilima_in12_hacker → mfac.anti_group (former_friend)`
- 6 `based_in` source IDs updated from `fac.macro.sub` to `fac.sub` format
- All character `current_faction_id` updated to specific faction IDs

- [x] Map all char→faction relations to specific faction IDs
- [x] Update all relation IDs to reflect new source/target IDs
- [x] Validate: no relation points to a macro-faction ID where it should point to a faction

---

## Execution order

```
FL-0 (rework factions.json) → FL-3 (validate) → FL-4 (update relations)
     → LP-0 (rename in code) → LP-1... (Life Pack)
```

FL-1 and FL-2 are done.

---

## Key decisions from this session

| Decision | Details |
|----------|---------|
| Hot Forno cell eliminated | Cris starts without faction, joins Anti Group during BN1 |
| Forno = character name | Secondary character, leader of the Levi-Montalcini barrio |
| Levi-Montalcini = barrio name | Outsider barrio in Agora where The Recess is |
| Katalin Kariko = barrio name | Biotechnology barrio in Agora where The Nest is |
| All barrio names TBD | Will be renamed to women who revolutionized each sector |
| Golden Cage = new name | Replaces "The Cage" / "La Jaula" |
| Pobla 2 = new name | Replaces "El Poblado" / "The Village" |
| Last Road = new name | Replaces "The Road" / "La Carretera" |
| The Headquarters = new name | Replaces "La Sede" |
| The Workshop = new name | Replaces "El Taller" (with "The") |
| Wall = area (level 4) | Contains The First Wall and The Second Wall (level 5) |
| The Train = region (level 3) | Own territory, same level as Kilima |
| Locations base must be level 5 | Macro-factions don't have bases — factions do |
| Location tonics mostly seeded | Resolved in Chronica by lineage. Only 4 fixed. |
| Zone tags seeded | Districts/barrios/sections assigned per seed |
| Rooms fixed by nature | A garage is always a garage |
| Lockers = level 7 | Movable containers, physical location for items |
| The Recess = abandoned school | Artists, fiesta interrumpida, Cris territory, A# fixed |
| The Cemetery = robot junkyard | Dev passes through, robots fighting to survive |
| The Avenue = Net charging cabins | Kive meets Agency SL, Dev finds him |
| The Central Station = train arrival | Kive + Yeri arrive, split |
| The Plaza = virtual funeral | Net public space |
| The Mortuary = Len's belongings | Golden Cage, post-incineration |
| Recess replaces Forno as fiesta location | The fiesta/cena from the timeline is at The Recess |
| Daycare in The Cave | Children free of chips, Cris discovers them |
| World note = fixed by narrative arc | Changes per BN |
| Territory note = derived | Average or gambling |
| Region notes = seeded | Gambling in Chronica |
| Location notes = 4 fixed + 13 seeded | Seeded resolved in Chronica by lineage |
| Room notes = fixed by nature | Determined by function/use |
| Life Pack mode (major/minor) is global | Affects all intervals across all octaves |
| Harmonic affinity is universal | Same function for any entity pair, octave doesn't matter |

---

## Files ready for Claude Code

| File | Status | Action needed |
|------|--------|---------------|
| `locations.json` | DONE | Ready to use |
| `kilima_locations.md` | DONE | Ready to use |
| `kilima_factions.md` | DONE | Ready to use |
| `factions.json` | DONE | FL-0: split macro_factions + factions arrays. Migrated to worlds/. |
| `relations.json` | DONE | FL-4: all IDs updated. 30 relations. |
| `characters.json` | DONE | LP-0: IDs kilima_in12_*, faction IDs, location IDs all updated. |
| `CLAUDE.md` | DONE | Ready to use |
| `README.md` | DONE | Ready to use |
| `gigagen_roadmap_lifepack.md` | DONE | LP-0 through LP-8 |
| `gigagen_roadmap_factions_locations.md` | DONE | This file |
| `lifepack_estructura.md` | DONE | Conceptual definition |
| `lifepack_template.json` | DONE | Empty template all slots |
| `kilima_in12_rebel_lifepack.json` | DONE | Kive's Life Pack partially filled |
