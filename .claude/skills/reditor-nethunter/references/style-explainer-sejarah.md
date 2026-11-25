# Preset Style: Explainer Sejarah Chibi (2D flat-shaded, 16:9)

Diturunkan dari analisis video referensi explainer sejarah berbahasa Indonesia (4:12, 1920x1080, 30 fps, −14 LUFS). Yang ditiru adalah GAYA dan TEKNIK, bukan aset. DILARANG memakai logo, nama kanal, desain karakter persis, atau end card studio mana pun; kartu logo dan end card memakai brand pengguna (tanyakan nama brand jika belum ada).

## 1. Format & audio
- Default Mode B (16:9, 1920x1080, 30 fps); Mode C boleh, highlight = adegan hook + angka statistik + klimaks.
- Durasi wajar 2–5 menit. Shot rata-rata 4–6 detik, satu ide per shot.
- Audio bersambung tanpa jeda (VO + musik + SFX); satu-satunya jeda yang disengaja ±0,8 detik di sting logo. Mix akhir −14 LUFS, puncak ≤ −1 dB: `ffmpeg -i in.mp4 -af loudnorm=I=-14:TP=-1:LRA=11 -c:v copy out.mp4`.
- SFX diegetik bila pengguna menyediakan (ledakan, helikopter, hujan, langkah). Jangan mengunduh SFX/musik dari internet tanpa izin pengguna.

## 2. Struktur babak (isi `beat` di manifest)
| Urutan | beat | Isi | Energi |
|---|---|---|---|
| 1 | `cold-open` | Tanggal/tempat di objek (kalender, surat, papan) + suasana tegang | T2 |
| 2 | `hook-action` | 20–35 dtk aksi dramatis tanpa konteks, kekerasan distilasi | T3 |
| 3 | `logo-sting` | Kartu brand 3–4 dtk, latar warna aksen solid | T2 |
| 4 | `human-impact` | Sudut pandang orang biasa (warga, keluarga) | T1–T2 |
| 5 | `stat-punch` | Montase polaroid + kartu statistik angka besar | T3 |
| 6 | `map-context` | Peta ilustrasi + bola-bendera bergerak | T2 |
| 7 | `flashback-cause` | Kartu tahun mundur, tokoh, konferensi, sebab | T1–T2 |
| 8 | `escalation` | Klimaks konflik | T3 |
| 9 | `explain-how` | Diagram potongan melintang/berlabel (cara/taktik/mekanisme) | T2 |
| 10 | `turning-point` | Opini publik, berita, protes | T2 |
| 11 | `resolution` | Dokumen/perjanjian, pesan penutup | T1 |
| 12 | `end-card` | Panel warna aksen kiri + kredit/CTA kanan, frame terakhir digelapkan | T1 |
Babak boleh digabung untuk video pendek, tetapi urutan hook → logo → isi → resolusi → end card dipertahankan.

## 3. Bahasa visual
- **Ilustrasi flat dengan shading lembut**: gradien halus, rim light 1–2 px warna terang, bayangan lunak (`filter: blur`), bukan flat datar.
- **Kedalaman 2.5D**: 3–4 lapis parallax (latar jauh blur 6–10 px, tengah tajam, latar depan gelap blur besar yang melintas). Kamera selalu bergerak: push-in `scale` 1.0→1.06 sepanjang adegan, atau pan 40–120 px.
- **Manusia = chibi** (SVG primitif): kepala bulat ±45% tinggi badan, badan kapsul kecil, tangan bulat tanpa jari, mata titik/garis, tanpa hidung/mulut detail. Identitas lewat atribut: helm (tentara), caping/topi khas (warga), jas+dasi (politisi), rambut putih+janggut (tokoh tua). Ekspresi lewat bentuk mata (`> <`), alis miring, tetes keringat, ikon "!" pop-in.
- **Negara/organisasi = bola-bendera**: lingkaran dengan pola bendera (SVG `clipPath`), highlight specular di kiri atas, bayangan elips di bawah, mata/aksesori penanda (kacamata hitam, topi, kumis). Gambar bendera sebagai bentuk sederhana dari kode, bukan mengunduh.
- **Massa = siluet** hitam/gelap dengan rim light tipis (penonton, demonstran, wartawan).
- **Kekerasan distilasi**: siluet di latar merah dengan speed lines, percikan merah abstrak, darah hanya bentuk merah sederhana. Tidak ada luka realistis.
- **Partikel ambien** selalu ada (debu, daun, abu, hujan diagonal, bintik cahaya), deterministik dari `frame` dan `random(seed)` Remotion.
- **Vignette kuat** di hampir semua adegan (lapis 5), lebih tebal di adegan gelap.

## 4. Grading per suasana (`mood` per adegan → lapis 4 `ColorGrade`)
| mood | Palet acuan | Perlakuan |
|---|---|---|
| `past-sepia` | `#463C2F` `#7B6750` `#302A23` | sepia, kontras rendah, vignette kuat |
| `danger` | `#000000` `#952E2E` `#46191A` | siluet hitam + merah tua, speed lines |
| `village` | `#60574E` `#736D62` `#867E6F` | hangat redup |
| `fire` | `#261A18` `#61372A` `#AB7350` + oranye api | glow oranye, asap |
| `grief` | `#3C3E3C` `#616662` `#79807E` | desaturasi ±80%, sedikit blur tepi |
| `map-calm` | `#949445` `#8CB9B0` `#B1D6D5` | cerah, zaitun + toska |
| `map-war` | `#9D413A` `#7F392F` glow `#BFA44F` | merah bata, garis pantai menyala |
| `jungle` | `#4E3710` `#573E0F` hijau daun | hangat lembap |
| `archive-tv` | abu + scanline | desaturasi, scanline, vignette bulat |
Warna aksen brand (default merah coral `#EE3048`, boleh diganti brand pengguna) hanya dipakai di kartu logo, label diagram, dan end card.

## 5. Kartu teks (isi `onScreenText` di manifest; teks layar minimal, sisanya dibawa VO)
- `yearCard`: tahun besar putih pojok kiri bawah, fade + geser 12 px. Wajib di setiap lompatan waktu.
- `statCard`: dua baris — angka besar (mis. "2.000.000") + label kapital pendek — di atas foto/polaroid. Wajib untuk setiap angka penting.
- `nameLabel`: nama tokoh diketik per huruf (2 frame/huruf) di samping tokoh.
- `diagramLabel`: kotak warna aksen, teks putih kapital, pop-in overshoot (`springs.bouncy`), dipakai di diagram potongan melintang.
- `objectText`: tulisan di objek (kalender, papan protes, dokumen), ikut bergerak bersama objek.
- Font: sans geometris sangat tebal (Poppins/Montserrat 800), putih, bayangan lembut `0 4px 16px rgba(0,0,0,.35)`.
- Takarir karaoke: tetap tersedia, tetapi untuk preset ini tanyakan pengguna apakah ingin ditampilkan (video referensi tidak memakai takarir terbakar). Jika ya, gaya kecil di `bottom: 7%` agar tidak bersaing dengan kartu teks.

## 6. Transisi (isi `transitionIn`; dibuat sebagai animasi masuk adegan, TANPA tumpang tindih)
`foreground-wipe` (objek gelap latar depan menyapu layar) · `whip-flash` (blur geser 6 frame + flash warna solid 2 frame) · `zoom-through` (zoom menembus objek) · `split-panel` (panel bergeser dengan garis pemisah putih) · `splatter` (percikan merah membesar menutup layar) · `map-morph` (warna peta berubah di tempat) · `tv-static` (scanline + desaturasi) · `polaroid-pin` (foto jatuh dan tertempel) · `logo-assemble` (garis-garis menyatu jadi logo). Variasikan: jangan pakai transisi yang sama dua kali berturut-turut.

## 7. Gerak & animasi
- Karakter gaya puppet/cut-out: rig sederhana (kepala, badan, 2 tangan, 2 kaki) dengan rotasi sendi dari `Math.sin(frame/…)`; jalan memantul `translateY = |sin|·6px`.
- Getar kamera saat ledakan: offset 4–10 px meluruh 12 frame, deterministik.
- Elemen ikon/label masuk dengan overshoot (`springs.bouncy`); teks tahun dan statistik dengan `springs.smooth`.
- Speed lines radial dan motion blur (`filter: blur` horizontal) untuk aksi T3.

## 8. Pustaka komponen yang disarankan
`Chibi` (props: role, outfit, headwear, expression, pose) · `FlagBall` (props: flag pattern, accessory, expression) · `SilhouetteCrowd` · `ParallaxScene` (layers[]) · `IllustratedMap` (region, mode calm/war, glowCoast) · `CrossSection` (tunnels/rooms + diagramLabel) · `PolaroidBoard` · `Calendar` · `Document` · `ProtestSign` · `RetroTV` · `Explosion`/`Fire`/`Smoke`/`Rain`/`Leaves` · `YearCard` · `StatCard` · `NameLabel` · `LogoSting` · `EndCard`. Semua dibuat dari SVG/CSS di kode; aset statis yang berat (latar parallax) masuk alur Cache Aset PNG.

## 9. Tambahan skema manifest untuk preset ini
```json
{
  "style": { "preset": "explainer-sejarah-chibi", "accent": "#EE3048", "brandName": "<brand pengguna>" },
  "scenes": [
    {
      "id": "scene-05-stat",
      "beat": "stat-punch",
      "energy": "T3",
      "mood": "grief",
      "transitionIn": "polaroid-pin",
      "onScreenText": [{ "type": "statCard", "value": "2.000.000", "label": "WARGA TEWAS" }],
      "captionText": "..."
    }
  ]
}
```

## 10. Contoh override `theme.ts`
```ts
colors: {
  bgPrimary: '#1E1A17', bgSecondary: '#2B2420',
  surfaceGlass: 'rgba(20,16,14,0.6)', surfaceBorder: 'rgba(255,255,255,0.14)',
  textPrimary: '#FFFFFF', textSecondary: '#D9D2C7',
  accentPrimary: '#EE3048', accentHighlight: '#F2B84B',
},
typography: { fontHeading: 'Poppins, sans-serif', fontBody: 'Poppins, sans-serif', fontMono: 'JetBrains Mono, monospace' },
```
Lapis 1 `MovingGradient` diganti latar ilustrasi adegan; glassmorphism tidak dipakai di preset ini.

## 11. Pemeriksaan contact sheet khusus preset
- Setiap lompatan waktu punya `yearCard`; setiap angka penting punya `statCard`.
- Tidak ada frame yang kamera/elemennya benar-benar diam.
- Grading berubah sesuai `mood`; adegan duka benar-benar desaturasi.
- Tidak ada logo/nama kanal pihak lain; kekerasan tetap distilasi.
