# Scolecite Ski

Full-colour Python 3 neon needle-slope arcade for ElbowOS.

Lean a frost rider down a fan of white scolecite needles. Scoop copper gems, thread magenta gates, and ollie crevasses. Not a ROM, not an emulator.

Featured account: https://x.com/ElbowOS

Drive reel: https://drive.google.com/file/d/1zo0tcq-c1wqJQIpMwAa9JR2bGAIX5NGj/view

## Play

```bash
pip install -r requirements.txt
python3 scolecite_ski.py --play
```

A / Left lean left. D / Right lean right. Space or W ollie. R restart.

## Record a 9:16 reel

```bash
python3 scolecite_ski.py --record
```

Writes a 15-second 1080x1920 h264 MP4 (dummy SDL video driver, ffmpeg libx264 yuv420p CRF 20, +faststart).
