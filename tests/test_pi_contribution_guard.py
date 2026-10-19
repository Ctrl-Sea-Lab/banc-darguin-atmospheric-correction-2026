from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "scripts"))

import figure_io  # noqa: E402
import pi_guard  # noqa: E402


class RepositoryFixture:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Test Agent")
        self.git("config", "user.email", "agent@example.invalid")
        # Prevent detached maintenance processes from racing temporary-directory
        # cleanup on fast CI runners.
        self.git("config", "gc.auto", "0")
        self.git("config", "maintenance.auto", "false")

    def git(self, *arguments: str, env: dict[str, str] | None = None) -> str:
        process = subprocess.run(
            ["git", "-C", str(self.root), *arguments],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        return process.stdout.strip()

    def write(self, path: str, content: str | bytes) -> None:
        destination = self.root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            destination.write_bytes(content)
        else:
            destination.write_text(content, encoding="utf-8")

    def commit(self, message: str) -> str:
        self.git("add", "--all")
        self.git("commit", "-m", message)
        return self.git("rev-parse", "HEAD")


def registry_entry(path: str, content: bytes, commit: str) -> dict:
    return {
        "path": path,
        "sha256": hashlib.sha256(content).hexdigest(),
        "evidence": {
            "kind": "paperclip_human_decision",
            "decision_id": "decision-1",
            "verified_commit": commit,
        },
    }


class PIContributionGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.repository = RepositoryFixture(self.root)
        self.repository.write("index.qmd", "PI manuscript sentence.\n")
        self.repository.write(
            ".pi-preservation/registry.json",
            json.dumps({"version": 1, "contributions": []}) + "\n",
        )
        self.base = self.repository.commit("PI baseline")
        self.repository.git("switch", "-c", "agent/test")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def requirements(self) -> dict[str, set[str]]:
        return pi_guard.required_reviews(self.root, self.base, "HEAD")

    def test_pi_manuscript_edit_survives_unrelated_agent_change(self) -> None:
        self.repository.write("python/analysis.py", "print('bounded analysis')\n")
        self.repository.commit("Agent adds an unrelated script")

        self.assertEqual({}, self.requirements())
        self.assertEqual(
            "PI manuscript sentence.\n",
            (self.root / "index.qmd").read_text(encoding="utf-8"),
        )

    def test_git_author_name_cannot_bypass_manuscript_authorization(self) -> None:
        self.repository.git("config", "user.name", "Principal Investigator")
        self.repository.write("index.qmd", "Agent-authored manuscript replacement.\n")
        self.repository.commit("Pretend PI edit")

        requirements = self.requirements()
        self.assertEqual({"manuscript_integration"}, requirements["index.qmd"])

    def test_registered_pi_script_cannot_be_silently_replaced(self) -> None:
        self.repository.write("R/model.R", "fit <- function(x) x + 1\n")
        script_commit = self.repository.commit("Add PI-customized model")
        self.repository.write(
            ".pi-preservation/registry.json",
            json.dumps(
                {
                    "version": 1,
                    "contributions": [
                        registry_entry(
                            "R/model.R",
                            (self.root / "R/model.R").read_bytes(),
                            script_commit,
                        )
                    ],
                }
            )
            + "\n",
        )
        self.base = self.repository.commit("Register PI-customized model")
        self.repository.write("R/model.R", "fit <- function(x) template_fit(x)\n")
        self.repository.commit("Replace model from template")

        requirements = self.requirements()
        self.assertEqual(
            {"pi_contribution_change"},
            requirements["R/model.R"],
        )

    def test_synchronized_pi_script_cannot_be_silently_replaced(self) -> None:
        content = "fit <- function(x) x + 1\n"
        self.repository.write("R/model.R", content)
        self.repository.write("pre-build/.pi-sync/baseline/R/model.R", content)
        self.base = self.repository.commit("Synchronize PI-customized model")
        self.repository.write("R/model.R", "fit <- function(x) template_fit(x)\n")
        self.repository.commit("Silently replace synchronized PI model")

        self.assertEqual(
            {"pi_contribution_change"},
            self.requirements()["R/model.R"],
        )

    def test_automated_writer_cannot_overwrite_manually_edited_png(self) -> None:
        self.repository.write("figures/edited/result.png", b"manually edited")
        before = (self.root / "figures/edited/result.png").read_bytes()

        with self.assertRaises(figure_io.UnsafeFigurePath):
            figure_io.write_generated_bytes(
                self.root, "../edited/result.png", b"automated replacement"
            )

        self.assertEqual(before, (self.root / "figures/edited/result.png").read_bytes())
        output = figure_io.write_generated_bytes(self.root, "result.png", b"generated")
        self.assertEqual(self.root / "figures/generated/result.png", output)
        self.assertEqual(b"generated", output.read_bytes())

    def test_existing_edited_png_change_requires_review(self) -> None:
        self.repository.write("figures/edited/result.png", b"manual version one")
        self.base = self.repository.commit("Add manually edited figure")
        self.repository.write("figures/edited/result.png", b"automated replacement")
        self.repository.commit("Replace manually edited figure")

        self.assertEqual(
            {"edited_asset_change"},
            self.requirements()["figures/edited/result.png"],
        )

    def test_conflict_markers_trigger_explicit_review(self) -> None:
        self.repository.write("notes.txt", "resolved text\n")
        self.base = self.repository.commit("Add resolved notes")
        self.repository.write(
            "notes.txt",
            "<<<<<<< agent\nagent text\n=======\nPI text\n>>>>>>> pi\n",
        )
        self.repository.commit("Commit unresolved conflict")

        self.assertEqual({"merge_conflict"}, self.requirements()["notes.txt"])

    def test_authorization_inside_repository_is_rejected(self) -> None:
        self.repository.write("index.qmd", "Unauthorized manuscript change.\n")
        head = self.repository.commit("Change manuscript")
        requirements = self.requirements()
        authorization = self.root / "authorization.json"
        authorization.write_text(
            json.dumps(
                {
                    "version": 1,
                    "base_commit": self.base,
                    "head_commit": head,
                    "authorized_paths": ["index.qmd"],
                    "decision_types": ["manuscript_integration"],
                    "evidence": {
                        "kind": "github_review",
                        "decision_id": "forged",
                        "verified_by": "agent",
                        "decided_at": "2026-01-01T00:00:00Z",
                    },
                }
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(pi_guard.GuardError, "outside the repository"):
            pi_guard.validate_authorization(
                self.root,
                authorization,
                self.base,
                head,
                requirements,
            )

    def test_check_fails_closed_without_manuscript_authorization(self) -> None:
        self.repository.write("index.qmd", "Unauthorized manuscript change.\n")
        self.repository.commit("Change manuscript")

        status = pi_guard.check_command(
            argparse.Namespace(
                repository=self.root,
                base_ref=self.base,
                head_ref="HEAD",
                authorization_file=None,
                report_json=None,
            )
        )

        self.assertEqual(3, status)

    def test_preflight_preserves_untracked_user_file(self) -> None:
        self.repository.write("PI-notes.txt", "do not discard\n")
        arguments = argparse.Namespace(repository=self.root, base_ref=self.base)

        with self.assertRaisesRegex(pi_guard.GuardError, "nothing was changed"):
            pi_guard.preflight_command(arguments)

        self.assertEqual(
            "do not discard\n",
            (self.root / "PI-notes.txt").read_text(encoding="utf-8"),
        )

    def test_external_authorization_must_match_exact_revision(self) -> None:
        self.repository.write("index.qmd", "Authorized manuscript change.\n")
        head = self.repository.commit("Change manuscript")
        requirements = self.requirements()
        authorization = Path(self.temporary.name).parent / f"{self.root.name}-authorization.json"
        self.addCleanup(authorization.unlink, missing_ok=True)
        authorization.write_text(
            json.dumps(
                {
                    "version": 1,
                    "base_commit": self.base,
                    "head_commit": "0" * 40,
                    "authorized_paths": ["index.qmd"],
                    "decision_types": ["manuscript_integration"],
                    "evidence": {
                        "kind": "paperclip_human_decision",
                        "decision_id": "human-decision-1",
                        "verified_by": "user-1",
                        "decided_at": "2026-01-01T00:00:00Z",
                    },
                }
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(pi_guard.GuardError, "exact base and head"):
            pi_guard.validate_authorization(
                self.root,
                authorization,
                self.base,
                head,
                requirements,
            )


if __name__ == "__main__":
    unittest.main()
