# Contributing to Ghost Talent

Ghost Talent is an open-source emerging AI talent intelligence project. Contributions should improve discovery quality, evidence quality, reproducibility, or historical evaluation.

## Useful contributions

Good areas to work on include:

- new public technical evidence sources
- stronger GitHub and research identity resolution
- source-status and degradation reporting
- score-history and Rising Fast detection
- benchmark design and breakout definitions
- reproducible backtests
- documented false positives / false negatives
- contribution-quality improvements
- performance and caching improvements
- tests for scoring and snapshot integrity

## Contribution principles

1. **Evidence first.** Concrete technical claims should point back to public evidence.
2. **Uncertainty stays uncertainty.** Do not force identity matches or fabricate missing evidence.
3. **No sensitive-attribute ranking.** Do not infer or rank on race, ethnicity, religion, health, political beliefs, sexual orientation, or similar sensitive traits.
4. **No future leakage.** Historical work may only use evidence observable at or before its `as_of_date`.
5. **Keep scoring inspectable.** Material scoring changes need a rationale, tests, and a new `score_version` when semantics change.
6. **Keep scope focused.** Prefer small, reviewable pull requests over broad unrelated refactors.
7. **Never commit secrets.** API tokens and local `.env` files must remain local.

## Pull request checklist

A useful PR should normally include:

- a clear problem statement
- the smallest implementation that proves the change
- tests or a minimal reproducible example where applicable
- any methodology impact called out explicitly
- no unrelated cleanup or formatting churn

If a change modifies Ghost Score, Ghost Radar, evidence semantics, historical snapshots, or benchmark definitions, explain how old and new results differ.

## Good first contributions

If you are new to the project, useful starting points include:

- expose GitHub/OpenAlex source status in the API and UI
- add tests for rate-limit degradation paths
- improve evidence `subject_id` consistency
- add snapshot browsing utilities
- document a scoring failure case with public evidence

Check the open issues for scoped tasks.

## Research and benchmark contributions

Benchmark contributions are especially welcome. A benchmark proposal should define the cohort, `as_of_date`, outcome definition, evaluation horizon, metrics, and leakage controls before reporting results.

Wins and misses must both be retained.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python -m unittest discover -s tests
```

On macOS, `./start.command` provides the local product experience.

## Discussion

Open an issue when a proposal changes methodology, scoring assumptions, evidence policy, or benchmark definitions. Concrete counterexamples are more valuable than generic feature requests.