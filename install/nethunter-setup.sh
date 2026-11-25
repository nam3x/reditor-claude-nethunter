#!/usr/bin/env bash
# nethunter-setup.sh — Pasang semua dependensi reditor di Kali NetHunter (chroot arm64) lewat terminal NetHunter.
# Aman dijalankan ulang (idempotent). Jalankan sebagai root di "Kali Chroot" (NetHunter Terminal -> KALI).
#
#   cd ~/reditor-claude-nethunter && bash install/nethunter-setup.sh
#
# Opsi env:
#   REDITOR_SKIP_WHISPER=1   lewati faster-whisper (hemat ±300 MB)
#   REDITOR_SKIP_CLAUDE=1    lewati pemasangan Claude Code
#   REDITOR_SKIP_CHROMIUM=1  lewati chromium apt (fallback browser Remotion)
#   REDITOR_SKIP_MODELS=1    lewati unduhan model u2net (±176 MB)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
say()  { printf '\n\033[1;36m== %s\033[0m\n' "$*"; }
warn() { printf '\033[33m[!] %s\033[0m\n' "$*"; }
SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"

say "0. Cek lingkungan"
ARCH="$(uname -m)"; echo "arch=$ARCH"
case "$ARCH" in aarch64|arm64|x86_64) ;; armv7l|armhf) warn "armhf 32-bit: Remotion tidak didukung. Pakai alur 'reditor edit' (ffmpeg) saja.";; esac
if [ -d /sdcard ] && [[ "$ROOT" == /sdcard* ]]; then
  warn "Proyek ada di /sdcard (FUSE): symlink & izin eksekusi bermasalah, npm install bisa gagal."
  warn "Pindahkan ke /root:  cp -r \"$ROOT\" /root/ && cd /root/$(basename "$ROOT")"
fi

say "1. Paket apt (ffmpeg, node, python, font, library Chromium)"
export DEBIAN_FRONTEND=noninteractive
$SUDO apt-get update -y
PKGS=(ffmpeg python3 python3-pip python3-venv python3-numpy git curl rsync ca-certificates unzip xz-utils
      fonts-inter fonts-noto-core fonts-noto-color-emoji fonts-dejavu-core fontconfig
      libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1
      libxfixes3 libxrandr2 libgbm1 libasound2 libpango-1.0-0 libcairo2 libxshmfence1)
# libasound2 diganti libasound2t64 di Debian/Kali terbaru
apt-cache show libasound2t64 >/dev/null 2>&1 && PKGS=("${PKGS[@]/libasound2/libasound2t64}")
[ "${REDITOR_SKIP_CHROMIUM:-0}" = "1" ] || PKGS+=(chromium)
avail=()
for p in "${PKGS[@]}"; do apt-cache show "$p" >/dev/null 2>&1 && avail+=("$p") || warn "paket $p tidak ada di repo, dilewati"; done
$SUDO apt-get install -y --no-install-recommends "${avail[@]}"

say "2. Node.js >= 18"
NODE_MAJOR=0; command -v node >/dev/null && NODE_MAJOR=$(node -p 'process.versions.node.split(".")[0]')
if [ "$NODE_MAJOR" -lt 18 ]; then
  $SUDO apt-get install -y nodejs npm || true
  NODE_MAJOR=$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)
fi
if [ "$NODE_MAJOR" -lt 18 ]; then
  warn "Node repo terlalu lama -> pasang Node 22 LTS dari nodejs.org (arm64)"
  NV=v22.11.0; NA=$([ "$ARCH" = "x86_64" ] && echo x64 || echo arm64)
  curl -fsSL "https://nodejs.org/dist/$NV/node-$NV-linux-$NA.tar.xz" -o /tmp/node.tar.xz
  $SUDO tar -xJf /tmp/node.tar.xz -C /usr/local --strip-components=1 && rm -f /tmp/node.tar.xz
fi
node -v; npm -v

say "3. /dev/shm (Chromium butuh >= 256 MB; chroot NetHunter sering 64 MB)"
SHM=$(df -m /dev/shm 2>/dev/null | awk 'NR==2{print $2}' || echo 0)
if [ "${SHM:-0}" -lt 256 ]; then
  $SUDO mount -t tmpfs -o size=512M tmpfs /dev/shm 2>/dev/null && echo "/dev/shm -> 512M" || warn "gagal remount /dev/shm; Remotion akan memakai --disable-dev-shm-usage"
fi

say "4. Python: graphify, faster-whisper, OpenCV 4 (Haar) + onnxruntime (u2net) untuk pelacakan"
PIP=(python3 -m pip install --break-system-packages -q)
"${PIP[@]}" graphifyy || pipx install graphifyy || warn "graphify gagal dipasang (opsional)"
# OpenCV 5 menghapus Haar -> kunci ke 4.x. apt python3-opencv (4.x) juga boleh.
"${PIP[@]}" "opencv-python-headless<5" || $SUDO apt-get install -y python3-opencv || warn "OpenCV gagal (pelacakan wajah nonaktif)"
"${PIP[@]}" onnxruntime || warn "onnxruntime gagal (segmentasi badan u2net nonaktif, fallback HOG)"
if [ "${REDITOR_SKIP_MODELS:-0}" != "1" ]; then
  bash "$ROOT/bin/reditor" models || warn "unduh model gagal; ulangi nanti: reditor models"
fi
if [ "${REDITOR_SKIP_WHISPER:-0}" != "1" ]; then
  "${PIP[@]}" faster-whisper || warn "faster-whisper gagal (butuh wheel ctranslate2 aarch64). Alternatif: whisper.cpp, lihat docs/REKOMENDASI.md"
fi

say "5. Studio Remotion (npm install + Chrome Headless Shell)"
cd "$ROOT/studio"
npm install --no-audit --no-fund
# Remotion mengunduh Chrome Headless Shell linux-arm64. Jika gagal (jaringan/arsitektur), pakai chromium apt.
if ! npx remotion browser ensure 2>/dev/null; then
  for b in /usr/bin/chromium /usr/bin/chromium-browser; do
    if [ -x "$b" ]; then
      warn "Chrome Headless Shell gagal diunduh -> pakai $b"
      grep -q REDITOR_BROWSER "$HOME/.bashrc" 2>/dev/null || echo "export REDITOR_BROWSER=$b" >> "$HOME/.bashrc"
      export REDITOR_BROWSER="$b"; break
    fi
  done
fi
# Font untuk Remotion offline (Inter + Poppins dari npm @fontsource)
mkdir -p public/fonts
for f in inter poppins; do
  npm pack "@fontsource/$f@5.1.0" --silent >/dev/null 2>&1 && tar -xzf "fontsource-$f-5.1.0.tgz" && \
  cp package/files/*-latin-{400,500,700,800}-normal.woff2 public/fonts/ 2>/dev/null; rm -rf package "fontsource-$f-5.1.0.tgz"
done
cd "$ROOT"

say "6. VFX prosedural (bila belum ada)"
[ -f VFX/light-leaks/leak_warm_01.mp4 ] || bash editor/gen_vfx.sh VFX 4

say "7. Perintah 'reditor' + graphify"
chmod +x bin/reditor editor/*.sh editor/*.py studio/scripts/*.sh 2>/dev/null || true
$SUDO ln -sf "$ROOT/bin/reditor" /usr/local/bin/reditor
command -v graphify >/dev/null && graphify update "$ROOT" >/dev/null 2>&1 && echo "graphify-out/ dibuat" || true

if [ "${REDITOR_SKIP_CLAUDE:-0}" != "1" ] && ! command -v claude >/dev/null; then
  say "8. Claude Code CLI"
  npm install -g @anthropic-ai/claude-code || warn "gagal; coba: curl -fsSL https://claude.ai/install.sh | bash"
fi

say "Selesai"
reditor doctor || true
cat <<'EOF'

Langkah berikut:
  1) Taruh file: raw-footage/  referensi/  VO/  Musik/  (VFX/ sudah terisi)
  2) cd ~/reditor-claude-nethunter && claude      -> minta: "buat video dari raw footage + VO"
     atau manual: reditor transcribe && reditor edit auto && reditor edit preview
EOF
