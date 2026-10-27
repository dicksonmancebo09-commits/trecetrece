# Instalación de Stable Diffusion + OmniRoute + skills de desarrollo

## Qué se configura

- **REA**: reverse engineering y herramientas de investigación.
- **ComfyUI**: interfaz de generación local con modelos de Stable Diffusion.
- **OmniRoute**: gateway de modelos/proveedores de IA, con dashboard y API compatibles. Necesita que configures un proveedor en el dashboard.
- **Ponytail**: skill que favorece la solución mínima completa y evita sobreingeniería.
- **Humanizer**: skill para reescribir texto de forma natural sin alterar los hechos.
- **Impeccable**: skill de diseño de interfaces y refinamiento visual.
- **UI/UX Pro Max**: base de referencias, estilos, paletas, tipografía y guías UX.
- **Scrapling**: framework de Python para extraer y rastrear información web. Los navegadores que necesita para sitios dinámicos son una instalación adicional opcional.

Fuentes:
- REA: https://github.com/morluto/rea
- ComfyUI: https://github.com/Comfy-Org/ComfyUI
- OmniRoute: https://github.com/diegosouzapw/OmniRoute
- Ponytail: https://github.com/DietrichGebert/ponytail
- Humanizer: https://github.com/blader/humanizer
- Impeccable: https://github.com/pbakaus/impeccable
- UI/UX Pro Max: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- Scrapling: https://github.com/D4Vinci/Scrapling

## Instalación completa en Codespaces/Linux

El contenedor usa Node.js y Python 3.12. El comando de creación instala el stack de IA, las cuatro skills de GitHub Copilot y Scrapling.

También se puede ejecutar desde la terminal del proyecto:

```bash
bash tools/install_all_tools.sh
```

Los archivos de skills se colocan en `.github/skills/` dentro del workspace, para que el repositorio y el agente de Copilot puedan encontrarlos.

## Arrancar las interfaces

```bash
bash tools/start_ai_stack.sh
```

- **ComfyUI:** http://localhost:8188
- **OmniRoute dashboard:** http://localhost:20128/dashboard
- **OmniRoute API:** http://localhost:20128/v1

OmniRoute no se conecta automáticamente a ComfyUI. Son herramientas diferentes: ComfyUI genera imágenes con un checkpoint local y OmniRoute enruta consultas a proveedores de IA. Conectar ComfyUI a un flujo de agentes específico requiere configuración adicional.

## Modelo de Stable Diffusion

ComfyUI puede instalarse sin los pesos del modelo. Para que pueda generar imágenes hace falta un checkpoint compatible.

El instalador ofrece Stable Diffusion 1.5, de aproximadamente 4.27 GB, desde su repositorio publicado en Hugging Face. No descarga ese archivo de forma automática en cada creación de Codespace.

```bash
bash tools/install_ai_stack.sh --with-model
```

El script comprueba el SHA-256 declarado antes de mover el modelo a `ComfyUI/models/checkpoints/`. Consulta y acepta los términos/licencia del modelo antes de usarlo: https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5

En un Codespace sin GPU, la generación puede ser muy lenta. Si necesitas crear muchas imágenes, una máquina local con GPU compatible o un servidor de GPU será más práctica.

## Skills de GitHub Copilot

Instalador de proyecto:

```bash
bash tools/install_project_skills.sh
```

Los cuatro destinos esperados son:
- `.github/skills/ponytail/SKILL.md`
- `.github/skills/humanizer/SKILL.md`
- `.github/skills/impeccable/SKILL.md`
- `.github/skills/ui-ux-pro-max/SKILL.md`

Después de la instalación, abre una sesión nueva de Copilot para recargar las skills. Impeccable también incluye comandos de diseño propios, que dependen del host compatible y sus adaptadores.

## Scrapling

Scrapling se instala en un entorno Python aparte, para no mezclar dependencias con ComfyUI.

```bash
bash tools/install_scrapling.sh
```

La instalación incluye los fetchers de Scrapling. Para instalar también los navegadores requeridos por ciertas páginas dinámicas:

```bash
bash tools/install_scrapling.sh --with-browsers
```

El modo con navegadores descarga más componentes y ocupa almacenamiento adicional. Respeta las políticas, límites de uso y términos de los sitios que consultes.

## Windows PowerShell

```powershell
.\tools\install_all_tools.ps1
.\tools\start_ai_stack.ps1
```

Para descargar el checkpoint:
```powershell
.\tools\install_ai_stack.ps1 -WithModel
```

Para los navegadores de Scrapling:
```powershell
.\tools\install_scrapling.ps1 -WithBrowsers
```

## Verificación real

Se considera instalado cuando los archivos de skill existen, los módulos Python se importan y las versiones de CLI responden. Se considera que **el generador funciona** solo cuando hay checkpoint, se ejecuta un workflow en ComfyUI y se produce una imagen de prueba.

OmniRoute solo estará conectado a proveedores cuando se configuren desde su dashboard. No guardes claves de proveedor en GitHub. No subas checkpoints, salidas grandes, ROMs comerciales ni binarios derivados al repositorio.
