# Plan maestro de transformación visual — LATINO AMÉRICA Zector Cero

**Versión:** 1.0 · **Fecha:** 27 de octubre de 2026  
**Estado:** planificación; ninguna fase nueva se considera completada. La identidad oficial del juego es **LATINO AMÉRICA Zector Cero**. La [guía de identidad visual de los siete escenarios](SEVEN_SCENARIO_VISUAL_IDENTITIES.md) y el [atlas vectorial](../../assets/concept/latino-america-zector-cero-seven-scenarios.svg) son los puntos de partida artísticos actuales.

## Objetivo

Transformar visualmente la ROM completa poco a poco, con revisiones pequeñas y reversibles. La primera sala es una prueba de calibración, no el alcance final. Debemos llevar un inventario de cobertura hasta incluir todas las áreas y categorías visuales aplicables. Mantendremos separadas dos salidas:

1. **Ruta ROM/GBA privada:** cambios compatibles con los límites reales de la consola, probados sobre una copia local que no se publica.
2. **Ruta de simulación independiente:** escenas y mecánicas editables en Unity o Unreal Engine, usando código propio y recursos con licencia verificada.

Una captura o atlas de 4096 × 4096 sirve para inspección, comparación o presentación. No convierte una ROM de GBA en un juego 4K: la pantalla original es 240 × 160 y el hardware limita tiles, paletas y memoria. Los archivos maestros sin escalar se conservan siempre.

## Control obligatorio antes de cada intento: pasado, presente y futuro

**Pasado:** revisar las ROMs y prototipos anteriores disponibles, comparar hashes y cambios reales, identificar errores conocidos y no reutilizar offsets/punteros sin comprobarlos.

**Presente:** confirmar qué archivos y herramientas están accesibles ahora, sus versiones y su estado real. No limitar automáticamente el trabajo a Codespaces; usar el entorno local de análisis y los conectores si existen. Nunca afirmar que se abrió una aplicación o se ejecutó una prueba sin evidencia.

**Futuro:** antes de escribir, prever regresiones en tiles, mapas, paletas compartidas, compresión, referencias, colisiones, animaciones, compatibilidad con emuladores, layouts móviles y la posibilidad de volver a la versión anterior.

Cada tarea debe terminar con una etiqueta real: **generado**, **comprobado estáticamente**, **probado en herramienta** o **probado en juego**. No declarar que toda la ROM está completada hasta que el inventario confirme la cobertura de todas las áreas y categorías aplicables.

## Dirección artística: Villa Duarte y sus barrios

La dirección artística principal debe estar inspirada específicamente en Villa Duarte, Santo Domingo Este, y en sus barrios. No convertir el lugar en un escenario urbano genérico. Las fotografías reales del sector son la referencia visual primaria; los juegos citados más adelante sirven solo para estudiar composición, atmósfera y legibilidad, no para decidir la identidad de los escenarios.

**Main Deck room 1 / Docking Bays es solo un benchmark técnico para explorar la ROM, no el referente artístico del juego.**

- **Arquitectura y calle:** fachadas residenciales de varias alturas y acabados, bloques y hormigón, pintura pastel o viva, rejas, galerías, balcones, persianas, muros bajos, pequeños talleres y comercios de planta baja.
- **Textura urbana:** aceras irregulares, asfalto parcheado, callejones, coches aparcados, bicicletas/motocicletas, cables aéreos y postes, plantas tropicales y sombras duras de sol. Usar solo lo que corresponda a la zona, sin llenar cada escena de clichés.
- **Comercio y vida cotidiana:** colmados, repuestos y talleres con identidad gráfica ficticia; envases, sillas y objetos cotidianos cuando haya espacio para ellos. Evitar estereotipos de residentes o pobreza.
- **Variantes por sector:** El Caliche, La Francia Nueva, Calero, Pueblo Nuevo, Los Molinos y Simonico no son intercambiables. Conseguir referencias específicas antes de asignar a cada zona una arquitectura o una distribución distintiva.
- **Paleta:** hormigón cálido, sombras frías azuladas/moradas, fachadas coral/rosa viejo/amarillo/menta/azul claro, vegetación tropical y acentos saturados pequeños. El neón/cyberpunk no es la identidad por defecto.
- **Pixel art:** mantener límites legibles a resolución nativa. El detalle no puede confundir plataformas, suelo, colisiones, jugador, enemigos, puertas ni pickups.
- **Diseño de zonas:** calles residenciales, callejones, interior de colmado/taller, patios, azoteas y pasos de servicio son posibilidades, no una lista obligatoria. Usarlas según progresión y referencias.
- **Fuentes de estilo y procedencia:** [Biblia visual Villa Duarte](VILLA_DUARTE_VISUAL_BIBLE.md), con referencias fotográficas a Villa Duarte, El Caliche y La Francia Nueva. Las fotos son referencias, no assets para copiar sin confirmar licencia.
- **Referencia de videojuego:** Castlevania: Aria of Sorrow para atmósfera y contraste; Spider-Man: Mysterio's Menace para ritmo urbano lateral; X-Men: Reign of Apocalypse para siluetas y claridad de combate. Se estudian principios, no se copian assets ni código.


## Reglas no negociables

1. No hacer cambios en masa sin muestras y aprobación de la dirección visual.
2. Guardar los recursos originales en una carpeta maestra sin alterar.
3. Recolorear por lotes pequeños con una tabla de correspondencia de colores.
4. No cambiar dimensiones, pivotes ni hitboxes sin registrarlo.
5. Mantener las variantes ROM-compatible, Unity y Unreal separadas.
6. No sobrescribir la ROM original. Cada prueba binaria produce una salida local separada.
7. No subir ROMs, binarios extraídos, ROMs derivadas ni parches al repositorio público.
8. Registrar la fuente y licencia de cada recurso externo.
9. Etiquetar cada conclusión como verificada, probable o pendiente.
10. Buscar referencias precisas a la tarea, motor, versión, formato, licencia y plataforma; no basta una búsqueda genérica de pixel art.

---

## Fase 0 — establecer el punto de partida

**Objetivo:** conseguir una línea base reproducible.

Tareas:
- Identificar la ROM local por tamaño, SHA-256, código de juego y checksum de cabecera.
- Localizar en MAGE la sala o recurso a estudiar y registrar ID, tileset, paleta, mapa, dimensiones, colisiones, puertas, objetos y enemigos.
- Guardar capturas originales a resolución nativa y una hoja de referencia por recurso.
- Registrar herramienta y versión, además de resolución y zoom de cada captura.
- Distinguir recurso del juego, ilustración de referencia y asset abierto.

**Entregable:** ficha de la sala/recurso, capturas originales y tabla de procedencia.

**Aceptación:** se puede encontrar el mismo recurso y repetir la captura sin adivinar offsets.

## Fase 1 — auditoría visual e inventario

**Objetivo:** saber qué hay antes de cambiarlo.

Separar recursos en:
- jugador y animaciones;
- enemigos y estados;
- jefes;
- tiles de suelo, techo, pared y plataformas;
- fondos y planos lejanos;
- puertas, ascensores y transiciones;
- objetos, pickups, proyectiles y efectos;
- interfaz, iconos y fuentes;
- paletas, tilesets y mapas de tiles.

Para cada recurso registrar:
- ID o ruta exacta de origen, ancho × alto y modo de color;
- transparencia y color de fondo;
- paleta y número aproximado de colores;
- tamaño de frame y número de frames;
- pivote, hitbox y zona de contacto si aplica;
- salas y animaciones que lo usan;
- uso previsto: ROM, Unity, Unreal o referencia;
- procedencia y licencia.

**Entregable:** inventario visual y lista de dependencias por sala.

**Aceptación:** ningún recurso candidato a edición queda sin fuente, dimensiones o copia de respaldo.

## Fase 2 — hoja de estilo y pruebas A/B

**Objetivo:** decidir cómo se verá el proyecto antes de recolorizar todo.

Crear un paquete pequeño con:
1. paleta maestra provisional de 16–24 colores para la ruta pixel art;
2. paletas derivadas para luz, sombra, peligro, interacción y fondo;
3. reglas de contorno, sombreado, volumen y contraste;
4. reglas para letreros y elementos dominicanos;
5. escala de sprites y regla de píxel;
6. comparación lado a lado: original, recolor A, recolor B y reinterpretación de alta resolución;
7. lista de elementos que deben seguir siendo reconocibles.

Las referencias comerciales se anotan con enlaces legítimos y comentarios de principios generales. No se incorporan sus imágenes como assets libres.

**Entregable:** guía visual v0.1 y hoja comparativa.

**Aceptación:** se elige una dirección para probar en una sala y un enemigo, no en todo el juego.

## Fase 3 — recoloración controlada

**Objetivo:** mejorar el color y la legibilidad sin destruir la identidad de las formas.

Orden:
1. registrar la paleta original del recurso concreto;
2. clasificar colores por función: luz, sombra, fondo, contorno, peligro, interacción y transparencia;
3. preparar una tabla de color original a color nuevo;
4. aplicar el mapa exacto a una copia;
5. comparar lado a lado y dentro del juego;
6. validar los límites de paleta si vuelve a la ruta ROM;
7. guardar versión, comparación visual y changelog.

Reglas:
- preservar alpha, transparencia y contornos;
- no reemplazar globalmente un color si cumple funciones diferentes en otros recursos;
- no introducir degradados que borren la lectura del píxel;
- la versión con detalle nuevo es un asset alternativo y no reemplaza al original;
- en ROM, confirmar los límites de paleta y el mapeo del tileset con MAGE antes de escribir.

**Entregable:** un enemigo y un pequeño conjunto de tiles recolorizados con comparación A/B.

**Aceptación:** se reconoce el diseño a tamaño nativo y no cambian hitboxes ni pivotes accidentalmente.

## Fase 4 — upscale y archivo maestro 4K

**Objetivo:** ampliar imágenes para revisión sin destruir la fuente pixelada.

Entregables por imagen:
- source_native.png: fuente original intacta;
- scale_nearest.png: ampliación por vecino más cercano;
- preview_4096.png: lienzo de 4096 × 4096 para inspección;
- metadata.json: tamaño fuente, factor, método, hash y fecha;
- opcional detail_enhanced.png: reinterpretación artística de alta resolución, claramente etiquetada como tal.

Regla de escalado:
- Nunca estirar una imagen 240 × 160 para hacerla cuadrada.
- Una captura GBA de 240 × 160 escalada con factor entero 16 produce 3840 × 2560. Se puede centrar en un lienzo de 4096 × 4096 y dejar márgenes transparentes o de presentación.
- Una hoja de sprites de 256 × 256 con factor 16 produce 4096 × 4096 exactos.
- Si el factor solicitado no cabe en el lienzo, fallar con un mensaje claro; no reducir ni deformar silenciosamente.
- Método maestro de pixel art: vecino más cercano (nearest). Los filtros bicúbico o Lanczos interpolan colores y no deben sustituir la versión maestra.
- Las versiones de IA/super-resolution quedan separadas; sus detalles inferidos se registran.

**Entregable:** exportación 4K con fuente intacta y metadatos de transformación.

**Aceptación:** proporción conservada, bordes nítidos, sin blur ni cambios de transparencia.

## Fase 5 — primer escenario completo

**Objetivo:** validar la dirección visual en una sola sala pequeña.

Composición de prueba:
- fondo/edificios;
- plano medio;
- suelo y plataformas;
- puertas y elementos interactivos;
- iluminación ambiental;
- jugador placeholder;
- un enemigo patrullero;
- interfaz mínima de salud/energía.

Probar tres variantes de fondo (más oscuro, más cálido y neutro) sin cambiar simultáneamente la silueta del jugador.

**Entregable:** sala de prueba y comparación con la fuente.

**Aceptación:** lectura clara a tamaño nativo, contraste suficiente y coherencia visual entre colisiones y superficies.

## Fase 6 — jugador y enemigos por lotes

Orden:
1. jugador idle;
2. caminar/correr;
3. salto, caída y aterrizaje;
4. ataque, daño y muerte;
5. un enemigo patrullero con ida y vuelta;
6. segundo enemigo para validar contraste;
7. proyectiles y efectos;
8. jefe después de aprobar los elementos base.

Para cada animación revisar duración por frame, pivote común, alineación del suelo, continuidad de volumen, hitbox, claridad de estado, escala y rendimiento móvil. No producir una galería entera de enemigos antes de probar uno en movimiento.

## Fase 7 — dos salidas editables: ROM y simulación

### A. Ruta ROM/GBA privada
- identificar con precisión el recurso y todas sus referencias;
- exportar/reimportar con herramientas compatibles y conservar una copia de la base;
- respetar tiles, paletas, mapas y compresión;
- escribir sobre una copia con nombre y hash propios;
- probar en emulador/depurador y comparar la sala objetivo;
- no publicar ROM ni parche derivado.

### B. Simulación independiente
Elegir un motor principal por prototipo. No desarrollar dos juegos completos en paralelo antes de validar el diseño.

**Unity 2D**
- escenas, prefabs y código C# editables;
- scripts para movimiento, cámara, enemigo patrullero y controles;
- Pixel Perfect Camera y ajustes de importación compatibles con la versión del proyecto;
- perfiles de cámara y composición por aspecto.

**Unreal Engine**
- Paper 2D: Sprites, Flipbooks, Tile Sets y Tile Maps;
- ajustes de importación Paper 2D para conservar bordes pixelados;
- lógica en Blueprint y/o C++ editable, con nombres claros;
- configuración de plataforma y perfil de rendimiento móvil.

Antes de generar código, buscar referencias oficiales de la versión instalada. Entregar archivos editables, rutas, dependencias, instrucciones de importación/compilación y una prueba mínima, no solo pseudocódigo. Si Codespaces no tiene instalado un editor gráfico, distinguir código preparado de prueba real dentro del editor.

## Fase 8 — móvil horizontal y vertical

Diseñar ambos layouts por separado.

### Horizontal — formato tradicional
- cámara lateral principal;
- jugador y enemigo legibles;
- HUD separado de la zona de combate;
- controles táctiles para ambas manos;
- respetar safe areas y recortes de pantalla;
- mantener proporciones sin estirar sprites.

### Vertical
- cámara y composición adaptadas, no una simple rotación del layout horizontal;
- ventana de juego compacta, con HUD y controles en zonas dedicadas;
- valorar cámara más próxima, mayor altura visible o un marco lateral dentro del layout vertical;
- si la jugabilidad requiere lateralidad, preservar la vista lateral dentro del marco vertical o adaptar el encuadre por sala;
- controles apilados y accesibles sin tapar enemigos, puertas ni señales;
- probar distintas relaciones de aspecto, notch y áreas seguras.

**Entregables:** dos layouts independientes y capturas comparativas vertical/horizontal.

**Aceptación:** en ambas orientaciones se distinguen jugador, suelo, amenaza y salida; no hay texto cortado ni botones sobre los puntos de combate.

## Fase 9 — investigación exacta y referencias

Para cada problema, buscar por problema, herramienta, versión, formato y plataforma. Priorizar documentación oficial, README, código fuente de la herramienta y recursos con licencia verificable. Abrir y validar las páginas antes de citarlas.

Cada nota debe incluir problema concreto, versión, fuente/URL, afirmación respaldada, aplicación al proyecto y limitaciones. Si no hay navegación web disponible en la sesión, declarar esa limitación y no fingir una búsqueda actual.

**Entregable:** nota breve con referencias y consecuencias prácticas para el asset o el proyecto.

## Fase 10 — control de calidad y aprobación

Cada lote necesita:
- original, variante nueva y diff visual;
- dimensiones, formato, paleta y transparencia comprobados;
- prueba de cámara a tamaño nativo;
- una captura horizontal y una vertical si corresponde;
- estado: no probado, validado estáticamente o probado en motor;
- fuente/licencia y método de reversión.

No avanzar a la siguiente fase hasta aceptar el lote actual.

## Primera iteración recomendada

El primer sprint se limita a:
1. elegir una sala benchmark;
2. registrar captura nativa, tiles y paletas que la componen;
3. crear tres tratamientos de color para el fondo, conservando el original;
4. recolorizar un enemigo patrullero;
5. generar versión nearest y lienzo 4096 × 4096;
6. probar la sala en marco horizontal y layout vertical;
7. elegir dirección de arte antes de aplicarla a más salas.

El primer objetivo medible es una sala coherente, editable y comparada. Una vez aprobada la dirección visual, el trabajo se propaga por las demás salas, tilesets, paletas, sprites, animaciones, enemigos, efectos y elementos de interfaz hasta cubrir la ROM completa. La primera sala no es el límite del proyecto.

## Fuentes técnicas oficiales

- Unity Pixel Perfect Camera: https://docs.unity.com/en-us/engine/6000.0/manual/unity2d/2d-urp/2d-pixelperfect
- Preparación de sprites en Unity: https://docs.unity.com/en-us/engine/7000.0/manual/unity2d/2d-urp/2d-pixelperfect/prep-sprites
- Unity Android orientación: https://docs.unity.com/en-us/engine/6000.0/manual/platform-specific/android/getting-started/class-player-settings
- Unreal Paper 2D: https://dev.epicgames.com/documentation/en-us/unreal-engine/2d-in-unreal-engine
- Unreal Paper 2D sprites: https://dev.epicgames.com/documentation/en-us/unreal-engine/how-to-import-and-use-paper-2d-sprites-in-unreal-engine
- Unreal Android orientation: https://dev.epicgames.com/documentation/unreal-engine/android-settings-in-the-unreal-engine-project-settings
- Pillow nearest-neighbour resize: https://pillow.readthedocs.io/en/stable/reference/Image.html

Estas fuentes describen opciones técnicas, pero no deciden por nosotros la dirección artística.
