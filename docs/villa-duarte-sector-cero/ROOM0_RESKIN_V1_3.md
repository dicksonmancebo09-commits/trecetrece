# v1.3 — Título real y primer escenario conectado al mapa del juego

**Proyecto:** LATINO AMÉRICA Zector Cero  
**Fecha:** 27 de octubre de 2026  
**Build privada:** `LATINO_AMERICA_Zector_Cero_v1.3_TITLE_AND_FIRST_ROOM_RESKIN.gba`  
**Estado:** comprobaciones estáticas diseñadas para recursos y mapas; ejecución en emulador pendiente.

## Corrección importante

La v1.1 QA Viewer se descarta. Añadía un panel al principio y luego intentaba saltar al juego; no era una conversión real. La v1.2 sustituyó los recursos reales del título, pero no terminaba de rehacer el primer mapa jugable.

La v1.3 elimina esa ruta de trabajo y actúa sobre los recursos a los que apuntan los datos de sala.

## Integración de la pantalla de título

La v1.2 sustituyó el fondo real, la paleta y el tilemap del título; limpió los gráficos del antiguo logo y los objetos del menú, cambió el encabezado de GBA y conservó el código de arranque original. Esos cambios se mantienen en v1.3.

## Integración del escenario inicial

El área objetivo es **Main Deck, sala 0**, cuya entrada de sala utiliza un tileset ligado a las gráficas del tileset 61 y a la paleta 76. La v1.0 había redirigido recursos a bloques privados añadidos al final de la ROM; la v1.3 trabaja con esos punteros reales:

- Tabla de metatiles: `0x7B0000`.
- Mapa BG1: `0x7B2000`.
- Mapa BG2: `0x7B2400`.
- Gráficas del tileset: se conserva o redirige su puntero según el tamaño LZ, registrado en el informe.
- Paleta del escenario: `0x46B494`.

Se genera una biblioteca 4bpp de 368 tiles, una tabla con 384 metatiles de 16×16, un BG2 con la composición de calle de Villa Duarte y un BG1 transparente. El mapa de colisiones/clipdata y el código del juego permanecen intactos. El tilemap/room map se reconstruye de nuevo en lugar de dejar las estructuras espaciales originales apuntando a gráficos urbanos desordenados.

La imagen `LATINO_AMERICA_Zector_Cero_v1.3_room0_from_ROM_resources_2x.png` es una **reconstrucción a partir de los recursos escritos en la ROM**, no una captura de emulador. Algunas celdas de tiles de baja frecuencia se aproximan a patrones cercanos para respetar el límite de 368 tiles del formato 4bpp.

## Comprobaciones estáticas

- La gráfica LZ77 del escenario se descomprime al tamaño requerido.
- BG1 y BG2 decodifican exactamente 34×14 entradas y caben en sus bloques privados.
- La tabla de metatiles contiene 384 definiciones; todos los IDs del mapa están en rango.
- La cabecera GBA es válida y los bytes de arranque se conservan.
- El parche BPS aplicado a la v1.0 debe reproducir la v1.3 byte por byte.

**No probado en emulador.** Se debe abrir con mGBA/MAGE y comprobar título, START, transición, escenario, movimiento, colisiones y continuidad.

## Entrega y alcance

La ROM completa y el parche se mantienen fuera del repositorio público. El parche BPS requiere la v1.0 Urban Opening con SHA-256 `8b5e2a57bc45fbef9de3d258a50af21f7aa06a6248227b097072ece3374fe5f5`.

Esta v1.3 es el primer corte de integración real de título + sala 0, **no el juego completo**. Todavía faltan los demás tilesets/mapas, protagonista/animaciones, enemigos, jefes, proyectiles, HUD, pantallas de mapa/pausa, cinemáticas y diálogo integrado.