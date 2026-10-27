# v1.7 — Corrección de flujo y referencias compartidas

**Fecha:** 27 de octubre de 2026  
**ROM privada:** `LATINO_AMERICA_Zector_Cero_v1.7_TITLE_HANGAR_FIX.gba`  
**Parche:** `LATINO_AMERICA_Zector_Cero_v1.7_from_v1.6.bps`  
**Base exacta:** v1.6 con SHA-256 `43b34c080d7d78ca9e52d25edfe759686acb36706f88f527c845a45d23dc8722`.

## Hallazgos que motivan la v1.7

### A. v1.6 omitía la inicialización de la intro de arranque

En v1.6, los primeros cuatro bytes de `IntroHandler` se sustituyeron por `MOVS r0,#1; BX LR`. Eso hace que la rutina devuelva TRUE antes de ejecutar el flujo normal, omitiendo también `NewFileIntroInit()`. Es una modificación insegura del control de flujo y puede dejar estado global sin preparar.

**Corrección:** restaurar el prólogo original y cambiar el estado que se asigna después de `NewFileIntroInit()` de 1 a 3. Esto conserva la inicialización y salta las escenas del arranque sin salir de la función prematuramente.

### B. Los recursos de título se habían redirigido también para otras escenas

La v1.5 redirigió todas las referencias encontradas al fondo, mapa y paleta del título personalizado. No todos esos usos corresponden a la pantalla principal: algunos están en rutinas de intro/cinemática y esperan los gráficos y mapas originales. La v1.6 conserva esas referencias redirigidas y además intenta entrar directamente en la secuencia del hangar.

**Corrección:** solo las tres referencias del inicializador de la pantalla de título permanecen apuntando al arte urbano reubicado:
- GFX `0x86AB0 → 0x087C4000`
- tilemap `0x86AC4 → 0x087C0000`
- paleta `0x86AD4 → 0x087C1000`

Las referencias de otros usuarios se restauran a los recursos originales en `0x8605D08`, `0x8609220` y `0x8609120`.

## Conservado de v1.6

- Se mantienen los dos NOP que suprimen la creación de los objetos de copyright y PRESS START.
- START sigue siendo procesado por el manejador de entrada de título.
- Se mantiene el cambio a estado 11 de `NewFileIntroHandler` para una partida nueva, con el objetivo de empezar en la secuencia de llegada/entrada al hangar.
- Los cambios gráficos de la v1.5 (reubicación segura del arte de título y corrección de índice transparente del tileset) se conservan.

## Comprobaciones binarias

- Tamaño: 8.388.608 bytes.
- SHA-256 v1.6: `43b34c080d7d78ca9e52d25edfe759686acb36706f88f527c845a45d23dc8722`.
- SHA-256 v1.7: `66e68fb0f04f89d40ecfee21996e6be62e96a22f7f66198528ee6b2c5c2c2aaf`.
- Checksum de cabecera GBA: válido (`0x6D`).
- Las precondiciones de los bytes originales se comprobaron antes de escribir.
- El parche BPS se aplicó a v1.6 y reprodujo v1.7 byte por byte.

## Estado de ejecución

**No se ha confirmado aún la corrección en una sesión real de VBA-M/mGBA.** El contenedor local no pudo instalar mGBA por falta de resolución DNS; el workflow de GitHub Actions valida la instalación de herramientas pero no tiene acceso a las ROMs privadas.

Validación pendiente en una partida nueva:
1. Arranque: no deben aparecer la introducción “Nintendo Presents / Metroid”; debe entrar en el título personalizado.
2. Título: no deben aparecer los objetos originales de copyright ni PRESS START; START debe seguir avanzando.
3. Nueva partida: debe ejecutarse la secuencia de llegada/entrada al hangar.
4. Al terminar, el primer escenario debe cargar sin pantalla congelada o tiles ajenos.

El arte no debe considerarse funcionalmente validado hasta realizar esa prueba. Los binarios y parches ROM se mantienen fuera del repositorio público.
