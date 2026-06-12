"""
Motion Detection Alert System with Beep Sound and Video Recording
Author: Motion Alert Project
Description: Detects motion from webcam, triggers beep alert, and records video 
"""

import cv2
import numpy as np
import time
import os
import threading
import argparse
from datetime import datetime
from config import Config
from alert import AlertSystem
from recorder import VideoRecorder
from logger import MotionLogger


class MotionDetector:
    def __init__(self, config: Config):
        self.config = config
        self.alert = AlertSystem(config)
        self.recorder = VideoRecorder(config)
        self.logger = MotionLogger(config)

        self.cap = None
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=config.BACKGROUND_HISTORY,
            varThreshold=config.BACKGROUND_THRESHOLD,
            detectShadows=config.DETECT_SHADOWS
        )

        self.motion_detected = False
        self.last_motion_time = 0
        self.frame_count = 0
        self.recording_active = False
        self.running = False

        # Stats
        self.total_alerts = 0
        self.session_start = datetime.now()

    def initialize_camera(self):
        """Initialize the camera capture."""
        print(f"[INFO] Opening camera index {self.config.CAMERA_INDEX}...")
        self.cap = cv2.VideoCapture(self.config.CAMERA_INDEX)

        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera {self.config.CAMERA_INDEX}")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, self.config.FPS)

        actual_w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
        print(f"[INFO] Camera initialized: {actual_w}x{actual_h} @ {actual_fps:.1f} FPS")

    def preprocess_frame(self, frame):
        """Preprocess frame for motion detection."""
        # Resize for faster processing
        if self.config.PROCESSING_SCALE != 1.0:
            h, w = frame.shape[:2]
            new_w = int(w * self.config.PROCESSING_SCALE)
            new_h = int(h * self.config.PROCESSING_SCALE)
            frame_small = cv2.resize(frame, (new_w, new_h))
        else:
            frame_small = frame.copy()

        # Convert to grayscale and blur
        gray = cv2.cvtColor(frame_small, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (self.config.BLUR_KERNEL, self.config.BLUR_KERNEL), 0)
        return blurred

    def detect_motion(self, frame):
        """Detect motion in the current frame. Returns (motion_found, contours, fg_mask)."""
        processed = self.preprocess_frame(frame)
        fg_mask = self.background_subtractor.apply(processed)

        # Morphological operations to remove noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.dilate(fg_mask, kernel, iterations=2)

        # Threshold
        _, thresh = cv2.threshold(fg_mask, self.config.MOTION_THRESHOLD, 255, cv2.THRESH_BINARY)

        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Scale contours back if resized
        scale = 1.0 / self.config.PROCESSING_SCALE
        motion_found = False
        valid_contours = []

        for cnt in contours:
            area = cv2.contourArea(cnt) * (scale ** 2)
            if self.config.MIN_CONTOUR_AREA <= area <= self.config.MAX_CONTOUR_AREA:
                # Scale contour coordinates
                scaled_cnt = (cnt * scale).astype(np.int32)
                valid_contours.append((scaled_cnt, area))
                motion_found = True

        return motion_found, valid_contours, thresh

    def draw_detections(self, frame, contours, motion_found):
        """Draw bounding boxes and info on frame."""
        display = frame.copy()
        h, w = display.shape[:2]

        # Draw contours and bounding boxes
        for cnt, area in contours:
            x, y, bw, bh = cv2.boundingRect(cnt)
            color = (0, 0, 255) if motion_found else (0, 255, 0)
            cv2.rectangle(display, (x, y), (x + bw, y + bh), color, 2)
            cv2.putText(display, f"Area: {int(area)}", (x, y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)

        # Status bar at top
        status_color = (0, 0, 255) if motion_found else (0, 180, 0)
        cv2.rectangle(display, (0, 0), (w, 30), (0, 0, 0), -1)
        status_text = "⚠ MOTION DETECTED!" if motion_found else "● Monitoring..."
        cv2.putText(display, status_text, (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, status_color, 2)

        # Timestamp
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(display, ts, (w - 200, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        # Recording indicator
        if self.recording_active:
            cv2.circle(display, (w - 20, 50), 8, (0, 0, 255), -1)
            cv2.putText(display, "REC", (w - 55, 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Stats at bottom
        cv2.rectangle(display, (0, h - 28), (w, h), (0, 0, 0), -1)
        stats = f"Alerts: {self.total_alerts}  |  Frame: {self.frame_count}  |  Press 'q' to quit"
        cv2.putText(display, stats, (10, h - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)

        return display

    def handle_motion_event(self, frame):
        """Handle a motion detection event."""
        current_time = time.time()
        cooldown_passed = (current_time - self.last_motion_time) > self.config.ALERT_COOLDOWN

        if cooldown_passed:
            self.total_alerts += 1
            self.last_motion_time = current_time
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            print(f"[ALERT] Motion detected at {datetime.now().strftime('%H:%M:%S')} "
                  f"(Alert #{self.total_alerts})")

            # Beep alert in separate thread to not block video
            threading.Thread(target=self.alert.beep, daemon=True).start()

            # Save snapshot
            if self.config.SAVE_SNAPSHOTS:
                snap_path = os.path.join(self.config.SNAPSHOT_DIR, f"motion_{timestamp}.jpg")
                cv2.imwrite(snap_path, frame)
                print(f"[SNAPSHOT] Saved: {snap_path}")

            # Log event
            self.logger.log_motion(self.total_alerts, timestamp)

        # Start/continue recording
        if self.config.RECORD_ON_MOTION and not self.recording_active:
            self.recorder.start_recording(frame)
            self.recording_active = True

    def handle_no_motion(self):
        """Handle frame with no motion."""
        if self.recording_active:
            elapsed = time.time() - self.last_motion_time
            if elapsed > self.config.RECORDING_TIMEOUT:
                self.recorder.stop_recording()
                self.recording_active = False
                print("[RECORDER] Recording stopped (no motion)")

    def run(self):
        """Main detection loop."""
        self.initialize_camera()
        self.running = True

        os.makedirs(self.config.SNAPSHOT_DIR, exist_ok=True)
        os.makedirs(self.config.VIDEO_DIR, exist_ok=True)
        os.makedirs(self.config.LOG_DIR, exist_ok=True)

        print("\n" + "=" * 55)
        print("  Motion Detection Alert System — RUNNING")
        print("=" * 55)
        print(f"  Camera     : {self.config.CAMERA_INDEX}")
        print(f"  Resolution : {self.config.FRAME_WIDTH}x{self.config.FRAME_HEIGHT}")
        print(f"  Sensitivity: {self.config.MIN_CONTOUR_AREA} px² (min area)")
        print(f"  Snapshots  : {'ON' if self.config.SAVE_SNAPSHOTS else 'OFF'}")
        print(f"  Recording  : {'ON' if self.config.RECORD_ON_MOTION else 'OFF'}")
        print(f"  Display    : {'ON' if self.config.SHOW_WINDOW else 'OFF'}")
        print("=" * 55)
        print("  Press 'q' to quit | 's' for snapshot | 'r' to reset\n")

        # Warm-up frames for background model
        print("[INFO] Warming up background model (2 seconds)...")
        warmup_end = time.time() + 2
        while time.time() < warmup_end:
            ret, frame = self.cap.read()
            if ret:
                self.preprocess_frame(frame)

        print("[INFO] Detection started!\n")

        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    print("[WARNING] Failed to read frame. Retrying...")
                    time.sleep(0.1)
                    continue

                self.frame_count += 1
                motion_found, contours, mask = self.detect_motion(frame)

                if motion_found:
                    self.handle_motion_event(frame)
                else:
                    self.handle_no_motion()

                # Write frame to recorder
                if self.recording_active:
                    self.recorder.write_frame(frame)

                # Display window
                if self.config.SHOW_WINDOW:
                    display = self.draw_detections(frame, contours, motion_found)
                    cv2.imshow("Motion Detection Alert System", display)

                    if self.config.SHOW_MASK:
                        cv2.imshow("Motion Mask", mask)

                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        print("\n[INFO] Quit requested by user.")
                        break
                    elif key == ord('s'):
                        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                        path = os.path.join(self.config.SNAPSHOT_DIR, f"manual_{ts}.jpg")
                        cv2.imwrite(path, frame)
                        print(f"[SNAPSHOT] Manual snapshot saved: {path}")
                    elif key == ord('r'):
                        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
                            history=self.config.BACKGROUND_HISTORY,
                            varThreshold=self.config.BACKGROUND_THRESHOLD,
                            detectShadows=self.config.DETECT_SHADOWS
                        )
                        print("[INFO] Background model reset.")

        except KeyboardInterrupt:
            print("\n[INFO] Interrupted by user.")
        finally:
            self.cleanup()

    def cleanup(self):
        """Release resources."""
        self.running = False
        if self.recording_active:
            self.recorder.stop_recording()
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.logger.log_session_end(self.total_alerts, self.session_start)
        print(f"\n[INFO] Session ended. Total alerts: {self.total_alerts}")
        print("[INFO] Resources released. Goodbye!")


def parse_args():
    parser = argparse.ArgumentParser(description="Motion Detection Alert System")
    parser.add_argument("--camera", type=int, default=0, help="Camera index (default: 0)")
    parser.add_argument("--sensitivity", type=int, default=500,
                        help="Min contour area in px² (default: 500, lower = more sensitive)")
    parser.add_argument("--no-display", action="store_true", help="Run without display window")
    parser.add_argument("--no-record", action="store_true", help="Disable video recording")
    parser.add_argument("--no-snapshot", action="store_true", help="Disable snapshots")
    parser.add_argument("--cooldown", type=float, default=3.0,
                        help="Alert cooldown in seconds (default: 3)")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    cfg = Config()

    # Apply CLI overrides
    cfg.CAMERA_INDEX = args.camera
    cfg.MIN_CONTOUR_AREA = args.sensitivity
    cfg.SHOW_WINDOW = not args.no_display
    cfg.RECORD_ON_MOTION = not args.no_record
    cfg.SAVE_SNAPSHOTS = not args.no_snapshot
    cfg.ALERT_COOLDOWN = args.cooldown

    detector = MotionDetector(cfg)
    detector.run()