#!/usr/bin/env python3
"""
outline.py — Tanam outline badan bercahaya (putih + glow emas #E8C27A) ke klip shorts, berdenyut mengikuti ketukan.

Pemakaian:
  python3 editor/outline.py --clip studio/public/shorts/s05.mp4 --track tracks/shorts/s05.json \
      --mode drop|fast|pulse|soft --beats 0,15,30,45 [--out sama-dengan-clip]
  --beats : ketukan dalam FRAME lokal klip (0 = frame pertama klip).
Masker dibaca dari folder `masksDir` di JSON track (dibuat `track.py --seg --masks DIR`).
Salinan asli disimpan sebagai <clip>.orig.mp4 (sekali saja), jadi bisa diulang dengan mode lain.
Hemat CPU HP: ring & glow dihitung di 1/2 resolusi dan di-cache per masker.
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys

import numpy as np

GOLD = np.array([122, 194, 232], np.float32)  # #E8C27A dalam BGR
WHITE = np.array([255, 255, 255], np.float32)


def intensity(mode, a, beat_idx):
    if mode == "drop":
        return 0.35 + 0.65 * math.exp(-a / 5)
    if mode == "fast":
        return 0.95 * math.exp(-a / 4)
    if mode == "pulse":
        return (0.85 * math.exp(-a / 6)) if beat_idx % 2 == 0 else 0.25 * math.exp(-a / 6)
    return 0.45  # soft (outro)


def main():
    import cv2
    ap = argparse.ArgumentParser()
    ap.add_argument("--clip", required=True)
    ap.add_argument("--track", required=True)
    ap.add_argument("--mode", default="pulse", choices=["drop", "fast", "pulse", "soft"])
    ap.add_argument("--beats", default="")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--out")
    a = ap.parse_args()

    tr = json.load(open(a.track))
    mdir = tr.get("masksDir")
    if not mdir or not os.path.isdir(mdir):
        sys.exit("[ERROR] track tidak punya masker. Jalankan track.py dengan --seg --masks DIR")
    samples = [s for s in tr["samples"] if s.get("mask")]
    if not samples:
        sys.exit("[WARN] tidak ada masker badan terdeteksi; outline dilewati.")
    beats = sorted(int(x) for x in a.beats.split(",") if x.strip()) or [0]

    orig = a.clip.replace(".mp4", ".orig.mp4")
    if not os.path.exists(orig):
        shutil.copy2(a.clip, orig)
    out = a.out or a.clip
    W, H = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                    "stream=width,height", "-of", "csv=p=0:s=x", orig],
                                   capture_output=True, text=True).stdout.strip().split("x"))
    w2, h2 = W // 2, H // 2
    ell = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))  # setara ellipse15 di 1/1 resolusi
    cache = {}

    def layers(name):
        if name not in cache:
            m = cv2.imread(os.path.join(mdir, name), cv2.IMREAD_GRAYSCALE)
            m = cv2.GaussianBlur(cv2.resize(m, (w2, h2)).astype(np.float32) / 255, (0, 0), 1.5)
            b = (m > 0.5).astype(np.uint8)
            ring = (cv2.dilate(b, ell) - b).astype(np.float32)
            ring = cv2.GaussianBlur(ring, (0, 0), 0.8)
            glow = np.clip(cv2.GaussianBlur(ring, (0, 0), 9) * 2.2, 0, 1)
            cache[name] = (cv2.resize(ring, (W, H))[..., None], cv2.resize(glow, (W, H))[..., None])
            if len(cache) > 40:
                cache.pop(next(iter(cache)))
        return cache[name]

    times = np.array([s["t"] for s in samples])
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", orig, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                            "-r", str(a.fps), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17",
                            "-pix_fmt", "yuv420p", out + ".tmp.mp4"], stdin=subprocess.PIPE)
    size = W * H * 3
    i = 0
    while True:
        buf = dec.stdout.read(size)
        if len(buf) < size:
            break
        f = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32)
        t = i / a.fps
        k = int(np.argmin(np.abs(times - t)))
        if abs(times[k] - t) < 0.5:
            last = max([b for b in beats if b <= i], default=beats[0])
            I = intensity(a.mode, i - last if i >= last else 99, beats.index(last))
            ring, glow = layers(samples[k]["mask"])
            f = f + ring * I * (WHITE - f) * 0.95
            f = 255 - (255 - f) * (1 - np.clip(glow * I * 0.55, 0, 1) * GOLD / 255)
        enc.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes())
        i += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    os.replace(out + ".tmp.mp4", out)
    print(f"OK outline ({a.mode}) {i} frame -> {out}")


if __name__ == "__main__":
    main()
