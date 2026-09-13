# Conflict-only source resolution: exploratory follow-up

Date: 2026-09-13. Status: registered before this follow-up's live calls.
Prior source study: run 34758271938, commit c6853c15662b6bec30091d8657fa7bab3a5c27cf.

## Why this experiment
The prior same-solver study completed 52 actual calls. DIRECT passed 2/16, VALUE_TOOL 1/16 (0/16 full source fidelity), REF_TOOL 6/16. A no-model ALL_ROWS control solved five of the eight distinct sources and stopped on three conflicting sources. Requiring a model to regenerate all applicable records introduced wrong-reference-kind, duplicate-record and omission failures. This follow-up changes the division of work, not the model weights.

## Frozen candidate
Retain every unambiguous typed source record deterministically. Construct candidate groups only when a stable item or scalar rule has conflicting values. Ask Qwen to return one currently effective reference ID from the conflicting group. The compiler accepts only an exact offered choice and does not allow the model to delete unrelated constraints, invent new rows or rewrite numbers. Feed the assembled specification into the same exact solver.

## Sample, controls and attribution
Reuse the eight constructed sources from the previous study, twice. This is POST-RESULT DEVELOPMENT, not a fresh held-out confirmation. Five sources need no model calls; three contain exactly one conflict. Six study model calls plus four inherited qualification canaries: maximum ten model calls, sixteen system outcomes. Do not call the ten deterministic outcomes model inference successes. Correct conflict choices are not supplied to the model; held-back effective specifications are used for offline evaluation only.

Same Qwen3.5-2B Unsloth Q8_0 / llama.cpp b10344 / CPU four threads / thinking=false / temperature=.6 / top_p=.95 / top_k=20. Study seeds match previous case/repeat seeds. No review, retry, output repair or best-of selection. No client max_tokens. Existing source packets and changed task interface are frozen before the run. A repeated source under a later engine session is not a simultaneous wall-clock A/B benchmark.

## Predictions and failure conditions
Measure source fidelity, final semantic correctness, exact enum format, unscorable output, model-selected outcomes, zero-call outcomes, actual calls/tokens and total elapsed time separately. A wrong source choice remains wrong even when syntactically valid. No-choice or out-of-set output is rejected rather than guessed. There is no automatic promotion, regardless of the development result.

## Explicit limits
The source adapter recognizes only a closed line-record grammar. It does not certify that arbitrary prose contains no additional obligations, that all source authority relations have been modeled, or that a numerical duplicate always means supersession. The current test supports only one conflict per affected source. A generic source-fidelity gate, multiple interacting conflicts, new identifiers, unseen instructions and distribution transfer remain separate work. A solver proves optimality only for the compiled specification, not automatically for the original task. No intrinsic model intelligence, company deployment, larger-model transfer or Max equivalence claim is permitted.

## Execution and evidence
Public standard GitHub CPU job; no company files, paid API/GPU or user test steps. Contents-read token only for GitHub acquisition metadata; token removed before starting inference. Publisher checksums required. Internal study budget 600 seconds; workflow timeout 15 minutes; server shut down in finally. Append request/response events and checkpoint each completed outcome. Preserve registration, raw visible responses, identities, token accounting and source hashes; independently rescore after artifact download. Eight deterministic compiler tests and Python compilation are preflight checks, not model trials.
