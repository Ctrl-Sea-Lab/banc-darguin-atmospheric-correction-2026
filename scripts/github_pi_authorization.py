#!/usr/bin/env python3
"""Derive exact-revision authorization from authenticated GitHub PI actions."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


TOKENS = {
    "manuscript_integration": "PI-MANUSCRIPT-INTEGRATION-AUTHORIZED",
    "pi_contribution_change": "PI-CONTRIBUTION-CHANGE-AUTHORIZED",
    "edited_asset_change": "PI-CONTRIBUTION-CHANGE-AUTHORIZED",
    "safeguard_change": "PI-CONTRIBUTION-CHANGE-AUTHORIZED",
    "merge_conflict": "PI-CONTRIBUTION-CHANGE-AUTHORIZED",
}


def fail(message: str) -> int:
    print(f"GitHub PI authorization: {message}", file=sys.stderr)
    return 2


def fetch_json(url: str, token: str, description: str) -> list[dict]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "ctrl-sea-pi-contribution-guard",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except (urllib.error.URLError, json.JSONDecodeError) as error:
        raise RuntimeError(f"cannot read {description}: {error}") from error


def fetch_reviews(repository: str, pull_request: int, token: str) -> list[dict]:
    return fetch_json(
        f"https://api.github.com/repos/{repository}/pulls/{pull_request}/reviews?per_page=100",
        token,
        "pull-request reviews",
    )


def fetch_comments(repository: str, pull_request: int, token: str) -> list[dict]:
    return fetch_json(
        f"https://api.github.com/repos/{repository}/issues/{pull_request}/comments?per_page=100",
        token,
        "pull-request comments",
    )


def comment_authorizes(body: str, required_tokens: set[str], head_commit: str) -> bool:
    """Require one exact, SHA-bound authorization line per decision token."""

    lines = {line.strip() for line in body.splitlines()}
    return all(f"{token} HEAD={head_commit}" in lines for token in required_tokens)


def select_review(
    reviews: list[dict], allowed: set[str], required_tokens: set[str], head_commit: str
) -> dict | None:
    candidates = [
        review
        for review in reviews
        if review.get("state") == "APPROVED"
        and review.get("commit_id") == head_commit
        and ((review.get("user") or {}).get("login") or "").lower() in allowed
    ]
    return next(
        (
            review
            for review in reversed(candidates)
            if required_tokens.issubset(set((review.get("body") or "").split()))
        ),
        None,
    )


def select_comment(
    comments: list[dict], allowed: set[str], required_tokens: set[str], head_commit: str
) -> dict | None:
    if re.fullmatch(r"[0-9a-f]{40}", head_commit) is None:
        return None
    candidates = [
        comment
        for comment in comments
        if ((comment.get("user") or {}).get("login") or "").lower() in allowed
        and comment_authorizes(comment.get("body") or "", required_tokens, head_commit)
    ]
    return candidates[-1] if candidates else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--guard-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pull-request-number", type=int)
    parser.add_argument("--head-commit")
    arguments = parser.parse_args(argv)

    allowed = {
        login.strip().lower()
        for login in os.environ.get("PI_GITHUB_LOGINS", "").split(",")
        if login.strip()
    }
    if not allowed:
        return fail("PI_GITHUB_LOGINS is not configured; protected changes fail closed")
    token = os.environ.get("GITHUB_TOKEN")
    repository = os.environ.get("GITHUB_REPOSITORY")
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not token or not repository or not event_path:
        return fail("required GitHub Actions context is unavailable")

    event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    pull_request = event.get("pull_request") or {}
    issue = event.get("issue") or {}
    number = (
        arguments.pull_request_number
        or pull_request.get("number")
        or issue.get("number")
        or event.get("number")
    )
    head_commit = arguments.head_commit or (pull_request.get("head") or {}).get("sha")
    report = json.loads(arguments.guard_report.read_text(encoding="utf-8"))
    if not number or not head_commit or head_commit != report.get("head_commit"):
        return fail("workflow event is not bound to the checked head commit")

    required_tokens = {
        TOKENS[decision_type]
        for decision_type in report.get("required_decision_types", [])
    }
    try:
        reviews = fetch_reviews(repository, int(number), token)
        comments = fetch_comments(repository, int(number), token)
    except RuntimeError as error:
        return fail(str(error))
    selected_review = select_review(reviews, allowed, required_tokens, head_commit)
    selected_comment = select_comment(comments, allowed, required_tokens, head_commit)
    if selected_review is None and selected_comment is None:
        tokens = ", ".join(sorted(required_tokens))
        return fail(
            "current-head approval or SHA-bound comment from a configured PI is "
            "required with token(s): " + tokens
        )

    if selected_review is not None:
        selected = selected_review
        evidence_kind = "github_review"
        decided_at = selected.get("submitted_at")
    else:
        selected = selected_comment
        evidence_kind = "github_pi_comment"
        decided_at = selected.get("updated_at") or selected.get("created_at")
    reviewer = (selected.get("user") or {}).get("login")
    authorization = {
        "version": 1,
        "base_commit": report["base_commit"],
        "head_commit": report["head_commit"],
        "authorized_paths": report["required_paths"],
        "decision_types": report["required_decision_types"],
        "evidence": {
            "kind": evidence_kind,
            "decision_id": str(selected.get("id")),
            "verified_by": reviewer,
            "decided_at": decided_at,
        },
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(authorization, indent=2) + "\n", encoding="utf-8")
    print(
        f"GitHub PI authorization: verified {evidence_kind} "
        f"{selected.get('id')} by {reviewer}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
