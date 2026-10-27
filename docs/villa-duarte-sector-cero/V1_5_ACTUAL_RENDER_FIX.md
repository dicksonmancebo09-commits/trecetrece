# v1.5 — Corrección real de la corrupción visual

**Fecha:** 27 de octubre de 2026  
**Build privada:** `LATINO_AMERICA_Zector_Cero_v1.5_ACTUAL_RENDER_FIX.gba`  
**Estado:** validación binaria y reconstrucción de recursos; ejecución de CPU en mGBA pendiente.

## Diagnóstico confirmado a partir de los bytes y las capturas de v1.4

### 1. Desbordamiento del gráfico de título

El recurso de gráficos del fondo original tiene un hueco asignado de 3.320 bytes (0x605D08–0x606A00). La gráfica urbana insertada ocupaba 12.808 bytes comprimidos, por lo que se desbordaba y sobrescribía el blob siguiente, además de los recursos de paleta y mapa. El mapa comprimido también medía 1.473 bytes, pero su hueco original era de 688 bytes.

**Corrección:** se restauró desde la ROM base el tramo afectado `0x605D08–0x609F10`, se colocaron el fondo, la paleta y el mapa en espacio libre `0x7C4000`, `0x7C1000` y `0x7C0000`, respectivamente, y se actualizaron las referencias literales usadas por la rutina del título. Los datos de la intro que se habían pisado se restauran.

### 2. Transparencia incorrecta en la sala 0

El BG2 de la calle usaba el índice de color 0 para colores visibles del arte. En los tiles 4bpp de GBA, el índice 0 es transparente, de modo que se veían capas de fondo que debían quedar ocultas por el arte urbano.

**Corrección:** los 13 colores de la sala se desplazaron de índices 0–12 a índices 1–13 y se ajustó la paleta. El índice 0 queda reservado para transparencia. Además, el metatile 383 de BG1 ahora señala un tile nuevo de 32 bytes completamente vacío; el tile hardware usado es 560, después del tile-base de 192.

### 3. Verificaciones

- LZ77 round-trip del fondo y mapa del título.
- El segmento ROM afectado coincide byte por byte con la ROM base limpia.
- Las referencias del código apuntan a las ubicaciones reubicadas.
- GFX de sala, tabla de metatiles y paleta son compatibles con los nuevos índices.
- Checksum de cabecera GBA válido.
- Parche BPS desde v1.4 aplicado y verificado byte por byte.
- ZIP de entrega validado.

**No se afirma que la ROM esté probada en mGBA.** Las imágenes de la carpeta de diagnóstico son reconstrucciones de recursos y no capturas de emulador. La prueba en mGBA aún debe comprobar título, START, carga de sala, movimiento y transiciones.

Los binarios de ROM y parches se mantienen fuera del repositorio público.