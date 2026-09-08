# Ghost Talent

**Open-source emerging talent intelligence.**

**Discover exceptional AI engineers and researchers before they become obvious.**

Ghost Talent starts from a technical frontier — CUDA, Triton, LLM inference, compilers, runtimes, distributed systems — and looks for people whose **public technical evidence is becoming stronger before their public visibility catches up**.

Recruiting search asks:

> I need a CUDA engineer. Who matches the role?

Ghost Talent asks:

> Who in CUDA / Triton / inference is becoming unusually well-validated before the market broadly notices?

## Current status

Ghost Talent is an **experimental research and discovery system**. It does **not** yet have mature predictive-validity results and does not claim to outperform professional sourcing, technical review, simple baselines, or random controls.

Six historical prospective freeze records are recorded: one under score version `0.1.5` and five under `0.2.8`. **For v0.2.8, only one complete cohort (20/100 recorded positions) is currently member-by-member inspectable in this repository. The other four v0.2.8 records (80 positions) have no public member files and no public SHA-256 commitment at protocol-v2 adoption time, so their member-level artifact existence is treated as unverified from public evidence and they are ineligible for headline predictive-validity claims unless an original artifact is recovered with defensible provenance.** Candidates may overlap across cohorts. No 30/90/180-day outcome horizon has matured.

The five v0.2.8 cohorts were created in one execution window and are not independent temporal replications. They also had no synchronized random-control cohort at T0, so they cannot by themselves satisfy the stricter protocol-v2 headline-validity gate.

**Governing benchmark protocol:** [`docs/BENCHMARK_PROTOCOL_v2.md`](docs/BENCHMARK_PROTOCOL_v2.md). It was adopted after the 2026-09-08 freezes but before any outcome horizon matured; the repository does not pretend its new T0 design requirements existed retroactively.

## What is different

Ghost Talent separates:

`Discovery → External Validation → Recommendation → Prospective Evaluation`

A person can rank highly in discovery and still receive `WATCH`, `LOW CONFIDENCE`, or `PROVEN / ALREADY VISIBLE` rather than an emerging recommendation.

The active score version is **0.2.8**:

`Ghost Score = 0.30 Capability + 0.25 External Validation + 0.25 Momentum + 0.10 Visibility Gap + 0.10 Evidence Confidence`

`Capability = 0.65 Internal Capability + 0.35 External Validation`

`Radar = 0.35 External Validation + 0.25 Momentum + 0.20 Visibility Gap + 0.15 Capability + 0.05 Evidence Confidence`

Full specification: [`docs/GHOST_SCORE.md`](docs/GHOST_SCORE.md)

## Hard recommendation rules

**High GitHub activity alone can never create EARLY SIGNAL or STRONG SIGNAL.**

Current defenses include:

- self-owned activity is not external validation,
- stars, forks and general issue activity do not drive Momentum,
- missing prior history does not become synthetic acceleration,
- truncated GitHub history is reported and conservatively capped,
- documentation/tests/examples/CI paths do not count as core implementation evidence,
- inspected PRs need substantive-change evidence,
- `COLLABORATOR` approval is not maintainer acceptance; current acceptance evidence requires repository `OWNER` or `MEMBER`,
- already-visible strong people are routed to `PROVEN / ALREADY VISIBLE` rather than emerging recommendations.

v0.2.8 reduces dependence on a curated upstream allowlist. Recognized repositories are context, not a mandatory gateway to EARLY SIGNAL.

## Recommendation states

- **STRONG SIGNAL** — strong recent external validation, sufficient history, and recent owner/member-approved core-path evidence.
- **EARLY SIGNAL** — credible recent verified external-project evidence with sufficient history and confidence.
- **WATCH** — interesting capability or Radar, but not enough external proof.
- **DISCOVERED** — found by Scout; no recommendation implied.
- **LOW CONFIDENCE** — evidence coverage or trust is insufficient.
- **PROVEN / ALREADY VISIBLE** — clearly strong, but no longer an emerging “ghost”.

## Candidate Dossier

A Scout card is only an evidence summary. The Candidate Dossier is the decision layer: technical profile, why now, best external evidence, evidence mix, trajectory, recommendation, and main evidence risk.

> **Why should a technical reviewer spend time on this person now?**

## Evidence and identity

Current public sources are GitHub and OpenAlex. Coverage is incomplete by design and strong closed-source engineers can be missed. Cross-source identity uncertainty remains uncertainty. Public work is used for research intelligence only; Ghost Talent is not an employment-decision system and does not infer sensitive attributes.

## Benchmark

| Benchmark ID | Score | Size | Full cohort public here? | Evidence eligibility |
|---|---:|---:|---|---|
| `2026-09-08-cuda-triton-v01` | 0.1.5 | 20 | No | historical record; not member-level public here |
| `2026-09-08-llm-inference-cuda-triton-v028` | 0.2.8 | 20 | No | member artifact unverified from public evidence |
| `2026-09-08-ai-compiler-runtime-v028` | 0.2.8 | 20 | No | member artifact unverified from public evidence |
| `2026-09-08-quantization-kernels-v028` | 0.2.8 | 20 | No | member artifact unverified from public evidence |
| `2026-09-08-inference-infrastructure-v028` | 0.2.8 | 20 | No | member artifact unverified from public evidence |
| `2026-09-08-distributed-training-systems-v028` | 0.2.8 | 20 | **Yes** | publicly inspectable frozen cohort |

The public cohort is [`benchmarks/2026-09-08-distributed-training-systems-v028/cohort.json`](benchmarks/2026-09-08-distributed-training-systems-v028/cohort.json). Missing historical member files will never be reconstructed from later API data.

Protocol v2 requires, before any future headline predictive-validity claim: a full frozen artifact, SHA-256 commitment at freeze time, a 90-day primary horizon, blind adjudication, member-level evidence, simple baselines, an eligible same-population random control, and deduplicated pooled statistics where pooling is used. Null/negative results must be published as prominently as positive results.

Operational registry: [`docs/BENCHMARK.md`](docs/BENCHMARK.md).

## Credibility work before outcomes mature

Current credibility work includes adversarial/anti-gaming tests, false-positive invariants, component-correlation analysis, identity audit protocol, retrospective-validation rules, and automated GitHub Actions checks. These are sanity checks, **not substitutes for predictive validation**.

See [`docs/ADVERSARIAL_TESTS.md`](docs/ADVERSARIAL_TESTS.md), [`docs/CREDIBILITY_PHASE.md`](docs/CREDIBILITY_PHASE.md), and [`docs/RETROSPECTIVE_VALIDATION.md`](docs/RETROSPECTIVE_VALIDATION.md).

## Run locally

Python 3.10+.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools
pip install -e .
python -m ghost_talent.app
```

Then open `http://127.0.0.1:8765`. On macOS, `./start.command` is available as a convenience launcher.

A GitHub token is optional for lightweight public discovery, but **full External Validation and recommendation-quality output require authenticated GitHub access**. Keep tokens local and never commit them.

## Known limitations

- no mature predictive-validity result yet,
- only 20/100 v0.2.8 recorded positions are member-level public here,
- the four unpublished v0.2.8 member artifacts have no public pre-outcome hash commitment at v2 adoption time,
- the existing v0.2.8 cohorts lack synchronized random controls and are not temporal replications,
- protocol v2 is currently stricter than the benchmark software; several enforcement features remain to be implemented before a v2 headline claim,
- deterministic weights and thresholds remain uncalibrated hypotheses,
- GitHub followers are a weak visibility proxy,
- public-event history is incomplete,
- public OSS evidence undercovers strong closed-source engineers,
- external PR inspection is bounded,
- cross-source identity verification remains conservative.

## Principles

1. Discovery is not recommendation.
2. Self-owned activity is not external validation.
3. A score is not evidence by itself.
4. Missing evidence stays missing.
5. Identity uncertainty remains uncertainty.
6. Historical evidence cannot be rewritten with future information.
7. Wins, misses, null results, and protocol failures remain visible.
8. Frozen, publicly inspectable, and validated are different claims.
9. Sensitive personal attributes are outside the model.

## License

MIT.

## Maintainer

Created and maintained by **AmazingKimi**.
