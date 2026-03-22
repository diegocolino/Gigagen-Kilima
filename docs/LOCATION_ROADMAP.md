# Location System — Implementation Roadmap

> Roadmap for implementing the harmonic location system.
> Part of the Location & Faction patch. See PATCH_ROADMAP.md for the integrated plan.
> Engine docs: gigagen/gigagen_location_system.md
> Kilima data: kilima/kilima_locations.md

---

## Current state

### What works
- 15 key Act 1 locations defined with IDs, zones, and classes.
- Zone hierarchy documented (Capital > City > Village + external zones).
- Characters have starting locations at H00.
- Simulator moves characters between locations during events.

### What's broken or missing
- `locations.json` uses old faction IDs (fac.resistance, fac.unions, fac.ai).
- No `tonic` field — locations have no harmonic identity.
- No `parent_location_id` — hierarchy is documented but not in data.
- No `secondary_faction_ids` — disputed locations can't be represented.
- Many locations from the zone hierarchy have no IDs or JSON entries.
- No harmonic functions for location-character or location-faction interactions.
- Location-faction control table is outdated.

---

## Tasks

### Data model (Phase 1 of patch)

- [ ] Add `tonic: str | None` to Location model
- [ ] Add `parent_location_id: str | None` to Location model
- [ ] Add `secondary_faction_ids: list[str]` to Location model
- [ ] Keep existing fields (`zone_level`, `biome_tags`, `controlling_faction_id`, `tension`, `access`, `status`)

### Locations.json rewrite (Phase 1 + 3)

- [ ] Update all `controlling_faction_id` to new faction IDs
- [ ] Add `tonic: null` to all locations (filled later)
- [ ] Add `parent_location_id` for hierarchy
- [ ] Add `secondary_faction_ids: []` for all
- [ ] Add missing locations that exist in hierarchy but not in JSON (sub-locations of Cave, Capital, City, etc.)
- [ ] Decide which sub-locations need their own JSON entries vs are just lore

### Tonic assignment (Phase 3)

- [ ] Define 12 lineage notes (or assign directly)
- [ ] Assign tonics to 15 Act 1 key locations
- [ ] Assign tonics to major zone-level locations
- [ ] Verify narrative resonance (Forno should feel like home for Kive/Luka/Cris)
- [ ] Verify political tension (City tonic should create friction with Union Corp AND Anti Group)

### Harmonic functions (Phase 2)

- [ ] `character_location_affinity()` — structural + modal combined
- [ ] `location_instability()` — for disputed zones
- [ ] `control_quality()` — how well a faction fits a location harmonically
- [ ] `location_scale()` — generate the current modal influence

### Simulator integration (Phase 4)

- [ ] Character movement calculates affinity on arrival
- [ ] Faction control changes trigger modal influence recalculation
- [ ] Location instability feeds into event probability
- [ ] Cohesion affected by harmonic fit of territory

### Event-Location integration (Phase 4 — critical)

- [ ] Every event in bn1.yaml must resolve to a `loc.*` ID
- [ ] Update `timeline_maps.json` with complete location mapping (event location names → loc IDs)
- [ ] Events that move characters trigger affinity calculation at destination
- [ ] Events that change faction control (H52-H56 Cave invasion, H16 declaration, H20 Luka turns) trigger modal influence recalculation for ALL characters present
- [ ] Event log entries enriched with: location_id, modal_influence, character_affinities
- [ ] Disputed location events: stacked influences calculated when multiple factions claim same territory

---

## Decisions needed from author

1. Tonic notes for key locations (requires lineage notes or direct choice)
2. Which sub-locations get JSON entries vs remain lore-only
3. La Academia — Bohemian Academy in the Capital or Union Corp?
4. El Puerto — Kilima Lines or uncontrolled?
5. Los Servidores — Union Corp Systems ministry or shared?
6. La Enfermería (Cave) — Amparo Foundation presence inside Anti Group territory?
7. Virtual Net locations — which are Agency SL Net Service?
8. Kilima Mail logistics hubs — where?
