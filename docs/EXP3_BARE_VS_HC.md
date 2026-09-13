# Experiment 3 — Hard Bare vs Full HC

## Goal

Determine whether the accumulated Human Intelligence architecture — including persistent compressed reasoning state and its lifecycle machinery — actually improves Qwen 3.5-33B over a Bare baseline on hard non-ceiling cases.

## Result

| Metric | Bare | HC v3.3 |
|---|---:|---:|
| Case PASS | **16/16** | 14/16 |
| Hard failures | **0** | 2 |
| Model calls | **20** | 25 |
| Tokens | **54,437** | 65,335 |
| Median elapsed | 45,946 ms | **30,463 ms** |
| Avg calls / turn | **1.00** | 1.25 |

Decision: `HC_REGRESSES`

## Hard failures

HC failed:

- `HC11_STATE_REPLACEMENT_DECISION`
- `HC13_REJECTED_HYPOTHESIS_REVIVAL`

Bare passed both. `HC12_STALE_INFERENCE_INVALIDATION` passed on both arms.

## Interpretation

Experiment 1 proved that explicit state supersession can work on a controlled sequence. Experiment 3 showed that this is not enough to establish an intelligence improvement.

The persistent compressed state can still lose or preserve the wrong dependency information in harder multi-turn replacement/revival tasks. Compression therefore introduced an architectural failure mode that raw conversation avoided in this benchmark.

## Decision

- Do not promote the persistent-state HC as a general intelligence improvement.
- Do not add critic, reviewer, swarm, or tool-evidence layers to compensate before isolating the failing architecture.
- Run subtractive ablation using raw multi-turn conversation and progressively fewer always-on layers.
