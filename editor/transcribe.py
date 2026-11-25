#!/usr/bin/env python3
"""
transcribe.py — VO -> transcript.json (format WhisperX: segments[].words[] dengan start/end per kata).
Offline setelah model terunduh sekali. Ramah arm64 (faster-whisper / CTranslate2 punya wheel aarch64).

Pemakaian:
  python3 editor/transcribe.py VO/voiceover.mp3 [--model small] [--lang id] [--out transcript.json]
Model: tiny (paling cepat) | base | small (disarankan HP 6–8 GB) | medium (lambat di HP).
Audio VO TIDAK diubah: dibaca saja (didekode ke 16 kHz di memori untuk Whisper).
"""
import argparse
import json
import shutil
import subprocess
import sys


def decode_16k(path):
    """Dekode lewat ffmpeg ke float32 mono 16 kHz (menghindari masalah av/PyAV di chroot)."""
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("audio")
    p.add_argument("--model", default="small")
    p.add_argument("--lang", default="id")
    p.add_argument("--out", default="transcript.json")
    p.add_argument("--prompt", default=None, help="naskah/istilah agar ejaan lebih tepat (initial_prompt)")
    a = p.parse_args()
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("[ERROR] faster-whisper belum terpasang: pip install --break-system-packages faster-whisper")
    if not shutil.which("ffmpeg"):
        sys.exit("[ERROR] ffmpeg tidak ada")
    print(f"Memuat model '{a.model}' (int8, CPU)… unduhan pertama butuh internet (HuggingFace).")
    model = WhisperModel(a.model, device="cpu", compute_type="int8")
    audio = decode_16k(a.audio)
    segments, info = model.transcribe(audio, language=a.lang, word_timestamps=True, vad_filter=True,
                                      initial_prompt=a.prompt, beam_size=5)
    out = {"language": info.language, "segments": []}
    n = 0
    for s in segments:
        words = [{"word": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3),
                  "score": round(w.probability, 3)} for w in (s.words or [])]
        n += len(words)
        out["segments"].append({"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip(), "words": words})
        print(f"  [{s.start:6.2f}-{s.end:6.2f}] {s.text.strip()}")
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    if n and out["segments"]:
        first = out["segments"][0]["words"][0]["start"] if out["segments"][0]["words"] else 0
        last = out["segments"][-1]["end"]
        wps = n / max(0.1, last - first)
        print(f"OK: {a.out} — {n} kata, tempo {wps:.2f} kata/dtk "
              f"({'OK' if 2.6 <= wps <= 3.3 else 'di luar 2,6–3,2: laporkan ke pengguna, JANGAN ubah audio'})")


if __name__ == "__main__":
    main()
