# Puerta de integración GBA — primera sala de prueba

**Proyecto:** LATINO AMÉRICA Zector Cero  
**Fecha:** 2 de noviembre de 2026  
**Estado:** preparada como protocolo; no ejecutada sobre ROM en esta sesión.

## Objetivo

Integrar una única sala representativa como prueba vertical antes de aplicar cambios al resto del juego. La prueba debe demostrar que arte, tilemap, recursos, puertas y colisiones trabajan juntos en la ROM real.

## Bloqueos previos

- La ROM exacta debe estar disponible localmente en `private-roms/` (no se sube al repositorio).
- Su tamaño, cabecera y SHA-256 deben coincidir con el perfil seleccionado o con un perfil explícitamente revisado.
- La extracción por sala debe determinar dimensiones de mapa, BG maps, clipdata, sprites, eventos y punteros reales.
- La sala elegida debe tener un recurso privado disponible o una estrategia de asignación nueva sin sobrescribir otros consumidores.

## Procedimiento

### A. Inventario de ROM

1. Ejecutar `tools/gba_rom_audit.py` con `--rom`, `--profile` y `--config config/gba_lab.json`.
2. Guardar el informe y confirmar que el SHA-256 observado corresponde al perfil esperado.
3. Si hay una ROM de referencia limpia, pasarla mediante `--baseline` para obtener delta y comprobar rangos protegidos.
4. No usar `--ignore-profile-sha` como atajo para aceptar una base desconocida.

### B. Selección de sala y extracción

1. Seleccionar la primera sala del flujo de apertura tras verificar su ID e índice de origen en la ROM exacta.
2. Extraer el tamaño real, mapas de BG, clipdata, puertas, sprites, eventos, tileset entry y recursos de paleta/fondo.
3. Generar lista de todos los consumidores del tileset, gráficos y paleta; calcular el espacio realmente reservado.
4. Marcar las posiciones de puertas y zonas de colisión en una ficha técnica revisada por la ROM.

### C. Exportación de gráficos

El exportador `tools/png_to_gba_4bpp.py` acepta un **PNG indexado**, no un SVG. El atlas objetivo debe rasterizarse sin antialias, cuantizarse deliberadamente a un máximo de 16 entradas y validar el índice transparente para el layer BG u OBJ.

Ejemplo tras generar un PNG indexado y revisar su paleta:

```bash
python3 tools/png_to_gba_4bpp.py private-roms/exports/opening-room-indexed.png \
  --output-dir private-roms/assets/opening-room \
  --prefix opening-room
```

El script valida round-trip 4bpp y LZ77. Eso prueba la conversión de gráficos, no la composición de una sala ni su funcionamiento en el juego.

### D. Patching privado y pruebas

1. Preparar un manifiesto privado de parche con hash exacto de ROM base, bytes previos esperados, longitudes iguales y escrituras no solapadas.
2. Aplicar el parche solo a una copia nueva; nunca sobrescribir la ROM original.
3. Ejecutar `tools/run_gba_diagnostic.sh` con la ROM y perfil apropiados.
4. Revisar capturas y logs manualmente. El proceso debe mostrar entrada y salida correctas, suelo/plataformas fiables, puerta conectada, objetos visibles, paleta correcta y guardado intacto.
5. Repetir una secuencia de navegación definida para confirmar que no existe softlock ni crash.

## Condiciones de aceptación

- [ ] Hash y cabecera de ROM base verificados.
- [ ] Datos extraídos de la ROM exacta, no inferidos de la ROM de referencia.
- [ ] Grafo de puertas y destinos de eventos revisados para esta sala.
- [ ] Gráficos indexados/exportados y round-trip documentado.
- [ ] Tilemap y colisiones de esta sala revisados conjuntamente.
- [ ] Recursos compartidos y rangos libres auditados.
- [ ] Parche aplicado sobre una copia con precondiciones verificadas.
- [ ] Capturas y logs de mGBA revisados; arranque, movimiento, puertas y guardado aprobados.

**No avanzar a una integración masiva de 382 salas antes de pasar esta puerta.**
## Datos de referencia ya automatizados

El extractor [extract_reference_room_metadata.py](../../tools/extract_reference_room_metadata.py) puede completar dimensiones por capa y recuentos de spritesets desde el código fuente fijado, sin copiar ROM ni mapas RLE al repositorio. Esta información ayuda a seleccionar una sala de prueba, pero no sustituye la extracción de los mapas BG/clipdata desde la ROM privada. La puerta de integración A–D sigue siendo obligatoria.
