import React from 'react';
import { AbsoluteFill, useCurrentFrame } from 'remotion';
import { theme } from '../theme';

/** Lapis 1 — gradien bergerak pelan (tidak pernah layar kosong). */
export const MovingGradient: React.FC = () => {
  const f = useCurrentFrame();
  const x = 50 + Math.sin(f / 90) * 20;
  const y = 40 + Math.cos(f / 120) * 15;
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(circle at ${x}% ${y}%, ${theme.colors.bgSecondary} 0%, ${theme.colors.bgPrimary} 60%)`,
      }}
    />
  );
};

/** Lapis 4 — grading tipis (clean modern: kontras lembut, sedikit teal di bayangan). */
export const ColorGrade: React.FC = () => (
  <AbsoluteFill
    style={{
      pointerEvents: 'none',
      background: 'linear-gradient(180deg, rgba(20,60,90,0.10), rgba(255,170,90,0.06))',
      mixBlendMode: 'soft-light',
    }}
  />
);

/** Lapis 5 — vignette + grain prosedural (SVG turbulence, seed berganti tiap 2 frame). */
export const GrainVignette: React.FC = () => {
  const f = useCurrentFrame();
  const seed = Math.floor(f / 2) % 50;
  return (
    <AbsoluteFill style={{ pointerEvents: 'none' }}>
      <svg width="100%" height="100%" style={{ position: 'absolute', opacity: 0.07, mixBlendMode: 'overlay' }}>
        <filter id={`g${seed}`}>
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={seed} stitchTiles="stitch" />
        </filter>
        <rect width="100%" height="100%" filter={`url(#g${seed})`} />
      </svg>
      <AbsoluteFill style={{ background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,0.45) 100%)' }} />
    </AbsoluteFill>
  );
};
