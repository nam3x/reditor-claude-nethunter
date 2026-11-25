export type WordTiming = { word: string; startFrame: number; endFrame: number };

export type Scene = {
  id: string;
  beat?: 'hook' | 'setup' | 'climax' | 'cta' | string;
  energy?: 'T1' | 'T2' | 'T3';
  highlight?: boolean;
  /** 'kinetic' (default) | 'footage' | 'image' | '3d-showcase' */
  visualType?: string;
  headline?: string;
  subtext?: string;
  captionText?: string;
  /** relatif ke public/, mis. "footage/clip01.mp4" (dari folder raw-footage/) */
  footage?: string;
  /** detik awal yang dipakai dari footage (trim in) */
  footageIn?: number;
  /** relatif ke public/, mis. "images/ref_01.jpg" (dari folder referensi/) */
  image?: string;
  /** VFX overlay opsional untuk adegan ini, relatif ke public/vfx/ */
  vfx?: { file: string; blend?: 'screen' | 'overlay' | 'soft-light' | 'multiply' | 'lighten'; opacity?: number }[];
  /** transisi masuk (dianimasikan di dalam adegan, tanpa tumpang tindih) */
  transitionIn?: 'fade' | 'slide' | 'zoom' | 'flash' | 'whip' | 'none';
  mood?: 'neutral' | 'warm' | 'cool' | 'tense' | 'happy';
  startFrame: number;
  durationInFrames: number;
  audioStartFrame: number;
  wordTimings: WordTiming[];
};

export type Source = { short: string; year?: string; full?: string; url?: string; claim?: string; scenes?: string[] };

export type Timeline = {
  projectTitle: string;
  fps: number;
  audioPath: string | null;
  musicPath?: string | null;
  musicVolume?: number;
  fullDurationInFrames: number;
  highlightDurationInFrames: number;
  fullScenes: Scene[];
  highlightScenes: Scene[];
  sources?: Source[];
  disclaimer?: string;
};
