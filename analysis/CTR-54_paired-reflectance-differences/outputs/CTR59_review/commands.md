# Executed verification commands

Checkout: project `.task-worktrees/CTR-59`, branch `ctr-59-independent-review`, starting from `7b9232da45c68c82c5f996b37357f15fb7b9ed55`. Variables below abbreviate paths; no shell environment modification is required to read this record.

- PROJECT: `/mnt/PaperClip_Projects/projects/banc-darguin-atmospheric-correction-2026`
- A: `analysis/CTR-54_paired-reflectance-differences`
- R: `$A/outputs/CTR59_review`

1. Inspect `git status --short --branch`, `git log`, `git worktree list`, repository instructions and candidate scripts. Create dedicated review worktree at exact candidate.
2. `$PROJECT/.venv/bin/python scripts/pi_sync.py --repository . verify-ready --task-id CTR-59 --agent karl-popper --path analysis/CTR-54_paired-reflectance-differences/outputs/CTR59_review`. Passed. Initial wrapper-triggered frozen restore stopped as unnecessary; canonical Python used.
3. `$PROJECT/.venv/bin/python $R/scripts/independent_checks.py`. Results: `provenance/independent_checks.log`, JSON; exit 0.
4. `$PROJECT/scripts/project-env.sh Rscript $R/scripts/independent_models.R $A $R`. Results: `provenance/independent_models.log`, tables, R session; exit 0.
5. `python3 $R/scripts/display_check.py $R/outputs/display $R/outputs/display/previous.html`. Candidate HTML copied unchanged; previous HTML from `git show 1bbb23b3b94e775a60aa921f8c9c4f86f51926cb:analysis/CTR-54_paired-reflectance-differences/report.html`. Script derives from candidate `ctr58_display.py`, renaming only output prefixes. Exit 0. Visually inspected 1920px screenshot and original temporal figure.
6. `$PROJECT/scripts/check-env.sh` in canonical project: passed, no changes proposed, Python versions/sources valid and R consistent.
7. Python stdlib: compare 21 consumed-file SHA-256s against disk and exact upstream `git show` bytes; compare locks; inventory path/duplicate ranking; 142 raw sizes/mtimes; new March 27 B8 checksum. Results: `provenance/provenance_checks.json`.
8. Copy report source, bibliography, CSS, investigation config, two included report tables, referenced figures and unchanged canonical render/project-env helpers to `/tmp/ctr59-render-*/`. Execute copied `scripts/render-analysis.sh` targeting the isolated investigation, with canonical `RENV_PATHS_LIBRARY`. Exit 0, HTML bitwise identical. See `provenance/render.log` and JSON. Temporary directory removed by context manager.
9. `zipfile.ZipFile.testzip()` of CTR58_review_package.zip plus exact member byte comparisons of report, map PNG/PDF and temporal PNG: passed, `provenance/package_links.json`.
10. Access six cited primary documentation pages with web tool; pertinent source claims and limitations recorded in report.

No full raw rehash, full geospatial/influence rerun, author-branch edit, raw-data change, system install, merge or publication was performed.
