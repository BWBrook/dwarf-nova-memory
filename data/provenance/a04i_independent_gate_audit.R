#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
root <- normalizePath(if (length(args)) args[[1]] else ".", mustWork = TRUE)

read_json <- function(path) {
  jsonlite::fromJSON(path, simplifyVector = FALSE)
}

sha256 <- function(path) {
  out <- system2("shasum", c("-a", "256", path), stdout = TRUE, stderr = TRUE)
  if (!length(out) || !is.null(attr(out, "status"))) stop("shasum failed: ", path)
  strsplit(out[[1]], "[[:space:]]+")[[1]][[1]]
}

same_number <- function(observed, expected, tolerance = 2e-12) {
  isTRUE(all.equal(as.numeric(observed), as.numeric(expected), tolerance = tolerance))
}

waveform <- c(
  "core_level_mean", "rise_slope_median", "end_slope_median",
  "end_residual_sd_median", "log_below_above_slope_ratio",
  "rho_duration_end_slope", "rho_duration_rise_slope",
  "rho_duration_core_level"
)
cadence <- c(
  "episodes_per_year", "duration_median", "above_fit_fraction",
  "below_fit_fraction"
)
eras <- c("1910_1929", "1930_1949", "1950_1959")

input_path <- file.path(root, "outputs/a04i_inputs_frozen_20261108/inputs.json")
receipt_path <- file.path(root, "outputs/a04i_qualification_20261108/receipt.json")
selected_path <- file.path(root, "configs/a04i_selected.json")
grid_path <- file.path(root, "configs/a04i_grid.json")
calibration_receipt_path <- file.path(root, "outputs/a04i_calibration_20261108/receipt.json")
public_calibration_path <- file.path(root, "data/simulations/a04i_calibration_20261108.json")

inputs <- read_json(input_path)
receipt <- read_json(receipt_path)
selected <- read_json(selected_path)

head_commit <- system2("git", c("-C", root, "rev-parse", "HEAD"), stdout = TRUE)
tracked_status <- system2(
  "git", c("-C", root, "status", "--porcelain", "--untracked-files=no"),
  stdout = TRUE
)

cat("A04i independent qualification-gate audit\n")
cat("R:", R.version.string, "\n")
cat("jsonlite:", as.character(utils::packageVersion("jsonlite")), "\n")
cat("receipt_sha256:", sha256(receipt_path), "\n")
cat("public_calibration_sha256:", sha256(public_calibration_path), "\n")
cat("HEAD:", head_commit, "\n")
cat("freeze_commit:", receipt$freeze_commit, "\n")
cat("tracked_status_clean:", length(tracked_status) == 0L, "\n\n")

receipt_contract_match <- identical(receipt$stage, "a04i-qualification") &&
  identical(receipt$commit, receipt$freeze_commit) &&
  identical(receipt$freeze_commit, head_commit) &&
  identical(receipt$seed_base, paste0("a04i-qualification|", receipt$freeze_commit)) &&
  identical(as.integer(receipt$replicates_per_pair), 150L)
cat("receipt_contract_match:", receipt_contract_match, "\n\n")

hash_checks <- list(
  inputs = c(input_path, receipt$inputs_sha256),
  selected = c(selected_path, receipt$selected_config_sha256),
  grid = c(grid_path, receipt$grid_sha256),
  calibration_receipt = c(calibration_receipt_path, receipt$calibration_receipt_sha256)
)
for (name in names(receipt$source_sha256)) {
  hash_checks[[paste0("source:", name)]] <- c(
    file.path(root, name), receipt$source_sha256[[name]]
  )
}
for (name in names(receipt$qualification_attempts_sha256)) {
  hash_checks[[paste0("qualification_attempt:", name)]] <- c(
    file.path(root, "outputs/a04i_qualification_20261108", name),
    receipt$qualification_attempts_sha256[[name]]
  )
}

cat("HASH RECONCILIATION\n")
hash_ok <- logical(length(hash_checks))
names(hash_ok) <- names(hash_checks)
for (name in names(hash_checks)) {
  actual <- sha256(hash_checks[[name]][[1]])
  expected <- hash_checks[[name]][[2]]
  hash_ok[[name]] <- identical(actual, expected)
  cat(name, "expected=", expected, "actual=", actual,
      "match=", hash_ok[[name]], "\n", sep = " ")
}
cat("all_hashes_match:", all(hash_ok), "\n\n")

calibration <- read_json(public_calibration_path)
all_statistics <- c(waveform, cadence)
real_all <- vapply(
  all_statistics, function(name) as.numeric(inputs$joint_targets[[name]]), numeric(1)
)
scales <- vapply(
  all_statistics,
  function(name) as.numeric(calibration$receipt$fixed_objective_scales[[name]]),
  numeric(1)
)
calibration_checks <- lapply(calibration$attempts, function(attempt) {
  samples <- attempt$raw_feature_vectors
  replicate_ids <- vapply(samples, function(sample) as.integer(sample$replicate), integer(1))
  valid <- vapply(samples, function(sample) isTRUE(sample$valid), logical(1))
  x <- t(vapply(samples, function(sample) {
    vapply(
      all_statistics,
      function(name) as.numeric(sample$statistics[[name]]),
      numeric(1)
    )
  }, numeric(length(all_statistics))))
  objective <- sum(((colMeans(x) - real_all) / scales)^2)
  id <- attempt$configuration$configuration_id
  private_hash <- receipt$calibration_attempts_sha256[[paste0(id, ".json")]]
  list(
    id = id,
    family = attempt$configuration$family,
    objective = objective,
    recorded_objective = as.numeric(attempt$objective),
    complete = length(samples) == 16L && identical(replicate_ids, 0:15) && all(valid),
    objective_match = same_number(objective, attempt$objective),
    private_hash_match = identical(attempt$private_attempt_sha256, private_hash)
  )
})

cat("CALIBRATION WINNER RECOMPUTATION\n")
for (check in calibration_checks) {
  cat(sprintf(
    "%s family=%s objective=%.15g recorded=%.15g complete=%s objective_match=%s private_hash_match=%s\n",
    check$id, check$family, check$objective, check$recorded_objective,
    check$complete, check$objective_match, check$private_hash_match
  ))
}
calibration_winners <- list()
calibration_winner_match <- logical()
for (family in c("v2", "v4")) {
  candidates <- calibration_checks[vapply(
    calibration_checks, function(x) identical(x$family, family), logical(1)
  )]
  ordering <- order(
    vapply(candidates, function(x) x$objective, numeric(1)),
    vapply(candidates, function(x) x$id, character(1))
  )
  winner <- candidates[[ordering[[1]]]]
  pair_id <- paste0(family, "-phase")
  expected_id <- selected[[pair_id]]$configuration_id
  receipt_id <- calibration$receipt$selected[[pair_id]]$configuration_id
  calibration_winners[[family]] <- winner
  calibration_winner_match[[family]] <- identical(winner$id, expected_id) &&
    identical(winner$id, receipt_id)
  cat(sprintf(
    "winner %s: %s objective=%.15g selected_match=%s\n",
    family, winner$id, winner$objective, calibration_winner_match[[family]]
  ))
}
calibration_pass <- all(vapply(
  calibration_checks,
  function(x) x$complete && x$objective_match && x$private_hash_match,
  logical(1)
)) && all(calibration_winner_match)
cat("calibration_pass:", calibration_pass, "\n\n")

block_check <- function(samples, names, real) {
  x <- t(vapply(samples, function(sample) {
    vapply(names, function(name) as.numeric(sample$statistics[[name]]), numeric(1))
  }, numeric(length(names))))
  colnames(x) <- names
  n <- nrow(x)
  p <- ncol(x)
  centre <- colMeans(x)
  covariance <- cov(x)
  difference <- real - centre
  q <- as.numeric(crossprod(difference, solve(covariance, difference)))
  f_statistic <- n * (n - p) * q / (p * (n - 1) * (n + 1))
  prediction_p <- pf(f_statistic, p, n - p, lower.tail = FALSE)
  z <- difference / sqrt(diag(covariance))
  list(
    n = n, p = p, mean = centre, covariance = covariance, q = q,
    f_statistic = f_statistic, prediction_p = prediction_p, z = z,
    max_abs_z = max(abs(z)),
    pass = prediction_p >= 0.01 && max(abs(z)) <= 3.3
  )
}

pair_results <- list()
for (pair_id in names(selected)) {
  configuration <- selected[[pair_id]]
  attempt_name <- paste0(configuration$configuration_id, ".json")
  attempt <- read_json(file.path(
    root, "outputs/a04i_qualification_20261108", attempt_name
  ))
  samples <- attempt$samples
  replicate_ids <- vapply(samples, function(sample) as.integer(sample$replicate), integer(1))
  valid <- vapply(samples, function(sample) isTRUE(sample$valid), logical(1))
  complete <- length(samples) == 150L && identical(replicate_ids, 0:149) && all(valid)

  expected_configuration <- selected[[pair_id]]
  configuration_match <- identical(
    jsonlite::toJSON(attempt$configuration, auto_unbox = TRUE, null = "null"),
    jsonlite::toJSON(expected_configuration, auto_unbox = TRUE, null = "null")
  )

  real_waveform <- vapply(
    waveform, function(name) as.numeric(inputs$joint_targets[[name]]), numeric(1)
  )
  real_cadence <- vapply(
    cadence, function(name) as.numeric(inputs$joint_targets[[name]]), numeric(1)
  )
  wave <- block_check(samples, waveform, real_waveform)
  cad <- block_check(samples, cadence, real_cadence)

  diversity <- list()
  for (era in eras) {
    values <- unlist(lapply(samples, function(sample) sample$diversity[[era]]), use.names = FALSE)
    target <- inputs$joint_diversity[[era]]
    summary <- c(
      episodes = length(values),
      median = stats::median(values),
      share_le_2 = mean(values <= 2)
    )
    diversity[[era]] <- list(
      summary = summary,
      pass = abs(summary[["median"]] / as.numeric(target$median) - 1) <= 0.15 &&
        abs(summary[["share_le_2"]] - as.numeric(target$share_le_2)) <= 0.05
    )
  }

  receipt_pair <- receipt$pairs[[pair_id]]
  eligible <- complete && configuration_match && wave$pass && cad$pass &&
    all(vapply(diversity, function(x) x$pass, logical(1)))
  numerical_agreement <- c(
    waveform_q = same_number(wave$q, receipt_pair$waveform$hotelling_q),
    waveform_f = same_number(wave$f_statistic, receipt_pair$waveform$f_statistic),
    waveform_p = same_number(wave$prediction_p, receipt_pair$waveform$prediction_p_raw),
    waveform_max_z = same_number(
      wave$max_abs_z,
      max(abs(unlist(receipt_pair$waveform$z_raw, use.names = FALSE)))
    ),
    cadence_q = same_number(cad$q, receipt_pair$cadence$hotelling_q),
    cadence_f = same_number(cad$f_statistic, receipt_pair$cadence$f_statistic),
    cadence_p = same_number(cad$prediction_p, receipt_pair$cadence$prediction_p_raw),
    cadence_max_z = same_number(
      cad$max_abs_z,
      max(abs(unlist(receipt_pair$cadence$z_raw, use.names = FALSE)))
    ),
    waveform_pass = identical(wave$pass, isTRUE(receipt_pair$waveform$pass)),
    cadence_pass = identical(cad$pass, isTRUE(receipt_pair$cadence$pass)),
    valid_records = identical(as.integer(receipt_pair$valid_records), 150L)
  )
  for (era in eras) {
    receipt_diversity <- receipt_pair$diversity[[era]]
    numerical_agreement <- c(
      numerical_agreement,
      setNames(
        c(
          identical(
            as.integer(diversity[[era]]$summary[["episodes"]]),
            as.integer(receipt_diversity$summary$episodes)
          ),
          same_number(diversity[[era]]$summary[["median"]], receipt_diversity$summary$median),
          same_number(
            diversity[[era]]$summary[["share_le_2"]],
            receipt_diversity$summary$share_le_2
          ),
          identical(diversity[[era]]$pass, isTRUE(receipt_diversity$passed))
        ),
        paste0(era, c("_episodes", "_median", "_share_le_2", "_pass"))
      )
    )
  }

  pair_results[[pair_id]] <- list(
    complete = complete,
    configuration_match = configuration_match,
    wave = wave,
    cadence = cad,
    diversity = diversity,
    eligible = eligible,
    numerical_agreement = numerical_agreement,
    receipt_eligible = isTRUE(receipt_pair$eligible)
  )

  cat("PAIR", pair_id, "\n")
  cat("attempt:", attempt_name, "samples:", length(samples),
      "replicates_exact_0_149:", identical(replicate_ids, 0:149),
      "all_valid:", all(valid), "configuration_match:", configuration_match, "\n")
  cat(sprintf(
    "waveform: Q=%.15g F=%.15g p=%.15g max_abs_z=%.15g pass=%s\n",
    wave$q, wave$f_statistic, wave$prediction_p, wave$max_abs_z, wave$pass
  ))
  cat(sprintf(
    "cadence: Q=%.15g F=%.15g p=%.15g max_abs_z=%.15g pass=%s\n",
    cad$q, cad$f_statistic, cad$prediction_p, cad$max_abs_z, cad$pass
  ))
  for (era in eras) {
    d <- diversity[[era]]
    cat(sprintf(
      "diversity %s: episodes=%d median=%.15g share_le_2=%.15g pass=%s\n",
      era, as.integer(d$summary[["episodes"]]), d$summary[["median"]],
      d$summary[["share_le_2"]], d$pass
    ))
  }
  cat("numerical_agreement_with_receipt:", all(numerical_agreement), "\n")
  cat("independent_eligible:", eligible,
      "receipt_eligible:", isTRUE(receipt_pair$eligible), "\n\n")
}

independent_eligible <- sort(names(pair_results)[vapply(
  pair_results, function(x) x$eligible, logical(1)
)])
receipt_eligible <- sort(unlist(receipt$eligible_pair_ids, use.names = FALSE))

cat("FINAL\n")
cat("independent_eligible:", paste(independent_eligible, collapse = ","), "\n")
cat("receipt_eligible:", paste(receipt_eligible, collapse = ","), "\n")
cat("eligible_sets_match:", identical(independent_eligible, receipt_eligible), "\n")
cat("all_pair_numerics_match:", all(vapply(
  pair_results, function(x) all(x$numerical_agreement), logical(1)
)), "\n")

audit_pass <- identical(head_commit, receipt$freeze_commit) &&
  length(tracked_status) == 0L && receipt_contract_match && all(hash_ok) &&
  calibration_pass &&
  identical(independent_eligible, receipt_eligible) &&
  all(vapply(pair_results, function(x) {
    x$complete && x$configuration_match &&
      all(x$numerical_agreement) && identical(x$eligible, x$receipt_eligible)
  }, logical(1)))
cat("audit_pass:", audit_pass, "\n")
if (!audit_pass) quit(status = 1L)
