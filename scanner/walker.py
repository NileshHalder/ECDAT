"""
File discovery and directory traversal.
Skips noisy/irrelevant paths so findings stay signal, not noise.
"""
import os

SKIP_DIRS = {".git", "node_modules", "vendor", "__pycache__", ".venv", "dist", "build"}
SKIP_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".lock", ".min.js"}


def walk_files(root_path: str):
    """Yield file paths under root_path, skipping noisy directories/extensions."""
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if not any(fname.endswith(ext) for ext in SKIP_EXTENSIONS):
                yield os.path.join(dirpath, fname)
