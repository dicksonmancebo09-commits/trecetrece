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

## 2. Guardar ROMs de prueba de forma privada

\`\`\`bash
mkdir -p private-roms
\`\`\`

Copia ahí la ROM base y la candidata, por ejemplo:

- \`private-roms/Urban_Opening_v1.0.gba\`
- \`private-roms/LATINO_AMERICA_Zector_Cero_v1.3.gba\`

El directorio \`private-roms/\` está excluido de Git. **No subas una ROM comercial, una ROM modificada ni un parche derivado al repositorio público.**

## 3. Ejecutar pruebas comparables

\`\`\`bash
bash tools/run_gba_diagnostic.sh private-roms/Urban_Opening_v1.0.gba
bash tools/run_gba_diagnostic.sh private-roms/LATINO_AMERICA_Zector_Cero_v1.3.gba
\`\`\`

Cada ejecución abre la ROM en mGBA dentro de una pantalla virtual, captura la pantalla inicial, envía Enter (el control START por defecto en mGBA) una vez, captura la siguiente pantalla, guarda los mensajes del emulador y ejecuta la sonda de cabecera.

El paquete se genera en:

\`\`\`
private-roms/diagnostics/NOMBRE-ROM-FECHA.zip
\`\`\`

Ejecuta la base y la candidata por separado con la misma configuración. Así podremos comparar exactamente el título, los mensajes, y la pantalla que aparece tras START.

## 4. Compartir el resultado para diagnosticar

Adjunta los ZIPs de \`private-roms/diagnostics/\` en la conversación. Contienen capturas, log, versión de mGBA, hash y metadatos de cabecera, **pero no incluyen la ROM**. Con esos datos se puede diferenciar mejor entre un problema visual del título, error de carga, pantalla negra y fallo posterior a START.

## Alcance y límites

- Una captura a los 5 segundos y otra después de una pulsación no demuestra que el juego entero funcione.
- Que el proceso de mGBA siga vivo **no** significa que el juego no se haya quedado bloqueado. Hay que inspeccionar las capturas y los mensajes.
- Este script todavía no valida movimiento, colisiones, puertas, transiciones, enemigos ni guardado; esos pasos se reproducirán después con controles y capturas adicionales.
- GitHub Actions comprobará la instalación del emulador y la sintaxis de los scripts, pero no puede probar una ROM que permanece dentro del Codespace privado y no está en el repositorio.
- Este flujo usa el paquete estable de mGBA para el primer diagnóstico visual. Un diagnóstico de bajo nivel con breakpoints y memoria podrá añadirse después de reproducir el fallo.

## Recuperación manual

Para abrir el emulador con ventana (si el entorno tiene escritorio remoto disponible):

\`\`\`bash
mgba-qt private-roms/LATINO_AMERICA_Zector_Cero_v1.3.gba
\`\`\`

Teclas predeterminadas en mGBA: Enter = START, X = A y Z = B.
