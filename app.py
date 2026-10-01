"""
Backend de transcripción multilingüe con NVIDIA Canary 1B v2 (Gradio).
Sirve para un Hugging Face Space o para Google Colab.
Expone la API  /transcribe  que usa index.html.
"""
import os
import tempfile

import gradio as gr
import librosa
import soundfile as sf
import torch
from nemo.collections.asr.models import ASRModel

try:  # en ZeroGPU hace falta este decorador; en otros sitios no hace nada
    import spaces
    gpu = spaces.GPU(duration=120)
except ImportError:
    def gpu(fn):
        return fn

MODEL_NAME = "nvidia/canary-1b-v2"
SR = 16000
CHUNK_SECONDS = 30      # bloques de 30 s para mostrar el progreso
BATCH = 8               # bloques procesados a la vez
MAX_MINUTES = 120
LANGS = ["es", "en", "fr", "de", "it", "pt"]

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Cargando {MODEL_NAME} en {device} ...")
model = ASRModel.from_pretrained(MODEL_NAME).eval().to(device)
print("Modelo listo.")


def _run_batch(paths, lang):
    with torch.inference_mode():
        out = model.transcribe(paths, source_lang=lang, target_lang=lang,
                               batch_size=len(paths), verbose=False)
    return [(getattr(o, "text", o) or "").strip() for o in out]


@gpu
def transcribe(audio, lang="es"):
    if not audio:
        raise gr.Error("Sube o graba un audio primero.")
    if lang not in LANGS:
        raise gr.Error(f"Idioma no válido: {lang}")

    wav, _ = librosa.load(audio, sr=SR, mono=True)
    if len(wav) / SR > MAX_MINUTES * 60:
        raise gr.Error(f"El audio supera {MAX_MINUTES} minutos.")

    n = CHUNK_SECONDS * SR
    pieces = [wav[i:i + n] for i in range(0, len(wav), n)]
    pieces = [p for p in pieces if len(p) > 0.3 * SR] or pieces[:1]

    segments = []
    with tempfile.TemporaryDirectory() as tmp:
        paths = []
        for k, piece in enumerate(pieces):
            path = os.path.join(tmp, f"{k:04d}.wav")
            sf.write(path, piece, SR)
            paths.append(path)

        for b in range(0, len(paths), BATCH):
            texts = _run_batch(paths[b:b + BATCH], lang)
            for j, text in enumerate(texts):
                segments.append({"start": (b + j) * CHUNK_SECONDS, "text": text})
            yield {"done": len(segments), "total": len(paths), "segments": list(segments)}


demo = gr.Interface(
    fn=transcribe,
    inputs=[
        gr.Audio(type="filepath", label="Audio"),
        gr.Dropdown(LANGS, value="es", label="Idioma del audio"),
    ],
    outputs=gr.JSON(label="Transcripción"),
    api_name="transcribe",
    title="Canary 1B v2 · Transcriptor multilingüe",
    flagging_mode="never",
)

if __name__ == "__main__":
    demo.queue().launch(share=True)  # share=True crea un enlace público (útil en Colab)
