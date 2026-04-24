"""Tests for the prompt builder."""

from cvagent.prompt import build_open_application_prompt, build_prompt

_PROFILE = {
    "contact": {"name": "Jane Doe"},
    "skills": ["Python", "Docker"],
    "work_history": [
        {
            "company": "Acme",
            "title": "Engineer",
            "start": "2020-01",
            "end": None,
            "highlights": ["Built things"],
        }
    ],
    "projects": [
        {"name": "MyProject", "description": "A project", "tech": ["Python"]}
    ],
}

_JOB = {
    "company": "Futurice",
    "role": "Backend Engineer",
    "description": "We need a Python engineer.",
    "tone": "professional",
    "target_length": "medium",
}


def test_prompt_contains_company():
    prompt = build_prompt(_PROFILE, _JOB)
    assert "Futurice" in prompt


def test_prompt_contains_applicant_name():
    prompt = build_prompt(_PROFILE, _JOB)
    assert "Jane Doe" in prompt


def test_prompt_contains_skills():
    prompt = build_prompt(_PROFILE, _JOB)
    assert "Python" in prompt
    assert "Docker" in prompt


def test_prompt_tone_instruction():
    prompt = build_prompt(_PROFILE, _JOB)
    assert "formal and professional" in prompt


def test_prompt_length_instruction():
    prompt = build_prompt(_PROFILE, _JOB)
    assert "350 words" in prompt


def test_prompt_friendly_tone():
    job = {**_JOB, "tone": "friendly"}
    prompt = build_prompt(_PROFILE, job)
    assert "warm and approachable" in prompt


def test_prompt_short_length():
    job = {**_JOB, "target_length": "short"}
    prompt = build_prompt(_PROFILE, job)
    assert "200 words" in prompt


def test_prompt_work_history_present():
    prompt = build_prompt(_PROFILE, _JOB)
    assert "Acme" in prompt
    assert "Built things" in prompt


def test_prompt_no_profile_contact_falls_back():
    profile = {**_PROFILE, "contact": {}}
    prompt = build_prompt(profile, _JOB)
    assert "Applicant" in prompt


# ---------------------------------------------------------------------------
# Open application prompt tests
# ---------------------------------------------------------------------------

_COMPANY = {
    "name": "Stripe",
    "industry": "Fintech / Payments",
    "mission": "Increase the GDP of the internet.",
    "products": "Payment APIs, Radar fraud detection, Stripe Atlas",
    "tech_signals": "Ruby, Go, React, AWS",
    "culture": "Remote-friendly, high-trust, deeply technical",
    "url": "https://stripe.com",
}


def test_open_application_prompt_contains_company_name():
    prompt = build_open_application_prompt(_PROFILE, _COMPANY)
    assert "Stripe" in prompt


def test_open_application_prompt_contains_applicant_name():
    prompt = build_open_application_prompt(_PROFILE, _COMPANY)
    assert "Jane Doe" in prompt


def test_open_application_prompt_contains_skills():
    prompt = build_open_application_prompt(_PROFILE, _COMPANY)
    assert "Python" in prompt
    assert "Docker" in prompt


def test_open_application_prompt_contains_mission():
    prompt = build_open_application_prompt(_PROFILE, _COMPANY)
    assert "GDP of the internet" in prompt


def test_open_application_prompt_no_role_section():
    prompt = build_open_application_prompt(_PROFILE, _COMPANY)
    assert "Target Job" not in prompt
    assert "Job Description" not in prompt


def test_open_application_prompt_instructs_no_specific_role():
    prompt = build_open_application_prompt(_PROFILE, _COMPANY)
    assert "open application" in prompt.lower() or "no specific role" in prompt.lower()


def test_open_application_prompt_tone_professional():
    prompt = build_open_application_prompt(_PROFILE, _COMPANY, tone="professional")
    assert "formal and professional" in prompt


def test_open_application_prompt_tone_friendly():
    prompt = build_open_application_prompt(_PROFILE, _COMPANY, tone="friendly")
    assert "warm and approachable" in prompt


def test_open_application_prompt_length_short():
    prompt = build_open_application_prompt(_PROFILE, _COMPANY, length="short")
    assert "200 words" in prompt


def test_open_application_prompt_contains_work_history():
    prompt = build_open_application_prompt(_PROFILE, _COMPANY)
    assert "Acme" in prompt
    assert "Built things" in prompt


def test_open_application_prompt_missing_company_fields_graceful():
    company = {"name": "Sparse Co"}
    prompt = build_open_application_prompt(_PROFILE, company)
    assert "Sparse Co" in prompt
