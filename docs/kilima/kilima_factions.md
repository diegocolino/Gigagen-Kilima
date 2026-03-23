# Kilima Factions — Complete Reference

> Political and organizational structure of Kilima.
> Updated 2026-03-23 to reflect new location names, base rules, and nomenclature.
> For the generic engine, see `gigagen_faction_system.md`.
> For locations, see `kilima_locations.md`.

---

## Faction Architecture

### Terminology

| Term | Definition |
|------|-----------|
| **Macro-faction** | A mode (interval pattern). Defines harmonic identity. No tonic. Template. In code (pre-LP-0): `faction`. |
| **Faction** | Macro-faction + tonic = concrete scale. Has leader, members, territory. In code (pre-LP-0): `subdivision`. |

The rename from `subdivision` → `faction` and `faction` → `macro_faction` in code is milestone LP-0.

### Base Location Rule

Every macro-faction has a `base_location_id` that must point to a level 5 location (not a region or area). This is the physical headquarters where the macro-faction operates from.

### Scale Families in Kilima

| Family | Notes | Macro-factions |
|--------|-------|----------------|
| 7-note (Greek modes) | 7 | Union Corp, Agency SL, Anti Group, Amparo Foundation, Bohemian Academy, Cult Order, Guard Force |
| 6-note (Symmetric) | 6 | Backdoor |
| 5-note (Pentatonic) | 5 | Kilima Lines, Kilima Mail |

### Reserved modes (for NB2/NB3)
- Harmonic minor (7 notes)
- Phrygian dominant (7 notes)

---

## The 10 Macro-factions

### 1. Union Corp — Ionian

**Intervals:** 2-2-1-2-2-2-1
**Character:** Sovereign, order, the facade of the system.
**Base:** The Headquarters (`loc.headquarters`) — Agora
**Function:** Political governance. The 12 ministries represent every sector of society. In reality, 6 ministries are functional and 6 are theater — a design by Flai to channel citizen frustration horizontally while structural decisions are made by the AI.

**Relationship to other macro-factions:**
- Agency SL executes Union Corp's cultural standards and manages Life Packs.
- Guard Force enforces Union Corp's decisions by force.
- Flai (the AI) created Union Corp for psychological stability, not efficiency.

**12 Factions (Ministries):**

| # | Ministry | Note | Apostle | Type | Leader | Agora barrio |
|---|----------|------|---------|------|--------|-------------|
| 1 | Culture | C | Juan (John) | Simulated | TBD | TBD (woman name) |
| 2 | Education | C# | Simón el Zelote | Real | TBD | TBD |
| 3 | Energy | D | Pedro (Peter) | Real | TBD | TBD |
| 4 | Defense | D# | Santiago el Menor | Real | TBD | TBD |
| 5 | Biotechnology | E | Tomás (Thomas) | Real | TBD | Katalin Kariko |
| 6 | Structures | F | Santiago el Mayor | Real | TBD | TBD |
| 7 | Systems | F# | Judas Iscariote | Real | TBD | TBD |
| 8 | Interior | G | Mateo (Matthew) | Simulated | **Saarah (LEA, G)** | TBD |
| 9 | Memory | G# | Judas Tadeo | Simulated | TBD | TBD |
| 10 | Materials | A | Andrés (Andrew) | Simulated | TBD | TBD |
| 11 | Engineering | A# | Felipe (Philip) | Simulated | TBD | TBD |
| 12 | Exterior | B | Bartolomé | Simulated | TBD | TBD |

**Real ministries** (actually affect the system): Education, Energy, Defense, Biotechnology, Structures, Systems.

**Simulated ministries** (theater of control): Culture, Interior, Memory, Materials, Engineering, Exterior. Their purpose: channel frustration, organize identities, prevent citizens from questioning Flai, give the illusion of participation.

**Key narrative element:** Saarah leads Interior — a simulated ministry. She believes she governs. When she discovers her ministry is theater → political break.

**Agora barrios:** Each ministry controls a barrio in Agora. There is a 13th barrio (Levi-Montalcini) that is outsider territory — not controlled by Union Corp. All barrio names will be renamed to women who revolutionized each sector.

---

### 2. Agency SL — Aeolian

**Intervals:** 2-1-2-2-1-2-2
**Character:** The elegant shadow of power. Espionage, media, cultural control.
**Base:** The Tower (`loc.tower`) — Capitol
**Function:** The interface between the system and the citizen. Agency SL manages Life Packs — the system that replaces money in Kilima. Flai calculates each person's contribution, proposes a Life Pack (housing, food, clothing, transport), and Agency SL delivers it. They are also the builders and operators of virtual environments in Net (schools, entertainment, vacations). They control the narrative through media and propaganda, and run espionage operations.

**Relationship to other macro-factions:**
- Executes Union Corp's cultural standards.
- Provides Life Packs calculated by Flai and approved by Union Corp.
- Builds and maintains Net's virtual environments.
- Runs intelligence operations across all macro-factions.

**5 Factions:**

| Faction | Function | Key members |
|---------|----------|-------------|
| Master Council | Governing body, strategic decisions, negotiations with Union Corp | Luka (HER, D) — deserts during NB1 |
| Contracts Bureau | Management of artists, celebrities, careers. Contracts = slavery. | TBD leader |
| Intelligence Department | Espionage, infiltration, surveillance, covert operations | TBD leader |
| Marketing Division | Press, propaganda, narrative control, Yellow Road promotion | TBD leader |
| Net Service | Construction and maintenance of virtual environments in Net | Ali (LOV, F) — member. TBD leader |

---

### 3. Anti Group — Phrygian

**Intervals:** 1-2-2-2-1-2-2
**Character:** Combative, battle-ready, threatening.
**Base:** The Cave (`loc.cave`) — Pobla 2
**Function:** Clandestine opposition. Dissidents, cyberactivists, ex-military. Fights Union Corp, Agency SL, and Flai. Operates through infiltration, propaganda, sabotage, and underground networks.

**3 Factions (Cells):**

| Cell | Root note | Leader | Location | Function |
|------|----------|--------|----------|----------|
| Direnis Cell | B | Freya (DEI, B) | The Cave — Pobla 2 | Command center, strategy |
| Red Fist Dragons | D# | Kive (REB, D#) | The Workshop — Pobla 2 | Direct action, operations |
| Dust Parade | A | Yeri (EXP, A) | The Oasis Suspiro — Last Road | External connections, logistics |

Note: Hot Forno cell eliminated. Cris starts without faction — joins Anti Group during BN1 at The Cave. Forno is now a secondary character, leader of the Levi-Montalcini barrio.

---

### 4. Amparo Foundation — Lydian

**Intervals:** 2-2-2-1-2-2-1
**Character:** Ethereal, idealist, impossible aspiration.
**Base:** The Nest (`loc.nest`) — Agora (Katalin Kariko barrio)
**Function:** Humanitarian aid. In a world where breathing requires expensive chips, food is synthetic, and exiles have no Life Pack, Amparo Foundation is the only thing between the forgotten and death. Operates hospitals, aid programs, and refugee support.

**4 Factions:**

| Faction | Function | Key members |
|---------|----------|-------------|
| Vital Care | Hospital, medical attention, chip maintenance. The Nest, The Clinic, The Infirmary. | Nora (CAR, C) — member. TBD leader |
| Open Breath | CRA (breathing chip) access program for Pobla 2 and marginal zones | TBD leader |
| Ground Zero | Assistance to Discarded, Forgotten, and Dark Zone communities. Food, shelter. | TBD leader |
| (name in review) | Refuge and protection for displaced people, fugitives, Savages | TBD leader |

---

### 5. Bohemian Academy — Mixolydian

**Intervals:** 2-2-1-2-2-1-2
**Character:** Epic, expansive, open to the world.
**Base:** The Library (`loc.library`) — Golden Cage
**Function:** Free thought, uncontrolled culture, authentic human experience. Golden Cage is semi-autonomous, outside Union Corp's direct jurisdiction. Home to Savages (unmodified humans), artists, thinkers. Practices direct democracy. Organizes festivals and art exhibitions. Opposes the Yellow Road philosophy. Serves as intellectual counterweight to the system, cultural refuge, and living memory.

**4 Factions:**

| Faction | Function | Key members |
|---------|----------|-------------|
| Grand Library | Knowledge archive, real history, research. The Library. | Pau (JES, C#) — member. TBD leader |
| Open Forum | Public debate, direct democracy, festivals. Nomad movement operates here. | TBD leader |
| Natural Sciences Circle | Physical world research, biology, organics. Mushrooms, evolution, Stoned Monkey. | TBD leader |
| Arts Collective | Free artistic creation. Music, visual art, performance. | TBD leader |

---

### 6. Cult Order — Locrian

**Intervals:** 1-2-2-1-2-2-2
**Character:** Unstable, void, ritual dissonance.
**Base:** The Cathedral (`loc.cathedral`) — Capitol
**Function:** Religion, prophecy, the supernatural. Custodians of The Prophecy (a girl born under special alignment will be Supreme Sensible and change history). Manages public worship, investigates the Ether, and controls the spiritual narrative. In a world of synthetic everything, Cult Order offers meaning — and uses it as control.

**Connection to The Prophecy:** Len (ORP, E) fulfills The Prophecy. She is initiated into Cult Order at the Capitol funeral ceremony without knowing it. Freya (DEI, B) also falls within the B Locrian scale (B C D E F G A).

**2 Factions (confirmed):**

| Faction | Function |
|---------|----------|
| High Clergy | Religious leadership, The Cathedral, dogma, ceremonies, prophecy interpretation. TBD leader |
| Lower Chapel | Popular religion, sermons, recruitment, street presence. TBD leader |

**2 Factions (in review):**
- Supernatural research branch (Ether, Sensibles — may cross with Agency SL)
- Spiritual movement branch (Awakened absorbed into religious structure)

---

### 7. Guard Force — Dorian

**Intervals:** 2-1-2-2-2-1-2
**Character:** Firm, martial, sustaining.
**Base:** The First Wall (`loc.first_wall`) — Wall
**Function:** The armed force of Kilima. Border control, military operations, prison management, arena entertainment. Enforces Union Corp's decisions physically. Controls who moves between zones of Kilima.

**4 Factions:**

| Faction | Function | Key members |
|---------|----------|-------------|
| Wall Command | Border control, The First Wall + The Second Wall, patrols, zone access enforcement | TBD leader |
| Moon Soldiers | The Colony (lunar prison), Helium-3 extraction, forced labor management | TBD leader |
| Arena Corps | The Coliseum, gladiators, Military School, combat training | Brais (INN, G#) — member. TBD leader |
| Road Patrol | Last Road, Mercenaries, Masks (elite mercenaries), external territory control | TBD leader |

---

### 8. Backdoor — Whole Tone

**Intervals:** 2-2-2-2-2-2
**Character:** Ambiguous, floating, non-place. The harmonic no-man's-land.
**Base:** The Backdoor (`loc.backdoor`) — Pobla 2
**Function:** Clandestine Net access, hacking, digital underground. The Backdoor is the only unauthorized entry point to Net. Dev operates from the most harmonically distant note in the system — F# is the tritone of C, maximum distance from the establishment.

**No factions.** Backdoor is a small, hermetic network. Dev leads it alone.

**Scale:** F# whole tone → F# G# A# C D E. Characters whose notes fall inside: Dev (F#), Len (E), Cris (A#), Luka (D).

**Leader:** Dev (HCK, F#)

---

### 9. Kilima Lines — Pentatonic Major

**Intervals:** 2-2-3-2-3
**Character:** Ancestral, functional, simple.
**Base:** The Central Station (`loc.central_station`) — Capitol
**Function:** Transport of living beings. The Train, The Zeppelin, The Port. Kilima Lines moves people across Kilima, to Golden Cage, and along Last Road. In a world where most people live in cubicles connected to Net, physical movement is a privilege. Kilima Lines controls that privilege.

**Part of the Kilima Service group** (alongside Kilima Mail). Independent macro-factions that share branding but sometimes conflict over shared resources and overlapping roles.

**Factions:** TBD

---

### 10. Kilima Mail — Pentatonic Minor

**Intervals:** 3-2-2-3-2
**Character:** Blues, industrial, survival logistics.
**Base:** TBD (no level 5 location assigned yet)
**Function:** Transport of goods. Cargo, supplies, Life Pack physical components, synthetic food, materials. The supply chain that keeps Kilima alive. More industrial, less visible than Kilima Lines.

**Part of the Kilima Service group** (alongside Kilima Lines). Independent macro-factions that sometimes conflict — a train carrying both passengers and cargo creates jurisdictional friction.

**Factions:** TBD

---

## Character → Macro-faction Assignments

| Character | Note | Archetype | Primary macro-faction | Faction | Role | Secondary |
|-----------|------|-----------|----------------------|---------|------|-----------|
| Kive | D# | REB | Anti Group | Red Fist Dragons | Leader | — |
| Len | E | ORP | Agency SL | (occult branch TBD) | Member | Cult Order (initiated unknowingly) |
| Dev | F# | HCK | Backdoor | — | Leader | Ex-Anti Group |
| Saarah | G | LEA | Union Corp | Interior | Leader | — |
| Cris | A# | CRE | (none — starts unaffiliated) | — | — | Joins Anti Group during BN1 |
| Brais | G# | INN | Guard Force | Arena Corps | Member | — |
| Ali | F | LOV | Agency SL | Net Service | Member | — |
| Pau | C# | JES | Bohemian Academy | Grand Library | Member | — |
| Luka | D | HER | Agency SL | Master Council | Member | Deserts to Anti Group during NB1 |
| Yeri | A | EXP | Anti Group | Dust Parade | Leader | — |
| Nora | C | CAR | Amparo Foundation | Vital Care | Member | — |
| Freya | B | DEI | Anti Group | Direnis Cell | Leader | Cult Order (scale match) |

---

## Flai (The AI)

Flai is **not a macro-faction**. Flai is an omnipresent entity that operates through the system. In code, Flai is a character without skin and with access to all information that other entities have restricted. Flai is multi-relational — connected to every macro-faction, every location, every system.

**Flai's functions:**
- Calculates Life Pack scores for every citizen
- Controls Net, The Eye (surveillance), consciousness transfer technology
- Created Union Corp for psychological stability
- Designed the real/simulated ministry split
- Monitors all macro-factions but cannot subdue Sensibles
- Final arbiter at The Table alongside Union Corp leaders

---

## The Life Pack System (in-world)

There is no money in Kilima. Flai calculates each person's contribution (human, robot, cyborg). Based on this score, Flai proposes a **Life Pack**: housing, clothing, food, transport, and other essentials.

- Each person has a **score** and a **rank**.
- Exceeding a threshold → better Life Pack (move from Pobla 2 to Agora, from Agora to Capitol).
- Dropping below a threshold → worse Life Pack (demotion).
- Life Packs are calculated by Flai, approved by Union Corp, and **delivered by Agency SL**.

This is the mechanism that makes meritocracy feel real in a dystopia where machines do everything. The Yellow Road ideology (promoted by Union Corp via Agency SL's Marketing Division) tells citizens they can climb through talent and effort. In practice, the system is rigged.

Note: the in-world "Life Pack" (economic system) is different from the Gigagen "Life Pack" (character spectrum system). Same name, different concepts. The in-world Life Pack is lore. The Gigagen Life Pack is game architecture.

---

## Secondary Groups (not macro-factions)

These groups exist in Kilima but are not major macro-factions. They may be absorbed, become macro-factions in future narrative blocks, or remain independent social groups.

| Group | Description | Location | Potential link |
|-------|-------------|----------|---------------|
| The Nomads | Counterculture valuing physical experience. Oppose Yellow Road. | Golden Cage | Bohemian Academy (Open Forum) |
| The Mercenaries | Hired soldiers. Protect Union Corp interests. | Last Road | Guard Force (Road Patrol) |
| The Masks | Elite mercenaries. Never fail. Loyalty = money. | Last Road | Guard Force (Road Patrol) |
| The Outcasts (Parias) | Marginalized drug producers. Illegal sales. | Last Road | Reserved (crime macro-faction?) |
| The Forgotten (Olvidados) | Isolated community. Agriculture/hunting. | The Dark Zone | Amparo Foundation (Ground Zero) |
| The Discarded (Descartados) | Exiled for not meeting Union Corp standards. | Dark Zone periphery | Amparo Foundation (Ground Zero) |
| The Awakened (Despiertos) | Social movement challenging AI control. | Various | Cult Order (spiritual branch, in review) |
| Criminal groups | Control The Infrared, The Glow drug. | Net | Reserved (crime macro-faction?) |

---

## Open Items

- [ ] Leader for Anti Group's Forno cell (secondary character named Forno)
- [ ] Name for Amparo Foundation's refuge faction
- [ ] Cult Order: 2 factions in review (supernatural research + spiritual movement)
- [ ] Factions for Kilima Lines and Kilima Mail
- [ ] Leaders for all TBD factions (secondary characters)
- [ ] Len's specific placement within Agency SL (occult branch not yet formalized)
- [ ] All faction root notes for Agency SL (pending leader assignments)
- [ ] Base location for Kilima Mail (no level 5 location assigned)
- [ ] Rename all Agora barrios to women who revolutionized each sector
