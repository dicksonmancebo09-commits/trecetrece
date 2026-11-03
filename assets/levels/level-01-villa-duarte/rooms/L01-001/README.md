# L01-001 — Hangar de cuarentena 01

Primera pasada de producción visual. Sala fuente `L01_R082`, Main Deck índice 82 (1-based), 19×14 bloques (304×224 px). ROM limpia fijada por SHA-256 `a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8`.

Se decodificaron BG0, BG1, BG2 y clipdata originales (266 celdas por capa, sin errores). Se creó un borrador de tilemap urbano de 38×28 tiles de 8×8 px usando el atlas L01 v0.2: hormigón, ventanas enrejadas, compuerta central, accesos laterales, paneles y zanja de servicio.

`clipdata.csv` se conserva como referencia original; no se declara adaptado. El tilemap requiere resolver la asignación real de tileset/base de tile/banco de paleta/VRAM antes de convertirlo al formato de BG de la ROM. ROM sin modificar, punteros intactos y sin prueba runtime. Este es un artefacto visual de producción, no una sala jugable.

Paquete completo y preview se entregan en esta conversación.