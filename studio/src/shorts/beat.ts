// Utilitas ketukan untuk ShortsBeat (semua dalam frame global komposisi).
export type BeatInfo = {
  lastIdx: number; // indeks ketukan terakhir yang sudah lewat
  lastF: number; // frame ketukan terakhir
  a: number; // frame sejak ketukan terakhir
  beatsSinceDrop: number; // <0 sebelum drop
};

export function beatAt(frame: number, beatsF: number[], dropF: number): BeatInfo {
  let lo = 0;
  let hi = beatsF.length - 1;
  let idx = -1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (beatsF[mid] <= frame) {
      idx = mid;
      lo = mid + 1;
    } else hi = mid - 1;
  }
  const lastF = idx >= 0 ? beatsF[idx] : 0;
  const dropIdx = beatsF.findIndex((b) => b >= dropF);
  return { lastIdx: idx, lastF, a: frame - lastF, beatsSinceDrop: dropIdx >= 0 ? idx - dropIdx : -1 };
}

export const inOutCubic = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
export const clamp01 = (t: number) => Math.max(0, Math.min(1, t));
