# Guía de voz y localización — LATINO AMÉRICA Zector Cero

**Locale base:** `es-419` (español latinoamericano)  
**Estado:** guía aprobada para redacción; los textos de ejemplo aún no están insertados en la ROM.  
**Regla crítica:** no ejecutar una prueba de ROM que se presente como prueba de localización hasta identificar y revisar el archivo de textos realmente usado, su codificación y su tabla de saltos de línea.

## Hallazgo actual del repositorio

La rama `main` no contiene todavía una tabla de traducción ni un archivo de diálogo conectado al motor. Por tanto, no se puede afirmar honestamente que la traducción actual de la ROM ya use esta jerga. Se establece aquí un paquete original de voz y diálogo para integrar cuando se identifiquen la fuente de texto y el importador. No se copia texto del guion original de Metroid Fusion.

## La voz del juego

El español debe sentirse caribeño y callejero. La base cotidiana es **dominicana**; el habla cubana y puertorriqueña aparecen con fuerza en personajes concretos; el patois jamaiquino se usa en la voz propia del personaje jamaiquino y en mensajes de radio. México, Colombia y Argentina quedan como variantes opcionales para personajes invitados o comunicaciones puntuales.

Objetivo práctico para el conjunto de conversaciones, no una cuota mecánica por línea:
- **Dominicana:** 50–60 % de los intercambios, con expresiones y ritmo locales.
- **Cubana:** 10–15 %, principalmente en la voz del mecánico Lázaro.
- **Puertorriqueña:** 10–15 %, principalmente en la voz de Lía.
- **Patois jamaiquino:** 5–10 %, en los mensajes y conversaciones de Kade, sin convertirlo en una colección de frases turísticas.
- **Mexicana, colombiana y argentina:** participaciones ocasionales, habilitables cuando el personaje y la escena lo justifiquen.

Estos porcentajes sirven de brújula para el guion, no de estadística de traducción ni de afirmación sobre la población de Villa Duarte.

## Reglas de escritura

1. **La jerga debe ser abundante, pero comprensible.** Como regla de revisión, la mayoría de las líneas de personaje debe contener una marca coloquial, un giro regional, una muletilla o un remate cómico. No metas cinco expresiones en una misma frase solo para demostrar que existen.
2. **Cada personaje mantiene su voz.** Yeyo y Majo usan dominicanismos; Lázaro, cubanismos; Lía, puertorriqueñismos; Kade usa patois donde le salga naturalmente y español cuando habla con la cuadrilla. No hagas que todos hablen igual.
3. **La comedia nace de la situación.** Chistes sobre portones, apagones, callejones, herramientas, alarmas, planes absurdos y supervivencia; no burlas sobre nacionalidad, acento, pobreza o identidad cultural.
4. **Nada de acentos escritos de forma ilegible.** Usar contracciones como `ta'`, `pa'` o `na'` con moderación. No deformar cada palabra para representar la pronunciación.
5. **No sustituir términos de interfaz por jerga.** Salud, energía, inventario, guardar, continuar, confirmar, puerta bloqueada y objetivo deben ser claros. La jerga va en diálogos, mensajes de radio y reacciones.
6. **El patois no es “español con acento”.** Es una lengua criolla jamaicana con historia y orgullo cultural propios. Kade no es un chiste ambulante; entiende la situación, tiene competencia técnica y su humor no se basa en que hable distinto.
7. **Evitar la mezcla sin contexto.** Un mismo personaje no alterna al azar `asere`, `acho`, `parce`, `che` y `no manches`. Las expresiones viajan a través de personajes y encuentros.
8. **Mantener la intención del texto.** Si una línea viene de un recurso de juego existente, conservar quién habla, qué información transmite, el orden de decisiones y las consecuencias. El texto original de este paquete es nuevo; no reemplaza texto de la ROM automáticamente.
9. **Pensar en el tamaño de pantalla.** Se parte de una guía de 28 caracteres por línea, con saltos manuales en `lines`. El límite real solo se decide al comprobar la fuente, la fuente tipográfica, la caja de diálogo y el motor.
10. **No ocultar texto cortado.** Antes de una prueba de ROM, revisar saltos, caracteres acentuados, signos, apóstrofos, tildes, longitud y codificación byte a byte.

## Personajes y registros

### Yeyo — dominicano, corredor del barrio
Rápido, observador, descarado, con humor seco. Vocabulario base: `qué lo que`, `vaina`, `diache`, `dique`, `tiguere`, `jevi`, `boche`, `guayar la yuca`, `resolver`, `pariguayo`. No usar todos juntos. La expresión `guayar la yuca` se puede usar para trabajar duro o pasar trabajo, según el contexto.

### Majo — dominicana, reparadora y estratega
Sarcástica, práctica y menos fanfarrona que Yeyo. Remata los planes absurdos. Usa `no me vengas con esa vaina`, `eso no me cuadra`, `te voy a dar un boche` o un refrán cuando encaje; no es una caricatura de una mujer gritona.

### Lázaro — cubano, mecánico
Ingenioso, directo, resuelve lo que otros dan por perdido. Vocabulario base: `asere`, `¿qué bolá?`, `ñó`, `resolver`, `en candela`, `en la fuácata`. Se usa con sentido: `en candela` puede señalar que algo está complicado o peligroso, no que todo esté literalmente ardiendo.

### Lía — puertorriqueña, operadora de radio
Aguda, segura, responde con rapidez. Vocabulario base: `acho`, `mano`, `bendito`, `zumba`, `brutal`, `janguear`. El anglicismo no se usa en cada oración: el personaje sabe cuándo hablar claro y cuándo bromear.

### Kade — jamaiquino, técnico de radio y sonido
Calmado cuando los demás pierden la cabeza. Usa Patois/patwa auténtico en saludos, énfasis y despedidas, y español al coordinar una acción con la cuadrilla. Frases elegidas con contexto: `Wha' gwaan?` (saludo, “¿qué pasa?”), `Wha'appen?` (saludo entre amistades), `Nuff` (mucho/bastante), `Rhaatid!` (sorpresa, “¡wow!”), `Bless up` (saludo o buenos deseos), `Walk good` (despedida: cuídate), `Criss` (bien/fino) y `bashment` (fiesta o evento animado). No añadirlas como adornos sin sentido.

### Voces opcionales en cameos
- **México:** `no manches`, `órale`, `no hay bronca`; el registro puede variar y alguna expresión es vulgar.
- **Colombia:** `parce`, `bacano`, `una chimba` solo cuando el personaje y el contexto lo admitan.
- **Argentina:** `che`, `quilombo`, `boludo` con prudencia; son informales y pueden ser insultos según el tono.

Los cameos son opcionales: no hace falta meter una voz de cada país en todos los escenarios.

## Muestra del tono deseado

- **Yeyo:** «Dique que el atajo era por aquí. Mi brújula es más pariguaya que yo».
- **Majo:** «Ese portón no está trancao: está haciendo un posgrado en no abrir».
- **Lázaro:** «Asere, eso está en candela. Y no, no es una función extra».
- **Lía:** «Acho, mano, ¿quién diseñó este pasillo? ¿Un arquitecto con claustrofobia al revés?».
- **Kade:** «Rhaatid! Nuff cable up there. Mira por dónde pisas, mi gente».
- **Kade, al despedirse:** «Bless up. Walk good».

## Puerta obligatoria antes de probar la ROM

Una prueba de juego no valida por sí sola la traducción. Antes de declarar aprobada la localización, deben completarse estas comprobaciones:

- [ ] Identificar la ROM de trabajo, parche o variante de traducción exactos, con hash y procedencia.
- [ ] Localizar la fuente de textos/tabla de traducción realmente usada. Si solo vive dentro de la ROM, extraerla sin modificar la copia original.
- [ ] Registrar codificación, tabla de caracteres, compresión, límites de bytes y rutina de saltos de línea.
- [ ] Asociar las líneas reales a IDs estables y mapear el texto nuevo a esos IDs; no inventar IDs de texto de la ROM.
- [ ] Revisar español, dialecto, contexto, humor y consistencia de cada hablante.
- [ ] Validar caracteres acentuados, ¿¡, apóstrofos del patois y caracteres admitidos por la fuente.
- [ ] Ejecutar comprobación automática de longitud y saltos de línea contra las dimensiones reales del cuadro.
- [ ] Solo después realizar la prueba en emulador y comprobar que las líneas aparecen completas, en el momento correcto y sin corromper otras pantallas.

**Estado actual:** la rama principal no contiene un fichero de traducción de ROM identificable en el árbol revisado. El catálogo de muestra es un borrador original listo para revisión; no se ha inyectado ni probado en la ROM.
 
## Referencias de consulta

- Academia Dominicana de la Lengua, [El Diccionario fraseológico del español dominicano](https://academia.org.do/2016/06/02/el-diccionario-fraseologico-del-espanol-dominicano/): documenta la importancia del uso contextual de frases y locuciones dominicanas, incluida `guayar la yuca`.
- Fundéu Guzmán Ariza, [De palabra en palabra: guayar](https://academia.org.do/wp-content/uploads/2025/01/BOLETIN-DIGITAL-DE-LA-ACADEMIA-DOMINICANA-DE-LA-LENGUA-DE-ENERO-DE-2025.pdf): recoge sentidos coloquiales de `guayar` y `guayar la yuca`.
- Visit Jamaica, [Jamaican Patois](https://www.visitjamaica.com/discover-jamaica/people-heritage/language/): describe el patois como una variedad criolla con historia y enumera expresiones como `Wha' gwaan?`, `Bless up`, `Nuff`, `Rhaatid!`, `Walk Good`, `Criss` y `Bashment`.
- Universidad Carlos III de Madrid, [Manual para estudiantes visitantes — Puerto Rico](https://www.uc3m.es/secretaria-virtual/media/secretaria-virtual/doc/archivo/doc_mne_puerto-rico_mayaguez_guia/manual-para-estudiantes-visitantes.pdf): trata anglicismos y expresiones puertorriqueñas como `janguiar`.
- Cuban Spanish Academy, [Frases cubanas comunes](https://www.cubanspanishclasses.com/es/common-cuban-phrases/): referencia auxiliar para expresiones cubanas coloquiales.
- Academia Mexicana de la Lengua, [No mames](https://academia.org.mx/consultas/consultas-frecuentes/item/no-mames): explica el registro y la variante eufemística `no manches`.
- [Diccionario de Jergas de Habla Hispana](https://www.jergasdehablahispana.org/): consulta secundaria para comprobar significados y marcadores regionales.

Las fuentes guían la revisión del registro; no convierten una expresión en universal ni sustituyen una revisión con hablantes de cada región.
