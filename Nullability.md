# TLA nullability contracts

This page owns the project's AngelScript spelling and validator workflow. The
reusable compiler/runtime and native pointer contracts are documented in
[Engine nullability](Engine/Docs/en/contributing/coding-contracts/nullability.md)
and [smart pointers](Engine/Docs/en/contributing/coding-contracts/smart-pointers.md).
Read [Scripts](Docs/Scripts.md) for TLA side, state and lifetime policy.

## Choose the contract at the source

Use `T` when a handle must exist and `T?` when absence is a valid observable state.
Native script-facing borrows use `ptr<T>` / `nptr<T>` respectively, including
exported ref-type members and callback templates. Do not replace a required
contract with nullable early returns merely to hide an invariant failure. A
legitimately missing lookup result still needs a nullable local and explicit
handling; it must not be assigned to a non-null local first.

```angelscript
Critter? target = Game.GetCritter(id);
if (target == null) {
    return;
}

// Здесь target сужен до Critter; отсутствие уже обработано
```

The compiler parses the suffix natively. It warns on a redundant null comparison,
dereference before narrowing and a redundant `?` on a provably non-null
initializer. Fix warnings at the declaration/caller, not by suppressing them.

## Narrowing, casts and components

Narrow a **local** with `if (x != null)`, a returning `if (x == null)`, a guarded
ternary or short-circuit `&&` / `||`. Repeated member access/calls do not become
the same narrowed local; bind once. Do not assume a compound block-head condition
narrows every local inside the body: guard each separately as required by the
current compiler. A potentially failing downcast uses `cast<T?>(x)`; the
non-null spelling `cast<T>(x)` is an assertion of success, not a type-test idiom.

Generated component accessors are not optional handles. Check `item.HasRadio`,
`cr.HasDialogContext`, etc. before accessing the component; do not compare its
accessor with `null`. `Game.Chosen` is non-null and throws when no chosen exists:
check `HasChosen` **before** assigning/accessing it. Fallible entity lookups and
dictionary `get(..., null)` results must bind to `T?` before narrowing. Proto
lookup behavior is API-specific; read its current declaration rather than
assuming every `Get*` is nullable.

## Event and RemoteCall parity

The `?` on `///@ Event` and `///@ RemoteCall` arguments is part of the metadata
contract. Every corresponding `[[Event]]`, `[[ServerRemoteCall]]`,
`[[ClientRemoteCall]]` or `[[AdminRemoteCall]]` implementation preserves it.

```angelscript
///@ Event Server Game OnCritterDamaged(Critter cr, Critter? attacker, int32 damage)

[[Event]]
void OnCritterDamaged(Critter cr, Critter? attacker, int32 damage)
{
    // Обработчик сохраняет nullable-контракт источника урона
}
```

MetadataBaker propagates the nullable bit. The project validator matches
declarations and handlers across files; compilation of separate sides is not a
substitute for this parity check. Dispatcher-owned attributed entrypoints are
not reusable direct-call helpers.

## Native boundary and runtime checks

`///@ ExportMethod` and other generated script-facing handle surfaces use exact
current `ptr<T>` / `nptr<T>` types, including containers and `FindFunc` /
`CheckFunc` callback signatures. Bare entity `T*` and the former `FO_NULLABLE`
marker are not nullable export contracts. Internal/foreign-ABI pointers and
EngineHook signatures follow their separate owning Engine declarations.

Codegen inserts `NativeDataProvider::CheckArgNotNull` / `CheckReturnNotNull` at
`MethodDesc::Call`, covering native dispatch as well as the AS adapter. The
current AS runtime also checks null assignments into non-null script handle
slots (`asBC_RefCpyChk`); the old claim that script-to-script null enforcement
was unimplemented is obsolete. Runtime violations are distinct from compiler
warnings. The [Engine guide](Engine/Docs/en/contributing/coding-contracts/nullability.md#runtime-enforcement)
owns validated meta-types, assignment/call boundaries, arrays and exact exception
behavior; do not infer per-element array guarantees from scalar checks.

TLA's script server runs single-threaded. Nullability does **not** require the
removed `Sync` module or `[[Async]]` attributes. Callbacks can still synchronously
destroy entities; follow the actual owner/lifetime boundary.

## Formatting and generated GUI

Use `Format :: Scripts` or
[format_project.py](Tools/Formatter/format_project.py), never raw clang-format
on `.fos`/`.fogui`: the wrapper repairs nullable suffixes that clang-format treats
as ternary operators (`T ?`, split casts and arrays). It preserves the detected
line-ending style and normalizes EOF to one terminator. Existing script CRLF
must be preserved when manually rewriting a source file.

GUI warnings name `Scripts/Generated/GuiScreens.fos`, but the fix belongs in its
owning `.fogui` embedded code or generator. Follow
[ContentWorkflow](Docs/ContentWorkflow.md#gui-generation), including its paired
source/output exception; do not prescribe regeneration for every small code fix
or patch only generated output. Dialog special answers additionally require
globally visible `DialogAnswerLink` metadata; this is a bake contract, not a
nullable check.

## Tooling and verification

The active tool owner is [NullableEstimate](Tools/NullableEstimate/README.md).
From the repository root (use verified `python3` on non-Windows hosts):

```sh
py -3 Tools/NullableEstimate/test_validate_nullable.py
py -3 Tools/NullableEstimate/validate_nullable.py
py -3 Tools/NullableEstimate/apply_nullables.py --check
py -3 Tools/NullableEstimate/estimate_nullables.py
```

`validate_nullable.py` rejects invalid script `?`, obsolete `FO_NULLABLE`, raw
script-facing handles and Event/RemoteCall mismatches. Its native scan is
deliberately limited to exported methods/FO_SCRIPT_API, exported RefType members
and FindFunc/CheckFunc, not arbitrary internal pointers or SetupBakersHook.
This scan boundary does not relax the Engine's broader native hook contract.
`apply_nullables.py --check` is read-only; without it the helper may rewrite
source. `estimate_nullables.py` reports coverage. The author decides nullable
intent; none of these tools can infer it from a body.

VS Code: `Analyze :: Nullable Placement` runs the validator; `Analyze :: Nullable
All` adds marker analysis, focused tests and coverage. CI's `validate` job runs
the focused tests, validator and marker check. The legacy
`apply_native_nullable.py` is only for pre-`ptr`/`nptr` revisions, outside the
current gate. Compile every affected side and run the relevant behavior as in
[BuildAndLaunch](Docs/BuildAndLaunch.md); static spelling alone is not runtime proof.
