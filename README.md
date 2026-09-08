# Ghost Talent

**Open-source emerging talent intelligence.**

**Discover exceptional AI engineers and researchers before they become obvious.**

Ghost Talent starts from a technical frontier — CUDA, Triton, LLM inference, compilers, runtimes, distributed systems — and looks for people whose **public technical evidence is becoming stronger before their public visibility catches up**.

Recruiting search asks:

> I need a CUDA engineer. Who matches the role?

Ghost Talent asks:

> Who in CUDA / Triton / inference is becoming unusually well-validated before the market broadly notices?

## Current status

Ghost Talent is an **experimental research and discovery system**. It does **not** yet have mature predictive-validity results and does not claim to outperform professional sourcing, technical review, or simple baselines.

One real prospective cohort is already frozen and waiting for 30 / 90 / 180-day outcomes. That cohort was frozen under score version `0.1.5`, so its future results will validate that historical model only. A new prospective cohort under the current model is required to validate current behavior directly.

Until outcomes mature, the project should be judged as a falsifiable early-talent hypothesis engine, not a proven prediction system.

## What is different

Ghost Talent separates four stages that ordinary GitHub talent search often collapses together:

`Discovery → External Validation → Recommendation → Prospective Evaluation`

A person can rank highly in discovery and still receive `WATCH`, `LOW CONFIDENCE`, or `PROVEN / ALREADY VISIBLE` rather than an emerging recommendation.

The active score version is **0.2.8**:

`Ghost Score = 0.30 Capability + 0.25 External Validation + 0.25 Momentum + 0.10 Visibility Gap + 0.10 Evidence Confidence`

`Capability = 0.65 Internal Capability + 0.35 External Validation`

`Radar = 0.35 External Validation + 0.25 Momentum + 0.20 Visibility Gap + 0.15 Capability + 0.05 Evidence Confidence`

Full specification: [`GHOST_SCORE.md`](GHOST_SCORE.md)

## Hard recommendation rules

**High GitHub activity alone can never create EARLY SIGNAL or STRONG SIGNAL.**

Current defenses include:

- self-owned activity is not external validation,
- stars, forks and general issue activity do not drive Momentum,
- missing prior history does not become synthetic acceleration,
- 100-event-truncated GitHub history is reported and conservatively capped,
- documentation / tests / examples / CI paths do not count as core implementation evidence,
- inspected PRs need a substantive-change gate before receiving stronger credit,
- `COLLABORATOR` approval is not treated as maintainer acceptance; current acceptance evidence requires repository `OWNER` or `MEMBER`,
- already-visible strong people are routed to `PROVEN / ALREADY VISIBLE` rather than emerging recommendations.

v0.2.8 also reduces dependence on a curated upstream allowlist. Recognized repositories remain useful context, but they are **not a mandatory gateway** to EARLY SIGNAL. A substantive PR in a newer or less famous external project can count when changed-file core evidence or owner/member approval verifies the work.

## Recommendation states

- **STRONG SIGNAL** — strong recent external validation, sufficient history, and recent owner/member-approved core-path evidence.
- **EARLY SIGNAL** — credible recent verified external-project evidence with sufficient history and confidence; curated-upstream status is not required.
- **WATCH** — interesting capability or Radar, but not enough external proof.
- **DISCOVERED** — found by Scout; no recommendation implied.
- **LOW CONFIDENCE** — evidence coverage or trust is insufficient.
- **PROVEN / ALREADY VISIBLE** — clearly strong, but no longer an emerging “ghost”.

## Candidate Dossier

A Scout card is only an evidence summary. The Candidate Dossier is the decision layer:

- technical profile,
- why now,
- best external evidence,
- evidence mix,
- trajectory,
- recommendation,
- main evidence risk.

The practical question is:

> **Why should a technical reviewer spend time on this person now?**

## Evidence and identity

Current public sources are GitHub and OpenAlex. Coverage is incomplete by design and strong closed-source engineers can be missed.

Cross-source identity uncertainty remains uncertainty. A name match is not treated as verified identity. Public work is used for research intelligence only; Ghost Talent is not an employment-decision system and does not infer sensitive attributes.

## Benchmark

The first real production cohort is frozen and immutable:

- benchmark ID: `2026-09-08-cuda-triton-v01`
- query: `LLM inference CUDA Triton`
- source snapshot: `20260907T162245054462Z-b36e731d`
- as-of: `2026-09-07T16:22:45.054462Z`
- cohort size: 20
- score version: `0.1.5`

It must never be recomputed using v0.2.8.

Benchmark metrics include Precision@K, Breakout Lead Time, and comparison against followers, stars and raw contribution count. Wins and misses are both retained.

**Important validation gap:** the first cohort can validate only frozen score version `0.1.5`. The next benchmark action is to freeze one or more independent prospective cohorts under `0.2.8` so future outcomes can test the current model directly.

Protocol: [`docs/BENCHMARK.md`](docs/BENCHMARK.md)

## Credibility work before outcomes mature

Before the prospective benchmark can answer “does this actually work?”, Ghost Talent can still test “does this model fail in obvious ways?”

Current credibility work includes:

- adversarial / anti-gaming tests,
- false-positive invariants,
- component-correlation analysis,
- identity audit protocol,
- retrospective validation protocol with explicit historical-observability rules.

These are sanity checks, **not substitutes for predictive validation**.

See:

- [`docs/ADVERSARIAL_TESTS.md`](docs/ADVERSARIAL_TESTS.md)
- [`docs/CREDIBILITY_PHASE.md`](docs/CREDIBILITY_PHASE.md)
- [`docs/RETROSPECTIVE_VALIDATION.md`](docs/RETROSPECTIVE_VALIDATION.md)

## Run locally

Python 3.10+.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools
pip install -e .
python -m ghost_talent.app
```

Then open `http://127.0.0.1:8765`.

On macOS, `./start.command` remains available as a convenience launcher.

A GitHub token is optional for lightweight public discovery, but **full External Validation and recommendation-quality output require authenticated GitHub access**. Keep tokens local and never commit them.

## Known limitations

- no mature predictive-validity result yet,
- the first frozen cohort validates an older model rather than current v0.2.8,
- deterministic weights and thresholds remain uncalibrated hypotheses,
- GitHub followers are a weak visibility proxy,
- GitHub public-event history is incomplete and can truncate at 100 events,
- public OSS evidence undercovers excellent closed-source engineers,
- external PR inspection is bounded rather than a complete code review,
- mixed external-project inspection can still miss important PRs,
- cross-source identity verification remains conservative.

## Principles

1. Discovery is not recommendation.
2. Self-owned activity is not external validation.
3. A score is not evidence by itself.
4. Missing evidence stays missing.
5. Identity uncertainty remains uncertainty.
6. Historical evidence cannot be rewritten with future information.
7. Benchmark wins and misses both remain visible.
8. Sensitive personal attributes are outside the model.

## License

MIT.

## Maintainer

Created and maintained by **AmazingKimi**.
