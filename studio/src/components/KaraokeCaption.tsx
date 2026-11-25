import React, { useMemo } from 'react';
import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import type { WordTiming } from '../types';
import { theme } from '../theme';

const MAX_CHARS = 22; // kelompokkan per jumlah karakter, bukan jumlah kata

function groupLines(words: WordTiming[]) {
  const lines: WordTiming[][] = [];
  let cur: WordTiming[] = [];
  let len = 0;
  for (const w of words) {
    const add = w.word.length + (cur.length ? 1 : 0);
    if (cur.length && len + add > MAX_CHARS) {
      lines.push(cur);
      cur = [];
      len = 0;
    }
    cur.push(w);
    len += add;
    if (/[.!?]$/.test(w.word)) {
      lines.push(cur);
      cur = [];
      len = 0;
    }
  }
  if (cur.length) lines.push(cur);
  // tampilkan 2 baris per halaman
  const pages: WordTiming[][][] = [];
  for (let i = 0; i < lines.length; i += 2) pages.push(lines.slice(i, i + 2));
  return pages;
}

export const KaraokeCaption: React.FC<{ words: WordTiming[] }> = ({ words }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const isVertical = height > width;
  const pages = useMemo(() => groupLines(words ?? []), [words]);
  if (!pages.length) return null;

  // halaman aktif = halaman terakhir yang kata pertamanya sudah mulai
  let pageIdx = 0;
  pages.forEach((p, i) => {
    if (frame >= p[0][0].startFrame - 2) pageIdx = i;
  });
  const page = pages[pageIdx];
  const pageStart = page[0][0].startFrame;
  const pop = spring({ frame: frame - pageStart + 2, fps, config: theme.springs.snappy });

  return (
    <AbsoluteFill
      style={{
        justifyContent: 'flex-end',
        alignItems: 'center',
        paddingBottom: isVertical ? height * 0.26 : height * 0.07, // vertikal: di atas chip sumber (74,8%) & jauh dari 15% UI bawah
        pointerEvents: 'none',
      }}
    >
      <div style={{ transform: `scale(${0.92 + pop * 0.08})`, opacity: pop, textAlign: 'center' }}>
        {page.map((line, li) => (
          <div key={li} style={{ display: 'flex', justifyContent: 'center', gap: 16, flexWrap: 'nowrap' }}>
            {line.map((w, wi) => {
              const active = frame >= w.startFrame && frame < Math.max(w.endFrame, w.startFrame + 3);
              const past = frame >= w.endFrame;
              const s = spring({ frame: frame - w.startFrame, fps, config: theme.springs.bouncy });
              return (
                <span
                  key={wi}
                  style={{
                    fontFamily: theme.typography.fontHeading,
                    fontWeight: 800,
                    fontSize: isVertical ? 64 : 56,
                    lineHeight: 1.25,
                    color: active ? theme.colors.accentHighlight : past ? theme.colors.textPrimary : 'rgba(248,250,252,0.55)',
                    WebkitTextStroke: '2px rgba(0,0,0,0.55)',
                    paintOrder: 'stroke fill',
                    textShadow: '0 4px 18px rgba(0,0,0,0.6)',
                    display: 'inline-block',
                    transform: active ? `translateY(${-6 * s}px) scale(${1 + 0.08 * s})` : 'none',
                  }}
                >
                  {w.word}
                </span>
              );
            })}
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};
