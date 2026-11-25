# Aturan Wajib Adegan 3D (`@remotion/three`)

## 1. Tiga Hukum Deterministik
1. **Dilarang keras memakai `useFrame()`** dari `@react-three/fiber`. Semua posisi, rotasi, dan pergerakan kamera wajib dihitung murni dari `useCurrentFrame()` dan `spring()`.
2. **Wajib `layout="none"` pada `<Sequence>`:** Di dalam `<ThreeCanvas>`, setiap `<Sequence>` harus ditulis `<Sequence layout="none">` agar tidak menyisipkan tag `<div>` ke dalam graf WebGL.
3. **Renderer ANGLE:** Pastikan konfigurasi render menyertakan `--gl=angle` (atau `Config.setChromiumOpenGlRenderer('angle')` di `remotion.config.ts`).

## 2. Optimasi Aset 3D
- Gunakan format `.glb` terkompresi di folder `public/models/` dan muat dengan `useGLTF()`.
- Pasang pencahayaan lingkungan dari file HDRI ringan atau kombinasi `ambientLight` + `directionalLight` dengan `castShadow` terukur agar waktu render tetap cepat.
