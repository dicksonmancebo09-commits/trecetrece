# Fase 1 — paleta nocturna de Calero

**Script:** [scripts/phase1_calero.py](../../scripts/phase1_calero.py)  
**Pruebas:** [tests/test_phase1_calero.py](../../tests/test_phase1_calero.py)

## Objetivo

Crear una candidata de ROM cambiando una sola fila de 16 colores (32 bytes) para el estilo nocturno urbano dominicano de Calero. La entrada se conserva sin escribir sobre ella; se genera otra ROM con su informe JSON.

## Entrada esperada y guardas

El script espera `roms/fusion.gba`, correspondiente a la build visual v0.9 documentada, SHA-256:

    54f3291e54fdca088d440ef2dd51f41dc2c80b17c195956f633660ab790e3b00

También exige el tamaño de 8 MiB, código de juego `AMTE`, título de cabecera `METROID4USA.` y checksum de cabecera correcto. Si el SHA no coincide, aborta; no debe usarse la ROM original o una versión distinta como sustituto silencioso.

La paleta de Main Deck/paleta 76 se documenta en el estudio de sala 0 en el offset de archivo `0x46B494` (dirección de cartucho `0x0846B494`). La fase sustituye solo ese bloque de 32 bytes. El offset se ha documentado en el estudio previo de Main Deck sala 0; la verificación visual de que la misma paleta está activa en el checkpoint exacto de la build v0.9 sigue siendo una comprobación de ejecución pendiente.

## Ejecutar

Desde la raíz del proyecto, primero valida el archivo y genera un informe sin escribir la ROM de salida:

    python3 scripts/phase1_calero.py --base roms/fusion.gba --dry-run

Después de revisar el informe y confirmar que el SHA y el offset son correctos, construye la candidata:

    python3 scripts/phase1_calero.py --base roms/fusion.gba

Salidas previstas:

- `build/sector_cero_fase1.gba`
- `build/fase1_report.json`

Si ya existen salidas de una ejecución anterior, el programa se detiene. `--force` permite reemplazarlas explícitamente.

Para validar de forma reproducible en pruebas sintéticas:

    python3 -m unittest discover -s tests -p "test_phase1_calero.py" -v

## Límite visual importante

Los siete primeros colores vienen del fragmento de paleta recibido. Las entradas 7–15 se completaron como una propuesta inicial de Calero nocturno porque el fragmento compartido terminaba en la entrada 6; deben revisarse en el atlas y en mGBA antes de aprobarse como paleta final.

En un fondo GBA, el índice de paleta 0 es un valor de color, no un canal alfa. Se conserva como negro base y no debe tratarse como transparente. La transparencia de un píxel depende del tipo de capa/recurso; esta fase no cambia metatiles, tilemap, composición de capas, colisiones, código, punteros ni sprites.

El reporte registra SHA-256 de entrada y salida, la paleta anterior/nueva, los bytes modificados, los rangos exactos de cambio y la validez del checksum de cabecera. Un informe correcto prueba la modificación binaria prevista, no certifica que la escena se vea bien dentro del juego.
