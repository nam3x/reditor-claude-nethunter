#!/usr/bin/env python3
"""
beats.py — Deteksi tempo, beat, downbeat & aksen dari musik (numpy murni; tanpa librosa/numba, ringan di arm64).

Pemakaian:
  python3 editor/beats.py Musik/lagu.mp3 [--out beats.json] [--start 0] [--duration 60]
Output beats.json:
  {"bpm": 124.1, "beats": [..dtk..], "downbeats": [..], "accents": [..], "drops": [..], "duration": 61.2}
  - beats     : setiap ketukan (dipakai untuk cut sinkron beat)
  - downbeats : ketukan 1 tiap bar (cut utama / ganti klip)
  - accents   : ketukan dengan energi onset tertinggi (±20% teratas) -> goyang kamera / punch / flash
  - drops     : lonjakan energi besar (bagian "drop"/chorus) -> impact, transisi besar
Algoritme: spectral flux -> autokorelasi (tempo) -> dynamic programming beat tracking (Ellis 2007).
"""
import argparse
import json
import subprocess
import sys

import numpy as np

SR = 22050
N_FFT = 2048
HOP = 512


def decode(path, start=0.0, duration=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start)]
    if duration:
        cmd += ["-t", str(duration)]
    cmd += ["-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def onset_envelope(y):
    # frame terpusat (seperti librosa center=True): frame t berpusat di t*HOP
    y = np.concatenate([np.zeros(N_FFT // 2, np.float32), y, np.zeros(N_FFT // 2, np.float32)])
    n = 1 + max(0, (len(y) - N_FFT) // HOP)
    if n < 8:
        sys.exit("[ERROR] audio terlalu pendek")
    win = np.hanning(N_FFT).astype(np.float32)
    idx = np.arange(N_FFT)[None, :] + HOP * np.arange(n)[:, None]
    frames = y[idx] * win
    mag = np.abs(np.fft.rfft(frames, axis=1))
    # 40 pita log-frekuensi (30 Hz–11 kHz) berbobot sama, agar hi-hat (noise lebar) tidak mengalahkan kick/snare
    freqs = np.fft.rfftfreq(N_FFT, 1 / SR)
    edges = np.geomspace(30, SR / 2, 41)
    bands = np.stack([mag[:, (freqs >= lo) & (freqs < hi)].mean(axis=1) if np.any((freqs >= lo) & (freqs < hi))
                      else np.zeros(n) for lo, hi in zip(edges[:-1], edges[1:])], axis=1)
    logm = np.log1p(100 * bands)
    flux = np.maximum(0, np.diff(logm, axis=0)).sum(axis=1)
    flux = np.concatenate([[0], flux])
    # buang tren lambat, normalisasi
    k = 16
    local = np.convolve(flux, np.ones(k) / k, mode="same")
    env = np.maximum(0, flux - local)
    env /= env.std() + 1e-9
    rms = np.sqrt((frames ** 2).mean(axis=1))
    return env, rms


def estimate_period(env, fps, bpm_min=70, bpm_max=180, prior=120):
    env0 = env - env.mean()
    ac = np.correlate(env0, env0, mode="full")[len(env0) - 1:]
    lags = np.arange(len(ac))
    bpm = 60 * fps / np.maximum(lags, 1)
    valid = (bpm >= bpm_min) & (bpm <= bpm_max)
    weight = np.exp(-0.5 * (np.log2(bpm / prior) / 0.9) ** 2)  # condong ke ±120 BPM
    score = np.where(valid, ac * weight, -np.inf)
    lag = int(np.argmax(score))
    # haluskan dengan interpolasi parabola
    if 1 <= lag < len(ac) - 1:
        a, b, c = ac[lag - 1], ac[lag], ac[lag + 1]
        den = a - 2 * b + c
        off = 0.5 * (a - c) / den if den != 0 else 0
        return lag + float(np.clip(off, -0.5, 0.5))
    return float(lag)


def track_beats(env, period, tightness=100.0):
    n = len(env)
    score = env.copy()
    back = -np.ones(n, dtype=int)
    p = period
    lo, hi = int(round(p / 2)), int(round(p * 2))
    for t in range(n):
        a, b = max(0, t - hi), t - lo
        if b <= a:
            continue
        prev = np.arange(a, b)
        pen = -tightness * (np.log((t - prev) / p)) ** 2
        cand = score[prev] + pen
        j = int(np.argmax(cand))
        if cand[j] > 0:
            score[t] += cand[j]
            back[t] = prev[j]
    # mulai dari skor maksimum di ujung (satu periode terakhir)
    tail = np.arange(max(0, n - int(p)), n)
    t = int(tail[np.argmax(score[tail])])
    beats = []
    while t >= 0:
        beats.append(t)
        t = back[t]
    return np.array(beats[::-1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--out", default="beats.json")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--duration", type=float, default=None)
    ap.add_argument("--bpm", type=float, default=None, help="paksa BPM jika deteksi meleset (mis. 2x/0.5x)")
    a = ap.parse_args()

    y = decode(a.audio, a.start, a.duration)
    env, rms = onset_envelope(y)
    fps = SR / HOP
    period = (60 * fps / a.bpm) if a.bpm else estimate_period(env, fps)
    bf = track_beats(env, period)
    times = bf * HOP / SR
    bpm = 60 * fps / period

    # downbeat: fase (0..3) yang jumlah onset-nya terbesar
    strengths = env[bf] if len(bf) else np.array([])
    phase = int(np.argmax([strengths[k::4].sum() for k in range(4)])) if len(bf) >= 8 else 0
    downs = times[phase::4]

    # aksen: 20% beat terkuat
    acc = times[strengths >= np.percentile(strengths, 80)] if len(bf) else np.array([])

    # drop: kenaikan RMS besar (rata-rata 2 dtk sesudah vs sebelum)
    w = int(2 * fps)
    drops = []
    if len(rms) > 2 * w:
        cs = np.concatenate([[0], np.cumsum(rms)])
        thr = np.percentile(rms, 60)
        cand = []
        for t in bf:
            if t - w < 0 or t + w >= len(rms):
                continue
            before = (cs[t] - cs[t - w]) / w
            after = (cs[t + w] - cs[t]) / w
            if after > thr:
                cand.append((t * HOP / SR, after / (before + 1e-9)))
        # ambil puncak rasio (> 1.8) dengan jarak minimal 6 dtk
        for tt, r in sorted(cand, key=lambda x: -x[1]):
            if r < 1.8:
                break
            if all(abs(tt - d) > 6 for d in drops):
                drops.append(tt)
        drops.sort()

    out = {
        "source": a.audio, "offset": a.start, "bpm": round(float(bpm), 2),
        "duration": round(len(y) / SR, 3),
        "beats": [round(float(t + a.start), 3) for t in times],
        "downbeats": [round(float(t + a.start), 3) for t in downs],
        "accents": [round(float(t + a.start), 3) for t in acc],
        "drops": [round(float(t + a.start), 3) for t in drops],
    }
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
    print(f"OK {a.out}: {out['bpm']} BPM, {len(out['beats'])} beat, {len(out['downbeats'])} downbeat, "
          f"{len(out['accents'])} aksen, {len(out['drops'])} drop")


if __name__ == "__main__":
    main()
