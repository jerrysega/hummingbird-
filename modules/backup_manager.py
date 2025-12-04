import os
import json
from datetime import datetime

class BackupManager:
    def __init__(self, backup_dir="data/backup"):
        self.backup_dir = backup_dir
        os.makedirs(self.backup_dir, exist_ok=True)

    def save_backup(self, snapshot: dict):
        """Save snapshot into dated backup folder."""
        date_folder = datetime.now().strftime("%Y-%m-%d")
        full_path = os.path.join(self.backup_dir, date_folder)

        os.makedirs(full_path, exist_ok=True)

        timestamp = datetime.now().strftime("%H-%M-%S")
        file_path = os.path.join(full_path, f"{timestamp}.json")

        with open(file_path, "w") as f:
            json.dump(snapshot, f, indent=2)

        return file_path
