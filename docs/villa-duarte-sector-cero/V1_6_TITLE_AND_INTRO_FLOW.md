# v1.6 — limpieza del título y salto a la entrada del hangar

**Fecha:** 27 de octubre de 2026  
**ROM privada:** `LATINO_AMERICA_Zector_Cero_v1.6_TITLE_AND_INTRO_FLOW.gba`  
**Base de parche:** v1.5 Actual Render Fix.

## Cambios

1. **Omite la intro de arranque “Nintendo Presents / Metroid Fusion”.** La función `IntroHandler` devuelve TRUE inmediatamente; el flujo principal pasa al título personalizado.
2. **Elimina los objetos de copyright y PRESS START** que se dibujaban sobre el fondo personalizado y aparecían como fragmentos repetidos. Se desactivan las dos llamadas a `TitleScreenSetupObject`; el input START sigue funcionando.
3. **Salta la narración y las escenas iniciales al crear una partida nueva.** Después de `NewFileIntroInit`, el estado global pasa de 1 a 11 (`NewFileIntroLandingOnBsl`), dejando fuera los estados 1–10 y entrando directamente en la secuencia de llegada/entrada de la nave al hangar BSL. El estado interno de escena se inicializa a cero por el inicializador.

## Parches exactos

| Offset ROM | Cambio |
|---|---|
| `0x87610` | `30 B5 00 25` → `01 20 70 47` (return TRUE) |
| `0x86A4A` | llamada de copyright → dos NOP Thumb |
| `0x86A54` | llamada de PRESS START → dos NOP Thumb |
| `0x8777E` | `MOVS r0,#1` → `MOVS r0,#11` |

Solo 13 bytes cambian realmente, contando que un byte del último halfword permanece igual.

## Validación binaria

- Tamaño: 8.388.608 bytes.
- Checksum de cabecera GBA válido: `0x6D`.
- Cada offset se valida contra sus bytes anteriores antes de escribir.
- No se alteran otras posiciones.
- BPS aplicado a la v1.5 da exactamente la salida v1.6 byte por byte.
- Hashes de ROM/parche en el paquete privado `SHA256SUMS.txt`.

## Límites de validación

**No se ha ejecutado esta ROM en mGBA en esta sesión.** Se verificó el patch binario y el flujo de control de las funciones decompiladas, pero hace falta probar en el emulador:

- Arranque: debe entrar directamente al título personalizado sin el splash.
- Título: no debe aparecer el texto original de copyright ni PRESS START; la tecla START sigue funcionando.
- En una partida nueva sin `introPlayed`, debe saltar la narración y entrar en la escena de la nave/hangar.

Las partidas que ya tienen el flag `introPlayed=true` pueden omitir la introducción completa por lógica original del juego, así que se recomienda probar con una partida nueva.

ROM y parche excluidos del repositorio público; no subir binarios comerciales ni parches derivados.
