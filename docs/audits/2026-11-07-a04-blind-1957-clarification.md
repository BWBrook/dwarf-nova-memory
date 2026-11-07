# Clarification of E1957-07 alternative end

This additive note does not modify the sealed files or the primary E1957-07 annotation.

## Discrepancy

The structured alternative fields in `annotation.csv` give:

- `alternative_end_earliest_jd = 2436167.7`, ID `50675431` (B, magnitude 9.9);
- `alternative_end_latest_jd = 2436167.7`, ID `50675432` (F, magnitude 10.5).

The notes in `annotation.csv` and `report.md` instead describe an alternative end of `[2436167.7, 2436168.29)`, using B ID `50675431` and F ID `50675433`.

Both forms arose from the same source rows, but they apply different meanings of “after.” The protocol orders rows by JD and then native observation ID and defines `end_latest` as the first F row after the last B row. Under that row ordering, F ID `50675432` follows B ID `50675431` at the same reported JD, so the structured fields are the literal mechanical result: `[2436167.7, 2436167.7)`. The prose used the first F row at a strictly later JD, ID `50675433` at JD 2436168.29, producing `[2436167.7, 2436168.29)`.

## Correct interpretation

The tied-JD form is not an exact, zero-uncertainty end. It records conflicting B and F classifications at the same reported epoch. Native observation-ID ordering breaks a database tie; it does not establish physical temporal order or a perfectly observed threshold crossing. The empty numerical interval therefore exposes a protocol representation problem for tied contradictory rows.

The two source-supported alternatives are:

1. **Literal row-ordered protocol representation:** `[2436167.7, 2436167.7)`, last-B ID `50675431`, first subsequent-row F ID `50675432`. Interpret this as a tied B/F epoch with unresolved boundary, not as zero uncertainty.
2. **Strictly-later-JD ambiguity envelope:** `[2436167.7, 2436168.29)`, last-B ID `50675431`, first F at a later reported epoch ID `50675433`. ID `50675433` also supplies the second independent F report needed for observation-time end confirmation after the tail.

The structured fields and prose should therefore not be treated as competing empirical claims. The structured fields implement the stated JD-plus-ID ordering; the prose records a conservative non-empty temporal envelope. A future protocol revision should specify how tied contradictory B/F rows are encoded and should not allow a zero-width bracket to imply zero uncertainty.

The sealed primary end remains unchanged: `[2436167.239, 2436167.5)`, with last-B ID `50675421` and first-F ID `50675422`. Primary labels, type, class, duration, and following-gap values are unchanged.
