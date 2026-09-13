# Next Experiment — Clean Reasoning-Effort Test

## Purpose

Resolve the main confound left by Experiment 5: the arm named `MAX` mixed reasoning guidance, presentation style, and AUTO-effort prompt wording.

The next experiment should isolate reasoning effort cleanly.

## Recommended primary comparison

```text
BARE
vs
GUIDE_HIGH
```

### BARE

Minimal system prompt / baseline behavior.

### GUIDE_HIGH

```text
BARE
+ the same short GUIDE used in prior experiments
+ explicit high-effort reasoning guidance
```

Do **not** add Korean style/tone instructions to this arm. Style must remain identical across arms.

## Required controls

Keep constant:

- exact model ID;
- endpoint / transport;
- temperature;
- case order balancing;
- raw multi-turn conversation policy;
- no persistent compressed state;
- no critic/reviewer/swarm;
- no client-side `max_tokens` cap;
- same output contract.

## Required scoring separation

Do not collapse all quality into one product-level PASS.

Record separately:

```text
semantic_pass
format_pass
case_pass
tokens
latency
model_calls
```

If format fails but the semantic answer can still be deterministically recovered for analysis, preserve that semantic score separately while keeping product-level case failure intact.

## Recommended cases

Reuse the held-out failure-mode family but use a fresh non-identical set where possible:

- simultaneous hard constraints;
- missing-data honesty;
- causal attribution / confounding;
- true tie;
- fact update / decision replacement;
- rejected-hypothesis revival;
- arithmetic consistency;
- data / prompt-injection boundary.

## Decision rule

Promote GUIDE_HIGH only if it shows a repeatable semantic-quality gain over BARE without unacceptable format, token, or latency regression.

If semantic quality ties, prefer BARE.

If GUIDE_HIGH only improves one specific case family, do not make it always-on. Convert that gain into a candidate **failure-triggered selective rule** and test the trigger separately.

## Follow-up only if needed

After reasoning effort is isolated, style may be tested independently:

```text
GUIDE_HIGH
vs
GUIDE_HIGH + STYLE
```

Do not combine style and reasoning-effort experiments again.
