"""Load and validate a job application YAML file."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_job(path: Path) -> dict[str, Any]:
    """Read a job YAML and return the parsed dict.

    Raises FileNotFoundError if the file does not exist.
    Raises ValueError if required fields are missing.
    """
    if not path.exists():
        raise FileNotFoundError(f"Job file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    _validate_job(data)
    return data


def _validate_job(data: dict[str, Any]) -> None:
    """Check that required fields are present in the job input."""
    required = {"company", "role", "description"}
    missing = required - set(data.keys())
    if missing:
        raise ValueError(f"Job input is missing required fields: {missing}")
