import React from 'react';
import {
  AbsoluteFill, Img, OffthreadVideo, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig,
} from 'remotion';
import type { Scene } from './types';
import { theme } from './theme';
import { KaraokeCaption } from './components/KaraokeCaption';
import { VfxOverlay } from './components/VfxOverlay';
import { useTransitionIn } from './components/transitions';

export const StoryScene: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const isVertical = height > width;
  const dur = scene.durationInFrames; // jangan pakai durasi komposisi untuk exit / Ken Burns
  const t = useTransitionIn(scene.transitionIn ?? 'fade', dur);

  // Ken Burns + exit lembut
  const kb = interpolate(frame, [0, dur], [1.04, 1.12], { extrapolateRight: 'clamp' });
  const exit = interpolate(frame, [dur - 8, dur], [1, 0.0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  const head = spring({ frame, fps, config: theme.springs.snappy });
  const sub = spring({ frame: frame - 5, fps, config: theme.springs.smooth });
  const float = Math.sin(frame / 18) * 6; // micro-motion saat diam

  return (
    <AbsoluteFill style={{ ...t.style }}>
      {/* Lapis 2: media */}
      {scene.visualType === 'footage' && scene.footage ? (
        <AbsoluteFill style={{ transform: `scale(${1 + (kb - 1) * 0.4})` }}>
          <OffthreadVideo
            src={staticFile(scene.footage)}
            startFrom={Math.round((scene.footageIn ?? 0) * fps)}
            muted
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          />
        </AbsoluteFill>
      ) : null}
      {scene.visualType === 'image' && scene.image ? (
        <AbsoluteFill style={{ transform: `scale(${kb})` }}>
          <Img src={staticFile(scene.image)} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        </AbsoluteFill>
      ) : null}
      {scene.visualType === 'footage' || scene.visualType === 'image' ? (
        <AbsoluteFill style={{ background: 'linear-gradient(180deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0) 35%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.65) 100%)' }} />
      ) : null}

      {/* VFX per adegan (light leak, dust, grain, flare) */}
      {(scene.vfx ?? []).map((v, i) => (
        <VfxOverlay key={i} file={v.file} blend={v.blend} opacity={v.opacity} />
      ))}

      {/* Lapis 3: grafis + takarir */}
      <AbsoluteFill
        style={{
          justifyContent: 'center',
          alignItems: isVertical ? 'center' : 'flex-start',
          padding: isVertical ? '0 80px' : '0 140px',
          top: isVertical ? '-12%' : 0,
          opacity: exit,
        }}
      >
        {scene.headline ? (
          <div
            style={{
              fontFamily: theme.typography.fontHeading,
              fontWeight: 800,
              fontSize: isVertical ? 88 : 104,
              lineHeight: 1.05,
              letterSpacing: -1.5,
              color: theme.colors.textPrimary,
              textAlign: isVertical ? 'center' : 'left',
              maxWidth: isVertical ? 920 : 1100,
              textShadow: '0 6px 30px rgba(0,0,0,0.45)',
              opacity: head,
              transform: `translateY(${(1 - head) * 40 + float}px) scale(${0.94 + head * 0.06})`,
            }}
          >
            {scene.headline}
          </div>
        ) : null}
        {scene.subtext ? (
          <div
            style={{
              marginTop: 28,
              fontFamily: theme.typography.fontBody,
              fontWeight: 500,
              fontSize: isVertical ? 44 : 46,
              color: theme.colors.textSecondary,
              textAlign: isVertical ? 'center' : 'left',
              maxWidth: isVertical ? 880 : 1000,
              opacity: sub,
              transform: `translateY(${(1 - sub) * 30}px)`,
            }}
          >
            {scene.subtext}
          </div>
        ) : null}
      </AbsoluteFill>

      <KaraokeCaption words={scene.wordTimings} />
      {t.flash}
    </AbsoluteFill>
  );
};
