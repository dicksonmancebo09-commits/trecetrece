# Herramienta LZ77 para GBA: inspección, extracción y compresión

**Script:** [tools/lz77_tool.py](../../tools/lz77_tool.py)  
**Pruebas:** [tests/test_lz77_tool.py](../../tests/test_lz77_tool.py)

Esta herramienta trabaja con el formato BIOS LZ77 de GBA de tipo 0x10. No necesita dependencias externas.

## Capacidades

- **scan:** busca streams candidatos en una ROM y produce un informe JSON con offsets, tamaño declarado, bytes consumidos y hash del contenido descomprimido.
- **extract:** descomprime un bloque desde un offset de archivo conocido y guarda los bytes en un archivo independiente.
- **compress:** comprime un archivo independiente y verifica la ida y vuelta mediante el decodificador incluido.
- Impone por defecto un límite de salida de 4 MiB para evitar asignaciones de memoria desproporcionadas.
- No altera la ROM ni instala automáticamente recursos.

Los resultados del escaneo son **candidatos heurísticos**, no una identificación concluyente de gráficos. Algunos bytes aleatorios pueden formar un stream válido. Verifica los offsets mediante punteros/tablas y abre el contenido extraído en la herramienta adecuada antes de usarlo.

## Comandos de ejemplo

### Escanear una ROM (solo lectura)

    python3 tools/lz77_tool.py scan "private-roms/Castlevania-Aria-of-Sorrow.gba" --report /tmp/castlevania-lz77-candidates.json

Por defecto se comprueban offsets alineados a 4 bytes, con tamaño descomprimido de 32 bytes a 4 MiB. Para escanear cada byte, con mayor coste y más falsos positivos:

    python3 tools/lz77_tool.py scan "private-roms/Castlevania-Aria-of-Sorrow.gba" --alignment 1 --report /tmp/castlevania-lz77-candidates-all.json

### Extraer un bloque tras confirmar el offset

    python3 tools/lz77_tool.py extract "private-roms/Castlevania-Aria-of-Sorrow.gba" --offset 0x123456 --output /tmp/candidate.bin

0x123456 es un ejemplo, no una dirección comprobada. Para convertir una dirección ROM 0x08xxxxxx en offset de archivo, resta 0x08000000.

### Comprimir un recurso editado en un archivo nuevo

    python3 tools/lz77_tool.py compress /tmp/candidate-edited.bin --output /tmp/candidate-edited.lz

Esto solo crea un stream comprimido aparte. No lo inserta en la ROM, no actualiza punteros y no acredita que el juego pueda cargarlo.

## Generar una vista previa de tiles 4bpp

Después de extraer un bloque a un archivo independiente, se puede generar un atlas en escala de grises para comprobar su estructura:

    python3 tools/gba_4bpp_preview.py /tmp/candidate.bin --skip-bytes 4 --columns 16 --scale 3 --output /tmp/candidate-preview.png

Usa `--skip-bytes 4` solo cuando hayas verificado que el bloque tiene una cabecera de cuatro bytes. El escaneo heurístico de Castlevania detectó muchos bloques cuyo tamaño menos cuatro bytes es múltiplo de 32; eso es una pista para probar este desplazamiento, no una garantía de que todos los bloques tengan ese formato.

El visor interpreta el resto como tiles GBA 4bpp secuenciales de 8×8 píxeles (32 bytes por tile). La imagen usa una paleta de grises basada en el índice 0–15; no reproduce la paleta de colores real del juego. Una imagen legible apoya la hipótesis de que el contenido son tiles, pero no demuestra que el bloque esté bien identificado por punteros o tablas.

## Validación

Desde la raíz del proyecto:

    python3 -m unittest discover -s tests -v
    python3 -m py_compile tools/lz77_tool.py

Las pruebas usan fixtures sintéticos; no requieren ROMs comerciales. Incluyen una comprobación cruzada: el output del compresor nuevo también debe decodificarse con gba_lz77_decompress de tools/gba_rom_audit.py. Las pruebas estáticas no sustituyen a la validación en mGBA o en un editor específico del juego.

## Separación de archivos privados

Guarda ROMs, saves y parches en private-roms/ (o en una ubicación privada fuera del repositorio). Los recursos extraídos y los informes pueden ir a /tmp/ durante la investigación. No añadas ROMs comerciales ni parches derivados al control de versiones.
