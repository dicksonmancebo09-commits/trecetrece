# Cola de trabajo: recursos comprimidos prioritarios

Fecha: 2026-10-28  
ROM examinada: `METROID4USA`, código `AMTE`, 8 MiB. SHA-256: `a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8`.

## Fase siguiente

El barrido estático detectó 464 streams LZ77 completos. Esta cola prioriza bloques que tienen referencia exacta de puntero y salida descomprimida de al menos 8 KiB. El orden es una heurística para elegir por dónde empezar a investigar; **no asigna nombres ni garantiza que cada bloque sea un gráfico**.

| ID | Prioridad | Offset ROM | Comprimido | Descomprimido | Referencias exactas | Ratio |
|---|---|---:|---:|---:|---:|---:|
| LZ001 | P1 | `0x3F6C34` | 6,995 | 13,568 | 12 | 1.940 |
| LZ002 | P1 | `0x3EF960` | 3,795 | 8,960 | 11 | 2.361 |
| LZ003 | P1 | `0x65C468` | 14,065 | 32,768 | 6 | 2.330 |
| LZ004 | P2 | `0x598898` | 497 | 2,048 | 19 | 4.121 |
| LZ005 | P1 | `0x60BCA4` | 17,684 | 32,768 | 3 | 1.853 |
| LZ006 | P1 | `0x6101B8` | 11,405 | 32,768 | 3 | 2.873 |
| LZ007 | P1 | `0x65FC24` | 11,230 | 23,552 | 7 | 2.097 |
| LZ008 | P1 | `0x42011C` | 8,487 | 17,280 | 7 | 2.036 |
| LZ009 | P1 | `0x590C9C` | 7,896 | 32,768 | 2 | 4.150 |
| LZ010 | P1 | `0x593274` | 12,611 | 32,768 | 2 | 2.598 |
| LZ011 | P1 | `0x5E116C` | 14,455 | 32,768 | 2 | 2.267 |
| LZ012 | P1 | `0x6238F4` | 11,842 | 32,768 | 2 | 2.767 |
| LZ013 | P1 | `0x62B5F4` | 18,732 | 32,768 | 2 | 1.749 |
| LZ014 | P1 | `0x663EAC` | 15,721 | 32,768 | 2 | 2.084 |
| LZ015 | P1 | `0x679420` | 17,323 | 32,768 | 2 | 1.892 |
| LZ016 | P1 | `0x67D7CC` | 12,509 | 32,768 | 2 | 2.620 |
| LZ017 | P1 | `0x72F2E0` | 17,886 | 32,768 | 2 | 1.832 |
| LZ018 | P1 | `0x56A254` | 9,746 | 32,768 | 1 | 3.362 |
| LZ019 | P1 | `0x56F71C` | 13,613 | 32,768 | 1 | 2.407 |
| LZ020 | P1 | `0x59A1B8` | 14,151 | 32,768 | 1 | 2.316 |
| LZ021 | P1 | `0x59DB08` | 17,005 | 32,768 | 1 | 1.927 |
| LZ022 | P1 | `0x5A44CC` | 16,105 | 32,768 | 1 | 2.035 |
| LZ023 | P1 | `0x5A965C` | 5,939 | 32,768 | 1 | 5.517 |
| LZ024 | P1 | `0x5B113C` | 11,175 | 32,768 | 1 | 2.932 |
| LZ025 | P1 | `0x5B4580` | 9,979 | 32,768 | 1 | 3.284 |
| LZ026 | P1 | `0x5BA254` | 19,475 | 32,768 | 1 | 1.683 |
| LZ027 | P1 | `0x5C4050` | 19,660 | 32,768 | 1 | 1.667 |
| LZ028 | P1 | `0x5C9B4C` | 28,010 | 32,768 | 1 | 1.170 |
| LZ029 | P1 | `0x5D4E6C` | 26,463 | 32,768 | 1 | 1.238 |
| LZ030 | P1 | `0x5E49E4` | 16,427 | 32,768 | 1 | 1.995 |
| LZ031 | P1 | `0x5EAC18` | 13,141 | 32,768 | 1 | 2.494 |
| LZ032 | P1 | `0x5F7190` | 14,786 | 32,768 | 1 | 2.216 |
| LZ033 | P1 | `0x5FAB54` | 13,187 | 32,768 | 1 | 2.485 |
| LZ034 | P1 | `0x60093C` | 19,271 | 32,768 | 1 | 1.700 |
| LZ035 | P1 | `0x6150E8` | 13,753 | 32,768 | 1 | 2.383 |
| LZ036 | P1 | `0x61B89C` | 24,332 | 32,768 | 1 | 1.347 |
| LZ037 | P1 | `0x626738` | 20,155 | 32,768 | 1 | 1.626 |
| LZ038 | P1 | `0x66B524` | 14,065 | 32,768 | 1 | 2.330 |
| LZ039 | P1 | `0x73422C` | 22,601 | 32,768 | 1 | 1.450 |
| LZ040 | P1 | `0x74EB50` | 19,087 | 32,768 | 1 | 1.717 |

## Criterio y próximos pasos

1. **Prioridad 1:** inspeccionar LZ001–LZ040 con visualización 4bpp y 8bpp, y explorar paletas BGR555 candidatas. No cambiar la ROM todavía.
2. Buscar en código las referencias fuente listadas por el catálogo y determinar qué rutina carga cada bloque.
3. Contrastar las cargas con mGBA para asociar recursos a una pantalla, sala, enemigo, efecto o cinemática.
4. Solo después de confirmar el recurso, documentar offset, tamaño, paleta/formato, consumidores y límite seguro de edición.
5. Crear un reemplazo de prueba aislado en una copia de trabajo y comprobar el arranque y la escena en mGBA.

## Límites de interpretación

El catálogo usa el prefijo LZ77 de BIOS GBA (0x10), comprueba que el flujo pueda decodificarse hasta la longitud declarada y cruza cada inicio con palabras que parecen punteros alineados a 4 bytes, normalizando el bit Thumb. Una coincidencia LZ77 o un valor con forma de puntero puede ser accidental. Los IDs son estables solo para el mismo hash de ROM y los mismos parámetros de análisis.
