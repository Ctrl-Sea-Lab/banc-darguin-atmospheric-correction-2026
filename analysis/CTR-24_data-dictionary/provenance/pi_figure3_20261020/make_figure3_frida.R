#!/usr/bin/env Rscript

# Reproducible publication rendering of the Figure 3 matchup.
#
# Inputs (read-only):
#   figures/figure3_matchup_data.csv
#   figures/figure3_metrics.csv
# Outputs (new files; existing files are never overwritten):
#   figures/figure3_asd_satellite_matchup_frida.svg
#   figures/figure3_asd_satellite_matchup_frida.png

suppressPackageStartupMessages({
  library(dplyr)
  library(ggplot2)
  library(patchwork)
  library(readr)
})

script_arg <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
if (length(script_arg) != 1L) {
  stop("Run this script with Rscript so the project root can be resolved.")
}

project_root <- normalizePath(
  file.path(dirname(sub("^--file=", "", script_arg)), ".."),
  mustWork = TRUE
)
project_path <- function(...) file.path(project_root, ...)

input_matchup <- project_path("figures", "figure3_matchup_data.csv")
input_metrics <- project_path("figures", "figure3_metrics.csv")
output_svg <- project_path("figures", "figure3_asd_satellite_matchup_frida.svg")
output_png <- project_path("figures", "figure3_asd_satellite_matchup_frida.png")

existing_outputs <- c(output_svg, output_png)[file.exists(c(output_svg, output_png))]
if (length(existing_outputs) > 0L) {
  stop("Refusing to overwrite existing output(s): ", paste(existing_outputs, collapse = ", "))
}

matchup <- read_csv(input_matchup, show_col_types = FALSE) |>
  mutate(
    target = recode(target, "Algal mud" = "Macroalgae"),
    correction = factor(correction, levels = c("ACOLITE", "Sen2Cor")),
    target = factor(
      target,
      levels = c(
        "Dry sand", "Microphytobenthos mud", "Macroalgae",
        "White sand", "Seagrass"
      )
    ),
    station_status = factor(
      if_else(station == "AC03", "AC03 (unresolved)", "Other stations"),
      levels = c("Other stations", "AC03 (unresolved)")
    )
  )

metrics <- read_csv(input_metrics, show_col_types = FALSE) |>
  filter(sensitivity == "AC03 included", metric %in% c("rmse", "bias")) |>
  select(correction, metric, estimate, ci_low, ci_high)

expected_counts <- matchup |>
  count(correction)
if (nrow(matchup) != 144L || any(expected_counts$n != 72L)) {
  stop("Expected 72 paired values per processor (144 rows total).")
}
if (anyNA(matchup[c("asd_reflectance", "satellite_reflectance", "station", "target")])) {
  stop("Required matchup fields contain missing values.")
}
if (nrow(metrics) != 4L) {
  stop("Expected RMSD and bias metrics for both processors with AC03 included.")
}

fmt_signed <- function(x) sprintf("%+.3f", x)
annotation <- metrics |>
  mutate(
    statistic = case_when(
      metric == "rmse" ~ sprintf(
        "RMSD %.3f [%.3f, %.3f]", estimate, ci_low, ci_high
      ),
      metric == "bias" ~ sprintf(
        "Bias %s [%s, %s]", fmt_signed(estimate), fmt_signed(ci_low), fmt_signed(ci_high)
      )
    )
  ) |>
  arrange(correction, factor(metric, levels = c("rmse", "bias"))) |>
  summarise(label = paste(statistic, collapse = "\n"), .by = correction)

# Okabe--Ito-derived categorical palette; all categories remain distinguishable
# under common colour-vision deficiencies and are reinforced by direct legend labels.
band_colours <- c(B1="#4c17e1",B2="#6999fe",B3="#a4d26f",B4="#e47121",
                  B5="#b80a0a",B6="#7e0000",B7="#111111",B8="#111111",B8A="#111111")

common_theme <- theme_classic(base_family = "sans", base_size = 8.5) +
  theme(
    axis.line = element_line(linewidth = 0.35, colour = "#222222"),
    axis.ticks = element_line(linewidth = 0.35, colour = "#222222"),
    axis.ticks.length = grid::unit(2.5, "pt"),
    axis.title = element_text(size = 8.5, colour = "#111111"),
    axis.text = element_text(size = 7.5, colour = "#222222"),
    plot.title = element_text(size = 9, face = "bold", hjust = 0),
    plot.margin = margin(5, 6, 3, 5),
    legend.title = element_text(size = 8, face = "bold"),
    legend.text = element_text(size = 7.5),
    legend.key.height = grid::unit(9, "pt"),
    legend.key.width = grid::unit(13, "pt"),
    legend.spacing.x = grid::unit(4, "pt")
  )

make_panel <- function(processor, panel_label) {
  panel_data <- filter(matchup, correction == processor)
  panel_note <- filter(annotation, correction == processor)$label

  ggplot(panel_data, aes(asd_reflectance, satellite_reflectance)) +
    geom_abline(
      slope = 1, intercept = 0, linewidth = 0.55,
      linetype = "22", colour = "#666666"
    ) +
    geom_smooth(
      method = "lm", formula = y ~ x, se = TRUE,
      colour = "#222222", fill = "#777777", alpha = 0.14,
      linewidth = 0.65, fullrange = TRUE
    ) +
    geom_point(
      aes(fill = band, shape = target),
      size = 2.15, stroke = 0.55, colour = "#202020", alpha = 1
    ) +
    annotate(
      "label", x = 0.025, y = 0.675, label = panel_note,
      hjust = 0, vjust = 1, size = 2.45, lineheight = 1.05,
      label.size = 0, fill = scales::alpha("white", 0.86), colour = "#222222"
    ) +
    scale_fill_manual(values = band_colours, drop = FALSE) +
    scale_shape_manual(values = c("Dry sand"=21,"Microphytobenthos mud"=22,"Macroalgae"=23,"White sand"=24,"Seagrass"=25)) +
    scale_x_continuous(
      breaks = seq(0, 0.7, 0.1),
      expand = expansion(mult = 0)
    ) +
    scale_y_continuous(
      breaks = seq(0, 0.7, 0.1),
      expand = expansion(mult = 0)
    ) +
    coord_equal(xlim = c(0, 0.70), ylim = c(0, 0.70), clip = "off") +
    labs(
      title = paste0(panel_label, "  ", processor),
      x = "ASD field reflectance",
      y = "Satellite surface reflectance",
      fill = "Band",
      shape = "Surface class"
    ) +
    common_theme
}

figure <- make_panel("Sen2Cor", "a") + make_panel("ACOLITE", "b") +
  plot_layout(guides = "collect") &
  theme(legend.position = "bottom", legend.box = "vertical") &
  guides(
    fill = guide_legend(
      nrow = 1, byrow = TRUE, order = 1,
      override.aes = list(shape = 21, alpha = 1, colour = "#202020")
    ),
    shape = guide_legend(
      nrow = 1, order = 2,
      override.aes = list(fill = "white", alpha = 1, colour = "#202020")
    )
  )

ggsave(
  output_svg, figure,
  width = 183, height = 104, units = "mm",
  device = svglite::svglite, bg = "white"
)
ggsave(
  output_png, figure,
  width = 183, height = 104, units = "mm",
  dpi = 600, device = ragg::agg_png, bg = "white"
)

message("Created: ", output_svg)
message("Created: ", output_png)
