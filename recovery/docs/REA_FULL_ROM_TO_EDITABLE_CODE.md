# De ROM GBA a código editable — plan reproducible

## Entrada confirmada

- ROM estudiada: Metroid Fusion USA/Australia, código GBA `AMTE`, tamaño 8.388.608 bytes.
- SHA-256 registrado: `a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8`.
- SHA-1 registrado: `ca33f4348c2c05dd330d37b97e2c5a69531dfe87`.
- Complemento de checksum de cabecera: `0x98`.
- Palabra de entrada `0xEA00002E`: rama ARM desde `0x08000000` a `0x080000C0`.

Si la ROM local tiene un hash distinto, no reutilices automáticamente los offsets ni las conclusiones.

## Herramientas que se necesitan

- REA: preflight, coordinación y salida preliminar si el proveedor responde.
- Ghidra con lenguaje ARM little-endian ARMv4T (`ARM:LE:32:v4t`) para validar código ARM7TDMI/Thumb. La vía genérica de REA para arquitectura `arm` podría usar ARMv7; no la trates como prueba final si no confirma v4T.
- mGBA debugger para observar la ejecución real, registros, memoria y transiciones.
- MAGE para inspeccionar salas, mapas, puertas, objetos y colisiones propios del juego.
- Una referencia de código de terceros puede ayudar a comparar nombres y lógica; verifica licencia, estado y avisos del proyecto antes de reutilizarla.

## Procedimiento de análisis

1. Calcular hashes, comprobar tamaño/cabecera y decodificar el salto de entrada.
2. Confirmar REA, Node, proveedores y backend Ghidra con el script incluido.
3. Abrir la ROM como Raw Binary en Ghidra, base `0x08000000`, little-endian, ARM:LE:32:v4t.
4. Seguir el salto real, distinguir el estado ARM/Thumb y marcar pools literales/datos para evitar desensamblar toda la ROM como código.
5. Registrar rangos de funciones, entradas/salidas, referencias, datos asociados y confianza.
6. Correlacionar con mGBA los primeros estados de arranque y una rutina cada vez.
7. Avanzar por movimiento/colisiones, salas/puertas, enemigos, proyectiles, jefes/eventos, texto, gráficos, audio y guardado.
8. Crear módulos C solo cuando el límite de la función y su comportamiento tengan evidencia. Mantener por separado los datos/recursos y su formato.
9. Antes de afirmar que la recompilación es equivalente, reproducir una build de referencia o documentar precisamente cualquier diferencia.

## Cobertura al comenzar

| Subsistema | Estado |
|---|---|
| Identidad de la ROM y entrada | Verificado estáticamente para el hash registrado |
| Inicialización de arranque | Modelo parcial |
| Despachador de 15 modos | Direcciones de la tabla observadas; rutina completa no reconstruida |
| Movimiento/física | Pendiente |
| Salas, mapas y transiciones | Pendiente; referencias a confirmar en MAGE |
| IA de enemigos y jefes | Pendiente |
| Eventos/cutscenes | Estados generales identificados, lógica pendiente |
| Recursos gráficos/audio/texto | Inventario heurístico, clasificación exhaustiva pendiente |
| Build reproducible | Pendiente |

## Privacidad y veracidad

El script guarda salida y logs bajo `private-roms/rea-analysis/`. No los añadas al repositorio. No se incluye ninguna ROM ni parche. Los archivos C de este directorio son código de análisis escrito para expresar observaciones verificadas; no se presentan como código original completo del juego ni como build jugable.
