# v1.2 — Sustitución real de recursos del título

**Proyecto:** LATINO AMÉRICA Zector Cero  
**Fecha:** 27 de octubre de 2026  
**Estado:** recursos y cabecera comprobados estáticamente; prueba de emulador pendiente.  
**Build privada:** el binario ROM y el parche no se suben a este repositorio público.

## Corrección del enfoque

La v1.1 QA Viewer añadía una pantalla de prueba antes del juego y luego intentaba saltar a la entrada de arranque. No convertía el título real. Queda **obsoleta; no debe usarse como versión de prueba actual**.

La v1.2 conserva el arranque original y modifica los recursos que el juego carga para su pantalla de título. No añade un visor de inicio ni un gancho de arranque.

## Recursos reales modificados

| Recurso | Offset de ROM | Cambio |
|---|---:|---|
| Gráficos de objetos del menú/título | 0x590C9C | Se eliminó el arte original de objetos; el título dibujado en el nuevo fondo sustituye los sprites visuales de menú |
| Gráficos del logo de fondo | 0x593274 | El logo anterior se volvió transparente |
| Gráficos del fondo de título | 0x605D08 | Sustituidos por pixel art original de barrio |
| Paleta del fondo | 0x609120 | Nueva paleta de 16 colores en BGR555 |
| Tilemap del fondo | 0x609220 | Mapa de tiles 4bpp para 240 × 160 |
| Título de cabecera GBA | 0xA0 | `LATINO ZCERO`; código `LZC0`; checksum recalculado |

Los recursos se reemplazan dentro de sus asignaciones existentes y los flujos LZ77 se verifican después de escribirlos. El código de arranque se conserva.

## Escenario jugable inicial

La build anterior v1.0 ya contiene un intento de sustitución del tileset del Main Deck, sala 0, con gráficos de temática urbana y datos de mapa añadidos. La v1.2 conserva dichos recursos, así como los punteros modificados del prototipo. **La sala no está declarada probada en juego** hasta observarla en mGBA/MAGE; los renders disponibles son reconstrucciones gráficas, no capturas de emulador.

## Entregables privados

- ROM candidata: `LATINO_AMERICA_Zector_Cero_v1.2_REAL_Title_Reskin.gba`
- Parche BPS desde la v1.0 Urban Opening: `LATINO_AMERICA_Zector_Cero_v1.2_REAL_Title_Reskin.bps`
- Vista previa del arte insertado: `LATINO_AMERICA_Zector_Cero_v1.2_Title_Screen.png`
- Informe de hashes y comprobaciones: `LATINO_AMERICA_Zector_Cero_v1.2_REAL_Title_Reskin_report.json`

Fuente requerida para BPS: v1.0 Urban Opening, SHA-256 `8b5e2a57bc45fbef9de3d258a50af21f7aa06a6248227b097072ece3374fe5f5`.

## Alcance real y trabajo restante

Esta **no es la conversión completa**. La mayoría de los demás mapas/tilesets, el protagonista y sus animaciones, los enemigos/jefes/proyectiles, la interfaz, las cinemáticas y los punteros de diálogo siguen pendientes. El objetivo es reemplazar esos recursos de forma sistemática y compatible con los mapas de juego, no simplemente recolorear el fondo o añadir pantallas de presentación.

## Estado de validación

- LZ77 de fondo, mapa de tiles, logo y objetos: round-trip estático correcto.
- Todos los nuevos recursos caben dentro de sus bloques asignados.
- Cabecera GBA: checksum correcto.
- Parche BPS: aplicado a la v1.0 de referencia, salida coincidente byte por byte.
- Emulador, arranque, pulsación de START, transición al juego y apariencia del escenario inicial: **pendiente**.
