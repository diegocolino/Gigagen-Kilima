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

El universo no aparece de golpe. Se genera por capas. Cada capa activa octavas del Life Pack:

1. **Genesis** — Define qué puede medirse. Parámetros posibles. Activa octava 0 (lore).
2. **Theogony** — Fuerzas invisibles: ánimas, elementos, linajes. Activa octavas 1 y 2.
3. **Chronica** — Re-simula el pasado. Parte de esqueleto canónico, no genera historia aleatoria. Activa octavas 7 y 8.
4. **Contempo** — Materializa el presente visible. Activa octavas 3, 4 y 5. El Life Pack completo cobra sentido.
5. **Existence** — Introduce al jugador en el sistema.

No tocar esta arquitectura. Conservarla como esqueleto maestro.

---

## Nomenclatura (IMPORTANTE)

| Término correcto | Definición | Término obsoleto |
|-----------------|-----------|-----------------|
| **Macro-facción** | Modo armónico (Dórico, Frigio...). Sin tónica. Plantilla. | "facción" en código antiguo |
| **Facción** | Macro-facción + tónica = escala concreta. Operativa. Tiene líder, miembros, territorio. | "subdivisión" en código antiguo |
| **kilima_in12_{archetype}** | Patrón de ID para personajes de la primera colección de 12 | `kilima_{archetype}` |

El renombrado en código es LP-0 (primer milestone del roadmap del Life Pack).

---

## Metas

### Meta faro

Conseguir la primera simulación que relacione todos los tipos de entidades en todo el espectro armónico. Cargar el Life Pack del Rebelde (Kive) y ver cómo muta e interactúa durante la simulación del BN1. **Cerrar el sistema armónico global antes de seguir metiendo lore, personajes, locations, eventos.**

### Meta a corto plazo

Redefinir los indicadores de armonía ahora que la armonía es universal y trabaja con todas las entidades. El motor armónico actual (`harmony.py`) tiene funciones específicas por tipo (`character_faction_affinity`, `character_location_affinity`). Estas deberían simplificarse hacia una función universal `harmonic_affinity(note_a, note_b)` donde el contexto lo pone el caller, no la función. Esto es un refactor que simplifica en vez de complicar.

### Milestones técnicos

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

- Combate completo
- Físicas
- Godot
- Metaverso
- Tercera revolución
- Skills completas (diccionario pendiente)

---

## Diagnóstico del código (marzo 2026)

El sistema base es lo bastante escalable. No hay que empezar de cero. El cimiento aguanta:

- Separación Gigagen/Kilima limpia
- Modelos Pydantic extensibles
- Simulador data-driven
- 205 tests pasando

Lo que hay que hacer:

- **Simplificar** `harmony.py`: menos funciones específicas, más función universal
- **Añadir** modelo LifePack al lado de lo existente (no dentro de Character — referenciado por ID, JSON separado en `lifepacks/`)
- **Extender** el simulador sin tocar su lógica core (nuevo event rule type: `unlock_lifepack_slot`)
- **Renombrar** nomenclatura (LP-0, lo más arriesgado pero mecánico)

**Alerta permanente:** si en algún momento una decisión contradice el algoritmo base o complica lo que debería ser simple, parar y replantear. Mejor reconstruir sobre terreno firme que parchear.

---

## Estructura de carpetas

```
docs/
├── CLAUDE.md                      # ← ESTE ARCHIVO
├── README.md                      # Índice de documentación
├── gigagen/                       # Docs del motor
│   ├── gigagen_ontology.md
│   ├── gigagen_faction_system.md
│   ├── gigagen_roadmap_lifepack.md
│   └── ...
├── kilima/                        # Docs del worldpack
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
│   ├── lifepack.py                # NUEVO
│   ├── world_state.py
│   ├── simulator.py
│   ├── seed.py
│   └── invariants.py
├── io/
│   ├── load_worldpack.py
│   └── export_world_state.py
├── cli/
│   ├── console.py
│   └── tui/
└── __main__.py

worlds/kilima/
├── world.json
├── characters.json
├── factions.json
├── locations.json
├── relations.json
├── invariants.json
├── event_rules.json
├── lifepacks/                     # NUEVO
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
- **Tests:** pytest (205 passing)
- **Sin dependencias pesadas.** Sin frameworks web, sin BD, sin Godot todavía.

---

## Sobre el autor y cómo trabajar con él

- Necesita sentir **fundamento**. No le sirve una solución "funcional" si no está justificada dentro del sistema. La arbitrariedad le bloquea.
- Piensa **relacionalmente**, no taxonómicamente. No parte de "qué es esto" sino de "cómo se vincula con lo demás".
- Le entusiasman los avances concretos, pero **solo cuando siente que el cimiento es real**.
- Se beneficia mucho de **diccionarios y vocabularios cerrados**.
- El criterio de verdad no es solo técnico: una decisión es buena si es programable, jugable, y parece derivada del propio universo.

**Instrucción clave:** no intentes impresionar ni completar demasiado rápido. Ayúdale a descubrir la forma mínima correcta de cada pieza, una por una. Si algo contradice el algoritmo base o complica lo que debería ser simple, dilo.

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
