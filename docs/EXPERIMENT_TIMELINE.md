# Experiment Timeline

## Research question

How much external reasoning structure improves Qwen 3.5-33B, and which layers should remain always-on versus conditional?

## v2.x — Benchmark infrastructure before architecture claims

Early Bare/Upgraded and Bare/Guarded/Reviewed runs were not trusted as quality evidence because the harness itself introduced confounds:

- evaluator separator sensitivity falsely rejected a correct answer;
- one benchmark objective was under-specified;
- a long-running benchmark process terminated before summary completion;
- a client-side `max_tokens=4096` cap caused `finish=length` and was initially at risk of being misread as a model/server limitation.

These failures led to durable per-arm checkpointing, explicit resume, tolerant deterministic scoring, and removal of client-side token ceilings.

## v3.1 — Persistent-state prototype

A first persistent reasoning-state design retained decision-relevant facts, constraints, and inferences. It could reconstruct follow-up comparisons without the original prompt, but state update testing exposed two defects:

1. stale and corrected values remained active simultaneously;
2. state inspection/re-ingestion could duplicate records.

A stop rule blocked further architecture expansion until lifecycle semantics were repaired.

## Experiment 1 — v3.2 State Lifecycle / Supersession

Semantic keys were introduced so one CURRENT value exists per stable state item. Dependent derived state is recomputed or invalidated when source facts change.

PASS sequence:

1. Baseline: A→C→D = 7h / cost4.
2. C corrected 2/2 → 5/5: no feasible path.
3. B corrected 4/4 → 1/1: A→B→D = 6h / cost3.

Old facts, stale totals, and superseded decisions were absent from CURRENT state after each update.

Interpretation: state lifecycle is technically viable. This did not yet prove that persistent compressed state improves reasoning versus Bare.

## Experiment 2 — v3.3 Visible Numeric Consistency

A narrow deterministic verifier was added for visible arithmetic only.

Verified behaviors:

- `4 vs 6, difference 1` → local patch to `difference 2`;
- correct `difference 2` remains unchanged;
- `2+4+3=8` → `EQUATION_MISMATCH`, expected 9;
- `6>7` → `FALSE_INEQUALITY`;
- `6<=7` → no issue.

Safe patches require zero extra model calls. Blocking numeric conflicts may use at most one focused correction call.

Interpretation: deterministic verification is a valid local mechanism, but its general always-on value remained unproven.

## Experiment 3 — Hard Bare vs Full HC

Full persistent-state HC was compared against Bare on 16 hard cases.

Result:

- Bare: 16/16, hard failures 0, calls 20, tokens 54,437.
- HC v3.3: 14/16, hard failures 2, calls 25, tokens 65,335.

HC failed `HC11_STATE_REPLACEMENT_DECISION` and `HC13_REJECTED_HYPOTHESIS_REVIVAL`; Bare passed both.

Interpretation: compressed persistent reasoning state can lose or preserve the wrong dependency information in harder multi-turn replacement/revival tasks. Persistent state was removed from the default architecture candidate.

## Experiment 4 — Subtractive Ablation

The architecture was reduced to raw multi-turn conversation with three arms:

- BARE: minimal baseline.
- GUIDE: BARE + short reasoning guidance.
- LITE: GUIDE + deterministic numeric verifier.

Result:

- BARE: 11/12, hard fail 1.
- GUIDE: 12/12, hard fail 0.
- LITE: 12/12, hard fail 0.

GUIDE used fewer tokens and had lower median latency than BARE in this run. LITE matched quality, but its verifier never activated.

Interpretation at the time: GUIDE became the minimal winner candidate; LITE provided no observed additional quality benefit.

## Experiment 5 — Held-out Confirmation

An independent held-out suite was run with 8 case types × 2 repeats × 3 arms.

Final result:

- BARE: 16/16, format failures 0, tokens 37,178, median 9,234.5 ms.
- GUIDE: 15/16, format failures 1, tokens 43,831, median 14,511.5 ms.
- MAX bundle: 11/16, format failures 7, tokens 71,582, median 34,419.5 ms.

The MAX arm was later source-audited and found to be a bundle of GUIDE + Korean style + AUTO-effort prompt guidance, not a pure high-reasoning arm.

Interpretation:

- GUIDE superiority did not reproduce.
- The current MAX bundle should not be promoted.
- Bare is now the strongest default baseline candidate.
- Future tests must separate semantic correctness, format compliance, style, and reasoning effort.

## Current research direction

Do not add more always-on layers by default. Test whether selective, failure-triggered reasoning guidance can retain Bare efficiency while preventing known failure modes.
