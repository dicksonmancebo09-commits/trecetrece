# Registro de fuentes y verificación

**Revisión realizada:** 27 de octubre de 2026.  
**Propósito:** centralizar los repositorios, herramientas y referencias del proyecto Villa Duarte — Sector Cero. Este archivo distingue fuentes consultadas de validaciones pendientes.

## Herramientas y análisis de Metroid Fusion

| Fuente | URL | Qué aporta | Estado / precaución |
|---|---|---|---|
| MAGE Themes | https://github.com/ConConner/MAGE-Themes | Editor para Metroid Fusion y Zero Mission; mapas, gráficos, datos de salas y herramientas de edición. | README consultado el 27-10-2026: requiere .NET Runtime 10+ y declara compatibilidad con ROMs norteamericanas (U). Confirmar que la ROM base y la versión de la herramienta coincidan. |
| MAGE Themes, fork | https://github.com/raygunpewpewpew/MAGE-Themes | Variante publicada del editor. | Confirmar si este fork está vigente y qué cambios aporta antes de elegirlo como herramienta principal. |
| Metroid Fusion decompilation | https://github.com/metroidret/mf | Código y datos de una descompilación en progreso; referencias técnicas sobre estructuras internas. | El README actual advierte que la descompilación no es “shiftable” y que no debe utilizarse como base para modificar una ROM. GitHub muestra licencia MIT; revisar el archivo LICENSE y atribuciones antes de reutilizar código. |
| OpenMFOR | https://git.inabaudonge.reisen/OpenMFOR/OpenMFOR | Análisis del juego, aleatorización, lógica y utilidades para ROMs. | El proyecto indica compatibilidad USA/Australia. No se ha ejecutado ni auditado para este proyecto. |
| MFOR original | https://github.com/Kazuto88/MFOR | Randomizer original, validación de ROM base y lógica de juego. | GitHub muestra GPL-3.0. No copiar código al producto propio sin revisión de licencia. |
| MARS Patcher | https://github.com/MetroidAdvRandomizerSystem/mars-patcher-py | Biblioteca de parcheado utilizada en herramientas de randomización de Metroid Advance. | PyPI/GitHub muestra GPLv3 y desarrollo Alpha; es opcional, no un requisito confirmado del proyecto. |
| Data Crystal: Metroid Fusion | https://datacrystal.tcrf.net/wiki/Metroid_Fusion | Compilación de datos de ROM, versiones y referencias técnicas. | Fuente comunitaria; corroborar datos con la ROM exacta y fuentes primarias. |

## Recursos de arte con licencia abierta

| Fuente | URL | Qué aporta | Estado / precaución |
|---|---|---|---|
| Tiddybub/2d-assets | https://github.com/Tiddybub/2d-assets | Índice de packs 2D, incluido el grupo modern-urban y el pack pico-8-city. | El README declara CC0 para los packs incluidos y un SOURCE.md por pack. Revisar la procedencia del archivo que realmente se vaya a usar. |
| Kenney — Pico-8 City | https://kenney.nl/assets/pico-8-city | Tiles y objetos pixel-art para entornos urbanos. | Página de Kenney consultada el 27-10-2026: CC0. No es arte dominicano por sí mismo; requiere dirección de arte propia para el estilo del proyecto. |
| Kenney — licencia/FAQ | https://kenney.nl/support | Explicación del autor sobre sus recursos CC0. | La licencia debe confirmarse en cada pack descargado y en el archivo de licencia que acompaña al contenido. |

## Referencias visuales comerciales — solo como estudio de diseño

| Juego | Referencia | Uso de estudio previsto |
|---|---|---|
| Castlevania: Aria of Sorrow | https://www.konami.com/games/castlevania/us/en-us/page/history_2003_gba | Atmósfera, contraste, espacios por capas y legibilidad visual. |
| Spider-Man: Mysterio's Menace | https://www.nintendo.com/es-es/Juegos/Game-Boy-Advance/Spiderman-Mysterio-s-Menace-267310.html | Ritmo de plataformas laterales, movilidad y lectura de espacios urbanos. |
| X-Men: Reign of Apocalypse | Sin página oficial verificada en esta revisión. | Referencia visual mencionada en conversaciones anteriores; los detalles específicos quedan pendientes de una fuente fiable. |

Estas referencias no autorizan copiar sprites, fondos, animaciones, música, mapas ni código de los juegos comerciales. Se utilizan para describir principios generales de diseño.

## Registro del prototipo

- ROM de referencia informada: Metroid Fusion USA/Australia, código GBA AMTE, 8 MiB.
- El prototipo visual previo cambió una sala inicial; no todo el juego.
- Se reportaron validaciones estáticas, no una prueba de ejecución confirmada en MAGE o emulador.
- Los binarios de ROM y los parches derivados no se suben a este repositorio público.
- El siguiente método de trabajo queda pendiente de definición; no se autoriza por defecto modificar otras salas.

## Comprobaciones pendientes

1. Localizar el elemento llamado **REA**: no figura en el árbol público de la rama main inspeccionada el 27-10-2026.
2. Determinar si REA está en una carpeta local, un Codespace, otra rama o en otro repositorio.
3. Elegir la herramienta y versión de MAGE después de comprobar la región/base de ROM.
4. Verificar en ejecución cualquier cambio técnico antes de declararlo correcto.
5. Mantener un inventario por archivo de assets: procedencia, licencia, fecha, edición y uso previsto.
