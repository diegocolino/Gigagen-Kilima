# Kilima Bible — Index

> This file is the MAP of Kilima's canonical lore.
> It does NOT contain everything — it points to where everything lives.
> Each section has its own file. This is the table of contents.

---

## The Universe

Kilima (within the "Basura Digital" framework) is a techno-political and mystic-digital dystopia. The world is organized around **The Mountain**, a central geographic structure that symbolizes social hierarchy and domination.

For full world background, history, and context:
→ See **kilima_lore.md**

---

## File Index

### Core documents

| File | Contains | Status |
|------|----------|--------|
| `kilima_lore.md` | World background, history, The Mountain, the three revolutions, The Ether, elements system, Sensibles, Animas, Cabinas, Plan Despega, technologies | DONE |
| `kilima_characters.md` | The 12 principals (in12) — identities, lineages, bonds, archetypes, hero types, arc summaries | DONE |
| `kilima_locations.md` | All locations with descriptions, zone levels, faction control | DONE |
| `kilima_factions.md` | The 4 factions — nature, base, leadership, political dynamics, 12 syndicates | DONE |
| `kilima_parked_ideas.md` | Good ideas not needed for Act 1 — NPCs, scenes, world ideas, triads, alchemy | DONE |

### Timeline documents

| File | Contains | Status |
|------|----------|--------|
| `kilima_timeline_bn1.yaml` | NB1 master file — 62 hours, all events, characters, variables, lore, relationships | DONE (v5.0) |
| `kilima_timeline_bn2.yaml` | NB2 master file | NOT STARTED |
| `kilima_timeline_global.yaml` | Global timeline spanning all narrative blocks | NOT STARTED |

### Hero arc documents (one per archetype)

| File | Archetype | Character | Hero type | Status |
|------|-----------|-----------|-----------|--------|
| `kilima_hero_rebel.md` | Rebel | Kive | Tragic hero | TO CREATE |
| `kilima_hero_orphan.md` | Orphan | Len | Mythological hero | TO CREATE |
| `kilima_hero_hacker.md` | Hacker | Dev | Action hero | TO CREATE |
| `kilima_hero_leader.md` | Leader | Saarah | Anti-villain | TO CREATE |
| `kilima_hero_creator.md` | Creator | Cris | Urban hero (antihero) | TO CREATE |
| `kilima_hero_innocent.md` | Innocent | Brais | Redemption hero | TO CREATE |
| `kilima_hero_lover.md` | Lover | Ali | Romantic hero | TO CREATE |
| `kilima_hero_jester.md` | Jester | Pau | Fantasy hero | TO CREATE |
| `kilima_hero_hero.md` | Hero | Luka | Archetypal hero | TO CREATE |
| `kilima_hero_explorer.md` | Explorer | Yeri | Post-apocalyptic hero | TO CREATE |
| `kilima_hero_caregiver.md` | Caregiver | Nora | Protector hero | TO CREATE |
| `kilima_hero_deity.md` | Deity | Freya | Criminal hero | TO CREATE |

Each hero arc document defines:
- The arc steps specific to that hero type
- Which events map to which arc steps
- Which narrative blocks the arc spans
- Trigger chains (how this arc's steps trigger other arcs)

### System documents (Gigagen, not Kilima)

| File | Contains | Status |
|------|----------|--------|
| `CLAUDE.md` | Master context — what the project is, how to work on it | OK (minor updates needed) |
| `ontology.md` | Formal data models — BaseEntity, Relation, WorldState | OK (minor additions needed) |
| `invariants.md` | What's fixed, variable, derived, forbidden | REWRITTEN |
| `roadmap.md` | Development milestones | OK (minor updates needed) |

---

## The 12 Principals — Quick Reference

| ID | Name | Archetype | Note | Hero type | Key bond |
|----|------|-----------|------|-----------|----------|
| char.rebel | Kive | REB | D# | Tragic | Len (sibling), Luka (childhood friends) |
| char.orphan | Len (Helena) | ORP | E | Mythological | Kive (sibling), Nora (maternal figure) |
| char.hacker | Dev (Andrew) | HCK | F# | Action | Len (partner), Freya (predecessor) |
| char.leader | Saarah (Saarah Strike) | LEA | G | Anti-villain | Luka (future partner) |
| char.creator | Cris (Rous) | CRE | A# | Urban/Antihero | Saarah (ally), Freya (mentor) |
| char.innocent | Brais (Brais de Lügen) | INN | G# | Redemption | Kive (friend/spy), Len (Limbo) |
| char.lover | Ali (Alizia Shirokeji) | LOV | F | Romantic | Kive (ex-girlfriend) |
| char.jester | Pau (Paulo) | JES | C# | Fantasy | Kive (best friend), Nora (companion) |
| char.hero | Luka (Luka Karuso) | HER | D | Archetypal | Kive (childhood friends), Saarah (bond) |
| char.explorer | Yeri (Alexis Hieri) | EXP | A | Post-apocalyptic | Group (connector) |
| char.caregiver | Nora | CAR | C | Protector | Len (maternal figure), Kive (serious ex) |
| char.deity | Freya (Freya Megami) | DEI | B | Criminal | Kive (oneiric/intimate), Dev (succession) |

---

## The 4 Factions — Quick Reference

| ID | Name | Base | Leader (NB1) |
|----|------|------|-------------|
| fac.resistance | The Resistance | The Cave | Freya (Dev was previous) |
| fac.agency | The Agency | The Capital | TBD |
| fac.unions | The Unions | The Capital | TBD |
| fac.ai | The AI | The Net | The AI itself |

---

## Key Lore Concepts — Quick Reference

For full details see `kilima_lore.md`.

- **The Orphan**: Len has no mother. Nora is her maternal figure.
- **The Butterfly Clip**: Len's material bond with Air-type Anima. Missing from fake body. Agency captured the Anima.
- **The Limbo**: Subzone of The Net where transferred consciousnesses truly exist.
- **Brais-automaton**: After death, Brais's body is reanimated by Agency as controllable weapon. Real Brais is in Limbo.
- **The Ether**: Natural (Sensibles) vs Synthetic (Capital). Central conflict axis.
- **Sensibles**: People who can perceive Animas. Len is the only Supreme Sensible.
- **62 hours**: NB1 spans exactly 62 hours. Three dawns. The Rebel always dies.
- **Dev's line**: "a self-centered girl and her justice-obsessed brother" — spoken always, accept or refuse.

---

## Narrative Blocks — Overview

| Block | Scope | Primary arcs | Status |
|-------|-------|-------------|--------|
| NB1 | Funeral → Declaration → Cave invasion → Cut to black | Rebel (opens+closes), seeds for all others | DEFINED (v5.0) |
| NB2 | Second Revolution proper | Creator, Hero, Caregiver, Ruler, Innocent (redemption), Fool (transformation) | NOT STARTED |
| NB3 | Third Revolution | Hacker, Orphan | NOT STARTED |
| NB_FINAL | Final War / Metaverse | Orphan (conclusion) | NOT STARTED |

The Rebel's arc is the only one that opens AND closes in NB1.
The Explorer's arc is already complete (happened in Prologue / First Revolution).
The Orphan's arc stretches to the end of the universe.
