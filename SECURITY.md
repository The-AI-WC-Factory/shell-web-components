# Security policy

No production package is released during Phase 0. Supported version policy will be defined by AI before the first release.

Use GitHub's private vulnerability reporting when enabled (Security → Report a vulnerability). Do not disclose secrets or vulnerability details in public Issues. If private reporting is unavailable, do not post sensitive details; raise a product-management request to enable the channel.

AI performs security triage, remediation, testing and advisory/release preparation. The account owner handles required account consent only.

Workflows use read-only tokens by default, immutable action pins, hosted runners and no secrets for untrusted PR checks. Do not use pull_request_target to execute PR code. Publication requires a dedicated, narrowly scoped job and trusted publisher identity, not a stored long-lived npm token.
