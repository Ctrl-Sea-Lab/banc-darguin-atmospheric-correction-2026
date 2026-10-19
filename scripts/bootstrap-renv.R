args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1L || !args[[1L]] %in% c("restore", "initialize")) {
  stop("usage: bootstrap-renv.R restore|initialize", call. = FALSE)
}

mode <- args[[1L]]
project <- normalizePath(Sys.getenv("RENV_PROJECT"), winslash = "/", mustWork = TRUE)
expected_version <- "1.3.1"
source_url <- "https://cloud.r-project.org/src/contrib/renv_1.3.1.tar.gz"
source_sha256 <- "e16281908ddf0ed6f8f6f8ad3f2cc4788af6de04c1ab223517aa1cc9acb30731"

r_version <- paste(R.version$major, strsplit(R.version$minor, ".", fixed = TRUE)[[1L]][1L], sep = ".")
library <- file.path(project, "renv", "library", paste0("R-", r_version), R.version$platform)
dir.create(library, recursive = TRUE, showWarnings = FALSE)
.libPaths(unique(c(library, .Library.site, .Library)))

install_renv <- function() {
  archive <- tempfile(fileext = ".tar.gz")
  on.exit(unlink(archive), add = TRUE)
  download.file(source_url, archive, mode = "wb", quiet = FALSE)
  checksum <- strsplit(system2("sha256sum", archive, stdout = TRUE), "[[:space:]]+")[[1L]][1L]
  if (!identical(checksum, source_sha256)) {
    stop("renv source checksum mismatch", call. = FALSE)
  }
  install.packages(archive, repos = NULL, type = "source", lib = library)
}

if (!requireNamespace("renv", lib.loc = library, quietly = TRUE)) {
  install_renv()
}
if (!identical(as.character(utils::packageVersion("renv", lib.loc = library)), expected_version)) {
  stop("project renv version does not match the pinned version", call. = FALSE)
}

if (identical(mode, "initialize")) {
  options(repos = c(CRAN = "https://cloud.r-project.org"))
  renv::install(c("knitr", "rmarkdown", "reticulate", "testthat"), project = project)
  renv::snapshot(project = project, type = "all", prompt = FALSE)
} else {
  lockfile <- file.path(project, "renv.lock")
  if (!file.exists(lockfile)) {
    stop("renv.lock is missing; initialization is not an ordinary restore", call. = FALSE)
  }
  # Keep ordinary restores read-only with respect to the reviewed autoloader.
  # renv refreshes activate.R from its installed package during restore, which
  # can otherwise create formatting or repository-metadata-only drift. A renv
  # upgrade must update the scaffold deliberately with the pinned version.
  renv:::renv_scope_binding(renv:::the, "activate_deferred", TRUE)
  renv::restore(project = project, lockfile = lockfile, prompt = FALSE)
}
