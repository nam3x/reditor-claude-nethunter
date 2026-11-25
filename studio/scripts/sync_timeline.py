#!/usr/bin/env python3
"""
sync_timeline.py — Menyusun timeline Remotion dari manifest.json (+ transkrip WhisperX opsional).

Perbaikan utama dibanding versi awal:
- Durasi adegan dihitung dari FRASA JANGKAR (anchor) yang dicocokkan ke transkrip,
  bukan diketik manual. Adegan berakhir tepat saat adegan berikutnya mulai bicara.
- Tanpa transkrip: durasi diperkirakan dari jumlah kata captionText (kecepatan bicara).
- Mencatat audioPath + audioStartFrame per adegan, sehingga komposisi Highlight
  bisa memotong voiceover yang tepat untuk tiap adegan.
- Timeline back-to-back tanpa tumpang tindih transisi, sehingga takarir tidak bergeser.

Pemakaian (jalankan dari root proyek):
  python3 scripts/sync_timeline.py --manifest manifest.json --transcript transcript.json
  python3 scripts/sync_timeline.py --manifest manifest.json            # tanpa audio/transkrip
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

WORDS_PER_SEC = 2.9      # target tempo bicara (sedang-cepat) saat tanpa transkrip
MIN_SCENE_SEC = 2.0
TAIL_PAD_SEC = 0.6       # jeda setelah kata terakhir sebelum video selesai
ANCHOR_WORDS = 3         # panjang anchor default (diambil dari awal captionText)
ANCHOR_WINDOW = 25       # jangkauan fallback kata pertama anchor (kata) agar adegan tidak meloncat jauh


def norm(token: str) -> str:
    return re.sub(r"[^\w]", "", token.lower(), flags=re.UNICODE)


def tokens_of(text: str):
    return [t for t in (norm(x) for x in (text or "").split()) if t]


def audio_duration_sec(path):
    if not path or not shutil.which("ffprobe") or not os.path.exists(path):
        return None
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return float(out)
    except Exception:
        return None


def load_words(path):
    if not path:
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[WARN] Transkrip {path} tidak ditemukan, memakai perkiraan durasi.", file=sys.stderr)
        return []
    words = []
    source = data.get("word_segments") or [w for s in data.get("segments", []) for w in s.get("words", [])]
    for w in source:
        if w.get("start") is None or w.get("end") is None:
            continue  # WhisperX kadang tidak memberi waktu untuk angka/simbol
        token = w["word"].strip()
        # Whisper memecah kata ulang: "Tiba" + "-tiba" -> gabungkan jadi "Tiba-tiba"
        if token.startswith("-") and words:
            prev = words[-1]; prev["word"] += token; prev["norm"] = norm(prev["word"]); prev["end"] = float(w["end"])
            continue
        words.append({"word": token, "norm": norm(token),
                      "start": float(w["start"]), "end": float(w["end"])})
    return words


def find_anchor(words, anchor_tokens, from_idx):
    """Cari urutan anchor_tokens di words mulai from_idx. Kembalikan index kata pertama atau None."""
    n = len(anchor_tokens)
    if n == 0:
        return None
    for i in range(from_idx, len(words) - n + 1):
        if all(words[i + k]["norm"] == anchor_tokens[k] for k in range(n)):
            return i
    # fallback: kata pertama anchor saja, tapi hanya di dekat posisi terakhir (maks 25 kata ke depan)
    for i in range(from_idx, min(len(words), from_idx + ANCHOR_WINDOW)):
        if words[i]["norm"] == anchor_tokens[0]:
            print(f"[WARN] anchor '{' '.join(anchor_tokens)}' hanya cocok sebagian (kata pertama) di kata ke-{i}; "
                  f"periksa ejaan anchor.", file=sys.stderr)
            return i
    return None


def estimate_sec(scene):
    n = len(tokens_of(scene.get("captionText") or scene.get("subtext") or scene.get("headline", "")))
    return max(MIN_SCENE_SEC, n / WORDS_PER_SEC + 0.8)


def even_word_timings(scene, dur):
    raw = (scene.get("captionText") or scene.get("subtext") or scene.get("headline", "")).split()
    if not raw:
        return []
    usable = max(1, dur - 8)
    step = usable / len(raw)
    out = []
    for i, tok in enumerate(raw):
        s = round(i * step)
        out.append({"word": tok, "startFrame": s, "endFrame": max(s + 1, round((i + 1) * step))})
    return out


def main():
    p = argparse.ArgumentParser(description="Sinkronisasi manifest -> timeline.generated.json")
    p.add_argument("--manifest", required=True)
    p.add_argument("--transcript", help="JSON WhisperX (segments[].words[] atau word_segments[])")
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--out", default="src/timeline.generated.json")
    args = p.parse_args()

    with open(args.manifest, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    fps = manifest.get("fps", args.fps)
    scenes = manifest.get("scenes", [])
    audio_path = manifest.get("audioPath")  # relatif terhadap public/, mis. "audio/voiceover.mp3"
    words = load_words(args.transcript)

    # ---- 1. Tentukan detik mulai tiap adegan ----
    starts = []
    if words:
        cursor = 0
        for i, sc in enumerate(scenes):
            if i == 0:
                starts.append(0.0)  # adegan pertama selalu mulai di frame 0 (hook tanpa layar kosong)
                continue
            anchor = tokens_of(sc.get("anchor") or " ".join((sc.get("captionText") or "").split()[:ANCHOR_WORDS]))
            idx = find_anchor(words, anchor, cursor)
            if idx is None:
                print(f"[WARN] Anchor adegan '{sc.get('id')}' tidak ditemukan di transkrip; "
                      f"memakai perkiraan dari jumlah kata.", file=sys.stderr)
                starts.append(starts[-1] + estimate_sec(scenes[i - 1]))
            else:
                # mulai sedikit sebelum kata pertama agar visual mendahului suara
                starts.append(max(starts[-1] + MIN_SCENE_SEC / 2, words[idx]["start"] - 0.15))
                cursor = idx + 1
        speech_end = words[-1]["end"] + TAIL_PAD_SEC
        a_dur = audio_duration_sec(os.path.join("public", audio_path)) if audio_path else None
        total_sec = max(speech_end, a_dur or 0, starts[-1] + MIN_SCENE_SEC)
    else:
        t = 0.0
        for sc in scenes:
            starts.append(t)
            override = sc.get("durationInFrames")
            t += (override / fps) if override else estimate_sec(sc)
        total_sec = t

    # ---- 2. Konversi ke frame (satu kali pembulatan, tanpa celah/tumpang tindih) ----
    start_frames = [round(s * fps) for s in starts] + [round(total_sec * fps)]

    full, highlight, hl_cursor = [], [], 0
    for i, sc in enumerate(scenes):
        sf, ef = start_frames[i], start_frames[i + 1]
        dur = max(1, ef - sf)
        if words:
            s_sec, e_sec = sf / fps, ef / fps
            wt = [{"word": w["word"],
                   "startFrame": max(0, round((w["start"] - s_sec) * fps)),
                   "endFrame": min(dur, max(1, round((w["end"] - s_sec) * fps)))}
                  for w in words if s_sec <= w["start"] < e_sec]
        else:
            wt = even_word_timings(sc, dur)

        entry = {**sc, "startFrame": sf, "durationInFrames": dur,
                 "audioStartFrame": sf, "wordTimings": wt}
        entry.pop("anchor", None)
        full.append(entry)
        if sc.get("highlight"):
            highlight.append({**entry, "startFrame": hl_cursor})
            hl_cursor += dur

    audio_ok = bool(audio_path) and os.path.exists(os.path.join("public", audio_path))
    if audio_path and not audio_ok:
        print(f"[WARN] public/{audio_path} belum ada; video dirender tanpa suara.", file=sys.stderr)

    out = {
        "projectTitle": manifest.get("projectTitle", "Untitled"),
        "fps": fps,
        "audioPath": audio_path if audio_ok else None,
        "fullDurationInFrames": start_frames[-1],
        "highlightDurationInFrames": hl_cursor,
        "fullScenes": full,
        "highlightScenes": highlight,
        # reditor: diteruskan apa adanya dari manifest
        "sources": manifest.get("sources", []),
        "disclaimer": manifest.get("disclaimer"),
        "musicPath": manifest.get("musicPath") if manifest.get("musicPath") and os.path.exists(os.path.join("public", manifest["musicPath"])) else None,
        "musicVolume": manifest.get("musicVolume", 0.08),
    }
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    src = "transkrip+anchor" if words else "perkiraan jumlah kata"
    print(f"OK ({src}): Full={len(full)} adegan, {start_frames[-1]} frame ({start_frames[-1]/fps:.1f}s) | "
          f"Highlight={len(highlight)} adegan, {hl_cursor} frame ({hl_cursor/fps:.1f}s)")


if __name__ == "__main__":
    main()
