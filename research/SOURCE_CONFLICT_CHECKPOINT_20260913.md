# Source and conflict architecture checkpoint — 2026-09-13

Status: ACTUAL EXECUTION AND EVIDENCE RETRIEVAL COMPLETE. Runtime candidate is NOT PROMOTED.
This advances the research position after AUTONOMOUS_CHECKPOINT.md's original 76-call checkpoint. Preserve all historical findings and failure boundaries.

## Accepted structure and operating constraint
The user explicitly accepted and requested persistence of autonomous research architecture v0.2. The AI owns experiment choice, authorized execution, evidence retrieval, independent rescoring and subsequent design decisions. The user runs no tests or commands and pastes no outputs. No company data, paid API/GPU, extra permissions or endless daemon are authorized. ARCHITECTURE_AUTONOMOUS_v0.2.md is the saved public operating specification. BARE/GUIDE_HIGH remains an optional diagnostic rather than the master sequence.

## Completed source-interface study
Experiment Q35_2B_SOURCE_FIDELITY_SAME_SOLVER_V1. Execution commit c6853c15662b6bec30091d8657fa7bab3a5c27cf; run 34758271938; job 103726378504.
Same real Qwen3.5-2B Unsloth Q8_0, llama.cpp b10344, CPU four threads, thinking=false. Eight new constructed sources, two seeds, three arms: 48 study calls plus four canaries. Four tasks have Korean narratives but the line-record grammar is English throughout. No repair or review calls.

| Arm | End-to-end success | Full source fidelity | Study model calls | Study tokens |
|---|---:|---:|---:|---:|
| DIRECT (no-tool diagnostic) | 2/16 | not measured | 16 | 4,381 |
| VALUE_TOOL (rewrite all facts) | 1/16 | 0/16 | 16 | 6,730 |
| REF_TOOL (choose all source IDs) | 6/16 | 6/16 | 16 | 5,622 |

VALUE_TOOL and REF_TOOL use the SAME exact operational solver. The comparison concerns interface/work division, not pure intrinsic reasoning. DIRECT does not establish an identical-tool comparison. VALUE_TOOL and REF_TOOL each have nine unscorable tool-input failures; do not interpret these as nine proven semantic reasoning errors. Format_pass here includes tool-input compatibility, not JSON syntax alone. REF vs VALUE paired end-to-end outcomes: six REF wins, one VALUE win, nine ties.
A no-model ALL_ROWS compiler solved five of the eight distinct sources and rejected three conflicting packets. The exact-spec solver control passed eight, but is not a model trial. VALUE_TOOL's one correct final answer included an invented, irrelevant zero-valued item, so source fidelity was still false. A correct final answer alone was not sufficient evidence of faithful task representation.
Full cost: 52 actual completed calls, 16,988 known physical tokens, elapsed 526,232.82 ms, no transport errors. Result file: results/source_protocol_v1_summary.json.

## Follow-up actually performed, not merely proposed
Candidate: keep every unambiguous typed source record deterministically, expose only a conflicting stable-key choice to the model, then assemble exact referenced bytes and use the same solver. The model cannot delete unrelated constraints or retype numbers through this interface. This reduces the model's decision surface rather than adding another critic.
Experiment Q35_2B_CONFLICT_ONLY_FOLLOWUP_V1. Execution commit cd73e923afa42df82849131a64c083198999347d; run 34759099035; job 103728588442.
The eight sources were REUSED after inspecting the prior study. This is post-result development, NOT fresh held-out confirmation. The implementation was frozen and preregistered before this follow-up's calls.

- Sixteen system outcomes: 15 complete successes, 15 exact source representations, 16 valid output contracts.
- Ten outcomes required zero model calls and all ten passed; these are deterministic outcomes, NOT model successes.
- Six genuine Qwen conflict choices: five correct. Item correction: L04 twice. Unapproved draft: L01 twice. Time-limit correction: R02 once (wrong) and R04 once (correct).
- Six study calls used 1,560 tokens. Four canaries used 255 tokens. Total ten actual completed calls, 1,815 physical tokens, 75,946.16 ms including model acquisition/setup. Study outcome processing sum was 9,672.6556 ms; do not turn this cross-job timing into a hardware speedup claim.

Compared with the prior REF_TOOL pass over these same sources, study calls fell from 16 to 6 (62.5%) and observed study tokens from 5,622 to 1,560 (about 72.3%). This includes intentionally avoiding model calls on ten deterministic repetitions; it is a pipeline-cost observation, not equal per-call model throughput or independent held-out improvement. Result file: results/conflict_protocol_v1_summary.json.

## Remaining real failure
S04 repeat 1 chose old rule R02 (time <=9) instead of effective R04 (time <=5). The solver then correctly solved the WRONG specification, returning A+B with time7/cost5/value23. Its valid output violated the actual effective limit. Source references protect copied values, but do not prove the selected record is authoritative or current.

## Evidence and preservation
Both jobs completed; their inference servers were shut down. No unattended or recurring research job remains active.
Source artifact 10318495777: SHA-256 970b55fca4e51717fdc72ef0e78891953fba1a132b73ddbca6597bbc374d1a79.
Conflict artifact 10318720487: SHA-256 4082ab4dac699f0c4e58504c3d5fb4dd4150e5c9aca87f70b656cbaaca5e5970.
Actual mounted ZIP hashes matched GitHub. Source study: all 48 outcomes rescored identically and all 48 model-request hashes matched. Follow-up: all 16 outcomes rescored identically, all six study-request hashes matched; scorable answers also matched separately specified expected answers. Model identity and registered source/code hashes matched.
Durable Drive source (synthetic inputs, actual visible outputs, metadata, hashes and audits): document 18W9j3oB-DK1kFsLhmgS-RJzCkJLnP5wLz-o5zrfFn0M. It was exported and compared after only BOM/line-whitespace/blank-line normalization; normalized text equality passed. This is not a byte-identical Google Docs export claim. Body SHA-256 before native import: 4f62a2f19403beb78be1fb321f4088701c9c381195ccccd14815945bc88edaac.
This checkpoint added 62 actual model calls and 18,803 known physical tokens. The five completed autonomous runs now total 138 actual calls and 44,494 known physical tokens, excluding earlier acquisition-only failures with no model inference. No target-deployment or Max-reference call is included.

## Current decision
Retain conflict-only source compilation as a promising bounded system candidate. Do not deploy or claim Max-like performance. Do not discard earlier null/negative results or rewrite them as successes.
The next target is reliable source applicability and scope coverage, not another full-state regeneration prompt. Preserve the zero-call deterministic path. First freeze a fresh source set with changed row IDs/order, both old-approved and new-approved choices, explicit limit corrections, and negative unsupported-scope cases. Compare against deterministic ALL_ROWS and simple latest-row controls as well as the same-solver model interface; these prevent crediting ordinary parsing to AI.
The current compiler supports only a closed record grammar and one conflict per affected test source. It cannot certify that unrestricted prose contains no omitted conditions, or correctly handle partially overlapping exceptions, revoked list constraints, multiple interacting revisions or source authority outside that grammar. Those must be explicit unknown/unsupported conditions until implemented and independently tested, never silently treated as valid.
If fresh source applicability remains unreliable, compare an explicit evidence-bound decision contract and a larger qualified model as distinct factors. Do not add a default review loop without showing an actual net benefit. Any larger-model acquisition must stay within authorized compute and data boundaries. Company deployment, larger-model transfer and Qwen3.8-Max equivalence remain NOT_MEASURED.

## Resume entry points
1. This checkpoint and the two result JSON files.
2. research/ARCHITECTURE_AUTONOMOUS_v0.2.md.
3. experiments/posthoc/conflict_only_candidate.py and experiments/conflict_protocol_v1/study.py.
4. The frozen source study and two preregistrations for exact provenance.
The AI must keep the user out of manual testing and choose the next bounded research step from the remaining evidence gap.
