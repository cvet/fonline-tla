#!/usr/bin/env python3
"""Exercise an NPC barter lifecycle through the stdio MCP adapter.

The runner attaches to an already connected in-game client, uses QA commands only for setup,
opens Dialog and Barter through their real gameplay flow, captures verified screenshots, completes
one purchase, returns to Dialog, and writes a structured JSON report.

Example:
  python Tools/AiControlMcp/tla_barter_playtest.py --map arroyo \
    --npc-dialog-id arroyo_cassidy --hex 82 113 --output Workspace/AiControlBarterPlaytests/cassidy
"""

from __future__ import annotations

import argparse
import math
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable

from ai_control_runner import (
    ADAPTER_PATH,
    McpProcess,
    SmokeError,
    build_adapter_command,
    call_tool,
    configure_stdio,
    initialize_client,
    observe,
    run_command,
    wait_ready,
    write_json_report,
)
from tla_gui_screenshot_test import tga_barter_panels_are_visible


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CAPS_COUNT = 10_000
SPECIAL_DIALOG_BARTER = 0xF2


def resolve_output_directory(workspace_root: Path, requested: str) -> Path:
    if requested.strip():
        output = Path(requested).expanduser()
        if not output.is_absolute():
            output = workspace_root / output
    else:
        output = workspace_root / "Workspace" / "AiControlBarterPlaytests" / time.strftime("barter-%Y%m%d-%H%M%S")

    output = output.resolve()
    try:
        output.relative_to(workspace_root.resolve())
    except ValueError as exc:
        raise ValueError(f"--output must stay inside the workspace: {output}") from exc
    if output.exists() and not output.is_dir():
        raise ValueError(f"--output is not a directory: {output}")
    return output


def wait_for_observation(
    client: McpProcess,
    endpoint: dict[str, Any],
    predicate: Callable[[dict[str, Any]], bool],
    timeout: float,
    label: str,
    poll_interval: float = 0.2,
) -> dict[str, Any]:
    deadline = time.monotonic() + max(timeout, 0.0)
    last = observe(client, endpoint)
    while True:
        if predicate(last):
            return last
        if time.monotonic() >= deadline:
            raise SmokeError(f"timed out waiting for {label}; last observation={last}")
        time.sleep(max(poll_interval, 0.01))
        last = observe(client, endpoint)


def item_count(items: Any, proto_id: str) -> int:
    if not isinstance(items, list):
        return 0
    return sum(
        int(item.get("count", 0))
        for item in items
        if isinstance(item, dict) and str(item.get("protoId", "")) == proto_id
    )


def item_by_proto(items: Any, proto_id: str) -> dict[str, Any] | None:
    if not isinstance(items, list):
        return None
    for item in items:
        if (
            isinstance(item, dict)
            and str(item.get("protoId", "")) == proto_id
            and int(item.get("count", 0)) > 0
        ):
            return item
    return None


def barter_snapshot(observation: dict[str, Any]) -> dict[str, Any]:
    barter = observation.get("barter")
    return barter if isinstance(barter, dict) else {}


def assert_barter_contract(barter: dict[str, Any]) -> None:
    if barter.get("active") is not True:
        raise SmokeError("barter did not become active")
    if type(barter.get("session")) is not int or int(barter["session"]) <= 0:
        raise SmokeError(f"invalid barter session: {barter.get('session')!r}")
    if type(barter.get("coefficient")) is not int or not 5 <= int(barter["coefficient"]) <= 95:
        raise SmokeError(f"invalid barter coefficient: {barter.get('coefficient')!r}")
    if type(barter.get("masterTrader")) is not bool:
        raise SmokeError("barter masterTrader metadata is missing")
    for name in ("playerOfferTotal", "traderOfferTotal"):
        if type(barter.get(name)) is not int or int(barter[name]) < 0:
            raise SmokeError(f"invalid barter pricing field {name}: {barter.get(name)!r}")
    for name in ("playerInventory", "playerOffer", "traderInventory", "traderOffer"):
        if not isinstance(barter.get(name), list):
            raise SmokeError(f"barter collection {name} is missing")


def find_npc(observation: dict[str, Any], dialog_id: str, expected_hex: tuple[int, int] | None) -> dict[str, Any] | None:
    critters = observation.get("critters")
    if not isinstance(critters, list):
        return None
    matches = [
        critter
        for critter in critters
        if isinstance(critter, dict) and str(critter.get("dialogId", "")) == dialog_id
    ]
    if not matches:
        return None
    if expected_hex is None:
        chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
        expected_hex = (int(chosen.get("hexX", 0)), int(chosen.get("hexY", 0)))
    return min(
        matches,
        key=lambda critter: abs(int(critter.get("hexX", 0)) - expected_hex[0])
        + abs(int(critter.get("hexY", 0)) - expected_hex[1]),
    )


def screenshot_relative_path(workspace_root: Path, output: Path, file_name: str) -> str:
    return (output / file_name).relative_to(workspace_root).as_posix()


def capture_screenshot(
    client: McpProcess,
    endpoint: dict[str, Any],
    workspace_root: Path,
    output: Path,
    file_name: str,
    settle_ms: int,
    timeout_ms: int,
    require_barter_panels: bool = False,
) -> dict[str, Any]:
    capture = call_tool(
        client,
        "tla_save_screenshot",
        {
            **endpoint,
            "path": screenshot_relative_path(workspace_root, output, file_name),
            "settleMs": settle_ms,
            "timeoutMs": timeout_ms,
            "pollIntervalMs": 100,
        },
    )
    if capture.get("verified") is not True:
        raise SmokeError(f"screenshot {file_name} was not verified: {capture.get('failure')}")
    if require_barter_panels:
        screenshot_path = output / file_name
        try:
            panels_visible = tga_barter_panels_are_visible(screenshot_path)
        except (OSError, ValueError) as exc:
            raise SmokeError(f"screenshot {file_name} has invalid barter content: {exc}") from exc
        if not panels_visible:
            raise SmokeError(f"screenshot {file_name} does not show all barter item panels and offer totals")
        capture["contentCheck"] = {"ok": True, "message": "barter_panels_visible"}
    return capture


def wait_for_npc(
    client: McpProcess,
    endpoint: dict[str, Any],
    dialog_id: str,
    expected_hex: tuple[int, int] | None,
    timeout: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    observation = wait_for_observation(
        client,
        endpoint,
        lambda value: find_npc(value, dialog_id, expected_hex) is not None,
        timeout,
        f"visible NPC with dialogId={dialog_id}",
    )
    npc = find_npc(observation, dialog_id, expected_hex)
    if npc is None:
        raise SmokeError(f"NPC with dialogId={dialog_id} disappeared")
    return observation, npc


def cleanup_active_dialog(client: McpProcess, endpoint: dict[str, Any], timeout_ms: int) -> None:
    try:
        current = observe(client, endpoint)
        barter = barter_snapshot(current)
        if barter.get("active") is True:
            run_command(client, "tla_barter_return_dialog", endpoint, timeout_ms=timeout_ms)
            current = wait_for_observation(
                client,
                endpoint,
                lambda value: barter_snapshot(value).get("active") is not True,
                max(timeout_ms / 1000.0, 1.0),
                "barter cleanup",
            )
        dialog = current.get("dialog") if isinstance(current.get("dialog"), dict) else {}
        if dialog.get("active") is True:
            run_command(client, "tla_close_dialog", endpoint, timeout_ms=timeout_ms)
    except (OSError, SmokeError, ValueError):
        pass


def run(args: argparse.Namespace, workspace_root: Path, output: Path) -> dict[str, Any]:
    started_ms = int(time.time() * 1000)
    endpoint = {"endpointId": args.endpoint_id} if args.endpoint_id else {}
    report: dict[str, Any] = {
        "schemaVersion": 1,
        "kind": "tla_npc_barter_playtest",
        "ok": False,
        "startedAtUnixMs": started_ms,
        "config": {
            "host": args.host,
            "port": args.port,
            "endpointId": args.endpoint_id or None,
            "map": args.map,
            "npcDialogId": args.npc_dialog_id,
            "hex": list(args.hex) if args.hex else None,
            "capsCount": args.caps_count,
        },
        "outputDirectory": str(output),
        "steps": [],
        "screenshots": [],
    }

    def step(name: str, **details: Any) -> None:
        report["steps"].append({"name": name, "ok": True, **details})

    adapter_command = build_adapter_command(ADAPTER_PATH, args.host, args.port, args.timeout, args.token)
    adapter_command.extend(["--workspace-root", str(workspace_root)])
    request_timeout = max(args.timeout, args.command_timeout_ms / 1000.0 + 5.0, args.state_timeout + 5.0)
    client = McpProcess(adapter_command, request_timeout=request_timeout)
    normal_close_completed = False

    try:
        initialize_client(client, "tla-barter-playtest")
        wait_ready(
            client,
            endpoint,
            args.command_timeout_ms,
            require_map=True,
            require_chosen=True,
            poll_interval_ms=200,
        )
        initial = observe(client, endpoint)
        if initial.get("hasChosen") is not True or initial.get("hasMap") is not True:
            raise SmokeError("current client must already have a chosen critter on a map")
        if barter_snapshot(initial).get("active") is True:
            raise SmokeError("current client already has an active barter session")
        if isinstance(initial.get("dialog"), dict) and initial["dialog"].get("active") is True:
            run_command(client, "tla_close_dialog", endpoint, timeout_ms=args.command_timeout_ms)
            wait_for_observation(
                client,
                endpoint,
                lambda value: not bool((value.get("dialog") or {}).get("active")),
                args.state_timeout,
                "initial dialog close",
            )
        step("ready", map=initial.get("map"), chosen=initial.get("chosen"))

        initial_caps = item_count(initial.get("inventory"), "bottle_caps")
        run_command(
            client,
            "tla_act",
            endpoint,
            {"type": "qa_give_item", "stringArg": "bottle_caps", "intArg": args.caps_count},
            timeout_ms=args.command_timeout_ms,
            label="QA give bottle_caps",
        )
        with_caps = wait_for_observation(
            client,
            endpoint,
            lambda value: item_count(value.get("inventory"), "bottle_caps") >= initial_caps + args.caps_count,
            args.state_timeout,
            "QA bottle_caps inventory update",
        )
        step("qa_give_caps", before=initial_caps, after=item_count(with_caps.get("inventory"), "bottle_caps"))

        teleport_arguments: dict[str, Any] = {"type": "qa_teleport_map", "stringArg": args.map}
        expected_hex = tuple(args.hex) if args.hex else None
        if expected_hex is not None:
            teleport_arguments.update({"x": expected_hex[0], "y": expected_hex[1]})
        run_command(
            client,
            "tla_act",
            endpoint,
            teleport_arguments,
            timeout_ms=args.command_timeout_ms,
            label=f"QA teleport map {args.map}",
        )
        on_map, npc = wait_for_npc(
            client,
            endpoint,
            args.npc_dialog_id,
            expected_hex,
            args.state_timeout,
        )
        npc_id = npc.get("id")
        if type(npc_id) not in (int, str):
            raise SmokeError(f"NPC {args.npc_dialog_id} has no usable id")
        step("qa_teleport_map", requestedMap=args.map, actualMap=on_map.get("map"), npc=npc)

        run_command(
            client,
            "tla_talk_to",
            endpoint,
            {"targetId": npc_id},
            timeout_ms=args.command_timeout_ms,
            label=f"talk to {args.npc_dialog_id}",
        )
        dialog_observation = wait_for_observation(
            client,
            endpoint,
            lambda value: bool((value.get("dialog") or {}).get("active"))
            and str((value.get("dialog") or {}).get("dialogId", "")) == args.npc_dialog_id,
            args.state_timeout,
            f"dialog {args.npc_dialog_id}",
        )
        dialog = dialog_observation.get("dialog") or {}
        step("dialog_open", dialogId=dialog.get("dialogId"), talkerId=dialog.get("talkerId"), answers=len(dialog.get("answers") or []))
        dialog_capture = capture_screenshot(
            client,
            endpoint,
            workspace_root,
            output,
            "dialog.tga",
            args.settle_ms,
            args.command_timeout_ms,
        )
        report["screenshots"].append({"stage": "dialog", **dialog_capture})

        run_command(
            client,
            "tla_dialog_answer",
            endpoint,
            {"answerIndex": SPECIAL_DIALOG_BARTER},
            timeout_ms=args.command_timeout_ms,
            label="special barter dialog answer",
        )
        barter_observation = wait_for_observation(
            client,
            endpoint,
            lambda value: barter_snapshot(value).get("active") is True,
            args.state_timeout,
            "active NPC barter",
        )
        barter = barter_snapshot(barter_observation)
        assert_barter_contract(barter)
        session = int(barter["session"])
        if str(barter.get("traderId")) != str(npc_id):
            raise SmokeError(f"barter traderId {barter.get('traderId')} does not match talked NPC {npc_id}")
        step(
            "barter_open",
            traderId=barter.get("traderId"),
            session=session,
            coefficient=barter.get("coefficient"),
            masterTrader=barter.get("masterTrader"),
        )

        trader_items = [
            item
            for item in barter["traderInventory"]
            if isinstance(item, dict) and int(item.get("count", 0)) > 0 and str(item.get("protoId", "")) != "bottle_caps"
        ]
        if not trader_items:
            raise SmokeError(f"NPC {args.npc_dialog_id} has no non-currency barter inventory")
        trader_item = trader_items[0]
        trader_item_id = trader_item.get("id")
        trader_item_proto = str(trader_item.get("protoId", ""))
        player_item_count_before = item_count(barter["playerInventory"], trader_item_proto)
        trader_item_count_before = item_count(barter["traderInventory"], trader_item_proto)
        caps_before = item_count(barter["playerInventory"], "bottle_caps")

        run_command(
            client,
            "tla_barter_transfer",
            endpoint,
            {"itemId": trader_item_id, "source": "trader_inventory", "count": 1},
            timeout_ms=args.command_timeout_ms,
            label="move trader item to offer",
        )
        trader_offer_observation = wait_for_observation(
            client,
            endpoint,
            lambda value: int(barter_snapshot(value).get("traderOfferTotal", 0)) > 0
            and item_count(barter_snapshot(value).get("traderOffer"), trader_item_proto) >= 1,
            args.state_timeout,
            "trader offer pricing",
        )
        trader_offer = barter_snapshot(trader_offer_observation)
        trader_offer_total = int(trader_offer["traderOfferTotal"])

        caps_item = item_by_proto(trader_offer.get("playerInventory"), "bottle_caps")
        if caps_item is None:
            raise SmokeError("bottle_caps are not visible in the barter player inventory")
        run_command(
            client,
            "tla_barter_transfer",
            endpoint,
            {"itemId": caps_item.get("id"), "source": "player_inventory", "count": 1},
            timeout_ms=args.command_timeout_ms,
            label="price one bottle_cap",
        )
        one_cap_observation = wait_for_observation(
            client,
            endpoint,
            lambda value: int(barter_snapshot(value).get("playerOfferTotal", 0)) > 0,
            args.state_timeout,
            "bottle_cap offer pricing",
        )
        one_cap_barter = barter_snapshot(one_cap_observation)
        cap_unit_value = int(one_cap_barter["playerOfferTotal"])
        caps_needed = max(1, math.ceil(trader_offer_total / cap_unit_value))
        if caps_needed > caps_before:
            raise SmokeError(f"trade needs {caps_needed} bottle_caps but only {caps_before} are visible")
        if caps_needed > 1:
            run_command(
                client,
                "tla_barter_transfer",
                endpoint,
                {"itemId": caps_item.get("id"), "source": "player_inventory", "count": caps_needed - 1},
                timeout_ms=args.command_timeout_ms,
                label="move enough bottle_caps to offer",
            )

        assembled_observation = wait_for_observation(
            client,
            endpoint,
            lambda value: int(barter_snapshot(value).get("playerOfferTotal", 0))
            >= int(barter_snapshot(value).get("traderOfferTotal", 0))
            > 0,
            args.state_timeout,
            "sufficient assembled barter offer",
        )
        assembled = barter_snapshot(assembled_observation)
        assert_barter_contract(assembled)
        step(
            "offer_assembled",
            item={"id": trader_item_id, "protoId": trader_item_proto, "count": 1},
            caps=caps_needed,
            capUnitValue=cap_unit_value,
            playerOfferTotal=assembled.get("playerOfferTotal"),
            traderOfferTotal=assembled.get("traderOfferTotal"),
        )
        assembled_capture = capture_screenshot(
            client,
            endpoint,
            workspace_root,
            output,
            "barter-assembled.tga",
            args.settle_ms,
            args.command_timeout_ms,
            require_barter_panels=True,
        )
        report["screenshots"].append({"stage": "barter_assembled", **assembled_capture})

        run_command(
            client,
            "tla_barter_offer",
            endpoint,
            timeout_ms=args.command_timeout_ms,
            label="submit barter offer",
        )

        def refreshed_successfully(value: dict[str, Any]) -> bool:
            current_barter = barter_snapshot(value)
            if current_barter.get("active") is not True or int(current_barter.get("session", 0)) != session:
                return False
            offers_empty = not current_barter.get("playerOffer") and not current_barter.get("traderOffer")
            received_item = item_count(current_barter.get("playerInventory"), trader_item_proto) >= player_item_count_before + 1
            spent_caps = item_count(current_barter.get("playerInventory"), "bottle_caps") <= caps_before - caps_needed
            trader_spent_item = item_count(current_barter.get("traderInventory"), trader_item_proto) <= trader_item_count_before - 1
            return bool(offers_empty and received_item and spent_caps and trader_spent_item)

        refreshed_observation = wait_for_observation(
            client,
            endpoint,
            refreshed_successfully,
            args.state_timeout,
            "successful server barter refresh",
        )
        refreshed = barter_snapshot(refreshed_observation)
        assert_barter_contract(refreshed)
        if int(refreshed.get("playerOfferTotal", -1)) != 0 or int(refreshed.get("traderOfferTotal", -1)) != 0:
            raise SmokeError("barter refresh left non-zero offer totals")
        step(
            "offer_refreshed",
            session=refreshed.get("session"),
            playerItemCount=item_count(refreshed.get("playerInventory"), trader_item_proto),
            capsRemaining=item_count(refreshed.get("playerInventory"), "bottle_caps"),
        )

        run_command(
            client,
            "tla_barter_return_dialog",
            endpoint,
            timeout_ms=args.command_timeout_ms,
            label="return from barter to dialog",
        )
        resumed_observation = wait_for_observation(
            client,
            endpoint,
            lambda value: barter_snapshot(value).get("active") is not True
            and bool((value.get("dialog") or {}).get("active"))
            and str((value.get("dialog") or {}).get("dialogId", "")) == args.npc_dialog_id,
            args.state_timeout,
            "resumed NPC dialog",
        )
        resumed_dialog = resumed_observation.get("dialog") or {}
        if str(resumed_dialog.get("talkerId")) != str(npc_id):
            raise SmokeError(f"resumed dialog talkerId {resumed_dialog.get('talkerId')} does not match NPC {npc_id}")
        step("dialog_resumed", dialogId=resumed_dialog.get("dialogId"), talkerId=resumed_dialog.get("talkerId"))
        resumed_capture = capture_screenshot(
            client,
            endpoint,
            workspace_root,
            output,
            "dialog-resumed.tga",
            args.settle_ms,
            args.command_timeout_ms,
        )
        report["screenshots"].append({"stage": "dialog_resumed", **resumed_capture})

        run_command(
            client,
            "tla_close_dialog",
            endpoint,
            timeout_ms=args.command_timeout_ms,
            label="close resumed dialog",
        )
        closed = wait_for_observation(
            client,
            endpoint,
            lambda value: not bool((value.get("dialog") or {}).get("active"))
            and barter_snapshot(value).get("active") is not True,
            args.state_timeout,
            "dialog close",
        )
        normal_close_completed = True
        step("closed", screen=closed.get("screen"))
        report["ok"] = True
    except (OSError, SmokeError, ValueError) as exc:
        report["error"] = str(exc)
        report["steps"].append({"name": "failure", "ok": False, "error": str(exc)})
    finally:
        if not normal_close_completed:
            cleanup_active_dialog(client, endpoint, args.command_timeout_ms)
        client.close()
        report["finishedAtUnixMs"] = int(time.time() * 1000)

    return report


def main() -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.environ.get("TLA_AI_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("TLA_AI_PORT", "43011")))
    parser.add_argument("--token", default=os.environ.get("TLA_AI_TOKEN", ""))
    parser.add_argument("--timeout", type=float, default=float(os.environ.get("TLA_AI_TIMEOUT", "3")))
    parser.add_argument("--endpoint-id", default="", help="Optional adapter endpoint id; the current/default client is used otherwise.")
    parser.add_argument("--workspace-root", default=os.environ.get("TLA_WORKSPACE_ROOT", str(WORKSPACE_ROOT)))
    parser.add_argument("--map", default="arroyo", help="Location/map proto passed to QA teleport-map.")
    parser.add_argument(
        "--npc-dialog-id",
        "--npc",
        dest="npc_dialog_id",
        default="arroyo_cassidy",
        help="Expected dialogId of the NPC trader.",
    )
    parser.add_argument("--hex", nargs=2, type=int, metavar=("X", "Y"), help="Optional NPC hex used by QA teleport-map and NPC selection.")
    parser.add_argument("--caps-count", type=int, default=DEFAULT_CAPS_COUNT, help="QA bottle_caps grant used to fund the purchase.")
    parser.add_argument("--output", default="", help="Output directory inside the workspace for report.json and verified TGA files.")
    parser.add_argument("--settle-ms", type=int, default=300)
    parser.add_argument("--command-timeout-ms", type=int, default=20000)
    parser.add_argument("--state-timeout", type=float, default=45.0)
    args = parser.parse_args()

    if args.caps_count <= 0:
        parser.error("--caps-count must be positive")
    if not 0 <= args.settle_ms <= 10000:
        parser.error("--settle-ms must be in the 0..10000 range")
    if not 0 <= args.command_timeout_ms <= 60000:
        parser.error("--command-timeout-ms must be in the 0..60000 range")
    if args.state_timeout <= 0:
        parser.error("--state-timeout must be positive")

    workspace_root = Path(args.workspace_root).resolve()
    try:
        output = resolve_output_directory(workspace_root, args.output)
    except ValueError as exc:
        parser.error(str(exc))
    output.mkdir(parents=True, exist_ok=True)

    report = run(args, workspace_root, output)
    report_path = output / "report.json"
    report["reportPath"] = str(report_path)
    write_json_report(report_path, report)
    print(report_path)
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
