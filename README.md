# reditor — Claude Code video editor untuk Kali NetHunter

Edit video **langsung dari HP** lewat terminal NetHunter: Claude Code + skill `reditor-nethunter`
(turunan *remotion-storyteller*) + editor ffmpeg ringan + paket VFX bebas lisensi + peta kode graphify.

```
raw-footage/   klip & foto mentah            VO/      voiceover final (dipakai apa adanya)
referensi/     gambar/video acuan gaya       Musik/   musik latar (di-duck otomatis di bawah VO)
VFX/           light leak, flare, dust, grain, LUT .cube, transisi, SFX (prosedural, bebas lisensi)
editor/        editor ffmpeg (EDL JSON), transkripsi, generator VFX/LUT
studio/        proyek Remotion (Shorts 9:16, YouTube 16:9, highlight; takarir karaoke; sumber fakta)
bin/reditor    CLI satu pintu
.claude/skills/reditor-nethunter/   skill Claude Code (aturan sutradara + referensi preset)
docs/REKOMENDASI.md                 referensi kode lain yang lebih kuat + saran integrasi
```

## Pasang di NetHunter (sekali)
1. Buka **NetHunter Terminal → Kali** (chroot, root).
2. Clone ke filesystem chroot (bukan `/sdcard`):
   ```bash
   cd /root && git clone https://github.com/nam3x/reditor-claude-nethunter.git
   cd reditor-claude-nethunter && bash install/nethunter-setup.sh
   ```
   Installer memasang ffmpeg, Node ≥ 18, Python, font, library Chromium, `npm install` studio
   (Chrome Headless Shell linux-arm64 atau fallback `chromium` apt), **graphify**, faster-whisper,
   membuat paket VFX, menautkan perintah `reditor`, dan Claude Code CLI.
3. `reditor doctor` → semua `[ok]`.

## Pakai
**Dengan Claude (disarankan):**
```bash
cd /root/reditor-claude-nethunter && claude
> edit raw footage di folder raw-footage pakai VO, gaya clean modern 9:16
```
**Manual (Mode Editor, paling cepat di HP):**
```bash
cp /sdcard/DCIM/Camera/*.mp4 raw-footage/ ; cp /sdcard/Download/vo.mp3 VO/
reditor transcribe          # VO -> transcript.json (per kata)
reditor edit auto 9:16      # susun edit.json dari raw-footage
reditor edit preview        # 540p cepat
reditor edit render         # 1080p final -> out/edit_final.mp4
reditor export              # salin ke /sdcard/Movies/reditor
```
**Manual (Mode Remotion / motion graphic):**
```bash
reditor link && reditor sync           # folder -> studio/public, manifest -> timeline
reditor still ShortVertical 45         # cek 1 frame
reditor render short                   # out: studio/out/short_9x16.mp4
```

## Tips HP
- Isi daya + matikan optimasi baterai untuk NetHunter Terminal saat render panjang.
- RAM < 4 GB: `export REDITOR_CONCURRENCY=1`. Transkripsi lebih ringan: `reditor transcribe VO/x.mp3 --model base`.
- Render panjang di latar: `nohup reditor render short > out/render.log 2>&1 & tail -f out/render.log`.

Teruji di container x86_64 (Remotion 4.0.540 still + render, editor ffmpeg 1080/540p, loudnorm −14 LUFS).
Di perangkat arm64 nyata belum diuji — jalankan `reditor doctor` dan laporkan bila ada yang gagal.
