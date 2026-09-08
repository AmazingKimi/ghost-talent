# Ghost Talent

**Open-source emerging talent intelligence.**

**Discover exceptional AI engineers and researchers before they become obvious.**

Ghost Talent starts from a technical frontier — CUDA, Triton, LLM inference, compilers, runtimes, distributed systems — and looks for people whose public technical evidence is becoming stronger before conventional visibility makes them obvious.

Recruiting search asks:

> I need a CUDA engineer. Who matches the role?

Ghost Talent asks:

> Who in CUDA / Triton / inference is becoming unusually well-validated before the market broadly notices?

That is the category we are building: **Emerging Talent Intelligence**.

## Current research status

Ghost Talent is an **experimental research and discovery system**. It does not yet have mature predictive-validity results.

A real prospective benchmark cohort has been frozen and is now waiting for 30 / 90 / 180-day outcomes. Until those outcomes mature, Ghost Talent does **not** claim that its ranking predicts future technical success or outperforms simple baselines.

The current goal is narrower: make early-talent hypotheses evidence-grounded, auditable, falsifiable, and prospectively testable.

## What is different

Most talent systems optimize for people who are already easy to find: famous researchers, obvious maintainers, polished résumés, or candidates already inside a hiring funnel.

Ghost Talent focuses on the gap between:

- demonstrated technical work,
- external technical validation,
- recent trajectory,
- and current public visibility.

A high score is not automatically a recommendation. Discovery and recommendation are separate stages.

## Current scoring model

The active model is score version **0.2.6**.

`Ghost Score = 0.30 Capability + 0.25 External Validation + 0.25 Momentum + 0.10 Visibility Gap + 0.10 Evidence Confidence`

Capability itself combines internal execution evidence and external validation:

`Capability = 0.65 Internal Capability + 0.35 External Validation`

Ghost Radar asks which candidates are worth attention now:

`Radar = 0.35 External Validation + 0.25 Momentum + 0.20 Visibility Gap + 0.15 Capability + 0.05 Evidence Confidence`

### Important rule

**High GitHub activity alone can never produce an EARLY SIGNAL or STRONG SIGNAL.**

External evidence is required. Current gates include recent recognized-upstream contributions, changed-file core-path evidence, maintainer-approved review evidence, sufficient confidence, low current visibility, and anti-noise checks.

## Recommendation states

Ghost Talent separates discovery from recommendation:

- **STRONG SIGNAL** — strong recent external validation, including recent maintainer-approved core-path evidence.
- **EARLY SIGNAL** — credible recent upstream validation, still relatively low visibility.
- **WATCH** — internal capability or activity is interesting, but external validation is not yet strong enough.
- **DISCOVERED** — found by the Scout, but evidence is not sufficient for recommendation.
- **LOW CONFIDENCE** — source coverage, identity confidence, or noise makes the record unsafe to recommend.
- **PROVEN / ALREADY VISIBLE** — clearly strong and externally validated, but already too visible to count as an emerging "ghost".

Ranking never means automatic recommendation.

## External Validation

The current model distinguishes self-controlled work from externally accepted work.

Collected signals include:

- external merged pull requests,
- recognized upstream repositories,
- changed-file inspection for core technical paths,
- maintainer-approved reviews on the same PR,
- recency of those external signals,
- repository ownership,
- verified research links where available.

External validation is deliberately weighted separately from raw repository contribution volume.

## Evidence Mix

Candidate records expose how much of the available evidence comes from:

- self-owned repositories,
- external repository contributions,
- verified external pull requests,
- verified research evidence,
- unclassified repository evidence.

Evidence concentrated in self-owned repositories can reduce confidence.

## Anti-noise and anti-gaming stance

Ghost Talent treats raw activity as easy to misread and potentially gameable.

Current defenses include:

- bot / automation filtering,
- course / homework / tutorial repository patterns,
- self-owned evidence concentration penalties,
- external-validation gates for EARLY / STRONG,
- recency requirements for emerging recommendations,
- maintainer-approval checks,
- changed-file core-path checks,
- separation of PROVEN / ALREADY VISIBLE from emerging signals.

The public adversarial test plan is in [`docs/ADVERSARIAL_TESTS.md`](docs/ADVERSARIAL_TESTS.md).

## Candidate Dossier

A Scout result is only a candidate. The Candidate Dossier adds the decision layer:

- technical profile,
- why now,
- best external evidence,
- evidence mix,
- trajectory,
- external validation structure,
- recommendation status,
- main evidence risk.

The purpose is to answer: **why should a technical reviewer spend time on this person now?**

## Discovery workflow

`technical topic → wide scout → contributor + merged-PR discovery → evidence → external validation → scoring → recommendation gate → Candidate Dossier → immutable snapshot → benchmark cohort`

Current public sources:

- GitHub
- OpenAlex

Source coverage is incomplete by design. Ghost Talent will miss strong people whose important work is private, internal, unpublished, or absent from these sources.

## Prospective evaluation infrastructure

Every successful Scout run can produce an immutable dated snapshot and append-only history.

This is not yet a "historical moat" claim. It is **prospective evaluation infrastructure** designed to make later claims auditable.

The first real production benchmark cohort is frozen:

- benchmark ID: `2026-09-08-cuda-triton-v01`
- query: `LLM inference CUDA Triton`
- source snapshot: `20260907T162245054462Z-b36e731d`
- as-of: `2026-09-07T16:22:45.054462Z`
- cohort size: 20
- score version: `0.1.5`

This cohort is immutable and must never be recomputed using later score versions.

## Benchmark

Ghost Talent Benchmark evaluates frozen cohorts only after future outcomes become observable.

Supported metrics include:

- Precision@5 / @10 / @20,
- Breakout Lead Time,
- comparison with followers,
- comparison with repository stars,
- comparison with raw contribution count,
- explicit no-future-leakage rules.

Protocol: [`docs/BENCHMARK.md`](docs/BENCHMARK.md)

No predictive-validity claim should be made before real outcome windows mature.

## Credibility work before 30-day outcomes

While prospective cohorts mature, Ghost Talent can still test whether its current model behaves sanely.

The credibility suite focuses on:

- false-positive sanity tests,
- anti-gaming / adversarial cases,
- identity audit procedures,
- component-correlation analysis,
- evidence concentration checks,
- recommendation-state invariants.

These checks are **not substitutes for predictive validation**. They only test whether the model violates obvious constraints before the real benchmark matures.

## Run locally

Ghost Talent supports Python 3.10 and newer.

### macOS launcher

```bash
chmod +x start.command
./start.command
```

### Manual setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools
pip install -e .
python -m ghost_talent.app
```

Then open `http://127.0.0.1:8765`.

A GitHub token is optional but recommended because unauthenticated GitHub API requests have a much lower rate limit. Keep tokens local and never commit them.

## Principles

1. Every important claim should be traceable to public evidence.
2. Discovery is not recommendation.
3. Self-owned activity is not external validation.
4. Raw activity volume is not technical quality.
5. Missing evidence stays missing.
6. Identity uncertainty remains uncertainty.
7. Historical snapshots are append-only.
8. Backtests must prevent future-information leakage.
9. Benchmark wins and misses both remain visible.
10. Sensitive personal attributes are outside the ranking model.

## Public methodology

- [`GHOST_SCORE.md`](GHOST_SCORE.md)
- [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md)
- [`docs/BENCHMARK.md`](docs/BENCHMARK.md)
- [`docs/ADVERSARIAL_TESTS.md`](docs/ADVERSARIAL_TESTS.md)

## Limitations

Ghost Talent currently relies mainly on GitHub and OpenAlex public evidence. GitHub activity is not a complete measure of technical ability, followers are an imperfect visibility proxy, identity resolution remains conservative, source APIs can degrade, and deterministic thresholds are not probability calibration.

The current scoring weights and thresholds are hypotheses to be tested, not truths discovered from training data.

## License

MIT.

## Maintainer

Created and maintained by **AmazingKimi**.
