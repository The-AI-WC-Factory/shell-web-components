# Contributing

Humans submit product requirements, expected behavior, priorities and general policies through Issues. Engineering contributions must be AI-operated and identify the agent/tool and validation evidence in the PR.

An AI agent translates an accepted Issue into a technical plan, implements it on an Issue-linked feature branch, runs checks, and obtains independent AI review. Humans do not supply implementation code, tests, architecture or code reviews.

Follow docs/governance.md. Link the Issue using `Refs #N`; close it only when all acceptance criteria pass. Keep technical decision records under docs/decisions/ when needed. Do not publish features before Phase 0 is complete.

Local governance validation: `python3 .github/scripts/validate_governance.py`. This is a scaffold check, not a component test suite.

Contributions are licensed under the repository's MIT license. Report vulnerabilities using SECURITY.md rather than public Issues containing exploit details or secrets.


Every PR must have a native GitHub Development link to its corresponding Issue; a textual Refs #N mention alone is insufficient. Verify the link after PR creation and before merge. For Git Flow PRs targeting develop, set the Development link manually because closing keywords only take effect on the default branch. Keep the bootstrap Issue open until all Phase 0 acceptance criteria pass, even if a linked feature PR has merged.
