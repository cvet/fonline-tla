# NullableEstimate

Nullability checks and migration helpers for TLA scripts and native script bindings.

## Active gate

Run from the repository root:

```bash
python Tools/NullableEstimate/test_validate_nullable.py
python Tools/NullableEstimate/validate_nullable.py
```

`validate_nullable.py` checks two contracts:

- AngelScript `T?` placement plus `///@ Event` / `///@ RemoteCall` handler parity.
- Native script handles: non-null is `ptr<T>`, nullable is `nptr<T>`, and bare `T*` is rejected in `///@ ExportMethod`/`FO_SCRIPT_API` signatures, members named by `///@ ExportRefType ... Export = ...`, and `FindFunc`/`CheckFunc` template arguments.

The native scan is intentionally boundary-specific. It does not report ordinary internal raw pointers or `///@ EngineHook` declarations such as `SetupBakersHook`; those use different native contracts. Comments and string literals are ignored.

`FO_NULLABLE` belonged to the former raw-pointer ABI and is now rejected. Choose `ptr<T>` or `nptr<T>` directly instead.

## Other tools

- `apply_nullables.py`: script-side analysis and cleanup; pass `--check` for a read-only CI gate.
- `estimate_nullables.py`: script nullability coverage report.
- `analyze_redundant_nullchecks.py`, `auto_mark_nullables.py`, `find_dead_nullchecks.py`: focused migration/audit helpers.
- `apply_native_nullable.py`: legacy helper for pre-`ptr`/`nptr` engine revisions; it is not part of the current gate.

The author owns nullable intent. These tools do not infer a native `ptr<T>` versus `nptr<T>` contract from function bodies.

