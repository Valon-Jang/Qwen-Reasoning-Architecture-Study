# Source fidelity and same-solver interfaces — frozen development protocol

Status: PREREGISTERED DEVELOPMENT SCREEN; no model result at creation.
Date: 2026-09-13. Prior checkpoint: f67a6adb5e5d982c2ed2c12dc2fd79c7c12d53fe.

## Adopted research operating structure
The user accepted the no-manual-test research architecture v0.2. The research agent owns experiment selection, bounded execution, evidence retrieval, rescoring and the next design decision. This acceptance does NOT promote a model capability or claim Max equivalence. Existing Exp1–Exp5 and all failed attempts remain intact. See ARCHITECTURE_AUTONOMOUS_v0.2.md.

## Next hypothesis
After the 2B model's feasible-but-inferior answer exposed a blind spot, test the source-to-specification boundary. Numeric retranscription may be a needless error source. A compact source-reference interface can move exact copying and finite optimization to the same deterministic tool while retaining source applicability selection in the model. This is system engineering, not proof of intrinsic intelligence gain.

## Arms and attribution
- DIRECT: same source, model outputs selection and totals without a tool. Diagnostic only, not the same-tool architecture control.
- VALUE_TOOL: one model call copies all effective values and constraints into a fixed schema; the host calls a generic exact solver.
- REF_TOOL: one model call selects effective visible item/rule row IDs; a restricted source adapter copies those rows exactly into the SAME solver.
Primary comparison: VALUE_TOOL vs REF_TOOL. This tests interface/work division, not pure reasoning effort. Prompts/output lengths differ by design and are charged in full. Same Qwen3.5-2B Unsloth Q8 instrument, llama.cpp b10344, CPU four threads, thinking=false, temperature=.6, top_p=.95, top_k=20, no client max_tokens, no retry/review calls.

## Controls
A no-model ALL_ROWS adapter receives every machine-readable row. It may solve clean sources or fail closed on conflicting records. It is reported to prevent claiming that a model is needed for already structured input.
A positive exact-specification control supplies the known effective specification to the solver. It tests the instrument only and is NEVER counted as a model success.
Independent final scoring enumerates bit masks, separate from the operational solver's combinations. Hidden effective specifications and optimal selections are never supplied to model prompts or operational tools. The solver now legitimately solves the optimization problem: unlike the earlier input-only validator, it is NOT restricted to error detection. Do not attribute its computation to the model.

## Frozen sample and conditions
Eight fresh constructed sources, two fixed seeds per source and per arm: 48 study calls. Four existing basic canaries precede the study: maximum 52 model calls. 4 English and 4 Korean task/authority narratives share a controlled English record grammar; NOT an all-Korean document benchmark. Cases: clean single, clean pair, item correction, limit correction, unapproved draft, exclusion, dependency+incompatibility, genuine tie. Any optimum is allowed in the tied case.
Arm order rotates across cases; repeat two reverses each first-repeat order. No shared initial samples, no best-of selection. Record schema defects, source fidelity, final semantic score, strict format score and natural completion separately. Repeated seeds are not 16 independent task families.

## Source fidelity and verification limits
Source-reference copying protects copied bytes, NOT semantic completeness. The adapter cannot certify that the model selected every applicable condition. Audit equality with the held-back effective specification is a research measurement, NOT a deployed oracle. A wrong specification can accidentally yield the right final answer; count and report this separately. No global optimality claim is allowed for the original user task if the compiled source is unverified. The exact solver certifies only the specification it receives.

## Quality/cost gate
Report source_fidelity, semantic_pass/null, format_pass, end-to-end case_pass, wrong_spec_right_answer, all tool errors, prompt/completion tokens, known/unknown cost, model wall time and deterministic assessment time. Format-invalid recoverable JSON remains semantically scorable. There is no automatic promotion; any observed gain needs a new distribution and further source-scope testing. Do not claim statistical significance or 3.8-Max equivalence from this pilot.

## Runtime and evidence
Public standard Ubuntu GitHub CPU only. No company data, credential extraction, paid API or paid GPU. Publisher-checksummed weights, loopback server, contents-read GitHub token only for GitHub metadata; remove token from child environment. Bound experiment to 1400 seconds and job to 30 minutes. Any incomplete request stops the experiment; record started/completed counts without silently replaying. Save append-only request/response events and atomic summary after each completed call. Upload only synthetic evidence, never weights or secrets. Server always shut down. Publish evidence hashes and rescore actual outputs before reporting success.

Code and case content hashes are recorded before model provisioning. 25 local unit tests, including 200 random two-solver agreement checks, are deterministic preflight evidence, NOT Qwen trials.
