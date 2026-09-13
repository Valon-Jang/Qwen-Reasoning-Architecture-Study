# Current Conclusion

## Strongest supported default

The strongest default architecture observed so far is:

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

## Why this is the current winner

### Persistent compressed reasoning state

Technically viable at the lifecycle level, but it regressed hard multi-turn reasoning in Experiment 3. It should not be the default reasoning substrate.

### Always-on GUIDE

Promising in Experiment 4, but the advantage did not reproduce in the independent held-out confirmation. Current evidence does not support promoting GUIDE as a universal default.

### Deterministic numeric verifier

The mechanism itself is validated, but its always-on general reasoning value is not established. It should be treated as a narrow safety/correctness tool, not an intelligence layer.

### MAX bundle

The current MAX bundle strongly regressed product-level success, format reliability, token use, and latency. It should not be promoted.

This does not prove that high reasoning effort is inherently harmful because the tested MAX arm also included style/output instructions and used AUTO-effort prompt guidance rather than a clean high-only condition.

## Broader hypothesis

The experiments increasingly support a **selective augmentation** hypothesis:

> The model should remain close to its unmodified reasoning distribution until a specific observable failure mode justifies adding a narrow intervention.

This is different from adding a permanent chain of reasoning rules, persistent compressed state, critic loops, or reviewer layers to every turn.

## What is considered established vs not established

### Established in this program

- State supersession can be implemented cleanly.
- Visible deterministic numeric consistency can be verified locally.
- Full persistent-state HC can regress relative to Bare.
- GUIDE can help on one benchmark but does not yet show general reproducible superiority.
- The current MAX bundle regresses and should not be promoted.
- Durable per-arm checkpoint/resume can recover benchmark progress across transient transport failures.

### Not established

- That Bare is universally optimal for all Qwen tasks.
- That higher reasoning effort itself is harmful.
- That GUIDE is useless.
- That deterministic verification never helps general quality.
- That the observed results transfer to other Qwen sizes, versions, endpoints, or task distributions.

## Current design principle

> **Do not add an always-on reasoning layer unless it repeatedly beats Bare on independent held-out tests under matched conditions.**
