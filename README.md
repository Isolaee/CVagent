# Project Name: CV agent
 
## What This Project Does
Goal of this project is to automate writing customized cover letters.
There will be static declaration file of users skills, projects and history.
Each cover letter will be customized for given application and users skills.

## Tech Stack
 - Python, python-docx, Ollama (local LLM), PyYAML

## Setup

1. Copy the example profile and fill in your details:
   ```bash
   cp data/user_profile.example.yaml data/user_profile.yaml
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run Ollama with a model (e.g. `ollama pull mistral`)
4. Generate a cover letter:
   ```bash
   python -m cvagent.cli data/jobs/myjob.yaml --format docx
   ```

> `data/user_profile.yaml` is gitignored — your personal data stays local only.


## Coding Rules
 
- Use Python for all new files
- Test critical functions
- Comment complex logic
- Use semantic commits
 
## Don't Change
 
- Authentication system (unless explicitly requested)
- Database schema (migration required)
- Production environment variables