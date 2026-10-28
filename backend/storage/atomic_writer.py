import json
import os
import shutil
import tempfile
from typing import Any

class AtomicWriter:
    """
    Atomic file writer to prevent corruption during system crashes or cloud sync operations.
    Writes first to a temporary file in the same directory, flushes, then replaces target atomically.
    """
    @staticmethod
    def write_json(target_path: str, data: Any, indent: int = 2) -> None:
        target_dir = os.path.dirname(os.path.abspath(target_path))
        os.makedirs(target_dir, exist_ok=True)
        
        # Create temp file in same directory to ensure atomic os.replace across filesystem boundaries
        tmp_fd, tmp_path = tempfile.mkstemp(dir=target_dir, prefix=".tmp_atomic_", suffix=".json")
        try:
            with os.fdopen(tmp_fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, target_path)
        except Exception:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise

    @staticmethod
    def read_json(target_path: str) -> Any:
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"File not found: {target_path}")
        with open(target_path, 'r', encoding='utf-8') as f:
            return json.load(f)
