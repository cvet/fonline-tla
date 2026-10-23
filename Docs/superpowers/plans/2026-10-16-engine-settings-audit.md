# Engine settings ownership and relevance implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Remove the two project-owned day-curve settings from Engine and audit every remaining native setting for an actual owner and consumer.

**Architecture:** TLA owns constant default time/color arrays in `DayColor.fos`. Its existing script evaluates them and submits colors through `Map.SetDayColors`; the generic runtime `Map.GlobalDayColor` property remains. Project settings currently accept scalar base types, so the migration does not add array-valued project settings. The audit distinguishes active runtime/build settings, conditionally active features, public script inputs and settings without a verified consumer.

**Tech Stack:** C++, AngelScript, Python tools, CMake, official MiMo CLI.

**Spec:** Current user request to remove `GlobalDayColorTime` / `GlobalDayColor` from Engine and audit all other settings; prior instruction to keep game policy in the project. The request authorizes implementation, not speculative deletion of unrelated settings.

## Global constraints

- Preserve both dirty worktrees and all prior changes; no staging, commits or pushes.
- Keep TLA's four time keys `300 600 1140 1380` and channel-major palette `18 128 103 51 18 128 95 40 53 128 86 29` unchanged.
- Preserve independent per-map overrides, fixed map time, global time and client/mapper updates.
- Preserve generic `Map.SetDayColors` and the resulting `Map.GlobalDayColor`; remove only the two configuration declarations.
- Use existing code style, empty lines around control flow and semantic stages, Russian script comments, and the owning file's final-newline convention.
- The initial MiMo migration assignment was cancelled with zero edits after Codex found an invalid array-setting assumption. Codex implemented the migration; MiMo owned the bounded independent audit. Codex owns shell/Git/build/tests, native contracts, artifacts and final conclusions. One worker at a time; no concurrent writes or builds during its handoff.
- Audit all `SETTING` declarations in `Engine/Source/Common/Settings.inc`, including platform, backend, startup/internal and packaging consumers. Check both full keys and actual member reads; declaration/docs/test hits alone do not prove a live production consumer.

## Review focus

- An empty map curve must use the same project palette, while an authored map curve retains priority independently for times and colors.
- Both CLIENT and MAPPER must compile and update map tint; SERVER must retain shared pure-function/default-selection tests.
- Native array-setting tests must use neutral inputs or test-owned metadata instead of retaining game configuration as a fixture.
- A setting without a TLA reader may still be required by another backend, platform, generic script API, host bootstrap or packager.
- Inventory coverage must reconcile exactly with parsed declarations and show unresolved cases explicitly.

## Task 1: Project day-curve ownership

**Files:** `Scripts/DayColor.fos`, `Scripts/Tests/Test_DayColor.fos`, `TLA.fomain`.

- [x] Declare constant default time/color arrays in `DayColor.fos`; remove the two config keys and migrate script readers.
- [x] Add shared selection helpers and regressions for empty-map defaults and nonempty map overrides, preserving interpolation tests.
- [x] Review the cancelled MiMo attempt against its captured baseline (zero edits); Codex completes the corrected constant-array design and verifies compilation/baking/harness.

## Task 2: Native contract removal and neutral coverage

**Files:** Engine `Source/Common/Settings.inc`, `Source/Tests/Test_Settings.cpp`, `Source/Tests/Test_ScriptBuiltins.cpp`, `Source/Tests/Test_ManagedScriptBaker.cpp`, three affected example configs; owning EN/RU migration/changelog and generated contract artifacts.

- [x] Remove native settings and example entries. Preserve array-binding coverage with neutral/test-owned inputs.
- [x] Regenerate owning API/reference metadata, translations and dispositions; record removal in the current uncommitted release.
- [x] Run affected native tests and contract/documentation checks.

## Task 3: Complete settings audit and acceptance

**Deliverable:** `Docs/EngineSettingsAudit.md`, with an exhaustive per-setting inventory and evidence for findings.

- [x] Build an inventory for every native setting and check consumers across Engine Source/BuildTools/Examples and TLA Scripts/SourceExt/config/tooling.
- [x] Inspect candidate unused or game-owned settings beyond textual matches; distinguish evidence, inference and coverage gaps.
- [x] Obtain a bounded independent MiMo audit of the inventory/candidate findings, review it and reconcile coverage.
- [x] Run `Verify :: All`, affected visible client/mapper tint checks, and final source/reference audit. Report any failed gate without masking it.
- [x] Save MiMo retrospective reports outside the repository and summarize final changes, audit findings and verification.

Final acceptance: Verify :: All passed (588 native cases, 110 script cases, 156 Python tests / 82 subtests); 19 focused docs tests and 412-page Engine docs validation passed. Native API and contract checks passed. Actual Mapper fallback noon/dawn and normal client registration/render passed with clean diagnostics and preserved caches. Independent audit original report accepted 5/5; the cancelled invalid-design attempt remains recorded separately. Managed-specific tests remain not_run in the disabled TLA backend. No commits/staging/push.
