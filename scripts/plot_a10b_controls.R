args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 2L)
gains <- read.csv(args[[1]], stringsAsFactors = FALSE)
variants <- c("prefix_point", "prefix_uniform_end", "retrospective_point", "oracle_point")
keys <- c(paste("v2-phase", c("null", "structured", "gross", "offset", "adaptive", "alternative")),
          paste("v4-phase", c("null", "alternative")))
labels <- c("v2: independent null", "v2: structured, no direct effect", "v2: gross reports",
            "v2: persistent offsets", "v2: adaptive observing", "v2: injected effect",
            "v4: null (stress)", "v4: injected effect (stress)")
dat <- gains[gains$comparison == "gain_M3_M2" & gains$variant %in% variants, ]
stopifnot(nrow(dat) == length(keys) * length(variants))
stopifnot(all(dat$failed_or_missing_replicates == 0L))
dat$row <- match(paste(dat$family, dat$case), keys)
dat$variant_index <- match(dat$variant, variants)
limits <- range(c(0, dat$mc_lower, dat$mc_upper), finite = TRUE)
padding <- max(diff(limits) * 0.08, 0.0005)
limits <- limits + c(-padding, padding)
colours <- c("#163D65", "#00837F", "#BA601C", "#555555")
shapes <- c(16, 17, 15, 18)
offsets <- c(0.25, 0.08, -0.08, -0.25)
if (grepl("\\.png$", args[[2]], ignore.case = TRUE)) {
  png(args[[2]], width = 11, height = 7, units = "in", res = 160, pointsize = 11, type = "cairo")
} else {
  svg(args[[2]], width = 11, height = 7, pointsize = 11, family = "sans")
}
layout(matrix(1:2, ncol = 1), heights = c(0.89, 0.11))
par(mar = c(4.3, 15, 5, 1.5), xaxs = "i", yaxs = "i")
plot(NA, xlim = limits, ylim = c(0.4, 8.7), yaxt = "n", ylab = "", bty = "n",
     xlab = "M3 minus M2 log-score gain (nats per scored forecast)")
for (position in seq(1.5, 7.5, 1)) abline(h = position, col = "#EEEEEE")
abline(v = 0, col = "#777777", lty = 2)
axis(2, at = 8:1, labels = labels, las = 1, tick = FALSE)
for (i in seq_len(nrow(dat))) {
  d <- dat[i, ]
  y <- 9 - d$row + offsets[d$variant_index]
  segments(d$mc_lower, y, d$mc_upper, y, col = colours[d$variant_index], lwd = 1.4)
  points(d$mean_gain_nats, y, pch = shapes[d$variant_index], col = colours[d$variant_index], cex = 1.05)
}
title(main = "A10b synthetic development controls", adj = 0, font.main = 2, line = 2.5)
mtext("Nominal 95% Monte Carlo intervals across eight v2 or four v4 trials; not real-star evidence",
      side = 3, adj = 0, line = 1.0, cex = 0.85)
par(mar = c(0, 15, 0, 1.5))
plot.new()
legend("center", bty = "n", ncol = 2,
       legend = c("Prefix point", "Prefix uniform end", "Retrospective (leaky)", "Oracle timing (strict match)"),
       col = colours, pch = shapes, lty = 1, cex = 0.85)
invisible(dev.off())
