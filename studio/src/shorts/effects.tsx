import React from 'react';

// Efek garis tipis putih + aksen emas lembut, menempel di wajah/badan (kanvas 1080x1440, ikut gerak kamera).
export const GOLD = '#E8C27A';
const stroke = { stroke: '#fff', strokeWidth: 4, fill: 'none', strokeLinecap: 'round' as const };

export type Anchor = [number, number, number]; // cx, cy, r (px kanvas 1080x1440)
export type Body = [number, number, number, number]; // x0, y0, x1, y1
type P = { f: number; face: Anchor; body: Body; a: number; beatIdx: number; beatsF: number[] };

const fade = (age: number, life: number) => Math.max(0, 1 - age / life);

/** hati garis putih (kadang isi emas) muncul tiap 2 ketukan di samping wajah, naik 6 px/frame, pudar setelah 40 frame */
const Hearts: React.FC<P> = ({ f, face, beatsF }) => {
  const [cx, cy, r] = face;
  const items = beatsF
    .map((bf, i) => ({ bf, i }))
    .filter(({ bf, i }) => i % 2 === 0 && f >= bf && f - bf < 40);
  return (
    <>
      {items.map(({ bf, i }) => {
        const age = f - bf;
        const side = i % 4 === 0 ? 1 : -1;
        const x = cx + side * (r * 1.6 + 20) + Math.sin(age / 5) * 10;
        const y = cy - age * 6;
        const s = 1 + 0.3 * Math.exp(-age / 6);
        const filled = i % 6 === 0;
        return (
          <path
            key={i}
            transform={`translate(${x} ${y}) scale(${s})`}
            d="M0 12 C -18 -4, -12 -22, 0 -10 C 12 -22, 18 -4, 0 12 Z"
            {...stroke}
            fill={filled ? GOLD : 'none'}
            opacity={fade(age, 40)}
          />
        );
      })}
    </>
  );
};

/** 3 bintang 4 sudut di sekitar wajah, berkelip + membesar di ketukan */
const Sparkle: React.FC<P> = ({ f, face, a }) => {
  const [cx, cy, r] = face;
  const pts = [[-1.5, -1.1], [1.6, -0.6], [1.2, 1.2]];
  return (
    <>
      {pts.map(([dx, dy], i) => {
        const tw = 0.6 + 0.4 * Math.sin(f / 4 + i * 2);
        const s = (0.8 + 0.6 * Math.exp(-a / 5)) * tw * (i === 0 ? 1.2 : 0.9);
        return (
          <path
            key={i}
            transform={`translate(${cx + dx * r} ${cy + dy * r}) scale(${s})`}
            d="M0 -22 Q 3 -3 22 0 Q 3 3 0 22 Q -3 3 -22 0 Q -3 -3 0 -22 Z"
            fill={i === 1 ? GOLD : '#fff'}
            opacity={tw}
          />
        );
      })}
    </>
  );
};

/** elips putus-putus emas di atas kepala, berputar, berdenyut di ketukan */
const Halo: React.FC<P> = ({ f, face, a }) => {
  const [cx, cy, r] = face;
  const pulse = 1 + 0.08 * Math.exp(-a / 5);
  return (
    <ellipse
      cx={cx}
      cy={cy - r * 1.35}
      rx={r * 0.95 * pulse}
      ry={r * 0.26 * pulse}
      stroke={GOLD}
      strokeWidth={4}
      fill="none"
      strokeDasharray="18 12"
      strokeDashoffset={-f * 2}
      opacity={0.9}
    />
  );
};

/** lingkaran mengembang dari wajah tiap ketukan */
const Rings: React.FC<P> = ({ face, a }) => {
  const [cx, cy, r] = face;
  return (
    <>
      {[0, 6].map((d) => {
        const age = a - d;
        if (age < 0 || age > 24) return null;
        return <circle key={d} cx={cx} cy={cy} r={r * (1 + age * 0.12)} {...stroke} strokeWidth={3} opacity={fade(age, 24)} />;
      })}
    </>
  );
};

/** 10 garis radial memancar dari wajah di ketukan */
const Burst: React.FC<P> = ({ face, a }) => {
  const [cx, cy, r] = face;
  if (a > 14) return null;
  const k = a / 14;
  return (
    <>
      {Array.from({ length: 10 }).map((_, i) => {
        const ang = (i / 10) * Math.PI * 2 + 0.3;
        const r0 = r * (1.4 + k * 1.2);
        const r1 = r0 + 40 * (1 - k);
        return (
          <line
            key={i}
            x1={cx + Math.cos(ang) * r0}
            y1={cy + Math.sin(ang) * r0}
            x2={cx + Math.cos(ang) * r1}
            y2={cy + Math.sin(ang) * r1}
            stroke={i % 3 === 0 ? GOLD : '#fff'}
            strokeWidth={4}
            strokeLinecap="round"
            opacity={1 - k}
          />
        );
      })}
    </>
  );
};

/** lengkung swoosh di kedua sisi badan, digambar dengan pathLength + strokeDashoffset */
const Arcs: React.FC<P> = ({ body, a }) => {
  const [x0, y0, x1, y1] = body;
  const h = y1 - y0;
  const draw = Math.min(1, a / 8);
  const op = Math.max(0, 1 - Math.max(0, a - 10) / 10);
  const midY = y0 + h * 0.45;
  return (
    <>
      {[
        `M ${x0 - 30} ${midY - h * 0.25} Q ${x0 - 110} ${midY} ${x0 - 30} ${midY + h * 0.25}`,
        `M ${x1 + 30} ${midY - h * 0.25} Q ${x1 + 110} ${midY} ${x1 + 30} ${midY + h * 0.25}`,
      ].map((d, i) => (
        <path key={i} d={d} {...stroke} stroke={i ? GOLD : '#fff'} pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - draw} opacity={op} />
      ))}
    </>
  );
};

const MAP: Record<string, React.FC<P>> = { hearts: Hearts, sparkle: Sparkle, halo: Halo, rings: Rings, burst: Burst, arcs: Arcs };

export const TrackedFx: React.FC<{ fx: string | null; f: number; face?: Anchor; body?: Body; a: number; beatIdx: number; beatsF: number[] }> = ({
  fx, f, face, body, a, beatIdx, beatsF,
}) => {
  if (!fx || !MAP[fx] || !face) return null;
  const C = MAP[fx];
  return (
    <svg width={1080} height={1440} viewBox="0 0 1080 1440" style={{ position: 'absolute', inset: 0, filter: 'drop-shadow(0 0 10px rgba(255,255,255,.55))', overflow: 'visible' }}>
      <C f={f} face={face} body={body ?? [face[0] - 200, face[1] - 100, face[0] + 200, 1440]} a={a} beatIdx={beatIdx} beatsF={beatsF} />
    </svg>
  );
};
