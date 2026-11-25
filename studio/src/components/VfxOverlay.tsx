import React from 'react';
import { AbsoluteFill, Img, OffthreadVideo, staticFile } from 'remotion';

/**
 * VFX overlay dari folder VFX/ (disalin ke public/vfx/).
 * Video overlay hitam-latar (light leak, flare, dust) dipasang dengan blend 'screen'.
 * Grain/texture abu-abu netral cocok dengan 'overlay' / 'soft-light'.
 */
export const VfxOverlay: React.FC<{ file: string; blend?: string; opacity?: number }> = ({ file, blend = 'screen', opacity = 0.8 }) => {
  const src = staticFile(file.startsWith('vfx/') ? file : `vfx/${file}`);
  const style: React.CSSProperties = {
    width: '100%', height: '100%', objectFit: 'cover',
    mixBlendMode: blend as React.CSSProperties['mixBlendMode'], opacity,
  };
  const isVideo = /\.(mp4|mov|webm|mkv)$/i.test(file);
  return (
    <AbsoluteFill style={{ pointerEvents: 'none', mixBlendMode: blend as React.CSSProperties['mixBlendMode'] }}>
      {isVideo ? <OffthreadVideo src={src} muted style={style} /> : <Img src={src} style={style} />}
    </AbsoluteFill>
  );
};
