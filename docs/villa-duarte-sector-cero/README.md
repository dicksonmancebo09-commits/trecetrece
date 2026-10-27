# Villa Duarte — Sector Cero

## Propósito

Crear un videojuego original inspirado en el ritmo y las posibilidades técnicas de los juegos de acción/plataformas de Game Boy Advance, con escenarios urbanos dominicanos, personajes y enemigos propios. Metroid Fusion sirve como material de estudio para investigar cómo se organizan mapas, tiles, paletas, colisiones, puertas y encuentros; no será la identidad creativa del juego final.

El proyecto no está destinado a distribuir una ROM modificada. El objetivo es aprender del funcionamiento técnico y, a partir de ahí, construir una experiencia propia.

## Principios

1. **Cambios trazables:** registrar cada hipótesis, archivo afectado, prueba y resultado.
2. **Sin modificaciones a ciegas:** inspeccionar el recurso exacto y validar referencias/punteros antes de escribir datos.
3. **Separar estudio y creación:** las referencias comerciales orientan el análisis, pero sus sprites, música, mapas, nombres y diseños no se copian al juego final.
4. **Procedencia de activos:** conservar la URL de origen y la licencia específica de cada recurso externo.
5. **No distribuir ROMs:** no almacenar en este repositorio público la ROM original, una ROM modificada ni parches binarios derivados.

## Alcance de la siguiente etapa

El alcance visual ya no se limita a una sala: la meta es transformar la ROM completa, cubriendo todos los recursos y todas las áreas aplicables. La primera sala sirve para calibrar el estilo y el método. Se realizarán copias y validaciones incrementales para detectar regresiones; nunca se presentará como terminado lo que no se haya comprobado.

## Estado técnico conocido

- ROM de referencia estudiada localmente: Metroid Fusion, región USA/Australia, código de juego **AMTE**, 8 MiB.
- Prototipo visual anterior: modificación de la sala 0 del área **MAIN_DECK**, con mapas y tiles urbanos de prueba.
- Alcance real de ese prototipo: **solo una sala**. No transforma el juego completo, no rediseña el conjunto de enemigos y no representa una versión terminada.
- Validaciones anteriores: comprobaciones estáticas de tamaño, cabecera, compresión y dimensiones de los mapas.
- Limitación: el prototipo no quedó probado en ejecución dentro de MAGE ni de un emulador; por tanto, no debe tratarse como una compilación validada en juego.
- El trabajo de ROM se pausa hasta acordar el nuevo procedimiento. No asumir que el siguiente paso es modificar otra sala.

## Próximos pasos de investigación

1. Confirmar dónde está el elemento llamado **REA**: la rama main inspeccionada el 27 de octubre de 2026 no lo muestra en su árbol de archivos.
2. Revisar en la herramienta de edición la estructura real del juego, sin escribir todavía cambios nuevos.
3. Definir si el prototipo final será una ROM de estudio privada o un juego independiente con motor y assets propios.
4. Crear un inventario reutilizable de mapas, recursos y mecánicas, distinguiendo hechos verificados de hipótesis.
5. Definir pruebas de ejecución reproducibles antes de considerar cualquier cambio como correcto.

## Enlaces internos

- [Herramientas y repositorios](research/TOOLS_AND_REPOSITORIES.md)
- [Notas técnicas de ROM](research/ROM_TECHNICAL_NOTES.md)
- [Arte y licencias](research/ART_DIRECTION_AND_LICENSES.md)
- [Bitácora](WORKLOG.md)
- [Auditoría del repositorio](REPOSITORY_AUDIT.md)
