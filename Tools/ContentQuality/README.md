# Content quality checks

These tests are static source audits for authored text packs. They ratchet known
gaps without accepting new ones. A green run does not prove translated
completeness, runtime text lookup, or quest-state reachability. The
[item component validator](#item-property-components) statically audits item
prototypes, map item instances and Item migration rules.

## English text surface

`test_english_text_surface.py` scans every `Texts/*.engl.fotxt` pack and every
`Dialogs/*.fodlg` file. Packs contain bare entries; dialogs use `[Text engl]`
sections. It reads one entry per line in the `{key}{subkey}{value}` shape and records the serialized identity
`{key}{subkey}` for each entry whose value contains a Cyrillic character
(U+0400..U+04FF). Scanning starts at a standalone `[Text engl]` header line and
ends at the next standalone bracket header line, so a literal `[` inside entry
text does not hide later entries. Files are decoded as strict UTF-8 with
`utf-8-sig`: a BOM is accepted and malformed bytes fail the audit.

`Tools/ContentQuality/english_text_baseline.json` records the only permitted
historical backlog for the scanned surfaces. It has exactly two members:

- `cyrillic_entries` maps a repository-relative POSIX path to the exact list of
  offending `{key}{subkey}` identities.
- `dialogs_without_english_block` lists dialogs with no `[Text engl]` section.

Both contract tests compare the current sets with the baseline exactly. There is
no count budget and no pack-filename ceiling whitelist. A new untranslated
identity fails even when an old identity was corrected in the same change, and a
new clean `*.engl.fotxt` pack needs no baseline entry.

### Baseline workflow (shrink only)

The tests never write or regenerate the repository baseline, and there is no
bless or update command. When English text is authored:

1. Translate the entry, then delete only its literal `{key}{subkey}` string from
   the matching path in `cyrillic_entries`.
2. If a path's list becomes empty, remove the path entry; the observed offender
   map does not contain paths with no remaining identities.
3. When a dialog gains a usable `[Text engl]` section, remove its path from
   `dialogs_without_english_block`. The new section is still scanned: any
   Cyrillic identity in it is a new failure, not an automatic baseline entry.
4. Never add a path or identity to admit an untranslated value. Correct the text
   or keep the failure.

The 2026-10-28 baseline snapshot observed 526 files with Cyrillic English
identities (6 packs and 520 dialogs; 1,572 distinct pack identities and 16,269
dialog identities) and 63 dialogs without an English section. The older
481-dialog ceiling undercounted because splitting at any `[` discarded content
after a literal bracket. These counts are dated notes, not acceptance
conditions; the tests compare exact sets.

## Quest text coverage

`test_quest_text_coverage.py` discovers properties declared in `Scripts/*.fos`
with `Group = Quests`; the optional `Quest` tag is not required. For every
declared property it requires, in both `Texts/Quest.russ.fotxt` and
`Texts/Quest.engl.fotxt`:

- at least one nonzero numeric state key (`isdigit()` and greater than zero),
  so `QName` or `QDesc` metadata cannot substitute for state text;
- both `QName` and `QDesc` keys, checked individually in each language.

It also freezes exact missing-metadata and Russian-only key tuples and rejects
orphan `CritterProperty::*` entries whose property has no live declaration in
either language pack. The lowercase `Qdesc` in the Russian pack is a historical
typo recorded as a key tuple, not permission to reinterpret case.

The quest constants are exact baselines too: remove a missing-metadata tuple
once that key exists, and remove a Russian-only tuple once the English key is
added. Never replace a tuple with a property-level allowance that could hide a
different missing key for the same property.

## Why count ceilings were unsound

Aggregate ceilings let one corrected old key pay for a new untranslated key
under an unchanged total: the old English tests compared only per-pack counts,
a total dialog-offender count, and a missing-block count. Property-level quest
gaps were equally maskable because a known property could acquire another
missing state or metadata key. Per-file identity sets, exact missing-file sets,
and exact language/property/key tuples remove those escapes.

## Syntax and static limits

- Entries must stay one per line and start at column zero; trailing spaces/tabs
  after the closing brace are accepted. Values may contain
  braces, brackets and Cyrillic text, but the parsers do not support multiline
  values or indented entry lines.
- A dialog section header must be a standalone line such as `[Text engl]`; a
  bracket inside an entry value is ordinary text. Bare `.fotxt` entries need
  no language header; the filename selects their language. The missing-section
  list covers dialogs only.
- The English scan detects only literal U+0400..U+04FF characters. It does not
  judge translation quality, prove that a key is used, or replace runtime text
  validation.
- The quest check audits declarations and pack entries only. It does not prove
  engine behavior, runtime quest state reachability, or translation quality.
- Baseline data and known-gap constants are historical evidence. Shrink them as
  defects are fixed; do not expand them to obtain green tests.

## Item property components

`validate_item_components.py` checks the
[property-component convention](../../Docs/Scripts.md#property-components) in
`Items/**/*.foitem`, item instances (`[.../Item]` sections with `$Proto`) of
`Maps/*.fomap` and `Scripts/Migration.fos`. It reads `///@ Property Item`
declarations from `Scripts/**/*.fos` except `Scripts/Generated/`. Prototype
values resolve like the baker: ancestors depth first, direct parents left to
right, the child last, a repeated ancestor only at its first reach. Map
instances take markers from their prototype. Static means effective
`Static = True` or the legacy `IsStatic = True`.

A rule that involves an undeclared component is inactive, so declaring a kind
marker activates its checks. The kind components are Armor, Drug, Weapon, Ammo,
Key, Container, Door, Grid and Car. Every finding is an error:

| Code | Reported when |
| --- | --- |
| `legacy-prefixed-key` | A key `<C>_<F>` names a declared component `<C>`; author `<C>.<F>`. |
| `legacy-type-key` | A `Type` key remains after `Item.Type` is no longer declared. |
| `transition-mismatch` | While `Type` is declared, effective `Type = X` and marker `X` disagree for a declared kind component. |
| `field-without-marker` | `<C>.<F>` is authored where the effective prototype marker `<C>` is not true. |
| `marker-on-instance` | A map item instance authors a component marker. |
| `exclusive-kind` | More than one kind marker is enabled. |
| `locker-mismatch` | `Locker` without `Door` or `Container`, or the reverse; active once all three are declared. |
| `static-mismatch` | `Grid` on a non-static prototype, or another kind on a static one. |
| `missing-migration-rule` | A manifest name is no longer declared and `Scripts/Migration.fos` lacks `MigrationRule Property Item Rename` or `Remove` for it. |
| `dangling-migration-target` | A project `Property Item Rename` target is neither a script-declared Item property nor an Engine `ItemProperties` field. |

`Item.Type` is no longer declared (2026-11-01), so `legacy-type-key` is active
and `transition-mismatch` is inactive; the transition check stays for older trees.

Key findings point at the authored key line. `exclusive-kind`, `locker-mismatch`,
`static-mismatch` and `transition-mismatch` are reported per resolved prototype at
its section line, so a parent defect repeats on each child.

`item_component_legacy_names.txt` is the frozen manifest of legacy Item names
captured on 2026-10-31 before the component migration: 111 flat
`<Kind>_<Field>` properties plus `Type`, `CarIsBioEngine`, `CarIsNoLockpick`
and `IsLockpick`. Never edit or regenerate it to silence a finding; add the
migration rule. Only the project rule file counts for `missing-migration-rule`;
Engine rules and `Transform` actions are not consulted.

Limits: missing parents, cycles, duplicate ids and unknown instance prototypes
are left to the baker. `+=` lines are not parsed, and backslash-continued lines are not joined.
A clean run does not prove that saved documents migrate at runtime or that
scripts guard component access.

```text
py -3 Tools/ContentQuality/validate_item_components.py --summary
py -3 Tools/ContentQuality/validate_item_components.py --root <project-root>
```

Without `--summary` each finding is printed as `path:line: [code] message`. The
exit code is 1 when anything is reported. VS Code task: `Analyze :: Item Components`.

## Commands

Run from the repository root:

```text
python -m pytest Tools/ContentQuality
python -m pytest Tools/ContentQuality/test_english_text_surface.py
python -m pytest Tools/ContentQuality/test_quest_text_coverage.py
python -m pytest Tools/ContentQuality/test_content_quality_regressions.py
python -m pytest Tools/ContentQuality/test_validate_item_components.py
```

`test_content_quality_regressions.py` builds owned temporary full-shape roots
and literal baselines, drives the actual contract tests, verifies rejection and
acceptance cases, and cleans its temporary roots.
