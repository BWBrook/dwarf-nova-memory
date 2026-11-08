#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
root <- normalizePath(if (length(args) >= 1L) args[[1]] else ".", mustWork = TRUE)
out_dir <- normalizePath(
  if (length(args) >= 2L) args[[2]] else
    file.path(root, "outputs/a04i_recovery_independent_audit"),
  mustWork = TRUE
)
metrics_path <- file.path(root, "outputs/a04i_recovery_20261108/metrics.csv")
receipt_path <- file.path(root, "outputs/a04i_recovery_20261108/receipt.json")
receipt <- jsonlite::fromJSON(receipt_path, simplifyVector = FALSE)

eras <- c("1910_1929", "1930_1949", "1950_1959")
rules <- c("C1_7", "C2_095")
ordinary_cases <- c("primary", "structured")
decisive_cases <- c(ordinary_cases, "gross")
z95 <- 1.96

key_fields <- c(
  "family", "phase", "case", "stratum", "replicate", "threshold",
  "extractor", "rule", "extraction_error"
)
numeric_fields <- c(
  "reference_event_count", "onset_effective_covered", "end_effective_covered",
  "short_outside_mar_may_complete_count", "short_outside_mar_may_count",
  "false_confirmed_count", "exposure_years",
  "operational_confirmation_false_emission_count",
  "operational_confirmation_ambiguous_emission_count",
  "operational_confirmation_candidate_count",
  "operational_confirmation_observed_count",
  "operational_confirmation_missing_count",
  "operational_confirmation_premature_count",
  "total_bias", "recovered_r", "oracle_r_all"
)
flag_fields <- c(
  "total_bias_undefined", "recovered_r_undefined", "oracle_r_all_undefined"
)
wanted <- c(key_fields, numeric_fields, flag_fields)
header <- names(utils::read.csv(
  metrics_path, nrows = 0L, check.names = FALSE, stringsAsFactors = FALSE
))
missing_fields <- setdiff(wanted, header)
if (length(missing_fields)) stop("missing required metrics columns: ", paste(missing_fields, collapse = ", "))
classes <- rep("NULL", length(header))
names(classes) <- header
classes[header %in% c("family", "phase", "case", "stratum", "extractor", "rule",
                      "extraction_error", flag_fields)] <- "character"
classes[header %in% c("replicate", "threshold", numeric_fields)] <- "numeric"
rows <- utils::read.csv(
  metrics_path, colClasses = classes, na.strings = c("", "None", "null", "nan", "NaN"),
  check.names = FALSE, stringsAsFactors = FALSE
)

falsey <- function(x) {
  is.na(x) | tolower(trimws(as.character(x))) %in% c("", "0", "false", "none", "null")
}

normal_interval <- function(estimate, mcse) {
  if (!is.finite(estimate) || !is.finite(mcse)) return(c(lower = NA_real_, upper = NA_real_))
  c(lower = estimate - z95 * mcse, upper = estimate + z95 * mcse)
}

wilson <- function(estimate, n_eff) {
  n_eff <- max(1, as.numeric(n_eff))
  z2 <- z95^2
  centre <- (estimate + z2 / (2 * n_eff)) / (1 + z2 / n_eff)
  half <- z95 * sqrt(estimate * (1 - estimate) / n_eff + z2 / (4 * n_eff^2)) /
    (1 + z2 / n_eff)
  c(lower = centre - half, upper = centre + half)
}

ratio_interval <- function(numerator, denominator, rare = FALSE) {
  undefined <- sum(!is.finite(numerator) | !is.finite(denominator) | denominator < 0)
  if (undefined > 0L) {
    return(list(estimate = NA_real_, mcse = NA_real_, lower = NA_real_, upper = NA_real_,
                undefined = undefined, effective_n = NA_real_))
  }
  total_denominator <- sum(denominator)
  if (!is.finite(total_denominator) || total_denominator <= 0) {
    return(list(estimate = NA_real_, mcse = NA_real_, lower = NA_real_, upper = NA_real_,
                undefined = length(denominator), effective_n = NA_real_))
  }
  estimate <- sum(numerator) / total_denominator
  residuals <- numerator - estimate * denominator
  mcse <- if (length(residuals) > 1L) {
    stats::sd(residuals) / sqrt(length(residuals)) / mean(denominator)
  } else {
    NA_real_
  }
  interval <- normal_interval(estimate, mcse)
  effective_n <- NA_real_
  if (rare) {
    if (estimate <= 0 || estimate >= 1) {
      effective_n <- length(denominator)
    } else if (!is.finite(mcse) || mcse == 0) {
      effective_n <- total_denominator
    } else {
      effective_n <- min(total_denominator, max(1, estimate * (1 - estimate) / mcse^2))
    }
    guard <- wilson(estimate, effective_n)
    interval[["lower"]] <- max(0, min(interval[["lower"]], guard[["lower"]]))
    interval[["upper"]] <- min(1, max(interval[["upper"]], guard[["upper"]]))
  }
  list(
    estimate = estimate, mcse = mcse, lower = interval[["lower"]],
    upper = interval[["upper"]], undefined = 0L, effective_n = effective_n
  )
}

mean_interval <- function(values) {
  finite <- values[is.finite(values)]
  undefined <- length(values) - length(finite)
  if (!length(finite)) {
    return(list(estimate = NA_real_, mcse = NA_real_, lower = NA_real_, upper = NA_real_,
                undefined = undefined, effective_n = NA_real_))
  }
  estimate <- mean(finite)
  mcse <- if (length(finite) > 1L) stats::sd(finite) / sqrt(length(finite)) else NA_real_
  interval <- normal_interval(estimate, mcse)
  list(
    estimate = estimate, mcse = mcse, lower = interval[["lower"]],
    upper = interval[["upper"]], undefined = undefined, effective_n = length(finite)
  )
}

gate <- function(metric, bound, direction) {
  if (metric$undefined > 0L || !is.finite(metric$lower) || !is.finite(metric$upper)) {
    return("INCONCLUSIVE")
  }
  if (direction == "above") {
    if (metric$lower >= bound) return("PASS")
    if (metric$upper < bound) return("FAIL")
    return("INCONCLUSIVE")
  }
  if (direction == "below") {
    if (metric$upper < bound) return("PASS")
    if (metric$lower >= bound) return("FAIL")
    return("INCONCLUSIVE")
  }
  if (direction == "inside") {
    if (metric$lower > -bound && metric$upper < bound) return("PASS")
    if (metric$lower >= bound || metric$upper <= -bound) return("FAIL")
    return("INCONCLUSIVE")
  }
  stop("unknown gate direction")
}

metric_record <- function(name, result, status, bound, direction) {
  data.frame(
    metric = name, estimate = result$estimate, mcse = result$mcse,
    lower = result$lower, upper = result$upper,
    undefined = result$undefined, effective_n = result$effective_n,
    bound = bound, direction = direction, status = status,
    stringsAsFactors = FALSE
  )
}

cell_summary <- function(cell) {
  onset <- ratio_interval(cell$onset_effective_covered, cell$reference_event_count)
  end <- ratio_interval(cell$end_effective_covered, cell$reference_event_count)
  short <- ratio_interval(
    cell$short_outside_mar_may_complete_count, cell$short_outside_mar_may_count
  )
  retrospective_false <- ratio_interval(cell$false_confirmed_count, cell$exposure_years)
  unsafe <- ratio_interval(
    cell$operational_confirmation_false_emission_count +
      cell$operational_confirmation_ambiguous_emission_count,
    cell$exposure_years
  )
  bias <- mean_interval(cell$total_bias)
  premature <- ratio_interval(
    cell$operational_confirmation_premature_count,
    cell$operational_confirmation_observed_count,
    rare = TRUE
  )
  missing <- ratio_interval(
    cell$operational_confirmation_missing_count,
    cell$operational_confirmation_candidate_count,
    rare = TRUE
  )
  metrics <- list(
    onset_effective_coverage = list(value = onset, bound = 0.90, direction = "above"),
    end_effective_coverage = list(value = end, bound = 0.90, direction = "above"),
    short_outside_mar_may_completeness = list(value = short, bound = 0.95, direction = "above"),
    false_confirmed_per_year = list(value = retrospective_false, bound = 0.20, direction = "below"),
    operational_confirmation_unsafe_per_year = list(value = unsafe, bound = 0.20, direction = "below"),
    total_bias = list(value = bias, bound = 0.02, direction = "inside"),
    operational_confirmation_premature_fraction = list(
      value = premature, bound = 0.02, direction = "below"
    ),
    operational_confirmation_missing_fraction = list(
      value = missing, bound = 0.05, direction = "below"
    )
  )
  if (unique(cell$case) == "gross") {
    metrics <- metrics[c("false_confirmed_per_year", "operational_confirmation_unsafe_per_year")]
  }
  records <- do.call(rbind, lapply(names(metrics), function(name) {
    item <- metrics[[name]]
    status <- gate(item$value, item$bound, item$direction)
    metric_record(name, item$value, status, item$bound, item$direction)
  }))
  errors <- sum(!falsey(cell$extraction_error))
  verdict <- if (errors > 0L || any(records$status == "FAIL")) {
    "FAIL"
  } else if (all(records$status == "PASS")) {
    "PASS"
  } else {
    "INCONCLUSIVE"
  }
  keys <- cell[1L, c("family", "phase", "case", "stratum", "rule"), drop = FALSE]
  records <- cbind(keys[rep(1L, nrow(records)), , drop = FALSE], records)
  records$replicates <- nrow(cell)
  records$extraction_errors <- errors
  records$cell_verdict <- verdict
  records
}

expected_metric_hash <- receipt$metrics_sha256
actual_metric_hash <- strsplit(
  system2("shasum", c("-a", "256", metrics_path), stdout = TRUE)[[1]],
  "[[:space:]]+"
)[[1]][[1]]

decisive <- rows[
  rows$family == "v2-phase" & rows$phase == "phase" &
    rows$case %in% decisive_cases & rows$stratum %in% eras &
    rows$threshold == 10 & rows$extractor == "X4" & rows$rule %in% rules,
  , drop = FALSE
]
decisive_key <- do.call(paste, c(decisive[c(
  "family", "phase", "case", "stratum", "replicate", "threshold", "extractor", "rule"
)], sep = "|"))
cell_key <- do.call(paste, c(decisive[c("rule", "case", "stratum")], sep = "|"))
cell_counts <- table(cell_key)
grid_ok <- nrow(rows) == 16650L && nrow(decisive) == 7200L &&
  !anyDuplicated(decisive_key) && length(cell_counts) == 18L && all(cell_counts == 400L)

bias_finite <- is.finite(rows$total_bias) & is.finite(rows$recovered_r) & is.finite(rows$oracle_r_all)
bias_difference <- rows$total_bias[bias_finite] -
  (rows$recovered_r[bias_finite] - rows$oracle_r_all[bias_finite])
max_bias_identity_error <- if (length(bias_difference)) max(abs(bias_difference)) else NA_real_
ordinary_decisive <- decisive[decisive$case %in% ordinary_cases, , drop = FALSE]
ordinary_bias_complete <- all(is.finite(ordinary_decisive$total_bias)) &&
  all(falsey(ordinary_decisive$total_bias_undefined)) &&
  all(falsey(ordinary_decisive$recovered_r_undefined)) &&
  all(falsey(ordinary_decisive$oracle_r_all_undefined))

groups <- split(decisive, cell_key, drop = TRUE)
cell_metrics <- do.call(rbind, lapply(groups, cell_summary))
row.names(cell_metrics) <- NULL
utils::write.csv(
  cell_metrics, file.path(out_dir, "independent_cell_metrics.csv"), row.names = FALSE,
  na = ""
)

cell_verdicts <- unique(cell_metrics[c(
  "family", "phase", "case", "stratum", "rule", "replicates",
  "extraction_errors", "cell_verdict"
)])
decision_rows <- lapply(rules, function(rule) {
  selected <- cell_verdicts[cell_verdicts$rule == rule, , drop = FALSE]
  ordinary <- selected[selected$case %in% ordinary_cases, , drop = FALSE]
  gross <- selected[selected$case == "gross", , drop = FALSE]
  statuses <- c(ordinary$cell_verdict, gross$cell_verdict)
  verdict <- if (nrow(ordinary) == 6L && nrow(gross) == 3L &&
                 length(statuses) == 9L && all(statuses == "PASS")) {
    "PASS"
  } else if (any(statuses == "FAIL")) {
    "FAIL"
  } else {
    "INCONCLUSIVE"
  }
  data.frame(
    rule = rule, ordinary_cells = nrow(ordinary), gross_cells = nrow(gross),
    pass_cells = sum(statuses == "PASS"), fail_cells = sum(statuses == "FAIL"),
    inconclusive_cells = sum(statuses == "INCONCLUSIVE"), verdict = verdict,
    stringsAsFactors = FALSE
  )
})
decisions <- do.call(rbind, decision_rows)
selected_rule <- if (decisions$verdict[decisions$rule == "C1_7"] == "PASS") {
  "C1_7"
} else if (decisions$verdict[decisions$rule == "C2_095"] == "PASS") {
  "C2_095"
} else {
  NA_character_
}
decisions$selected_rule <- ifelse(is.na(selected_rule), "", selected_rule)
utils::write.csv(
  decisions, file.path(out_dir, "independent_global_decisions.csv"), row.names = FALSE
)

cat("A04i independent raw recovery decision derivation\n")
cat("R:", R.version.string, "\n")
cat("metrics_sha256_expected:", expected_metric_hash, "\n")
cat("metrics_sha256_actual:", actual_metric_hash, "\n")
cat("metrics_hash_match:", identical(expected_metric_hash, actual_metric_hash), "\n")
cat("all_metric_rows:", nrow(rows), "\n")
cat("decisive_rows:", nrow(decisive), "\n")
cat("grid_ok:", grid_ok, "\n")
cat("finite_total_bias_rows_checked:", length(bias_difference), "\n")
cat("max_abs_total_bias_identity_error:", format(max_bias_identity_error, digits = 17), "\n")
cat("ordinary_bias_complete:", ordinary_bias_complete, "\n\n")

ordered_cells <- cell_verdicts[order(
  match(cell_verdicts$rule, rules), match(cell_verdicts$case, decisive_cases),
  match(cell_verdicts$stratum, eras)
), , drop = FALSE]
cat("CELL VERDICTS\n")
for (i in seq_len(nrow(ordered_cells))) {
  cell <- ordered_cells[i, ]
  cat(sprintf(
    "%s %s %s n=%d errors=%d verdict=%s\n",
    cell$rule, cell$case, cell$stratum, cell$replicates,
    cell$extraction_errors, cell$cell_verdict
  ))
  details <- cell_metrics[
    cell_metrics$rule == cell$rule & cell_metrics$case == cell$case &
      cell_metrics$stratum == cell$stratum,
    , drop = FALSE
  ]
  for (j in seq_len(nrow(details))) {
    detail <- details[j, ]
    cat(sprintf(
      "  %-52s est=% .12g mcse=%.12g CI=[% .12g,% .12g] undefined=%d status=%s\n",
      detail$metric, detail$estimate, detail$mcse, detail$lower, detail$upper,
      detail$undefined, detail$status
    ))
  }
}

cat("\nGLOBAL DECISIONS\n")
print(decisions, row.names = FALSE)
cat("selected_rule:", ifelse(is.na(selected_rule), "NONE", selected_rule), "\n")

integrity_pass <- identical(expected_metric_hash, actual_metric_hash) && grid_ok &&
  is.finite(max_bias_identity_error) && max_bias_identity_error <= 5e-15 &&
  ordinary_bias_complete
cat("independent_derivation_integrity_pass:", integrity_pass, "\n")
if (!integrity_pass) quit(status = 1L)
