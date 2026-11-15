# GUI tip null-parent guard plan

**Goal:** Stop the repeated `ScriptException: GUI object not found` in
`TLA_Server.log` from `Tip::OnDraw()`.

**Architecture:** Guard the nullable `obj.Parent` in the authored `.fogui`
handlers before the `GuiScreensExt::NeedObject` narrowing, then regenerate
`Scripts/Generated/GuiScreens.fos` with the project generator. No generated
file is hand-edited.

**Requirements:** [content workflow](../ContentWorkflow.md#gui-generation),
[nullability](../Nullability.md), [animation/GUI verification](../BuildAndLaunch.md#select-verification-by-the-change).

## Root cause

`Gui::GetFocusedObjects()` can return an object without a parent (a screen root
or another top-level object). The `Tip` draw handlers in `Gui/Character.fogui`
and `Gui/Registration.fogui` call
`GuiScreensExt::NeedObject(obj.Parent)` unconditionally; `NeedObject` throws on
`null` by design. Commit `592a721fa` replaced the nullable
`cast<BaseStat>(obj.Parent)` form with this narrowing, so the old no-op case now
throws on every draw and floods the log (837 repeats in the recorded session).

## Scope

- `Gui/Character.fogui`: guard all parent-derived stat checks and the trailing
  `PropsPanel` lookup; keep the `TextLevel`/`TextExp` checks working without a
  parent.
- `Gui/Registration.fogui`: guard the same parent-derived stat checks.
- Regenerate `Scripts/Generated/GuiScreens.fos`; no other GUI behavior changes.
- Do not touch `NeedObject` itself: callers with a real contract still rely on
  its loud failure.

## Steps and acceptance

- [x] Capture the current manifest/hash of `Scripts/Generated/GuiScreens.fos`
  and confirm the generator reproduces it before the edit.
- [x] Edit both `.fogui` sources; parent == null skips parent-derived updates
  and no longer throws.
- [x] Run `Generate :: GuiScreens.fos`; inspect the generated diff against the
  sources.
- [x] `CompileAngelScript`; the native roles were already built from the same
  Engine bump and no native source changed here.
- [x] Bake resources; run the AngelScript harness under `LocalTest`.
- [x] Run the GUI generator tests and formatter; confirm no unrelated churn.
- [ ] Validate the visible tip path with an ordinary client session if
  available; otherwise record the exact limitation.

## Verification record

Evidence root: ignored `Workspace/gui-tip-null-parent/`.

Before the edit, regenerating `GuiScreens.fos` from the unchanged sources
reproduced the committed file byte-for-byte (no diff). After the edit, the
generated diff contains only the `Registration::Tip` and `Character::Tip`
draw handlers; the two `.fogui` diffs contain only the parent guards.

- `CompileAngelScript`: exit 0, "Scripts compilation succeeded!".
- `BakeResources`: exit 0, "Baking complete!", no warnings; the three
  `Scripts.fos-bin-*` outputs were rebuilt.
- `TLA_ServerHeadless.exe --ApplySubConfig LocalTest --Testing.Enabled True`:
  exit 0, `COMPLETE: 128 passed, 0 failed, 0 skipped (of 128)`.
- `pytest Tools`: 220 passed, 89 subtests; `Tools/InterfaceEditor` tests:
  4 passed. Formatter `scripts --check`: 0 changed. Nullable markers,
  validator tests, placement, coverage and the script-quality ratchet: exit 0.
  `git diff --check`: clean.

Qualification limit: no ordinary client session was run. Reproducing the
logged path needs a live character screen with a focused parentless object;
the local Memory DB has no account, and the change is CLIENT-only, so the
server harness cannot exercise `Tip::OnDraw`. The fix removes the throw and
keeps the parent-present behavior unchanged; the owner should confirm the
original hover/focus scenario in a normal client session.
