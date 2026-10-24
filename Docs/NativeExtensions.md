# TLA native extensions

Read [Engine/AGENTS.md](../Engine/AGENTS.md) explicitly before `SourceExt/` or Engine
work, then the [native extension guide](../Engine/Docs/en/how-to/native-extensions.md).
It owns reusable C++ structure, pointer, exception, lifetime and profiling rules.
TLA keeps project policy here; a Markdown link is not automatic instruction loading.

## Source owners and registration

| Source | Responsibility |
| --- | --- |
| `CommonExtension.cpp` | Shared SHA helpers; bundled `SHA/` is a static library. |
| `ServerExtension.cpp` | Server image checks, dialog plumbing, visibility hooks and busy/free stubs. |
| `ClientExtension.cpp` / `.h` | `Game.FormatTags`, busy/free stubs, `ClientInitHook`, `ClientExtData` and embedded-client index. |
| `ClientAiBridge.cpp` | Localhost TCP automation protocol paired with `Scripts/AiControl.fos` and `Tools/AiControlMcp/`; [AiControl](AiControl.md). |
| `BakerExtension.cpp`, `DialogBaker.*` | Project dialog baking and baker setup. |
| `Dialogs.*` | Dialog parsing/runtime representation shared by game roles. |
| `TestDialogs.cpp` | Native dialog regressions in the project UnitTests target. |

The exact list is [AddEngineSources](../CMakeLists.txt), with `COMMON`, `SERVER`,
`CLIENT`, `BAKER` and `TESTS` roles. Adding/removing a native source requires
updating its registration. `SourceExt/ContentMigration.cpp` and
`SourceExt/AcmDecoder.cpp` are historical paths, not current extension files.
Current persistence migration behavior must be located in the relevant script,
metadata or Engine owner instead of inventing a replacement file.

Fallout ACM support is now an **optional Engine importer** selected by TLA's
`FO_AUDIO_ACM=ON`. Sources are `Engine/Source/Tools/AudioBaker-Acm.*`; coverage is
`Engine/Source/Tests/Test_AudioBakerAcm.cpp` plus `Test_AudioBaker.cpp`. Baking
converts `.acm` to Ogg Vorbis: effects mono, `sound/music/` stereo. The stale
project-decoder comment in `TLA.fomain` is not a reason to add another decoder.
TLA also opts into DAT/ZIP and FRM/RIX importers through CMake; PNG/TGA/FOFRM are
built-in. Storage providers remain separate positive CMake options.

The default `Server.DbStorage=Memory` needs no optional database provider.
Persistent storage requires selecting/enabling the corresponding
`FO_DATABASE_JSON`, `FO_DATABASE_SQLITE` or `FO_DATABASE_MONGO` option and
reconfiguring. Check the Engine's
[component selection](../Engine/Docs/en/how-to/build/project-configuration.md#optional-native-components)
and [storage upgrade boundary](../Engine/Docs/en/explanation/persistence/index.md#storage-formats-and-upgrade-boundary)
before reusing old JSON/SQLite storage; the Engine does not promise automatic
conversion of every historical format. Never test a format change on the only
copy of a database.

## Binding and review

`///@ EngineHook` names/signatures come from Engine codegen. `///@ ExportMethod`
binds methods: the receiver is the first argument, and `Server_`/`Client_`/`Common_`
mapping determines the script name (for example `Server_Game_LoadImage` → server
`Game.LoadImage`). Use `FO_SCRIPT_API` on exported hooks/methods and exact current
handle types. Script-facing borrows use `ptr<T>`/`nptr<T>`, not a bare entity `T*`;
ordinary internal or foreign-ABI pointers have their owning contract. Project
validation: [Nullability](../Nullability.md).

Match adjacent naming, member order and grouping before adding a pattern. Keep
constructors/destructors before ordinary methods, separate semantic stages and
complete control-flow blocks with blank lines, and review that spacing manually.
Fixed-width aliases, `size_t`, `numeric_cast`, file-local static helpers, Engine
ownership/callable types and per-engine state follow the Engine checklist. Entities
use pointers rather than references. Do not introduce hidden mutable static state.

Use the current invariant vocabulary (`FO_VERIFY_AND_THROW`, `FO_STRONG_ASSERT`
as appropriate), not removed `FO_RUNTIME_ASSERT` spellings or silent fallbacks.
`noexcept` requires a real no-throw contract: inspect every call, especially
cleanup/RAII callbacks. A throwing release call in an asserted no-throw callback
can terminate the process. Follow
[exception safety](../Engine/Docs/en/contributing/coding-contracts/exception-safety.md).

`FO_TRACE_ZONE(Category)` opens meaningful `.cpp` work units, blocking boundaries
or rare expensive paths. Accessors, tiny/per-element helpers, tests and
`FO_SCRIPT_API` exports have no manual zone; generated bindings already supply it.
The removed stack-entry macros are not needed for stack traces. See
[profiling policy](../Engine/Docs/en/how-to/quality/profiling.md#placing-zones).
Native source prose stays English; edited C++ follows the Engine EOF convention.

Build affected targets and execute covered native regressions, then compile/bake
script consumers and run the changed player path. The project Client target
depends on ClientLib; do not accept an old external runtime module or bypass a
compatibility mismatch. [BuildAndLaunch](BuildAndLaunch.md) owns exact commands.
