"""CLI entry point for CVagent."""

from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from cvagent.job import fetch_job_from_url, load_job
from cvagent.llm import DEFAULT_ANTHROPIC_MODEL, DEFAULT_MODEL, DEFAULT_PROVIDER, generate
from cvagent.profile import load_profile
from cvagent.prompt import build_open_application_prompt, build_prompt
from cvagent.renderer import render_docx, render_markdown, render_text, render_to_stdout

_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_PROFILE = _REPO_ROOT / "data" / "user_profile.yaml"
_DEFAULT_OUTPUT_DIR = _REPO_ROOT / "output"


def main() -> None:
	parser = argparse.ArgumentParser(description="Generate a customized cover letter using a local or cloud LLM.")
	parser.add_argument(
		"job",
		help="Path to a job YAML file, or a URL to a job posting page",
	)
	parser.add_argument(
		"--profile",
		type=Path,
		default=_DEFAULT_PROFILE,
		help="Path to user_profile.yaml (default: data/user_profile.yaml)",
	)
	parser.add_argument(
		"--provider",
		choices=["ollama", "anthropic"],
		default=DEFAULT_PROVIDER,
		help="LLM provider to use (default: ollama). Use 'anthropic' for Claude via API.",
	)
	parser.add_argument(
		"--model",
		default=None,
		help=(
			f"Model name. Ollama default: {DEFAULT_MODEL}. "
			f"Anthropic default: {DEFAULT_ANTHROPIC_MODEL}."
		),
	)
	parser.add_argument(
		"--format",
		choices=["markdown", "text", "stdout", "docx"],
		default="markdown",
		help="Output format (default: markdown)",
	)
	parser.add_argument(
		"--output",
		type=Path,
		default=None,
		help="Output file path (auto-named from company + role if omitted)",
	)
	parser.add_argument(
		"--open-application",
		action="store_true",
		help="Generate an open (speculative) cover letter by crawling the company URL.",
	)
	parser.add_argument(
		"--tone",
		choices=["professional", "friendly", "enthusiastic"],
		default="professional",
		help="Tone for open application letters (default: professional).",
	)
	parser.add_argument(
		"--length",
		choices=["short", "medium", "long"],
		default="medium",
		help="Target length for open application letters (default: medium).",
	)
	args = parser.parse_args()

	# Resolve model default based on provider
	if args.model is None:
		args.model = DEFAULT_ANTHROPIC_MODEL if args.provider == "anthropic" else DEFAULT_MODEL

	profile = load_profile(args.profile)

	if args.open_application:
		if not (args.job.startswith("http://") or args.job.startswith("https://")):
			parser.error("--open-application requires a company URL (http/https) as the job argument")
		from cvagent.company import crawl_company
		company = crawl_company(args.job, model=args.model, provider=args.provider)
		prompt = build_open_application_prompt(profile, company, tone=args.tone, length=args.length)
		slug = f"{company['name']}_open_application".lower().replace(" ", "_")
		print(f"Generating open application for {company['name']} via {args.provider}...")
		job = {**company, "role": "Open Application"}
	else:
		if args.job.startswith("http://") or args.job.startswith("https://"):
			job = fetch_job_from_url(args.job, model=args.model, provider=args.provider)
		else:
			job = load_job(Path(args.job))
		prompt = build_prompt(profile, job)
		slug = f"{job['company']}_{job['role']}".lower().replace(" ", "_")
		print(f"Generating cover letter for {job['role']} at {job['company']} via {args.provider}...")

	text = generate(prompt, model=args.model, provider=args.provider)

	if args.format == "stdout":
		render_to_stdout(text)
		return

	# Auto-name output file based on company + role slug
	if args.output is None:
		_EXT = {"markdown": "md", "text": "txt", "docx": "docx"}
		ext = _EXT[args.format]
		args.output = _DEFAULT_OUTPUT_DIR / f"{slug}.{ext}"

	if args.format == "markdown":
		render_markdown(text, args.output)
	elif args.format == "docx":
		render_docx(text, args.output, profile, job)
	else:
		render_text(text, args.output)


if __name__ == "__main__":
	main()
