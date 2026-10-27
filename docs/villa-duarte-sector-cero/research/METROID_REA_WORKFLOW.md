# Flujo de R.E. para Metroid Fusion con REA

Fecha de preparación: 2026-10-27.

## Objetivo

Usar **Reverse Engineer Anything (REA)** como asistente de investigación y registro de evidencia para entender comportamientos concretos de Metroid Fusion, empezando en modo de solo lectura. No se va a asumir que REA puede reconstruir todo el juego automáticamente, ni se editará la ROM hasta que una hipótesis esté comprobada.

## Por qué hace falta más de una herramienta

- **REA:** coordina preguntas de análisis, consulta funciones, desensamblado, referencias y pseudocódigo a través de proveedores compatibles.
- **Ghidra con perfil exacto:** analiza el código ARM/Thumb. Para GBA, el perfil del procesador debe ser ARM7TDMI / ARMv4T cuando se realiza una importación manual.
- **MAGE:** inspecciona la estructura propia de Metroid Fusion: salas, mapas, tiles, paletas, puertas, enemigos y colisiones. No sustituye al análisis del código máquina.
- **mGBA con depurador:** permite contrastar hipótesis durante la ejecución observando PC, registros, breakpoints, memoria y cambios de estado.
- **Metroid Fusion Decomp:** repositorio de referencia para comparar nombres y lógica ya investigados. Su README advierte explícitamente que la descompilación no es “shiftable” y que no debe usarse como base directa para modificar una ROM.

Fuentes:
- REA: https://github.com/morluto/rea
- Flujo de binarios sin cabecera en REA: https://github.com/morluto/rea/blob/main/docs/raw-binary.md
- Ghidra, definición ARMv4T: https://github.com/NationalSecurityAgency/ghidra/blob/master/Ghidra/Processors/ARM/data/languages/ARM.ldefs
- Mapa de memoria GBA y ARM7TDMI: https://reverseengineering.wiki/index.php/Platform%3AGame_Boy_Advance
- Descompilación de referencia: https://github.com/metroidret/mf

## Limitación importante de la vía binaria genérica de REA

La documentación de REA para `raw-binary` asigna la arquitectura `arm` a la lengua de Ghidra `ARM:LE:32:v7`. El GBA utiliza ARM7TDMI, basado en ARMv4T y con estados ARM y Thumb. Por ello, la salida de esta vía de REA sirve como **prueba exploratoria**, no como evidencia final de una instrucción concreta. Cuando la versión de REA no permite seleccionar ARMv4T, se debe contrastar el código relevante con una importación directa de Ghidra configurada como `ARM:LE:32:v4t`, little-endian, dirección base `0x08000000`. No mezclar resultados de ambos perfiles sin etiquetarlos.

## Fase 1 — comprobar el Codespace

En la terminal del Codespace:

```bash
node --version
rea --version
rea doctor --json
rea capabilities
rea providers --json
```

Después, ejecuta `rea setup` y elige solo un agente que realmente esté instalado y disponible en el Codespace. Revisa el plan que presenta antes de aprobarlo. Reinicia el agente después de la configuración.

La instalación de REA no implica que Ghidra esté instalada. Según la documentación de REA, el proveedor de Ghidra en Linux requiere una versión de Ghidra compatible con REA (la guía actual especifica Ghidra 12.1.4) y un JDK de 64 bits 21. REA puede registrar una instalación existente, pero no descarga Ghidra ni Java por sí solo. Usa la guía oficial antes de instalar:
https://github.com/morluto/rea/blob/main/README.md
https://github.com/morluto/rea/blob/main/docs/installation.md

## Fase 2 — mantener la ROM fuera del repositorio público

No guardes la ROM comercial en un directorio que puedas añadir al repo público. Dentro del Codespace, crea una carpeta local ignorada solo por Git:

```bash
mkdir -p private-roms
printf '\n/private-roms/\n' >> .git/info/exclude
```

Sube o copia la copia de estudio que tengas derecho a utilizar a `private-roms/MetroidFusion.gba`. Confirma que Git la ignora:

```gitignore
# Comprobación de exclusión local
git check-ignore -v private-roms/MetroidFusion.gba
```

Si el comando no indica que el archivo está excluido, no continúes ni ejecutes `git add`. No subas la ROM a GitHub, ni a un issue, ni a un artefacto de CI.

Comprueba identidad y tamaño:

```bash
stat -c '%n %s bytes' private-roms/MetroidFusion.gba
sha256sum private-roms/MetroidFusion.gba
xxd -g 1 -l 4 private-roms/MetroidFusion.gba
xxd -g 1 -s 0xac -l 4 private-roms/MetroidFusion.gba
```

La ROM estudiada en las comprobaciones anteriores fue identificada como Metroid Fusion USA/Australia, código GBA `AMTE`, 8 MiB. Su SHA-256 registrado fue `a56ce3d7f8f3f4f4d0468d421fff5dd3ee3aec99a58244377e43aae769dc3fe8`. Si tu fichero no coincide, no asumas que direcciones, mapas o referencias son equivalentes; registra su hash real primero.

## Fase 3 — prueba limitada con REA

Cuando `rea doctor --json` confirme que el proveedor Ghidra está disponible, ejecuta una inspección preliminar de solo lectura:

```bash
ROM="$PWD/private-roms/MetroidFusion.gba"
rea inspect "$ROM" \
  --target-format raw-binary \
  --architecture arm \
  --entry-point 0x08000000 \
  --provider ghidra \
  --json > private-roms/rea-overview.json
```

Si el comando termina correctamente, conserva el resumen en la carpeta ignorada local y registra en la bitácora la versión de REA, la versión del proveedor, el hash de la ROM y las advertencias. No asumas que todas las áreas detectadas como código son realmente código: una ROM incluye cabecera, gráficos, mapas, tablas y datos comprimidos.

La ROM del cartucho se mapea normalmente en `0x08000000`; offset de archivo = dirección de ROM − `0x08000000`. La entrada GBA es una instrucción ARM de salto en los primeros cuatro bytes y la cabecera ocupa los 192 bytes iniciales. Verifica el salto que exista en el archivo concreto; no copies una dirección de inicio de otro juego.

## Fase 4 — análisis exacto del código en Ghidra

En una importación Ghidra independiente, configura:

- Formato: Raw Binary.
- Processor/language: `ARM:LE:32:v4t`.
- Endian: little-endian.
- Base address / mapping: `0x08000000`.
- Estado ARM/Thumb: sigue los saltos, llamadas y cambios de estado; no interpretes bytes de datos como instrucciones por defecto.
- Comprueba que la primera instrucción en `0x08000000` es un salto válido y sigue la dirección de destino en el código real.

Una vez localizada una rutina, registra su dirección, rango de bytes, llamadas entrantes/salientes y datos referenciados. Valida las instrucciones relevantes con un segundo desensamblado o con la ejecución en el depurador antes de asignarles un nombre semántico.

## Fase 5 — elegir una pregunta, no analizar el juego entero de una vez

Orden sugerido:

1. **Arranque y bucle principal:** entrada, inicialización, actualización por frame y espera de VBlank.
2. **Movimiento del jugador:** lectura de controles, velocidad, aceleración, salto, colisiones y estado de animación.
3. **Salas y puertas:** estructura de datos de sala, transición, cámara y carga de objetos.
4. **Un enemigo concreto:** instancia, rutina de actualización, estados, patrulla, daño, muerte y drops.
5. **Jefes y eventos:** fases, temporizadores, condiciones de transición y triggers.

Para cada pregunta: formula una hipótesis, localiza un punto de entrada, sigue callers/callees y referencias, etiqueta las observaciones con direcciones exactas, marca dudas y no edites la ROM.

## Fase 6 — contrastar código y comportamiento

Con MAGE, identifica la sala exacta, el tipo de enemigo y los datos visuales asociados. En mGBA, reproduce el evento y observa cuándo cambian las variables relevantes. Contrasta esos cambios con las rutinas de Ghidra y la evidencia de REA.

Una conclusión solo se marca como verificada si:
- hay una dirección/rango de código concreto;
- los bytes se han interpretado con el perfil ARMv4T correcto;
- las llamadas/referencias respaldan el razonamiento;
- el comportamiento observado en ejecución concuerda, o se registra claramente que no se ha probado.

## Prompt inicial sugerido para el agente con REA

```text
Investiga de forma estrictamente de solo lectura la ROM local de Metroid Fusion.
No modifiques ni reescribas la ROM, no generes parches y no edites archivos de juego.

Primero valida el hash, tamaño, código AMTE y el mapeo de direcciones.
Inspecciona el punto de entrada 0x08000000 y sigue el salto real de arranque.
Devuelve una tabla con: dirección virtual, offset del archivo, bytes, instrucción,
referencias/calls relevantes, evidencia que respalda cada afirmación y confianza.
Separa código de datos comprimidos/tablas; no etiquetes funciones por intuición.
Indica explícitamente el perfil de procesador utilizado y sus limitaciones.
Como REA puede usar ARM:LE:32:v7 para la vía raw-binary, señala cada resultado
que deba verificarse en Ghidra con ARM:LE:32:v4t. No presentes como verificado
nada que no tenga evidencia suficiente.
Termina proponiendo una única próxima pregunta de investigación.
```

## Qué no hacer

- No analizar el archivo completo suponiendo que cada byte es código.
- No aplicar cambios de ROM mientras investigamos.
- No copiar sprites, música, mapas o código propietario al juego nuevo.
- No usar una descompilación incompleta como base directa de construcción.
- No declarar una rutina comprendida solo por un nombre sugerido por la IA.
- No subir ROMs, binarios extraídos, análisis privados o parches al repositorio público.
- No equiparar “sin fines de lucro” con permiso automático de redistribución.

## Criterio de salida

La primera meta no es obtener una ROM modificada. Es tener un informe reproducible del arranque y de una rutina pequeña, con direcciones comprobadas y evidencia suficiente para seguir con movimiento, salas o patrullas.
