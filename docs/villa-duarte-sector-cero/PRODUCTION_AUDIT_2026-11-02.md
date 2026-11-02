# Auditoría de producción — 2 de noviembre de 2026

**Proyecto:** LATINO AMÉRICA Zector Cero  
**Rama auditada:** `agent/rea-editable-analysis`  
**Alcance:** registro de salas, manifiesto de lotes, metadatos técnicos, atlas de barrio y preparación de integración GBA.

## Resultado ejecutivo

| Área | Resultado | Alcance real |
|---|---|---|
| Identificadores | **382/382 verificados** | IDs del plan maestro cotejados con el registro JSON; sin duplicados ni huérfanos |
| Distribución | **7/7 niveles coherentes** | Conteos por barrio y cobertura de índices fuente completos |
| Puertas de referencia | **898 registros** | 0 destinos predeterminados y 0 variantes de evento sin sala destino |
| Cinco lotes | **382/382 asignados** | 87 + 87 + 87 + 87 + 34, sin solapamiento ni huecos |
| Fichas técnicas | **382/382 enriquecidas con referencia** | Dimensiones de clipdata/BG, longitudes declaradas, variantes de spriteset y puertas; los mapas RLE y la verificación de ROM exacta siguen pendientes |
| Atlas | **7 bibliotecas SVG** | 2 paquetes anteriores + 5 atlas nuevos; 320 módulos nuevos; colores contrastados contra las 7 paletas declaradas; PNG indexado/4bpp aún sin resultado CI verificado |
| Integración ROM | **No iniciada en binario** | Falta acceso a la ROM privada exacta y completar extracción técnica por sala |
| Pruebas en emulador | **Pendientes** | No se ejecutó una ROM durante esta auditoría |

## 1. Verificación de las 382 salas

El registro `data/world/sector-cero-room-registry-v1.json` contiene 382 entradas con 382 `room_id` distintos. El listado de salas de `LEVEL_ROOM_MASTER_PLAN_V2.md` devuelve los mismos 382 identificadores únicos: no hay diferencias entre ambos conjuntos.

| Nivel | Barrio | Esperadas | Encontradas | Resultado |
|---|---|---:|---:|---|
| L01 | Villa Duarte | 87 | 87 | Correcto |
| L02 | El Caliche | 54 | 54 | Correcto |
| L03 | La Francia Nueva | 61 | 61 | Correcto |
| L04 | Calero | 39 | 39 | Correcto |
| L05 | Pueblo Nuevo | 48 | 48 | Correcto |
| L06 | Los Molinos | 52 | 52 | Correcto |
| L07 | Simónico | 41 | 41 | Correcto |
| **Total** | | **382** | **382** | **Correcto** |

También se comprobaron los índices fuente: no hay duplicados de combinación área/índice y cada registro cumple `room_index_1based = room_index_0based + 1`. La cobertura de índices por área es continua desde 1 hasta su conteo declarado.

## 2. Puertas y salas huérfanas

El registro contiene **898 registros de puerta**. Se verificaron tanto los destinos predeterminados como los destinos alternativos asociados a eventos:

- Destinos predeterminados que apuntan a un ID inexistente: **0**.
- Variantes de evento que apuntan a un ID inexistente: **0**.
- Salas duplicadas en el registro maestro: **0**.
- Salas fuera de los cinco lotes: **0**.

**Límite importante:** este control valida referencias internas del grafo extraído de la fuente de referencia. No demuestra que esa topología coincida byte por byte con la ROM privada del proyecto, ni que las rutas creativas entre barrios estén ya adaptadas.

## 3. Normalización de los cinco lotes

Se consolidó la asignación en `data/world/sector-cero-production-manifest-v1.json`. Los cinco registros JSON de lote permiten comprobar el vínculo entre ID de producción e ID maestro.

| Lote | Salas | Acumulado |
|---|---:|---:|
| 1 | 87 | 87 |
| 2 | 87 | 174 |
| 3 | 87 | 261 |
| 4 | 87 | 348 |
| 5 | 34 | 382 |

Correcciones aplicadas durante la auditoría:

- Se creó el registro JSON del lote 1, que no estaba presente con esa ruta.
- Se creó el JSON del lote 4 y se añadieron a su documento los 87 IDs maestros que faltaban en la tabla.
- Se creó el JSON del lote 5; sus 34 IDs coinciden con las 34 salas restantes de Simónico.
- Los lotes 2 y 3 se contrastaron con el registro maestro; sus 87 IDs por lote coinciden con el reparto esperado.
- Se comprobó la cobertura conjunta: 382 asignaciones y 382 IDs únicos.

## 4. Fichas técnicas por sala

Se creó `data/world/sector-cero-room-technical-sheets-v1.json` con **382 fichas técnicas enriquecidas con metadatos de referencia**, una por sala. Cada entrada incorpora:

- ID maestro, ID de producción, lote, barrio, rol y briefing.
- Área fuente, índice de sala, coordenadas y metadatos de sala.
- Índice de entrada de tileset y referencias de gráficos, paleta, fondo, tilemap y animaciones.
- Puertas y destinos de referencia.
- Conteo de salas consumidoras por recurso compartido.
- Dimensiones en bloques y píxeles (bloque fuente de 16 px), longitudes declaradas de capas clipdata/BG, variantes y recuentos de spritesets, hashes de los archivos fuente y campos pendientes para mapas BG, clipdata, enemigos, eventos, puertas adaptadas y offsets de punteros.

**No se deben confundir las fichas enriquecidas con fichas de integración completas.** Ya hay dimensiones y declaraciones de capas de la referencia para las 382 salas; lo que sigue pendiente es el contenido comprimido de los mapas BG/clipdata, la distribución espacial de colisiones, coordenadas individuales de sprites, eventos y ubicaciones de punteros, todo cotejado contra la ROM exacta.

## 5. Atlas gráficos

Se generaron cinco bibliotecas SVG originales, cada una de 256 × 256 px, con 64 módulos de 32 × 32 px sobre cuadrícula lógica de 8 × 8 px: **320 módulos nuevos en total**.

| Nivel | Atlas | Estado |
|---|---|---|
| L01 Villa Duarte | [SVG v0.2](../../assets/levels/level-01-villa-duarte/level-01-villa-duarte-atlas-v0.2.svg) · [JSON](../../assets/levels/level-01-villa-duarte/level-01-villa-duarte-atlas-v0.2.json) | SVG editable existente; PNG indexado/4bpp pendiente |
| L02 El Caliche | [Paquete de atlas y preview](../../assets/tiles/scenario-02/README.md) | SVG y exportaciones PNG descritas en el paquete; importación y prueba ROM pendientes |
| L03 La Francia Nueva | [SVG v0.1](../../assets/levels/level-03-la-francia-nueva/level-03-atlas-v0.1.svg) · [JSON](../../assets/levels/level-03-la-francia-nueva/level-03-atlas-v0.1.json) | Creado en esta auditoría |
| L04 Calero | [SVG v0.1](../../assets/levels/level-04-calero/level-04-atlas-v0.1.svg) · [JSON](../../assets/levels/level-04-calero/level-04-atlas-v0.1.json) | Creado en esta auditoría |
| L05 Pueblo Nuevo | [SVG v0.1](../../assets/levels/level-05-pueblo-nuevo/level-05-atlas-v0.1.svg) · [JSON](../../assets/levels/level-05-pueblo-nuevo/level-05-atlas-v0.1.json) | Creado en esta auditoría |
| L06 Los Molinos | [SVG v0.1](../../assets/levels/level-06-los-molinos/level-06-atlas-v0.1.svg) · [JSON](../../assets/levels/level-06-los-molinos/level-06-atlas-v0.1.json) | Creado en esta auditoría |
| L07 Simónico | [SVG v0.1](../../assets/levels/level-07-simonico/level-07-atlas-v0.1.svg) · [JSON](../../assets/levels/level-07-simonico/level-07-atlas-v0.1.json) | Creado en esta auditoría |

Los cinco SVG nuevos son **primeras bibliotecas de módulos**, no arte final aprobado, mapas de sala ni tilemaps. Se inspeccionaron los siete SVG: los colores de relleno/trazo presentes coinciden con las 16 entradas declaradas de cada paleta. Esa comprobación es estática; aún no hay PNG indexados ni archivos 4bpp/BGR555/LZ77 confirmados como artefactos de ejecución.

## 6. Automatización de la auditoría

Se añadieron:

- `tools/audit_sector_cero_rooms.py`: valida IDs, distribución, índices fuente, destinos de puertas, cobertura de lotes y cobertura de fichas.
- `tests/test_audit_sector_cero_rooms.py`: pruebas para datos coherentes, duplicados, destinos rotos y IDs ausentes.
- Integración del control en `.github/workflows/gba-diagnostic-toolchain.yml`.

**Estado de CI:** el workflow está configurado para ejecutar el control al cambiar estos archivos. No se dispone aquí de un resultado de ejecución de GitHub Actions; hasta que el job aparezca como exitoso, los tests automatizados deben considerarse pendientes de ejecución. La validación estructural informada arriba se realizó leyendo y comparando los datos del repositorio.

## 7. Integración GBA y pruebas

No se aplicó ningún cambio binario durante esta auditoría. El repositorio mantiene las ROM, los saves y los manifiestos binarios derivados dentro de `private-roms/`, excluidos de Git. En este turno no hay acceso al archivo ROM privado ni a su Codespace, por lo que no sería correcto inventar un hash observado, afirmar que se ha parcheado el juego o declarar una prueba mGBA satisfactoria.

La versión v1.3 figura retirada como candidata funcional tras el informe anterior de pantalla ilegible y bloqueo. No debe utilizarse como build aprobada sin reproducir y corregir el fallo.

### Secuencia de integración segura

1. Obtener en el entorno privado la ROM base exacta y ejecutar la auditoría de solo lectura con el perfil correspondiente de `config/gba_lab.json`. Confirmar el SHA-256 observado frente al perfil; no omitir la comprobación para “hacer pasar” el análisis.
2. Extraer dimensiones, BG maps, clipdata, sets de sprites, eventos y punteros del room objetivo. Verificar si cada recurso es compartido y qué otras salas lo consumen.
3. Indexar los SVG a PNG de 16 entradas con transparencia validada para BG u OBJ según el destino. El exportador `tools/png_to_gba_4bpp.py` requiere PNG indexado; no convierte SVG de forma directa.
4. Exportar los gráficos a 4bpp, BGR555 y LZ77 dentro de `private-roms/`; conservar los informes de round-trip.
5. Componer un único room tilemap de prueba y crear una copia nueva de la ROM. Usar `tools/apply_guarded_patch.py` con hash de base, bytes previos esperados y rangos reservados no solapados.
6. Ejecutar el diagnóstico mGBA y revisar las capturas, logs y navegación real: arranque, puerta de entrada/salida, colisiones, transparencia, paleta, sprites y guardado.
7. Solo después de superar esa prueba vertical, ampliar la integración a grupos de salas conectadas. No realizar sustituciones globales de recursos compartidos sin auditar todos sus consumidores.

## 9. Dimensiones de referencia extraídas en las 382 salas

La extracción se completó leyendo directamente los **382 archivos C de sala** en el repositorio de referencia `metroidret/mf`, commit fijado `de76565c897c05838503717db9aa2adfe92aeba3`. El resultado se guarda en [`sector-cero-reference-room-metadata-v1.json`](../../data/world/sector-cero-reference-room-metadata-v1.json) y se incorporó a las 382 fichas técnicas.

| Comprobación de fuente | Resultado |
|---|---:|
| Archivos de sala recuperados y analizados | **382/382** |
| Salas con dimensiones de clipdata declaradas | **382/382** |
| Dimensiones coincidentes entre clipdata y capas BG declaradas | **382/382** |
| Conflictos dimensionales encontrados | **0** |
| Declaraciones de capa clipdata | 382 |
| Declaraciones BG1 | 382 |
| Declaraciones BG2 | 381 |
| Declaraciones BG0 | 69 |
| Declaraciones BG3 en estos archivos | 0 |

**Unidad:** el código de referencia declara dimensiones en bloques de 16 × 16 píxeles. Por tanto, una sala de 34 × 24 bloques declara 544 × 384 píxeles. Esto es dimensión de mapa, no resolución de pantalla; la pantalla objetivo sigue siendo 240 × 160.

### Distribución de variantes de spriteset

| Variante | Salas que la declaran | Posiciones declaradas en total |
|---:|---:|---:|
| 0 | 382 | 1.593 |
| 1 | 70 | 443 |
| 2 | 17 | 114 |
| 3 | 0 | 0 |
| **Total de filas de posición** | — | **2.150** |

Estos son recuentos de filas de colocación en los archivos fuente. No significan que se hayan importado los sprites ni que se haya probado su aparición en el juego.

### Límite sobre colisiones y tilemaps

El código C contiene dimensiones y referencias a recursos comprimidos, pero los binarios `.rle` de clipdata/BG no estaban disponibles en el árbol público consultado. La extracción no inventa ni reconstruye una matriz de colisión. Tampoco valida estos metadatos contra la ROM privada del usuario: para eso se necesita el archivo local, comprobar su SHA-256 y extraer sus mapas/punteros reales.

## Criterio de cierre de esta auditoría

La **auditoría estructural de referencia** está completada: 382 IDs coherentes, 5 lotes completos, 898 puertas sin destinos huérfanos, dimensiones y declaraciones de capas recuperadas para 382 salas y 382 fichas técnicas enriquecidas. La **producción gráfica** tiene 7 bibliotecas SVG; la conversión PNG/4bpp está automatizada pero todavía sin ejecución CI confirmada. La **integración y validación dentro de la ROM privada** sigue abierta; no se declara que el videojuego contenga ya las 382 salas.
## 8. Automatización y extracción técnica ampliada

Después del inventario inicial se añadieron dos etapas automatizadas:

- `tools/extract_reference_room_metadata.py` consulta los archivos fuente de las 382 salas en el commit fijado `de76565c897c05838503717db9aa2adfe92aeba3`. Extrae dimensiones de clipdata y BG presentes en las declaraciones C, longitud declarada de sus arrays, hash del archivo de referencia y variantes/recuentos de colocaciones de spritesets. El script actualiza las 382 fichas y genera `sector-cero-reference-room-metadata-v1.json`.
- `tools/render_gba_atlas_indexed.py` rasteriza los siete SVG usando sus paletas declaradas. El workflow `.github/workflows/zector-cero-production-assets.yml` ejecuta además `png_to_gba_4bpp.py`, que comprueba round-trip 4bpp y LZ77, y publica los recursos binarios como artifact de CI.

**Estado de ejecución:** la automatización está incorporada al repositorio; no se presenta como completada hasta que GitHub Actions muestre un job verde y los PNG, JSON de extracción y artifact estén disponibles en la rama.

**Límite de la extracción:** los archivos C de referencia contienen las dimensiones y referencias a los bloques RLE, pero los binarios de clipdata `.rle` no están disponibles en el árbol público consultado. Por ello, la extracción no inventa una matriz de colisión ni guarda bytes de esos mapas. Para completar la disposición espacial de colisiones, sprites y eventos se necesita leer la ROM privada exacta y validar su hash.
