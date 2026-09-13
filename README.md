# Qwen Reasoning Architecture Study

Controlled experiments on reasoning guidance, persistent state, deterministic verification, and minimal reasoning architecture for Qwen 3.5-33B.

> **Exp3 correction — 2026-09-13:** Original contract-inclusive results remain BARE 16/16 and HC 14/16. Retrospective review of all 40 visible turn outputs finds a logged-decision semantic tie, 16/16 cases per arm: HC omitted FINAL on three turns across two cases while stating the correct decisions. The earlier state-replacement/revival reasoning-loss explanation is withdrawn. Read the [corrected Exp3 report](docs/EXP3_BARE_VS_HC.md). No model was rerun.

> Before interpreting the results, read **[Research Scope, Premises, Rationale, and Limitations](docs/RESEARCH_SCOPE_AND_LIMITATIONS.md)**. It defines why the experiments were run, what BARE means, the deployment and benchmark assumptions, the known confounds, and the claims these results do **not** support. Older Exp3 semantic-loss wording in historical records is superseded by the correction above.

## Current conclusion

The retained minimal default candidate is:

> **Preserve raw conversation, keep the base model minimally constrained, and add reasoning structure only when a specific failure signal justifies it.**

The experiments started from the hypothesis that more external reasoning structure would improve Qwen. The tested always-on bundles have not demonstrated a reproducible decision-semantic advantage; this is not proof that added structure inherently damages reasoning.

- Persistent compressed reasoning state was technically made correct at the lifecycle level. Exp3's corrected decision semantics tie Bare; the tested HC bundle instead regresses contract-inclusive success and increases calls/total tokens.
- A deterministic numeric verifier works correctly, but has not shown a general quality gain when always attached.
- A short reasoning GUIDE won one subtractive ablation, but the gain did not reproduce on an independent held-out confirmation set.
- The current MAX bundle regressed product-level success and format stability, used more tokens, and had higher observed latency in Exp5. It was not a clean high-reasoning-only arm, so it should not be interpreted as evidence that deeper reasoning itself is harmful or as a controlled speed result.
- Bare Qwen remains the minimal default baseline; the selective-intervention policy is a hypothesis requiring its own matched validation.

## Experiment sequence

| Stage | Question | Result | Decision |
|---|---|---|---|
| v2.x harness work | Can Bare/Guarded/Reviewed be compared reliably? | Early runs invalidated by evaluator, runner, and client token-cap defects | Fix benchmark infrastructure first |
| Exp1 v3.2 | Can persistent state replace facts and retire stale inferences correctly? | PASS | Lifecycle mechanism is technically viable |
| Exp2 v3.3 | Can visible arithmetic inconsistencies be corrected deterministically? | PASS | Narrow deterministic verifier is viable |
| Exp3 | Does full persistent-state HC improve over Bare? | Contract-inclusive Bare 16/16 vs HC 14/16; post-hoc decision semantics 16/16 each | No semantic gain; contract/cost regression; no promotion |
| Exp4 | Which minimal layer survives subtraction? | Bare 11/12, GUIDE 12/12, LITE 12/12 | GUIDE became a minimal winner candidate |
| Exp5 held-out | Does GUIDE superiority reproduce, and does MAX help? | Bare 16/16, GUIDE 15/16, MAX 11/16 | GUIDE superiority not reproduced; MAX bundle rejected |

## Key quantitative results

### Experiment 3 — Hard Bare vs HC

| Metric | Bare | HC v3.3 |
|---|---:|---:|
| Original contract-inclusive case PASS | **16/16** | 14/16 |
| Post-hoc logged-decision semantic cases | 16/16 | 16/16 |
| Post-hoc logged-decision semantic turns | 20/20 | 20/20 |
| FINAL-marker omission turns | **0/20** | 3/20 |
| Legacy scorer hard-failure cases | **0** | 2 |
| Model calls | **20** | 25 |
| Tokens | **54,437** | 65,335 |
| Avg calls / turn | **1.00** | 1.25 |
| Descriptive median elapsed only | 45,946 ms | 30,463 ms |

The two original HC failed cases were `HC11_STATE_REPLACEMENT_DECISION` and `HC13_REJECTED_HYPOTHESIS_REVIVAL`. All three affected turn outputs state the correct decision but omit FINAL. Their original machine-contract failures are preserved; they are not evidence of failed replacement/revival reasoning. The audit scores target decisions relative to logged gold, not every prose assertion or the completeness of hidden state. Full historical scorer and execution-hash verification remain unavailable.

### Experiment 4 — Subtractive Ablation

| Metric | BARE | GUIDE | LITE |
|---|---:|---:|---:|
| Case PASS | 11/12 | **12/12** | **12/12** |
| Hard failures | 1 | **0** | **0** |
| Model calls | 18 | 18 | 18 |
| Tokens | 54,927 | 51,576 | **46,927** |
| Median elapsed | 36,368 ms | **28,135 ms** | 39,797 ms |
| Verifier patches | 0 | 0 | 0 |

GUIDE was the winner candidate in this experiment. LITE matched quality, but its verifier never activated, so the experiment provided no observed quality benefit from the verifier over GUIDE. Exp3's corrected rationale does not change these independently observed Exp4 results.

### Experiment 5 — Held-out confirmation

Benchmark: `Q35_DIRECT_RC1_HELDOUT_8_V1`  
8 held-out cases × 2 repeats × 3 arms.

| Metric | BARE | GUIDE | MAX bundle |
|---|---:|---:|---:|
| Case PASS | **16/16** | 15/16 | 11/16 |
| Reported format failures | **0** | 1 | 7 |
| Model calls | 22 | 22 | 22 |
| Tokens | **37,178** | 43,831 | 71,582 |
| Descriptive median elapsed | 9,234.5 ms | 14,511.5 ms | 34,419.5 ms |

Decision: `MAX_REGRESSION_DO_NOT_PROMOTE`

The final run completed with `unknown_or_failed_requests=[]`; transient WinHTTP failures were recovered through durable checkpoint/resume.

## Important interpretation boundary

The Exp5 arm named `MAX` is not a pure high-reasoning arm. Source inspection showed that it is effectively:

```text
GUIDE + Korean style instructions + AUTO-effort prompt guidance
```

Therefore the correct claim is:

> **The current MAX bundle regresses on the recorded product-level comparison and should not be promoted.**

It is not valid to claim from this experiment alone that stronger reasoning effort itself harms Qwen.

Also, product-level `case_pass` includes format compliance. Future experiments should report semantic correctness and format compliance separately. Exp3 and Exp5 provide a same-direction contract-risk signal under different treatments, not same-treatment replication or a causal law. Their format-failure counting units must not be pooled without raw-scoring verification.

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

This is a shift from **always-on reasoning augmentation** toward **failure-triggered selective augmentation**, not a claim that Exp3 demonstrated semantic degradation from compressed state.

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

For the full methodological boundary, including small sample size, targeted benchmark design, internal deployment effects, limited stochastic replication, transport/token accounting limits, MAX confounding, semantic/format separation, and incomplete external reproducibility, see **[RESEARCH_SCOPE_AND_LIMITATIONS.md](docs/RESEARCH_SCOPE_AND_LIMITATIONS.md)**. Its historical Exp3 interpretation is superseded by the linked 2026-09-13 raw-output correction.
