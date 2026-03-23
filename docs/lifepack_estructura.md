# Life Pack — Estructura

## Premisa fundamental

Todas las entidades de Gigagen tienen un arquetipo = una nota.
Un personaje es: su tónica + las entidades en cada grado de su Life Pack.
El Life Pack es el espectro completo de existencia de ese personaje, organizado por octavas.

---

## Entidades del sistema

### Arquetipo

Unidad mínima de identidad. Cada arquetipo corresponde a una nota cromática (C, C#, D... B). Hay 12 arquetipos universales. Toda entidad del sistema — personaje, objeto, location, ánima, facción — está arquetipizada, es decir, tiene una nota asignada.

### Personaje

Una tónica (su arquetipo) + su Life Pack completo. El personaje no es un acorde ni una melodía: es un espectro de frecuencias que abarca desde los infrasonidos (pasado) hasta los ultrasonidos (futuro). Lo que "suena" en cada octava define quién es, qué tiene, qué sabe, a quién conoce y qué le ha pasado.

### Objeto

Entidad física o conceptual con arquetipo propio. Herramientas, armas, artefactos, recursos. Se asignan en la octava 4 del Life Pack del personaje. El intervalo entre la tónica del personaje y la nota del objeto define el tipo de vínculo (dominio, carga, pilar...).

### Location

Lugar con arquetipo propio. Se asigna en la octava 3 del Life Pack. El intervalo define el tipo de relación espacial-emocional (raíz, refugio, prisión, pilar...).

### Ánima

Entidad viva, espíritu elemental con arquetipo propio (gambleado al inicio de cada simulación). Se asigna en la octava 1. El número de ánimas activas depende de los elementos desbloqueados por el personaje. Las ánimas se ganan, no se eligen.

### Skill

Habilidad o capacidad con arquetipo propio. Se asigna en la octava 5. Para personajes sin ánimas (como Dev), esta octava emula funciones que otros realizan vía octava 1.

### Evento

Marca narrativa con arquetipo propio. Se asigna en la octava 8. No es "qué pasó" sino "qué cicatriz llevas". Los eventos se desbloquean conforme avanza la narrativa.

### Linaje

Herencia singular. Un solo slot en la octava 2. La tónica del personaje en esa octava = su linaje.

### Lore (definición arquetípica)

JSON de 12 entradas en la octava 0: cómo el personaje se relaciona particularmente con cada uno de los 12 arquetipos universales. No es inventario — es el motor de referencia que Gigagen consulta para resolver comportamiento. Es constitucional, no cambia.

### Macro-facción

Identidad armónica colectiva = un modo (Dórico, Frigio, Jónico, Eólico, Lidio, Mixolidio, Locrio, tonos enteros, pentatónica mayor, pentatónica menor...). El modo define el carácter, el color, la personalidad de la macro-facción. No tiene tónica fija — es una plantilla.

### Facción

Macro-facción + tónica = escala concreta. La tónica viene del líder de la facción. La facción es operativa: tiene miembros, territorio, cohesión, poder. En la documentación anterior se llamaba "subdivisión" — esa nomenclatura queda obsoleta.

### Elemento

Propiedad innata del personaje (invariante). 4 fundamentales (Agua, Fuego, Tierra, Aire) que se combinan en 6 mixtas, 4 truncadas y 1 suprema (Ether). Los elementos determinan qué ánimas puede desbloquear un personaje. No son entidades en sí — son condiciones de acceso a la octava 1.

---

## Relaciones entre entidades

### Arquetipo ↔ Nota

Relación 1:1 fija. Cada arquetipo ES una nota. No hay arquetipo sin nota ni nota sin arquetipo.

### Personaje ↔ Entidades (vía Life Pack)

La tónica del personaje + la nota de cualquier entidad = un intervalo. Ese intervalo determina en qué slot del Life Pack cae la entidad y qué tipo de vínculo representa. La relación no se elige — se calcula.

### Personaje ↔ Personaje (octava 7)

Los 12 semitonos de la octava 7 definen 12 tipos de vínculo relacional. Cada personaje tiene una relación predefinida con todos los demás por distancia interválica. Unísono = espejo. Semitono = fricción. Tercera menor = aliado oscuro. Quinta justa = pilar. Tritono = némesis.

### Personaje ↔ Facción (sistema armónico macro)

La nota del personaje cae dentro o fuera de la escala de la facción. Esto se calcula automáticamente y define afinidad, tensión, y coste de doble militancia. No necesita slot en el Life Pack — es propiedad emergente del sistema.

### Facción ↔ Macro-facción

Relación de pertenencia. La facción hereda el modo de su macro-facción y le añade una tónica concreta. Facciones de la misma macro-facción son "primas" — comparten modo pero difieren en escala.

### Facción ↔ Facción (entre macro-facciones)

El intervalo entre las tónicas de dos facciones define su relación: quinta justa = alianza natural, tritono = némesis, semitono = fricción. Facciones de macro-facciones distintas añaden la diferencia de modo como capa extra de compatibilidad/incompatibilidad.

### Elemento ↔ Ánima

Los elementos son la llave, las ánimas son la puerta. Dominar un elemento desbloquea el slot de ánima correspondiente. Fusionar elementos (Fuego + Tierra = Metal) desbloquea slots adicionales sin eliminar los anteriores.

### Skill ↔ Ánima (caso Dev)

Para personajes sin elementos (octava 1 vacía), las skills de octava 5 pueden emular efectos elementales a través de objetos tecnológicos de octava 4. La cadena es: octava 4 (objeto tech) → octava 5 (skill emuladora) → efecto equivalente a octava 1 (ánima). Poder condicional: si pierde la tecnología, pierde el acceso.

### Evento ↔ Personaje (octava 8)

Los eventos no se asignan al inicio — se desbloquean durante la narrativa. Cada evento deja una cicatriz en el slot correspondiente a su intervalo con la tónica del personaje. Un personaje acumula eventos como acumula heridas.

---

## Lógica de llenado por octava

No hay regla universal. Cada octava tiene su propia lógica:

| Octava | Tipo | Lógica | Slots |
|--------|------|--------|-------|
| -1.. | Infrasonidos (pasado) | Por definir | — |
| 0 | Lore | 12 slots fijos por arquetipo, iguales para todos | 12 |
| 1 | Ánimas | Variable por personaje, depende de elementos | 0–11 |
| 2 | Linajes | Slot único | 1 |
| 3 | Locations | Acorde interno (tónica, 3m, 3M, 5J + desbloqueables) | 4+ |
| 4 | Objetos | Acorde interno (tónica, 3m, 3M, 5J + desbloqueables) | 4+ |
| 5 | Skills | Acorde interno (tónica, 3m, 3M, 5J + desbloqueables) | 4+ |
| 6 | Reservada | Palomita suelta, por definir | — |
| 7 | Personajes | 12 slots completos, todos activos | 12 |
| 8 | Eventos | Pendiente de detalle | 12 |
| 9+ | Ultrasonidos (futuro) | Por definir | — |

---

## Alteraciones

Las alteraciones no cambian qué entidad ocupa un slot — cambian la cualidad del vínculo. Son dinámicas: pueden mutar durante la narrativa sin alterar la estructura del Life Pack.

- **Mayor** → vínculo luminoso, dominio, disfrute
- **Menor** → vínculo con peso, dolor, carga
- **Aumentada** → vínculo que se ha estirado más allá de lo sano (obsesión, dependencia, descontrol)
- **Disminuida** → vínculo roto, perdido, traicionado

Ejemplo: la quinta justa de Kive en octava 7 (relación pilar) puede pasar a quinta disminuida si esa relación se rompe. El slot sigue ocupado por la misma persona — pero la cualidad del vínculo ha cambiado. El espectro suena distinto.
