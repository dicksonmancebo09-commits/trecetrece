# Instalación de Stable Diffusion + OmniRoute

## Qué instalamos

- **ComfyUI** es la interfaz/generador local compatible con Stable Diffusion. Requiere un checkpoint de modelo.
- **Stable Diffusion 1.5** es el checkpoint inicial que se ofrece como descarga opcional. Está publicado en Hugging Face bajo CreativeML OpenRAIL-M; revisa esa licencia y sus condiciones.
- **OmniRoute** es el gateway que unifica proveedores/modelos de IA a través de una API compatible; requiere configurar un proveedor en su dashboard. No se conecta automáticamente a ComfyUI ni sustituye el checkpoint de Stable Diffusion.
- **REA** se conserva instalado porque forma parte de las herramientas de investigación del proyecto.

Fuentes oficiales:
- ComfyUI: https://github.com/Comfy-Org/ComfyUI
- OmniRoute: https://github.com/diegosouzapw/OmniRoute
- OmniRoute quick start: https://github.com/diegosouzapw/OmniRoute/wiki/Quick-Start
- Stable Diffusion 1.5 checkpoint (4.27 GB, SHA-256 publicado): https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/blob/main/v1-5-pruned-emaonly.safetensors

## En Codespaces/Linux

La configuración de Codespaces instala Node.js y Python 3.12 y ejecuta el script del proyecto. Ejecuta manualmente si quieres instalar/actualizar:

```bash
bash tools/install_ai_stack.sh
```

Arranca los servicios:

```bash
bash tools/start_ai_stack.sh
```

Se abrirán estos puertos en Codespaces:
- OmniRoute dashboard: http://localhost:20128/dashboard
- OmniRoute API: http://localhost:20128/v1
- ComfyUI: http://localhost:8188

### Descargar el modelo de Stable Diffusion

El checkpoint ocupa aproximadamente 4.27 GB. No se descarga automáticamente para no consumir la cuota de almacenamiento/banda en cada Codespace. Cuando estés listo para descargarlo:

```bash
bash tools/install_ai_stack.sh --with-model
```

El script verifica el SHA-256 `6ce0161689b3853acaa03779ec93eafe75a02f4ced659bee03f50797806fa2fa` antes de instalar el archivo en `models/checkpoints`. Para el juego, empieza generando concept art y variantes de paleta; después conviértelas/adáptalas a pixel art manualmente.

### Conectar OmniRoute

1. Abre el dashboard y ve a Providers.
2. Conecta un proveedor gratuito o introduce una clave obtenida directamente de ese proveedor.
3. No guardes contraseñas, tokens ni API keys en GitHub.
4. Para clientes compatibles con OpenAI, el endpoint local es `http://localhost:20128/v1`. Toma la API key del dashboard y configura en el cliente el modelo/proveedor que hayas habilitado.

OmniRoute dirige solicitudes de modelos/proveedores de IA. ComfyUI es el generador local de imágenes. Que ambos estén instalados no configura por sí solo un flujo entre ellos; cualquier integración concreta se añadirá y probará como una tarea separada.

## Instalación en Windows (PowerShell)

Requisitos: Node.js 22+, Git y Python 3.12+. Desde la raíz del repositorio:

```powershell
.\tools\install_ai_stack.ps1
.\tools\start_ai_stack.ps1
```

Para descargar también el checkpoint de 4.27 GB:

```powershell
.\tools\install_ai_stack.ps1 -WithModel
```

La instalación detecta una GPU NVIDIA con `nvidia-smi`; si no detecta NVIDIA, instala la versión CPU de PyTorch. En CPU la generación puede ser muy lenta. Para AMD/Intel en Windows, utiliza la guía oficial de ComfyUI adecuada a tu GPU en vez de asumir que el modo CPU es óptimo.

## Verificación

Después de arrancar, comprueba:
- ComfyUI carga en el puerto 8188 y reconoce el checkpoint en Checkpoints.
- Genera una imagen sencilla mediante un workflow de ComfyUI. La importación de Python por sí sola no demuestra que el generador funcione.
- OmniRoute abre su dashboard en el puerto 20128 y lista los modelos del proveedor que conectaste.

En Codespaces sin GPU, ComfyUI funciona en modo CPU y puede tardar bastante. Para generación rápida, lo ideal es instalarlo en un equipo con GPU compatible o alojarlo en una máquina que disponga de GPU.

Los modelos y outputs se guardan fuera del repositorio; no subas checkpoints enormes, modelos ni outputs innecesarios a GitHub.
