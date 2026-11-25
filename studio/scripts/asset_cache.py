#!/usr/bin/env python3
"""
asset_cache.py — Cache aset PNG hasil render di repo GitHub (private) agar bisa dipakai ulang.

Kunci cache = sha256 dari isi yang menentukan tampilan aset (komponen, props, style,
ukuran, dan isi file kode komponennya). Aset yang kuncinya sama tidak dirender ulang.

Struktur repo cache:
  assets/<key>.png
  index.json          { "<key>": {"name":..., "project":..., "size":"WxH", "created":...} }

Perintah (jalankan dari root proyek Remotion):
  python3 scripts/asset_cache.py init --repo PEMILIK/NAMA-REPO
  python3 scripts/asset_cache.py key  --spec spec.json            # cetak kunci
  python3 scripts/asset_cache.py get  --repo R --spec spec.json --dest public/cache/
        -> exit 0 + cetak path jika ADA di cache (HIT); exit 3 jika belum ada (MISS)
  python3 scripts/asset_cache.py put  --repo R --spec spec.json --file out/x.png
        -> commit + push PNG ke repo cache

spec.json contoh:
  {"name": "bg-hook", "project": "kemasan-kertas", "component": "src/stills/HookBg.tsx",
   "props": {"title": "..."}, "style": {...}, "width": 1080, "height": 1920,
   "deps": ["src/components/Art.tsx", "src/theme.ts"]}
  deps = file kode lain yang ikut menentukan tampilan; isinya ikut masuk kunci cache.

Opsi repo (untuk init/get/put):
  --branch asset-cache   simpan di branch ini (dibuat bila belum ada)
  --subdir asset-cache   simpan di subfolder ini di dalam repo
  --repo juga boleh path/URL git lokal (mis. untuk uji), selain PEMILIK/NAMA.
"""
import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys

CACHE_DIR = os.path.expanduser("~/.remotion-asset-cache")
MAX_BYTES = 50 * 1024 * 1024
BRANCH = None   # diisi dari --branch
SUBDIR = ""     # diisi dari --subdir


def run(cmd, cwd=None, check=True):
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)


def compute_key(spec):
    payload = {k: spec.get(k) for k in ("component", "props", "style", "width", "height")}
    comp = spec.get("component")
    if comp and os.path.exists(comp):
        payload["componentHash"] = hashlib.sha256(open(comp, "rb").read()).hexdigest()
    deps = {}
    for d in sorted(spec.get("deps") or []):
        deps[d] = hashlib.sha256(open(d, "rb").read()).hexdigest() if os.path.exists(d) else "MISSING"
        if deps[d] == "MISSING":
            print(f"[WARN] deps {d} tidak ditemukan", file=sys.stderr)
    if deps:
        payload["deps"] = deps
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(blob).hexdigest()[:20]


def local_path(repo):
    name = repo.rstrip("/").replace("://", "_").replace("/", "__").replace(":", "_")
    return os.path.join(CACHE_DIR, name + (f"@{BRANCH}" if BRANCH else ""))


def root(path):
    """Folder tempat assets/ dan index.json (repo + --subdir)."""
    return os.path.join(path, SUBDIR) if SUBDIR else path


def remote_url(repo):
    return repo if ("://" in repo or repo.startswith(("/", ".", "~")) or repo.endswith(".git")) else f"https://github.com/{repo}.git"


def sync(repo):
    """Clone atau pull repo cache. Return path lokal, atau None jika tidak bisa diakses."""
    path = local_path(repo)
    try:
        if os.path.isdir(os.path.join(path, ".git")):
            has_remote = run(["git", "ls-remote", "--heads", "origin", BRANCH], cwd=path, check=False).stdout.strip() if BRANCH else "y"
            if has_remote:
                run(["git", "pull", "--ff-only", "-q", "origin"] + ([BRANCH] if BRANCH else []), cwd=path)
        else:
            os.makedirs(CACHE_DIR, exist_ok=True)
            url = remote_url(repo); use_gh = url == f"https://github.com/{repo}.git" and shutil.which("gh")
            clone = (lambda extra: ["gh", "repo", "clone", repo, path, "--", "-q"] + extra) if use_gh else (lambda extra: ["git", "clone", "-q", url, path] + extra)
            r = run(clone(["--branch", BRANCH, "--single-branch"] if BRANCH else []), check=False)
            if r.returncode != 0:
                shutil.rmtree(path, ignore_errors=True)
                run(clone([]))
                if BRANCH:
                    run(["git", "checkout", "-q", "-B", BRANCH], cwd=path)  # branch belum ada di remote: buat
        return path
    except subprocess.CalledProcessError as e:
        print(f"[WARN] Repo cache {repo} tidak bisa diakses: {(e.stderr or '').strip()[:200]}",
              file=sys.stderr)
        return path if os.path.isdir(path) else None


def load_index(path):
    f = os.path.join(root(path), "index.json")
    return json.load(open(f, encoding="utf-8")) if os.path.exists(f) else {}


def cmd_init(a):
    if not shutil.which("gh"):
        sys.exit("[ERROR] gh CLI tidak ada; buat repo private secara manual di GitHub.")
    r = run(["gh", "repo", "view", a.repo, "--json", "visibility"], check=False)
    if r.returncode == 0:
        vis = json.loads(r.stdout).get("visibility")
        print(f"Repo {a.repo} sudah ada (visibility: {vis}).")
        if vis != "PRIVATE":
            print("[WARN] Repo cache BUKAN private. Aset bisa dilihat publik.", file=sys.stderr)
    else:
        run(["gh", "repo", "create", a.repo, "--private",
             "--description", "Cache aset PNG remotion-storyteller"])
        print(f"Repo private {a.repo} dibuat.")
    path = sync(a.repo)
    if path and not os.path.exists(os.path.join(root(path), "index.json")):
        os.makedirs(os.path.join(root(path), "assets"), exist_ok=True)
        json.dump({}, open(os.path.join(root(path), "index.json"), "w"))
        run(["git", "add", "-A"], cwd=path)
        run(["git", "commit", "-qm", "init cache aset"], cwd=path)
        run(["git", "push", "-q", "-u", "origin", "HEAD"], cwd=path, check=False)


def cmd_key(a):
    print(compute_key(json.load(open(a.spec, encoding="utf-8"))))


def cmd_get(a):
    spec = json.load(open(a.spec, encoding="utf-8"))
    key = compute_key(spec)
    path = sync(a.repo)
    src = os.path.join(root(path), "assets", f"{key}.png") if path else None
    if src and os.path.exists(src):
        os.makedirs(a.dest, exist_ok=True)
        dst = os.path.join(a.dest, f"{spec.get('name', key)}.png")
        shutil.copy2(src, dst)
        print(dst)
        print(f"HIT {key}", file=sys.stderr)
        sys.exit(0)
    print(f"MISS {key}", file=sys.stderr)
    sys.exit(3)


def cmd_put(a):
    spec = json.load(open(a.spec, encoding="utf-8"))
    key = compute_key(spec)
    if os.path.getsize(a.file) > MAX_BYTES:
        sys.exit("[WARN] File > 50 MB, tidak diunggah ke cache.")
    path = sync(a.repo)
    if not path:
        sys.exit("[WARN] Repo cache tidak bisa diakses; aset hanya tersimpan lokal.")
    os.makedirs(os.path.join(root(path), "assets"), exist_ok=True)
    shutil.copy2(a.file, os.path.join(root(path), "assets", f"{key}.png"))
    idx = load_index(path)
    idx[key] = {"name": spec.get("name"), "project": spec.get("project"),
                "size": f"{spec.get('width')}x{spec.get('height')}",
                "created": datetime.datetime.now().isoformat(timespec="seconds")}
    json.dump(idx, open(os.path.join(root(path), "index.json"), "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    rel = (SUBDIR + "/") if SUBDIR else ""
    run(["git", "add", f"{rel}assets/{key}.png", f"{rel}index.json"], cwd=path)
    run(["git", "commit", "-qm", f"aset {spec.get('name', key)} ({key})"], cwd=path, check=False)
    r = run(["git", "push", "-q", "-u", "origin", "HEAD"], cwd=path, check=False)
    if r.returncode != 0:
        sys.exit(f"[WARN] Push gagal ({r.stderr.strip()[:200]}); commit tersimpan lokal, "
                 f"push ulang nanti.")
    print(f"OK disimpan ke {a.repo}{'@' + BRANCH if BRANCH else ''}: {rel}assets/{key}.png")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("init", "key", "get", "put"):
        s = sub.add_parser(name)
        if name != "key":
            s.add_argument("--repo", required=True)
            s.add_argument("--branch", default=None)
            s.add_argument("--subdir", default="")
        if name != "init":
            s.add_argument("--spec", required=True)
        if name == "get":
            s.add_argument("--dest", default="public/cache/")
        if name == "put":
            s.add_argument("--file", required=True)
    a = p.parse_args()
    global BRANCH, SUBDIR
    BRANCH, SUBDIR = getattr(a, "branch", None), (getattr(a, "subdir", "") or "").strip("/")
    {"init": cmd_init, "key": cmd_key, "get": cmd_get, "put": cmd_put}[a.cmd](a)


if __name__ == "__main__":
    main()
