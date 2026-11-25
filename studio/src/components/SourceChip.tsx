import React from 'react';
import { AbsoluteFill, Sequence, interpolate, useCurrentFrame, useVideoConfig } from 'remotion';
import type { Scene, Source } from '../types';

const Chip: React.FC<{ label: string; dur: number }> = ({ label, dur }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const isVertical = height > width;
  const fade = Math.round(fps * 0.25);
  const o = interpolate(frame, [0, fade, dur - fade, dur], [0, 1, 1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ alignItems: 'center', top: isVertical ? '74.8%' : '70%', pointerEvents: 'none' }}>
      <div
        style={{
          opacity: o,
          fontFamily: 'Poppins, Inter, sans-serif',
          fontWeight: 700,
          fontSize: 30,
          color: '#F8FAFC',
          background: 'rgba(10,12,20,0.62)',
          border: '1px solid rgba(255,255,255,0.18)',
          padding: '10px 22px',
          borderRadius: 999,
          whiteSpace: 'nowrap',
        }}
      >
        {label}
      </div>
    </AbsoluteFill>
  );
};

export const SourceChip: React.FC<{ scenes: Scene[]; sources: Source[] }> = ({ scenes, sources }) => (
  <>
    {sources.flatMap((src, i) =>
      scenes
        .filter((sc) => src.scenes?.includes(sc.id))
        .map((sc) => (
          <Sequence key={`${i}-${sc.id}`} from={sc.startFrame} durationInFrames={sc.durationInFrames} layout="none">
            <Chip label={`Sumber: ${src.short}${src.year ? ' · ' + src.year : ''}`} dur={sc.durationInFrames} />
          </Sequence>
        )),
    )}
  </>
);
