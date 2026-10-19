args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1L || !args[[1L]] %in% c("add", "remove", "update", "snapshot")) {
  stop("usage: manage-r-dependencies.R add|remove|update|snapshot [PACKAGE ...]", call. = FALSE)
}

operation <- args[[1L]]
specs <- args[-1L]
if (operation != "snapshot" && length(specs) == 0L) {
  stop("at least one package is required", call. = FALSE)
}
if (operation == "snapshot" && length(specs) != 0L) {
  stop("snapshot does not accept package arguments", call. = FALSE)
}

allowed_spec <- "^[A-Za-z][A-Za-z0-9.]*(@[0-9][A-Za-z0-9.-]*)?$"
if (length(specs) && any(!grepl(allowed_spec, specs))) {
  stop("only CRAN package names and optional name@version specs are allowed", call. = FALSE)
}

project <- normalizePath(Sys.getenv("RENV_PROJECT"), winslash = "/", mustWork = TRUE)
library <- normalizePath(.libPaths()[1L], winslash = "/", mustWork = TRUE)
if (!startsWith(library, file.path(project, "renv", "library"))) {
  stop("active R library is outside this repository", call. = FALSE)
}
if (!requireNamespace("renv", quietly = TRUE)) {
  stop("project renv is unavailable; run ./scripts/bootstrap-env.sh", call. = FALSE)
}

package_names <- sub("@.*$", "", specs)
if (operation == "add") {
  renv::install(specs, project = project)
} else if (operation == "remove") {
  renv::remove(package_names, project = project)
} else if (operation == "update") {
  renv::update(package_names, project = project)
}

renv::snapshot(project = project, type = "all", prompt = FALSE)
lock <- renv::lockfile_read(file.path(project, "renv.lock"))
invalid <- vapply(
  lock$Packages,
  function(record) !identical(record$Source, "Repository") ||
    !identical(record$Repository, "CRAN"),
  logical(1L)
)
if (any(invalid)) {
  stop(
    sprintf("renv.lock contains unapproved sources: %s", paste(names(lock$Packages)[invalid], collapse = ", ")),
    call. = FALSE
  )
}
status <- renv::status(project = project)
if (!isTRUE(status$synchronized)) {
  stop("renv status is not synchronized after snapshot", call. = FALSE)
}
