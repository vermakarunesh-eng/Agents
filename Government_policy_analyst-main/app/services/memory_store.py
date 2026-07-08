import json
from pathlib import Path

from app.config import get_settings


def write_memory(name: str, payload: dict) -> Path:
    directory = get_settings().memory_dir
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.json"
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return path

