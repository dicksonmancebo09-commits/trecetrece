# REA en GitHub Codespaces

## Qué hace este entorno

El Dev Container usa la imagen Node.js 22 de Microsoft y, cuando Codespaces termina de crear el entorno, instala la CLI **REA (Reverse Engineer Anything)**, versión fijada **6.8.0**, con npm global. La configuración del repositorio no contiene una ROM ni descarga juegos.

- Proyecto de REA: https://github.com/Opiuz/REA
- Sitio y guía oficial: https://rea.tools/
- Guía de instalación: https://github.com/Opiuz/REA/blob/main/docs/installation.md
- Node.js requerido por las instrucciones de REA: 22.x (>=22.19), 24.x (>=24.11) o 26+.

## Cómo abrir el Codespace

1. Abre [trecetrece en GitHub Codespaces](https://codespaces.new/dicksonmancebo09-commits/trecetrece?quickstart=1).
2. Acepta la creación del Codespace. GitHub puede pedir elegir rama; selecciona `main` después de que se integre esta configuración.
3. Espera a que termine la configuración inicial del contenedor.
4. En la terminal integrada, verifica la instalación con `rea --version` y `rea --help`.

Si el Codespace ya estaba abierto antes de añadir `.devcontainer/devcontainer.json`, ejecuta **Codespaces: Rebuild Container** desde la paleta de comandos para que use la nueva configuración.

## Conectar REA al agente

La instalación de la CLI no configura automáticamente todos los agentes. En la terminal ejecuta:

```bash
rea setup
```

Revisa el plan que REA presenta antes de aprobar cambios de configuración. Elige únicamente el cliente que realmente esté instalado y se vaya a utilizar en este Codespace. Después reinicia o vuelve a conectar ese cliente y comprueba el estado con los comandos de diagnóstico que indique la versión instalada.

No se fuerza una configuración automática de agente durante la creación del entorno, porque los clientes disponibles y sus credenciales dependen de cada cuenta.

## Importante para el proyecto GBA

REA es una herramienta de investigación de software; **no es un editor de ROM ni sustituye a MAGE**. Instalar la CLI no demuestra por sí mismo que REA pueda analizar correctamente una ROM de Game Boy Advance. El flujo para importar una ROM en Ghidra u otro motor, seleccionar arquitectura y validar resultados requiere una prueba específica. El archivo debe mantenerse fuera de este repositorio público.

Para seguir trabajando con ROMs en el Codespace:
- no subir ROMs comerciales, ROMs modificadas ni parches binarios a este repositorio;
- no dar por válida una conclusión del análisis sin evidencias y verificación independiente;
- registrar los resultados, herramientas y limitaciones en la bitácora del proyecto.

## Solución de problemas

- Si `rea --version` no aparece, confirma que la creación del contenedor terminó; después prueba `npm install --global rea-agents@6.8.0` y vuelve a ejecutar `rea --version`.
- Si el entorno ya existía, reconstruye el contenedor para ejecutar `postCreateCommand`.
- Si `rea setup` no detecta el agente deseado, no inventes un cliente ni pegues tokens. Consulta la lista de clientes admitidos por la documentación de la versión instalada.
