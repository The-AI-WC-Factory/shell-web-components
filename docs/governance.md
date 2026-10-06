# Git Flow and GitHub governance

## Branches and routing
- `main`: released states; only release/* or hotfix/* PRs, except the one-time Phase 0 governance promotion from develop. The initial MIT/README commit is the sole branch-seeding exception.
- `develop`: next integrated release; feature/* PRs plus release/hotfix synchronization.
- `feature/<issue>-<slug>`: branches from develop and merges into develop.
- `release/<version>`: branches from develop; stabilize through feature PRs into the release branch, then merge into main and back into develop.
- `hotfix/<issue>-<slug>`: branches from main; fix through feature PRs into the hotfix branch, then merge into main and develop (and an active release branch when applicable).

Use merge commits for release/hotfix synchronization to preserve ancestry. Avoid rebasing or squashing the long-lived integration history. Delete completed feature branches through a controlled AI operation; retain main and develop.

## Gates
Active rulesets cover main, develop, release/* and hotfix/*: PR required, conversations resolved, strict `governance` and `independent-ai-review` status checks, no force pushes or deletion, and no bypass actors. Required checks fail closed. Human code approvals and human CODEOWNERS are not used.

The independent-ai-review check accepts an APPROVED GitHub PR review from an explicitly allowed AI bot, attached to the current head SHA and distinct from the author. Provisioning that reviewer is a Phase 0 prerequisite; comments, self-review and skipped checks cannot satisfy it. Supported bot identities are in .github/ai-dlc.json; verify the actual integration identity before changing that list.

The bootstrap feature PR cannot merge before both gates pass. To promote governance into main without pretending it is a product release, an AI opens a develop → main PR titled `chore: promote Phase 0 governance`; its body links the bootstrap Issue and states `Phase 0 governance promotion`. The policy allows this route only while phase is 0 and no implementation paths exist. No tag or package is published.

## Project
Use the personal Project [Web Components 2.0 — AI-DLC](https://github.com/users/glyad/projects/1), link the repository, and track the bootstrap Issue and PR. The original organization Project is retained as migration history. Status: Todo/In Progress/Done; Phase: Phase 0/Phase 1/Release. Keep the bootstrap Issue open while any acceptance criterion is blocked. Project automation must use a dedicated narrow app/token if cross-project API access is needed; GITHUB_TOKEN alone must not be assumed to have owner-level Project access.

## Audit record
Each PR links an Issue, identifies AI execution, records check/artifact links and independent reviewer evidence. AI authors technical decisions. Product-management decisions stay in Issues. Phase 0 is not complete until enforcement, CI, independent review and branch promotion have been verified.


Every PR must have a native GitHub Development link to its corresponding Issue; a textual Refs #N mention alone is insufficient. Verify the link after PR creation and before merge. For Git Flow PRs targeting develop, set the Development link manually because closing keywords only take effect on the default branch. Keep the bootstrap Issue open until all Phase 0 acceptance criteria pass, even if a linked feature PR has merged.


## Dependency update handoff
Dependabot PRs are update candidates, not merge-ready engineering PRs. The AI maintainer creates a dedicated dependency Issue, branches `feature/<issue>-dependency-update` from develop, applies the candidate diff, opens a native Issue-linked PR with `Refs #<issue>`, and obtains governance checks and current-head independent AI approval. Link the original Dependabot candidate in that PR. Close the candidate only after the compliant feature PR merges. Never exempt Dependabot branches from Git Flow or Issue linkage.

## Approval verifier trust boundary — Phase 0 blocker
The proposed Actions review job is a diagnostic, not a tamper-proof independent approval authority: PR-defined Actions can impersonate its job name under the same Actions integration. Phase 0 must remain blocked until a dedicated trusted GitHub App publishes the required approval check on the exact reviewed PR head, and the ruleset binds that check to the App's integration ID. The App must execute no PR code, load policy from protected base code (with an explicit pinned bootstrap policy), re-fetch the PR head before reporting, reject stale approvals, retain decisions across comment-only reviews, and handle dismissal/changes requested. Required installation permissions: metadata read, contents read, pull requests read, checks write. No contents-write, administration or merge permission. App hosting, credentials and installation must be provisioned before claiming this guarantee. Do not bypass existing rules or merge the bootstrap while this blocker remains.

The runnable handoff is `.github/scripts/handoff_dependabot.py`: an AI operator runs `python3 .github/scripts/handoff_dependabot.py <candidate-pr-number> --dry-run`, then the same command without `--dry-run`. It verifies the Dependabot identity, develop ancestry, complete workflow-only diff, and unchanged refs before creating an Issue, feature branch, draft PR and native Development link. It never executes candidate code. Duplicate or partial handoffs require the AI operator to resume existing resources, rather than create duplicates. The operator validates changes, obtains AI approval, and merges through the protected gates.
