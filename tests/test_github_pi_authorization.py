from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "scripts"))

import github_pi_authorization as authorization  # noqa: E402


HEAD = "a" * 40
TOKEN = "PI-CONTRIBUTION-CHANGE-AUTHORIZED"


class GitHubPIAuthorizationTests(unittest.TestCase):
    def test_exact_sha_bound_pi_comment_is_accepted(self) -> None:
        selected = authorization.select_comment(
            [
                {
                    "id": 17,
                    "user": {"login": "SigOiry"},
                    "body": f"{TOKEN} HEAD={HEAD}",
                }
            ],
            {"sigoiry"},
            {TOKEN},
            HEAD,
        )

        self.assertEqual(17, selected["id"])

    def test_comment_for_previous_head_is_rejected(self) -> None:
        selected = authorization.select_comment(
            [
                {
                    "id": 18,
                    "user": {"login": "SigOiry"},
                    "body": f"{TOKEN} HEAD={'b' * 40}",
                }
            ],
            {"sigoiry"},
            {TOKEN},
            HEAD,
        )

        self.assertIsNone(selected)

    def test_token_embedded_in_prose_is_rejected(self) -> None:
        selected = authorization.select_comment(
            [
                {
                    "id": 19,
                    "user": {"login": "SigOiry"},
                    "body": f"Please use {TOKEN} HEAD={HEAD} after review.",
                }
            ],
            {"sigoiry"},
            {TOKEN},
            HEAD,
        )

        self.assertIsNone(selected)

    def test_comment_from_unconfigured_account_is_rejected(self) -> None:
        selected = authorization.select_comment(
            [
                {
                    "id": 20,
                    "user": {"login": "agent-account"},
                    "body": f"{TOKEN} HEAD={HEAD}",
                }
            ],
            {"sigoiry"},
            {TOKEN},
            HEAD,
        )

        self.assertIsNone(selected)

    def test_approved_review_channel_remains_supported(self) -> None:
        selected = authorization.select_review(
            [
                {
                    "id": 21,
                    "state": "APPROVED",
                    "commit_id": HEAD,
                    "user": {"login": "SigOiry"},
                    "body": TOKEN,
                }
            ],
            {"sigoiry"},
            {TOKEN},
            HEAD,
        )

        self.assertEqual(21, selected["id"])

    def test_main_records_authenticated_comment_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            report = root / "report.json"
            output = root / "authorization.json"
            event = root / "event.json"
            report.write_text(
                json.dumps(
                    {
                        "base_commit": "c" * 40,
                        "head_commit": HEAD,
                        "required_paths": ["AGENTS.md"],
                        "required_decision_types": ["safeguard_change"],
                    }
                ),
                encoding="utf-8",
            )
            event.write_text(json.dumps({"issue": {"number": 8}}), encoding="utf-8")
            comment = {
                "id": 22,
                "user": {"login": "SigOiry"},
                "body": f"{TOKEN} HEAD={HEAD}",
                "updated_at": "2026-10-19T19:00:00Z",
            }
            environment = {
                "PI_GITHUB_LOGINS": "SigOiry",
                "GITHUB_TOKEN": "test-token",
                "GITHUB_REPOSITORY": "Ctrl-Sea-Lab/Research-Template",
                "GITHUB_EVENT_PATH": str(event),
            }
            with mock.patch.dict(os.environ, environment, clear=False), mock.patch.object(
                authorization, "fetch_reviews", return_value=[]
            ), mock.patch.object(authorization, "fetch_comments", return_value=[comment]):
                status = authorization.main(
                    [
                        "--guard-report",
                        str(report),
                        "--output",
                        str(output),
                        "--pull-request-number",
                        "8",
                        "--head-commit",
                        HEAD,
                    ]
                )

            self.assertEqual(0, status)
            evidence = json.loads(output.read_text(encoding="utf-8"))["evidence"]
            self.assertEqual("github_pi_comment", evidence["kind"])
            self.assertEqual("22", evidence["decision_id"])
            self.assertEqual("SigOiry", evidence["verified_by"])


if __name__ == "__main__":
    unittest.main()
