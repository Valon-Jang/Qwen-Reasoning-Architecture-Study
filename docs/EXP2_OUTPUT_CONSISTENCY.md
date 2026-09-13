# Experiment 2 — Output Consistency

## Goal

Test whether visible deterministic arithmetic mistakes in otherwise valid model answers can be caught and corrected locally without adding unnecessary model calls.

## Triggering defect

A prior Qwen answer correctly stated two costs as 4 and 6 but summarized the difference as 1. The correct difference is 2.

## Verifier scope

The v3.3 verifier was intentionally narrow:

- explicit sums and differences;
- numeric comparisons and inequalities;
- simple stated deltas.

It was not intended to become a general critic or reviewer.

## Regression results

- Wrong delta `4 vs 6, difference 1` → locally corrected to `difference 2` with `patches=1`, `hard_issues=0`.
- Correct delta `4 vs 6, difference 2` → unchanged with `patches=0`, `hard_issues=0`.
- `2+4+3=8` → detected `EQUATION_MISMATCH`, expected 9.
- `6>7` → detected `FALSE_INEQUALITY`.
- `6<=7` → no issue.

The same verifier function was wired into normal HC output before emission. Safe unambiguous corrections do not add a model call; blocking numeric conflicts may trigger at most one focused correction call.

## Conclusion

**PASS — deterministic numeric verification is a valid mechanism.**

This establishes correctness of the verifier itself. It does not establish that attaching the verifier to every turn improves general reasoning quality. Experiment 4 later showed zero verifier activations in the tested ablation set, so its always-on general benefit remains unproven.
