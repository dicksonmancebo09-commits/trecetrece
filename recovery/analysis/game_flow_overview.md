# Flujo principal reconstruido — resumen técnico

Este mapa combina el despachador observado en la ROM con los nombres y transiciones contrastados en la referencia de código `metroidret/mf`. No es una descompilación función por función.

## Cada frame

1. Limpia la marca de trabajo por frame.
2. Actualiza audio.
3. Comprueba solicitud de reinicio.
4. Lee entradas y ejecuta comprobaciones de reset.
5. Incrementa contadores de frames.
6. Lee el modo principal en RAM (`0x03000BDE`) y despacha mediante la tabla observada desde el offset ROM `0x278`.
7. Espera la solicitud de VBlank.

## Estados principales

| ID | Estado | Transición conocida de alto nivel |
|---:|---|---|
| 0 | Título | Idioma, intro/título, selector o demo |
| 1 | Juego | Gameplay; mapa/pausa, escena, SA-X, final o muerte |
| 2 | Reinicio suave | Ejecuta reset |
| 3 | Mapa/pausa | Vuelve al juego o entra en escena |
| 4 | Escena/cutscene | Juego, mapa, game over o depuración |
| 5 | Primer plano de SA-X | Regresa al gameplay |
| 6 | Menú para borrar SRAM | Reinicia o regresa al título |
| 7 | Selector/intro de nueva partida | Juego, intro o título |
| 8 | Game over | Reanuda si hay partida guardada o reinicia |
| 9 | Final | Pasa a créditos |
| 10 | Muerte por colisión con SR388 | Pasa a game over |
| 11 | Créditos | Pasa a reinicio suave |
| 12 | Demo | Usa el manejador de gameplay y termina/regenera demo |
| 13 | Desconocido | Rutina aún no descrita completamente |
| 14 | Depuración | El despachador no realiza acción en este caso |

## Evidencia y límites

- El punto de entrada del archivo es un salto ARM desde `0x08000000` hacia `0x080000C0`.
- La inicialización configura pilas/modos, el slot de interrupción y una llamada BX a `0x08000231`, que entra en Thumb en `0x08000230`.
- El despachador lee `0x03000BDE`, limita valores a 14 y usa la tabla en el offset `0x278`; sus 15 entradas se representan en `src/reconstructed/game_mode_dispatch.c`.
- El inventario heurístico previo detectó candidatos LZ77 y cadenas ASCII, pero incluye falsos positivos/solapamientos. No debe utilizarse como catálogo definitivo de recursos.
- No se afirma que REA haya sido ejecutado desde esta conversación. La ejecución real se realiza en el Codespace con el script de este directorio.
