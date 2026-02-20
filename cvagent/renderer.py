"""Format and save the generated cover letter."""

from __future__ import annotations

from pathlib import Path


def render_markdown(text: str, output_path: Path) -> None:
    """Write the cover letter as a .md file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
    print(f"Cover letter written to: {output_path}")


def render_text(text: str, output_path: Path) -> None:
    """Write the cover letter as a plain .txt file (strips markdown bold markers)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    clean = text.replace("**", "")
    output_path.write_text(clean, encoding="utf-8")
    print(f"Cover letter written to: {output_path}")


def render_to_stdout(text: str) -> None:
    """Print the cover letter directly to the terminal."""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60 + "\n")
