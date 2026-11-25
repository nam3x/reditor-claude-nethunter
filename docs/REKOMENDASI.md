# Rekomendasi: referensi kode yang lebih kuat untuk reditor

Urut dari yang paling berdampak untuk alur HP (NetHunter, arm64, tanpa GPU).

## 1. whisper.cpp — transkripsi per kata paling ringan di HP
- Repo: https://github.com/ggml-org/whisper.cpp
- Kenapa: C/C++ murni, dioptimasi NEON arm64, tanpa PyTorch. Di HP biasanya lebih cepat & hemat RAM
  daripada faster-whisper, dan tetap memberi timestamp per token/kata (`--output-json-full`, `-ml 1`).
- Remotion punya pembungkus resminya: `@remotion/install-whisper-cpp` (+ `@remotion/captions`), sehingga
  transkrip langsung jadi format caption Remotion.
- Saran integrasi: tambahkan backend `--engine whispercpp` di `editor/transcribe.py` yang mengubah JSON
  whisper.cpp ke format `segments[].words[]` yang sudah dipakai `sync_timeline.py` & editor.

## 2. remotion-dev/template-tiktok — takarir gaya TikTok resmi
- Repo: https://github.com/remotion-dev/template-tiktok
- Kenapa: contoh resmi Remotion untuk caption per kata (`createTikTokStyleCaptions`) + whisper.cpp.
  Pola pengelompokan kata & animasinya bisa menggantikan logika manual di `KaraokeCaption.tsx`.
- Catatan: tetap pertahankan aturan skill (safe zone 9:16, kelompok per jumlah karakter, chip sumber).

## 3. PySceneDetect — pilih titik potong raw footage otomatis
- Repo: https://github.com/Breakthrough/PySceneDetect
- Kenapa: mendeteksi pergantian shot di klip panjang, sehingga `reditor edit auto` bisa memilih `in`
  di awal shot yang bersih (bukan asal tengah klip). Python murni + OpenCV, jalan di arm64.

## 4. auto-editor — buang bagian diam/kosong di RAW FOOTAGE
- Repo: https://github.com/WyattBlue/auto-editor
- Kenapa: memotong otomatis bagian tanpa suara/gerak pada footage talking-head atau vlog.
- **Jangan dipakai ke VO** — aturan skill melarang memotong jeda/hening di voiceover.

## 5. Alternatif mesin motion graphic (bila Remotion terlalu berat)
- Revideo — https://github.com/redotvideo/revideo (fork Motion Canvas dengan render headless & API).
- Motion Canvas — https://github.com/motion-canvas/motion-canvas (animasi berbasis generator, editor visual).
- Keduanya tetap memakai browser untuk render, jadi tidak lebih ringan secara drastis di HP; Remotion tetap
  pilihan utama karena ekosistem (`@remotion/three`, captions, Lambda) dan skill ini sudah teruji di sana.

## 6. Yang TIDAK disarankan untuk NetHunter
- editly (https://github.com/mifi/editly): editor deklaratif bagus, tetapi bergantung pada `headless-gl`
  yang sering gagal di-build di arm64/chroot. Editor ffmpeg di `editor/reditor_edit.py` meniru konsepnya
  (EDL JSON → ffmpeg) tanpa dependensi native tambahan.
- MoviePy: mudah, tapi memproses frame di Python (jauh lebih lambat di CPU HP dibanding filtergraph ffmpeg).

## 7. Render berat → pindahkan ke cloud (opsional)
- `@remotion/lambda` atau `@remotion/cloudrun`: HP cukup menyusun manifest & preview `still`, render final di cloud.
  Butuh akun AWS/GCP dan kredensial — hanya jika pengguna memintanya.
