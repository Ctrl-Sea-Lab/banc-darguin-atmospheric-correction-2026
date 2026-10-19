args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) {
  stop("usage: Rscript R/generate_example_figure.R OUTPUT.png", call. = FALSE)
}

output <- normalizePath(args[[1]], mustWork = FALSE)
dir.create(dirname(output), recursive = TRUE, showWarnings = FALSE)

years <- 2019:2025
cover <- c(42, 45, 47, 46, 51, 55, 58)
png(output, width = 1200, height = 720, res = 144)
plot(
  years,
  cover,
  type = "o",
  pch = 19,
  col = "#006d77",
  xlab = "Survey year",
  ylab = "Illustrative canopy cover (%)",
  main = "Example marine habitat monitoring trend"
)
grid()
dev.off()
cat(output, "\n")
