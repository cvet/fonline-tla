from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BAG_ID_RE = re.compile(r"^BagId\s*=\s*(\d+)\s*$", re.MULTILINE)

class MapBagIdContractTests(unittest.TestCase):
    def test_all_map_bag_ids_exist_in_server_config(self) -> None:
        config = json.loads(
            (PROJECT_ROOT / "Resources/ServerData/BagsConfig.json").read_text(encoding="utf-8-sig")
        )
        configured = {int(entry["BagId"]) for entry in config}
        missing: set[tuple[str, int]] = set()

        for path in sorted((PROJECT_ROOT / "Maps").glob("*.fomap")):
            for match in BAG_ID_RE.finditer(path.read_text(encoding="utf-8-sig")):
                bag_id = int(match.group(1))
                if bag_id not in configured:
                    missing.add((path.name, bag_id))

        self.assertEqual(missing, set())

    def test_repaired_map_bags_match_their_authored_roles(self) -> None:
        intro = (PROJECT_ROOT / "Maps/intro_init.fomap").read_text(encoding="utf-8-sig")
        redding = (PROJECT_ROOT / "Maps/redding_miners.fomap").read_text(encoding="utf-8-sig")
        sf_hubb = (PROJECT_ROOT / "Maps/sf_hubb.fomap").read_text(encoding="utf-8-sig")

        self.assertEqual(intro.count("$Proto = BosPrivate\nBagId = 263"), 2)
        self.assertIn("$Proto = Wade\nAiId = 22\nBagId = 85\nDialogId = redd_andrew", redding)
        self.assertIn(
            "$Proto = HubologistGuard\nAiId = 22\nBagId = 81\nDialogId = redd_gate_guard_inner",
            redding,
        )
        self.assertNotIn("BagId = 203", sf_hubb)

    def test_den_replication_bank_guards_use_configured_bags(self) -> None:
        config = json.loads(
            (PROJECT_ROOT / "Resources/ServerData/BagsConfig.json").read_text(encoding="utf-8-sig")
        )
        configured = {int(entry["BagId"]) for entry in config}
        source = (PROJECT_ROOT / "Maps/repl_bank_den.fomap").read_text(encoding="utf-8-sig")

        self.assertTrue({int(value) for value in BAG_ID_RE.findall(source)} <= configured)


if __name__ == "__main__":
    unittest.main()
