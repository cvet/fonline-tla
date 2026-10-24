# Automatic builds and manual release publication

Keep automatic push/PR validation, quality gates, native unit tests, script
compilation, content bake, platform product builds and packaging. Only the release
job runs exclusively on workflow_dispatch. Publish only a manually dispatched
master run; other manual refs remain dry runs. Serialize publishing runs without
cancelling a release in progress and retain immutable tags/assets.

Edit owners: .github/workflows/build.yml and Docs/BuildAndLaunch.md. Preserve the
existing version modification and all matrices, commands, artifact formats and
permissions. Add quality-gates to the package prerequisite list.

- [x] Implement the bounded workflow/documentation change.
- [x] Validate YAML, Actions syntax and job dependencies; check event/ref cases
      against the original workflow with wrong-behavior controls.
- [x] Confirm version preservation and final diff; no remote run/publication,
      staging, commit or push is authorized.

Private evidence: Workspace/manual-release-ci-20261024/.

Verification of the initial scope (2026-10-24): actionlint 1.7.12 passes; four event/ref cases and quality-failure
blocking pass; original auto-publisher, stale publish/cancellation and quality
bypass controls are rejected. Three release/package Bash blocks pass bash -n.
All existing check jobs, matrices, payload commands, permissions and version
bytes are preserved. No remote workflow, release, staging, commit or push was run.

Clarification on 2026-10-25: builds and packaging must remain automatic. Removed
the four dispatch-only guards from the platform/package jobs; only release
publication stays manual. Earlier verification artifacts describe the earlier
scope and remain preserved. Updated verification is recorded separately in
Workspace/automatic-build-manual-publish-20261025/.

Verification of the corrected scope (2026-10-25): actionlint passes; push/PR
automatically reach all platform builds and packaging, while the release job is
manual. Four event/ref cases and quality-failure blocking pass. Six wrong-behavior
controls are rejected, including restoring each removed job guard independently.
The YAML differs from the previous version only by removing those four guards;
publication/concurrency safeguards and the owner's VERSION bytes are unchanged.
