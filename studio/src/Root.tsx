import React from 'react';
import { Composition } from 'remotion';
import timelineJson from './timeline.generated.json';
import { StoryComposition } from './StoryComposition';
import type { Timeline } from './types';
import { loadFonts } from './fonts';

loadFonts();

const timeline = timelineJson as unknown as Timeline;
const fps = timeline.fps || 30;

export const RemotionRoot: React.FC = () => (
  <>
    {/* Mode B — YouTube 16:9 */}
    <Composition
      id="MainStory"
      component={StoryComposition}
      durationInFrames={Math.max(1, timeline.fullDurationInFrames)}
      fps={fps}
      width={1920}
      height={1080}
      defaultProps={{ variant: 'full' as const }}
    />
    {/* Mode A / Mode C Full — 9:16 timeline penuh */}
    <Composition
      id="ShortVertical"
      component={StoryComposition}
      durationInFrames={Math.max(1, timeline.fullDurationInFrames)}
      fps={fps}
      width={1080}
      height={1920}
      defaultProps={{ variant: 'full' as const }}
    />
    {/* Mode C Short — hanya adegan highlight */}
    <Composition
      id="HighlightVertical"
      component={StoryComposition}
      durationInFrames={Math.max(1, timeline.highlightDurationInFrames || 1)}
      fps={fps}
      width={1080}
      height={1920}
      defaultProps={{ variant: 'highlight' as const }}
    />
  </>
);
