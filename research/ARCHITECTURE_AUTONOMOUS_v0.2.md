# Qwen Max-like research architecture v0.2 — accepted operating structure

Date: 2026-09-13. Status: USER-ACCEPTED RESEARCH PROCESS; not a validated Max-like runtime.

## Goal and authority
Develop and test an efficient external architecture around Qwen3.5 toward the user's Max-like goal. The user does not run commands, execute Qwen tests, or paste logs. The research AI chooses hypotheses, acquires an authorized execution route, conducts bounded experiments, retrieves evidence and makes the next research decision. No paid resources, company data export or security-boundary expansion is implied.

## Two systems, not one bloated prompt
Research system: goal and capability gap -> evidence -> hypothesis and cheapest disproof -> real-model test -> independent scoring -> quality/cost comparison -> retain, revise or discard -> reusable implementation.
Runtime candidate: task contract -> relevant source and execution facts -> minimal Qwen judgment -> tool execution -> observable result checks -> narrow intervention only as needed.
Research history is not injected wholesale into runtime prompts. More agents and more review calls are not defaults. Source summaries locate original evidence; they do not replace it. Execution facts are distinct from compressed inferred conclusions.

## Verified execution route
Versioned experiment code in the public research repository -> bounded standard GitHub-hosted Ubuntu CPU job -> publisher-checksummed public Qwen weights and llama.cpp -> loopback inference -> independent scoring -> result artifact -> AI retrieval, hash verification and visible-output rescoring. Company deployment and Max reference evaluation remain separate gates.
No continuous or scheduled research daemon is asserted. Each job has a wall-clock limit, scoped permissions and server cleanup. The research AI makes subsequent decisions in the active conversation.

## Evidence ladder
Keep separate: transport/model acquisition, basic instrument qualification, target-task baseline adequacy, architecture gain, fresh-task replication, larger-model transfer, target-reference comparison. Small-model evidence cannot be called company-deployment or Max equivalence. A basic canary pass is not general capability certification. All-zero and all-perfect screens can be uninformative for architecture comparison.

## Established history and boundaries
Preserve Exp1–Exp5, their raw observed counts and limitations. Lifecycle and arithmetic mechanism passes do not imply intelligence improvement. Compressed HC regressed; GUIDE advantage did not reproduce; the earlier MAX bundle mixed style and AUTO guidance. BARE/GUIDE_HIGH is an optional diagnostic, not the fixed master sequence.
The autonomous 0.8B and 2B runs completed 76 real calls with no user test steps. See AUTONOMOUS_CHECKPOINT.md and the three autolab summaries for exact identities and costs. Do not pool historical arms as independent measurements. The 0.8B configuration failed basic controls; 2B passed a narrow canary but not the tested harder screen.

## Completion means goal evidence, not merely no detected error
A real 2B answer passed the input-only feasibility/format/arithmetic validator but was dominated by another feasible alternative. The post-hoc one-swap checker found an improvement with no additional model call. This remains post-hoc mechanism evidence, not a live repaired answer or a held-out gain. Failure to find a one-swap improvement does not certify global optimality.
Next candidate: source-faithful structured inputs and executable objective-quality evidence. A solver is allowed to compute from its supplied task, but its contribution must be distinguished from model reasoning. Even an exact solver cannot certify the original goal if the source was mistranslated or a condition was omitted.

## Evaluation and efficiency
Record semantic_pass/null, format_pass, end-to-end case_pass, task-objective quality, source fidelity when observable, actual and logical model calls, token components, unknown usage, runtime and human intervention. Keep operational tool results separate from hidden evaluation labels. Wrong specifications that accidentally produce the right answer must be visible.
Use identical-tool baselines for architectural claims; no-tool BARE is a separate diagnostic. Development feedback is not fresh held-out confirmation. Quantization, engine, native thinking settings and source grammar define the scope of every result.
Efficiency is total cost per verified outcome, not merely fewer model calls. Research cost and deployment cost are separate. Compile repeated wins into small tools or source interfaces; remove components whose benefit disappears in integration.

## Persistence and safety
Freeze code, task definitions, evaluation and configuration before live calls. Preserve completed requests immediately; classify transport failures independently; do not silently replay unknown side effects. Never use an arbitrary client max_tokens ceiling and then attribute truncation to model ability. Use explicit wall-clock budgets, clean shutdown and INCOMPLETE states instead.
Store important evidence permanently rather than relying on expiring Actions artifacts. Never upload model weights, real keys or company files into result packages. The GitHub job token is scoped to GitHub metadata and removed from the inference-server environment.

## Current next experiment
SOURCE_PROTOCOL_V1_PREREGISTRATION.md compares direct answers against copied-value and source-reference interfaces to the same solver. Its results must remain a bounded system study, not a claim that Qwen weights became a larger model.
