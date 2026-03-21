# Ontología formal de Gigagen

> Definiciones canónicas de los modelos de datos. Este documento es ley.

---

## BaseEntity

Toda entidad real del universo tiene estos campos universales:

```python
class BaseEntity:
    id: str              # Formato: "{type}.{slug}" → "char.rebel", "fac.resistencia"
    entity_type: str     # character | faction | location | item | anima
    name: str            # Nombre canónico (civil en Kilima)
    tags: list[str]      # Etiquetas transversales, no hardcodeadas como campos
    canon_level: str     # "fixed" | "seeded" | "derived"
    description: str     # Una línea. Solo para debugging y lectura humana.
```

### Regla fundamental

- **identity** = lo que define qué ES esa cosa (no cambia entre seeds si es fixed)
- **state** = cómo ESTÁ ahora mismo en esta seed / momento (cambia)

Cada tipo de entidad extiende BaseEntity con campos de identity y state propios.

---

## Tipos de entidad para el arranque

Solo 5 tipos. No más hasta que estos estén sólidos.

### Character

```python
class Character(BaseEntity):
    # Identity (fixed en Kilima para los 12 principales)
    archetype: str           # Código: "REB", "ORP", "HCK", etc.
    note: str                # Nota musical: "D#", "E", "F#", etc.
    hero_type: str           # "tragic_hero", "mythological_hero", "action_hero", etc.
    civil_name: str          # Nombre civil canónico: "Kive", "Len", "Dev"
    role_name: str           # Nombre de rol: "El Rebelde", "La Huérfana"
    lineage: str | None      # Founding lineage: "Radbot", "Amsoni-Meyar", etc. (fixed for in12)
    
    # State (varía por seed/simulación)
    status: str              # "active" | "dead" | "missing" | "captive" | "digitalized" | "transferred" | "automaton"
    current_location_id: str # Referencia a location
    current_faction_id: str | None  # Referencia a facción (puede no tener)
    emotional_load: str      # "neutral" | "grief" | "rage" | "hope" | "fear"
```

**Nota:** `name` (de BaseEntity) = nombre civil como campo principal.

### Faction

```python
class Faction(BaseEntity):
    # Identity
    doctrine_tags: list[str]     # ["insurgent", "underground"], ["control", "coercive"]
    base_location_id: str        # Sede principal
    
    # State
    status: str                  # "active" | "dissolved" | "underground" | "dominant"
    power: float                 # 0.0 a 1.0
    cohesion: float              # 0.0 a 1.0
    leader_id: str | None        # Referencia a character
```

### Location

```python
class Location(BaseEntity):
    # Identity
    zone_level: str              # "high" | "mid" | "low" | "external" | "hidden" | "virtual"
    biome_tags: list[str]        # ["mountain", "industrial"], ["floating", "artistic"]
    
    # State
    status: str                  # "stable" | "tense" | "fragile" | "unstable" | "hidden" | "active" | "breached" | "besieged"
    controlling_faction_id: str | None
    tension: float               # 0.0 a 1.0
    access: str                  # "open" | "restricted" | "sealed" | "clandestine"
```

### Item

```python
class Item(BaseEntity):
    # Identity
    item_kind: str               # "weapon" | "artifact" | "document" | "key" | "symbol"
    slot: str | None             # "hand" | "body" | "mind" | None
    symbol_tags: list[str]
    rarity: str                  # "common" | "rare" | "unique"
    
    # State
    owner_id: str | None
    sealed: bool
```

### Anima

Las ánimas son **entidades plenas** con personalidad, apariencia e historia propia. Son personajes como los humanos, pero habitan otro plano. En La Red se manifiestan con facilidad; en el mundo físico se necesita un don (herencia o aprendizaje).

Hay **16 elementos** (catálogo cerrado) organizados en jerarquía de composición. Las ánimas son instancias de cualquiera de estos elementos.

**Catálogo de elementos:**

| Tier | Elemento | Composición | Afinidad |
|------|----------|-------------|----------|
| Fundamental | Agua | puro | +++ |
| Fundamental | Fuego | puro | +++ |
| Fundamental | Tierra | puro | +++ |
| Fundamental | Aire | puro | +++ |
| Mixto | Nube | Agua + Fuego | ++ |
| Mixto | Barro | Agua + Tierra | ++ |
| Mixto | Hielo | Agua + Aire | ++ |
| Mixto | Metal | Fuego + Tierra | ++ |
| Mixto | Humo | Fuego + Aire | ++ |
| Mixto | Polvo | Tierra + Aire | ++ |
| Truncado | Lava | Agua + Fuego + Tierra | + |
| Truncado | Humedad | Agua + Fuego + Aire | + |
| Truncado | Ceniza | Agua + Tierra + Aire | + |
| Truncado | Tormenta | Fuego + Tierra + Aire | + |
| Supremo | Éter Natural | los 4 fundamentales | * |
| Supremo | Éter Sintético | los 4 fundamentales (artificial) | * |

El Éter existe en dos formas: natural (ligado a los Sensibles) y sintético (lo que La Capital intenta fabricar).

```python
class Anima(BaseEntity):
    # Identity
    element: str                 # Uno de los 16 elementos del catálogo
    temperament_tags: list[str]  # ["volatile", "purifying"], ["calm", "deep"]
    visibility_class: str        # "visible" | "sensitive_only" | "supreme_only" | "hidden"
    personality: str             # Descripción breve de su carácter propio
    
    # State
    bonded_character_id: str | None
    stability: float             # 0.0 a 1.0
    manifestation_level: float   # 0.0 a 1.0
    current_plane: str           # "physical" | "red" | "dormant"
```

Las ánimas tienen relaciones propias (con su portador, con otras ánimas, con localizaciones) usando el mismo sistema de Relation.

---

## Relation (objeto de primera clase)

Las relaciones NO van embebidas dentro de entidades. Son objetos independientes.

```python
class Relation:
    id: str              # Formato: "rel.{source}.{target}.{kind}"
    source_id: str       # Referencia a entidad origen
    target_id: str       # Referencia a entidad destino
    kind: str            # Tipo de relación (ver vocabulario abajo)
    weight: float        # 0.0 (débil) a 1.0 (máxima)
    polarity: int        # -1 (hostil/negativa), 0 (neutra), 1 (positiva)
    tags: list[str]      # ["core", "political", "personal", "structural"]
    canon_level: str     # "fixed" | "seeded" | "derived"
    origin_event_id: str | None  # De dónde nació esta relación
```

### Sistema armónico de afinidad (propiedad calculada)

Cuando ambas entidades de una relación tienen nota (archetype → note), el intervalo musical entre ellas produce una **afinidad armónica base**. Este valor NO se almacena: se calcula.

```
harmonic_affinity(note_a, note_b) → float entre -1.0 y 1.0
```

Tabla de referencia de intervalos (semitonos → efecto):

| Semitonos | Intervalo | Efecto base |
|-----------|-----------|-------------|
| 0 | Unísono | Identidad / resonancia total |
| 1 | Segunda menor | Tensión fuerte / fricción |
| 2 | Segunda mayor | Tensión moderada |
| 3 | Tercera menor | Tensión dramática / vínculo emocional tenso |
| 4 | Tercera mayor | Afinidad emocional / armonía cálida |
| 5 | Cuarta justa | Estabilidad / soporte |
| 6 | Tritono | Némesis / tensión máxima / disonancia |
| 7 | Quinta justa | Aliado natural / armonía fuerte |
| 8 | Sexta menor | Melancolía / vínculo agridulce |
| 9 | Sexta mayor | Afinidad dulce / complemento |
| 10 | Séptima menor | Tensión dinámica / empuje |
| 11 | Séptima mayor | Tensión elevada / aspiración |

Este valor base se **modifica** por: facción compartida, relaciones comunes, historial de eventos, estado emocional actual. El peso final influye en el `weight` efectivo de la relación en runtime.

### Vocabulario cerrado de relation.kind

**Personaje ↔ Personaje:**
- `sibling` — hermanos
- `partner` — pareja actual
- `ex_partner` — expareja
- `close_friend` — amistad fuerte
- `former_friend` — amistad rota o pasada
- `rival` — rivalidad activa
- `mentor` — tutoría/protección
- `distrust` — distrust
- `childhood_best_friends` — grew up together
- `oneiric_bond` — dream connection
- `maternal_figure` — maternal/paternal figure
- `leadership_succession` — one succeeded the other as leader
- `reunited_in_limbo` — reconnected after transfer to The Limbo
- `automaton_of` — the automaton body of a transferred consciousness
- `future_partner` — destined romantic partners (meet during NB1, bond deepens post-NB1)
- `contacted_in_limbo` — one entity contacts another in The Limbo (telepathic/oneiric link)

**Personaje ↔ Facción:**
- `member_of` — miembro
- `leader_of` — líder
- `allied_with` — aliado externo
- `opposed_to` — oposición
- `infiltrated_in` — infiltrado

**Personaje ↔ Location:**
- `lives_in` — reside
- `tied_to` — vínculo identitario
- `hidden_in` — escondido

**Facción ↔ Location:**
- `based_in` — sede
- `controls` — controla
- `influences` — influencia indirecta
- `hides_in` — presencia clandestina

---

## WorldState

El estado cargado en runtime para una seed concreta.

```python
class WorldState:
    world_id: str            # "world.kilima"
    seed: int                # Seed determinista
    phase: str               # "block_1_start" | "block_1_mid" | "second_revolution" | etc.
    description: str
    
    entities: dict[str, BaseEntity]     # Todas las entidades indexadas por id
    relations: list[Relation]           # Todas las relaciones activas
    
    active_faction_ids: list[str]
    active_location_ids: list[str]
    
    tags: list[str]
```

---

## Cosas que NO son entidades (todavía)

| Concepto | Clasificación actual | Razón |
|----------|---------------------|-------|
| Archetype | Catálogo maestro | No vive en el mundo, lo define |
| Note | Catálogo maestro | Atributo, no entidad |
| Element | Catálogo maestro | Categoría abstracta |
| Rule | Definición sistémica | Pertenece a Gigagen, no al mundo |
| Skill | Capacidad por catálogo | Referenciada, no instanciada (aún) |
| Lore | Salida derivada | Documentación, no runtime |
| Lineage | Estructura histórica | Se promocionará a entidad si hace falta |
| Symbol | Etiqueta semántica | Va en tags por ahora |
| Event | Registro temporal | Se implementará como suceso, no entidad |

---

## Regla de oro para añadir campos

Antes de añadir cualquier campo nuevo a cualquier modelo, preguntar:

1. ¿Es identidad o estado?
2. ¿Es universal o específico de un tipo?
3. ¿Es dato propio o referencia a otra entidad?
4. ¿Es fixed, seeded o derived?
5. ¿Puede ir como tag en vez de campo?

Si no se puede responder con claridad, **no se añade**.
