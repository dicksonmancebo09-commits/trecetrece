# Plan maestro de transformación visual — Villa Duarte: Sector Cero

**Versión:** 1.0 · **Fecha:** 27 de octubre de 2026  
**Estado:** planificación; ninguna fase nueva se considera completada.

## Objetivo

Transformar la presentación visual poco a poco, con revisiones pequeñas y reversibles. Mantendremos separadas dos salidas:

1. **Ruta ROM/GBA privada:** cambios compatibles con los límites reales de la consola, probados sobre una copia local que no se publica.
2. **Ruta de simulación independiente:** escenas y mecánicas editables en Unity o Unreal Engine, usando código propio y recursos con licencia verificada.

Una captura o atlas de 4096 × 4096 sirve para inspección, comparación o presentación. No convierte una ROM de GBA en un juego 4K: la pantalla original es 240 × 160 y el hardware limita tiles, paletas y memoria. Los archivos maestros sin escalar se conservan siempre.

## Dirección artística provisional

- **Lugar:** barrio dominicano reconocible: balcones y galerías, fachadas de bloques y hormigón, persianas metálicas, cables aéreos, aceras, postes, colmado, letreros, motor-concho y carros compactos.
- **Lectura de juego:** siluetas del jugador y los enemigos claras contra el fondo. Suelo, plataformas, puertas y objetos interactivos deben distinguirse inmediatamente.
- **Paleta:** caribeña urbana, con luz cálida, hormigón, sombras azuladas/moradas y acentos específicos para peligro e interacción. Es una hipótesis que se valida con muestras, no un cambio masivo.
- **Lenguaje visual:** preservar la lectura del pixel art en la ruta retro. No suavizar bordes por defecto. Cualquier versión con detalle añadido será una variante separada.
- **Referencias:** Castlevania: Aria of Sorrow para atmósfera y contraste; Spider-Man: Mysterio's Menace para ritmo urbano lateral; X-Men: Reign of Apocalypse para siluetas y claridad de combate. Se estudian principios visuales, no se copian sprites, mapas, animaciones, música ni código comercial.
- **Identidad propia:** los personajes, emblemas, escenarios, nombres, animaciones y assets finales deben ser propios o tener licencia compatible.

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

El primer objetivo medible es una sala coherente, editable y comparada. No es una ROM final ni un juego completo.

## Fuentes técnicas oficiales

- Unity Pixel Perfect Camera: https://docs.unity.com/en-us/engine/6000.0/manual/unity2d/2d-urp/2d-pixelperfect
- Preparación de sprites en Unity: https://docs.unity.com/en-us/engine/7000.0/manual/unity2d/2d-urp/2d-pixelperfect/prep-sprites
- Unity Android orientación: https://docs.unity.com/en-us/engine/6000.0/manual/platform-specific/android/getting-started/class-player-settings
- Unreal Paper 2D: https://dev.epicgames.com/documentation/en-us/unreal-engine/2d-in-unreal-engine
- Unreal Paper 2D sprites: https://dev.epicgames.com/documentation/en-us/unreal-engine/how-to-import-and-use-paper-2d-sprites-in-unreal-engine
- Unreal Android orientation: https://dev.epicgames.com/documentation/unreal-engine/android-settings-in-the-unreal-engine-project-settings
- Pillow nearest-neighbour resize: https://pillow.readthedocs.io/en/stable/reference/Image.html

Estas fuentes describen opciones técnicas, pero no deciden por nosotros la dirección artística.
