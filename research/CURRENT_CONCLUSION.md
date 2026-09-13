# Current Conclusion

> **Corrected 2026-09-13:** [Exp3 raw-output regrading](../docs/EXP3_BARE_VS_HC.md) finds a logged-decision semantic tie (16/16 each). HC's three missing FINAL markers cause the unchanged 14/16 contract-inclusive score. The previous reasoning/dependency-loss explanation is withdrawn. This correction supersedes inconsistent historical wording without changing original logs or other experiments.

## Retained minimal default candidate

The retained default candidate is:

```text
RAW MULTI-TURN CONVERSATION
        ↓
      BARE
        ↓
only when a concrete failure signal is detected
inject the smallest relevant reasoning aid
        ↓
use deterministic verification only where correctness is mechanically checkable
```

This is an engineering baseline and selective-augmentation hypothesis, not proof that the whole selective policy has beaten matched alternatives.

## Why added default layers are not promoted

### Persistent compressed reasoning state

Technically viable at the lifecycle level. Exp3 now shows a target-decision semantic tie with Bare, not observed semantic degradation. The tested HC bundle still has three FINAL-marker omissions across two cases, five additional calls and 10,898 additional total tokens. Do not promote this implementation without fixing and revalidating its contract/cost behavior. Do not reject persistent state generally on the basis of a withdrawn reasoning-loss claim.

### Always-on GUIDE

Promising in Experiment 4, but the advantage did not reproduce in the independent held-out confirmation. Current evidence does not support promoting GUIDE as a universal default.

### Deterministic numeric verifier

The mechanism itself is validated, but its always-on general reasoning value is not established. It should be treated as a narrow safety/correctness tool, not an intelligence layer.

### MAX bundle

The current MAX bundle regressed recorded product-level success and format reliability, used more tokens and showed higher descriptive latency in Exp5. It should not be promoted.

This does not prove that high reasoning effort is inherently harmful because the tested MAX arm also included style/output instructions and used AUTO-effort prompt guidance rather than a clean high-only condition.

## Broader hypothesis

A **selective augmentation** hypothesis remains worth testing:

> Preserve the model's useful baseline behavior and add a narrow intervention only when its observable benefit justifies its total cost.

This is different from adding a permanent chain of reasoning rules, persistent compressed state, critic loops, or reviewer layers to every turn. Exp3 does not prove the hypothesis: selective retrieval or selective intervention was not an arm there.

## What is considered established vs not established

### Observed or validated within the stated program scope

- State supersession can be implemented cleanly on the tested sequences.
- Visible deterministic numeric consistency can be verified locally.
- Exp3 target-decision semantics tie; the tested HC bundle has worse contract-inclusive outcomes and higher aggregate token/call costs.
- GUIDE can help on one benchmark but does not yet show general reproducible superiority.
- The current MAX bundle regresses on the recorded product-level test and should not be promoted.
- Durable per-arm checkpoint/resume can recover benchmark progress across transient transport failures.

### Not established

- That Bare is universally optimal for all Qwen tasks.
- That Exp3 showed semantic reasoning failure or dependency loss from compression.
- That higher reasoning effort itself is harmful.
- That GUIDE is useless.
- That deterministic verification never helps general quality.
- That three Exp3 marker omissions and Exp5 format failures establish same-treatment replication or a universal causal effect of structure.
- That completion-token counts measure internal reasoning, or prompt-token growth proves exact historical payload contents.
- That the observed results transfer to other Qwen sizes, versions, endpoints, or task distributions.

## Current design principle

> **Do not add an always-on reasoning layer unless it repeatedly beats Bare under matched conditions on separately defined semantic, contract, and cost measures.**

Continue the independently recorded [source-applicability investigation](SOURCE_CONFLICT_CHECKPOINT_20260913.md). Its later small-model system results are not retroactively invalidated by correcting the Exp3 interpretation, and they are not proof of Max-like equivalence.
