# Auditoría posterior a la v1.3 — build no válida

**Fecha:** 27 de octubre de 2026  
**Estado:** v1.3 retirada como candidata funcional tras el informe del usuario de pantalla de título ilegible y bloqueo/crash.

## Resultado reportado por el usuario

El juego muestra una pantalla inicial que no se entiende y falla al continuar; los escenarios no dan la transformación esperada. La build no debe tratarse como jugable ni como entrega aprobada.

## Fallo visual demostrado: banco de paleta del título

El código original de la pantalla de título copia la paleta de fondo desde el bloque de ROM `0x609120` a `PALRAM_BASE + 0x100`; eso son los bancos BG 8–15. En v1.3, las 1.024 entradas del tilemap en `0x609220` tienen banco de paleta 0. El renderer de reconstrucción previo interpretó la paleta como si empezara en el banco 0; esa imagen no era una representación fiel del resultado real del hardware.

**Corrección requerida:** codificar el banco de paleta adecuado (8–15, con 8 como primer banco de la paleta nueva) en las entradas del mapa y reconstruir la vista desde la asignación real de paleta del GBA.

## Verificación del mapa de la sala 0

Rectificación de una sospecha preliminar: el mapa y la tabla de metatiles sí tienen referencias en la ROM. En la build v1.3:

- `0x3C0014` contiene un puntero a `0x087B0000` (tabla de metatiles).
- `0x3C2C58` contiene un puntero a `0x087B2000` (BG1).
- `0x3C2C5C` contiene un puntero a `0x087B2400` (BG2).

Comprobaciones estáticas repetidas:

- El tileset GFX se descomprime a 11.776 bytes (368 tiles 4bpp).
- La tabla contiene 384 definiciones de metatiles; sus índices de tiles están en el rango 0–367.
- BG1 y BG2 descomprimen 476 entradas cada uno para una sala de 34×14 bloques.
- BG2 usa IDs de metatile 0–304; BG1 usa 383 como metatile transparente, compuesto por el tile 0 vacío.
- Estos resultados validan formato/rangos, **no** el comportamiento durante el juego.

## Causa del crash

No se ha demostrado la causa exacta del crash. No había un emulador GBA instalable/disponible en el entorno usado para esta revisión, así que no se pudo reproducir ni depurar una ejecución. No se debe afirmar que los controles, la entrada a la sala o las transiciones funcionan.

## Puerta para una nueva build

Antes de llamar funcional a otra ROM se debe:

1. Corregir el banco de paleta del título y revisar los otros atributos de mapa.
2. Comparar una variante con cambios de título aislados frente a otra con cambios de sala aislados, para localizar el cuelgue.
3. Ejecutar ambas en mGBA o MAGE, revisar logs, título, START, inicio de partida, carga de sala, movimiento y transición.
4. Solo después publicar una build de prueba con alcance y hashes correctos.

Hasta completar ese proceso, **v1.3 está retirada como build funcional y no debe volver a recomendarse para jugar**. La ROM original y v1.0 siguen siendo referencias de comparación, no versiones certificadas en emulador.
