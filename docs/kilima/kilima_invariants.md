# Invariants of Kilima

> What cannot change, what can vary, and what is forbidden.

> **TODO:** This file mixes Kilima-specific invariants with generic engine rules.
> A `gigagen/gigagen_invariants.md` should be created that defines the generic
> invariant system (fixed/seeded/derived/variable/forbidden framework), and this
> file should only contain Kilima-specific rules that load into that system —
> same pattern as faction_system.md (engine) + kilima_factions.md (worldpack).

---

## Universal invariants (every seed, every run)

### World structure (fixed)
- The Mountain exists with its hierarchy: Capital (top), City (mid), Village (bottom)
- The Cage exists as semi-autonomous floating city
- The Cave exists as Resistance headquarters (historically impenetrable — breached for the first time in NB1)
- The Net exists as digital metaverse controlled by The AI
- The Limbo exists as subzone within The Net where transferred consciousnesses truly reside
- The Forno exists as a place in Kilima — Luka's old workplace, Kive and Luka's childhood place

### Factions (fixed)
- Exist: The Resistance, The Agency, The Unions, The AI
- Each has a fixed nature and base location
- The Resistance is led by Freya (at NB1 start). Dev was the previous leader.

### The 12 principals (fixed)
- Exactly 12 central nodes exist
- Each has a fixed archetype, note, and hero type
- Each has a canonical civil name
- Structural relationships between them are fixed (see below)
- Equal in ontological rank (relative centrality varies by seed/phase)

| Character | Archetype | Note | Hero type |
|-----------|-----------|------|-----------|
| Kive | Rebel (REB) | D# | Tragic hero |
| Len | Orphan (ORP) | E | Mythological hero |
| Dev | Hacker (HCK) | F# | Action hero |
| Saarah | Leader (LEA) | G | Anti-villain |
| Cris | Creator (CRE) | A# | Urban hero (antihero) |
| Brais | Innocent (INN) | G# | Redemption hero |
| Ali | Lover (LOV) | F | Romantic hero |
| Pau | Jester (JES) | C# | Fantasy hero |
| Luka | Hero (HER) | D | Archetypal hero |
| Yeri | Explorer (EXP) | A | Post-apocalyptic hero |
| Nora | Caregiver (CAR) | C | Protector hero |
| Freya | Deity (DEI) | B | Criminal hero |

### Fixed relationships
| Source | Target | Kind | Notes |
|--------|--------|------|-------|
| Kive | Len | sibling | Brother-sister |
| Dev | Len | partner | Romantic partners |
| Kive | Ali | ex_partner | Ali is Kive's ex-girlfriend |
| Kive | Nora | ex_partner | Most serious ex. Nora became Len's maternal figure through this. |
| Kive | Pau | close_friend | Best friend |
| Kive | Brais | close_friend | Close friends — Brais secretly works for The Agency |
| Kive | Luka | childhood_best_friends | Grew up together. This bond breaks Luka free from Agency. |
| Kive | Saarah | former_friend | |
| Brais | Nora | partner | Current partners |
| Luka | Saarah | future_partner | Meet at NB1 funeral, bond deepens, eventually marry |
| Nora | Len | maternal_figure | Nora is Len's strongest maternal figure. Len has no mother (the Orphan). |
| Freya | Dev | leadership_succession | Dev was Resistance leader before Freya. He stepped down. |
| Kive | Freya | oneiric_bond | Dream connection (deepens to intimacy at The Cave during NB1). |
| Len | Brais | reunited_in_limbo | After both die, reunited in The Limbo. |
| Freya | Len | contacted_in_limbo | Freya contacts Len; Len reads her mind (prophecy, ether, genetic plan). |

### Fixed faction memberships (NB1 start)
| Character | Faction | Kind |
|-----------|---------|------|
| Kive | Resistance | member_of |
| Freya | Resistance | leader_of |
| Dev | Resistance | former_leader_of (now independent) |
| Luka | Agency | member_of (turns during NB1 — fixed) |
| Brais | Agency | infiltrated_in (secret) |

### Fixed faction-location bonds
| Faction | Location | Kind |
|---------|----------|------|
| Resistance | The Cave | based_in |
| Agency | The Capital | based_in |
| Unions | The Capital | based_in |
| AI | The Net | based_in |

---

## NB1-specific invariants

### Duration and structure (fixed)
- NB1 spans exactly 62 hours
- Three dawns: H00 (funeral), H30 (travel), H62 (death)
- Post-credits exist outside the 62-hour clock

### Fixed events (cannot change between seeds)
- Len is already dead physically at NB1 start
- Her consciousness exists in The Limbo (subzone of The Net)
- Four simultaneous funerals happen at H00
- Kive declares war on The Agency at H16
- Luka turns from Agency to Resistance (fixed — triggered by seeing Kive broken at The Forno, H20)
- Brais is killed at H20 (always dies defending Kive's people)
- Brais's consciousness is transferred to The Limbo (always happens)
- Brais's body is reanimated as Agency-controlled automaton (always happens)
- Nora and Pau are kidnapped at H20 (parallel with Forno dinner)
- Nora discovers the missing Butterfly Clip at H08 (keeps it secret until NB2)
- Freya contacts Len in The Limbo at H10
- The army invades The Cave at H52-H56 (historic first breach)
- They followed Yeri's route (Yeri's connector ability = the fatal flaw)
- Brais-automaton fires at Kive at H62
- The Rebel always dies (H62 or early NB2)
- Dev speaks the line "a self-centered girl and her justice-obsessed brother" (always, accept or refuse)

### Variables (only 3 in NB1)

| ID | Name | Event | Hour | Type | Options |
|----|------|-------|------|------|---------|
| VAR_DEV | Dev's decision | E09 | H35 | binary 50/50 | participates / refuses |
| VAR_BRAIS | Brais's Agency response | E07B | H16 | binary | lies (protects Kive) / betrays (full intel) |
| VAR_ENDING | Who dies at H62 | E24 | H62 | binary | Kive dies / Pau intercepts and dies |

### Variable effects

**VAR_DEV:**
- If participates: Dev opens The Backdoor for Kive, builds declaration broadcast infrastructure, stays at Cave
- If refuses: Dev leaves Cave at H49, sees army movement, Len contacts him telepathically at H51, he returns with Backdoor crew at H62 (too late for the shot, saves everyone else)
- Affects: NB2 resources, declaration reach, Dev's guilt arc

**VAR_BRAIS:**
- If lies: Kidnapping happens at H20 (standard timing). Group has full Forno evening.
- If betrays: Kidnapping accelerated to ~H19. Less time before the news hits.
- Affects: Cohesion, group preparation time, emotional weight

**VAR_ENDING:**
- Ending A: Kive dies at H62. Never sees the revolution. Pau lives → Utopia in NB2 (mushroom transforms him, driven to find way to revive Kive but can't).
- Ending B: Pau intercepts bullet. Pau dies. Kive survives → dies early in NB2. Pau → Utopia in NB2 (mushroom revives him — fantasy hero death/resurrection arc).
- THE REBEL ALWAYS DIES.

### Derived variables (emerge from simulation)
- Group cohesion score (cumulative from event impacts)
- Individual emotional states per character per hour
- Relationship weight shifts (bonds deepen or strain)
- Declaration reach / audience size
- Casualties during the Cave siege (besides the main shot)

### Outcome vocabulary (closed)

**life_state:** alive | dead | missing | captive | digitalized | transferred | automaton
**bond_state:** together | separated | broken | unresolved | deepened
**political_alignment:** aligned | conflicted | betrayed | radicalized | turned
**capture_state:** free | captured | escaped | released | rescued
**visibility_state:** public | hidden | exposed | underground | besieged
**location_state:** stable | tense | fragile | unstable | breached | fallen

---

## Prohibitions (forbidden)

Things the system MUST NEVER produce:

### Identity
- Remove any of the 12 from canon
- Change a character's root archetype
- Change a character's note
- Change a character's hero type
- Len ceases to be The Orphan
- Kive ceases to be The Rebel
- Kive and Len cease to be siblings
- Dev has no relevance to Len
- Nora is not Len's maternal figure

### Relationships
- Delete fixed relationships
- Invent blood relations not in canon
- Kive and Luka are not childhood friends
- Ali was not Kive's ex
- Freya was not Dev's successor as Resistance leader

### Scenario
- Start NB1 with Third Revolution active
- Delete Len's initial death
- The Mountain doesn't exist
- The Net doesn't exist
- The Cave is not breached in NB1 (it IS breached — first time in history)
- The Rebel survives NB1 AND NB2 (impossible — always dies)
- Utopia is visited in NB1 (moved to NB2)
- Brais survives NB1 physically (always dies at H20)
- Luka doesn't turn (always turns)

### Lore
- The Butterfly Clip doesn't exist
- The Limbo doesn't exist
- Brais-automaton concept is removed
- Len's telepathic abilities (H51) are removed

---

## Summary

```
fixed    → Cannot change between seeds
seeded   → Fixed at run start, coherent during run, varies between seeds
derived  → Emerges from simulation
variable → Explicitly decided (only 3 in NB1)
forbidden → System MUST NOT produce this
```
