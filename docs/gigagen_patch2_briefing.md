# PATCH 2 — La Escalera de Descendencia

> **Prioridad:** Este es el parche estructural más importante del proyecto.
> **Orden de lectura:** Este fichero primero, luego PATCH2_ROADMAP.md, luego el código.
> **Tono:** Construye desde la filosofía hacia abajo. El código debe emerger del sistema, no al revés.

---

## Qué se está construyendo

Gigagen tiene modelos, tiene datos, tiene simulador — pero no tiene **pipeline**. El proceso de generación de un universo ocurre todo en `load_worldpack.py` (259 líneas y creciendo) sin estructura que refleje el sistema conceptual.

Este parche formaliza la **Escalera de Descendencia**: los cinco escalones que transforman leyes abstractas en un universo simulable. Cada escalón tiene responsabilidad clara, inputs definidos, outputs verificables.

Después de este parche, añadir una nueva entidad (Items, Ánimas con datos, Characters 2gen) no significa engordar `load_worldpack.py` — significa saber exactamente en qué escalón vive y escribir ahí.

---

## La Escalera — filosofía

La Escalera no es una metáfora. Es la arquitectura real del sistema. Cada escalón produce un estado del mundo más rico que el anterior, y ningún escalón puede operar sin el anterior.

```
Genesis    → el universo puede existir
Theogony   → el universo tiene magia e historia potencial
Chronica   → el universo tiene un pasado concreto
Contempo   → el universo tiene un presente simulable
Existence  → el universo tiene un jugador dentro
```

**Regla fundamental:** cada escalón recibe un `WorldState` y devuelve un `WorldState` más completo. El pipeline es una cadena de transformaciones puras.

```python
ws = genesis(x, y)
ws = theogony(ws)
ws = chronica(ws, seed)
ws = contempo(ws)
ws = existence(ws)
```

---

## Los cinco escalones

### Genesis — Universo Primigenio

**Entrada:** `x.json` + `y.json`
**Salida:** `WorldState` con leyes y catálogos cargados. Sin entidades. Sin historia.
**Sin seed.** Determinista. Igual en todos los universos Gigagen.

#### x.json — Eva / Software
Todo lo abstracto. Las leyes que gobiernan cómo las cosas se relacionan:
- Arquetipos (12) y sus propiedades
- Intervalos harmónicos y sus afinidades
- Familias de escala (greek, symmetric, pentatonic)
- Tipos de relación y sus polaridades
- Tipos de entidad permitidos
- Reglas de canon_level

`x.json` define la **física relacional** del universo. Si cambias algo aquí, cambia cómo todo se relaciona con todo.

#### y.json — Adán / Hardware
Todo lo concreto. El catálogo de materia que puede existir:
- Las 12 notas cromáticas
- Los 16 elementos (con jerarquía de composición)
- Los tiers de personaje (S/A/B)
- Los niveles de location (1-6)
- Los rangos de item y skill
- Los modos harmónicos disponibles

`y.json` define el **catálogo de existencia**. Si añades un elemento nuevo o un tier nuevo, solo tocas aquí.

**Validación de Genesis:** `y.json` debe respetar las leyes de `x.json`. Si hay 13 notas en `y.json` pero `x.json` dice que el sistema cromático tiene 12, Genesis falla limpio.

**Location nivel 1:** Genesis produce WORLD — la location raíz de toda jerarquía. Es el único artefacto concreto que Genesis genera. Todo lo demás son leyes y catálogos.

---

### Theogony — Universo Mágico

**Entrada:** `WorldState` de Genesis + datos del worldpack
**Salida:** `WorldState` con ánimas, linajes y primeras locations instanciados
**Sin seed.** Las reglas del gambleo se definen aquí, pero los dados no se lanzan todavía.

#### Qué instancia Theogony

**Ánimas (16 elementos):**
Los 16 elementos existen desde el principio del universo mágico. No son consecuencia de la historia — son anteriores a ella. Fundamentales (Agua, Fuego, Tierra, Aire), Mixtos (Nube, Barro, Hielo, Metal, Humo, Polvo), Truncados (Lava, Tormenta, Ceniza, Humedad + 2 más).

**Linajes:**
Los linajes son las familias primordiales — existen antes de que haya facciones políticas. Cada linaje tiene:

*Campos fixed (Theogony los instancia):*
- `id`, `name`, `archetype`, `note` — identidad inmutable
- `element_pool` — qué elementos son posibles para este linaje (restricción fija)
- `tier` — Founder / Leader / Notary

*Campos seeded (Theogony los declara, Chronica los resuelve):*
- `element` — cuál del element_pool le toca en esta seed
- `founding_era` — en qué revolución se consolidó
- `origin_location_id` — dónde se asentó

Theogony dice "el linaje Radbot puede ser Fuego, Metal o Lava". Chronica decide cuál.

**Locations nivel 2:**
Las grandes divisiones del mundo — anteriores a la historia política.

**Items tier S y Skills tier S:**
Los artefactos y habilidades primordiales. Únicos, anteriores a la civilización.

#### Lo que Theogony NO hace
- No asigna elementos concretos a linajes
- No crea macrofactions
- No lanza ningún dado
- No usa la seed

---

### Chronica — Universo Impreso

**Entrada:** `WorldState` de Theogony + worldpack data + **seed**
**Salida:** `WorldState` con pasado completo generado
**La seed entra aquí. Una sola seed. Se consume con RNG por namespace.**

Chronica es el escalón más complejo. Es un **generador de pasado**: toma un universo con leyes y potencial, y produce una historia concreta.

#### La seed y sus namespaces

Una seed, múltiples RNGs independientes:

```python
rng_elements  = Random(seed + "elements")   # qué elemento toca a cada linaje
rng_founders  = Random(seed + "founders")   # quién fundó qué
rng_modes     = Random(seed + "modes")      # modos a macrofactions
rng_events    = Random(seed + "events")     # resolución de macro/micro-events
rng_locations = Random(seed + "locations")  # asignación de locations a factions
rng_2gen      = Random(seed + "2gen")       # characters 2gen
```

Cada namespace es reproducible e independiente. Añadir un nuevo tipo de gambleo no rompe los demás.

#### Qué genera Chronica, en orden

**1. Resolver linajes (seed: elements)**
Para cada linaje, elegir dentro de su `element_pool`. Esto determina la afinidad elemental de toda la historia que viene después.

**2. Asignar modos a macrofactions (seed: modes)**
Las macrofactions no se predeclaran — emergen. Chronica agrupa linajes con elementos compatibles, y el modo de cada macrofaction se hereda del linaje fundador. Una macrofaction no "tiene" un modo arbitrariamente — lo hereda de su sangre.

**3. Gamblear fundadores — Characters 1gen (seed: founders)**
Tres tiers:
- **Tier S — Founder:** nota cromática fija (una por linaje, las 12 notas). Son los padres del universo.
- **Tier A — Leader:** 3 por Founder. Major o minor se setea aquí.
- **Tier B — Notary:** 5 por Leader.

**4. Macro-events (seed: events)**
Los eventos históricos canónicos del worldpack (Capitol Foundation, First Revolution, First Wall Foundation, Agora Foundation, Second Wall Foundation en Kilima). Cada uno tiene planteamiento fijo y resolución gambleada. La resolución de un macro-event afecta qué linajes ganan poder, qué locations se fundan, qué macrofactions emergen.

**5. Locations niveles 3-6 (seed: locations)**
Las locations que no son primordiales — nacen de la historia. Su tonic se asigna aquí, derivado del linaje que las fundó.

**6. Micro-events (seed: events)**
Eventos menores que llenan el pasado. Menos estructurados que los macro-events, pero igual de consecuentes para el estado de H00.

**7. Characters 2gen (seed: 2gen)**
Los personajes que nacen de la historia — NPCs, secundarios, antagonistas menores. Sus tiers y notas se gamblear dentro de los rangos que definen los Characters 1gen de su linaje.

**Items tier A y Skills tier B** también se instancian en Chronica — artefactos y habilidades que nacieron durante la historia.

#### Lo que Chronica NO hace
- No simula el presente
- No genera el árbol de eventos de BN1
- No instancia los 12 principales de IN12 (eso es Contempo)

---

### Contempo — Universo Presente

**Entrada:** `WorldState` de Chronica
**Salida:** `WorldState` con presente completo y simulable
**Determinista dado Chronica.**

Contempo es donde vive BN1 y todos los actos futuros. Toma el pasado generado por Chronica y construye el presente.

#### Qué instancia Contempo

**IN12 — Los 12 principales:**
Con todas sus propiedades actuales: habilidades, objetos, ubicaciones, Life Packs. Sus estados en H00 se derivan directamente de Chronica.

**Minor Wheel — Secundarios y terciarios:**
Generados por afinidad harmónica con los IN12. Aliados y antagonistas emergen de las consonancias y disonancias de las notas.

**Árbol de eventos:**
BN1 y actos futuros. Planteamiento + árbol de posibilidades. Las decisiones y acciones de los personajes generan ramificaciones.

**X + Y converge aquí:**
El evento final — la fusión de Dev + Len + IA + toda la conciencia humana — está superpuesto en todos los finales posibles de Contempo. Es el atractor inevitable. BN1 es el primer paso hacia él.

---

### Existence — Universo Jugable

**Entrada:** `WorldState` de Contempo
**Salida:** universo interactivo con jugador dentro
**Determinista. Base conceptual — implementación futura.**

El jugador crea un personaje, entra al universo, interactúa con IN12, facciones, locations. Existence es la capa que hace Gigagen un mundo habitable, no solo simulable.

Por ahora: sentar las bases conceptuales. No implementar.

---

## Arquitectura de código resultante

```
src/gigagen/
├── core/              ← modelos puros (entity, relation, world_state, harmony, lifepack)
├── layers/
│   ├── __init__.py
│   ├── genesis.py     ← carga x.json + y.json, produce WorldState base
│   ├── theogony.py    ← instancia ánimas, linajes, locations L2, items/skills tier S
│   ├── chronica.py    ← seed + RNG namespaces, genera pasado completo
│   ├── contempo.py    ← IN12, Minor Wheel, árbol de eventos
│   └── existence.py   ← stub — jugador e interactividad (futuro)
├── io/                ← solo lectura/escritura de disco
└── cli/               ← TUI
```

Cada layer tiene firma canónica:

```python
def run(ws: WorldState, config: dict) -> WorldState:
    ...
```

El pipeline principal:

```python
ws = genesis.run(WorldState(), {"x": x_path, "y": y_path})
ws = theogony.run(ws, worldpack_config)
ws = chronica.run(ws, worldpack_config, seed=seed)
ws = contempo.run(ws, worldpack_config)
# existence.run() — futuro
```

---

## Reglas críticas

### io/ solo toca disco
`load_worldpack.py` pasa a ser un coordinador ligero que lee ficheros y llama a las layers. No tiene lógica de transformación.

### Cada layer es testeable en aislamiento
Dado un `WorldState` de entrada y una config, la salida es determinista (excepto Chronica, que es determinista dado seed + config). Los tests pueden verificar cada escalón independientemente.

### Los 292 tests existentes deben seguir pasando
Este parche es una restructura, no una reescritura. La lógica existente se mueve, no se cambia.

### El `?` al final de cada escalón
Ningún escalón se cierra hasta que todas sus preguntas abiertas tienen respuesta. Antes de implementar un escalón, resolver todos sus `?`.

---

## Qué NO hace este parche

- No añade datos de Kilima nuevos (Items, Ánimas con datos, Characters 2gen)
- No implementa Existence
- No cambia los modelos Pydantic existentes (salvo añadir Lineage)
- No toca la TUI
- No implementa el árbol de eventos de Contempo

El objetivo es la **infraestructura**. Los datos vienen en parches posteriores.

---

## Preguntas abiertas antes de empezar (`?`)

### Genesis
- [ ] Estructura interna exacta de `x.json` — ¿qué campos, qué formato?
- [ ] Estructura interna exacta de `y.json` — ¿qué campos, qué formato?

### Theogony
- [ ] Modelo `Lineage` — ¿qué campos fixed vs seeded declarados?
- [ ] ¿`element_pool` es una lista de elementos o probabilidades ponderadas?
- [ ] Datos de Kilima: ¿cuántos linajes tiene Kilima? ¿Cuáles?

### Chronica
- [ ] ¿Los macro-events canónicos van en el worldpack o en Gigagen core?
- [ ] ¿Cómo se modela la resolución de un macro-event? ¿Es un dict de outcomes posibles?

### Contempo
- [ ] ¿El Minor Wheel es un algoritmo puro o necesita datos del worldpack?

### Existence
- [ ] Sin preguntas por ahora. Es un stub.
