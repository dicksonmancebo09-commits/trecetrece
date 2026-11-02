# LATINO AMÉRICA Zector Cero — auditoría estática de ROM v1.7

**Fecha:** 2 de noviembre de 2026  
**Modo:** solo lectura. No se modificó ninguna de las ROM originales.

## Resultado

**75/75 comprobaciones estáticas superadas.**

La ROM base y la candidata v1.7 coinciden exactamente con los SHA-256 fijados en `config/gba_lab.json`. La cabecera GBA de v1.7 es coherente, los bytes esperados de la corrección título/hangar están presentes, los 18 punteros declarados apuntan a sus destinos esperados y los recursos gráficos declarados se descomprimen correctamente.

**Esto no es una validación de ejecución.** No se pudo iniciar mGBA ni VBA-M en este entorno; la CPU del GBA no se ejecutó.

## Archivos auditados

| Archivo | Tamaño | SHA-256 | Resultado |
|---|---:|---|---|
| `Metroid Fusion (USA, Australia).gba` | 8.388.608 bytes | `a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8` | Coincide con la ROM base fijada |
| `LATINO_AMERICA_Zector_Cero_v1.7_TITLE_HANGAR_FIX.gba` | 8.388.608 bytes | `66e68fb0f04f89d40ecfee21996e6be62e96a22f7f66198528ee6b2c5c2c2aaf` | Coincide con el perfil v1.7 fijado |

Cabecera v1.7: título `LATINO ZCERO`, game code `LZC0`, checksum complementario calculado y almacenado `0x6D`.

## Comprobaciones superadas

| Área | Resultado |
|---|---:|
| Hashes fijados de ROM base y v1.7 | 2/2 |
| Tamaño y campos de cabecera | 4/4 |
| Bytes esperados de título/intro/hangar | 7/7 |
| Punteros esperados del perfil | 18/18 |
| Tramo protegido de recursos originales `0x605D08–0x60920F` | Coincide byte a byte con la ROM base |
| Recursos comprimidos/raw y longitudes declaradas | 4/4 |
| Tabla de metatiles de Main Deck, sala 0 | Correcta: 384 registros × 4 subtiles |
| Transparencia del metatile 383 y tile 560 | Correcta: tile gráfico de 32 bytes en cero |
| Mapas BG1 y BG2 de Main Deck, sala 0 | Decodifican a 34 × 14 bloques |
| Reservas de los 7 bloques auditados | Dentro de ROM y sin solapamientos |
| **Total** | **75/75** |

### Recursos verificados

| Recurso | Offset | Bytes comprimidos/raw | Bytes descomprimidos |
|---|---:|---:|---:|
| Tileset Main Deck sala 0 | `0x416E8C` | 2.843 | 11.808 |
| Tilemap de título | `0x7C0000` | 1.468 | 2.048 |
| Paleta de título | `0x7C1000` | 256 | 256 |
| Gráficos de título | `0x7C4000` | 12.325 | 20.480 |

BG1 decodifica a 476 entradas, todas con ID 383 (metatile transparente). BG2 decodifica a 476 entradas, con 305 valores únicos, IDs de 0 a 304. Las longitudes de los streams coinciden con las declaradas en el perfil.

## Diferencia binaria base → v1.7

La comparación byte a byte encontró **81.362 bytes distintos**, aproximadamente el **0,96991 %** del archivo. Se agrupan en 102 tramos al unir diferencias separadas por hasta ocho bytes, repartidos en 16 bloques de 64 KiB.

Este delta mide diferencias entre versiones; **no identifica por sí solo qué cambios representan salas nuevas** ni demuestra que 382 mapas hayan sido instalados.

## Qué queda validado y qué no

**Validado estáticamente:** la identidad de ambas ROM, la integridad de cabecera, las correcciones esperadas de título/intro, los destinos de punteros declarados, los recursos de título y la implementación estructural auditada de Main Deck sala 0.

**No validado:** la ejecución del arranque, la pantalla de título en un emulador, el salto real a la secuencia del hangar, las colisiones y puertas en ejecución, el guardado dentro del juego o el comportamiento en hardware real.

**No demostrado por esta v1.7:** la integración de las **382 salas**. El perfil técnico que se ha podido comprobar declara estructuras de mapa/metatiles para una sola sala personalizada —Main Deck, sala 0— además de los recursos del título. El registro maestro de 382 IDs sigue siendo un plan/registro de producción y no equivale a 382 habitaciones jugables dentro de la ROM.

## Archivo .sav

El archivo `.sav` aportado mide 32 KiB y contiene las cadenas `MetroidAGB-EUVerE004`, `MetroidEpisode4A`, `SAVE_END` y `ENDDATA_SEL_SAVE`. Es un archivo de guardado separado, no una ROM. La etiqueta `EUVerE004` aconseja no asumir compatibilidad con la ROM base USA/Australia sin comprobarla; no se utilizó para validar la ROM.

## Próxima secuencia técnica

1. Ejecutar v1.7 en mGBA o VBA-M desde una copia de trabajo y registrar vídeo/capturas/logs del título, START y transición al hangar.
2. Auditar la estructura de salas y recursos originales de la ROM completa, no solo la ficha de Main Deck sala 0.
3. Para cada sala del registro, obtener mapas BG/clipdata reales, colisiones, puertas, enemigos y eventos; resolver consumidores de recursos compartidos.
4. Integrar una sala vertical completa y probarla antes de escalar a los cinco lotes y las 382 salas.

El JSON de auditoría local conserva las 75 comprobaciones, hashes de recursos, diferencias binarias y límites de alcance. Las ROM y los saves no se subieron al repositorio.
