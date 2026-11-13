"""Load shared project defaults with nested per-project overrides."""
import json
from pathlib import Path


def read_json(path):
    return json.loads(path.read_text())


def merge(defaults, overrides):
    result = dict(defaults)
    for key, value in overrides.items():
        previous = result.get(key)
        result[key] = merge(previous, value) if isinstance(previous, dict) and isinstance(value, dict) else value
    return result


def load_project(root):
    root = Path(root).resolve()
    return merge(read_json(root.parent / 'defaults.json'), read_json(root / 'overrides.json'))
