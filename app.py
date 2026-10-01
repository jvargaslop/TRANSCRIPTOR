"""
Backend de transcripción con NVIDIA Canary-Qwen 2.5B (Gradio).
Sirve para un Hugging Face Space o para Google Colab.
Expone la API  /transcribe  que usa index.html.
"""
import os
import tempfile

import gradio as gr
import librosa
import soundfile as sf
import torch
from nemo.collections.speechlm2.models import SALM

try:  # en ZeroGPU hace falta este decorador; en otros sitios no hace nada
    import spaces
    gpu = spaces.GPU(duration=120)
except ImportError:
    def gpu(fn):
        return fn

SR = 16000
CHUNK_SECONDS = 30      # el modelo ve hasta ~40 s por bloque
BATCH = 8               # bloques procesados a la vez
MAX_MINUTES = 120
MAX_NEW_TOKENS = 384

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Cargando Canary-Qwen 2.5B en {device} ...")
model = SALM.from_pretrained("nvidia/canary-qwen-2.5b")
model = (model.bfloat16() if device == "cuda" else model).eval().to(device)
print("Modelo listo.")


def _run_batch(paths):
    prompts = [[{
        "role": "user",
        "content": f"Transcribe the following: {model.audio_locator_tag}",
        "audio": [p],
    }] for p in paths]
    with torch.inference_mode():
        ids = model.generate(prompts=prompts, max_new_tokens=MAX_NEW_TOKENS)
    return [model.tokenizer.ids_to_text(i.cpu()).strip() for i in ids]


@gpu
def transcribe(audio):
    if not audio:
        raise gr.Error("Sube o graba un audio primero.")

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
            texts = _run_batch(paths[b:b + BATCH])
            for j, text in enumerate(texts):
                segments.append({"start": (b + j) * CHUNK_SECONDS, "text": text})
            yield {"done": len(segments), "total": len(paths), "segments": list(segments)}


demo = gr.Interface(
    fn=transcribe,
    inputs=gr.Audio(type="filepath", label="Audio"),
    outputs=gr.JSON(label="Transcripción"),
    api_name="transcribe",
    title="Canary-Qwen 2.5B · Transcriptor (inglés)",
    flagging_mode="never",
)

if __name__ == "__main__":
    demo.queue().launch(share=True)  # share=True crea un enlace público (útil en Colab)
