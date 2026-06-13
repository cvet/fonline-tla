# Nullability

Convention and runtime enforcement for nullable values across AngelScript and the native engine boundary.

## Core principle

> Better to not pass `null` at all than to defensively check inside and bail out.
>
> A parameter or return may be marked nullable **only when the function meaningfully handles both null and non-null cases**. Early-exit-on-null guards are a code smell — the contract should be non-null and the caller fixed instead.

This applies symmetrically on both sides of the script-engine boundary.

## Script side: `T?` suffix

AngelScript modules in [Scripts/](../Scripts/) use a Kotlin/C#-style `?` suffix on the type to mark nullability. Default is **non-nullable**.

```angelscript
// Return may be null
Location? GetCritterLocation(Critter cr)
{
    if (cr.MapId == ZERO_IDENT) {
        return null;
    }
    Map map = cr.GetMap();
    return map != null ? map.GetLocation() : null;
}

// Parameter may be null — body handles both cases
void OnCritterUseWeapon(Critter cr, WeaponUseMode useMode, HitLocation aim, Critter? target, mpos targetHex)
{
    mpos resolvedTargetHex = target != null ? target.Hex : targetHex;
    // ...
}
```

The `?` suffix is now **parsed natively by the AngelScript compiler** (FOnline "strong nullable" patch in [Engine/ThirdParty/AngelScript/sdk/angelscript/source/as_parser.cpp](../Engine/ThirdParty/AngelScript/sdk/angelscript/source/as_parser.cpp) and `as_compiler.cpp`). It is no longer stripped by a preprocessor — the compiler tracks nullability through type checking and emits **compile-time diagnostics** (see «Compile-time diagnostics» below). The parser distinguishes type-suffix `?` from the ternary operator `?` by scanning forward at the same nesting level: a type-suffix is followed by an identifier/`[`/`,`/`)` boundary; a ternary is followed by `:` after the truthy expression.

### Compile-time diagnostics

The compiler now reports three nullability problems as warnings. Treat them as errors to fix, not noise:

| Warning | Meaning | Fix |
|---------|---------|-----|
| `Redundant null comparison: 'T@' is a non-nullable handle and can never be null` | A `== null` / `!= null` test on a value the compiler knows is non-null. | Remove the test. If the source *can* actually be null, mark the source `T?` (or the API `FO_NULLABLE`). |
| `Dereference of nullable handle 'T@?' without a null-check` | A field/method access on a `T?` value that has not been narrowed. | Narrow it first (see narrowing below), or — if it was over-marked — drop the `?`. |
| `Redundant '?': initializer of type 'T@' cannot be null` | A `T? x = <non-null expr>;` local where the initializer is provably non-null. | Drop the `?`: `T x = <expr>;`. |

**Flow-sensitive narrowing.** Inside a guarded scope the compiler narrows a `T?` **local** (not a member access or repeated call) to non-nullable `T`. Recognized forms — one operand must be the literal `null`, the other the local:

- `if (x != null) { /* x is T here */ }` and `if (x == null) { return; } /* x is T after */`
- the same in a ternary: `x != null ? x.foo() : ...`
- short-circuits: `x != null && x.foo()`, `x == null || x.foo()`

Not recognized: multi-condition conjunctions in a block head (`if (a != null && b != null) { ... }` does **not** narrow `a`/`b` in the block body — bind/guard each separately), member-access targets (`obj.Field != null` does not narrow `obj.Field`; bind it to a local first), and a fresh call each time (`Game.GetCritter(id) != null && !Game.GetCritter(id).IsX` — the second call is unnarrowed; bind once to a `T?` local).

**Reference casts.** `cast<T>(x)` is typed **non-nullable** `T@` (the "assume the cast succeeds" contract), so `cast<T>(x) != null` warns as redundant even though a failed downcast returns `null` at runtime. For the type-test idiom, spell the cast nullable: `cast<T?>(x) != null`, or `T? y = cast<T?>(x); if (y != null) { ... }`.

**Formatting.** clang-format treats `?` as the conditional operator and mangles the nullable suffix (`Item? item` → `Item ? item`, `cast<Item?>(x)` → `cast < Item ? > (x)`, `T?[] a` even splits across lines). Always format via the project formatter — VS Code `Format :: *` tasks, [Tools/Formatter/format_project.py](Tools/Formatter/format_project.py), or [FormatSource.bat](FormatSource.bat) — which post-processes clang-format output to restore the suffix in both `.fos` and `.fogui`. Do **not** run `Tools/clang-format-20.exe` directly on these files; it re-mangles the suffix. The GUI generator ([Tools/InterfaceEditor/generate_gui_screens.py](Tools/InterfaceEditor/generate_gui_screens.py)) applies the same repair, so regenerated `Scripts/GuiScreens.fos` stays clean.

### `///@ Event` and `///@ RemoteCall` declarations

The same `?` suffix is supported in `///@ Event` and `///@ RemoteCall` tag declarations, and the [`MetadataBaker`](../Engine/Source/Tools/MetadataBaker.cpp) propagates the per-arg nullable bit into the baked engine metadata (`ArgDesc::Nullable` on `EntityEventDesc::Args` / `RemoteCallDesc::Args`).

```angelscript
///@ Event Server Game OnCritterDamaged(Critter cr, Critter? attacker, int32 damage)
///@ Event Server Game OnCritterDead(Critter critter, Critter? killer)
///@ RemoteCall Server SwitchCharacter(Critter? newCritter)
```

The declaration is the contract. Every `[[Event]]` subscriber and every `[[ServerRemoteCall]]` / `[[ClientRemoteCall]]` / `[[AdminRemoteCall]]` implementation that matches the event/call name must use the same `?` marker on each argument. [`validate_nullable.py`](../Tools/NullableEstimate/validate_nullable.py) walks all `.fos` files, pairs declarations with their handlers by function name, and fails on any per-arg nullable mismatch.

```angelscript
// Matches the OnCritterDamaged declaration above.
[[Event]]
void OnCritterDamaged(Critter cr, Critter? attacker, int32 damage) { ... }

// Would be rejected by validate_nullable.py — declaration has `Critter?`,
// handler drops the `?`:
[[Event]]
void OnCritterDamaged(Critter cr, Critter attacker, int32 damage) { ... }
```

The AngelScript compiler now parses `?` natively and emits the compile-time diagnostics above, so per-arg nullability is checked while compiling. `validate_nullable.py` still enforces declaration↔handler parity across files (the compiler only sees one translation unit at a time), and the engine's runtime null guards on entity meta-types back it up — see «Runtime enforcement» below.

## Engine side: `FO_NULLABLE` macro

Native methods declared with `///@ ExportMethod` in [Engine/Source/Scripting/](../Engine/Source/Scripting/) use the inverse-of-pointer-default macro `FO_NULLABLE`. Defined as empty in [Engine/Source/Essentials/BasicCore.h](../Engine/Source/Essentials/BasicCore.h), it documents the nullability contract that codegen emits into the AS-side metadata.

```cpp
///@ ExportMethod
FO_SCRIPT_API FO_NULLABLE Map* Server_Critter_GetMap(Critter* self)
{
    return self->GetEngine()->EntityMngr.GetMap(self->GetMapId());
}

///@ ExportMethod
FO_SCRIPT_API void Server_Player_SwitchCritter(Player* self, FO_NULLABLE Critter* cr)
{
    self->GetEngine()->SwitchPlayerCritter(self, cr);
}
```

The `self` (first parameter — `this` receiver) and the implicit `engine` parameter for global methods are **never** marked: AS validates `this` before dispatch.

## Runtime enforcement

Runtime validation is plumbed through codegen-generated `MethodDesc::Call` lambdas, **not** the AS-to-native bridge. [Engine/BuildTools/codegen.py](../Engine/BuildTools/codegen.py) emits per-method calls to `NativeDataProvider::CheckArgNotNull` / `CheckReturnNotNull` (defined in [Engine/Source/Common/ScriptSystem.h](../Engine/Source/Common/ScriptSystem.h)) right before/after the native invocation:

```
MethodDesc::Call(call)
  → NativeDataProvider::CheckArgNotNull(call, i, "Server_Player_SetCritter", "cr", "Critter")   // for each non-nullable entity arg
  → native invocation
  → NativeDataProvider::CheckReturnNotNull(call, "...", "...")                                  // for non-nullable entity return
```

Doing it at the `MethodDesc::Call` boundary means **every** caller of an `///@ ExportMethod` is covered — the AS-to-native bridge, native test harnesses, future Mono-backend dispatch, anyone. The check has no per-call lookup cost beyond a single pointer compare.

Violation surface: `ScriptException` with the method name, parameter name and type, propagated to the calling AngelScript context.

**Scope of enforcement:** every **script handle** crossing the script ↔ native boundary is validated. Concretely codegen emits the check when the meta-type is one of:
- a `///@ ExportEntity` name (`Critter`, `Item`, `Map`, `Location`, `Player`, `Game`, `ImGui`) or the generic `Entity`,
- an entity relative (`Abstract<Entity>`, `Proto<Entity>`, `Static<Entity>` — currently `AbstractItem`, `ProtoCritter`, `ProtoItem`, `ProtoLocation`, `ProtoMap`, `StaticItem`),
- a `///@ ExportRefType` class (`MovingContext`, `MapSpriteHolder`, `SpritePattern`, `VideoPlayback`, `ScriptImGui`).

On the C++ engine side the matching pointer spellings (`Critter*`/`CritterView*`, `Map*`/`MapView*`, `ProtoItem*`, `StaticItem*`, `MovingContext*`, …) are all in scope. The membership test lives in `is_validated_pointer_meta_type(...)` in [Engine/BuildTools/codegen.py](../Engine/BuildTools/codegen.py); the [validate_nullable.py](#tooling) walker mirrors it by parsing `///@ ExportEntity` / `///@ ExportRefType` headers at runtime.

Marking `?` / `FO_NULLABLE` on a primitive value type (`int`, `bool`, `mpos`, `hstring`, …) is the only misuse [validate_nullable.py](#tooling) flags — those types have no `null` representation, so the marker is meaningless.

**Out of scope (not implemented yet):** script-to-script call validation. AS does not natively call our bridge for direct script→script invocation; runtime enforcement there would require patching the AS interpreter (`asCContext::ExecuteNext`). In practice script-to-script null contracts are kept by:
- the static analyzer (see [Tooling](#tooling))
- the convention itself — every chain eventually reaches an engine call, which IS validated

## TLA migration notes

The current engine enforces these contracts during normal runtime, not only during static checks:

- Bind nullable dictionary/engine results as nullable locals. For example, `dict.get(id, null)` must assign to `T?`, not `T`, when the key can be absent.
- Generated component accessors are not nullable probes. Check `Has<Component>` first (`cr.HasDialogContext`, `item.HasRadio`, etc.), then use the component accessor.
- Worker-run callbacks that touch entities need sync coverage. Mark the callback `[[Async]]`, lock the relevant entities with `Sync::Lock...`, and remember that `Game.Sync(...)` replaces the held lock set.
- Dialog metadata participates in baking. Special answer links used by `.fodlg` files need globally visible `///@ Enum DialogAnswerLink ...` declarations, otherwise the dialog baker cannot resolve them even if AngelScript compilation succeeds.
- The client `Chosen` accessor (`Game.Chosen`) is **non-nullable and throws** when there is no chosen critter. Guard with `HasChosen` instead of a null-check: replace `if (Chosen == null) return;` with `if (!HasChosen) return;`, and place the `HasChosen` guard *before* any `Critter chosen = Chosen;` assignment (the assignment itself throws when absent). `Game.GetCritter`, `Game.GetItem`, `Critter.GetItem`, `Map.GetCritterAtScreenPos`, etc. are `FO_NULLABLE` — bind their results to `T?` and narrow.
- GUI screen warnings surface in the generated [Scripts/GuiScreens.fos](Scripts/GuiScreens.fos), but the fix belongs in the owning [Gui/*.fogui](Gui/) embedded code (the `?` markers live there in `Type? name` form; clang-format renders them `Type ? name` in the generated output). Edit the `.fogui`, regenerate with `Generate :: GuiScreens.fos`, then recompile — regeneration is faithful, so a fix in the source reproduces exactly.

## Tooling

Four Python tools in [Tools/NullableEstimate/](../Tools/NullableEstimate/):

| Tool | Purpose |
|------|---------|
| `apply_nullables.py` | Scans `.fos` and strips dead defensive null guards on entity-pointer params that are NOT marked `?` — codegen / convention guarantees them non-null. Does **not** add or remove `?` markers; the author owns placement. Idempotent. |
| `apply_native_nullable.py` | Walks `///@ ExportMethod` declarations in `Engine/Source/Scripting/*ScriptMethods.cpp` and strips dead defensive `if (param == nullptr) throw ...;` guards on entity-pointer params that are NOT marked `FO_NULLABLE` — codegen emits `NativeDataProvider::CheckArgNotNull` for those. Does **not** add or remove `FO_NULLABLE` markers; the author owns placement. Idempotent. |
| `validate_nullable.py` | Read-only placement check. Fails when `FO_NULLABLE` appears outside an `///@ ExportMethod` signature, on a non-pointer / primitive type, or when a script `?` is applied to a primitive. The marker on a non-entity handle (RefType / script class) is **allowed** — codegen does not emit a runtime check for it, but the marker is valid declarative documentation. |
| `estimate_nullables.py` | Read-only coverage report — counts function/parameter/return shapes across `.fos`. |

The applier tools accept `--check` (exit non-zero if dead defensive guards still exist) or `--dry-run` (preview without writing). `validate_nullable.py` is always read-only. CI uses these check modes to fail PRs that drift.

### Why the appliers don't auto-add markers

Earlier revisions of the analyzers tried to infer marker placement from body shape (`return nullptr;` somewhere → mark return; no defensive throw + no dereference → mark param). The heuristics produced churn against a curated codebase: a one-liner `void TransferToMap(Critter* self, Map* map, mpos hex) { ... transfer(self, map, hex, ...); }` would round-trip to `FO_NULLABLE Map* map` because the body only forwards the pointer — but the contract is non-null. Author intent is the source of truth; the analyzer's job is now only to delete dead guards that codegen has made redundant.

## Workflows

### VS Code tasks ([.vscode/tasks.json](../.vscode/tasks.json))

Generators (modify code) — run after editing scripts or native exports:
- `Generate :: Nullable Markers (Scripts)` → `apply_nullables.py`
- `Generate :: Nullable Markers (Engine)` → `apply_native_nullable.py`
- `Generate and Format All` → bundles both, then formatter pass

Analyzers (check-only, exit non-zero on drift) — run before committing or in CI:
- `Analyze :: Nullable Markers (Scripts)` → `apply_nullables.py --check`
- `Analyze :: Nullable Markers (Engine)` → `apply_native_nullable.py --check`
- `Analyze :: Nullable Placement` → `validate_nullable.py`
- `Analyze :: Nullable Coverage` → `estimate_nullables.py`
- `Analyze All` → bundles all four

### CI

`.github/workflows/ci.yml` (`analyze` job) runs the script and engine appliers in `--check` mode plus `validate_nullable.py` on every push and PR. Drift in either the script `?` markers, the native `FO_NULLABLE` annotations, or a misplaced marker (outside an `///@ ExportMethod` or on a non-entity type) fails the run with a hint pointing to the generator task to fix it.

### Manual

```bash
python Tools/NullableEstimate/apply_nullables.py          # apply script-side markers
python Tools/NullableEstimate/apply_native_nullable.py    # apply engine-side markers
python Tools/NullableEstimate/validate_nullable.py        # check placement
python Tools/NullableEstimate/estimate_nullables.py       # report only
```

Append `--check` to either applier to verify idempotency without writing files.

## Adding / editing markers

When you write a new script function or native export, you can either:
1. Write it however you want and run `Generate :: Nullable Markers` — the analyzer fills in the markers per the rule above and strips any dead defensive code.
2. Write the marker yourself if you know better than the heuristic (e.g. user-facing API where you want to lock the contract). The analyzer is idempotent: it won't re-introduce dead checks once stripped, and respects existing markers when their pattern matches the rule.

When the analyzer's heuristic gets it wrong (saw it with `dynamic_cast<X*>(param)` paths where param is genuinely nullable), prefer extending the heuristic in [apply_native_nullable.py](../Tools/NullableEstimate/apply_native_nullable.py) over a one-off manual edit — the next CI check will revert manual edits otherwise.

## See also

- [Scripts.md](Scripts.md) — overall AngelScript module organization and conventions.
- [NativeExtensions.md](NativeExtensions.md) — `///@ ExportMethod` codegen pipeline and engine source layout.
- [Testing.md](Testing.md) — running unit and gameplay tests that exercise the runtime check.
