# Autonomous execution transition — 2026-09-13

## User constraint
No user-run Qwen tests, command launching, or copy/paste of test outputs. The research agent must obtain and operate an execution route itself. Smaller real Qwen models and explicit proxy experiments are allowed, but their evidence may not be relabeled as target-deployment or Qwen3.8-Max equivalence.

## Execution scope
Public synthetic research only. Standard GitHub-hosted Ubuntu CPU runner; no paid inference API or GPU provisioning, no company endpoint or key, no company/user documents in prompts. Model weights stay ephemeral and are not committed or included in evidence artifacts. The job token has contents-read only and is removed from the process environment before model-server launch.

## First pilot
Q35_SMALL_REAL_FEEDBACK_PILOT_V1. Real Qwen3.5-0.8B Q8_0 weights are the intended small-model instrument. Twelve synthetic constrained-selection problems (six English, six Korean), one seeded sample each. BARE is the initial sample. Both conditional recovery policies branch from exactly that sample and use the same input-only trigger: schema, feasibility and numeric consistency. SELF_REVIEW receives a generic recheck request; VERIFIED_REPAIR receives the same request plus recomputed violations. At most one extra call per recovery policy. Hidden exhaustive optimality scoring is unavailable to the operational validator and model. Silent feasible-but-suboptimal errors are measured explicitly. This is developmental screening, not held-out confirmation or general intelligence evaluation.

## Observed execution incident
Run 34755221135, commit 40cda27491fde96015acc68fe4afb0dd7a37f616: GitHub execution launched autonomously; 19/19 harness/scorer tests passed; asset acquisition failed with HTTP 401 before any inference call. The original exception omitted the acquisition stage, so which upstream request failed was not established. Model calls: 0. Do not call this a model-quality failure.

One bounded transport repair adds host-scoped job-token authentication for the GitHub metadata API and explicit acquisition-stage diagnostics. Experimental inputs, prompts, scoring, temperature, model choice and token-cap policy are unchanged. Outcome remains pending until real execution evidence is read.

## Development fixture correction
A negative test mutated a shared winning-selection list. Copying the list and adding test_fixture_copy_isolation fixed the defect; the full 19-test suite passed locally and on the hosted runner. Never expose shared mutable oracle fixtures to negative-case mutation.
