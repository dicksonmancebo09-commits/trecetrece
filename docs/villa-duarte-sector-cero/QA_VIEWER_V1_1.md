> **OBSOLETA — NO USAR COMO BUILD ACTUAL.** La v1.1 añadía un visor antes del juego y luego intentaba saltar a la entrada original; no era una conversión real de la pantalla de título y no debe tratarse como la ROM de prueba vigente. Usa la [v1.2 — sustitución real de recursos de título](REAL_TITLE_RESKIN_V1_2.md), que reemplaza recursos dentro de la ROM y conserva el arranque original.

# Candidata v1.1 — QA Viewer de escenarios

**Proyecto:** LATINO AMÉRICA Zector Cero  
**Fecha:** 27 de octubre de 2026  
**Estado:** build creada y comprobada estáticamente; emulador pendiente.  
**Entrega privada:** ROM y parche se facilitan en la conversación; no se publican como binarios en este repositorio.

## Qué incorpora esta candidata

Se construyó sobre la salida v1.0 Urban Opening archivada. Al iniciar, antes de saltar a la entrada original del juego, muestra un visor de dos pantallas GBA de 240 × 160 píxeles:

- **L:** Escenario 1 — Entrada al Barrio.
- **R:** Escenario 2 — Callejones del Caliche.
- **START:** intenta continuar a la entrada original del prototipo v1.0.

Las dos pantallas son ilustraciones originales de revisión en BGR555 con una muestra de diálogo del borrador es-419. Se diseñaron para comprobar escala y legibilidad a resolución GBA; no son capturas de emulador ni los atlas SVG insertados como tiles nativos.

## Lo que NO significa

Esta candidata **no** sustituye los mapas o tilesets reales de las salas del juego. Tampoco conecta el paquete completo de diálogo es-419 con la rutina de texto y sus punteros. La jugabilidad que se conserva sigue siendo la de v1.0. Por eso se llama *QA Viewer candidate*, no versión completa con todos los cambios integrados.

## Verificaciones estáticas

| Comprobación | Resultado |
|---|---|
| ROM de entrada | 8 MiB; SHA-256 8b5e2a57bc45fbef9de3d258a50af21f7aa06a6248227b097072ece3374fe5f5 |
| Tamaño de la candidata | 16 MiB |
| SHA-256 de la candidata | 02bec9687e9e93d2a27aa595b48df74a1142e29288cfed37b8d6d468e350cbe1 |
| Dirección de entrada del visor | 0x08800000; instrucción ARM comprobada: 0xEA1FFFFE |
| Tamaño de cada pantalla | 76.800 bytes (240 × 160 × 2) |
| Checksum de cabecera almacenado / recalculado | 0x98 / 0x98 |
| Parche BPS | 153.927 bytes; SHA-256 add313d6933402e97e3dd50fe58340ec5697c94776cdbd8208010eba0fda1053 |
| Reaplicación del BPS a v1.0 | PASS: produce la candidata byte por byte |
| Arranque, controles y retorno al juego | No comprobados en emulador |

## Prueba manual pendiente

1. Abrir el archivo .gba en mGBA u otro emulador GBA.
2. Confirmar que aparece el escenario 1.
3. Pulsar y soltar R y comprobar que aparece el escenario 2; pulsar y soltar L para volver.
4. Pulsar START y comprobar que arranca el prototipo de juego.
5. Anotar cuelgues, pantalla negra, problemas de control o fallos al entrar al juego.

La prueba se debe marcar como **probada en emulador** solo después de observar los cuatro pasos en una sesión real.

## Uso del parche

El parche BPS se aplica sobre la build v1.0 Urban Opening indicada arriba, **no sobre una ROM limpia**. Los archivos binarios se mantienen fuera del repositorio público.