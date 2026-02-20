"""Tests for job loading and validation."""

import pytest

from cvagent.job import load_job


def test_load_job_file_not_found(tmp_path):
    missing = tmp_path / "missing.yaml"
    with pytest.raises(FileNotFoundError, match="missing.yaml"):
        load_job(missing)


def test_load_job_missing_required_field(tmp_path):
    # Job missing 'description'
    yaml_content = "company: Acme\nrole: Engineer\n"
    f = tmp_path / "job.yaml"
    f.write_text(yaml_content)
    with pytest.raises(ValueError, match="description"):
        load_job(f)


def test_load_job_valid(tmp_path):
    yaml_content = (
        "company: Futurice\n"
        "role: Senior Python Engineer\n"
        "description: We need a Python engineer.\n"
    )
    f = tmp_path / "job.yaml"
    f.write_text(yaml_content)
    job = load_job(f)
    assert job["company"] == "Futurice"
    assert job["role"] == "Senior Python Engineer"
