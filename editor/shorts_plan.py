#!/usr/bin/env python3
"""
shorts_plan.py — Alur "video-editor-shorts" (Cetakinds) untuk NetHunter: footage + musik -> Shorts 9:16 sinkron beat.

  python3 editor/shorts_plan.py analyze            # grid analisis footage + beats.json musik -> analisis/
  python3 editor/shorts_plan.py init [--seconds 30] # draf plan.json (rentang lagu dgn drop di dtk ~12–20, shot per bagian)
  python3 editor/shorts_plan.py sheet              # contact sheet frame tengah tiap shot + kotak crop (cek cx)
  python3 editor/shorts_plan.py build [--no-track] [--no-outline]
        -> potong klip 3:4 (1080x1440) ke studio/public/shorts/, lacak wajah/badan, tanam outline,
           mastering musik, tulis studio/src/shorts.data.json + studio/src/track.json
  Lalu render: bash studio/scripts/render_chunks.sh ShortsBeat   (per potongan, aman RAM HP)

plan.json:
{ "music": "Musik/lagu.mp3", "musicStart": 41.2, "title": "Judul", "artist": "Artis", "vo": null,
  "shots": [ {"src": "raw-footage/a.mp4", "srcStart": 12.3, "beats": 8, "cx": 0.5, "cy": 0.45,
              "section": "intro|drop|main|fast|outro", "speed": 1.0, "motion": "push|pull|pan|tilt",
              "effect": null|"hearts"|"sparkle"|"halo"|"rings"|"burst"|"arcs", "outline": false} ] }
"""
import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
FPS = 30
TAIL = 12  # frame ekor untuk crossfade
VIDEO_EXT = (".mp4", ".mov", ".mkv", ".webm", ".m4v", ".avi", ".3gp")
AUDIO_EXT = (".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac", ".opus")
PUB = os.path.join(ROOT, "studio", "public", "shorts")
SRC = os.path.join(ROOT, "studio", "src")
MOTIONS = ["push", "pan", "pull", "tilt"]


def P(rel):
    return rel if os.path.isabs(rel) else os.path.join(ROOT, rel)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-2000:])
        sys.exit(f"[ERROR] gagal: {' '.join(cmd[:5])} ...")
    return r.stdout


def probe(path):
    from track import probe as _p
    return _p(path)


def first(folder, exts):
    d = P(folder)
    fs = sorted(f for f in os.listdir(d) if f.lower().endswith(exts) and not f.startswith(".")) if os.path.isdir(d) else []
    return os.path.join(folder, fs[0]) if fs else None


def load_beats(music, start=0.0):
    out = P("analisis/beats.json")
    if not os.path.exists(out) or json.load(open(out)).get("source") != P(music):
        os.makedirs(P("analisis"), exist_ok=True)
        run([sys.executable, os.path.join(ROOT, "editor", "beats.py"), P(music), "--out", out])
    return json.load(open(out))


# ----------------------------------------------------------------------------- analyze
def cmd_analyze(a):
    os.makedirs(P("analisis"), exist_ok=True)
    raw = P("raw-footage")
    vids = sorted(f for f in os.listdir(raw) if f.lower().endswith(VIDEO_EXT)) if os.path.isdir(raw) else []
    for v in vids:
        w, h, dur = probe(os.path.join(raw, v))
        step = max(1.0, dur / 25)  # 25 frame -> grid 5x5 dengan stempel waktu
        out = P(f"analisis/grid_{os.path.splitext(v)[0]}.jpg")
        run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(raw, v), "-vf",
             f"fps=1/{step:.3f},scale=200:-2,drawtext=text='%{{pts\\:hms}}':x=4:y=4:fontsize=16:fontcolor=yellow:box=1:boxcolor=black,"
             f"tile=5x5", "-frames:v", "1", out])
        # deteksi cut bawaan (dissolve sering lolos -> beri margin 0,3 dtk saat memilih jendela)
        sc = subprocess.run(["ffmpeg", "-v", "info", "-i", os.path.join(raw, v), "-vf",
                             "select='gt(scene,0.25)',showinfo", "-an", "-f", "null", "-"],
                            capture_output=True, text=True).stderr
        cuts = [round(float(l.split("pts_time:")[1].split()[0]), 2) for l in sc.splitlines() if "pts_time:" in l]
        print(f"{v}: {w}x{h} {dur:.1f}s  grid={os.path.relpath(out, ROOT)}  cut bawaan={cuts[:30]}")
    music = a.music or first("Musik", AUDIO_EXT)
    if music:
        b = load_beats(music)
        print(f"Musik {music}: {b['bpm']} BPM, {len(b['beats'])} beat, drop di {b['drops']}")
    else:
        print("[WARN] Musik/ kosong")


# ----------------------------------------------------------------------------- init
SECTIONS = [("intro", 8), ("drop", 8), ("main", 4), ("main", 4), ("fast", 2), ("fast", 2), ("fast", 2), ("fast", 2),
            ("main", 4), ("main", 4), ("outro", 8)]


def cmd_init(a):
    music = a.music or first("Musik", AUDIO_EXT)
    if not music:
        sys.exit("[ERROR] Musik/ kosong — mode shorts butuh musik.")
    b = load_beats(music)
    beats = b["beats"]
    if len(beats) < 16:
        sys.exit("[ERROR] beat terlalu sedikit")
    # rentang lagu kontinu: drop jatuh di detik ~15 video, mulai tepat di ketukan
    drop = (b["drops"] or [beats[min(len(beats) - 1, 32)]])[0]
    start_beat = max(0, min(range(len(beats)), key=lambda i: abs(beats[i] - (drop - 15))))
    music_start = beats[start_beat]
    period = 60 / b["bpm"]
    intro_beats = max(4, int(round((drop - music_start) / period)))
    raw = P("raw-footage")
    vids = sorted(f for f in os.listdir(raw) if f.lower().endswith(VIDEO_EXT)) if os.path.isdir(raw) else []
    if not vids:
        sys.exit("[ERROR] raw-footage/ kosong")
    cursor = {v: 0.5 for v in vids}
    shots, total, k = [], 0.0, 0
    intro = []
    while intro_beats > 0:  # intro panjang dipecah per 8 ketukan (1 shot = 8 beat)
        n = 8 if intro_beats >= 12 else intro_beats
        intro.append(("intro", n)); intro_beats -= n
    plan_secs = intro + SECTIONS[1:]
    while total < a.seconds:
        sec, n = plan_secs[min(k, len(plan_secs) - 1)] if k < len(plan_secs) else ("main", 4)
        if total + n * period >= a.seconds - 4 * period:  # sisa waktu -> tutup dengan outro
            sec, n = "outro", max(4, int(round((a.seconds - total) / period)))
        v = vids[k % len(vids)]
        _, _, dur = probe(os.path.join(raw, v))
        speed = 0.7 if sec == "outro" else 1.0
        need = n * period * speed + 0.5
        st = cursor[v] if cursor[v] + need < dur else 0.3
        cursor[v] = st + need + 0.3
        tr = P(f"tracks/{os.path.splitext(v)[0]}.json")
        cx = 0.5
        if os.path.exists(tr):  # cx dari lintasan kasar (track.py --all)
            ss = [s for s in json.load(open(tr))["samples"] if st <= s["t"] <= st + need]
            if ss:
                cx = round(sum(s["cx"] for s in ss) / len(ss), 3)
        effect = {"drop": "burst", "fast": None, "outro": "halo"}.get(sec)
        shots.append({"src": os.path.join("raw-footage", v), "srcStart": round(st, 2), "beats": n, "cx": cx, "cy": 0.45,
                      "section": sec, "speed": speed, "motion": MOTIONS[k % 4], "effect": effect,
                      "outline": sec in ("drop", "fast", "outro")})
        total += n * period
        k += 1
        if sec == "outro":
            break
    plan = {"music": music, "musicStart": round(music_start, 3), "title": a.title, "artist": a.artist,
            "vo": None, "shots": shots}
    json.dump(plan, open(P("plan.json"), "w"), indent=2, ensure_ascii=False)
    print(f"OK plan.json: {len(shots)} shot, ±{total:.1f} dtk, lagu mulai {music_start:.2f}s, drop di video "
          f"±{drop - music_start:.1f}s. Sesuaikan srcStart/cx/effect lalu: reditor shorts sheet")


# ----------------------------------------------------------------------------- timing
def timing(plan):
    b = load_beats(plan["music"])
    t0 = plan["musicStart"]
    rel = [t - t0 for t in b["beats"] if t >= t0 - 0.02]
    out, bi = [], 0
    for i, s in enumerate(plan["shots"]):
        if bi + s["beats"] >= len(rel):
            print(f"[WARN] lagu habis di shot {i}", file=sys.stderr)
            break
        sf, ef = round(rel[bi] * FPS), round(rel[bi + s["beats"]] * FPS)
        out.append({**s, "id": f"s{i:02d}", "startF": sf, "durF": ef - sf, "beatIdx": bi})
        bi += s["beats"]
    beatsF = [round(t * FPS) for t in rel[:bi + 1]]
    drops = [round((d - t0) * FPS) for d in b["drops"] if d >= t0]
    dropF = drops[0] if drops else (out[1]["startF"] if len(out) > 1 else 0)
    return out, beatsF, dropF, (out[-1]["startF"] + out[-1]["durF"]) if out else 0


def crop_box(w, h, cx, cy):
    """Crop 3:4 dari sumber. Lanskap: tinggi penuh; potret: lebar penuh."""
    if w / h >= 0.75:
        ch = h - h % 2; cw = int(ch * 3 / 4) // 2 * 2
        x = int(min(max(cx * w - cw / 2, 0), w - cw)); y = 0
    else:
        cw = w - w % 2; ch = int(cw * 4 / 3) // 2 * 2
        x = 0; y = int(min(max(cy * h - ch / 2, 0), h - ch))
    return cw, ch, x, y


def cmd_sheet(a):
    plan = json.load(open(P("plan.json")))
    shots, *_ = timing(plan)
    os.makedirs(P("analisis/sheet"), exist_ok=True)
    for s in shots:
        w, h, _ = probe(P(s["src"]))
        cw, ch, x, y = crop_box(w, h, s["cx"], s.get("cy", 0.45))
        mid = s["srcStart"] + s["durF"] / FPS * s.get("speed", 1) / 2
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{mid:.2f}", "-i", P(s["src"]), "-frames:v", "1", "-vf",
             f"drawbox=x={x}:y={y}:w={cw}:h={ch}:color=yellow@0.9:t=6,scale=360:-2,"
             f"drawtext=text='{s['id']} {s['section']}':x=6:y=6:fontsize=22:fontcolor=white:box=1:boxcolor=black",
             P(f"analisis/sheet/{s['id']}.jpg")])
    n = len(shots); cols = 4
    run(["ffmpeg", "-v", "error", "-y", "-pattern_type", "glob", "-i", P("analisis/sheet/s*.jpg"), "-vf",
         f"scale=360:-2,pad=360:640:(ow-iw)/2:(oh-ih)/2,tile={cols}x{(n + cols - 1) // cols}:padding=4",
         "-frames:v", "1", P("analisis/shots_sheet.jpg")])
    print("OK analisis/shots_sheet.jpg (kotak kuning = crop 3:4). Perbaiki cx di plan.json bila subjek terpotong.")


# ----------------------------------------------------------------------------- build
def cut_clip(s, out):
    w, h, dur = probe(P(s["src"]))
    need = s["srcStart"] + (s["durF"] + TAIL) / FPS * float(s.get("speed", 1.0))
    if need > dur + 0.05:
        print(f"  [WARN] {s['id']}: sumber {s['src']} hanya {dur:.2f}s, butuh sampai {need:.2f}s -> "
              f"frame akhir ditahan. Majukan srcStart atau kurangi beats.", file=sys.stderr)
    cw, ch, x, y = crop_box(w, h, s["cx"], s.get("cy", 0.45))
    sp = float(s.get("speed", 1.0))
    soft = "unsharp=5:5:0.5," if ch < 900 else ""  # sumber 480p: tajamkan sedikit
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s['srcStart']:.3f}", "-i", P(s["src"]), "-vf",
         f"setpts=PTS/{sp},fps={FPS},crop={cw}:{ch}:{x}:{y},scale=1080:1440:flags=lanczos,{soft}"
         f"eq=contrast=1.04:saturation=1.06:gamma=1.02,setsar=1,tpad=stop_mode=clone:stop={s['durF'] + TAIL}",
         "-frames:v", str(s["durF"] + TAIL), "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17",
         "-pix_fmt", "yuv420p", out])


def per_frame(track_json, n_frames):
    """Sampel track (fps rendah) -> anchor per frame [cx_px, cy_px, r_px] di kanvas 1080x1440."""
    ss = track_json["samples"]
    if not ss:
        return {"face": [[540, 560, 120]] * n_frames, "body": [[0, 0, 1080, 1440]] * n_frames}
    face, body = [], []
    j = 0
    for f in range(n_frames):
        t = f / FPS
        while j + 1 < len(ss) and ss[j + 1]["t"] <= t:
            j += 1
        s0 = ss[j]; s1 = ss[min(j + 1, len(ss) - 1)]
        u = 0 if s1["t"] == s0["t"] else min(1, max(0, (t - s0["t"]) / (s1["t"] - s0["t"])))
        lerp = lambda k: s0[k] * (1 - u) + s1[k] * u  # noqa: E731
        face.append([round(lerp("cx") * 1080, 1), round(lerp("cy") * 1440, 1), round(lerp("w") / 2 * 1080, 1)])
        bb = s0.get("body") or [0.2, 0.1, 0.8, 1.0]
        body.append([round(bb[0] * 1080), round(bb[1] * 1440), round(bb[2] * 1080), round(bb[3] * 1440)])
    return {"face": face, "body": body}


def master_audio(plan, total_s, out):
    t0, T = plan["musicStart"], total_s + 0.3
    vo = plan.get("vo")
    if vo and os.path.exists(P(vo)):  # dengan VO: musik di-duck, target -14 LUFS (VO apa adanya)
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(t0), "-t", f"{T:.3f}", "-i", P(plan["music"]), "-i", P(vo),
             "-filter_complex",
             "[0:a]volume=-16dB,aformat=channel_layouts=stereo[m];[1:a]aformat=channel_layouts=stereo,asplit[v][sc];"
             "[m][sc]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=450[md];"
             f"[v][md]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1:LRA=11,afade=t=out:st={max(0, T - 2):.2f}:d=2",
             "-ar", "48000", "-c:a", "aac", "-b:a", "256k", out])
        return
    f = ("highpass=f=30,bass=g=2.5:f=90:w=0.6,equalizer=f=3200:t=q:w=1:g=1.5,"
         "acompressor=threshold=-18dB:ratio=2.5:attack=15:release=120:makeup=2")
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(t0), "-i", P(plan["music"]), "-t", f"{T:.3f}", "-af",
         f"{f},loudnorm=I=-8.5:TP=-1.5:LRA=9,volume=2.2dB,alimiter=limit=0.84:attack=1:release=60:level=false,"
         f"afade=t=in:d=0.15,afade=t=out:st={max(0, T - 3):.2f}:d=3", "-ar", "48000", "-c:a", "aac", "-b:a", "256k", out])


def cmd_build(a):
    plan = json.load(open(P("plan.json")))
    shots, beatsF, dropF, totalF = timing(plan)
    os.makedirs(PUB, exist_ok=True)
    os.makedirs(P("tracks/shorts"), exist_ok=True)
    tracks = {}
    for s in shots:
        out = os.path.join(PUB, f"{s['id']}.mp4")
        print(f"[klip] {s['id']} {s['section']:5s} {s['beats']} beat  {s['src']} @{s['srcStart']}s")
        cut_clip(s, out)
        if (s.get("effect") or s.get("outline")) and not a.no_track:
            from track import track as do_track
            seg = bool(s.get("outline")) and not a.no_outline
            mdir = P(f"tracks/shorts/{s['id']}_masks") if seg else None
            tj = do_track(out, fps=15, out=P(f"tracks/shorts/{s['id']}.json"), seg=seg, masks_dir=mdir, scale_w=540)
            tracks[s["id"]] = {"fx": s.get("effect"), **per_frame(tj, s["durF"] + TAIL)}
            if seg and tj.get("samples") and any(x.get("mask") for x in tj["samples"]):
                local = [f - s["startF"] for f in beatsF if s["startF"] <= f < s["startF"] + s["durF"]]
                mode = {"drop": "drop", "fast": "fast", "outro": "soft"}.get(s["section"], "pulse")
                run([sys.executable, os.path.join(ROOT, "editor", "outline.py"), "--clip", out,
                     "--track", P(f"tracks/shorts/{s['id']}.json"), "--mode", mode,
                     "--beats", ",".join(map(str, local))])
    print("[audio] mastering musik")
    master_audio(plan, totalF / FPS, os.path.join(PUB, "audio_full.m4a"))
    data = {"fps": FPS, "totalF": totalF, "dropF": dropF, "beatsF": beatsF,
            "title": plan.get("title") or "", "artist": plan.get("artist") or "",
            "audio": "shorts/audio_full.m4a",
            "shots": [{k: s[k] for k in ("id", "startF", "durF", "section", "motion", "effect", "beatIdx")}
                      | {"file": f"shorts/{s['id']}.mp4"} for s in shots]}
    json.dump(data, open(os.path.join(SRC, "shorts.data.json"), "w"), indent=1)
    json.dump(tracks, open(os.path.join(SRC, "track.json"), "w"))
    print(f"OK: {len(shots)} shot, {totalF} frame ({totalF / FPS:.1f}s), drop di frame {dropF}. "
          f"Cek: reditor still ShortsBeat {dropF + 3}  lalu  bash studio/scripts/render_chunks.sh ShortsBeat")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("analyze"); s.add_argument("--music")
    s = sub.add_parser("init"); s.add_argument("--music"); s.add_argument("--seconds", type=float, default=30)
    s.add_argument("--title", default=""); s.add_argument("--artist", default="")
    sub.add_parser("sheet")
    s = sub.add_parser("build"); s.add_argument("--no-track", action="store_true"); s.add_argument("--no-outline", action="store_true")
    a = ap.parse_args()
    {"analyze": cmd_analyze, "init": cmd_init, "sheet": cmd_sheet, "build": cmd_build}[a.cmd](a)


if __name__ == "__main__":
    main()
