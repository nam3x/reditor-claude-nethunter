// Memuat font lokal dari public/fonts (diisi installer dari @fontsource) agar render offline & konsisten.
// Jika file tidak ada, Chromium memakai font sistem (fonts-inter dari apt) — render tetap jalan.
import { continueRender, delayRender, staticFile } from 'remotion';

const FILES: [string, string, string][] = [
  ['Inter', '400', 'inter-latin-400-normal.woff2'],
  ['Inter', '500', 'inter-latin-500-normal.woff2'],
  ['Inter', '700', 'inter-latin-700-normal.woff2'],
  ['Inter', '800', 'inter-latin-800-normal.woff2'],
  ['Poppins', '700', 'poppins-latin-700-normal.woff2'],
];

let started = false;
export function loadFonts() {
  if (started || typeof document === 'undefined') return;
  started = true;
  const handle = delayRender('fonts');
  Promise.all(
    FILES.map(async ([family, weight, file]) => {
      try {
        const face = new FontFace(family, `url(${staticFile(`fonts/${file}`)})`, { weight });
        await face.load();
        document.fonts.add(face);
      } catch {
        /* file belum ada -> fallback font sistem */
      }
    }),
  ).finally(() => continueRender(handle));
}
