# CLAUDE.md — Contexto maestro del proyecto Gigagen / Kilima

> Este archivo es la brújula del proyecto. Léelo antes de tocar cualquier código.

---

## Qué es este proyecto

Hay dos cosas distintas que viven juntas:

### Gigagen (el framework)

Un programa en Python que funciona como **compilador de universos relacionales**. No es un generador de mapas ni un creador de NPCs al uso. Es un sistema para:

- Cargar datos canónicos de un universo (worldpack)
- Generar estados de mundo reproducibles por seed
- Aplicar reglas de identidad, relación e historia
- Producir un presente simulable donde las entidades tienen vínculos, herencias y tensiones

Gigagen es **reusable**. En teoría, otro worldpack podría generar otro universo distinto.

### Kilima (el worldpack)

El universo concreto del autor. Una distopía techno-política y místico-digital organizada en torno a La Montaña, con 12 personajes centrales, facciones, localizaciones y una historia de revoluciones.

Kilima **no es genérico**. Es la obra autoral construida con Gigagen.

### La relación entre ambos

```
Gigagen = gramática / motor / framework
Kilima  = poema / mundo / instancia concreta
```

- Gigagen define *cómo se puede generar un universo*
- Kilima define *qué universo concreto quiero generar*
- Gigagen genera variación → Kilima impone identidad
- Una seed no crea "otro mundo": crea otra trayectoria válida de Kilima

**Regla de trabajo:** cada vez que definas algo, pregunta: ¿esto pertenece a Gigagen o a Kilima?

---

## Principio ontológico fundamental

### Todo es entidad. Toda entidad está arquetipizada.

Esta es la idea más importante del proyecto. No hay jerarquía de tipos donde unos son "nodos" y otros son "registros" o "catálogos". Todo — personajes, objetos, locations, ánimas, skills, eventos, facciones — es una entidad con un arquetipo asignado. Un arquetipo = una nota cromática. Hay 12 arquetipos universales, 12 notas.

Esto significa que cualquier entidad puede relacionarse armónicamente con cualquier otra. Un personaje tiene afinidad con un objeto, con una location, con otro personaje, con un evento — y esa afinidad se calcula exactamente igual en todos los casos: intervalo entre sus notas.

### El sistema es relacional, no taxonómico

Una entidad no vale por sí sola; vale por cómo se relaciona con las demás. La singularidad de cada entidad nace de su posición en la red de relaciones, no de propiedades internas.

### Clasificación de estado

Las entidades tienen propiedades que se clasifican según su mutabilidad:

| Categoría | Significado |
|-----------|-------------|
| **fixed** | No puede cambiar entre seeds. Identidad. |
| **seeded** | Se decide al iniciar la simulación, permanece coherente en esa run |
| **derived** | Emerge de relaciones y reglas durante la simulación |
| **forbidden** | Trayectorias que el sistema NO debe producir |

---

## El sistema armónico

### Base: nota contra nota

La función armónica fundamental es simple: dadas dos notas, calcula el intervalo en semitonos y devuelve una afinidad base (float). Es universal. No cambia.

```
harmonic_affinity(note_a, note_b) → float
```

Unísono = máxima resonancia. Quinta justa = pilar. Tercera = color. Tritono = máxima tensión. Semitono = fricción.

### La armonía es universal

Al estar todo arquetipizado, la misma función calcula la afinidad entre cualquier par de entidades: personaje ↔ personaje, personaje ↔ objeto, personaje ↔ location, objeto ↔ evento, etc. No hacen falta funciones específicas por tipo. La nota es la nota.

### La octava no afecta a la afinidad

La octava (en qué registro del Life Pack vive una entidad) es organización, no resonancia. D# contra A# siempre es quinta justa, da igual si uno es un personaje y el otro es un objeto. La octava determina el tipo de slot y la lógica de llenado, pero no el cálculo armónico.

### Modo global

Cada Life Pack tiene un modo (mayor o menor) que afecta a cómo se interpretan los intervalos de tercera, sexta y séptima en todos los slots. Mayor = expresión integrada/expansiva. Menor = expresión tensionada/contractiva. No es moral: es color armónico. Un personaje puede cambiar de modo durante la narrativa — y cuando lo hace, todo su espectro se recalcula.

### Alteraciones

Las alteraciones (mayor/menor/aumentada/disminuida) cambian la cualidad del vínculo entre una entidad y un slot, sin cambiar qué entidad ocupa el slot. Son dinámicas: mutan durante la narrativa.

- Mayor → vínculo luminoso, dominio
- Menor → vínculo con peso, carga
- Aumentada → obsesión, dependencia, descontrol
- Disminuida → roto, perdido, traicionado

---

## El Life Pack

El Life Pack es el espectro completo de existencia de un personaje, organizado por octavas de frecuencia. Un personaje es: su tónica + las entidades en cada grado de su Life Pack.

### Mapa de octavas

| Octava | Tipo | Lógica de llenado | Se activa en |
|--------|------|-------------------|-------------|
| infrasonidos | Pasado muerto (Theogony, Chronica) | Por definir | — |
| 0 | Lore (definición arquetípica) | 12 slots fijos por arquetipo, iguales para todos | Genesis |
| 1 | Ánimas (espíritus elementales) | Variable por elementos del personaje | Theogony |
| 2 | Linajes | Slot único | Theogony |
| 3 | Locations | Acorde interno (tónica, 3m, 5J + desbloqueables) | Contempo |
| 4 | Objetos | Acorde interno | Contempo |
| 5 | Skills | Acorde interno | Contempo |
| 6 | Reservada | Por definir | — |
| 7 | Personajes (relaciones) | 12 slots completos por intervalo | Chronica |
| 8 | Eventos (cicatrices narrativas) | Invariantes + variables por resolver | Chronica |
| ultrasonidos | Futuro (variantes, bifurcaciones) | Por definir | — |

### Reglas del Life Pack

- Cada octava tiene su propia lógica de llenado. No hay regla universal.
- Los slots se desbloquean durante la narrativa (eventos → unlock de locations, objetos, etc.)
- La octava 0 es constitucional: define cómo el personaje se relaciona con cada arquetipo. No muta.
- La octava 1 depende de los elementos innatos. Dominar un elemento desbloquea un slot de ánima. Fusionar elementos desbloquea más slots sin eliminar los anteriores.
- Las octavas 3, 4, 5 usan lógica de acorde interno: 4 slots iniciales (tónica, 3m, 3M, 5J), el resto se desbloquea.
- La octava 7 se auto-calcula desde el roster de personajes disponible.
- La octava 8 contiene invariantes (siempre pasan) y variables (la simulación debe resolverlas).

### Documentación del Life Pack

| Archivo | Contenido |
|---------|-----------|
| `lifepack_estructura.md` | Definición conceptual de todas las entidades y relaciones |
| `lifepack_template.json` | Plantilla JSON vacía con todos los slots |
| `gigagen_roadmap_lifepack.md` | Milestones de implementación LP-0 a LP-8 |
| `kilima_in12_rebel_lifepack.json` | Life Pack de Kive (primer ejemplo, parcialmente rellenado) |

---

## El eje elemental-anímico

- Las Ánimas son entidades plenas: tienen personalidad, arquetipo, nota. Son personajes como los humanos, pero no viven en el plano físico de la misma manera.
- En La Red se manifiestan con facilidad. En el mundo físico, se necesita un don.
- Hay 16 elementos en jerarquía: 4 Fundamentales (Agua, Fuego, Tierra, Aire) → 6 Mixtos → 4 Truncados → Éter (Supremo).
- Los elementos son condiciones de acceso a la octava 1 del Life Pack. No son entidades en sí.
- Caso especial: Len tiene Éter de base (sensible suprema, espectro elemental completo). Dev tiene octava 1 vacía (emula efectos elementales vía skills + objetos tecnológicos — poder condicional).

---

## La escalera de descendencia (arquitectura de capas)

El universo no aparece de golpe. Se genera por capas. Cada capa activa octavas del Life Pack y tiene responsabilidad clara sobre qué entidades instancia y cuándo.

Documento completo: `docs/gigagen/gigagen_offspringladder_ontology.md`

### Los cinco escalones

#### 1. Genesis — Universo Primigenio
**Entrada:** `x.json` (Eva/Software — leyes, arquetipos, intervalos, tipos de relación) + `y.json` (Adán/Hardware — notas cromáticas, elementos, tiers, modos, niveles)
**Sin seed. Determinista.**

Carga las leyes del universo y el catálogo de materia. Valida que `y.json` respeta las leyes de `x.json`. Produce WORLD (location nivel 1) — el único artefacto concreto. No hay entidades todavía, solo las condiciones para que existan.

Activa: octava 0 (lore arquetípico)

**En Kilima:** `x.json` = Len (software, lo intangible). `y.json` = Dev (hardware, lo tangible). El evento final del universo — la fusión Dev + Len + IA + toda la conciencia humana — es X + Y convergiendo. El atractor inevitable superpuesto en todos los finales.

#### 2. Theogony — Universo Mágico
**Entrada:** WorldState de Genesis + datos del worldpack
**Sin seed. Define las reglas del gambleo pero no lanza los dados.**

Instancia las fuerzas primordiales anteriores a la historia: ánimas (los 16 elementos como entidades), linajes (con `element_pool` fijo pero elemento concreto sin resolver), locations nivel 2, items tier S, skills tier S.

Los linajes tienen campos **fixed** (id, name, archetype, note, element_pool, tier) y campos **seeded** declarados pero vacíos (element, founding_era, origin_location_id) — Chronica los resuelve.

Activa: octavas 1 y 2 (ánimas, linajes)

#### 3. Chronica — Universo Impreso
**Entrada:** WorldState de Theogony + worldpack data + **seed**
**La seed entra aquí. Una sola seed. Se consume con RNG por namespace.**

```python
rng_elements  = Random(seed + "elements")   # elemento de cada linaje
rng_founders  = Random(seed + "founders")   # quién fundó qué
rng_modes     = Random(seed + "modes")      # modos a macrofactions
rng_events    = Random(seed + "events")     # resolución de macro/micro-events
rng_locations = Random(seed + "locations")  # asignación locations a factions
rng_2gen      = Random(seed + "2gen")       # characters 2gen
```

Genera en orden: elementos de linajes → macrofactions emergen (agrupando linajes con elementos compatibles, modo heredado del linaje fundador) → characters 1gen (Founders Tier S, Leaders Tier A, Notaries Tier B) → macro-events históricos resueltos → locations niveles 3-6 con tonic derivado → micro-events → characters 2gen.

Las macrofactions **no se predeclaran** — emergen de la historia. Su modo no se asigna arbitrariamente, se hereda del linaje fundador.

Activa: octavas 7 y 8 (personajes/relaciones, eventos/cicatrices)

#### 4. Contempo — Universo Presente
**Entrada:** WorldState de Chronica
**Determinista dado Chronica.**

Materializa el presente: IN12 con estado H00, Minor Wheel para secundarios y terciarios por afinidad harmónica, árbol de eventos (BN1 y actos futuros). El Life Pack completo cobra sentido aquí.

X + Y converge en Contempo como atractor — el evento final está superpuesto en todos los finales posibles. BN1 es el primer paso.

Activa: octavas 3, 4 y 5 (locations, objetos, skills)

#### 5. Existence — Universo Jugable
**Determinista. Base conceptual — implementación futura.**

El jugador entra al universo: crea un personaje, interactúa con IN12, accede a facciones, ocupa locations. El universo deja de ser un modelo y se convierte en una experiencia.

### Regla fundamental de la Escalera

Cada escalón recibe un `WorldState` y devuelve un `WorldState` más completo. El pipeline es una cadena de transformaciones:

```python
ws = genesis.run(ws, {"x": x_path, "y": y_path})
ws = theogony.run(ws, worldpack_config)
ws = chronica.run(ws, worldpack_config, seed=seed)
ws = contempo.run(ws, worldpack_config)
# existence.run() — futuro
```

**No tocar esta arquitectura. Conservarla como esqueleto maestro.**

---

## Nomenclatura (IMPORTANTE)

| Término correcto | Definición | Término obsoleto |
|-----------------|-----------|-----------------|
| **Macro-facción** | Modo armónico (Dórico, Frigio...). Sin tónica. Plantilla. | "facción" en código antiguo |
| **Facción** | Macro-facción + tónica = escala concreta. Operativa. Tiene líder, miembros, territorio. | "subdivisión" en código antiguo |
| **kilima_in12_{archetype}** | Patrón de ID para personajes de la primera colección de 12 | `kilima_{archetype}` |
| **x.json** | Fichero primordial de leyes (Eva/Software/Len) | — |
| **y.json** | Fichero primordial de catálogo (Adán/Hardware/Dev) | — |
| **Linaje** | Familia primordial con element_pool. Nace en Theogony. | — |

El renombrado macro-facción/facción en código es LP-0 (primer milestone del roadmap del Life Pack).

---

## Metas

### Meta faro

Conseguir la primera simulación que relacione todos los tipos de entidades en todo el espectro armónico. Cargar el Life Pack del Rebelde (Kive) y ver cómo muta e interactúa durante la simulación del BN1. **Cerrar el sistema armónico global antes de seguir metiendo lore, personajes, locations, eventos.**

Esta meta requiere que la Escalera de Descendencia esté implementada. El Patch 2 es el prerrequisito.

### ✅ Patch 2 — Completado (marzo 2026)

La Escalera de Descendencia está implementada como arquitectura de código real:

| Archivo | Cambio |
|---------|--------|
| `src/gigagen/layers/genesis.py` | Carga x.json + y.json, valida, produce catalogs + loc.world |
| `src/gigagen/layers/theogony.py` | Instancia 16 animas, 13 linajes, locations L2 |
| `src/gigagen/layers/chronica.py` | SeedEngine con namespaces, resuelve elementos de linajes |
| `src/gigagen/layers/contempo.py` | Carga IN12, factions, relations, lifepacks, seed variation |
| `src/gigagen/layers/__init__.py` | `run_pipeline()` ejecuta las 5 capas en secuencia |
| `src/gigagen/io/load_worldpack.py` | Refactorizado a **55 líneas** (era 260). Delega al pipeline |
| `src/gigagen/io/load_legacy.py` | Lógica legacy para worldpacks sin x.json/y.json |
| `src/gigagen/core/entity.py` | Añadido modelo `Lineage` (NOT archetypized) |
| `src/gigagen/core/world_state.py` | `DescendenceStep` literal, `Catalogs` model |
| `worlds/kilima/x.json` | Leyes del universo (Eva/Software) |
| `worlds/kilima/y.json` | Catálogo de materia (Adán/Hardware) |
| `worlds/kilima/lineages.json` | 13 linajes canónicos de Kilima |

**342 tests passing.** Pipeline funcional: `genesis → theogony → chronica → contempo`

Ver: `docs/gigagen/gigagen_patch2_briefing.md` y `docs/gigagen/gigagen_patch2_roadmap.md`

### Milestones técnicos (después del Patch 2)

Detalle completo en `gigagen_roadmap_lifepack.md`. Resumen:

1. **LP-0** — Renombrado global (subdivision → faction, faction → macro_faction, IDs con in12)
2. **LP-1** — Modelo LifePack en Pydantic (genérico, sin datos de Kilima)
3. **LP-2** — Loader de lifepacks desde worldpack
4. **LP-3** — Modo global (mayor/menor) como propiedad del Life Pack
5. **LP-4** — Octava 7 auto-calculada desde roster de personajes
6. **LP-5** — Unlock de slots durante simulación via event rules
7. **LP-6** — Octava 8 integrada con sistema invariant/variable
8. **LP-7** — TUI para inspección del Life Pack
9. **LP-8** — Ánimas (octava 1, estructura base)

### Lo que NO toca ahora

- `animas.json` con datos ricos de Kilima (Patch 3)
- Datos concretos de Kilima para Chronica (macro-events, characters 2gen, locations L3-L6)
- God Mode TUI
- Minor Wheel en Contempo
- Árbol de eventos de BN1
- Items y Skills con datos de Kilima
- Combate completo
- Físicas
- Godot
- Metaverso
- Tercera revolución
- Skills completas (diccionario pendiente)

---

## Diagnóstico del código (marzo 2026)

El sistema base es escalable y el Patch 2 está completo:

- Separación Gigagen/Kilima limpia
- Modelos Pydantic extensibles
- Simulador data-driven
- **342 tests pasando**
- Escalera de Descendencia implementada (`src/gigagen/layers/`)
- `load_worldpack.py` refactorizado a 55 líneas

Lo que queda pendiente:

- ~~**Restructurar** `src/gigagen/` añadiendo carpeta `layers/`~~ ✅ Patch 2
- ~~**Refactorizar** `load_worldpack.py` (<80 líneas)~~ ✅ Patch 2 (55 líneas)
- ~~**Añadir** modelo `Lineage` a `entity.py`~~ ✅ Patch 2
- ~~**Crear** `x.json` + `y.json` en `worlds/kilima/`~~ ✅ Patch 2
- ~~**Tipar** `WorldState.phase` como `DescendenceStep`~~ ✅ Patch 2
- **Simplificar** `harmony.py`: menos funciones específicas, más función universal `harmonic_affinity(note_a, note_b)`
- **Renombrar** nomenclatura (LP-0, lo más arriesgado pero mecánico)

**Alerta permanente:** si en algún momento una decisión contradice el algoritmo base o complica lo que debería ser simple, parar y replantear. Mejor reconstruir sobre terreno firme que parchear.

---

## Estructura de carpetas

```
docs/
├── CLAUDE.md                          # ← ESTE ARCHIVO
├── README.md                          # Índice de documentación
├── gigagen/                           # Docs del motor
│   ├── gigagen_ontology.md
│   ├── gigagen_offspringladder_ontology.md  # NUEVO — filosofía de la Escalera
│   ├── gigagen_patch2_briefing.md     # NUEVO — qué construye el Patch 2
│   ├── gigagen_patch2_roadmap.md      # NUEVO — plan de implementación Patch 2
│   ├── gigagen_faction_system.md
│   ├── gigagen_roadmap_lifepack.md
│   └── ...
├── kilima/                            # Docs del worldpack
│   ├── kilima_bible.md
│   ├── kilima_lore.md
│   ├── kilima_characters.md
│   ├── kilima_factions.md
│   ├── kilima_locations.md
│   ├── kilima_invariants.md
│   ├── lifepack_estructura.md
│   └── data/
│       ├── characters.json
│       ├── factions.json
│       ├── locations.json
│       ├── relations.json
│       └── world.json

src/gigagen/
├── core/
│   ├── entity.py
│   ├── relation.py
│   ├── harmony.py
│   ├── lifepack.py
│   ├── world_state.py
│   ├── simulator.py
│   ├── seed.py
│   └── invariants.py
├── layers/                            # NUEVO (Patch 2)
│   ├── __init__.py
│   ├── genesis.py
│   ├── theogony.py
│   ├── chronica.py
│   ├── contempo.py
│   └── existence.py
├── io/
│   ├── load_worldpack.py              # Refactorizar → coordinador ligero
│   └── export_world_state.py
├── cli/
│   ├── console.py
│   └── tui/
└── __main__.py

worlds/kilima/
├── x.json                             # NUEVO — leyes del universo (Eva/Software)
├── y.json                             # NUEVO — catálogo de materia (Adán/Hardware)
├── world.json
├── characters.json
├── factions.json
├── locations.json
├── relations.json
├── lineages.json                      # NUEVO — linajes de Kilima
├── invariants.json
├── event_rules.json
├── lifepacks/
│   ├── kilima_in12_rebel.json
│   └── ...
└── timelines/
    └── bn1.yaml
```

---

## Stack técnico

- **Lenguaje:** Python 3.11+
- **Modelos de datos:** Pydantic v2
- **Formato de datos:** JSON
- **TUI:** Textual
- **Tests:** pytest (342 passing)
- **Sin dependencias pesadas.** Sin frameworks web, sin BD, sin Godot todavía.

---

## Sobre el autor y cómo trabajar con él

- Necesita sentir **fundamento**. No le sirve una solución "funcional" si no está justificada dentro del sistema. La arbitrariedad le bloquea.
- Piensa **relacionalmente**, no taxonómicamente. No parte de "qué es esto" sino de "cómo se vincula con lo demás".
- Le entusiasman los avances concretos, pero **solo cuando siente que el cimiento es real**.
- Se beneficia mucho de **diccionarios y vocabularios cerrados**.
- El criterio de verdad no es solo técnico: una decisión es buena si es programable, jugable, y parece derivada del propio universo.
- Prefiere diseño antes que código. No empezar a implementar hasta que el diseño esté cerrado.
- Metodología lenta y metódica. Cerrar cada decisión antes de abrir la siguiente.

**Instrucción clave:** no intentes impresionar ni completar demasiado rápido. Ayúdale a descubrir la forma mínima correcta de cada pieza, una por una. Si algo contradice el algoritmo base o complica lo que debería ser simple, dilo. Empieza siempre por la Fase 0 de cualquier parche — estructura antes que lógica.

---

## Referencia rápida: los 12 arquetipos

| Código | Arquetipo | Nota | Personaje (kilima_in12) |
|--------|-----------|------|------------------------|
| CAR | Caregiver | C | Nora |
| JES | Jester | C# | Pau |
| HER | Hero | D | Luka |
| REB | Rebel | D# | Kive |
| ORP | Orphan | E | Len |
| LOV | Lover | F | Ali |
| HCK | Hacker | F# | Dev |
| LEA | Leader | G | Saarah |
| INN | Innocent | G# | Brais |
| EXP | Explorer | A | Yeri |
| CRE | Creator | A# | Cris |
| DEI | Deity | B | Freya |
