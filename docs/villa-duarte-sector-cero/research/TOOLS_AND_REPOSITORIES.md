# Herramientas y repositorios de referencia

Documento de investigación: herramientas para inspeccionar el juego de referencia, fuentes de datos técnicos y bibliotecas de recursos. Los proyectos enlazados son externos e independientes.

## Herramientas para estudiar la ROM

### MAGE Themes — editor de Metroid para GBA
- Repositorio: https://github.com/ConConner/MAGE-Themes
- Otra versión publicada: https://github.com/raygunpewpewpew/MAGE-Themes
- MAGE (Metroid Advance Game Editor) se creó para editar Metroid Fusion y Metroid Zero Mission. MAGE Themes es una evolución/fork con cambios y funciones adicionales.
- La documentación del proyecto indica compatibilidad con las versiones norteamericanas (U) de los juegos; confirmar requisitos y compatibilidad de la versión concreta antes de usarla.
- MAGE es una aplicación de escritorio, no un conector de ChatGPT ni una terminal remota de GitHub.
- Uso previsto aquí: inspeccionar salas, mapas, gráficos, paletas, enemigos y colisiones antes de planificar cambios. No asumir que toda ROM o versión modificada es compatible.

### Metroid Fusion Decompilation
- Repositorio: https://github.com/metroidret/mf
- Proyecto de descompilación en progreso. Su README advierte que la descompilación no es “shiftable” y que no debe usarse como base directa para trabajar en una ROM modificada.
- Uso recomendado: fuente de aprendizaje y referencia técnica, respetando su licencia, notas de construcción y estado de desarrollo. No copiar código al proyecto propio sin comprobar licencia y procedencia.

### Open Metroid Fusion Open Randomizer (OpenMFOR)
- Repositorio: https://git.inabaudonge.reisen/OpenMFOR/OpenMFOR
- Proyecto comunitario centrado en aleatorización y análisis de Metroid Fusion.
- Uso previsto: referencia secundaria para comprender herramientas de análisis y parches; no es el motor del juego nuevo ni una fuente de assets.

### Metroid Fusion — Data Crystal
- Referencia: https://datacrystal.tcrf.net/wiki/Metroid_Fusion
- Resume identificación de versiones, códigos de región, información de ROM y enlaces a utilidades. Verificar los datos contra la copia concreta que se esté analizando.

## Fuentes de assets con licencia abierta

### Tiddybub/2d-assets
- Repositorio: https://github.com/Tiddybub/2d-assets
- Biblioteca curada de packs de arte 2D. El repositorio declara que sus packs son CC0 y conserva referencias de origen.
- Antes de incorporar un archivo, revisar la carpeta del pack y su SOURCE.md; registrar el nombre exacto del archivo y la procedencia en nuestro propio inventario.

### Kenney — Pico-8 City
- Página del autor: https://kenney.nl/assets/pico-8-city
- Página del pack: https://kenney-assets.itch.io/pico-8-city
- El pack se publica bajo CC0 1.0 Universal según la página de Kenney. Incluye tiles y objetos urbanos pensados para paisajes de ciudad.
- Estos recursos pueden servir como bloque inicial de estudio, pero conviene adaptarlos y combinarlos con arte original para construir una identidad dominicana diferenciada.

## Referencias visuales de juegos comerciales

- Castlevania: Aria of Sorrow — referencia de atmósfera, contraste, lectura de siluetas y composición de espacios.
- Spider-Man: Mysterio's Menace — referencia de ritmo visual urbano y plataformas laterales.
- X-Men: Reign of Apocalypse — referencia de legibilidad de combate, variedad de enemigos y ritmo de encuentros.

Son referencias de dirección artística y diseño, no fuentes para copiar sprites, animaciones, música, mapas ni otros elementos propietarios.

## Reglas de uso

- No incluir ROMs comerciales ni ROMs modificadas en este repositorio.
- No subir parches IPS/BPS/UPS ni archivos que contengan datos extraídos de la ROM.
- No asumir que “gratuito” o “sin fines de lucro” elimina los derechos de terceros.
- Mantener por cada asset: archivo, autor/fuente, URL, licencia, fecha de consulta y modificaciones realizadas.
- Priorizar arte, música, fuentes y código propios o con licencias claramente compatibles.
