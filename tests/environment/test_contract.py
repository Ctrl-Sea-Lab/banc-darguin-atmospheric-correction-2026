from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_project_environment_is_repository_scoped() -> None:
    code = (
        "import json,os; "
        "print(json.dumps({k:os.environ[k] for k in "
        "['QUARTO_PYTHON','RETICULATE_PYTHON','RENV_PROJECT',"
        "'R_PROFILE_USER','UV_CACHE_DIR','RENV_PATHS_CACHE','UV_PYTHON_DOWNLOADS']}))"
    )
    result = run("./scripts/project-env.sh", "python3", "-c", code)
    assert result.returncode == 0, result.stderr
    environment = json.loads(result.stdout)
    assert Path(environment["QUARTO_PYTHON"]) == ROOT / ".venv/bin/python"
    assert environment["RETICULATE_PYTHON"] == environment["QUARTO_PYTHON"]
    assert Path(environment["RENV_PROJECT"]) == ROOT
    assert Path(environment["R_PROFILE_USER"]) == ROOT / ".Rprofile"
    assert Path(environment["UV_CACHE_DIR"]) == ROOT / ".cache/uv"
    assert Path(environment["RENV_PATHS_CACHE"]) == ROOT / ".cache/renv"
    assert environment["UV_PYTHON_DOWNLOADS"] == "manual"


def test_render_helper_rejects_template() -> None:
    result = run("./scripts/render-analysis.sh", "analysis/_template")
    assert result.returncode == 64
    assert "not an active investigation" in result.stderr


def test_render_helper_rejects_repository_root() -> None:
    result = run("./scripts/render-analysis.sh", ".")
    assert result.returncode == 64
    assert "direct child of analysis" in result.stderr


def test_investigation_template_has_environment_provenance_contract() -> None:
    template = ROOT / "analysis/_template"
    required = (
        "report.qmd",
        "_quarto.yml",
        "task.yml",
        "scripts",
        "figures",
        "tables",
        "outputs",
        "provenance/.gitkeep",
    )
    assert all((template / path).exists() for path in required)

    task = (template / "task.yml").read_text()
    required_fields = (
        'python_lockfile: "../../uv.lock"',
        'r_lockfile: "../../renv.lock"',
        'validation_status: "not_run"',
        'provenance_file: "provenance/environment.json"',
        "This YAML is not evidence of authenticated PI approval.",
    )
    assert all(field in task for field in required_fields)


def test_provenance_recorder_rejects_template() -> None:
    result = run(
        str(ROOT / ".venv/bin/python"),
        "scripts/record-provenance.py",
        "analysis/_template",
        "--render-command",
        "not-run",
    )
    assert result.returncode == 2
    assert "not an active investigation" in result.stderr


def test_protected_manuscript_paths_are_not_in_workflow() -> None:
    workflow = (ROOT / ".github/workflows/reproducibility.yml").read_text()
    forbidden = ("quarto render index.qmd", "quarto render .", "docs/", "manuscript/")
    assert not any(value in workflow for value in forbidden)
