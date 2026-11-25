# reditor-claude-nethunter — panduan untuk Claude

Proyek editor video + motion graphic yang dijalankan dari **terminal Kali NetHunter** (Android arm64, chroot, tanpa GPU).
Komunikasi dengan pengguna memakai **Bahasa Indonesia**.

- Skill utama: `.claude/skills/reditor-nethunter/SKILL.md` — WAJIB dipakai untuk semua permintaan video
  (edit raw footage, motion graphic, takarir, VFX, render). Aturan kerasnya (Gerbang Aset, VO tidak diubah,
  Sumber Fakta, loudness) tidak boleh dilanggar.
- CLI satu pintu: `bin/reditor` (`reditor help`). Mulai dengan `reditor doctor` bila ada error lingkungan.
- Folder input pengguna: `raw-footage/`, `referensi/`, `VO/`, `Musik/`, `VFX/`. Jangan commit media pengguna.
- Tiga alur: `reditor edit` (ffmpeg, footage + VO), `reditor shorts` (Shorts sinkron beat dari footage + musik,
  aturan dari skill video-editor-shorts di `references/shorts-beat.md`), dan `studio/` Remotion (motion graphic).

## Peta kode (graphify)
- Sebelum membaca banyak file, baca `graphify-out/GRAPH_REPORT.md` atau jalankan `graphify explain "NamaKomponen"` /
  `graphify path "A" "B"`. Perbarui setelah menambah/menghapus/mengganti nama komponen: `reditor graph`
  (tambahkan `--force` lewat `graphify update . --force` setelah refaktor yang menghapus file).
- `graphify-out/manifest.json` BUKAN manifest video; manifest video = `studio/manifest.json`.
- Jangan pakai `graphify add <url>`, `graphify hook install`, `graphify watch` dalam alur video.

## Batas perangkat
- Render panjang dijalankan di latar (`nohup ... &`) dan dipantau lewat log; ukur 60 frame dulu, laporkan estimasi.
- RAM kecil: `REDITOR_CONCURRENCY=1`. Browser gagal: `export REDITOR_BROWSER=/usr/bin/chromium`.
