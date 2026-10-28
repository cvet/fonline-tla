# QuestInventory

Generators for the quest registry evidence described in
[Docs/Quests.md](../../Docs/Quests.md). They read authored inputs only
(`Scripts/`, `Dialogs/`, `Texts/`, `Maps/`, `Critters/`); nothing under
`Baking/` or `Cache/` is read. Script scans use the top-level `Scripts/*.fos`
scope only (generated `Scripts/Content.fos` is excluded from binding evidence).
Outputs are deterministic UTF-8/LF TSVs with one terminal newline. The default
location is next to the scripts, but `--output`/`--output-dir` accept any path,
including paths outside the project root; missing parents are created and a
repeat run is byte-stable.
Fields use standard CSV quoting with a tab delimiter, preserving embedded tabs
and quotes. Read with `csv.DictReader(..., delimiter="\t")`, not string splitting.

## `build_quest_transitions.py` — `quest_transitions.tsv` + `quest_chains.tsv`

`quest_transitions.tsv` is an **answer index, not an evaluated transition
graph**. It has one row per (quest property, dialog, speech, answer) that
mentions a `Group = Quests` property:

| Column | Meaning |
| --- | --- |
| `property` | Quest property the row indexes. |
| `dialog`, `speech`, `answer` | Source dialog and answer location. |
| `quest_demands`, `quest_results` | Every raw `Property Player`/`Property Npc` payload for this property, in source order, including operators and values. `-` when absent. |
| `other_demands`, `other_results` | Every nonmatching payload in source order, including other quest properties, items, scripts, `Or` and `NoRecheck` controls. `-` when absent. |

An answer touching several quest properties produces one row per property; a
payload for another quest property stays visible in the `other_*` columns of
each row. `+=` and similar operations remain raw: no absolute destination is
inferred, and repeated predicates are never collapsed. Only the exact `[Dialog]`
section is read. Full-line `//` comments and inline `#` preceded by whitespace
are stripped, matching `SourceExt/Dialogs.cpp`; quotes do not escape that `#`
boundary. Command names are case-insensitive and indentation-tolerant, while `[Text ...]`
and `[Comment]` blocks and speech-level `Script` commands are ignored.
The two demand columns preserve order within each column, not their relative
interleaving. In particular, `Or` controls cannot be evaluated from this index;
use the authored answer when checking logical groups or runtime behavior.
`quest_chains.tsv` aggregates the PipBoy city, dialogs and map-file families
(prefix before the first `_`) of their map bindings. The family is a maps-only
approximation, not a city or runtime-reachability proof.

## `build_quest_inventory.py` — `quests_inventory.tsv`

One row per critter declaration whose `Group` tag is `Quests`; the `Quest` and
`Max` tags are parsed independently, in either order, and are both optional.
The columns are `property`, `quest_tag`, `max_tag`, `type`, `declared_in`,
`qname_city`, `dialogs_using`, `scripts_using`, `state_texts_russ`,
`has_qname_qdesc`, `bindings_of_user_dialogs`, `reachability`; absent optional
`Quest`/`Max` tags are empty fields. The tool records the declaration
site/type/tags, PipBoy city (`QName` from `Quest.russ.fotxt` only), dialogs
using the property, outside references from top-level scripts, numeric `russ`
state-text count, the `QName`/`QDesc` flag, binding evidence and a
classification.

`has_qname_qdesc` is `yes` only when **both** `QName` and `QDesc` occur in
**both** `Quest.russ.fotxt` and `Quest.engl.fotxt` for that property. Dialog use
means actual `Demand`/`Result` `Property` payloads in `[Dialog]`; lines in
`[Text ...]` or comment blocks do not count. Binding evidence is textual:
map/`Critters` `DialogId` values, runtime `DialogId = Content::Dialog::NAME`
assignments, and `script-ref:` entries for other exact `Content::Dialog::NAME`
references (`FooDialog::NAME` does not match). Scripts are not compiled and
disabled/conditionally compiled code is still text evidence, so none of this
proves activation or runtime reachability.

Classifications:

- `bound-reference` — at least one binding reference exists; this is evidence,
  not proof that the referencing system is active.
- `unbound` — dialog(s) use the property but no binding reference was found.
- `script-only` — no dialog use, but a top-level script mentions the property.
- `no-dialog` — no dialog use and no outside-script mention.

Run with the `Generate :: Quest Inventory` / `Generate :: Quest Transitions`
tasks, or directly:

```text
py -3 Tools/QuestInventory/build_quest_inventory.py
py -3 Tools/QuestInventory/build_quest_transitions.py
```

Regenerate both after editing dialogs or quest properties and commit the TSVs
with the content change — they are review aids, not build inputs. Reference
matching uses ASCII identifier boundaries, so `SomeQuest` does not match
`SomeQuestCounter`.
