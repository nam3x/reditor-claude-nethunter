#!/usr/bin/env bash
# gen_vfx.sh — Paket VFX prosedural (bebas lisensi, buatan sendiri) untuk edit clean-modern.
# Ringan untuk HP: dibuat di resolusi kecil lalu di-upscale saat render (isi VFX lembut, jadi tetap halus).
# Pemakaian: bash editor/gen_vfx.sh [FOLDER_VFX=VFX] [DETIK=4] [--with-music]
set -euo pipefail
OUT="${1:-VFX}"; SEC="${2:-4}"; WITH_MUSIC="${3:-}"
W=540; H=960            # 9:16 dasar; untuk 16:9 cukup di-crop/scale (objectFit: cover)
FPS=30
mkdir -p "$OUT"/{light-leaks,flares,dust,grain,textures,luts,sfx,transitions}
FF=(ffmpeg -hide_banner -loglevel error -y)
ENC=(-c:v libx264 -preset veryfast -crf 24 -pix_fmt yuv420p -movflags +faststart -an)
here="$(cd "$(dirname "$0")" && pwd)"

echo "[1/7] Light leaks (blend: screen)"
leak() { # nama  R G B  arah
  local name=$1 r=$2 g=$3 b=$4 dir=$5
  # dihitung di 1/4 resolusi (gumpalan cahaya lembut), lalu di-upscale -> ±16x lebih cepat di HP
  "${FF[@]}" -f lavfi -i "color=black:s=$((W/4))x$((H/4)):r=${FPS}:d=${SEC}" -vf \
  "format=rgb24,geq=\
r='${r}*exp(-((X-W*(0.5+${dir}*0.45*sin(2*PI*T/${SEC})))^2/(2*(W*0.33)^2)+(Y-H*(0.35+0.15*cos(2*PI*T/${SEC})))^2/(2*(H*0.30)^2)))':\
g='${g}*exp(-((X-W*(0.5+${dir}*0.45*sin(2*PI*T/${SEC})))^2/(2*(W*0.30)^2)+(Y-H*(0.35+0.15*cos(2*PI*T/${SEC})))^2/(2*(H*0.27)^2)))':\
b='${b}*exp(-((X-W*(0.5+${dir}*0.45*sin(2*PI*T/${SEC})))^2/(2*(W*0.26)^2)+(Y-H*(0.35+0.15*cos(2*PI*T/${SEC})))^2/(2*(H*0.24)^2)))',\
gblur=sigma=8,scale=${W}:${H}:flags=bicubic,eq=contrast=1.05" "${ENC[@]}" "$OUT/light-leaks/$name.mp4"
}
leak leak_warm_01 255 150 60 1
leak leak_amber_02 255 190 90 -1
leak leak_cool_01 80 170 255 1
leak leak_magenta_01 240 80 200 -1

echo "[2/7] Anamorphic flare (blend: screen)"
"${FF[@]}" -f lavfi -i "color=black:s=${W}x${H}:r=${FPS}:d=${SEC}" -vf \
"format=rgb24,geq=\
r='90*exp(-((Y-H*0.42)^2)/(2*6^2))*exp(-((X-W*(-0.2+1.4*T/${SEC}))^2)/(2*(W*0.6)^2))+200*exp(-(((X-W*(-0.2+1.4*T/${SEC}))^2+(Y-H*0.42)^2))/(2*14^2))':\
g='150*exp(-((Y-H*0.42)^2)/(2*5^2))*exp(-((X-W*(-0.2+1.4*T/${SEC}))^2)/(2*(W*0.6)^2))+220*exp(-(((X-W*(-0.2+1.4*T/${SEC}))^2+(Y-H*0.42)^2))/(2*14^2))':\
b='255*exp(-((Y-H*0.42)^2)/(2*5^2))*exp(-((X-W*(-0.2+1.4*T/${SEC}))^2)/(2*(W*0.6)^2))+255*exp(-(((X-W*(-0.2+1.4*T/${SEC}))^2+(Y-H*0.42)^2))/(2*14^2))',\
gblur=sigma=2" "${ENC[@]}" "$OUT/flares/flare_blue_sweep.mp4"

echo "[3/7] Dust & bokeh melayang (blend: screen)"
# Hemat CPU HP: medan partikel dihitung SEKALI (1 frame), lalu digulir ke atas dengan crop -> loop mulus.
field() { # out n rmin rmax seed w h blur
  "${FF[@]}" -f lavfi -i "color=black:s=$6x$7" -vf \
  "format=gray,geq=lum='$(python3 "$here/particles_expr.py" "$2" "$3" "$4" 0 "$5")',gblur=sigma=$8" -frames:v 1 "$1"
}
drift() { # field.png out.mp4 loops
  "${FF[@]}" -loop 1 -i "$1" -filter_complex \
  "[0]split[a][b];[a][b]vstack,crop=${W}:${H}:0:'${H}-mod(t*$3*${H}/${SEC},${H})',fps=${FPS},format=yuv420p" \
  -t "$SEC" "${ENC[@]}" "$2"
}
TMPD="$(mktemp -d)"
field "$TMPD/dust.png" 70 1.0 2.4 7 "$W" "$H" 0.5
drift "$TMPD/dust.png" "$OUT/dust/dust_float_01.mp4" 1
field "$TMPD/bokeh.png" 18 9 26 21 "$W" "$H" 3
drift "$TMPD/bokeh.png" "$OUT/dust/bokeh_soft_01.mp4" 1
rm -f "$TMPD/dust.png" "$TMPD/bokeh.png"; rmdir "$TMPD"

echo "[4/7] Film grain (blend: overlay / soft-light)"
"${FF[@]}" -f lavfi -i "color=0x808080:s=${W}x${H}:r=${FPS}:d=${SEC}" -vf \
"noise=alls=28:allf=t+u,gblur=sigma=0.6,format=yuv420p" "${ENC[@]}" "$OUT/grain/grain_fine_01.mp4"
"${FF[@]}" -f lavfi -i "color=0x808080:s=${W}x${H}:r=${FPS}:d=${SEC}" -vf \
"noise=alls=45:allf=t+u,gblur=sigma=1.2,format=yuv420p" "${ENC[@]}" "$OUT/grain/grain_35mm_01.mp4"

echo "[5/7] Tekstur PNG (vignette, gradient, scanline)"
"${FF[@]}" -f lavfi -i "color=black:s=1080x1920" -vf \
"format=rgba,geq=r=0:g=0:b=0:a='255*min(1,max(0,(hypot(X-W/2,Y-H/2)/hypot(W/2,H/2)-0.55)/0.45))'" -frames:v 1 "$OUT/textures/vignette_9x16.png"
"${FF[@]}" -f lavfi -i "color=black:s=1920x1080" -vf \
"format=rgba,geq=r=0:g=0:b=0:a='255*min(1,max(0,(hypot(X-W/2,Y-H/2)/hypot(W/2,H/2)-0.55)/0.45))'" -frames:v 1 "$OUT/textures/vignette_16x9.png"
"${FF[@]}" -f lavfi -i "color=black:s=1080x1920" -vf \
"format=rgba,geq=r=0:g=0:b=0:a='if(lt(mod(Y,4),2),40,0)'" -frames:v 1 "$OUT/textures/scanlines_9x16.png"

echo "[6/7] Transisi (blend: screen)"
"${FF[@]}" -f lavfi -i "color=white:s=${W}x${H}:r=${FPS}:d=0.4" -vf "fade=t=out:st=0.05:d=0.35" "${ENC[@]}" "$OUT/transitions/flash_white_0.4s.mp4"
"${FF[@]}" -f lavfi -i "color=black:s=${W}x${H}:r=${FPS}:d=0.6" -vf \
"format=rgb24,geq=r='255*exp(-((X-W*(-0.3+1.6*T/0.6))^2)/(2*(W*0.12)^2))':g='235*exp(-((X-W*(-0.3+1.6*T/0.6))^2)/(2*(W*0.12)^2))':b='210*exp(-((X-W*(-0.3+1.6*T/0.6))^2)/(2*(W*0.12)^2))',gblur=sigma=20" \
"${ENC[@]}" "$OUT/transitions/light_sweep_0.6s.mp4"

echo "[7/7] LUT + SFX"
python3 "$here/gen_luts.py" "$OUT/luts" >/dev/null
A=(-ar 48000 -ac 2)
"${FF[@]}" -f lavfi -i "anoisesrc=d=0.7:c=pink:a=0.6" -af "highpass=f='200',lowpass=f=3000,afade=t=in:d=0.35,afade=t=out:st=0.35:d=0.35,volume=0.8" "${A[@]}" "$OUT/sfx/whoosh_soft.wav"
"${FF[@]}" -f lavfi -i "aevalsrc='0.6*sin(2*PI*(900-600*t/0.12)*t)*exp(-t*35)':d=0.15" "${A[@]}" "$OUT/sfx/pop.wav"
"${FF[@]}" -f lavfi -i "aevalsrc='0.5*sin(2*PI*2200*t)*exp(-t*90)':d=0.06" "${A[@]}" "$OUT/sfx/click.wav"
"${FF[@]}" -f lavfi -i "aevalsrc='0.35*sin(2*PI*1568*t)*exp(-t*4)+0.2*sin(2*PI*2349*t)*exp(-t*5)':d=1.2" "${A[@]}" "$OUT/sfx/ding.wav"
"${FF[@]}" -f lavfi -i "aevalsrc='0.9*sin(2*PI*(60-30*t)*t)*exp(-t*6)':d=0.9" -af "lowpass=f=400" "${A[@]}" "$OUT/sfx/impact_low.wav"
"${FF[@]}" -f lavfi -i "anoisesrc=d=2:c=white:a=0.4" -af "highpass=f='300',afade=t=in:d=1.9:curve=exp,afade=t=out:st=1.9:d=0.1,volume=0.7" "${A[@]}" "$OUT/sfx/riser_2s.wav"

if [ "$WITH_MUSIC" = "--with-music" ]; then
  MUS="$(dirname "$OUT")/Musik"; mkdir -p "$MUS"
  echo "[+] Bed musik prosedural 60 dtk -> $MUS/bed_procedural_clean.mp3"
  "${FF[@]}" -f lavfi -i "aevalsrc='0.08*(sin(2*PI*220*t)+sin(2*PI*277.18*t)+sin(2*PI*329.63*t))*(0.6+0.4*sin(2*PI*0.25*t))+0.05*sin(2*PI*55*t)*exp(-mod(t,0.5)*8)':d=60" \
    -af "lowpass=f=2500,aecho=0.8:0.7:400:0.25,afade=t=in:d=1,afade=t=out:st=59:d=1" -ac 2 -b:a 160k "$MUS/bed_procedural_clean.mp3"
fi
echo "Selesai. Lihat $OUT/README.md untuk mode blend yang disarankan."
