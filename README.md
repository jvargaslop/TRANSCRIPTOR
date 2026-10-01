# Transcriptor web de audio (español y más) · NVIDIA Canary 1B v2

Transcribe audio a texto desde el navegador, **sin instalar nada en tu equipo**.
La interfaz es una página estática (HTML) que se publica gratis en GitHub Pages;
el modelo corre aparte, en una GPU en la nube (Google Colab, Kaggle o Hugging Face).

> **English TL;DR:** a static web page (GitHub Pages) that sends audio to a Gradio
> backend running NVIDIA Canary 1B v2 on a free cloud GPU (Colab/Kaggle) or a
> Hugging Face Space. Supports Spanish, English, French, German, Italian and Portuguese.
> No local Python needed.

**Estado:** proyecto experimental. Las instalaciones de NeMo y los límites de
las plataformas gratuitas cambian con frecuencia; si algo falla, mira la sección
[Problemas frecuentes](#problemas-frecuentes).

---

## Cómo funciona

```
 Navegador (index.html)  ──►  Backend Gradio (app.py)  ──►  Canary 1B v2 (GPU)
   GitHub Pages                Colab / Kaggle / HF Space
```

- `index.html`: página con selector de idioma, subida o grabación de audio,
  progreso por bloques, y botones para copiar o descargar el texto (.txt).
- `app.py`: backend en [Gradio](https://www.gradio.app) que expone la API `/transcribe`.
  Corta el audio en bloques de 30 s, los transcribe en lotes y devuelve resultados parciales.

## Idiomas

La página ofrece español, inglés, francés, alemán, italiano y portugués.
El modelo [`nvidia/canary-1b-v2`](https://huggingface.co/nvidia/canary-1b-v2)
admite 25 idiomas europeos; puedes añadir más editando la lista `LANGS` en `app.py`
y las opciones del `<select>` en `index.html`.

**El idioma no se detecta solo:** elige el idioma del audio antes de transcribir.

## Archivos

| Archivo | Para qué sirve |
|---|---|
| `index.html` | Interfaz web (se publica en GitHub Pages) |
| `app.py` | Backend con el modelo |
| `requirements.txt` | Dependencias de Python (para Hugging Face Spaces) |
| `packages.txt` | Paquetes del sistema (`ffmpeg`, `libsndfile1`) para Spaces |

## Puesta en marcha

### 1. Publicar la página (GitHub Pages)

1. Haz un fork de este repositorio, o crea uno y sube `index.html`.
2. *Settings → Pages → Branch: `main` / root → Save*.
3. La página quedará en `https://TU-USUARIO.github.io/NOMBRE-REPO/`.

### 2. Arrancar el backend (elige una opción)

El modelo necesita una **GPU**. Todas las opciones siguientes se usan desde el navegador.

#### Opción A · Google Colab o Kaggle (gratis, enlace temporal)

1. Crea un notebook y activa una **GPU T4**.
   - Colab: *Entorno de ejecución → Cambiar tipo de entorno → GPU T4*.
   - Kaggle: *Session options → Accelerator → GPU T4*, y **Internet: On**
     (requiere verificar el teléfono en tu perfil).
2. Instala las dependencias (tarda varios minutos):
   ```
   !apt-get -qq install -y ffmpeg libsndfile1
   %pip install "nemo_toolkit[asr]" gradio librosa soundfile
   ```
   Si el instalador pide reiniciar, reinicia la sesión (sin borrar el entorno).
3. Crea `app.py`: copia su contenido en una celda cuya **primera línea** sea
   `%%writefile app.py` (o sube el archivo al panel de archivos).
4. Arranca, en una celda sola:
   ```
   !python app.py
   ```
5. Cuando veas `Modelo listo.` y `Running on public URL: https://xxxx.gradio.live`,
   copia ese enlace.
6. Abre tu página de GitHub Pages, pégalo en **Backend** y transcribe.

El enlace cambia en cada arranque y deja de funcionar si la sesión se cierra.

#### Opción B · Hugging Face Space (enlace fijo)

1. Crea un Space con SDK **Gradio** y una GPU (ZeroGPU con cuenta PRO, o una GPU de pago por hora).
2. Sube `app.py`, `requirements.txt` y `packages.txt`.
3. En la página, escribe en **Backend**: `tu-usuario/nombre-del-space`.

#### Opción C · En tu equipo (si tienes Python y GPU NVIDIA)

```bash
pip install "nemo_toolkit[asr]" gradio librosa soundfile
python app.py
```
Abre el enlace local que imprime Gradio y pégalo en **Backend**.

## Uso de la API (opcional)

El backend es una app de Gradio, así que puedes llamarlo desde código:

```python
from gradio_client import Client, handle_file

client = Client("https://xxxx.gradio.live")   # o "usuario/space"
for update in client.submit(handle_file("audio.wav"), "es", api_name="/transcribe"):
    print(update["done"], "/", update["total"])
```
Cada actualización devuelve `{"done", "total", "segments": [{"start", "text"}, ...]}`.

## Límites

- Hasta **120 minutos** por audio (configurable con `MAX_MINUTES`).
- Las marcas de tiempo son por bloque de 30 s, no por palabra.
- Las plataformas gratuitas tienen cuota de GPU y cierran sesiones inactivas.
- El audio se envía al backend que tú indiques. **No uses backends de terceros con audio confidencial.**

## Problemas frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `Failed to fetch` en la página | El backend está caído, el enlace es antiguo, o la red bloquea `gradio.live` | Abre el enlace en otra pestaña; si dice "No interface is running", vuelve a ejecutar `app.py` y usa el enlace nuevo |
| `No module named 'nemo'` | Instalación perdida tras reiniciar la sesión, o sin internet | Activa Internet (Kaggle) y repite la instalación |
| `Temporary failure in name resolution` | Notebook sin internet | Kaggle: *Internet: On* y reiniciar la sesión |
| `%%writefile ... cell body is empty` | El código no está en la misma celda | Pon `%%writefile app.py` en la primera línea y el código debajo, en una sola celda |
| El modelo corre en `cpu` | GPU no activada o incompatible | Elige **T4** (evita la P100 en Kaggle), comprueba con `!nvidia-smi` y `torch.cuda.is_available()` |
| Se queda sin memoria | Lotes demasiado grandes | Baja `BATCH` en `app.py` |
| Avisos rojos de `protobuf`, `requests`, etc. al instalar | Conflictos con paquetes preinstalados del entorno | Son avisos; ignóralos si la instalación termina |

## Licencias y créditos

- Modelo: [NVIDIA Canary 1B v2](https://huggingface.co/nvidia/canary-1b-v2), publicado con licencia CC-BY-4.0. Revisa su ficha por si cambia.
- [NVIDIA NeMo](https://github.com/NVIDIA/NeMo) y [Gradio](https://github.com/gradio-app/gradio), cada uno con su propia licencia.
- El código de este repositorio: añade el archivo `LICENSE` que prefieras (por ejemplo MIT).

## Contribuir

Las ideas y mejoras son bienvenidas: más idiomas, detección automática de idioma,
exportar a SRT/VTT, o una versión alternativa con Whisper. Abre un *issue* o un *pull request*.
