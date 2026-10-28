# Dialogs

The dialog system: the `.fodlg` authoring format, the server runtime that
checks demands and applies results, the native baker, and the authored
handler library. Quest state transitions ride on this system — see
[Quests](Quests.md). Routing overview: [Systems](Systems.md). Verified
against revision `e2b5b90b0` (static analysis).

## Shape

| Piece | Owner |
| --- | --- |
| `Dialogs/*.fodlg` | Authored dialogs (859 files at the source baseline): speech graph, demands/results and language text blocks; some existing English blocks are missing. |
| [Scripts/Dialogs.fos](../Scripts/Dialogs.fos) | Server runtime: `RunDialog`, `SpeechAnswer` RPC, `CloseDialog`, demand/result evaluation (`CheckAnswerDemands`, `UseAnswerResults`), dialog context component; client context receiver. |
| [Scripts/Dialog.fos](../Scripts/Dialog.fos) | Authored handler library: `[[DialogDemand]]`/`[[DialogResult]]` functions dialogs call by name. |
| `SourceExt/Dialogs.cpp/.h`, `SourceExt/DialogBaker.cpp` | Project native: `.fodlg` parser and baker ([NativeExtensions](NativeExtensions.md)). |
| `SourceExt/ServerExtension.cpp:233-345` | Native bridge: `Game.RunSpeechScript`, `Game.DialogScriptDemand`, `Game.DialogScriptResult` — find AS functions by name and verify their attributes. |
| `SourceExt/TestDialogs.cpp` | Native unit tests for dialog value normalization (`@token`, `Content::*`, boolean `0/1` spelling). |
| [Scripts/NpcDialog.fos](../Scripts/NpcDialog.fos) | Separate system: autonomous NPC-to-NPC barks (table-driven phrases + scene triggers), not player dialogs. |
| `Gui/Dialog.fogui` | Client dialog screen (modal talk UI). |

Baking (see [TLA.fomain](../TLA.fomain) packs): the `Texts` pack bakes
`Dialogs/` with the `DialogText` baker into client text packs keyed
`TextPackName::Dialogs` + dialog id + text id; the server-only `ServerData`
pack bakes `Dialogs/` with the `Dialog` baker into runtime `DialogPack`s.
Editing a dialog therefore requires a bake before both sides see it.

## The `.fodlg` format

```text
[Comment]
Free-form notes.

[Dialog]
Speech <id>                      # node; Speech 1 routes to the first matching answer
  Script Ns::Func                # optional speech script: fills TextArgs
  Answer <link> # comment        # next Speech id, or Exit / Exit* variants
    Demand Property Player KlamBobWater == 2
    Demand Item Player bottle_full > 19
    Result Property Player KlamBobWater = 3
    Result Item Player bottle_caps += 400
    Result Item Npc booze += 200
    Result Script Dialog::AttackPlayer

[Text russ]
{Name}{}{Боб}
{DescAliveShort}{}{...}
{Speech 18}{}{...}
{Speech 18 Answer 19}{}{...}

[Text engl]
{Name}{}{Whiskey Bob}
{DescAliveShort}{}{...}
{Speech 18}{}{...}
{Speech 18 Answer 19}{}{...}
```

- **Answer labels**: `Answer 18` links to `Speech 18`; `Exit` closes (the
  parser canonicalizes `Exit`/`Exit*` spellings, `SourceExt/Dialogs.cpp:96`);
  `*` suffixes on any label only disambiguate multiple answers with the same
  target within one speech. The special links `Barter` (-2) and `Attack` (-3)
  come from the `///@ Enum DialogAnswerLink` metadata in
  `Scripts/Dialogs.fos:35-36` and must stay globally visible for the baker.
- **Demands**: conditions normally form an AND sequence, with explicit OR
  markers handled by the runtime. `Property Player|Npc <prop> <op> <value>`
  compares a property by index (`< > = ! } {` and accepted spellings in the parser);
  `Item Player|Npc <pid> <op> <n>` compares stack counts via
  `ItemStacks::CountItem`; `Script Ns::Func [args]` calls a
  `[[DialogDemand]]` function. `Demand` on properties of the *main-slot item*,
  the *location*, the *map* or a *global* also exist in the runtime
  (`DR_PROP_ITEM/LOCATION/MAP/GLOBAL`), though authored files mostly use
  critter properties and items. A `DR_OR` token after a failed demand forgives
  the failure group (OR semantics). `NoRecheck` marks demands skipped during
  the anti-cheat recheck.
- **Results**: `Property` with `= + - * /`; `Item` with `= + - * /` — applied
  as a count delta through `ItemStacks::AddItem`/`DestroyItem` (never below
  zero); `Script Ns::Func [args]` calls a `[[DialogResult]]` function; an
  nonzero `int` result overrides the next speech id; zero preserves the
  current answer link.
- **Arguments** in script demands/results are baked as legacy generic values:
  `NormalizeDialogScriptValue` strips a leading `@` or the `Content::*`
  prefix, retaining the final token name as a string-backed generic value.
  Consumers perform their required conversions; this is not eager hash-ID
  resolution. Property booleans compare as `0/1`.
- **Text blocks**: entries keyed `Speech <id>` and `Speech <id> Answer
  <label>`; `{Name}`, `{DescAliveShort}`, `{DescAliveFull}` feed critter
  name/description. Inline tags `@sex@|male|female|` and `@pname@` are
  substituted client-side by `Game.FormatTags(text, textArgs, talker)` from
  the `TextArgs` string produced by the speech script.

## Runtime flow (server)

1. **Entry points**: the ordinary path is the action-cursor talk action
   (`Scripts/DropMenuHandler.fos:319` → `Dialogs::RunDialog`). Scripted
   entries: doors (`Scripts/Item.fos:123` `DoorAutoDialog`), bases
   (`Scripts/Base.fos:256`), events (`GameEventRacing`, `DenGhost`), item use
   (`Scripts/ClientItems.fos:615`), energy barriers, etc.
2. **`RunDialog(cr, talker, ignoreDistance)`** (`Scripts/Dialogs.fos:58`):
   the talker must have a `DialogId` and both must pass `IsCrittersCanTalk`
   (alive, same map, distance ≤ `TalkDistance`/`Dialog.TalkDistance` = 3).
   Speech 1 is a *router*: its first demand-passing answer's results run, and
   its link selects the actual first visible speech (the classic
   "Преддиалоговые установки" pattern). A speech with no visible answers is
   spoken over the NPC's head (`Messaging::Say`) instead of opening the UI.
3. **Context**: talking state lives in the `DialogContext` critter component
   (dialog id, talker, current/previous speech, visible answer indices,
   deadline, TextArgs). A 1-second repeating time event (`ProcessDialog`)
   closes the dialog when the critter moves, the `Dialog.TalkMaxTime`
   (100 s) elapses, or the talker breaks distance rules (unless
   `ignoreDistance`).
4. **Answer selection** (`SpeechAnswer` `[[ServerRemoteCall]]`,
   `Scripts/Dialogs.fos:162`): the client sends an *index* into the visible
   answer list. The server closes on close/barter pseudo-indices, re-evaluates
   demands of the current speech's answers with `recheck = true`, skipping
   `NoRecheck` demands (anti-cheat;
   the chosen answer must still pass), applies the answer's results, then
   follows the link — including pseudo-links back (`-1`), barter (`-2` →
   `Barter::StartNpcBarter`), and `0` = close. `Attack` (`-3`) is parsed but
   its transition handler is an unimplemented TODO; it does not attack.
   `Result Script Dialog::AttackPlayer` is a separate implemented action.
5. **Lifecycle safety**: `InitDialogs` subscribes to knockout/dead/finish and
   closes the dialog. The answer path checks `Talking` and `DialogId` after
   callbacks; do not generalize that to detecting every same-pack speech switch.
6. **Client**: `ReceiveDialogContext` (`Scripts/Dialogs.fos:912`) formats the
   speech and answers with `Game.FormatTags` and shows `Gui/Dialog.fogui`
   (the AiControl bridge also snapshots the state for automation).

## Script handler contract

`Demand Script Ns::Func` and `Result Script Ns::Func` resolve functions by
name at call time; the native bridge requires the `DialogDemand`/
`DialogResult` attribute (`SourceExt/ServerExtension.cpp:264,295`) —
`AngelScript.ExtraDirectCallBlockingAttributes` additionally forbids calling
them directly from scripts. Signatures (master = Player/Npc per the demand's
`Who`, slave = the other side):

```angelscript
[[DialogDemand]] bool Func(Critter master, Critter? slave, any arg0..arg4);
[[DialogResult]] void Func(Critter master, Critter? slave, any arg0..arg4);
[[DialogResult]] int  Func(...);   // nonzero return overrides the next speech id
```

These are signature patterns, with zero to five `any` arguments. Non-NPC
dialogs can have a null second critter. Speech scripts (`Script Ns::Func`
under a speech) have no attribute gate — they are found by name and called as
`void/int32 f(Critter, Critter?,
string& textArgs)`; a failed call surfaces as `"!"` and aborts the dialog
with an exception.

[Scripts/Dialog.fos](../Scripts/Dialog.fos) is the shared library (36 result
handlers and 40 demand handlers at the source baseline). Notable results:
`ToHeal`, `DropDrugs`, `DropRadiation`, `ShowLocation`, `TransferToMap/
Location/Global`, `GiveHolodisk`, `DoorOpen`, `AttackPlayer`, `TeamAttack`,
`SkillUp`, `QuestReward1..3`, `CreateLocation`, `TimeoutSet`, loyalty/
memory setters (`SetLoyality`, `SetNameMemNpcPlayer`, …). Notable demands:
chance rolls (`ChanceOneFromTwo/Three/Five`), loyalty/click-counter checks,
`IsNpcStory`. Location modules add their own handlers next to their dialogs
(e.g. `Scripts/KlamJura.fos` `Replay`).

## Adding or changing a dialog

1. Edit the `.fodlg` and both text blocks. `Tools/ContentQuality` has bounded
   pack and English-surface checks, not exhaustive per-dialog translation
   parity. Keep Speech 1 as the state router.
2. New script handlers go in `Scripts/Dialog.fos` (shared) or the owning
   location module, with the right attribute and `any` args; remember
   results can be re-applied if the player re-clicks an answer — make them
   idempotent or gate them with a state property.
3. Bake (`Bake Resources`) — dialogs are baked into both a client text pack
   and the server `DialogPack`; a stale bake is the classic "dialog pack not
   found" exception source.
4. Verify through the normal talk path in a client; `Dialog.TalkDistance`/
   `TalkMaxTime` from [TLA.fomain](../TLA.fomain) frame the interaction.
   `SourceExt/TestDialogs.cpp` covers only native value normalization, not
   content.
