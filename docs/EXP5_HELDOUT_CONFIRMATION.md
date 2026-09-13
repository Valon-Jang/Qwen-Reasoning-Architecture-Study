# Experiment 5 — Held-out Confirmation

## Goal

Test whether the GUIDE advantage observed in Experiment 4 reproduces on a fresh held-out set, and compare the current MAX-like bundle under the same transport/model conditions.

Benchmark: `Q35_DIRECT_RC1_HELDOUT_8_V1`

Design:

- 8 held-out case types;
- 2 repeats;
- 3 arms;
- same model, same transport, same temperature;
- completed turns checkpointed and reused on explicit resume;
- transport failures not scored as model-quality failures.

## Final result

```json
{
  "benchmark": "Q35_DIRECT_RC1_HELDOUT_8_V1",
  "repeats": 2,
  "complete": true,
  "decision": "MAX_REGRESSION_DO_NOT_PROMOTE",
  "unknown_or_failed_requests": []
}
```

| Metric | BARE | GUIDE | MAX bundle |
|---|---:|---:|---:|
| Case runs | 16 | 16 | 16 |
| Case PASS | **16** | 15 | 11 |
| Format failures | **0** | 1 | 7 |
| Model calls | 22 | 22 | 22 |
| Total tokens | **37,178** | 43,831 | 71,582 |
| Median case elapsed | **9,234.5 ms** | 14,511.5 ms | 34,419.5 ms |

## GUIDE result

GUIDE did not reproduce its Exp4 advantage.

Relative to BARE in this run:

- one fewer product-level PASS;
- one format failure vs zero;
- about 17.9% more tokens;
- about 57% higher median latency.

Exp4 and Exp5 raw case counts are therefore:

```text
Exp4: BARE 11/12, GUIDE 12/12
Exp5: BARE 16/16, GUIDE 15/16

Raw combined counts:
BARE  27/28
GUIDE 27/28
```

These counts are not treated as a formal pooled statistical estimate, but they show that the Exp4 GUIDE advantage did not replicate.

## MAX interpretation boundary

Source inspection after the run showed that `MAX` is not a pure high-reasoning arm. It is effectively:

```text
GUIDE
+ Korean presentation/style instructions
+ AUTO-effort prompt guidance
```

The benchmark call path did not invoke the separate `high` effort wording.

Therefore the valid conclusion is:

> **The current MAX bundle regresses and should not be promoted.**

The experiment does **not** establish that high reasoning effort itself reduces semantic reasoning quality.

## Scoring boundary

The current summary's `case_pass` combines semantic correctness and format compliance. Format failure can therefore lower product-level PASS even if an underlying choice was semantically correct.

Future comparisons must report at least:

- `semantic_pass`;
- `format_pass`;
- `case_pass`;
- tokens;
- latency.

## Runner result

Several transient `WINHTTP_TRANSPORT_FAILURE` events occurred during the run, but successful arm results were checkpointed individually and the run eventually completed with:

```text
complete=true
unknown_or_failed_requests=[]
```

This validates the checkpoint/resume design for this benchmark workflow.

## Decision

- Do not promote the current MAX bundle.
- Do not promote always-on GUIDE as a general default from current evidence.
- Retain BARE as the strongest default baseline candidate.
- Next clean reasoning-effort test should remove style confounds and separate semantic from format scoring.
