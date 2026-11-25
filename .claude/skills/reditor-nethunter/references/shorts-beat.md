# Mode Shorts Beat — dari skill `video-editor-shorts` (Cetakinds), versi NetHunter

Claude berperan sebagai video editor Shorts/Reels: raw footage + musik → potong sinkron beat, gerak kamera,
motion graphic yang menempel di wajah/badan, gaya modern clean (Remotion), MP4 jadi.

**Output default:** 1080x1920, 30 fps, H.264 + AAC, `+faststart`. Durasi mengikuti permintaan (boleh > 60 dtk).
Beri versi di nama file (`_v1`, `_v2`, …) — `reditor shorts render v2`.

## Selera pengguna (wajib)
- **Modern, clean, enak dilihat.** Garis tipis putih + aksen emas lembut `#E8C27A`, font Inter. Dilarang: teks kartun
  ber-outline tebal, emoji besar, bintang berserakan, bingkai mencolok ("kaya anak TK").
- **Tanpa caption/teks di atas video** kecuali diminta. Karaoke hanya bila ada voiceover/dialog jelas.
- **Goyang kamera seperlunya**, tidak terus-menerus (bikin pusing): hanya di drop, awal bar, dan bagian fast.
- **Motion graphic menempel di wajah/badan** pada pose tertentu agar video terasa hidup.
- **Musik tanpa VO = full**: keras, jelas, beat nendang (master ≈ −9 LUFS). Dengan VO: musik di-duck, −14 LUFS.
- Jangan menulis nama orang di layar bila identitasnya belum pasti.
- Subjek ambigu ("close up baju biru" padahal banyak yang berbaju biru): ambil tafsiran paling masuk akal, sebut dalam
  satu baris, lanjut.

## Hubungan dengan aturan reditor
- Gerbang Aset: raw footage pengguna = acuan visual. **Mode ini tidak butuh VO** (edit musik); bila ada VO di `VO/`,
  isi `"vo"` di `plan.json` → musik di-duck dan VO dipakai apa adanya (aturan Tempo VO tetap berlaku).
- Loudness: pengecualian −9 LUFS hanya untuk edit musik tanpa VO; selain itu −14 LUFS.
- Aturan voiceover: kalau Claude menulis naskah VO, berhenti setelah naskah dan tunggu pengguna mengirim VO; jangan lanjut
  storyboard, kode, SFX, atau render sebelum itu.

## Alur (pakai daftar tugas; tracking & render dijalankan di latar, tunggu selesai sebelum membalas)
| Langkah | Perintah | Catatan |
|---|---|---|
| 1. Aset | file sudah di `raw-footage/`, `Musik/`, `referensi/` | unggahan pengguna jangan diubah |
| 2. Analisis footage | `reditor shorts analyze` | grid 5x5 + stempel waktu per video → `analisis/grid_*.jpg` (lihat dengan Read), daftar cut bawaan (`scene>0.25`; dissolve sering lolos → sisakan margin 0,3 dtk). Perbesar segmen kandidat: `ffmpeg -ss S -t 30 -i v -vf "fps=1,scale=200:-1,tile=6x5" ...`. Kumpulkan footage ± durasi + 20%. |
| 3. Musik & beat | (otomatis) `analisis/beats.json` | `editor/beats.py` (numpy, pengganti librosa yang berat di arm64): BPM, beat, downbeat, aksen, drop. Bila BPM meleset 2x/0,5x: `reditor beats Musik/x.mp3 --bpm 124`. |
| 4. Rencana shot | `reditor shorts init 30 --title ".." --artist ".."` | rentang lagu kontinu dengan drop di detik ~12–20, dipotong tepat di ketukan. Lalu **sutradarai `plan.json`** (srcStart, beats, cx, section, effect, outline). |
| 5. Cek crop | `reditor shorts sheet` | contact sheet frame tengah tiap shot + kotak crop kuning → perbaiki `cx`. Subjek berjalan → `cx` kompromi. Opsional: `reditor track --all` dulu agar `init` mengisi `cx` dari posisi wajah. |
| 6–8. Bangun | `reditor shorts build` | potong klip 3:4, lacak wajah/badan, tanam outline, mastering musik, tulis `studio/src/shorts.data.json` + `track.json` |
| 9. Render | `reditor still ShortsBeat <frame>` lalu `nohup reditor shorts render v1 > out/shorts.log 2>&1 &` | render per potongan (default 300 frame; `REDITOR_CHUNK`) |

## Rencana shot (plan.json)
| Bagian | Shot | Transisi | Efek |
|---|---|---|---|
| intro | 8 beat | crossfade 12 frame | tanpa goyang |
| drop | 8 beat, wajah ke kamera | flash putih lembut + motion blur | goyang besar (A0=18), outline `drop`, `burst` |
| main | 4 beat | zoom-in + blur 5 frame | goyang kecil tiap 4 ketukan setelah drop |
| fast | 2 beat | whip geser + blur | goyang A0=7, outline `fast` (kilat tiap ketukan) |
| outro | 8–12 beat, slow-mo 0,7x | fade bersama musik | outline `soft`, tanpa goyang |
Cut = ketukan kumulatif dibulatkan ke frame (`round(t*30)`), dihitung otomatis oleh `shorts_plan.py`.
`motion` bergiliran: `push` (1.06→1.14), `pan` (x ±22, rot ±0.6), `pull` (1.15→1.06), `tilt` (y +20→−20, rot −1.2→0), kurva inOut cubic.

## Klip 3:4
Sumber lanskap: crop tinggi penuh lebar 3:4 di `cx`; sumber potret (video HP): lebar penuh, tinggi 4:3 di `cy`.
Diskalakan ke 1080x1440 lanczos (+unsharp bila sumber < 900 px), `eq=contrast=1.04:saturation=1.06:gamma=1.02`,
+12 frame ekor untuk crossfade. Sumber 480p jangan dicrop penuh 9:16 (buram) — tampil sebagai kartu.
Salinan sebelum outline disimpan sebagai `sNN.orig.mp4`.

## Pelacakan wajah & badan (`editor/track.py`)
- Wajah: Haar `frontalface_alt2` (OpenCV **4.x**; OpenCV 5 tidak punya Haar). Badan: u2net_human_seg via onnxruntime
  (`reditor models`, ±176 MB) → komponen terbesar = badan; kepala = pita atas 22% tinggi badan (fallback bila wajah
  tak terdeteksi: `[hx, hy+0.35r, 0.9r]`). Tanpa model u2net → HOG person (tanpa outline).
- Hanya shot yang diberi `effect`/`outline` yang dilacak (15 fps; u2net ±0,4 dtk/frame di server, 1–3 dtk di HP).
  Tahan nilai terakhir saat hilang, haluskan moving average 7 sampel, interpolasi ke tiap frame.
- Cakupan < 40% → beri tahu pengguna dan pilih shot lain untuk efek, jangan dipaksakan.

## Outline badan (ditanam, `editor/outline.py`)
Ring putih dari masker (dilate − masker) + glow emas, intensitas per mode: drop `0.35+0.65e^(-a/5)`, fast `0.95e^(-a/4)`
(kilat tiap ketukan), pulse (tiap 2 ketukan), soft untuk outro; `a` = frame sejak ketukan terakhir.

## Komposisi `ShortsBeat` (studio/src/shorts/)
- Latar = klip yang sama `blur(46px) brightness(.5) saturate(1.25)`; kartu 940x1253 di (70, 330), radius 44, bayangan
  lembut, tepi 1,5px putih 28%. Di dalam kartu: wadah 1080x1440 `scale(940/1080)` → wadah gerak berisi video **dan**
  SVG efek, sehingga efek ikut gerak kamera.
- Pemanis: chip "Now Playing" (vinyl berputar, judul + artis, 5 bar equalizer; tampil bila `title` diisi), progress bar
  tipis + 4 titik ketukan, kartu membesar 1,2% per ketukan setelah drop, sapuan cahaya tiap 16 ketukan, cincin tipis
  tiap 8 ketukan, grain 0.07 + vignette.
- Efek menempel (SVG, `drop-shadow(0 0 10px rgba(255,255,255,.55))`), pilih sesuai pose di grid analisis:

| Pose | `effect` | Perilaku |
|---|---|---|
| tangan love, tangan di dada, monyong, cium | `hearts` | hati garis putih (sesekali isi emas) tiap 2 ketukan di samping wajah, naik 6 px/frame, pudar 40 frame |
| senyum ke kamera | `sparkle` | 3 bintang 4 sudut di sekitar wajah, berkelip + membesar di ketukan |
| pose kalem / senyum | `halo` | elips putus-putus emas di atas kepala, berputar, denyut di ketukan |
| menunjuk kamera | `rings` | lingkaran mengembang dari wajah tiap ketukan |
| kepal tangan di drop | `burst` + `outline` | 10 garis radial memancar dari wajah di ketukan |
| kepal / melambai | `arcs` | lengkung swoosh di kedua sisi badan (pathLength + strokeDashoffset) |
| semua shot fast, drop, outro | `outline: true` | garis bercahaya di siluet |
Tidak semua shot diberi efek; sisakan shot polos agar tidak ramai.

## Render di HP
- `--concurrency` ≤ `nproc` (default 2, `REDITOR_CONCURRENCY`). Render penuh bisa kena OOM/SIGKILL → `render_chunks.sh`
  merender per 300 frame (HP 8 GB boleh 600–670 via `REDITOR_CHUNK`), potongan yang sudah ada dilewati, lalu
  digabung + mux `audio_full.m4a`.
- Perbaiki satu shot: hapus potongan `studio/out/parts/p_A-B.mp4` yang memuat shot itu, jalankan render lagi.
- Hanya audio berubah: mux ulang dengan `-c:v copy`.
- Pratinjau cepat: `reditor still ShortsBeat N` (skala penuh) atau `npx remotion still ... --scale=0.5`.

## Cek sebelum kirim
`ffprobe` (durasi, 1080x1920, 30 fps, AAC) + `ebur128=peak=true` (≈ −9 LUFS tanpa VO, peak ≤ −1 dBFS); 6–8 frame
(awal, drop, fast, sambungan potongan, akhir) dilihat dengan Read: subjek tidak terpotong, efek menempel di wajah/badan,
tepi kartu tidak bolong. Kirim (`reditor export` → galeri HP); ringkas perubahan dalam poin; sebut kekurangan tersisa.

## Revisi
Simpan `plan.json`, `analisis/`, `tracks/shorts/`, dan proyek Remotion. Revisi cukup ubah bagian terkait di `plan.json`
lalu `reditor shorts build` (klip yang tidak berubah tetap dipotong ulang cepat) dan render ulang potongan terkait.
