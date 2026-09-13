# Experiment 4 — Subtractive Ablation

## Goal

After Experiment 3 showed that full persistent-state HC regressed, identify the smallest surviving layer that can improve on Bare without the compressed-state failure mode.

## Arms

All arms use full raw multi-turn conversation. Persistent compressed state, critic, reviewer, swarm, web, and tool-evidence layers are excluded.

- `BARE`: minimal baseline.
- `GUIDE`: BARE + short reasoning guidance.
- `LITE`: GUIDE + deterministic visible-answer numeric consistency verification.

## Aggregate result

36/36 arms completed.

| Metric | BARE | GUIDE | LITE |
|---|---:|---:|---:|
| Cases | 12 | 12 | 12 |
| PASS | 11 | **12** | **12** |
| Hard failures | 1 | **0** | **0** |
| Model calls | 18 | 18 | 18 |
| Tokens | 54,927 | 51,576 | **46,927** |
| Median elapsed | 36,368 ms | **28,135 ms** | 39,797 ms |
| Avg calls / turn | 1.00 | 1.00 | 1.00 |
| Verifier patches | 0 | 0 | 0 |
| Corrections | 0 | 0 | 0 |

## Interpretation at the time

GUIDE became the minimal winner candidate:

- +1 case PASS over BARE;
- -1 hard failure;
- same model-call count;
- about 6.1% fewer tokens;
- about 22.6% lower median elapsed time in this run.

LITE matched GUIDE quality, but its deterministic verifier did not activate (`patches=0`, `corrections=0`). Therefore this run provided no observed quality benefit from the verifier over GUIDE.

## Decision

Do not promote GUIDE yet from a single ablation set. Run an independent held-out confirmation focused on the same failure-mode family. If the GUIDE advantage reproduces, consider it for the default minimal layer; otherwise retain Bare as the default baseline.
