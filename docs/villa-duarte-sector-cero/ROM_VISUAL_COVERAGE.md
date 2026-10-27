# Matriz de cobertura visual — ROM completa

**Objetivo:** transformar visualmente toda la ROM de Metroid Fusion de forma trazable.  
**Estado actual:** auditoría inicial; no declarar cubierto lo que no se ha inventariado.

## Línea base confirmada en el entorno de trabajo

La sonda de metadatos se ejecutó de forma real el 27-10-2026 sobre el archivo local:

- Archivo: `/mnt/data/Metroid Fusion (USA, Australia).gba`
- Tamaño: 8.388.608 bytes (8 MiB)
- Código GBA: `AMTE`
- Título de cabecera leído: `METROID4USA.`
- Checksum de cabecera esperado/observado: `0x98` / `0x98`, válido
- SHA-256: `a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8`
- Primera palabra little-endian: `0xEA00002E`, decodificada como salto ARM de `0x08000000` a `0x080000C0` (offset de archivo `0xC0`).
- Esto confirma algunos campos de cabecera, no la autenticidad total, la validez de todos los datos ni que una ROM transformada funcione en juego.

## Prototipos locales previos observados

Los archivos siguientes existen en el entorno de trabajo, no se añaden al repositorio público:

| Archivo | SHA-256 | Alcance conocido |
|---|---|---|
| `Villa_Duarte_Sector_Cero_v0.8.gba` | `de4217c5df5e7b7d57d9bb43555a2f4ee3b62bf873b65817e768340911569850` | Prototipo previo; cambios concretos por auditar. |
| `Villa_Duarte_Sector_Cero_v0.9_VISUAL.gba` | `54f3291e54fdca088d440ef2dd51f41dc2c80b17c195956f633660ab790e3b00` | Prototipo visual previo; requiere auditoría de diferencias y punteros antes de reutilizar cambios. |
| `Villa_Duarte_Sector_Cero_v1.0_URBAN_OPENING.gba` | `8b5e2a57bc45fbef9de3d258a50af21f7aa06a6248227b097072ece3374fe5f5` | Prueba de sala inicial; no representa una transformación visual de toda la ROM y no se confirmó prueba en juego. |

No se debe usar estos hashes como afirmación de calidad, compatibilidad ni validez visual. Son identificadores para evitar confundir archivos.

## Matriz por categoría

Estado permitido: **Sin auditar**, **Inventariado**, **Diseño aprobado**, **Modificado**, **Comprobado estáticamente**, **Probado en juego**.

| Categoría | Cobertura actual | Trabajo requerido | Estado |
|---|---|---|---|
| ROM base, cabecera, hashes | Identificación inicial | Congelar hash base y comparar variantes | Inventariado parcialmente |
| Arranque y código principal | No auditado de forma integral | No cambiar código si basta con recursos; identificar dependencias cuando proceda | Sin auditar |
| Todos los tilesets | Solo un tileset de una prueba conocida | Enumerar IDs, dimensiones, compresión, paletas y reutilización | Sin auditar |
| Todas las paletas | Solo una paleta parcial conocida en prototipo | Auditar usuarios por paleta y límites de color | Sin auditar |
| Todos los mapas y salas | Solo sala inicial de prueba conocida | Enumerar áreas, salas, capas BG, conexiones y dependencias | Sin auditar |
| Fondos/escenarios | Prueba urbana de sala inicial | Diseño global con variaciones por zona y continuidad | Sin auditar |
| Jugador y animaciones | Sin auditoría global confirmada | Inventariar estados, frames, hitboxes y paletas | Sin auditar |
| Enemigos y variantes | Sin auditoría global confirmada | Inventariar familias, animaciones, estados y apariciones por sala | Sin auditar |
| Jefes | Sin auditoría global confirmada | Inventariar fases, sprites, efectos y estados | Sin auditar |
| Proyectiles y efectos | Sin auditoría global confirmada | Inventariar y clasificar por paleta/animación | Sin auditar |
| Objetos, puertas y elevadores | Sin auditoría global confirmada | Inventario por ID y aparición en mapa | Sin auditar |
| HUD, iconos y pantallas | Sin auditoría global confirmada | Inventariar y definir estilo/legibilidad | Sin auditar |
| Audio/música | Existe investigación v0.8 separada | No modificar en etapa visual salvo necesidad explícita | Pendiente de decisión |
| Upscale 4K de recursos | Plan documentado; lote completo no generado | Exportar con fuente y metadatos, no deformar proporciones | Sin auditar |
| Layout móvil horizontal | Solo plan | Crear simulación editable y probar proporciones | Sin auditar |
| Layout móvil vertical | Solo plan | Crear composición alternativa y comprobar safe areas | Sin auditar |
| Compatibilidad de ROM final | Sin prueba integral confirmada | Comprobar en emulador y/o hardware cuando sea viable | Sin auditar |

## Registro por cada lote o categoría

| Fecha | ID de recurso/sala | Categoría | Versión de entrada | Cambios realizados | Archivo de salida/hash | Verificación | Reversión |
|---|---|---|---|---|---|---|---|
| 2026-10-27 | MAIN_DECK room 0 / Urban Opening v1.0 | Integridad ROM/IPS | ROM base SHA `a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8` | Aplicado IPS archivado; 7.892 registros y 59.501 bytes distintos | Salida SHA `8b5e2a57bc45fbef9de3d258a50af21f7aa06a6248227b097072ece3374fe5f5` | Comprobado estáticamente: coincide byte por byte con el prototipo archivado; no se ejecutó en emulador | Conservar base original y reaplicar el IPS solo sobre una copia |

## Criterio para declarar la transformación completa

La ROM solo podrá describirse como visualmente transformada de extremo a extremo cuando:
1. todas las categorías aplicables estén inventariadas;
2. todos los tilesets, mapas/salas, sprites, paletas, animaciones y UI relevantes tengan un estado explícito;
3. no queden recursos omitidos por suposiciones;
4. se revisen referencias, compresión y colisiones tras cada lote;
5. la salida final pase comprobaciones estructurales y se pruebe en un emulador;
6. se informe por separado qué se probó y qué no.

Una matriz sin completar no es un defecto: sirve para que el progreso sea medible y para evitar volver a afirmar que una única sala equivale al juego completo.

## Candidata v1.1 QA Viewer — 2026-10-27

Se generó una ROM privada con una pantalla de revisión previa al juego para inspeccionar dos conceptos originales (Entrada al Barrio y Callejones del Caliche) a 240 × 160. El parche BPS se reaplicó sobre v1.0 y la salida coincidió byte por byte; la cabecera conserva checksum 0x98. **Pendiente de prueba en emulador.** Esta herramienta no cuenta como reemplazo de tilesets/mapas del juego ni como integración de la traducción completa. Detalles y hashes en [QA_VIEWER_V1_1.md](QA_VIEWER_V1_1.md).

## 2026-10-27 — v1.2: título real, sin visor de arranque

El nuevo build sustituye los recursos reales de la pantalla de título (fondo gráfico, paleta, tilemap, gráficos del logo y objetos de menú) dentro de sus bloques ROM; no añade código de arranque. La cabecera cambia a `LATINO ZCERO`. LZ77, límites de recursos, checksum y BPS pasan validaciones estáticas; no hay prueba en emulador. El reskin anterior de la sala 0 se conserva, aunque su apariencia aún no se certifica como prueba en juego. Los demás niveles, sprites y UI siguen pendientes. Ver [REAL_TITLE_RESKIN_V1_2.md](REAL_TITLE_RESKIN_V1_2.md).

## v1.3 — Main Deck sala 0 conectada a escena urbana

Se reescriben la tabla de metatiles y mapas BG1/BG2 privados a los que apuntan los datos de sala para que usen la composición urbana de Villa Duarte. Se conserva clipdata y código de arranque; título real ya sustituido en v1.2. La salida se reconstruye desde los recursos de la ROM y no constituye captura de juego. Emulador pendiente. Los demás escenarios, sprites y UI continúan sin completar. Ver [ROOM0_RESKIN_V1_3.md](ROOM0_RESKIN_V1_3.md).

## Auditoría de v1.3 — build retirada

Tras el reporte del usuario, v1.3 no es una build funcional. Fallo confirmado del título: bancos de paleta del tilemap inconsistentes con la dirección de carga de la paleta. Formatos/rangos estáticos de tabla y mapas se verificaron, pero la ejecución no. La causa del crash sigue desconocida. Las referencias de tabla/mapas privados sí están conectadas, así que la hipótesis de punteros ausentes queda rectificada. Ver [POSTMORTEM_V1_3.md](POSTMORTEM_V1_3.md).
