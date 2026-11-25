# Standar Koreografi & Gerak 2D Remotion

## 1. Kurva & Fisika Gerak
- **Dilarang** menggunakan `Math.random()`, `Date.now()`, atau CSS `transition` / `animation`.
- Gunakan `spring()` untuk masuknya elemen dengan konfigurasi snappy (`mass: 0.8, damping: 14, stiffness: 180`).
- Seluruh `interpolate()` wajib menyertakan `{ extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }`.
- Animasi keluar (*exit*) harus **1.5x lebih cepat** daripada animasi masuk (*entrance*): masuk 15 frame (`spring({..., durationInFrames: 15})`), keluar 10 frame.
- Jangan pakai `TransitionSeries` dengan transisi tumpang tindih: durasi video jadi lebih pendek dari timeline dan takarir tertinggal dari voiceover.

## 2. Koreografi & Stagger
- Terapkan *stagger* 3–6 frame antar elemen atau antar kata pada tipografi kinetik.
- Gunakan masuk multi-properti sekaligus: `opacity` (0 -> 1), `translateY` (24px -> 0), dan `scale` (0.94 -> 1).
- Tambahkan *micro-motion* halus pada elemen yang sedang diam agar layar tidak pernah membeku:
  `const floatY = Math.sin(frame / 15) * 4;`

## 3. Komposisi 5 Lapis Wajib
Susunan dari bawah ke atas. Lapis 1, 4, 5 sudah tersedia di `components/Layers.tsx` dan dirender sekali di `StoryComposition` (konstan, tidak berkedip saat ganti adegan); `StoryScene` hanya mengisi lapis 2–3 dengan latar transparan:
1. **Lapisan 1 (Base):** Gradient mesh gelap/bertekstur yang bergerak perlahan.
2. **Lapisan 2 (Media / 3D):** `<OffthreadVideo>`, gambar dengan *Ken Burns* (`scale` 1.0 -> 1.08), atau `<ThreeStage>`.
3. **Lapisan 3 (Grafis, Tipografi & Takarir):** Kartu kaca (*glassmorphism*), teks utama, dan `<KaraokeCaption>`.
4. **Lapisan 4 (Color Grade):** Overlay gradien halus untuk menyatukan kontras teks.
5. **Lapisan 5 (Tekstur & Vignette):** *Film grain* tipis (SVG `feTurbulence` dengan `seed = frame % 12`, `opacity` ±0.05) + vignette tepi layar (`pointerEvents: 'none'`).
