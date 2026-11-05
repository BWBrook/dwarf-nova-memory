# Reproducibility and shared-agent workflow

## One scientific record

Keep the question, definitions and decisions versioned alongside the code. The
shortest route through the repository is README → research brief → methods →
current coordination board. Detailed evidence lives in the bibliography and
evidence register, with links from the scientific notes.

Use a new branch or worktree per bounded task when Claude and Codex are operating
concurrently. Claim ownership in `coordination/board.md`. Merge after reviewing
the actual diff and evidence. Avoid both agents editing the same scientific
definition without a recorded reconciliation. No model family is assumed to be
the better scientist or programmer; rotate implementer and reviewer roles.

## Commit messages and handoffs

A handoff states the changed assumption or implementation, inputs used, commands
run, observed result, limitations and next unresolved question. Prefer a small
number of coherent commits over a stream of unreviewable generated changes.
Retain abandoned approaches when they informed a choice, in a short decision
note or a branch/tag that is clearly labelled exploratory.

Never let agreement between agents replace a scientific test. Independently
derive a likelihood term, construct an adversarial fixture or reproduce an
event annotation without seeing the original answer. For a key claim, save what
the reviewer was given and what they produced independently.

## Reproducible runs

For a real analysis run, save:

- Git commit and dirty/clean status; code/configuration hashes.
- Immutable raw-data hashes, archive release, query and retrieval metadata.
- Fully expanded analysis configuration and selected target list.
- Python/R and package versions; platform details when consequential.
- Random-seed derivation and replicate IDs; sampler settings and diagnostics.
- Data exclusions, censoring, failed fits and missing outputs, with reasons.
- Model predictions before scoring and the evaluation protocol version.

The seed demo saves a deterministic seed, Python version, configuration and CSV
hashes. Its frozen seed version is traceable through the repository commit. It
does not claim to implement the complete run record for future real analyses.

## Freezing an evaluation

Development plots can reveal the future accidentally. Decide the development
period and withhold evaluation observations from exploratory notebooks and
plots before the first target audit. Reading a paper about an eventual test
epoch also exposes information: record that prior knowledge, including known
unusual episodes, rather than calling it a wholly unseen test. Define a file-level access boundary or separate development/evaluation
exports. State whether historical upload availability is known. Where unknown,
use observational-time retrospective evaluation language.

Freeze thresholds, model choices, hyperparameter tuning, window/season rules and
scoring before evaluation. The final test data are not a reusable tuning budget.
If an outcome is inspected and the protocol changes, mark it as development and
reserve new validation if possible. A dated, versioned internal protocol can be
valuable without claiming formal preregistration.

## Computation

The seed is intentionally laptop-scale. Its core is Python's standard library;
Matplotlib is optional for a figure. For Bayesian/latent inference, choose an
implementation only after the simplest design is recoverable and identifiable.
Candidate tools should be justified by the model and diagnostics, not selected
because a GPU is available.

The user's multi-node CPU resources are useful later for independent simulation
replicates, source-specific fits and sensitivity grids. Assign a unique seed to
each replicate from a recorded master seed and stable replicate ID. Keep
scheduling and data transport separate from the statistical model. Use the
A100 only if a measured workload benefits; neither deep learning nor massive
computation is required to make the first paper worthwhile.

## Publication record

Keep a result-neutral manuscript outline until evaluation is complete. Record
which hypotheses are confirmatory, which are exploratory, and all material
protocol changes. Choose a venue based on the achieved contribution. Document
human and agent contributions according to the actual journal's policy at
submission time; do not assume current policy or list an agent as an author.
Authorship, external contact and submission remain decisions for the user.
