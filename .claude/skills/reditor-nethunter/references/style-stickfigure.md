# Preset Style: Stick-figure Kok Bisa (Cetakinds), 3D toon, 9:16

Diturunkan dari 12 video referensi Shorts (warung buah "pisang tahanan", kampung yang melarang langkah seirama, survivorship bias pesawat ×2, Tembok Besar Cina, SPBU "mulai dari nol", desa petir, koboi "never draw first", serta video Cetakinds: internet mati sebulan, Italian brainrot, mantan, stasiun pertama). Yang ditiru adalah GAYA dan TEKNIK, bukan aset. DILARANG memakai logo, nama kanal, watermark, atau desain tokoh persis milik kanal lain; brand yang tampil hanya milik pengguna (Cetakinds).

## 1. Format & audio
- Default Mode A (9:16, 1080x1920, 30 fps), durasi 55–100 dtk (umumnya 60–75).
- Tempo VO bahasa Indonesia di semua referensi 2,3–2,7 kata/dtk. Untuk preset ini, **anggaran kata = durasi × 2,5** (60 dtk ≈ 150 kata), dan tempo terukur 2,2–2,6 kata/dtk dianggap normal (tidak perlu ditawari rekam ulang). Audio tetap tidak diubah.
- Musik dari kode: pizzicato + glockenspiel ceria (D minor untuk misteri, D mayor untuk payoff), string pad + denyut rendah untuk tegang, string + pizz jarang untuk malam, reed "jinjit" untuk mengendap. Mood berganti per babak. Musik ±20 LU di bawah VO dengan ducking. Puncak SFX dibuat −7 dB dari puncak VO agar tumpukan SFX tetap ≥ 6 dB di bawah VO.
- SFX standar: whoosh di setiap whip, pop/bubble untuk label, stamp untuk cap, boing untuk bingung, riser sebelum reveal, thud + sparkle untuk angka besar, scribble untuk coretan, klik + ding saat tombol ikuti ditekan.

## 2. Bahasa visual
- **Dunia:** 3D low-poly dengan shading toon 3 tingkat, garis tinta gelap (#1e1a22) di semua benda, langit gradasi, awan kotak-kotak, umbul-umbul warna-warni khas kampung, rumah atap pelana, jalan aspal dengan marka.
- **Tokoh:** kepala bulat besar putih (#fbf8f1) dengan wajah sederhana (mata titik, alis, mulut), badan kapsul berwarna, celana setengah bola, kaki-tangan tongkat hitam tipis, bayangan bulat di kaki. Identitas lewat atribut: peci, caping, helm, topi pet, topi tinggi, topi koboi, helm proyek, hijab, rambut mangkuk hitam, kacamata, kumis, dasi. Ekspresi: neutral, happy, laugh, shock, scared, smug, sad, angry, worried, confused, squint, sleep, plus tetes keringat dan pipi merah.
- **Gerak tokoh:** selalu idle (napas + kepala miring halus), mulut buka-tutup tiap 1/8 detik saat ia yang bicara, pose menunjuk/melambai/bersorak/melompat, jalan dengan kaki berayun + badan memantul.
- **Ritme:** 10–16 shot per 60 detik (rata-rata 3–4 dtk). Ide baru mendapat setup baru. Shot pertama sudah bergerak di frame 0. Kamera selalu bergerak (push-in + drift tangan). Close-up wajah untuk reaksi. Mekanisme dijelaskan di papan tulis/poster/layar HP dengan titik merah, lingkaran merah yang digambar perlahan, dan panah.
- **Mood per babak:** day, sunset, night (biru gelap, jendela menyala), indoor (hangat), past (sepia untuk kilas balik), danger (merah), dark.
- **Transisi** (sebagai animasi masuk/keluar, tanpa tumpang tindih): whip (blur geser 0,16 dtk di akhir adegan lama dan awal adegan baru) untuk pindah tempat, cut di lokasi sama, flash putih 0,1 dtk untuk benturan/angka besar. Jangan flash dua kali berturut-turut.
- **Detail kecil untuk kerangka F (cerita kampung):**
  - Shot rata-rata 2–3 dtk (referensi: 3,0 dtk dan 2,1 dtk); hampir setiap frasa takarir baru mendapat sudut baru.
  - Frame 0: wide lokasi dengan tokoh pemegang aturan sudah bergerak; dalam 3 dtk pertama close-up benda bertulisan (label krem bergaris tepi, huruf navy tebal, garis bawah oranye "TAHANAN"; papan larangan berikon). Tulisan label bisa berganti mengikuti ucapan ("TAHANAN" → "BEBAS JUMAT" dengan kata kedua oranye).
  - Isi tersembunyi ditunjukkan dengan potongan/x-ray benda (karung transparan memperlihatkan pisang + mangga); orbit pelan mengelilingi benda kunci.
  - Sains digambar di objek nyata, bukan papan tulis: garis putus-putus kuning dari pisang ke mangga sebagai "gas", panah kuning turun berurutan di lantai jembatan, panah dua arah kuning yang memanjang untuk ayunan yang membesar.
  - Penanda bunyi grafis: not musik kuning melayang dari radio, tiga garis getar di samping peluit/gelas, kilatan kecil di sekitar benda yang berubah.
  - Hitungan hari: tally marks tergores di kayu/kertas yang bertambah; papan klip dengan rute dan coretan hitungan.
  - Cahaya mengikuti waktu cerita: siang netral → sore oranye-ungu untuk adegan curi-curi → pagi terang untuk reveal. Tokoh marah/kecewa: layar meredup ±40% saat ia menatap.
  - Reaksi lewat close-up push-in: mata O membelalak, mata >< mengernyit, alis menukik, menyipit curiga. Kerumunan seragam (kaus merah 17-an, seragam sekolah putih) berderet, tokoh utama beda warna baju.
  - Pembuka dan penutup berpasangan: shot terakhir wide pull-back ke lokasi awal (pos jaga, warung) sebagai bookend; referensi tidak memakai watermark, end card, atau chip sumber (untuk Cetakinds tetap pakai aturan brand dan sumber).

## 3. Implementasi di @remotion/three (sudah diuji)
- `MeshToonMaterial` dengan `gradientMap` 3 tingkat (`DataTexture` 3x1, nilai 90/175/255, `NearestFilter`).
- **Garis tinta (inverted hull):** clone geometri, hapus atribut `uv` dan `normal`, `mergeVertices` lalu `computeVertexNormals` (agar sudut kotak tidak bolong), material `MeshBasicMaterial` `BackSide` warna tinta, vertex digeser sepanjang normal 0,02–0,03 unit lewat `onBeforeCompile`.
- **Wajah:** digambar di `CanvasTexture` 1024x512 yang membungkus bola kepala (equirect). Titik depan (+z) ada di u = 0,25, v = 0,5. Cache tekstur per kombinasi ekspresi/bicara/keringat.
- **Rambut:** `SphereGeometry(r, 24, 12, 0.27π, 1.46π, 0, 0.52π)` diputar y = π/2 agar celah wajah ada di depan, ditambah poni penuh `thetaLength 0.27π`. Celah yang lebih sempit akan menutupi mata.
- **Kamera:** fov vertikal 50°. Tinggi yang terlihat ≈ 0,93 × jarak, lebar ≈ 0,52 × jarak. Tiga tokoh berdiri butuh jarak 7–8 unit; close-up wajah 3–3,6 unit. **Papan diagram di 9:16 harus tegak** (lebar ≤ 0,5 × jarak kamera), karena papan lebar akan terpotong.
- Papan diagram = plane `MeshBasicMaterial` (`fog: false`) dengan `CanvasTexture` yang digambar ulang dari `useCurrentFrame()` lalu `needsUpdate = true`.
- Benda khusus (gerobak, mesin, pompa bensin, pesawat) dirakit dari primitif box/silinder/kerucut/torus bertinta. Jangan memakai model berat.
- Tanpa GPU (2 core) render sekitar 1 frame/dtk per proses di 1080x1920: jalankan render final di latar belakang dan pantau log.

## 4. Elemen layar (isi `onScreenText`)
`tag` (label pil berwarna bergaris tinta, pop pegas, bisa dicoret) · `yearCard` (tahun Montserrat 900 bergaris + chip tanggal merah, pojok kiri atas) · `calendar` ("HARI KE / 30 / tanpa internet") · `counter` (angka bergulir format id-ID "64.600", awalan Rp, akhiran °C) · `checklist` (centang hijau satu per satu) · `bubble` (balon kata/chat) · `stamp` ("MITOS!", "MASIH CAIR") · `ring`/`cross`/`arrow` (anotasi merah) · `mark` (? atau ! melayang di atas kepala).

## 5. Zona layar 1080x1920
- Area aman Shorts/Reels: x 90–990, y 200–1500. Label/judul di y 250–500; wajah dan objek penting di y 350–1200.
- **Takarir karaoke di y ≈ 1305 (68%)**, sesuai semua referensi. Untuk preset ini ini menggantikan posisi bawah 18%, dan tetap di luar 15% area terbawah.
- Chip sumber di y ≈ 1436 (74,8%), watermark di y ≈ 1545 (80,5%). Jangan menaruh info di bawah y 1600.

## 6. Takarir
**Mode `frasa-sorot` (dari referensi kerangka F):** 1–2 kata per tampilan; frasa benda/nama tidak dipisah ("warung buah", "Bu Yati", "langkah seirama"). Poppins ExtraBold ±96 px, putih dengan garis gelap tebal + bayangan lembut, pusat di y ≈ 1353 (70,5%). Kata kunci berwarna kuning #FFCF49 pada ±30–40% tampilan: nama tokoh, benda aturan, angka/waktu penting, istilah sains, dan kata punchline; kata klimaks diperbesar ±1,2× ("sekeras batu", "serentak", "bareng"). Angka ditulis seperti diucapkan ("dua belas", "langkah kesepuluh"). Tanda baca dibuang kecuali tanda kutip pembuka dialog. Saat transisi whip, takarir ikut memudar sebentar.

**Mode default:** Satu kata per tampilan dengan pop kecil, Poppins ExtraBold (800) putih bergaris gelap tebal (±22% ukuran huruf), ±96 px, titik/koma dibuang, ? dan ! tetap tampil. Untuk sejarah, opsinya huruf kapital Montserrat 900 ±104 px. Frasa angka ditukar ke bentuk layar ("nol derajat" → "0°C", "dua puluh lima" → "25").

## 7. Brand Cetakinds
- File: `public/brand/watermark.png` (logo kecil transparan) dan `public/brand/logo.png` (logo lengkap). Jika belum ada, minta ke pengguna. Fallback-nya wordmark "cetak" navy #1d3a5f + "inds" oranye #f08a24.
- Watermark ±118 px lebar, opacity 0,9, di tengah bawah takarir. Disembunyikan saat end card.
- **End card mulai kata "Pencet":** layar digelapkan 50% → kartu logo putih bersudut bulat (±330 px, garis navy) di y ≈ 23% → tombol oranye "+ IKUTI" di y ≈ 37,5%, ditekan jari kartun di detik ke-1 lalu berubah navy "DIIKUTI ✓" (SFX klik + ding) → daftar "Sumber:" di y ≈ 43,5%. Takarir tetap jalan.

## 8. Tambahan skema manifest
```json
{
  "style": { "preset": "stickfigure-kokbisa", "brand": "Cetakinds", "caption": "poppins" },
  "disclaimer": "",
  "sources": [{ "short": "Frostburg State Univ.", "year": "", "full": "Frostburg State University, General Chemistry Online — Why isn't 0°F the lowest possible temperature for a salt/ice/water mixture?", "url": "https://antoine.frostburg.edu/chem/senese/101/solutions/faq/print-zero-fahrenheit.shtml", "claim": "Larutan garam tetap cair sampai -21,1 °C", "scenes": ["scene-09-minus21"] }],
  "scenes": [
    { "id": "scene-09-minus21", "beat": "climax", "energy": "T3", "mood": "night", "transitionIn": "flash",
      "onScreenText": [{ "type": "counter", "from": 0, "to": -21, "suffix": "°C" }, { "type": "stamp", "text": "MASIH CAIR" }],
      "captionText": "Air garam bisa tetap cair sampai minus dua puluh satu derajat." }
  ]
}
```

## 9. Pemeriksaan contact sheet khusus preset
- Tidak ada tokoh, label, atau papan yang terpotong tepi layar. Wajah tidak tertutup takarir.
- Setiap angka/tahun penting punya elemen layar (counter/yearCard/tag).
- Chip sumber muncul di adegan klaim; end card menampilkan logo, tombol DIIKUTI, dan daftar sumber.
- Tidak ada logo/watermark/nama kanal lain.
