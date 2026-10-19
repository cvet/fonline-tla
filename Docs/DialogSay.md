# Text input from a dialog

A speech may declare an optional `SayScript` before its first `Answer`:

```text
Speech 3
  Script ReplicationTerminal::TransferReal
  SayScript ReplicationTerminal::HandleTransferReal
  Answer Back
```

`Script` still prepares speech lexemes when entering the speech. `SayScript`
receives submitted text, with this exact signature:

```angelscript
void HandleTransferReal(Critter player, Critter? talker, string text)
```

The talker is null for scenery dialogs. The baker checks that the handler exists
and has the expected signature. A missing `SayScript` disables the Say button's
action. Duplicate bindings, missing arguments, and bindings after answers are
syntax errors.

The client sends only text and the speech revision captured when opening Say.
`Scripts/Say.fos` resolves the dialog, speech and talker from the server's current
`DialogContext`. It checks the revision, life, map, timeout and conversation
conditions before calling the handler. Reopening Say on the same speech works
without rerunning `Script`; accepted submissions do not consume the binding.
Handlers must validate gameplay-specific inputs and balances on every call.

Changing speech or closing the dialog invalidates old input. Reinitializing the
client closes the old conversation. No handler selection is persisted in
`SayHandlerId`, and dialog text does not fire `OnPlayerSaidText`.
Standalone input also uses `Say`, with a one-shot server callback (see below).

Verification after rebuilding and baking:

- Open `repl_terminal`, enter a sum, then submit again from the same speech.
- Cancel Say, reopen it, and submit a valid sum.
- Try entering text on a speech without `SayScript`.
- Submit a captured request after changing speech, closing the dialog, moving
  out of range, expiry or reconnecting: no handler must run.
- Exercise both barman name-entry branches and the terminal recipient branch.

Native parser coverage is in `SourceExt/TestDialogs.cpp` (`Dialog SayScript*`).

## Selecting an answer from server scripts

Use `Dialogs::ForceDialogResult(player, talkerId, dialogId, isNpc, result, refresh)`.
For NPC dialogs pass the NPC id and the active dialog pack id; for scenery dialogs
pass `ZERO_IDENT` and `isNpc = false`. The function requires a matching active
conversation and uses the same demand checks, answer results and transition logic
as a player click. `result` is the zero-based index in the displayed answer list,
not a speech id. Answer result scripts may override the target speech.

`refresh` resends the existing context before selecting the answer; it does not
restart the dialog or rerun its speech script. `0xF0` only refreshes, `0xF1` closes
and `0xF2` selects barter, preserving the old special answer codes.

The former client RPC was a no-op after removal of `Game.CustomCall`. Call the
server helper directly instead of `player.PlayerClientCall.ForceDialogResult`.
The terminal recipient handler now selects answer index 1, whose
`ChoosePlayerResult` routes to speech 3 (self) or 8 (another player).

Legacy reference: `C:/work/foclassic/Source/ServerNpc.cpp`, answer processing near
lines 1703–1738. `ANSWER_BEGIN` called `Send_Talk`; normal answers were indexed
from zero, rechecked, and passed through `Dialog_UseResult` before following links.

## Standalone input

`Say::Show(player, titleKey, inputKey, handler, context)` opens the same Say window
without a dialog. Use `TextPackKey()` for an empty initial input. Both non-empty
keys are localized on the client. The callback has this signature:

```angelscript
void HandleText(Critter player, string text, any[] context)
```

`context` stays on the server. ElectronicLock passes the lock id; CompRiddle
passes map id, scenery prototype and hex. Both revalidate their target on reply.
The client sends only a request id, text and a cancellation flag. The server
checks the owner, controlled critter, life, map, distance and 120-second timeout.
It consumes the request before invoking the callback. Cancel, logout, client
reinitialization, death, knockout, opening another request or starting a dialog
revokes the old binding. A callback may open another request safely.

The in-memory callback registry requires the `Say` mutable-global exception; it
is intentionally not saved. Lifecycle events clean up requests; no event is used
to dispatch submitted text. The deprecated SayExtended screen has no input RPCs.
Its `CanSendSay` property remains only for save compatibility and grants no access.

Legacy reference: `C:/work/foclassic/Source/ServerScript.cpp`, `Cl_ShowScreen`,
bound a script callback and stored `ScreenCallbackBindId` on the player.
This implementation requires no engine or SourceExt changes.

Regression harness: `Scripts/Tests/Test_Say.fos` checks owner isolation, duplicate
submission and cancellation. In-game checks: cancel/reopen, replace an open
request, submit after walking away or reconnecting, and repeat both lock and
computer interactions. Rebuild/bake scripts before testing.
