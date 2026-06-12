"""
Configuration settings for the Motion Detection Alert System.
Edit this file to tune sensitivity, recording, alerts, and paths.
"""


class Config:
    # ── Camera ──────────────────────────────────────────────────
    CAMERA_INDEX = 0          # 0 = default webcam, 1 = second camera, etc.
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
    FPS = 30

    # ── Motion Detection ────────────────────────────────────────
    # Background subtractor settings
    BACKGROUND_HISTORY = 500       # Frames used to build background model
    BACKGROUND_THRESHOLD = 16      # Sensitivity of background model (lower = more sensitive)
    DETECT_SHADOWS = True          # Detect and ignore shadows

    # Preprocessing
    PROCESSING_SCALE = 0.5        # Scale down frame before processing (0.5 = half size, faster)
    BLUR_KERNEL = 21              # Gaussian blur kernel size (must be odd)
    MOTION_THRESHOLD = 25         # Pixel threshold for motion mask (0–255)

    # Contour filtering
    MIN_CONTOUR_AREA = 500        # Minimum area (px²) to count as motion (increase to reduce false alerts)
    MAX_CONTOUR_AREA = 500_000    # Maximum area (ignore huge changes like lighting shifts)

    # ── Alert ────────────────────────────────────────────────────
    ALERT_COOLDOWN = 3.0          # Seconds between consecutive alerts (prevents beep spam)
    BEEP_FREQUENCY = 1000         # Beep frequency in Hz (Windows only for winsound)
    BEEP_DURATION = 500           # Beep duration in milliseconds
    BEEP_REPEAT = 2               # Number of beeps per alert
    BEEP_INTERVAL = 0.2           # Seconds between repeated beeps

    # ── Recording ────────────────────────────────────────────────
    RECORD_ON_MOTION = True       # Start recording when motion is detected
    RECORDING_TIMEOUT = 5.0       # Stop recording N seconds after last motion
    VIDEO_CODEC = "mp4v"          # Codec: mp4v, XVID, MJPG
    VIDEO_EXTENSION = ".mp4"      # Output file extension

    # ── Snapshots ────────────────────────────────────────────────
    SAVE_SNAPSHOTS = True         # Save JPEG snapshot on each alert

    # ── Display ──────────────────────────────────────────────────
    SHOW_WINDOW = True            # Show live video window
    SHOW_MASK = False             # Also show the motion mask window

    # ── Paths ────────────────────────────────────────────────────
    SNAPSHOT_DIR = "output/snapshots"
    VIDEO_DIR = "output/videos"
    LOG_DIR = "output/logs"