// Konfigurasi Remotion yang ramah HP (Kali NetHunter chroot, arm64, tanpa GPU).
// Semua nilai bisa ditimpa lewat env tanpa mengedit file ini.
import { Config } from '@remotion/cli/config';
import fs from 'node:fs';

const env = process.env;

// 1) Browser: pakai Chrome Headless Shell bawaan Remotion (linux-arm64 didukung).
//    Jika unduhan diblokir / gagal di chroot, pakai Chromium dari apt.
const candidates = [
  env.REDITOR_BROWSER,
  '/usr/bin/chromium',
  '/usr/bin/chromium-browser',
  '/usr/lib/chromium/chromium',
].filter(Boolean) as string[];
if (env.REDITOR_BROWSER && fs.existsSync(env.REDITOR_BROWSER)) {
  Config.setBrowserExecutable(env.REDITOR_BROWSER);
} else if (env.REDITOR_USE_SYSTEM_CHROMIUM === '1') {
  const found = candidates.find((p) => fs.existsSync(p));
  if (found) Config.setBrowserExecutable(found);
}

// 2) Render CPU-only: swangle = WebGL lewat SwiftShader (aman untuk @remotion/three tanpa GPU).
Config.setChromiumOpenGlRenderer((env.REDITOR_GL as 'swangle' | 'angle' | 'egl' | 'swiftshader') || 'swangle');

// 3) HP punya RAM terbatas: concurrency kecil, JPEG frame (lebih ringan dari PNG).
Config.setConcurrency(Number(env.REDITOR_CONCURRENCY || 2));
Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(Number(env.REDITOR_JPEG_QUALITY || 88));
Config.setOverwriteOutput(true);

// 4) Encoding: H.264 + AAC, CRF moderat (cukup tajam untuk Shorts/YouTube).
Config.setCodec('h264');
Config.setCrf(Number(env.REDITOR_CRF || 20));
Config.setPixelFormat('yuv420p');

// 5) Timeout lebih panjang: CPU HP lambat saat frame pertama / adegan 3D.
Config.setDelayRenderTimeoutInMilliseconds(Number(env.REDITOR_TIMEOUT_MS || 120000));
