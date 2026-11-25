# Panduan Pola Adegan Storytelling & Safe Zone

## 1. Struktur 4 Babak Narasi
1. **Hook (0–3 detik pertama):** Pertanyaan memancing, fakta mengejutkan, atau visual kontras. Wajib langsung bergerak di frame 0 tanpa layar kosong.
2. **Setup / Konteks:** Penjelasan latar belakang masalah atau sejarah singkat dengan diagram bertahap / B-roll / objek 3D.
3. **Puncak Informasi (Climax):** Data utama, perbandingan skala, atau demonstrasi inti (energi `T3`).
4. **Resolusi / CTA:** Kesimpulan ringkas dan ajakan bertindak yang bersih.

## 2. Batas Kepadatan & Safe Zone
- **Aturan 7 Kata:** Headline utama maksimal 7 kata per adegan; teks pendukung maksimal 15–20 kata.
- **Mode Vertikal (9:16 — 1080x1920):**
  - Pusatkan teks utama dan objek 3D di area tengah (Y: 22% hingga 68%).
  - Letakkan **Takarir Karaoke** pada posisi `bottom: 18%` agar tidak pernah tertutup tombol UI Shorts/Reels/TikTok di **15% area terbawah**.
- **Mode Horizontal (16:9 — 1920x1080):**
  - Gunakan aturan sepertiga (*rule of thirds*) atau *split-screen* (kiri untuk teks/data, kanan untuk objek 3D/B-roll), dengan takarir karaoke di `bottom: 7%`.

## 3. Struktur Skema `manifest.json`
```json
{
  "projectTitle": "Judul Proyek",
  "mode": "hybrid",
  "fps": 30,
  "audioPath": "audio/voiceover.mp3",
  "scenes": [
    {
      "id": "scene-01-hook",
      "beat": "hook",
      "energy": "T3",
      "highlight": true,
      "visualType": "3d-showcase",
      "modelPath": "models/box.glb",
      "headline": "Maksimal Tujuh Kata Utama",
      "subtext": "Penjelasan singkat maksimal lima belas kata.",
      "anchor": "Tahukah kamu kemasan",
      "captionText": "Tahukah kamu, kemasan kertas jauh lebih ramah lingkungan?"
    }
  ]
}
```
- `captionText` wajib: kalimat voiceover persis seperti yang diucapkan di adegan itu.
- `anchor` opsional: 2–4 kata pertama yang diucapkan di adegan itu (default 3 kata pertama `captionText`). Adegan pertama selalu mulai di frame 0.
- **Jangan isi `durationInFrames`.** Durasi dihitung `sync_timeline.py` dari transkrip. Hanya boleh diisi sebagai override jika tidak ada voiceover sama sekali.
- `audioPath` relatif terhadap folder `public/`. Jika file belum ada, video dirender tanpa suara (skrip memberi peringatan).
