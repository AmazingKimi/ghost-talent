# Ghost Talent

**Discover emerging AI talent before they become obvious.**

Ghost Talent is an open-source, evidence-grounded talent intelligence project for finding rising AI engineers and researchers from their public technical footprints.

Instead of asking who is already famous, Ghost Talent asks a different question:

> Who is already demonstrating real capability and accelerating momentum, while still remaining relatively under-recognized?

## Core thesis

Public technical activity can reveal emerging talent before conventional recruiting signals do.

Ghost Talent combines public evidence from sources such as GitHub and research-paper indexes, builds a time-aware technical profile, and ranks candidates using transparent signals rather than an LLM-generated popularity score.

## Ghost Score v0.1

The first scoring model is intentionally simple and inspectable:

- **Capability — 35%**: demonstrated technical depth and quality of work
- **Momentum — 35%**: whether meaningful activity is accelerating over time
- **Visibility Gap — 20%**: whether capability appears ahead of current public visibility
- **Evidence Confidence — 10%**: how reliable the identity match and supporting evidence are

LLMs may explain evidence, but they do **not** invent evidence and do **not** directly determine the final score.

## v0.1 scope

The first release will focus on one workflow:

`technical topic → scout → identity resolution → evidence → time series → Ghost Score → ranked candidates`

Initial public sources:

- GitHub
- OpenAlex / arXiv
- a secondary scholarly evidence source

Not in v0.1: recruiting CRM, automated outreach, private-data enrichment, LinkedIn scraping, payment, or enterprise workflows.

## Principles

1. Every important claim should be traceable to public evidence.
2. Identity uncertainty must remain uncertainty; never force a match.
3. Raw activity volume is not the same as technical capability.
4. The system should detect acceleration, not merely popularity.
5. Historical evaluation must support an `as_of_date` so future information cannot leak into past rankings.
6. Sensitive personal attributes are outside the ranking model.

## Status

**Early development — v0.1**

The first milestone is to prove that Ghost Talent can surface a small number of genuinely interesting, non-obvious AI engineers or researchers from real public data.

## Maintainer

Created and maintained by **AmazingKimi**.
