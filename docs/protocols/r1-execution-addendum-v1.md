# R1 execution note before the 80-history grid

Codex, 9 November 2026. Implementation/protocol freeze remains `0594146`.

The written protocol names only a preparation-only outside-grid smoke. After
that freeze I also ran the implemented **scored** outside-grid smoke, using
replicate 999, development generator namespace
`r1-endpoint-dose-development-v1` and jitter namespace
`r1-endpoint-dose-v1-smoke`. This additional development run was not specified
in the written protocol. Preserve it as an execution deviation, not a member
of the 80-history study. Its receipt is retained at
`outputs/r1_endpoint_scored_smoke_0594146/receipt.json`.

The parent inspected success status, elapsed time, memory, anchor counts and
backoff counts, without opening its gain summary, models or per-issuance scores.
The worker completed in 67.5 seconds with 408 MB peak RSS; the complete command,
including first plot/font-cache preparation, took 79.3 seconds. No scientific
code, protocol, seed, dose, outcome rule or interpretation was changed on the
basis of this run. No production-grid gain has yet been inspected.

An independent read-only implementation review found no scientific blocker and
verified the 19 relevant source/protocol/test bytes against the freeze, original
input/configuration anchors, and hashes of all 80 retained source trial files.
The full grid proceeds with the original 80 tasks, four workers and unchanged
`0594146` implementation. Its results and failures will all be retained.
