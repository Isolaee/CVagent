# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run all tests
.venv/bin/pytest

# Run a single test file or specific test
.venv/bin/pytest tests/test_prompt.py
.venv/bin/pytest tests/test_company.py::test_crawl_company_success

# Lint and format (ruff)
.venv/bin/ruff check --fix cvagent/
.venv/bin/ruff format cvagent/

# Run the tool (job posting file)
python3 -m cvagent data/jobs/myjob.yaml --provider anthropic --format docx

# Run the tool (live job URL)
python3 -m cvagent https://company.com/careers/role --provider anthropic --format docx

# Open application mode (crawls the company website)
python3 -m cvagent https://company.com --open-application --provider anthropic --tone enthusiastic --length medium
```

The pre-commit hook runs `ruff check --fix`, `ruff format`, and the full pytest suite on every commit.

## Architecture

**End-to-end data flow** (both modes):

```
user_profile.yaml ──► load_profile()
                                      ├──► build_prompt()              ──► generate() ──► render_*()
job YAML / URL ──► load_job()         │
                   fetch_job_from_url()
                                      └──► build_open_application_prompt()
company URL ──► crawl_company()       │
```

### Two generation modes

**Standard (job-specific):** `job` arg is a YAML file path or a job-posting URL. When a URL, `fetch_job_from_url()` fetches the page, strips HTML, and calls the LLM to extract `{company, role, description, location}` as JSON. This job dict + profile feed into `build_prompt()`.

**Open application:** `--open-application` flag. `job` arg must be a company homepage URL. `crawl_company()` fetches the main page, discovers up to 4 relevant subpages (about/team/products/mission/culture/values), combines the text, and calls the LLM to extract `{name, industry, mission, products, tech_signals, culture}`. This company dict + profile feed into `build_open_application_prompt()`, which instructs the LLM to identify the 3–5 best skill alignment points and build the letter around them.

### LLM abstraction (`llm.py`)

`generate(prompt, model, provider)` routes to either Ollama (local daemon, default) or Anthropic API. Default models: `mistral` for Ollama, `claude-sonnet-4-6` for Anthropic. The function is called twice in open-application mode — once inside `crawl_company()` for extraction and once for letter generation.

### What profile fields actually reach the LLM

`build_prompt()` and `build_open_application_prompt()` inject: `contact.name`, `skills`, `work_history` (with highlights), `projects` (with tech list). **Not injected:** `summary`, `education`, `languages`, `contact.linkedin`, `contact.github`, `contact.portfolio`, per-project `url`. These fields are loaded by `load_profile()` but unused in prompts — they exist only for potential future use or for `render_docx()`.

### DOCX renderer (`renderer.py`)

`render_docx()` produces a two-table layout: a navy header box (name + contact info) and a two-column body (light-grey sidebar with RECIPIENT/SENDER labels, right column with letter text). It uses raw `python-docx` XML manipulation (`parse_xml`, `nsdecls`) for cell backgrounds and fixed table layout — Word's default APIs don't support these. The `job` dict passed to `render_docx` needs at minimum a `company` key; for open applications the CLI synthesises `{"role": "Open Application", **company}`.

### Job YAML format

```yaml
company: "Acme Corp"
role: "Software Engineer"
description: >
  Full job description text...
location: "Helsinki"      # optional
tone: "professional"      # professional | friendly | enthusiastic
target_length: "medium"   # short (~200w) | medium (~350w) | long (~500w)
```

## Style

- **Indentation:** tabs (ruff enforces this — do not use spaces in source files)
- **Line length:** 120 characters
- **Quotes:** double quotes
- **Target:** Python 3.9+

## Key paths

- `data/user_profile.yaml` — gitignored; copy from `data/user_profile.example.yaml`
- `data/jobs/` — gitignored; store job YAML files here
- `output/` — gitignored; generated cover letters land here
- `.env` — gitignored; set `ANTHROPIC_API_KEY=sk-ant-...` here
