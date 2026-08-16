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
  python Tools/AiControlMcp/tla_quest_runner.py --trace-dialog --map arroyo \
    --npc CassidyStage4 --dialog arroyo_cassidy --flag ArroyoCassidyLetter \
    [--report trace.json]
  python Tools/AiControlMcp/tla_quest_runner.py --list
"""

from __future__ import annotations

import argparse
from collections import deque
import json
import re
import socket
import sys
import time
from pathlib import Path

# Per-quest specs. A "stage" navigates one NPC's dialog until the quest property reaches target_value.
#   map        : location/map proto for qa_teleport_map
#   npc        : dialogId of the NPC
#   npc_hex    : optional [x, y] to teleport near (when the NPC is far from the map entry)
#   prefer     : answer-substring priorities (the agent picks the first answer matching one of these)
#   target     : quest-property value reached after this stage
#   target_mode: "at_least" (default for monotonic quest stages) or "exact"
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
                "name": "deliver", "map": "vault_city/vcity_courtyard", "npc": "vc_cindy",
                "npc_hex": [65, 55], "target": 2,
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
#  - authored @@ text variants change visible wording while retaining the same stable answer slot.
#  - localization: run the client with --Client.Language russ so dialog text matches the Russian `prefer`.
#  - a few answers are gated by baker quirks (Den Mom's "Virginia" answer stays hidden even with the GAME
#    flag set) — those need content-side attention, not just a spec.

# Exit-like / dead-end answers the navigator must not pick while a fresh non-exit answer remains.
AVOID = ["[выход]", "выход]", "[уходите]", "уходите]", "осматрива", "передума", "[лжет", "[лжёт",
         "до свид", "свидан", "ничего, спасибо", "ничего пожалуй", "не буду", "не сейчас",
         "не хочу", "мне пора", "я пош", "уйду", "уйти", "забудь", "отстань", "пойду", "нахрен",
         "налить", "выпь", "поторг", "торгу", "в другой раз", "барт"]

ANSWER_KEYWORD_STOP_WORDS = {
    "буду", "быть", "вас", "вам", "ваш", "вот", "все", "всё", "для", "его", "если", "есть",
    "ещё", "или", "как", "когда", "мне", "может", "мой", "надо", "нет", "ничего", "она", "они",
    "оно", "пока", "потом", "почему", "просто", "себя", "тебе", "тебя", "тогда", "только", "тут",
    "уже", "хочу", "чего", "чтобы", "это", "этот", "этого", "этой", "этим", "этом", "я",
}

TRACE_DISCOVERY_HINTS = (
    "работ", "задани", "помо", "дело", "просьб", "письм", "отнес", "принес",
    "передам", "конечно", "соглас", "берусь", "брон", "ржав", "смаз", "робот",
    "почин", "техник", "посмотр", "новост", "произош", "вирджин", "проблем",
)
TRACE_EXPLORATION_HINTS = ("искать", "разыск", "пойти")
TRACE_LOW_PRIORITY_HINTS = (
    "налей", "выпить", "выпью", "купить", "в налич", "товар", "торгов", "спасибо",
    "мне пора", "лучше пойду", "не буду", "не могу", "нет, мне", "передумал", "другие планы",
)


def normalize_property_name(name):
    """Accept plan-style Critter.Flag/CritterProperty::Flag spellings and return the QA property name."""
    value = str(name).strip()
    if "::" in value:
        value = value.rsplit("::", 1)[-1]
    if "." in value:
        value = value.rsplit(".", 1)[-1]
    if not value:
        raise ValueError("quest flag must not be empty")
    return value


def answer_keyword_set(answer):
    """Build stable substring candidates from a visible localized answer."""
    normalized = " ".join(str(answer).strip().lower().split())
    normalized = normalized.strip("[](){}<>.,!?;:\"'—–- ")
    words = re.findall(r"[0-9a-zа-яё]+", normalized, flags=re.IGNORECASE)
    distinctive = [
        (index, word)
        for index, word in enumerate(words)
        if len(word) >= 4 and word not in ANSWER_KEYWORD_STOP_WORDS
    ]
    distinctive.sort(key=lambda entry: (-len(entry[1]), entry[0]))

    keywords = []
    if normalized:
        keywords.append(normalized)
    for _, word in distinctive[:3]:
        if word not in keywords:
            keywords.append(word)
    return keywords


def rank_trace_candidates(candidates):
    ranked = sorted(
        candidates,
        key=lambda candidate: (
            -candidate["stage_advance"],
            -candidate["to_value"],
            len(candidate["node_path"]),
            candidate["answer"].casefold(),
        ),
    )
    for rank, candidate in enumerate(ranked, start=1):
        candidate["rank"] = rank
    return ranked


def trace_answer_selectors(answers):
    """Order visible answers for discovery while retaining index/text replay selectors."""
    selectors = []
    for index, answer in enumerate(answers):
        text = str(answer)
        lowered = text.lower()
        if any(hint in lowered for hint in TRACE_DISCOVERY_HINTS):
            priority = 0
        elif any(hint in lowered for hint in TRACE_EXPLORATION_HINTS):
            priority = 1
        elif any(hint in lowered for hint in TRACE_LOW_PRIORITY_HINTS):
            priority = 3
        else:
            priority = 2
        selectors.append((priority, index, {"index": index, "text": text, "answer_count": len(answers)}))
    selectors.sort(key=lambda entry: (entry[0], entry[1]))
    return [entry[2] for entry in selectors]


def apply_setup(b, setup):
    """Apply quest prerequisites before a stage: critter props, game props, or granted items."""
    for s in setup or []:
        if "prop" in s:
            # Confirm the write instead of treating command queuing as a server acknowledgement. A callback
            # can still end without a result when its entity is destroyed while Game.Sync waits/acquires.
            set_quest_value(b, s["prop"], int(s["value"]), timeout=30.0)
        elif "game_prop" in s:
            b.act("qa_set_game_prop", stringArg=s["game_prop"], intArg=int(s["value"]))
        elif "item" in s:
            b.act("qa_give_item", stringArg=s["item"], intArg=int(s.get("count", 1)))
        time.sleep(0.9)


class BridgeError(Exception):
    pass


class DialogOpenError(BridgeError):
    pass


class TraceRootChanged(BridgeError):
    def __init__(self, observation):
        super().__init__("dialog replay root changed")
        self.observation = observation


class Bridge:
    def __init__(self, host, port, token="", timeout=10.0):
        self.host, self.port, self.timeout = host, port, timeout
        self._buf = b""
        self._qa_request_id = int(time.monotonic_ns() % 2147483646) + 1
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

    def next_qa_request_id(self):
        request_id = self._qa_request_id
        self._qa_request_id = 1 if request_id >= 2147483647 else request_id + 1
        return request_id

    def close(self):
        try:
            self._sock.close()
        except OSError:
            pass


def quest_value(obs, name):
    target = normalize_property_name(name)
    for q in (obs.get("quests") or []):
        if normalize_property_name(q.get("name", "")) == target:
            return q.get("value")
    return None


def quest_target_reached(value, target, mode="at_least"):
    """Check a stage target without making completed monotonic quests impossible to rerun."""
    if value is None:
        return False
    if mode == "at_least":
        return value >= target
    if mode == "exact":
        return value == target
    raise ValueError(f"unknown quest target mode: {mode}")


def quest_value_server(b, name, timeout=6.0):
    """Authoritative server-side read of a critter property via the qa_get_prop round-trip. Needed for
    Server-scope quest flags (not OwnerSync) that never appear in the client observation. Returns int|None."""
    cursor = 0
    for e in b.events(0, 500):
        cursor = max(cursor, e.get("seq", 0))
    request_id = b.next_qa_request_id()
    b.act("qa_get_prop", stringArg=name, intArg=request_id)
    deadline = time.time() + timeout
    while time.time() < deadline:
        for e in b.events(cursor, 500):
            cursor = max(cursor, e.get("seq", 0))
            ev = e.get("event", {})  # bridge wraps payloads as {"event": {...}, "seq": N}
            if (
                ev.get("type") == "qa_prop_value"
                and ev.get("requestId") == request_id
                and normalize_property_name(ev.get("prop", ""))
                == normalize_property_name(name)
            ):
                return ev.get("value")
        remaining = deadline - time.time()
        if remaining > 0:
            time.sleep(min(0.4, remaining))
    return None


def read_quest(b, name, server_timeout=30.0):
    """Quest value preferring the client observation (fast, OwnerSync quests), falling back to an
    authoritative server read when the property is absent client-side (Server-scope quest flags)."""
    v = quest_value(b.observe_safe() or {}, name)
    if v is not None:
        return v
    return read_quest_authoritative(b, name, timeout=server_timeout)


def read_quest_authoritative(b, name, timeout=30.0, attempts=10):
    """Read server-first, retrying when an async request ends without a correlated response."""
    deadline = time.monotonic() + max(0.0, timeout)
    attempts = max(1, int(attempts))
    for attempt in range(attempts):
        remaining = max(0.0, deadline - time.monotonic())
        attempt_timeout = remaining / (attempts - attempt)
        value = quest_value_server(b, name, timeout=attempt_timeout)
        if value is not None:
            return value
    return quest_value(b.observe_safe() or {}, name)


def close_dialog(b, timeout=3.0):
    """Close any active dialog/modal so map transfers aren't blocked by an in-progress conversation."""
    o = b.observe_safe() or {}
    if o.get("dialog", {}).get("active"):
        b.act("close_dialog")
    elif o.get("screen", {}).get("modalActive"):
        b.act("close_screen")
    else:
        return
    wait_for_observation(
        b,
        lambda observation: not bool((observation.get("dialog") or {}).get("active"))
        and not bool((observation.get("screen") or {}).get("modalActive")),
        timeout,
    )
    b.act("clear_actions")


def expected_map_proto(pid):
    """Return the map proto expected in an observation for a QA location/map target."""
    return pid.split("/", 1)[-1]


def observed_map_proto(observation):
    if not observation or not observation.get("hasMap"):
        return None
    map_info = observation.get("map") or {}
    return map_info.get("protoId")


def teleport_map(b, pid, timeout=60, poll_interval=2.0):
    close_dialog(b)
    expected_proto = expected_map_proto(pid)
    initial = b.observe()
    if observed_map_proto(initial) == expected_proto:
        return initial

    b.act("qa_teleport_map", stringArg=pid)
    deadline = time.monotonic() + timeout
    last_observation = initial
    observed_after_command = False
    while time.monotonic() < deadline:
        time.sleep(min(poll_interval, max(0.0, deadline - time.monotonic())))
        observation = b.observe_safe()
        if observation is not None:
            last_observation = observation
            observed_after_command = True
        if observed_map_proto(observation) == expected_proto:
            return observation

    final_observation = b.observe_safe()
    if final_observation is not None:
        last_observation = final_observation
        observed_after_command = True
        if observed_map_proto(final_observation) == expected_proto:
            return final_observation

    actual_proto = observed_map_proto(last_observation)
    if not observed_after_command or actual_proto is None:
        raise BridgeError(
            f"qa teleport to {pid} timed out: client/map observation unavailable after command "
            f"(last observed map {actual_proto or '<none>'})"
        )
    raise BridgeError(
        f"qa teleport to {pid} timed out: expected map {expected_proto}, observed {actual_proto}"
    )


def adjacent_hexes(x, y):
    """Six neighbouring hexes in the engine's odd-column offset coordinate system."""
    if x % 2 == 0:
        offsets = ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (0, -1))
    else:
        offsets = ((1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (0, 1))
    return [(x + dx, y + dy) for dx, dy in offsets]


def npc_approach_hexes(npc, map_info=None):
    candidates = adjacent_hexes(int(npc["hexX"]), int(npc["hexY"]))
    map_info = map_info or {}
    width = map_info.get("width")
    height = map_info.get("height")
    if isinstance(width, int) and isinstance(height, int):
        candidates = [(x, y) for x, y in candidates if 0 <= x < width and 0 <= y < height]
    return candidates


def chosen_at_hex(observation, target_hex):
    chosen = (observation or {}).get("chosen") or {}
    return chosen.get("hexX") == target_hex[0] and chosen.get("hexY") == target_hex[1]


def wait_for_observation(b, predicate, timeout, poll_interval=0.25):
    deadline = time.monotonic() + timeout
    while True:
        observation = b.observe_safe()
        if observation is not None and predicate(observation):
            return observation
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return None
        time.sleep(min(poll_interval, remaining))


def event_cursor(b):
    cursor = 0
    for event in b.events(0, 500):
        cursor = max(cursor, event.get("seq", 0))
    return cursor


def read_talk_diagnostic(b, cursor, npc_id):
    latest = None
    for event in b.events(cursor, 500):
        cursor = max(cursor, event.get("seq", 0))
        payload = event.get("event", {})
        if payload.get("type") == "talk_diagnostic" and payload.get("npcId") == npc_id:
            latest = payload
    return cursor, latest


def format_talk_diagnostic(diagnostic):
    if not diagnostic:
        return ""
    status = diagnostic.get("status", "unknown")
    distance = diagnostic.get("distance")
    talk_distance = diagnostic.get("talkDistance")
    player_sees = diagnostic.get("playerSeesNpc")
    npc_sees = diagnostic.get("npcSeesPlayer")
    return (
        f"server={status}, distance={distance}/{talk_distance}, "
        f"playerSeesNpc={str(player_sees).lower()}, npcSeesPlayer={str(npc_sees).lower()}"
    )


def teleport_chosen_hex(b, target_hex, timeout, retry_interval=2.0):
    """Retry the async QA transfer until the server-side transfer is observed."""
    deadline = time.monotonic() + max(0.0, timeout)
    while True:
        b.act("qa_teleport_hex", x=target_hex[0], y=target_hex[1])
        remaining = max(0.0, deadline - time.monotonic())
        observation = wait_for_observation(
            b,
            lambda current: chosen_at_hex(current, target_hex),
            min(retry_interval, remaining),
        )
        if observation is not None:
            return observation
        if time.monotonic() >= deadline:
            return None


def open_dialog_near_npc(
    b,
    npc,
    teleport_timeout=10.0,
    dialog_timeout=10.0,
    talk_retry_interval=2.0,
):
    """Try every valid adjacent hex and retry talk while the confirmed position is retained."""
    initial = b.observe_safe()
    if initial is None:
        raise DialogOpenError(f"cannot open dialog with NPC {npc['id']}: client observation unavailable")

    visible_npc = next(
        (cr for cr in (initial.get("critters") or []) if cr.get("id") == npc.get("id")),
        npc,
    )
    candidates = npc_approach_hexes(visible_npc, initial.get("map"))
    failures = []
    for target_hex in candidates:
        current = b.observe_safe()
        if current is None:
            raise DialogOpenError(
                f"cannot open dialog with NPC {npc['id']}: client observation unavailable"
            )
        if not chosen_at_hex(current, target_hex):
            if teleport_chosen_hex(b, target_hex, teleport_timeout) is None:
                if b.observe_safe() is None:
                    raise DialogOpenError(
                        f"cannot open dialog with NPC {npc['id']}: client observation unavailable "
                        f"while checking teleport to {target_hex}"
                    )
                failures.append(f"{target_hex}: teleport not observed")
                continue

        b.act("clear_actions")
        cursor = event_cursor(b)
        diagnostic = None
        dialog_deadline = time.monotonic() + max(0.0, dialog_timeout)
        while True:
            b.act("talk_to", targetId=npc["id"])
            remaining = max(0.0, dialog_deadline - time.monotonic())
            if wait_for_observation(
                b,
                lambda observation: bool((observation.get("dialog") or {}).get("active")),
                min(max(0.0, talk_retry_interval), remaining),
            ) is not None:
                return target_hex
            cursor, current_diagnostic = read_talk_diagnostic(b, cursor, npc["id"])
            if current_diagnostic is not None:
                diagnostic = current_diagnostic
            if b.observe_safe() is None:
                raise DialogOpenError(
                    f"cannot open dialog with NPC {npc['id']}: client observation unavailable "
                    f"while waiting for dialog at {target_hex}"
                )
            if time.monotonic() >= dialog_deadline:
                break
        diagnostic_text = format_talk_diagnostic(diagnostic)
        failures.append(
            f"{target_hex}: dialog did not open"
            + (f" ({diagnostic_text})" if diagnostic_text else "")
        )
        b.act("clear_actions")

    details = "; ".join(failures) if failures else "no in-bounds adjacent hexes"
    raise DialogOpenError(f"cannot open dialog with NPC {npc['id']}: {details}")


def find_npc(b, dialog_id, hint_hex=None, proto_id=None):
    """Find a visible NPC by dialogId and optional protoId; nudge near hint_hex to refresh visibility."""
    def matches(critter):
        return critter.get("dialogId") == dialog_id and (
            proto_id is None or critter.get("protoId") == proto_id
        )

    o = b.observe()
    hit = [c for c in (o.get("critters") or []) if matches(c)]
    if hit:
        return hit[0]
    if hint_hex:
        hx, hy = hint_hex
        for (tx, ty) in [(hx + 1, hy), (hx - 1, hy), (hx, hy + 2), (hx, hy - 2), (hx + 3, hy)]:
            b.act("qa_teleport_hex", x=tx, y=ty)
            for _ in range(3):
                time.sleep(2)
                o = b.observe_safe() or {}
                hit = [c for c in (o.get("critters") or []) if matches(c)]
                if hit:
                    return hit[0]
    return None


def dialog_signature(observation):
    dialog = (observation or {}).get("dialog") or {}
    return (
        bool(dialog.get("active")),
        str(dialog.get("dialogId", "")),
        str(dialog.get("text", "")),
        tuple(str(answer) for answer in (dialog.get("answers") or [])),
    )


def dialog_replay_signature(observation):
    """Ignore randomized greetings and cosmetic exit variants when comparing replay roots."""
    active, dialog_id, _text, answers = dialog_signature(observation)
    replayable_answers = tuple(
        answer
        for answer in answers
        if answer.strip().lower().rstrip(".!?") != "ничего"
        and "неважно" not in answer.lower()
        and not any(marker in answer.lower() for marker in AVOID)
    )
    return active, dialog_id, "", replayable_answers


def wait_for_dialog_update(b, previous_signature, timeout=3.0, poll_interval=0.15):
    """Wait for a dialog answer to change/close the visible node, returning the latest observation."""
    deadline = time.monotonic() + timeout
    latest = b.observe_safe()
    while latest is not None and time.monotonic() < deadline:
        if dialog_signature(latest) != previous_signature:
            return latest
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(poll_interval, remaining))
        latest = b.observe_safe()
    return latest


def set_quest_value(b, quest, value, timeout=5.0, current_value=None, retry_interval=2.0):
    """Set and observe a critter property through the async QA surface.

    `qa_set_prop` only confirms that the client sent the async remote call. The script callback can still
    end without writing if its critter is destroyed while Game.Sync waits/acquires, so both trace resets and
    property prerequisites resend until the callback publishes a correlated acknowledgement after `SetAsInt`.
    """
    if current_value == value:
        return current_value

    deadline = time.monotonic() + max(0.0, timeout)
    cursor = 0
    for event in b.events(0, 500):
        cursor = max(cursor, event.get("seq", 0))
    request_id = b.next_qa_request_id()
    observed = None

    while True:
        b.act("qa_set_prop", stringArg=quest, intArg=int(value), x=request_id)
        attempt_deadline = min(
            deadline,
            time.monotonic() + max(0.0, retry_interval),
        )
        while True:
            for event in b.events(cursor, 500):
                cursor = max(cursor, event.get("seq", 0))
                payload = event.get("event", {})
                if (
                    payload.get("type") == "qa_prop_set"
                    and payload.get("requestId") == request_id
                    and normalize_property_name(payload.get("prop", ""))
                    == normalize_property_name(quest)
                ):
                    observed = payload.get("value")
                    if observed == value:
                        return observed

            remaining = attempt_deadline - time.monotonic()
            if remaining <= 0:
                break
            time.sleep(min(0.2, remaining))

        if time.monotonic() >= deadline:
            raise BridgeError(f"could not set {quest}={value}; acknowledged {observed}")


def resolve_trace_answer(answers, selector):
    """Replay exact text first, then the same stable answer slot for authored @@ text variants."""
    expected_index = int(selector["index"])
    expected_text = str(selector["text"])
    if 0 <= expected_index < len(answers) and answers[expected_index] == expected_text:
        return expected_index
    matching = [index for index, answer in enumerate(answers) if answer == expected_text]
    if len(matching) == 1:
        return matching[0]
    if len(answers) == selector.get("answer_count") and 0 <= expected_index < len(answers):
        return expected_index
    return None


def open_trace_root(
    b, npc, dialog_id, quest, baseline, reset_timeout=5.0, current_value=None
):
    set_quest_value(
        b, quest, baseline, timeout=reset_timeout, current_value=current_value
    )
    close_dialog(b)
    open_dialog_near_npc(b, npc)
    observation = b.observe_safe()
    dialog = (observation or {}).get("dialog") or {}
    if not dialog.get("active"):
        raise DialogOpenError(f"dialog {dialog_id} did not become active")
    if dialog_id and dialog.get("dialogId") != dialog_id:
        raise DialogOpenError(
            f"expected dialog {dialog_id}, observed {dialog.get('dialogId') or '<none>'}"
        )
    return observation


def stabilize_trace_root(b, npc, dialog_id, quest, baseline, max_opens=4, reset_timeout=5.0):
    """Confirm repeated opens share a base; answer-triggered one-shot changes are rebased later."""
    observation = open_trace_root(b, npc, dialog_id, quest, baseline, reset_timeout=reset_timeout)
    previous_signature = dialog_replay_signature(observation)
    signatures = [previous_signature]
    for open_count in range(2, max_opens + 1):
        close_dialog(b)
        observation = open_trace_root(
            b, npc, dialog_id, quest, baseline, reset_timeout=reset_timeout
        )
        current_signature = dialog_replay_signature(observation)
        signatures.append(current_signature)
        if current_signature == previous_signature:
            return observation, open_count
        previous_signature = current_signature
    raise DialogOpenError(
        f"dialog {dialog_id} root did not stabilize after {max_opens} opens: "
        + " -> ".join(repr(signature[3][:2]) for signature in signatures)
    )


def evaluate_trace_path(
    b,
    npc,
    dialog_id,
    quest,
    baseline,
    selectors,
    answer_timeout=3.0,
    reset_timeout=5.0,
    current_value=None,
    expected_root_signature=None,
):
    """Reset the traced flag, replay one visible answer path, and return its observed transitions."""
    observation = open_trace_root(
        b,
        npc,
        dialog_id,
        quest,
        baseline,
        reset_timeout=reset_timeout,
        current_value=current_value,
    )
    if (
        expected_root_signature is not None
        and dialog_replay_signature(observation) != expected_root_signature
    ):
        raise TraceRootChanged(observation)
    node_path = []
    current_value = baseline
    for selector in selectors:
        dialog = (observation or {}).get("dialog") or {}
        answers = [str(answer) for answer in (dialog.get("answers") or [])]
        answer_index = resolve_trace_answer(answers, selector)
        if answer_index is None:
            raise BridgeError(
                f"trace path drifted at depth {len(node_path)}: answer {selector['text']!r} is unavailable"
            )

        before = current_value
        previous_signature = dialog_signature(observation)
        answer_text = answers[answer_index]
        b.act("dialog_answer", intArg=answer_index)
        observation = wait_for_dialog_update(b, previous_signature, timeout=answer_timeout)
        after = read_quest_authoritative(b, quest)
        current_value = after
        node_path.append({
            "dialog_text": dialog.get("text", ""),
            "answer_index": answer_index,
            "answer": answer_text,
            "from_value": before,
            "to_value": after,
        })
    return observation, node_path, current_value


def trace_dialog_paths(
    b,
    npc,
    dialog_id,
    quest,
    baseline,
    max_depth=12,
    max_paths=96,
    max_candidates=8,
    answer_timeout=3.0,
    reset_timeout=5.0,
    max_seconds=180.0,
):
    """Explore a bounded live dialog by replay, ranking answers that increase the requested quest flag.

    Only the requested flag is restored between branches. The caller should use a disposable QA character
    because arbitrary authored answer side effects (items and other properties) cannot be rolled back here.
    """
    started_at = time.monotonic()
    deadline = started_at + max(0.0, max_seconds)
    root, root_stabilization_opens = stabilize_trace_root(
        b, npc, dialog_id, quest, baseline, reset_timeout=reset_timeout
    )
    root_dialog = (root or {}).get("dialog") or {}
    root_signature = dialog_replay_signature(root)
    queue = deque(
        (tuple((selector,)), 1)
        for selector in trace_answer_selectors(root_dialog.get("answers") or [])
    )
    expanded_states = set()
    candidates = []
    errors = []
    explored_paths = 0
    current_value = baseline
    root_rebases = 0

    while (
        queue
        and explored_paths < max_paths
        and len(candidates) < max_candidates
        and time.monotonic() < deadline
    ):
        selectors, depth = queue.popleft()
        explored_paths += 1
        try:
            observation, node_path, current_value = evaluate_trace_path(
                b,
                npc,
                dialog_id,
                quest,
                baseline,
                selectors,
                answer_timeout=answer_timeout,
                reset_timeout=reset_timeout,
                current_value=current_value,
                expected_root_signature=root_signature,
            )
        except TraceRootChanged as exc:
            current_value = baseline
            root = exc.observation
            root_dialog = (root or {}).get("dialog") or {}
            root_signature = dialog_replay_signature(root)
            root_rebases += 1
            if root_rebases > 4:
                errors.append({
                    "path": [selector["text"] for selector in selectors],
                    "error": "dialog replay root changed more than 4 times",
                })
                break
            queue = deque(
                (tuple((selector,)), 1)
                for selector in trace_answer_selectors(root_dialog.get("answers") or [])
            )
            expanded_states.clear()
            continue
        except BridgeError as exc:
            current_value = None
            errors.append({"path": [selector["text"] for selector in selectors], "error": str(exc)})
            continue

        transition = node_path[-1]
        before = transition["from_value"]
        after = transition["to_value"]
        if before is not None and after is not None and after > before:
            candidates.append({
                "answer": transition["answer"],
                "keywords": answer_keyword_set(transition["answer"]),
                "from_value": before,
                "to_value": after,
                "stage_advance": after - before,
                "node_path": node_path,
            })
            continue

        dialog = (observation or {}).get("dialog") or {}
        answers = [str(answer) for answer in (dialog.get("answers") or [])]
        if depth >= max_depth or not dialog.get("active") or not answers:
            continue

        state = (
            str(dialog.get("dialogId", "")),
            str(dialog.get("text", "")),
            tuple(answers),
            after,
        )
        if state in expanded_states:
            continue
        expanded_states.add(state)
        children = trace_answer_selectors(answers)
        for child in reversed(children):
            queue.appendleft((selectors + (child,), depth + 1))

    elapsed_seconds = time.monotonic() - started_at
    time_limit_reached = bool(queue) and time.monotonic() >= deadline
    return {
        "baseline": baseline,
        "dialog_id": dialog_id,
        "root_stabilization_opens": root_stabilization_opens,
        "root_rebases": root_rebases,
        "explored_paths": explored_paths,
        "max_depth": max_depth,
        "max_paths": max_paths,
        "max_candidates": max_candidates,
        "candidate_limit_reached": len(candidates) >= max_candidates,
        "max_seconds": max_seconds,
        "elapsed_seconds": round(elapsed_seconds, 3),
        "time_limit_reached": time_limit_reached,
        "truncated": bool(queue),
        "candidates": rank_trace_candidates(candidates),
        "branch_errors": errors,
    }


def _is_avoid(a):
    al = a.lower()
    return any(w in al for w in AVOID)


def navigate_dialog(b, npc, prefer, target, quest, target_mode="at_least", max_steps=18, max_opens=4):
    """Talk to npc and walk the dialog until quest reaches target.

    Robust against the three things that break naive keyword navigation on complex NPCs:
    - first-meeting intros / "continue" speeches with a single answer are auto-advanced;
    - exit-like answers ("[Уходите]", "осматриваюсь", "передумал" ...) are never chosen while a
      fresh non-exit answer exists, so the walk doesn't bail out of the tree early;
    - (speech, answer) pairs are remembered across dialog re-opens, so each re-open explores a new
      branch instead of repeating the same wrong turn.
    """
    def open_dialog():
        return open_dialog_near_npc(b, npc)

    steps = []
    seen = set()  # (speech-text prefix, answer-text) pairs already chosen — persists across re-opens
    for _ in range(max_opens):
        if quest_target_reached(quest_value(b.observe_safe() or {}, quest), target, target_mode):
            close_dialog(b)
            return steps, True
        open_dialog()
        for _ in range(max_steps):
            o = b.observe_safe() or {}
            if quest_target_reached(quest_value(o, quest), target, target_mode):
                close_dialog(b)
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
        if quest_target_reached(read_quest(b, quest), target, target_mode):
            return steps, True
    return steps, quest_target_reached(read_quest(b, quest), target, target_mode)


def ensure_in_game(b, register, name, login_timeout):
    if not b.observe().get("hasChosen"):
        b.act("register" if register else "login", stringArg=name)
        deadline = time.time() + login_timeout
        while time.time() < deadline and not (b.observe_safe() or {}).get("hasChosen"):
            time.sleep(1.5)
    return bool(b.observe().get("hasChosen"))


def load_setup_json(value):
    if not value:
        return []
    source = str(value)
    if source.startswith("@"):
        source = Path(source[1:]).read_text(encoding="utf-8")
    elif not source.lstrip().startswith("["):
        path = Path(source)
        if path.is_file():
            source = path.read_text(encoding="utf-8")
    parsed = json.loads(source)
    if not isinstance(parsed, list) or not all(isinstance(entry, dict) for entry in parsed):
        raise ValueError("--setup-json must be a JSON array of setup objects")
    return parsed


def run_trace(args):
    quest = normalize_property_name(args.flag)
    report = {
        "mode": "trace-dialog",
        "map": args.trace_map,
        "npc": args.npc,
        "dialog": args.dialog,
        "flag": quest,
        "ok": False,
        "state_warning": "only the traced flag is restored; use a disposable QA character",
    }
    b = Bridge(args.host, args.port, args.token, args.timeout)
    original_value = None
    try:
        if not ensure_in_game(b, args.register, args.name, args.login_timeout):
            report["error"] = "could not enter game"
            return report

        teleport_map(b, args.trace_map, timeout=args.map_timeout)
        setup = load_setup_json(args.setup_json)
        original_value = read_quest_authoritative(b, quest)
        if original_value is None:
            report["error"] = f"quest flag {quest} is unavailable"
            return report
        apply_setup(b, setup)
        baseline = read_quest_authoritative(b, quest)
        if baseline is None:
            report["error"] = f"quest flag {quest} is unavailable after setup"
            return report
        npc = find_npc(b, args.dialog, args.npc_hex, proto_id=args.npc)
        report["npc_found"] = bool(npc)
        report["setup_injected"] = setup
        report["original_value"] = original_value
        if not npc:
            report["error"] = (
                f"NPC proto {args.npc} with dialog {args.dialog} not found on {args.trace_map}"
            )
            return report

        trace = trace_dialog_paths(
            b,
            npc,
            args.dialog,
            quest,
            baseline,
            max_depth=args.trace_max_depth,
            max_paths=args.trace_max_paths,
            max_candidates=args.trace_max_candidates,
            answer_timeout=args.trace_answer_timeout,
            reset_timeout=args.trace_reset_timeout,
            max_seconds=args.trace_max_seconds,
        )
        report.update(trace)
        report["ok"] = bool(trace["candidates"])
        if not report["ok"]:
            report["error"] = f"no answer advancing {quest} was found within trace bounds"
        return report
    except (BridgeError, DialogOpenError, OSError, ValueError, json.JSONDecodeError) as exc:
        report["error"] = str(exc)
        return report
    finally:
        if original_value is not None:
            try:
                set_quest_value(b, quest, original_value, timeout=args.trace_reset_timeout)
                report["restored_value"] = original_value
                report["flag_restored"] = True
            except (BridgeError, OSError) as exc:
                report["flag_restored"] = False
                report["restore_error"] = str(exc)
                report["ok"] = False
        try:
            close_dialog(b)
        except (BridgeError, OSError):
            pass
        b.close()


def run(args):
    spec = QUESTS[args.quest]
    report = {"quest": args.quest, "title": spec["title"], "ok": False, "stages": []}
    b = Bridge(args.host, args.port, args.token, args.timeout)
    try:
        # Enter game.
        if not ensure_in_game(b, args.register, args.name, args.login_timeout):
            report["error"] = "could not enter game"
            return report

        apply_setup(b, spec.get("setup"))  # quest-wide prerequisites (run once after entering game)

        for stage in spec["stages"]:
            target_mode = stage.get("target_mode", spec.get("target_mode", "at_least"))
            current_value = read_quest(b, spec["quest"])
            if quest_target_reached(current_value, stage["target"], target_mode):
                current_observation = b.observe_safe() or {}
                report["stages"].append({
                    "stage": stage["name"],
                    "map": (current_observation.get("map") or {}).get("protoId"),
                    "npc": stage["npc"],
                    "npc_found": None,
                    "ok": True,
                    "quest_value": current_value,
                    "dialog_steps": 0,
                    "already_satisfied": True,
                })
                continue

            o = teleport_map(b, stage["map"], timeout=args.map_timeout)
            apply_setup(b, stage.get("setup"))  # per-stage prerequisites (after teleport, before talking)
            npc = find_npc(b, stage["npc"], stage.get("npc_hex"))
            sr = {"stage": stage["name"], "map": (o.get("map") or {}).get("protoId"),
                  "npc": stage["npc"], "npc_found": bool(npc)}
            if not npc:
                sr["ok"] = False
                report["stages"].append(sr)
                report["error"] = f"NPC {stage['npc']} not found on {stage['map']}"
                return report
            try:
                steps, reached = navigate_dialog(
                    b, npc, stage["prefer"], stage["target"], spec["quest"], target_mode
                )
            except DialogOpenError as exc:
                sr["ok"] = False
                sr["quest_value"] = quest_value(b.observe_safe() or {}, spec["quest"])
                sr["dialog_steps"] = 0
                sr["error"] = str(exc)
                report["stages"].append(sr)
                report["error"] = str(exc)
                return report
            sr["ok"] = reached
            sr["quest_value"] = read_quest(b, spec["quest"])
            sr["dialog_steps"] = len(steps)
            sr["already_satisfied"] = False
            report["stages"].append(sr)
            if not reached:
                report["error"] = f"stage {stage['name']} did not reach {spec['quest']}={stage['target']}"
                return report

        report["final_quest_value"] = read_quest(b, spec["quest"])
        report["transitions_verified"] = sum(
            1 for stage in report["stages"] if stage.get("ok") and not stage.get("already_satisfied", False)
        )
        report["exercised"] = report["transitions_verified"] > 0
        report["ok"] = all(s["ok"] for s in report["stages"])
        if getattr(args, "require_exercised", False) and not report["exercised"]:
            report["ok"] = False
            report["error"] = "quest state was already satisfied; no transition was exercised"
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
    ap.add_argument("--register", action="store_true")
    ap.add_argument("--require-exercised", action="store_true",
                    help="fail when all quest stages were already satisfied before the run")
    ap.add_argument("--login-timeout", type=float, default=45.0)
    ap.add_argument("--map-timeout", type=float, default=90.0,
                    help="seconds to wait for an observed map proto after QA teleport")
    ap.add_argument("--report", default="")
    ap.add_argument("--list", action="store_true", help="list known quest specs and exit")
    ap.add_argument("--trace-dialog", action="store_true",
                    help="discover visible answer paths that advance one quest flag")
    ap.add_argument("--map", dest="trace_map", default="",
                    help="location/map target used by --trace-dialog")
    ap.add_argument("--npc", default="", help="NPC prototype id used by --trace-dialog")
    ap.add_argument("--dialog", default="", help="expected dialog id used by --trace-dialog")
    ap.add_argument("--flag", default="", help="Critter quest property traced by --trace-dialog")
    ap.add_argument("--npc-hex", nargs=2, type=int, metavar=("X", "Y"),
                    help="optional NPC visibility hint used by --trace-dialog")
    ap.add_argument("--setup-json", default="",
                    help="JSON array (or file path) with qa_set_prop/game_prop/give_item prerequisites")
    ap.add_argument("--trace-max-depth", type=int, default=12)
    ap.add_argument("--trace-max-paths", type=int, default=96)
    ap.add_argument("--trace-max-candidates", type=int, default=8)
    ap.add_argument("--trace-max-seconds", type=float, default=180.0)
    ap.add_argument("--trace-answer-timeout", type=float, default=3.0)
    ap.add_argument("--trace-reset-timeout", type=float, default=30.0)
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass

    if args.list:
        for k, v in QUESTS.items():
            print(f"{k}: {v['title']}")
        return 0

    if args.map_timeout <= 0:
        ap.error("--map-timeout must be positive")

    if args.trace_dialog:
        missing = [
            option
            for option, value in (
                ("--map", args.trace_map),
                ("--npc", args.npc),
                ("--dialog", args.dialog),
                ("--flag", args.flag),
            )
            if not value
        ]
        if missing:
            ap.error(f"--trace-dialog requires {', '.join(missing)}")
        if (
            args.trace_max_depth < 1
            or args.trace_max_paths < 1
            or args.trace_max_candidates < 1
            or args.trace_max_seconds <= 0
            or args.trace_answer_timeout <= 0
            or args.trace_reset_timeout <= 0
        ):
            ap.error("trace bounds must be positive")
        report = run_trace(args)
    else:
        report = run(args)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(text, encoding="utf-8")
    print(text)
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
