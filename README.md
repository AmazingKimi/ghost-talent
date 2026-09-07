# Ghost Talent

**Discover emerging AI talent before they become obvious.**

Ghost Talent is an open-source, evidence-grounded talent intelligence project for finding rising AI engineers and researchers from their public technical footprints.

Instead of asking who is already famous, Ghost Talent asks a different question:

> Who is already demonstrating real capability and accelerating momentum, while still remaining relatively under-recognized?

## Core thesis

Public technical activity can reveal emerging talent before conventional recruiting signals do.

Ghost Talent combines public evidence from sources such as GitHub and research-paper indexes, builds a time-aware technical profile, and ranks candidates using transparent signals rather than a black-box popularity score.

## Ghost Score v0.1

The first scoring model is intentionally simple and inspectable:

- **Capability — 35%**: demonstrated technical depth and quality of work
- **Momentum — 35%**: whether meaningful activity is accelerating over time
- **Visibility Gap — 20%**: whether capability appears ahead of current public visibility
- **Evidence Confidence — 10%**: how reliable the identity match and supporting evidence are

Explanations may summarize evidence, but they do not create evidence and do not directly determine the final score.

## v0.1 scope

The first release focuses on one workflow:

`technical topic → scout → identity resolution → evidence → time series → Ghost Score → ranked candidates`

Current public sources:

- GitHub
- OpenAlex

Planned next: arXiv / secondary scholarly evidence, stronger identity resolution, historical backtesting and watchlists.

Not in v0.1: recruiting CRM, automated outreach, private-data enrichment, LinkedIn scraping, payment, or enterprise workflows.

## Run locally

Ghost Talent supports Python 3.8 and newer.

### macOS launcher

Clone the repository, then run:

```bash
chmod +x start.command
./start.command
```

After the first `chmod`, `start.command` can also be opened from Finder. It creates a local virtual environment, installs compatible dependencies, starts the server and opens the browser automatically.

### Manual setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools
pip install -e .
python -m ghost_talent.app
```

Then open:

```text
http://127.0.0.1:8765
```

A GitHub token is optional but useful because unauthenticated GitHub API requests have a much lower rate limit. If you have one, export `GITHUB_TOKEN` in your shell before starting the app.

## What the first scout does

1. Searches repositories related to the requested technical topic.
2. Collects contributors from those repositories.
3. Reads current public profile and recent public activity signals.
4. Cross-checks a candidate's public name against relevant OpenAlex works.
5. Builds evidence records and calculates the four Ghost Score dimensions.
6. Returns a ranked list with links back to the underlying evidence.

## Principles

1. Every important claim should be traceable to public evidence.
2. Identity uncertainty must remain uncertainty; never force a match.
3. Raw activity volume is not the same as technical capability.
4. The system should detect acceleration, not merely popularity.
5. Historical evaluation must support an `as_of_date` so future information cannot leak into past rankings.
6. Sensitive personal attributes are outside the ranking model.

## Current limitations

This is an early scoring model. GitHub public events provide only a limited activity window, and OpenAlex identity matching is currently conservative and name-based. Scores should be treated as discovery signals, not employment decisions or predictions of future success.

## Status

**Early development — v0.1**

The first milestone is to prove that Ghost Talent can surface a small number of genuinely interesting, non-obvious AI engineers or researchers from real public data.

## Maintainer

Created and maintained by **AmazingKimi**.
