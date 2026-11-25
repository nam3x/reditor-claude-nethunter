import { beatAt, clamp01, inOutCubic } from './beat';

export type Cam = { x: number; y: number; rot: number; scale: number; blur: number };

/**
 * Motion control per shot (bergiliran) + goyang SEPERLUNYA:
 * hanya di drop, bagian fast, dan tiap 4 ketukan setelah drop (bukan intro/outro).
 */
export function camera(opts: {
  local: number; // frame di dalam shot
  dur: number;
  motion: string;
  section: string;
  global: number;
  beatsF: number[];
  dropF: number;
}): Cam {
  const { local, dur, motion, section, global, beatsF, dropF } = opts;
  const p = inOutCubic(clamp01(local / Math.max(1, dur)));
  let x = 0, y = 0, rot = 0, scale = 1.06;
  switch (motion) {
    case 'push': scale = 1.06 + 0.08 * p; break;
    case 'pull': scale = 1.15 - 0.09 * p; break;
    case 'pan': x = -22 + 44 * p; rot = -0.6 + 1.2 * p; scale = 1.1; break;
    case 'tilt': y = 20 - 40 * p; rot = -1.2 + 1.2 * p; scale = 1.1; break;
  }
  const b = beatAt(global, beatsF, dropF);
  const dropIdx = beatsF.findIndex((f) => f >= dropF);
  let A0 = 0;
  if (b.lastIdx === dropIdx) A0 = 18;
  else if (section === 'fast') A0 = 7;
  else if (b.beatsSinceDrop > 0 && b.beatsSinceDrop % 4 === 0 && section !== 'intro' && section !== 'outro') A0 = 6;
  const a = b.a;
  const amp = A0 * Math.exp(-a / 4);
  x += amp * Math.cos(a * 1.9) * (b.lastIdx % 2 ? 1 : -1) * 0.7;
  y += amp * Math.sin(a * 2.3) * 0.7;
  rot += amp * 0.04 * Math.cos(a * 1.9);
  scale += (A0 ? 0.002 * A0 : 0) * Math.exp(-a / 3.5);
  if (section !== 'intro' && section !== 'outro') {
    x += Math.sin(global * 0.11) * 2.5; // getar tangan sangat halus
    y += Math.cos(global * 0.09) * 2;
  }
  // motion blur hanya saat drop
  const blur = b.lastIdx === dropIdx ? 3 * Math.exp(-a / 3) : 0;
  return { x, y, rot, scale, blur };
}
