import React from 'react';
import { AbsoluteFill, Audio, Sequence, staticFile, interpolate, useVideoConfig } from 'remotion';
import timelineJson from './timeline.generated.json';
import type { Timeline } from './types';
import { StoryScene } from './StoryScene';
import { MovingGradient, ColorGrade, GrainVignette } from './components/Layers';
import { SourceChip } from './components/SourceChip';
import { Disclaimer } from './components/Disclaimer';

const timeline = timelineJson as unknown as Timeline;

export const StoryComposition: React.FC<{ variant: 'full' | 'highlight' }> = ({ variant }) => {
  const { durationInFrames, fps } = useVideoConfig();
  const scenes = variant === 'highlight' ? timeline.highlightScenes : timeline.fullScenes;
  const musicVol = timeline.musicVolume ?? 0.08; // jauh di bawah VO (±−20 LU)

  return (
    <AbsoluteFill style={{ backgroundColor: '#000' }}>
      {/* Lapis 1: latar konstan (transisi tidak pernah memperlihatkan layar kosong) */}
      <MovingGradient />

      {/* Lapis 2–3: adegan back-to-back, tanpa TransitionSeries */}
      {scenes.map((scene) => (
        <Sequence key={scene.id} from={scene.startFrame} durationInFrames={scene.durationInFrames} name={scene.id}>
          <StoryScene scene={scene} />
          {variant === 'highlight' && timeline.audioPath ? (
            <Audio
              src={staticFile(timeline.audioPath)}
              startFrom={scene.audioStartFrame}
              endAt={scene.audioStartFrame + scene.durationInFrames}
            />
          ) : null}
        </Sequence>
      ))}

      {/* Chip sumber mengikuti adegan berisi klaim (ikut terpotong benar di highlight) */}
      <SourceChip scenes={scenes} sources={timeline.sources ?? []} />
      {timeline.disclaimer ? <Disclaimer text={timeline.disclaimer} /> : null}

      {/* Lapis 4–5: grading + grain/vignette, sekali untuk seluruh video */}
      <ColorGrade />
      <GrainVignette />

      {/* Audio: VO utuh untuk timeline penuh; musik di bawah VO dengan fade */}
      {variant === 'full' && timeline.audioPath ? <Audio src={staticFile(timeline.audioPath)} /> : null}
      {timeline.musicPath ? (
        <Audio
          src={staticFile(timeline.musicPath)}
          loop
          volume={(f) =>
            musicVol *
            interpolate(f, [0, fps * 0.8, durationInFrames - fps, durationInFrames], [0, 1, 1, 0], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            })
          }
        />
      ) : null}
    </AbsoluteFill>
  );
};
