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
Use the organization Project named `Web Components 2.0 — AI-DLC`, link the repository, and track the bootstrap Issue and PR. Status: Todo/In Progress/Done; Phase: Phase 0/Phase 1/Release. Keep the bootstrap Issue open while any acceptance criterion is blocked. Project automation must use a dedicated narrow app/token if cross-project API access is needed; GITHUB_TOKEN alone must not be assumed to have organization Project access.

## Audit record
Each PR links an Issue, identifies AI execution, records check/artifact links and independent reviewer evidence. AI authors technical decisions. Product-management decisions stay in Issues. Phase 0 is not complete until enforcement, CI, independent review and branch promotion have been verified.
