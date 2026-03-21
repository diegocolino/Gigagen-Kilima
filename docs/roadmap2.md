# Roadmap 2 — Consolidation Phase

> Roadmap1 milestones M1–M5 are complete (103 tests passing). Before adding new features, consolidate the foundation (C1–C6).

---

## Current state

- Canonical models implemented and validated (Pydantic v2)
- Kilima worldpack loaded: 12 characters, 4 factions, 15 locations, 25 relations
- Seed-based variation with invariant validation
- Temporal simulation of the 62-hour NB1 timeline
- Interactive console with full command set
- **103 tests passing** across 4 test modules
- Repo pushed to GitHub

---

## C1 — Vocabulary & relation fixes

**Goal:** Every relation kind used in data or documentation exists in code, and vice versa.

**Findings:**
- `future_partner` (Luka ↔ Saarah) documented in invariants.md but missing from `relation.py` RELATION_KINDS and `relations.json`
- `contacted_in_limbo` (Freya ↔ Len) documented but missing from code and data
- `oneiric_bond` vs `oneiric_then_intimate` (Kive ↔ Freya) — inconsistency between invariants.md and relations.json

**Deliverables:**
- [ ] Add `future_partner` and `contacted_in_limbo` to RELATION_KINDS in `src/gigagen/core/relation.py`
- [ ] Resolve `oneiric_bond` / `oneiric_then_intimate` — decide canonical kind, update everywhere
- [ ] Add Luka ↔ Saarah relation to `worlds/kilima/relations.json`
- [ ] Add Freya ↔ Len relation to `worlds/kilima/relations.json`
- [ ] Cross-check all relation kinds: ontology.md ↔ relation.py ↔ relations.json ↔ invariants.md (single source of truth)
- [ ] Tests verifying every relation in invariants.json exists in relations.json

**Success criteria:** Zero undocumented relation kinds. Zero documented-but-missing relations.

---

## C2 — Data completeness audit

**Goal:** All worldpack data files are complete and internally consistent.

**Findings:**
- `worlds/kilima/timelines/bn1.yaml` may be truncated — verify full events section (E01–E24, all 62 hours)
- Agency leader_id is null (documented as TBD)
- 3 characters have no faction (Dev, Cris, Ali) — verify this is intentional per lore

**Deliverables:**
- [ ] Verify bn1.yaml contains complete events section with all hours covered
- [ ] Cross-validate event_rules.json against bn1.yaml events (every rule references a real event)
- [ ] Document why Dev, Cris, Ali have no faction (or assign if lore dictates)
- [ ] Decide on Agency leader — placeholder or TBD with explicit justification
- [ ] Verify all character `current_location_id` values match existing location IDs
- [ ] Verify all faction `base_location_id` values match existing location IDs

**Success criteria:** Every entity reference resolves. No orphan IDs.

---

## C3 — New data files: hero arcs

**Goal:** Create the 12 hero arc documents referenced in kilima_bible.md.

**Findings:** 0 of 12 hero arc files exist. These are needed before M9 (hero arc tracking) from roadmap1.

**Deliverables:**
- [ ] Define hero arc template (arc steps, event mappings, narrative block span, trigger chains)
- [ ] `docs/kilima_hero_rebel.md` — Kive (Tragic hero) — flagship, defines the template
- [ ] `docs/kilima_hero_orphan.md` — Len (Mythological hero)
- [ ] `docs/kilima_hero_hacker.md` — Dev (Action hero)
- [ ] `docs/kilima_hero_leader.md` — Saarah (Anti-villain)
- [ ] `docs/kilima_hero_creator.md` — Cris (Urban hero / antihero)
- [ ] `docs/kilima_hero_innocent.md` — Brais (Redemption hero)
- [ ] `docs/kilima_hero_lover.md` — Ali (Romantic hero)
- [ ] `docs/kilima_hero_jester.md` — Pau (Fantasy hero)
- [ ] `docs/kilima_hero_hero.md` — Luka (Archetypal hero)
- [ ] `docs/kilima_hero_explorer.md` — Yeri (Post-apocalyptic hero)
- [ ] `docs/kilima_hero_caregiver.md` — Nora (Protector hero)
- [ ] `docs/kilima_hero_deity.md` — Freya (Criminal hero)

**Success criteria:** Each file defines arc steps tied to specific NB1 events. kilima_bible.md index fully resolved.

---

## C4 — Code quality & test hardening

**Goal:** Tests validate data integrity, not just model construction.

**Findings:**
- No tests for `validate_invariants()` function
- No tests verifying documented relations exist in data
- No tests for bidirectional relation consistency
- No tests for forbidden state detection

**Deliverables:**
- [ ] Test: `validate_invariants()` passes on valid worldstate
- [ ] Test: `validate_invariants()` rejects deliberately broken worldstate
- [ ] Test: every relation in invariants.json exists in loaded worldstate
- [ ] Test: forbidden states (from invariants.json) are never produced by seed variation
- [ ] Test: all entity cross-references resolve (no orphan IDs)
- [ ] Test: event_rules.json actions produce valid entity states

**Success criteria:** If someone edits a JSON and breaks a canonical constraint, a test catches it.

---

## C5 — Lore verification pass

**Goal:** Docs and data tell the same story. No contradictions between documentation and JSON/YAML.

**Deliverables:**
- [ ] Cross-check kilima_characters.md against characters.json (names, archetypes, lineages, notes)
- [ ] Cross-check kilima_factions.md against factions.json (names, leadership, bases)
- [ ] Cross-check kilima_locations.md against locations.json (names, zones, access)
- [ ] Cross-check kilima_lore.md element list against ontology.md element catalog
- [ ] Cross-check invariants.md rules against invariants.json
- [ ] Reconcile any differences — docs win when describing author intent, data wins when reflecting implementation

**Success criteria:** A reader of the docs and a reader of the data reach the same conclusions about the world.

---

## C6 — Pre-implementation design for roadmap1 M6+

**Goal:** Before implementing Chronica, Strong Contempo, or Animas, design the data structures and validate against lore.

**Deliverables:**
- [ ] Design document: Chronica layer — what data does it need? What does it produce?
- [ ] Design document: Anima assignment — how are animas distributed to characters? What data files are needed?
- [ ] Design document: Strong Contempo — what "complete visible present" means concretely
- [ ] Validate designs against ontology.md layer definitions (Genesis → Theogony → Chronica → Contempo → Existence)
- [ ] Identify any new entity types, relation kinds, or JSON files needed

**Success criteria:** When we start implementing roadmap1 M6, we know exactly what files to create and what models to extend.

---

## Advancement rule

Same as roadmap1: no milestone starts until the previous one is closed and validated.

Each milestone must be:
- Programmable
- Verifiable
- Ontology-respecting
- Free of arbitrariness

---

## Relationship to roadmap1

Roadmap2 milestones C1–C6 slot **between** roadmap1 M5 and M6. Once consolidation is complete, roadmap1 M6+ (Chronica, Strong Contempo, Animas, Hero arc tracking, Godot viewer, Gameplay) resume on a solid foundation.

```
roadmap1: M1 ✓ → M2 ✓ → M3 ✓ → M4 ✓ → M5 ✓ → [consolidation] → M6 → M7 → ...
roadmap2:                                         C1 → C2 → C3 → C4 → C5 → C6
```
