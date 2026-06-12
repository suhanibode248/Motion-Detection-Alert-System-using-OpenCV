"""
Motion Detection Alert System
- Opens live camera window
- Draws red box around detected objects
- Beeps when motion is detected
- Press 'q' to quit
"""

import cv2
import numpy as np
import time
import sys
import os
import threading
from datetime import datetime


# ── Settings ──────────────────────────────────────────────────
CAMERA_INDEX     = 0      # 0 = default webcam
MIN_CONTOUR_AREA = 500    # lower = more sensitive
ALERT_COOLDOWN   = 3.0    # seconds between beeps
BEEP_FREQUENCY   = 1000   # Hz
BEEP_DURATION_MS = 500    # milliseconds
BEEP_COUNT       = 2      # beeps per alert
# ──────────────────────────────────────────────────────────────


def beep():
    """Cross-platform beep."""
    for i in range(BEEP_COUNT):
        try:
            if sys.platform == "win32":
                import winsound
                winsound.Beep(BEEP_FREQUENCY, BEEP_DURATION_MS)
            elif sys.platform == "darwin":
                os.system("afplay /System/Library/Sounds/Ping.aiff")
            else:  # Linux
                try:
                    import sounddevice as sd
                    duration = BEEP_DURATION_MS / 1000
                    sr = 44100
                    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
                    tone = (0.5 * np.sin(2 * np.pi * BEEP_FREQUENCY * t)).astype(np.float32)
                    tone[:int(sr*0.01)]  *= np.linspace(0, 1, int(sr*0.01))
                    tone[-int(sr*0.01):] *= np.linspace(1, 0, int(sr*0.01))
                    sd.play(tone, samplerate=sr)
                    sd.wait()
                except ImportError:
                    print("\a", end="", flush=True)
        except Exception:
            print("\a", end="", flush=True)
        if i < BEEP_COUNT - 1:
            time.sleep(0.2)


def main():
    print("=" * 50)
    print("  Motion Detection Alert System")
    print("=" * 50)
    print(f"  Opening camera {CAMERA_INDEX}...")

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open camera {CAMERA_INDEX}")
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    print("  Camera opened! Press 'q' to quit.\n")

    bg_sub = cv2.createBackgroundSubtractorMOG2(
        history=500, varThreshold=16, detectShadows=True
    )
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    last_alert_time = 0
    total_alerts    = 0

    # Warm up background model silently
    for _ in range(30):
        ret, frame = cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            bg_sub.apply(cv2.GaussianBlur(gray, (21, 21), 0))

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        h, w = frame.shape[:2]

        # ── Detect motion ──────────────────────────────────────
        gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (21, 21), 0)
        fg_mask = bg_sub.apply(blurred)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.dilate(fg_mask, kernel, iterations=2)
        _, thresh = cv2.threshold(fg_mask, 25, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detected = [c for c in contours if cv2.contourArea(c) >= MIN_CONTOUR_AREA]

        motion = len(detected) > 0

        # ── Draw bounding boxes ────────────────────────────────
        for cnt in detected:
            x, y, bw, bh = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x+bw, y+bh), (0, 0, 255), 2)
            cv2.putText(frame, "Object", (x, y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)

        # ── Status bar ─────────────────────────────────────────
        bar_color = (0, 0, 200) if motion else (0, 140, 0)
        cv2.rectangle(frame, (0, 0), (w, 38), (0, 0, 0), -1)

        if motion:
            cv2.putText(frame, "⚠  MOTION DETECTED!", (10, 26),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "●  Monitoring...", (10, 26),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 220, 0), 2)

        # Timestamp top-right
        ts = datetime.now().strftime("%H:%M:%S")
        cv2.putText(frame, ts, (w - 90, 26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        # Alert count bottom
        cv2.rectangle(frame, (0, h - 28), (w, h), (0, 0, 0), -1)
        cv2.putText(frame, f"Total Alerts: {total_alerts}   |   Press 'q' to quit",
                    (10, h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (180, 180, 180), 1)

        # ── Beep alert ─────────────────────────────────────────
        if motion:
            now = time.time()
            if now - last_alert_time >= ALERT_COOLDOWN:
                total_alerts   += 1
                last_alert_time = now
                print(f"[ALERT #{total_alerts}] Motion detected at {ts} "
                      f"— {len(detected)} object(s)")
                threading.Thread(target=beep, daemon=True).start()

        # ── Show window ────────────────────────────────────────
        cv2.imshow("Motion Detection — Press Q to Quit", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\n[INFO] Quit by user.")
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"[INFO] Done. Total alerts: {total_alerts}")


if __name__ == "__main__":
    main()