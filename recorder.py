"""
Video Recorder — starts and stops recording based on motion events.
Each motion event creates a new timestamped video file.
"""

import cv2
import os
from datetime import datetime


class VideoRecorder:
    def __init__(self, config):
        self.config = config
        self.writer = None
        self.current_file = None
        self.recording = False
        self.frames_written = 0

    def start_recording(self, first_frame):
        """Begin a new video recording."""
        if self.recording:
            return

        os.makedirs(self.config.VIDEO_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"motion_{timestamp}{self.config.VIDEO_EXTENSION}"
        self.current_file = os.path.join(self.config.VIDEO_DIR, filename)

        h, w = first_frame.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*self.config.VIDEO_CODEC)
        self.writer = cv2.VideoWriter(
            self.current_file, fourcc, self.config.FPS, (w, h)
        )

        if not self.writer.isOpened():
            print(f"[RECORDER] WARNING: Could not open VideoWriter for {self.current_file}")
            self.writer = None
            return

        self.recording = True
        self.frames_written = 0
        print(f"[RECORDER] Recording started → {self.current_file}")

    def write_frame(self, frame):
        """Write a single frame to the current recording."""
        if self.recording and self.writer and self.writer.isOpened():
            self.writer.write(frame)
            self.frames_written += 1

    def stop_recording(self):
        """Finalize and close the current recording."""
        if not self.recording:
            return

        if self.writer:
            self.writer.release()
            self.writer = None

        duration_s = self.frames_written / max(self.config.FPS, 1)
        size_kb = 0
        if self.current_file and os.path.exists(self.current_file):
            size_kb = os.path.getsize(self.current_file) // 1024

        print(f"[RECORDER] Recording saved: {self.current_file} "
              f"({self.frames_written} frames, ~{duration_s:.1f}s, {size_kb} KB)")

        self.recording = False
        self.frames_written = 0
        self.current_file = None

    def is_recording(self):
        return self.recording