# Ghost Talent — Prospective Benchmark Protocol (v2)

Protocol version: **v2** (adopted 2026-09-08).

This document is the single source of truth for how Ghost Talent's prospective benchmark is designed, frozen, evaluated, and reported. It supersedes prior informal benchmark descriptions. Any substantive future change creates a new protocol version and must not be applied retroactively to already-frozen cohorts.

If a shorter summary elsewhere conflicts with this document, this document governs.

The benchmark tests a falsifiable claim:

> Can Ghost Talent identify later-breakout technical people earlier than simple visibility baselines and an eligible random control?

It is not a hiring leaderboard. It is a longitudinal research protocol over public technical evidence.

**Adoption note.** v2 was adopted after the existing 2026-09-08 cohorts were frozen but before any 30/90/180-day outcome horizon matured. T0 design requirements added by v2 — especially synchronized random controls, domain-expectation registration, and freeze-time SHA-256 publication — are forward requirements and must never be represented as if they existed for the earlier freezes. Evaluation safeguards adopted before outcome review — including blind adjudication, horizon preregistration, conservative publication rules, and failure prominence — may govern future evaluation only with this post-freeze adoption timing disclosed.

---

## 1. Cohort registry: disclosure, not validity

Six historical prospective freeze records are recorded: one legacy cohort under score version `0.1.5` and five under `0.2.8`.

| Benchmark ID | Score version | Positions | As-of date | Full file in public repo? | Public SHA-256 commitment? | Current member-artifact status |
| --- | --- | ---: | --- | --- | --- | --- |
| `2026-09-08-cuda-triton-v01` | 0.1.5 | 20 | `2026-09-07T16:22:45Z` | **No** | No | `existence-unverified from public evidence` |
| `2026-09-08-llm-inference-cuda-triton-v028` | 0.2.8 | 20 | `2026-09-08T00:51:28Z` | No | No | `existence-unverified from public evidence` |
| `2026-09-08-ai-compiler-runtime-v028` | 0.2.8 | 20 | `2026-09-08T00:53:40Z` | No | No | `existence-unverified from public evidence` |
| `2026-09-08-quantization-kernels-v028` | 0.2.8 | 20 | `2026-09-08T00:55:31Z` | No | No | `existence-unverified from public evidence` |
| `2026-09-08-inference-infrastructure-v028` | 0.2.8 | 20 | `2026-09-08T00:57:21Z` | No | No | `existence-unverified from public evidence` |
| `2026-09-08-distributed-training-systems-v028` | 0.2.8 | 20 | `2026-09-08T03:32:59Z` | **Yes** | Not yet published | `publicly inspectable` |

Only **20/120 recorded positions overall** are currently member-by-member inspectable from this repository. Within v0.2.8 specifically, that is **20/100**.

A freeze metadata record is not the same thing as proof that the original member-level artifact still exists. Because no public member file or pre-outcome SHA-256 commitment is available for the five unpublished cohorts, v2 does **not** call those member artifacts cryptographically frozen. Unless an original artifact is recovered with defensible provenance, they are ineligible for headline predictive-validity claims.

No outcome horizon has matured. Predictive validity is **not established**.

---

## 2. Statistical independence

### 2.1 Positions are not independent people

The same person may appear in more than one query cohort, and a candidate may appear in both the legacy `0.1.5` cohort and a `0.2.8` cohort. Cohort positions are not independent observations of unique people.

### 2.2 Per-cohort and pooled metrics are different claims

1. **Per-cohort metrics** answer a query-specific ranking question. Precision@K and breakout rate may be reported within one eligible frozen cohort, labeled with cohort ID, score version, and horizon. They must not be summed across cohorts and described as independent trials.
2. **Cross-cohort / pooled metrics** span more than one cohort. They must deduplicate by stable subject identity before calculation. One real-world breakout may count at most once in a pooled unique-person metric. Every pooled publication must report both total cohort positions and unique candidate count.

### 2.3 No pooled evaluator, no pooled claim

The current evaluator computes one cohort at a time. Until a published and tested stable-identity deduplicating evaluator exists, Ghost Talent must not publish pooled Precision@K or a pooled breakout rate across the five v0.2.8 cohorts.

### 2.4 Cross-version overlap

A candidate appearing under both `0.1.5` and `0.2.8` cannot be presented as two independent breakout events in a pooled comparison. Version-specific results may be shown side by side, but overlap must be disclosed and any cross-version conclusion must include a deduplicated sensitivity view.

### 2.5 Same-window cohorts are not temporal replication

The five v0.2.8 cohorts were frozen during one execution window on 2026-09-08. They test query-domain breadth within one execution period, not independent replication across time. Shared API state, source outages, truncation, or pipeline defects could affect several cohorts simultaneously.

Future rounds intended as genuine replication must be frozen in separate execution sessions on different dates. Each round must be reported separately before any pooled cross-time claim is made.

---

## 3. Baseline and control design

Three comparison types are required for future protocol-v2 benchmark rounds.

### 3.1 Naive popularity baselines

Rank the same eligible source population by:

- raw GitHub follower count;
- top-repository stars;
- raw contribution count.

Baseline values must be frozen at T0.

### 3.2 Random control cohort

For at least one query per benchmark round, freeze a random control drawn from the same discovery population and execution window as the scored cohort.

The discovery population is operationally the union of eligible contributors and recent merged-PR authors returned by the Scout discovery stage for that query **before score-based ranking or enrichment selection**.

The control must:

- be sampled without Ghost Score ranking;
- use uniform random sampling from the eligible discovery population;
- record the sampling frame size, RNG algorithm, RNG seed, and sampled stable subject IDs;
- be frozen and published at T0 with the same artifact-integrity rules as the scored cohort;
- be carried through the same outcome rubric and blinded adjudication effort.

A control larger than the scored cohort is allowed and encouraged for power, but its size must be preregistered at T0. A later random sample cannot be retroactively labeled a synchronized control for the 2026-09-08 cohorts.

**No headline predictive-validity claim may be made for a query domain that has never had an eligible random control evaluated.**

### 3.3 Domain-selection disclosure

Domains are maintainer-selected unless explicitly drawn from a separately preregistered domain list. At freeze time each future cohort must record an expectation label: `expected-strong`, `neutral`, or `expected-weak`, with a short rationale. At least one domain per benchmark round must be preregistered `expected-weak` or `neutral`; it may not be chosen after outcomes are observed.

### 3.4 Power limitation

Small cohorts imply wide uncertainty. A nonsignificant test is **not evidence that Ghost Talent and the control are equivalent**; it is only insufficient evidence of separation at the stated sample size.

Therefore every published proportion must include a 95% confidence interval, effect sizes must be reported alongside p-values, and no single 20-person cohort is sufficient by itself for a broad product-level predictive-validity claim.

---

## 4. Outcome Definition v0.1

The existing cohorts carry `outcome_definition_version: 0.1`. The operational rules below were made explicit after T0 but before any outcome horizon matured. That timing must accompany future results; it must not be described as freeze-time preregistration for the existing cohorts.

A candidate may be marked `breakout=true` only when new public evidence after the cohort `as_of_date` establishes at least one of:

- `maintainer_or_core_role`;
- `major_oss_contribution`;
- `project_breakout`;
- `research_breakout`;
- `public_role_transition`.

`public_role_transition` requires independently observable technical significance. Ordinary lateral job mobility is not sufficient.

### 4.1 Positive adjudication requirements

A positive requires all of:

1. at least one public evidence URL;
2. identity attributable under the benchmark's identity rules;
3. the relevant event occurred after T0;
4. an allowed outcome type;
5. a breakout date where the public evidence permits one.

Evidence already observable at T0 is not a breakout. Ambiguous identity, timing, or technical significance is `unadjudicated`, not forced positive or negative.

### 4.2 Miss definition

A candidate is a miss at a stated horizon only when the horizon has elapsed, the candidate has been reviewed under the same rubric, and no qualifying post-T0 evidence was found. `unreviewed` is neither a miss nor a win.

### 4.3 Intervention / endogeneity disclosure

If project users contact, recruit, fund, promote, or otherwise intervene on a candidate after seeing Ghost Talent output, that intervention is an uncontrolled confounder. The model's own recommendation or downstream action caused by it must never be used as outcome evidence, and any known intervention must be disclosed with the candidate-level result.

### 4.4 Blind adjudication

Outcome evidence searching and labeling must hide, as far as operationally possible:

- Ghost Score;
- Radar score;
- recommendation state;
- scored-vs-random-control membership;
- original rank.

The adjudicator may see candidate identity because identity is necessary to search public evidence. Candidate identities from scored and control cohorts should be mixed under randomized adjudication IDs before review. Model/control labels and scores are joined back only after adjudication is logged.

If genuine blinding is impossible — including a reviewer who already remembers rankings — the result must be labeled non-blind and the limitation disclosed alongside the result.

**Reliability check:** all positive labels plus a preregistered random sample of at least 20% of non-positive reviewed cases must receive a second adjudication by an independent reviewer where feasible. If an independent reviewer is unavailable, a washout-period re-review may be used but must be labeled as such. Disagreements and their resolution must be published. This reliability sample is a quality-control check, not a substitute for the primary statistical test.

### 4.5 Failure of the outcome definition is reportable

If v0.1 proves too subjective, permissive, or strict, that failure and motivating examples must be published. Any revision creates a new outcome-definition version and does not retroactively rewrite existing labels.

---

## 5. Horizon and endpoint preregistration

Three evaluation horizons exist: 30, 90, and 180 days.

- **Primary horizon:** 90 days.
- **Secondary confirmation horizon:** 180 days.
- **Exploratory early horizon:** 30 days.

All matured horizons available at publication time must be reported together. A favorable secondary horizon may not replace an unfavorable primary horizon.

For a future v2-eligible scored-vs-random-control experiment, the **primary endpoint is the 90-day qualifying-breakout proportion across the full preregistered scored cohort** (for a 20-person cohort, equivalent to Precision@20 / breakout rate) compared with the eligible random control. Precision@5 and Precision@10 remain secondary ranking diagnostics and are not the sole basis for a headline predictive-validity claim.

For the existing 2026-09-08 cohorts, this endpoint/horizon choice was adopted after T0 but before outcomes matured and must be disclosed as such.

---

## 6. Statistical decision rule

The following rules apply to future v2-eligible scored-vs-random-control headline analyses.

### 6.1 Estimates and intervals

Every published binary proportion must report:

- numerator and denominator;
- point estimate;
- Wilson 95% confidence interval;
- number unreviewed;
- number unadjudicated.

### 6.2 Primary comparison

At the 90-day primary horizon, compare the full preregistered scored cohort with the synchronized random control using a **two-sided Fisher exact test** on breakout / non-breakout counts. The preregistered significance threshold is `alpha = 0.05`.

Report the absolute risk difference and risk ratio (where defined) alongside the p-value and confidence intervals. The p-value is not a substitute for effect size.

If the control cohort is larger than the scored cohort, Fisher's exact test still uses the full preregistered control counts. Do **not** plug the observed control rate into a one-sample binomial test as if that estimated rate were known without uncertainty.

### 6.3 Interpretation

- `p < 0.05` with a positive effect favors evidence of separation for that preregistered experiment; it does not by itself establish general predictive validity.
- `p >= 0.05` is a **null / inconclusive result**, not proof of equivalence.
- A negative effect is a negative result even if sampling uncertainty is wide.
- All outcomes — positive, negative, or inconclusive — receive equal publication prominence.

No ad-hoc confidence-interval-overlap rule is used to redefine significance after results are seen.

### 6.4 Missing adjudications

When any position is `unadjudicated`, report both:

1. **as-adjudicated:** unadjudicated cases excluded from the denominator;
2. **conservative:** unadjudicated cases counted as non-breakout.

Any headline analysis must use the conservative variant, with the as-adjudicated sensitivity analysis shown alongside it. `unreviewed` cases invalidate a completed headline analysis for that cohort until review is completed or the missingness is explicitly handled under a new preregistered protocol version.

### 6.5 Multiplicity

The 90-day full-cohort scored-vs-random comparison is the single primary confirmatory test for a v2 experiment. Precision@5, Precision@10, 30-day results, 180-day results, naive-baseline comparisons, and additional domains are secondary/exploratory unless separately preregistered before T0. They must not be cherry-picked to replace the primary result.

---

## 7. Artifact integrity and missing historical files

### 7.1 Recovery only, never reconstruction

An unpublished historical artifact may be published only if the original frozen file is recovered from an original local artifact or backup with defensible provenance. It must not be reconstructed from current or future API data and presented as the original.

### 7.2 Current historical classification

The five unpublished cohort member files — the legacy `0.1.5` cohort plus four v0.2.8 cohorts — have no public member artifact and no public pre-outcome SHA-256 commitment at v2 adoption time. Their member-level existence is therefore `existence-unverified from public evidence`.

Their historical metadata may remain visible for transparency, but they are ineligible for headline predictive-validity claims unless an original artifact is recovered with defensible provenance.

### 7.3 Immediate pre-outcome hash commitment

Before any outcome adjudication begins:

- the currently public distributed-training cohort must receive a published SHA-256 commitment over its exact `cohort.json` bytes;
- if any of the five unpublished original files is genuinely available locally, its exact SHA-256 should be published immediately with provenance;
- inability to produce a hash must not be disguised with a placeholder value or a reconstructed artifact.

A hash committed now proves byte-fixation no later than the commitment commit; it does **not** by itself prove the file existed at the earlier T0. Freeze-time provenance and snapshot linkage remain separate evidence.

### 7.4 Forward freeze-time commitment

Every new v2 cohort — scored or control — must publish at T0:

- the complete frozen cohort artifact;
- SHA-256 of the exact artifact bytes;
- source snapshot identifier;
- score / protocol / outcome-definition versions;
- sampling metadata where applicable.

A run that fails to publish the artifact and hash at freeze time is not eligible for the publicly verifiable benchmark set.

---

## 8. Reporting requirements

A result may be described as evidence relevant to predictive validity only when the applicable material is publicly inspectable together:

1. frozen scored cohort artifact;
2. eligible synchronized random-control artifact for a v2 headline claim;
3. artifact SHA-256 commitments;
4. governing protocol and adoption timing;
5. evaluation horizon and primary endpoint;
6. member-level adjudication evidence, including negative, unadjudicated, and unreviewed records;
7. naive baseline comparisons;
8. unique-person deduplication counts for any pooled statistic;
9. blinding and intervention disclosures;
10. statistical test, effect size, confidence intervals, and complete denominators.

Partial publication is not a benchmark result.

---

## 9. Failure prominence

This protocol does not certify that Ghost Score has predictive validity. It defines the minimum conditions under which a future result is interpretable.

A positive, negative, or statistically inconclusive result must be published with the **same prominence, artifact completeness, and methodological detail**. A failure to beat the random control or naive baselines is a legitimate result and must not be hidden, delayed selectively, or replaced by a more favorable horizon/domain after outcomes are known.

A null result means the experiment did not establish separation at its stated sample size; it does not prove the model and control are equivalent.

---

## 10. Forward implementation requirements

Protocol text is not a substitute for code enforcement. Before Ghost Talent makes a v2 headline predictive-validity claim, public benchmark tooling must implement and test:

- preservation of the pre-score discovery population required for random sampling;
- synchronized random-control generation with recorded seed and sampling metadata;
- blind adjudication packages that hide score, rank, recommendation, and model/control membership;
- validation of allowed outcome types, public evidence fields, and post-T0 timing;
- 90-day primary-endpoint evaluation;
- Fisher exact primary comparison with effect sizes and Wilson intervals;
- stable-subject deduplication for pooled metrics;
- SHA-256 generation and verification at freeze time;
- explicit exclusion of ineligible historical artifacts from headline aggregation;
- tests proving failed/incomplete runs cannot silently enter the eligible benchmark set.

---

## 11. Changelog

- **v2 (2026-09-08):** random-control requirement; domain-selection disclosure; blind adjudication and reliability review; primary 90-day full-cohort endpoint; preregistered Fisher exact comparison and uncertainty reporting; artifact hash commitments; cross-cohort deduplication; same-window replication warning; intervention disclosure; equal publication prominence for positive, negative, and inconclusive results. Corrected public registry to 20/120 inspectable positions overall (20/100 for v0.2.8).
- **v1 (2026-09-08):** frozen outcome rubric; aggregation/dedup rules; missing-artifact rules; frozen/publicly-inspectable/validated distinction.
