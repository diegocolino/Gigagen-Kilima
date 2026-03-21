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

## Los dos ejes del sistema

### 1. Eje arquetípico-musical (mente)

- 12 arquetipos = 12 lógicas cognitivas base
- 12 notas musicales
- La singularidad de cada NPC no nace de tener una IA distinta, sino de: relaciones, contexto, objetos, facción, linaje, elemento/ánima, estado tonal
- La música no es adorno: es lenguaje operativo (resonancia, disonancia, triadas, modos, tensiones, resoluciones)
- Mayor = expresión integrada/expansiva. Menor = expresión tensionada/contractiva. No es moral fija.

#### Sistema armónico de intervalos (ya probado)

En un mod previo de Hytale se implementó y funcionó un sistema donde:
- Cada entidad tiene una nota base (por su arquetipo)
- El **intervalo musical** entre dos entidades determina su **afinidad base** (un float)
- Ese índice base se modifica por: facción compartida, relaciones comunes, historial, estado actual
- Ejemplo: tritono (6 semitonos) = némesis / tensión máxima. Quinta justa (7 semitonos) = aliado natural. Tercera menor/mayor = tensiones naturales en grupo.
- El sistema era sencillo y funcional. Debe portarse a Gigagen como función calculada en la capa de relaciones.

La función objetivo sería algo como: `harmonic_affinity(note_a, note_b) → float base`, que luego se ajusta por contexto.

### 2. Eje elemental-anímico (poder)

- Las Ánimas son **entidades plenas**: tienen personalidad, apariencia, historia propia. Son personajes como los humanos, pero no viven en el plano físico de la misma manera.
- En La Red se manifiestan con facilidad. En el mundo físico, se necesita un don (por herencia o aprendizaje). Len nació con ese don (Sensible Suprema).
- Separan: arquetipo = mente/conducta vs. ánima = poder/stats/física/afinidad
- Un Caregiver Agua y un Caregiver Fuego comparten lógica profunda, pero no se manifiestan igual
- Hay **16 elementos** en jerarquía: 4 Fundamentales (Agua, Fuego, Tierra, Aire) → 6 Mixtos → 4 Truncados → Éter (Supremo, en dos formas: natural y sintético). Las ánimas son **instancias** de estos elementos.
- La tensión Éter natural vs. Éter sintético es un eje de conflicto central (Sensibles vs. Capital).
- Las ánimas tienen relaciones con su portador, con otras ánimas, con localizaciones donde se manifiestan.
- Las ánimas se asignan a NPCs, influyen en facciones, afectan locations, dejan rastro en objetos

---

## La escalera de descendencia (arquitectura de capas)

El universo no aparece de golpe. Se genera por capas:

1. **Genesis** — Define qué puede medirse. No valores concretos: parámetros posibles.
2. **Theogony** — Fuerzas invisibles: ánimas, elements, skills, rules, symbols, gramática mágica.
3. **Chronica** — Re-simula el pasado usando las mismas lógicas que Contempo/Existence, pero hacia atrás. No genera historia aleatoria: redibuja una historia que ya tiene esqueleto canónico.
   - En Kilima: parte de los 12 linajes fundadores (familias de poder que financiaron La Montaña) y la Primera Revolución como eventos estructurales.
   - Chronica produce un pasado con consecuencias reales que desemboca en el presente de Contempo.
4. **Contempo** — Materializa el presente visible: estado actual del mundo.
   - En Gigagen: estructura genérica del presente.
   - En Kilima: el presente concreto con los 12 protagonistas.
5. **Existence** — Introduce al jugador en el sistema.

No tocar esta arquitectura. Conservarla como esqueleto maestro.

---

## Principios ontológicos fundamentales

### Una entidad no vale por sí sola; vale por cómo se relaciona

Esta es la idea más importante del proyecto. El sistema es **relacional**, no taxonómico.

### Separación sagrada de planos

Cada vez que aparezca una duda, preguntar: ¿esto es identidad, estado, relación, capacidad o consecuencia?

| Plano | Qué es | Ejemplo |
|-------|--------|---------|
| **Identidad** | Lo que una cosa *es* | Kive es El Rebelde, arquetipo REB, nota D# |
| **Estado** | Cómo *está* ahora | alive, active, location: loc.jaula |
| **Relación** | Cómo está *vinculada* con otra cosa | sibling con La Huérfana |
| **Capacidad** | Qué *puede hacer* | skills, poderes |
| **Acción** | Qué *ejecuta* en runtime | intervención en evento |
| **Efecto** | Qué *cambia* al ejecutarse | daño, alianza rota |
| **Consecuencia** | Qué persistencia deja ese cambio | herencia, memoria |
| **Historia** | Registro encadenado de consecuencias | chronica |

### Clasificación fixed / seeded / derived / forbidden

| Categoría | Significado |
|-----------|-------------|
| **fixed** | No puede cambiar entre seeds |
| **seeded** | Se decide al iniciar la simulación, permanece coherente en esa run |
| **derived** | No se decide al inicio, emerge de relaciones y reglas |
| **forbidden** | Trayectorias que el sistema NO debe producir |

---

## Vocabulario ontológico

No todo es "Entity". Hay cuatro clases de cosas:

1. **Entidades** — Nodos del universo: Character, Faction, Location, Item, Anima
2. **Relaciones** — Vínculos entre entidades (objeto de primera clase, no lista embebida)
3. **Capacidades/definiciones** — Skill, Rule, SymbolSet, Archetype, Element (catálogos, no entidades)
4. **Sucesos** — Event, ChronicleEntry, Transition (registros temporales)

---

## Meta inmediata

Conseguir que Gigagen pueda **cargar Kilima y generar una versión válida de su presente**.

No perfecta. No jugable aún. Pero sí coherente y reproducible por seed.

### Lo que NO toca ahora

- Combate completo
- Físicas
- Godot
- Metaverso
- Tercera revolución
- Sistema narrativo final
- Ánimas completas
- Skills completas

### Lo que SÍ toca

1. Modelos canónicos: BaseEntity, Relation, WorldState
2. Worldpack de Kilima con JSON mínimos
3. Loader que cargue el worldpack y valide
4. Primer export reproducible por seed

### Criterios de validación del primer hito

Un world_state exportado está bien si cumple:

1. **Separación limpia** — No hay datos de Kilima incrustados en Gigagen
2. **Entidades coherentes** — Identidad y estado claramente separados
3. **Relaciones como primer ciudadano** — No son decoración ni listas arbitrarias
4. **Seed con variación controlada** — La seed cambia estados y tensiones, no destruye identidad

---

## Estructura de carpetas objetivo

```
D:\Gigagen_Kilima\
├── docs/                          # Project documentation
│   ├── CLAUDE.md                  # ← THIS FILE
│   ├── ontology.md                # Formal models: entity, relation, state
│   ├── kilima_bible.md            # INDEX pointing to all kilima_ files
│   ├── kilima_lore.md             # World background, ether, elements, etc.
│   ├── kilima_characters.md       # The 12 principals
│   ├── kilima_locations.md        # All locations
│   ├── kilima_factions.md         # The 4 factions
│   ├── kilima_hero_*.md           # 12 hero arc files (one per archetype)
│   ├── invariants.md              # Fixed / seeded / derived / forbidden
│   └── roadmap.md                 # Milestones
├── src/
│   └── gigagen/
│       ├── core/                  # Core models
│       │   ├── entity.py
│       │   ├── relation.py
│       │   └── world_state.py
│       ├── catalogs/              # Master catalogs (Gigagen, not Kilima)
│       │   ├── archetypes.json
│       │   ├── notes.json
│       │   ├── elements.json
│       │   └── relation_types.json
│       ├── layers/                # The 5 layers
│       │   ├── genesis.py
│       │   ├── theogony.py
│       │   ├── chronica.py
│       │   ├── contempo.py
│       │   └── existence.py
│       └── io/                    # Load and export
│           ├── load_worldpack.py
│           └── export_world_state.py
├── worlds/
│   └── kilima/
│       ├── world.json
│       ├── characters.json
│       ├── factions.json
│       ├── locations.json
│       ├── relations.json
│       ├── invariants.json
│       └── timelines/
│           └── bn1.yaml           # The 62-hour NB1 master (v5.0)
└── outputs/
```

---

## Stack técnico

- **Lenguaje:** Python 3.11+
- **Modelos de datos:** Pydantic v2 (recomendado para validación fuerte de JSON contra modelos)
- **Formato de datos:** JSON
- **Sin dependencias pesadas** al principio. Sin frameworks web, sin BD, sin Godot todavía.

---

## Sobre el autor y cómo trabajar con él

- Necesita sentir **fundamento**. No le sirve una solución "funcional" si no está justificada dentro del sistema. La arbitrariedad le bloquea.
- Piensa **relacionalmente**, no taxonómicamente. No parte de "qué es esto" sino de "cómo se vincula con lo demás".
- Le entusiasman los avances concretos, pero **solo cuando siente que el cimiento es real**.
- Se beneficia mucho de **diccionarios y vocabularios cerrados**.
- El criterio de verdad no es solo técnico: una decisión es buena si es programable, jugable, y parece derivada del propio universo.

**Instrucción clave:** no intentes impresionar ni completar demasiado rápido. Ayúdale a descubrir la forma mínima correcta de cada pieza, una por una.

---

## Referencia rápida: los 12 arquetipos

| Código | Arquetipo | Nota |
|--------|-----------|------|
| CAR | Caregiver | C |
| JES | Jester | C# / Db |
| HER | Hero | D |
| REB | Rebel | D# / Eb |
| ORP | Orphan | E |
| LOV | Lover | F |
| HCK | Hacker | F# / Gb |
| LEA | Leader | G |
| INN | Innocent | G# / Ab |
| EXP | Explorer | A |
| CRE | Creator | A# / Bb |
| DEI | Deity | B |
