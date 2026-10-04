# Releases and artifacts

Phase 0 creates no npm package, version tag or GitHub Release. Its CI artifact is governance evidence, not a distributable library.

Before the first library release, AI must implement and validate:
1. Product/browser compatibility acceptance criteria and real unit, integration, accessibility, browser, API, package and security gates.
2. Versioning and changelog automation with SemVer; establish npm scope ownership and exact package name.
3. Git Flow release stabilization, release candidates, main promotion, and back-merge to develop. Hotfixes originate from main and synchronize back.
4. A publication workflow bound to verified release commits and protected version tags. Re-run deterministic tests on the exact release commit; require independent AI review. No human technical reviewers.
5. npm trusted publishing using OIDC, minimal job permissions (`id-token: write` only for the publication job), provenance and a dedicated release environment restricted to approved refs.
6. GitHub Release notes, immutable version tags, package artifact hashes, SBOM, artifact attestations, license checks and reproducible build evidence. Configure retention and access appropriate to public distribution.
7. AI-operated failure/rollback/deprecation procedures and vulnerability response. Do not enable publication from PRs or arbitrary workflow inputs.

These are required future gates, not implemented capabilities. The Phase 0 workflow deliberately contains no deploy or publish command and has no publication secrets.
