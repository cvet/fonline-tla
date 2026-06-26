#!/usr/bin/env python3
"""Launch-option discovery helpers for the The Life After AI-control MCP adapter."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any


def binary_name_for_role(role: str) -> str:
    suffix = ".exe" if os.name == "nt" else ""
    return {
        "server": f"TLA_Server{suffix}",
        "server_headless": f"TLA_ServerHeadless{suffix}",
        "client": f"TLA_Client{suffix}",
        "client_headless": f"TLA_ClientHeadless{suffix}",
    }[role]


def format_setting_value(value: Any) -> str:
    if isinstance(value, bool):
        return "True" if value else "False"
    return str(value)


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def normalize_launch_accounts(accounts: Any) -> list[dict[str, str]]:
    if accounts is None:
        return []
    if not isinstance(accounts, list):
        raise ValueError("accounts must be an array")

    normalized: list[dict[str, str]] = []
    for index, account in enumerate(accounts):
        if isinstance(account, str):
            name = account
            password = ""
        elif isinstance(account, dict):
            raw_name = account.get("name", account.get("login", account.get("accountId", "")))
            name = str(raw_name)
            password = str(account.get("password", ""))
        else:
            raise ValueError(f"accounts[{index}] must be a string or object")

        name = name.strip()
        password = password.strip()
        if not name:
            raise ValueError(f"accounts[{index}] has empty name")
        if ";" in name or ";" in password:
            raise ValueError("accounts names/passwords cannot contain ';'")

        normalized.append({"name": name, "password": password})

    return normalized


def encode_launch_setting_list(values: list[str]) -> str:
    return ";".join(values)


def launch_recipe_arguments(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "tla_launch_scene":
        return build_scene_launch_arguments(arguments)
    if name == "tla_launch_accounts":
        return build_accounts_launch_arguments(arguments)
    if name == "tla_launch_two_players":
        return build_two_players_launch_arguments(arguments)
    raise ValueError(f"Unknown launch recipe: {name}")


def build_scene_launch_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    scene = str(arguments.get("scene", "")).strip()
    if not scene:
        raise ValueError("scene is required")

    launch_args = copy_launch_arguments(arguments)
    launch_args.setdefault("role", "server_headless")
    launch_args.setdefault("subConfig", "SceneLaunch")
    set_launch_setting(launch_args, "Scene.Startup", scene)
    return launch_args


def build_accounts_launch_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    accounts = normalize_launch_accounts(arguments.get("accounts"))
    if not accounts:
        raise ValueError("accounts must contain at least one account")

    launch_args = copy_launch_arguments(arguments)
    launch_args["accounts"] = accounts
    launch_args.setdefault("role", "server_headless")
    launch_args.setdefault("subConfig", "SceneLaunch")

    scene = str(arguments.get("scene", "")).strip()
    if scene:
        set_launch_setting(launch_args, "Scene.Startup", scene)

    return launch_args


def build_two_players_launch_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    accounts = normalize_launch_accounts(arguments.get("accounts"))
    if accounts and len(accounts) != 2:
        raise ValueError("tla_launch_two_players accounts must contain exactly two entries")

    launch_args = copy_launch_arguments(arguments)
    launch_args.setdefault("role", "server_headless")
    launch_args.setdefault("subConfig", "SceneLaunchTwoPlayers")
    launch_args.setdefault("clientCount", 2)
    if accounts:
        launch_args["accounts"] = accounts

    scene = str(arguments.get("scene", "Intro")).strip()
    if scene:
        set_launch_setting(launch_args, "Scene.Startup", scene)

    return launch_args


def copy_launch_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    launch_args = dict(arguments)
    launch_args.pop("scene", None)

    settings = dict(launch_args.get("settings") or {})
    launch_args["settings"] = settings
    return launch_args


def set_launch_setting(arguments: dict[str, Any], name: str, value: Any) -> None:
    settings = dict(arguments.get("settings") or {})
    settings[name] = value
    arguments["settings"] = settings


def build_launch_options(workspace_root: Path, schema_version: int, launch_roles: tuple[str, ...]) -> dict[str, Any]:
    fomain_path = workspace_root / "TLA.fomain"
    tasks_path = workspace_root / ".vscode" / "tasks.json"
    scenes_dir = workspace_root / "Scripts" / "Scenes"

    subconfigs, base_settings = parse_fomain_launch_config(fomain_path)
    vscode_scenes, default_scene = parse_startup_scene_input(tasks_path)
    scene_scripts = sorted(path.stem.removeprefix("Scene_") for path in scenes_dir.glob("Scene_*.fos")) if scenes_dir.exists() else []
    scene_script_set = set(scene_scripts)
    task_scene_set = set(vscode_scenes)
    script_backed_task_scenes = [scene for scene in vscode_scenes if scene in scene_script_set]
    selectable_scenes = script_backed_task_scenes if vscode_scenes else scene_scripts
    missing_scene_scripts = [scene for scene in vscode_scenes if scene not in scene_script_set]
    script_only_scenes = [scene for scene in scene_scripts if vscode_scenes and scene not in task_scene_set]

    return {
        "schemaVersion": schema_version,
        "workspaceRoot": str(workspace_root),
        "configPath": str(fomain_path),
        "tasksPath": str(tasks_path),
        "roles": list(launch_roles),
        "defaultLaunch": {
            "role": "server_headless",
            "subConfig": "SceneLaunch",
            "clientCount": 1,
            "sceneSetting": "Scene.Startup",
            "scene": default_scene or (selectable_scenes[0] if selectable_scenes else ""),
            "enableAiControl": True,
            "waitForBridge": True,
            "selectFirstEndpoint": True,
        },
        "shortcuts": {
            "subConfig": "Pass to tla_launch.subConfig; applied before explicit settings overrides.",
            "scene": "Pass through tla_launch.settings as Scene.Startup.",
            "clientCount": "Pass to tla_launch.clientCount for server/server_headless embedded clients.",
            "autoLoginName": "Shortcut for Auth.AutoLoginName; embedded clients derive suffixes from client index.",
            "autoLoginPassword": "Shortcut for Auth.AutoLoginPassword.",
            "accounts": "Array of account strings or objects with name/password; maps to Auth.AutoLoginNames/Auth.AutoLoginPasswords and sets clientCount when omitted.",
            "aiControl": "Use aiControlPort / aiControlToken / aiControlPortStride or the aiControl object.",
        },
        "subConfigs": subconfigs,
        "baseSettings": base_settings,
        "startupScenes": {
            "default": default_scene,
            "vscodeOptions": vscode_scenes,
            "sceneScripts": scene_scripts,
            "missingSceneScripts": missing_scene_scripts,
            "scriptOnly": script_only_scenes,
            "selectable": selectable_scenes,
        },
    }


def parse_fomain_launch_config(path: Path) -> tuple[list[dict[str, Any]], dict[str, str]]:
    if not path.exists():
        return [], {}

    subconfigs: list[dict[str, Any]] = []
    base_settings: dict[str, str] = {}
    current_section = ""
    current_subconfig: dict[str, Any] | None = None

    def flush_subconfig() -> None:
        nonlocal current_subconfig
        if current_subconfig is None:
            return
        if current_subconfig.get("name"):
            subconfigs.append(current_subconfig)
        current_subconfig = None

    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("[") and line.endswith("]"):
            flush_subconfig()
            current_section = line[1:-1].strip()
            if current_section == "SubConfig":
                current_subconfig = {"name": "", "parent": "", "settings": {}}
            continue

        if "=" not in line:
            continue

        key, value = (part.strip() for part in line.split("=", 1))
        if current_section == "SubConfig" and current_subconfig is not None:
            if key == "Name":
                current_subconfig["name"] = value
            elif key == "Parent":
                current_subconfig["parent"] = value
            else:
                current_subconfig["settings"][key] = value
        elif not current_section:
            base_settings[key] = value

    flush_subconfig()
    return subconfigs, base_settings


def parse_startup_scene_input(path: Path) -> tuple[list[str], str]:
    if not path.exists():
        return [], ""

    text = path.read_text(encoding="utf-8-sig")
    try:
        tasks = json.loads(text)
    except json.JSONDecodeError:
        return parse_startup_scene_input_fallback(text)

    inputs = tasks.get("inputs", [])
    if not isinstance(inputs, list):
        return [], ""

    for entry in inputs:
        if not isinstance(entry, dict) or entry.get("id") != "startupSceneName":
            continue
        options = entry.get("options", [])
        scenes = [str(option) for option in options if isinstance(option, str)]
        default = entry.get("default")
        return scenes, str(default) if isinstance(default, str) else ""

    return [], ""


def parse_startup_scene_input_fallback(text: str) -> tuple[list[str], str]:
    input_match = re.search(r'\{[^{}]*"id"\s*:\s*"startupSceneName"[^{}]*\}', text, re.DOTALL)
    if input_match is None:
        return [], ""

    block = input_match.group(0)
    options_match = re.search(r'"options"\s*:\s*\[(.*?)\]', block, re.DOTALL)
    scenes = re.findall(r'"([^"]+)"', options_match.group(1)) if options_match is not None else []
    default_match = re.search(r'"default"\s*:\s*"([^"]+)"', block)
    return scenes, default_match.group(1) if default_match is not None else ""
