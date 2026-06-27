#!/usr/bin/env python3
"""TLA quest-cycle runner over the AI control bridge.

Drives a full quest cycle end-to-end through the bridge: register a character, teleport to the
quest giver's map, navigate the (now readable) dialog to accept, then teleport to the turn-in NPC's
map and navigate to hand it in, asserting the quest property advances at each stage. Quest specs are
data-driven (see QUESTS); the Cassidy letter cycle (Arroyo → Vault City) is the reference flow.

Prereqs: a running server + client with AiControl.Enabled=True AND AiControl.AllowQaCommands=True
(qa_teleport_* is used to reach content and position next to NPCs), e.g.
  TLA_ServerHeadless.exe --ApplySubConfig LocalTest --AiControl.AllowQaCommands True
  TLA_Client.exe        --ApplySubConfig LocalTest --AiControl.Enabled True --AiControl.AllowQaCommands True

Usage:
  python Tools/AiControlMcp/tla_quest_runner.py --quest cassidy_letter [--report run.json]
  python Tools/AiControlMcp/tla_quest_runner.py --list
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import time

# Per-quest specs. A "stage" navigates one NPC's dialog until the quest property reaches target_value.
#   map        : location/map proto for qa_teleport_map
#   npc        : dialogId of the NPC
#   npc_hex    : optional [x, y] to teleport near (when the NPC is far from the map entry)
#   prefer     : answer-substring priorities (the agent picks the first answer matching one of these)
#   target     : quest-property value reached after this stage
QUESTS = {
    "cassidy_letter": {
        "quest": "ArroyoCassidyLetter",
        "title": "Cassidy's letter to Cyndi (Arroyo -> Vault City)",
        "stages": [
            {
                "name": "accept", "map": "arroyo", "npc": "arroyo_cassidy", "target": 1,
                "prefer": ["работ", "на мели", "одно дело", "да, конечно", "почему бы",
                           "может и не сразу", "заглянуть", "конечно", "могу"],
            },
            {
                "name": "deliver", "map": "vault_city", "npc": "vc_cindy", "npc_hex": [65, 55], "target": 2,
                "prefer": ["письмо", "кассиди", "кесседи", "касиди", "от ", "передать", "вот оно",
                           "держи", "привет", "да", "здравств", "меня зовут", "кто вы"],
            },
        ],
    },
    "arroyo_mynoc_oil": {
        # Full cycle on a single giver (no travel): accept the "bring me grease for the armour" task,
        # then hand in the oil_can. The accept answer needs Intellect > 3; the turn-in needs oil_can in
        # inventory — both supplied via stage `setup` so the runner is self-contained.
        "quest": "ArroyoMynocOil",
        "title": "Mynoc's armour grease (Arroyo, accept + turn-in)",
        "stages": [
            {
                "name": "accept", "map": "arroyo", "npc": "arroyo_mynoc", "npc_hex": [92, 83], "target": 1,
                "setup": [{"prop": "IntellectBase", "value": 6}],
                "prefer": ["принесу тебе смазку", "смазку", "поржавела", "броня", "заметил", "спросить", "да"],
            },
            {
                "name": "turnin", "map": "arroyo", "npc": "arroyo_mynoc", "npc_hex": [92, 83], "target": 2,
                "setup": [{"item": "oil_can", "count": 1}],
                "prefer": ["есть маслёнка", "маслёнка", "масло", "смазк", "вот", "держи", "брон", "да"],
            },
        ],
    },
    "den_smitty_robot": {
        # Multi-stage, single town (Den): accept at Smitty, then fix his Mr. Handy robot at the workbench
        # (examine needs SkillRepair > 59; the repair needs pump_parts + oil_can + super_tool_kit), then
        # report back to Smitty. Demonstrates a quest gated by both a skill and inventory items, all set via
        # stage `setup`. Verified end-to-end: DenSmittyFixit 1 -> 2 -> 3 -> 4.
        "quest": "DenSmittyFixit",
        "title": "Smitty's broken Mr. Handy robot (Den, accept -> repair -> report)",
        "stages": [
            {
                "name": "accept", "map": "den", "npc": "den_smitty", "npc_hex": [307, 148], "target": 1,
                "setup": [{"prop": "IntellectBase", "value": 6}],
                "prefer": ["у тебя работ", "работы нет", "можешь что-нибудь у меня починить",
                           "починить или улучшить", "классный у тебя робот", "не работает",
                           "могу посмотреть", "руки у меня", "да мого", "считай", "починен"],
            },
            {
                "name": "examine", "map": "den", "npc": "den_mr_handy", "npc_hex": [311, 142], "target": 2,
                "setup": [{"prop": "SkillRepair", "value": 85}],
                "prefer": ["умный", "посмотрите что с ним", "будем искать", "опаньки", "починить"],
            },
            {
                "name": "repair", "map": "den", "npc": "den_mr_handy", "npc_hex": [311, 142], "target": 3,
                "setup": [{"item": "pump_parts"}, {"item": "oil_can"}, {"item": "super_tool_kit"}],
                "prefer": ["умный", "попробуем починить", "починить", "живой", "скажу смитти"],
            },
            {
                "name": "report", "map": "den", "npc": "den_smitty", "npc_hex": [307, 148], "target": 4,
                "prefer": ["я починил твою рухлядь", "починил", "рухлядь", "молодец", "книж", "готово", "да"],
            },
        ],
    },
    "klam_vaccination": {
        # Single-NPC quest in a third town (Klamath): Hish hands out syringes to vaccinate his three
        # brahmins, then pays on report. The accept (=1) is pure dialog navigation; completion (=2) is gated
        # by the three per-brahmin sub-task flags KlamVaccinationB1/B2/B3 (set in-world by using the `vaccine`
        # item on each brahmin) — supplied here via stage `setup` so the runner is self-contained.
        "quest": "KlamVaccination",
        "title": "Hish's brahmin vaccination (Klamath, accept -> vaccinate sub-task -> report)",
        "stages": [
            {
                "name": "accept", "map": "klamath", "npc": "klam_hish", "npc_hex": [82, 132], "target": 1,
                "setup": [{"prop": "IntellectBase", "value": 6}],
                "prefer": ["конечно берусь", "не волнуйся", "не промахнусь", "так что насчет работы",
                           "так что насчёт работы", "насчет работы", "насчёт работы", "ищу где можно заработать",
                           "ищу, где можно заработать", "заработать", "хим", "ещё вопросы", "еще вопросы"],
            },
            {
                "name": "report", "map": "klamath", "npc": "klam_hish", "npc_hex": [82, 132], "target": 2,
                "setup": [{"prop": "KlamVaccinationB1", "value": 1}, {"prop": "KlamVaccinationB2", "value": 1},
                          {"prop": "KlamVaccinationB3", "value": 1}],
                "prefer": ["разумеется", "кадровый ветеринар", "практически", "получил задание", "укольчики",
                           "всё нормально", "ветеринар"],
            },
        ],
    },
}

# NOTE: cassidy_letter (accept→deliver, cross-town), arroyo_mynoc_oil (accept→turn-in, one giver),
# den_smitty_robot (accept→repair→report, skill+item gated) and klam_vaccination (accept→sub-task→report,
# Server-scope flag) are verified reference flows across three towns.
# Adding a quest is adding a spec, but each quest's dialog tree differs and the navigator is heuristic, so a
# new spec usually needs a short live trace to confirm. Known wrinkles encoded as `setup`/`prefer` knobs:
#  - prerequisite demands: a quest answer can require a critter property (Intellect, CurrentHp via Doc's
#    IsToHeal), an inventory item (oil_can), or a GAME flag — set them with stage `setup`
#    ({"prop"/"game_prop"/"item": ...}); note qa_set_prop sets CRITTER props and qa_set_game_prop sets GAME
#    props (e.g. DenVirginIsAway), which are different scopes.
#  - Server-scope quest flags: ~1/3 of quest properties are `Server` (not `OwnerSync`), so they never appear in
#    the client observation's `quests`. read_quest() falls back to qa_get_prop (an authoritative server read)
#    for those — e.g. KlamVaccination. The fast client path still serves the OwnerSync majority.
#  - guard NPCs (Arroyo Todd) never open a dialog at all — not a loyalty gate (default loyalty 5 passes).
#  - localization: run the client with --Client.Language russ so dialog text matches the Russian `prefer`.
#  - a few answers are gated by baker quirks (Den Mom's "Virginia" answer stays hidden even with the GAME
#    flag set) — those need content-side attention, not just a spec.

# Exit-like / dead-end answers the navigator must not pick while a fresh non-exit answer remains.
AVOID = ["[выход]", "выход]", "[уходите]", "уходите]", "осматрива", "передума", "[лжет", "[лжёт",
         "до свид", "свидан", "ничего, спасибо", "ничего пожалуй", "не буду", "не сейчас",
         "не хочу", "мне пора", "я пош", "уйду", "уйти", "забудь", "отстань", "пойду", "нахрен",
         "налить", "выпь", "поторг", "торгу", "в другой раз", "барт"]


def apply_setup(b, setup):
    """Apply quest prerequisites before a stage: critter props, game props, or granted items."""
    for s in setup or []:
        if "prop" in s:
            b.act("qa_set_prop", stringArg=s["prop"], intArg=int(s["value"]))
        elif "game_prop" in s:
            b.act("qa_set_game_prop", stringArg=s["game_prop"], intArg=int(s["value"]))
        elif "item" in s:
            b.act("qa_give_item", stringArg=s["item"], intArg=int(s.get("count", 1)))
        time.sleep(0.9)


class BridgeError(Exception):
    pass


class Bridge:
    def __init__(self, host, port, token="", timeout=10.0):
        self.host, self.port, self.timeout = host, port, timeout
        self._buf = b""
        self._sock = socket.create_connection((host, port), timeout=timeout)
        self._sock.settimeout(timeout)
        if token:
            self.call("auth", {"token": token})

    def call(self, method, params=None):
        self._sock.sendall((json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}) + "\n").encode("utf-8"))
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

    def observe(self):
        return self.call("observe")["observation"]

    def observe_safe(self):
        try:
            return self.observe()
        except (BridgeError, OSError):
            return None

    def act(self, t, **p):
        p["type"] = t
        return self.call("act", p)

    def events(self, after_seq=0, limit=500):
        return self.call("events", {"afterSeq": after_seq, "limit": limit}).get("events", [])

    def close(self):
        try:
            self._sock.close()
        except OSError:
            pass


def quest_value(obs, name):
    for q in (obs.get("quests") or []):
        if name in str(q.get("name", "")):
            return q.get("value")
    return None


def quest_value_server(b, name, timeout=6.0):
    """Authoritative server-side read of a critter property via the qa_get_prop round-trip. Needed for
    Server-scope quest flags (not OwnerSync) that never appear in the client observation. Returns int|None."""
    cursor = 0
    for e in b.events(0, 500):
        cursor = max(cursor, e.get("seq", 0))
    b.act("qa_get_prop", stringArg=name)
    deadline = time.time() + timeout
    while time.time() < deadline:
        for e in b.events(cursor, 500):
            cursor = max(cursor, e.get("seq", 0))
            ev = e.get("event", {})  # bridge wraps payloads as {"event": {...}, "seq": N}
            if ev.get("type") == "qa_prop_value" and name in str(ev.get("prop", "")):
                return ev.get("value")
        time.sleep(0.4)
    return None


def read_quest(b, name):
    """Quest value preferring the client observation (fast, OwnerSync quests), falling back to an
    authoritative server read when the property is absent client-side (Server-scope quest flags)."""
    v = quest_value(b.observe_safe() or {}, name)
    if v is not None:
        return v
    return quest_value_server(b, name)


def close_dialog(b):
    """Close any active dialog/modal so map transfers aren't blocked by an in-progress conversation."""
    o = b.observe_safe() or {}
    if o.get("dialog", {}).get("active") or o.get("screen", {}).get("modalActive"):
        b.act("dialog_answer", intArg=0xF2)  # advancing/closing answer
        time.sleep(1)
        b.act("close_screen")
        b.act("clear_actions")
        time.sleep(1)


def teleport_map(b, pid, timeout=30):
    close_dialog(b)
    cur = (b.observe().get("map") or {}).get("protoId")
    b.act("qa_teleport_map", stringArg=pid)
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(2)
        o = b.observe_safe()
        if o and o.get("hasMap") and (o.get("map") or {}).get("protoId") != cur:
            return o
    return b.observe()


def find_npc(b, dialog_id, hint_hex=None):
    """Find a visible NPC by dialogId; if hint_hex given and not visible, nudge there + re-observe to sync."""
    o = b.observe()
    hit = [c for c in (o.get("critters") or []) if c.get("dialogId") == dialog_id]
    if hit:
        return hit[0]
    if hint_hex:
        hx, hy = hint_hex
        for (tx, ty) in [(hx + 1, hy), (hx - 1, hy), (hx, hy + 2), (hx, hy - 2), (hx + 3, hy)]:
            b.act("qa_teleport_hex", x=tx, y=ty)
            for _ in range(3):
                time.sleep(2)
                o = b.observe_safe() or {}
                hit = [c for c in (o.get("critters") or []) if c.get("dialogId") == dialog_id]
                if hit:
                    return hit[0]
    return None


def _is_avoid(a):
    al = a.lower()
    return any(w in al for w in AVOID)


def navigate_dialog(b, npc, prefer, target, quest, max_steps=18, max_opens=4):
    """Talk to npc and walk the dialog until quest reaches target.

    Robust against the three things that break naive keyword navigation on complex NPCs:
    - first-meeting intros / "continue" speeches with a single answer are auto-advanced;
    - exit-like answers ("[Уходите]", "осматриваюсь", "передумал" ...) are never chosen while a
      fresh non-exit answer exists, so the walk doesn't bail out of the tree early;
    - (speech, answer) pairs are remembered across dialog re-opens, so each re-open explores a new
      branch instead of repeating the same wrong turn.
    """
    def open_dialog():
        b.act("qa_teleport_hex", x=npc["hexX"] + 1, y=npc["hexY"])
        time.sleep(1.2)
        b.act("talk_to", targetId=npc["id"])
        t = time.time() + 14
        while time.time() < t:
            time.sleep(1.4)
            if (b.observe_safe() or {}).get("dialog", {}).get("active"):
                return True
        return False

    steps = []
    seen = set()  # (speech-text prefix, answer-text) pairs already chosen — persists across re-opens
    for _ in range(max_opens):
        if quest_value(b.observe_safe() or {}, quest) == target:
            return steps, True
        open_dialog()
        for _ in range(max_steps):
            o = b.observe_safe() or {}
            if quest_value(o, quest) == target:
                return steps, True
            d = o.get("dialog", {})
            if not d.get("active"):
                break
            ans = d.get("answers") or []
            key = d.get("text", "")[:40]
            steps.append({"text": d.get("text"), "answers": ans})
            # 1) keyword-preferred, unseen
            pick = next((i for i, a in enumerate(ans)
                         if any(w in a.lower() for w in prefer) and (key, a) not in seen), None)
            # 2) auto-advance a single-answer intro/continue speech
            if pick is None and len(ans) == 1:
                pick = 0
            # 3) any unseen, non-exit answer (systematic exploration)
            if pick is None:
                pick = next((i for i, a in enumerate(ans) if (key, a) not in seen and not _is_avoid(a)), None)
            # 4) keyword-preferred even if already seen
            if pick is None:
                pick = next((i for i, a in enumerate(ans) if any(w in a.lower() for w in prefer)), None)
            if pick is None:
                break  # nothing useful left here; close + re-open to try a fresh branch
            seen.add((key, ans[pick]))
            b.act("dialog_answer", intArg=pick)
            time.sleep(2.4)
        close_dialog(b)
        time.sleep(0.8)
        # Authoritative check once per open-cycle (cheap vs per-step): a terminal quest answer closes the
        # dialog, and Server-scope flags are invisible to the per-step client check inside the loop.
        if read_quest(b, quest) == target:
            return steps, True
    return steps, read_quest(b, quest) == target


def run(args):
    spec = QUESTS[args.quest]
    report = {"quest": args.quest, "title": spec["title"], "ok": False, "stages": []}
    b = Bridge(args.host, args.port, args.token, args.timeout)
    try:
        # Enter game.
        if not b.observe().get("hasChosen"):
            b.act("register" if args.register else "login", stringArg=args.name)
            deadline = time.time() + args.login_timeout
            while time.time() < deadline and not (b.observe_safe() or {}).get("hasChosen"):
                time.sleep(1.5)
        if not b.observe().get("hasChosen"):
            report["error"] = "could not enter game"
            return report

        apply_setup(b, spec.get("setup"))  # quest-wide prerequisites (run once after entering game)

        for stage in spec["stages"]:
            o = teleport_map(b, stage["map"])
            apply_setup(b, stage.get("setup"))  # per-stage prerequisites (after teleport, before talking)
            npc = find_npc(b, stage["npc"], stage.get("npc_hex"))
            sr = {"stage": stage["name"], "map": (o.get("map") or {}).get("protoId"),
                  "npc": stage["npc"], "npc_found": bool(npc)}
            if not npc:
                sr["ok"] = False
                report["stages"].append(sr)
                report["error"] = f"NPC {stage['npc']} not found on {stage['map']}"
                return report
            steps, reached = navigate_dialog(b, npc, stage["prefer"], stage["target"], spec["quest"])
            sr["ok"] = reached
            sr["quest_value"] = read_quest(b, spec["quest"])
            sr["dialog_steps"] = len(steps)
            report["stages"].append(sr)
            if not reached:
                report["error"] = f"stage {stage['name']} did not reach {spec['quest']}={stage['target']}"
                return report

        report["final_quest_value"] = read_quest(b, spec["quest"])
        report["ok"] = all(s["ok"] for s in report["stages"])
        return report
    except (BridgeError, OSError) as exc:
        report["error"] = str(exc)
        return report
    finally:
        b.close()


def main():
    ap = argparse.ArgumentParser(description="TLA quest-cycle runner over the AI control bridge")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=43011)
    ap.add_argument("--token", default="")
    ap.add_argument("--timeout", type=float, default=10.0)
    ap.add_argument("--quest", default="cassidy_letter", choices=sorted(QUESTS.keys()))
    ap.add_argument("--name", default="QuestRunner")
    ap.add_argument("--register", action="store_true", default=True)
    ap.add_argument("--login-timeout", type=float, default=45.0)
    ap.add_argument("--report", default="")
    ap.add_argument("--list", action="store_true", help="list known quest specs and exit")
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass

    if args.list:
        for k, v in QUESTS.items():
            print(f"{k}: {v['title']}")
        return 0

    report = run(args)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        with open(args.report, "w", encoding="utf-8") as fh:
            fh.write(text)
    print(text)
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
