# VFX/ — paket efek untuk edit clean & modern

Semua file di folder ini **dibuat sendiri secara prosedural** oleh `editor/gen_vfx.sh` (ffmpeg + Python),
jadi bebas lisensi untuk proyek ini (komersial/YouTube aman). Buat ulang / tambah durasi:
`reditor vfx` atau `bash editor/gen_vfx.sh VFX 6 --with-music`.

| Folder | Isi | Blend | Opacity saran | Kapan dipakai |
|---|---|---|---|---|
| `light-leaks/` | leak_warm, leak_amber, leak_cool, leak_magenta (4 dtk loop) | `screen` | 0.3–0.6 | transisi, momen emosional, intro |
| `flares/` | flare_blue_sweep (anamorphic streak) | `screen` | 0.4–0.8 | reveal judul, produk |
| `dust/` | dust_float (partikel halus), bokeh_soft | `screen` | 0.2–0.5 | intro/outro, adegan tenang |
| `grain/` | grain_fine, grain_35mm (abu-abu netral) | `overlay` / `soft-light` | 0.08–0.15 | seluruh video (tekstur sinematik) |
| `textures/` | vignette 9:16 & 16:9 (PNG alpha), scanlines | normal / `multiply` | 0.3–0.6 | fokus ke tengah, gaya retro |
| `transitions/` | flash_white_0.4s, light_sweep_0.6s | `screen` | 0.6–1 | hook / klimaks (maks 2 per video) |
| `luts/` | clean_bright, teal_orange, moody_film, warm_soft, bw_contrast (.cube 33³) | `lut3d` | strength 0.6–0.85 | satu LUT untuk seluruh video |
| `sfx/` | whoosh_soft, pop, click, ding, impact_low, riser_2s (WAV 48 kHz) | — | −12 s/d −18 dB | whoosh=transisi, pop=teks, impact=klimaks |

Pemakaian:
- **Mode Editor** (`edit.json`): `"vfx": [{"file": "VFX/light-leaks/leak_warm_01.mp4", "blend": "screen", "opacity": 0.45}]`
- **Mode Remotion** (`studio/manifest.json`): `"vfx": [{"file": "vfx/light-leaks/leak_warm_01.mp4", "blend": "screen", "opacity": 0.45}]`
- LUT juga bisa dipakai di CapCut/VN/LumaFusion (impor file `.cube`).

## Menambah VFX dari internet (cek lisensi per file!)
Taruh file unduhan di subfolder yang sesuai (mis. `VFX/light-leaks/`). Overlay berlatar hitam → blend `screen`.
Lisensi bisa berbeda per klip di situs yang sama — baca halaman lisensi sebelum dipakai di konten monetisasi.

| Sumber | Isi | Catatan lisensi |
|---|---|---|
| Mixkit — https://mixkit.co/free-stock-video/overlays/ | light leak, partikel, bokeh, film burn | Free License: komersial tanpa atribusi; sebagian klip **Restricted** (non-komersial). Cek per klip. |
| Pexels — https://www.pexels.com/search/videos/light%20leak/ | light leak, dust, bokeh, footage stok | Pexels License: gratis, tanpa atribusi; tidak boleh dijual ulang apa adanya. |
| Pixabay — https://pixabay.com/videos/search/overlay/ | overlay, partikel, musik & SFX | Pixabay Content License: gratis komersial tanpa atribusi (dengan pengecualian tertentu). |
| Videezy — https://www.videezy.com/free-video/overlay | overlay, film grain | Item "Free License" wajib atribusi; item Pro berbayar. |
| Motion Array — https://motionarray.com/video-effects/free-light-leaks-overlays/ | light leak pack gratis | Perlu akun; ikuti lisensi Motion Array. |
| PremiumBeat — https://www.premiumbeat.com/blog/10-free-film-grains-for-video-editors/ | film grain 35mm gratis | Freebie blog; baca syarat di halaman unduhan. |
| Uppbeat — https://uppbeat.io/motion-graphics/category/overlays | overlay & musik | Tier gratis butuh kredit/akun. |

Musik: pakai file dari pengguna di `Musik/`, YouTube Audio Library, Pixabay Music, atau bed prosedural
(`Musik/bed_procedural_clean.mp3`). Jangan meniru lagu yang ada.
