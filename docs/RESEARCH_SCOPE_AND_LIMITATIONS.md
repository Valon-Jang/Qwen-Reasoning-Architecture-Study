# Research Scope, Premises, Rationale, and Limitations

This document defines what this research program is trying to learn, the assumptions under which the experiments were run, why each experiment was necessary, and what the current results do **not** justify claiming.

## Why this research exists

The original question was not whether a larger or newer model is better. The working question was narrower:

> **How far can the same Qwen 3.5-33B deployment be improved by changing the reasoning architecture around it?**

The model weights were kept unchanged. The research changed prompt structure, state handling, deterministic verification, output contracts, and controller behavior.

The initial hypothesis was that more external reasoning structure could improve reliability. The experiments progressively became subtractive: a layer survives only if it beats a simpler baseline under controlled tests.

## Core premises

### Same base model, different surrounding architecture

The experiments concern a tested Qwen 3.5-33B deployment through an internal OpenAI-compatible endpoint. They do not modify model weights.

### BARE is the research baseline, not a universal vendor-pure condition

`BARE` is the minimal baseline used by this program. In the later QWEN35MAX comparison it was reconstructed from the Exp4 raw-API baseline prompt. Therefore the supported wording is:

> BARE outperformed the tested augmented arms under this harness.

not:

> Unmodified Qwen universally outperforms all prompting.

### Product success and semantic reasoning are different

A useful agent must reach the right answer and obey the required output/tool contract. These should be measured separately. Experiment 5 still partially mixed format compliance into `case_pass`; the next experiment explicitly separates `semantic_pass` and `format_pass`.

### Simpler wins ties

If an added layer does not produce a repeatable quality advantage, prefer the simpler architecture because added layers also add tokens, latency, state complexity, and new failure modes.

## Why the experiments were run in this order

### Phase 0 — Fix the benchmark first

Early v2.x comparisons exposed evaluator defects, an under-specified case, runner termination, and an artificial client-side `max_tokens=4096` ceiling. These failures led to durable checkpoint/resume, explicit transport-failure classification, tolerant scoring, and removal of the client token cap before later architecture claims.

### Experiment 1 — State lifecycle

Persistent state cannot help if corrected facts coexist with stale facts or old conclusions survive after their premises change. Experiment 1 therefore tested replacement, invalidation, and current-state lifecycle only. It did not test whether persistent state was smarter than Bare.

### Experiment 2 — Deterministic numeric consistency

A real output showed values 4 and 6 while describing the difference as 1. Because visible arithmetic is mechanically checkable, Experiment 2 tested whether such errors could be corrected without another model call. This validated a narrow mechanism, not a general intelligence upgrade.

### Experiment 3 — Full HC vs Bare

After lifecycle and numeric-verification components worked individually, the full persistent-state HC faced the actual promotion gate. It lost 14/16 to Bare 16/16, invalidating the assumption that a technically correct compressed state layer is automatically a better reasoning substrate.

### Experiment 4 — Subtractive ablation

Instead of adding more complexity, persistent compressed state was removed and raw multi-turn conversation restored. BARE, GUIDE, and LITE were compared. GUIDE and LITE reached 12/12 versus BARE 11/12, making GUIDE a candidate rather than a final winner.

### Experiment 5 — Held-out confirmation

A fresh held-out suite tested whether GUIDE's advantage reproduced. It did not: BARE 16/16, GUIDE 15/16. The `MAX` arm later proved to be a bundle of GUIDE + Korean presentation style + AUTO-effort prompt guidance, so its regression is valid for that bundle but cannot isolate pure high-reasoning effort.

## What current evidence supports

- state supersession can be implemented cleanly;
- visible deterministic numeric checks can work locally;
- full persistent compressed HC can regress against Bare;
- GUIDE can help on one benchmark but has not shown reproducible general superiority;
- the tested MAX bundle regresses strongly and should not be promoted;
- checkpoint/resume can preserve completed benchmark evidence across transient transport failures;
- the strongest current default candidate is raw multi-turn conversation + minimal BARE prompt, with narrow augmentation only when justified.

## Major limitations

### Small sample sizes

The completed hard comparisons are small-N engineering studies: Exp3 used 16 hard cases, Exp4 used 12 cases, and Exp5 used 8 held-out case types × 2 repeats. No claim of statistical significance is made.

### Failure-mode-targeted benchmark distribution

Many cases were deliberately designed around observed failure modes such as simultaneous constraints, unsupported inference, state replacement, stale inference, rejected-hypothesis revival, arithmetic, causal confounding, and data/instruction boundaries. This is useful for stress testing but is not a random sample of real-world tasks.

### Held-out is not an external blind benchmark

Exp5 used fresh non-identical cases, but they were built from the same general failure-mode families. It is a held-out confirmation within this program, not a third-party independent benchmark.

### Limited stochastic replication

Exp5 used only two repeats per case type; earlier experiments had even less full-suite replication. One-case differences are engineering evidence, not universal probability estimates.

### Internal deployment boundary

The tested Qwen 3.5-33B runs behind an internal OpenAI-compatible endpoint. Serving stack, quantization, scheduler, gateway, and inference settings may differ from other Qwen deployments. Results do not automatically transfer to other Qwen sizes, later versions, public endpoints, or other model families.

### Cross-experiment latency is not a fixed hardware benchmark

Within one matched experiment, latency is useful as a relative operational metric. Across Exp3/Exp4/Exp5, server load, transport state, harness version, context length, and network conditions differ enough that medians should not be treated as a controlled hardware benchmark.

### Token accounting and transport failures

Completed-call token totals are recorded. Failed transport attempts may have consumed server-side tokens that were never returned, so real infrastructure usage during failures can be undercounted.

### Exp5 MAX is confounded

MAX combined GUIDE, Korean style/output instructions, and AUTO-effort guidance. The experiment proves the tested bundle regressed. It does not prove high reasoning effort itself is harmful.

### Exp5 format and semantics are not fully separated

`case_pass` includes format compliance. MAX had seven format failures. Without recovering a semantic score from every malformed answer, 11/16 cannot be interpreted as pure reasoning correctness.

### LITE verifier did not activate in Exp4

LITE matched GUIDE at 12/12 but recorded zero patches and zero corrections. Exp4 therefore gives no evidence that the verifier caused a quality gain.

### Mechanism PASS is not intelligence PASS

Exp1 and Exp2 validated mechanisms. They should not be cited as proof that HC was smarter than Bare. Exp3 was the first direct promotion test, and HC lost.

### Persistent-state diagnosis is architectural, not microscopic

Exp3 directly observed replacement/revival failures, but hidden model reasoning is not observable. The interpretation that compressed state lost or preserved the wrong dependency information fits the evidence but is not a proof about internal chain-of-thought.

### No chain-of-thought claim

The research evaluates observable inputs, outputs, state transitions, harness behavior, and metrics. It does not claim access to private model chain-of-thought.

### Production tool capability is separate

Reasoning benchmark quality does not prove Blender, FreeCAD, PowerPoint, HyperFrames, file tools, or other production integrations are reliable. Those require independent end-to-end tests.

### Reproducibility is currently partial

The repository preserves summaries and interpretation, but not yet every raw model response, intermediate checkpoint, or exact historical harness artifact. It is a research record, not yet a fully self-contained external reproduction package.

Future archival work should preserve, when safe and non-sensitive: sanitized prompts, case definitions, scoring code, raw per-case outputs, exposed seed/temperature/request settings, harness version/hash, and sanitized result logs. Internal endpoints, credentials, company data, and sensitive deployment details must remain excluded.

## Generalization boundary

The strongest justified current claim is:

> **For the tested Qwen 3.5-33B deployment and these controlled benchmark families, always-on additional reasoning structure has not shown a reproducible advantage over the minimal BARE baseline; the most promising direction is selective augmentation triggered by specific failure signals.**

The following claims are not justified:

- Bare prompting is universally optimal;
- more reasoning always hurts;
- persistent memory is generally harmful;
- verification layers are unnecessary;
- GUIDE never helps;
- the results transfer unchanged to other models or Qwen versions.

## Promotion standard going forward

A new always-on layer should not become the default unless it:

1. beats BARE on semantic quality under matched conditions;
2. repeats the gain on a fresh held-out set;
3. does not introduce unacceptable format failures;
4. keeps token and latency cost proportionate to the gain;
5. survives at least one test outside the exact failure family that motivated it.

If a layer helps only one identifiable failure family, prefer a failure-triggered selective intervention rather than global promotion.
