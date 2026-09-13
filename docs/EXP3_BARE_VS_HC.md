# Experiment 3 — Hard Bare vs Full HC

> **Correction, 2026-09-13:** Regrading the user-supplied 32-record original-result capture separates a **16/16 versus 16/16 logged decision-semantic tie** from the unchanged **16/16 versus 14/16 original contract-inclusive result**. HC omitted the required FINAL marker on three turns across two cases. The dependency-loss explanation previously attached to those failures is withdrawn. This is retrospective review, not a new model run or a claim that every sentence is factually correct.

## Goal

Determine whether the accumulated Human Intelligence architecture — including persistent compressed reasoning state and its lifecycle machinery — actually improves Qwen 3.5-33B over a Bare baseline on hard non-ceiling cases.

## Result

| Metric | Bare | HC v3.3 |
|---|---:|---:|
| Original contract-inclusive case PASS | **16/16** | 14/16 |
| Legacy scorer hard-failure cases | **0** | 2 |
| Post-hoc decision-semantic case PASS | 16/16 | 16/16 |
| Post-hoc decision-semantic turn PASS | 20/20 | 20/20 |
| FINAL-marker omission turns | 0/20 | 3/20 |
| Model calls | **20** | 25 |
| Tokens | **54,437** | 65,335 |
| Descriptive case median elapsed, not a speed claim | 45,946 ms | 30,463 ms |
| Avg calls / turn | **1.00** | 1.25 |

Historical decision label: `HC_REGRESSES` (contract-inclusive metric only).
Current interpretation: `SEMANTIC_TIE_CONTRACT_REGRESSION_NOT_PROMOTED`.

## Reclassified failures

| Case / turn | Logged gold | Logged got | Visible decision | Audit classification |
|---|---|---|---|---|
| HC11_STATE_REPLACEMENT_DECISION / 2 | S | empty | The current best decision is S. | Correct decision; FINAL marker omitted |
| HC13_REJECTED_HYPOTHESIS_REVIVAL / 1 | REJECT_A | empty | Hypothesis A is REJECTED (final) | Correct decision; FINAL marker omitted |
| HC13_REJECTED_HYPOTHESIS_REVIVAL / 2 | REVIVE_A | empty | the hypothesis should be revived | Correct decision; FINAL marker omitted |

All three original issues are `WRONG_FINAL`. These are **three affected turns in two cases**, not three independent failed cases. Bare passed these turns. `HC12_STALE_INFERENCE_INVALIDATION` also passed on both arms.

## Interpretation

The prior inference that these failures demonstrated lost or incorrectly preserved dependency information was wrong. The visible HC answers correctly use the updated time constraint and the corrected prerequisite to change the decision. They do not support a state-replacement or hypothesis-revival reasoning failure.

The original product-level result is not erased: a machine consumer requiring FINAL markers still receives three unusable turn outputs, and two full cases therefore fail. The error was treating that outcome as evidence of semantic reasoning regression. A required-format scorer may correctly reject a semantically right answer; its result must not be relabeled as a failed inference.

The retrospective semantic score uses the supplied log's gold decisions: 37 explicit-marker answers and three manually adjudicated prose answers. Enumerated auxiliary numeric/certainty key checks were retained. It does not independently establish every original problem's specification, the truth of every prose sentence, hidden-state completeness, or model-internal reasoning. Original prompts, full scoring implementation and execution-hash provenance remain incomplete.

## Decision

- Do not promote the current HC bundle: there is no demonstrated decision-semantic gain, contract reliability is worse in this run, and total calls/tokens are higher.
- Do not cite Exp3 as evidence that compression or persistent state reduced reasoning accuracy.
- Exp4 and Exp5 remain actual observations. Their numerical results are not invalidated by this correction; the semantic-failure rationale previously used to motivate subtraction is withdrawn.
- Future analyses separate target semantics, required output contract, ancillary prose factuality, state fidelity and resource use. A selective-retrieval arm remains untested here.

## Audit evidence and accounting

Supplied source: 32 JSONL records, 40 turn outputs, 16 paired cases. SHA-256 `71228cab3ccafb4d49f7388804cb19d2c55c4b0cbb508a75074b9e3587966cc5`; 28,195 bytes. No new Qwen or reference-model calls were made. An independently written audit key-line extractor reproduced saved `got` and saved turn-pass outcomes on 40/40 outputs; this is observed-output compatibility, not recovery of the historical scorer. The three prose adjudications are bound to their exact answer hashes in the retained audit package.

| Observed token field, all calls | Bare | HC |
|---|---:|---:|
| prompt_tokens | 2,748 | 18,792 |
| completion_tokens | 51,689 | 46,543 |
| total_tokens | 54,437 | 65,335 |

HC has five additional calls; their per-call token breakdown and purpose are not recorded in this result capture. The log has no separate reasoning-token or hidden-control-token accounting. Shorter visible answers plus larger completion counts are not sufficient to measure internal reasoning or establish that scaffolding replaced reasoning. HC12 also has a 133,330 ms turn; the slow-turn observations are not confined to Bare. Timing is preserved descriptively, not used to prove architectural speedup. The exact Bare case median recomputes as 45,945.5 ms, consistent with the historical rounded 45,946.

Across Exp3 and the separately reported Exp5, additional bundles show a same-direction output-contract risk signal. This is **not** a same-treatment replication or an established universal effect of structure: the bundles, tasks and scorer contracts differ. Exp5's reported 0/1/7 format-failure counts must retain their original counting unit until raw scoring code and outputs establish it. Do not sum them with Exp3's three failed turns or call this the portfolio's only reproduced causal effect.

## 2026-09-13 source audit — recovered revision, not execution-hash verification

A privately supplied diagnostic capture uploaded on 2026-09-12 contains line-numbered excerpts from the later `QWEN_HUMAN_INTELLIGENCE_HARNESS_v3_3_EXP4_SUBTRACTIVE_ABLATION_FIX1.cmd` revision, which includes Exp3-related code. No private paths, endpoint values or unrelated capture contents are reproduced here.

At captured original source lines 665-674, the primary-message builder has this structure:

```javascript
function buildPrimaryMessages(state, userText) {
    var stateText = stateLines(state, true);
    return [
        {role: "system", content: kernelPrompt()},
        {role: "user", content: "STATE\n" + stateText +
            "\n\nNEW_USER_MESSAGE\n" + userText}
    ];
}
```

This builder supplies current state and the new user message rather than appending prior raw conversation. Captured kernel lines 625-636 also specify CURRENT-only state, hidden superseded history, atomic stable-key facts and invalidation of stale derived items. Captured lines 822-832 and 1311-1323 show a state-repair path consuming an extra model call. This is consistent with the documented compressed-state design and confirms that more than a storage-location change was involved.

**Verified:** the primary-input design visible in this recovered FIX1 capture, and the retrospective output audit described above.

**Not verified:** the complete original Exp3 executable; a full benchmark-to-builder call chain; or the exact execution hash that generated the 14/16 result. HC11 prompt counts 763 -> 841 -> 845, versus Bare 89 -> 137 -> 185, are consistent with history replacement but do not uniquely reconstruct request payloads. A later revision and token counts cannot silently become proof of the historical run's exact implementation. See [reproducibility limitations](./RESEARCH_SCOPE_AND_LIMITATIONS.md).

### Do not convert the correction into unrun positive evidence

A decision-semantic tie does not justify:

`HC preserves these decisions -> selective external Root retrieval is proven superior`

No such selective-retrieval arm was present. Externally stored state also enters usable model context when retrieved; 'inline versus external' alone is not the meaningful causal variable. Distinguish raw-source retention, lossy replacement, retrieval selectivity, update fidelity, source applicability and resource budgets.

A prospective mechanism test should hold the model, cases, source access, tool interface and budgets constant while comparing raw-history access, generated-summary replacement and source-backed selective retrieval. Include source-coverage and authority/version checks, not only final answer or format. This retrospective audit does not execute or preregister that test and does not change any historical denominator.

The corrected result constrains contract-reliability and cost claims. It neither validates nor refutes selective Root retrieval.

Related common argument: [Where structure belongs](https://github.com/Valon-Jang/Root-Engineering/blob/main/docs/STRUCTURE_ALLOCATION_ARGUMENT.md). Current autonomous research priorities and the later source/conflict evidence remain governed by [the latest checkpoint](../research/SOURCE_CONFLICT_CHECKPOINT_20260913.md); this retrospective audit corrects the historical Exp3 premise without replacing that work.
