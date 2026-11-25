import { SpringConfig } from 'remotion';

export const theme = {
  colors: {
    bgPrimary: '#0B0F19',
    bgSecondary: '#131A2A',
    surfaceGlass: 'rgba(15, 23, 42, 0.72)',
    surfaceBorder: 'rgba(255, 255, 255, 0.16)',
    textPrimary: '#F8FAFC',
    textSecondary: '#94A3B8',
    accentPrimary: '#38BDF8',
    accentHighlight: '#F59E0B',
  },
  typography: {
    fontHeading: 'Inter, system-ui, sans-serif',
    fontBody: 'Inter, system-ui, sans-serif',
    fontMono: 'JetBrains Mono, monospace',
  },
  springs: {
    snappy: { mass: 0.8, damping: 14, stiffness: 180 } satisfies Partial<SpringConfig>,
    smooth: { mass: 1.0, damping: 18, stiffness: 120 } satisfies Partial<SpringConfig>,
    bouncy: { mass: 0.7, damping: 10, stiffness: 200 } satisfies Partial<SpringConfig>,
  },
};
