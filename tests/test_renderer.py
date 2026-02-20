"""Tests for output rendering."""

from cvagent.renderer import render_markdown, render_text


def test_render_markdown_creates_file(tmp_path):
    out = tmp_path / "letter.md"
    render_markdown("# Hello **World**", out)
    assert out.exists()
    assert out.read_text() == "# Hello **World**"


def test_render_markdown_preserves_bold_markers(tmp_path):
    out = tmp_path / "letter.md"
    render_markdown("I am **experienced** in Python.", out)
    assert "**experienced**" in out.read_text()


def test_render_text_creates_file(tmp_path):
    out = tmp_path / "letter.txt"
    render_text("Hello World", out)
    assert out.exists()


def test_render_text_strips_bold_markers(tmp_path):
    out = tmp_path / "letter.txt"
    render_text("Hello **World** and **Python**", out)
    content = out.read_text()
    assert "**" not in content
    assert "Hello World and Python" in content


def test_render_markdown_creates_parent_dirs(tmp_path):
    out = tmp_path / "nested" / "dir" / "letter.md"
    render_markdown("Hello", out)
    assert out.exists()
