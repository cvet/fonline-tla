# AI control historical verification and fixes

Preserved from the former long `Docs/AiControl.md` during the 2026-10-24 audit.
These are dated run results and implementation narratives, not current pass claims.
Current launch/acceptance: [AiControl](../AiControl.md). Protocol:
[AiControlProtocol](../AiControlProtocol.md). The bridge's QA mutation commands are
privileged setup; their historical passes do not prove an ordinary player path.

Routes: [recorded runs](#verified-end-to-end-2026-07-11),
[dialog trace seeds](#dialog-trace-seeds-2026-08-08),
[quest authoring lessons](#adding-more-quests-what-still-needs-care),
[text-key fixes](#fixed-empty-dialog-text-key-mismatch).

## Verified end-to-end (2026-07-11)

- `register` / `login` drive the real TLA auth path; a character spawns and `observe` populates
  `chosen` / `map` / `critters` / `mapItems` / `quests`.
- `move_to_hex` moves the chosen to the exact target hex; `pick_item` / `talk_to` auto-walk to their target;
  `say`, `attack_entity`, `dialog_answer` are accepted and processed; dialogs open and advance by answer index.
- Dialog observation captures `dialogId` / `talkerId` / answer structure. A fresh `repl1` registration opened
  the ordinary `repl_hubb_oper` dialog with readable speech and answer; an engine framebuffer capture also
  confirmed the composed dialog window renders correctly. ContentQuality verifies every reachable speech and
  answer in all 17 `repl_*.fodlg` files is present and non-empty in both languages (excluding invisible
  pre-dialog routing node 1).
- `environment_query path` correctly reports reachable vs unreachable target hexes (`reachable` /
  `pathLength`); `obstacles` lists blocked hexes — used by the playtest runner to pick reachable targets.
- `qa_teleport_hex` repositions on the current map; `qa_teleport_map arroyo` reaches the real `arroyo` village
  map with its quest NPCs. Exact `vault_city/vcity_courtyard` targeting is verified through the split remote-call
  contract; an unknown proto returns `unknown_map_target` without reaching server validation.
- After the dialog text-key fix, a real quest dialog is read and navigated end-to-end: the agent walked the
  Savinelli caravan-escort dialog on `arroyo_bridge` through 5 readable speeches, choosing meaningful answers.
- A real quest is **accepted with an observable state change**: on the `arroyo` village map the agent talked
  to Cassidy, asked for work, read the offer ("отнеси письмо в Город-Убежище для Синди"), answered "Да,
  конечно", and `observation.quests` then shows `CritterProperty::ArroyoCassidyLetter = 1`, with the
  `letter_to_sindy` item added to inventory. (Caravan-escort quests, by contrast, are correctly time-gated —
  they only accept near departure.)
- **A full quest cycle completes end-to-end** across two cities via teleport: after accepting the Cassidy
  letter at Arroyo, the agent `qa_teleport_map vault_city/vcity_courtyard` reaches Cindy (`vc_cindy` at
  hex `65,55`), reads her dialog ("От Кэссиди?! ... Давай его скорей сюда!"), answers "Вот оно, держи.", and
  the quest advances to `CritterProperty::ArroyoCassidyLetter = 2` with the `letter_to_sindy` item consumed.
  (The `CreateLocation` sandbox instance DOES spawn the map-placed quest NPCs; an earlier "missing Cindy"
  reading was a wrong-hex lookup. After `qa_teleport_hex` on a large map, nudge a couple of hexes and
  re-`observe` to let the client sync nearby critters.)
- The whole cycle is reproducible through `tla_quest_runner.py --quest cassidy_letter --require-exercised`
  (`ok: true`, `transitions_verified: 2`, `ArroyoCassidyLetter` 0 → 1 → 2). `qa_teleport_map` sets
  `AutoGarbage=false` on the instances it creates
  (and recreates a destroyed one) so a content location persists across runner stages/runs.
- **A second full quest cycle** runs on a single giver: `tla_quest_runner.py --quest arroyo_mynoc_oil`
  (`ok: true`, `ArroyoMynocOil` 0 → 1 → 2) — accept "Я принесу тебе смазку" (gated on `Intellect > 3`, set via
  stage `setup`) then hand in the `oil_can` ("У меня есть маслёнка", item granted via `setup`). This exercises
  the robust navigator (Mynoc's accept lives several topic-tree hops deep behind a first-meeting intro).
- **A third and fourth full quest cycle** broaden the shapes and towns: `den_smitty_robot` (`DenSmittyFixit`
  1 → 2 → 3 → 4 — accept at Smitty, repair his Mr. Handy at the workbench gated on `SkillRepair` + three
  items, report back) and `klam_vaccination` (`KlamVaccination` 0 → 1 → 2 in Klamath — accept Hish's syringe
  task, the three per-brahmin sub-task flags supplied via `setup`, then report). `KlamVaccination` is a
  `Server`-scope flag (not `OwnerSync`), so it is verified through the `qa_get_prop` round-trip, not the client
  observation.
- The QA-setup commands are verified: `qa_set_prop Experience 5000` / `qa_set_prop ArroyoCassidyLetter 1`
  change the observed property; `qa_give_item stimpak 3` / `qa_give_item letter_to_sindy` add the items;
  `qa_get_prop KlamVaccination` reads back a `Server`-scope flag the observation can't see. These unblock and
  verify quests with prerequisites: some givers gate their dialog on faction loyalty or a prior quest stage
  (Arroyo's Todd needs `Dialog::CheckLoyality`), which a fresh QA character lacks — set the prerequisite first,
  then run the quest.
- **Fixed an event-buffer flood:** `OnInputLost` fired every frame while the client window was unfocused (the
  normal state for an automated/headless client), pushing `input_lost` until it evicted real events
  (`command_completed`, `qa_prop_value`, `qa_prop_set`) from the bounded event ring. It is now gated behind
  `AiControl.CaptureRawInputEvents` (off by default), so automation runs see a clean event stream.
- **Held input survives an unfocused client:** the same per-frame `OnInputLost` made `Input` release every
  pressed button and key on the next frame, so a simulated hold (the action-cursor menu, a drag) could not be
  driven. `Input` now resets once per focus loss (the first `OnInputLost` after input was live), and the bridge
  exposes `mouse_down` / `mouse_up` / `mouse_move` and `key_down` / `key_up` to hold input across frames.
- `smoke_ai_control_mcp.py` (static and live) and `tla_mechanics_playtest.py` pass.

### Dialog trace seeds (2026-08-08)

`--trace-dialog` was verified against a fresh Russian client and the real `CassidyStage4` NPC on `arroyo`.
The bounded replay handled the one-shot introduction, found the three-answer path through "work" and the letter
offer, and emitted `Да, конечно.` as the rank-1 candidate for `ArroyoCassidyLetter` (`0 → 1`). The JSON report
recorded 5 explored paths, 1 root rebase, no branch errors, the complete node path, and a confirmed restore to
the original value 0.

The same live workflow covers the real Arroyo Mynoc placement (`protoId=EnclaveGuard`,
`dialogId=arroyo_mynoc`) with `IntellectBase=6` supplied through the acknowledged setup path. Quest-guided
ordering found `Я заметил... Твоя броня, она несколько поржавела...` → `Я принесу тебе смазку...` in 2 explored
paths and 13.7 seconds, observed `ArroyoMynocOil` 0 → 1, reported no branch errors, and confirmed restore to 0.

The Den seed is now live-verified across all four authored stages. The real `HomesteaderMale` / `den_smitty`
path accepted the job (`DenSmittyFixit` 0 → 1); `MrHandy` / `den_mr_handy` exposed the Repair-85 diagnosis
(1 → 2) and accepted `pump_parts` + `oil_can` + `super_tool_kit` (2 → 3); Smitty then accepted the report
(3 → 4). Every trace found a ranked candidate without branch errors and restored the original flag value 0.
Reports are `Build/_artifacts/trace-dialog/smitty-{accept,examine,repair,report}-live.json`. This validates 3 of
the 7 Stage-0 trace quests.

The fourth seed uses the real Klamath `MasterTrader` / `klam_hish` at hex 82,132. With `IntellectBase=6`,
bounded replay found the five-answer path from looking for work through the name joke and vaccination offer to
`Хорошо, не волнуйся. Я не промахнусь.`, observed `KlamVaccination` 0 → 1 in 5 explored paths and 20.97 seconds,
reported no branch errors, and restored 0. The report is
`Build/_artifacts/trace-dialog/klam-hish-accept-live.json`.

The three fresh Arroyo traces complete the Stage-0 criterion. The normal Todd talk path first reported
`no_visible_start_speech` despite an alive, talk-enabled, adjacent and mutually visible NPC. The project dialog
parser was retaining the `@` sigil and full `Content::*` qualifier in script arguments; normalizing those values
restored the authored loyalty demand, after which `ArroyoProofOfDeath` advanced 0 → 1 without a mechanic bypass.
Todd's follow-up offer advanced `ArroyoLetterToLinnett` 0 → 1 with `ArroyoProofOfDeath=3` as its authored
prerequisite. Finally, stable-slot replay handled Mynoc's randomized `@@` wording and exposed an unconditional
minimum-group guard that contradicted the solo stage-1 dialog branch. Restricting that guard to stage 2 produced
the full 13-answer path and `ArroyoMynocDefence` 0 → 1. All three runs had no branch errors and restored 0; reports
are `Build/_artifacts/trace-dialog/arroyo-{todd-proof,letter-linnett,mynoc-defence}-live.json`. Stage-0 trace
coverage is **7/7**.

The next Den trace corrected a stale diagnosis and completed `DenMomSlut` end to end. The parser already inferred
`DenVirginIsAway` as a Game property; the hidden answer came from comparing integer property value `"0"` with
textual any value `"false"`. Dialog property booleans are now normalized to `0`/`1`, restoring all 51 authored
boolean demand/results. Live replay advanced 0 → 1 at Mom in 27 paths, 1 → 2 at Virginia in 2 paths (executing
`DenVirgin::GoAway`), and 2 → 3 at Mom in 1 path. All runs restored the original flag and had no branch/log errors.
Reports are `Build/_artifacts/trace-dialog/den-{mom-slut-accept,virginia-away,mom-slut-report}-live.json`.

### Mechanics beyond dialog (verified 2026-06-21)

A battery of non-dialog gameplay mechanics was driven end-to-end on a real client, each with an observable
state change in `chosen` / `inventory` / `mapItems`:

- **Skill use (self first-aid).** `qa_set_prop SkillFirstAid 200` → `qa_set_prop CurrentHp 6` →
  `use_skill SkillFirstAid` (no target ⇒ applied to self); `chosen.currentHp` went 6 → 33.
- **Item use / healing.** `qa_set_prop CurrentHp 5` → `qa_give_item stimpak` → `use_item <stimpak id>`;
  `chosen.currentHp` went 5 → 18 (the stimpak healed the character).
- **Combat / kill.** `qa_give_item super_sledge` → `move_item <weapon id>` to slot `CritterItemSlot::Main`
  (= 1; `Inventory` 0, `Main` 1, `Secondary` 2, `Armor` 3) to equip it → locate a `mob_brahmin` (passive,
  spawns on the Arroyo maps) → `attack_entity` (`mode` 0), re-issued each AP cycle while polling the target's
  `isAlive`; the brahmin died and `chosen.experience` went 0 → 80. Boost damage first with
  `qa_set_prop SkillMeleeWeapons 250` / `qa_set_prop StrengthBase 10`. Attack maps to
  `CurPlayer.ServerCall.Attack(targetId, mode)`.
- **Weapon reload.** `qa_give_item _10mm_pistol` + `qa_give_item _10mm_ap 30` → `move_item` the pistol to the
  `Main` slot → `reload <pistol id>` (accepted).
- **Equip / inventory move.** `move_item <id> <slot>` — verified round-tripping a `_10mm_pistol` through
  `Main` (1) → `Secondary` (2) → `Inventory` (0) with the observed `inventory[].slot` matching each request.
- **Drop.** `drop_item <id>` puts the item on the ground (it appears in `mapItems`). (Ground re-pickup was
  timing-flaky in the batch.)
- **Crafting (FixBoy).** `qa_set_prop SkillOutdoorsman 120` → `qa_give_item brahmin_skin 3` / `pocket_lint` /
  `rope` / `knife` → `craft 1` (recipe id 1 = `leather_armor`); the armour appeared in `inventory` and the
  resources were consumed (`brahmin_skin` 3 → 1). The server checks the recipe's skill/material/tool demands
  and only crafts when they pass.
- **Barter.** Teleport next to a merchant (Arroyo `arroyo_cassidy` at `(82,113)`), `talk_to`, then pick the
  barter answer ("Может, поторгуем?"); `chosen`'s active `screen` becomes `GuiScreen::Barter`. The barter
  answer is the engine `Answer Barter` link, which routes through `Barter::StartNpcBarter`.
- **Loot / container grid.** Kill a critter, then `loot_critter <id>` opens `GuiScreen::PickUp` and
  `operate_container` (`intArg=3` = take + all) pulls its inventory. Verified on a `mob_brahmin` corpse.
- **Global-map travel does NOT work from a sandbox map (and corrupts transfer state).** `qa_teleport_global`
  (`TransferToGlobal`) is a no-op from the `qa_teleport_map` sandbox instances (they carry no valid worldmap
  position), and after calling it the character's hex transfers stop applying (a stuck transfer state) — a
  fresh character recovers. Real global-map travel needs canonical world/town state, not a `CreateLocation`
  sandbox; treat `qa_teleport_global` as unsupported there. Sleeping/rest is likewise not a general mechanic
  in TLA (only mining has a `STR_NEED_REST` gate).
- **Sneak is NOT implemented in TLA.** `toggle_sneak` never changes `chosen.inSneakMode`, because the game
  itself stubs it: the `Tla::ChosenSneak` action body has its `Game.CustomCall(...)` commented out
  (`ChosenActions.fos`) and the `UseSneak` RemoteCall is disabled (commented `///` not `///@`, body inside
  `/* */`). The bridge now returns `sneak_not_implemented_in_game` instead of silently queuing a no-op — a
  game-content gap, not a bridge defect.

### Adding more quests (what still needs care)

The upgraded navigator (auto-advance intros, strong exit-avoidance, seen-tracking across re-opens) handles
both a simple giver (Cassidy) and a deep topic-tree giver (Mynoc). What remains per-quest is mostly *getting
the right answers to appear*, via stage `setup` and the right client language:

- **Localization.** The default client runs `Client.Language = engl`, so any NPC that *has* an English
  translation shows English answers and the Russian `prefer` keywords never match. **Run the client with
  `--Client.Language russ`** (the specs are written from the `.fodlg` `[Text russ]` source).
- **Prerequisite demands.** A quest answer can be hidden behind a critter property (`Intellect`, `CurrentHp`
  for Doc's `IsToHeal`), an inventory item (Mynoc's `oil_can`), or a GAME flag — supply them with stage
  `setup` (`qa_set_prop` for critter props, `qa_set_game_prop` for game props, `qa_give_item` for items).
- **Non-quest flags.** Some "quest-like" props are not in `CritterPropertyGroup::Quests`, so they never appear
  in `observation.quests` (Arroyo `ArroyoDocHealing` is a `Server` flag, `Max = 2`). Pick targets that *are*
  `Group = Quests` if you want to assert progress from the observation.
- **Resolved parser migration defects.** Todd's `@!` loyalty argument had been hashed with the sigil after the
  project dialog parser moved away from `ResolveGenericValue`; the parser now restores the legacy script-argument
  spelling. Den Mom's hidden "Virginia" answer was not a Game/Player scope mismatch: the parser inferred the Game
  owner correctly, but property boolean `false` remained text instead of integer `0`. Property booleans are now
  normalized to their integer storage spelling, and both normal talk paths are live-green.

The `QUESTS` dict ships three verified flows plus a `NOTE` documenting these knobs:

- `cassidy_letter` — accept at Arroyo, deliver across town to Vault City (`ArroyoCassidyLetter` 0 → 1 → 2).
- `arroyo_mynoc_oil` — accept + turn-in at one giver, gated by `Intellect` and an `oil_can` item
  (`ArroyoMynocOil` 0 → 1 → 2).
- `den_smitty_robot` — four stages in one town: accept at Smitty → examine the Mr. Handy robot (needs
  `SkillRepair > 59`) → repair it (needs `pump_parts` + `oil_can` + `super_tool_kit`) → report back
  (`DenSmittyFixit` 1 → 2 → 3 → 4). Shows a quest gated by both a skill and inventory items, all supplied via
  stage `setup`.

Adding a quest is: pick a `Group = Quests` target, give each stage its `setup`, and run once against a Russian
client to confirm.

## Fixed: empty dialog text (key mismatch)

Surfacing dialog `text`/`answers` via the bridge exposed a real game bug: all dialog speech/answer strings
resolved empty. Root cause — a text-pack key mismatch between the baker and the runtime lookup. The
`DialogBaker` stores each dialog text under a 4-part key `FromParts("Dialogs", <dialogName>, <textKey>, ...)`
(it includes the dialog name), but `Dialogs.fos` looked it up with only the text key
(`TextPackKey(TextPackName::Dialogs, "" + textId)`), so the keys never matched and `Game.GetText` returned
empty for every dialog (a normal player saw the same).

Fix (in `Scripts/Dialogs.fos`): build the lookup with the dialog id as the first key part —
`TextPackKey(TextPackName::Dialogs, dialogId, textId)` in `ReceiveDialogContext` (screen text + answers) and
the answerless `Say`/`Info` path. Verified: `arroyo_laumer` now reads its real Russian quest dialog and the
agent navigates it answer-by-answer.

### Fixed: empty NPC floating text (numbered dialog strings)

The same class of bug hit the **numbered** dialog strings — the lines NPCs say on their head in combat/ambient
(`Messaging::Say`/`SayOnHead`/`Info`), keyed by `MsgStr::DialogTextId(dialogId, num)`. `DialogBaker` stores
these under `[Dialogs, <dialogName>, <100000000 + num>]` (the authored key base `100000000` is shared by every
dialog; the dialog name disambiguates), but the call sites looked them up as
`TextPackKey(TextPackName::Dialogs, "" + MsgStr::DialogTextId(dialogId, num))`, which is wrong **twice**: it
omits the dialog name, and `DialogTextId = dialogId.uhash + 12000 + num` no longer reproduces the baked key
(the 64-bit `uhash` overflows to a garbage number). So all of these floating lines were empty.

Fix: a single helper `MsgStr::DialogTextKey(dialogId, num)` →
`TextPackKey(TextPackName::Dialogs, dialogId, "" + (100000000 + num))`, and the **101** call sites across 26
files (`TextPackKey(TextPackName::Dialogs, "" + (MsgStr::DialogTextId(EXPR, N)))` → `DialogTextKey(EXPR, N)`)
were migrated to it. Verified through the `qa_get_text` debug command (resolves `MsgStr::DialogTextKey` for a
given dialog id + number): `klam_aldo` 1/2/3 ("Не могу к доске подобраться…", …), `all_poker` 0 ("Ваши карты:"),
`bh_phil` 200 — all now return their real text.

### Fixed: empty dialog text in `@text` format tags (poker / roulette / banker / NPC names)

The other consumer of the numbered dialog strings is the `@text Dialogs <id>@` **format tag** — built
server-side (poker card names, roulette, the replication-banker "spy" descriptors) and resolved client-side by
`Game.FormatTags` so each player sees their own language. The tag carried a single id
(`MsgStr::DialogTextId(...)`), so — like the `Say`/`Info` path — it omitted the dialog name and used the wrong
number; all of it rendered empty. NPC names via `@text Dialogs <MsgStr::NpcNameDlgTextId(dlg)>@` were broken
the same way (the name is stored under the string key `"Name"`).

Fix, in two parts:
- **Engine** (`SourceExt/ClientExtension.cpp::FormatTags`): the `@text` tag now also accepts a three-token form
  `@text <pack> <subkey> <key>@` → `FromPack(pack, subkey, key)` (a second key). The two-token form is
  unchanged, so every existing tag keeps its behaviour.
- **Script**: two helpers — `MsgStr::DialogTextTag(dialogId, num)` → `@text Dialogs <dialogId> <100000000+num>@`
  and `MsgStr::NpcNameTag(dialogId)` → `@text Dialogs <dialogId> Name@` — and **157** sites migrated to them
  (146 numbered-text across `Dialog.fos`/`Poker.fos`/`Roulette.fos`, 11 NPC-name across 8 files).

Verified end-to-end with the `qa_format_tags` debug command (runs a raw string through `Game.FormatTags`):
`@text Dialogs klam_aldo 100000001@` → "Не могу к доске подобраться…", `@text Dialogs all_raider Name@` →
"Рейдер", `@text Dialogs all_poker 100000000@` → "Ваши карты:", and the same tag embedded mid-sentence
resolves in place. (Requires a native `TLA_Client` rebuild for the `FormatTags` change.)

### Fixed: empty proto-name `@text` tags (critter / item / location names)

`@text Critters/Item/Locations <id>@` (NPC, item and location names in a handful of messages) were broken
differently. The engine `ProtoTextBaker` stores a proto's localized `$Text <lang>` name under
`[<pack>, <protoId>]` — i.e. the **proto id string itself is the key**, and the pack names are `Critters`,
`Items` (plural!) and `Locations`. The call sites instead passed a number (`pid.uhash` via
`NpcProtoNameTextId`/`ItemNameTextId`/`LocNameTextId`) and, for items, the wrong pack name `Item` (singular) —
so all of it missed and rendered empty.

Fix: helpers `MsgStr::NpcProtoNameTag(pid)` → `@text Critters <pid>@`, `MsgStr::ItemNameTag(item)` /
`ProtoItemNameTag(pid)` → `@text Items <pid>@`, `MsgStr::LocNameTag(pid)` → `@text Locations <pid>@`, with the
**15** sites (across `Behemoth`/`Caravan`/`FighterQuest`/`GameEventCaches`/`NcrPostman`/`Repairer`/`Resources`/
`Traveller`) migrated to them. These are plain two-token tags (no engine change needed beyond the three-token
support already added). Verified via `qa_format_tags`: `@text Critters Algernon@` → "Алжернон",
`@text Items _10mm_ap@` → "10 мм ББ", `@text Locations klamath@` → "Кламат", and embedded in a sentence.

## Roadmap (next)

- A content-driven quest runner on top of `qa_teleport_map` (accept → travel → turn in) covering more quests;
  the Cassidy letter cycle above is the reference flow.
- The proto-text long tail is **done** (full key scheme verified — name `[Pack, protoId]`, desc
  `[Pack, protoId, "Desc"]`, numbered `[Pack, protoId, "<rawN>"]`). Item names/descriptions in look/examine
  (`ItemNameKey`/`ItemInfoKey`, 9 sites in `ClientMain.fos`); all 16 worldmap/crafting GUI sites — location
  name/desc/map/entrance/picture + crafting item names (`LocNameKey`/`LocInfoKey`/`LocPicKey`/`LocLabelPicKey`/
  `LocMapNameKey`/`LocEntranceNameKey`/`LocEntrancePicx|yKey`/`ProtoItemNameKey`) edited in the `.fogui` source
  and regenerated into `GuiScreens.fos`. The old single-key resolvers (`GetItemText`/`GetLocationText`/
  `GetCritterText`/`HasLocationText`) are now unused and were removed. Also fixed the `AddDialogStr`/STR-const
  system: the replication-bank terminal + roulette messages were empty because `AddDialogStr(int msg)` did a
  single-key lookup of a `DialogTextId` number — the RemoteCall is now `AddDialogStr(hstring dialogId, int
  strNum, …)` → `DialogTextKey`, the STR constants became plain string numbers, and `DialogBarman.fos`'s
  malformed `text Dialogs/Locations` tags (missing the leading `@`) were corrected. Verified
  (`@text Dialogs repl_terminal 100000000@` → "Ошибка. Пожалуйста обратитесь…"). The only `DialogTextId`
  remnants left are vestigial (commented-out poker `// Todo: SayMsg` consts + one Caravan debug log).
- Global-map observation + travel/enter — for canonical world state and travel-only mechanics (random
  encounters, party travel). Quest accept/turn-in itself already works via `qa_teleport_map` (the sandbox
  instance spawns the map-placed quest NPCs).
- Resolved quest titles/objective text in `quests` (and faction, skills/abilities observation).
- Richer screen/affordance surfaces beyond the current barter, container/item metadata, and nine-window
  contextual GUI runner (registration customization and remaining mechanic-owned screens).
- Content-driven playtest runners per quest/mechanic on top of `qa_teleport_map`; optionally adapt more of the
  ported advisory/agent-runtime adapter layer.
