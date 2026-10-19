from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "scripts"))

import pi_guard  # noqa: E402
import pi_sync  # noqa: E402


def run_git(repository: Path, *arguments: str) -> str:
    process = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return process.stdout.strip()


def write(repository: Path, relative: str, content: str | bytes) -> None:
    destination = repository / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        destination.write_bytes(content)
    else:
        destination.write_text(content, encoding="utf-8")


class PISynchronizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.repository = Path(self.temporary.name)
        run_git(self.repository, "init", "-b", "main")
        run_git(self.repository, "config", "user.name", "Sync Test")
        run_git(self.repository, "config", "user.email", "sync@example.invalid")
        write(self.repository, "index.qmd", "alpha\nmiddle\nomega\n")
        write(self.repository, "library.bib", "@misc{example, title={Example}}\n")
        write(self.repository, "R/figure.R", "value <- 1\n")
        write(self.repository, "python/figure.py", "value = 1\n")
        write(self.repository, "figures/generated/result.png", b"PNG-original")
        write(self.repository, "figures/edited/README.md", "Manual assets.\n")
        run_git(self.repository, "add", "--all")
        run_git(self.repository, "commit", "-m", "authoritative baseline")
        run_git(self.repository, "switch", "-c", "pi/editing")
        pi_sync.initialize(self.repository)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def acceptance(
        self,
        paths: list[str],
        *,
        accepted_head: str | None = None,
        inside_repository: bool = False,
    ) -> Path:
        if inside_repository:
            path = self.repository / "acceptance.json"
        else:
            descriptor, name = tempfile.mkstemp(prefix="pi-acceptance-", suffix=".json")
            os.close(descriptor)
            path = Path(name)
            self.addCleanup(path.unlink, missing_ok=True)
        path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "operation": "post_acceptance_refresh",
                    "accepted_head": accepted_head or run_git(self.repository, "rev-parse", "HEAD"),
                    "accepted_paths": paths,
                    "evidence": {
                        "kind": "paperclip_human_decision",
                        "decision_id": "decision-accepted-1",
                        "verified_by": "user-pi",
                        "decided_at": "2026-10-19T12:00:00Z",
                    },
                }
            ),
            encoding="utf-8",
        )
        return path

    def test_imports_pi_manuscript_edit(self) -> None:
        edited = "alpha\nmiddle revised by PI\nomega\n"
        write(self.repository, "pre-build/index.qmd", edited)
        report = pi_sync.synchronize(self.repository, "import")

        self.assertEqual(edited, (self.repository / "index.qmd").read_text())
        self.assertEqual(
            edited,
            (self.repository / "pre-build/.pi-sync/baseline/index.qmd").read_text(),
        )
        self.assertTrue(
            any(item["action"] == "imported-from-workspace" for item in report["changes"])
        )

    def test_imports_pi_r_and_python_modifications(self) -> None:
        write(self.repository, "pre-build/R/figure.R", "value <- 2 # PI\n")
        write(self.repository, "pre-build/python/figure.py", "value = 2  # PI\n")
        pi_sync.synchronize(self.repository, "import")

        self.assertEqual("value <- 2 # PI\n", (self.repository / "R/figure.R").read_text())
        self.assertEqual(
            "value = 2  # PI\n", (self.repository / "python/figure.py").read_text()
        )

    def test_imports_photoshop_edited_png_and_new_psd(self) -> None:
        png = b"\x89PNG\r\n\x1a\nphotoshop-edit"
        psd = b"8BPS\x00\x01editable-source"
        write(self.repository, "pre-build/figures/edited/manuscript.png", png)
        write(self.repository, "pre-build/figures/edited/manuscript.psd", psd)
        pi_sync.synchronize(self.repository, "import")

        self.assertEqual(png, (self.repository / "figures/edited/manuscript.png").read_bytes())
        self.assertEqual(psd, (self.repository / "figures/edited/manuscript.psd").read_bytes())

    def test_divergent_binary_conflict_stops_without_writes(self) -> None:
        canonical_path = self.repository / "figures/generated/result.png"
        workspace_path = self.repository / "pre-build/figures/generated/result.png"
        baseline_path = (
            self.repository / "pre-build/.pi-sync/baseline/figures/generated/result.png"
        )
        canonical_path.write_bytes(b"agent-regeneration")
        workspace_path.write_bytes(b"photoshop-edit")

        with self.assertRaises(pi_sync.SyncConflict) as captured:
            pi_sync.synchronize(self.repository, "import")

        self.assertEqual(b"agent-regeneration", canonical_path.read_bytes())
        self.assertEqual(b"photoshop-edit", workspace_path.read_bytes())
        self.assertEqual(b"PNG-original", baseline_path.read_bytes())
        self.assertEqual(
            "divergent binary changes",
            captured.exception.report["conflicts"][0]["reason"],
        )
        report = json.loads(
            (self.repository / "pre-build/.pi-sync/last-report.json").read_text()
        )
        self.assertEqual("conflict", report["result"])

    def test_psd_binary_conflict_is_reported(self) -> None:
        write(self.repository, "pre-build/figures/edited/source.psd", b"8BPS-version-one")
        pi_sync.synchronize(self.repository, "import")
        write(self.repository, "figures/edited/source.psd", b"8BPS-agent-version")
        write(self.repository, "pre-build/figures/edited/source.psd", b"8BPS-PI-version")
        run_git(self.repository, "add", "figures/edited/source.psd")
        run_git(self.repository, "commit", "-m", "accepted authoritative PSD")

        with self.assertRaises(pi_sync.SyncConflict) as captured:
            pi_sync.synchronize(
                self.repository,
                "refresh",
                acceptance_file=self.acceptance(["figures/edited/source.psd"]),
            )

        self.assertEqual(
            "figures/edited/source.psd",
            captured.exception.report["conflicts"][0]["path"],
        )

    def test_full_cycle_and_repeated_refresh_are_idempotent(self) -> None:
        write(self.repository, "pre-build/index.qmd", "alpha\nmiddle PI\nomega\n")
        pi_sync.synchronize(self.repository, "import")
        write(
            self.repository,
            "index.qmd",
            "alpha\nmiddle PI\nomega\naccepted revision\n",
        )
        run_git(self.repository, "add", "index.qmd")
        run_git(self.repository, "commit", "-m", "accepted manuscript revision")
        first = pi_sync.synchronize(
            self.repository,
            "refresh",
            acceptance_file=self.acceptance(["index.qmd"]),
        )
        content_after_first = (self.repository / "pre-build/index.qmd").read_bytes()
        state_after_first = (self.repository / "pre-build/.pi-sync/state.json").read_bytes()
        second = pi_sync.synchronize(self.repository, "refresh")

        self.assertIn(b"middle PI", content_after_first)
        self.assertIn(b"accepted revision", content_after_first)
        self.assertTrue(
            any(
                item["action"] == "refreshed-from-authoritative"
                for item in first["changes"]
            )
        )
        self.assertEqual([], second["changes"])
        self.assertEqual(
            content_after_first, (self.repository / "pre-build/index.qmd").read_bytes()
        )
        self.assertEqual(
            state_after_first,
            (self.repository / "pre-build/.pi-sync/state.json").read_bytes(),
        )

    def test_refresh_merges_non_overlapping_text_then_imports_it(self) -> None:
        write(self.repository, "pre-build/index.qmd", "alpha PI\nmiddle\nomega\n")
        write(self.repository, "index.qmd", "alpha\nmiddle\nomega accepted\n")
        run_git(self.repository, "add", "index.qmd")
        run_git(self.repository, "commit", "-m", "accepted manuscript revision")
        refresh = pi_sync.synchronize(
            self.repository,
            "refresh",
            acceptance_file=self.acceptance(["index.qmd"]),
        )
        merged = (self.repository / "pre-build/index.qmd").read_text()

        self.assertIn("alpha PI", merged)
        self.assertIn("omega accepted", merged)
        self.assertTrue(
            any(item["action"] == "merged-into-workspace" for item in refresh["changes"])
        )
        pi_sync.synchronize(self.repository, "import")
        self.assertEqual(merged, (self.repository / "index.qmd").read_text())

    def test_figure_promotion_refuses_overwrite_of_manual_edit(self) -> None:
        write(self.repository, "pre-build/.pi-sync/generated/result.png", b"new-generation")
        write(self.repository, "pre-build/figures/generated/result.png", b"manual-pixel-edit")

        with self.assertRaises(pi_sync.SyncConflict) as captured:
            pi_sync.promote_figure(
                self.repository,
                "figures/generated/result.png",
                "pre-build/.pi-sync/generated/result.png",
            )

        self.assertIn(
            "manual edit protected", captured.exception.report["conflicts"][0]["reason"]
        )
        self.assertEqual(
            b"manual-pixel-edit",
            (self.repository / "pre-build/figures/generated/result.png").read_bytes(),
        )

    def test_sync_never_switches_the_active_branch(self) -> None:
        branch_before = run_git(self.repository, "branch", "--show-current")
        write(self.repository, "pre-build/library.bib", "@misc{pi, title={PI edit}}\n")
        pi_sync.synchronize(self.repository, "import")

        self.assertEqual(branch_before, run_git(self.repository, "branch", "--show-current"))

    def test_imported_manuscript_still_requires_integration_authorization(self) -> None:
        base = run_git(self.repository, "rev-parse", "main")
        write(self.repository, "pre-build/index.qmd", "PI manuscript integration proposal.\n")
        pi_sync.synchronize(self.repository, "import")
        run_git(self.repository, "add", "--all")
        run_git(self.repository, "commit", "-m", "import PI manuscript proposal")
        requirements = pi_guard.required_reviews(self.repository, base, "HEAD")

        self.assertEqual(
            {"manuscript_integration", "pi_contribution_change"},
            requirements["index.qmd"],
        )

    def test_baseline_hash_tampering_fails_closed(self) -> None:
        write(self.repository, "pre-build/.pi-sync/baseline/index.qmd", "tampered baseline\n")

        with self.assertRaisesRegex(pi_sync.SyncError, "baseline hash mismatch"):
            pi_sync.synchronize(self.repository, "import")

    def test_task_scoped_receipt_allows_only_matching_protected_task(self) -> None:
        pi_sync.synchronize(
            self.repository,
            "import",
            task_id="CTR-101",
            prepared_by="ada-lovelace",
        )

        report = pi_sync.verify_ready(
            self.repository,
            "CTR-101",
            "johannes-gutenberg",
            ["index.qmd"],
        )
        self.assertTrue(report["affected"])
        with self.assertRaisesRegex(pi_sync.SyncError, "receipt is for"):
            pi_sync.verify_ready(
                self.repository,
                "CTR-102",
                "johannes-gutenberg",
                ["index.qmd"],
            )

    def test_protected_edit_makes_task_receipt_stale(self) -> None:
        pi_sync.synchronize(
            self.repository,
            "import",
            task_id="CTR-101",
            prepared_by="ada-lovelace",
        )
        write(self.repository, "pre-build/index.qmd", "silent overwrite attempt\n")

        with self.assertRaisesRegex(pi_sync.SyncError, "receipt is stale"):
            pi_sync.verify_ready(
                self.repository,
                "CTR-101",
                "johannes-gutenberg",
                ["index.qmd"],
            )

    def test_conflict_blocks_protected_task_but_not_investigation(self) -> None:
        write(self.repository, "figures/generated/result.png", b"agent-version")
        write(self.repository, "pre-build/figures/generated/result.png", b"PI-version")

        with self.assertRaises(pi_sync.SyncConflict):
            pi_sync.synchronize(
                self.repository,
                "import",
                task_id="CTR-101",
                prepared_by="ada-lovelace",
            )
        with self.assertRaisesRegex(pi_sync.SyncError, "state 'conflict'"):
            pi_sync.verify_ready(
                self.repository,
                "CTR-101",
                "edward-tufte",
                ["figures/generated/result.png"],
            )
        report = pi_sync.verify_ready(
            self.repository,
            "CTR-202",
            "rachel-carson",
            ["analysis/CTR-202_independent/report.qmd"],
        )
        self.assertFalse(report["affected"])
        self.assertEqual("ready", report["result"])

    def test_refresh_requires_external_exact_head_acceptance(self) -> None:
        original_workspace = (self.repository / "pre-build/index.qmd").read_bytes()
        write(self.repository, "index.qmd", "accepted committed manuscript\n")
        run_git(self.repository, "add", "index.qmd")
        run_git(self.repository, "commit", "-m", "accepted manuscript")

        with self.assertRaisesRegex(pi_sync.SyncError, "provide externally authenticated"):
            pi_sync.synchronize(self.repository, "refresh")
        self.assertEqual(original_workspace, (self.repository / "pre-build/index.qmd").read_bytes())

        with self.assertRaisesRegex(pi_sync.SyncError, "outside the repository"):
            pi_sync.synchronize(
                self.repository,
                "refresh",
                acceptance_file=self.acceptance(["index.qmd"], inside_repository=True),
            )
        with self.assertRaisesRegex(pi_sync.SyncError, "exact current HEAD"):
            pi_sync.synchronize(
                self.repository,
                "refresh",
                acceptance_file=self.acceptance(["index.qmd"], accepted_head="0" * 40),
            )

    def test_refresh_rejects_uncommitted_authoritative_content(self) -> None:
        write(self.repository, "index.qmd", "uncommitted authoritative edit\n")
        acceptance = self.acceptance(["index.qmd"])

        with self.assertRaisesRegex(pi_sync.SyncError, "not committed"):
            pi_sync.synchronize(
                self.repository,
                "refresh",
                acceptance_file=acceptance,
            )


class PISynchronizationPolicyTests(unittest.TestCase):
    def test_policy_names_every_team_role_and_scope(self) -> None:
        policy = json.loads(
            (REPOSITORY / ".pi-preservation/sync-policy.json").read_text(encoding="utf-8")
        )
        self.assertEqual("ctrl-sea.pi-sync-policy.v1", policy["schema"])
        self.assertEqual(["analysis/"], policy["unaffected_prefixes"])
        self.assertEqual(
            pi_sync.PROTECTED_SINGLE_FILES,
            set(policy["protected_paths"]["files"]),
        )
        self.assertEqual(
            set(pi_sync.PROTECTED_PREFIXES),
            set(policy["protected_paths"]["prefixes"]),
        )
        self.assertEqual(
            {
                "charles-darwin",
                "ada-lovelace",
                "johannes-gutenberg",
                "rachel-carson",
                "edward-tufte",
                "roger-tomlinson",
                "thomas-bayes",
                "karl-popper",
                "alan-turing",
            },
            set(policy["roles"]),
        )


if __name__ == "__main__":
    unittest.main()
