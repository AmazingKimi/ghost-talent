# Ghost Talent

**Open-source emerging talent intelligence.**

**Discover exceptional AI engineers and researchers before they become obvious.**

Ghost Talent starts from a technical frontier — CUDA, Triton, LLM inference, compilers, research areas — and looks for people whose demonstrated capability and momentum are rising faster than their public visibility.

Recruiting search asks:

> I need a CUDA engineer. Who matches the role?

Ghost Talent asks:

> In CUDA / Triton / inference, who is getting stronger before the market notices?

That is the category we are building: **Emerging Talent Intelligence**.

## Why Ghost Talent

Most talent systems are optimized for people who are already easy to find: famous researchers, highly followed engineers, obvious maintainers, polished résumés, or candidates already inside a hiring funnel.

Ghost Talent focuses on the **visibility gap** between demonstrated technical strength and current public recognition.

The goal is not to predict careers with certainty. The goal is to surface strong, rising technical people earlier and make every ranking traceable to evidence.

In a September 2026 scan of adjacent public GitHub projects, we found several strong recruiting, sourcing, and hidden-talent tools. Among the projects reviewed, we did not find one centered on the same explicit combination of **technical momentum + visibility gap + public OSS evidence + immutable first-detection history + historical breakout benchmarking**.

See [`docs/COMPETITIVE_LANDSCAPE.md`](docs/COMPETITIVE_LANDSCAPE.md) for the reviewed projects and category boundary.

## Ghost Score

The current deterministic model is:

`Ghost Score = 0.35 Capability + 0.35 Momentum + 0.20 Visibility Gap + 0.10 Evidence Confidence`

- **Capability — 35%**: demonstrated technical depth and quality of work
- **Momentum — 35%**: whether meaningful activity is accelerating relative to an observable baseline
- **Visibility Gap — 20%**: whether technical strength appears ahead of current public visibility
- **Evidence Confidence — 10%**: how reliable the identity match and supporting evidence are

Raw contribution count is not treated as technical quality. Where available, Ghost Talent separately inspects merged pull requests, changed-file scope, and technical paths such as CUDA, Triton, kernels, compilers, inference, attention, GEMM, MoE, quantization, GPU and benchmarks.

Public specification: [`GHOST_SCORE.md`](GHOST_SCORE.md)

Full methodology and publication rules: [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md)

## Ghost Radar

Ghost Score measures the current evidence-backed profile. Ghost Radar asks a narrower question:

> Which candidates look unusually early and worth watching now?

The current Radar model emphasizes:

`0.35 Momentum + 0.30 Contribution Quality + 0.25 Visibility Gap + 0.10 Evidence Confidence`

`EARLY SIGNAL` is only emitted when hard evidence thresholds are met. Activity alone is not enough.

## Current workflow

`technical topic → wide scout → contributor + merged-PR discovery → evidence → scoring → ranking → immutable snapshot → first-detected ledger → longitudinal history → benchmark cohort`

Current public sources:

- GitHub
- OpenAlex

Current capabilities include:

- wide candidate discovery across multiple repositories
- recent merged-PR author discovery
- contribution-quality inspection
- momentum and visibility-gap scoring
- repository dominance control
- immutable dated snapshots
- first-detected ledger
- deterministic Ghost Score explanations
- Ghost Radar / EARLY SIGNAL detection
- source-status reporting
- conservative cross-source identity handling
- append-only candidate time series
- 7-day / 30-day trajectory semantics
- Rising Fast v2
- local query watchlist runner
- frozen benchmark cohort engine

## Historical moat

Every successful Scout run can produce an append-only historical snapshot. Candidate first-detection records and query-scoped longitudinal observations are retained separately.

That makes it possible to ask, later:

> Did Ghost Talent identify this person before they became obvious?

Code can be copied. A dated record of who was found before they became obvious cannot be recreated later.

## Ghost Talent Benchmark

Ghost Talent now includes a versioned benchmark framework designed to test predictive validity rather than assume it.

A benchmark freezes an existing Scout snapshot before outcomes are known, retains Ghost Score and simple baseline values, and evaluates the cohort later at explicit horizons such as 30, 90 and 180 days.

Benchmark v0.1 supports:

- immutable frozen cohorts
- versioned Breakout Outcome definitions
- Precision@5 / @10 / @20
- Breakout Lead Time
- comparison against followers, repository stars and raw contributions
- outcome-adjudication templates
- explicit no-future-leakage rules

Protocol: [`docs/BENCHMARK.md`](docs/BENCHMARK.md)

Freeze the latest local snapshot for a query:

```bash
ghost-talent-benchmark freeze \
  --query "LLM inference CUDA Triton" \
  --benchmark-id "2026-09-08-cuda-triton-v01" \
  --top-k 20
```

A frozen cohort is written once and cannot be silently overwritten.

Historical evaluation must never use information that was not observable at the original `as_of_date`.

## Run locally

Ghost Talent supports Python 3.10 and newer.

### macOS launcher

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

A GitHub token is optional but recommended because unauthenticated GitHub API requests have a much lower rate limit. Keep tokens local and never commit them.

## Principles

1. Every important claim should be traceable to public evidence.
2. Identity uncertainty remains uncertainty; never force a match.
3. Raw activity volume is not the same as technical capability.
4. The system should detect acceleration, not merely popularity.
5. Historical snapshots are append-only.
6. Backtests must prevent future-information leakage.
7. Missing evidence stays missing; it is never fabricated.
8. Sensitive personal attributes are outside the ranking model.
9. Benchmark wins and misses both remain visible.

## Roadmap

The public roadmap is tracked in [`docs/ROADMAP.md`](docs/ROADMAP.md).

Near-term priorities:

- freeze the first real benchmark cohort
- continue daily/periodic time-series accumulation
- 30/90/180-day outcome adjudication
- stronger identity resolution and more source evidence
- reproducible public benchmark artifacts

## v0.1.0

Ghost Talent is usable end-to-end as a local open-source technical talent radar. The `v0.1.0` milestone established the public category, methodology, evidence model, Ghost Score, Radar concept, immutable snapshots and first-detected ledger.

Release notes: [`releases/v0.1.0.md`](releases/v0.1.0.md)

## Contributing

Methodology critiques, evidence-source work, identity resolution, reproducibility, benchmark design, performance improvements, and documented failure cases are welcome.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and the public issues.

## GitHub launch kit

Suggested Topics, social-preview copy, category wording, and discovery phrases are kept in [`docs/GITHUB_LAUNCH.md`](docs/GITHUB_LAUNCH.md).

## Search terms

Emerging AI talent · AI engineer discovery · AI researcher discovery · GitHub talent intelligence · open-source talent radar · hidden technical talent · CUDA engineer discovery · Triton engineer discovery · LLM inference talent · technical talent intelligence · evidence-grounded talent discovery

## Limitations

This is an early research and discovery system. GitHub public events provide a limited activity window, OpenAlex identity matching remains conservative, and source APIs can rate-limit or degrade. Benchmark outcomes require future observation; the existence of the benchmark framework is not evidence that Ghost Talent already has predictive validity.

## License

MIT.

## Maintainer

Created and maintained by **AmazingKimi**.
