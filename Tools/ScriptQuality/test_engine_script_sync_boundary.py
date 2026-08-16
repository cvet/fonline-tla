from __future__ import annotations

import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTING_ROOT = PROJECT_ROOT / "Engine/Source/Scripting"


class EngineScriptSyncBoundaryTests(unittest.TestCase):
    def test_engine_script_methods_block_only_in_explicit_game_sync(self) -> None:
        calls: list[tuple[str, str]] = []
        for path in SCRIPTING_ROOT.glob("*.cpp"):
            source = path.read_text(encoding="utf-8-sig")
            for match in re.finditer(r"\bSyncEntit(?:y|ies)\s*\(", source):
                api_at = source.rfind("FO_SCRIPT_API", 0, match.start())
                if api_at < 0:
                    calls.append((path.name, "<outside FO_SCRIPT_API>"))
                    continue

                signature_end = source.find("{", api_at, match.start())
                signature = source[api_at:signature_end]
                calls.append((path.name, " ".join(signature.split())))

        self.assertTrue(calls, "expected the explicit Game.Sync implementation to remain present")
        for path, signature in calls:
            with self.subTest(path=path, signature=signature):
                self.assertEqual(path, "ServerGlobalScriptMethods.cpp")
                self.assertIn("Server_Game_Sync(", signature)

    def test_gameplay_scripts_call_game_sync_only_through_sync_module(self) -> None:
        offenders: list[str] = []
        for path in (PROJECT_ROOT / "Scripts").glob("*.fos"):
            if path.name == "Sync.fos":
                continue

            source = path.read_text(encoding="utf-8-sig")
            source = re.sub(r"//.*", "", source)
            if "Game.Sync(" in source:
                offenders.append(path.name)

        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
