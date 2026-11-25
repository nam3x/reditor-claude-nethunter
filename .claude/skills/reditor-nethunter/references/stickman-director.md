# Preset Stickman Director (A1–A8, B1–B7) untuk Remotion

Diadaptasi dari repo `kaomei/stickman-video-director` (lisensi MIT, © 2026 Stickman Video Director contributors). Yang diambil hanya aturan gaya, cara menyutradarai, dan gerbang kualitas. DILARANG memakai gambar/video contoh repo itu sebagai aset video, meniru tokoh persis kanal inspirasinya, atau menampilkan nama kanal lain. Brand yang tampil tetap milik pengguna.

Di repo asli, A (Model Engine) menghasilkan prompt untuk model video (Google Flow/Omni/Veo) dan B (Code Engine) merender animasi lewat kode. Di skill ini semua preset dirender dengan Remotion, jadi dari A yang dipakai adalah **gaya dan cara menyutradarainya**, bukan alur pembuatan prompt-nya.

## 0. Kelayakan di Remotion (sebutkan ke pengguna sebelum konfirmasi)
| Tingkat | Preset | Artinya |
|---|---|---|
| **Penuh** | A1, A2, B1, B3, B7 | Bisa dibuat murni dengan kode (SVG/canvas) mendekati contoh aslinya. |
| **Mendekati** | A3, A4, A5, B2, B4, B5 | Bisa dengan kode, tetapi latar lukis/tekstur lebih sederhana dari aslinya. B5 butuh gambar avatar dari pengguna. |
| **Terbatas** | A6, A7, A8, B6 | Aslinya bergantung pada lukisan/model video. Tanpa gambar latar/tokoh dari pengguna, hasil kode hanya tafsiran gaya; katakan itu dengan jujur. |

Catat pilihan sebagai `"style": { "preset": "stickman-a1-dark" }` (pola: `stickman-a1-light`, `stickman-a1-dark`, `stickman-a2-tech`, `stickman-a2-story`, `stickman-a3` … `stickman-b7`).

## 1. Aturan sutradara bersama (berlaku untuk semua preset)
1. **Gaya tetap, cerita berubah.** Kunci tokoh di `style.cast` (kartu tokoh: peran, proporsi kepala-badan, rambut, wajah, busana, satu aksesori khas). Setiap tokoh berulang punya ≥2 pembeda yang bukan warna. Lokasi, properti, akting, dan kamera berubah mengikuti cerita; cara menggambar tidak berubah dalam satu video.
2. **Rantai aksi sebab-akibat.** Setiap adegan punya `action`: pemicu → kontak → respons benda/lingkungan → reaksi tokoh → `exitState`. Contoh: dorong slab tidak bergeser → ambil tuas → slab rebah jadi jembatan → tokoh melangkah di atasnya. Bacalah urutan adegan sebagai storyboard bisu: penonton tanpa suara harus tahu apa yang dilakukan tokoh dan apa akibatnya.
3. **Sambungan antar adegan.** Adegan berikutnya mewarisi `exitState` adegan sebelumnya (pose, pegangan, posisi/kondisi properti, arah gerak, arah kamera), ATAU ada potongan lokasi/waktu yang disengaja dan terbaca. Jangan mengulang ancang-ancang aksi yang sudah selesai.
4. **Penutup aktif.** Adegan terakhir harus punya satu aksi/perubahan grafis dengan akibat terlihat sebelum ditahan; bukan tokoh berdiri diam.
5. **Gerbang diam 2,5 detik.** Subjek utama (tokoh atau benda fokus) wajib mengalami perubahan bermakna paling lambat tiap 2,5 detik. Zoom seluruh layar, ganti takarir, partikel latar, dan micro-motion sinus TIDAK dihitung. Pengecualian: jeda reaksi bermotivasi (A3, A4, A5) dan aturan B4 (setiap shot ≤3 detik).
6. **Satu fokus per beat.** Satu aksi utama terbaca dalam satu waktu; aksi sekunder mengikuti gaya/kejadian yang sama dengan sedikit tunda.
7. **Anatomi dan kontak.** Tepat 2 lengan dan 2 kaki per tokoh. Lengan yang bergerak MENGGANTIKAN pose lamanya (tidak ada lengan tertinggal). Panjang tulang tetap (IK 2 tulang: bahu–siku–tangan, pinggul–lutut–kaki); hitung kontinu dulu, baru dibulatkan. Kaki menapak saat berjalan (bukan meluncur), tangan benar-benar menyentuh benda yang dipegang, benda ikut tangan. Jejak gerak hanya pada properti/grafis, bukan duplikat tungkai.
8. **Kepemilikan properti.** Catat posisi awal, siapa memegang, kapan berpindah, dan posisi akhir. Benda tidak muncul tiba-tiba, berlipat ganda, atau kembali ke tempat semula setelah dipindah.
9. **Dua rasio, dua tata letak.** 16:9 memakai staging kiri-tengah-kanan, gerak lateral, match cut horizontal. 9:16 memakai kedalaman depan-belakang, reveal vertikal, dan elemen bertumpuk. Ganti rasio = susun ulang adegan, bukan crop.
10. **Warna dan teks.** Warna aksen diberi makna cerita (cemas, bahaya, berhasil). Teks di dalam ilustrasi hanya lewat `onScreenText`; ikon pesan/kartu/notifikasi dibuat tanpa tulisan kecuali diperlukan.
11. **Suara.** SFX dipasang di kontak, perubahan, dan pendaratan yang terlihat (tetap mengikuti aturan loudness skill). Musik adalah bed utuh per film/babak, bukan potongan per adegan.

## 2. Preset

### A1 · Hitam Putih Klasik (Light / Dark) — Penuh
- **Kanvas:** Light = putih murni datar; Dark = hitam pekat datar. Tanpa gradien, grain, bayangan, vignette, atau kedalaman 3D.
- **Tokoh:** kepala lingkaran kosong, badan dan tungkai satu garis, ketebalan garis medium seragam, tanpa baju dan tanpa isian. Default boleh ekspresi garis sederhana di kepala (tanpa mata detail); jika pengguna minta tanpa wajah, kepala kosong total. Tokoh tetap monokrom (hitam di Light, putih di Dark).
- **Warna:** maksimal 3 aksen jenuh, hanya pada properti dan efek grafis (mis. merah = usaha sia-sia/bahaya, biru = titik ungkit, emas = aksi/berhasil, ungu = pikiran cemas).
- **Properti:** kontur datar dengan sedikit garis (mis. kertas terlipat satu lipatan). Pilih properti yang bentuk/perilakunya menyampaikan ide dan bisa disentuh tokoh. Ruang kosong luas.
- **Remotion:** SVG `stroke` dengan `strokeLinecap/strokeLinejoin: round`, rig sendi + IK 2 tulang. Lapis 1, 4, 5 diganti kanvas datar.
- **Cek:** tidak ada tungkai ganda, ketebalan garis sama di semua adegan, aksen tidak mengenai tokoh, kanvas tetap murni.

### A2 · Pop Modern (kupluk merah) — Penuh
- **Tokoh (sama untuk A2.1 dan A2.2):** stickman 2D, kupluk merah cerah membulat tanpa pompom, kaus kuning, celana pendek, kaki-tangan tongkat hitam. Kepala tanpa mata detail (titik sederhana saja). Kupluk dan kaus selalu ada.
- **A2.1 Teknologi Minimalis:** studio putih high-key, grid lantai perspektif abu sangat samar, panel UI kaca sian/biru menyala. DILARANG tekstur papan sirkuit, panel sci-fi, lorong pesawat, beton retak. Aksi fisik: melompat menabrak langit-langit kaca lalu memantul lucu, ketukan sepatu memunculkan riak sian di grid, pena cahaya menggambar jembatan, menyentuh panel kaca memunculkan ikon gembok, mendorong pintu brankas ke cahaya.
- **A2.2 Cerita Berwarna:** latar penuh warna (kamar lampu hangat, jalan senja, puncak di atas awan), cahaya sinematik, latar diblur ringan; tokoh tetap datar 2D.
- Hindari morph cair abstrak (tangga meleleh jadi jam); pakai interaksi fisik.

### A3 · Gua Prasejarah (komedi gelap) — Mendekati
- **Tampilan:** kontur hitam kasar (SVG `feTurbulence` + `feDisplacementMap` kecil, seed berganti tiap 3–4 frame), kepala putih terisi, wajah kartun ekspresif (mata, alis, mulut), tungkai tongkat hitam, baju kulit binatang, palet tanah oker/cokelat + aksen api hangat, tekstur kertas halus.
- **Cerita:** masalah modern diterjemahkan jadi tugas fisik prasejarah (rekomendasi tanpa henti = kepala suku terus menyodorkan camilan; beban kerja = ikatan tombak yang terus bertambah). Alur premis → solusi menggoda/eskalasi → pembalikan/callback. Tatapan datar atau jeda reaksi boleh.
- Ini analogi fiksi, bukan sejarah: isi `disclaimer`. Cast card wajib; penampilan tidak berubah antar adegan.

### A4 · Cerita Hangat — Mendekati
- **Tokoh default:** kepala bulat putih terisi, dua mata oval kecil gelap, alis garis, mulut lengkung pendek; torso ramping tertutup isian putih berkontur gelap; lengan dan kaki satu garis gelap medium; tangan bulat kecil, kaki pendek membulat; tanpa rambut/aksesori.
- **Latar:** kartun 2D penuh warna dengan cahaya lembut dan kedalaman; bukan sketsa, bukan bingkai kertas.
- **Aturan lokasi:** setiap segmen naratif baru = lokasi baru yang mudah dikenali (kantor → peron stasiun → taman), kecuali pengguna minta satu lokasi atau callback disengaja. Variasikan wide, close-up aksi, tracking, dan foreground lewat.
- "Hangat" adalah perlakuan visual; topik cemas/serius tetap dijaga maknanya.

### A5 · Kartun Sejarah — Mendekati
- **Tokoh:** kepala putih bulat menyatu dengan leher putih pendek yang masuk ke kerah baju (siluet putih kontinu, kontur hitam hanya di sisi); mata oval vertikal hitam pejal tanpa pupil; hidung satu lengkung kecil; alis dan mulut per tokoh; tungkai terbuka garis hitam ramping; telapak tangan hitam pejal bentuk sarung tangan bulat (±18% diameter kepala panjangnya, ±10% lebarnya) dengan satu benjolan jempol, tanpa jari.
- **Era pack (catat di manifest):** zaman/tempat dan premis faktual; busana + aksesori tiap peran; lokasi dan landmark; palet 4–6 warna dengan perannya.
- Latar lukis penuh warna dengan cel shading; busana boleh berbayang lembut. Fakta sejarah wajib bersumber (chip sumber); adegan komedi rekaan ditandai `disclaimer`.
- Berbeda dari Explainer Sejarah Chibi: A5 berpusat pada tokoh yang mengalami keseharian zaman itu.

### A6 · Amber Noir — Terbatas
- **Tokoh:** kepala hitam matte bulat dengan leher hitam pendek, tanda mata putih krem kecil, mulut garis; protagonis berhoodie merah-oranye dengan tudung turun; tangan dan tungkai hitam sederhana.
- **Dunia:** cahaya ambar keemasan + bayangan ungu plum tua, kota berlapis, kontur bersudut, cel shading tertahan.
- **Cerita:** pengandaian ("Bagaimana jika semua barang 10.000× lebih murah?") → godaan → akibat tak terduga. Takarir huruf kapital dinamis; judul putih kecil di kiri atas.
- Tanpa gambar dari pengguna: siluet vektor + gradien ambar-plum; sebutkan bahwa ini tafsiran.

### A7 · Rubber Hose (1930-an) — Terbatas
- **Tokoh:** wajah bulat putih kertas, dua helai rambut tipis melengkung, mata oval hitam, alis dan mulut kecil; leher, tulang belakang, dan tungkai garis tinta sempit (tidak ada dada terisi); tangan kecil, kaki lengkung hitam pendek.
- **Dunia:** latar era lawas berkontur pena dengan detail engsel/sambungan; sage-abu, abu mutiara, taupe, gading, aksen merah bata pudar (bukan monokrom, bukan sepia).
- **Gerak:** antisipasi → gerak lentur → benturan/overshoot → pulih, kedip dan reaksi wajah; tulang belakang tetap garis saat melengkung. Di Remotion, tungkai = path Bezier kuadrat dengan titik kontrol pegas (`spring` damping rendah).
- Narasi/lirik tidak wajib; cocok untuk video mengikuti musik.

### A8 · Terinspirasi Ghibli — Terbatas
- **Tokoh:** wajah bulat, mata titik, lengan-kaki garis tipis, pewarnaan datar cel.
- **Dunia:** latar seperti cat guas, langit-laut biru pekat, awan kumulus tinggi, bayangan matahari tegas. Pilih 1–2 detail yang ikut aksi (angin mengangkat kanopi → surat terbang → tokoh menangkapnya); semua kain/benda ringan mengikuti satu arah angin.
- **Gerak:** satu aksi utama per shot: pemicu → tenaga → kontak → hasil → reda.
- Kode hanya bisa mendekati (lapisan gradien + noise + bayangan tegas); hasil terbaik butuh latar lukisan dari pengguna. Jangan menyebut nama studio di video.

### B1 · Seni Garis Minimalis — Penuh
- **Kertas:** #FDFDFC dengan grid persegi sangat samar (garis 0,8 px, rgba(76,90,105,0.036), jarak 64 px pada lebar 1280; skalakan proporsional), tanpa grain.
- **Tokoh:** ramping, ±4–4,5 kepala tingginya; garis pena hitam halus agak tidak rata; mata oval hitam, alis yang jelas naik/turun/miring, mulut yang berubah besar (kaget, frustrasi, menyipit, senyum lebar); tangan dan kaki oval kecil. Seluruh tubuh ikut berakting (condong, menoleh, berat badan).
- **Properti:** gambar tangan berwarna (kuning/merah/hijau hangat + tinta navy), panah melengkung, coretan marker. Screenshot nyata boleh sebentar di bingkai membulat bergaris halus.
- **Teks:** teks pendek besar tulisan tangan (Caveat) sebagai fokus adegan; takarir frasa pendek Noto Sans 600 lebih kecil di bawah.
- **Ritme:** tokoh tampil ±60–70% waktu; sisanya close-up benda/teks. Elemen muncul berurutan sesuai urutan ucapan (bukan semua sekaligus lalu bergoyang).

### B2 · Gambar Tangan Berwarna — Mendekati
- Kertas hangat, kontur tinta halus tidak rata, properti berwarna redup tetapi beragam, lingkungan sehari-hari yang mudah dikenali. Tokoh kepala bulat, mata titik, mulut garis.
- Judul adegan tulisan tangan; takarir sans-serif tinta gelap di label kertas gading membulat (40 unit pada lebar 1280 untuk 16:9, 72 untuk 9:16).
- Tokoh tidak perlu terus melambai; ritme datang dari perubahan fokus, sudut, dan informasi. Cerita baru harus memakai lokasi/komposisi berbeda dari video sebelumnya (catat peta adegan).

### B3 · TV Retro — Penuh
- Layar gelap, tokoh dan gambar putih-abu bercahaya tipis, teks putih bersih, scanline halus, sesekali gangguan sinyal ringan. Efek TV dipasang sebagai satu lapis akhir; uji dulu tanpa efek, baru nyalakan.
- Setiap garis penghubung/panah terikat ke objek asal dan tujuan, dan punya fungsi sebelum → proses → sesudah. Geser global atau noise CRT bukan bukti gerak.
- Cocok: sains sehari-hari, perilaku hewan, misteri pendek.

### B4 · Thriller Bertahan Hidup — Mendekati
- Kontur hitam sedikit organik, bidang warna lukis lebar, cel shadow; kepala putih bulat, wajah hitam minimal, badan dan tungkai tongkat hitam tanpa baju, sarung tangan kartun putih membulat dengan jempol terbaca.
- Pembuka setengah berbayang, eskalasi visual di 3 detik pertama, ancaman muncul dari gelap. **Setiap shot ≤3 detik**; crop, zoom kecil, atau ganti takarir tidak mereset hitungan.
- Ambiens pelan terus mengalir + SFX sesuai cerita, di bawah VO. Jangan pakai efek mengilap 3D atau hitam pekat total.

### B5 · Penjelasan dengan Avatar — Mendekati (butuh gambar avatar)
- Pembawa acara (avatar pengguna, mis. maskot Cetakinds; tokoh terkenal perlu izin) bicara di kanan bawah; panggung kiri berisi stickman anonim dan benda raksasa yang memperagakan ide (diseret tagihan, tergencet tekanan).
- Kertas hangat, tinta gelap, aksen merah, teks penekanan hitam-merah. Metafora visual berganti-ganti dengan serah terima yang jelas: kelompok lama menyingkir sebelum pemeran utama baru mengambil alih.
- Gerak bibir mengikuti amplitudo VO (`visualizeAudio`/`getAudioData` dari `@remotion/media-utils`). Takarir maksimal 3 baris semantik.

### B6 · Meme Story — Terbatas
- Garis tinta tebal-tipis, cat matte, cahaya lembut, latar luas; ekspresi meme berlebihan. Paling bagus 9:16.
- Pelacakan menyamping, kedalaman berlapis, serah terima benda, close-up reaksi, jeda agar lelucon terbaca. Takarir satu baris Archivo Black bergaris.
- Latar cat butuh gambar dari pengguna; versi kode lebih datar.

### B7 · Teater Piksel — Penuh
- **Kanvas logis** 320×180 (9:16: 180×320, disusun ulang), diperbesar tepat 6× dengan nearest-neighbor. Di Remotion: gambar ke `<canvas>` ukuran logis di setiap `useCurrentFrame()`, tampilkan dengan `image-rendering: pixelated` dan `transform: scale(6)`. Semua koordinat dibulatkan ke grid setelah IK. Tanpa rotasi piksel yang buram dan tanpa tepi vektor halus. Lapis 1, 4, 5 skill dimatikan.
- **Tokoh (piksel logis):** garis tungkai putih 1 px dengan bayangan 1 px di kanan (#0c101c), tungkai jauh #c7cbd2; kepala radius luar 5 / dalam putih 4, outline #080e1c; torso 12, bahu ke kepala 8, tiap segmen kaki 9, tiap segmen lengan 7,3. Saat diam, kaki di pinggul x±2 dan tanah 17,85 di bawah pinggul. Setiap tokoh punya 1–2 aksesori profesi kecil yang menempel di bagian tubuhnya (topi koki + celemek; topi kurir + tas).
- **Huruf:** alfabet bitmap 7 baris, jarak antarhuruf 1 px, bayangan (1,1); krem #fff0cc, aksen teal #71c4c0. Tanpa font OS; karakter yang tidak ada di peta glyph harus memunculkan error, bukan diganti kotak.
- **Takarir:** satu baris; 16:9 di y=165 logis dengan lebar total ≤292; 9:16 ±60% lebar (maksimal 65%, margin ≥17,5% tiap sisi).
- **Dunia:** dithering terbatas, palet per lokasi/suasana. Tanpa scanline CRT, tanpa sarung tangan B4.
- **Aksi:** jalan dari samping dengan kaki bergantian dan telapak menapak; pilihan ditampilkan sebagai benda berbeda berlabel A/B/C, hanya satu yang disorot pada satu waktu. Kamera: konteks → close-up kontrol/properti → pemicu → kembali ke akibat.
- **Penutup wajib (kecuali pengguna menolak):** renungan dengan ketikan retro, teks berpendar lembut, gerak kecil, dan musik yang pas.

## 3. Tambahan skema manifest
```json
{
  "style": {
    "preset": "stickman-b7",
    "captionMode": "phrase",
    "cast": [{ "id": "kurir", "card": "stickman putih piksel, topi kurir biru, tas selempang cokelat" }]
  },
  "scenes": [
    {
      "id": "scene-03-tombol",
      "beat": "climax",
      "location": "kamar kos malam",
      "action": {
        "trigger": "kurir menekan tombol percepat",
        "contact": "tombol amblas di bawah telapak",
        "response": "kalender berganti cepat, kaki tetap di tempat",
        "reaction": "kurir menoleh kaget"
      },
      "exitState": "tangan masih di tombol, kamera close-up",
      "captionText": "Satu tombol, dan setahun lewat begitu saja."
    }
  ]
}
```
- `captionMode`: `karaoke` (default skill, per kata), `phrase` (frasa semantik satu baris; B5 boleh ≤3 baris), atau `bitmap` (B7). Waktu tetap diambil dari transkrip.

## 4. Pengganti aturan umum untuk preset ini
- **Lapis 1/4/5** (gradien bergerak, color grade, grain/vignette) dimatikan untuk A1 dan B7; diganti tekstur kertas untuk A3, B1, B2, B5; diganti lapis TV untuk B3.
- **Spring default** (snappy) diganti: A7 memakai damping rendah dengan overshoot; B7 memakai posisi yang dibulatkan ke grid piksel.
- **Voiceover tetap dari pengguna.** Repo asli memakai TTS (Gemini dan lainnya); di skill ini TTS tetap dilarang, dan musik/SFX tetap dari pengguna atau prosedural.
- **Micro-motion sinus** tetap boleh dipakai, tetapi tidak menggantikan Gerbang diam 2,5 detik.

## 5. Cek contact sheet tambahan
- Untuk adegan >3 detik, ambil frame tiap 1 detik: subjek utama harus berubah bermakna (gerbang 2,5 detik; B4 ≤3 detik per shot).
- Jumlah tungkai benar, tidak ada lengan tertinggal, tangan menyentuh benda yang dipegang, kaki menapak.
- Frame awal tiap adegan cocok dengan `exitState` adegan sebelumnya, atau potongan lokasinya jelas.
- Adegan terakhir menunjukkan perubahan, bukan pose diam.
- 9:16 tersusun ulang, tidak ada elemen penting terpotong; B7 tidak ada piksel buram atau ukuran piksel campur.
- Palet dan tokoh sesuai preset di semua adegan; tidak ada nama kanal atau aset dari repo asal.
