testthat::test_that("R and Python bindings are project-local", {
  root <- normalizePath(Sys.getenv("RENV_PROJECT"))
  library <- normalizePath(.libPaths()[1L])
  testthat::expect_true(startsWith(library, file.path(root, "renv", "library")))

  python <- normalizePath(reticulate::py_config()$python)
  expected <- normalizePath(Sys.getenv("RETICULATE_PYTHON"))
  testthat::expect_identical(python, expected)
})
