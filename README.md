# Qwen Reasoning Architecture Study

Controlled experiments on reasoning guidance, persistent state, deterministic verification, and minimal reasoning architecture for Qwen 3.5-33B.

> Before interpreting the results, read **[Research Scope, Premises, Rationale, and Limitations](docs/RESEARCH_SCOPE_AND_LIMITATIONS.md)**. It defines why the experiments were run, what BARE means, the deployment and benchmark assumptions, the known confounds, and the claims these results do **not** support.

## Current conclusion

The strongest default architecture observed so far is the simplest one:

> **Preserve raw conversation, keep the base model minimally constrained, and add reasoning structure only when a specific failure signal justifies it.**

The experiments started from the hypothesis that more external reasoning structure would improve Qwen. The results progressively pushed in the opposite direction.

- Persistent compressed reasoning state was technically made correct at the lifecycle level, but regressed hard multi-turn reasoning versus Bare.
- A deterministic numeric verifier works correctly, but has not shown a general quality gain when always attached.
- A short reasoning GUIDE won one subtractive ablation, but the gain did not reproduce on an independent held-out confirmation set.
- The current MAX bundle strongly regressed product-level success, format stability, token use, and latency. It was not a clean high-reasoning-only arm, so it should not be interpreted as evidence that deeper reasoning itself is harmful.
- Bare Qwen is currently the strongest default baseline across the completed controlled experiments.

## Experiment sequence

| Stage | Question | Result | Decision |
|---|---|---|---|
| v2.x harness work | Can Bare/Guarded/Reviewed be compared reliably? | Early runs invalidated by evaluator, runner, and client token-cap defects | Fix benchmark infrastructure first |
| Exp1 v3.2 | Can persistent state replace facts and retire stale inferences correctly? | PASS | Lifecycle mechanism is technically viable |
| Exp2 v3.3 | Can visible arithmetic inconsistencies be corrected deterministically? | PASS | Narrow deterministic verifier is viable |
| Exp3 | Does full persistent-state HC improve over Bare? | Bare 16/16 vs HC 14/16 | Do not promote persistent compressed HC |
| Exp4 | Which minimal layer survives subtraction? | Bare 11/12, GUIDE 12/12, LITE 12/12 | GUIDE became a minimal winner candidate |
| Exp5 held-out | Does GUIDE superiority reproduce, and does MAX help? | Bare 16/16, GUIDE 15/16, MAX 11/16 | GUIDE superiority not reproduced; MAX bundle rejected |

## Key quantitative results

### Experiment 3 — Hard Bare vs HC

| Metric | Bare | HC v3.3 |
|---|---:|---:|
| Case PASS | **16/16** | 14/16 |
| Hard failures | **0** | 2 |
| Model calls | **20** | 25 |
| Tokens | **54,437** | 65,335 |
| Avg calls / turn | **1.00** | 1.25 |
| Median elapsed | 45,946 ms | **30,463 ms** |

Observed HC hard failures:

- `HC11_STATE_REPLACEMENT_DECISION`
- `HC13_REJECTED_HYPOTHESIS_REVIVAL`

### Experiment 4 — Subtractive Ablation

| Metric | BARE | GUIDE | LITE |
|---|---:|---:|---:|
| Case PASS | 11/12 | **12/12** | **12/12** |
| Hard failures | 1 | **0** | **0** |
| Model calls | 18 | 18 | 18 |
| Tokens | 54,927 | 51,576 | **46,927** |
| Median elapsed | 36,368 ms | **28,135 ms** | 39,797 ms |
| Verifier patches | 0 | 0 | 0 |

GUIDE was the winner candidate in this experiment. LITE matched quality, but its verifier never activated, so the experiment provided no observed quality benefit from the verifier over GUIDE.

### Experiment 5 — Held-out confirmation

Benchmark: `Q35_DIRECT_RC1_HELDOUT_8_V1`  
8 held-out cases × 2 repeats × 3 arms.

| Metric | BARE | GUIDE | MAX bundle |
|---|---:|---:|---:|
| Case PASS | **16/16** | 15/16 | 11/16 |
| Format failures | **0** | 1 | 7 |
| Model calls | 22 | 22 | 22 |
| Tokens | **37,178** | 43,831 | 71,582 |
| Median elapsed | **9,234.5 ms** | 14,511.5 ms | 34,419.5 ms |

Decision: `MAX_REGRESSION_DO_NOT_PROMOTE`

The final run completed with `unknown_or_failed_requests=[]`; transient WinHTTP failures were recovered through durable checkpoint/resume.

## Important interpretation boundary

The Exp5 arm named `MAX` is not a pure high-reasoning arm. Source inspection showed that it is effectively:

```text
GUIDE + Korean style instructions + AUTO-effort prompt guidance
```

Therefore the correct claim is:

> **The current MAX bundle regresses and should not be promoted.**

It is not valid to claim from this experiment alone that stronger reasoning effort itself harms Qwen.

Also, product-level `case_pass` includes format compliance. Future experiments should report semantic correctness and format compliance separately.

## Combined signal from Exp4 + Exp5

These two sets are not pooled as a formal statistical estimate, but their raw case counts are informative:

```text
Exp4: BARE 11/12, GUIDE 12/12
Exp5: BARE 16/16, GUIDE 15/16

Raw combined counts:
BARE  27/28
GUIDE 27/28
```

The GUIDE advantage seen in Exp4 did not reproduce on the held-out set. There is currently no evidence that always-on GUIDE is a general improvement over Bare.

## Current architecture hypothesis

```text
RAW MULTI-TURN CONVERSATION
        ↓
      BARE
        ↓
only when a failure signal is detected
inject the smallest relevant reasoning rule
        ↓
use deterministic verification only for facts that are safely checkable
```

This is a shift from **always-on reasoning augmentation** toward **failure-triggered selective augmentation**.

## Repository map

```text
README.md
├─ docs/
│  ├─ RESEARCH_SCOPE_AND_LIMITATIONS.md
│  ├─ EXPERIMENT_TIMELINE.md
│  ├─ EXP1_STATE_LIFECYCLE.md
│  ├─ EXP2_OUTPUT_CONSISTENCY.md
│  ├─ EXP3_BARE_VS_HC.md
│  ├─ EXP4_SUBTRACTIVE_ABLATION.md
│  └─ EXP5_HELDOUT_CONFIRMATION.md
├─ results/
│  ├─ exp3_summary.json
│  ├─ exp4_summary.json
│  └─ exp5_heldout_summary.json
└─ research/
   ├─ CURRENT_CONCLUSION.md
   └─ NEXT_EXPERIMENT.md
```

## Research boundary

These results apply to the tested Qwen 3.5-33B deployment, prompts, harnesses, and benchmark cases. They do not establish a general law about all Qwen models, all reasoning prompts, or all agent systems.

For the full methodological boundary, including small sample size, targeted benchmark design, internal deployment effects, limited stochastic replication, transport/token accounting limits, MAX confounding, semantic/format separation, and incomplete external reproducibility, see **[RESEARCH_SCOPE_AND_LIMITATIONS.md](docs/RESEARCH_SCOPE_AND_LIMITATIONS.md)**.
