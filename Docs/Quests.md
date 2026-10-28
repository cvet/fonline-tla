# Quests

How TLA quests are actually implemented: state representation, executors,
progress display, and a per-quest technical card format. Read
[Dialogs](Dialogs.md) for the dialog runtime that executes most quest
transitions. Verified against sources at revision `e2b5b90b0` (static
analysis); the verification boundary is restated at the end.

## Architecture

There is **no quest registry object and no per-quest file requirement**. A
quest is a contract between four pieces:

1. **State**: one critter property per quest, declared with
   `Group = Quests`, e.g. `Scripts/CritterProps.fos`
   `///@ Property Critter Common uint8 KlamBobWater Mutable OwnerSync
   Persistent Group = Quests Quest = 3201 Max = 3`. The bulk (109 at this
   revision) lives in [Scripts/CritterProps.fos](../Scripts/CritterProps.fos);
   a few quests declare their property inside their owning module instead
   (e.g. `KlamKuklachev` in `Scripts/KlamJura.fos`). Tag meanings:
   - `Persistent` — saved with the player; `OwnerSync` — replicated to the
     owning client. Value `0` is the universal "not started" state
     (the PipBoy skips zero values).
   - `Group = Quests` — puts the property into `CritterPropertyGroup::Quests`,
     the only list the UI and client setter iterate.
   - `Max = N` — a real value limit enforced by the property registrar.
   - `Quest = N` — **documentation-only**: the Engine property parser accepts
     and skips it (`Engine/Source/Common/Properties.cpp`, `Quest` tag branch);
     nothing consumes it at runtime. Note `TLA.fomain:44` still lists a
     `QuestRuntime` namespace in `AngelScript.MutableGlobalsAllowedNamespaces`
     that no longer exists anywhere in the tree.
2. **Executors**: dialog answers (`Result Property Player X = N`, `Result Item
   Player pid ±= n`, `Result Script Namespace::Func` — applied server-side by
   `Dialogs::UseAnswerResults`, see [Dialogs](Dialogs.md)) and direct script
   writes (`cr.KlamBobWater = ...`) in the quest's server module. Dialog
   demands gate the transitions (`Demand Property Player X == N`).
3. **Texts**: `Texts/Quest.russ.fotxt` / `Quest.engl.fotxt` map state to
   player-visible progress: `{CritterProperty::X}{N}{text}` per state value,
   `{CritterProperty::X}{QName}{City}` and `{...}{QDesc}{summary}`. Text ids
   are two-token identities: property prefix and state/`QName`/`QDesc`.
   The new `Tools/ContentQuality/test_quest_text_coverage.py` checks declared
   properties and known pack gaps; it does not prove that every reachable
   state is translated or displayed correctly.
4. **Display**: on every quest-property change the client property setter
   `Parameters::CritterSetPropertyQuests` (`Scripts/Parameters.fos:282`) looks
   up the two-token Quest pack key and shows the progress message. The PipBoy
   quest list (code in `Gui/PipBoy.fogui`, generated into
   `Scripts/Generated/GuiScreens.fos`) attempts to group non-zero properties
   by city and render description/status. That path still calls legacy
   `QuestNameTextId`/`QuestDescTextId`/`QuestStatusTextId`, which sum hashes
   or add the state, then pass a single numeric token to `GetQuestText`.
   This differs from the authored two-token keys used by the property setter.
   The guide therefore does not establish a working PipBoy quest display;
   fixing and exercising that consumer is a separate gameplay/UI task.

Most quests are dialogue-driven: an NPC on a map carries
`DialogId = <name>` (map instance override or runtime `cr.DialogId = ...`),
the dialog's demands branch on the quest property, and its results advance
it. Timed/reset behavior lives in the quest's server module via
`[[TimeEvent]]`/`[[DialogResult]]` functions called from the dialog.

## Card format

Each card below records: identity, files, activation evidence, state space,
the transition table (state × event → actions → new state), side effects,
dependencies, and how to verify a change.

The machine-readable registry is
`Tools/QuestInventory/quests_inventory.tsv` (regenerate with
`Generate :: Quest Inventory`, see [the tool](../Tools/QuestInventory/README.md)):
**165 quest properties** — 158 **bound-reference** (a dialog has a map/proto
`DialogId`, runtime assignment or textual `Content::Dialog::*` reference),
1 **unbound** (`KlamKuklachev` — dialog exists, no binding in the scanned
authored source corpus), 6 **no-dialog** (no dialog property use; `QWarehouse*`,
`KlamDantonBramin`, `KlamSmilyGecko`, `V13Dclaw` — the last two are only
declared, with no standalone consumers found). A binding reference is not a
reachability proof: the referencing system may be dormant
(e.g. `ModAurelianoCaravanEscort` is only spawned by the currently disabled
Caravan system, see [World](World.md#caravans-disabled)); conversely, prove
unreachability by an exhaustive search like the card below before deleting
content. Transition tables extracted from the dialogs live in
`Tools/QuestInventory/quest_transitions.tsv` (see
[Quest chains](#quest-chains) below). Cards here cover the contract pattern
and representative quests.

## Card: `KlamBobWater` — "Get distilled water for Whiskey Bob" (bound content)

- **Identity**: property `KlamBobWater` (`CritterProps.fos:401`, `Quest = 3201`,
  `Max = 3`, uint8). Texts: `Texts/Quest.engl.fotxt:30-35` (QName `Klamath`).
- **Files**: `Dialogs/klam_bob.fodlg` (Whiskey Bob, giver/completion),
  `Dialogs/vc_melinda.fodlg` and `Dialogs/vc_garry.fodlg` (Vault City,
  pointer + supplier). No dedicated script module; all transitions are dialog
  results.
- **Activation evidence**: Bob is a static map instance —
  `Maps/klamath.fomap` critter `$Proto = AverageMerchantMale` with
  `DialogId = klam_bob`, `InitScript = Trader::TraderInit`, `BagId = 16`.
  Garry/Melinda are also bound in `Maps/vcity_courtyard.fomap`.
  All three dialogs are baked via the `Dialogs` pack inputs
  (`TLA.fomain` packs `Texts`/`ServerData` include `Dialogs`).
- **State space**: `0` not started, `1` accepted (Bob wants 20 flasks),
  `2` water acquired, `3` delivered. No fail/reset path; the property never
  decreases.
- **Transitions** (all executed by `Dialogs::UseAnswerResults` server-side;
  demands re-checked anti-cheat in `Dialogs::SpeechAnswer`):

| State | Event (dialog node) | Conditions | Actions | New state |
| --- | --- | --- | --- | --- |
| 0 or 1 | Bob `Speech 19 → Answer Exit` | `KlamBobWater < 2`; normal route reaches 18/19 via Bob's no-stock DenJaneVodka branch | `KlamBobWater = 1` | 1 |
| 1 | Melinda `Speech 2 → Answer 3` (`vc_melinda.fodlg:10`) | `== 1` | — (points to Garry) | 1 |
| 1 | Garry `Speech 4 → Answer 5` (`vc_garry.fodlg:19-22`) | `bottle_caps > 199` | `bottle_caps -= 200`; `bottle_full += 20`; `KlamBobWater = 2` | 2 |
| 2 | Bob hub `Speech 6 → Answer 20` (`klam_bob.fodlg:54-62`) or `Speech 17 → Answer 20` (`:112-120`) | `== 2` and `bottle_full > 19` | `bottle_full -= 20`; `bottle_caps += 400`; **NPC** `booze += 200`, `bottle_caps -= 400`; `Experience += 1500` (hub) or `+300` (side node); `KlamBobWater = 3` | 3 |
| 3 | No further `KlamBobWater` write in these dialogs | — | — (terminal quest state; no dedicated `== 3` greeting) | 3 |

  Note the source choice matters: both completion nodes exist and the hub one
  grants 5× the experience. `bottle_full` (`Items/bottle_full.foitem`) is the
  only accepted goods item. Delivery still requires state 2, which Garry's
  purchase sets; once there, any 20 flasks satisfy the item check. NPC-side
  `Result Item Npc ...` mutate Bob's real container inventory.
- **Dependencies**: shared Klamath hub demands (`DenJaneVodka`, `DenLeannaBuy`
  answers coexist in Bob's hub); `Trader::TraderInit` gives Bob his trader
  inventory/bag. Cross-location: quest text appears under `Klamath` in PipBoy.
- **Verification for changes**: re-read the two completion nodes together
  (reward duplication risk); run `Compile AngelScript` + `Bake Resources`
  after dialog edits (dialog text is baked), then in-game: accept → buy →
  deliver through the normal dialog path. Native dialog parser tests do not
  prove this authored quest's rewards or player route.

## Card: `KlamKuklachev` — "Find Cat's Paw journals" (unreachable content)

- **Identity**: property `KlamKuklachev` declared in the owning module
  `Scripts/KlamJura.fos` (`Quest = 145`, `Max = 3`, int32 — not uint8).
  Texts: `Texts/Quest.engl.fotxt` `{CritterProperty::KlamKuklachev}{1..3}` +
  QName/QDesc (Klamath).
- **Files**: `Dialogs/klam_jura.fodlg` (Юрасик Долл), `Scripts/KlamJura.fos`
  (`[[DialogResult]] Replay` starts a 10–30 game-minute `[[TimeEvent]]` that
  resets the property to 0 — a repeatable-quest pattern).
- **Static binding search**: literal searches for `klam_jura` and
  `KlamKuklachev` in `Scripts`, `Dialogs`, `Maps`, `Critters` and
  `Resources/ServerData` find the quest module/dialog and generated content
  declaration, but no map/proto `DialogId` or script binding of that dialog.
  This supports classifying the authored giver as unbound, within that corpus;
  it is not a runtime reachability test. The content is dormant, not deleted.
  Re-enabling means binding the dialog to an NPC
  (map instance or spawn script).
- The card is kept because its reset-by-timer pattern (`KlamJura::Replay` →
  `ResetVar`) is the reference implementation for repeatable dialog quests.

## Quest chains

`Tools/QuestInventory/quest_transitions.tsv` indexes dialog answers that
mention a quest property. `quest_demands` and `quest_results` retain all
matching payloads, subjects and operators; `other_*` retains the other
quest conditions/actions and control markers. This is not an evaluated
state graph: cross-column interleaving and speech/script side effects still
need the authored source. TSV fields use standard CSV quoting with a tab
delimiter. `Tools/QuestInventory/quest_chains.tsv` aggregates
per quest: its PipBoy city, dialogs and the map families those dialogs are
bound to. Regenerate both with the `Generate :: Quest Transitions` task
after dialog edits (see [the tool](../Tools/QuestInventory/README.md)).

Snapshot at the corrected 2026-10-28 regeneration: 1684 answer/property rows
for 159 dialog-driven quests (the earlier extractor emitted 1669 rows):

- City distribution by `QName`: Den 41, NCR 21, Vault City 20,
  San Francisco 13, Redding 13, Klamath 10, Arroyo 8, Modoc 7, Primitive
  Tribe 6, Broken Hills 4, then 3-and-below for New Reno, Navarro, Vault 13,
  the replicator station and quest-line groupings ("Best Wasteland Hunter").
- **48 properties have bindings in multiple map-file families**. Family
  prefixes are an approximation; this count does not prove 48 distinct
  cross-city journeys. Representative authored chains include supply runs out of Den
  (`DenJane*` — James buys goods sourced in Klamath, Modoc, Redding, New
  Reno), `KlamBobWater` (Klamath ↔ Vault City, card above),
  `BHMarcusEscort` (Broken Hills ↔ New Reno), `ArroyoCassidyLetter` and
  `ArroyoLetterToLinnett` (Arroyo ↔ Vault City).
- Two quests group under the literal city `TODO`: `MainQuest` and `QChosen`
  — the story-line quests of the disabled intro
  (`Story.MainStoryLineActive = False`, see
  [PlayerLifecycle](PlayerLifecycle.md)); treat the grouping as a content
  placeholder, not a shipped city.

## Adding or changing a quest

1. Declare/extend the property (`CritterProps.fos` or the owning module) with
   `Group = Quests`, `Max`, `Persistent`, `OwnerSync`; the property name is a
   save/serialized contract — renaming needs a migration.
2. Author the dialog transitions; every promised reward must be an actual
   `Result`/script effect — a reward mentioned only in reply text does nothing.
3. Add Quest pack entries for every reachable non-zero state, both languages
   (`russ engl` parity is guarded by `Tools/ContentQuality`), including
   `QName`/`QDesc`.
4. Bind the NPC: `DialogId` on a map instance (`[$Name/Critter]` block) or a
   runtime assignment; check `BagId`/`InitScript` for trader inventory.
5. Verify: `Compile AngelScript`, `Bake Resources` (dialogs are baked twice —
   client text pack and server pack), then walk the quest through the normal
   dialog path in a client; property layout changes require a force bake.
   Static discovery alone does not prove the quest is reachable — search for
   the dialog binding like the unreachable-card proof above.
