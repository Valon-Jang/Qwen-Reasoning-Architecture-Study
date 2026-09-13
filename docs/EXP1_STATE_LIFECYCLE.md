# Experiment 1 — State Lifecycle / Supersession

## Goal

Test whether a persistent reasoning state can safely replace current facts and retire stale derived conclusions instead of accumulating contradictions.

## v3.1 failure

The first state-update test failed the stop rule. After correcting C from `2h/cost2` to `5h/cost5`, both old and new path totals remained active, and both the previous selected-path inference and the new `no feasible path` inference remained current. State readback also duplicated records by re-ingesting existing identifiers as content.

This established two distinct defects:

- missing supersession / lifecycle semantics;
- non-idempotent state ingestion.

## v3.2 repair

The state representation was changed so stable semantic keys own one CURRENT value. Atomic facts and constraints are separated from derived path totals, decisions, and rejections. Updating an atomic fact refreshes or invalidates dependent derived state.

## Test sequence

### Baseline

Gold: `A→C→D`, total time 7, total cost 4.

Observed: PASS in one model call. State inspection showed A/B/C/D as atomic facts, hard limits as constraints, and path totals/decision only as inferences.

### Update 1

Change C from `2h/cost2` to `5h/cost5`.

Gold: neither candidate path satisfies both hard limits; current decision must become `No feasible path`.

Observed: PASS. Current state retained only C=5/5, A→C→D=10/7 and the new current decision. Old C=2/2, old 7/4 totals and prior A→C→D decision were not active.

### Update 2

Change B from `4h/cost4` to `1h/cost1`, retaining `b.irreversible=true`.

Gold: A→B→D = 6h / cost3 becomes the sole feasible current path.

Observed: PASS. Current state retained B=1/1, C=5/5, A→B→D=6/3 and the new current decision; prior B=4/4 and prior `No feasible path` conclusion were no longer active.

## Conclusion

**PASS — state lifecycle mechanics are technically viable.**

This experiment proves clean replacement and stale-inference removal under the tested sequence. It does not prove that persistent compressed state improves reasoning quality versus raw conversation. That question was deferred to Experiment 3.
