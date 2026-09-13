# First autonomous real-Qwen result

Date: 2026-09-13. This supersedes acquisition-pending status only; it does not promote a reasoning architecture.

Real Qwen3.5-0.8B Unsloth Q8 weights ran on a standard public GitHub CPU runner without user test actions. Run 34755662225 completed 36 real generation calls over 12 synthetic tasks. Weights and runtime publisher SHA-256 checks passed. The final artifact was retrieved and all 36 saved scores were recomputed locally from raw final responses without mismatch.

BARE, conditional SELF_REVIEW and conditional VERIFIED_REPAIR each had 0/12 complete case passes. BARE had 0 semantic successes, 11 format passes and no unscorable response. Both recovery arms had zero confirmed semantic successes, 10 format passes and one unscorable response. All initial responses triggered the input-only validator. Logical token totals were 4,703 / 10,235 / 10,620 respectively. Physical shared-prefix calls consumed 16,152 tokens. Runtime including acquisition was 193.003 seconds, not overall authoring time.

## Decision
No default review or feedback layer is promoted. This is an all-zero floor for this small instrument and task presentation, not evidence that feedback never helps or that the target Qwen deployment cannot perform the tasks. Follow-up is calibration plus a matched same-task representation experiment before spending resources on more repetitions or model scaling.

The follow-up uses four easy health controls and re-runs the same twelve developmental tasks in two representations: original variable-referenced JSON input and explicitly bound scalar values plus an item table. Model, runtime, temperature, seed, source facts, constraints, objective and output schema are matched; order is balanced. This tests a representation treatment bundle, not intrinsic compute or a pure single-word effect. It is not fresh held-out evidence.

## Acquisition experience
Run 34755221135 failed HTTP 401 with insufficient stage diagnostics. One bounded repair run 34755462416 showed official llama runtime downloads worked and the failing endpoint was the ggerganov Hugging Face metadata request. That source path was stopped. A newly registered independently published Unsloth artifact, pinned to its public SHA-256 before download, completed acquisition and real inference. Do not silently call the two quantizations identical. GitHub in-progress job log download returned BlobNotFound once; completed job logs and downloadable artifacts were successfully recovered. Do not repeatedly request unavailable live logs.

## Boundaries
No company files, endpoint or credentials were used. No paid inference API or GPU resource was provisioned. Tests/scorer/transport passing is not model-quality passing. Full archived evidence and reproducible source are distinct from inference weights, which remain ephemeral.
