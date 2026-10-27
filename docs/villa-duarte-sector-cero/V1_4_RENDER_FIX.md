# v1.4 Render Fix — cambios y estado de validación

**Fecha:** 27 de octubre de 2026.

La build privada v1.4 corrige dos incoherencias del render GBA detectadas al revisar los bytes de v1.3:

1. El mapa del fondo del título seleccionaba el banco de paleta 0, aunque la paleta urbana se carga en el banco 8. En v1.4 todas las entradas del mapa de título seleccionan el banco 8.
2. La tabla de metatiles usaba índices locales 0–367, pero el tileset se carga en VRAM en el índice hardware 192. En v1.4 se suma 192 al índice de cada subtile, preservando bits de flip y paleta. El rango final es 192–559.

## Validación binaria

- Tamaño de ROM: 8.388.608 bytes.
- SHA-256 de la v1.3 de entrada: `96347bd1e9e73b5ccd9f1efc9737dd183920bad389153e8d0567e6830187b6db`.
- SHA-256 de la v1.4 de salida: `bea31b027ecaf19b34567f96de16f82814871764830127980d4ead23982502e0`.
- Checksum de cabecera GBA: válido (`0x6D`).
- Mapa de título: LZ77 comprimido de nuevo y round-trip verificado; 1.024 entradas seleccionan banco 8.
- Tabla de sala 0: 1.536 subtiles ajustados; índices 192–559; los bits de flip/paleta permanecen iguales.
- Parche BPS: `LATINO_AMERICA_Zector_Cero_v1.4_RENDER_FIX.bps`; su base requerida es la v1.3 con SHA-256 anterior. Se aplicó mediante el verificador local y produjo la salida byte por byte.

## Alcance y límite

Esta versión corrige los dos defectos gráficos localizados, pero **no se ha validado en una sesión real de mGBA**. El intento de instalar mGBA en el contenedor actual no terminó dentro del tiempo disponible; el workflow de GitHub Actions solo valida la instalación del toolchain en su runner, no ejecuta una ROM privada. No se debe afirmar que el crash quedó resuelto hasta revisar una ejecución real del juego.

La ROM y el parche se mantienen fuera del repositorio público. No subir binarios de ROM ni parches derivados.
