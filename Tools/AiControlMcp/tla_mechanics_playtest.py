#!/usr/bin/env python3
"""TLA mechanics playtest runner over the AI control bridge.

Self-contained, dependency-free. Connects directly to the client bridge TCP line protocol
(see Docs/AiControl.md), registers/logs in a character, and runs a small reachability-aware
mechanics sequence (observe -> probe reachable targets via environment_query -> move -> talk),
then writes a JSON report.

Prereqs: a running server and a client with AiControl.Enabled=True, e.g.
  TLA_ServerHeadless.exe --ApplySubConfig LocalTest
  TLA_Client.exe        --ApplySubConfig LocalTest --AiControl.Enabled True

Usage:
  python Tools/AiControlMcp/tla_mechanics_playtest.py --name TestBot1 [--register] [--report path.json]
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import time


class BridgeError(Exception):
    pass


class Bridge:
    """Newline-delimited JSON-RPC client for the Ai control native bridge."""

    def __init__(self, host: str, port: int, token: str = "", timeout: float = 8.0) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self._buf = b""
        self._sock = socket.create_connection((host, port), timeout=timeout)
        self._sock.settimeout(timeout)
        if token:
            self.call("auth", {"token": token})
        self._qid = 5000

    def call(self, method: str, params: dict | None = None) -> dict:
        req = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
        self._sock.sendall((json.dumps(req) + "\n").encode("utf-8"))
        while b"\n" not in self._buf:
            chunk = self._sock.recv(65536)
            if not chunk:
                raise BridgeError("connection closed")
            self._buf += chunk
        line, self._buf = self._buf.split(b"\n", 1)
        msg = json.loads(line.decode("utf-8"))
        if "error" in msg:
            raise BridgeError(str(msg["error"]))
        return msg.get("result", {})

    def reconnect(self) -> bool:
        try:
            self._sock.close()
        except OSError:
            pass
        try:
            self._buf = b""
            self._sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
            self._sock.settimeout(self.timeout)
            return True
        except OSError:
            return False

    def observe(self) -> dict:
        return self.call("observe")["observation"]

    def observe_safe(self) -> dict | None:
        try:
            return self.observe()
        except (BridgeError, OSError):
            self.reconnect()
            return None

    def act(self, cmd_type: str, **params) -> dict:
        params["type"] = cmd_type
        return self.call("act", params)

    def latest_seq(self) -> int:
        return self.call("events", {"afterSeq": 0, "limit": 1})["latestSeq"]

    def env_path(self, to_x: int, to_y: int) -> dict | None:
        """Run a path reachability query from the chosen to (to_x, to_y); returns the result dict."""
        self._qid += 1
        qid = self._qid
        after = self.latest_seq()
        self.act("environment_query", intArg=qid, screenX=-1, screenY=-1, x=to_x, y=to_y, stringArg="path")
        deadline = time.time() + 8
        while time.time() < deadline:
            ev = self.call("events", {"afterSeq": after, "limit": 200})
            for entry in ev["events"]:
                d = entry["event"]
                if d.get("type") == "environment_query_result" and d.get("queryId") == qid:
                    return d.get("result")
            after = ev["latestSeq"]
            time.sleep(0.3)
        return None

    def close(self) -> None:
        try:
            self._sock.close()
        except OSError:
            pass


def wait_chosen(bridge: Bridge, timeout: float) -> dict | None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        obs = bridge.observe_safe()
        if obs and obs.get("hasChosen") and obs.get("hasMap"):
            return obs
        time.sleep(1.5)
    return None


def manhattan(a: dict, x: int, y: int) -> int:
    return abs(a["hexX"] - x) + abs(a["hexY"] - y)


def run(args: argparse.Namespace) -> dict:
    report: dict = {
        "ok": False,
        "name": args.name,
        "steps": [],
        "findings": [],
        "metrics": {},
    }

    def step(name: str, ok: bool, **extra) -> None:
        report["steps"].append({"step": name, "ok": ok, **extra})

    try:
        bridge = Bridge(args.host, args.port, args.token, args.timeout)
    except OSError as exc:
        report["error"] = f"cannot connect to bridge {args.host}:{args.port}: {exc}"
        return report

    try:
        obs = bridge.observe()
        if not obs.get("hasChosen"):
            cmd = "register" if args.register else "login"
            bridge.act(cmd, stringArg=args.name)
            step(f"{cmd}:{args.name}", True)
            obs = wait_chosen(bridge, args.login_timeout)
            if obs is None:
                step("enter_game", False, detail="no chosen/map after login")
                report["findings"].append("login/register did not reach in-game state")
                return report
        step("enter_game", True)

        # Optional QA teleport to a content map/location (requires AiControl.AllowQaCommands=True).
        if args.teleport_map:
            bridge.act("qa_teleport_map", stringArg=args.teleport_map)
            deadline = time.time() + 30
            on_content = False
            while time.time() < deadline:
                time.sleep(2)
                cur = bridge.observe_safe()
                if cur and cur.get("hasMap") and cur.get("map", {}).get("protoId") != obs.get("map", {}).get("protoId"):
                    obs = cur
                    on_content = True
                    break
            step(f"teleport_map:{args.teleport_map}", on_content,
                 map=obs.get("map", {}).get("protoId") if on_content else None)
            if not on_content:
                report["findings"].append(f"qa_teleport_map {args.teleport_map} did not change map (AllowQaCommands?)")

        ch = obs["chosen"]
        report["metrics"]["chosen"] = {
            "hex": [ch["hexX"], ch["hexY"]], "hp": [ch.get("currentHp"), ch.get("maxHp")],
            "level": ch.get("level"),
        }
        report["metrics"]["map"] = obs.get("map")
        report["metrics"]["visible"] = {
            "critters": len(obs.get("critters") or []),
            "mapItems": len(obs.get("mapItems") or []),
            "inventory": len(obs.get("inventory") or []),
            "quests": len(obs.get("quests") or []),
        }
        step("observe", True, **report["metrics"]["visible"])

        # Reachability probe over visible critters + map items.
        targets = []
        for c in (obs.get("critters") or []):
            targets.append(("critter", c["id"], c["hexX"], c["hexY"], c.get("dialogId") or ""))
        for it in (obs.get("mapItems") or []):
            targets.append(("item", it["id"], it["hexX"], it["hexY"], it.get("protoId") or ""))

        reachable = []
        for kind, oid, x, y, tag in targets[: args.max_probe]:
            res = bridge.env_path(x, y)
            if res and res.get("reachable"):
                reachable.append({"kind": kind, "id": oid, "hex": [x, y], "tag": tag,
                                  "pathLength": res.get("pathLength")})
        report["metrics"]["reachableTargets"] = len(reachable)
        report["metrics"]["probedTargets"] = min(len(targets), args.max_probe)
        step("reachability_probe", True, reachable=len(reachable), probed=min(len(targets), args.max_probe))
        if not reachable:
            report["findings"].append("no reachable visible targets from spawn (env_path)")

        # Navigate to the nearest reachable target and interact.
        ch = bridge.observe()["chosen"]
        reachable.sort(key=lambda t: abs(t["hex"][0] - ch["hexX"]) + abs(t["hex"][1] - ch["hexY"]))
        talked = False
        moved = False
        for tgt in reachable[: args.max_interact]:
            tx, ty = tgt["hex"]
            start = (ch["hexX"], ch["hexY"])
            if tgt["kind"] == "critter" and tgt["tag"]:
                bridge.act("talk_to", targetId=tgt["id"])
            else:
                bridge.act("move_to_hex", x=tx, y=ty)
            deadline = time.time() + args.move_timeout
            reissue = time.time()
            while time.time() < deadline:
                time.sleep(2)
                o = bridge.observe_safe()
                if o is None:
                    continue
                ch = o.get("chosen") or ch
                cur = (ch["hexX"], ch["hexY"])
                if cur != start:
                    moved = True
                if o.get("dialog", {}).get("active"):
                    talked = True
                    d = o["dialog"]
                    step("talk_to", True, dialogId=d.get("dialogId"), answers=len(d.get("answers") or []),
                         textEmpty=(d.get("text", "") == ""))
                    if (d.get("text", "") == ""):
                        report["findings"].append(f"dialog {d.get('dialogId')} opened with empty text (content/localization)")
                    # advance/close the dialog
                    bridge.act("dialog_answer", intArg=0)
                    break
                if abs(cur[0] - tx) + abs(cur[1] - ty) <= 1:
                    break
                if time.time() - reissue > 16:
                    if tgt["kind"] == "critter" and tgt["tag"]:
                        bridge.act("talk_to", targetId=tgt["id"])
                    else:
                        bridge.act("move_to_hex", x=tx, y=ty)
                    reissue = time.time()
            if talked:
                break
        step("navigation", moved or talked, moved=moved, talked=talked)
        report["metrics"]["moved"] = moved
        report["metrics"]["talked"] = talked

        report["ok"] = all(s["ok"] for s in report["steps"])
        return report
    except (BridgeError, OSError) as exc:
        report["error"] = str(exc)
        return report
    finally:
        bridge.close()


def main() -> int:
    ap = argparse.ArgumentParser(description="TLA mechanics playtest over the AI control bridge")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=43011)
    ap.add_argument("--token", default="")
    ap.add_argument("--timeout", type=float, default=8.0)
    ap.add_argument("--name", default="TestBot1", help="character name to register/login")
    ap.add_argument("--register", action="store_true", help="register a fresh character instead of login")
    ap.add_argument("--teleport-map", default="", help="QA teleport to this map/location proto after login (needs AllowQaCommands)")
    ap.add_argument("--login-timeout", type=float, default=45.0)
    ap.add_argument("--move-timeout", type=float, default=100.0)
    ap.add_argument("--max-probe", type=int, default=12, help="max visible targets to reachability-probe")
    ap.add_argument("--max-interact", type=int, default=4, help="max reachable targets to attempt interacting")
    ap.add_argument("--report", default="", help="write JSON report to this path")
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass

    report = run(args)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        with open(args.report, "w", encoding="utf-8") as fh:
            fh.write(text)
    print(text)
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
