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

Experiment 1 demonstrated that explicit state supersession can work on a controlled sequence. Experiment 3 showed that this is not enough to establish an intelligence improvement.

The tested persistent compressed-state bundle failed on replacement/revival tasks where Bare passed. Loss or incorrect preservation of dependency information is a plausible mechanism, but this comparison did not isolate compression from prompt rules, history replacement, state-update machinery, output contracts and extra calls. Treat the result as regression of the tested bundle, not a causal proof that compression alone caused the failures.

## Decision

- Do not promote the persistent-state HC as a general intelligence improvement.
- Do not add critic, reviewer, swarm, or tool-evidence layers to compensate before isolating the failing architecture.
- Run subtractive ablation using raw multi-turn conversation and progressively fewer always-on layers.

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

**Verified:** the primary-input design visible in this recovered FIX1 capture.

**Not verified:** the complete original Exp3 executable; a full benchmark-to-builder call chain; the exact execution hash that generated the 14/16 result; or a replay of the failed model responses. A later revision cannot silently become proof of the historical run's exact implementation. See [reproducibility limitations](./RESEARCH_SCOPE_AND_LIMITATIONS.md).

### Do not convert the negative result into unrun positive evidence

Even an exact historical hash match would not justify:

`HC compressed state lost -> selective external Root retrieval is proven superior`

No such selective-retrieval arm was present. Externally stored state also enters usable model context when retrieved; 'inline versus external' alone is not the meaningful causal variable. Distinguish raw-source retention, lossy replacement, retrieval selectivity, update fidelity, source applicability and resource budgets.

A prospective mechanism test should hold the model, cases, source access, tool interface and budgets constant while comparing raw-history access, generated-summary replacement and source-backed selective retrieval. Include source-coverage and authority/version checks, not only final answer or format. This audit does not execute or preregister that test and does not change any historical denominator.

The failure remains valuable precisely because it constrains architecture claims. It motivates testing the principle 'Navigate the Root. Do not dump the Root'; it does not already validate it.

Related common argument: [Where structure belongs](https://github.com/Valon-Jang/Root-Engineering/blob/main/docs/STRUCTURE_ALLOCATION_ARGUMENT.md). Current autonomous research priorities and the later source/conflict evidence remain governed by [the latest checkpoint](../research/SOURCE_CONFLICT_CHECKPOINT_20260913.md); this retrospective audit does not supersede that work.
