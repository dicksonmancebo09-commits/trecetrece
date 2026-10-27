# Diagnóstico GBA en GitHub Codespaces — mGBA

Este flujo instala **mGBA**, un emulador GBA de código abierto, dentro del entorno de Codespaces y prepara capturas reproducibles para investigar fallos de arranque. mGBA oficial ofrece interfaces gráficas y de línea de comandos; Debian empaqueta la interfaz Qt como \`mgba-qt\`.

Fuentes:
- Proyecto oficial: https://github.com/mgba-emu/mgba
- Descargas oficiales: https://mgba.io/downloads.html
- Paquete Debian \`mgba-qt\`: https://packages.debian.org/bookworm/games/mgba-qt
- Manual de opciones de mGBA: https://manpages.debian.org/bookworm/mgba-qt/mgba-qt.6.en.html

## 1. Instalar en Codespaces

El \`postCreateCommand\` del contenedor instala estas herramientas al crear o reconstruir el Codespace. Si el Codespace ya existe, ejecuta una vez:

\`\`\`bash
bash tools/install_gba_emulator.sh
\`\`\`

Instala mGBA Qt/SDL, Xvfb (pantalla virtual), xdotool (entrada de teclado), ImageMagick (capturas), zip y Python. No descarga ni instala ROMs.

## 2. Perfil central de parámetros

La configuración central está en [`config/gba_lab.json`](../../config/gba_lab.json). Evita repetir valores a mano. Incluye:

- Perfiles con título/código/hash para la ROM base y las versiones conocidas.
- Mapa de hardware GBA: VRAM, BGR555, tiles 4bpp, banco de paleta, índice transparente y posiciones de recursos conocidas.
- Binarios de emulador, resolución virtual, niveles de log, tiempos de arranque, mapeo de teclas y secuencia de checkpoints.
- Puertas mínimas de calidad estática y de ejecución.

Los perfiles de versiones conocidas son identificadores exactos. Si la ROM cambia, el perfil debe fallar por SHA o bytes esperados; para una build nueva usa `gba_candidate_unpinned` hasta registrar un perfil nuevo.

## 3. Guardar ROMs de prueba de forma privada

```bash
mkdir -p private-roms
```

Copia ahí la ROM base y la candidata, por ejemplo:

- `private-roms/MetroidFusion_original_backup.gba`
- `private-roms/LATINO_AMERICA_Zector_Cero_v1.7_TITLE_HANGAR_FIX.gba`

El directorio `private-roms/` y las extensiones de ROM/parches/save están ignorados por Git. **No subas una ROM comercial, ROM modificada ni un parche derivado al repositorio público.**

## 4. Auditoría estática antes de ejecutar

Para auditar la build conocida v1.7 contra la base limpia:

```bash
python3 tools/gba_rom_audit.py \
  --rom private-roms/LATINO_AMERICA_Zector_Cero_v1.7_TITLE_HANGAR_FIX.gba \
  --profile zector_cero_v1_7 \
  --baseline private-roms/MetroidFusion_original_backup.gba \
  --report private-roms/diagnostics/v1.7-static-audit.json
```

Para una candidata nueva cuyo SHA aún no esté registrado:

```bash
python3 tools/gba_rom_audit.py \
  --rom private-roms/candidate.gba \
  --profile gba_candidate_unpinned \
  --baseline private-roms/MetroidFusion_original_backup.gba \
  --report private-roms/diagnostics/candidate-static-audit.json
```

El informe registra SHA-256, título/código, checksum, bytes esperados (si el perfil los declara), cantidad de bytes cambiados y rangos del delta. Los rangos protegidos solo se comparan si pasas una ROM de referencia. La herramienta es de solo lectura: no repara ni modifica la entrada.

## 5. Pruebas de ejecución comparables

La tarea **GBA: diagnosticar ROM (capturas + log)** usa el archivo central de parámetros. Desde la terminal:

```bash
bash tools/run_gba_diagnostic.sh private-roms/MetroidFusion_original_backup.gba \
  --profile gba_candidate_unpinned \
  --baseline private-roms/MetroidFusion_original_backup.gba

bash tools/run_gba_diagnostic.sh private-roms/LATINO_AMERICA_Zector_Cero_v1.7_TITLE_HANGAR_FIX.gba \
  --profile zector_cero_v1_7 \
  --baseline private-roms/MetroidFusion_original_backup.gba
```

Se ejecutan los siguientes checkpoints (ajustables en `config/gba_lab.json`):

1. Arranque y pantalla principal.
2. Pulsación START y pantalla siguiente.
3. Confirmación con A para entrar en la nueva partida.
4. Espera para observar la llegada al hangar.
5. Pulsación derecha para observar si el juego responde al movimiento.

Las ROMs se copian a un directorio temporal privado para que las partidas guardadas generadas no alteren el archivo fuente. El directorio temporal se elimina al terminar. El ZIP final incluye capturas de ventana, log de mGBA, hash, perfil, estado de proceso e informe estático opcional, **pero no la ROM ni los saves**.

El resultado se guarda en `private-roms/diagnostics/`. Si la ventana del emulador no se pudo identificar, el script lo marca como fallo de diagnóstico aunque haya logrado capturar el escritorio virtual.

## 6. Compartir el resultado para diagnosticar

Adjunta el ZIP de `private-roms/diagnostics/` en la conversación. Con esos datos podemos comparar de forma reproducible la base y la candidata.

## Alcance y límites

- Una captura a los 7 segundos y otra tras START/A/derecha no certifican todo el juego.
- Que el proceso de mGBA siga vivo **no** significa que el juego esté respondiendo; hay que inspeccionar las capturas.
- Esta smoke test no certifica colisiones, puertas, todos los enemigos, guardado o transiciones de áreas.
- GitHub Actions comprueba dependencias, perfiles, sintaxis y pruebas unitarias, pero no ejecuta ROMs privadas que no se encuentran en el repositorio.
- El paquete de mGBA instalado en Ubuntu se usa sin depender de la opción de autorrecarga `--script`, cuya disponibilidad varía según la compilación de mGBA. Para scripting de bajo nivel, usa el menú Tools → Scripting de una instalación que lo incluya y registra su versión.

## Recuperación manual

Para abrir una ROM en ventana si tienes un escritorio disponible:

```bash
mgba-qt private-roms/LATINO_AMERICA_Zector_Cero_v1.7_TITLE_HANGAR_FIX.gba
```

Teclas predeterminadas configuradas en este perfil: Enter = START, X = A, Z = B, Backspace = SELECT, flechas = dirección, A/S = L/R.


## Verificación de la instalación mGBA (27-10-2026)

- GitHub Actions: [ejecución de validación](https://github.com/dicksonmancebo09-commits/trecetrece/actions/runs/40514550712) completada con éxito.
- En runner Ubuntu 24.04 se instaló mGBA Qt/SDL **0.10.2**, Xvfb, xdotool e ImageMagick.
- Pasaron la detección de mGBA, la comprobación sintáctica `bash -n` de ambos scripts y la compilación sintáctica del probe Python.
- **Límite deliberado:** esa ejecución no ejecutó una ROM. El archivo privado permanece en `private-roms/`; el test real requiere ejecutar el script de diagnóstico en el Codespace que contiene la ROM.
