#!/usr/bin/env python3
"""
reditor_edit.py — Editor video berbasis ffmpeg (tanpa browser), ringan untuk Kali NetHunter / arm64.

Membaca `edit.json` (EDL) lalu:
  1. Menormalkan tiap klip raw-footage (trim, crop ke 9:16/16:9, fps, LUT, Ken Burns/punch-in, VFX blend)
     menjadi file antara di .reditor-work/  (bisa dilanjutkan bila HP mati di tengah jalan).
  2. Menyambung klip dengan transisi xfade (fade, smoothleft, circleopen, zoomin, dll).
  3. Lapis akhir: grain + vignette + takarir karaoke (ASS, dari transcript.json) + teks judul per klip.
  4. Audio: VO apa adanya (tidak di-stretch/dipotong) + musik dengan ducking sidechain + SFX + audio asli klip,
     lalu loudnorm -14 LUFS.

Pemakaian (dari root proyek):
  python3 editor/reditor_edit.py auto   [--aspect 9:16] [--out edit.json]   # susun EDL otomatis dari raw-footage/
  python3 editor/reditor_edit.py render [--edit edit.json] [--preview]      # render (preview = 540p, cepat)
  python3 editor/reditor_edit.py check  [--edit edit.json]                  # validasi file & durasi saja

Semua path di edit.json relatif terhadap root proyek.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORK = os.path.join(ROOT, ".reditor-work")
VIDEO_EXT = (".mp4", ".mov", ".mkv", ".webm", ".m4v", ".avi", ".3gp")
IMAGE_EXT = (".jpg", ".jpeg", ".png", ".webp")
AUDIO_EXT = (".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac", ".opus")
XFADES = ["fade", "smoothleft", "smoothup", "circleopen", "fadeblack", "zoomin", "slideleft", "dissolve"]


# ----------------------------------------------------------------------------- util
def sh(cmd, quiet=True):
    if not quiet:
        print("  $", " ".join(cmd[:6]), "...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-3000:])
        raise SystemExit(f"[ERROR] perintah gagal: {' '.join(cmd[:4])} ...")
    return r.stdout


def probe_duration(path):
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                              "-of", "default=nw=1:nk=1", path], capture_output=True, text=True).stdout.strip()
        return float(out)
    except Exception:
        return 0.0


def has_audio(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip()
    return bool(out)


def P(rel):
    return rel if os.path.isabs(rel) else os.path.join(ROOT, rel)


def first_file(folder, exts):
    d = P(folder)
    if not os.path.isdir(d):
        return None
    files = sorted(f for f in os.listdir(d) if f.lower().endswith(exts) and not f.startswith("."))
    return os.path.join(folder, files[0]) if files else None


def dims(aspect, preview):
    w, h = (1080, 1920) if aspect == "9:16" else (1920, 1080)
    if preview:
        w, h = w // 2, h // 2
    return w, h


def esc_filter_path(p):
    # path di dalam filtergraph ffmpeg: escape \ : ' ,
    return p.replace("\\", "/").replace(":", r"\:").replace("'", r"\'").replace(",", r"\,")


def ass_time(t):
    t = max(0.0, t)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def ass_color(hex_rgb, alpha="00"):
    h = hex_rgb.lstrip("#")
    return f"&H{alpha}{h[4:6]}{h[2:4]}{h[0:2]}".upper()


# ----------------------------------------------------------------------------- auto EDL
def cmd_auto(a):
    raw = P("raw-footage")
    clips = sorted(f for f in os.listdir(raw) if f.lower().endswith(VIDEO_EXT + IMAGE_EXT) and not f.startswith(".")) \
        if os.path.isdir(raw) else []
    if not clips:
        sys.exit("[ERROR] raw-footage/ kosong. Salin klip video/foto ke folder itu dulu.")
    vo = first_file("VO", AUDIO_EXT)
    music = first_file("Musik", AUDIO_EXT)
    vo_dur = probe_duration(P(vo)) if vo else 0
    target = vo_dur or a.seconds
    per = max(1.5, target / len(clips))
    leaks = sorted(os.path.join("VFX/light-leaks", f) for f in os.listdir(P("VFX/light-leaks"))) \
        if os.path.isdir(P("VFX/light-leaks")) else []
    out_clips = []
    for i, f in enumerate(clips):
        src = os.path.join("raw-footage", f)
        is_img = f.lower().endswith(IMAGE_EXT)
        avail = 9999 if is_img else probe_duration(P(src))
        start = 0.0 if avail <= per else round(min(1.0, (avail - per) / 2), 2)
        c = {"src": src, "in": start, "duration": round(per, 2),
             "motion": "kenburns" if is_img or i % 2 == 0 else "punch"}
        if leaks and i % 3 == 1:
            c["vfx"] = [{"file": leaks[i % len(leaks)], "blend": "screen", "opacity": 0.45}]
        if i > 0:
            c["transition"] = {"type": XFADES[i % 4], "duration": 0.35}
        out_clips.append(c)
    edit = {
        "aspect": a.aspect, "fps": 30, "output": "out/edit_final.mp4",
        "lut": "VFX/luts/clean_bright.cube", "lutStrength": 0.8,
        "grain": {"file": "VFX/grain/grain_fine_01.mp4", "opacity": 0.12},
        "vignette": 0.35,
        "vo": vo, "transcript": "transcript.json" if os.path.exists(P("transcript.json")) else None,
        "captions": {"enabled": True, "font": "Inter", "size": 0, "color": "#FFFFFF", "highlight": "#F59E0B",
                     "maxChars": 22, "uppercase": False},
        "music": music, "musicGainDb": -20, "duck": True,
        "sfx": [],
        "clips": out_clips,
    }
    with open(P(a.out), "w", encoding="utf-8") as f:
        json.dump(edit, f, indent=2, ensure_ascii=False)
    print(f"OK: {a.out} ({len(out_clips)} klip, ±{per:.1f} dtk/klip, target {target:.1f} dtk"
          f"{' = durasi VO' if vo_dur else ''}). Edit manual bila perlu, lalu: reditor edit render")


# ----------------------------------------------------------------------------- render klip
def clip_filter(c, w, h, fps, edit, dur):
    motion = c.get("motion", "none")
    f = []
    # isi frame (cover) + crop ke rasio target; sedikit lebih besar untuk ruang gerak kamera
    over = 1.12 if motion in ("kenburns", "punch") else 1.0
    W2, H2 = int(w * over) // 2 * 2, int(h * over) // 2 * 2
    f.append(f"scale={W2}:{H2}:force_original_aspect_ratio=increase:flags=bicubic,crop={W2}:{H2}")
    f.append(f"fps={fps},setsar=1")
    n = max(1, int(round(dur * fps)))
    if motion == "kenburns":
        # zoom pelan 1.00 -> 1.10 di tengah (crop bergerak, lebih ringan dari zoompan)
        f.append(f"crop=w='{W2}/(1+0.10*min(n/{n},1))':h='{H2}/(1+0.10*min(n/{n},1))':"
                 f"x='(in_w-out_w)/2':y='(in_h-out_h)/2'")
    elif motion == "punch":
        # punch-in cepat di awal (ease-out) lalu tahan — terasa "editan modern"
        f.append(f"crop=w='{W2}/(1+0.08*(1-pow(1-min(n/{max(1, int(fps*0.5))},1),3)))':"
                 f"h='{H2}/(1+0.08*(1-pow(1-min(n/{max(1, int(fps*0.5))},1),3)))':x='(in_w-out_w)/2':y='(in_h-out_h)/2'")
    f.append(f"scale={w}:{h}:flags=bicubic")
    lut = c.get("lut", edit.get("lut"))
    if lut and os.path.exists(P(lut)):
        strength = float(c.get("lutStrength", edit.get("lutStrength", 1.0)))
        if strength >= 0.99:
            f.append(f"lut3d=file='{esc_filter_path(P(lut))}'")
        else:
            f.append(f"split[o][l];[l]lut3d=file='{esc_filter_path(P(lut))}'[g];[o][g]blend=all_expr='A*(1-{strength})+B*{strength}'")
    if c.get("speed"):
        f.append(f"setpts=PTS/{float(c['speed'])}")
    f.append("format=yuv420p")
    return ",".join(f)


def render_clip(i, c, edit, w, h, fps, preview):
    src = P(c["src"])
    if not os.path.exists(src):
        sys.exit(f"[ERROR] klip tidak ditemukan: {c['src']}")
    dur = float(c.get("duration", 3))
    tr_next = float(c.get("_tail", 0))
    total = dur + tr_next  # ekor untuk overlap xfade berikutnya
    key = hashlib.sha1(json.dumps([c, edit.get("lut"), edit.get("lutStrength"), w, h, fps, total],
                                  sort_keys=True).encode()).hexdigest()[:12]
    out = os.path.join(WORK, f"clip_{i:03d}_{key}.mp4")
    if os.path.exists(out) and probe_duration(out) > 0.1:
        print(f"  [cache] klip {i+1}: {c['src']}")
        return out
    is_img = c["src"].lower().endswith(IMAGE_EXT)
    speed = float(c.get("speed", 1.0))
    inp = (["-loop", "1", "-t", f"{total:.3f}", "-i", src] if is_img
           else ["-ss", f"{float(c.get('in', 0)):.3f}", "-t", f"{total*speed + 0.5:.3f}", "-i", src])
    vf = clip_filter(c, w, h, fps, edit, total)
    graph = f"[0:v]{vf}[base]"
    extra_in = []
    last = "base"
    for k, v in enumerate(c.get("vfx", [])):
        vp = P(v["file"])
        if not os.path.exists(vp):
            print(f"  [WARN] VFX tidak ada: {v['file']} (dilewati)")
            continue
        if vp.lower().endswith(IMAGE_EXT):
            extra_in += ["-loop", "1", "-t", f"{total:.3f}", "-i", vp]
        else:
            extra_in += ["-stream_loop", "-1", "-t", f"{total:.3f}", "-i", vp]
        idx = 1 + k
        mode = {"soft-light": "softlight"}.get(v.get("blend", "screen"), v.get("blend", "screen"))
        op = float(v.get("opacity", 0.6))
        graph += (f";[{idx}:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={fps},"
                  f"format=gbrp,setsar=1[fx{k}];[{last}]format=gbrp[b{k}];"
                  f"[b{k}][fx{k}]blend=all_mode={mode}:all_opacity={op}:shortest=1,format=yuv420p[v{k}]")
        last = f"v{k}"
    graph += f";[{last}]trim=duration={total:.3f},setpts=PTS-STARTPTS[vout]"
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *inp, *extra_in,
           "-filter_complex", graph, "-map", "[vout]", "-an",
           "-c:v", "libx264", "-preset", "ultrafast" if preview else "veryfast", "-crf", "18",
           "-pix_fmt", "yuv420p", "-r", str(fps), out]
    print(f"  klip {i+1}/{len(edit['clips'])}: {c['src']} ({total:.2f} dtk)")
    sh(cmd)
    return out


# ----------------------------------------------------------------------------- takarir ASS
def load_words(path):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    src = d.get("word_segments") or [w for s in d.get("segments", []) for w in s.get("words", [])]
    words = []
    for w in src:
        if w.get("start") is None or w.get("end") is None:
            continue
        t = w["word"].strip()
        if t.startswith("-") and words:
            words[-1]["word"] += t; words[-1]["end"] = float(w["end"]); continue
        words.append({"word": t, "start": float(w["start"]), "end": float(w["end"])})
    return words


def build_ass(edit, w, h, starts, total):
    cap = edit.get("captions") or {}
    vertical = h > w
    scale = h / (1920 if vertical else 1080)
    size = int(cap.get("size") or (64 if vertical else 56)) * scale
    font = cap.get("font", "Inter")
    margin_v = int((0.26 * h) if vertical else 0.07 * h)  # selaras dengan studio (di atas chip sumber)
    col, hi = cap.get("color", "#FFFFFF"), cap.get("highlight", "#F59E0B")
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {w}", f"PlayResY: {h}", "WrapStyle: 2", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
        "MarginR, MarginV, Encoding",
        # karaoke \kf: Secondary (belum diucapkan) -> Primary (aktif/sudah)
        f"Style: Cap,{font},{size:.0f},{ass_color(hi)},{ass_color(col, '30')},&H96000000,&H64000000,-1,0,0,0,100,100,0,0,1,"
        f"{max(2, 4*scale):.1f},{max(1, 2*scale):.1f},2,60,60,{margin_v},1",
        f"Style: Head,{font},{(96 if vertical else 104)*scale:.0f},&H00FFFFFF,&H00FFFFFF,&H64000000,&H50000000,-1,0,0,0,"
        f"100,100,-1,0,1,0,{3*scale:.1f},5,80,80,0,1",
        f"Style: Sub,{font},{44*scale:.0f},&H00E2E8F0,&H00E2E8F0,&H64000000,&H50000000,0,0,0,0,100,100,0,0,1,0,"
        f"{2*scale:.1f},5,80,80,0,1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    # judul/subjudul per klip (tipografi kinetik ringan: fade + naik)
    cy = int(h * (0.36 if vertical else 0.45))
    for c, st in zip(edit["clips"], starts):
        dur = float(c.get("duration", 3))
        if c.get("headline"):
            lines.append(f"Dialogue: 2,{ass_time(st+0.05)},{ass_time(st+dur-0.1)},Head,,0,0,0,,"
                         f"{{\\fad(180,150)\\move({w//2},{cy+int(40*scale)},{w//2},{cy},0,260)}}{c['headline']}")
        if c.get("subtext"):
            lines.append(f"Dialogue: 2,{ass_time(st+0.2)},{ass_time(st+dur-0.1)},Sub,,0,0,0,,"
                         f"{{\\fad(200,150)\\pos({w//2},{cy+int(120*scale)})}}{c['subtext']}")
    tr = edit.get("transcript")
    if cap.get("enabled", True) and tr and os.path.exists(P(tr)):
        words = load_words(P(tr))
        maxc = int(cap.get("maxChars", 22))
        groups, cur, ln = [], [], 0
        for wd in words:
            add = len(wd["word"]) + (1 if cur else 0)
            if cur and (ln + add > int(maxc * 1.6) or wd["start"] - cur[-1]["end"] > 0.7):
                groups.append(cur); cur, ln = [], 0
            cur.append(wd); ln += add
            if wd["word"].endswith((".", "!", "?")):
                groups.append(cur); cur, ln = [], 0
        if cur:
            groups.append(cur)
        for gi, g in enumerate(groups):
            start = g[0]["start"] - 0.05
            end = groups[gi + 1][0]["start"] - 0.05 if gi + 1 < len(groups) else min(total, g[-1]["end"] + 0.6)
            end = max(end, g[-1]["end"]) if gi + 1 >= len(groups) else end
            parts, t, chars = [], start, 0
            for k, wd in enumerate(g):
                gap = max(0, wd["start"] - t)
                if gap > 0.01:
                    parts.append(f"{{\\k{int(round(gap*100))}}}")
                txt = wd["word"].upper() if cap.get("uppercase") else wd["word"]
                if k and chars + len(txt) + 1 > maxc:  # pindah baris berdasarkan jumlah karakter
                    parts.append("\\N"); chars = 0
                elif k:
                    parts.append(" ")
                parts.append(f"{{\\kf{max(1, int(round((wd['end']-wd['start'])*100)))}}}{txt}")
                chars += len(txt) + 1
                t = wd["end"]
            lines.append(f"Dialogue: 1,{ass_time(start)},{ass_time(end)},Cap,,0,0,0,,{{\\fad(80,60)}}" + "".join(parts))
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, "captions.ass")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


# ----------------------------------------------------------------------------- render utama
def plan(edit):
    clips = edit["clips"]
    # ekor klip i = durasi transisi klip i+1 (agar xfade tidak memendekkan timeline)
    for i, c in enumerate(clips):
        nxt = clips[i + 1].get("transition") if i + 1 < len(clips) else None
        c["_tail"] = float(nxt.get("duration", 0.35)) if nxt and nxt.get("type", "cut") != "cut" else 0.0
    starts, t = [], 0.0
    for c in clips:
        starts.append(t); t += float(c.get("duration", 3))
    return starts, t


def cmd_check(a, quiet=False):
    edit = json.load(open(P(a.edit), encoding="utf-8"))
    errs = []
    for c in edit.get("clips", []):
        if not os.path.exists(P(c["src"])):
            errs.append(f"klip hilang: {c['src']}")
        for v in c.get("vfx", []):
            if not os.path.exists(P(v["file"])):
                errs.append(f"VFX hilang: {v['file']}")
    for k in ("vo", "music", "lut", "transcript"):
        if edit.get(k) and not os.path.exists(P(edit[k])):
            errs.append(f"{k} hilang: {edit[k]}")
    starts, total = plan(edit)
    vo_dur = probe_duration(P(edit["vo"])) if edit.get("vo") and os.path.exists(P(edit["vo"])) else 0
    if not quiet:
        print(f"Klip: {len(edit.get('clips', []))} | timeline klip: {total:.2f} dtk | VO: {vo_dur:.2f} dtk")
        if vo_dur and abs(vo_dur - total) > 0.3:
            print(f"[INFO] Timeline klip ≠ VO. Video mengikuti VO ({vo_dur:.2f} dtk): klip terakhir "
                  f"{'diperpanjang (freeze)' if total < vo_dur else 'dipotong'}; VO tidak diubah.")
        for e in errs:
            print("[ERROR]", e)
        print("OK" if not errs else f"{len(errs)} masalah.")
    return edit, errs


def cmd_render(a):
    edit, errs = cmd_check(a, quiet=False)
    if errs:
        sys.exit(1)
    if not shutil.which("ffmpeg"):
        sys.exit("[ERROR] ffmpeg tidak ada. Jalankan: reditor setup")
    os.makedirs(WORK, exist_ok=True)
    w, h = dims(edit.get("aspect", "9:16"), a.preview)
    fps = int(edit.get("fps", 30))
    starts, total = plan(edit)
    vo = P(edit["vo"]) if edit.get("vo") else None
    vo_dur = probe_duration(vo) if vo else 0
    final_dur = vo_dur + float(edit.get("tailPad", 0.3)) if vo_dur else total

    print(f"[1/3] Menormalkan {len(edit['clips'])} klip -> {w}x{h} @{fps}")
    files = [render_clip(i, c, edit, w, h, fps, a.preview) for i, c in enumerate(edit["clips"])]

    print("[2/3] Menyambung + transisi + takarir + grain/vignette")
    inputs, graph, last = [], [], None
    for i, fpath in enumerate(files):
        inputs += ["-i", fpath]
    acc = float(edit["clips"][0].get("duration", 3))
    last = "0:v"
    for i in range(1, len(files)):
        c = edit["clips"][i]
        tr = c.get("transition") or {}
        typ = tr.get("type", "cut")
        if typ == "cut":
            graph.append(f"[{last}][{i}:v]concat=n=2:v=1:a=0[x{i}]")
        else:
            d = float(tr.get("duration", 0.35))
            graph.append(f"[{last}][{i}:v]xfade=transition={typ}:duration={d}:offset={acc:.3f}[x{i}]")
        # setelah xfade, panjang = acc + durasi klip i + ekor klip i
        acc += float(c.get("duration", 3))
        last = f"x{i}"
    vlab = last
    n_in = len(files)
    # perpanjang / potong ke durasi akhir (VO menentukan)
    graph.append(f"[{vlab}]tpad=stop_mode=clone:stop_duration={max(0, final_dur - total) + 1:.3f},"
                 f"trim=duration={final_dur:.3f},setpts=PTS-STARTPTS[vt]")
    vlab = "vt"
    g = edit.get("grain")
    if g and os.path.exists(P(g["file"])):
        inputs += ["-stream_loop", "-1", "-i", P(g["file"])]
        graph.append(f"[{n_in}:v]scale={w}:{h},fps={fps},format=gbrp,setsar=1[gr];[{vlab}]format=gbrp[vg];"
                     f"[vg][gr]blend=all_mode=overlay:all_opacity={float(g.get('opacity', 0.12))}:shortest=1,format=yuv420p[vgr]")
        vlab = "vgr"; n_in += 1
    vig = float(edit.get("vignette", 0))
    if vig > 0:
        graph.append(f"[{vlab}]vignette=angle={0.35 + vig*0.5:.3f}:mode=forward[vv]")
        vlab = "vv"
    ass = build_ass(edit, w, h, starts, final_dur)
    fontsdir = P("studio/public/fonts") if os.path.isdir(P("studio/public/fonts")) else None
    sub = f"subtitles='{esc_filter_path(ass)}'" + (f":fontsdir='{esc_filter_path(fontsdir)}'" if fontsdir else "")
    graph.append(f"[{vlab}]{sub},format=yuv420p[vout]")

    # ---- audio
    print("[3/3] Mix audio (VO apa adanya, musik di-duck, SFX) + loudnorm -14 LUFS")
    a_parts, a_labels = [], []
    if vo:
        inputs += ["-i", vo]; vo_idx = n_in; n_in += 1
        a_parts.append(f"[{vo_idx}:a]aresample=48000,aformat=channel_layouts=stereo,asplit=2[vo][vosc]")
        a_labels.append("[vo]")
    if edit.get("music") and os.path.exists(P(edit["music"])):
        inputs += ["-stream_loop", "-1", "-i", P(edit["music"])]; m_idx = n_in; n_in += 1
        gain = float(edit.get("musicGainDb", -20))
        fade_out = max(0, final_dur - 1.0)
        a_parts.append(f"[{m_idx}:a]aresample=48000,aformat=channel_layouts=stereo,volume={gain}dB,"
                       f"atrim=duration={final_dur:.3f},afade=t=in:d=0.8,afade=t=out:st={fade_out:.3f}:d=1[mus]")
        if vo and edit.get("duck", True):
            a_parts.append("[mus][vosc]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=450:makeup=1[musd]")
            a_labels.append("[musd]")
        else:
            a_labels.append("[mus]")
            if vo:
                a_parts.append("[vosc]anullsink")
    elif vo:
        a_parts.append("[vosc]anullsink")
    for k, s in enumerate(edit.get("sfx", [])):
        if not os.path.exists(P(s["file"])):
            continue
        inputs += ["-i", P(s["file"])]; idx = n_in; n_in += 1
        ms = int(float(s.get("at", 0)) * 1000)
        a_parts.append(f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,volume={float(s.get('gainDb', -12))}dB,"
                       f"adelay={ms}|{ms}[sfx{k}]")
        a_labels.append(f"[sfx{k}]")
    for i, c in enumerate(edit["clips"]):  # audio asli klip (ambience), opsional
        if c.get("audioGainDb") is None or c["src"].lower().endswith(IMAGE_EXT) or not has_audio(P(c["src"])):
            continue
        inputs += ["-ss", f"{float(c.get('in', 0)):.3f}", "-t", f"{float(c.get('duration', 3)):.3f}", "-i", P(c["src"])]
        idx = n_in; n_in += 1
        ms = int(starts[i] * 1000)
        a_parts.append(f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,volume={float(c['audioGainDb'])}dB,"
                       f"afade=t=in:d=0.1,adelay={ms}|{ms}[ca{i}]")
        a_labels.append(f"[ca{i}]")
    if a_labels:
        a_parts.append(f"{''.join(a_labels)}amix=inputs={len(a_labels)}:duration=longest:normalize=0,"
                       f"atrim=duration={final_dur:.3f},loudnorm=I=-14:TP=-1:LRA=11[aout]")
    full_graph = ";".join(graph + a_parts)
    out = P(edit.get("output", "out/edit_final.mp4"))
    if a.preview:
        out = out.replace(".mp4", "_preview.mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-stats", "-y", *inputs,
           "-filter_complex", full_graph, "-map", "[vout]"]
    if a_labels:
        cmd += ["-map", "[aout]", "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
    cmd += ["-c:v", "libx264", "-preset", "ultrafast" if a.preview else edit.get("preset", "medium"),
            "-crf", str(edit.get("crf", 20)), "-pix_fmt", "yuv420p", "-r", str(fps),
            "-movflags", "+faststart", "-t", f"{final_dur:.3f}", out]
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit("[ERROR] render gagal (lihat pesan ffmpeg di atas).")
    print(f"\nSelesai: {os.path.relpath(out, ROOT)} ({probe_duration(out):.2f} dtk, target {final_dur:.2f} dtk)")


def main():
    p = argparse.ArgumentParser(description="reditor — editor ffmpeg untuk NetHunter")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("auto"); s.add_argument("--aspect", default="9:16", choices=["9:16", "16:9"])
    s.add_argument("--out", default="edit.json"); s.add_argument("--seconds", type=float, default=30)
    s = sub.add_parser("render"); s.add_argument("--edit", default="edit.json"); s.add_argument("--preview", action="store_true")
    s = sub.add_parser("check"); s.add_argument("--edit", default="edit.json")
    a = p.parse_args()
    {"auto": cmd_auto, "render": cmd_render, "check": cmd_check}[a.cmd](a)


if __name__ == "__main__":
    main()
