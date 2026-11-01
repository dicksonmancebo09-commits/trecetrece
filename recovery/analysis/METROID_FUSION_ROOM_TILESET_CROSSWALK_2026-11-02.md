# Cruce de sala → tileset → recursos gráficos (Metroid Fusion GBA)

**Fecha de extracción:** 2 de noviembre de 2026  
**Fuente:** rama main del proyecto comunitario [metroidret/mf](https://github.com/metroidret/mf), concretamente src/room.c, src/data/rooms_data.c, include/structs/room.h e include/data/rooms_data.h.

## Resultado comprobado

La referencia contiene **382 entradas de sala**: Main Deck 87, Sector 1 54, Sector 2 61, Sector 3 39, Sector 4 48, Sector 5 52 y Sector 6 41. Se extrajeron todas las entradas y se comprobó que no faltara ningún índice de sala. La columna tileset_entry es el índice que guarda cada RoomEntryRom.tileset; no es el nombre del archivo de gráficos.

La ruta del código es:

1. sAreaRoomEntryPointers[gCurrentArea][gCurrentRoom] selecciona la entrada de la sala.
2. RoomLoadEntry() copia entry.tileset a gCurrentRoomEntry.tilesetNumber.
3. RoomLoadTileset() usa ese índice para consultar sTilesetEntries[].
4. Esa segunda tabla decide por separado el recurso de gráficos de tiles, paleta, gráficos de fondo, tilemap y animaciones.

Por tanto, **el número de tileset de una sala no identifica por sí solo un barrio ni un conjunto único de píxeles**. Es una clave hacia otra tabla.

## La diferencia de numeraciones que estaba causando la confusión

Hay tres nombres distintos:

- **Índice de entrada:** por ejemplo tileset_entry = 19 en una sala.
- **Índice de sTilesetEntries[]:** es el mismo índice de entrada; resuelve los recursos reales.
- **Nombre del recurso:** por ejemplo sTileset_19_Gfx o sTileset_19_Pal. Es el número que aparece en nombres de archivo bajo data/tilesets/; no tiene por qué coincidir con el índice de entrada.

### Si “tileset 19” significa la entrada de sala 19

sTilesetEntries[19] usa:

| Recurso | ID |
|---|---:|
| Gráficos de tiles | sTileset_18_Gfx |
| Paleta | sTileset_18_Pal |
| Gráficos de fondo | sTileset_12_Bg_Gfx |
| Tilemap | sTileset_18_Tilemap |
| Tiles animados / paleta animada | 0 / 0 |

En esta referencia, la entrada 19 aparece en **Main Deck, salas 38 y 84** (coordenadas de mapa 21,6 y 25,6).

### Si “tilesets/19” significa el recurso gráfico sTileset_19_Gfx

Ese recurso lo comparten las entradas **20–25**. Cada una usa un recurso de paleta distinto (19–24), pero el mismo gráfico de tiles 19, el fondo 13 y el tilemap 19. Se usa en las salas iniciales:

| Área | Sala | Entrada | Paleta |
|---|---:|---:|---:|
| Sector 1 | 0 | 20 | 19 |
| Sector 2 | 0 | 21 | 20 |
| Sector 3 | 0 | 22 | 21 |
| Sector 4 | 0 | 23 | 22 |
| Sector 5 | 0 | 24 | 23 |
| Sector 6 | 0 | 25 | 24 |

**Conclusión:** reemplazar sTileset_19_Gfx afecta a esas seis salas iniciales. Cambiar solamente sTileset_19_Pal afecta a la entrada 20, no a las otras cinco variantes de paleta. No debe editarse ese recurso como si perteneciera a una sola sala.

## Corrección del parche de paleta “Calero”

El informe de la fase 1 identifica la escritura de 32 bytes en 0x46B4B4 como la fila 1 de sTileset_61_Pal. En la tabla de recursos, esta paleta está compartida por las entradas 69 y 70:

| Entrada | Gráficos | Paleta | Fondo | Tilemap | Animación |
|---:|---:|---:|---:|---:|---:|
| 69 | 50 | 61 | 42 | 50 | 0 |
| 70 | 50 | 61 | 43 | 50 | 5 |

Y las dos entradas aparecen en estas salas del Main Deck:

| Área / sala | Entrada | Coordenadas mapa | Datos visuales que declara el código |
|---|---:|---:|---|
| Main Deck, sala 71 | 69 | (8,9) | BG_PROP_DIM_ROOM, sBg0_QuarantineBaySpotlight |
| Main Deck, sala 46 | 70 | (9,10) | sBg0_Snowflakes, efecto EFFECT_SNOWFLAKES_COLD |

Por eso, el cambio de paleta a sTileset_61_Pal **no es exclusivo de una sola sala “Calero”**: afecta a las dos salas que usan las entradas 69 y 70. En particular, la sala 46 está descrita en el código con nieve y efecto de frío; la sala 71 es una sala oscurecida con foco de la bahía de cuarentena. No son etiquetas semánticas de barrio: son los datos que realmente declara la referencia.

Para aislar el tinte en una única sala, hay que separar la paleta que comparten las entradas 69/70: crear una copia de paleta propia y hacer que sólo la entrada escogida apunte a ella, o crear una entrada de tileset derivada. Modificar la paleta compartida no sirve para diferenciar las dos salas. Antes de escribir la nueva referencia/puntero hay que localizar su tabla binaria exacta y verificar espacio seguro; este documento no afirma que ese puntero ya se haya parcheado.

## Índices de tileset por sala

Formato: índice de sala: índice de entrada en sTilesetEntries[]. Estos números permiten cruzar cada sala con la tabla de recursos.

### Main Deck (87 salas): 1:16, 2:16, 3:11, 4:11, 5:11, 6:30, 7:8, 8:13, 9:10, 10:28, 11:12, 12:28, 13:26, 14:27, 15:60, 16:10, 17:84, 18:18, 19:29, 20:18, 21:18, 22:27, 23:50, 24:79, 25:35, 26:37, 27:39, 28:17, 29:36, 30:38, 31:27, 32:10, 33:12, 34:17, 35:27, 36:27, 37:12, 38:19, 39:15, 40:29, 41:8, 42:8, 43:17, 44:12, 45:27, 46:70, 47:27, 48:56, 49:54, 50:56, 51:56, 52:56, 53:56, 54:56, 55:54, 56:10, 57:18, 58:12, 59:55, 60:6, 61:6, 62:66, 63:97, 64:12, 65:66, 66:10, 67:17, 68:55, 69:61, 70:18, 71:69, 72:18, 73:27, 74:63, 75:6, 76:6, 77:84, 78:80, 79:85, 80:83, 81:13, 82:89, 83:56, 84:19, 85:26, 86:7, 87:96

### Sector 1 (54 salas): 1:12, 2:10, 3:11, 4:41, 5:41, 6:30, 7:41, 8:30, 9:41, 10:46, 11:13, 12:41, 13:41, 14:11, 15:41, 16:30, 17:14, 18:88, 19:12, 20:14, 21:88, 22:88, 23:88, 24:12, 25:88, 26:88, 27:4, 28:88, 29:88, 30:88, 31:35, 32:41, 33:30, 34:12, 35:30, 36:88, 37:46, 38:41, 39:41, 40:87, 41:73, 42:12, 43:41, 44:41, 45:41, 46:41, 47:41, 48:94, 49:94, 50:30, 51:88, 52:88, 53:2, 54:20

### Sector 2 (61 salas): 1:12, 2:10, 3:31, 4:31, 5:32, 6:31, 7:31, 8:15, 9:31, 10:32, 11:67, 12:67, 13:31, 14:31, 15:32, 16:12, 17:64, 18:65, 19:32, 20:58, 21:32, 22:59, 23:31, 24:58, 25:32, 26:45, 27:31, 28:11, 29:74, 30:31, 31:31, 32:58, 33:31, 34:95, 35:95, 36:95, 37:13, 38:12, 39:67, 40:12, 41:72, 42:32, 43:30, 44:31, 45:72, 46:31, 47:67, 48:13, 49:12, 50:67, 51:92, 52:94, 53:94, 54:31, 55:9, 56:58, 57:58, 58:95, 59:72, 60:95, 61:21

### Sector 3 (39 salas): 1:12, 2:10, 3:33, 4:45, 5:33, 6:34, 7:34, 8:33, 9:34, 10:40, 11:42, 12:42, 13:42, 14:40, 15:42, 16:42, 17:82, 18:34, 19:42, 20:75, 21:15, 22:34, 23:34, 24:34, 25:51, 26:13, 27:42, 28:40, 29:71, 30:33, 31:13, 32:12, 33:11, 34:40, 35:42, 36:34, 37:94, 38:94, 39:22

### Sector 4 (48 salas): 1:12, 2:10, 3:30, 4:15, 5:11, 6:47, 7:43, 8:43, 9:43, 10:91, 11:12, 12:52, 13:43, 14:52, 15:52, 16:52, 17:52, 18:52, 19:52, 20:47, 21:47, 22:12, 23:47, 24:52, 25:52, 26:45, 27:76, 28:43, 29:13, 30:47, 31:90, 32:12, 33:86, 34:52, 35:43, 36:47, 37:47, 38:52, 39:12, 40:52, 41:52, 42:81, 43:94, 44:94, 45:47, 46:47, 47:12, 48:23

### Sector 5 (52 salas): 1:12, 2:10, 3:48, 4:48, 5:15, 6:48, 7:49, 8:49, 9:49, 10:45, 11:49, 12:11, 13:49, 14:49, 15:48, 16:15, 17:48, 18:48, 19:48, 20:57, 21:49, 22:49, 23:48, 24:67, 25:77, 26:49, 27:48, 28:48, 29:12, 30:48, 31:94, 32:13, 33:48, 34:48, 35:48, 36:48, 37:94, 38:12, 39:48, 40:48, 41:48, 42:49, 43:68, 44:49, 45:48, 46:67, 47:48, 48:13, 49:12, 50:67, 51:49, 52:24

### Sector 6 (41 salas): 1:12, 2:10, 3:44, 4:44, 5:44, 6:44, 7:44, 8:44, 9:62, 10:44, 11:12, 12:62, 13:62, 14:44, 15:62, 16:93, 17:78, 18:62, 19:62, 20:62, 21:12, 22:3, 23:12, 24:11, 25:15, 26:72, 27:72, 28:72, 29:13, 30:62, 31:62, 32:30, 33:62, 34:67, 35:12, 36:94, 37:94, 38:67, 39:67, 40:11, 41:25

## Frecuencia global de entradas

2=1 · 3=1 · 4=1 · 6=4 · 7=1 · 8=3 · 9=1 · 10=11 · 11=11 · 12=33 · 13=11 · 14=2 · 15=7 · 16=2 · 17=4 · 18=6 · 19=2 · 20=1 · 21=1 · 22=1 · 23=1 · 24=1 · 25=1 · 26=2 · 27=8 · 28=2 · 29=2 · 30=10 · 31=15 · 32=7 · 33=4 · 34=8 · 35=2 · 36=1 · 37=1 · 38=1 · 39=1 · 40=4 · 41=15 · 42=8 · 43=6 · 44=8 · 45=4 · 46=2 · 47=9 · 48=20 · 49=12 · 50=1 · 51=1 · 52=13 · 54=2 · 55=2 · 56=7 · 57=1 · 58=5 · 59=1 · 60=1 · 61=1 · 62=10 · 63=1 · 64=1 · 65=1 · 66=2 · 67=11 · 68=1 · 69=1 · 70=1 · 71=1 · 72=6 · 73=1 · 74=1 · 75=1 · 76=1 · 77=1 · 78=1 · 79=1 · 80=1 · 81=1 · 82=1 · 83=1 · 84=2 · 85=1 · 86=1 · 87=1 · 88=12 · 89=1 · 90=1 · 91=1 · 92=1 · 93=1 · 94=12 · 95=5 · 96=1 · 97=1

## Archivos de datos

- [CSV completo de 382 salas y recursos derivados](metroid_fusion_room_tilesets_2026-11-02.csv)
- [Selector de sala y carga de tileset](https://github.com/metroidret/mf/blob/main/src/room.c)
- [Tablas de salas y recursos sTilesetEntries](https://github.com/metroidret/mf/blob/main/src/data/rooms_data.c)
- [Estructura RoomEntryRom](https://github.com/metroidret/mf/blob/main/include/structs/room.h)
- [Declaraciones de las tablas por área](https://github.com/metroidret/mf/blob/main/include/data/rooms_data.h)

## Límite de interpretación

El código identifica **área, índice de sala, índice de tileset y recursos cargados**, pero no traduce automáticamente una sala a “Calero”, “Villa Duarte” o a un nombre de barrio. Para eso hace falta decidir qué sala original se está sustituyendo y revisar su composición visual. La asignación “Main Deck → Calero” usada por la fase 1 sigue siendo una decisión del proyecto, no un nombre que exista en el juego original.
