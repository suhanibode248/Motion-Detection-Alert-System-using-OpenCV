# 🎥 Motion Detection Alert System

Detects moving objects via webcam, plays a **beep alert**, and optionally **records video** and **saves snapshots** whenever motion is detected.

---

## 📁 Project Structure

```
motion_alert/
├── motion_detector.py   ← Main script (run this)
├── config.py            ← All settings in one place
├── alert.py             ← Cross-platform beep system
├── recorder.py          ← Video recording module
├── logger.py            ← CSV event logger
├── requirements.txt     ← Python dependencies
├── README.md
└── output/              ← Created automatically on first run
    ├── snapshots/       ← JPEG images on each alert
    ├── videos/          ← MP4 recordings
    └── logs/            ← CSV log files
```

---

## ⚙️ How It Works

```
Camera Frame
    │
    ▼
Background Subtraction (MOG2)
    │
    ▼
Gaussian Blur + Morphological Cleanup
    │
    ▼
Contour Detection
    │
    ├─ No contours above threshold → Keep monitoring
    │
    └─ Contour found → Motion Event!
            ├── 🔔 Beep Alert (cross-platform)
            ├── 📸 Save Snapshot (JPEG)
            ├── 🎥 Start/Continue Video Recording
            └── 📝 Log to CSV
```

---

## 🚀 Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the detector
```bash
python motion_detector.py
```

### 3. Run with options
```bash
# Use a different camera
python motion_detector.py --camera 1

# Higher sensitivity (smaller area threshold)
python motion_detector.py --sensitivity 200

# Headless mode (no display window, e.g. Raspberry Pi)
python motion_detector.py --no-display

# Disable recording (alert + snapshot only)
python motion_detector.py --no-record

# Custom alert cooldown (10 seconds between alerts)
python motion_detector.py --cooldown 10
```

### All CLI options
| Flag | Default | Description |
|------|---------|-------------|
| `--camera N` | 0 | Camera index |
| `--sensitivity N` | 500 | Min contour area (px²); lower = more sensitive |
| `--cooldown N` | 3.0 | Seconds between alerts |
| `--no-display` | off | Run without GUI window |
| `--no-record` | off | Disable video recording |
| `--no-snapshot` | off | Disable JPEG snapshots |

---

## 🎛️ Keyboard Controls (when display is ON)

| Key | Action |
|-----|--------|
| `q` | Quit the program |
| `s` | Save a manual snapshot |
| `r` | Reset background model |

---

## ⚙️ Configuration (`config.py`)

Key settings you can tune:

| Setting | Default | Description |
|---------|---------|-------------|
| `MIN_CONTOUR_AREA` | 500 | Minimum motion area in pixels² |
| `ALERT_COOLDOWN` | 3.0 | Seconds between beep alerts |
| `BEEP_FREQUENCY` | 1000 | Beep tone in Hz |
| `BEEP_REPEAT` | 2 | Number of beeps per alert |
| `RECORDING_TIMEOUT` | 5.0 | Seconds after last motion to stop recording |
| `BACKGROUND_THRESHOLD` | 16 | Background model sensitivity (lower = more sensitive) |
| `PROCESSING_SCALE` | 0.5 | Frame scale for processing (0.5 = faster, less accurate) |

---

## 🔔 Beep Sound — Platform Support

| Platform | Method |
|----------|--------|
| Windows | `winsound.Beep()` (built-in) |
| macOS | `afplay /System/Library/Sounds/Ping.aiff` |
| Linux | `sounddevice` (sine wave) → `beep` command → terminal bell |

Install `sounddevice` for the best Linux/macOS experience:
```bash
pip install sounddevice
```

---

## 📊 Output Files

- **Snapshots**: `output/snapshots/motion_YYYYMMDD_HHMMSS.jpg`
- **Videos**: `output/videos/motion_YYYYMMDD_HHMMSS.mp4`
- **Logs**: `output/logs/motion_log_YYYYMMDD.csv`

---

## 🧪 Troubleshooting

| Problem | Fix |
|---------|-----|
| "Cannot open camera 0" | Try `--camera 1` or check camera permissions |
| No beep on Linux | Run `sudo apt install beep` or `pip install sounddevice` |
| Too many false alerts | Increase `MIN_CONTOUR_AREA` or `ALERT_COOLDOWN` in config.py |
| Missing detections | Decrease `MIN_CONTOUR_AREA` or `BACKGROUND_THRESHOLD` |
| Slow performance | Decrease `FRAME_WIDTH`/`FRAME_HEIGHT` or lower `PROCESSING_SCALE` |

---

## 📦 Requirements

- Python 3.8+
- OpenCV (`opencv-python`)
- NumPy
- Camera/webcam

Optional (for better audio on Linux/macOS):
- `sounddevice`