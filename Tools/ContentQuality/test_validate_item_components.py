#!/usr/bin/env python3

from __future__ import annotations

import contextlib
import io
import re
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate_item_components as validator  # noqa: E402 - import the sibling tool under test.


ROOT = Path(__file__).resolve().parents[2]

LEGACY_PREFIX_RE = re.compile(r"^(Weapon|Armor|Ammo|Car|Door|Locker|Container|Grid|Lockpick)_")
LEGACY_EXTRA_NAMES = {"Type", "CarIsBioEngine", "CarIsNoLockpick", "IsLockpick"}


def write(root: Path, relative: str, text: str) -> None:
    """Write authored text the way the repository stores it: UTF-8 with CRLF."""
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))


def marker(component: str, side: str = "Common") -> str:
    return f"///@ Property Item {side} bool {component} Component"


def component_field(component: str, name: str, type_name: str = "int32") -> str:
    return f"///@ Property Item Common {type_name} {component}.{name} Mutable PublicSync Persistent"


TYPE_DECLARATION = "///@ Property Item Common ItemType Type Mutable PublicSync Persistent"


def declare(root: Path, *declarations: str) -> None:
    write(root, "Scripts/Declarations.fos", "namespace Declarations\n{\n\n" + "\n".join(declarations) + "\n\n}\n")


def proto(name: str, *lines: str) -> str:
    return "[ProtoItem]\n$Name = " + name + "\n" + "".join(line + "\n" for line in lines) + "\n"


def map_item(proto_name: str, *lines: str) -> str:
    return "[$Name/Item]\n$Id = 1\n$Proto = " + proto_name + "\nHex = 10 10\n" + "".join(line + "\n" for line in lines) + "\n"


def write_map(root: Path, *sections: str) -> None:
    write(root, "Maps/test_map.fomap", "[ProtoMap]\n$Name = test_map\n\n" + "".join(sections))


def found(root: Path) -> list[tuple[str, str, int]]:
    return [(violation.code, violation.path, violation.line) for violation in validator.validate(root)]


def found_codes(root: Path) -> list[str]:
    return [violation.code for violation in validator.validate(root)]


def test_field_without_marker_is_error(tmp_path: Path) -> None:
    declare(tmp_path, marker("Weapon"), component_field("Weapon", "MaxAmmoCount"))
    write(tmp_path, "Items/pistol.foitem", proto("pistol", "Weapon.MaxAmmoCount = 6"))
    write(tmp_path, "Items/gun.foitem", proto("gun", "Weapon = True", "Weapon.MaxAmmoCount = 6"))
    write(tmp_path, "Items/rock.foitem", proto("rock", "Weight = 100"))
    write_map(
        tmp_path,
        map_item("rock", "Weapon.MaxAmmoCount = 1"),
        map_item("gun", "Weapon.MaxAmmoCount = 2"),
    )

    assert found(tmp_path) == [
        ("field-without-marker", "Items/pistol.foitem", 3),
        ("field-without-marker", "Maps/test_map.fomap", 8),
    ]


def test_inherited_marker_enables_child_fields(tmp_path: Path) -> None:
    declare(tmp_path, marker("Weapon"), component_field("Weapon", "MaxAmmoCount"))
    write(tmp_path, "Items/base_weapon.foitem", proto("base_weapon", "Weapon = True"))
    write(
        tmp_path,
        "Items/rifles.foitem",
        proto("rifle", "$Parent = base_weapon", "Weapon.MaxAmmoCount = 5")
        + proto("sniper_rifle", "$Parent = rifle", "Weapon.MaxAmmoCount = 1"),
    )
    write_map(tmp_path, map_item("sniper_rifle", "Weapon.MaxAmmoCount = 3"))

    assert found(tmp_path) == []


def test_parent_order_and_repeated_parents_follow_baker(tmp_path: Path) -> None:
    declare(tmp_path, marker("Weapon"), component_field("Weapon", "MaxAmmoCount"))
    write(
        tmp_path,
        "Items/parents.foitem",
        proto("enabled", "Weapon = True")
        + proto("disabled", "Weapon = False")
        + proto("right_disables", "$Parent = enabled disabled", "Weapon.MaxAmmoCount = 1")
        + proto("right_enables", "$Parent = disabled enabled", "Weapon.MaxAmmoCount = 1")
        + proto("mid_disables", "$Parent = enabled", "Weapon = False")
        + proto("mid_keeps", "$Parent = enabled")
        + proto("diamond", "$Parent = mid_disables mid_keeps", "Weapon.MaxAmmoCount = 1"),
    )

    # The rightmost parent wins; a repeated ancestor contributes only at its first reach,
    # so "enabled" reached again through mid_keeps does not undo mid_disables.
    assert [(code, line) for code, _path, line in found(tmp_path)] == [
        ("field-without-marker", 12),
        ("field-without-marker", 31),
    ]


def test_marker_on_map_instance_is_error(tmp_path: Path) -> None:
    declare(tmp_path, marker("Weapon"), marker("Radio"))
    write(tmp_path, "Items/gun.foitem", proto("gun", "Weapon = True"))
    write(tmp_path, "Items/radio.foitem", proto("radio", "Radio = True"))
    write_map(tmp_path, map_item("gun", "Weapon = True"), map_item("radio", "Radio = False"))

    assert found(tmp_path) == [
        ("marker-on-instance", "Maps/test_map.fomap", 8),
        ("marker-on-instance", "Maps/test_map.fomap", 14),
    ]


def test_two_kind_markers_is_error(tmp_path: Path) -> None:
    declare(tmp_path, marker("Weapon"), marker("Armor"), marker("Radio"))
    write(tmp_path, "Items/hybrid.foitem", proto("hybrid", "Weapon = True", "Armor = True"))
    write(tmp_path, "Items/gun.foitem", proto("gun", "Weapon = True", "Radio = True"))

    assert found(tmp_path) == [("exclusive-kind", "Items/hybrid.foitem", 1)]


def test_locker_requires_door_or_container(tmp_path: Path) -> None:
    active = tmp_path / "active"
    declare(active, marker("Locker"), marker("Door"), marker("Container"))
    write(active, "Items/door.foitem", proto("door", "Door = True", "Locker = True"))
    write(active, "Items/locker.foitem", proto("locker", "Container = True", "Locker = True"))
    write(active, "Items/box.foitem", proto("box", "Container = True"))
    write(active, "Items/lock.foitem", proto("lock", "Locker = True"))

    assert found(active) == [
        ("locker-mismatch", "Items/box.foitem", 1),
        ("locker-mismatch", "Items/lock.foitem", 1),
    ]

    inactive = tmp_path / "inactive"
    declare(inactive, marker("Locker"), marker("Container"))
    write(inactive, "Items/lock.foitem", proto("lock", "Locker = True"))

    assert found(inactive) == []


def test_portable_kind_on_static_is_error(tmp_path: Path) -> None:
    declare(tmp_path, marker("Weapon"))
    write(tmp_path, "Items/gun.foitem", proto("gun", "Weapon = True"))
    write(tmp_path, "Items/legacy_static_gun.foitem", proto("legacy_static_gun", "Weapon = True", "IsStatic = True"))
    write(tmp_path, "Items/static_gun.foitem", proto("static_gun", "Weapon = True", "Static = True"))
    write(tmp_path, "Items/wall.foitem", proto("wall", "IsStatic = True"))

    assert found(tmp_path) == [
        ("static-mismatch", "Items/legacy_static_gun.foitem", 1),
        ("static-mismatch", "Items/static_gun.foitem", 1),
    ]


def test_grid_on_dynamic_is_error(tmp_path: Path) -> None:
    declare(tmp_path, marker("Grid"))
    write(tmp_path, "Items/exit_grid.foitem", proto("exit_grid", "Grid = True", "IsStatic = True"))
    write(tmp_path, "Items/stairs.foitem", proto("stairs", "Grid = True", "Static = true"))
    write(tmp_path, "Items/loose_grid.foitem", proto("loose_grid", "Grid = True"))
    write(tmp_path, "Items/unstatic_grid.foitem", proto("unstatic_grid", "Grid = True", "IsStatic = False"))

    assert found(tmp_path) == [
        ("static-mismatch", "Items/loose_grid.foitem", 1),
        ("static-mismatch", "Items/unstatic_grid.foitem", 1),
    ]


def test_type_marker_mismatch_while_type_declared(tmp_path: Path) -> None:
    declare(tmp_path, TYPE_DECLARATION, marker("Weapon"))
    write(tmp_path, "Items/typed_only.foitem", proto("typed_only", "Type = Weapon"))
    write(tmp_path, "Items/marker_only.foitem", proto("marker_only", "Type = Misc", "Weapon = True"))
    write(tmp_path, "Items/gun.foitem", proto("gun", "Type = Weapon", "Weapon = True"))
    write(tmp_path, "Items/inherited.foitem", proto("inherited", "$Parent = typed_only", "Weapon = True"))
    write(tmp_path, "Items/armor.foitem", proto("armor", "Type = Armor"))
    write_map(tmp_path, map_item("gun", "Type = Misc"))

    # Armor is not declared as a component yet, so its Type value is not checked.
    assert found(tmp_path) == [
        ("transition-mismatch", "Items/marker_only.foitem", 1),
        ("transition-mismatch", "Items/typed_only.foitem", 1),
        ("transition-mismatch", "Maps/test_map.fomap", 4),
    ]


def test_type_key_after_type_removed_is_error(tmp_path: Path) -> None:
    declare(tmp_path, marker("Weapon"))
    write(tmp_path, "Items/gun.foitem", proto("gun", "Type = Weapon", "Weapon = True"))
    write(tmp_path, "Items/rock.foitem", proto("rock", "Weight = 1"))
    write_map(tmp_path, map_item("rock", "Type = Misc"))

    assert found(tmp_path) == [
        ("legacy-type-key", "Items/gun.foitem", 3),
        ("legacy-type-key", "Maps/test_map.fomap", 8),
    ]


def test_legacy_prefixed_key_for_declared_component_is_error(tmp_path: Path) -> None:
    declare(tmp_path, marker("Weapon"), component_field("Weapon", "MaxAmmoCount"))
    write(
        tmp_path,
        "Items/gun.foitem",
        proto("gun", "Weapon = True", "Weapon_MaxAmmoCount = 6", "Armor_AC = 5", "Weapon.MaxAmmoCount = 6"),
    )
    write_map(tmp_path, map_item("gun", "Weapon_Skill_0 = SkillSmallGuns", "Grid_ToMap = elsewhere"))

    # Armor and Grid are not declared components, so their flat keys are still legal.
    assert found(tmp_path) == [
        ("legacy-prefixed-key", "Items/gun.foitem", 4),
        ("legacy-prefixed-key", "Maps/test_map.fomap", 8),
    ]


def test_removed_legacy_name_requires_migration_rule(tmp_path: Path) -> None:
    declare(tmp_path, TYPE_DECLARATION, marker("Weapon"), component_field("Weapon", "MaxAmmoCount"))
    write(tmp_path, "Tools/ContentQuality/item_component_legacy_names.txt", "IsLockpick\nType\nWeapon_Caliber\nWeapon_MaxAmmoCount\n")
    write(
        tmp_path,
        "Scripts/Migration.fos",
        "namespace Migration\n{\n\n#if SERVER\n\n"
        "///@ MigrationRule Property Item Rename Weapon_MaxAmmoCount Weapon.MaxAmmoCount\n"
        "///@ MigrationRule Property Item Remove IsLockpick\n"
        "///@ MigrationRule Property Critter Remove Weapon_Caliber\n"
        "\n#endif\n\n}\n",
    )

    # Type is still declared, so it needs no rule yet; the Critter rule does not cover an Item name.
    assert found(tmp_path) == [("missing-migration-rule", "Tools/ContentQuality/item_component_legacy_names.txt", 3)]


def test_rename_target_must_be_declared(tmp_path: Path) -> None:
    declare(
        tmp_path,
        marker("Weapon"),
        component_field("Weapon", "MaxAmmoCount"),
        "///@ Property Item Common string TextArgs Mutable PublicSync Persistent",
        "///@ Property Critter Common int32 CritterOnly Mutable",
    )
    write(tmp_path, "Scripts/Generated/GuiScreens.fos", component_field("Weapon", "Calibre", "Caliber") + "\n")
    write(
        tmp_path,
        "Engine/Source/Common/EntityProperties.h",
        "class ItemProperties : public EntityProperties\n{\npublic:\n"
        "    ///@ MigrationRule Property Item Rename IsStatic Static\n"
        "    ///@ ExportProperty Common Persistent\n"
        "    FO_ENTITY_PROPERTY(bool, Static);\n"
        "    FO_ENTITY_PROPERTY(vector<uint8_t>, MultihexLines);\n"
        "};\n\n"
        "class CritterProperties : public EntityProperties\n{\npublic:\n"
        "    FO_ENTITY_PROPERTY(int32_t, Multihex);\n"
        "};\n",
    )
    write(
        tmp_path,
        "Scripts/Migration.fos",
        "namespace Migration\n{\n\n#if SERVER\n\n"
        "///@ MigrationRule Property Item Rename Lexems TextArgs\n"
        "///@ MigrationRule Property Item Rename Weapon_MaxAmmoCount Weapon.MaxAmmoCount\n"
        "///@ MigrationRule Property Item Rename OldStatic Static\n"
        "///@ MigrationRule Property Item Rename BlockLinesOld MultihexLines\n"
        "///@ MigrationRule Property Item Rename Weapon_Caliber Weapon.Calibre\n"
        "///@ MigrationRule Property Item Rename OldMultihex Multihex\n"
        "///@ MigrationRule Property Item Rename OldCritterOnly CritterOnly\n"
        "///@ MigrationRule Property Critter Rename Lexems Missing\n"
        "\n#endif\n\n}\n",
    )

    # Generated scripts do not declare metadata, and Critter-only names are not Item targets.
    assert found(tmp_path) == [
        ("dangling-migration-target", "Scripts/Migration.fos", 10),
        ("dangling-migration-target", "Scripts/Migration.fos", 11),
        ("dangling-migration-target", "Scripts/Migration.fos", 12),
    ]


def test_cli_reports_summary_and_exit_code(tmp_path: Path) -> None:
    declare(tmp_path, marker("Weapon"), component_field("Weapon", "MaxAmmoCount"))
    write(tmp_path, "Items/gun.foitem", proto("gun", "Weapon = True", "Weapon.MaxAmmoCount = 6"))

    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        assert validator.main(["--root", str(tmp_path), "--summary"]) == 0
    assert "Result: 0 violation(s)." in output.getvalue()

    write(tmp_path, "Items/pistol.foitem", proto("pistol", "Weapon.MaxAmmoCount = 6"))
    output = io.StringIO()
    errors = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
        assert validator.main(["--root", str(tmp_path)]) == 1
    assert "field-without-marker: 1" in output.getvalue()
    assert "Result: 1 violation(s)." in output.getvalue()
    assert "Items/pistol.foitem:3: [field-without-marker]" in errors.getvalue()


def test_legacy_manifest_is_frozen_baseline() -> None:
    names = (ROOT / "Tools/ContentQuality/item_component_legacy_names.txt").read_text(encoding="utf-8").splitlines()

    assert len(names) == 115
    assert len(set(names)) == len(names)
    assert LEGACY_EXTRA_NAMES <= set(names)
    assert all(LEGACY_PREFIX_RE.match(name) or name in LEGACY_EXTRA_NAMES for name in names)
    assert sum(1 for name in names if LEGACY_PREFIX_RE.match(name)) == 111


def test_repository_is_clean() -> None:
    result = validator.scan_project(ROOT)

    assert result.proto_count > 0
    assert result.instance_count > 0
    assert "Radio" in result.components
    assert [validator.format_violation(violation) for violation in result.violations] == []
