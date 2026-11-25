import React from 'react';
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { theme } from '../theme';

/**
 * Transisi MASUK di dalam adegan (timeline tetap back-to-back, takarir tidak bergeser).
 * fade | slide | zoom | flash | whip | none
 */
export function useTransitionIn(kind: string, dur: number): { style: React.CSSProperties; flash: React.ReactNode } {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  const s = spring({ frame, fps, config: theme.springs.smooth, durationInFrames: Math.min(18, dur) });
  const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
  switch (kind) {
    case 'none':
      return { style: {}, flash: null };
    case 'slide':
      return { style: { transform: `translateX(${(1 - s) * width * 0.12}px)`, opacity: s }, flash: null };
    case 'zoom':
      return { style: { transform: `scale(${1.18 - 0.18 * s})`, opacity: s }, flash: null };
    case 'whip': {
      const blur = interpolate(frame, [0, 8], [40, 0], clamp);
      return { style: { transform: `translateX(${(1 - s) * width * 0.35}px)`, filter: `blur(${blur}px)` }, flash: null };
    }
    case 'flash': {
      const o = interpolate(frame, [0, 2, 9], [0.9, 0.7, 0], clamp);
      return { style: {}, flash: <AbsoluteFill style={{ background: '#fff', opacity: o, pointerEvents: 'none' }} /> };
    }
    default:
      return { style: { opacity: interpolate(frame, [0, 8], [0, 1], clamp) }, flash: null };
  }
}
