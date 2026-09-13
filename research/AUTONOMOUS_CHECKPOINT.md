# Autonomous research checkpoint — 2026-09-13

## Current operating constraint
The user will not run Qwen tests, launch commands, or paste test outputs. Research must obtain and operate its own authorized execution route. Smaller real Qwen instruments are allowed, but small-model evidence is not target-deployment or Qwen3.8-Max equivalence. This supersedes the old user-execution dependency; it does not erase Exp1–Exp5 or authorize paid resources/company-data export.

## Actual execution completed
The research agent published bounded experiments, launched standard public GitHub CPU jobs, acquired publisher-checksummed real model weights, collected real responses and retrieved evidence artifacts without user test actions.

| Stage | Model/instrument | Real calls | Observed outcome |
|---|---|---:|---|
| Feedback pilot | Qwen3.5-0.8B / Unsloth Q8 | 36 | BARE, SELF_REVIEW and VERIFIED_REPAIR each 0/12 complete successes |
| Calibration + representation | Same 0.8B instrument | 28 | Basic controls 2/4; raw JSON and explicit table representations each 0/12 |
| Instrument qualification | Qwen3.5-2B / Unsloth Q8 | 12 | Basic controls 8/8 across two seeds; four development optimization cases 0/4 |

Total: **76 completed real model calls, 25,691 known physical tokens, zero user test steps**. The two recovery policies reuse the same initial sample; their logical cost totals must not be summed as physical calls/tokens. All three finished runs have no transport errors. Two earlier acquisition-only attempts failed before any model inference and remain separate evidence.

Source execution commits/runs:
- b6385f10a514fd008760620a233ff4dc4c0b010c / 34755662225
- 918bebcb6059e4636c7eb1b96f336b390fc09b33 / 34756276184
- 1e7acd51e2930307d34f2217af303465901e7c8e / 34756584855

The three evidence archives were downloaded, their SHA-256 identities matched GitHub artifact digests, and their visible responses were independently rescored locally. The first two result tables are in results/autolab_08b_v2_summary.json and results/autolab_08b_calibration_summary.json. The 2B result is in results/autolab_2b_qualification_summary.json.

## What changed in the architecture
Separate transport success, instrument qualification, target-task baseline and architecture improvement. A functioning model server is not automatically an adequate research proxy. The observed 0.8B configuration fails basic controls; it is not selected for target-like architecture conclusions. The 2B configuration passes the narrow canary gate, not general adequacy: its harder-task floor remains unresolved. Quantization, engine, input presentation and model capacity causes have not been isolated.

Do not install review loops merely because they run successfully. The first pilot showed added calls/cost without complete successes. Representation shortened input and reduced token use, but did not produce a quality gain. No augmented reasoning architecture is promoted.

## New observed failure: feasible is not optimal
In 2B P04 the model returned A+F: time 6, cost 20, value 35. The input-only operational validator found no count, feasibility, sum or formatting error. Yet A+G has time 6, cost 17, value 37. This is a real silent objective-quality miss, not an arithmetic or schema failure.

A small **post-hoc one-swap dominance witness checker** was implemented. It uses only fixed task inputs and the candidate, not the hidden optimality oracle. It finds the better feasible alternative in this observed case with zero additional model calls. Seven unit tests pass, including a two-swap trap showing that failure to find a one-swap improvement does NOT certify global optimality. On the existing developmental task set, all 93 feasible-but-suboptimal candidates among 105 feasible candidates had a valid one-swap witness; this is local mechanism validation, not 93 model trials.

The suggested A+G answer independently meets the P04 gold score, but it was computed after inspecting the failed development case. It is not a held-out result, a live model repair success, or a reason to rewrite the original 0/4 score. Keep the source-to-constraint fidelity problem explicit: current synthetic inputs already supply exact structured facts.

## Current decision / next research
The autonomous execution route is verified. The Max-like objective is NOT achieved. Next candidate: source-faithful structured task representation + executable feasibility/objective witnesses, compared against identical-tool baselines. First establish non-floor target-task controls and distinguish evidence presentation, deterministic execution, and model decision contributions. Use fresh problems before promotion; do not assume the 2B canary gate proves larger-model transfer.

The old BARE/GUIDE_HIGH comparison remains an optional diagnostic, not a mandatory research sequence. Company deployment and Max reference were not called. No unbounded or scheduled research daemon is running; the recorded jobs finished and their inference servers were shut down.
