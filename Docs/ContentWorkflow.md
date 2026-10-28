# Content, GUI and configuration workflow

Start from the consumer: combat code for combat data, dialog demand/result code
for `.fodlg`, screen callbacks for `.fogui`. A valid file or clean bake does not
prove correct gameplay. Locate the owner through [Systems](Systems.md).

## Authored inputs and outputs

Authored inputs are `Scripts/**/*.fos`, `Critters/*.focr`, `Items/*.foitem` and
`.fopro`, authored `FixedType` data in `.foinfo`, `Maps/*.fomap` and `.foloc`,
`Dialogs/*.fodlg`, `Gui/*.fogui`,
`Texts/*.fotxt`, `Resources/*`, and `TLA.fomain`. Script directories are explicitly
listed in both `Metadata` and `Scripts` packs; discovery is not recursive.

```text
Gui/*.fogui + InterfaceEditor.cfg + Python generator
  -> Scripts/Generated/GuiScreens.fos
Authored sources + generated scripts + TLA.fomain
  -> BakeResources / ForceBakeResources
  -> Baking/ + resource packs
  -> matching Binaries/ applications
```

Never hand-edit `Scripts/Content.fos`, baked output under `Baking/`, cache under
`Cache/` or generated `VERSION`. Update the owning source/generator. Version
generation uses `Tools/GenerateVersion/generate_version.py` and its VS Code task.
Local package/build trees are debugging outputs, not source-of-truth content.

`TLA.fomain` owns resource-pack inputs and destinations: metadata, configs, scripts,
embedded/core engine resources, text/proto text, common/server data, Fallout art
and sound archives, music/video, mapper resources, protos and maps. Do not repeat
an older pack table instead of inspecting these declarations. `Scripts/Core/`
is project-owned; the former Engine AngelScript core path is obsolete.

Run `Bake Resources` after changes to scripts, dialogs, maps/locations, prototypes,
text, GUI, resources or config. Use `Force Bake Resources` after Engine updates,
property declaration/layout moves or evidence of stale incremental output. Preserve
the failure and prove its cause rather than repeatedly forcing an unexplained bake.
Format authored inputs with the relevant `Format :: *` task before final checks.

### Image descriptors and packaging roots

Authored `.fofrm` files use PascalCase `Key = Value`: `Frame` for one reference,
continued `Frames` for an ordered list, and `Offset = X Y` for placement. Direction
zero is the unnamed section; use positive `Fps` (default 10). Do not reintroduce
legacy `frm_N`, `count`, `offs_x`/`offs_y` or `[dir_0]`. The complete grammar and
dependency rules belong to the [Engine image guide](../Engine/Docs/en/how-to/content/image-format.md).
Refer to the public wrapper when a FOFRM consumes a source image.

TLA sets `Baking.FilterResources = False`, matching the Engine default. Packaging
includes every current baked output of each target-eligible pack, including art,
sound, music, video and common/server data selected by dynamic runtime names.
No project resource-root catalog is required. Pack roles and target-specific
suffix exclusions still apply; a client package does not gain server-only data.

The Baker still publishes `Baking/Resources.usage.json`, bound to matching
build/config markers. With filtering disabled it lists all available outputs
registered by the current bake; packaging consumes that list rather than stale
or unrelated files left on disk. Rebuild/rebake after changing the setting.
`True` opts into typed-root/dependency selection described in the
[Engine baking guide](../Engine/Docs/en/explanation/content-pipeline/baking.md#resource-usage-manifest).
TLA does not use that mode. Test an actual package separately when claiming
packaged-runtime support.

Authored `FixedType` instances use `.foinfo`; keep that extension in
`Baking.ProtoFileExtensions` so the prototype baker reads their typed rows.

## GUI generation

The source is `Gui/*.fogui`, including embedded code in `GlobalScope`,
`ClassFields`, `OnDraw`, `OnGlobalMouseDown`, `OnLMouseClick`, the generator's
`CODE_KEYS` and `CALLBACK_METHODS`. Read those lists before declaring a callback
or expression unsupported.

The supported generator is
[generate_gui_screens.py](../Tools/InterfaceEditor/generate_gui_screens.py), invoked
by `Generate :: GuiScreens.fos`. Its
[InterfaceEditor.cfg](../Tools/InterfaceEditor/InterfaceEditor.cfg) sets
`GuiOutputPath=../../Scripts/Generated`; therefore the project's output is
`Scripts/Generated/GuiScreens.fos`. The script's default/help text and historical
documents may still mention `Scripts/GuiScreens.fos`; that is not the configured
output. Do not use `InterfaceEditor.exe -SilentGenerate`, which emits an
incompatible layout.

For embedded behavior fixes:

1. Find and edit the owning `.fogui` code.
2. If the baked project needs the correction immediately, apply the identical
   code change to `Scripts/Generated/GuiScreens.fos` too. This is the narrow
   paired-source exception, never permission to patch generated output alone.
3. Regenerate when screen identity or non-code properties change, or when an
   intentional generated refresh is required. Review the complete generated
   diff, including screen names/prefixes and callback receivers; do not assume
   regeneration is a behavior-free operation.
4. Compile/bake, build the affected client/mapper, then exercise the visible
   interaction. Fix generated diagnostics at `.fogui` or the generator.

Reusable GUI runtime contracts remain in
[Engine GUI lifecycle](../Engine/Docs/en/reference/gui-runtime/lifecycle.md);
TLA's layout, generator and player acceptance remain here.

## Localization and content contracts

Text packs are baked for `russ engl`; the default client language is `engl`.
Preserve the existing localized pack structure and update both surfaces when
nearby content expects that. Serialized names (`///@ Property/Enum/Setting/Event/
RemoteCall`, proto IDs, text keys and identifiers) stay English; do not translate
or rename them while translating comments. Script comments/headers are Russian;
native C++ is English; continue existing document language.

Check content consumers before changing symbols. Dialog special answers require
`DialogAnswerLink` enum metadata; prototype/save/network identity changes need
an explicit migration decision. Property relocation needs a force bake and
matching client/server metadata even when the stored name is unchanged.

## Content format quick reference

Representative contracts; system-specific behavior lives in the deep-dive
guides ([Items](Items.md), [Dialogs](Dialogs.md), [World](World.md),
[Quests](Quests.md), [Combat](Combat.md)).

| Kind | File | Shape |
| --- | --- | --- |
| Item proto | `Items/*.foitem` | `[ProtoItem]`, `$Name` = proto id (→ `Content::Item::<name>`), `$Parent` lists inherited protos, `$Text russ/engl [Desc]` embeds names; plain `Key = Value` property lines. Families: root gameplay protos, `Static/` scenery/walls, `Custom/` project system protos (`default_weapon`, `Trigger`, `ExitGrid`…), `Explode/`, `Flying/` effect protos. |
| Critter proto | `Critters/*.focr` | `[ProtoCritter]` with `$Parent`; `*Base` stats, `AiId` (Fallout 2 AI packet index), `BagId` (random loot bag), `TeamId`, skills, `KillExperience`. Current quest-NPC dialog bindings primarily live on map instances or in scripts; this is content placement, not a prohibition on proto property values. |
| Map | `Maps/*.fomap` | `[ProtoMap]` header (`Size`, `DayColor` curve, `Music`, `AmbientSound`) + repeated `[$Name/Critter]`/item instance blocks: `$Id`, `$Proto`, and instance overrides (`Hex`, `Dir`, `DialogId`, `BagId`, `TeamId`, `InitScript`, `Val0..3`). `DialogId` here is the primary quest-NPC binding. |
| Location proto | `Maps/*.foloc` | `[ProtoLocation]` with `MapEntrances` map/entry pairs, `MapProtos`/`Automaps` map-name lists, `Radius`, and `$Text` entries (name/description plus numeric keys for global-map music/ambient per map). |
| Dialog | `Dialogs/*.fodlg` | Speech/answer graph with `Demand`/`Result` lines + `[Text russ]`/`[Text engl]` blocks; baked twice (client text pack + server `DialogPack`). Format: [Dialogs](Dialogs.md). |
| Text pack | `Texts/*.fotxt` | `{key}{num}{text}` entries; the Quest pack keys progress text by `{CritterProperty::X}{value}` + `QName`/`QDesc` (see [Quests](Quests.md)); msg ids are consumed via `MsgStr` constants. |
| Generated ids | `Scripts/Content.fos` | Declarations of every content id (`Content::Item/Critter/Map/Location/Dialog::*`); regenerate by baking — never hand-edit. |

`Weight` is grams by convention, `Volume` abstract container units;
`Deterioration` is hundredths of a percent (see [Items](Items.md)). Proto
inheritance recursively resolves the loaded catalog; parents need not precede
children in a file. Parent-list order determines overrides; repeated paths
depend on `Baking.AllowRepeatedProtoParents`, while cycles are rejected.
Validators: `Tools/ContentQuality`
guards text-pack parity; the property registrar rejects malformed `///@`
declarations at bake time.

## Configuration and secure channel

`TLA.fomain` owns runtime defaults, bake settings and named subconfigs. Preserve
owner-selected settings, including Memory storage, transport selection and
single-threaded logic. Pass task-only overrides with isolated runtime paths;
do not make them permanent incidentally. Engine settings are read-only runtime
configuration; project-owned state and saved options follow [Scripts](Scripts.md).

Every connection uses Noise. The server requires `ServerNetwork.ChannelSecretKey`
and the client pins its public half in `ClientNetwork.ChannelServerKeys`.
The base config's development pair is intentionally public and only suitable for
local runs. Never reproduce a production secret in Git, chat, logs or reports.

`PublicGame` reads the secret on the host via `$TARGET_FILE{...}`. Its public pin
is deliberately empty until issued: this profile cannot connect successfully
until the correct pin is supplied. Generate the host key through
`Engine/BuildTools/secure_channel_key.py generate <file>`; consult
[Engine security](../Engine/Docs/en/how-to/release/security-and-secrets.md) before
changing the substitution/save/log/package flow. A local smoke does not qualify
public hosting or authorize a deployment.
