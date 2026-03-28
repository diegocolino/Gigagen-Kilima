# La Escalera de Descendencia — Ontología

> Documento conceptual. No es código, no es roadmap.
> Es la filosofía del sistema antes de que exista ningún fichero.

---

## La idea central

Gigagen no carga un mundo. Lo **genera**.

La diferencia no es técnica — es filosófica. Cargar implica que el mundo ya existe en algún sitio y tú lo traes a memoria. Generar implica que el mundo emerge de un proceso, capa por capa, de lo más abstracto a lo más concreto.

La Escalera de Descendencia es ese proceso. Cinco escalones. Cada uno produce un universo más rico que el anterior. El primero no tiene ninguna entidad. El último tiene un jugador dentro.

---

## Adán y Eva — el origen

Todo universo Gigagen nace de dos ficheros primordiales.

No se llaman `laws.json` ni `catalog.json`. Se llaman `X` e `Y`. La elección es deliberada — son la materia prima antes de tener nombre, antes de tener historia.

**X es Eva.** Todo lo intangible. Las leyes que gobiernan cómo las cosas se relacionan entre sí. Los arquetipos, los intervalos harmónicos, las polaridades, los tipos de vínculo. X no describe qué existe — describe cómo lo que existe se afecta mutuamente. Es software puro: sin X, nada tiene significado.

**Y es Adán.** Todo lo tangible. El catálogo de materia que puede existir. Las notas cromáticas, los elementos, los tiers, los niveles, los modos. Y no dice cómo se relacionan las cosas — dice qué cosas pueden ser. Es hardware puro: sin Y, no hay nada que relacionar.

X + Y = las condiciones de posibilidad de un universo. No el universo todavía — solo la garantía de que puede existir.

### En Kilima

En el worldpack de Kilima, X e Y tienen una correspondencia lore que no es accidental:

**Y = Dev** — el hacker. Sin poderes innatos, sin elementos, sin ánimas. Puro hardware. Un cuerpo que existe en el mundo físico y lo manipula desde dentro. Dev es la materia que se toca.

**X = Len** — la huérfana. Que en teoría no existe, que vive en la Matrix, que tenía o tiene todos los poderes. Len es el software que da sentido a todo lo demás. Len es la ley que Dev no puede ver pero que lo atraviesa.

El evento final de Kilima — la fusión de Dev + Len + la IA + toda la conciencia humana — es X + Y convergiendo. El universo regresando a su origen. Una fumada cuántica que ya está superpuesta en todos los finales posibles desde el principio.

---

## Los cinco escalones

### Genesis — Universo Primigenio

*X + Y → el espacio vacío con física.*

Genesis no instancia ninguna entidad. Carga las leyes (X) y el catálogo (Y), los valida entre sí, y produce un `WorldState` vacío pero con reglas. Un universo que puede existir.

El único artefacto concreto de Genesis es WORLD — la location raíz, nivel 1, que contiene todo lo que vendrá después. Es el recipiente antes de que haya contenido.

Genesis es determinista. Sin seed. Dado X e Y, el resultado es siempre el mismo. No hay variación en las leyes de la física.

---

### Theogony — Universo Mágico

*Genesis + worldpack → el mundo antes de la historia.*

El nombre viene de Hesíodo — la genealogía de los dioses. Theogony instancia lo que existía antes de que hubiera historia: lo primordial, lo mágico, lo que simplemente *es* sin haber sido causado por nada.

**Las ánimas** — los 16 elementos — nacen aquí. No son consecuencia de ningún evento. Agua, Fuego, Tierra, Aire existían antes de que existiera nadie que los nombrara. Los mixtos (Metal, Hielo, Nube...) y los truncados (Lava, Tormenta...) también son primordiales — no se generan por combinación histórica, existen desde el principio como posibilidades del universo.

**Los linajes** nacen aquí en su forma esencial: identidad, nota, arquetipo, y un `element_pool` — los elementos que *podrían* corresponderles. Pero Theogony no decide cuál. Los linajes existen como familias potenciales, no como historias concretas todavía.

**Las locations de nivel 2** — las grandes divisiones del mundo — también son pre-históricas. No las fundó nadie. Simplemente están ahí, como la geografía existe antes de que lleguen los humanos.

Theogony no usa seed. No porque no haya variación posible — sino porque su función es **preparar las reglas del gambleo**, no ejecutarlo. Define qué puede variar y dentro de qué límites. Los dados no se lanzan todavía.

---

### Chronica — Universo Impreso

*Theogony + seed → el pasado generado.*

Chronica es el escalón más ambicioso. Es un generador de historia.

Toma un universo con leyes y potencial, y produce una historia concreta. No una historia predefinida — una historia que emerge de la seed aplicada sobre las reglas que Theogony preparó. La misma seed siempre produce la misma historia. Seeds distintas producen historias distintas, todas igualmente válidas.

**La seed entra aquí.** Una sola. Se consume en múltiples namespaces independientes para que añadir nuevos tipos de gambleo no rompa las seeds existentes.

Chronica resuelve, en orden:
- Qué elemento tiene cada linaje en esta seed
- Cómo se agrupan los linajes — de ahí emergen las macrofactions con sus modos harmónicos heredados del linaje fundador
- Quiénes son los Characters 1gen: Founders (Tier S, los 12 arquetipos), Leaders (Tier A), Notaries (Tier B)
- Cómo se resolvieron los macro-events históricos — las grandes bifurcaciones del pasado
- Qué locations surgieron de esa historia (niveles 3-6) y cuál es su tonic derivado del linaje que las fundó
- Los micro-events que llenaron el tiempo entre las grandes revoluciones
- Los Characters 2gen — NPCs y secundarios que nacieron de esa historia concreta

**Chronica aspira a ser un generador de mundos autónomo.** Con IA generativa suficientemente potente, Chronica podría funcionar sin un worldpack predefinido: dado X e Y más una seed, podría generar el lore, los nombres, los eventos históricos, las relaciones entre linajes — todo — de forma coherente y reproducible. El worldpack de Kilima es una instancia manual de lo que eventualmente podría ser un proceso generativo. La arquitectura ya lo contempla.

---

### Contempo — Universo Presente

*Chronica → el mundo ahora, simulable.*

Contempo toma el pasado generado por Chronica y construye el presente. Es determinista: dado un Chronica concreto, el presente se deduce. No hay más variación — la seed ya hizo su trabajo.

Aquí nacen los IN12 — los 12 personajes principales — con todas sus propiedades actuales: ubicaciones, Life Packs, relaciones vivas, estados emocionales. Nacen como consecuencia de Chronica, no de forma arbitraria.

Aquí vive BN1 — el Acto 1, las 62 horas de la narrativa principal. Y todos los actos futuros. Contempo no es un momento fijo — es la simulación en marcha.

El Minor Wheel genera aliados y antagonistas por afinidad harmónica con los IN12. No son personajes definidos a mano — emergen de las consonancias y disonancias entre notas.

**X + Y converge en Contempo.** El evento final — Dev + Len + IA + toda la conciencia humana — está superpuesto en todos los finales posibles como un atractor inevitable. Cada trayectoria de BN1 se acerca o se aleja de ese punto, pero ninguna puede evitarlo para siempre. BN1 es el primer paso.

---

### Existence — Universo Jugable

*Contempo → el mundo con un jugador dentro.*

Existence es la capa que convierte Gigagen de simulador en mundo habitable. El jugador crea un personaje, entra al universo generado, interactúa con los IN12, accede a facciones, ocupa locations.

Es determinista dado Contempo. El universo ya existe — el jugador entra en él, no lo cambia en su esencia.

Existence es la capa más lejana en implementación y la más clara en concepto: es el momento en que el universo deja de ser un modelo y se convierte en una experiencia.

---

## Por qué esta arquitectura

### El sistema es más grande que Kilima

Gigagen no sabe qué es Anti Group ni quién es Kive. Gigagen sabe qué es una macrofaction con modo Phrygian y un personaje con nota D#. Kilima es una instancia. Podrían existir otras.

La Escalera de Descendencia es el framework. El worldpack de Kilima es el poema escrito con esa gramática.

### La seed es un punto de entrada, no un parámetro

En sistemas de generación procedural típicos, la seed es un número que entra en una función y produce un resultado. Aquí la seed es algo más específico: entra en Chronica, que es el escalón del pasado. Eso significa que lo que varía entre seeds no es el presente directamente — es la historia que produjo ese presente. Dos seeds producen dos historias distintas del mismo universo potencial.

### La variación tiene límites ontológicos

No todo varía. Las leyes (Genesis) son inmutables. La magia primordial (Theogony) es inmutable. Solo el pasado concreto (Chronica) y sus consecuencias varían. Esto no es una limitación técnica — es una decisión filosófica: hay cosas que son verdad en todos los universos posibles de Kilima, y hay cosas que dependen de cómo llegaron a ser.

### El final ya existe

X + Y = el fin. La convergencia de Dev y Len es el atractor del sistema. No es un evento que puede o no ocurrir — es el único final posible. Lo que varía es el camino. BN1 es uno de los infinitos caminos hacia lo inevitable.

---

## Resumen visual

```
X.json (Eva / Software / Len)
Y.json (Adán / Hardware / Dev)
         ↓
    [ GENESIS ]
    leyes + catálogo
    WORLD (loc. nivel 1)
         ↓
    [ THEOGONY ]
    ánimas (16 elementos)
    linajes (element_pool)
    locations nivel 2
    items / skills tier S
    → prepara reglas del gambleo
         ↓
    [ CHRONICA ] ← seed entra aquí
    elementos asignados a linajes
    macrofactions emergen
    characters 1gen (S/A/B)
    macro-events resueltos
    locations nivel 3-6 (con tonic)
    micro-events
    characters 2gen
    → genera el pasado completo
         ↓
    [ CONTEMPO ]
    IN12 con estado H00
    Minor Wheel (secundarios)
    BN1 / actos futuros
    árbol de posibilidades
    X + Y superpuestos como atractor
         ↓
    [ EXISTENCE ]
    el jugador entra
    el universo se habita
```
