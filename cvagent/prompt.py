"""Build the LLM prompt from profile + job data."""

from __future__ import annotations

from typing import Any

# Maps job YAML values to human-readable instructions embedded in the prompt
_LENGTH_GUIDE: dict[str, str] = {
    "short": "approximately 200 words",
    "medium": "approximately 350 words",
    "long": "approximately 500 words",
}

_TONE_GUIDE: dict[str, str] = {
    "professional": "formal and professional",
    "friendly": "warm and approachable",
    "enthusiastic": "enthusiastic and energetic",
}


def build_prompt(profile: dict[str, Any], job: dict[str, Any]) -> str:
    """Compose the full prompt string to send to the LLM.

    Structures applicant profile and job details into a single instruction
    block that works well with Mistral and Llama instruction-tuned models.
    """
    tone = _TONE_GUIDE.get(job.get("tone", "professional"), "formal and professional")
    length = _LENGTH_GUIDE.get(job.get("target_length", "medium"), "approximately 350 words")

    skills_str = ", ".join(profile.get("skills", []))
    work_str = _format_work_history(profile.get("work_history", []))
    projects_str = _format_projects(profile.get("projects", []))

    contact = profile.get("contact", {})
    name = contact.get("name", "Applicant")

    prompt = f"""You are an expert career coach and professional writer specialising in ATS-optimised cover letters.
Write a cover letter for the following applicant and job.

# Applicant
Name: {name}
Skills: {skills_str}

## Work History
{work_str}

## Projects
{projects_str}

# Target Job
Company: {job['company']}
Role: {job['role']}
Location: {job.get('location', 'Not specified')}

## Job Description
{job['description'].strip()}

# Instructions

## Content rules (truthfulness)
- Use ONLY the skills, experience, and projects listed above — do not invent, infer, or embellish
- Do not claim proficiency in any technology not listed in the Skills section
- Every specific claim must be traceable to the work history or projects provided
- If a required skill from the job description is not in the applicant's profile, do not mention it

## ATS and AI screening rules
- Mirror exact keywords and phrases from the job description where they match the applicant's real experience
- Use standard section flow: opening hook → relevant experience → why this company → call to action
- Spell out acronyms on first use (e.g. "Continuous Integration (CI)")
- Avoid tables, columns, images, headers/footers, or any formatting that ATS parsers cannot read
- Use plain paragraph text only; no bullet points inside the letter body
- Bold (**phrase**) may be used sparingly for the most critical skill matches
- Keep sentences under 25 words where possible for readability scoring

## Format
- Write {length}
- Tone: {tone}
- Address the letter to the hiring team at {job['company']}
- Output only the cover letter text — no subject line, no preamble, no commentary
"""
    return prompt


def build_open_application_prompt(
    profile: dict[str, Any],
    company: dict[str, Any],
    tone: str = "professional",
    length: str = "medium",
) -> str:
    """Compose a prompt for an open (speculative) application letter.

    Unlike build_prompt(), there is no specific role or job description.
    The LLM is directed to identify the applicant's top skill alignment
    points against the company's domain and build the letter around them.
    """
    tone_guide = _TONE_GUIDE.get(tone, "formal and professional")
    length_guide = _LENGTH_GUIDE.get(length, "approximately 350 words")

    skills_str = ", ".join(profile.get("skills", []))
    work_str = _format_work_history(profile.get("work_history", []))
    projects_str = _format_projects(profile.get("projects", []))

    contact = profile.get("contact", {})
    name = contact.get("name", "Applicant")

    prompt = f"""You are an expert career coach writing an open (speculative) application letter.

# Applicant
Name: {name}
Skills: {skills_str}

## Work History
{work_str}

## Projects
{projects_str}

# Target Company
Name: {company.get('name', 'the company')}
Industry: {company.get('industry', 'Unknown')}
Mission: {company.get('mission', 'Unknown')}
Products / Services: {company.get('products', 'Unknown')}
Tech Signals: {company.get('tech_signals', 'Unknown')}
Culture: {company.get('culture', 'Unknown')}

# Instructions

## Skills alignment (high points)
- Identify the 3–5 skills from the applicant profile that best match the company's domain, products, and tech stack
- Build the body of the letter around these alignment points — they are the "high points" of the application
- Bold (**phrase**) each high-point skill or key achievement on first use to aid the reader's eye

## Content rules (truthfulness)
- Use ONLY the skills, experience, and projects listed above — do not invent, infer, or embellish
- Do not claim proficiency in any technology not listed in the Skills section
- Every specific claim must be traceable to the work history or projects provided

## Letter structure
- Opening: who the applicant is and why this company specifically (reference mission or products concretely)
- Body: concrete evidence for each high-point skill matched to the company's context
- Closing: express genuine openness to any role where these skills add value; end with a clear call to action

## Format
- Write {length_guide}
- Tone: {tone_guide}
- Address the letter to the hiring team at {company.get('name', 'the company')}
- This is an open application with no specific role — do not reference a posted job
- Output only the cover letter text — no subject line, no preamble, no commentary
"""
    return prompt


def _format_work_history(history: list[dict[str, Any]]) -> str:
    lines = []
    for entry in history:
        end = entry.get("end") or "Present"
        lines.append(f"- {entry['title']} at {entry['company']} ({entry['start']} to {end})")
        for highlight in entry.get("highlights", []):
            lines.append(f"  * {highlight}")
    return "\n".join(lines)


def _format_projects(projects: list[dict[str, Any]]) -> str:
    lines = []
    for p in projects:
        tech = ", ".join(p.get("tech", []))
        lines.append(f"- {p['name']}: {p['description']} [{tech}]")
    return "\n".join(lines)
