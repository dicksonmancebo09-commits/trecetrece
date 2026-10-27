# Notas técnicas: ROM de referencia

Estas notas registran lo que se observó en el análisis local previo. No incluyen la ROM ni datos binarios extraídos.

## Identificación informada

- Juego: Metroid Fusion.
- Edición objetivo: USA/Australia, código de juego GBA **AMTE**, tamaño 8 MiB (8.388.608 bytes).
- SHA-256 del archivo original usado en las comprobaciones anteriores: **a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8**.
- Suma de comprobación de cabecera GBA reportada: **0x98**.
- Referencia externa para códigos y mapa de ROM: https://datacrystal.tcrf.net/wiki/Metroid_Fusion
- La suma de comprobación de cabecera no es, por sí sola, una prueba suficiente de que el archivo sea una copia íntegra o de la región correcta.

## Prototipo visual anterior: alcance limitado

La prueba v1.0 modificó únicamente la sala 0 de AREA_MAIN_DECK como ejercicio de integración de gráficos urbanos. Las notas del proceso indicaban:

- Tileset identificado como conjunto 96.
- Mapa de sala de 34 × 14 bloques.
- Gráficos comprimidos y paleta personalizada de prueba.
- Mapas BG1 y BG2 reemplazados en esa sala.
- Colisiones, enemigos y puertas no fueron deliberadamente rediseñados en esa prueba.

No considerar esos detalles una especificación definitiva: deben contrastarse otra vez con la ROM base y con la versión concreta del editor antes de continuar.

## Validaciones realizadas previamente

El informe previo comunicó comprobaciones estáticas del tamaño de archivo, identificador de juego, checksum de cabecera, descompresión de gráficos, dimensiones de los mapas y rangos de punteros. No se confirmó el comportamiento en ejecución.

## Limitaciones y decisiones

- La prueba afecta a una única sala; no es una conversión de todo el juego.
- No existe una prueba de juego confirmada desde MAGE o un emulador.
- Las ROMs y los parches binarios deben permanecer fuera de este repositorio público.
- Antes de nuevas modificaciones, documentar cada recurso, guardar una copia de referencia fuera del repo, inspeccionar el destino exacto y definir una prueba verificable.
- No asumir que cambiar gráficos de una ROM es el camino definitivo para el producto final. La arquitectura objetivo debe decidirse antes de realizar más trabajo.
