import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from 'remotion';

export const Disclaimer: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const o = interpolate(frame, [0, 8, fps * 3 - 8, fps * 3], [0, 1, 1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ alignItems: 'center', top: '12.5%', pointerEvents: 'none' }}>
      <div style={{ opacity: o * 0.85, fontFamily: 'Inter, sans-serif', fontSize: 26, color: '#E2E8F0', background: 'rgba(0,0,0,0.45)', padding: '6px 16px', borderRadius: 8 }}>
        {text}
      </div>
    </AbsoluteFill>
  );
};
