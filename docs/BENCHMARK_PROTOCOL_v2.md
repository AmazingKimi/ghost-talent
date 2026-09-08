# Ghost Talent — Prospective Benchmark Protocol (v2)

This document is the single source of truth for how Ghost Talent's prospective benchmark is designed, frozen, evaluated, and reported. It supersedes prior informal descriptions in `README.md` and `docs/BENCHMARK.md`. Any future change creates a new protocol version and must not be applied retroactively to already-frozen cohorts.

**Adoption note (2026-09-08):** v2 was adopted after the existing 2026-09-08 cohorts were frozen but before any 30/90/180-day outcome horizon matured. Rules that require T0-time design (notably synchronized random controls) are forward requirements and must not be represented as if they existed at the original freezes. Evaluation/reporting safeguards adopted before outcome review — blind adjudication, the primary horizon, anti-selection rules, and failure publication — govern future evaluation where applicable and their post-freeze adoption must be disclosed.

## 1. Current cohort registry — disclosure, not validity

Six prospective cohort freeze records are recorded: one legacy `0.1.5` record and five `0.2.8` records. Public `main` currently contains a full cohort file only for `2026-09-08-distributed-training-systems-v028`.

| Cohort | Score version | Positions | Freeze record | Full file public? | SHA-256 commitment |
|---|---:|---:|---|---|---|
| `2026-09-08-cuda-triton-v01` | 0.1.5 | 20 | Yes | **No** | not available from public repo |
| `2026-09-08-llm-inference-cuda-triton-v028` | 0.2.8 | 20 | Yes | **No** | **unverified — required if original artifact is recovered** |
| `2026-09-08-ai-compiler-runtime-v028` | 0.2.8 | 20 | Yes | **No** | **unverified — required if original artifact is recovered** |
| `2026-09-08-quantization-kernels-v028` | 0.2.8 | 20 | Yes | **No** | **unverified — required if original artifact is recovered** |
| `2026-09-08-inference-infrastructure-v028` | 0.2.8 | 20 | Yes | **No** | **unverified — required if original artifact is recovered** |
| `2026-09-08-distributed-training-systems-v028` | 0.2.8 | 20 | Yes | **Yes** | public artifact; future cohorts must commit hash at freeze time |

Only **20/100 v0.2.8 positions** are currently member-by-member inspectable from this repository. Because no SHA-256 commitment for the four unpublished v0.2.8 member files is available in the public repository at v2 adoption time, v2 treats their member-level existence as **unverified from public evidence**, not as cryptographically committed frozen artifacts. Their freeze metadata remains part of the historical record, but they are ineligible for headline predictive-validity claims unless an original artifact is recovered and can be given defensible provenance. No outcome horizon has matured; predictive validity is not established.

## 2. Statistical independence

Candidates may appear in multiple cohorts. Cohort positions are not independent people.

- **Per-cohort metrics:** Precision@K may be reported within one frozen query cohort, labeled by cohort ID and score version. Per-cohort numbers must not be summed as independent trials.
- **Pooled metrics:** any cross-cohort person-level breakout rate/count/headline must deduplicate by stable subject identity. One real-world breakout counts at most once. Report total positions and unique candidates side by side.
- **No pooled evaluator, no pooled claim:** until a published deduplicating evaluator exists, no pooled Precision@K or pooled breakout rate may be claimed.
- **Cross-version overlap:** v0.1.5/v0.2.8 overlap must be disclosed; any cross-version conclusion requires a deduplicated sensitivity view.
- **Same-window cohorts are not temporal replications:** the five v0.2.8 cohorts were frozen in one execution window. They test domain breadth under one execution period, not independent replication. Future replication rounds must use separate dates/execution sessions and report rounds separately before pooled cross-time claims.

## 3. Baseline and control design

Three controls are required for future protocol-v2 benchmark rounds:

1. **Naive popularity baselines:** followers, top-repository stars, and raw contributions, applied to the same source population.
2. **Random control cohort:** for at least one query per benchmark round, draw a same-size, same-time cohort by uniform random sampling from the same query source population, without Ghost Score ranking, and carry it through identical blind adjudication. This estimates the domain base rate. No headline predictive-validity claim may be made for a query domain that has never had an eligible random control evaluated.
3. **Domain-selection disclosure:** domains are maintainer-selected unless drawn from a separately pre-registered list. At least one future cohort per round should use a domain the maintainers did not expect to produce a strong signal.

**Existing-cohort limitation:** the 2026-09-08 v0.2.8 cohorts did not have synchronized random controls at T0. A later random sample must not be mislabeled as their contemporaneous control. These cohorts therefore cannot by themselves satisfy the v2 headline-validity gate.

## 4. Outcome Definition v0.1 and adjudication

The existing cohorts carry `outcome_definition_version: 0.1`. v2 makes the operational adjudication rules explicit before any outcome horizon matures; this post-freeze clarification must be disclosed with results and must not be represented as T0 preregistration.

A candidate may be `breakout=true` only when new public evidence after T0 establishes one of:

- `maintainer_or_core_role`
- `major_oss_contribution`
- `project_breakout`
- `research_breakout`
- `public_role_transition`

`public_role_transition` requires independently observable technical significance; ordinary lateral mobility does not qualify.

Positive adjudication requires a public evidence URL, identity match, post-T0 timing, an allowed outcome type, and a breakout date where determinable. T0-visible evidence is not a breakout. Ambiguous identity/timing/significance is `unadjudicated`. A miss requires a matured horizon, completed review under the same rubric, and no qualifying post-T0 evidence. Unreviewed is neither win nor miss.

### 4.1 Blind adjudication

Outcome adjudication must hide Ghost Score, Radar score, recommendation state, and control/scored status from the adjudicator while evidence is searched and labels are assigned. Candidate identity may be revealed only to the extent necessary to search public evidence; ranking/model status must remain hidden. Scores/control labels are joined only after adjudication is logged.

If genuine blinding is impossible — including a single adjudicator who already remembers rankings — that limitation must be disclosed alongside every result. A non-blind result must not be described as blind.

### 4.2 Outcome-definition failure is reportable

If v0.1 proves subjective, permissive, or too strict, publish that failure and examples. A revised outcome definition receives a new version and does not rewrite existing adjudications.

## 5. Horizon preregistration

- **90 days is the primary horizon** for future headline claims under v2.
- 30 and 180 days are secondary/exploratory.
- All matured horizons must be reported together; the most favorable horizon may not be selectively reported.

For the existing cohorts, this primary-horizon choice was adopted after T0 but before any horizon matured and must be disclosed as such.

## 6. Reporting requirements

A result may be described as evidence relevant to predictive validity only when the applicable evidence is publicly inspectable together:

1. frozen cohort file;
2. governing protocol/outcome rubric and adoption timing;
3. reported horizons;
4. member-level adjudication evidence, including unadjudicated/unreviewed cases;
5. naive baselines and, for v2-eligible headline claims, an eligible random control;
6. deduplicated unique-candidate counts for pooled statistics;
7. disclosure of adjudication blinding limitations.

Wins, misses, null results, and protocol failures receive equal publication prominence. Partial publication is not a benchmark result.

## 7. Missing cohort files and cryptographic commitments

### 7.1 Recovery

An unpublished historical artifact may be published only if the original file is recovered from the original local artifact/backup with defensible provenance. It must not be reconstructed from later API data.

### 7.2 Immediate hash rule

A SHA-256 commitment is useful only if made before outcomes are known. At v2 adoption time, no public SHA-256 commitment is available for the four unpublished v0.2.8 member files. Ghost Talent therefore **does not claim that such a commitment already exists**.

If an original file is presently available locally, compute and publish its SHA-256 immediately, before outcome adjudication, together with provenance. If no stable original artifact can be produced, classify that cohort's member-level artifact as `existence-unverified` rather than pretending a cryptographic freeze exists.

### 7.3 Permanent classification

A metadata-only/existence-unverified historical cohort may be reported for historical transparency but is permanently ineligible for headline predictive-validity claims unless its original artifact is recovered with defensible provenance. A later good-looking outcome does not upgrade its evidence status.

### 7.4 Forward hash commitment

Every new v2 prospective cohort must publish its full frozen artifact **and SHA-256 hash at freeze time**. A run that fails either requirement is not part of the publicly verifiable benchmark set.

## 8. Forward implementation requirements

Before Ghost Talent makes a v2 headline predictive-validity claim, the public benchmark tooling must implement and test:

- random-control sampling from the same query source population;
- blind outcome templates that omit scores/recommendation/control labels;
- validation of allowed outcome types and evidence fields;
- T0/horizon timing checks;
- stable-identity deduplication for pooled metrics;
- artifact SHA-256 generation/verification at freeze time;
- explicit exclusion of ineligible historical metadata-only/existence-unverified cohorts from headline aggregation.

Protocol text is not a substitute for code enforcement.

## 9. Falsifiability and publication

This protocol does not certify predictive validity. It defines minimum conditions under which a future result — positive, negative, or null — is interpretable.

If Ghost Talent has no useful predictive signal, its primary-horizon performance should fail to separate meaningfully from eligible controls/baselines. **That null or negative result must be published with the same prominence and artifact completeness required for a positive result.**

No result is evidence of predictive validity unless the frozen artifact, governing protocol, evaluation horizon, member-level adjudication evidence, eligible controls, and baseline comparison are available for inspection.
