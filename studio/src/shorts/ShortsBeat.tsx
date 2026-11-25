import React from 'react';
import {
  AbsoluteFill, Audio, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame,
} from 'remotion';
import dataJson from '../shorts.data.json';
import trackJson from '../track.json';
import { beatAt } from './beat';
import { camera } from './camera';
import { GOLD, TrackedFx, type Anchor, type Body } from './effects';

type Shot = { id: string; file: string; startF: number; durF: number; section: string; motion: string; effect: string | null; beatIdx: number };
type Data = { fps: number; totalF: number; dropF: number; beatsF: number[]; title: string; artist: string; audio: string | null; shots: Shot[] };
type Track = Record<string, { fx: string | null; face: Anchor[]; body: Body[] }>;

export const shortsData = dataJson as unknown as Data;
const tracks = trackJson as unknown as Track;
const TAIL = 12;
const CARD = { x: 70, y: 330, w: 940, h: 1253, r: 44 };
const S = CARD.w / 1080;
const font = 'Inter, system-ui, sans-serif';

/** Transisi masuk per bagian (klip sebelumnya tetap terlihat di bawah lewat ekor 12 frame). */
function entrance(section: string, local: number): React.CSSProperties {
  const c = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
  switch (section) {
    case 'intro':
    case 'outro':
      return { opacity: interpolate(local, [0, 12], [0, 1], c) };
    case 'main': {
      const k = interpolate(local, [0, 5], [1, 0], c);
      return { transform: `scale(${1 + 0.08 * k})`, filter: `blur(${6 * k}px)` };
    }
    case 'fast': {
      const k = interpolate(local, [0, 5], [1, 0], c);
      return { transform: `translateX(${160 * k}px)`, filter: `blur(${10 * k}px)` };
    }
    default:
      return {};
  }
}

const ShotLayer: React.FC<{ shot: Shot; bg?: boolean }> = ({ shot, bg }) => {
  const local = useCurrentFrame();
  const global = shot.startF + local;
  const d = shortsData;
  const cam = camera({ local, dur: shot.durF, motion: shot.motion, section: shot.section, global, beatsF: d.beatsF, dropF: d.dropF });
  const b = beatAt(global, d.beatsF, d.dropF);
  const tr = tracks[shot.id];
  const fi = Math.min(local, (tr?.face?.length ?? 1) - 1);
  const video = <OffthreadVideo src={staticFile(shot.file)} muted style={{ width: '100%', height: '100%', objectFit: 'cover' }} />;
  if (bg) {
    return <AbsoluteFill style={{ filter: 'blur(46px) brightness(.5) saturate(1.25)', transform: 'scale(1.15)' }}>{video}</AbsoluteFill>;
  }
  const flash = shot.section === 'drop' ? interpolate(local, [0, 2, 10], [0.55, 0.4, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }) : 0;
  return (
    <AbsoluteFill style={entrance(shot.section, local)}>
      {/* wadah gerak: video DAN efek ikut gerak kamera */}
      <div
        style={{
          position: 'absolute', width: 1080, height: 1440, transformOrigin: '50% 45%',
          transform: `translate(${cam.x}px, ${cam.y}px) rotate(${cam.rot}deg) scale(${cam.scale})`,
          filter: cam.blur > 0.05 ? `blur(${cam.blur}px)` : undefined,
        }}
      >
        {video}
        {tr ? (
          <TrackedFx fx={tr.fx} f={local} face={tr.face?.[fi]} body={tr.body?.[fi]} a={b.a} beatIdx={b.lastIdx}
            beatsF={d.beatsF.map((x) => x - shot.startF)} />
        ) : null}
      </div>
      {flash > 0 ? <AbsoluteFill style={{ background: '#fff', opacity: flash }} /> : null}
    </AbsoluteFill>
  );
};

const NowPlaying: React.FC<{ f: number; a: number }> = ({ f, a }) => {
  const d = shortsData;
  if (!d.title) return null;
  return (
    <div style={{ position: 'absolute', left: 70, top: 200, width: 940, height: 96, display: 'flex', alignItems: 'center', gap: 22,
      padding: '0 26px', boxSizing: 'border-box', borderRadius: 28, background: 'rgba(255,255,255,0.08)',
      border: '1.5px solid rgba(255,255,255,0.18)', backdropFilter: 'blur(14px)' }}>
      <svg width={58} height={58} viewBox="-30 -30 60 60" style={{ transform: `rotate(${f * 3}deg)` }}>
        <circle r={28} fill="#111" stroke="rgba(255,255,255,.35)" strokeWidth={1.5} />
        <circle r={18} fill="none" stroke="rgba(255,255,255,.12)" />
        <circle r={8} fill={GOLD} />
      </svg>
      <div style={{ flex: 1, minWidth: 0, fontFamily: font, color: '#fff' }}>
        <div style={{ fontSize: 30, fontWeight: 700, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{d.title}</div>
        <div style={{ fontSize: 24, fontWeight: 500, opacity: 0.65 }}>{d.artist}</div>
      </div>
      <div style={{ display: 'flex', gap: 6, alignItems: 'flex-end', height: 40 }}>
        {[0, 1, 2, 3, 4].map((i) => {
          const h = 10 + 28 * Math.abs(Math.sin(f / (4 + i) + i)) * (0.5 + 0.5 * Math.exp(-a / 6));
          return <div key={i} style={{ width: 6, height: h, borderRadius: 3, background: i === 2 ? GOLD : '#fff' }} />;
        })}
      </div>
    </div>
  );
};

export const ShortsBeat: React.FC = () => {
  const f = useCurrentFrame();
  const d = shortsData;
  const b = beatAt(f, d.beatsF, d.dropF);
  const afterDrop = f >= d.dropF && d.dropF > 0;
  const cardPulse = afterDrop ? 1 + 0.012 * Math.exp(-b.a / 4) : 1;
  const sweep = b.lastIdx >= 0 && b.lastIdx % 16 === 0 ? interpolate(b.a, [0, 18], [-0.4, 1.4], { extrapolateRight: 'clamp' }) : -1;
  const ring = b.lastIdx > 0 && b.lastIdx % 8 === 0 && b.a < 20 ? b.a / 20 : -1;
  const endFade = interpolate(f, [d.totalF - 20, d.totalF], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const progress = f / Math.max(1, d.totalF);

  return (
    <AbsoluteFill style={{ backgroundColor: '#07080c' }}>
      {/* latar: klip yang sama, blur */}
      {d.shots.map((s) => (
        <Sequence key={`bg-${s.id}`} from={s.startF} durationInFrames={s.durF + TAIL}>
          <ShotLayer shot={s} bg />
        </Sequence>
      ))}
      <AbsoluteFill style={{ background: 'linear-gradient(180deg, rgba(0,0,0,.25), rgba(0,0,0,.05) 40%, rgba(0,0,0,.45))' }} />

      <NowPlaying f={f} a={b.a} />

      {/* kartu */}
      <div style={{ position: 'absolute', left: CARD.x, top: CARD.y, width: CARD.w, height: CARD.h, borderRadius: CARD.r, overflow: 'hidden',
        transform: `scale(${cardPulse})`, boxShadow: '0 30px 80px rgba(0,0,0,.55)', opacity: endFade }}>
        <div style={{ position: 'absolute', width: 1080, height: 1440, transform: `scale(${S})`, transformOrigin: '0 0' }}>
          {d.shots.map((s) => (
            <Sequence key={s.id} from={s.startF} durationInFrames={s.durF + TAIL} layout="none">
              <ShotLayer shot={s} />
            </Sequence>
          ))}
        </div>
        {sweep > -1 ? (
          <div style={{ position: 'absolute', inset: 0, background: `linear-gradient(105deg, transparent ${sweep * 100 - 18}%, rgba(255,255,255,.22) ${sweep * 100}%, transparent ${sweep * 100 + 18}%)` }} />
        ) : null}
        <div style={{ position: 'absolute', inset: 0, borderRadius: CARD.r, border: '1.5px solid rgba(255,255,255,.28)', pointerEvents: 'none' }} />
      </div>

      {ring >= 0 ? (
        <div style={{ position: 'absolute', left: CARD.x - 20 * ring, top: CARD.y - 20 * ring, width: CARD.w + 40 * ring, height: CARD.h + 40 * ring,
          borderRadius: CARD.r + 20 * ring, border: `2px solid ${GOLD}`, opacity: 0.7 * (1 - ring) }} />
      ) : null}

      {/* progress bar tipis + 4 titik ketukan */}
      <div style={{ position: 'absolute', left: 70, top: 1630, width: 940, height: 4, borderRadius: 2, background: 'rgba(255,255,255,.18)' }}>
        <div style={{ width: `${progress * 100}%`, height: '100%', borderRadius: 2, background: '#fff' }} />
      </div>
      <div style={{ position: 'absolute', left: 0, right: 0, top: 1662, display: 'flex', justifyContent: 'center', gap: 16 }}>
        {[0, 1, 2, 3].map((i) => {
          const on = b.lastIdx >= 0 && ((b.lastIdx % 4) + 4) % 4 === i;
          return <div key={i} style={{ width: 10, height: 10, borderRadius: 5, background: on ? GOLD : 'rgba(255,255,255,.3)', transform: `scale(${on ? 1 + 0.5 * Math.exp(-b.a / 4) : 1})` }} />;
        })}
      </div>

      {/* grain 0.07 + vignette */}
      <svg width="100%" height="100%" style={{ position: 'absolute', inset: 0, opacity: 0.07, mixBlendMode: 'overlay', pointerEvents: 'none' }}>
        <filter id={`sg${f % 12}`}><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={f % 12} /></filter>
        <rect width="100%" height="100%" filter={`url(#sg${f % 12})`} />
      </svg>
      <AbsoluteFill style={{ background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,.5) 100%)', pointerEvents: 'none' }} />

      {d.audio ? <Audio src={staticFile(d.audio)} /> : null}
    </AbsoluteFill>
  );
};
