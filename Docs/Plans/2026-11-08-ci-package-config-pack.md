# CI repair: package job, Metadata config pack

**Goal:** Fix the failing `package` job of GitHub Actions run `42354305213`
(push `603d113a`, Engine `0d1a56de63` / 2026.1.114-dev) without regressing the
passing jobs.

**Architecture:** Align the `TLA.fomain` pack layout with the Engine's packaging
contract (configs live in the `Metadata` pack) and verify that bake output and
packager inputs agree.

**Requirements:** Engine
[baking guide](../../Engine/Docs/en/explanation/content-pipeline/baking.md#built-in-baker-types),
[configuration reference](../../Engine/Docs/en/reference/settings/configuration-and-data-sources.md#packaged-application-configuration),
[integration procedure](../DocumentationMaintenance.md#engine-submodule-updates).

## Constraints

- No staging, commits, push or Engine edits. Preserve the owner's other work.
- Sub-configs, settings and the other pack declarations stay unchanged.
- A bake writer must not overlap a consumer.

## Evidence

Run `42354305213`: 20 jobs green (including `unit-tests`, fixed upstream by
Engine `0d1a56de63`), `package` failed, `release` skipped. Log of `package`
(public job id `128358741865`, read with the owner-provided token, read-only):

```
[Package] Make Client (LocalTest) for Windows
  File ".../Engine/BuildTools/package.py", line 1502, in read_config_data
    assert os.path.isfile(config_path), 'Config file not found'
AssertionError: Config file not found
```

`read_config_data` looks for `<Baking>/Metadata/<config>.fomain-client|server`.
TLA bakes configs through a separate server-only pack `Configs` with
`Bakers = Config`, so the file sits in `Baking/Configs/` instead. Engine
2026.1.98-dev (changelog, Migration) already required a shared `Metadata` pack
with `Bakers=Metadata Config ClientConfig` and moved config outputs into
`Baking/Metadata`; that migration was not carried into `TLA.fomain`, and local
`Verify :: All` does not run `MakePackage-*`. `MakePackage-Dev` passes only
because its binaries are `NoRes` (no resources, no config read); `Test` uses
`Raw` resources.

## Change

`TLA.fomain`: `Metadata` pack `Bakers = Metadata Config ClientConfig`; remove
the `Configs` pack.

## Steps and acceptance

- [x] Read the failing job log; identify the exact assertion and its owner.
- [x] Change the pack layout.
- [x] Force a complete bake; warning-free; `Baking/Metadata` contains every
  `<SubConfig>.fomain-client/server` and the compact profiles.
- [x] Execute the packager's config step against the new bake output.
- [x] Rebuild checks that depend on the layout (harness, unit tests, script and
  format gates).
- [x] Record results and qualification limits.

## Verification record

Evidence root: ignored `Workspace/ci-package-20261108/`.

- `cmake --preset auto` and `ForceBakeResources`: exit 0, "Baking complete!",
  no warnings. `Baking/Configs` is gone; `Baking/Metadata` holds
  `(Root)`, `LocalTest`, `PublicGame` and `Unpackaged` `.fomain-client/server`
  plus `-embedded-client/server`, and all four `LocalTest` files are listed in
  `Resources.usage.json`.
- The failing step, run locally the way CI runs it (`package.py -target Client`
  and `-target Server`, `-pack Raw -config LocalTest`, real build hash): it now
  passes `read_config_data` (`Config LocalTest.fomain-client`,
  `Embedded config LocalTest.fomain-embedded-client`, length 5640 /
  `LocalTest.fomain-server`) and starts building resource packs. I stopped both
  runs at the 2-minute limit while packing the large `FOArt` pack, so full
  package completion is not locally proven; the rest of the CI step (packing,
  `MakePackage-Dev` already passes) was not changed by this fix.
- Rebuilt `TLA_ServerHeadless`, `TLA_Client`, `TLA_UnitTests`: exit 0, no
  warnings. Harness `COMPLETE: 128 passed, 0 failed, 0 skipped (of 128)`;
  `TLA_UnitTests.exe` exit 0 (`assertions: 1326909 | 1326909 passed`).
- Script ratchet, nullable validator, `pytest Tools` (220 passed, 89 subtests),
  fomain formatter (0 changed), `git diff --check`: clean.

Qualification limits: Windows x64 only; no Linux `MakePackage-Test` run (CI is
the proof); `release` stays unexercised (workflow_dispatch only).
