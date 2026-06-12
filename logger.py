"""
Motion Logger — writes detection events and session summaries to a CSV log file.
"""

import csv
import os
from datetime import datetime


class MotionLogger:
    def __init__(self, config):
        self.config = config
        os.makedirs(config.LOG_DIR, exist_ok=True)

        date_str = datetime.now().strftime("%Y%m%d")
        self.log_file = os.path.join(config.LOG_DIR, f"motion_log_{date_str}.csv")

        # Write header if new file
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["alert_number", "timestamp", "event"])
            print(f"[LOGGER] New log file created: {self.log_file}")
        else:
            print(f"[LOGGER] Appending to existing log: {self.log_file}")

    def log_motion(self, alert_number: int, timestamp: str):
        """Log a single motion detection event."""
        try:
            with open(self.log_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([alert_number, timestamp, "motion_detected"])
        except Exception as e:
            print(f"[LOGGER] Error writing log: {e}")

    def log_session_end(self, total_alerts: int, session_start: datetime):
        """Append a session summary entry."""
        duration = datetime.now() - session_start
        minutes = int(duration.total_seconds() // 60)
        seconds = int(duration.total_seconds() % 60)
        try:
            with open(self.log_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    total_alerts,
                    datetime.now().strftime("%Y%m%d_%H%M%S"),
                    f"session_ended (duration={minutes}m{seconds}s, total_alerts={total_alerts})"
                ])
        except Exception as e:
            print(f"[LOGGER] Error writing session end: {e}")