# Transcriptor web (sin instalar nada) · Canary-Qwen 2.5B

Dos piezas:
- `index.html` → página estática. Se aloja gratis en **GitHub Pages**.
- `app.py` + `requirements.txt` + `packages.txt` → backend con GPU. Se ejecuta en la nube (Hugging Face o Colab), no en tu PC.

El modelo necesita GPU, por eso no puede correr solo en GitHub Pages.

---

## 1. Publicar la página en GitHub Pages
1. Crea un repositorio en github.com (público).
2. Sube `index.html` (botón *Add file → Upload files*).
3. *Settings → Pages → Branch: main / root → Save*.
4. En un minuto tendrás `https://TU-USUARIO.github.io/NOMBRE-REPO/`.

## 2. Backend: elige una opción

### Opción A · Hugging Face Space (enlace fijo)
1. Crea cuenta en huggingface.co → *New Space* → SDK **Gradio**.
2. Hardware: necesita GPU. Con cuenta **PRO** puedes usar *ZeroGPU*; si no, elige una GPU de pago por hora (T4/L4) y páusala cuando no la uses.
3. Sube `app.py`, `requirements.txt` y `packages.txt` al Space.
4. Espera a que termine de construir (la primera vez descarga ~5 GB).
5. En la página, escribe en "Backend": `tu-usuario/nombre-del-space`.

### Opción B · Google Colab (gratis, enlace temporal)
1. Abre colab.research.google.com → *Nuevo cuaderno* → *Entorno de ejecución → Cambiar tipo → GPU (T4)*.
2. Sube `app.py` desde el panel de archivos (icono de carpeta).
3. Ejecuta en una celda:
   ```
   !apt-get -qq install -y ffmpeg libsndfile1
   !pip install -q "nemo_toolkit[asr,tts] @ git+https://github.com/NVIDIA/NeMo.git" gradio librosa soundfile
   !python app.py
   ```
4. Al terminar de cargar aparece una línea `Running on public URL: https://xxxx.gradio.live`.
5. Pega ese enlace en el campo "Backend" de la página. Dura mientras el cuaderno siga abierto (unas 72 h como máximo).

## Notas
- El modelo transcribe **inglés**.
- Audios de hasta 120 min; se procesan en bloques de 30 s.
- Si tu red de oficina bloquea `huggingface.co`, `gradio.live` o `cdn.jsdelivr.net`, la página no podrá conectar.
- Si la instalación de NeMo falla, revisa el `requirements.txt` del Space oficial de NVIDIA: https://huggingface.co/spaces/nvidia/canary-qwen-2.5b
