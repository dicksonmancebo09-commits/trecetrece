# Barrido estático de la ROM completa — 2026-10-28

## Resultado real y alcance

Se recorrieron los **8 MiB completos** de la copia local y se contrastó la identidad con el inventario previo. Este informe es un análisis estático de bytes, cabecera, flujo de arranque, tabla de modos, punteros alineados, streams LZ77 completos, texto ASCII heurístico y entropía por bloques. **No es una descompilación semántica completa ni una reconstrucción jugable.** En este entorno no están instalados REA ni Ghidra, y en esta pasada no se ejecutó una traza dinámica de mGBA.

## Identidad y cabecera

- Título GBA: `METROID4USA`; código: `AMTE`; tamaño: `8,388,608` bytes (8 MiB).
- SHA-256: `a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8`.
- SHA-1: `ca33f4348c2c05dd330d37b97e2c5a69531dfe87`.
- Checksum de cabecera: el byte leído y el esperado son `0x98`; la cabecera es válida.
- La instrucción inicial `0xEA00002E` salta de `0x08000000` a `0x080000C0`. El bloque de cabecera `0xA0–0xBD` es dato, no código ARM.
- El arranque ARM observado prepara las pilas IRQ/Sistema, instala una dirección de servicio de interrupción en `0x03007FFC` y transfiere control al puntero Thumb `0x08000231` (código alineado en `0x08000230`).

## Despachador de estados

En `0x08000230` el código Thumb lee el modo desde RAM `0x03000BDE`, comprueba el rango de 0 a 14 y usa la tabla de punteros situada en el offset de ROM `0x278` (`0x08000278`). Se han confirmado estas 15 entradas de tabla; las etiquetas son nombres descriptivos cruzados con la referencia de código de la versión correspondiente, no nombres recuperados de símbolos de la ROM:

| Modo | Etiqueta de trabajo | Destino GBA |
|---:|---|---:|
| 0 | TITLE | `0x080002B4` |
| 1 | IN_GAME | `0x08000448` |
| 2 | SOFT_RESET | `0x08000548` |
| 3 | MAP_SCREEN | `0x080004D0` |
| 4 | CUTSCENE | `0x0800054E` |
| 5 | SA_X_CLOSE_UP | `0x080005D0` |
| 6 | ERASE_SRAM_MENU | `0x080005E4` |
| 7 | FILE_SELECT_OR_INTRO | `0x080003AC` |
| 8 | GAME_OVER | `0x08000624` |
| 9 | ENDING | `0x0800069C` |
| 10 | DIED_FROM_SR388_COLLISION | `0x080006B0` |
| 11 | CREDITS | `0x080006D0` |
| 12 | DEMO | `0x080006E4` |
| 13 | UNKNOWN | `0x08000730` |
| 14 | DEBUG | `0x0800074C` |

Esto identifica la columna vertebral del flujo global, pero no explica todavía toda la lógica interna de cada modo ni los eventos que cambian de estado.

## Barrido estructural de los 8 MiB

- **55,984** palabras alineadas de 32 bits cuyo valor cae dentro de la ventana de ROM `0x08000000–0x087FFFFF`; representan **30,898 destinos únicos**. Esto sirve para buscar referencias, pero incluye coincidencias y valores que no son punteros efectivos.
- **464** streams `0x10` que el decodificador LZ77 pudo consumir completos hasta la longitud declarada, probando inicios alineados a 2 y 4 bytes.
- **386** de esos inicios de LZ77 también tienen al menos una referencia exacta entre las palabras-puntero escaneadas. Son candidatos prioritarios, no una clasificación automática como tiles, mapas o sprites.
- **35,295** segmentos ASCII imprimibles de seis bytes o más. El conteo es deliberadamente mecánico; incluye secuencias accidentales de datos y no equivale a 35,295 cadenas legibles del juego.
- El barrido de entropía cubrió cada bloque de 64 KiB. Como patrón general, `0x400000–0x680000` contiene muchas ventanas de entropía alta compatibles con datos compactados; `0x280000–0x380000` y `0x680000–0x740000` tienen más estructura/bytes repetidos. Son descripciones estadísticas, no etiquetas de recurso confirmadas.
- El último byte distinto de `0xFF` está en `0x79ECC7`; desde `0x79ECC8` hasta el final hay **398,136 bytes de relleno `0xFF`**.

### Zonas con mayor concentración de streams LZ77 completos

Los inicios se concentran especialmente en `0x3F0000–0x450000`, `0x480000–0x530000`, `0x570000–0x670000` y `0x730000–0x79FFFF`. El JSON adjunto ofrece el conteo por ventana de 64 KiB y los candidatos de mayor tamaño con offset, longitud comprimida, longitud descomprimida y referencias.

### Referencias que conviene resolver primero

Los destinos con más referencias exactas dentro del barrido alineado incluyen `0x083BF884` (683), `0x0828998E` (641), `0x08080808` (304), `0x0828998C` (211), `0x083BF850` (195) y `0x080A6D54` (128). El destino `0x08080808` es un buen recordatorio de que el conteo de palabras por sí solo no certifica un puntero legítimo; se deben verificar alineación, contexto de código y uso en ejecución.


## Comprobación visual de una muestra de recursos

Además del conteo automático, se decodificaron visualmente 36 candidatos con salida de al menos `0x2000` bytes y referencia exacta de puntero. Se interpretaron provisionalmente como tiles GBA de 4 bpp, en mosaicos de 8×8 píxeles y escala de grises. En múltiples bloques aparecen estructuras visuales coherentes —piezas de escenarios, paneles, iconos, efectos y arte de personajes/cinemáticas—, lo que confirma que una parte de los candidatos LZ77 contiene gráficos reales y no solo coincidencias estadísticas.

Offsets representativos de la muestra: `0x3EF960`, `0x42011C`, `0x5438F8`, `0x5A44CC`, `0x5B4580`, `0x5C9B4C`, `0x5DB5CC`, `0x5EDF70`, `0x60093C`, `0x605D08`, `0x6238F4`, `0x65C468`, `0x65FC24`, `0x66EC18`, `0x75ED6C` y `0x770084`.

Esta visualización no identifica todavía el nombre funcional de cada recurso: falta conocer la paleta real, el orden de tiles, las tablas que los referencian y el punto del juego que los carga. No se debe editar esos offsets a ciegas.

## Qué se puede afirmar ya

1. La identidad y cabecera de la ROM son coherentes.
2. El arranque ARM/Thumb y la tabla central de 15 modos están localizados.
3. La ROM no es una masa homogénea: el scan detecta regiones con muchos punteros, candidatos LZ77 completos, datos repetitivos y relleno final.
4. Se puede priorizar el trabajo sobre tablas con muchas referencias y los bloques comprimidos que además son apuntados.

## Qué sigue pendiente para completar el análisis del juego

- Desensamblar y delimitar funciones en ARM7TDMI, distinguiendo ARM y Thumb y evitando tratar tablas/recursos como instrucciones.
- Clasificar cada bloque LZ77 y enlazarlo con sus punteros consumidores; confirmar formato y uso de gráficos/mapas/sprites.
- Reconstruir tablas de salas, puertas, colisiones, objetos y metadatos; contrastarlas con MAGE cuando esté disponible.
- Seguir en mGBA el arranque y transiciones de modo, y luego movimiento/física, enemigos, proyectiles, jefes, eventos, texto, audio y guardado.
- Validar toda rutina reconstruida contra la ejecución real antes de presentarla como equivalente.

El proceso de REA/Ghidra y el trazado dinámico no quedan certificados por este informe: esos pasos siguen pendientes de ejecutarse en el Codespace/entorno que tenga las herramientas correspondientes. No se ha guardado la ROM ni un parche binario en el repositorio.
