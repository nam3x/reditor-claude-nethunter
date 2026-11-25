#!/usr/bin/env python3
"""
track.py — Lacak wajah & badan di footage (CPU, ramah arm64) untuk motion control dan motion graphic yang menempel.

Detektor (otomatis memilih yang tersedia):
  * wajah : Haar `haarcascade_frontalface_alt2` (OpenCV 4.x; OpenCV 5 tidak punya Haar -> pakai opencv-python-headless<5
            atau apt python3-opencv), file XML juga dicari di editor/models/.
  * badan : segmentasi u2net_human_seg (ONNX, onnxruntime) bila editor/models/u2net_human_seg.onnx ada
            (`reditor models`), jika tidak -> HOG person detector OpenCV.

Pemakaian:
  python3 editor/track.py raw-footage/klip.mp4 [--fps 6] [--out tracks/klip.json]       # lintasan kasar (reframe, cx)
  python3 editor/track.py --all                                                          # semua video raw-footage/
  python3 editor/track.py studio/public/shorts/s03.mp4 --fps 15 --seg --masks DIR        # klip shorts: + masker badan PNG

Output JSON (ternormalisasi 0..1 terhadap frame video yang dilacak; t = detik):
  {"width":..,"height":..,"fps":..,"coverage":..,
   "samples":[{"t":..,"found":true,"cx":..,"cy":..,"w":..,"h":..,           # subjek utama (wajah, atau kepala dari badan)
               "face":[cx,cy,r]|null,"body":[x0,y0,x1,y1]|null,"mask":"m_0003.png"|null}]}
"""
import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODELS = os.path.join(ROOT, "editor", "models")
VIDEO_EXT = (".mp4", ".mov", ".mkv", ".webm", ".m4v", ".avi", ".3gp")


def need_cv2():
    try:
        import cv2  # noqa: F401
        import numpy  # noqa: F401
    except ImportError:
        sys.exit("[ERROR] OpenCV belum ada: apt install python3-opencv  (atau pip install --break-system-packages 'opencv-python-headless<5')")


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height:stream_side_data=rotation:format=duration", "-of", "json", path],
                         capture_output=True, text=True).stdout
    d = json.loads(out or "{}")
    st = (d.get("streams") or [{}])[0]
    w, h = int(st.get("width", 0)), int(st.get("height", 0))
    for sd in st.get("side_data_list", []) or []:
        if abs(int(sd.get("rotation", 0) or 0)) in (90, 270):
            w, h = h, w  # video HP vertikal dengan metadata rotasi
    return w, h, float((d.get("format") or {}).get("duration", 0))


def frames(path, fps, scale_w):
    """Dekode lewat ffmpeg (lebih andal di chroot daripada cv2.VideoCapture) ke BGR kecil."""
    import numpy as np
    w, h, _ = probe(path)
    sh_ = int(round(h * scale_w / w / 2) * 2)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={fps},scale={scale_w}:{sh_}",
                          "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    size = scale_w * sh_ * 3
    i = 0
    while True:
        buf = p.stdout.read(size)
        if len(buf) < size:
            break
        yield i / fps, np.frombuffer(buf, np.uint8).reshape(sh_, scale_w, 3)
        i += 1
    p.wait()


class Detectors:
    def __init__(self, use_seg):
        import cv2
        self.cv2 = cv2
        self.face = None
        cands = [os.path.join(MODELS, "haarcascade_frontalface_alt2.xml")]
        if hasattr(cv2, "data"):
            cands.append(os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_alt2.xml"))
        if hasattr(cv2, "CascadeClassifier"):
            for c in cands:
                if os.path.exists(c):
                    self.face = cv2.CascadeClassifier(c)
                    break
        if self.face is None:
            print("[WARN] Haar tidak tersedia (OpenCV 5?) -> wajah diperkirakan dari kepala badan. "
                  "Pasang: pip install --break-system-packages 'opencv-python-headless<5'", file=sys.stderr)
        self.seg = None
        onnx = os.path.join(MODELS, "u2net_human_seg.onnx")
        if use_seg:
            try:
                import onnxruntime as ort
                if os.path.exists(onnx):
                    so = ort.SessionOptions()
                    so.intra_op_num_threads = max(1, (os.cpu_count() or 2) - 1)
                    self.seg = ort.InferenceSession(onnx, so, providers=["CPUExecutionProvider"])
                else:
                    print("[WARN] model u2net belum ada -> jalankan `reditor models` (±176 MB). Pakai HOG.", file=sys.stderr)
            except ImportError:
                print("[WARN] onnxruntime belum ada -> pip install --break-system-packages onnxruntime. Pakai HOG.",
                      file=sys.stderr)
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    def segment(self, bgr):
        """u2net_human_seg: input 320x320 ternormalisasi ImageNet -> masker float 0..1 seukuran frame."""
        import numpy as np
        cv2 = self.cv2
        H, W = bgr.shape[:2]
        x = cv2.resize(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB), (320, 320)).astype(np.float32) / 255.0
        x = (x - np.array([0.485, 0.456, 0.406], np.float32)) / np.array([0.229, 0.224, 0.225], np.float32)
        x = x.transpose(2, 0, 1)[None]
        out = self.seg.run(None, {self.seg.get_inputs()[0].name: x})[0][0, 0]
        out = (out - out.min()) / (out.max() - out.min() + 1e-9)
        return cv2.resize(out, (W, H))

    def detect(self, bgr, want_mask):
        import numpy as np
        cv2 = self.cv2
        H, W = bgr.shape[:2]
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        res = {"face": None, "body": None, "mask": None}
        # --- badan
        if self.seg is not None:
            m = self.segment(bgr)
            b = (m > 0.5).astype(np.uint8)
            n, lab, stats, _ = cv2.connectedComponentsWithStats(b)
            if n > 1:
                k = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
                if stats[k, cv2.CC_STAT_AREA] > 0.01 * W * H:
                    x, y, w, h = stats[k, :4]
                    res["body"] = [x / W, y / H, (x + w) / W, (y + h) / H]
                    if want_mask:
                        res["mask"] = ((lab == k) * 255).astype(np.uint8)
        else:
            rects, weights = self.hog.detectMultiScale(gray, winStride=(8, 8), padding=(8, 8), scale=1.06)
            if len(rects):
                j = int(max(range(len(rects)), key=lambda i: float(weights[i]) * rects[i][2] * rects[i][3]))
                x, y, w, h = rects[j]
                res["body"] = [x / W, y / H, (x + w) / W, (y + h) / H]
        # --- wajah (Haar), diutamakan yang dekat kepala badan
        if self.face is not None:
            sc = 540 / W
            g = cv2.equalizeHist(cv2.resize(gray, (540, int(H * sc))))
            faces = self.face.detectMultiScale(g, 1.1, 4, minSize=(int(50 * 540 / 1080), int(50 * 540 / 1080)))
            best = None
            for (x, y, w, h) in faces:
                cx, cy, r = (x + w / 2) / 540, (y + h / 2) / (H * sc), (w / 2) / 540
                score = w * h
                if res["body"]:
                    bx0, by0, bx1, by1 = res["body"]
                    head_y = by0 + 0.11 * (by1 - by0)
                    if not (bx0 - 0.05 <= cx <= bx1 + 0.05 and cy <= head_y + 0.25):
                        continue
                    score /= 1 + abs(cy - head_y) * 10
                if best is None or score > best[0]:
                    best = (score, [cx, cy, r])
            if best:
                res["face"] = best[1]
        # fallback kepala dari badan: pita atas 22% tinggi badan
        if res["face"] is None and res["body"]:
            bx0, by0, bx1, by1 = res["body"]
            bh = by1 - by0
            if res["mask"] is not None:
                band = res["mask"][int(by0 * H): int((by0 + 0.22 * bh) * H)]
                cols = np.where(band.any(axis=0))[0]
                if len(cols):
                    hx = (cols.min() + cols.max()) / 2 / W
                    r = (cols.max() - cols.min()) / 2 / W
                else:
                    hx, r = (bx0 + bx1) / 2, (bx1 - bx0) * 0.2
            else:
                hx, r = (bx0 + bx1) / 2, (bx1 - bx0) * 0.2
            hy = by0 + 0.11 * bh
            res["head"] = [hx, hy + 0.35 * r * W / H, 0.9 * r]
        return res


def smooth(samples, keys=("cx", "cy", "w", "h"), win=7):
    """Isi celah (interpolasi / tahan nilai terakhir) lalu moving average `win` sampel."""
    import numpy as np
    idx = [i for i, s in enumerate(samples) if s["found"]]
    if not idx:
        for s in samples:
            s.update(cx=0.5, cy=0.4, w=0.0, h=0.0)
        return samples
    for i, s in enumerate(samples):
        if s["found"]:
            continue
        prev = max((j for j in idx if j < i), default=None)
        nxt = min((j for j in idx if j > i), default=None)
        if prev is None or nxt is None:
            src = samples[nxt if prev is None else prev]
            s.update({k: src[k] for k in keys})
        else:
            f = (i - prev) / (nxt - prev)
            s.update({k: samples[prev][k] * (1 - f) + samples[nxt][k] * f for k in keys})
    k_ = np.ones(win) / win
    for k in keys:
        v = np.array([s[k] for s in samples], float)
        pad = np.pad(v, (win // 2, win // 2), mode="edge")
        v = np.convolve(pad, k_, mode="valid")
        for s, x in zip(samples, v):
            s[k] = round(float(x), 4)
    return samples


def track(path, fps=6, out=None, seg=False, masks_dir=None, scale_w=480):
    import cv2
    det = Detectors(use_seg=seg)
    w, h, dur = probe(path)
    samples, hits = [], 0
    if masks_dir:
        os.makedirs(masks_dir, exist_ok=True)
    for i, (t, bgr) in enumerate(frames(path, fps, scale_w)):
        r = det.detect(bgr, want_mask=bool(masks_dir))
        s = {"t": round(t, 3), "face": r["face"], "body": r["body"], "mask": None}
        anchor = r["face"] or r.get("head")
        if anchor:
            hits += 1
            s.update(found=True, cx=float(anchor[0]), cy=float(anchor[1]), w=float(anchor[2]) * 2, h=float(anchor[2]) * 2 * w / h)
        else:
            s["found"] = False
        if masks_dir and r["mask"] is not None:
            name = f"m_{i:04d}.png"
            cv2.imwrite(os.path.join(masks_dir, name), r["mask"])
            s["mask"] = name
        samples.append(s)
    samples = smooth(samples)
    res = {"src": os.path.relpath(path, ROOT), "width": w, "height": h, "duration": dur, "fps": fps,
           "coverage": round(hits / max(1, len(samples)), 3), "masksDir": masks_dir, "samples": samples}
    if out:
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        with open(out, "w") as f:
            json.dump(res, f)
        print(f"OK {os.path.relpath(out, ROOT)}: {len(samples)} sampel, subjek {res['coverage']*100:.0f}%"
              + ("  [WARN] cakupan rendah: cek manual / pakai --seg" if res["coverage"] < 0.4 else ""))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--fps", type=float, default=6)
    ap.add_argument("--seg", action="store_true", help="pakai u2net (lebih akurat, lebih lambat)")
    ap.add_argument("--masks", help="folder untuk masker badan PNG (butuh --seg)")
    ap.add_argument("--out")
    a = ap.parse_args()
    need_cv2()
    if a.all:
        raw = os.path.join(ROOT, "raw-footage")
        vids = [os.path.join(raw, f) for f in sorted(os.listdir(raw)) if f.lower().endswith(VIDEO_EXT)]
    elif a.video:
        vids = [os.path.abspath(a.video)]
    else:
        ap.error("beri path video atau --all")
    for v in vids:
        out = a.out if (a.out and len(vids) == 1) else os.path.join(
            ROOT, "tracks", os.path.splitext(os.path.basename(v))[0] + ".json")
        track(v, a.fps, out, a.seg, a.masks)


if __name__ == "__main__":
    main()
