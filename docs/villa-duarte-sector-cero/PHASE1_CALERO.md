# Fase 1 — paleta nocturna de Calero

**Script:** [scripts/phase1_calero.py](../../scripts/phase1_calero.py)  
**Pruebas:** [tests/test_phase1_calero.py](../../tests/test_phase1_calero.py)

## Objetivo

Crear una candidata de ROM cambiando una sola fila de 16 colores (32 bytes) para el estilo nocturno urbano dominicano de Calero. La entrada se conserva sin escribir sobre ella; se genera otra ROM con su informe JSON.

## Entrada esperada y guardas

El script espera `roms/fusion.gba`, correspondiente a la build visual v0.9 documentada, SHA-256:

    54f3291e54fdca088d440ef2dd51f41dc2c80b17c195956f633660ab790e3b00

También exige el tamaño de 8 MiB, código de juego `AMTE`, título de cabecera `METROID4USA` y checksum de cabecera correcto. Si el SHA no coincide, aborta; no debe usarse la ROM original o una versión distinta como sustituto silencioso.

La tabla de paleta del tileset 61 empieza en el offset de archivo `0x46B494` (dirección de cartucho `0x0846B494`) y contiene 14 filas de 16 colores. En la ROM v0.9 verificada, la fila 0 (`0x46B494`–`0x46B4B3`) está completamente a cero; no la modificamos. El mapa del tileset 61 usa el banco de paleta 1 para sus tiles visibles, por lo que la fase sustituye la fila/banco 1 en `0x46B4B4`–`0x46B4D3` (dirección de cartucho `0x0846B4B4`). La verificación visual de que esta fila es la correcta para el checkpoint escogido sigue pendiente de ejecución en mGBA.

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

En los tiles GBA 4bpp, el índice de píxel 0 es transparente. Esto no significa que toda la fila/banco 0 de la tabla sea un canal alfa; esa fila de paleta contiene 16 entradas, y aquí se conserva intacta porque está vacía en la base. La fase no cambia metatiles, tilemap, composición de capas, colisiones, código, punteros ni sprites.

El reporte registra SHA-256 de entrada y salida, la paleta anterior/nueva, los bytes modificados, los rangos exactos de cambio y la validez del checksum de cabecera. Un informe correcto prueba la modificación binaria prevista, no certifica que la escena se vea bien dentro del juego.
