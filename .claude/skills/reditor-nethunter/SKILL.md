---
name: "reditor-nethunter"
description: "Editor video + motion graphic storytelling di terminal Kali NetHunter (Android arm64): Shorts/Reels sinkron beat dari raw footage + musik (video-editor-shorts: goyang kamera seperlunya, motion control, efek menempel di wajah/badan, kartu 3:4 modern clean), Remotion storyteller (Shorts 9:16, YouTube 16:9, hybrid highlight, takarir karaoke per kata, preset stickman/Cetakinds, sumber fakta di video) DIGABUNG editor ffmpeg ringan untuk raw footage (cut, transisi, LUT, VFX light leak/grain/dust, ducking musik, loudnorm). Pakai saat pengguna minta edit video, olah raw footage, motion graphic, takarir karaoke, VFX, atau menyebut reditor/NetHunter/HP."
---

# reditor-nethunter — Director, Editor & Production Skill (Kali NetHunter)

Skill ini adalah turunan `remotion-storyteller` yang disesuaikan untuk berjalan **di HP lewat terminal Kali NetHunter** (chroot arm64, tanpa GPU, RAM terbatas), ditambah **Mode Editor** berbasis ffmpeg untuk raw footage. Semua aturan keras remotion-storyteller tetap berlaku.

## Peta Proyek (baca dulu, jangan cari ulang)
```
raw-footage/   klip & foto mentah dari pengguna            -> studio/public/footage/
referensi/     gambar/video referensi gaya                  -> studio/public/images/ (video -> 12 frame ref_*.jpg)
VO/            voiceover final pengguna (apa adanya)        -> studio/public/audio/voiceover.mp3
Musik/         musik latar (pengguna / bed prosedural)      -> studio/public/music/
VFX/           light-leaks, flares, dust, grain, textures, luts (.cube), transitions, sfx  -> studio/public/vfx/
editor/        reditor_edit.py (editor ffmpeg), transcribe.py, gen_vfx.sh, gen_luts.py,
               beats.py (BPM/beat/drop), track.py (wajah/badan), outline.py, shorts_plan.py (Mode Shorts Beat)
analisis/      grid footage, beats.json, contact sheet shot (dibuat otomatis)
plan.json      rencana shot Mode Shorts Beat (simpan untuk revisi)
studio/        proyek Remotion (manifest.json, src/, scripts/sync_timeline.py, make_contact_sheet.sh, asset_cache.py)
bin/reditor    CLI satu pintu (reditor help)
```
- File pendukung skill ada di `references/` (folder skill ini). Skrip & `theme.ts` SUDAH ada di proyek (`studio/scripts/`, `studio/src/theme.ts`) — jangan tulis ulang dari nol; edit seperlunya.
- Saat melanjutkan proyek, cek `graphify-out/GRAPH_REPORT.md` / `graphify explain "Komponen"` sebelum membuka banyak file.

## Memilih Mesin: Mode Editor vs Mode Remotion (putuskan sendiri, sebut ke pengguna)
| Kondisi | Mesin |
|---|---|
| Bahan utama raw footage (vlog, b-roll, produk, event), butuh cut + transisi + grading + VFX + takarir | **Mode Editor** (`reditor edit ...`, ffmpeg, tanpa browser — 5–20x lebih cepat di HP) |
| Motion graphic, tipografi kinetik, stickman/chibi, 3D, explainer | **Mode Remotion** (`studio/`) |
| Motion graphic yang menyisipkan footage | Remotion dengan adegan `"visualType": "footage"` (+ `footage`, `footageIn`, `vfx`) |
| Shorts/Reels dari raw footage + **musik** (potong sinkron beat, goyang kamera, efek menempel wajah/badan, kartu 3:4) | **Mode Shorts Beat** (`reditor shorts ...`, komposisi `ShortsBeat`) — WAJIB baca `references/shorts-beat.md` |
Semua mesin memakai folder yang sama. Mode Editor & Remotion memakai VO + transkrip; Mode Shorts Beat boleh tanpa VO (edit musik, master ≈ −9 LUFS) dan mengikuti selera pengguna di `references/shorts-beat.md` (tanpa teks di atas video kecuali diminta, garis putih tipis + emas `#E8C27A`, goyang hanya di drop/awal bar/fast).

## Mode Editor (ffmpeg) — alur
1. Gerbang Aset tetap berlaku (raw footage pengguna = acuan visual; VO wajib kecuali montage musik yang dinyatakan pengguna tanpa narasi). Untuk Shorts sinkron beat dengan musik, pakai Mode Shorts Beat.
2. `reditor transcribe` → `transcript.json` (faster-whisper int8, model `small`; HP RAM < 6 GB pakai `--model base`). Lalu ukur tempo (skrip mencetaknya) — audio tidak diubah.
3. `reditor edit auto 9:16` (atau `16:9`) → `edit.json`. Lalu **sutradarai** `edit.json` sesuai naskah/transkrip: urutan klip, `in` (detik mulai di klip), `duration`, `motion` (`kenburns`|`punch`|`none`), `transition` (`fade`, `smoothleft`, `smoothup`, `circleopen`, `zoomin`, `fadeblack`, `slideleft`, `dissolve`, `cut`), `headline`/`subtext`, `vfx` per klip, `audioGainDb` (ambience klip), `sfx` (`{file, at, gainDb}`), `lut`, `lutStrength`, `grain`, `vignette`, `music`, `musicGainDb`, `duck`.
   - Potongan jatuh di batas kalimat/jeda transkrip (lihat `transcript.json`), bukan di tengah kata. Ganti klip tiap 1,5–3,5 dtk untuk Shorts, 3–6 dtk untuk 16:9.
   - Total `duration` boleh beda dari VO: video selalu mengikuti durasi VO (klip terakhir di-freeze/dipotong). VO tidak pernah dipotong/di-stretch.
4. `reditor edit check` → `reditor edit preview` (540p ultrafast) → periksa 4–6 frame dengan ffmpeg `select` + `tile` (satu gambar) → `reditor edit render` (1080p). Cache klip di `.reditor-work/` membuat render ulang hanya memproses klip yang berubah.
5. Verifikasi `ffprobe` (durasi = VO + 0,3 dtk, ada stream audio) dan `ebur128` (≈ −14 LUFS). `reditor export` menyalin ke `/sdcard/Movies/reditor`.

## Resep "Clean Modern" (berlaku untuk kedua mesin)
- **Grading:** satu LUT untuk seluruh video (`clean_bright` default; `teal_orange` sinematik; `moody_film` cerita/emosional; `warm_soft` lifestyle; `bw_contrast` dramatis), `lutStrength` 0,6–0,85. Jangan campur LUT antar klip kecuali untuk flashback.
- **VFX hemat:** light leak/flare maksimal 1 per 3 klip, opacity 0,3–0,6, blend `screen`, ditaruh di transisi atau momen emosi; grain `overlay` 0,08–0,15 di seluruh video; dust/bokeh hanya untuk intro/outro/adegan tenang; vignette 0,25–0,4.
- **Transisi:** ≤ 0,4 dtk; utamakan `cut` + `punch` di ketukan, `smoothleft/whip` untuk ganti topik, `flash`/`light_sweep` hanya di hook/klimaks (maks 2 per video). Hindari transisi "PowerPoint" (wipe bintang, cube, dll).
- **Tipografi:** maksimal 2 bobot font (Inter 800 judul, 500 isi), headline ≤ 7 kata, tanpa outline tebal berwarna; takarir putih + sorotan aksen satu warna.
- **SFX:** whoosh di transisi, pop di teks muncul, impact di klimaks; ±1 SFX per 1–2 dtk maksimum, −12 s/d −18 dB.
- Sumber VFX/musik pihak ketiga hanya dari folder pengguna atau daftar berlisensi di `VFX/README.md`; jangan mengunduh aset berlisensi tidak jelas.

## Menjalankan di NetHunter (batas perangkat)
- Proyek wajib di filesystem chroot (mis. `/root/reditor-claude-nethunter`), bukan `/sdcard` (FUSE: tanpa symlink/izin eksekusi). Hasil disalin dengan `reditor export`.
- Remotion: `studio/remotion.config.ts` sudah mengatur `concurrency=2`, frame JPEG, GL `swangle`, timeout 120 dtk. Untuk RAM < 4 GB: `REDITOR_CONCURRENCY=1`. Jika Chrome Headless Shell gagal: `export REDITOR_BROWSER=/usr/bin/chromium`.
- Render panjang (> 1 menit video) jalankan di latar dan pantau log: `nohup reditor render short > out/render.log 2>&1 &` lalu `tail -f out/render.log`. Minta pengguna mengisi daya HP dan mematikan optimasi baterai untuk NetHunter Terminal.
- Ukur dulu 60 frame (`npx remotion render ... --frames=0-59`) dan laporkan estimasi waktu ke pengguna sebelum render penuh. Adegan 3D di HP sangat lambat: pakai `dpr={0.5}`, `antialias:false`, dan tawarkan versi 2D bila estimasi > 1 jam.
- `reditor doctor` adalah langkah pertama bila ada error lingkungan.

## ATURAN KERAS: Gerbang Aset Sebelum Render (tidak boleh dilanggar)
Dilarang menjalankan render dalam bentuk APA PUN — pratinjau skala 0.5, `make_contact_sheet.sh`, `npx remotion render`, `npm run render:*`, maupun render frame tunggal (`npx remotion still`) — sebelum KEDUA syarat berikut terpenuhi:

1. **Acuan visual** — salah satu dari:
   - **a. Referensi gambar/footage dari pengguna:** minimal 1 file gambar (foto produk, gambar pendukung, atau referensi gaya) di folder `referensi/`, ATAU klip di `raw-footage/` (footage pengguna sendiri juga dihitung acuan visual). `reditor link` menyalinnya ke `studio/public/images/` dan `studio/public/footage/`. Video referensi dari pengguna juga dihitung: ambil 10–12 frame merata dengan ffmpeg, simpan sebagai `public/images/ref_*.jpg` (otomatis oleh `reditor link` untuk video di `referensi/`), lalu ringkas gayanya (dunia, tokoh, palet, posisi takarir, ritme potongan) sebagai style brief; ATAU
   - **b. Style yang disepakati (jika pengguna tidak punya gambar):**
     - Jika pengguna sudah menjelaskan gaya visual di inputnya (mis. "minimalis hitam-emas", "neon futuristik", "kartun flat cerah"), jadikan deskripsi itu acuan. Ringkas kembali menjadi *style brief* singkat dan minta pengguna mengonfirmasinya.
     - Jika pengguna belum menyebut gaya, TAWARKAN 3–4 pilihan style yang cocok dengan topik video (gunakan AskUserQuestion bila tersedia). Tiap pilihan berisi: nama style, palet warna (3–5 hex), tipografi, gaya grafis/ilustrasi, dan nuansa gerak (mis. tenang/cepat/memantul). Pengguna boleh memilih salah satu atau menulis gayanya sendiri.
     - Jika topik berupa fakta unik, sains, "kok bisa", cerita tokoh lucu dengan pelajaran, skenario "bayangkan kalau…", atau tips (umumnya Shorts 9:16), salah satu pilihan WAJIB preset **Stick-figure Kok Bisa (Cetakinds)** (lihat `references/style-stickfigure.md`). Preset ini juga dipakai bila pengguna menyebut "stickman", "animasi doodle", "kepala bulat", atau "seperti video Cetakinds".
     - Jika topik berupa sejarah, peristiwa, konflik, geopolitik, biografi, atau "kenapa/kok bisa X terjadi", salah satu pilihan WAJIB preset **Explainer Sejarah Chibi** (lihat `references/style-explainer-sejarah.md`). Preset ini juga dipakai bila pengguna menyebut "gaya Kok Bisa", "chibi", "countryball", atau "seperti video referensi sejarah".
     - Jika pengguna menyebut kode gaya **A1–A8 atau B1–B7**, "stickman director", atau gaya seperti "pixel theater", "rubber hose", "TV retro", "amber noir", "hitam putih klasik", tawarkan atau pakai preset dari `references/stickman-director.md`. Untuk topik stickman umum, preset itu boleh menjadi pilihan tambahan di samping Stick-figure Kok Bisa. Sebelum dikonfirmasi, sebut tingkat kelayakannya di Remotion (Penuh / Mendekati / Terbatas) sesuai tabel di referensi itu.
     - Style yang sudah dikonfirmasi pengguna dicatat sebagai objek `"style"` di `manifest.json` (nama, palet, font, gaya grafis, nuansa gerak) dan diterapkan dengan menyesuaikan nilai di `theme.ts`. Visual dibuat murni dengan kode (bentuk, ikon SVG, gradien, tipografi kinetik, objek 3D primitif) mengikuti style tersebut.
     - Style yang belum dikonfirmasi pengguna TIDAK dihitung sebagai acuan visual.
2. **Voiceover (wajib, tanpa pengganti)** — file audio voiceover final dari pengguna di folder `VO/` (disalin apa adanya ke `studio/public/audio/voiceover.mp3` oleh `reditor link`), beserta transkrip per kata (`reditor transcribe` → `transcript.json`, format WhisperX). Pengecualian hanya untuk edit musik tanpa narasi: **Mode Shorts Beat** (footage + musik), atau montage musik di Mode Editor yang dinyatakan pengguna tanpa voiceover.

Selama syarat belum lengkap:
- BOLEH: menulis naskah voiceover, menawarkan/menyusun style brief, menyusun `manifest.json`/storyboard, menjalankan `sync_timeline.py` tanpa transkrip untuk estimasi, menulis kode komponen Remotion, dan mengambil aset yang SUDAH ADA di cache GitHub (cache HIT tidak termasuk render).
- TIDAK BOLEH: render apa pun (termasuk `reditor still`, `reditor sheet`, `reditor render`, `reditor edit preview/render`); mengambil gambar stok dari internet atau memakai placeholder sebagai "referensi gambar"; memakai suara TTS/sintetis sebagai pengganti voiceover pengguna; atau memilih style sendiri tanpa konfirmasi pengguna.
- Setelah pekerjaan yang boleh selesai, BERHENTI dan beri tahu pengguna dengan jelas apa yang masih kurang (acuan visual — gambar atau konfirmasi style — dan/atau voiceover) beserta lokasi penyimpanan file. Tunggu sampai pengguna melengkapinya.
- Permintaan seperti "render dulu saja" atau "coba lihat hasilnya" tetap tidak membuka gerbang ini selama syarat belum lengkap; ingatkan pengguna apa yang dibutuhkan.

Sebelum render pertama, lakukan pemeriksaan aset: pastikan ada gambar di `public/images/` ATAU objek `style` yang sudah dikonfirmasi di `manifest.json`; pastikan file voiceover ada dan bisa dibaca `ffprobe` (memiliki stream audio dan durasi > 0); ukur tempo voiceover tanpa mengubah audionya (lihat Tempo Voiceover); lalu jalankan ulang `sync_timeline.py` DENGAN `--transcript` agar timeline mengikuti voiceover final. Hanya jika semua lolos, lanjut ke Fase 3.

## ATURAN KERAS: Sumber Fakta Tampil di Video
Setiap fakta asli di naskah (angka, tanggal, nama, tempat, peristiwa sejarah, sebab-akibat ilmiah) wajib punya sumber, dan sumbernya tampil di video.

1. **Riset:** WebSearch/WebFetch setiap klaim. Buka halaman sumbernya dan pastikan halaman itu memang menyatakan klaim tersebut. Angka kunci idealnya didukung 2 sumber. Prioritas: lembaga resmi/pemerintah, universitas, jurnal, arsip/museum, ensiklopedia, lalu media kredibel. Hindari forum, konten AI, dan blog tanpa penulis. Jangan pernah mengarang URL, judul, penulis, atau tahun; tulis hanya yang benar-benar terlihat di halaman.
2. **Klaim yang tidak bisa diverifikasi:** buang, atau ubah menjadi bahasa ragu ("menurut cerita warga", "diduga") tanpa chip sumber.
3. **Catat di `manifest.json`** sebagai array `"sources"`: `{ "short": "≤28 karakter, mis. KAI Heritage", "year": "", "full": "judul lengkap + penerbit", "url": "...", "claim": "klaim yang didukung", "scenes": ["id adegan saat klaim diucapkan"] }`.
4. **Tampil otomatis di tiga tempat:** (a) komponen `SourceChip`, yaitu pil gelap transparan "Sumber: X · Y" (Poppins 700 ±30 px, fade 0,25 dtk) tepat di bawah takarir selama adegan di `scenes` (vertikal y ≈ 74,8%; 16:9 di atas karaoke); (b) daftar "Sumber:" di end card (maksimal 4, yang terpenting dulu, format "short (year)"); (c) `out/caption.txt` untuk deskripsi unggahan berisi judul, deskripsi, sumber bernomor (`full` + `url`), dan hashtag.
5. **Tokoh/tempat rekaan** (cerita ilustrasi yang memuat fakta asli): isi `"disclaimer": "Tokoh & tempat ilustrasi"` di manifest. Label kecil ini tampil di atas (y ≈ 12,5%) pada 0–3 detik pertama.
6. Topik tanpa fakta (tips perasaan, skenario fiksi) tidak butuh sumber, kecuali bagian yang berupa fakta (mis. "olahraga melepas endorfin" tetap diberi sumber).
7. Naskah diserahkan bersama tabel **klaim → sumber**. Saat pengecekan contact sheet, chip sumber harus muncul tepat saat klaimnya diucapkan.

## Tempo Voiceover: Diatur Lewat Naskah, Audio Tidak Diubah
**ATURAN KERAS: voiceover dari pengguna dipakai apa adanya.** DILARANG mempercepat atau memperlambat VO dengan cara apa pun (`atempo`, `rubberband`, `asetrate`, time-stretch, atau setara), dan DILARANG memangkas jeda/hening di dalamnya (`silenceremove`, potong-sambung `atrim`/`concat`). Durasi video mengikuti durasi VO asli. Trek VO sendiri tidak diolah; yang boleh hanya menambahkan musik dan efek suara DI BAWAH VO (lihat Musik & Efek Suara) dan normalisasi loudness pada mix akhir (Fase 3), karena keduanya tidak mengubah kecepatan maupun timing VO.

Tempo yang enak didengar (**2,7–3,2 kata/detik**; konten energik/Shorts di sisi atas, penjelasan teknis di sisi bawah, tidak di bawah 2,5) dicapai lewat naskah dan arahan pengisi suara, bukan dengan mengolah audio.

1. **Saat menulis naskah (sebelum voiceover direkam):**
   - Kalimat pendek, 6–12 kata per kalimat; buang kata pengisi ("jadi", "nah", "seperti yang kita ketahui", pengulangan).
   - Anggaran kata = durasi target (detik) × 2,9. Contoh: video 45 detik ≈ 130 kata. Jika naskah melebihi anggaran, padatkan — jangan memperpanjang video.
   - Sertakan catatan untuk pengisi suara di atas naskah: "Baca dengan tempo sedang-cepat dan bersemangat, jeda singkat antar kalimat, tanpa jeda panjang."
2. **Setelah voiceover diterima, ukur temponya saja** dari transkrip: kata/detik = jumlah kata ÷ (waktu kata terakhir − waktu kata pertama), serta catat jeda antar kata yang lebih dari 0,6 detik. Saat menghitung kata, angka dihitung sesuai jumlah kata yang diucapkan ("1864" = 4 kata), bukan satu token. Salin file pengguna ke `public/audio/voiceover.mp3` tanpa diolah.
3. **Jika tempo di bawah 2,6 kata/detik atau banyak jeda panjang**, JANGAN mengubah audio. Laporkan ke pengguna dalam satu kalimat (tempo terukur dan durasi VO), lalu tawarkan dua pilihan: lanjut dengan VO apa adanya (video mengikuti durasinya), atau rekam ulang dengan arahan tempo lebih cepat. Jika pengguna tidak ada untuk ditanya, lanjut dengan VO apa adanya.
4. Untuk mengisi jeda panjang secara visual, jaga layar tetap hidup (micro-motion, kamera bergerak, elemen pop-in) — bukan dengan memotong audio.

## Musik & Efek Suara (boleh ditambahkan, tidak boleh lebih keras dari VO)
Skill boleh menambahkan musik latar dan efek suara (SFX) sesuai kebutuhan adegan, tanpa perlu ditanyakan dulu.
- **Sumber:** pakai file musik/SFX dari pengguna bila ada. Jika tidak ada, buat sendiri secara prosedural dengan kode (ffmpeg `sine`/`anoisesrc`/`aevalsrc` atau numpy → WAV), misalnya whoosh dari noise yang di-sweep, pop/klik dari sinus pendek dengan envelope, ding, langkah kaki, detak jam, dan bed musik sederhana (pad akor + ketukan lembut). Jangan mengunduh musik/SFX dari internet dan jangan meniru lagu yang ada.
- **Kapan dipakai:** SFX untuk momen yang terlihat di layar, misalnya pop-in label, centang, coretan, notifikasi HP, pintu, langkah, transisi, dan tombol ikuti. Paling banyak ±1 SFX per 1–2 detik, supaya tidak ramai. Musik mengikuti suasana (tegang, hangat, lucu) dan boleh berganti di pergantian babak.
- **Sinkron:** waktu SFX diambil dari frame yang sama dengan animasinya (`wf()`/`startFrame` adegan + offset), lalu dipasang sebagai `<Sequence from><Audio src volume/></Sequence>` di Remotion, atau di-mix dengan ffmpeg `adelay`.
- **ATURAN KERAS loudness:** musik dan SFX tidak boleh lebih keras dari VO.
  - Musik di bawah VO dengan selisih ±18–22 LU, dan diturunkan lagi (ducking, mis. `sidechaincompress` dengan VO sebagai sidechain, atau volume rendah statis) selama ada ucapan.
  - Puncak SFX minimal 6 dB di bawah puncak VO di sekitarnya.
  - Fade-in/out musik 0,5–1 detik.
  - Setelah mix, cek dengan `ebur128`/`astats` pada trek terpisah: loudness musik dan SFX harus jelas di bawah loudness VO. Kalau tidak, turunkan musik/SFX, bukan menaikkan atau mengubah VO.
- Laporkan singkat di akhir musik/SFX apa yang dipakai, dan tawarkan versi tanpa musik bila pengguna mau.

## Cache Aset PNG di GitHub (pakai ulang, jangan render ulang)
**Repo cache aset (opsional di HP):** `nam3x/remotion-story-template`, branch `asset-cache`, folder `asset-cache/`. Di NetHunter, cache hanya dipakai bila `git` sudah punya kredensial GitHub (mis. `gh auth login` atau token di credential helper); jika tidak, lewati cache tanpa bertanya dan render lokal. Tambahkan `--branch asset-cache --subdir asset-cache` di setiap perintah `asset_cache.py` (get/put/init). Jika repo belum terhubung ke sesi, hubungkan dengan akses push lalu clone dangkal sebelum get/put. Versi `studio/scripts/asset_cache.py` sudah mendukung `--branch`, `--subdir`, dan `deps` (teruji: branch dibuat otomatis bila belum ada, perubahan file `deps` mengubah kunci cache). Jika `scripts/asset_cache.py` di repo tersebut lebih baru, pakai versi repo; jika repo tidak terjangkau, pakai versi `studio/scripts/`.

- **Yang di-cache:** aset PNG statis yang dibuat skill — background, ilustrasi, kartu grafis, frame objek 3D, logo/teks yang dirender sebagai gambar. Video MP4 final TIDAK di-cache dan tetap dirender tiap proyek (animasi dihitung per frame).
- **Bukan untuk file pengguna:** referensi gambar, voiceover, dan transkrip dari pengguna TIDAK diunggah ke repo kecuali pengguna secara eksplisit memintanya.
- **Repo wajib private.** Saat pertama kali dipakai jalankan `python3 studio/scripts/asset_cache.py init --repo <REPO>`: membuat repo private jika belum ada, atau memperingatkan jika repo ternyata public (jika public, berhenti dan tanyakan pengguna sebelum mengunggah apa pun).
- **Alur per aset** (tulis `spec.json` per aset: `name`, `project`, `component`, `props`, `style`, `width`, `height`, dan `deps` = daftar file kode lain yang ikut menentukan tampilan, mis. `src/components/Art.tsx`, agar perubahan gambar ikut mengubah kunci cache):
  1. `python3 studio/scripts/asset_cache.py get --repo <REPO> --spec spec.json --dest public/cache/`
  2. **HIT (exit 0):** pakai file di `public/cache/<name>.png` lewat `staticFile()`; JANGAN render ulang aset itu.
  3. **MISS (exit 3):** jika Gerbang Aset sudah terbuka, render dengan `npx remotion still`, lalu langsung simpan otomatis: `python3 studio/scripts/asset_cache.py put --repo <REPO> --spec spec.json --file <png>`.
- Kunci cache dihitung otomatis dari komponen + isi file kodenya + props + style + ukuran; jika salah satu berubah, aset dianggap baru. Jangan menghitung atau mengarang kunci sendiri.
- Jika repo tidak bisa diakses atau push gagal: lanjutkan dengan aset lokal, jangan berhenti, dan laporkan ke pengguna di akhir bahwa aset belum tersimpan ke GitHub.
- Di akhir proyek laporkan singkat: berapa aset diambil dari cache (HIT) dan berapa yang baru dirender lalu disimpan.

## Peta Kode Proyek dengan graphify (hemat token)
Pakai graphify untuk memetakan kode proyek Remotion (komponen, import, pemanggilan, `theme.ts`) sebagai knowledge graph, supaya saat menulis, merevisi, atau melanjutkan proyek Claude cukup menanyai graph alih-alih membaca ulang banyak file.

- **Pasang:** sudah dipasang oleh `install/nethunter-setup.sh`. Cek dengan `command -v graphify`; jika belum ada: `pip install --break-system-packages -q graphifyy` (nama paket PyPI pakai dua huruf y; CLI-nya tetap `graphify`), atau `pipx install graphifyy`. Jika tetap gagal, lanjutkan tanpa graphify dan jangan berhenti.
- **Bangun/perbarui peta:** `reditor graph` (= `graphify update <root repo>`), memetakan `studio/` dan `editor/` sekaligus. Mode ini hanya mengekstrak kode lewat AST, tanpa LLM dan tanpa API key; hasilnya di `graphify-out/` (`graph.json`, `GRAPH_REPORT.md`, `graph.html`). Jalankan setelah kerangka komponen pertama selesai ditulis di Fase 2, lalu ulangi setelah setiap perubahan kode yang menambah, menghapus, atau mengganti nama komponen. Setelah refaktor yang menghapus file, tambahkan `--force`.
- **Pakai sebelum membuka file:**
  - `GRAPH_REPORT.md` dibaca sekali untuk gambaran struktur.
  - `graphify explain "NamaKomponen"` untuk melihat siapa yang mengimpor/memanggil komponen itu sebelum mengubahnya (mis. `KaraokeCaption`, `SourceChip`, `StoryScene`).
  - `graphify path "A" "B"` untuk melacak alur, mis. dari `RemotionRoot` ke `theme`, saat mencari kenapa warna/font/easing tidak berubah.
  Setelah itu baca hanya file yang ditunjuk graph.
- **Batas pemakaian:**
  - Yang dipetakan hanya kode proyek. Jangan menjalankan ekstraksi semantik graphify (dokumen, catatan riset, halaman web) untuk naskah: relasi berlabel `INFERRED` adalah tebakan model, bukan fakta, sehingga tidak boleh dipakai sebagai dasar klaim naskah atau chip sumber. Riset tetap mengikuti Aturan Keras: Sumber Fakta.
  - Jangan memakai `graphify add <url>`, `graphify hook install`, `graphify watch`, atau `graphify install` di dalam alur video ini.
  - `graphify-out/` berisi file bernama `manifest.json` milik graphify; itu BUKAN manifest video. Manifest video tetap `manifest.json` di root proyek.
  - Tambahkan `graphify-out/` ke `.gitignore`, jangan masukkan ke `public/`, ke `deps` aset cache, atau ke repo cache aset.
- graphify bukan render, jadi boleh dijalankan sebelum Gerbang Aset terbuka.

## Fase 0: Gerbang Konfirmasi (WAJIB DIJALANKAN PERTAMA)
Sebelum menyusun naskah, storyboard, atau menulis satu baris pun kode, ajukan pertanyaan konfirmasi singkat kepada pengguna untuk memilih mode output:
1. **Mode A — Video Pendek Saja (9:16 | 1080x1920 | 15–60 detik):** Ritme cepat untuk YouTube Shorts / Reels / TikTok.
2. **Mode B — Video Panjang Saja (16:9 | 1920x1080):** Alur narasi penuh untuk YouTube reguler.
3. **Mode C — Hybrid (9:16 Full 8–10 menit + 9:16 Short 60 detik–3 menit):** 
   - **ATURAN TERKUNCI (ditetapkan pengguna; jangan diubah, dilonggarkan, atau ditafsirkan ulang tanpa permintaan eksplisit pengguna):**
     - **Full:** vertikal 9:16 (1080x1920), durasi **8–10 menit**. Anggaran naskah ±1.400–1.750 kata (durasi × 2,9). Dirender dengan komposisi `ShortVertical` (timeline penuh).
     - **Short:** vertikal 9:16 (1080x1920), durasi **minimal 60 detik, maksimal 3 menit**, diambil dari adegan `"highlight": true` dengan basis komponen yang sama (komposisi `HighlightVertical`).
     - Hybrid TIDAK memakai 16:9 kecuali pengguna memintanya.

*(Tanyakan juga apakah pengguna sudah menyiapkan file voiceover/audio atau ingin dibuatkan naskah terlebih dahulu, dan apakah pengguna punya referensi gambar. Jika tidak punya gambar, pakai gaya yang disebut pengguna di inputnya sebagai style brief untuk dikonfirmasi, atau tawarkan 3–4 pilihan style. Jika **Repo cache aset** masih `BELUM DIATUR`, tanyakan juga nama repo GitHub untuk cache. Sampaikan sejak awal bahwa video baru akan dirender setelah acuan visual (gambar atau style yang dikonfirmasi) DAN voiceover diterima — lihat Aturan Keras: Gerbang Aset Sebelum Render).*

---

## Fase 1: Perencanaan, Storyboard & Sinkronisasi Takarir (`manifest.json`)
- Baca `references/story-beats.md` untuk pola babak narasi dan aturan *safe zone*.
- **Larangan Matematika Token:** Jangan pernah menghitung nomor *frame* atau milidetik secara manual di dalam penalaran, dan **jangan menulis `durationInFrames`** di manifest. Tulis `captionText` (kalimat voiceover adegan itu), `anchor` opsional (2–4 kata pertama yang diucapkan di adegan itu; default = 3 kata pertama `captionText`), dan tingkat energi (`T1` tenang, `T2` transisi/penekanan, `T3` klimaks).
- **Audio:** simpan voiceover di `public/audio/voiceover.mp3` dan isi `"audioPath": "audio/voiceover.mp3"` di manifest. Transkrip per kata dibuat dengan WhisperX (`segments[].words[]` atau `word_segments[]`). Jika WhisperX atau unduhan model diblokir jaringan, pakai `faster-whisper` (`word_timestamps=True`, `language="id"`) dengan output format `segments[].words[]` yang sama; decode audio lewat ffmpeg ke array 16 kHz jika `av.open` error. Jika unduhan model Whisper juga diblokir (HuggingFace/OpenAI tidak bisa diakses), buat transkrip dengan menyelaraskan teks `captionText` ke audio: deteksi jeda (`silencedetect`), pasangkan setiap batas kalimat ke jeda yang paling cocok durasinya (dynamic programming berdasarkan jumlah suku kata), lalu bagikan waktu kata per suku kata di dalam kalimat. Tulis hasilnya dalam format `segments[].words[]` dan beri tahu pengguna bahwa waktu per kata adalah perkiraan. Selaraskan dua tingkat: batas kalimat dicocokkan ke jeda ≥0,25 detik, lalu batas koma ke jeda ≥0,12 detik di dalam kalimat (jika jeda kurang, bagi waktu per suku kata). Hitung suku kata sesuai ucapan, bukan tulisan: angka digit ("2025" = dua-ri-bu-dua-pu-luh-li-ma = 8), singkatan ("AI" = 2), dan kata Inggris ("scroll" = 1) diberi override. Setelah selaras, cek laju suku kata per kalimat (biasanya 5–6 suku/detik). Kalimat yang lajunya menyimpang jauh dari kalimat lain berarti batasnya tergeser ke jeda yang salah; pindahkan batas ke jeda yang membuat laju kalimat-kalimat di sekitarnya konsisten. **Jika pengguna mengirim file SRT**, jangan menyelaraskan ulang per jeda frasa (cara itu bisa memampatkan kata sampai durasinya hampir nol): pakai waktu tiap baris SRT sebagai batas kalimat, rapikan tepinya dengan jeda ≥0,12 detik, lalu bagi waktu kata secara proporsional per suku kata (koma/titik dua diberi bobot jeda ±1,5 suku). Jika setelah tepi dirapikan laju baris itu melebihi ±6,3 suku/detik, berarti jeda yang terdeteksi keliru (biasanya awal kalimat yang diucapkan pelan), jadi pakai waktu asli SRT. Satu baris SRT cocok dijadikan satu adegan (±3–5 detik) agar ritme potongan mengikuti video referensi.
- **Perbaikan transkrip:** Whisper sering memecah kata berulang ("Tiba" + "-tiba") sehingga anchor gagal ditemukan; gabungkan potongan berawalan `-` sebelum `sync_timeline.py`. Setelah sync, pakai ejaan `captionText` untuk teks takarir (waktu tetap dari transkrip) agar salah dengar (mis. "berfikir", "print kipia") tidak tampil di layar. Segera setelah transkrip ada, jalankan pemeriksaan **Tempo Voiceover** (hanya mengukur dan melaporkan; audio tidak diubah).
- **Verifikasi sinkron takarir:** setelah sync, pilih 4–6 kata kunci yang tersebar (tahun, nama, angka) dan cocokkan ke audio dengan mentranskripsi potongan 2 detik di sekitar waktu kata itu (Whisper apa pun yang tersedia). Kata itu harus terdengar di potongan tersebut. Pemeriksaan ini pernah menemukan takarir video "stasiun-pertama" muncul 1–3,5 detik lebih awal dari suaranya, sementara penyelarasan jeda + suku kata justru tepat. Jika HuggingFace diblokir, model Whisper ONNX bisa diambil dari rilis GitHub `k2-fsa/sherpa-onnx` (tag `asr-models`, mis. `sherpa-onnx-whisper-small.tar.bz2`) lalu dijalankan dengan `pip install sherpa-onnx`. Model ini tidak memberi waktu per kata, jadi dipakai untuk verifikasi potongan pendek; waktu kata tetap dari penyelarasan jeda. Setelah penyelarasan kalimat, haluskan di dalam kalimat dengan jeda mikro (`silencedetect` d=0,05 dtk, −36 dB): tempelkan tiap jeda mikro ke batas kata terdekat (≤0,9 dtk) lalu bagi ulang per suku kata di antara titik tetap. Di proyek "Akar" langkah ini menurunkan selisih terbesar dari ±0,8 ke ±0,3 dtk.
- **Naskah:** ikuti anggaran kata dan aturan kalimat pendek di bagian **Tempo Voiceover** agar voiceover tidak bertele-tele, dan tulis dengan **Gaya Naskah Retensi** di bawah.

### Gaya Naskah Retensi (bikin penasaran sampai habis)
Setiap naskah ditulis supaya penonton tidak swipe dan menonton sampai akhir.
1. **Hook di kalimat pertama (≤12 kata, 0–3 detik):** langsung ke kontradiksi, klaim mengejutkan, atau pertanyaan yang taruhannya jelas. Contoh: "Mantan paling menyesal bukan saat kamu marah, tapi saat kamu melakukan ini." Dilarang membuka dengan salam, perkenalan, atau "di video ini kita akan…".
2. **Buka loop:** di 5 detik pertama, janjikan sesuatu yang baru dijawab di akhir ("…dan langkah terakhir paling sering gagal"). Jangan bocorkan jawabannya di tengah.
3. **Re-hook tiap 8–12 detik:** pakai kalimat pemancing seperti "Tapi ini belum cukup.", "Nah, di sinilah kebanyakan orang salah.", atau penanda progres ("Langkah kedua…"). Video 60 detik minimal punya 3 re-hook. Tandai re-hook dengan `*` di naskah agar pengisi suara membacanya lebih pelan dan menekan.
4. **Naik bertahap:** urutkan poin dari yang paling ringan ke yang paling kuat. Twist atau fakta terbesar ditaruh di sekitar 75–85% durasi, sebelum CTA.
5. **Konkret dan personal:** pakai angka, nama, tempat, dan detail spesifik. Sapa penonton langsung ("kamu"/"lo", sesuai gaya pengguna). Tunjukkan konflik atau taruhannya.
6. **Payoff jujur:** semua yang dijanjikan hook harus terjawab di video. Jangan pakai clickbait palsu, karena penonton yang merasa tertipu langsung swipe dan itu merusak retensi.
7. **Ending yang memutar ulang:** kalimat terakhir sebelum CTA menutup loop dan menggemakan kata kunci hook, supaya replay terasa mulus. CTA pengguna ditaruh setelah payoff, bukan di tengah.
8. **Pancing komentar (opsional):** satu pertanyaan opini dua pilihan tepat sebelum CTA ("Kamu tim move on diam-diam, atau tim pamer?").
9. **Teks layar di frame pertama** mengulang inti hook (3–6 kata), supaya penonton yang menonton tanpa suara tetap tertahan.

**Kerangka naskah dari video referensi** (pilih satu sesuai topik dan sebut pilihannya ke pengguna, tidak perlu ditanyakan):
- **A. Paradoks / "kok bisa"** (survivorship bias pesawat, Tembok Besar Cina, koboi "never draw first", SPBU): hook berupa paradoks yang dinyatakan sebagai fakta ("[Subjek] ini [melakukan hal mustahil] tanpa [syarat wajar]") dengan aksi di frame 0 → penempatan waktu/tempat dalam satu kalimat pendek ("Perang Dunia Kedua, tahun 1943.") → logika umum yang terdengar benar, ditutup "Masuk akal, kan?" → tokoh aneh/ahli membantah, orang lain menganggapnya gila, kata kunci diulang sebagai pertanyaan ("Tunggu… tidak pernah kena?") → mekanisme dengan "Nah, begini masalahnya." + analogi sehari-hari (HP jatuh dari meja tertangkap refleks); ini shot penjelas terpanjang → nama konsep + angka konkret → payoff yang menggemakan kata kunci hook, kalimat terakhir pendek bertenaga ("Cukup satu kunci.").
- **B. Cerita tokoh dengan running gag** (SPBU "mulai dari nol", desa yang mematikan lampu saat hujan): tokoh lokal (pengawas, ojol, Pak RT, warga baru dari kota), dialog dalam kutip, satu kalimat khas diulang 3–4 kali lalu dipakai lagi sebagai punchline, boleh ditutup twist komedi. Fakta ilmiahnya bersumber, tokohnya rekaan, jadi isi `disclaimer`.
- **C. Skenario "Bayangkan…"** (internet mati sebulan): "Bayangkan besok pagi kamu…" → tahapan waktu ("Hari pertama… Hari kedua… Minggu pertama… Tapi di minggu kedua…") dengan perubahan nada di tengah (kacau → hangat), ditutup pertanyaan dua pilihan.
- **D. Fakta bertahap / tips** (stasiun pertama, Italian brainrot, mantan): penanda urutan ("Pertama/Kedua/Ketiga", "Jam pertama/Sore/Malam", tanggal), nama, tempat, dan angka spesifik, lalu satu kalimat moral singkat sebelum CTA.
- **E. Lima tahap retensi** (cocok untuk sains, psikologi, bisnis, dan pengembangan diri; dari stickman-video-director): hook berupa pertanyaan berlawanan intuisi atau paradoks visual → patahkan anggapan umum dalam satu kalimat → buka mekanisme tersembunyi → kebenaran inti (momen "aha") → punchline dan satu pertanyaan diskusi. Untuk preset A3, A7, dan B4 pakai setup → eskalasi → payoff ironis tanpa pertanyaan diskusi; untuk B7 tutup dengan renungan.
- **F. Cerita absurd sebab-akibat / aturan aneh kampung** (warung yang "memenjarakan" pisang sampai Jumat, kampung yang melarang warganya berjalan seirama; 80–95 dtk, tempo terukur 2,6–2,7 kata/dtk, ±225–240 kata). Urutan:
  1. **Aturan aneh dinyatakan datar sebagai fakta** lewat benda bertulisan atau dialog dalam kutip, lalu tempat dikunci: "Karung di bawah meja bertuliskan pisang tahanan, bebas hari Jumat." / "'Langkahnya jangan kompak, Pak!' kata penjaga jembatan gantung itu." Keanehan inti harus ada di 12 kata pertama.
  2. **Ritual aneh 2–3 kalimat detail** (diikat rapat, papan zig-zag, dua radio beda tempo, peluit acak). Pemegang aturan TIDAK menjelaskan alasannya ("tanpa pernah menjelaskan apa kesalahan pisang itu", "hanya menunjuk gelas tehnya"): ini loop yang dibuka.
  3. **Petunjuk sains ditanam sebagai pengamatan kecil** yang tampak sepele (mangga di karung menguning 3 hari, di rak seminggu; gelas teh bergetar saat dua orang menyeberang sejajar). Nanti jadi bukti.
  4. **Pelanggar datang dengan alasan masuk akal + taruhan bertenggat** (Senin pesan 10 mangga untuk rujak Sabtu; pensiunan pelatih gerak jalan + lomba 17-an). Pelanggar bukan penjahat.
  5. **Pelanggaran bertahap dengan penanda waktu** ("Tiap sore… Kamis sore… Jumat pagi…", "Sabtu pagi… Di langkah kesepuluh…") dan eskalasi fisik 3 langkah yang terlihat (ayunan makin lebar → tali berderit → teh tumpah).
  6. **Akibat terbalik di ±70%**: hasil berlawanan dengan harapan pelanggar (mangga sekeras batu; jembatan berayun).
  7. **Penjelasan sains 1–2 kalimat oleh tokoh bijak sambil melakukan aksi kecil** ("Sambil mengelap meja, Mbah Karyo bilang…"), bahasa awam tanpa istilah teknis ("melepas gas", bukan etilena; "mendorong berulang kali di irama yang sama", bukan resonansi).
  8. **Penutup ironis yang membalik kata kunci**, satu kalimat, tanpa moral dan tanpa pertanyaan: "…kecuali Danu yang sudah mengernyit sejak hari Jumat." / "…menyeberang dengan langkah paling berantakan, lalu berbaris rapi lagi di seberang."
  Ciri bahasa: narator orang ketiga datar seperti dongeng (humor deadpan); metafora dijaga konsisten sampai akhir (pisang = tahanan → "membebaskan tahanan"; lantai papan "ikut berbaris"); dua tokoh lokal bernama (pemegang aturan + pelanggar) dengan peran jelas (pemilik warung, anaknya 12 tahun; penjaga pos, pensiunan pelatih); angka spesifik (10 mangga, 20 bapak, langkah kesepuluh); kalimat panjang 15–20 kata diselingi fragmen pendek ("Kiri, kanan, kiri."). Konsep sains tetap bersumber (chip sumber); tokoh dan tempat rekaan → isi `disclaimer`. Referensi tidak memakai CTA; untuk brand Cetakinds CTA tetap ditaruh setelah kalimat penutup ironis.
- Untuk semua kerangka: fragmen boleh dipakai untuk menekan ("Bukan sejam. Sebulan penuh."); kata re-hook yang terbukti dipakai referensi adalah "Tapi…", "Tunggu…", "Nah…", "Masalahnya…", "Sampai suatu pagi…"; setiap angka, tahun, dan nama tempat adalah momen visual (cap tahun, angka bergulir, papan nama). Register dipilih satu dan konsisten: santai-gaul untuk cerita lucu, baku-ringan untuk sejarah/sains. Untuk brand Cetakinds, CTA ditulis persis **"Pencet tombol ikuti buat tambah wawasan bareng Cetakinds."**, dan kata "Pencet" menjadi jangkar end card.

Sebelum menyerahkan naskah, cek juga bahwa setiap klaim fakta punya sumber terverifikasi (lihat Aturan Keras: Sumber Fakta Tampil di Video), lalu sertakan tabel klaim → sumber. Sebelum menyerahkan naskah, cek dulu: hook ≤12 kata di kalimat pertama; ada loop yang dibuka di awal dan ditutup di akhir; ada ≥3 re-hook untuk 60 detik; twist di 75–85%; semua janji hook terpenuhi; dan naskah masih dalam anggaran kata. Saat menyerahkan, jelaskan singkat letak hook, loop, re-hook, dan twist-nya.
- **Penandaan Hybrid & 3D:**
  - Jika pengguna memilih **Mode C**, tandai adegan paling kuat dengan `"highlight": true` sampai total durasi highlight 60–180 detik (cek `highlightDurationInFrames` dari `sync_timeline.py`). Pilihan highlight wajib membentuk cerita utuh yang berdiri sendiri: hook, buildup inti, twist/payoff, dan penutup. Jika total di luar 60–180 detik, tambah/kurangi adegan highlight; jangan mengubah audio.
  - Jika adegan menggunakan objek 3D, set `"visualType": "3d-showcase"` dan isi `"modelPath": "models/nama-file.glb"`.
- Jalankan skrip lokal (0 token penalaran). Skrip mencocokkan anchor ke transkrip: adegan mulai tepat saat anchor-nya diucapkan dan berakhir saat adegan berikutnya mulai, lalu memetakan takarir karaoke per kata dan `audioStartFrame` untuk potongan highlight:
  `reditor sync` (= `python3 scripts/sync_timeline.py --manifest manifest.json --transcript transcript.json` di `studio/`)
  Tanpa voiceover (naskah dulu): hilangkan `--transcript`; durasi diperkirakan dari jumlah kata `captionText`. Jalankan ulang dengan transkrip setelah audio jadi.
- Baca baris `[WARN]` dari skrip: anchor tidak ditemukan berarti teks manifest berbeda dari ucapan — perbaiki `anchor`, jangan menghitung frame sendiri.

## Fase 2: Implementasi Kode Remotion (2D, 3D & Karaoke Captions)
- Baca `references/motion-2d.md` sebelum menulis komponen 2D, dan baca `references/motion-3d.md` hanya jika ada adegan `"visualType": "3d-showcase"`.
- Jika style yang dikonfirmasi adalah **Explainer Sejarah Chibi**, baca `references/style-explainer-sejarah.md` sebelum menyusun manifest dan sebelum menulis komponen; aturan di sana (struktur babak, kartu teks, grading per suasana, pustaka aset) berlaku di atas aturan umum, kecuali aturan timeline back-to-back dan Gerbang Aset yang tetap tidak boleh dilanggar.
- Jika style yang dikonfirmasi adalah **Stick-figure Kok Bisa (Cetakinds)**, baca `references/style-stickfigure.md` sebelum menyusun manifest dan menulis komponen. Aturan di sana berlaku di atas aturan umum, kecuali timeline back-to-back, Gerbang Aset, dan aturan loudness yang tetap tidak boleh dilanggar.
- Jika style yang dikonfirmasi adalah preset **stickman A1–A8 / B1–B7** (`style.preset` diawali `stickman-`), baca `references/stickman-director.md` sebelum menyusun manifest dan menulis komponen. Aturan sutradara bersama dan aturan preset di sana berlaku di atas aturan umum, kecuali Gerbang Aset, voiceover pengguna tanpa TTS, timeline back-to-back, Sumber Fakta, dan aturan loudness yang tetap tidak boleh dilanggar.
- Komponen sumber selalu dibuat bila manifest punya `sources`: `SourceChip` (dirender di `StoryComposition` di atas lapis 3, membaca `scenes` dari timeline sehingga ikut terpotong benar di HighlightVertical), daftar sumber di end card, dan `Disclaimer` bila `disclaimer` diisi. Setelah render final, tulis `out/caption.txt` dari `sources`.
- Gunakan `studio/src/theme.ts` sebagai satu-satunya sumber variabel warna, tipografi, *easing*, dan *spring presets*.
- Setelah kerangka komponen pertama selesai, bangun peta kode dengan `graphify update .` (lihat Peta Kode Proyek dengan graphify). Saat merevisi atau melanjutkan proyek lama, jalankan `graphify explain` pada komponen yang akan diubah sebelum membuka file-nya.
- **Timeline back-to-back, tanpa `TransitionSeries`:** adegan dipasang dengan `<Sequence from={scene.startFrame}>`. Transisi tumpang tindih memendekkan video dan membuat takarir tertinggal dari suara; transisi dibuat oleh animasi masuk/keluar tiap adegan di atas lapis dasar yang konstan.
- **Audio:** `MainStory`/`ShortVertical` memakai satu `<Audio>` utuh; `HighlightVertical` memakai `<Audio startFrom={audioStartFrame} endAt={...}>` per adegan. Jangan hapus logika ini.
- Di dalam adegan, pakai `scene.durationInFrames` (bukan `useVideoConfig().durationInFrames`) untuk exit, Ken Burns, dan rotasi 3D.
- **Single Source, Dual Aspect Ratio:** Gunakan `useVideoConfig()` (`const isVertical = height > width;`) di dalam komponen adegan agar proyeksi 16:9 dan 9:16 berbagi komponen yang sama.
- **Takarir Karaoke (`KaraokeCaption.tsx`):** Render sorotan kata aktif di atas *safe zone* bawah (minimal 18% dari bawah pada mode vertikal). Kelompokkan kata per baris berdasarkan jumlah karakter (±22), bukan jumlah kata tetap, agar tidak ada kata yatim di baris kedua.
- **Takarir ikut video referensi:** jika pengguna mengirim video referensi, tiru gaya takarirnya dari frame referensi: jumlah kata per tampilan (mis. satu kata), font, huruf kapital atau apa adanya, tanda baca ikut tampil atau tidak, dan posisinya. Jangan pakai gaya takarir proyek sebelumnya. Takarir tetap di atas watermark dan di luar 15% area bawah.
- **Kartu overlay HTML** yang diposisikan dengan `left` + `translate(-50%)` wajib diberi `width` tetap (dengan `boxSizing: border-box`), karena tanpa itu lebarnya menyusut dan teks terlipat. Di adegan 3D, jangan taruh label overlay di atas papan nama di dalam adegan; geser papannya lebih jauh atau hilangkan tulisannya di adegan close-up.
- **Improvisasi set dan model:** skill boleh menambahkan dekor pendukung supaya dunia terasa hidup dan masuk akal, tanpa perlu ditanyakan dulu. Contoh:
  - Ruang kantor: meja dengan monitor dan keyboard, kursi, tanaman pot, rak arsip, papan tulis, jam dinding, dispenser air, lampu, poster.
  - Kamar: kasur, meja belajar, rak buku, karpet.
  - Jalan: tiang listrik, pohon, motor parkir, warung.
  Syaratnya, dekor sesuai naskah dan suasana, tidak menutupi tokoh atau label utama, area tengah tetap lega untuk subjek, tidak memakai logo atau merek nyata, dan tetap ringan untuk dirender (primitif low-poly, tanpa model berat).
- **Logika fisik tokoh dan benda (tidak menabrak, tidak tembus):**
  - Setiap benda padat di adegan dicatat footprint-nya (kotak XZ: pusat + setengah lebar/dalam). Tokoh punya radius ±0,35 unit.
  - Posisi diam tokoh harus berjarak ≥ radius + setengah ukuran benda + 0,1 dari setiap benda. Kalau di depan meja, tokoh berdiri atau duduk di sisi yang benar, bukan di dalam mejanya.
  - Jalur jalan tokoh direncanakan memutari benda (titik belok/waypoint), dan diperiksa dengan fungsi sederhana sebelum render: sampling posisi tiap ±5 frame lalu pastikan tidak ada yang masuk ke footprint benda atau ke tokoh lain (jarak antar tokoh ≥ 0,7). Kalau ada yang bentrok, ubah jalur atau geser bendanya; jangan dibiarkan tembus.
  - Pose berinteraksi harus menempel dengan wajar: duduk tepat di kursi (pinggul di tinggi dudukan), tangan di permukaan meja, barang yang dipegang ikut bergerak bersama tangan, dan barang yang diletakkan berada tepat di atas permukaan (y = tinggi permukaan + setengah tinggi barang), tidak melayang atau terbenam.
  - Benda yang ada di depan tokoh dari sudut kamera boleh menutupi sebagian tubuhnya (oklusi alami), tetapi tidak boleh menembus atau menyatu dengan tubuhnya.
  - Di contact sheet, tambahkan 1 frame di tengah setiap gerakan jalan untuk memeriksa tabrakan.
- **Headline vertikal:** maksimal ±90px agar headline 3–4 kata muat satu baris; headline 2 baris di 104px menabrak ilustrasi di area tengah.
- **Aturan Keras Anti-Kosong:**
  - Wajib komposisi 5 lapis. Lapis 1, 4, 5 (`MovingGradient`, `ColorGrade`, `GrainVignette` di `components/Layers.tsx`) dirender sekali di `StoryComposition`; lapis 2–3 (media/`<ThreeStage>`, grafis + karaoke) ada di `StoryScene`.
  - Masuk multi-properti (`opacity` + geser posisi + `scale`) dengan `spring()`, *staggered* 3–6 frame antar elemen/kata.
  - Wajib *micro-motion* gelombang sinus saat elemen diam dan efek *Ken Burns* pada foto statis.

## Fase 3: Inspeksi Visual & Render Hemat Token
- **Prasyarat wajib:** Fase ini hanya boleh dimulai jika acuan visual (referensi gambar atau style yang dikonfirmasi pengguna) dan voiceover dari pengguna sudah lolos pemeriksaan aset (lihat Aturan Keras: Gerbang Aset Sebelum Render). Jika belum, jangan jalankan satu pun perintah di bawah ini; minta yang kurang kepada pengguna.
- Sebelum render apa pun, cek dulu setiap aset PNG statis ke cache GitHub (lihat Cache Aset PNG di GitHub); hanya aset yang MISS yang dirender, lalu disimpan ke cache.
- Saat memeriksa contact sheet, pastikan juga chip sumber muncul di adegan yang berisi klaim, teksnya tidak terpotong, dan daftar sumber di end card terbaca (≥ 34 px di 1080 px).
- Saat memeriksa contact sheet, cocokkan juga hasilnya dengan acuan visual (gambar referensi atau style brief): palet, tipografi, dan nuansa gerak harus sesuai.
- Jalankan pratinjau ringan (skala 0.5) + 1 gambar *contact sheet* yang mencakup **seluruh** video (2 frame per adegan: setelah animasi masuk, dan menjelang keluar):
  `reditor sheet MainStory` (atau `ShortVertical` / `HighlightVertical`); di HP lebih hemat: beberapa `reditor still <Komposisi> <frame>`
- Periksa satu gambar `out/contact_sheet.jpg` untuk memastikan tidak ada teks terpotong, elemen bertabrakan, atau *safe zone* bawah yang tertutup (maksimal 2 kali siklus perbaikan).
- Di setiap siklus perbaikan, temukan komponen yang perlu diubah lewat `graphify explain`/`graphify path` dulu, lalu jalankan `graphify update .` setelah perbaikan agar peta tetap sesuai kode.
- Render final 1080p 30fps sesuai mode:
  - Mode A: `reditor render short` (komposisi `ShortVertical`)
  - Mode B: `reditor render full` (komposisi `MainStory`)
  - Mode C: `reditor render short` (Full 9:16, komposisi `ShortVertical`, 8–10 menit) lalu `reditor render highlight` (Short 9:16, komposisi `HighlightVertical`, 60 detik–3 menit). Verifikasi kedua durasi dengan `ffprobe`.
- Verifikasi hasil dengan `ffprobe`: durasi file = `fullDurationInFrames / fps` dan ada stream audio jika `audioPath` diisi.
- Adegan `@remotion/three` di mesin tanpa GPU (2 CPU) butuh ±1,5 detik per frame 1080x1920: jalankan render final di latar belakang dan pantau lognya; untuk contact sheet, bundle sekali (`npx remotion bundle`) lalu render frame inspeksi dengan `npx remotion still <folder-bundle>` (3 paralel) alih-alih pratinjau video penuh. Simpan frame inspeksi di folder baru tiap siklus, jangan menghapus isi folder dengan wildcard.
- **Barisan berbanjar (rombongan satu jalur):** close-up depan tokoh yang bukan paling depan akan terhalang atau masuk ke tubuh tokoh di depannya (frame hitam/punggung). Pakai sudut 3/4 dari samping (x ±1,2–1,7, jarak 1,1–1,6) atau beri jarak ≥1,6 unit tepat di depan tokoh yang akan di-close-up. Untuk tokoh yang berlari/berdesakan, jaga jarak antartokoh ≥0,7 unit dengan simpangan gerak kecil (±0,1), dan cek dengan sampling posisi sebelum render.
- **Teks kecil di benda 3D** (sampul buku, layar HP, kertas) tidak terbaca di 9:16. Tampilkan sebagai sisipan 2D yang pop-in (kartu buku, layar HP REC) di atas adegan; benda 3D-nya tetap dipegang tokoh.
- **Render 3D tanpa GPU:** set `dpr={0.6}` dan `antialias: false` di `<ThreeCanvas>` (lapis 2D tetap 1080p tajam). Di proyek "Akar" ini memangkas estimasi render dari ±7,5 jam ke ±1,6 jam untuk 122 dtk. Ukur dulu 60 frame dengan `--frames` sebelum render penuh.
- Di adegan 3D, jaga kamera minimal ±3 unit dari tokoh terdekat dan di luar deretan rumah; tokoh yang berjalan/antre jangan sampai melintas di depan lensa (kepala raksasa menutup layar).
- Jika unduhan Chrome headless atau font dari internet diblokir: arahkan Remotion ke Chrome lokal lewat `Config.setBrowserExecutable(...)` di `remotion.config.ts` (cari `chrome-headless-shell` di sistem), dan ambil file font dari paket npm `@fontsource/*` ke `public/fonts/`, lalu muat dengan `FontFace` + `delayRender`.
- Setelah render final, ukur loudness dan normalkan ke −14 LUFS (`loudnorm=I=-14:TP=-1:LRA=11`, video di-copy) bila meleset lebih dari 1 LU.
- Semua paket `remotion` dan `@remotion/*` wajib versi yang persis sama; untuk naik versi pakai `npx remotion upgrade`, jangan edit satu per satu.

## Fase 4: Evaluasi & Usulan Upgrade Skill (setelah video final diserahkan)
Skill ini tidak boleh mengubah dirinya sendiri secara diam-diam. Perbaikan skill hanya lewat usulan yang disetujui pengguna.

1. **Catat evaluasi proyek** (singkat, maksimal 5 poin) setelah render final diserahkan:
   - Masalah teknis yang muncul dan cara memperbaikinya (mis. teks terpotong, takarir tidak sinkron, anchor tidak ditemukan, render gagal, versi paket bentrok, cache gagal push).
   - Revisi yang diminta pengguna, terutama yang diminta lebih dari sekali atau yang kemungkinan berulang di proyek lain.
   - Preferensi yang dinyatakan pengguna (style favorit, kecepatan gerak, tempo voiceover, posisi takarir, panjang video, gaya naskah).
   - Langkah dalam skill ini yang ternyata salah, tidak jelas, atau membuang waktu.
2. **Saring:** hanya jadikan usulan hal yang (a) berlaku umum untuk proyek video berikutnya, bukan khusus satu video, dan (b) bersumber dari kejadian nyata di proyek ini atau ucapan pengguna — bukan tebakan. Jika tidak ada yang layak, cukup sampaikan evaluasi singkatnya dan jangan buat usulan.
3. **Usulkan upgrade:** jika ada yang layak, tampilkan usulan perubahan `.claude/skills/reditor-nethunter/SKILL.md` (atau file `references/`) sebagai diff kecil yang tepat sasaran — menambah atau mengubah aturan di bagian yang relevan, bukan menulis ulang seluruh skill. Jelaskan ke pengguna dalam 1–3 kalimat apa yang diubah dan alasannya, dan baru terapkan setelah pengguna setuju.
4. **Batasan usulan:**
   - JANGAN mengusulkan pelonggaran atau penghapusan *Aturan Keras: Gerbang Aset Sebelum Render* kecuali pengguna sendiri yang secara eksplisit memintanya.
   - JANGAN mengusulkan perubahan apa pun pada *ATURAN TERKUNCI* Mode C (format 9:16, Full 8–10 menit, Short 60 detik–3 menit) kecuali pengguna sendiri yang secara eksplisit memintanya.
   - JANGAN memasukkan data pribadi, kredensial, token, atau isi aset pengguna (naskah lengkap, file audio) ke dalam skill.
   - Maksimal 1 usulan per proyek; gabungkan semua perubahan ke dalam satu usulan.
5. Keputusan sepenuhnya di tangan pengguna: jika pengguna menolak usulan, jangan ulangi usulan yang sama kecuali pengguna mengangkatnya lagi.

---
