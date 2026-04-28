import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class FileTask:
    src: str
    dst: str
    is_folder: bool = False
    status: str = "queued"          # queued, copying, paused, done, failed, cancelled
    progress: float = 0.0
    speed: float = 0.0
    eta: float = 0.0
    error: Optional[str] = None
    size: int = 0
    copied_size: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.size == 0 and os.path.exists(self.src):
            if os.path.isfile(self.src):
                self.size = os.path.getsize(self.src)
            else:
                self.is_folder = True
                self.size = self._get_folder_size()

    def _get_folder_size(self) -> int:
        total = 0
        for root, _, files in os.walk(self.src):
            for f in files:
                total += os.path.getsize(os.path.join(root, f))
        return total