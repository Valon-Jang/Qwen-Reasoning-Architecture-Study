# Continuation Checkpoint

Date: 2026-09-13

## Research program

This research continues. The goal is not to train a new model, but to determine how far the same Qwen 3.5-33B can be improved by external reasoning architecture without adding unnecessary complexity, latency, tokens, or brittle state machinery.

Canonical repository:

- https://github.com/Valon-Jang/Qwen-Reasoning-Architecture-Study

## Completed evidence chain

- Exp1 v3.2 — State lifecycle / supersession: PASS.
- Exp2 v3.3 — Deterministic visible-numeric consistency: PASS.
- Exp3 — Full persistent-state HC vs Bare: HC_REGRESSES.
  - Bare 16/16
  - HC 14/16
- Exp4 — Subtractive ablation:
  - BARE 11/12
  - GUIDE 12/12
  - LITE 12/12
- Exp5 — Held-out confirmation:
  - BARE 16/16
  - GUIDE 15/16
  - MAX bundle 11/16
  - MAX format failures: 7

## Current interpretation

The strongest default candidate so far is the simplest architecture:

```text
RAW MULTI-TURN CONVERSATION
        ↓
      BARE
        ↓
only when a concrete failure signal exists
inject the smallest relevant reasoning aid
        ↓
use deterministic verification only where correctness is mechanically checkable
```

Do not promote persistent compressed reasoning state as the default reasoning substrate.

Do not claim that deterministic numeric verification is a general intelligence layer; it is a narrow correctness mechanism whose implementation works.

Do not promote always-on GUIDE yet. Its Exp4 advantage did not reproduce in Exp5.

Do not promote the current MAX bundle. It regressed product-level success, format stability, tokens, and latency.

## Critical interpretation boundary

Exp5 `MAX` was not a clean high-reasoning arm. Source inspection showed it mixed:

```text
GUIDE
+ Korean presentation style
+ AUTO-effort prompt guidance
```

Therefore Exp5 does **not** establish that stronger reasoning effort itself is harmful.

Future experiments must separate semantic correctness from format compliance.

## Next primary experiment

Run a clean:

```text
BARE
vs
GUIDE_HIGH
```

### GUIDE_HIGH

```text
BARE
+ the same short GUIDE used previously
+ explicit high-effort reasoning guidance
```

No Korean style/tone difference between arms.

### Controls

Keep matched:

- exact model ID
- endpoint / transport
- temperature
- case-order balancing
- raw multi-turn conversation policy
- output contract
- no persistent compressed state
- no critic / reviewer / swarm
- no client-side `max_tokens` cap

### Scoring

Record separately:

```text
semantic_pass
format_pass
case_pass
tokens
latency
model_calls
```

Decision rule:

- If semantic quality ties, BARE wins.
- Promote GUIDE_HIGH only for repeatable semantic gain without unacceptable format/token/latency regression.
- If GUIDE_HIGH helps only one failure family, convert that improvement into a selective trigger instead of an always-on layer.

## Research boundaries

Read before making broad claims:

- `docs/RESEARCH_SCOPE_AND_LIMITATIONS.md`
- `research/NEXT_EXPERIMENT.md`
- `research/CURRENT_CONCLUSION.md`

Do not generalize these results to all Qwen sizes/versions, all endpoints, all task distributions, or all reasoning prompts.

## Fresh-chat resume instruction

Use this exact message in a new chat:

> 큐웬 reasoning architecture 연구 이어서. GitHub Qwen-Reasoning-Architecture-Study와 최신 프로젝트 체크포인트 읽고, 다음 BARE vs GUIDE_HIGH 실험 설계부터 이어가자.
