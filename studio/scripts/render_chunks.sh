#!/usr/bin/env bash
# Render per potongan (aman RAM HP; render penuh bisa kena OOM/SIGKILL), lalu gabung + mux audio.
# Pemakaian (dari studio/): bash scripts/render_chunks.sh [Komposisi=ShortsBeat] [FRAME_PER_POTONGAN=300] [versi=v1]
#   Render ulang satu potongan saja: hapus out/parts/p_A-B.mp4 lalu jalankan lagi (yang ada dilewati).
set -euo pipefail
COMP="${1:-ShortsBeat}"; CHUNK="${2:-300}"; VER="${3:-v1}"
cd "$(dirname "$0")/.."
mkdir -p out/parts
TOTAL=$(python3 - "$COMP" <<'PY'
import json, sys
c = sys.argv[1]
if c == "ShortsBeat":
    print(json.load(open("src/shorts.data.json"))["totalF"])
else:
    t = json.load(open("src/timeline.generated.json"))
    print(t["highlightDurationInFrames"] if c == "HighlightVertical" else t["fullDurationInFrames"])
PY
)
CONC="${REDITOR_CONCURRENCY:-2}"
echo "Komposisi $COMP: $TOTAL frame, potongan $CHUNK frame, concurrency $CONC"
: > out/parts/parts.txt
s=0
while [ "$s" -lt "$TOTAL" ]; do
  e=$(( s + CHUNK - 1 )); [ "$e" -ge "$TOTAL" ] && e=$(( TOTAL - 1 ))
  f="out/parts/p_${s}-${e}.mp4"
  if [ ! -s "$f" ]; then
    echo "[render] frame $s-$e"
    MUTE=""; [ "$COMP" = "ShortsBeat" ] && MUTE="--muted"   # ShortsBeat: audio master di-mux di akhir
    npx remotion render src/index.ts "$COMP" "$f" --codec=h264 --crf=18 --concurrency="$CONC" $MUTE \
      --frames="$s-$e" --offthreadvideo-cache-size-in-bytes=400000000 --log=error
  else
    echo "[lewat] $f sudah ada"
  fi
  echo "file 'p_${s}-${e}.mp4'" >> out/parts/parts.txt
  s=$(( e + 1 ))
done
AUDIO=""
[ "$COMP" = "ShortsBeat" ] && AUDIO=$(python3 -c "import json;d=json.load(open('src/shorts.data.json'));print(d.get('audio') or '')")
OUT="out/${COMP}_${VER}.mp4"
if [ -n "$AUDIO" ] && [ -f "public/$AUDIO" ]; then
  ffmpeg -v error -y -f concat -safe 0 -i out/parts/parts.txt -i "public/$AUDIO" -map 0:v -map 1:a \
    -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -r 30 -c:a copy -movflags +faststart -shortest "$OUT"
else  # komposisi lain: audio (VO + musik) ikut dirender per potongan
  ffmpeg -v error -y -f concat -safe 0 -i out/parts/parts.txt -c:v copy -c:a aac -b:a 192k -movflags +faststart "$OUT"
fi
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height,r_frame_rate -of compact=p=0 "$OUT"
echo "Selesai: studio/$OUT"
