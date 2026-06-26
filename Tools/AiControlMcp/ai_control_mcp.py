#!/usr/bin/env python3
"""Minimal MCP stdio adapter for the The Life After AI control bridge."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import socket
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from ai_control_advisory import goal_has_xp_marker
from ai_control_advisory import int_or_default
from ai_control_advisory import result_limit
from ai_control_advisory import task_option
from ai_control_advisory import xp_progress_payload
from ai_control_advisory import xp_source_option
from ai_control_guides import agent_examples_text as guide_agent_examples_text
from ai_control_guides import conversation_guide_text as guide_conversation_guide_text
from ai_control_guides import operator_guide_text as guide_operator_guide_text
from ai_control_launch import as_bool as launch_as_bool
from ai_control_launch import binary_name_for_role as launch_binary_name_for_role
from ai_control_launch import build_accounts_launch_arguments as launch_build_accounts_launch_arguments
from ai_control_launch import build_launch_options as launch_build_launch_options
from ai_control_launch import build_scene_launch_arguments as launch_build_scene_launch_arguments
from ai_control_launch import build_two_players_launch_arguments as launch_build_two_players_launch_arguments
from ai_control_launch import copy_launch_arguments as launch_copy_launch_arguments
from ai_control_launch import encode_launch_setting_list as launch_encode_launch_setting_list
from ai_control_launch import format_setting_value as launch_format_setting_value
from ai_control_launch import launch_recipe_arguments as launch_launch_recipe_arguments
from ai_control_launch import normalize_launch_accounts as launch_normalize_launch_accounts
from ai_control_launch import parse_fomain_launch_config as launch_parse_fomain_launch_config
from ai_control_launch import parse_startup_scene_input as launch_parse_startup_scene_input
from ai_control_launch import parse_startup_scene_input_fallback as launch_parse_startup_scene_input_fallback
from ai_control_launch import set_launch_setting as launch_set_launch_setting
from ai_control_protocol import bridge_text_result as protocol_bridge_text_result
from ai_control_protocol import mcp_error as protocol_mcp_error
from ai_control_protocol import mcp_result as protocol_mcp_result


MCP_VERSION = "2025-11-25"
SERVER_NAME = "last-frontier-ai-control"
SERVER_VERSION = "0.1.0"
SCHEMA_VERSION = 1
OPERATOR_GUIDE_URI = "tla://guide/operator"
AGENT_EXAMPLES_URI = "tla://guide/agent-examples"
OPERATOR_GUIDE_PROMPT = "tla_operator_guide"
CONVERSATION_GUIDE_PROMPT = "tla_conversation_guide"
AGENT_EXAMPLES_PROMPT = "tla_agent_examples"
AGENT_EXAMPLES_PROMPT_DESCRIPTION = "Starter The Life After agent profiles and matching run hints."
ACTION_WAIT_ARGUMENTS = {"waitForCompletion", "timeoutMs", "pollIntervalMs", "limit", "includeEvents", "maxReturnedEvents"}
ACTION_SYNC_ARGUMENTS = {"syncAfterCompletion", "includeObservation", "includeStatus"}
ENDPOINT_TARGET_ARGUMENTS = {"endpointId", "processId", "endpointIndex", "host", "port", "token"}
COMMAND_META_ARGUMENTS = ACTION_WAIT_ARGUMENTS | ACTION_SYNC_ARGUMENTS | ENDPOINT_TARGET_ARGUMENTS
AGENT_RUN_META_ARGUMENTS = {
    "execute",
    "maxSteps",
    "maxActions",
    "stopOnNoAction",
    "stopOnBlocked",
    "respectDelay",
    "maxSleepMs",
    "minActionIntervalMs",
    "maxActionsPerMinute",
    "schedulerJitterMs",
    "schedulerSeed",
    "allowHighPriorityInterrupt",
    "stopOnSchedulerWait",
    "commandTimeoutMs",
    "syncAfterAction",
    "validatePath",
    "pathTimeoutMs",
    "pathCut",
    "allowRawInput",
    "allowCombat",
    "allowSpeech",
    "allowRosterDelete",
    "autoReply",
    "speechText",
    "allowedTools",
    "blockedTools",
    "enableLoopDetection",
    "stopOnLoop",
    "repeatedDecisionLimit",
    "failedActionLimit",
    "stuckMovementLimit",
    "stopOnDistress",
    "distressKeywords",
    "deploymentMode",
    "permissionMode",
    "agentDisclosure",
    "outOfBandCoordination",
    "policyNote",
}
AGENT_RUN_DECISION_ARGUMENTS = {
    "allowRawInput",
    "allowCombat",
    "allowSpeech",
    "allowRosterDelete",
    "allowedTools",
    "blockedTools",
}
AGENT_DEPLOYMENT_MODES = {"test_only", "private_qa", "supervised_agent", "marked_bot", "production_npc"}
AGENT_PERMISSION_MODES = {"observe_only", "command_safe", "full_gameplay", "raw_input_fallback", "qa_out_of_band"}
AGENT_POLICY_DEFAULT_DEPLOYMENT_MODE = "private_qa"
AGENT_POLICY_DEFAULT_PERMISSION_MODE = "command_safe"
AGENT_RUN_RAW_TOOLS = {"tla_mouse_click", "tla_key_press"}
AGENT_RUN_COMBAT_TOOLS = {"tla_attack_entity", "tla_attack_hex"}
AGENT_RUN_DESTRUCTIVE_TOOLS = {"tla_roster_delete"}
AGENT_RUN_FORBIDDEN_TOOLS = {
    "tla_act",
    "tla_act_and_sync",
    "tla_launch",
    "tla_launch_accounts",
    "tla_launch_scene",
    "tla_launch_two_players",
    "tla_logs",
    "tla_window_screenshot",
    "tla_schema",
    "tla_stop_process",
    "tla_agent_stop_all",
}
AGENT_RUN_FORBIDDEN_PREFIXES = ("tla_launch_", "tla_admin_")
AGENT_DISTRESS_KEYWORDS = (
    "stop",
    "leave me alone",
    "go away",
    "don't follow",
    "do not follow",
    "стоп",
    "остановись",
    "уйди",
    "отстань",
    "не мешай",
    "не следуй",
    "хватит",
)
AGENT_GOAL_RETREAT_MARKERS = (
    "flee",
    "retreat",
    "run away",
    "escape",
    "withdraw",
    "keep distance",
    "stay away",
    "avoid threat",
    "avoid danger",
    "avoid fight",
    "stay alive",
    "беги",
    "сбеги",
    "отступ",
    "держи дистан",
    "избег",
    "опас",
)
AGENT_GOAL_EXPLORE_MARKERS = (
    "explore",
    "wander",
    "walk through",
    "scout",
    "map the area",
    "unknown",
    "frontier",
    "nearby places",
    "исслед",
    "осмотр",
    "развед",
    "обойди",
)
AGENT_GOAL_EXIT_MARKERS = (
    "find exit",
    "exit",
    "leave map",
    "map transition",
    "enter location",
    "выход",
    "покин",
    "перейти",
)
AGENT_GOAL_MOVE_MARKERS = (
    "move to",
    "go to",
    "walk to",
    "reach hex",
    "идти",
    "перейди",
)
AGENT_GOAL_APPROACH_MARKERS = (
    "approach",
    "come to",
    "talk to",
    "pick item",
    "loot",
    "подойди",
    "поговор",
    "подбери",
    "обыщи",
)
AGENT_GOAL_FOLLOW_MARKERS = (
    "follow",
    "rendezvous",
    "stay with",
    "следуй",
    "держись рядом",
)
AGENT_GOAL_COMBAT_APPROACH_MARKERS = (
    "attack",
    "fight",
    "kill",
    "hunt",
    "shoot",
    "engage",
    "clear hostile",
    "атак",
    "бей",
    "бой",
    "уб",
    "охот",
    "стрел",
    "зачист",
)
NAV_APPROACH_NONCOMBAT_TYPES = {"talk_to", "pick_item", "pick_hex", "loot_critter"}
NAV_APPROACH_COMBAT_TYPES = {"attack_entity", "attack_hex"}
NAV_APPROACH_TYPES = NAV_APPROACH_NONCOMBAT_TYPES | NAV_APPROACH_COMBAT_TYPES
NAV_APPROACH_STANDING_TYPES = {*NAV_APPROACH_TYPES, "visible_item", "visible_critter"}
NAV_MAP_TARGET_TYPES = ("move_to_hex", "talk_to", "pick_item", "pick_hex", "loot_critter", "attack_entity", "attack_hex")
AGENT_APPROACH_DEFAULT_MAX_TARGETS = 4
AGENT_APPROACH_DEFAULT_MAX_CANDIDATES = 3
AGENT_APPROACH_DEFAULT_PATH_TIMEOUT_MS = 1200
AGENT_APPROACH_TYPE_PRIORITY = {
    "talk_to": 0,
    "visible_critter": 0,
    "loot_critter": 1,
    "pick_item": 2,
    "visible_item": 2,
    "pick_hex": 2,
    "attack_entity": 3,
    "attack_hex": 3,
}
ITEM_KIND_KEYWORDS = {
    "ammo": ("ammo", "bullet", "shell", "rocket", "cartridge", "round"),
    "healing": ("med", "medicine", "medkit", "stim", "heal", "bandage", "antidote", "rad", "recovery", "fieldaid", "drug"),
    "weapon": ("weapon", "gun", "pistol", "rifle", "shotgun", "knife", "spear", "bazooka", "laser", "lasgun", "secm", "secd", "rookie"),
    "armor": ("armor", "suit", "helmet", "coat", "jacket", "vest"),
    "currency": ("gold", "coin", "money", "cap", "caps", "token"),
    "food": ("food", "meat", "water", "drink", "beer", "moonshine", "ration"),
    "junk": ("junk", "trash", "scrap", "debris", "rock"),
}
CRITTER_ITEM_SLOT_MAIN = 1
CRITTER_ITEM_SLOT_ARMOR = 3
MELEE_WEAPON_MARKERS = ("knife", "spear", "blade", "club", "bat", "axe", "hammer", "melee", "unarmed", "fist")
RELOADABLE_WEAPON_MARKERS = ("gun", "pistol", "rifle", "shotgun", "smg", "secm", "secd", "laser", "lasgun", "bazooka", "rocket", "rookie")
BREACH_VISUAL_LABEL = "BRCH"
DEVICE_OVERRIDE_VISUAL_LABEL = "OVR"
DEFAULT_EXPLOSIVE_TIMER_SECONDS = 30
DANGEROUS_TARGET_MARKERS = (
    "raider",
    "bandit",
    "hostile",
    "enemy",
    "aggressive",
    "soldier",
    "guard",
    "battalion",
    "mutant",
    "ghoul",
    "vestnik",
    "explosion",
    "explosive",
    "blowup",
    "grenade",
    "boom",
    "rat",
    "dog",
    "hound",
    "robot",
    "bot",
    "policebot",
    "turret",
    "drone",
    "mech",
    "мутант",
    "гуль",
    "вестник",
    "солдат",
    "охран",
    "рейдер",
    "бандит",
    "крыса",
    "собак",
    "пёс",
    "пес",
    "взрыв",
    "гранат",
)
ALLY_TARGET_MARKERS = ("tutorial_josh", "josh", "helper", "guide", "ally", "джош", "помощ", "союз", "проводник")
PROTECTED_TARGET_MARKERS = (
    "trader",
    "merchant",
    "vendor",
    "settler",
    "civilian",
    "safenpc",
    "playerteam",
    "торгов",
    "торгаш",
    "купец",
    "поселен",
    "мирн",
)
PROTECTED_TARGET_TEAM_MARKERS = (
    "safenpc",
    "playerteam",
    "trader",
    "trader_main",
    "trader_neutral",
)
COMBAT_GOAL_MARKERS = ("attack", "fight", "kill", "clear", "hostile", "enemy", "protect", "preserve", "save", "dog", "rat", "атак", "бой", "уб", "зачист", "враг", "защит", "спас", "собак", "крыса", "джош", "союз")
ANSWER_INTENT_MARKERS = {
    "leave": ("пока", "до свид", "уйти", "уход", "законч", "хватит", "bye", "goodbye", "leave", "end"),
    "trade": ("бартер", "торг", "куп", "прод", "обмен", "товар", "trade", "barter", "buy", "sell"),
    "question": ("?", "что", "как", "где", "куда", "когда", "кто", "почему", "зачем", "расскаж", "what", "how", "where", "when", "why", "tell"),
    "accept": ("да", "соглас", "готов", "берусь", "помогу", "начать", "прин", "yes", "agree", "accept", "start", "ready"),
    "refuse": ("нет", "не хочу", "откаж", "позже", "не буду", "no", "refuse", "later"),
    "hostile": ("атак", "уб", "стрел", "угрож", "драться", "attack", "kill", "shoot", "fight", "threat"),
    "healing": ("леч", "мед", "аптеч", "medicine", "medkit", "heal"),
}
DEFAULT_ENVIRONMENT_QUERY_TIMEOUT_MS = 5000
DEFAULT_TACTICAL_PATH_TIMEOUT_MS = 15000
NAV_QUERY_OPTION_NAMES = (
    "fromX",
    "fromY",
    "cut",
    "includeDirections",
    "maxDirections",
    "maxDistance",
    "angle",
    "maxCritters",
    "avoidRadius",
    "searchRadius",
    "hazardWeight",
    "maxCandidates",
    "avoidPlayers",
    "maxThreats",
    "timeoutMs",
    "pollIntervalMs",
    "limit",
)
DEFAULT_WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
MAPS_ROOT = DEFAULT_WORKSPACE_ROOT / "Maps"
FOMAP_HEX_VALUE_RE = re.compile(r"^\s*Hex\s*=\s*(-?\d+)\s+(-?\d+)\s*$")
FOMAP_MULTIHEX_VALUE_RE = re.compile(r'"(-?\d+)\s+(-?\d+)"')
AUTHORED_ELEVATOR_TRIGGER_CACHE: dict[str, list[dict[str, Any]]] = {}
AUTHORED_STATIC_SCRIPT_ITEM_CACHE: dict[str, list[dict[str, Any]]] = {}
LAUNCH_ROLES = ("server", "server_headless", "client", "client_headless")
SAY_TYPE_VALUES = {"normal": 0, "shout": 1, "whisper": 2, "emote": 3}
INTEREST_TYPE_VALUES = {"self": 0, "group": 1, "unknown_place": 2, "known_place": 3, "camp": 4, "encounter": 5, "quest_giver": 6, "death_stash": 7}
SKILL_PROPERTY_NAMES = (
    "SkillMelee",
    "SkillSmallGuns",
    "SkillBigGuns",
    "SkillExplosions",
    "SkillTravelling",
    "SkillForaging",
    "SkillTechnics",
    "SkillMedicine",
    "SkillInfiltration",
    "SkillLeadership",
)
COMBAT_SKILL_NAMES = {"SkillMelee", "SkillSmallGuns", "SkillBigGuns", "SkillExplosions"}
ADMIN_PREPARE_PRESETS = (
    "power_up",
    "power_up_full",
    "max_carry_weight",
    "give_all_weapons",
    "add_points",
    "open_global_map",
    "open_entry_points",
    "open_current_location_entry_points",
    "move_to_global",
    "reset_replication",
    "transport_test",
    "juggernaut_build",
    "sniper_build",
    "infantry_build",
    "guard_provoke",
    "guard_make_member",
)
ADMIN_COMMAND_TYPES = {
    "admin_prepare",
    "admin_teleport_to_hex",
    "admin_move_to_map",
    "admin_to_faction_leader",
    "admin_spawn_mob_at_target",
    "admin_set_weather",
}
DEFAULT_LOG_NAMES = {
    "server": "TLA_Server.log",
    "server_headless": "TLA_ServerHeadless.log",
    "client": "TLA_Client.log",
    "client_headless": "TLA_ClientHeadless.log",
}
DEFAULT_AGENT_PROFILE = {
    "preset": "custom",
    "name": "",
    "displayName": "",
    "aliases": [],
    "role": "",
    "faction": "",
    "stance": "neutral",
    "goals": [],
    "taboos": [],
    "conversationStyle": "Stay in character, answer briefly, and use normal visible speech when a response is useful.",
    "responsePolicy": "Listen to visible speech, decide whether it is addressed to you, and respond only when the message needs your role-consistent reaction.",
    "speechStyle": "Natural, concise, and role-consistent.",
    "socialPolicy": "Reply when addressed or when the role clearly calls for it; stay quiet when busy, unsafe, or not involved.",
    "riskTolerance": "normal",
    "combatStyle": "defensive",
    "lootStyle": "practical",
    "activityLevel": "normal",
    "reactionProfile": "normal",
    "skillLevel": "average",
    "language": "russ",
}
NAV_RISK_TOLERANCE_MULTIPLIER = {"very_low": 1.6, "low": 1.3, "normal": 1.0, "high": 0.65}
NAV_ROUTE_FAILURE_RECENCY_MS = 30 * 60 * 1000
NAV_ROUTE_HAZARD_RADIUS = 2
NAV_ROUTE_CROWDING_RADIUS = 1
AGENT_HUMANIZED_MISTAKES = {"cautious_hesitation", "forget_low_priority", "non_optimal_route"}
AGENT_PROFILE_PRESETS: dict[str, dict[str, Any]] = {
    "qa_tester": {
        "role": "QA tester",
        "goals": ["exercise visible features", "record bugs with reproducible context"],
        "conversationStyle": "Brief and functional; mention test intent only when useful.",
        "responsePolicy": "Answer direct questions, avoid disrupting players, and prioritize bug reproduction.",
        "riskTolerance": "normal",
        "combatStyle": "defensive",
        "lootStyle": "test-relevant",
        "activityLevel": "busy",
        "reactionProfile": "normal",
        "skillLevel": "expert",
    },
    "wanderer": {
        "role": "wandering survivor",
        "goals": ["explore nearby places", "stay alive", "talk when approached"],
        "riskTolerance": "low",
        "combatStyle": "avoidant",
        "lootStyle": "survival",
        "activityLevel": "calm",
        "reactionProfile": "slow",
    },
    "trader": {
        "role": "travelling trader",
        "goals": ["find people", "offer trade", "avoid unnecessary combat"],
        "riskTolerance": "low",
        "combatStyle": "avoidant",
        "lootStyle": "valuable",
        "activityLevel": "normal",
    },
    "guard": {
        "role": "guard",
        "goals": ["watch nearby players", "answer short questions", "protect allies"],
        "riskTolerance": "high",
        "combatStyle": "defensive",
        "lootStyle": "minimal",
        "activityLevel": "watchful",
        "reactionProfile": "fast",
    },
    "newbie": {
        "role": "new player",
        "goals": ["learn controls", "ask simple questions", "avoid danger"],
        "riskTolerance": "very_low",
        "combatStyle": "avoidant",
        "lootStyle": "curious",
        "activityLevel": "hesitant",
        "reactionProfile": "slow",
        "skillLevel": "novice",
    },
    "social_player": {
        "role": "social player",
        "goals": ["greet nearby people", "keep conversations natural", "help when asked"],
        "conversationStyle": "Friendly, conversational, and not too long.",
        "socialPolicy": "Prefer replying to direct speech; do not spam greetings.",
        "riskTolerance": "normal",
        "activityLevel": "social",
    },
    "cautious_explorer": {
        "role": "cautious explorer",
        "goals": ["map the area", "avoid threats", "inspect interesting objects"],
        "riskTolerance": "low",
        "combatStyle": "defensive",
        "lootStyle": "survival",
        "activityLevel": "methodical",
    },
    "aggressive_raider": {
        "role": "aggressive raider",
        "goals": ["seek fights", "loot useful items", "intimidate enemies"],
        "riskTolerance": "high",
        "combatStyle": "aggressive",
        "lootStyle": "combat",
        "activityLevel": "busy",
        "reactionProfile": "fast",
    },
    "helper": {
        "role": "helper",
        "goals": ["answer direct questions", "guide confused players", "avoid taking over"],
        "conversationStyle": "Calm, clear, and concise.",
        "responsePolicy": "Reply to direct requests and greetings; otherwise observe quietly.",
        "riskTolerance": "normal",
        "combatStyle": "support",
        "lootStyle": "minimal",
    },
}
AGENT_PROFILE_TEXT_FIELDS = {
    "preset",
    "name",
    "displayName",
    "role",
    "faction",
    "stance",
    "conversationStyle",
    "responsePolicy",
    "speechStyle",
    "socialPolicy",
    "riskTolerance",
    "combatStyle",
    "lootStyle",
    "activityLevel",
    "reactionProfile",
    "skillLevel",
    "language",
}
AGENT_PROFILE_LIST_FIELDS = {"aliases", "goals", "taboos"}
SOCIAL_PROFILE_FIELDS = AGENT_PROFILE_TEXT_FIELDS | AGENT_PROFILE_LIST_FIELDS
SECOND_PERSON_MARKERS = (
    "ты",
    "тебя",
    "тебе",
    "тобой",
    "твой",
    "твоя",
    "твое",
    "твои",
    "вы",
    "вас",
    "вам",
    "вами",
    "ваш",
    "ваша",
    "ваше",
    "ваши",
    "you",
    "your",
)
QUESTION_MARKERS = (
    "?",
    "почему",
    "зачем",
    "как",
    "что",
    "где",
    "куда",
    "когда",
    "кто",
    "можешь",
    "можете",
    "можно",
    "why",
    "what",
    "where",
    "when",
    "how",
    "who",
    "can you",
)
REQUEST_MARKERS = (
    "помоги",
    "помогите",
    "нужно",
    "надо",
    "можешь",
    "можете",
    "дай",
    "дайте",
    "скажи",
    "скажите",
    "покажи",
    "покажите",
    "иди",
    "идите",
    "пойдем",
    "пойдём",
    "давай",
    "help",
    "need",
    "give",
    "tell",
    "show",
    "come",
    "go",
)
GREETING_MARKERS = ("привет", "здрав", "добрый", "доброе", "hello", "hi", "hey")
PROMISE_MARKERS = ("обеща", "обещаю", "сделаю", "помогу", "принесу", "вернусь", "promise", "i will", "i'll", "will help", "bring")
POSITIVE_TONE_MARKERS = ("спасибо", "рад", "отлично", "хорошо", "thanks", "thank you", "great", "good")
HOSTILE_TONE_MARKERS = ("убью", "атак", "ненавиж", "пошел", "пошёл", "дурак", "kill", "attack", "hate", "idiot", "stupid")
WORRIED_TONE_MARKERS = ("страш", "опас", "боюсь", "помог", "срочно", "умира", "scared", "danger", "afraid", "urgent", "dying")
QUEST_SURFACE_FIELDS = ("questSummary", "questLog", "visibleQuests", "pdaQuests", "questNotifications")
PDA_QUEST_SURFACE_FIELDS = ("quests", "questLog", "visibleQuests", "notifications")
QUEST_ENTRY_FIELDS = (
    "id",
    "questId",
    "title",
    "name",
    "text",
    "description",
    "objective",
    "status",
    "state",
    "statusCode",
    "stage",
    "progress",
    "target",
    "mapMarker",
    "location",
    "visible",
    "updatedAt",
)
SOCIAL_TOPIC_MARKERS = {
    "help": ("помоги", "помогите", "help"),
    "directions": ("куда", "где", "выход", "дорог", "маршрут", "where", "exit", "route", "direction"),
    "trade": ("торг", "торговл", "бартер", "куп", "прод", "товар", "trade", "barter", "buy", "sell"),
    "combat": ("атак", "бей", "бой", "уб", "стрел", "attack", "fight", "kill", "shoot"),
    "loot": ("лут", "обыщи", "подбери", "loot", "pick", "take"),
    "quest": ("квест", "задани", "работ", "quest", "task", "job"),
    "health": ("леч", "лечен", "аптеч", "мед", "умира", "heal", "med", "medicine", "dying"),
}


COMMAND_CATALOG: list[dict[str, Any]] = [
    {
        "type": "move_to_hex",
        "description": "Move the chosen critter to a map hex.",
        "required": ["x", "y"],
        "parameters": {"x": "Map hex X.", "y": "Map hex Y.", "append": "Append to current action queue."},
    },
    {
        "type": "global_move_to",
        "description": "Move the chosen global-map group to global map coordinates.",
        "required": ["x", "y"],
        "parameters": {"x": "Global map X.", "y": "Global map Y."},
    },
    {
        "type": "global_enter_interest",
        "description": "Enter an in-range global-map interest such as the current camp, encounter, quest giver, group, known place, or death stash (recovers lost loot to inventory).",
        "required": ["intArg"],
        "parameters": {
            "intArg": "InterestType enum value: self=0, group=1, known_place=3, camp=4, encounter=5, quest_giver=6, death_stash=7.",
            "x": "Trip id for self/group interests.",
            "targetId": "Location/container id for camp/encounter/death_stash interests.",
            "stringArg": "Location proto id for known_place interests or quest id for quest_giver interests.",
            "mapPid": "Optional known-place checkpoint map proto id.",
            "entryName": "Optional known-place checkpoint entry name.",
        },
    },
    {
        "type": "attack_entity",
        "description": "Attack a visible critter/entity target.",
        "required": ["targetId"],
        "parameters": {"targetId": "Target critter id.", "append": "Append to current action queue."},
    },
    {
        "type": "attack_hex",
        "description": "Attack a map hex.",
        "required": ["x", "y"],
        "parameters": {"x": "Map hex X.", "y": "Map hex Y.", "append": "Append to current action queue."},
    },
    {
        "type": "pick_item",
        "description": "Pick up or interact with a visible map item or scripted static scenery.",
        "required": ["itemId"],
        "parameters": {"itemId": "Map item id.", "isStatic": "True for scripted static scenery entries.", "append": "Append to current action queue."},
    },
    {
        "type": "pick_hex",
        "description": "Pick an item from a map hex when an exact item id is not known.",
        "required": ["x", "y"],
        "parameters": {"x": "Map hex X.", "y": "Map hex Y.", "append": "Append to current action queue."},
    },
    {
        "type": "talk_to",
        "description": "Start dialog with an NPC through the normal chosen action path.",
        "required": ["targetId"],
        "parameters": {
            "targetId": "NPC critter id from visible candidates.",
            "protoId": "Fallback NPC prototype id for static authored NPCs that are not listed in visible candidates.",
            "x": "Expected authored NPC map hex X for proto fallback.",
            "y": "Expected authored NPC map hex Y for proto fallback.",
            "append": "Append to current action queue.",
        },
    },
    {
        "type": "group_invite",
        "description": "Invite a visible player-controlled critter to the chosen player's group through the normal group request path.",
        "required": ["targetId"],
        "parameters": {"targetId": "Visible player critter id."},
    },
    {
        "type": "loot_critter",
        "description": "Open loot for a dead or lootable critter.",
        "required": ["targetId"],
        "parameters": {"targetId": "Target critter id.", "append": "Append to current action queue."},
    },
    {
        "type": "use_item",
        "description": "Use an inventory item, optionally on a target critter or item.",
        "required": ["itemId"],
        "parameters": {
            "itemId": "Inventory item id.",
            "targetId": "Optional target critter id.",
            "auxId": "Optional target item id.",
            "stringArg": "Optional use-mode string.",
            "append": "Append to current action queue.",
        },
    },
    {
        "type": "reload",
        "description": "Reload a weapon.",
        "required": ["itemId"],
        "parameters": {"itemId": "Weapon item id.", "auxId": "Optional ammo item id.", "intArg": "Non-zero means full reload.", "append": "Append."},
    },
    {
        "type": "unload",
        "description": "Unload a weapon.",
        "required": ["itemId"],
        "parameters": {"itemId": "Weapon item id.", "intArg": "Non-zero means unload all.", "append": "Append to current action queue."},
    },
    {
        "type": "move_item",
        "description": "Move an inventory item to a critter slot.",
        "required": ["itemId", "intArg"],
        "parameters": {"itemId": "Inventory item id.", "intArg": "CritterItemSlot enum value.", "append": "Append to current action queue."},
    },
    {
        "type": "drop_item",
        "description": "Drop an item from inventory.",
        "required": ["itemId"],
        "parameters": {"itemId": "Inventory item id.", "intArg": "Optional count; default is the whole stack.", "append": "Append to current action queue."},
    },
    {
        "type": "operate_container",
        "description": "Move items through the currently opened container/loot UI.",
        "required": ["intArg"],
        "parameters": {
            "itemId": "Optional item id inside the open collection; omit when taking or putting all.",
            "intArg": "Packed flags/count: bit 0 take, bit 1 all, higher bits item count.",
        },
    },
    {
        "type": "toggle_sneak",
        "description": "Toggle sneak mode.",
        "required": [],
        "parameters": {"append": "Append to current action queue."},
    },
    {
        "type": "set_overwatch",
        "description": "Hold or clear a SmallGuns overwatch sector. Direction uses hex direction 0..5; intArg=-1 clears.",
        "required": ["intArg"],
        "parameters": {"intArg": "Hex direction 0..5, or -1 to clear the current overwatch sector."},
    },
    {
        "type": "dialog_answer",
        "description": "Send an answer to the active dialog.",
        "required": ["intArg"],
        "parameters": {"intArg": "Zero-based answer index from observation.dialog.answers."},
    },
    {
        "type": "ui_answer",
        "description": "Answer the active semantic GUI prompt, such as confirm/yes-no/DialogBox/elevator, without raw mouse coordinates.",
        "required": [],
        "parameters": {"intArg": "Zero-based answer index from observation.uiPrompt.buttons; either intArg or stringArg satisfies this command.", "stringArg": "Button id when an index is not known; substitutes for intArg."},
    },
    {
        "type": "say",
        "description": "Send player-visible speech through the normal chat/say path.",
        "required": ["stringArg"],
        "parameters": {"stringArg": "Speech text.", "intArg": "SayType enum value: 0 normal, 1 shout, 2 whisper, 3 emote."},
    },
    {
        "type": "accept_agreement",
        "description": "Accept the account agreement through the normal registration path.",
        "required": [],
        "parameters": {},
    },
    {
        "type": "generate_critter",
        "description": "Confirm the current generated appearance/body for the chosen critter.",
        "required": [],
        "parameters": {},
    },
    {
        "type": "finish_generation",
        "description": "Apply default starting stat allocation through the normal character-generation server calls.",
        "required": [],
        "parameters": {},
    },
    {
        "type": "change_skill",
        "description": "Increase or decrease a character skill through the normal character-generation/progression server call.",
        "required": ["stringArg"],
        "parameters": {"stringArg": "Skill property name, such as SkillMelee or SkillSmallGuns.", "intArg": "Non-negative increases; negative decreases."},
    },
    {
        "type": "change_ability",
        "description": "Add or remove a generated ability modifier through the normal character-generation/progression server call.",
        "required": ["stringArg"],
        "parameters": {"stringArg": "Ability modifier proto id.", "intArg": "Non-negative adds; negative removes."},
    },
    {
        "type": "admin_prepare",
        "description": "Run an existing Admin.fos preparation preset on the chosen or target critter. Requires admin/moderator access and explicit allowAdmin confirmation; use only for QA setup, not player-like autonomous play.",
        "required": ["stringArg", "intArg"],
        "parameters": {"stringArg": "Preset plus optional reason as 'preset;reason=...'.", "targetId": "Optional target critter id; defaults to chosen.", "intArg": "Must be 1 to confirm admin use."},
    },
    {
        "type": "admin_teleport_to_hex",
        "description": "Teleport the admin's own critter to a map hex through the existing admin panel RPC. Requires full admin access and explicit allowAdmin confirmation.",
        "required": ["x", "y", "intArg"],
        "parameters": {"x": "Map hex X.", "y": "Map hex Y.", "stringArg": "Optional 'teleport;reason=...'.", "intArg": "Must be 1 to confirm admin use."},
    },
    {
        "type": "admin_move_to_map",
        "description": "Move the chosen or target critter to a location/map proto through the existing admin panel RPC. Requires admin/moderator access and explicit allowAdmin confirmation.",
        "required": ["stringArg", "intArg"],
        "parameters": {"stringArg": "'move_to_map;loc=<locationPid>;map=<mapPid>;reason=...'.", "targetId": "Optional target critter id; defaults to chosen.", "intArg": "Must be 1 to confirm admin use."},
    },
    {
        "type": "admin_to_faction_leader",
        "description": "Teleport the admin to a configured faction leader through the existing admin panel RPC. Requires full admin access and explicit allowAdmin confirmation.",
        "required": ["stringArg", "intArg"],
        "parameters": {"stringArg": "'faction_leader;faction=<factionKey>;reason=...'.", "intArg": "Must be 1 to confirm admin use."},
    },
    {
        "type": "admin_spawn_mob_at_target",
        "description": "Spawn a critter proto at the chosen or target critter through the existing admin panel RPC. Requires admin/moderator access and explicit allowAdmin confirmation.",
        "required": ["stringArg", "intArg"],
        "parameters": {"stringArg": "'spawn_mob;mob=<critterProtoId>;reason=...'.", "targetId": "Optional target critter id; defaults to chosen.", "intArg": "Must be 1 to confirm admin use."},
    },
    {
        "type": "admin_set_weather",
        "description": "Set or clear the current map weather through the existing admin panel RPC. Requires full admin access and explicit allowAdmin confirmation.",
        "required": ["stringArg", "intArg"],
        "parameters": {"stringArg": "'weather;weather=<weatherPid>;reason=...'; empty weather clears current map weather.", "intArg": "Must be 1 to confirm admin use."},
    },
    {
        "type": "request_roster",
        "description": "Request the current account roster state through the normal client/server path.",
        "required": [],
        "parameters": {},
    },
    {
        "type": "roster_create",
        "description": "Create a new account character at the given roster index when roster management is available.",
        "required": ["intArg"],
        "parameters": {"intArg": "Roster index to create; usually the current roster count."},
    },
    {
        "type": "roster_switch",
        "description": "Switch to an inactive account character by roster index when roster management is available.",
        "required": ["intArg"],
        "parameters": {"intArg": "Roster index from observation.account.roster.entries."},
    },
    {
        "type": "roster_delete",
        "description": "Delete an inactive account character by roster index when roster management is available.",
        "required": ["intArg"],
        "parameters": {"intArg": "Inactive roster index from observation.account.roster.entries."},
    },
    {
        "type": "close_screen",
        "description": "Close the active modal/top GUI screen through the normal client TryExit path.",
        "required": [],
        "parameters": {},
    },
    {
        "type": "set_resolution",
        "description": "QA diagnostic: set the client logical resolution through Game.SetResolution without resizing virtual host layout.",
        "required": ["x", "y"],
        "parameters": {"x": "Logical screen width.", "y": "Logical screen height."},
    },
    {
        "type": "toggle_fullscreen",
        "description": "QA diagnostic: toggle the client fullscreen state through Game.ToggleFullscreen.",
        "required": [],
        "parameters": {},
    },
    {
        "type": "mouse_click",
        "description": "Escape hatch for UI surfaces without a semantic command.",
        "required": ["screenX", "screenY", "intArg"],
        "parameters": {"screenX": "Screen X.", "screenY": "Screen Y.", "intArg": "MouseButton enum value."},
    },
    {
        "type": "key_press",
        "description": "Escape hatch for keyboard-only UI surfaces.",
        "required": ["intArg"],
        "parameters": {"intArg": "KeyCode enum value.", "stringArg": "Optional typed text."},
    },
    {
        "type": "clear_actions",
        "description": "Clear the current chosen action queue.",
        "required": [],
        "parameters": {},
    },
]

MODAL_BLOCKED_COMMAND_TYPES = {
    "move_to_hex",
    "global_move_to",
    "global_enter_interest",
    "attack_entity",
    "attack_hex",
    "pick_item",
    "pick_hex",
    "talk_to",
    "group_invite",
    "loot_critter",
    "use_item",
    "reload",
    "unload",
    "move_item",
    "drop_item",
    "toggle_sneak",
    "set_overwatch",
}

EVENT_CATALOG: list[dict[str, Any]] = [
    {"type": "bridge_started", "description": "AI bridge startup result.", "fields": ["success", "host", "port", "clientIndex"]},
    {"type": "bridge_stopped", "description": "AI bridge is stopping.", "fields": []},
    {"type": "command_completed", "description": "Queued command was consumed by the client loop.", "fields": ["commandSeq", "success", "message"]},
    {
        "type": "ai_control_profile",
        "description": "Gated AiControl script-side observation/loop profile emitted only when AiControl.ProfileObservationThresholdMs is positive.",
        "fields": ["kind", "seq", "totalMs", "hasMap", "hasChosen", "maxEntities", "parts"],
    },
    {"type": "connecting", "description": "Client started connecting to the game server.", "fields": []},
    {"type": "connecting_failed", "description": "Connection attempt failed.", "fields": []},
    {"type": "connected", "description": "Client transport connected.", "fields": []},
    {"type": "disconnected", "description": "Client transport disconnected.", "fields": []},
    {"type": "login_success", "description": "Server accepted login.", "fields": []},
    {"type": "first_connect", "description": "First client connection handshake completed in this session.", "fields": []},
    {"type": "info_message", "description": "Engine/server info message visible to the client.", "fields": ["message", "extraText"]},
    {"type": "screen_scrolled", "description": "The map/screen scrolled.", "fields": []},
    {"type": "input_lost", "description": "Client input focus was lost.", "fields": []},
    {"type": "pre_load_map", "description": "Map loading is about to begin.", "fields": ["locationProtoId", "mapProtoId", "screenSize"]},
    {"type": "map_load", "description": "Map data started loading.", "fields": []},
    {"type": "map_loaded", "description": "Map became active on the client.", "fields": []},
    {"type": "map_unloaded", "description": "Current map was unloaded.", "fields": []},
    {"type": "map_view", "description": "The client received a map view update around a hex.", "fields": ["hex"]},
    {"type": "critter_in", "description": "A critter entered client visibility.", "fields": ["critter"]},
    {"type": "critter_out", "description": "A critter left client visibility.", "fields": ["id"]},
    {"type": "critter_visibility_changed", "description": "Visibility mode changed for a known critter.", "fields": ["id", "visibility"]},
    {"type": "critter_action", "description": "Engine critter action event.", "fields": ["localCall", "critter", "action", "actionData", "contextItem"]},
    {"type": "critter_action_ex", "description": "Script-level local critter action event.", "fields": ["localCall", "critter", "action", "actionData", "contextItem"]},
    {"type": "item_map_in", "description": "Map item entered client visibility.", "fields": ["item"]},
    {"type": "item_map_out", "description": "Map item left client visibility.", "fields": ["id"]},
    {"type": "item_opened_changed", "description": "A visible item's opened/closed state changed, such as a door or container.", "fields": ["id", "protoId", "ownership", "hex", "opened", "canOpen", "hasDoor", "hasContainer", "hasLocker", "isGag", "noHighlight", "hasStaticScript"]},
    {"type": "item_inv_in", "description": "Inventory item appeared or refreshed.", "fields": ["item"]},
    {"type": "item_inv_out", "description": "Inventory item disappeared.", "fields": ["id"]},
    {"type": "custom_entity_in", "description": "Custom client entity entered replication/visibility.", "fields": ["entity"]},
    {"type": "custom_entity_out", "description": "Custom client entity left replication/visibility.", "fields": ["id"]},
    {"type": "receive_items", "description": "Server sent an item collection for loot/barter/container UI.", "fields": ["count", "context", "items"]},
    {"type": "faction_state_changed", "description": "The chosen critter's owner-visible faction membership or reputation changed.", "fields": ["faction", "pdaFactions"]},
    {"type": "level_changed", "description": "The chosen critter's public level changed; owner-visible experience progress is included for planning.", "fields": ["critterId", "level", "previousLevel", "experience", "nextLevelExperience", "experienceToNextLevel", "levelCap"]},
    {"type": "screen_size_changed", "description": "Client viewport size changed.", "fields": ["size"]},
    {"type": "screen_changed", "description": "A GUI screen was shown or hidden.", "fields": ["show", "screen", "uiPrompt"]},
    {"type": "ui_prompt_opened", "description": "A semantic GUI prompt opened and can be handled with tla_ui_answer.", "fields": ["screen", "uiPrompt"]},
    {"type": "ui_prompt_closed", "description": "A semantic GUI prompt closed.", "fields": ["screen", "uiPrompt"]},
    {"type": "console_message", "description": "Client console/message text.", "fields": ["text"]},
    {
        "type": "runtime_exception",
        "description": "Engine log exception/error surfaced by the AiControl bridge; inspect tla_logs for surrounding context.",
        "fields": ["source", "level", "category", "message", "raw", "hasStackTrace"],
    },
    {
        "type": "say_received",
        "description": "Player-visible speech was received by the client; MCP social context derives address/intent from this event.",
        "fields": ["critter", "speakerId", "speakerName", "speakerProtoId", "speakerHex", "speakerIsChosen", "listenerId", "listenerName", "distance", "sayType", "onHeadOnly", "text"],
    },
    {"type": "dialog_updated", "description": "Active dialog text/answers changed.", "fields": ["dialog"]},
    {"type": "dialog_closed", "description": "Active dialog closed.", "fields": ["dialogId"]},
    {
        "type": "quest_notification",
        "description": "Client-visible quest notification with the latest visible quest entry when available.",
        "fields": ["questId", "kind", "stage", "text", "quest"],
    },
    {
        "type": "admin_action_sent",
        "description": "AiControl sent an existing admin-panel RPC after explicit admin confirmation; inspect normal admin audit logs for authority-side details.",
        "fields": ["action", "detail", "targetId", "accessLevel", "access"],
    },
    {"type": "chosen_look_on_item", "description": "Chosen critter inspected an inventory item.", "fields": ["item"]},
    {"type": "barter_item", "description": "Barter offer item count changed.", "fields": ["myself", "itemId", "count", "traderIsPlayer"]},
    {"type": "show_statuses", "description": "Initial visible status list was received.", "fields": ["statuses"]},
    {"type": "show_status", "description": "A status became visible.", "fields": ["status"]},
    {"type": "hide_status", "description": "A status disappeared.", "fields": ["status"]},
    {"type": "prepare_to_load_scene", "description": "Client scene transition is starting.", "fields": []},
    {"type": "scene_loaded", "description": "Client scene transition completed.", "fields": []},
    {"type": "generation_ready", "description": "Character generation flow became ready.", "fields": []},
    {"type": "tutorial_finished", "description": "Tutorial step transition was requested.", "fields": ["chosenId", "current", "next"]},
    {"type": "roster_state", "description": "Account roster state was refreshed.", "fields": ["roster"]},
    {"type": "roster_action_result", "description": "Server accepted or rejected an AI roster action request.", "fields": ["action", "rosterIndex", "accepted", "message", "roster"]},
    {"type": "environment_query_result", "description": "Client-side map geometry/path/trace query completed.", "fields": ["queryId", "query", "success", "message", "result"]},
    {"type": "mouse_down", "description": "Raw input event emitted only when AiControl.CaptureRawInputEvents is enabled.", "fields": ["button", "pos"]},
    {"type": "mouse_up", "description": "Raw input event emitted only when AiControl.CaptureRawInputEvents is enabled.", "fields": ["button", "pos"]},
    {"type": "mouse_move", "description": "Raw input event emitted only when AiControl.CaptureRawInputEvents is enabled.", "fields": ["pos", "offset"]},
    {"type": "touch_tap", "description": "Raw input event emitted only when AiControl.CaptureRawInputEvents is enabled.", "fields": ["pos"]},
    {"type": "touch_double_tap", "description": "Raw input event emitted only when AiControl.CaptureRawInputEvents is enabled.", "fields": ["pos"]},
    {"type": "touch_scroll", "description": "Raw input event emitted only when AiControl.CaptureRawInputEvents is enabled.", "fields": ["pos", "offset"]},
    {"type": "touch_zoom", "description": "Raw input event emitted only when AiControl.CaptureRawInputEvents is enabled.", "fields": ["pos", "factor"]},
    {"type": "key_down", "description": "Raw input event emitted only when AiControl.CaptureRawInputEvents is enabled.", "fields": ["key", "text"]},
    {"type": "key_up", "description": "Raw input event emitted only when AiControl.CaptureRawInputEvents is enabled.", "fields": ["key"]},
]


class Bridge:
    def __init__(self, host: str, port: int, token: str, timeout: float, workspace_root: Path | None = None) -> None:
        self.host = host
        self.port = port
        self.token = token
        self.timeout = timeout
        self.next_id = 1
        self.events_cursor = 0
        self.endpoint_registry: dict[str, dict[str, Any]] = {}
        self.endpoint_cursors: dict[str, int] = {}
        self.agent_profiles: dict[str, dict[str, Any]] = {}
        self.agent_memories: dict[str, dict[str, Any]] = {}
        self.agent_decisions: dict[str, list[dict[str, Any]]] = {}
        self.agent_runtime: dict[str, dict[str, Any]] = {}
        self.next_agent_decision_id = 1
        self.selected_endpoint_id: str | None = None
        self.next_environment_query_id = initial_environment_query_id()
        self.orchestrator = Orchestrator(workspace_root or DEFAULT_WORKSPACE_ROOT)

    def request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
            file = sock.makefile("rwb")

            if self.token:
                auth_response = self._send(file, "auth", {"token": self.token})
                if auth_response.get("error"):
                    return auth_response
                if not auth_response.get("result", {}).get("authorized"):
                    return {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32001, "message": "Bridge authorization failed"},
                    }

            return self._send(file, method, params or {})

    def _send(self, file: Any, method: str, params: dict[str, Any]) -> dict[str, Any]:
        request_id = self.next_id
        self.next_id += 1
        request = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
        file.write((json.dumps(request, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8"))
        file.flush()

        line = file.readline()
        if not line:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32000, "message": "Bridge closed the connection"},
            }

        return json.loads(line.decode("utf-8"))


def bridge_owner(bridge: Any) -> Any:
    owner = bridge
    while hasattr(owner, "_bridge"):
        next_owner = getattr(owner, "_bridge")
        if next_owner is owner:
            break
        owner = next_owner
    return owner


class TargetBridge:
    def __init__(self, bridge: Any, endpoint: dict[str, Any]) -> None:
        self._bridge = bridge_owner(bridge)
        self.endpoint = register_endpoint(self._bridge, endpoint)

    @property
    def events_cursor(self) -> int:
        cursors = ensure_endpoint_cursors(self._bridge)
        endpoint_id = str(self.endpoint["endpointId"])
        # New endpoints start at 0, matching register_endpoint/select_bridge_endpoint; do not
        # seed from the owner's global cursor (that tracks the last-selected endpoint).
        return cursors.setdefault(endpoint_id, 0)

    @events_cursor.setter
    def events_cursor(self, value: int) -> None:
        cursors = ensure_endpoint_cursors(self._bridge)
        endpoint_id = str(self.endpoint["endpointId"])
        cursors[endpoint_id] = value
        selected_endpoint_id = getattr(self._bridge, "selected_endpoint_id", None)
        if selected_endpoint_id is None or selected_endpoint_id == endpoint_id:
            self._bridge.events_cursor = value

    def request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        old_host = getattr(self._bridge, "host", None)
        old_port = getattr(self._bridge, "port", None)
        old_token = getattr(self._bridge, "token", None)

        self._bridge.host = str(self.endpoint.get("host", "127.0.0.1"))
        self._bridge.port = int(self.endpoint["port"])
        self._bridge.token = str(self.endpoint.get("token", ""))

        try:
            return self._bridge.request(method, params)
        finally:
            if old_host is None:
                delattr(self._bridge, "host")
            else:
                self._bridge.host = old_host

            if old_port is None:
                delattr(self._bridge, "port")
            else:
                self._bridge.port = old_port

            if old_token is None:
                delattr(self._bridge, "token")
            else:
                self._bridge.token = old_token


@dataclass
class ManagedProcess:
    process_id: int
    role: str
    command: list[str]
    cwd: str
    process: subprocess.Popen[Any]
    started_at: float
    endpoints: list[dict[str, Any]]


class Orchestrator:
    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root
        self.next_process_id = 1
        self.processes: dict[int, ManagedProcess] = {}

    def launch(self, bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        role = str(arguments.get("role", "server_headless"))
        if role not in LAUNCH_ROLES:
            raise ValueError("role must be one of: " + ", ".join(LAUNCH_ROLES))

        binary = self.resolve_binary(role, arguments.get("binaryPath"))
        if binary is None:
            raise FileNotFoundError(f"Binary for role '{role}' was not found. Build the target or pass binaryPath.")

        cwd = self.resolve_working_directory(arguments.get("workingDirectory"))
        launch_settings = self.launch_settings(bridge, role, arguments)
        command = [str(binary), "-ApplyConfig", str(self.workspace_root / "TLA.fomain")]

        sub_config = arguments.get("subConfig")
        if isinstance(sub_config, str) and sub_config:
            command.extend(["-ApplySubConfig", sub_config])

        for key, value in launch_settings.items():
            command.extend([f"--{key}", format_setting_value(value)])

        process = subprocess.Popen(
            command,
            cwd=str(cwd),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        process_id = self.next_process_id
        self.next_process_id += 1
        endpoints = register_process_endpoints(bridge, process_id, self.build_endpoints(bridge, role, arguments, launch_settings))
        managed = ManagedProcess(process_id, role, command, str(cwd), process, time.time(), endpoints)
        self.processes[process_id] = managed

        wait_result: dict[str, Any] | None = None
        if endpoints and arguments.get("waitForBridge", True):
            wait_result = self.wait_for_endpoints(endpoints, int(arguments.get("timeoutMs", 15000)), float(arguments.get("probeIntervalMs", 250)) / 1000.0)

        selected_endpoint: dict[str, Any] | None = None
        if endpoints and arguments.get("selectFirstEndpoint", True):
            selected_endpoint = select_bridge_endpoint(bridge, endpoints[0])

        return_code = process.poll()

        return {
            "processId": process_id,
            "osPid": process.pid,
            "role": role,
            "running": return_code is None,
            "returnCode": return_code,
            "command": command,
            "cwd": str(cwd),
            "endpoints": endpoints,
            "selectedEndpoint": selected_endpoint,
            "wait": wait_result,
        }

    def list_processes(self) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []

        for process_id, managed in self.processes.items():
            return_code = managed.process.poll()
            result.append(
                {
                    "processId": process_id,
                    "osPid": managed.process.pid,
                    "role": managed.role,
                    "running": return_code is None,
                    "returnCode": return_code,
                    "startedAt": managed.started_at,
                    "cwd": managed.cwd,
                    "command": managed.command,
                    "endpoints": managed.endpoints,
                }
            )

        return result

    def stop(self, process_id: int | None, all_processes: bool, timeout_ms: int) -> dict[str, Any]:
        if all_processes:
            targets = list(self.processes.values())
        elif process_id is not None:
            if process_id not in self.processes:
                raise ValueError(f"Unknown processId: {process_id}")
            targets = [self.processes[process_id]]
        else:
            raise ValueError("Pass processId or all = true")

        stopped: list[dict[str, Any]] = []
        timeout = max(0, timeout_ms) / 1000.0

        for managed in targets:
            return_code = managed.process.poll()
            if return_code is None:
                managed.process.terminate()
                try:
                    managed.process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    managed.process.kill()
                    managed.process.wait(timeout=timeout if timeout > 0 else 5.0)

            return_code = managed.process.poll()
            stopped.append({"processId": managed.process_id, "osPid": managed.process.pid, "returnCode": return_code})
            self.processes.pop(managed.process_id, None)

        return {"stopped": stopped}

    def select_endpoint(self, bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
        endpoint: dict[str, Any]

        if "endpointId" in arguments:
            endpoint_id = str(arguments["endpointId"])
            registry = ensure_endpoint_registry(bridge)
            if endpoint_id not in registry:
                raise ValueError(f"Unknown endpointId: {endpoint_id}")
            endpoint = dict(registry[endpoint_id])
        elif "processId" in arguments:
            process_id = int(arguments["processId"])
            if process_id not in self.processes:
                raise ValueError(f"Unknown processId: {process_id}")

            endpoint_index = int(arguments.get("endpointIndex", 0))
            endpoints = self.processes[process_id].endpoints
            if endpoint_index < 0 or endpoint_index >= len(endpoints):
                raise ValueError(f"Endpoint index out of range: {endpoint_index}")
            endpoint = dict(endpoints[endpoint_index])
        else:
            if "port" not in arguments:
                raise ValueError("Pass processId + endpointIndex or direct host/port")
            endpoint = {
                "host": str(arguments.get("host", getattr(bridge, "host", "127.0.0.1"))),
                "port": int(arguments["port"]),
                "token": str(arguments.get("token", getattr(bridge, "token", ""))),
            }

        return {"selectedEndpoint": select_bridge_endpoint(bridge, endpoint)}

    def resolve_binary(self, role: str, requested_path: Any) -> Path | None:
        if isinstance(requested_path, str) and requested_path:
            path = Path(requested_path)
            if not path.is_absolute():
                path = self.workspace_root / path
            return path if path.exists() else None

        env_name = f"TLA_AI_{role.upper()}_EXE"
        env_path = os.environ.get(env_name)
        if env_path:
            path = Path(env_path)
            if not path.is_absolute():
                path = self.workspace_root / path
            return path if path.exists() else None

        name = binary_name_for_role(role)
        candidates = [
            self.workspace_root / name,
            self.workspace_root / "Binaries" / name,
            self.workspace_root / "Binaries" / "Server-Windows-win64" / name,
            self.workspace_root / "Binaries" / "Client-Windows-win64" / name,
            self.workspace_root / "Build" / "Auto" / name,
            self.workspace_root / "Build" / name,
            self.workspace_root / "TLA-Dev" / name,
            self.workspace_root / "TLA-Test" / name,
            self.workspace_root / "TLA-WinTest" / name,
        ]

        for candidate in candidates:
            if candidate.exists():
                return candidate

        for search_root in [self.workspace_root / "Binaries", self.workspace_root / "Build", self.workspace_root / "TLA-Dev", self.workspace_root / "TLA-Test", self.workspace_root / "TLA-WinTest"]:
            if not search_root.exists():
                continue
            for candidate in search_root.rglob(name):
                if candidate.is_file():
                    return candidate

        return None

    def resolve_working_directory(self, requested_path: Any) -> Path:
        if isinstance(requested_path, str) and requested_path:
            path = Path(requested_path)
            if not path.is_absolute():
                path = self.workspace_root / path
            return path
        return self.workspace_root

    def launch_settings(self, bridge: Any, role: str, arguments: dict[str, Any]) -> dict[str, Any]:
        settings = dict(arguments.get("settings") or {})
        enable_ai = bool(arguments.get("enableAiControl", True))
        accounts = normalize_launch_accounts(arguments.get("accounts"))

        if role in ("server", "server_headless"):
            client_count = int(arguments.get("clientCount", len(accounts) if accounts else 1))
            if accounts and "clientCount" in arguments and client_count < len(accounts):
                raise ValueError(
                    f"clientCount ({client_count}) must be >= number of accounts ({len(accounts)})"
                )
            settings["Server.AutoStartClientOnServer"] = client_count

        if accounts:
            settings["Auth.AutoLoginNames"] = encode_launch_setting_list([account["name"] for account in accounts])
            settings["Auth.AutoLoginPasswords"] = encode_launch_setting_list([account["password"] for account in accounts])
        if "autoLoginName" in arguments:
            settings["Auth.AutoLoginName"] = arguments["autoLoginName"]
        if "autoLoginPassword" in arguments:
            settings["Auth.AutoLoginPassword"] = arguments["autoLoginPassword"]

        if enable_ai:
            ai_control = dict(arguments.get("aiControl") or {})
            settings["AiControl.Enabled"] = True
            settings["AiControl.Host"] = ai_control.get("host", arguments.get("aiControlHost", getattr(bridge, "host", "127.0.0.1")))
            settings["AiControl.Port"] = int(ai_control.get("port", arguments.get("aiControlPort", getattr(bridge, "port", 43011))))
            settings["AiControl.Token"] = ai_control.get("token", arguments.get("aiControlToken", getattr(bridge, "token", "")))
            settings["AiControl.PortStride"] = int(ai_control.get("portStride", arguments.get("aiControlPortStride", 1)))

        return settings

    def build_endpoints(self, bridge: Any, role: str, arguments: dict[str, Any], settings: dict[str, Any]) -> list[dict[str, Any]]:
        if not as_bool(settings.get("AiControl.Enabled")):
            return []

        host = str(settings.get("AiControl.Host", getattr(bridge, "host", "127.0.0.1")))
        base_port = int(settings.get("AiControl.Port", getattr(bridge, "port", 43011)))
        token = str(settings.get("AiControl.Token", getattr(bridge, "token", "")))
        stride = max(int(settings.get("AiControl.PortStride", 1)), 1)
        count = 1

        if role in ("server", "server_headless"):
            count = max(int(settings.get("Server.AutoStartClientOnServer", arguments.get("clientCount", 1))), 0)

        return [{"host": host, "port": base_port + index * stride, "token": token, "clientIndex": index + 1} for index in range(count)]

    def wait_for_endpoints(self, endpoints: list[dict[str, Any]], timeout_ms: int, probe_interval: float) -> dict[str, Any]:
        deadline = time.monotonic() + max(0, timeout_ms) / 1000.0
        ready: list[dict[str, Any]] = []

        while True:
            ready = []
            for endpoint in endpoints:
                ready_endpoint = dict(endpoint)
                ready_endpoint["ready"] = probe_endpoint(endpoint)
                ready.append(ready_endpoint)

            if all(endpoint["ready"] for endpoint in ready):
                return {"ready": True, "endpoints": ready}
            if time.monotonic() >= deadline:
                return {"ready": False, "endpoints": ready}

            time.sleep(max(probe_interval, 0.05))


def binary_name_for_role(role: str) -> str:
    return launch_binary_name_for_role(role)


def format_setting_value(value: Any) -> str:
    return launch_format_setting_value(value)


def as_bool(value: Any) -> bool:
    return launch_as_bool(value)


def normalize_launch_accounts(accounts: Any) -> list[dict[str, str]]:
    return launch_normalize_launch_accounts(accounts)


def encode_launch_setting_list(values: list[str]) -> str:
    return launch_encode_launch_setting_list(values)


def endpoint_target_properties() -> dict[str, Any]:
    return {
        "endpointId": {"type": "string", "description": "Stable endpoint id returned by tla_launch or tla_endpoints."},
        "processId": {"type": "integer", "minimum": 1, "description": "Managed process id returned by tla_launch."},
        "endpointIndex": {"type": "integer", "minimum": 0, "description": "Endpoint index inside a managed process."},
        "host": {"type": "string", "description": "Direct bridge host for one call or selection."},
        "port": {"type": "integer", "minimum": 1, "maximum": 65535, "description": "Direct bridge port for one call or selection."},
        "token": {"type": "string", "description": "Direct bridge token for one call or selection."},
    }


def with_endpoint_target(schema: dict[str, Any]) -> dict[str, Any]:
    schema["properties"] = {**schema.get("properties", {}), **endpoint_target_properties()}
    return schema


def ensure_endpoint_registry(bridge: Any) -> dict[str, dict[str, Any]]:
    owner = bridge_owner(bridge)
    registry = getattr(owner, "endpoint_registry", None)
    if not isinstance(registry, dict):
        registry = {}
        owner.endpoint_registry = registry
    return registry


def ensure_endpoint_cursors(bridge: Any) -> dict[str, int]:
    owner = bridge_owner(bridge)
    cursors = getattr(owner, "endpoint_cursors", None)
    if not isinstance(cursors, dict):
        cursors = {}
        owner.endpoint_cursors = cursors
    return cursors


def ensure_agent_profiles(bridge: Any) -> dict[str, dict[str, Any]]:
    owner = bridge_owner(bridge)
    profiles = getattr(owner, "agent_profiles", None)
    if not isinstance(profiles, dict):
        profiles = {}
        owner.agent_profiles = profiles
    return profiles


def ensure_agent_memories(bridge: Any) -> dict[str, dict[str, Any]]:
    owner = bridge_owner(bridge)
    memories = getattr(owner, "agent_memories", None)
    if not isinstance(memories, dict):
        memories = {}
        owner.agent_memories = memories
    return memories


def ensure_agent_decisions(bridge: Any) -> dict[str, list[dict[str, Any]]]:
    owner = bridge_owner(bridge)
    decisions = getattr(owner, "agent_decisions", None)
    if not isinstance(decisions, dict):
        decisions = {}
        owner.agent_decisions = decisions
    return decisions


def ensure_agent_runtime(bridge: Any) -> dict[str, dict[str, Any]]:
    owner = bridge_owner(bridge)
    runtime = getattr(owner, "agent_runtime", None)
    if not isinstance(runtime, dict):
        runtime = {}
        owner.agent_runtime = runtime
    return runtime


def ensure_team_memories(bridge: Any) -> dict[str, dict[str, Any]]:
    owner = bridge_owner(bridge)
    memories = getattr(owner, "team_memories", None)
    if not isinstance(memories, dict):
        memories = {}
        owner.team_memories = memories
    return memories


def default_team_memory() -> dict[str, Any]:
    return {
        "notes": [],
        "facts": [],
        "bugs": [],
        "tasks": [],
        "updatedAt": None,
    }


def team_memory_key(arguments: dict[str, Any]) -> str:
    team_id = str(arguments.get("teamId", "")).strip()
    if team_id:
        return f"team:{team_id}"
    if "processId" in arguments:
        return f"process:{int(arguments['processId'])}"
    endpoint_ids = arguments.get("endpointIds")
    if isinstance(endpoint_ids, list) and endpoint_ids:
        return "endpoints:" + ",".join(sorted(str(endpoint_id) for endpoint_id in endpoint_ids))
    return "default"


def team_memory_for_key(bridge: Any, key: str) -> dict[str, Any]:
    memories = ensure_team_memories(bridge)
    memory = memories.get(key)
    if not isinstance(memory, dict):
        memory = default_team_memory()
        memories[key] = memory
    else:
        for field, default_value in default_team_memory().items():
            if field not in memory:
                memory[field] = default_value
    return memory


def team_memory_summary(memory: dict[str, Any]) -> dict[str, Any]:
    return {
        "notes": len(memory.get("notes", [])) if isinstance(memory.get("notes"), list) else 0,
        "facts": len(memory.get("facts", [])) if isinstance(memory.get("facts"), list) else 0,
        "bugs": len(memory.get("bugs", [])) if isinstance(memory.get("bugs"), list) else 0,
        "tasks": len(memory.get("tasks", [])) if isinstance(memory.get("tasks"), list) else 0,
        "updatedAt": memory.get("updatedAt"),
    }


def agent_profile_key(bridge: Any, endpoint: dict[str, Any] | None = None) -> str:
    if endpoint is None:
        endpoint = getattr(bridge, "endpoint", None)
    if isinstance(endpoint, dict) and endpoint.get("endpointId") is not None:
        return str(endpoint["endpointId"])
    return "default"


def normalize_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    if isinstance(value, list):
        result: list[str] = []
        for entry in value:
            if isinstance(entry, str) and entry.strip():
                result.append(entry.strip())
        return result
    return []


def normalized_agent_profile(arguments: dict[str, Any], existing: dict[str, Any] | None = None) -> dict[str, Any]:
    profile = {**DEFAULT_AGENT_PROFILE, **(existing or {})}
    preset_name = str(arguments.get("preset", "")).strip()
    if preset_name:
        if preset_name not in AGENT_PROFILE_PRESETS:
            raise ValueError("Unknown agent profile preset: " + preset_name)
        profile.update(AGENT_PROFILE_PRESETS[preset_name])
        profile["preset"] = preset_name

    for key in AGENT_PROFILE_TEXT_FIELDS:
        if key in arguments:
            profile[key] = str(arguments.get(key, "")).strip()

    for key in AGENT_PROFILE_LIST_FIELDS:
        if key in arguments:
            profile[key] = normalize_string_list(arguments.get(key))

    return profile


def agent_profile_for_target(bridge: Any) -> dict[str, Any]:
    profiles = ensure_agent_profiles(bridge)
    key = agent_profile_key(bridge)
    return normalized_agent_profile({}, profiles.get(key))


def set_agent_profile(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    endpoint = resolve_target_endpoint(bridge, arguments)
    profiles = ensure_agent_profiles(bridge)
    key = agent_profile_key(bridge, endpoint)
    profile_args = {key: value for key, value in arguments.items() if key in SOCIAL_PROFILE_FIELDS}
    profile = normalized_agent_profile(profile_args, profiles.get(key))
    profiles[key] = profile
    return {"endpoint": endpoint, "profile": profile}


def read_agent_profile(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    endpoint = resolve_target_endpoint(bridge, arguments)
    profiles = ensure_agent_profiles(bridge)
    key = agent_profile_key(bridge, endpoint)
    return {"endpoint": endpoint, "profile": normalized_agent_profile({}, profiles.get(key)), "presets": sorted(AGENT_PROFILE_PRESETS)}


def default_agent_memory() -> dict[str, Any]:
    return {
        "notes": [],
        "facts": [],
        "people": {},
        "places": {},
        "dialogs": {},
        "dialogChoices": [],
        "taskHints": [],
        "globalInterests": {},
        "travelHistory": [],
        "mapTransitions": [],
        "recentEvents": [],
        "visited": [],
        "visitedAreas": {},
        "recentPath": [],
        "knownHazards": {},
        "usefulItems": {},
        "interactions": [],
        "combatEncounters": [],
        "lootContainers": [],
        "activeCollection": {},
        "conversationThreads": {},
        "pendingRequests": [],
        "promises": [],
        "doNotRetry": [],
        "failedActions": [],
        "lastObservation": {},
        "lastStepAt": None,
    }


def agent_memory_for_key(bridge: Any, key: str) -> dict[str, Any]:
    memories = ensure_agent_memories(bridge)
    memory = memories.get(key)
    if not isinstance(memory, dict):
        memory = default_agent_memory()
        memories[key] = memory
    else:
        for field, default_value in default_agent_memory().items():
            if field not in memory:
                memory[field] = default_value
    return memory


def append_bounded(entries: list[Any], entry: Any, limit: int) -> None:
    entries.append(entry)
    overflow = len(entries) - limit
    if overflow > 0:
        del entries[:overflow]


def evict_oldest_dict_bounded(entries: dict[str, Any], keep_key: str, limit: int) -> None:
    # Cap dict-based memory stores by evicting the least-recently-seen entries (missing
    # lastSeenAt counts as oldest); never drop the key that was just inserted.
    if len(entries) <= limit:
        return
    overflow = len(entries) - limit
    candidates = sorted(
        (key for key in entries if key != keep_key),
        key=lambda key: entries[key].get("lastSeenAt", 0) if isinstance(entries[key], dict) else 0,
    )
    for key in candidates[:overflow]:
        del entries[key]


def append_unique_bounded(entries: list[Any], entry: dict[str, Any], limit: int, key_fields: tuple[str, ...]) -> None:
    signature = tuple(str(entry.get(field, "")) for field in key_fields)
    for index in range(len(entries) - 1, -1, -1):
        current = entries[index]
        if isinstance(current, dict) and tuple(str(current.get(field, "")) for field in key_fields) == signature:
            del entries[index]
            break
    append_bounded(entries, entry, limit)


def limited_memory_entries(entries: Any, limit: int) -> list[Any]:
    if not isinstance(entries, list):
        return []
    if limit <= 0:
        return []
    return entries[-min(limit, 200):]


def unix_ms() -> int:
    return int(time.time() * 1000)


def agent_runtime_for_key(bridge: Any, key: str) -> dict[str, Any]:
    runtime = ensure_agent_runtime(bridge)
    state = runtime.get(key)
    if not isinstance(state, dict):
        state = {
            "paused": False,
            "createdAt": unix_ms(),
            "lastTickAt": None,
            "lastDecisionId": None,
            "mode": "advisory",
        }
        runtime[key] = state
    return state


def agent_memory_summary(memory: dict[str, Any]) -> dict[str, Any]:
    return {
        "notes": len(memory.get("notes", [])) if isinstance(memory.get("notes"), list) else 0,
        "facts": len(memory.get("facts", [])) if isinstance(memory.get("facts"), list) else 0,
        "people": len(memory.get("people", {})) if isinstance(memory.get("people"), dict) else 0,
        "places": len(memory.get("places", {})) if isinstance(memory.get("places"), dict) else 0,
        "dialogs": len(memory.get("dialogs", {})) if isinstance(memory.get("dialogs"), dict) else 0,
        "dialogChoices": len(memory.get("dialogChoices", [])) if isinstance(memory.get("dialogChoices"), list) else 0,
        "taskHints": len(memory.get("taskHints", [])) if isinstance(memory.get("taskHints"), list) else 0,
        "globalInterests": len(memory.get("globalInterests", {})) if isinstance(memory.get("globalInterests"), dict) else 0,
        "travelHistory": len(memory.get("travelHistory", [])) if isinstance(memory.get("travelHistory"), list) else 0,
        "mapTransitions": len(memory.get("mapTransitions", [])) if isinstance(memory.get("mapTransitions"), list) else 0,
        "recentEvents": len(memory.get("recentEvents", [])) if isinstance(memory.get("recentEvents"), list) else 0,
        "visited": len(memory.get("visited", [])) if isinstance(memory.get("visited"), list) else 0,
        "visitedAreas": len(memory.get("visitedAreas", {})) if isinstance(memory.get("visitedAreas"), dict) else 0,
        "recentPath": len(memory.get("recentPath", [])) if isinstance(memory.get("recentPath"), list) else 0,
        "knownHazards": len(memory.get("knownHazards", {})) if isinstance(memory.get("knownHazards"), dict) else 0,
        "usefulItems": len(memory.get("usefulItems", {})) if isinstance(memory.get("usefulItems"), dict) else 0,
        "interactions": len(memory.get("interactions", [])) if isinstance(memory.get("interactions"), list) else 0,
        "combatEncounters": len(memory.get("combatEncounters", [])) if isinstance(memory.get("combatEncounters"), list) else 0,
        "lootContainers": len(memory.get("lootContainers", [])) if isinstance(memory.get("lootContainers"), list) else 0,
        "activeCollection": bool(memory.get("activeCollection", {}).get("active")) if isinstance(memory.get("activeCollection"), dict) else False,
        "conversationThreads": len(memory.get("conversationThreads", {})) if isinstance(memory.get("conversationThreads"), dict) else 0,
        "pendingRequests": len(memory.get("pendingRequests", [])) if isinstance(memory.get("pendingRequests"), list) else 0,
        "promises": len(memory.get("promises", [])) if isinstance(memory.get("promises"), list) else 0,
        "doNotRetry": len(memory.get("doNotRetry", [])) if isinstance(memory.get("doNotRetry"), list) else 0,
        "failedActions": len(memory.get("failedActions", [])) if isinstance(memory.get("failedActions"), list) else 0,
        "lastObservation": memory.get("lastObservation", {}),
        "lastStepAt": memory.get("lastStepAt"),
    }


def read_agent_memory(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    endpoint = resolve_target_endpoint(bridge, arguments)
    key = agent_profile_key(bridge, endpoint)
    memory = agent_memory_for_key(bridge, key)
    result = {"endpoint": endpoint, "key": key, "summary": agent_memory_summary(memory), "memory": memory}
    if bool(arguments.get("includeDecisions", False)):
        result["decisions"] = agent_decisions_for_key(bridge, key, int(arguments.get("limit", 20)))
    return result


def remember_agent_memory(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    endpoint = resolve_target_endpoint(bridge, arguments)
    key = agent_profile_key(bridge, endpoint)
    memory = agent_memory_for_key(bridge, key)
    kind = str(arguments.get("kind", "note")).strip() or "note"
    now = unix_ms()
    properties = arguments.get("properties") if isinstance(arguments.get("properties"), dict) else {}

    if kind in {"note", "fact", "failed_action"}:
        text = str(arguments.get("text", "")).strip()
        if not text:
            raise ValueError("text is required for note, fact, and failed_action memory")
        entry = {
            "time": now,
            "text": text,
            "tags": normalize_string_list(arguments.get("tags")),
            "source": str(arguments.get("source", "manual")),
            "properties": properties,
        }
        target_list = {"note": "notes", "fact": "facts", "failed_action": "failedActions"}[kind]
        append_bounded(memory[target_list], entry, 200)
        return {"endpoint": endpoint, "key": key, "kind": kind, "entry": entry, "summary": agent_memory_summary(memory)}

    if kind in {"person", "place", "dialog"}:
        memory_key = str(arguments.get("key", "")).strip()
        if kind == "dialog" and not memory_key:
            memory_key = dialog_memory_key({"dialogId": arguments.get("dialogId"), "talkerId": arguments.get("talkerId")})
        if not memory_key:
            raise ValueError("key is required for person, place, and dialog memory")
        bucket = {"person": "people", "place": "places", "dialog": "dialogs"}[kind]
        entry = dict(memory[bucket].get(memory_key, {})) if isinstance(memory[bucket].get(memory_key), dict) else {}
        entry.update(properties)
        if kind == "dialog":
            if "dialogId" in arguments:
                entry["dialogId"] = arguments.get("dialogId")
            if "talkerId" in arguments:
                entry["talkerId"] = arguments.get("talkerId")
        if "text" in arguments:
            entry["note"] = str(arguments.get("text", "")).strip()
        entry["key"] = memory_key
        entry["updatedAt"] = now
        memory[bucket][memory_key] = entry
        return {"endpoint": endpoint, "key": key, "kind": kind, "entry": entry, "summary": agent_memory_summary(memory)}

    if kind == "task_hint":
        text = str(arguments.get("text", "")).strip()
        if not text and not properties:
            raise ValueError("text or properties is required for task_hint memory")
        entry = {
            "time": now,
            "text": text,
            "source": str(arguments.get("source", "manual")),
            "tags": normalize_string_list(arguments.get("tags")),
            "properties": properties,
        }
        append_unique_bounded(memory["taskHints"], entry, 200, ("text", "source"))
        return {"endpoint": endpoint, "key": key, "kind": kind, "entry": entry, "summary": agent_memory_summary(memory)}

    raise ValueError("kind must be one of: note, fact, failed_action, person, place, dialog, task_hint")


def forget_agent_memory(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    endpoint = resolve_target_endpoint(bridge, arguments)
    key = agent_profile_key(bridge, endpoint)
    memories = ensure_agent_memories(bridge)
    kind = str(arguments.get("kind", "all")).strip() or "all"

    if kind == "all":
        memories[key] = default_agent_memory()
        ensure_agent_decisions(bridge)[key] = []
        return {"endpoint": endpoint, "key": key, "cleared": "all", "summary": agent_memory_summary(memories[key])}

    memory = agent_memory_for_key(bridge, key)
    if kind in {
        "notes",
        "facts",
        "recentEvents",
        "visited",
        "recentPath",
        "failedActions",
        "interactions",
        "combatEncounters",
        "lootContainers",
        "pendingRequests",
        "promises",
        "doNotRetry",
        "dialogChoices",
        "taskHints",
        "travelHistory",
        "mapTransitions",
    }:
        memory[kind] = []
    elif kind in {"people", "places", "dialogs", "globalInterests", "visitedAreas", "knownHazards", "usefulItems", "activeCollection", "conversationThreads"}:
        memory_key = str(arguments.get("key", "")).strip()
        if memory_key:
            memory[kind].pop(memory_key, None)
        else:
            memory[kind] = {}
    elif kind == "decisions":
        ensure_agent_decisions(bridge)[key] = []
    else:
        raise ValueError("kind must be all, notes, facts, people, places, dialogs, globalInterests, recentEvents, visited, visitedAreas, recentPath, knownHazards, usefulItems, interactions, combatEncounters, lootContainers, activeCollection, conversationThreads, pendingRequests, promises, doNotRetry, failedActions, dialogChoices, taskHints, travelHistory, mapTransitions, or decisions")

    return {"endpoint": endpoint, "key": key, "cleared": kind, "summary": agent_memory_summary(memory)}


def bridge_workspace_root(bridge: Any) -> Path:
    owner = bridge_owner(bridge)
    orchestrator = getattr(owner, "orchestrator", None)
    workspace_root = getattr(orchestrator, "workspace_root", None)
    if workspace_root is not None:
        return Path(workspace_root)
    return DEFAULT_WORKSPACE_ROOT


def agent_memory_directory(bridge: Any) -> Path:
    return bridge_workspace_root(bridge) / "Workspace" / "AiMemory"


def agent_memory_file_stem(arguments: dict[str, Any], key: str) -> str:
    name = str(arguments.get("name", "")).strip() or key
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("._-")
    return stem or "default"


def agent_memory_file_path(bridge: Any, arguments: dict[str, Any], key: str) -> Path:
    return agent_memory_directory(bridge) / (agent_memory_file_stem(arguments, key) + ".json")


def normalized_loaded_agent_memory(payload: Any) -> dict[str, Any]:
    source = payload.get("memory") if isinstance(payload, dict) and isinstance(payload.get("memory"), dict) else payload
    if not isinstance(source, dict):
        raise ValueError("memory file must contain an object or a {memory: object} payload")

    memory = default_agent_memory()
    for field, default_value in memory.items():
        value = source.get(field, default_value)
        if isinstance(default_value, list) and isinstance(value, list):
            memory[field] = value
        elif isinstance(default_value, dict) and isinstance(value, dict):
            memory[field] = value
        elif default_value is None or not isinstance(default_value, (list, dict)):
            memory[field] = value
    return memory


def save_agent_memory(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    endpoint = resolve_target_endpoint(bridge, arguments)
    key = agent_profile_key(bridge, endpoint)
    memory = agent_memory_for_key(bridge, key)
    directory = agent_memory_directory(bridge)
    directory.mkdir(parents=True, exist_ok=True)
    path = agent_memory_file_path(bridge, arguments, key)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "savedAt": unix_ms(),
        "key": key,
        "name": str(arguments.get("name", "")).strip(),
        "memory": memory,
    }
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(path)
    return {"endpoint": endpoint, "key": key, "path": str(path), "summary": agent_memory_summary(memory), "savedAt": payload["savedAt"]}


def load_agent_memory(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    endpoint = resolve_target_endpoint(bridge, arguments)
    key = agent_profile_key(bridge, endpoint)
    path = agent_memory_file_path(bridge, arguments, key)
    if not path.exists():
        raise ValueError(f"agent memory file not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"agent memory file is not valid JSON: {exc}") from exc
    memory = normalized_loaded_agent_memory(payload)
    ensure_agent_memories(bridge)[key] = memory
    return {"endpoint": endpoint, "key": key, "path": str(path), "summary": agent_memory_summary(memory), "loadedAt": unix_ms()}


def list_agent_memory_files(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    directory = agent_memory_directory(bridge)
    files: list[dict[str, Any]] = []
    if directory.exists():
        for path in sorted(directory.glob("*.json")):
            entry: dict[str, Any] = {"name": path.stem, "path": str(path), "size": path.stat().st_size}
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(payload, dict):
                    entry["key"] = payload.get("key")
                    entry["savedAt"] = payload.get("savedAt")
                    if isinstance(payload.get("memory"), dict):
                        entry["summary"] = agent_memory_summary(normalized_loaded_agent_memory(payload))
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                entry["error"] = str(exc)
            files.append(entry)
    return {"directory": str(directory), "files": files}


def agent_known_people(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    endpoint = resolve_target_endpoint(bridge, arguments)
    key = agent_profile_key(bridge, endpoint)
    people = agent_memory_for_key(bridge, key).get("people", {})
    return {"endpoint": endpoint, "key": key, "people": people if isinstance(people, dict) else {}}


def agent_known_places(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    endpoint = resolve_target_endpoint(bridge, arguments)
    key = agent_profile_key(bridge, endpoint)
    places = agent_memory_for_key(bridge, key).get("places", {})
    return {"endpoint": endpoint, "key": key, "places": places if isinstance(places, dict) else {}}


def agent_known_dialogs(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    endpoint = resolve_target_endpoint(bridge, arguments)
    key = agent_profile_key(bridge, endpoint)
    memory = agent_memory_for_key(bridge, key)
    return {
        "endpoint": endpoint,
        "key": key,
        "dialogs": memory.get("dialogs", {}) if isinstance(memory.get("dialogs"), dict) else {},
        "choices": limited_memory_entries(memory.get("dialogChoices"), int(arguments.get("limit", 20))),
    }


def endpoint_direct_id(endpoint: dict[str, Any]) -> str:
    return f"direct:{endpoint.get('host', '127.0.0.1')}:{int(endpoint['port'])}"


def normalize_endpoint(endpoint: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(endpoint)
    normalized["host"] = str(normalized.get("host", "127.0.0.1"))
    normalized["port"] = int(normalized["port"])
    normalized["token"] = str(normalized.get("token", ""))
    normalized["endpointId"] = str(normalized.get("endpointId") or endpoint_direct_id(normalized))
    return normalized


def register_endpoint(bridge: Any, endpoint: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_endpoint(endpoint)
    registry = ensure_endpoint_registry(bridge)
    cursors = ensure_endpoint_cursors(bridge)
    endpoint_id = str(normalized["endpointId"])
    registry[endpoint_id] = normalized
    cursors.setdefault(endpoint_id, 0)
    return normalized


def register_process_endpoints(bridge: Any, process_id: int, endpoints: list[dict[str, Any]]) -> list[dict[str, Any]]:
    registered: list[dict[str, Any]] = []
    for index, endpoint in enumerate(endpoints):
        endpoint_with_id = dict(endpoint)
        endpoint_with_id["processId"] = process_id
        endpoint_with_id["endpointIndex"] = index
        endpoint_with_id["endpointId"] = f"p{process_id}:e{index}"
        registered.append(register_endpoint(bridge, endpoint_with_id))
    return registered


def current_bridge_endpoint(bridge: Any) -> dict[str, Any]:
    selected_endpoint_id = getattr(bridge, "selected_endpoint_id", None)
    endpoint = normalize_endpoint(
        {
            "endpointId": selected_endpoint_id or None,
            "host": getattr(bridge, "host", "127.0.0.1"),
            "port": int(getattr(bridge, "port", 43011)),
            "token": getattr(bridge, "token", ""),
        },
    )
    endpoint_id = str(endpoint["endpointId"])
    cursors = ensure_endpoint_cursors(bridge)
    had_cursor = endpoint_id in cursors
    registered = register_endpoint(bridge, endpoint)
    if not had_cursor:
        cursors[endpoint_id] = int(getattr(bridge, "events_cursor", 0))
    return registered


def process_endpoint(bridge: Any, process_id: int, endpoint_index: int) -> dict[str, Any]:
    orchestrator = require_orchestrator(bridge)
    if process_id not in orchestrator.processes:
        raise ValueError(f"Unknown processId: {process_id}")

    endpoints = orchestrator.processes[process_id].endpoints
    if endpoint_index < 0 or endpoint_index >= len(endpoints):
        raise ValueError(f"Endpoint index out of range: {endpoint_index}")
    return register_endpoint(bridge, endpoints[endpoint_index])


def resolve_target_endpoint(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    registry = ensure_endpoint_registry(bridge)

    if "endpointId" in arguments:
        endpoint_id = str(arguments["endpointId"])
        if endpoint_id not in registry:
            raise ValueError(f"Unknown endpointId: {endpoint_id}")
        return register_endpoint(bridge, registry[endpoint_id])

    if "processId" in arguments:
        return process_endpoint(bridge, int(arguments["processId"]), int(arguments.get("endpointIndex", 0)))

    if "port" in arguments:
        return register_endpoint(
            bridge,
            {
                "host": str(arguments.get("host", getattr(bridge, "host", "127.0.0.1"))),
                "port": int(arguments["port"]),
                "token": str(arguments.get("token", getattr(bridge, "token", ""))),
            },
        )

    selected_endpoint_id = getattr(bridge, "selected_endpoint_id", None)
    if isinstance(selected_endpoint_id, str) and selected_endpoint_id in registry:
        return register_endpoint(bridge, registry[selected_endpoint_id])

    return current_bridge_endpoint(bridge)


def target_bridge(bridge: Any, arguments: dict[str, Any]) -> TargetBridge:
    return TargetBridge(bridge, resolve_target_endpoint(bridge, arguments))


def endpoint_summary(bridge: Any, probe: bool = False) -> dict[str, Any]:
    if not ensure_endpoint_registry(bridge):
        current_bridge_endpoint(bridge)
    selected_endpoint_id = getattr(bridge, "selected_endpoint_id", None)
    endpoints: list[dict[str, Any]] = []

    for endpoint in ensure_endpoint_registry(bridge).values():
        entry = dict(endpoint)
        entry["selected"] = endpoint.get("endpointId") == selected_endpoint_id
        entry["cursor"] = ensure_endpoint_cursors(bridge).get(str(endpoint["endpointId"]), 0)
        if probe:
            entry["ready"] = probe_endpoint(endpoint)
        endpoints.append(entry)

    return {"selectedEndpointId": selected_endpoint_id, "endpoints": endpoints}


def status_all_endpoints(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    probe = bool(arguments.get("probe", True))
    endpoints = resolve_status_all_endpoints(bridge, arguments)
    results: list[dict[str, Any]] = []

    for endpoint in endpoints:
        entry = {"endpoint": dict(endpoint), "ready": False}
        if not probe:
            results.append(entry)
            continue

        try:
            response = TargetBridge(bridge, endpoint).request("status")
        except OSError as exc:
            entry["error"] = str(exc)
        else:
            if "error" in response:
                entry["error"] = response["error"]
            else:
                entry["ready"] = True
                entry["status"] = response.get("result", response)
        results.append(entry)

    return {"selectedEndpointId": getattr(bridge, "selected_endpoint_id", None), "endpoints": results}


def resolve_status_all_endpoints(bridge: Any, arguments: dict[str, Any]) -> list[dict[str, Any]]:
    if "processId" in arguments or "endpointIds" in arguments:
        return resolve_wait_all_endpoints(bridge, arguments)

    if not ensure_endpoint_registry(bridge):
        current_bridge_endpoint(bridge)

    return [register_endpoint(bridge, endpoint) for endpoint in ensure_endpoint_registry(bridge).values()]


def wait_ready(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    selected_bridge = target_bridge(bridge, arguments)
    result = wait_endpoint_ready(selected_bridge, arguments)
    return {"jsonrpc": "2.0", "id": None, "result": result}


def wait_all_ready(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    endpoints = resolve_wait_all_endpoints(bridge, arguments)
    timeout_ms = clamp_int(arguments.get("timeoutMs", 60000), 0, 180000)
    poll_interval_ms = clamp_int(arguments.get("pollIntervalMs", 250), 0, 5000)
    deadline = time.monotonic() + timeout_ms / 1000.0
    states: dict[str, dict[str, Any]] = {str(endpoint["endpointId"]): {"endpoint": dict(endpoint), "ready": False, "attempts": 0} for endpoint in endpoints}

    while True:
        for endpoint in endpoints:
            endpoint_id = str(endpoint["endpointId"])
            if states[endpoint_id].get("ready"):
                continue

            attempts = int(states[endpoint_id].get("attempts", 0))
            state = poll_endpoint_ready(TargetBridge(bridge, endpoint), arguments)
            state["attempts"] = attempts + 1
            states[endpoint_id] = {"endpoint": dict(endpoint), **state}

        if all(state.get("ready") for state in states.values()):
            return {
                "jsonrpc": "2.0",
                "id": None,
                "result": {
                    "ready": True,
                    "timedOut": False,
                    "endpoints": list(states.values()),
                },
            }

        if time.monotonic() >= deadline:
            return {
                "jsonrpc": "2.0",
                "id": None,
                "result": {
                    "ready": False,
                    "timedOut": True,
                    "endpoints": list(states.values()),
                },
            }

        if poll_interval_ms > 0:
            time.sleep(poll_interval_ms / 1000.0)


def wait_endpoint_ready(bridge: Bridge, arguments: dict[str, Any]) -> dict[str, Any]:
    timeout_ms = clamp_int(arguments.get("timeoutMs", 60000), 0, 180000)
    poll_interval_ms = clamp_int(arguments.get("pollIntervalMs", 250), 0, 5000)
    deadline = time.monotonic() + timeout_ms / 1000.0
    last_state: dict[str, Any] = {"ready": False, "missing": readiness_requirement_names(arguments), "attempts": 0}

    while True:
        state = poll_endpoint_ready(bridge, arguments)
        state["attempts"] = int(last_state.get("attempts", 0)) + 1
        last_state = state

        if state["ready"]:
            return {"timedOut": False, **state}

        if time.monotonic() >= deadline:
            return {"timedOut": True, **state}

        if poll_interval_ms > 0:
            time.sleep(poll_interval_ms / 1000.0)


def poll_endpoint_ready(bridge: Bridge, arguments: dict[str, Any]) -> dict[str, Any]:
    try:
        response = bridge.request("observe")
    except OSError as exc:
        return {"ready": False, "missing": readiness_requirement_names(arguments), "error": str(exc), "observation": {}}

    if "error" in response:
        return {"ready": False, "missing": readiness_requirement_names(arguments), "error": response["error"], "observation": {}}

    payload = response.get("result", response)
    observation = unwrap_observation_payload(payload)
    missing = readiness_missing(observation, arguments)
    result: dict[str, Any] = {
        "ready": not missing,
        "missing": missing,
        "observation": observation if bool(arguments.get("includeObservation", True)) else {},
    }

    if isinstance(payload, dict) and "observationSeq" in payload:
        result["observationSeq"] = payload["observationSeq"]

    return result


def resolve_wait_all_endpoints(bridge: Any, arguments: dict[str, Any]) -> list[dict[str, Any]]:
    registry = ensure_endpoint_registry(bridge)

    endpoint_ids = arguments.get("endpointIds")
    if isinstance(endpoint_ids, list):
        endpoints: list[dict[str, Any]] = []
        for endpoint_id_value in endpoint_ids:
            endpoint_id = str(endpoint_id_value)
            if endpoint_id not in registry:
                raise ValueError(f"Unknown endpointId: {endpoint_id}")
            endpoints.append(register_endpoint(bridge, registry[endpoint_id]))
        return endpoints

    if "processId" in arguments:
        orchestrator = require_orchestrator(bridge)
        process_id = int(arguments["processId"])
        if process_id not in orchestrator.processes:
            raise ValueError(f"Unknown processId: {process_id}")
        return [register_endpoint(bridge, endpoint) for endpoint in orchestrator.processes[process_id].endpoints]

    if not registry:
        current_bridge_endpoint(bridge)

    return [register_endpoint(bridge, endpoint) for endpoint in ensure_endpoint_registry(bridge).values()]


def team_status_payload(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    endpoints = resolve_wait_all_endpoints(bridge, arguments)
    include_observation = bool(arguments.get("includeObservation", True))
    probe_status = bool(arguments.get("probeStatus", False))
    memory_key = team_memory_key(arguments)
    team_memory = team_memory_for_key(bridge, memory_key)
    members: list[dict[str, Any]] = []

    for endpoint in endpoints:
        selected_bridge = TargetBridge(bridge, endpoint)
        key = agent_profile_key(selected_bridge)
        member: dict[str, Any] = {
            "endpoint": dict(endpoint),
            "key": key,
            "profile": normalized_agent_profile({}, ensure_agent_profiles(selected_bridge).get(key)),
            "runtime": agent_runtime_for_key(selected_bridge, key),
            "memory": agent_memory_summary(agent_memory_for_key(selected_bridge, key)),
        }

        if probe_status:
            try:
                status_response = selected_bridge.request("status")
            except OSError as exc:
                member["statusError"] = str(exc)
            else:
                if "error" in status_response:
                    member["statusError"] = status_response["error"]
                else:
                    member["status"] = status_response.get("result", status_response)

        if include_observation:
            try:
                observe_response = selected_bridge.request("observe")
            except OSError as exc:
                member["observationError"] = str(exc)
            else:
                if "error" in observe_response:
                    member["observationError"] = observe_response["error"]
                else:
                    observation_payload = observe_response.get("result", observe_response)
                    observation = unwrap_observation_payload(observation_payload)
                    member["observationSeq"] = observation_payload.get("observationSeq") if isinstance(observation_payload, dict) else observation.get("seq")
                    member["observation"] = compact_observation_summary(observation)
                    member["area"] = area_summary_payload(observation)

        members.append(member)

    return {
        "selectedEndpointId": getattr(bridge_owner(bridge), "selected_endpoint_id", None),
        "teamMemoryKey": memory_key,
        "teamMemory": team_memory_summary(team_memory),
        "members": members,
        "counts": {"members": len(members)},
        "guidance": "Team status is MCP-side orchestration context. Profiles and memory are endpoint-local; observations are normal client-visible snapshots.",
    }


def team_status_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": None, "result": team_status_payload(bridge, arguments)}


def read_team_memory_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    key = team_memory_key(arguments)
    memory = team_memory_for_key(bridge, key)
    return {
        "jsonrpc": "2.0",
        "id": None,
        "result": {
            "key": key,
            "summary": team_memory_summary(memory),
            "memory": memory,
            "guidance": "Team memory is adapter-local QA/coordination context and must be populated from visible observations, explicit host notes, or MCP results.",
        },
    }


def remember_team_memory_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    key = team_memory_key(arguments)
    memory = team_memory_for_key(bridge, key)
    kind = str(arguments.get("kind", "note")).strip() or "note"
    if kind not in {"note", "fact", "bug", "task"}:
        raise ValueError("kind must be note, fact, bug, or task")
    text = str(arguments.get("text", "")).strip()
    properties = arguments.get("properties") if isinstance(arguments.get("properties"), dict) else {}
    if not text and not properties:
        raise ValueError("text or properties is required")

    now = unix_ms()
    entry = {
        "time": now,
        "kind": kind,
        "text": text,
        "source": str(arguments.get("source", "manual")),
        "tags": normalize_string_list(arguments.get("tags")),
        "endpointId": arguments.get("endpointId"),
        "severity": str(arguments.get("severity", "")).strip(),
        "properties": properties,
    }
    entry = {field: value for field, value in entry.items() if value not in (None, "")}
    bucket = {"note": "notes", "fact": "facts", "bug": "bugs", "task": "tasks"}[kind]
    append_unique_bounded(ensure_memory_list(memory, bucket), entry, 300, ("kind", "text", "endpointId", "source"))
    memory["updatedAt"] = now
    return {"jsonrpc": "2.0", "id": None, "result": {"key": key, "kind": kind, "entry": entry, "summary": team_memory_summary(memory)}}


def forget_team_memory_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    key = team_memory_key(arguments)
    memories = ensure_team_memories(bridge)
    kind = str(arguments.get("kind", "all")).strip() or "all"
    if kind == "all":
        memories[key] = default_team_memory()
        return {"jsonrpc": "2.0", "id": None, "result": {"key": key, "cleared": "all", "summary": team_memory_summary(memories[key])}}
    if kind not in {"notes", "facts", "bugs", "tasks"}:
        raise ValueError("kind must be all, notes, facts, bugs, or tasks")
    memory = team_memory_for_key(bridge, key)
    memory[kind] = []
    memory["updatedAt"] = unix_ms()
    return {"jsonrpc": "2.0", "id": None, "result": {"key": key, "cleared": kind, "summary": team_memory_summary(memory)}}


def team_assignment_target(bridge: Any, arguments: dict[str, Any], assignment: dict[str, Any], index: int, endpoints: list[dict[str, Any]]) -> dict[str, Any]:
    target = dict(assignment)
    if "index" in target and "endpointIndex" not in target:
        target["endpointIndex"] = target["index"]
    if "processId" in arguments and "processId" not in target and "endpointId" not in target and "port" not in target:
        target["processId"] = arguments["processId"]
    has_target = any(key in target for key in ENDPOINT_TARGET_ARGUMENTS)
    if not has_target and "endpointIds" in arguments and isinstance(arguments.get("endpointIds"), list) and index < len(arguments["endpointIds"]):
        target["endpointId"] = str(arguments["endpointIds"][index])
        has_target = True
    if not has_target and "processId" in arguments:
        target["processId"] = arguments["processId"]
        target.setdefault("endpointIndex", index)
        has_target = True
    if not has_target and index < len(endpoints):
        target["endpointId"] = str(endpoints[index]["endpointId"])
    return target


def team_assign_roles_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    assignments = arguments.get("assignments")
    if not isinstance(assignments, list) or not assignments:
        raise ValueError("assignments must be a non-empty array")

    endpoints = resolve_wait_all_endpoints(bridge, arguments)
    results: list[dict[str, Any]] = []
    for index, assignment_value in enumerate(assignments):
        if not isinstance(assignment_value, dict):
            raise ValueError(f"assignments[{index}] must be an object")
        target = team_assignment_target(bridge, arguments, assignment_value, index, endpoints)
        profile_args = {key: value for key, value in target.items() if key in SOCIAL_PROFILE_FIELDS or key in ENDPOINT_TARGET_ARGUMENTS}
        result = set_agent_profile(bridge, profile_args)
        results.append({"index": index, "key": agent_profile_key(bridge, result.get("endpoint") if isinstance(result.get("endpoint"), dict) else None), **result})

    return {"jsonrpc": "2.0", "id": None, "result": {"assignments": results, "team": team_status_payload(bridge, {**arguments, "includeObservation": False, "probeStatus": False})}}


def team_member_endpoint_id(member: dict[str, Any]) -> str:
    endpoint = member.get("endpoint") if isinstance(member.get("endpoint"), dict) else {}
    return str(endpoint.get("endpointId", ""))


def team_member_display(member: dict[str, Any]) -> str:
    profile = member.get("profile") if isinstance(member.get("profile"), dict) else {}
    endpoint_id = team_member_endpoint_id(member)
    return str(profile.get("displayName") or profile.get("name") or endpoint_id)


def team_member_role(member: dict[str, Any], index: int) -> str:
    profile = member.get("profile") if isinstance(member.get("profile"), dict) else {}
    role = str(profile.get("role") or "").strip()
    if role:
        return role
    preset = str(profile.get("preset") or "").strip()
    if preset and preset != "custom":
        return preset
    return "leader" if index == 0 else "follower"


def team_leader_member(members: list[dict[str, Any]], leader_endpoint_id: str) -> dict[str, Any] | None:
    if leader_endpoint_id:
        for member in members:
            if team_member_endpoint_id(member) == leader_endpoint_id:
                return member
    return members[0] if members else None


def same_map_area(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_map = left.get("map") if isinstance(left.get("map"), dict) else {}
    right_map = right.get("map") if isinstance(right.get("map"), dict) else {}
    if left_map.get("id") is not None and right_map.get("id") is not None:
        return str(left_map.get("id")) == str(right_map.get("id"))
    if left_map.get("protoId") is not None and right_map.get("protoId") is not None:
        return str(left_map.get("protoId")) == str(right_map.get("protoId"))
    return False


def follow_path_validation(bridge: Any, follower_endpoint_id: str, from_hex: Any, to_hex: Any, arguments: dict[str, Any]) -> dict[str, Any] | None:
    if not bool(arguments.get("validatePath", False)):
        return None
    if not isinstance(from_hex, dict) or not isinstance(to_hex, dict):
        return {"completed": False, "blockedBy": ["missing follower or leader hex"], "guidance": "Path validation needs both source and target hexes."}

    query_arguments = {
        "endpointId": follower_endpoint_id,
        "fromX": get_hex_value(from_hex, "x"),
        "fromY": get_hex_value(from_hex, "y"),
        "toX": get_hex_value(to_hex, "x"),
        "toY": get_hex_value(to_hex, "y"),
        "cut": int(arguments.get("pathCut", arguments.get("followDistance", 0))),
        "includeDirections": bool(arguments.get("includeDirections", False)),
        "maxDirections": int(arguments.get("maxDirections", 40)),
        "timeoutMs": int(arguments.get("pathTimeoutMs", arguments.get("timeoutMs", DEFAULT_ENVIRONMENT_QUERY_TIMEOUT_MS))),
        "pollIntervalMs": int(arguments.get("pollIntervalMs", 100)),
        "limit": int(arguments.get("limit", 100)),
    }
    response = environment_query(target_bridge(bridge, query_arguments), "path", query_arguments)
    if "error" in response:
        return {"completed": False, "error": response["error"]}
    result = response.get("result", response)
    route = result.get("result") if isinstance(result, dict) and isinstance(result.get("result"), dict) else {}
    return {
        "completed": bool(result.get("completed")) if isinstance(result, dict) else False,
        "timedOut": bool(result.get("timedOut")) if isinstance(result, dict) else False,
        "reachable": route.get("reachable"),
        "pathLength": route.get("pathLength"),
        "directDistance": route.get("directDistance"),
        "fromMovable": route.get("fromMovable"),
        "toMovable": route.get("toMovable"),
        "queryId": result.get("queryId") if isinstance(result, dict) else None,
    }


def apply_path_validation_to_plan(bridge: Any, plan: dict[str, Any], from_hex: Any, to_hex: Any, arguments: dict[str, Any]) -> None:
    if plan.get("tool") != "tla_move_to_hex":
        return
    endpoint_id = str(plan.get("endpointId") or (plan.get("arguments") if isinstance(plan.get("arguments"), dict) else {}).get("endpointId", ""))
    validation = follow_path_validation(bridge, endpoint_id, from_hex, to_hex, arguments)
    if validation is None:
        return
    plan["path"] = validation
    if validation.get("completed") and validation.get("reachable") is False:
        plan["step"] = "blocked"
        plan["tool"] = None
        plan["blockedBy"] = ["path unreachable"]
        plan["reason"] = "validated follower path is unreachable"


def team_rendezvous_payload(bridge: Any, members: list[dict[str, Any]], leader_endpoint_id: str, arguments: dict[str, Any]) -> dict[str, Any]:
    leader = team_leader_member(members, leader_endpoint_id)
    if leader is None:
        return {"available": False, "leaderEndpointId": None, "target": None, "members": [], "guidance": "No team endpoints are registered."}

    leader_area = leader.get("area") if isinstance(leader.get("area"), dict) else {}
    leader_chosen = leader_area.get("chosen") if isinstance(leader_area.get("chosen"), dict) else {}
    leader_global = leader_area.get("globalMap") if isinstance(leader_area.get("globalMap"), dict) else {}
    mode = str(leader_area.get("mode") or "")
    target: dict[str, Any] = {
        "leaderEndpointId": team_member_endpoint_id(leader),
        "leader": team_member_display(leader),
        "mode": mode,
        "map": leader_area.get("map"),
        "hex": leader_chosen.get("hex"),
        "globalPos": leader_global.get("pos"),
    }
    member_plans: list[dict[str, Any]] = []

    for member in members:
        endpoint_id = team_member_endpoint_id(member)
        area = member.get("area") if isinstance(member.get("area"), dict) else {}
        plan: dict[str, Any] = {"endpointId": endpoint_id, "name": team_member_display(member)}
        if endpoint_id == target["leaderEndpointId"]:
            plan.update({"role": "leader", "step": "hold", "reason": "leader defines rendezvous target"})
        elif mode == "map" and area.get("mode") == "map" and same_map_area(area, leader_area) and isinstance(target.get("hex"), dict):
            plan.update({"role": "follower", "step": "move", "tool": "tla_move_to_hex", "arguments": {"endpointId": endpoint_id, "x": get_hex_value(target["hex"], "x"), "y": get_hex_value(target["hex"], "y")}, "reason": "same visible map as leader"})
            chosen = area.get("chosen") if isinstance(area.get("chosen"), dict) else {}
            apply_path_validation_to_plan(bridge, plan, chosen.get("hex"), target.get("hex"), arguments)
        elif mode == "global" and area.get("mode") == "global" and isinstance(target.get("globalPos"), dict):
            plan.update({"role": "follower", "step": "global_move", "tool": "tla_global_move_to", "arguments": {"endpointId": endpoint_id, "x": get_hex_value(target["globalPos"], "x"), "y": get_hex_value(target["globalPos"], "y")}, "reason": "same global-map mode as leader"})
        else:
            plan.update({"role": "follower", "step": "blocked", "blockedBy": ["missing observation or different map/global mode"], "reason": "rendezvous needs both clients in a comparable visible area"})
        member_plans.append(plan)

    return {
        "available": True,
        "leaderEndpointId": target["leaderEndpointId"],
        "target": target,
        "members": member_plans,
        "guidance": "Rendezvous is an advisory plan only. Execute returned typed tools per endpoint after refreshing observations.",
    }


def team_plan_payload(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    status = team_status_payload(bridge, arguments)
    members = status.get("members") if isinstance(status.get("members"), list) else []
    role_plan = [
        {
            "endpointId": team_member_endpoint_id(member),
            "name": team_member_display(member),
            "role": team_member_role(member, index),
            "profilePreset": (member.get("profile") if isinstance(member.get("profile"), dict) else {}).get("preset"),
            "memory": member.get("memory"),
            "area": member.get("area"),
        }
        for index, member in enumerate(members)
    ]
    leader_endpoint_id = str(arguments.get("leaderEndpointId", ""))
    rendezvous = team_rendezvous_payload(bridge, members, leader_endpoint_id, arguments)
    return {
        "selectedEndpointId": status.get("selectedEndpointId"),
        "members": role_plan,
        "rendezvous": rendezvous,
        "guidance": "Team plan is MCP-side advice for coordinating normal endpoints; it does not execute commands or share hidden state.",
    }


def team_plan_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": None, "result": team_plan_payload(bridge, arguments)}


def group_rendezvous_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    plan = team_plan_payload(bridge, arguments)
    return {"jsonrpc": "2.0", "id": None, "result": {"selectedEndpointId": plan.get("selectedEndpointId"), "rendezvous": plan.get("rendezvous"), "members": plan.get("members", [])}}


def endpoint_by_id(bridge: Any, endpoint_id: str) -> dict[str, Any]:
    registry = ensure_endpoint_registry(bridge)
    if endpoint_id not in registry:
        raise ValueError(f"Unknown endpointId: {endpoint_id}")
    return register_endpoint(bridge, registry[endpoint_id])


def observed_endpoint_area(bridge: Any, endpoint: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    selected_bridge = TargetBridge(bridge, endpoint)
    response = selected_bridge.request("observe")
    if "error" in response:
        raise ValueError(f"observe failed for {endpoint.get('endpointId')}: {response['error']}")
    payload = response.get("result", response)
    observation = unwrap_observation_payload(payload)
    return payload if isinstance(payload, dict) else {}, observation, area_summary_payload(observation)


def rough_hex_distance(left: Any, right: Any) -> int | None:
    if not isinstance(left, dict) or not isinstance(right, dict):
        return None
    left_x = get_hex_value(left, "x")
    left_y = get_hex_value(left, "y")
    right_x = get_hex_value(right, "x")
    right_y = get_hex_value(right, "y")
    if left_x is None or left_y is None or right_x is None or right_y is None:
        return None
    return approximate_hex_distance((int(left_x), int(left_y)), (int(right_x), int(right_y)))


def follow_agent_plan(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    leader_endpoint_id = str(arguments.get("leaderEndpointId", "")).strip()
    follower_endpoint_id = str(arguments.get("followerEndpointId", arguments.get("endpointId", ""))).strip()
    if not leader_endpoint_id:
        raise ValueError("leaderEndpointId is required")
    if not follower_endpoint_id:
        raise ValueError("followerEndpointId is required")
    if leader_endpoint_id == follower_endpoint_id:
        raise ValueError("leaderEndpointId and followerEndpointId must be different")

    leader_endpoint = endpoint_by_id(bridge, leader_endpoint_id)
    follower_endpoint = endpoint_by_id(bridge, follower_endpoint_id)
    leader_payload, leader_observation, leader_area = observed_endpoint_area(bridge, leader_endpoint)
    follower_payload, follower_observation, follower_area = observed_endpoint_area(bridge, follower_endpoint)
    follow_distance = max(0, min(int(arguments.get("followDistance", 2)), 20))

    leader_chosen = leader_area.get("chosen") if isinstance(leader_area.get("chosen"), dict) else {}
    follower_chosen = follower_area.get("chosen") if isinstance(follower_area.get("chosen"), dict) else {}
    leader_global = leader_area.get("globalMap") if isinstance(leader_area.get("globalMap"), dict) else {}
    follower_global = follower_area.get("globalMap") if isinstance(follower_area.get("globalMap"), dict) else {}
    plan: dict[str, Any] = {
        "leaderEndpoint": leader_endpoint,
        "followerEndpoint": follower_endpoint,
        "leaderObservationSeq": leader_payload.get("observationSeq", leader_observation.get("seq")),
        "followerObservationSeq": follower_payload.get("observationSeq", follower_observation.get("seq")),
        "leaderArea": leader_area,
        "followerArea": follower_area,
        "followDistance": follow_distance,
        "execute": bool(arguments.get("execute", False)),
    }

    if leader_area.get("mode") == "map" and follower_area.get("mode") == "map" and same_map_area(leader_area, follower_area):
        leader_hex = leader_chosen.get("hex")
        follower_hex = follower_chosen.get("hex")
        distance = rough_hex_distance(leader_hex, follower_hex)
        plan["distance"] = distance
        if distance is not None and distance <= follow_distance:
            plan.update({"step": "hold", "tool": None, "arguments": {}, "reason": "follower is already within followDistance"})
        elif isinstance(leader_hex, dict):
            plan.update(
                {
                    "step": "move",
                    "tool": "tla_move_to_hex",
                    "arguments": {"endpointId": follower_endpoint_id, "x": get_hex_value(leader_hex, "x"), "y": get_hex_value(leader_hex, "y")},
                    "reason": "same visible map as leader",
                }
            )
            apply_path_validation_to_plan(bridge, plan, follower_hex, leader_hex, arguments)
        else:
            plan.update({"step": "blocked", "blockedBy": ["leader hex is not visible"], "reason": "missing leader hex"})
    elif leader_area.get("mode") == "global" and follower_area.get("mode") == "global" and isinstance(leader_global.get("pos"), dict):
        leader_pos = leader_global.get("pos")
        follower_pos = follower_global.get("pos")
        distance = rough_hex_distance(leader_pos, follower_pos)
        plan["distance"] = distance
        if distance is not None and distance <= follow_distance:
            plan.update({"step": "hold", "tool": None, "arguments": {}, "reason": "follower is already near leader on the global map"})
        else:
            plan.update(
                {
                    "step": "global_move",
                    "tool": "tla_global_move_to",
                    "arguments": {"endpointId": follower_endpoint_id, "x": get_hex_value(leader_pos, "x"), "y": get_hex_value(leader_pos, "y")},
                    "reason": "same global-map mode as leader",
                }
            )
    else:
        plan.update({"step": "blocked", "blockedBy": ["leader and follower are not in a comparable visible map/global mode"], "reason": "follow requires comparable visible areas"})

    return plan


def follow_agent_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    plan = follow_agent_plan(bridge, arguments)
    executed: dict[str, Any] | None = None
    if plan.get("execute") and plan.get("tool") in {"tla_move_to_hex", "tla_global_move_to"} and isinstance(plan.get("arguments"), dict):
        command_arguments = {**arguments, **plan["arguments"]}
        command_arguments.pop("leaderEndpointId", None)
        command_arguments.pop("followerEndpointId", None)
        if plan["tool"] == "tla_global_move_to":
            executed = global_move_with_memory(bridge, command_arguments)
        else:
            executed = act_with_optional_wait(target_bridge(bridge, command_arguments), typed_command_payload("tla_move_to_hex", command_arguments), command_arguments)
        plan["executed"] = {"error": executed["error"]} if "error" in executed else executed.get("result", executed)

    if executed is None:
        plan["executed"] = None
    return {"jsonrpc": "2.0", "id": None, "result": {"follow": plan, "guidance": "tla_follow_agent follows only through normal typed commands and only when leader/follower observations are comparable."}}


def normalized_team_role(profile: dict[str, Any], index: int) -> str:
    role = str(profile.get("role") or profile.get("preset") or "").strip().lower()
    if not role or role == "custom":
        return "leader" if index == 0 else "follower"
    for marker, normalized in (
        ("leader", "leader"),
        ("scout", "scout"),
        ("guard", "guard"),
        ("trader", "trader"),
        ("talker", "talker"),
        ("social", "talker"),
        ("looter", "looter"),
        ("loot", "looter"),
        ("follower", "follower"),
        ("helper", "talker"),
    ):
        if marker in role:
            return normalized
    return role


def role_task_bonus(role: str, option: dict[str, Any]) -> int:
    kind = str(option.get("kind", ""))
    tool = str(option.get("tool", ""))
    if role == "leader":
        if kind in {"account_gate", "generation_gate", "global_travel"}:
            return 15
        if kind == "follow":
            return -40
    if role == "guard":
        if kind == "combat" or tool in {"tla_attack_entity", "tla_target_options", "tla_cover_options", "tla_retreat_options", "tla_reload_options"}:
            return 25
        if kind == "follow":
            return 10
    if role == "scout":
        if kind == "global_travel" or tool in {"tla_nav_plan", "tla_explore_options", "tla_global_move_to"}:
            return 25
        if kind in {"pick_item", "loot_critter"}:
            return -10
    if role == "trader":
        if kind in {"dialog", "talk_to"}:
            return 20
        if tool in {"tla_dialog_answer", "tla_talk_to"}:
            return 20
    if role == "talker":
        if kind in {"dialog", "talk_to"}:
            return 30
        if kind == "combat":
            return -15
    if role == "looter":
        if kind in {"pick_item", "loot_critter"} or tool in {"tla_pick_item", "tla_loot_critter", "tla_container_options"}:
            return 30
    if role == "follower":
        if kind == "follow":
            return 35
        if kind == "global_travel":
            return 5
    return 0


def team_follow_task_option(member: dict[str, Any], leader_endpoint_id: str, arguments: dict[str, Any]) -> dict[str, Any] | None:
    endpoint_id = team_member_endpoint_id(member)
    if not endpoint_id or endpoint_id == leader_endpoint_id:
        return None
    return {
        "kind": "follow",
        "score": 65,
        "reason": "stay coordinated with leader endpoint",
        "tool": "tla_follow_agent",
        "arguments": {
            "leaderEndpointId": leader_endpoint_id,
            "followerEndpointId": endpoint_id,
            "followDistance": int(arguments.get("followDistance", 2)),
            "validatePath": bool(arguments.get("validatePath", False)),
        },
    }


def score_team_task(role: str, option: dict[str, Any]) -> dict[str, Any]:
    base_score = int(option.get("score", 50)) if isinstance(option.get("score"), int) else 50
    bonus = role_task_bonus(role, option)
    score = max(0, min(base_score + bonus, 120))
    result = dict(option)
    result["teamRole"] = role
    result["teamScore"] = score
    result["roleBonus"] = bonus
    return result


def team_tasks_payload(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    endpoints = resolve_wait_all_endpoints(bridge, arguments)
    max_results = max(1, min(int(arguments.get("maxResults", 5)), 50))
    leader_endpoint_id = str(arguments.get("leaderEndpointId", "")).strip() or (
        str(endpoints[0]["endpointId"]) if endpoints else ""
    )
    members: list[dict[str, Any]] = []
    assignments: list[dict[str, Any]] = []

    for index, endpoint in enumerate(endpoints):
        selected_bridge = TargetBridge(bridge, endpoint)
        key = agent_profile_key(selected_bridge)
        profile = normalized_agent_profile({}, ensure_agent_profiles(selected_bridge).get(key))
        role = normalized_team_role(profile, index)
        payload, observation, area = observed_endpoint_area(bridge, endpoint)
        action_suggestions = available_actions_payload(payload, observation, arguments)
        options_payload = task_options_payload(observation, action_suggestions, profile, arguments)
        options = [score_team_task(role, option) for option in options_payload.get("options", []) if isinstance(option, dict)]
        follow_task = team_follow_task_option({"endpoint": endpoint, "profile": profile}, leader_endpoint_id, arguments)
        if isinstance(follow_task, dict):
            options.append(score_team_task(role, follow_task))
        options.sort(key=lambda option: int(option.get("teamScore", 0)), reverse=True)

        member_result = {
            "endpoint": dict(endpoint),
            "key": key,
            "role": role,
            "profile": profile,
            "observationSeq": payload.get("observationSeq", observation.get("seq")) if isinstance(payload, dict) else observation.get("seq"),
            "area": area,
            "options": options[:max_results],
        }
        members.append(member_result)
        if options:
            top = dict(options[0])
            assignments.append(
                {
                    "endpointId": endpoint.get("endpointId"),
                    "role": role,
                    "task": top,
                    "reason": f"{role} role score {top.get('teamScore')}",
                }
            )

    assignments.sort(key=lambda entry: int((entry.get("task") if isinstance(entry.get("task"), dict) else {}).get("teamScore", 0)), reverse=True)
    return {
        "leaderEndpointId": leader_endpoint_id,
        "members": members,
        "assignments": assignments[: max(1, min(int(arguments.get("assignmentLimit", len(assignments) or 1)), 50))],
        "teamMemory": team_memory_summary(team_memory_for_key(bridge, team_memory_key(arguments))),
        "guidance": "Team tasks are role-aware advisory arbitration from visible per-endpoint task options. Execute selected tools explicitly per endpoint.",
    }


def team_tasks_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": None, "result": team_tasks_payload(bridge, arguments)}


def unwrap_observation_payload(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict):
        observation = payload.get("observation")
        if isinstance(observation, dict):
            return observation
        return payload
    return {}


def readiness_missing(observation: dict[str, Any], arguments: dict[str, Any]) -> list[str]:
    missing: list[str] = []

    if bool(arguments.get("requireConnected", True)) and not observation.get("connected"):
        missing.append("connected")
    if bool(arguments.get("requireMap", True)) and not observation.get("hasMap"):
        missing.append("hasMap")
    if bool(arguments.get("requireChosen", True)) and not observation.get("hasChosen"):
        missing.append("hasChosen")

    return missing


def readiness_requirement_names(arguments: dict[str, Any]) -> list[str]:
    names: list[str] = []
    if bool(arguments.get("requireConnected", True)):
        names.append("connected")
    if bool(arguments.get("requireMap", True)):
        names.append("hasMap")
    if bool(arguments.get("requireChosen", True)):
        names.append("hasChosen")
    return names


def readiness_properties() -> dict[str, Any]:
    return {
        "timeoutMs": {"type": "integer", "minimum": 0, "maximum": 180000},
        "pollIntervalMs": {"type": "integer", "minimum": 0, "maximum": 5000},
        "requireConnected": {"type": "boolean", "description": "Require observation.connected; default true."},
        "requireMap": {"type": "boolean", "description": "Require observation.hasMap; default true."},
        "requireChosen": {"type": "boolean", "description": "Require observation.hasChosen; default true."},
        "includeObservation": {"type": "boolean", "description": "Include the last observation in the result; default true."},
    }


def clamp_int(value: Any, minimum: int, maximum: int) -> int:
    return max(minimum, min(int(value), maximum))


def probe_endpoint(endpoint: dict[str, Any]) -> bool:
    try:
        response = Bridge(str(endpoint["host"]), int(endpoint["port"]), str(endpoint.get("token", "")), 1.0).request("ping")
        return "error" not in response
    except OSError:
        return False


def select_bridge_endpoint(bridge: Any, endpoint: dict[str, Any]) -> dict[str, Any]:
    normalized = register_endpoint(bridge, endpoint)
    bridge.host = str(normalized.get("host", "127.0.0.1"))
    bridge.port = int(normalized["port"])
    bridge.token = str(normalized.get("token", ""))
    bridge.selected_endpoint_id = str(normalized["endpointId"])
    bridge.events_cursor = ensure_endpoint_cursors(bridge).get(str(normalized["endpointId"]), 0)
    return normalized


def require_orchestrator(bridge: Any) -> Orchestrator:
    orchestrator = getattr(bridge, "orchestrator", None)
    if not isinstance(orchestrator, Orchestrator):
        raise ValueError("Launch orchestration is not available for this adapter instance")
    return orchestrator


def workspace_root_for_bridge(bridge: Any) -> Path:
    orchestrator = getattr(bridge, "orchestrator", None)
    if isinstance(orchestrator, Orchestrator):
        return orchestrator.workspace_root

    workspace_root = getattr(bridge, "workspace_root", None)
    if isinstance(workspace_root, Path):
        return workspace_root
    if isinstance(workspace_root, str):
        return Path(workspace_root)

    return DEFAULT_WORKSPACE_ROOT


def process_log_tail(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    workspace_root = workspace_root_for_bridge(bridge)
    cwd = workspace_root
    role = ""
    managed: ManagedProcess | None = None

    if "processId" in arguments:
        process_id = int(arguments["processId"])
        orchestrator = require_orchestrator(bridge)
        if process_id not in orchestrator.processes:
            raise ValueError(f"Unknown processId: {process_id}")
        managed = orchestrator.processes[process_id]
        cwd = Path(managed.cwd)
        role = managed.role

    log_name = str(arguments.get("logName") or DEFAULT_LOG_NAMES.get(role, "TLA_ServerHeadless.log"))
    lines = clamp_int(arguments.get("lines", 200), 1, 2000)
    max_bytes = clamp_int(arguments.get("maxBytes", 262144), 1024, 1048576)
    path = resolve_log_path(workspace_root, cwd, log_name)
    text, returned_lines, truncated = read_log_tail(path, max_bytes, lines)

    result: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "lines": returned_lines,
        "text": text,
        "truncatedBytes": truncated,
        "availableLogNames": available_log_names(cwd),
    }

    if managed is not None:
        result["process"] = {
            "processId": managed.process_id,
            "osPid": managed.process.pid,
            "role": managed.role,
            "running": managed.process.poll() is None,
            "returnCode": managed.process.poll(),
        }

    return {"jsonrpc": "2.0", "id": None, "result": result}


def process_window_screenshot(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    workspace_root = workspace_root_for_bridge(bridge)
    target = resolve_window_screenshot_target(bridge, arguments)
    os_pid = int(target["osPid"])
    mode = normalize_window_screenshot_mode(arguments.get("mode", "auto"))
    delay_ms = clamp_int(arguments.get("delayMs", 0), 0, 10000)
    path = resolve_window_screenshot_path(workspace_root, arguments.get("path"), os_pid)

    if delay_ms > 0:
        time.sleep(delay_ms / 1000.0)

    capture = capture_process_window_to_png(os_pid, path, mode)
    result: dict[str, Any] = {
        **capture,
        "process": target.get("process"),
        "endpoint": target.get("endpoint"),
        "path": str(path),
        "exists": path.exists(),
        "sizeBytes": path.stat().st_size if path.exists() else 0,
        "diagnostic": "os_window_screenshot",
        "visibility": "Captures the local OS window for visual QA; it is not part of the normal client observation stream.",
    }

    if bool(arguments.get("includeBase64", False)):
        max_bytes = clamp_int(arguments.get("maxBase64Bytes", 262144), 1, 5242880)
        size = int(result["sizeBytes"])
        if path.exists() and size <= max_bytes:
            result["base64"] = base64.b64encode(path.read_bytes()).decode("ascii")
        else:
            result["base64"] = None
            result["base64OmittedReason"] = f"Screenshot is {size} bytes; maxBase64Bytes is {max_bytes}"

    return {"jsonrpc": "2.0", "id": None, "result": result}


def resolve_window_screenshot_target(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    if "osPid" in arguments:
        os_pid = int(arguments["osPid"])
        result: dict[str, Any] = {"osPid": os_pid, "source": "osPid"}
        managed = managed_process_by_os_pid(bridge, os_pid)
        if managed is not None:
            result["process"] = managed_process_summary(managed)
        return result

    endpoint: dict[str, Any] | None = None
    if "endpointId" in arguments:
        endpoint = resolve_target_endpoint(bridge, {"endpointId": arguments["endpointId"]})
    elif "processId" not in arguments:
        selected_endpoint_id = getattr(bridge, "selected_endpoint_id", None)
        registry = ensure_endpoint_registry(bridge)
        if isinstance(selected_endpoint_id, str) and selected_endpoint_id in registry:
            endpoint = register_endpoint(bridge, registry[selected_endpoint_id])

    process_id: int | None = None
    if "processId" in arguments:
        process_id = int(arguments["processId"])
    elif isinstance(endpoint, dict) and endpoint.get("processId") is not None:
        process_id = int(endpoint["processId"])
    if process_id is None:
        raise ValueError("Pass processId, osPid, or endpointId for an endpoint created by tla_launch")

    orchestrator = require_orchestrator(bridge)
    if process_id not in orchestrator.processes:
        raise ValueError(f"Unknown processId: {process_id}")

    managed = orchestrator.processes[process_id]
    result = {
        "osPid": managed.process.pid,
        "source": "processId",
        "process": managed_process_summary(managed),
    }
    if endpoint is not None:
        result["source"] = "endpointId"
        result["endpoint"] = endpoint
    return result


def managed_process_by_os_pid(bridge: Any, os_pid: int) -> ManagedProcess | None:
    orchestrator = getattr(bridge, "orchestrator", None)
    if not isinstance(orchestrator, Orchestrator):
        return None

    for managed in orchestrator.processes.values():
        if managed.process.pid == os_pid:
            return managed
    return None


def managed_process_summary(managed: ManagedProcess) -> dict[str, Any]:
    return_code = managed.process.poll()
    return {
        "processId": managed.process_id,
        "osPid": managed.process.pid,
        "role": managed.role,
        "running": return_code is None,
        "returnCode": return_code,
        "cwd": managed.cwd,
    }


def normalize_window_screenshot_mode(value: Any) -> str:
    mode = str(value or "auto").replace("-", "_").lower()
    if mode in {"auto", "best", "default"}:
        return "auto"
    if mode in {"screen_client", "screenclient", "client", "copy_from_screen_client", "copyfromscreenclient"}:
        return "screen_client"
    if mode in {"screen", "copy_from_screen", "copyfromscreen"}:
        return "screen"
    if mode in {"print_window", "printwindow", "print"}:
        return "print_window"
    raise ValueError("mode must be 'auto', 'screenClient', 'screen', or 'printWindow'")


def resolve_window_screenshot_path(workspace_root: Path, requested_path: Any, os_pid: int) -> Path:
    default_name = f"{time.strftime('%Y%m%d-%H%M%S')}-{int(time.time() * 1000) % 1000:03d}-pid{os_pid}.png"

    if isinstance(requested_path, str) and requested_path.strip():
        path = Path(requested_path.strip())
        if not path.is_absolute():
            path = workspace_root / path
        if path.suffix == "":
            path = path / default_name
    else:
        path = workspace_root / "Workspace" / "AiControlScreenshots" / default_name

    path = path.resolve()
    if path.suffix.lower() != ".png":
        raise ValueError("Screenshot path must end with .png")
    if not is_path_under(path, workspace_root.resolve()):
        raise ValueError("Screenshot path must stay inside the workspace")

    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def capture_process_window_to_png(os_pid: int, path: Path, mode: str) -> dict[str, Any]:
    if sys.platform != "win32":
        raise OSError("tla_window_screenshot currently supports local Windows windows only")

    if mode == "auto":
        attempts: list[dict[str, Any]] = []
        for candidate in ("screen_client", "screen", "screen_client", "screen", "print_window"):
            try:
                payload = capture_process_window_to_png_once(os_pid, path, candidate)
            except OSError as exc:
                attempts.append({"mode": candidate, "ok": False, "error": str(exc)})
                continue

            payload["requestedMode"] = "auto"
            attempts.append(
                {
                    "mode": candidate,
                    "ok": True,
                    "blankLike": bool(payload.get("blankLike", False)),
                    "foregroundMatched": payload.get("foregroundMatched"),
                    "uniqueColorBuckets": payload.get("uniqueColorBuckets"),
                    "blackRatio": payload.get("blackRatio"),
                    "whiteRatio": payload.get("whiteRatio"),
                    "dominantBucketRatio": payload.get("dominantBucketRatio"),
                }
            )
            if not bool(payload.get("blankLike", False)) and (candidate == "print_window" or bool(payload.get("foregroundMatched", False))):
                payload["attempts"] = attempts
                return payload

        details = "; ".join(
            f"{attempt['mode']}: {attempt.get('error', 'blank' if attempt.get('blankLike') else 'untrusted')}" for attempt in attempts
        )
        raise OSError(f"All screenshot capture modes failed or returned blank/untrusted images: {details}")

    payload = capture_process_window_to_png_once(os_pid, path, mode)
    payload["requestedMode"] = mode
    return payload


def capture_process_window_to_png_once(os_pid: int, path: Path, mode: str) -> dict[str, Any]:
    script = build_windows_screenshot_script(os_pid, path, mode)
    completed = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or f"PowerShell exited with code {completed.returncode}"
        raise OSError(message)

    output = completed.stdout.strip()
    if not output:
        raise OSError("Screenshot capture did not return metadata")

    try:
        payload = json.loads(output.splitlines()[-1])
    except json.JSONDecodeError as exc:
        raise OSError(f"Screenshot capture returned invalid metadata: {output}") from exc

    payload["mode"] = mode
    payload["format"] = "png"
    return payload


def build_windows_screenshot_script(os_pid: int, path: Path, mode: str) -> str:
    output_path = powershell_single_quote(str(path))
    powershell_mode = powershell_single_quote(mode)
    return f"""
$ErrorActionPreference = 'Stop'
$ProcessIdValue = {os_pid}
$OutputPath = {output_path}
$Mode = {powershell_mode}
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;

public static class AiControlWindowCaptureNative
{{
    [StructLayout(LayoutKind.Sequential)]
    public struct Rect
    {{
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }}

    [StructLayout(LayoutKind.Sequential)]
    public struct Point
    {{
        public int X;
        public int Y;
    }}

    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out Rect rect);

    [DllImport("user32.dll")]
    public static extern bool GetClientRect(IntPtr hWnd, out Rect rect);

    [DllImport("user32.dll")]
    public static extern bool ClientToScreen(IntPtr hWnd, ref Point point);

    [DllImport("user32.dll")]
    public static extern bool IsIconic(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll")]
    public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint flags);

    [DllImport("user32.dll")]
    public static extern IntPtr GetDC(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern int ReleaseDC(IntPtr hWnd, IntPtr hDC);

    [DllImport("gdi32.dll")]
    public static extern bool BitBlt(IntPtr hdcDest, int nXDest, int nYDest, int nWidth, int nHeight, IntPtr hdcSrc, int nXSrc, int nYSrc, int dwRop);
}}
"@
$Process = Get-Process -Id $ProcessIdValue -ErrorAction Stop
$Handle = $Process.MainWindowHandle
if ($Handle -eq [IntPtr]::Zero) {{
    throw "Process $ProcessIdValue has no main window handle. Launch a visible client/server window or pass osPid for that process."
}}

$WindowRect = New-Object AiControlWindowCaptureNative+Rect
if (-not [AiControlWindowCaptureNative]::GetWindowRect($Handle, [ref]$WindowRect)) {{
    throw "GetWindowRect failed for process $ProcessIdValue"
}}

$WasMinimized = [AiControlWindowCaptureNative]::IsIconic($Handle)
if ($WasMinimized) {{
    [void][AiControlWindowCaptureNative]::ShowWindow($Handle, 9)
    Start-Sleep -Milliseconds 250
}}

if ($Mode -ne 'print_window') {{
    [void][AiControlWindowCaptureNative]::ShowWindow($Handle, 5)
    $Focused = [AiControlWindowCaptureNative]::SetForegroundWindow($Handle)
    Start-Sleep -Milliseconds 350
}}
else {{
    $Focused = $false
}}

$ForegroundHandle = [AiControlWindowCaptureNative]::GetForegroundWindow()
$ForegroundMatched = ($ForegroundHandle -eq $Handle)

$Rect = New-Object AiControlWindowCaptureNative+Rect
$CaptureArea = 'window'
if ($Mode -eq 'screen_client') {{
    $ClientRect = New-Object AiControlWindowCaptureNative+Rect
    if (-not [AiControlWindowCaptureNative]::GetClientRect($Handle, [ref]$ClientRect)) {{
        throw "GetClientRect failed for process $ProcessIdValue"
    }}
    $ClientPoint = New-Object AiControlWindowCaptureNative+Point
    $ClientPoint.X = 0
    $ClientPoint.Y = 0
    if (-not [AiControlWindowCaptureNative]::ClientToScreen($Handle, [ref]$ClientPoint)) {{
        throw "ClientToScreen failed for process $ProcessIdValue"
    }}

    $Rect.Left = $ClientPoint.X
    $Rect.Top = $ClientPoint.Y
    $Rect.Right = $ClientPoint.X + [Math]::Max(0, $ClientRect.Right - $ClientRect.Left)
    $Rect.Bottom = $ClientPoint.Y + [Math]::Max(0, $ClientRect.Bottom - $ClientRect.Top)
    $CaptureArea = 'client'
}}
else {{
    $Rect.Left = $WindowRect.Left
    $Rect.Top = $WindowRect.Top
    $Rect.Right = $WindowRect.Right
    $Rect.Bottom = $WindowRect.Bottom
}}

$Width = [Math]::Max(0, $Rect.Right - $Rect.Left)
$Height = [Math]::Max(0, $Rect.Bottom - $Rect.Top)
if ($Width -le 0 -or $Height -le 0) {{
    throw "Window has invalid dimensions: $Width x $Height"
}}

if ($Mode -ne 'print_window') {{
    $VirtualBounds = [System.Windows.Forms.SystemInformation]::VirtualScreen
    if ($Rect.Right -le $VirtualBounds.Left -or $Rect.Left -ge $VirtualBounds.Right -or $Rect.Bottom -le $VirtualBounds.Top -or $Rect.Top -ge $VirtualBounds.Bottom) {{
        throw "Capture rectangle is outside the virtual screen: $($Rect.Left),$($Rect.Top),$Width,$Height"
    }}
}}

function Get-BitmapSampleStats([System.Drawing.Bitmap]$Bitmap)
{{
    $Buckets = @{{}}
    $SamplePixels = 0
    $BlackPixels = 0
    $WhitePixels = 0
    $StepX = [Math]::Max(1, [int][Math]::Floor($Bitmap.Width / 64))
    $StepY = [Math]::Max(1, [int][Math]::Floor($Bitmap.Height / 64))

    for ($Y = 0; $Y -lt $Bitmap.Height; $Y += $StepY) {{
        for ($X = 0; $X -lt $Bitmap.Width; $X += $StepX) {{
            $Color = $Bitmap.GetPixel($X, $Y)
            $SamplePixels += 1
            if ($Color.R -lt 8 -and $Color.G -lt 8 -and $Color.B -lt 8) {{
                $BlackPixels += 1
            }}
            if ($Color.R -gt 247 -and $Color.G -gt 247 -and $Color.B -gt 247) {{
                $WhitePixels += 1
            }}

            $BucketR = [int][Math]::Floor($Color.R / 16)
            $BucketG = [int][Math]::Floor($Color.G / 16)
            $BucketB = [int][Math]::Floor($Color.B / 16)
            $Bucket = "$BucketR,$BucketG,$BucketB"
            if ($Buckets.ContainsKey($Bucket)) {{
                $Buckets[$Bucket] += 1
            }}
            else {{
                $Buckets[$Bucket] = 1
            }}
        }}
    }}

    $MaxBucketCount = 0
    foreach ($BucketCount in $Buckets.Values) {{
        if ($BucketCount -gt $MaxBucketCount) {{
            $MaxBucketCount = $BucketCount
        }}
    }}

    $BlackRatio = 0.0
    $WhiteRatio = 0.0
    $DominantBucketRatio = 0.0
    if ($SamplePixels -gt 0) {{
        $BlackRatio = $BlackPixels / $SamplePixels
        $WhiteRatio = $WhitePixels / $SamplePixels
        $DominantBucketRatio = $MaxBucketCount / $SamplePixels
    }}

    $BlankLike = $false
    if ($SamplePixels -gt 0) {{
        $BlankLike = ($Buckets.Count -le 4) -or ($DominantBucketRatio -ge 0.98) -or (($BlackRatio + $WhiteRatio) -ge 0.92 -and $Buckets.Count -le 24)
    }}

    return [ordered]@{{
        samplePixels = $SamplePixels
        uniqueColorBuckets = $Buckets.Count
        blackRatio = [Math]::Round($BlackRatio, 4)
        whiteRatio = [Math]::Round($WhiteRatio, 4)
        dominantBucketRatio = [Math]::Round($DominantBucketRatio, 4)
        blankLike = $BlankLike
    }}
}}

$Bitmap = New-Object System.Drawing.Bitmap -ArgumentList $Width, $Height
$Graphics = [System.Drawing.Graphics]::FromImage($Bitmap)
$CopyAttempts = 0
$CaptureMethod = $Mode
try {{
    if ($Mode -eq 'print_window') {{
        $Hdc = $Graphics.GetHdc()
        try {{
            $Ok = [AiControlWindowCaptureNative]::PrintWindow($Handle, $Hdc, 2)
        }}
        finally {{
            $Graphics.ReleaseHdc($Hdc)
        }}
        if (-not $Ok) {{
            throw "PrintWindow failed for process $ProcessIdValue"
        }}
    }}
    else {{
        $Size = New-Object System.Drawing.Size -ArgumentList $Width, $Height
        $Captured = $false
        $LastCaptureError = $null
        $CaptureMethod = 'bitblt'
        for ($Attempt = 1; $Attempt -le 5; $Attempt += 1) {{
            $CopyAttempts = $Attempt
            $ScreenHdc = [IntPtr]::Zero
            $BitmapHdc = [IntPtr]::Zero
            try {{
                $ScreenHdc = [AiControlWindowCaptureNative]::GetDC([IntPtr]::Zero)
                if ($ScreenHdc -eq [IntPtr]::Zero) {{
                    throw "GetDC(NULL) failed"
                }}
                $BitmapHdc = $Graphics.GetHdc()
                $Ok = [AiControlWindowCaptureNative]::BitBlt($BitmapHdc, 0, 0, $Width, $Height, $ScreenHdc, $Rect.Left, $Rect.Top, 0x00CC0020)
                if (-not $Ok) {{
                    throw "BitBlt failed"
                }}
                $Captured = $true
                break
            }}
            catch {{
                $LastCaptureError = $_.Exception.Message
                Start-Sleep -Milliseconds 150
            }}
            finally {{
                if ($BitmapHdc -ne [IntPtr]::Zero) {{
                    $Graphics.ReleaseHdc($BitmapHdc)
                }}
                if ($ScreenHdc -ne [IntPtr]::Zero) {{
                    [void][AiControlWindowCaptureNative]::ReleaseDC([IntPtr]::Zero, $ScreenHdc)
                }}
            }}
        }}
        if (-not $Captured) {{
            $CaptureMethod = 'copy_from_screen'
            for ($Attempt = 1; $Attempt -le 5; $Attempt += 1) {{
                $CopyAttempts = 5 + $Attempt
                try {{
                    $Graphics.CopyFromScreen($Rect.Left, $Rect.Top, 0, 0, $Size)
                    $Captured = $true
                    break
                }}
                catch {{
                    $LastCaptureError = $_.Exception.Message
                    Start-Sleep -Milliseconds 150
                }}
            }}
        }}
        if (-not $Captured) {{
            throw "Visible-screen capture failed after $CopyAttempts attempts: $LastCaptureError"
        }}
    }}

    $Stats = Get-BitmapSampleStats $Bitmap
    $Bitmap.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Png)
}}
finally {{
    $Graphics.Dispose()
    $Bitmap.Dispose()
}}

$Resolved = (Resolve-Path -LiteralPath $OutputPath).Path
$Payload = [ordered]@{{
    path = $Resolved
    osPid = $ProcessIdValue
    hwnd = $Handle.ToInt64()
    left = $Rect.Left
    top = $Rect.Top
    width = $Width
    height = $Height
    captureArea = $CaptureArea
    wasMinimized = $WasMinimized
    foregroundHwnd = $ForegroundHandle.ToInt64()
    foregroundMatched = $ForegroundMatched
    setForegroundResult = $Focused
    copyAttempts = $CopyAttempts
    captureMethod = $CaptureMethod
    samplePixels = $Stats.samplePixels
    uniqueColorBuckets = $Stats.uniqueColorBuckets
    blackRatio = $Stats.blackRatio
    whiteRatio = $Stats.whiteRatio
    dominantBucketRatio = $Stats.dominantBucketRatio
    blankLike = $Stats.blankLike
}}
[Console]::Out.Write(($Payload | ConvertTo-Json -Compress))
"""


def powershell_single_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def resolve_log_path(workspace_root: Path, cwd: Path, log_name: str) -> Path:
    if not log_name:
        raise ValueError("logName must not be empty")

    # Validate against both path flavors: on Linux a backslash is a literal
    # filename character, so PurePosixPath alone would accept "..\\evil.log".
    if PureWindowsPath(log_name).name != log_name or PurePosixPath(log_name).name != log_name:
        raise ValueError("logName must be a file name, not a path")

    path = (cwd / log_name).resolve()
    allowed_roots = [workspace_root.resolve(), cwd.resolve()]
    if not any(is_path_under(path, root) for root in allowed_roots):
        raise ValueError("Resolved log path is outside the workspace or process working directory")
    return path


def read_log_tail(path: Path, max_bytes: int, lines: int) -> tuple[str, list[str], bool]:
    if not path.exists() or not path.is_file():
        return "", [], False

    size = path.stat().st_size
    truncated = size > max_bytes

    with path.open("rb") as file:
        if truncated:
            file.seek(-max_bytes, os.SEEK_END)
        data = file.read()

    text = data.decode("utf-8", errors="replace")
    all_lines = text.splitlines()
    if truncated and all_lines:
        all_lines = all_lines[1:]
    returned_lines = all_lines[-lines:]
    return "\n".join(returned_lines), returned_lines, truncated


def available_log_names(cwd: Path) -> list[str]:
    if not cwd.exists() or not cwd.is_dir():
        return []
    return sorted(path.name for path in cwd.glob("*.log") if path.is_file())[:100]


def is_path_under(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def build_launch_options(workspace_root: Path) -> dict[str, Any]:
    return launch_build_launch_options(workspace_root, SCHEMA_VERSION, LAUNCH_ROLES)


def parse_fomain_launch_config(path: Path) -> tuple[list[dict[str, Any]], dict[str, str]]:
    return launch_parse_fomain_launch_config(path)


def parse_startup_scene_input(path: Path) -> tuple[list[str], str]:
    return launch_parse_startup_scene_input(path)


def parse_startup_scene_input_fallback(text: str) -> tuple[list[str], str]:
    return launch_parse_startup_scene_input_fallback(text)


def mcp_result(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return protocol_mcp_result(request_id, result)


def mcp_error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return protocol_mcp_error(request_id, code, message)


def bridge_text_result(response: dict[str, Any]) -> dict[str, Any]:
    return protocol_bridge_text_result(response)


def operator_guide_text() -> str:
    return guide_operator_guide_text([tool["name"] for tool in typed_command_tools()])


def conversation_guide_text(agent_name: str = "", agent_role: str = "", goals: str = "", conversation_style: str = "") -> str:
    return guide_conversation_guide_text(agent_name, agent_role, goals, conversation_style)


def agent_examples_text() -> str:
    return guide_agent_examples_text()


def schema_payload(section: str) -> dict[str, Any]:
    command_types = [command["type"] for command in COMMAND_CATALOG]
    protocol = {
        "schemaVersion": SCHEMA_VERSION,
        "bridgeTransport": "TCP localhost JSON-RPC lines",
        "mcpTransport": "stdio JSON-RPC, UTF-8",
        "bridgeMethods": {
            "observe": "Return the latest client observation.",
            "events": "Return queued events after afterSeq with an optional limit.",
            "act": "Queue a command from the command catalog.",
            "status": "Return bridge queue/status data.",
            "ping": "Connectivity check.",
        },
        "eventPolicy": {
            "default": "Low-volume client-visible semantic events are emitted by default.",
            "rawInput": "Mouse/key/touch events are emitted only when AiControl.CaptureRawInputEvents is enabled.",
            "render": "Per-frame render hooks are intentionally omitted from the default bridge stream.",
        },
        "mcpReadTools": {
            "tla_step": "Default agent read loop: next events, fresh observation, and action suggestions in one call.",
            "tla_sync": "Next events, fresh observation, and social context in one call.",
            "tla_social_context": "Read speech-focused social context, including address/intent heuristics and the configured agent profile.",
            "tla_agent_tick": "Read a step, update endpoint-local memory, and produce an advisory decision trace.",
            "tla_agent_run": "Run a bounded agent observe/decide loop and optionally execute normal typed tools behind safety gates.",
            "tla_agent_status": "Read endpoint-local profile, runtime, memory summary, and recent decisions.",
            "tla_available_actions": "Action suggestions derived from the current observation.",
            "tla_inventory_summary": "Inventory item grouping and quick item action options.",
            "tla_combat_options": "Visible combat priorities, target/reload/heal/stamina/retreat/cover options.",
            "tla_dialog_options": "Visible dialog answer classification and tla_dialog_answer suggestions.",
            "tla_task_options": "Compact priority list from gates, dialogs, progression, combat, global travel, and current action suggestions.",
            "tla_xp_source_plan": "Rank visible XP sources across progression spending, quests/dialogs, safe combat, supplies, travel, and exploration.",
            "tla_dialog_memory": "Endpoint-local memory of visible dialogs, task hints, and chosen answers.",
            "tla_task_memory": "Endpoint-local visible task hint memory plus current task priorities.",
            "tla_global_options": "Global-map interests, movement, and enter candidates.",
            "tla_travel_plan": "One-step global-map move/enter plan for a visible interest or explicit position.",
            "tla_route_memory": "Endpoint-local memory of visible global interests, travel attempts, and map/global transitions.",
            "tla_team_status": "Profiles, runtime/memory summaries, and optional observations across controlled endpoints.",
            "tla_team_memory": "Adapter-local shared team QA/coordination memory.",
            "tla_team_plan": "Advisory multi-endpoint role and rendezvous plan.",
            "tla_team_tasks": "Role-aware advisory task arbitration across controlled endpoints.",
            "tla_group_rendezvous": "Per-endpoint rendezvous movement suggestions without executing commands.",
            "tla_follow_agent": "Plan or execute a follower endpoint moving toward a leader endpoint through normal typed commands.",
            "tla_next_events": "Cursor-based event polling.",
            "tla_observe": "Fresh observation only.",
        },
    }
    commands = {
        "schemaVersion": SCHEMA_VERSION,
        "commandTypes": command_types,
        "genericInput": act_input_schema(command_types),
        "typedTools": [{"name": tool["name"], "commandType": typed_command_type_for_tool(tool["name"])} for tool in typed_command_tools()],
        "catalog": COMMAND_CATALOG,
    }
    observation = {
        "schemaVersion": SCHEMA_VERSION,
        "description": "Latest client-side snapshot built by Scripts/AiControl.fos.",
        "topLevelFields": {
            "schemaVersion": "Observation schema version.",
            "seq": "Monotonic observation build sequence.",
            "clientIndex": "Client instance index inside the current process; embedded clients start at 1.",
            "connected": "CurPlayer is available.",
            "hasMap": "CurMap is available.",
            "hasChosen": "Chosen critter is available.",
            "account": "Account/login summary and last roster state.",
            "admin": "Client-visible admin access summary and available admin prep surfaces; populated only from the current player's replicated AccessLevel.",
            "screen": "Active GUI screen and active screen list.",
            "mouse": "Current mouse position in screen coordinates.",
            "chosen": "Chosen critter object or null; additionally carries the chosen-only 'overwatch' object (see sharedShapes.chosenOverwatch).",
            "map": "Current map object or null.",
            "globalMap": "Current global-map state when chosen is travelling globally; otherwise active=false.",
            "critters": "Visible critters, capped by AiControl.MaxObservedEntities.",
            "mapItems": "Visible map items, capped by AiControl.MaxObservedEntities.",
            "inventory": "Chosen inventory items, capped by AiControl.MaxObservedEntities.",
            "pda": "Client-visible PDA surfaces currently relevant to AI, including quests.",
            "questLog": "Client-visible quest entries mirrored from the chosen critter's PDA QuestProgress.",
            "activeCollection": "Currently opened loot/container/barter collection state, if a PickUp/Barter modal or transfer context is active.",
            "uiPrompt": "Active semantic GUI prompt, such as confirm/yes-no/DialogBox/elevator, with answer buttons for tla_ui_answer.",
            "dialog": "Active dialog state and zero-based answers.",
            "availableActions": "Command types currently worth considering.",
        },
        "sharedShapes": {
            "hex": {"x": "Map hex X.", "y": "Map hex Y."},
            "screenPos": {"x": "Screen X.", "y": "Screen Y."},
            "critter": [
                "id",
                "protoId",
                "name",
                "hex",
                "dir",
                "isChosen",
                "controlledByPlayer",
                "alive",
                "dead",
                "knockout",
                "inSneakMode",
                "inCombat",
                "canMove",
                "moveBlockers",
                "globalSpeed",
                "fixedGlobalSpeed",
                "itemsWeight",
                "carryWeight",
                "overweight",
                "nonInteractible",
                "isBodyGenerated",
                "level",
                "experience",
                "nextLevelExperience",
                "experienceToNextLevel",
                "levelCap",
                "unspentStatPoints",
                "unspentSkillPoints",
                "unspentAbilityPoints",
                "curHealth",
                "maxHealth",
                "curStamina",
                "maxStamina",
                "visualFeedback",
                "factionId",
                "faction",
                "baseStats",
                "skills",
                "abilities",
                "partial",
                "partialReason",
            ],
            "faction": ["key", "name", "member", "standing", "standingStatus", "rankTitle", "rankName"],
            "critterSkill": ["id", "name", "value", "min", "max", "increaseCost", "canIncrease", "canDecrease"],
            "critterAbility": ["protoId", "name", "skill", "skillValue", "opened", "activated", "canAdd", "canRemove"],
            "critterVisualFeedback": ["labels", "suppression", "suppressionMax", "overwatchActive", "overwatchRemainingMs", "heat"],
            "chosenOverwatch": ["opened", "active", "dir", "remainingMs", "canEnter", "blockedReason"],
            "itemVisualFeedback": ["labels", "fuseActive", "fuseRemainingMs", "fuseSeconds", "timerCapable", "blastRadius", "chainBlastRadius"],
            "item": ["id", "protoId", "name", "count", "ownership", "cost", "weight", "canUse", "canUseOnSmth", "canPickUp", "canDrop", "canLoot", "canBarter", "deteriorable", "isBroken", "visualFeedback", "slot or hex", "static", "isStatic", "opened", "canOpen", "isGag", "noHighlight", "hasStaticScript", "lockerLocked", "lockerNoOpen", "hasMapExit", "hasMapEntry", "mapEntryName"],
            "screen": ["active", "activeScreens", "modalActive", "activeModal", "screens", "modalScreens", "top"],
            "screenEntry": ["name", "modal"],
            "activeCollection": ["active", "screen", "kind", "transferType", "containerId", "receivedCount", "items", "inventoryItems", "offerItems", "traderOfferItems"],
            "uiPrompt": ["active", "screen", "kind", "title", "text", "dialogId", "dialogBoxAnswerIndex", "currentMapProtoId", "buttons"],
            "uiPromptButton": ["index", "id", "text", "role", "enabled", "dangerous", "mapProtoId"],
            "pda": ["quests", "factions"],
            "questEntry": ["id", "questId", "title", "description", "objective", "status", "statusCode", "stage", "visible", "progress"],
            "admin": ["available", "connected", "accessLevel", "access", "moderator", "admin", "defaultTargetId", "actions", "preparePresets"],
            "globalMap": ["active", "tripId", "pos", "isMoving", "targetPos", "routeDistance", "routeHints", "selfHints", "size", "interests"],
            "globalInterest": ["type", "typeEnum", "id", "pos", "radius", "distance", "enterable", "inRange", "enterArguments"],
            "clientEntity": ["id", "name"],
            "account": ["connected", "playerId", "playerName", "loginPlatform", "autoLoginName", "localLogin", "webLogin", "steamLogin", "agreementAccepted", "roster"],
            "roster": ["mainCritterId", "max", "count", "canManageHere", "entries"],
            "rosterEntry": ["index", "id", "name", "loaded", "active"],
        },
    }
    events = {
        "schemaVersion": SCHEMA_VERSION,
        "ordering": "Events carry bridge sequence numbers in the bridge result; event payloads have a type field.",
        "catalog": EVENT_CATALOG,
    }
    social = {
        "schemaVersion": SCHEMA_VERSION,
        "description": "MCP-side social awareness derived from visible say_received events and the latest observation. It adds no privileged chat visibility.",
        "profile": {
            "name": "Optional in-character name for address detection.",
            "displayName": "Optional public display label for reports; name remains the address-detection field.",
            "aliases": "Alternative names players may use for the agent.",
            "role": "Role/persona supplied by the host, such as scout, trader, guard, tester, or companion.",
            "faction": "Optional in-world affiliation.",
            "stance": "Neutral/friendly/hostile/etc. role stance for planners.",
            "goals": "Short role goals used by the model when deciding whether and how to reply.",
            "taboos": "Role boundaries and actions to avoid.",
            "conversationStyle": "Tone and length guidance for replies.",
            "responsePolicy": "When the agent should answer or stay quiet.",
            "speechStyle": "Short style label or instruction for visible speech.",
            "socialPolicy": "Higher-level social turn-taking policy.",
            "riskTolerance": "Movement/combat risk preference.",
            "combatStyle": "Combat posture, such as avoidant, defensive, aggressive, or support.",
            "lootStyle": "Looting preference, such as minimal, practical, survival, valuable, or combat.",
            "activityLevel": "Pacing/idle tendency.",
            "reactionProfile": "fast, normal, or slow reaction baseline.",
            "skillLevel": "novice, average, expert, etc.",
            "language": "Preferred reply language; russ is the project default.",
        },
        "heardSpeech": {
            "source": "Events with type=say_received returned by tla_step, tla_sync, or tla_social_context.",
            "fields": ["seq", "speaker", "listener", "distance", "sayType", "onHeadOnly", "text", "selfSpeech", "addressedToAgent", "intent", "topics", "emotionalTone", "pendingRequest", "promise", "needsResponse", "reasons", "response"],
            "addressedToAgent": ["self", "likely", "possible", "unlikely"],
            "intent": ["question", "request", "greeting", "emote", "statement"],
        },
        "conversation": {
            "fields": ["threads", "pendingThreads", "counts", "profile", "guidance"],
            "threadFields": ["threadId", "speaker", "listener", "lastText", "intent", "topics", "emotionalTone", "addressedToAgent", "needsResponse", "urgency", "relation", "pendingRequest", "promise", "expectedReply"],
            "replyOptionFields": ["intent", "score", "tool", "arguments", "requiresModelText", "textInstruction", "reason"],
            "memoryFields": ["conversationThreads", "pendingRequests", "promises"],
        },
        "tools": ["tla_set_agent_profile", "tla_agent_profile", "tla_social_context", "tla_conversation_state", "tla_reply_options", "tla_relation_note", "tla_agent_say_planned", "tla_say"],
    }
    agent = {
        "schemaVersion": SCHEMA_VERSION,
        "description": "MCP-side advisory agent runtime. It adds profile, memory, pacing/status, and decision trace around normal client-visible tools without granting server authority.",
        "policy": {
            "authority": "Agent decisions are advisory; commands still go through normal typed tools and server validation.",
            "visibility": "Memory and decisions must be derived from client observations, events, MCP query results, or explicit host notes.",
            "mode": "tla_agent_tick is advisory. tla_agent_run is bounded and executes only when execute=true, still through typed tools and server validation.",
            "humanLikeMeans": "Believable client behavior, not deceptive real-user impersonation.",
            "deploymentModes": sorted(AGENT_DEPLOYMENT_MODES),
            "permissionModes": sorted(AGENT_PERMISSION_MODES),
            "readiness": "Marked/supervised/production deployment requires agentDisclosure before tla_agent_run may execute; qa_out_of_band is restricted to test_only/private_qa.",
        },
        "profileFields": sorted(SOCIAL_PROFILE_FIELDS),
        "profilePresets": sorted(AGENT_PROFILE_PRESETS),
        "memory": {
            "fields": [
                "notes",
                "facts",
                "people",
                "places",
                "dialogs",
                "dialogChoices",
                "taskHints",
                "globalInterests",
                "travelHistory",
                "mapTransitions",
                "recentEvents",
                "visited",
                "visitedAreas",
                "recentPath",
                "knownHazards",
                "usefulItems",
                "interactions",
                "combatEncounters",
                "lootContainers",
                "activeCollection",
                "conversationThreads",
                "pendingRequests",
                "promises",
                "doNotRetry",
                "failedActions",
                "lastObservation",
                "lastStepAt",
            ],
            "kinds": ["note", "fact", "failed_action", "person", "place", "dialog", "task_hint"],
            "scope": "Endpoint-local by default.",
            "persistence": "In-memory by default; use tla_agent_memory_save/load/files for explicit Workspace/AiMemory snapshots during long QA runs.",
        },
        "decision": {
            "fields": [
                "decisionId",
                "time",
                "goal",
                "goalTags",
                "intent",
                "priority",
                "suggestedTool",
                "arguments",
                "reasons",
                "requiresModelText",
                "suggestedDelayMs",
                "pacing",
                "humanization",
                "execute",
                "dryRun",
                "mode",
            ],
            "trace": "Recorded per endpoint by tla_agent_tick and readable through tla_agent_decisions or tla_agent_status.",
            "goalSupport": "Optional goal text plus nav target arguments can steer movement to explicit hexes, visible entity/item approach, retreat/keep-distance, exploration/frontier movement, transition finding, and visible-target following while still using normal typed tools.",
            "humanization": "Skill-level model for deterministic reaction delay, hesitation, and optional explicit mistakes. It is metadata-only unless allowHumanizedMistakes=true.",
        },
        "run": {
            "fields": ["steps", "actionsExecuted", "stoppedReason", "runtime", "policy"],
            "executionPolicy": "execute=false by default; raw input, combat, destructive roster deletion, model-required speech, deployment readiness, permission mode, and admin/hidden/generated surfaces have explicit gates.",
        },
        "tools": [
            "tla_agent_tick",
            "tla_agent_run",
            "tla_agent_status",
            "tla_agent_pause",
            "tla_agent_resume",
            "tla_agent_stop",
            "tla_agent_stop_all",
            "tla_agent_decisions",
            "tla_idle_options",
            "tla_agent_memory",
            "tla_agent_remember",
            "tla_agent_forget",
            "tla_agent_memory_save",
            "tla_agent_memory_load",
            "tla_agent_memory_files",
            "tla_agent_known_people",
            "tla_agent_known_places",
            "tla_agent_known_dialogs",
            "tla_idle_options",
            "tla_dialog_memory",
            "tla_task_memory",
            "tla_route_memory",
            "tla_team_status",
            "tla_team_memory",
            "tla_team_remember",
            "tla_team_forget",
            "tla_team_assign_roles",
            "tla_team_plan",
            "tla_team_tasks",
            "tla_group_rendezvous",
            "tla_follow_agent",
        ],
    }
    world = {
        "schemaVersion": SCHEMA_VERSION,
        "description": "Compact MCP-side world model derived from current client observations, visible events, social context, action suggestions, and advisory memory. It exposes no hidden server state.",
        "tools": [
            "tla_world_summary",
            "tla_area_summary",
            "tla_recent_changes",
            "tla_visible_interactables",
            "tla_interest_points",
            "tla_nav_options",
            "tla_nav_plan",
            "tla_find_nearest_reachable",
            "tla_find_safe_step",
            "tla_find_cover",
            "tla_find_vantage",
            "tla_explore_options",
            "tla_inventory_summary",
            "tla_loot_options",
            "tla_equip_options",
            "tla_ammo_options",
            "tla_healing_options",
            "tla_container_options",
            "tla_combat_options",
            "tla_target_options",
            "tla_retreat_options",
            "tla_reload_options",
            "tla_cover_options",
            "tla_dialog_options",
            "tla_quest_summary",
            "tla_task_options",
            "tla_xp_source_plan",
            "tla_map_transition_options",
            "tla_global_options",
            "tla_travel_plan",
            "tla_enter_options",
            "tla_dialog_memory",
            "tla_task_memory",
            "tla_route_memory",
        ],
        "worldSummary": {
            "fields": ["observation", "area", "changes", "interactables", "interestPoints", "nav", "social", "guidance"],
            "source": "tla_step plus MCP-side summarizers.",
        },
        "area": {
            "fields": ["mode", "map", "globalMap", "chosen", "counts", "dialogActive", "screen"],
            "mode": ["map", "global", "ui"],
        },
        "recentChanges": {
            "fields": ["counts", "speech", "critters", "items", "ui", "commands", "environment", "other"],
            "source": "Bridge events consumed from the endpoint cursor.",
        },
        "interactables": {
            "fields": ["critters", "items", "inventory", "dialog", "global", "utility"],
            "source": "Current observation and tla_available_actions candidate mapping.",
        },
        "interestPoints": {
            "fields": ["kind", "label", "score", "reason", "suggestedTool", "arguments", "hex", "pos"],
            "score": "Advisory priority score where higher means more likely to matter now.",
        },
        "navigation": {
            "fields": ["kind", "targetType", "label", "suggestedTool", "arguments", "reason", "recommendedChecks", "blockedBy", "hex", "pos"],
            "policy": "tla_nav_options is not path-validated; planner tools run client-side checks but still only advise normal typed commands.",
            "planningTools": {
                "tla_nav_plan": "Resolve an explicit or visible target and run path/tactical/optional trace checks.",
                "tla_find_nearest_reachable": "Path-check visible candidates and choose the nearest reachable one.",
                "tla_find_safe_step": "Score nearby local movement hexes with tactical path risk; visible landmarks are optional.",
                "tla_find_cover": "Rank visible obstacle anchors that block movement or line of fire.",
                "tla_find_vantage": "Trace line quality from the current or explicit source hex to visible targets.",
                "tla_explore_options": "Summarize client-visible exploration leads, optionally path-validated.",
            },
        },
        "inventoryLootCombat": {
            "fields": ["style", "counts", "categories", "options", "priorities", "guidance"],
            "policy": "Item and combat helpers use visible item/critter fields, profile style, and current action suggestions only. Compatibility and legality remain normal client/server validation.",
            "itemTags": sorted(ITEM_KIND_KEYWORDS),
            "tools": {
                "tla_inventory_summary": "Group inventory by tags and expose quick healing/reload/equip/drop options.",
                "tla_loot_options": "Rank visible pickups, corpses, and active container actions.",
                "tla_equip_options": "Suggest normal use/move item flows for equipment-like inventory.",
                "tla_ammo_options": "Group ammo-like and weapon-like items and show reload advice.",
                "tla_healing_options": "Suggest usable healing-like items against current health.",
                "tla_container_options": "Show active collection operation or precondition guidance.",
                "tla_combat_options": "Combine target, reload, healing, stamina recovery, retreat, and cover priorities.",
                "tla_target_options": "Rank visible attack candidates with player-target caution.",
                "tla_retreat_options": "Suggest movement/safe-step checks for withdrawal.",
                "tla_reload_options": "Suggest tla_reload arguments from visible items.",
                "tla_cover_options": "Suggest the next cover scan and validation flow.",
            },
        },
        "dialogTaskGlobal": {
            "fields": ["active", "dialogId", "talkerId", "options", "hints", "plan", "blocked", "dialogs", "choices", "taskHints", "globalInterests", "travelHistory", "mapTransitions", "guidance"],
            "policy": "These helpers use only visible dialog/global-map/action fields plus client-visible PDA quest surfaces. Quest summary must not read hidden server quest definitions.",
            "dialogIntents": sorted(ANSWER_INTENT_MARKERS),
            "tools": {
                "tla_dialog_options": "Classify visible dialog answers and suggest tla_dialog_answer arguments.",
                "tla_quest_summary": "Return visible quest/PDA entries and dialog task hints without hidden quest dictionaries.",
                "tla_task_options": "Prioritize visible gates, dialogs, combat, global travel, and ordinary action candidates.",
                "tla_xp_source_plan": "Rank visible XP sources from current observation and return normal typed-tool next steps where possible.",
                "tla_map_transition_options": "Summarize map/global transition candidates and current export gaps.",
                "tla_global_options": "Summarize global-map interests, movement candidates, and enter candidates.",
                "tla_travel_plan": "Pick one global-map move/enter step from an explicit position or visible interest.",
                "tla_enter_options": "List executable in-range global-map enters and blocked visible interests.",
                "tla_dialog_memory": "Read/update endpoint-local visible dialog memory and recent chosen answers.",
                "tla_task_memory": "Read/update endpoint-local visible task hints and current task options.",
                "tla_route_memory": "Read/update endpoint-local visible global-interest, travel-history, and map-transition memory.",
            },
        },
    }
    environment = {
        "schemaVersion": SCHEMA_VERSION,
        "description": "Client-side geometry queries derived from the currently replicated map view. These are advisory and expose no hidden server-only map state.",
        "tools": ["tla_env_path", "tla_env_trace", "tla_env_obstacles", "tla_env_tactical_path"],
        "queries": {
            "path": {
                "tool": "tla_env_path",
                "description": "Compute direct distance, path length, reachability, movability, optional path directions, and optional path hexes from one hex to another.",
                "fields": ["from", "to", "cut", "directDistance", "pathLength", "reachable", "fromMovable", "toMovable", "directions", "pathHexes"],
            },
            "trace": {
                "tool": "tla_env_trace",
                "description": "Trace a shooting/visibility line using the client map trace helper and list visible critters in the trace path.",
                "fields": ["from", "to", "traceHex", "directDistance", "maxDistance", "angle", "reachedTarget", "blocked", "traceHexMovable", "traceHexShootable", "crittersInPath"],
            },
            "obstacles": {
                "tool": "tla_env_obstacles",
                "description": "Scan a visible hex radius for non-movable/non-shootable hexes, critters, and items.",
                "fields": ["center", "radius", "count", "truncated", "obstacles"],
            },
            "tactical_path": {
                "tool": "tla_env_tactical_path",
                "description": "Estimate route length and risk around visible hostile-looking critters, with a bounded waypoint search for a lower-risk detour.",
                "fields": ["from", "to", "cut", "avoidRadius", "searchRadius", "hazardWeight", "basePathLength", "baseRisk", "bestPathLength", "bestRisk", "bestScore", "usesDetour", "bestVia", "candidatesChecked", "maxCandidates", "candidateLimitReached", "threats"],
            },
        },
    }
    orchestration = {
        "schemaVersion": SCHEMA_VERSION,
        "description": "Local process launcher owned by the MCP adapter. It passes normal engine command-line settings and then selects AI bridge endpoints.",
        "roles": list(LAUNCH_ROLES),
        "tools": [
            "tla_launch_options",
            "tla_launch_scene",
            "tla_launch_accounts",
            "tla_launch_two_players",
            "tla_launch",
            "tla_processes",
            "tla_logs",
            "tla_window_screenshot",
            "tla_endpoints",
            "tla_status_all",
            "tla_wait_ready",
            "tla_wait_all_ready",
            "tla_select_endpoint",
            "tla_stop_process",
            "tla_team_status",
            "tla_team_memory",
            "tla_team_remember",
            "tla_team_forget",
            "tla_team_assign_roles",
            "tla_team_plan",
            "tla_team_tasks",
            "tla_group_rendezvous",
            "tla_follow_agent",
        ],
        "endpointTargeting": {
            "default": "Bridge-backed tools use the selected endpoint when no endpoint target is supplied.",
            "endpointId": "Stable id returned by tla_launch or tla_endpoints.",
            "processIdEndpointIndex": "Target a managed process endpoint by processId plus endpointIndex.",
            "direct": "Pass host, port, and optional token for an ad-hoc endpoint.",
            "cursor": "tla_next_events and tla_sync keep independent cursors per endpoint.",
        },
        "diagnostics": {
            "tla_logs": "Workspace or managed-process log tails for runtime errors and script exceptions.",
            "tla_window_screenshot": "Adapter-side OS window screenshot saved under Workspace/AiControlScreenshots by default; use for visual render/particle/GUI QA without adding per-frame render events.",
        },
        "launchDefaults": {
            "role": "server_headless",
            "clientCount": "1 for server/server_headless launches, ignored for standalone clients.",
            "enableAiControl": True,
            "waitForBridge": True,
            "selectFirstEndpoint": True,
        },
        "settingOverrides": {
            "subConfig": "Passed as -ApplySubConfig before command-line setting overrides.",
            "settings": "Object of setting names to values, passed as --Setting.Name value.",
            "autoLoginName": "Shortcut for Auth.AutoLoginName.",
            "autoLoginPassword": "Shortcut for Auth.AutoLoginPassword.",
            "accounts": "Array of account strings or objects with name/password; passed as Auth.AutoLoginNames/Auth.AutoLoginPasswords.",
            "aiControlPort": "Shortcut for AiControl.Port; embedded clients use this as the first port.",
            "aiControlPortStride": "Shortcut for AiControl.PortStride.",
        },
        "launchOptions": "Use tla_launch_options or tla://launch/options for project-derived subconfigs, startup scenes, and base settings.",
    }
    team = {
        "schemaVersion": SCHEMA_VERSION,
        "description": "MCP-side multi-endpoint coordination helpers. They use endpoint-local profiles, memory summaries, and normal client-visible observations.",
        "tools": ["tla_team_status", "tla_team_memory", "tla_team_remember", "tla_team_forget", "tla_team_assign_roles", "tla_team_plan", "tla_team_tasks", "tla_group_rendezvous", "tla_follow_agent"],
        "policy": {
            "authority": "Team tools are advisory or profile-management helpers; gameplay still executes through normal per-endpoint typed commands.",
            "visibility": "Rendezvous plans use current observations from controlled clients and never hidden server positions.",
            "memory": "Shared team memory is adapter-local QA/coordination context; endpoint-local memory remains the source of per-account context.",
        },
        "statusFields": ["endpoint", "profile", "runtime", "memory", "observation", "area"],
        "rendezvousFields": ["leaderEndpointId", "target", "members", "tool", "arguments", "blockedBy"],
        "memoryFields": ["notes", "facts", "bugs", "tasks", "updatedAt"],
        "followFields": ["leaderEndpoint", "followerEndpoint", "leaderArea", "followerArea", "step", "tool", "arguments", "distance", "executed", "blockedBy"],
        "taskFields": ["leaderEndpointId", "members", "assignments", "role", "task", "teamScore", "roleBonus"],
    }
    sections = {
        "protocol": protocol,
        "commands": commands,
        "observation": observation,
        "events": events,
        "social": social,
        "agent": agent,
        "world": world,
        "environment": environment,
        "orchestration": orchestration,
        "team": team,
        "all": {
            "schemaVersion": SCHEMA_VERSION,
            "protocol": protocol,
            "commands": commands,
            "observation": observation,
            "events": events,
            "social": social,
            "agent": agent,
            "world": world,
            "environment": environment,
            "orchestration": orchestration,
            "team": team,
        },
    }
    return sections.get(section, sections["all"])


def act_input_schema(command_types: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "enum": command_types or [command["type"] for command in COMMAND_CATALOG],
                "description": "Command type from tla_schema commands.",
            },
            "targetId": {"type": ["integer", "string"], "description": "Critter/entity id for target commands."},
            "itemId": {"type": ["integer", "string"], "description": "Item id for item commands."},
            "auxId": {"type": ["integer", "string"], "description": "Auxiliary item/entity id, such as ammo or target item."},
            "x": {"type": "integer", "description": "Map hex X."},
            "y": {"type": "integer", "description": "Map hex Y."},
            "screenX": {"type": "integer", "description": "Screen X for mouse_click."},
            "screenY": {"type": "integer", "description": "Screen Y for mouse_click."},
            "intArg": {"type": "integer", "description": "Command-specific integer; see tla_schema commands."},
            "stringArg": {"type": "string", "description": "Command-specific string; see tla_schema commands."},
            "append": {"type": "boolean", "description": "Append to the current client action queue."},
            **endpoint_target_properties(),
            **action_wait_properties(),
            **action_sync_properties(),
        },
        "required": ["type"],
    }


def action_wait_properties() -> dict[str, Any]:
    return {
        "waitForCompletion": {"type": "boolean", "description": "Wait for matching command_completed before returning."},
        "timeoutMs": {"type": "integer", "minimum": 0, "maximum": 60000},
        "pollIntervalMs": {"type": "integer", "minimum": 0, "maximum": 5000},
        "limit": {"type": "integer", "minimum": 1, "maximum": 500, "description": "Maximum events to read per wait poll."},
        "includeEvents": {"type": "boolean", "description": "Include events consumed while waiting in the completion result."},
        "maxReturnedEvents": {"type": "integer", "minimum": 0, "maximum": 1000},
    }


def action_sync_properties() -> dict[str, Any]:
    return {
        "syncAfterCompletion": {"type": "boolean", "description": "After command wait, include a fresh observation/status snapshot."},
        "includeObservation": {"type": "boolean", "description": "Include fresh observation in action sync; default true."},
        "includeStatus": {"type": "boolean", "description": "Include bridge status in action sync."},
    }


def with_action_wait(schema: dict[str, Any]) -> dict[str, Any]:
    schema["properties"] = {**schema.get("properties", {}), **endpoint_target_properties(), **action_wait_properties(), **action_sync_properties()}
    return schema


def environment_from_to_properties(require_to: bool = True) -> dict[str, Any]:
    properties = {
        "fromX": {"type": "integer", "description": "Optional source map hex X; defaults to the chosen critter hex."},
        "fromY": {"type": "integer", "description": "Optional source map hex Y; defaults to the chosen critter hex."},
        "toX": {"type": "integer", "description": "Target map hex X."},
        "toY": {"type": "integer", "description": "Target map hex Y."},
    }
    if not require_to:
        properties["x"] = {"type": "integer", "description": "Optional center hex X; defaults to the chosen critter hex."}
        properties["y"] = {"type": "integer", "description": "Optional center hex Y; defaults to the chosen critter hex."}
    return properties


def environment_query_wait_properties() -> dict[str, Any]:
    return {
        "timeoutMs": {"type": "integer", "minimum": 0, "maximum": 60000, "description": "Maximum time to wait for environment_query_result; defaults to 5000ms, or 15000ms for tactical path queries."},
        "pollIntervalMs": {"type": "integer", "minimum": 0, "maximum": 5000},
        "limit": {"type": "integer", "minimum": 1, "maximum": 500, "description": "Maximum events to read per wait poll."},
    }


def nav_target_properties() -> dict[str, Any]:
    return {
        "toX": {"type": "integer", "description": "Explicit target map hex X."},
        "toY": {"type": "integer", "description": "Explicit target map hex Y."},
        "x": {"type": "integer", "description": "Alias for explicit target/center map hex X."},
        "y": {"type": "integer", "description": "Alias for explicit target/center map hex Y."},
        "targetType": {"type": "string", "description": "Visible command/candidate type, such as move_to_hex, talk_to, pick_item, attack_entity, or loot_critter."},
        "targetTypes": {"type": "array", "items": {"type": "string"}, "description": "Candidate types to consider."},
        "types": {"type": "array", "items": {"type": "string"}, "description": "Alias for targetTypes."},
        "targetId": {"type": ["integer", "string"], "description": "Visible critter/entity id to target."},
        "itemId": {"type": ["integer", "string"], "description": "Visible map item id to target."},
        "id": {"type": ["integer", "string"], "description": "Generic visible entity/item id."},
        "navOptionIndex": {"type": "integer", "minimum": 0, "description": "Index among matching visible navigation candidates; default 0."},
        "maxApproachTargets": {"type": "integer", "minimum": 1, "maximum": 20, "description": "Maximum visible targets checked by goal approach decisions; default 4."},
        "maxApproachCandidates": {"type": "integer", "minimum": 1, "maximum": 24, "description": "Maximum nearby standing hexes checked per approach target; default 3 for agent goals, 12 for direct navigation helpers."},
        "includeRawFallbacks": {"type": "boolean"},
        "includeBlocked": {"type": "boolean"},
        "memoryAware": {"type": "boolean", "description": "Apply endpoint-local failed-route/hazard/crowding memory to advisory scores; default true."},
        "failureMemoryMs": {"type": "integer", "minimum": 0, "description": "Recent failed-action window used by memory-aware route scoring; default 30 minutes."},
        "hazardRadius": {"type": "integer", "minimum": 0, "maximum": 30, "description": "Approximate remembered-hazard radius for advisory route scoring."},
        "crowdingRadius": {"type": "integer", "minimum": 0, "maximum": 30, "description": "Visible-critter crowding radius around route targets."},
    }


def nav_planner_properties() -> dict[str, Any]:
    return {
        **nav_target_properties(),
        "fromX": {"type": "integer", "description": "Optional source map hex X; defaults to chosen critter."},
        "fromY": {"type": "integer", "description": "Optional source map hex Y; defaults to chosen critter."},
        "cut": {"type": "integer", "minimum": 0, "maximum": 1000, "description": "Path cut; defaults to 1 for approach targets and 0 for explicit movement."},
        "simplePath": {"type": "boolean", "description": "Use tla_env_path instead of tla_env_tactical_path for tla_nav_plan."},
        "includeTrace": {"type": "boolean", "description": "Also run tla_env_trace to the target."},
        "includeDirections": {"type": "boolean", "description": "Include directions in path queries where applicable."},
        "maxDirections": {"type": "integer", "minimum": 0, "maximum": 240},
        "avoidRadius": {"type": "integer", "minimum": 0, "maximum": 30},
        "searchRadius": {"type": "integer", "minimum": 0, "maximum": 25},
        "hazardWeight": {"type": "integer", "minimum": 0, "maximum": 100},
        "maxCandidates": {"type": "integer", "minimum": 1, "maximum": 500, "description": "Candidate limit for high-level search and tactical waypoint checks."},
        "avoidPlayers": {"type": "boolean"},
        "maxThreats": {"type": "integer", "minimum": 0, "maximum": 80},
        **environment_query_wait_properties(),
    }


def advisory_option_properties() -> dict[str, Any]:
    return {
        "includeRawFallbacks": {"type": "boolean"},
        "includeBlocked": {"type": "boolean"},
        "maxResults": {"type": "integer", "minimum": 1, "maximum": 100},
        "healthThreshold": {"type": "number", "minimum": 0, "maximum": 1, "description": "Health ratio below which healing becomes high priority; defaults to 0.75."},
        "staminaThreshold": {"type": "number", "minimum": 0, "maximum": 100, "description": "Stamina ratio or percent below which recovery/retreat outranks attacks; defaults to 0.35."},
        "criticalStaminaThreshold": {"type": "number", "minimum": 0, "maximum": 100, "description": "Stamina ratio or percent treated as exhausted; defaults to 0.15."},
        "includeRefundOptions": {"type": "boolean", "description": "Include skill decreases and generated ability removals in progression advice; default false."},
        "allowUnsafeProgression": {"type": "boolean", "description": "QA-only: include progression options even when visible threats would normally block spending points."},
        "radius": {"type": "integer", "minimum": 0, "maximum": 30, "description": "Advisory scan radius for cover/retreat helpers."},
        "maxCandidates": {"type": "integer", "minimum": 1, "maximum": 500},
    }


def global_advisory_properties() -> dict[str, Any]:
    return {
        **advisory_option_properties(),
        "interestType": {"oneOf": [{"type": "string", "enum": list(INTEREST_TYPE_VALUES)}, {"type": "integer"}], "description": "Visible global interest type."},
        "interestId": {"type": ["integer", "string"], "description": "Visible global interest id."},
        "globalOptionIndex": {"type": "integer", "minimum": 0, "description": "Index in observation.globalMap.interests."},
        "targetIndex": {"type": "integer", "minimum": 0, "description": "Alias for globalOptionIndex."},
        "targetMapProtoId": {"type": "string", "description": "Optional desired local map proto for multi-level transitions such as elevators."},
        "x": {"type": "integer", "description": "Explicit global-map X position."},
        "y": {"type": "integer", "description": "Explicit global-map Y position."},
    }


def xp_source_plan_properties() -> dict[str, Any]:
    return {
        **global_advisory_properties(),
        "targetLevel": {"type": "integer", "minimum": 1, "description": "Target character level for the progress summary."},
        "planXpSources": {"type": "boolean", "description": "Also include top XP-source advice in tla_task_options."},
        "allowCombat": {"type": "boolean", "description": "Include visible combat sources; default true for advisory reads."},
        "allowRiskyEncounters": {"type": "boolean", "description": "Reserved host policy hint for encounter-heavy plans."},
        "preferQuests": {"type": "boolean", "description": "Reserved host policy hint for quest-first plans."},
        "includeAdvisorySources": {"type": "boolean", "description": "Include non-executable quest objectives as advisory sources; default true."},
    }


def typed_command_tools() -> list[dict[str, Any]]:
    id_schema = {"type": ["integer", "string"]}
    append_schema = {"type": "boolean", "description": "Append to the current client action queue."}
    say_type_schema = {"type": "string", "enum": list(SAY_TYPE_VALUES), "description": "Speech mode; defaults to normal."}
    hex_props = {
        "x": {"type": "integer", "description": "Map hex X."},
        "y": {"type": "integer", "description": "Map hex Y."},
        "append": append_schema,
    }

    return [
        {
            "name": "tla_move_to_hex",
            "title": "Move To Hex",
            "description": "Queue movement to a map hex.",
            "inputSchema": with_action_wait({"type": "object", "properties": hex_props, "required": ["x", "y"]}),
        },
        {
            "name": "tla_global_move_to",
            "title": "Global Move To",
            "description": "Request global-map group movement to global coordinates.",
            "inputSchema": with_action_wait({"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}, "required": ["x", "y"]}),
        },
        {
            "name": "tla_global_enter_interest",
            "title": "Enter Global Interest",
            "description": "Enter an in-range global-map interest from observation.globalMap.interests.",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {
                    "interestType": {"oneOf": [{"type": "string", "enum": [k for k in INTEREST_TYPE_VALUES if k != "unknown_place"]}, {"type": "integer"}]},
                    "interestId": {"type": ["integer", "string"], "description": "Use id from observation.globalMap.interests."},
                    "mapPid": {"type": "string", "description": "Optional known-place checkpoint map proto id."},
                    "entryName": {"type": "string", "description": "Optional known-place checkpoint entry name."},
                },
                "required": ["interestType", "interestId"],
            }),
        },
        {
            "name": "tla_attack_entity",
            "title": "Attack Entity",
            "description": "Queue an attack on a visible critter.",
            "inputSchema": with_action_wait({"type": "object", "properties": {"targetId": id_schema, "append": append_schema}, "required": ["targetId"]}),
        },
        {
            "name": "tla_attack_hex",
            "title": "Attack Hex",
            "description": "Queue an attack at a map hex.",
            "inputSchema": with_action_wait({"type": "object", "properties": hex_props, "required": ["x", "y"]}),
        },
        {
            "name": "tla_pick_item",
            "title": "Pick Item",
            "description": "Pick or interact with a visible map item or scripted static scenery.",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {
                    "itemId": id_schema,
                    "isStatic": {"type": "boolean", "description": "Set true for observation.mapItems entries with isStatic=true."},
                    "append": append_schema,
                },
                "required": ["itemId"],
            }),
        },
        {
            "name": "tla_pick_hex",
            "title": "Pick Hex",
            "description": "Pick an item from a hex when the exact item id is not known.",
            "inputSchema": with_action_wait({"type": "object", "properties": hex_props, "required": ["x", "y"]}),
        },
        {
            "name": "tla_talk_to",
            "title": "Talk To Critter",
            "description": "Start dialog with an NPC.",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {
                    "targetId": id_schema,
                    "protoId": {"type": "string", "description": "Fallback NPC prototype id when the NPC is static and not listed in visible candidates."},
                    **hex_props,
                    "append": append_schema,
                },
                "anyOf": [{"required": ["targetId"]}, {"required": ["protoId", "x", "y"]}],
            }),
        },
        {
            "name": "tla_group_invite",
            "title": "Invite To Group",
            "description": "Invite a visible player-controlled critter to the chosen player's group.",
            "inputSchema": with_action_wait({"type": "object", "properties": {"targetId": id_schema}, "required": ["targetId"]}),
        },
        {
            "name": "tla_loot_critter",
            "title": "Loot Critter",
            "description": "Open loot for a dead or lootable critter.",
            "inputSchema": with_action_wait({"type": "object", "properties": {"targetId": id_schema, "append": append_schema}, "required": ["targetId"]}),
        },
        {
            "name": "tla_use_item",
            "title": "Use Item",
            "description": "Use an inventory item, optionally on a critter or another item.",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {
                    "itemId": id_schema,
                    "targetId": id_schema,
                    "auxId": id_schema,
                    "useMode": {"type": "string", "description": "Optional use-mode string."},
                    "append": append_schema,
                },
                "required": ["itemId"],
            }),
        },
        {
            "name": "tla_reload",
            "title": "Reload Weapon",
            "description": "Reload a weapon with optional ammo.",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {"itemId": id_schema, "auxId": id_schema, "full": {"type": "boolean"}, "append": append_schema},
                "required": ["itemId"],
            }),
        },
        {
            "name": "tla_unload",
            "title": "Unload Weapon",
            "description": "Unload a weapon.",
            "inputSchema": with_action_wait({"type": "object", "properties": {"itemId": id_schema, "full": {"type": "boolean"}, "append": append_schema}, "required": ["itemId"]}),
        },
        {
            "name": "tla_move_item",
            "title": "Move Inventory Item",
            "description": "Move an inventory item to a critter slot enum value.",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {"itemId": id_schema, "slot": {"type": "integer", "description": "CritterItemSlot enum value."}, "append": append_schema},
                "required": ["itemId", "slot"],
            }),
        },
        {
            "name": "tla_drop_item",
            "title": "Drop Item",
            "description": "Drop an item from inventory.",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {"itemId": id_schema, "count": {"type": "integer", "minimum": 1}, "append": append_schema},
                "required": ["itemId"],
            }),
        },
        {
            "name": "tla_operate_container",
            "title": "Operate Container",
            "description": "Take or put items through the currently opened container/loot UI.",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {
                    "take": {"type": "boolean", "description": "true takes from the collection; false puts from inventory. Defaults to true."},
                    "all": {"type": "boolean", "description": "Move all eligible items. Defaults to true."},
                    "itemId": id_schema,
                    "count": {"type": "integer", "minimum": 1, "description": "Item count when all=false. Defaults to 1."},
                },
            }),
        },
        {
            "name": "tla_toggle_sneak",
            "title": "Toggle Sneak",
            "description": "Toggle sneak mode.",
            "inputSchema": with_action_wait({"type": "object", "properties": {"append": append_schema}}),
        },
        {
            "name": "tla_set_overwatch",
            "title": "Set Overwatch",
            "description": "Hold or clear a SmallGuns overwatch sector.",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {
                    "dir": {"type": "integer", "minimum": 0, "maximum": 5, "description": "Hex direction to watch."},
                    "clear": {"type": "boolean", "description": "Clear the current overwatch sector instead of setting one."},
                },
            }),
        },
        {
            "name": "tla_dialog_answer",
            "title": "Answer Dialog",
            "description": "Send a zero-based answer index to the active dialog.",
            "inputSchema": with_action_wait({"type": "object", "properties": {"answerIndex": {"type": "integer", "minimum": 0}}, "required": ["answerIndex"]}),
        },
        {
            "name": "tla_ui_answer",
            "title": "Answer UI Prompt",
            "description": "Answer the active semantic GUI prompt, such as confirm/yes-no/DialogBox/elevator.",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {
                    "answerIndex": {"type": "integer", "minimum": 0, "description": "Zero-based index from observation.uiPrompt.buttons."},
                    "answerId": {"type": "string", "description": "Optional button id such as yes/no/cancel or an elevator map proto id."},
                },
            }),
        },
        {
            "name": "tla_say",
            "title": "Say",
            "description": "Send player-visible speech through the normal chat/say path.",
            "inputSchema": with_action_wait({"type": "object", "properties": {"text": {"type": "string"}, "sayType": say_type_schema}, "required": ["text"]}),
        },
        {
            "name": "tla_accept_agreement",
            "title": "Accept Agreement",
            "description": "Accept the account agreement through the normal registration path.",
            "inputSchema": with_action_wait({"type": "object", "properties": {}}),
        },
        {
            "name": "tla_generate_critter",
            "title": "Generate Critter",
            "description": "Confirm the chosen critter's current generated appearance/body.",
            "inputSchema": with_action_wait({"type": "object", "properties": {}}),
        },
        {
            "name": "tla_finish_generation",
            "title": "Finish Generation",
            "description": "Apply a default starting stat allocation so a fresh generated critter can leave generation-gated maps.",
            "inputSchema": with_action_wait({"type": "object", "properties": {}}),
        },
        {
            "name": "tla_change_skill",
            "title": "Change Skill",
            "description": "Increase or decrease a character skill through the normal progression server call.",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {
                    "skill": {"type": "string", "enum": list(SKILL_PROPERTY_NAMES), "description": "Skill property name."},
                    "increase": {"type": "boolean", "description": "true increases, false decreases; defaults to true."},
                },
                "required": ["skill"],
            }),
        },
        {
            "name": "tla_change_ability",
            "title": "Change Ability",
            "description": "Add or remove a generated ability modifier through the normal progression server call.",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {
                    "protoId": {"type": "string", "description": "Ability modifier proto id."},
                    "add": {"type": "boolean", "description": "true adds, false removes; defaults to true."},
                },
                "required": ["protoId"],
            }),
        },
        {
            "name": "tla_admin_prepare",
            "title": "Admin Prepare Target",
            "description": "Use an existing admin-panel preparation preset on the chosen or target critter. QA setup only; requires allowAdmin=true and current admin/moderator access.",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {
                    "preset": {"type": "string", "enum": list(ADMIN_PREPARE_PRESETS)},
                    "targetId": id_schema,
                    "reason": {"type": "string", "description": "Audit reason for the admin action."},
                    "allowAdmin": {"type": "boolean", "description": "Must be true; explicit confirmation that this is admin QA setup, not normal play."},
                },
                "required": ["preset", "allowAdmin"],
            }),
        },
        {
            "name": "tla_admin_teleport_to_hex",
            "title": "Admin Teleport To Hex",
            "description": "Teleport the admin's own critter to a current-map hex through the existing admin panel RPC. Requires allowAdmin=true and full admin access.",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {
                    "x": {"type": "integer"},
                    "y": {"type": "integer"},
                    "reason": {"type": "string"},
                    "allowAdmin": {"type": "boolean", "description": "Must be true."},
                },
                "required": ["x", "y", "allowAdmin"],
            }),
        },
        {
            "name": "tla_admin_move_to_map",
            "title": "Admin Move To Map",
            "description": "Move the chosen or target critter to a location/map proto through the existing admin panel RPC. Requires allowAdmin=true and admin/moderator access.",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {
                    "locationPid": {"type": "string"},
                    "mapPid": {"type": "string"},
                    "targetId": id_schema,
                    "reason": {"type": "string"},
                    "allowAdmin": {"type": "boolean", "description": "Must be true."},
                },
                "required": ["locationPid", "mapPid", "allowAdmin"],
            }),
        },
        {
            "name": "tla_admin_to_faction_leader",
            "title": "Admin To Faction Leader",
            "description": "Teleport the admin to a configured faction leader through the existing admin panel RPC. Requires allowAdmin=true and full admin access.",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {
                    "factionKey": {"type": "string"},
                    "reason": {"type": "string"},
                    "allowAdmin": {"type": "boolean", "description": "Must be true."},
                },
                "required": ["factionKey", "allowAdmin"],
            }),
        },
        {
            "name": "tla_admin_spawn_mob_at_target",
            "title": "Admin Spawn Mob At Target",
            "description": "Spawn a critter proto at the chosen or target critter through the existing admin panel RPC. Requires allowAdmin=true and admin/moderator access.",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {
                    "mobPid": {"type": "string"},
                    "targetId": id_schema,
                    "reason": {"type": "string"},
                    "allowAdmin": {"type": "boolean", "description": "Must be true."},
                },
                "required": ["mobPid", "allowAdmin"],
            }),
        },
        {
            "name": "tla_admin_set_weather",
            "title": "Admin Set Weather",
            "description": "Set or clear current-map weather through the existing admin panel RPC. Requires allowAdmin=true and full admin access.",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {
                    "weatherPid": {"type": "string", "description": "Weather proto id; omit or empty to clear current map weather."},
                    "reason": {"type": "string"},
                    "allowAdmin": {"type": "boolean", "description": "Must be true."},
                },
                "required": ["allowAdmin"],
            }),
        },
        {
            "name": "tla_request_roster",
            "title": "Request Roster",
            "description": "Refresh account roster state.",
            "inputSchema": with_action_wait({"type": "object", "properties": {}}),
        },
        {
            "name": "tla_roster_create",
            "title": "Create Roster Character",
            "description": "Create a new account character at a roster index.",
            "inputSchema": with_action_wait({"type": "object", "properties": {"rosterIndex": {"type": "integer", "minimum": 0}}, "required": ["rosterIndex"]}),
        },
        {
            "name": "tla_roster_switch",
            "title": "Switch Roster Character",
            "description": "Switch to an inactive account character by roster index.",
            "inputSchema": with_action_wait({"type": "object", "properties": {"rosterIndex": {"type": "integer", "minimum": 0}}, "required": ["rosterIndex"]}),
        },
        {
            "name": "tla_roster_delete",
            "title": "Delete Roster Character",
            "description": "Delete an inactive account character by roster index.",
            "inputSchema": with_action_wait({"type": "object", "properties": {"rosterIndex": {"type": "integer", "minimum": 0}}, "required": ["rosterIndex"]}),
        },
        {
            "name": "tla_set_resolution",
            "title": "Set Resolution",
            "description": "QA diagnostic: set the client logical resolution through Game.SetResolution.",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {
                    "width": {"type": "integer", "minimum": 1},
                    "height": {"type": "integer", "minimum": 1},
                },
                "required": ["width", "height"],
            }),
        },
        {
            "name": "tla_toggle_fullscreen",
            "title": "Toggle Fullscreen",
            "description": "QA diagnostic: toggle the client fullscreen state through Game.ToggleFullscreen.",
            "inputSchema": with_action_wait({"type": "object", "properties": {}}),
        },
        {
            "name": "tla_clear_actions",
            "title": "Clear Action Queue",
            "description": "Clear queued client actions.",
            "inputSchema": with_action_wait({"type": "object", "properties": {}}),
        },
        {
            "name": "tla_close_screen",
            "title": "Close Screen",
            "description": "Close the active modal/top GUI screen through the normal client TryExit path.",
            "inputSchema": with_action_wait({"type": "object", "properties": {}}),
        },
        {
            "name": "tla_mouse_click",
            "title": "Mouse Click",
            "description": "Raw input fallback for UI surfaces without a semantic command.",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {"screenX": {"type": "integer"}, "screenY": {"type": "integer"}, "button": {"type": "integer", "description": "MouseButton enum value."}},
                "required": ["screenX", "screenY", "button"],
            }),
        },
        {
            "name": "tla_key_press",
            "title": "Key Press",
            "description": "Raw input fallback for keyboard-only UI surfaces.",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {"key": {"type": "integer", "description": "KeyCode enum value."}, "text": {"type": "string"}},
                "required": ["key"],
            }),
        },
    ]


def typed_command_tool_names() -> set[str]:
    return {tool["name"] for tool in typed_command_tools()}


def command_type_to_tool_name(command_type: str) -> str | None:
    for tool_name in typed_command_tool_names():
        if typed_command_type_for_tool(tool_name) == command_type:
            return tool_name
    return None


def command_catalog_entry(command_type: str) -> dict[str, Any] | None:
    for command in COMMAND_CATALOG:
        if command["type"] == command_type:
            return command
    return None


def typed_command_type_for_tool(name: str) -> str:
    return {
        "tla_move_to_hex": "move_to_hex",
        "tla_global_move_to": "global_move_to",
        "tla_global_enter_interest": "global_enter_interest",
        "tla_attack_entity": "attack_entity",
        "tla_attack_hex": "attack_hex",
        "tla_pick_item": "pick_item",
        "tla_pick_hex": "pick_hex",
        "tla_talk_to": "talk_to",
        "tla_group_invite": "group_invite",
        "tla_loot_critter": "loot_critter",
        "tla_use_item": "use_item",
        "tla_reload": "reload",
        "tla_unload": "unload",
        "tla_move_item": "move_item",
        "tla_drop_item": "drop_item",
        "tla_operate_container": "operate_container",
        "tla_toggle_sneak": "toggle_sneak",
        "tla_set_overwatch": "set_overwatch",
        "tla_dialog_answer": "dialog_answer",
        "tla_ui_answer": "ui_answer",
        "tla_say": "say",
        "tla_accept_agreement": "accept_agreement",
        "tla_generate_critter": "generate_critter",
        "tla_finish_generation": "finish_generation",
        "tla_change_skill": "change_skill",
        "tla_change_ability": "change_ability",
        "tla_admin_prepare": "admin_prepare",
        "tla_admin_teleport_to_hex": "admin_teleport_to_hex",
        "tla_admin_move_to_map": "admin_move_to_map",
        "tla_admin_to_faction_leader": "admin_to_faction_leader",
        "tla_admin_spawn_mob_at_target": "admin_spawn_mob_at_target",
        "tla_admin_set_weather": "admin_set_weather",
        "tla_request_roster": "request_roster",
        "tla_roster_create": "roster_create",
        "tla_roster_switch": "roster_switch",
        "tla_roster_delete": "roster_delete",
        "tla_set_resolution": "set_resolution",
        "tla_toggle_fullscreen": "toggle_fullscreen",
        "tla_clear_actions": "clear_actions",
        "tla_close_screen": "close_screen",
        "tla_mouse_click": "mouse_click",
        "tla_key_press": "key_press",
    }[name]


def require_arguments(arguments: dict[str, Any], *names: str) -> None:
    missing = [name for name in names if name not in arguments]
    if missing:
        raise ValueError("Missing required argument(s): " + ", ".join(missing))


def int_arg(arguments: dict[str, Any], name: str, default: int) -> int:
    # dict.get returns None (not the default) for a present-but-null value, and int(None)
    # raises TypeError. Treat explicit JSON null as "absent" and raise ValueError (caught as
    # a -32602 input error) for anything else non-numeric.
    value = arguments.get(name)
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be an integer")


def optional_append(arguments: dict[str, Any], command: dict[str, Any]) -> dict[str, Any]:
    if "append" in arguments:
        command["append"] = arguments["append"]
    return command


def require_admin_confirmation(arguments: dict[str, Any]) -> None:
    if not bool(arguments.get("allowAdmin", False)):
        raise ValueError("Admin tools require allowAdmin=true for explicit QA setup confirmation")


def admin_options(kind: str, **values: Any) -> str:
    parts = [kind]
    for key, value in values.items():
        if value is None:
            continue
        text = str(value).strip()
        if not text:
            continue
        parts.append(f"{key}={text.replace(';', ' ').replace(chr(10), ' ').replace(chr(13), ' ')}")
    return ";".join(parts)


def typed_command_payload(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "tla_move_to_hex":
        require_arguments(arguments, "x", "y")
        command: dict[str, Any] = {"type": "move_to_hex", "x": arguments["x"], "y": arguments["y"]}
        if "cut" in arguments or "intArg" in arguments:
            command["intArg"] = max(0, int(arguments.get("cut", arguments.get("intArg", 0))))
        return optional_append(arguments, command)
    if name == "tla_global_move_to":
        require_arguments(arguments, "x", "y")
        return {"type": "global_move_to", "x": arguments["x"], "y": arguments["y"]}
    if name == "tla_global_enter_interest":
        require_arguments(arguments, "interestType", "interestId")
        interest_type = interest_type_value(arguments["interestType"])
        if interest_type == INTEREST_TYPE_VALUES["unknown_place"]:
            raise ValueError("unknown_place interests are not enterable")

        interest_id = arguments["interestId"]
        command: dict[str, Any] = {"type": "global_enter_interest", "intArg": interest_type}
        if interest_type in {INTEREST_TYPE_VALUES["self"], INTEREST_TYPE_VALUES["group"]}:
            command["x"] = int(interest_id)
        elif interest_type in {INTEREST_TYPE_VALUES["known_place"], INTEREST_TYPE_VALUES["quest_giver"]}:
            string_arg = non_empty_string(interest_id, "interestId")
            if interest_type == INTEREST_TYPE_VALUES["known_place"] and (arguments.get("mapPid") or arguments.get("entryName")):
                map_pid = non_empty_string(arguments.get("mapPid"), "mapPid")
                entry_name = non_empty_string(arguments.get("entryName"), "entryName")
                string_arg = f"{string_arg};map={map_pid};entry={entry_name}"
            command["stringArg"] = string_arg
        elif interest_type in {INTEREST_TYPE_VALUES["camp"], INTEREST_TYPE_VALUES["encounter"], INTEREST_TYPE_VALUES["death_stash"]}:
            command["targetId"] = interest_id
        else:
            raise ValueError("interestType must be self, group, known_place, camp, encounter, quest_giver, or death_stash")
        return command
    if name == "tla_attack_entity":
        require_arguments(arguments, "targetId")
        return optional_append(arguments, {"type": "attack_entity", "targetId": arguments["targetId"]})
    if name == "tla_attack_hex":
        require_arguments(arguments, "x", "y")
        return optional_append(arguments, {"type": "attack_hex", "x": arguments["x"], "y": arguments["y"]})
    if name == "tla_pick_item":
        require_arguments(arguments, "itemId")
        command = {"type": "pick_item", "itemId": arguments["itemId"]}
        if bool(arguments.get("isStatic", False)):
            command["intArg"] = 1
        return optional_append(arguments, command)
    if name == "tla_pick_hex":
        require_arguments(arguments, "x", "y")
        return optional_append(arguments, {"type": "pick_hex", "x": arguments["x"], "y": arguments["y"]})
    if name == "tla_talk_to":
        if "targetId" in arguments:
            return optional_append(arguments, {"type": "talk_to", "targetId": arguments["targetId"]})
        require_arguments(arguments, "protoId", "x", "y")
        return optional_append(arguments, {"type": "talk_to", "stringArg": arguments["protoId"], "x": arguments["x"], "y": arguments["y"]})
    if name == "tla_group_invite":
        require_arguments(arguments, "targetId")
        return {"type": "group_invite", "targetId": arguments["targetId"]}
    if name == "tla_loot_critter":
        require_arguments(arguments, "targetId")
        return optional_append(arguments, {"type": "loot_critter", "targetId": arguments["targetId"]})
    if name == "tla_use_item":
        require_arguments(arguments, "itemId")
        command = {"type": "use_item", "itemId": arguments["itemId"]}
        if "targetId" in arguments:
            command["targetId"] = arguments["targetId"]
        if "auxId" in arguments:
            command["auxId"] = arguments["auxId"]
        if "useMode" in arguments:
            command["stringArg"] = arguments["useMode"]
        return optional_append(arguments, command)
    if name == "tla_reload":
        require_arguments(arguments, "itemId")
        command = {"type": "reload", "itemId": arguments["itemId"], "intArg": 1 if arguments.get("full") else 0}
        if "auxId" in arguments:
            command["auxId"] = arguments["auxId"]
        return optional_append(arguments, command)
    if name == "tla_unload":
        require_arguments(arguments, "itemId")
        return optional_append(arguments, {"type": "unload", "itemId": arguments["itemId"], "intArg": 1 if arguments.get("full") else 0})
    if name == "tla_move_item":
        require_arguments(arguments, "itemId", "slot")
        return optional_append(arguments, {"type": "move_item", "itemId": arguments["itemId"], "intArg": arguments["slot"]})
    if name == "tla_drop_item":
        require_arguments(arguments, "itemId")
        command = {"type": "drop_item", "itemId": arguments["itemId"]}
        if "count" in arguments:
            command["intArg"] = arguments["count"]
        return optional_append(arguments, command)
    if name == "tla_operate_container":
        take = bool(arguments.get("take", True))
        all_items = bool(arguments.get("all", True))
        count = int(arguments.get("count", 1))
        if count < 1:
            raise ValueError("count must be at least 1")
        command = {"type": "operate_container", "intArg": (count << 2) | (1 if take else 0) | (2 if all_items else 0)}
        if "itemId" in arguments:
            command["itemId"] = arguments["itemId"]
        return command
    if name == "tla_toggle_sneak":
        return optional_append(arguments, {"type": "toggle_sneak"})
    if name == "tla_set_overwatch":
        if bool(arguments.get("clear", False)):
            return {"type": "set_overwatch", "intArg": -1}
        require_arguments(arguments, "dir")
        direction = int_arg(arguments, "dir", 0)
        if direction < 0 or direction > 5:
            raise ValueError("dir must be in the 0..5 hex direction range")
        return {"type": "set_overwatch", "intArg": direction}
    if name == "tla_dialog_answer":
        require_arguments(arguments, "answerIndex")
        return {"type": "dialog_answer", "intArg": arguments["answerIndex"]}
    if name == "tla_ui_answer":
        if "answerIndex" not in arguments and "answerId" not in arguments:
            raise ValueError("Missing required argument(s): answerIndex or answerId")
        command: dict[str, Any] = {"type": "ui_answer"}
        if "answerIndex" in arguments:
            command["intArg"] = arguments["answerIndex"]
        else:
            command["intArg"] = -1
        if "answerId" in arguments:
            command["stringArg"] = str(arguments["answerId"])
        return command
    if name == "tla_say":
        require_arguments(arguments, "text")
        text = str(arguments["text"]).strip()
        if not text:
            raise ValueError("text must not be empty")
        return {"type": "say", "stringArg": text, "intArg": say_type_value(arguments.get("sayType", "normal"))}
    if name == "tla_accept_agreement":
        return {"type": "accept_agreement"}
    if name == "tla_generate_critter":
        return {"type": "generate_critter"}
    if name == "tla_finish_generation":
        return {"type": "finish_generation"}
    if name == "tla_change_skill":
        require_arguments(arguments, "skill")
        skill = skill_property_name(arguments["skill"])
        return {"type": "change_skill", "stringArg": skill, "intArg": 1 if bool(arguments.get("increase", True)) else -1}
    if name == "tla_change_ability":
        require_arguments(arguments, "protoId")
        proto_id = str(arguments["protoId"]).strip()
        if not proto_id:
            raise ValueError("protoId must not be empty")
        return {"type": "change_ability", "stringArg": proto_id, "intArg": 1 if bool(arguments.get("add", True)) else -1}
    if name == "tla_admin_prepare":
        require_arguments(arguments, "preset")
        require_admin_confirmation(arguments)
        preset = admin_prepare_preset(arguments["preset"])
        command = {"type": "admin_prepare", "stringArg": admin_options(preset, reason=arguments.get("reason")), "intArg": 1}
        if "targetId" in arguments:
            command["targetId"] = arguments["targetId"]
        return command
    if name == "tla_admin_teleport_to_hex":
        require_arguments(arguments, "x", "y")
        require_admin_confirmation(arguments)
        return {"type": "admin_teleport_to_hex", "x": arguments["x"], "y": arguments["y"], "stringArg": admin_options("teleport", reason=arguments.get("reason")), "intArg": 1}
    if name == "tla_admin_move_to_map":
        require_arguments(arguments, "locationPid", "mapPid")
        require_admin_confirmation(arguments)
        location_pid = non_empty_string(arguments["locationPid"], "locationPid")
        map_pid = non_empty_string(arguments["mapPid"], "mapPid")
        command = {"type": "admin_move_to_map", "stringArg": admin_options("move_to_map", loc=location_pid, map=map_pid, reason=arguments.get("reason")), "intArg": 1}
        if "targetId" in arguments:
            command["targetId"] = arguments["targetId"]
        return command
    if name == "tla_admin_to_faction_leader":
        require_arguments(arguments, "factionKey")
        require_admin_confirmation(arguments)
        return {"type": "admin_to_faction_leader", "stringArg": admin_options("faction_leader", faction=non_empty_string(arguments["factionKey"], "factionKey"), reason=arguments.get("reason")), "intArg": 1}
    if name == "tla_admin_spawn_mob_at_target":
        require_arguments(arguments, "mobPid")
        require_admin_confirmation(arguments)
        command = {"type": "admin_spawn_mob_at_target", "stringArg": admin_options("spawn_mob", mob=non_empty_string(arguments["mobPid"], "mobPid"), reason=arguments.get("reason")), "intArg": 1}
        if "targetId" in arguments:
            command["targetId"] = arguments["targetId"]
        return command
    if name == "tla_admin_set_weather":
        require_admin_confirmation(arguments)
        return {"type": "admin_set_weather", "stringArg": admin_options("weather", weather=arguments.get("weatherPid", ""), reason=arguments.get("reason")), "intArg": 1}
    if name == "tla_request_roster":
        return {"type": "request_roster"}
    if name == "tla_roster_create":
        require_arguments(arguments, "rosterIndex")
        return {"type": "roster_create", "intArg": arguments["rosterIndex"]}
    if name == "tla_roster_switch":
        require_arguments(arguments, "rosterIndex")
        return {"type": "roster_switch", "intArg": arguments["rosterIndex"]}
    if name == "tla_roster_delete":
        require_arguments(arguments, "rosterIndex")
        return {"type": "roster_delete", "intArg": arguments["rosterIndex"]}
    if name == "tla_set_resolution":
        require_arguments(arguments, "width", "height")
        width = int_arg(arguments, "width", 0)
        height = int_arg(arguments, "height", 0)
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive")
        return {"type": "set_resolution", "x": width, "y": height}
    if name == "tla_toggle_fullscreen":
        return {"type": "toggle_fullscreen"}
    if name == "tla_clear_actions":
        return {"type": "clear_actions"}
    if name == "tla_close_screen":
        return {"type": "close_screen"}
    if name == "tla_mouse_click":
        require_arguments(arguments, "screenX", "screenY", "button")
        return {"type": "mouse_click", "screenX": arguments["screenX"], "screenY": arguments["screenY"], "intArg": arguments["button"]}
    if name == "tla_key_press":
        require_arguments(arguments, "key")
        command = {"type": "key_press", "intArg": arguments["key"]}
        if "text" in arguments:
            command["stringArg"] = arguments["text"]
        return command

    raise ValueError(f"Unknown typed command tool: {name}")


def say_type_value(value: Any) -> int:
    key = str(value).strip().lower()
    if key not in SAY_TYPE_VALUES:
        raise ValueError("sayType must be one of: " + ", ".join(SAY_TYPE_VALUES))
    return SAY_TYPE_VALUES[key]


def interest_type_value(value: Any) -> int:
    if isinstance(value, int):
        return value
    key = str(value).strip().lower().replace("-", "_")
    if key not in INTEREST_TYPE_VALUES:
        raise ValueError("interestType must be one of: " + ", ".join(INTEREST_TYPE_VALUES))
    return INTEREST_TYPE_VALUES[key]


def skill_property_name(value: Any) -> str:
    key = str(value).strip()
    if "::" in key:
        key = key.rsplit("::", 1)[-1]
    for name in SKILL_PROPERTY_NAMES:
        if key == name or key.casefold() == name.casefold():
            return name
    raise ValueError("skill must be one of: " + ", ".join(SKILL_PROPERTY_NAMES))


def admin_prepare_preset(value: Any) -> str:
    key = str(value).strip().lower().replace("-", "_")
    if key not in ADMIN_PREPARE_PRESETS:
        raise ValueError("preset must be one of: " + ", ".join(ADMIN_PREPARE_PRESETS))
    return key


def non_empty_string(value: Any, name: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError(f"{name} must not be empty")
    return text


def available_actions(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    response = target_bridge(bridge, arguments).request("observe")
    if "error" in response:
        return response

    payload = response.get("result", response)
    observation = unwrap_observation_payload(payload)
    return {"jsonrpc": "2.0", "id": None, "result": available_actions_payload(payload, observation, arguments)}


def available_actions_payload(payload: Any, observation: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    include_raw = bool(arguments.get("includeRawFallbacks", False))
    include_blocked = bool(arguments.get("includeBlocked", True))
    action_types = observation_action_types(observation)
    actions: list[dict[str, Any]] = []

    for command_type in action_types:
        if not include_raw and command_type in {"mouse_click", "key_press"}:
            continue

        action = build_action_affordance(command_type, observation)
        if include_blocked or action.get("candidates") or not action.get("blockedBy"):
            actions.append(action)

    return {
        "observationSeq": payload.get("observationSeq") if isinstance(payload, dict) else observation.get("seq"),
        "availableTypes": action_types,
        "actions": actions,
        "rawFallbacksIncluded": include_raw,
        "includeBlocked": include_blocked,
        "note": "Advisory only; server validation may still reject a command because of range, visibility, cooldown, dialog, or ownership rules.",
    }


def explain_action(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    command_type = resolve_action_type_argument(arguments)
    catalog = command_catalog_entry(command_type)
    if catalog is None:
        raise ValueError(f"Unknown action type: {command_type}")

    tool_name = command_type_to_tool_name(command_type)
    result: dict[str, Any] = {
        "type": command_type,
        "tool": tool_name,
        "catalog": catalog,
        "argumentSources": action_argument_sources(command_type),
    }

    if bool(arguments.get("includeToolSchema", True)) and tool_name is not None:
        for tool in typed_command_tools():
            if tool["name"] == tool_name:
                result["toolSchema"] = tool["inputSchema"]
                break

    if not bool(arguments.get("staticOnly", False)):
        try:
            response = target_bridge(bridge, arguments).request("observe")
        except OSError as exc:
            result["observationError"] = str(exc)
        else:
            if "error" in response:
                result["observationError"] = response["error"]
            else:
                payload = response.get("result", response)
                observation = unwrap_observation_payload(payload)
                result["current"] = build_action_affordance(command_type, observation)
                if isinstance(payload, dict) and "observationSeq" in payload:
                    result["observationSeq"] = payload["observationSeq"]

    return {"jsonrpc": "2.0", "id": None, "result": result}


def resolve_action_type_argument(arguments: dict[str, Any]) -> str:
    if "type" in arguments:
        return str(arguments["type"])
    if "commandType" in arguments:
        return str(arguments["commandType"])
    if "tool" in arguments:
        tool_name = str(arguments["tool"])
        if tool_name not in typed_command_tool_names():
            raise ValueError(f"Unknown typed tool: {tool_name}")
        return typed_command_type_for_tool(tool_name)
    raise ValueError("Pass type, commandType, or tool")


def observation_action_types(observation: dict[str, Any]) -> list[str]:
    available = observation.get("availableActions")
    command_types = {command["type"] for command in COMMAND_CATALOG}

    if isinstance(available, list):
        result = [str(action) for action in available if str(action) in command_types]
        return result

    return [command["type"] for command in COMMAND_CATALOG]


def observation_screen_state(observation: dict[str, Any]) -> dict[str, Any]:
    screen = observation.get("screen")
    return screen if isinstance(screen, dict) else {}


def modal_screen_active(observation: dict[str, Any]) -> bool:
    screen = observation_screen_state(observation)
    if bool(screen.get("modalActive")):
        return True
    modal_screens = screen.get("modalScreens")
    return isinstance(modal_screens, list) and any(isinstance(entry, dict) for entry in modal_screens)


def active_modal_screen_name(observation: dict[str, Any]) -> str:
    screen = observation_screen_state(observation)
    active_modal = str(screen.get("activeModal") or "").strip()
    if active_modal:
        return active_modal
    top = screen.get("top") if isinstance(screen.get("top"), dict) else {}
    if top.get("modal"):
        return str(top.get("name") or "").strip()
    modal_screens = screen.get("modalScreens")
    if isinstance(modal_screens, list):
        for entry in reversed(modal_screens):
            if isinstance(entry, dict):
                name = str(entry.get("name") or "").strip()
                if name:
                    return name
            elif isinstance(entry, str) and entry.strip():
                return entry.strip()
    active = str(screen.get("active") or "").strip()
    return active


def gui_screen_kind(screen_name: str) -> str:
    return screen_name.rsplit("::", 1)[-1]


def modal_screen_blocker(observation: dict[str, Any]) -> str:
    name = active_modal_screen_name(observation)
    return f"modal screen active: {name}" if name else "modal screen active"


def build_action_affordance(command_type: str, observation: dict[str, Any]) -> dict[str, Any]:
    catalog = command_catalog_entry(command_type) or {"required": [], "description": ""}
    candidates = action_candidates(command_type, observation)
    blocked_by = action_blockers(command_type, observation, candidates)
    tool_name = command_type_to_tool_name(command_type)
    action: dict[str, Any] = {
        "type": command_type,
        "tool": tool_name,
        "description": catalog.get("description", ""),
        "required": catalog.get("required", []),
        "argumentSources": action_argument_sources(command_type),
        "candidates": candidates,
        "blockedBy": blocked_by,
    }

    if candidates:
        action["example"] = candidates[0].get("arguments", {})
    elif not catalog.get("required"):
        action["example"] = {}

    return action


def action_candidates(command_type: str, observation: dict[str, Any]) -> list[dict[str, Any]]:
    critters = [entry for entry in observation.get("critters", []) if isinstance(entry, dict)]
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    chosen_id = chosen.get("id") if isinstance(chosen, dict) else None
    visible_critters = [entry for entry in critters if entry.get("id") != chosen_id]
    live_critters = [entry for entry in visible_critters if entry.get("alive") and not entry.get("dead")]
    dead_critters = [entry for entry in visible_critters if entry.get("dead") or not entry.get("alive", True)]
    map_items = map_items_with_authored_static_scripts(observation)
    inventory = [entry for entry in observation.get("inventory", []) if isinstance(entry, dict)]
    dialog = observation.get("dialog") if isinstance(observation.get("dialog"), dict) else {}
    ui_prompt = observation.get("uiPrompt") if isinstance(observation.get("uiPrompt"), dict) else {}
    admin = observation_admin(observation)

    if command_type == "move_to_hex":
        return hex_candidates(map_items, live_critters, chosen)
    if command_type == "global_move_to":
        return global_move_candidates(observation)
    if command_type == "global_enter_interest":
        return global_enter_interest_candidates(observation)
    if command_type == "attack_entity":
        return [entity_candidate("targetId", entry, "visible critter") for entry in live_critters]
    if command_type == "attack_hex":
        return [hex_candidate(entry.get("hex"), "visible critter hex", {"x": get_hex_value(entry.get("hex"), "x"), "y": get_hex_value(entry.get("hex"), "y")}) for entry in live_critters if isinstance(entry.get("hex"), dict)]
    if command_type == "pick_item":
        return [item_candidate(entry, map_item_interactable_reason(entry)) for entry in map_items if map_item_interactable(entry)]
    if command_type == "pick_hex":
        return [hex_candidate(entry.get("hex"), map_item_interactable_reason(entry), {"x": get_hex_value(entry.get("hex"), "x"), "y": get_hex_value(entry.get("hex"), "y")}) for entry in map_items if map_item_interactable(entry) and isinstance(entry.get("hex"), dict)]
    if command_type == "talk_to":
        return [entity_candidate("targetId", entry, "visible alive dialog NPC") for entry in live_critters if critter_talk_candidate(entry)]
    if command_type == "group_invite":
        return [
            entity_candidate("targetId", entry, "visible player-controlled critter")
            for entry in live_critters
            if entry.get("controlledByPlayer") and entry.get("id") != chosen_id
        ]
    if command_type == "loot_critter":
        return [entity_candidate("targetId", entry, "visible dead or non-alive critter") for entry in dead_critters]
    if command_type == "use_item":
        candidates = timer_use_item_candidates(inventory)
        candidates.extend(inventory_item_candidate(entry, "inventory item with canUse=true") for entry in inventory if entry.get("canUse"))
        candidates.extend(breach_use_item_candidates(inventory, map_items))
        candidates.extend(device_override_use_item_candidates(inventory, visible_critters))
        return candidates
    if command_type in {"reload", "unload"}:
        return [inventory_item_candidate(entry, "inventory item; weapon suitability is server/client validated") for entry in inventory]
    if command_type == "move_item":
        return [inventory_item_candidate(entry, "inventory item; choose slot separately") for entry in inventory]
    if command_type == "drop_item":
        return [drop_item_candidate(entry) for entry in inventory if entry.get("canDrop")]
    if command_type == "operate_container":
        return [{"label": "take all", "reason": "currently opened container or loot UI", "arguments": {"take": True, "all": True}}]
    if command_type == "set_overwatch":
        return overwatch_candidates(chosen)
    if command_type == "dialog_answer" and isinstance(dialog, dict) and dialog.get("active"):
        return [dialog_answer_candidate(entry) for entry in dialog.get("answers", []) if isinstance(entry, dict)]
    if command_type == "ui_answer" and isinstance(ui_prompt, dict) and ui_prompt.get("active"):
        candidates = [ui_prompt_answer_candidate(entry, ui_prompt) for entry in ui_prompt.get("buttons", []) if isinstance(entry, dict)]
        candidates.sort(key=lambda candidate: 0 if candidate.get("enabled", True) else 1)
        return candidates
    if command_type == "say":
        return [{"label": "local speech", "arguments": {"text": "Привет.", "sayType": "normal"}, "reason": "normal player-visible speech"}]
    if command_type in {"accept_agreement", "generate_critter", "finish_generation"}:
        return [{"label": "no arguments", "arguments": {}, "reason": "registration flow command"}]
    if command_type == "change_skill":
        return progression_skill_candidates(observation)
    if command_type == "change_ability":
        return progression_ability_candidates(observation)
    if command_type == "admin_prepare":
        return admin_prepare_candidates(admin, chosen)
    if command_type == "admin_teleport_to_hex":
        return admin_teleport_candidates(observation, chosen)
    if command_type == "admin_move_to_map":
        return admin_default_target_candidates(admin, chosen, "target can be moved to a supplied location/map proto")
    if command_type == "admin_to_faction_leader":
        return [{"label": "faction leader teleport", "arguments": {"factionKey": "TradersFaction", "allowAdmin": True}, "reason": "supply factionKey from faction docs or admin diagnostics"}]
    if command_type == "admin_spawn_mob_at_target":
        return admin_default_target_candidates(admin, chosen, "spawn a supplied mobPid at this target")
    if command_type == "admin_set_weather":
        return [{"label": "clear weather", "arguments": {"weatherPid": "", "allowAdmin": True}, "reason": "empty weatherPid clears current map weather"}]
    if command_type == "roster_create":
        return roster_create_candidates(observation)
    if command_type in {"roster_switch", "roster_delete"}:
        return roster_entry_candidates(observation, command_type)
    if command_type in {"toggle_sneak", "clear_actions", "request_roster"}:
        return [{"label": "no arguments", "arguments": {}, "reason": "command has no required arguments"}]
    if command_type == "close_screen":
        return [{"label": "close active modal screen", "arguments": {}, "reason": "active modal/top GUI screen blocks ordinary world actions"}]
    if command_type in {"mouse_click", "key_press"}:
        return []

    return []


def progression_skill_candidates(observation: dict[str, Any]) -> list[dict[str, Any]]:
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    skills = chosen.get("skills") if isinstance(chosen.get("skills"), list) else []
    candidates: list[dict[str, Any]] = []
    for entry in skills:
        if not isinstance(entry, dict):
            continue
        try:
            skill = skill_property_name(entry.get("id"))
        except ValueError:
            continue
        if bool(entry.get("canIncrease")):
            candidates.append(
                {
                    "label": str(entry.get("name") or skill),
                    "id": skill,
                    "arguments": {"skill": skill, "increase": True},
                    "reason": f"skill can increase; value={entry.get('value')} cost={entry.get('increaseCost')}",
                }
            )
        if bool(entry.get("canDecrease")):
            candidates.append(
                {
                    "label": str(entry.get("name") or skill),
                    "id": skill,
                    "arguments": {"skill": skill, "increase": False},
                    "reason": f"skill can decrease back toward generation minimum; value={entry.get('value')}",
                }
            )
    return candidates


def overwatch_candidates(chosen: dict[str, Any]) -> list[dict[str, Any]]:
    overwatch = chosen.get("overwatch") if isinstance(chosen.get("overwatch"), dict) else {}
    if not overwatch.get("opened"):
        return []

    candidates: list[dict[str, Any]] = []
    if overwatch.get("active"):
        candidates.append(
            {
                "label": "clear overwatch",
                "arguments": {"clear": True},
                "reason": f"current overwatch sector dir={overwatch.get('dir')} remainingMs={overwatch.get('remainingMs')}",
            }
        )

    if overwatch.get("canEnter"):
        for direction in range(6):
            candidates.append(
                {
                    "label": f"watch dir {direction}",
                    "id": direction,
                    "arguments": {"dir": direction},
                    "reason": "SmallGuns overwatch is ready; pick the hex direction covering expected enemy movement",
                }
            )

    return candidates


def progression_ability_candidates(observation: dict[str, Any]) -> list[dict[str, Any]]:
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    abilities = chosen.get("abilities") if isinstance(chosen.get("abilities"), dict) else {}
    available = abilities.get("available") if isinstance(abilities.get("available"), list) else []
    candidates: list[dict[str, Any]] = []
    for entry in available:
        if not isinstance(entry, dict):
            continue
        proto_id = str(entry.get("protoId") or "").strip()
        if not proto_id:
            continue
        if bool(entry.get("canAdd")):
            candidates.append(
                {
                    "label": str(entry.get("name") or proto_id),
                    "id": proto_id,
                    "protoId": proto_id,
                    "arguments": {"protoId": proto_id, "add": True},
                    "reason": f"ability can be opened for {entry.get('skill')} >= {entry.get('skillValue')}",
                }
            )
        if bool(entry.get("canRemove")):
            candidates.append(
                {
                    "label": str(entry.get("name") or proto_id),
                    "id": proto_id,
                    "protoId": proto_id,
                    "arguments": {"protoId": proto_id, "add": False},
                    "reason": "generated ability can be removed/refunded",
                }
            )
    return candidates


def observation_admin(observation: dict[str, Any]) -> dict[str, Any]:
    admin = observation.get("admin")
    return admin if isinstance(admin, dict) else {}


def admin_prepare_candidates(admin: dict[str, Any], chosen: dict[str, Any]) -> list[dict[str, Any]]:
    if not bool(admin.get("available")):
        return []

    presets = admin.get("preparePresets") if isinstance(admin.get("preparePresets"), list) else []
    target_id = admin.get("defaultTargetId") or chosen.get("id")
    candidates: list[dict[str, Any]] = []
    for preset in presets:
        preset_name = str(preset).strip()
        if not preset_name:
            continue
        arguments: dict[str, Any] = {"preset": preset_name, "allowAdmin": True}
        if target_id:
            arguments["targetId"] = target_id
        candidates.append(
            {
                "label": preset_name,
                "id": preset_name,
                "arguments": arguments,
                "reason": "admin preparation preset available for this account; use only for QA setup",
            }
        )
    return candidates


def admin_default_target_candidates(admin: dict[str, Any], chosen: dict[str, Any], reason: str) -> list[dict[str, Any]]:
    if not bool(admin.get("available")):
        return []

    target_id = admin.get("defaultTargetId") or chosen.get("id")
    arguments: dict[str, Any] = {"allowAdmin": True}
    if target_id:
        arguments["targetId"] = target_id
    return [{"label": "chosen target", "id": target_id, "arguments": arguments, "reason": reason}]


def admin_teleport_candidates(observation: dict[str, Any], chosen: dict[str, Any]) -> list[dict[str, Any]]:
    admin = observation_admin(observation)
    if not bool(admin.get("admin")):
        return []
    hex_value = chosen.get("hex") if isinstance(chosen.get("hex"), dict) else {}
    if not hex_value:
        return []
    return [
        {
            "label": "chosen current hex",
            "arguments": {"x": get_hex_value(hex_value, "x"), "y": get_hex_value(hex_value, "y"), "allowAdmin": True},
            "reason": "supply another reachable setup hex when teleporting",
        }
    ]


def map_items_with_authored_static_scripts(observation: dict[str, Any]) -> list[dict[str, Any]]:
    map_items = [entry for entry in observation.get("mapItems", []) if isinstance(entry, dict)]
    authored_items = authored_static_script_items_for_observation(observation)
    if not authored_items:
        return map_items

    seen_ids = {str(entry.get("id")) for entry in map_items if entry.get("id") is not None}
    result = list(map_items)
    for item in authored_items:
        item_id = str(item.get("id"))
        if item_id in seen_ids:
            continue
        seen_ids.add(item_id)
        result.append(item)
    return result


def authored_static_script_items_for_observation(observation: dict[str, Any]) -> list[dict[str, Any]]:
    map_state = observation.get("map") if isinstance(observation.get("map"), dict) else {}
    map_proto_id = str(map_state.get("protoId") or "").strip()
    if not map_proto_id:
        return []
    return authored_static_script_items_for_map(map_proto_id)


def authored_static_script_items_for_map(map_proto_id: str) -> list[dict[str, Any]]:
    if map_proto_id in AUTHORED_STATIC_SCRIPT_ITEM_CACHE:
        return [copy_authored_static_script_item(item) for item in AUTHORED_STATIC_SCRIPT_ITEM_CACHE[map_proto_id]]

    path = authored_map_file(map_proto_id)
    if path is None:
        AUTHORED_STATIC_SCRIPT_ITEM_CACHE[map_proto_id] = []
        return []

    items = parse_authored_static_script_items(path)
    AUTHORED_STATIC_SCRIPT_ITEM_CACHE[map_proto_id] = items
    return [copy_authored_static_script_item(item) for item in items]


def copy_authored_static_script_item(item: dict[str, Any]) -> dict[str, Any]:
    result = dict(item)
    if isinstance(item.get("hex"), dict):
        result["hex"] = dict(item["hex"])
    if isinstance(item.get("statItemArgs"), list):
        result["statItemArgs"] = list(item["statItemArgs"])
    return result


def parse_authored_static_script_items(path: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    in_item = False
    item_id: int | str | None = None
    item_proto = ""
    item_static_script = ""
    item_stat_args: list[str] = []
    item_hex: dict[str, int] | None = None

    def flush_item() -> None:
        if item_id is None or not item_proto or not item_static_script or item_hex is None:
            return
        result.append(
            {
                "id": item_id,
                "protoId": item_proto,
                "name": item_proto,
                "count": 1,
                "ownership": "AuthoredStaticMap",
                "cost": 0,
                "weight": 0,
                "canUse": True,
                "canUseOnSmth": False,
                "canPickUp": False,
                "canDrop": False,
                "canLoot": False,
                "canBarter": False,
                "deteriorable": False,
                "isBroken": False,
                "static": True,
                "isStatic": True,
                "hasDoor": False,
                "hasContainer": False,
                "hasLocker": False,
                "hasMapExit": False,
                "hasMapEntry": False,
                "opened": False,
                "canOpen": False,
                "isGag": False,
                "noHighlight": False,
                "hasStaticScript": True,
                "staticScript": item_static_script,
                "statItemArgs": list(item_stat_args),
                "hex": dict(item_hex),
            }
        )

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line == "[Item]":
            if in_item:
                flush_item()
            in_item = True
            item_id = None
            item_proto = ""
            item_static_script = ""
            item_stat_args = []
            item_hex = None
            continue
        if line.startswith("[") and line.endswith("]"):
            if in_item:
                flush_item()
            in_item = False
            continue
        if not in_item:
            continue

        if line.startswith("$Id"):
            raw_id = line.split("=", 1)[1].strip() if "=" in line else ""
            try:
                item_id = int(raw_id)
            except ValueError:
                item_id = raw_id or None
            continue
        if line.startswith("$Proto"):
            item_proto = line.split("=", 1)[1].strip() if "=" in line else ""
            continue
        if line.startswith("StaticScript"):
            item_static_script = line.split("=", 1)[1].strip() if "=" in line else ""
            continue
        if line.startswith("StatItemArgs"):
            value = line.split("=", 1)[1].strip() if "=" in line else ""
            item_stat_args = [part for part in value.split() if part]
            continue

        hex_match = FOMAP_HEX_VALUE_RE.match(line)
        if hex_match is not None:
            item_hex = {"x": int(hex_match.group(1)), "y": int(hex_match.group(2))}

    if in_item:
        flush_item()
    return result


def map_item_interactable(entry: dict[str, Any]) -> bool:
    return bool(entry.get("canUse") or entry.get("canPickUp") or entry.get("hasDoor") or entry.get("hasContainer") or entry.get("hasLocker") or entry.get("hasStaticScript"))


def map_item_interactable_reason(entry: dict[str, Any]) -> str:
    if entry.get("isStatic") and entry.get("hasStaticScript"):
        return "scripted static scenery"
    if entry.get("canUse") or entry.get("canPickUp"):
        return "map item with canUse=true or canPickUp=true"
    if entry.get("hasDoor"):
        return "visible door map item"
    if entry.get("hasContainer") or entry.get("hasLocker"):
        return "visible container or locker map item"
    if entry.get("hasStaticScript"):
        return "scripted static scenery"
    return "interactable map item"


def action_blockers(command_type: str, observation: dict[str, Any], candidates: list[dict[str, Any]]) -> list[str]:
    blockers: list[str] = []
    available = observation_action_types(observation)
    if command_type not in available:
        blockers.append("not listed in observation.availableActions")

    if command_type in MODAL_BLOCKED_COMMAND_TYPES and modal_screen_active(observation):
        blockers.append(modal_screen_blocker(observation))

    if command_type in {
        "move_to_hex",
        "attack_entity",
        "attack_hex",
        "pick_item",
        "pick_hex",
        "talk_to",
        "group_invite",
        "loot_critter",
        "use_item",
        "reload",
        "unload",
        "move_item",
        "drop_item",
        "operate_container",
        "toggle_sneak",
        "set_overwatch",
        "clear_actions",
        "change_skill",
        "change_ability",
    }:
        if not observation.get("hasChosen"):
            blockers.append("observation.hasChosen=false")
        if command_type not in {"change_skill", "change_ability"} and not observation.get("hasMap"):
            blockers.append("observation.hasMap=false")

    if command_type == "operate_container":
        active_collection = observation.get("activeCollection") if isinstance(observation.get("activeCollection"), dict) else {}
        if not active_collection.get("active"):
            blockers.append("observation.activeCollection.active=false")
        received_count = active_collection_received_count(active_collection)
        if received_count is not None and received_count <= 0:
            blockers.append("observation.activeCollection.receivedCount=0 (no items to take; put-from-inventory with take=false still allowed)")

    if command_type in {"global_move_to", "global_enter_interest"}:
        global_map = observation.get("globalMap") if isinstance(observation.get("globalMap"), dict) else {}
        if not observation.get("hasChosen"):
            blockers.append("observation.hasChosen=false")
        if not global_map.get("active"):
            blockers.append("observation.globalMap.active=false")

    if command_type == "dialog_answer":
        dialog = observation.get("dialog") if isinstance(observation.get("dialog"), dict) else {}
        if not dialog.get("active"):
            blockers.append("dialog.active=false")

    if command_type == "ui_answer":
        ui_prompt = observation.get("uiPrompt") if isinstance(observation.get("uiPrompt"), dict) else {}
        if not ui_prompt.get("active"):
            blockers.append("observation.uiPrompt.active=false")

    if command_type == "say" and not observation.get("connected"):
        blockers.append("observation.connected=false")

    if command_type == "close_screen" and not modal_screen_active(observation):
        blockers.append("screen.modalActive=false")

    if command_type == "accept_agreement":
        account = observation.get("account") if isinstance(observation.get("account"), dict) else {}
        if not account.get("connected"):
            blockers.append("account.connected=false")
        if account.get("agreementAccepted"):
            blockers.append("account.agreementAccepted=true")

    if command_type == "generate_critter":
        account = observation.get("account") if isinstance(observation.get("account"), dict) else {}
        chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
        if not account.get("agreementAccepted"):
            blockers.append("account.agreementAccepted=false")
        if not observation.get("hasChosen"):
            blockers.append("observation.hasChosen=false")
        if chosen.get("isBodyGenerated"):
            blockers.append("chosen.isBodyGenerated=true")

    if command_type == "finish_generation":
        account = observation.get("account") if isinstance(observation.get("account"), dict) else {}
        chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
        if not account.get("agreementAccepted"):
            blockers.append("account.agreementAccepted=false")
        if not observation.get("hasChosen"):
            blockers.append("observation.hasChosen=false")
        if not chosen.get("isBodyGenerated"):
            blockers.append("chosen.isBodyGenerated=false")
        if int(chosen.get("unspentStatPoints") or 0) == 0:
            blockers.append("chosen.unspentStatPoints=0")

    if command_type in {"change_skill", "change_ability"}:
        account = observation.get("account") if isinstance(observation.get("account"), dict) else {}
        chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
        if account.get("agreementAccepted") is False:
            blockers.append("account.agreementAccepted=false")
        if chosen.get("isBodyGenerated") is False:
            blockers.append("chosen.isBodyGenerated=false")

    if command_type == "set_overwatch":
        chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
        overwatch = chosen.get("overwatch") if isinstance(chosen.get("overwatch"), dict) else {}
        if not overwatch.get("opened"):
            blockers.append("chosen.overwatch.opened=false")
        if not overwatch.get("canEnter") and not overwatch.get("active"):
            reason = str(overwatch.get("blockedReason") or "unknown")
            blockers.append(f"chosen.overwatch.canEnter=false:{reason}")

    if command_type in ADMIN_COMMAND_TYPES:
        admin = observation_admin(observation)
        if not admin.get("available"):
            blockers.append("observation.admin.available=false")
        if command_type in {"admin_prepare", "admin_move_to_map", "admin_spawn_mob_at_target"}:
            if not observation.get("hasChosen") and not admin.get("defaultTargetId"):
                blockers.append("no default admin target")
        if command_type in {"admin_teleport_to_hex", "admin_to_faction_leader", "admin_set_weather"} and not admin.get("admin"):
            blockers.append("observation.admin.admin=false")
        if command_type in {"admin_teleport_to_hex", "admin_set_weather"} and not observation.get("hasMap"):
            blockers.append("observation.hasMap=false")
        blockers.append("requires explicit allowAdmin=true")

    if command_type.startswith("roster_"):
        # Only roster_create/roster_switch/roster_delete reach here; request_roster has the
        # "request_" prefix, so no per-type exemption is needed.
        roster = observation_roster(observation)
        if not roster:
            blockers.append("account.roster is missing")
        if roster and not roster.get("canManageHere"):
            blockers.append("account.roster.canManageHere=false")

    required = (command_catalog_entry(command_type) or {}).get("required", [])
    if required and not candidates:
        blockers.append("no visible candidates for required arguments")

    return blockers


def active_collection_received_count(active_collection: dict[str, Any]) -> int | None:
    value = active_collection.get("receivedCount")
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def action_argument_sources(command_type: str) -> dict[str, str]:
    sources = {
        "move_to_hex": {"x/y": "Choose a reachable map hex; visible critter/item hexes can be used as landmarks."},
        "global_move_to": {"x/y": "Choose global map coordinates within observation.globalMap.size; interest positions can be used as landmarks."},
        "global_enter_interest": {
            "interestType/interestId": "Use type and id from an in-range entry in observation.globalMap.interests.",
            "mapPid/entryName": "Optional known-place checkpoint pair; server validates that the player has opened it.",
        },
        "attack_entity": {"targetId": "Use id from observation.critters where alive=true and isChosen=false."},
        "attack_hex": {"x/y": "Use a target hex, often from a visible critter hex."},
        "pick_item": {
            "itemId": "Use id from observation.mapItems where canUse=true/canPickUp=true or hasStaticScript=true.",
            "isStatic": "Set true for entries with isStatic=true.",
        },
        "pick_hex": {"x/y": "Use hex from observation.mapItems where canUse=true/canPickUp=true or hasStaticScript=true."},
        "talk_to": {
            "targetId": "Use id from observation.critters where alive=true, controlledByPlayer=false, notTalkable=false, inCombat=false, and dialogId is non-empty.",
            "protoId+x/y": "Fallback for authored static NPCs known by quest logic when visible candidates are missing; server still validates range, prototype, and dialog availability.",
        },
        "loot_critter": {"targetId": "Use id from observation.critters where dead=true or alive=false."},
        "use_item": {"itemId": "Use id from observation.inventory where canUse=true.", "targetId/auxId": "Optional visible critter/item ids.", "useMode": "Optional typed wrapper string such as timer:<seconds> for timer-capable explosives."},
        "reload": {"itemId": "Use id from observation.inventory for a weapon.", "auxId": "Optional ammo item id from inventory."},
        "unload": {"itemId": "Use id from observation.inventory for a weapon."},
        "move_item": {"itemId": "Use id from observation.inventory.", "slot": "CritterItemSlot enum value."},
        "drop_item": {"itemId": "Use id from observation.inventory where canDrop=true.", "count": "Optional stack count."},
        "operate_container": {"take/all": "Call after pick_item, pick_hex, or loot_critter opens a collection and a receive_items event arrives."},
        "toggle_sneak": {},
        "set_overwatch": {"dir": "Use hex direction 0..5. observation.chosen.overwatch reports active dir and readiness.", "clear": "Set intArg=-1 / clear=true to drop the held sector."},
        "dialog_answer": {"answerIndex": "Use index from observation.dialog.answers."},
        "ui_answer": {"answerIndex": "Use index from observation.uiPrompt.buttons.", "answerId": "Optional id from observation.uiPrompt.buttons when easier than index."},
        "say": {"text": "Short player-visible speech text.", "sayType": "Optional speech mode: normal, shout, whisper, or emote."},
        "change_skill": {"skill": "Use id from observation.chosen.skills where canIncrease/canDecrease is true.", "increase": "true increases, false decreases."},
        "change_ability": {"protoId": "Use protoId from observation.chosen.abilities.available.", "add": "true opens, false removes/refunds a generated ability."},
        "admin_prepare": {"preset": "Use observation.admin.preparePresets.", "targetId": "Defaults to observation.admin.defaultTargetId / chosen.id.", "allowAdmin": "Must be true for QA setup."},
        "admin_teleport_to_hex": {"x/y": "Choose a current-map setup hex.", "allowAdmin": "Must be true for QA setup."},
        "admin_move_to_map": {"locationPid/mapPid": "Use authored proto ids from docs, launch options, or known test setup.", "targetId": "Defaults to chosen.", "allowAdmin": "Must be true for QA setup."},
        "admin_to_faction_leader": {"factionKey": "Use a configured faction key.", "allowAdmin": "Must be true for QA setup."},
        "admin_spawn_mob_at_target": {"mobPid": "Use an authored critter proto id.", "targetId": "Defaults to chosen.", "allowAdmin": "Must be true for QA setup."},
        "admin_set_weather": {"weatherPid": "Use an authored WeatherType proto id, or empty to clear.", "allowAdmin": "Must be true for QA setup."},
        "accept_agreement": {},
        "generate_critter": {},
        "finish_generation": {},
        "request_roster": {},
        "roster_create": {"rosterIndex": "Use observation.account.roster.count when canManageHere=true and count < max."},
        "roster_switch": {"rosterIndex": "Use inactive entry.index from observation.account.roster.entries."},
        "roster_delete": {"rosterIndex": "Use inactive entry.index from observation.account.roster.entries."},
        "close_screen": {"screen": "Use when observation.screen.modalActive=true and no more specific semantic command should handle that modal."},
        "clear_actions": {},
        "mouse_click": {"screenX/screenY/button": "Raw input fallback; prefer semantic tools first."},
        "key_press": {"key/text": "Raw input fallback; prefer semantic tools first."},
    }
    return sources.get(command_type, {})


def hex_candidates(map_items: list[dict[str, Any]], critters: list[dict[str, Any]], chosen: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for entry in map_items[:5]:
        if isinstance(entry.get("hex"), dict):
            label = "map exit" if entry.get("hasMapExit") else "map item" if map_item_interactable(entry) or entry.get("hasDoor") or entry.get("hasContainer") or entry.get("hasLocker") else "map landmark"
            candidates.append(hex_candidate(entry["hex"], f"{label} {entry.get('protoId', entry.get('id'))}", {"x": get_hex_value(entry["hex"], "x"), "y": get_hex_value(entry["hex"], "y")}))
    for entry in critters[:5]:
        if isinstance(entry.get("hex"), dict):
            candidates.append(hex_candidate(entry["hex"], f"visible critter {entry.get('name', entry.get('id'))}", {"x": get_hex_value(entry["hex"], "x"), "y": get_hex_value(entry["hex"], "y")}))
    if not candidates and isinstance(chosen.get("hex"), dict):
        candidates.append(hex_candidate(chosen["hex"], "chosen current hex", {"x": get_hex_value(chosen["hex"], "x"), "y": get_hex_value(chosen["hex"], "y")}))
    return candidates


def global_move_candidates(observation: dict[str, Any]) -> list[dict[str, Any]]:
    global_map = observation.get("globalMap") if isinstance(observation.get("globalMap"), dict) else {}
    if not global_map.get("active"):
        return []

    candidates: list[dict[str, Any]] = []
    pos = global_map.get("pos") if isinstance(global_map.get("pos"), dict) else {}
    size = global_map.get("size") if isinstance(global_map.get("size"), dict) else {}
    if isinstance(pos, dict):
        width = int(size.get("width") or 0)
        height = int(size.get("height") or 0)
        x = get_hex_value(pos, "x")
        y = get_hex_value(pos, "y")
        nearby_offsets = ((10, 0), (-10, 0), (0, 10), (0, -10), (10, 10), (10, -10), (-10, 10), (-10, -10))
        seen_positions: set[tuple[int, int]] = set()
        for dx, dy in nearby_offsets:
            target_x = x + dx
            target_y = y + dy
            if width > 0:
                target_x = max(0, min(target_x, width - 1))
            if height > 0:
                target_y = max(0, min(target_y, height - 1))
            if (target_x, target_y) == (x, y) or (target_x, target_y) in seen_positions:
                continue
            seen_positions.add((target_x, target_y))
            candidates.append(
                {
                    "label": "nearby global position",
                    "pos": {"x": target_x, "y": target_y},
                    "reason": "small movement from current global position",
                    "arguments": {"x": target_x, "y": target_y},
                }
            )

    for interest in global_map.get("interests", [])[:5]:
        if isinstance(interest, dict) and isinstance(interest.get("pos"), dict):
            pos = interest["pos"]
            candidates.append(
                {
                    "label": f"global interest {interest.get('type', interest.get('id'))}",
                    "pos": pos,
                    "reason": "visible global-map interest position",
                    "arguments": {"x": get_hex_value(pos, "x"), "y": get_hex_value(pos, "y")},
                }
            )

    return candidates


def global_enter_interest_candidates(observation: dict[str, Any]) -> list[dict[str, Any]]:
    global_map = observation.get("globalMap") if isinstance(observation.get("globalMap"), dict) else {}
    if not global_map.get("active"):
        return []

    result: list[dict[str, Any]] = []
    for interest in global_map.get("interests", []):
        if not isinstance(interest, dict) or not interest.get("enterable") or not interest.get("inRange"):
            continue
        interest_type = observed_interest_type_name(interest)
        if interest_type == "unknown_place":
            continue
        result.append(
            {
                "label": f"{interest_type} {interest.get('id')}",
                "id": interest.get("id"),
                "pos": interest.get("pos"),
                "radius": interest.get("radius"),
                "distance": interest.get("distance"),
                "reason": "in-range enterable global-map interest",
                "arguments": {"interestType": interest_type, "interestId": interest.get("id")},
            }
        )
    return result


def entity_candidate(argument_name: str, entry: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "label": entry.get("name") or entry.get("protoId") or str(entry.get("id")),
        "id": entry.get("id"),
        "protoId": entry.get("protoId"),
        "hex": entry.get("hex"),
        "reason": reason,
        "arguments": {argument_name: entry.get("id")},
    }


def critter_talk_candidate(entry: dict[str, Any]) -> bool:
    dialog_id = entry.get("dialogId")
    if not isinstance(dialog_id, str) or not dialog_id:
        return False
    if entry.get("controlledByPlayer") or entry.get("notTalkable") or entry.get("inCombat"):
        return False
    return True


def item_candidate(entry: dict[str, Any], reason: str) -> dict[str, Any]:
    arguments = {"itemId": entry.get("id")}
    if entry.get("isStatic") is True:
        arguments["isStatic"] = True
    candidate = {
        "label": entry.get("protoId") or str(entry.get("id")),
        "id": entry.get("id"),
        "protoId": entry.get("protoId"),
        "hex": entry.get("hex"),
        "reason": reason,
        "arguments": arguments,
    }
    for key in (
        "static",
        "isStatic",
        "canUse",
        "canPickUp",
        "hasDoor",
        "hasContainer",
        "hasLocker",
        "hasMapExit",
        "hasMapEntry",
        "opened",
        "canOpen",
        "isGag",
        "noHighlight",
        "hasStaticScript",
        "lockerLocked",
        "lockerNoOpen",
    ):
        if key in entry:
            candidate[key] = entry.get(key)
    return candidate


def inventory_item_candidate(entry: dict[str, Any], reason: str) -> dict[str, Any]:
    candidate = item_candidate(entry, reason)
    candidate["slot"] = entry.get("slot")
    return candidate


def item_visual_feedback(entry: dict[str, Any]) -> dict[str, Any]:
    return entry.get("visualFeedback") if isinstance(entry.get("visualFeedback"), dict) else {}


def item_visual_feedback_labels(entry: dict[str, Any]) -> list[str]:
    visual_feedback = item_visual_feedback(entry)
    labels = visual_feedback.get("labels") if isinstance(visual_feedback.get("labels"), list) else []
    return [str(label) for label in labels]


def item_has_visual_feedback_label(entry: dict[str, Any], label: str) -> bool:
    return label in item_visual_feedback_labels(entry)


def critter_has_visual_feedback_label(entry: dict[str, Any], label: str) -> bool:
    return item_has_visual_feedback_label(entry, label)


def breach_inventory_item(entry: dict[str, Any]) -> bool:
    text = f"{entry.get('protoId', '')} {entry.get('name', '')}".casefold()
    return bool(entry.get("canUseOnSmth")) and "breach" in text


def device_override_inventory_item(entry: dict[str, Any]) -> bool:
    text = f"{entry.get('protoId', '')} {entry.get('name', '')}".casefold()
    return bool(entry.get("canUseOnSmth")) and ("override" in text or "relay" in text)


def timer_capable_inventory_item(entry: dict[str, Any]) -> bool:
    return entry.get("id") is not None and bool(entry.get("canUse")) and bool(item_visual_feedback(entry).get("timerCapable"))


def timer_use_item_candidates(inventory: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for item in inventory:
        if not timer_capable_inventory_item(item):
            continue

        candidate = inventory_item_candidate(item, f"timer-capable explosive; arm with {DEFAULT_EXPLOSIVE_TIMER_SECONDS}-second fuse")
        candidate["arguments"] = {"itemId": item.get("id"), "useMode": f"timer:{DEFAULT_EXPLOSIVE_TIMER_SECONDS}"}
        candidate["timerSeconds"] = DEFAULT_EXPLOSIVE_TIMER_SECONDS
        candidate["visualFeedback"] = item.get("visualFeedback")
        candidates.append(candidate)

    return candidates


def breach_use_item_candidates(inventory: list[dict[str, Any]], map_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    targets = [entry for entry in map_items if entry.get("id") is not None and item_has_visual_feedback_label(entry, BREACH_VISUAL_LABEL)]
    if not targets:
        return []

    candidates: list[dict[str, Any]] = []
    use_on_items = [entry for entry in inventory if entry.get("id") is not None and breach_inventory_item(entry)]
    for item in use_on_items:
        for target in targets:
            candidate = inventory_item_candidate(item, "usable breach item for visible BRCH target")
            candidate["arguments"] = {"itemId": item.get("id"), "auxId": target.get("id")}
            candidate["targetItem"] = {
                "id": target.get("id"),
                "protoId": target.get("protoId"),
                "hex": target.get("hex"),
                "visualFeedback": target.get("visualFeedback"),
            }
            candidate["targetItemId"] = target.get("id")
            candidate["visualLabel"] = BREACH_VISUAL_LABEL
            candidates.append(candidate)

    return candidates


def device_override_use_item_candidates(inventory: list[dict[str, Any]], critters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    targets = [entry for entry in critters if entry.get("id") is not None and critter_has_visual_feedback_label(entry, DEVICE_OVERRIDE_VISUAL_LABEL)]
    if not targets:
        return []

    candidates: list[dict[str, Any]] = []
    override_items = [entry for entry in inventory if entry.get("id") is not None and device_override_inventory_item(entry)]
    for item in override_items:
        for target in targets:
            candidate = inventory_item_candidate(item, "device override tool for visible OVR technical device")
            candidate["arguments"] = {"itemId": item.get("id"), "targetId": target.get("id")}
            candidate["targetCritter"] = {
                "id": target.get("id"),
                "protoId": target.get("protoId"),
                "name": target.get("name"),
                "hex": target.get("hex"),
                "visualFeedback": target.get("visualFeedback"),
            }
            candidate["targetCritterId"] = target.get("id")
            candidate["visualLabel"] = DEVICE_OVERRIDE_VISUAL_LABEL
            candidates.append(candidate)

    return candidates


def drop_item_candidate(entry: dict[str, Any]) -> dict[str, Any]:
    candidate = inventory_item_candidate(entry, "inventory item with canDrop=true")
    candidate["arguments"] = {"itemId": entry.get("id"), "count": entry.get("count", 1)}
    return candidate


def hex_candidate(hex_value: Any, reason: str, arguments: dict[str, Any]) -> dict[str, Any]:
    return {
        "label": reason,
        "hex": hex_value,
        "reason": reason,
        "arguments": arguments,
    }


def dialog_answer_candidate(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "label": entry.get("text", f"answer {entry.get('index')}"),
        "reason": "active dialog answer",
        "arguments": {"answerIndex": entry.get("index")},
    }


def ui_prompt_answer_candidate(entry: dict[str, Any], ui_prompt: dict[str, Any]) -> dict[str, Any]:
    arguments: dict[str, Any] = {}
    if "index" in entry:
        arguments["answerIndex"] = entry.get("index")
    button_id = str(entry.get("id") or "").strip()
    if button_id:
        arguments["answerId"] = button_id

    reason_parts = [f"active {ui_prompt.get('kind', 'ui')} prompt"]
    role = str(entry.get("role") or "").strip()
    if role:
        reason_parts.append(f"role={role}")
    if bool(entry.get("dangerous")):
        reason_parts.append("dangerous")
    if entry.get("enabled") is False:
        reason_parts.append("disabled")

    return {
        "label": entry.get("text") or button_id or f"answer {entry.get('index')}",
        "id": button_id or entry.get("index"),
        "role": role,
        "dangerous": bool(entry.get("dangerous")),
        "enabled": entry.get("enabled", True),
        "reason": "; ".join(reason_parts),
        "arguments": arguments,
    }


def roster_create_candidates(observation: dict[str, Any]) -> list[dict[str, Any]]:
    roster = observation_roster(observation)
    if not roster or not roster.get("canManageHere"):
        return []

    count = roster.get("count", 0)
    max_count = roster.get("max", 0)
    if isinstance(count, int) and isinstance(max_count, int) and count < max_count:
        return [{"label": f"create roster slot {count}", "reason": "next empty roster slot", "arguments": {"rosterIndex": count}}]
    return []


def roster_entry_candidates(observation: dict[str, Any], command_type: str) -> list[dict[str, Any]]:
    roster = observation_roster(observation)
    if not roster or not roster.get("canManageHere"):
        return []

    result: list[dict[str, Any]] = []
    for entry in roster.get("entries", []):
        if not isinstance(entry, dict) or entry.get("active"):
            continue
        result.append(
            {
                "label": entry.get("name") or f"roster {entry.get('index')}",
                "id": entry.get("id"),
                "reason": "inactive roster entry",
                "arguments": {"rosterIndex": entry.get("index")},
            }
        )
    return result


def observation_roster(observation: dict[str, Any]) -> dict[str, Any]:
    account = observation.get("account")
    if not isinstance(account, dict):
        return {}
    roster = account.get("roster")
    return roster if isinstance(roster, dict) else {}


def get_hex_value(hex_value: Any, name: str) -> Any:
    if isinstance(hex_value, dict):
        return hex_value.get(name)
    return None


def advance_events_cursor(bridge: Bridge, response: dict[str, Any]) -> None:
    if "error" in response:
        return

    result = response.get("result", {})
    if not isinstance(result, dict):
        return

    events = result.get("events") or []
    if isinstance(events, list) and events:
        seq = events[-1].get("seq", bridge.events_cursor)
        if isinstance(seq, int):
            bridge.events_cursor = max(bridge.events_cursor, seq)
        return

    latest_seq = result.get("latestSeq", bridge.events_cursor)
    if isinstance(latest_seq, int):
        bridge.events_cursor = max(bridge.events_cursor, latest_seq)


def wait_command_completion(bridge: Bridge, arguments: dict[str, Any]) -> dict[str, Any]:
    require_arguments(arguments, "commandSeq")

    command_seq = arguments["commandSeq"]
    if not isinstance(command_seq, int):
        raise ValueError("commandSeq must be an integer")

    timeout_ms = int_arg(arguments, "timeoutMs", 3000)
    poll_interval_ms = int_arg(arguments, "pollIntervalMs", 100)
    limit = int_arg(arguments, "limit", 100)
    include_events = arguments.get("includeEvents", True)
    max_returned_events = int_arg(arguments, "maxReturnedEvents", 100)

    timeout_ms = max(0, min(timeout_ms, 60000))
    poll_interval_ms = max(0, min(poll_interval_ms, 5000))
    limit = max(1, min(limit, 500))
    max_returned_events = max(0, min(max_returned_events, 1000))

    deadline = time.monotonic() + timeout_ms / 1000.0
    last_result: dict[str, Any] = {}
    collected_events: list[dict[str, Any]] = []
    events_truncated = False

    while True:
        response = bridge.request("events", {"afterSeq": bridge.events_cursor, "limit": limit})
        advance_events_cursor(bridge, response)

        if "error" in response:
            return response

        result = response.get("result", {})
        if isinstance(result, dict):
            last_result = result
            events = result.get("events") or []
            if isinstance(events, list):
                for entry in events:
                    if not isinstance(entry, dict):
                        continue

                    if include_events:
                        if len(collected_events) < max_returned_events:
                            collected_events.append(entry)
                        else:
                            events_truncated = True

                    event = entry.get("event")
                    if isinstance(event, dict) and event.get("type") == "command_completed" and event.get("commandSeq") == command_seq:
                        return {
                            "jsonrpc": "2.0",
                            "id": None,
                            "result": {
                                "completed": True,
                                "timedOut": False,
                                "commandSeq": command_seq,
                                "event": event,
                                "entry": entry,
                                "events": collected_events if include_events else [],
                                "eventsTruncated": events_truncated,
                                "cursor": bridge.events_cursor,
                                "latestSeq": result.get("latestSeq", bridge.events_cursor),
                            },
                        }

        if time.monotonic() >= deadline:
            return {
                "jsonrpc": "2.0",
                "id": None,
                "result": {
                    "completed": False,
                    "timedOut": True,
                    "commandSeq": command_seq,
                    "events": collected_events if include_events else [],
                    "eventsTruncated": events_truncated,
                    "cursor": bridge.events_cursor,
                    "latestSeq": last_result.get("latestSeq", bridge.events_cursor),
                },
            }

        if poll_interval_ms > 0:
            time.sleep(poll_interval_ms / 1000.0)


def action_command_payload(arguments: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in arguments.items() if key not in COMMAND_META_ARGUMENTS}


def action_wait_arguments(arguments: dict[str, Any], command_seq: int) -> dict[str, Any]:
    wait_arguments = {"commandSeq": command_seq}
    for key in ACTION_WAIT_ARGUMENTS - {"waitForCompletion"}:
        if key in arguments:
            wait_arguments[key] = arguments[key]
    return wait_arguments


def act_with_optional_wait(bridge: Bridge, command: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    response = bridge.request("act", command)
    sync_requested = bool(arguments.get("syncAfterCompletion"))
    should_wait = bool(arguments.get("waitForCompletion") or sync_requested)

    if "error" in response or not should_wait:
        return response

    result = response.get("result", {})
    if not isinstance(result, dict):
        return response

    command_seq = result.get("commandSeq")
    if type(command_seq) is not int:
        return response

    action_result = dict(result)
    wait_response = wait_command_completion(bridge, action_wait_arguments(arguments, command_seq))
    if "error" in wait_response:
        action_result["completionError"] = wait_response["error"]
    else:
        wait_result = wait_response.get("result", {})
        action_result["completion"] = wait_result if isinstance(wait_result, dict) else {}

    if sync_requested:
        action_result["sync"] = action_sync_snapshot(bridge, arguments)

    return {
        "jsonrpc": "2.0",
        "id": None,
        "result": action_result,
    }


def dialog_answer_with_memory(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    selected_bridge = target_bridge(bridge, arguments)
    observation: dict[str, Any] = {}
    observe_response = selected_bridge.request("observe")
    if "error" not in observe_response:
        observation_payload = observe_response.get("result", observe_response)
        observation = unwrap_observation_payload(observation_payload)

    response = act_with_optional_wait(selected_bridge, typed_command_payload("tla_dialog_answer", arguments), arguments)
    key = agent_profile_key(selected_bridge)
    memory = agent_memory_for_key(selected_bridge, key)
    remember_dialog_choice(memory, observation, arguments.get("answerIndex"), unix_ms(), response)
    return response


def global_move_with_memory(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    selected_bridge = target_bridge(bridge, arguments)
    observation: dict[str, Any] = {}
    observe_response = selected_bridge.request("observe")
    if "error" not in observe_response:
        observation_payload = observe_response.get("result", observe_response)
        observation = unwrap_observation_payload(observation_payload)

    response = act_with_optional_wait(selected_bridge, typed_command_payload("tla_global_move_to", arguments), arguments)
    key = agent_profile_key(selected_bridge)
    memory = agent_memory_for_key(selected_bridge, key)
    now = unix_ms()
    remember_global_map_state(memory, observation, now, "before_global_move")
    remember_map_transition_state(memory, observation, now, "before_global_move")
    remember_global_move_attempt(memory, observation, arguments, now, response)
    return response


def interest_type_name_from_value(value: int) -> str:
    for name, numeric in INTEREST_TYPE_VALUES.items():
        if numeric == value:
            return name
    return str(value)


def observed_interest_type_name(interest: dict[str, Any]) -> str:
    interest_type = str(interest.get("type") or "").strip()
    if interest_type in INTEREST_TYPE_VALUES:
        return interest_type

    type_enum = str(interest.get("typeEnum") or "").strip()
    enum_to_name = {
        "InterestType::Self": "self",
        "InterestType::Group": "group",
        "InterestType::UnknownPlace": "unknown_place",
        "InterestType::KnownPlace": "known_place",
        "InterestType::Camp": "camp",
        "InterestType::Encounter": "encounter",
        "InterestType::QuestGiver": "quest_giver",
        "InterestType::DeathStash": "death_stash",
    }
    return enum_to_name.get(type_enum, interest_type or type_enum)


def matching_visible_global_enter_interest(observation: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any] | None:
    global_map = observation.get("globalMap") if isinstance(observation.get("globalMap"), dict) else {}
    interests = global_map.get("interests") if isinstance(global_map.get("interests"), list) else []
    wanted_type = interest_type_name_from_value(interest_type_value(arguments.get("interestType")))
    wanted_id = str(arguments.get("interestId"))

    for interest in interests:
        if not isinstance(interest, dict):
            continue
        if observed_interest_type_name(interest) != wanted_type:
            continue
        if str(interest.get("id")) != wanted_id:
            continue
        if not bool(interest.get("enterable")) or not bool(interest.get("inRange")):
            return None
        return interest
    return None


def global_enter_with_memory(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    selected_bridge = target_bridge(bridge, arguments)
    observation: dict[str, Any] = {}
    observe_response = selected_bridge.request("observe")
    if "error" not in observe_response:
        observation_payload = observe_response.get("result", observe_response)
        observation = unwrap_observation_payload(observation_payload)

    if observation and matching_visible_global_enter_interest(observation, arguments) is None:
        wanted_type = interest_type_name_from_value(interest_type_value(arguments.get("interestType")))
        raise ValueError(f"interest_not_visible:{wanted_type}:{arguments.get('interestId')}")

    response = act_with_optional_wait(selected_bridge, typed_command_payload("tla_global_enter_interest", arguments), arguments)
    key = agent_profile_key(selected_bridge)
    memory = agent_memory_for_key(selected_bridge, key)
    now = unix_ms()
    remember_global_map_state(memory, observation, now, "before_global_enter")
    remember_map_transition_state(memory, observation, now, "before_global_enter")
    remember_global_enter_attempt(memory, observation, arguments, now, response)
    return response


def action_sync_snapshot(bridge: Bridge, arguments: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}

    if bool(arguments.get("includeObservation", True)):
        observe_response = bridge.request("observe")
        if "error" in observe_response:
            result["observationError"] = observe_response["error"]
        else:
            result["observation"] = observe_response.get("result", observe_response)

    if bool(arguments.get("includeStatus")):
        status_response = bridge.request("status")
        if "error" in status_response:
            result["statusError"] = status_response["error"]
        else:
            result["status"] = status_response.get("result", status_response)

    return result


def environment_query_type_for_tool(tool_name: str) -> str:
    return {
        "tla_env_path": "path",
        "tla_env_trace": "trace",
        "tla_env_obstacles": "obstacles",
        "tla_env_tactical_path": "tactical_path",
    }[tool_name]


def next_environment_query_id(bridge: Any) -> int:
    owner = bridge_owner(bridge)
    value = int(getattr(owner, "next_environment_query_id", 1))
    next_value = value + 1
    if next_value >= 2_000_000_000:
        next_value = 100_000
    setattr(owner, "next_environment_query_id", next_value)
    return value


def initial_environment_query_id() -> int:
    return 100_000 + int(time.time_ns() % 1_900_000_000)


def environment_query(bridge: Bridge, query_type: str, arguments: dict[str, Any]) -> dict[str, Any]:
    query_id = next_environment_query_id(bridge)
    command = environment_query_command(query_id, query_type, arguments)
    response = bridge.request("act", command)
    if "error" in response:
        return response

    accepted = response.get("result", response)
    wait_arguments = dict(arguments)
    wait_arguments.setdefault("timeoutMs", default_environment_query_timeout_ms(query_type))
    wait = wait_environment_query_result(bridge, query_id, wait_arguments)
    if "error" in wait:
        return wait

    result = wait.get("result", wait)
    if isinstance(result, dict):
        result["accepted"] = accepted
        result["queryId"] = query_id
    return {"jsonrpc": "2.0", "id": None, "result": result}


def default_environment_query_timeout_ms(query_type: str) -> int:
    return DEFAULT_TACTICAL_PATH_TIMEOUT_MS if query_type == "tactical_path" else DEFAULT_ENVIRONMENT_QUERY_TIMEOUT_MS


def environment_query_command(query_id: int, query_type: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if query_type != "obstacles":
        require_arguments(arguments, "toX", "toY")

    from_x = int(arguments["fromX"]) if "fromX" in arguments else -1
    from_y = int(arguments["fromY"]) if "fromY" in arguments else -1
    if ("fromX" in arguments) != ("fromY" in arguments):
        raise ValueError("fromX and fromY must be passed together")

    if query_type == "obstacles":
        to_x = int(arguments["x"]) if "x" in arguments else -1
        to_y = int(arguments["y"]) if "y" in arguments else -1
        if ("x" in arguments) != ("y" in arguments):
            raise ValueError("x and y must be passed together")
    else:
        to_x = int(arguments["toX"])
        to_y = int(arguments["toY"])

    return {
        "type": "environment_query",
        "intArg": query_id,
        "screenX": from_x,
        "screenY": from_y,
        "x": to_x,
        "y": to_y,
        "stringArg": environment_query_options(query_type, arguments),
    }


def environment_query_options(query_type: str, arguments: dict[str, Any]) -> str:
    options: list[str] = [query_type]
    for name in (
        "cut",
        "includeDirections",
        "maxDirections",
        "maxDistance",
        "angle",
        "maxCritters",
        "radius",
        "maxResults",
        "avoidRadius",
        "searchRadius",
        "hazardWeight",
        "maxCandidates",
        "avoidPlayers",
        "maxThreats",
    ):
        if name in arguments:
            value = arguments[name]
            if isinstance(value, bool):
                value = "1" if value else "0"
            options.append(f"{name}={value}")
    return ";".join(options)


def wait_environment_query_result(bridge: Bridge, query_id: int, arguments: dict[str, Any]) -> dict[str, Any]:
    timeout_ms = int_arg(arguments, "timeoutMs", 3000)
    poll_interval_ms = int_arg(arguments, "pollIntervalMs", 100)
    limit = int_arg(arguments, "limit", 100)

    timeout_ms = max(0, min(timeout_ms, 60000))
    poll_interval_ms = max(0, min(poll_interval_ms, 5000))
    limit = max(1, min(limit, 500))

    deadline = time.monotonic() + timeout_ms / 1000.0
    collected_events: list[dict[str, Any]] = []

    while True:
        response = bridge.request("events", {"afterSeq": bridge.events_cursor, "limit": limit})

        if "error" in response:
            return response

        result = response.get("result", {})
        if isinstance(result, dict):
            events = result.get("events") or []
            if isinstance(events, list):
                for entry in events:
                    if isinstance(entry, dict):
                        collected_events.append(entry)
                    event = entry.get("event") if isinstance(entry, dict) else None
                    if isinstance(event, dict) and event.get("type") == "environment_query_result" and event.get("queryId") == query_id:
                        # Advance only up to the matched event so any later events in the same
                        # batch stay visible to the next sync/step/social observation.
                        matched_seq = entry.get("seq") if isinstance(entry, dict) else None
                        if isinstance(matched_seq, int):
                            bridge.events_cursor = max(bridge.events_cursor, matched_seq)
                        return {
                            "jsonrpc": "2.0",
                            "id": None,
                            "result": {
                                "completed": True,
                                "timedOut": False,
                                "event": event,
                                "result": event.get("result"),
                                "events": collected_events,
                                "cursor": bridge.events_cursor,
                                "latestSeq": result.get("latestSeq", bridge.events_cursor),
                            },
                        }
        # No match in this batch: advance past everything consumed and keep polling.
        advance_events_cursor(bridge, response)

        if time.monotonic() >= deadline:
            return {
                "jsonrpc": "2.0",
                "id": None,
                "result": {
                    "completed": False,
                    "timedOut": True,
                    "events": collected_events,
                    "cursor": bridge.events_cursor,
                },
            }

        time.sleep(poll_interval_ms / 1000.0)


def sync_state(bridge: Bridge, arguments: dict[str, Any]) -> dict[str, Any]:
    if arguments.get("reset"):
        bridge.events_cursor = 0

    after_seq = 9223372036854775807 if arguments.get("seekLatest") else bridge.events_cursor
    events_response = bridge.request("events", {"afterSeq": after_seq, "limit": arguments.get("limit", 100)})
    advance_events_cursor(bridge, events_response)
    if "error" in events_response:
        return events_response

    observe_response = bridge.request("observe")
    if "error" in observe_response:
        return observe_response

    events_payload = events_response.get("result", events_response)
    observation_payload = observe_response.get("result", observe_response)
    observation = unwrap_observation_payload(observation_payload)
    result = {
        "events": events_payload,
        "observation": observation_payload,
        "cursor": bridge.events_cursor,
    }
    social = social_context_payload(bridge, events_payload, observation)
    result["social"] = social
    result["attention"] = attention_payload(events_payload, social, observation, arguments)
    endpoint = getattr(bridge, "endpoint", None)
    if isinstance(endpoint, dict):
        result["endpoint"] = endpoint

    if arguments.get("includeStatus"):
        status_response = bridge.request("status")
        if "error" in status_response:
            return status_response
        result["status"] = status_response.get("result", status_response)

    return {"jsonrpc": "2.0", "id": None, "result": result}


def step_state(bridge: Bridge, arguments: dict[str, Any]) -> dict[str, Any]:
    if arguments.get("reset"):
        bridge.events_cursor = 0

    after_seq = 9223372036854775807 if arguments.get("seekLatest") else bridge.events_cursor
    events_response = bridge.request("events", {"afterSeq": after_seq, "limit": arguments.get("limit", 100)})
    advance_events_cursor(bridge, events_response)
    if "error" in events_response:
        return events_response

    observe_response = bridge.request("observe")
    if "error" in observe_response:
        return observe_response

    observation_payload = observe_response.get("result", observe_response)
    observation = unwrap_observation_payload(observation_payload)
    events_payload = events_response.get("result", events_response)
    social = social_context_payload(bridge, events_payload, observation)
    result = {
        "events": events_payload,
        "observation": observation_payload,
        "actionSuggestions": available_actions_payload(observation_payload, observation, arguments),
        "social": social,
        "attention": attention_payload(events_payload, social, observation, arguments),
        "cursor": bridge.events_cursor,
    }
    endpoint = getattr(bridge, "endpoint", None)
    if isinstance(endpoint, dict):
        result["endpoint"] = endpoint

    if arguments.get("includeStatus"):
        status_response = bridge.request("status")
        if "error" in status_response:
            return status_response
        result["status"] = status_response.get("result", status_response)

    return {"jsonrpc": "2.0", "id": None, "result": result}


def social_context_state(bridge: Bridge, arguments: dict[str, Any]) -> dict[str, Any]:
    if arguments.get("reset"):
        bridge.events_cursor = 0

    after_seq = 9223372036854775807 if arguments.get("seekLatest") else bridge.events_cursor
    events_response = bridge.request("events", {"afterSeq": after_seq, "limit": arguments.get("limit", 100)})
    advance_events_cursor(bridge, events_response)
    if "error" in events_response:
        return events_response

    observe_response = bridge.request("observe")
    if "error" in observe_response:
        return observe_response

    events_payload = events_response.get("result", events_response)
    observation_payload = observe_response.get("result", observe_response)
    observation = unwrap_observation_payload(observation_payload)
    result: dict[str, Any] = {
        "social": social_context_payload(bridge, events_payload, observation),
        "cursor": bridge.events_cursor,
    }
    endpoint = getattr(bridge, "endpoint", None)
    if isinstance(endpoint, dict):
        result["endpoint"] = endpoint
    if bool(arguments.get("includeEvents", True)):
        result["events"] = events_payload
    if bool(arguments.get("includeObservation", True)):
        result["observation"] = observation_payload

    return {"jsonrpc": "2.0", "id": None, "result": result}


def conversation_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    selected_bridge = target_bridge(bridge, arguments)
    response = social_context_state(selected_bridge, arguments)
    if "error" in response:
        return response

    result = response.get("result", response)
    if not isinstance(result, dict):
        return response

    key = agent_profile_key(selected_bridge)
    memory = agent_memory_for_key(selected_bridge, key)
    social = result.get("social") if isinstance(result.get("social"), dict) else {}
    if bool(arguments.get("updateMemory", True)):
        remember_conversation_people(memory, social)
        remember_conversation_threads(memory, social)
    result["conversation"] = conversation_payload(social, memory, arguments)
    result["key"] = key
    result["memory"] = agent_memory_summary(memory)
    return {"jsonrpc": "2.0", "id": None, "result": result}


def reply_options_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    selected_bridge = target_bridge(bridge, arguments)
    response = conversation_state(selected_bridge, arguments)
    if "error" in response:
        return response

    result = response.get("result", response)
    conversation = result.get("conversation") if isinstance(result, dict) and isinstance(result.get("conversation"), dict) else {}
    threads = conversation.get("threads") if isinstance(conversation.get("threads"), list) else []
    selected_thread = select_conversation_thread(threads, arguments)
    profile = conversation.get("profile") if isinstance(conversation.get("profile"), dict) else {}
    options = reply_options_for_thread(selected_thread, profile, arguments)
    return {
        "jsonrpc": "2.0",
        "id": None,
        "result": {
            "endpoint": result.get("endpoint") if isinstance(result, dict) else None,
            "key": result.get("key") if isinstance(result, dict) else None,
            "thread": selected_thread,
            "replyOptions": options,
            "conversation": conversation,
            "guidance": "Choose an option, write role-consistent text when requiresModelText=true, then use tla_agent_say_planned or another normal typed tool.",
        },
    }


def relation_note_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    endpoint = resolve_target_endpoint(bridge, arguments)
    key = agent_profile_key(bridge, endpoint)
    memory = agent_memory_for_key(bridge, key)
    relation_key = str(arguments.get("key") or arguments.get("speakerId") or arguments.get("targetId") or "").strip()
    if not relation_key:
        raise ValueError("key, speakerId, or targetId is required")

    now = unix_ms()
    data = {
        "id": arguments.get("speakerId", arguments.get("targetId")),
        "name": arguments.get("name"),
        "attitude": arguments.get("attitude"),
        "trust": arguments.get("trust"),
        "hostility": arguments.get("hostility"),
        "relation": arguments.get("relation"),
        "note": arguments.get("note", arguments.get("text")),
        "tags": normalize_string_list(arguments.get("tags")),
        "updatedAt": now,
        "source": str(arguments.get("source", "manual")),
    }
    remember_known_person(memory, relation_key, data)
    return {
        "jsonrpc": "2.0",
        "id": None,
        "result": {
            "endpoint": endpoint,
            "key": key,
            "relationKey": relation_key,
            "person": memory.get("people", {}).get(relation_key),
            "summary": agent_memory_summary(memory),
        },
    }


def agent_say_planned_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    require_arguments(arguments, "text")
    text = str(arguments.get("text", "")).strip()
    if not text:
        raise ValueError("text must not be empty")

    delay_ms = max(0, min(int_arg(arguments, "delayMs", int_arg(arguments, "suggestedDelayMs", 0)), 60000))
    plan = {
        "tool": "tla_say",
        "arguments": {"text": text, "sayType": str(arguments.get("sayType", "normal"))},
        "threadId": arguments.get("threadId"),
        "reason": arguments.get("reason", ""),
        "decisionId": arguments.get("decisionId"),
        "delayMs": delay_ms,
        "dryRun": bool(arguments.get("dryRun", False)),
    }
    if plan["dryRun"]:
        return {"jsonrpc": "2.0", "id": None, "result": {"plan": plan, "executed": False}}

    selected_bridge = target_bridge(bridge, arguments)
    waited_ms = 0
    if bool(arguments.get("respectDelay")) and delay_ms > 0:
        waited_ms = min(delay_ms, 5000)
        time.sleep(waited_ms / 1000.0)
    command = typed_command_payload("tla_say", arguments)
    response = act_with_optional_wait(selected_bridge, command, arguments)
    if "error" in response:
        return response
    result = response.get("result", response)
    if action_response_accepted(response):
        remember_agent_outgoing_speech(selected_bridge, arguments, text, unix_ms())
    return {"jsonrpc": "2.0", "id": None, "result": {"plan": plan, "executed": True, "waitedMs": waited_ms, "say": result}}


def remember_agent_outgoing_speech(bridge: Any, arguments: dict[str, Any], text: str, now: int) -> None:
    key = agent_profile_key(bridge)
    memory = agent_memory_for_key(bridge, key)
    thread_id = str(arguments.get("threadId", "")).strip()
    lower_text = text.casefold()
    if thread_id:
        mark_pending_request_answered(memory, thread_id, text, now)
    promise = speech_promise_payload(lower_text, text)
    if promise is not None:
        speech = {
            "seq": None,
            "speaker": {"id": "agent", "name": agent_profile_for_target(bridge).get("name", "agent")},
            "text": text,
            "topics": promise.get("topics", []),
            "promise": {**promise, "status": "made"},
        }
        remember_promise(memory, thread_id or "agent", speech, now, "agent_say_planned")


def mark_pending_request_answered(memory: dict[str, Any], thread_id: str, text: str, now: int) -> None:
    requests = ensure_memory_list(memory, "pendingRequests")
    for request in reversed(requests):
        if not isinstance(request, dict) or str(request.get("threadId")) != thread_id:
            continue
        if request.get("status") not in {"open", "pending", None}:
            continue
        request["status"] = "answered"
        request["answeredAt"] = now
        request["answerText"] = text
        return


def remember_conversation_people(memory: dict[str, Any], social: dict[str, Any]) -> None:
    now = unix_ms()
    heard = social.get("heardSpeech") if isinstance(social.get("heardSpeech"), list) else []
    for speech in heard:
        if not isinstance(speech, dict):
            continue
        speaker = speech.get("speaker") if isinstance(speech.get("speaker"), dict) else {}
        speaker_id = speaker.get("id")
        if speaker_id is None:
            continue
        remember_known_person(
            memory,
            str(speaker_id),
            {
                "id": speaker_id,
                "name": speaker.get("name", ""),
                "protoId": speaker.get("protoId", ""),
                "lastHex": speaker.get("hex"),
                "lastSpeech": speech.get("text", ""),
                "lastSpeechIntent": speech.get("intent"),
                "lastAddressing": speech.get("addressedToAgent"),
                "lastTopics": speech.get("topics"),
                "lastEmotionalTone": speech.get("emotionalTone"),
                "lastSeenAt": now,
            },
        )


def remember_conversation_threads(memory: dict[str, Any], social: dict[str, Any]) -> None:
    now = unix_ms()
    heard = social.get("heardSpeech") if isinstance(social.get("heardSpeech"), list) else []
    threads = ensure_memory_dict(memory, "conversationThreads")
    for speech in heard:
        if not isinstance(speech, dict):
            continue
        speaker = speech.get("speaker") if isinstance(speech.get("speaker"), dict) else {}
        speaker_id = speaker.get("id")
        thread_id = f"speaker:{speaker_id}" if speaker_id is not None else f"speech:{speech.get('seq')}"
        entry = dict(threads.get(thread_id, {})) if isinstance(threads.get(thread_id), dict) else {}
        entry.update(
            {
                "threadId": thread_id,
                "speaker": speaker,
                "listener": speech.get("listener"),
                "lastSeq": speech.get("seq"),
                "lastText": speech.get("text", ""),
                "lastIntent": speech.get("intent"),
                "lastAddressing": speech.get("addressedToAgent"),
                "lastTopics": speech.get("topics") if isinstance(speech.get("topics"), list) else [],
                "lastEmotionalTone": speech.get("emotionalTone") if isinstance(speech.get("emotionalTone"), dict) else {},
                "needsResponse": bool(speech.get("needsResponse")),
                "updatedAt": now,
                "turns": int(entry.get("turns") or 0) + 1,
            }
        )
        if isinstance(speech.get("pendingRequest"), dict):
            request = remember_pending_request(memory, thread_id, speech, now)
            entry["lastPendingRequest"] = request
        if isinstance(speech.get("promise"), dict):
            promise = remember_promise(memory, thread_id, speech, now, "heard")
            entry["lastPromise"] = promise
        threads[thread_id] = entry


def remember_pending_request(memory: dict[str, Any], thread_id: str, speech: dict[str, Any], now: int) -> dict[str, Any]:
    speaker = speech.get("speaker") if isinstance(speech.get("speaker"), dict) else {}
    request = speech.get("pendingRequest") if isinstance(speech.get("pendingRequest"), dict) else {}
    entry = {
        "time": now,
        "updatedAt": now,
        "threadId": thread_id,
        "speakerId": speaker.get("id"),
        "speakerName": speaker.get("name"),
        "text": request.get("text", speech.get("text", "")),
        "intent": request.get("intent", speech.get("intent")),
        "topics": request.get("topics", speech.get("topics", [])),
        "status": request.get("status", "open"),
        "source": "visible_speech",
        "seq": speech.get("seq"),
    }
    requests = ensure_memory_list(memory, "pendingRequests")
    append_unique_bounded(requests, entry, 200, ("threadId", "speakerId", "text"))
    return entry


def remember_promise(memory: dict[str, Any], thread_id: str, speech: dict[str, Any], now: int, source: str) -> dict[str, Any]:
    speaker = speech.get("speaker") if isinstance(speech.get("speaker"), dict) else {}
    promise = speech.get("promise") if isinstance(speech.get("promise"), dict) else {}
    entry = {
        "time": now,
        "updatedAt": now,
        "threadId": thread_id,
        "speakerId": speaker.get("id"),
        "speakerName": speaker.get("name"),
        "text": promise.get("text", speech.get("text", "")),
        "topics": promise.get("topics", speech.get("topics", [])),
        "status": promise.get("status", "heard"),
        "source": source,
        "seq": speech.get("seq"),
    }
    promises = ensure_memory_list(memory, "promises")
    append_unique_bounded(promises, entry, 200, ("threadId", "speakerId", "text", "source"))
    return entry


def conversation_payload(social: dict[str, Any], memory: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    heard = social.get("heardSpeech") if isinstance(social.get("heardSpeech"), list) else []
    profile = social.get("profile") if isinstance(social.get("profile"), dict) else {}
    threads = [conversation_thread_from_speech(speech, memory, profile) for speech in heard if isinstance(speech, dict)]
    threads.sort(key=lambda thread: (not bool(thread.get("needsResponse")), -int(thread.get("seq") or 0)))
    limit = max(1, min(int_arg(arguments, "maxThreads", 12), 100))
    pending = [thread for thread in threads if thread.get("needsResponse")]
    return {
        "profile": profile,
        "threads": threads[:limit],
        "pendingThreads": pending[:limit],
        "memory": {
            "threads": len(memory.get("conversationThreads", {})) if isinstance(memory.get("conversationThreads"), dict) else 0,
            "pendingRequests": limited_memory_entries(memory.get("pendingRequests"), int_arg(arguments, "memoryLimit", 8)),
            "promises": limited_memory_entries(memory.get("promises"), int_arg(arguments, "memoryLimit", 8)),
        },
        "counts": {"heard": len(heard), "threads": min(len(threads), limit), "pending": len(pending)},
        "guidance": "Answer only when the selected thread needs or deserves a role-consistent response; silence is a valid option.",
    }


def conversation_thread_from_speech(speech: dict[str, Any], memory: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    speaker = speech.get("speaker") if isinstance(speech.get("speaker"), dict) else {}
    speaker_id = speaker.get("id")
    relation = {}
    people = memory.get("people") if isinstance(memory.get("people"), dict) else {}
    if speaker_id is not None and isinstance(people.get(str(speaker_id)), dict):
        relation = people[str(speaker_id)]

    addressing = str(speech.get("addressedToAgent", "unlikely"))
    intent = str(speech.get("intent", "statement"))
    needs_response = bool(speech.get("needsResponse"))
    urgency = "high" if needs_response else "normal" if addressing in {"likely", "possible"} or intent in {"question", "request"} else "low"
    thread_id = f"speaker:{speaker_id}" if speaker_id is not None else f"speech:{speech.get('seq')}"
    return {
        "threadId": thread_id,
        "seq": speech.get("seq"),
        "speaker": speaker,
        "listener": speech.get("listener"),
        "lastText": speech.get("text", ""),
        "intent": intent,
        "topics": speech.get("topics") if isinstance(speech.get("topics"), list) else [],
        "emotionalTone": speech.get("emotionalTone") if isinstance(speech.get("emotionalTone"), dict) else {},
        "addressedToAgent": addressing,
        "needsResponse": needs_response,
        "urgency": urgency,
        "relation": relation,
        "pendingRequest": speech.get("pendingRequest") if isinstance(speech.get("pendingRequest"), dict) else None,
        "promise": speech.get("promise") if isinstance(speech.get("promise"), dict) else None,
        "expectedReply": expected_reply_for_speech(intent, addressing, needs_response, profile),
        "speech": speech,
    }


def expected_reply_for_speech(intent: str, addressing: str, needs_response: bool, profile: dict[str, Any]) -> dict[str, Any]:
    if not needs_response:
        return {"required": False, "reason": "not directly addressed or no reply required"}
    language = str(profile.get("language", "russ"))
    if intent == "greeting":
        action = "greet_back"
    elif intent == "question":
        action = "answer_or_clarify"
    elif intent == "request":
        action = "accept_refuse_or_clarify"
    else:
        action = "acknowledge_if_useful"
    return {"required": addressing == "likely", "action": action, "language": language, "tool": "tla_agent_say_planned"}


def select_conversation_thread(threads: list[Any], arguments: dict[str, Any]) -> dict[str, Any] | None:
    thread_id = str(arguments.get("threadId", "")).strip()
    if thread_id:
        for thread in threads:
            if isinstance(thread, dict) and str(thread.get("threadId")) == thread_id:
                return thread
        return None
    for thread in threads:
        if isinstance(thread, dict) and thread.get("needsResponse"):
            return thread
    return threads[0] if threads and isinstance(threads[0], dict) else None


def reply_options_for_thread(thread: dict[str, Any] | None, profile: dict[str, Any], arguments: dict[str, Any]) -> list[dict[str, Any]]:
    if not thread:
        return [
            {
                "intent": "stay_silent",
                "score": 70,
                "requiresModelText": False,
                "reason": "no visible conversation thread currently needs a reply",
            }
        ]

    delay_ms = agent_reaction_delay_ms(profile)
    base_arguments = {"sayType": str(arguments.get("sayType", "normal")), "threadId": thread.get("threadId"), "delayMs": delay_ms}
    intent = str(thread.get("intent", "statement"))
    options = [
        {
            "intent": "reply",
            "score": 90 if thread.get("needsResponse") else 45,
            "tool": "tla_agent_say_planned",
            "arguments": base_arguments,
            "requiresModelText": True,
            "textInstruction": reply_text_instruction(intent, profile),
            "reason": "thread is addressed to the agent" if thread.get("needsResponse") else "optional role-consistent reply",
        },
        {
            "intent": "ask_clarification",
            "score": 75 if intent in {"question", "request"} else 35,
            "tool": "tla_agent_say_planned",
            "arguments": base_arguments,
            "requiresModelText": True,
            "textInstruction": "Ask a short clarifying question in character.",
            "reason": "use when the request/question is ambiguous",
        },
        {
            "intent": "stay_silent",
            "score": 20 if thread.get("needsResponse") else 80,
            "requiresModelText": False,
            "reason": "silence is acceptable when busy, unsafe, or not addressed",
        },
    ]
    if intent == "request":
        options.insert(
            2,
            {
                "intent": "refuse_politely",
                "score": 55,
                "tool": "tla_agent_say_planned",
                "arguments": base_arguments,
                "requiresModelText": True,
                "textInstruction": "Politely refuse or set a boundary according to the role.",
                "reason": "requests may be declined when unsafe, impossible, or against role taboos",
            },
        )
    options.sort(key=lambda item: int(item.get("score", 0)), reverse=True)
    return options


def reply_text_instruction(intent: str, profile: dict[str, Any]) -> str:
    style = str(profile.get("conversationStyle") or profile.get("speechStyle") or "Answer briefly and naturally.")
    if intent == "greeting":
        return f"Return a short greeting. Style: {style}"
    if intent == "question":
        return f"Answer the question if you know; otherwise ask for clarification. Style: {style}"
    if intent == "request":
        return f"Accept, refuse, or clarify the request according to the role. Style: {style}"
    return f"Acknowledge only if useful. Style: {style}"


def observe_target_payload(bridge: Any, arguments: dict[str, Any]) -> tuple[TargetBridge, dict[str, Any] | None, dict[str, Any], dict[str, Any]]:
    selected_bridge = target_bridge(bridge, arguments)
    response = selected_bridge.request("observe")
    if "error" in response:
        return selected_bridge, response, {}, {}

    payload = response.get("result", response)
    observation = unwrap_observation_payload(payload)
    return selected_bridge, None, payload, observation


def world_summary_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    selected_bridge = target_bridge(bridge, arguments)
    step_response = step_state(selected_bridge, arguments)
    if "error" in step_response:
        return step_response

    step_result = step_response.get("result", step_response)
    if not isinstance(step_result, dict):
        return step_response

    observation_payload = step_result.get("observation")
    observation = unwrap_observation_payload(observation_payload) if isinstance(observation_payload, dict) else {}
    key = agent_profile_key(selected_bridge)
    result: dict[str, Any] = {
        "endpoint": getattr(selected_bridge, "endpoint", None),
        "key": key,
        "summary": world_summary_payload(
            selected_bridge,
            observation,
            step_result.get("events") if isinstance(step_result.get("events"), dict) else {},
            step_result.get("actionSuggestions") if isinstance(step_result.get("actionSuggestions"), dict) else {},
            step_result.get("social") if isinstance(step_result.get("social"), dict) else {},
            arguments,
        ),
        "memory": agent_memory_summary(agent_memory_for_key(selected_bridge, key)),
        "cursor": step_result.get("cursor"),
    }
    if bool(arguments.get("includeStep", False)):
        result["step"] = step_result

    return {"jsonrpc": "2.0", "id": None, "result": result}


def area_summary_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    selected_bridge, error, observation_payload, observation = observe_target_payload(bridge, arguments)
    if error is not None:
        return error

    return {
        "jsonrpc": "2.0",
        "id": None,
        "result": {
            "endpoint": getattr(selected_bridge, "endpoint", None),
            "observationSeq": observation_payload.get("observationSeq") if isinstance(observation_payload, dict) else observation.get("seq"),
            "area": area_summary_payload(observation),
        },
    }


def visible_interactables_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    selected_bridge, error, observation_payload, observation = observe_target_payload(bridge, arguments)
    if error is not None:
        return error

    action_suggestions = available_actions_payload(observation_payload, observation, arguments)
    return {
        "jsonrpc": "2.0",
        "id": None,
        "result": {
            "endpoint": getattr(selected_bridge, "endpoint", None),
            "observationSeq": action_suggestions.get("observationSeq"),
            "interactables": visible_interactables_payload(observation, action_suggestions, arguments),
        },
    }


def interest_points_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    selected_bridge, error, observation_payload, observation = observe_target_payload(bridge, arguments)
    if error is not None:
        return error

    action_suggestions = available_actions_payload(observation_payload, observation, arguments)
    return {
        "jsonrpc": "2.0",
        "id": None,
        "result": {
            "endpoint": getattr(selected_bridge, "endpoint", None),
            "observationSeq": action_suggestions.get("observationSeq"),
            "interestPoints": interest_points_payload(observation, action_suggestions, arguments),
        },
    }


def nav_options_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    selected_bridge, error, observation_payload, observation = observe_target_payload(bridge, arguments)
    if error is not None:
        return error

    action_suggestions = available_actions_payload(observation_payload, observation, arguments)
    key = agent_profile_key(selected_bridge)
    profile = agent_profile_for_target(selected_bridge)
    memory = agent_memory_for_key(selected_bridge, key)
    return {
        "jsonrpc": "2.0",
        "id": None,
        "result": {
            "endpoint": getattr(selected_bridge, "endpoint", None),
            "observationSeq": action_suggestions.get("observationSeq"),
            "nav": nav_options_payload(observation, action_suggestions, arguments, profile, memory),
        },
    }


def advisory_observation_state(bridge: Any, arguments: dict[str, Any], key_name: str, payload_builder: Any) -> dict[str, Any]:
    selected_bridge, observe_error, observation_payload, observation, action_suggestions = observe_with_action_suggestions(bridge, arguments)
    if observe_error is not None:
        return observe_error

    profile = agent_profile_for_target(selected_bridge)
    return {
        "jsonrpc": "2.0",
        "id": None,
        "result": {
            "endpoint": getattr(selected_bridge, "endpoint", None),
            "observationSeq": action_suggestions.get("observationSeq"),
            "profile": {"combatStyle": profile.get("combatStyle"), "lootStyle": profile.get("lootStyle"), "riskTolerance": profile.get("riskTolerance")},
            key_name: payload_builder(observation, action_suggestions, profile, arguments),
        },
    }


def inventory_summary_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    return advisory_observation_state(bridge, arguments, "inventory", inventory_summary_payload)


def loot_options_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    return advisory_observation_state(bridge, arguments, "loot", loot_options_payload)


def equip_options_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    return advisory_observation_state(bridge, arguments, "equip", equip_options_payload)


def ammo_options_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    return advisory_observation_state(bridge, arguments, "ammo", ammo_options_payload)


def healing_options_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    return advisory_observation_state(bridge, arguments, "healing", healing_options_payload)


def container_options_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    return advisory_observation_state(bridge, arguments, "container", container_options_payload)


def combat_options_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    return advisory_observation_state(bridge, arguments, "combat", combat_options_payload)


def target_options_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    return advisory_observation_state(bridge, arguments, "targets", target_options_payload)


def retreat_options_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    return advisory_observation_state(bridge, arguments, "retreat", retreat_options_payload)


def reload_options_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    return advisory_observation_state(bridge, arguments, "reload", reload_options_payload)


def cover_options_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    return advisory_observation_state(bridge, arguments, "cover", cover_options_payload)


def dialog_options_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    return advisory_observation_state(bridge, arguments, "dialog", dialog_options_payload)


def quest_summary_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    return advisory_observation_state(bridge, arguments, "questSummary", quest_summary_payload)


def task_options_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    return advisory_observation_state(bridge, arguments, "tasks", task_options_payload)


def xp_source_plan_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    return advisory_observation_state(bridge, arguments, "xpPlan", xp_source_plan_payload)


def map_transition_options_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    return advisory_observation_state(bridge, arguments, "transitions", map_transition_options_payload)


def global_options_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    return advisory_observation_state(bridge, arguments, "global", global_options_payload)


def travel_plan_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    return advisory_observation_state(bridge, arguments, "travel", travel_plan_payload)


def enter_options_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    return advisory_observation_state(bridge, arguments, "enter", enter_options_payload)


def dialog_memory_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    selected_bridge, observe_error, observation_payload, observation, action_suggestions = observe_with_action_suggestions(bridge, arguments)
    if observe_error is not None:
        return observe_error

    key = agent_profile_key(selected_bridge)
    memory = agent_memory_for_key(selected_bridge, key)
    profile = agent_profile_for_target(selected_bridge)
    now = unix_ms()
    dialog = observation.get("dialog") if isinstance(observation.get("dialog"), dict) else {}
    if dialog.get("active"):
        remember_dialog_snapshot(memory, dialog, now, "dialog_memory")
        remember_task_hints_from_dialog(memory, dialog, now, "dialog_memory")

    return {
        "jsonrpc": "2.0",
        "id": None,
        "result": {
            "endpoint": getattr(selected_bridge, "endpoint", None),
            "key": key,
            "observationSeq": action_suggestions.get("observationSeq"),
            "summary": agent_memory_summary(memory),
            "current": dialog_options_payload(observation, action_suggestions, profile, arguments),
            "dialogs": memory.get("dialogs", {}) if isinstance(memory.get("dialogs"), dict) else {},
            "choices": limited_memory_entries(memory.get("dialogChoices"), int(arguments.get("limit", 20))),
            "taskHints": limited_memory_entries(memory.get("taskHints"), int(arguments.get("limit", 20))),
            "guidance": "Dialog memory is endpoint-local and derived from visible dialog observations/events or explicit MCP actions only.",
        },
    }


def task_memory_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    selected_bridge, observe_error, observation_payload, observation, action_suggestions = observe_with_action_suggestions(bridge, arguments)
    if observe_error is not None:
        return observe_error

    key = agent_profile_key(selected_bridge)
    memory = agent_memory_for_key(selected_bridge, key)
    profile = agent_profile_for_target(selected_bridge)
    now = unix_ms()
    dialog = observation.get("dialog") if isinstance(observation.get("dialog"), dict) else {}
    if dialog.get("active"):
        remember_dialog_snapshot(memory, dialog, now, "task_memory")
        remember_task_hints_from_dialog(memory, dialog, now, "task_memory")
    current_tasks = task_options_payload(observation, action_suggestions, profile, arguments)
    remember_task_hints_from_options(memory, current_tasks, now, "task_options")

    return {
        "jsonrpc": "2.0",
        "id": None,
        "result": {
            "endpoint": getattr(selected_bridge, "endpoint", None),
            "key": key,
            "observationSeq": action_suggestions.get("observationSeq"),
            "summary": agent_memory_summary(memory),
            "current": current_tasks,
            "taskHints": limited_memory_entries(memory.get("taskHints"), int(arguments.get("limit", 20))),
            "dialogChoices": limited_memory_entries(memory.get("dialogChoices"), int(arguments.get("limit", 20))),
            "guidance": "Task memory records visible task hints and recent dialog choices; it is not a quest/PDA state export.",
        },
    }


def route_memory_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    selected_bridge, observe_error, observation_payload, observation, action_suggestions = observe_with_action_suggestions(bridge, arguments)
    if observe_error is not None:
        return observe_error

    key = agent_profile_key(selected_bridge)
    memory = agent_memory_for_key(selected_bridge, key)
    profile = agent_profile_for_target(selected_bridge)
    now = unix_ms()
    remember_global_map_state(memory, observation, now, "route_memory")
    remember_map_transition_state(memory, observation, now, "route_memory")

    return {
        "jsonrpc": "2.0",
        "id": None,
        "result": {
            "endpoint": getattr(selected_bridge, "endpoint", None),
            "key": key,
            "observationSeq": observation_payload.get("observationSeq") if isinstance(observation_payload, dict) else observation.get("seq"),
            "summary": agent_memory_summary(memory),
            "current": {
                "area": area_summary_payload(observation),
                "global": global_options_payload(observation, action_suggestions, profile, arguments),
                "travel": travel_plan_payload(observation, action_suggestions, profile, arguments),
                "enter": enter_options_payload(observation, action_suggestions, profile, arguments),
            },
            "globalInterests": memory.get("globalInterests", {}) if isinstance(memory.get("globalInterests"), dict) else {},
            "travelHistory": limited_memory_entries(memory.get("travelHistory"), int(arguments.get("limit", 20))),
            "mapTransitions": limited_memory_entries(memory.get("mapTransitions"), int(arguments.get("limit", 20))),
            "guidance": "Route memory is endpoint-local and records only visible global-map interests, observed positions, map/global transitions, and MCP-issued move/enter attempts.",
        },
    }


def recent_changes_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    selected_bridge = target_bridge(bridge, arguments)
    if arguments.get("reset"):
        selected_bridge.events_cursor = 0

    after_seq = 9223372036854775807 if arguments.get("seekLatest") else selected_bridge.events_cursor
    events_response = selected_bridge.request("events", {"afterSeq": after_seq, "limit": arguments.get("limit", 100)})
    advance_events_cursor(selected_bridge, events_response)
    if "error" in events_response:
        return events_response

    events_payload = events_response.get("result", events_response)
    result: dict[str, Any] = {
        "endpoint": getattr(selected_bridge, "endpoint", None),
        "changes": recent_changes_payload(events_payload),
        "cursor": selected_bridge.events_cursor,
    }
    if bool(arguments.get("includeEvents", True)):
        result["events"] = events_payload

    return {"jsonrpc": "2.0", "id": None, "result": result}


def world_summary_payload(
    bridge: Any,
    observation: dict[str, Any],
    events_payload: dict[str, Any],
    action_suggestions: dict[str, Any],
    social: dict[str, Any],
    arguments: dict[str, Any],
) -> dict[str, Any]:
    key = agent_profile_key(bridge)
    profile = agent_profile_for_target(bridge)
    memory = agent_memory_for_key(bridge, key)
    return {
        "observation": compact_observation_summary(observation),
        "area": area_summary_payload(observation),
        "changes": recent_changes_payload(events_payload),
        "attention": attention_payload(events_payload, social, observation, arguments),
        "interactables": visible_interactables_payload(observation, action_suggestions, arguments),
        "interestPoints": interest_points_payload(observation, action_suggestions, arguments),
        "nav": nav_options_payload(observation, action_suggestions, arguments, profile, memory),
        "localMemory": local_map_memory_payload(memory, observation, int_arg(arguments, "memoryLimit", 8)),
        "social": {
            "pendingResponses": len(social.get("pendingResponses", [])) if isinstance(social.get("pendingResponses"), list) else 0,
            "heardSpeech": len(social.get("heardSpeech", [])) if isinstance(social.get("heardSpeech"), list) else 0,
            "profile": social.get("profile", {}),
        },
        "guidance": "Use this compact world model for planning; verify movement with tla_env_path/tla_env_tactical_path before issuing tla_move_to_hex.",
    }


def local_map_memory_payload(memory: dict[str, Any], observation: dict[str, Any], limit: int) -> dict[str, Any]:
    limit = max(1, min(limit, 50))
    map_state = observation.get("map") if isinstance(observation.get("map"), dict) else {}
    map_id = str(map_state.get("protoId") or map_state.get("id") or map_state.get("name") or "")
    recent_path = limited_memory_entries(memory.get("recentPath"), limit)
    known_hazards = memory.get("knownHazards") if isinstance(memory.get("knownHazards"), dict) else {}
    useful_items = memory.get("usefulItems") if isinstance(memory.get("usefulItems"), dict) else {}
    visited_areas = memory.get("visitedAreas") if isinstance(memory.get("visitedAreas"), dict) else {}
    active_collection = memory.get("activeCollection") if isinstance(memory.get("activeCollection"), dict) else {}
    current_areas = [area for area in visited_areas.values() if isinstance(area, dict) and (not map_id or str(area.get("map")) == map_id)]
    current_areas.sort(key=lambda area: int(area.get("lastSeenAt") or 0), reverse=True)
    hazards = [entry for entry in known_hazards.values() if isinstance(entry, dict)]
    hazards.sort(key=lambda entry: int(entry.get("lastSeenAt") or 0), reverse=True)
    frontier = local_unexplored_frontier(current_areas, recent_path, map_id, limit)
    return {
        "visitedCount": len(memory.get("visited", [])) if isinstance(memory.get("visited"), list) else 0,
        "visitedAreas": len(visited_areas),
        "currentMapAreas": current_areas[:limit],
        "unexploredFrontier": frontier,
        "recentPath": recent_path,
        "knownHazards": hazards[:limit],
        "usefulItems": list(useful_items.values())[-limit:],
        "recentInteractions": limited_memory_entries(memory.get("interactions"), limit),
        "recentCombat": limited_memory_entries(memory.get("combatEncounters"), limit),
        "recentLootContainers": limited_memory_entries(memory.get("lootContainers"), limit),
        "activeCollection": active_collection if active_collection.get("active") else {},
        "doNotRetry": limited_memory_entries(memory.get("doNotRetry"), limit),
        "guidance": "Endpoint-local memory is derived from visible observations/events and explicit MCP notes; treat hazards and do-not-retry entries as advisory, time-limited hints.",
    }


def local_unexplored_frontier(current_areas: list[dict[str, Any]], recent_path: list[Any], map_id: str, limit: int) -> list[dict[str, Any]]:
    visited_clusters: set[tuple[int, int]] = set()
    for area in current_areas:
        cluster = area.get("cluster") if isinstance(area.get("cluster"), dict) else {}
        try:
            visited_clusters.add((int(cluster.get("x")), int(cluster.get("y"))))
        except (TypeError, ValueError):
            continue

    origin_cluster: tuple[int, int] | None = None
    for entry in reversed(recent_path):
        if not isinstance(entry, dict):
            continue
        if map_id and str(entry.get("map")) != map_id:
            continue
        hex_value = entry.get("hex") if isinstance(entry.get("hex"), dict) else {}
        x, y = safe_hex_value_xy(hex_value)
        if x is not None and y is not None:
            origin_cluster = (x // 10, y // 10)
            break
    if origin_cluster is None and current_areas:
        cluster = current_areas[0].get("cluster") if isinstance(current_areas[0].get("cluster"), dict) else {}
        try:
            origin_cluster = (int(cluster.get("x")), int(cluster.get("y")))
        except (TypeError, ValueError):
            origin_cluster = None
    if origin_cluster is None:
        return []

    frontier: list[dict[str, Any]] = []
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
        cluster = (origin_cluster[0] + dx, origin_cluster[1] + dy)
        if cluster in visited_clusters:
            continue
        frontier.append(
            {
                "map": map_id or None,
                "cluster": {"x": cluster[0], "y": cluster[1]},
                "approxHex": {"x": cluster[0] * 10 + 5, "y": cluster[1] * 10 + 5},
                "reason": "adjacent cluster not yet visited by this endpoint memory",
            }
        )
        if len(frontier) >= limit:
            break
    return frontier


def area_summary_payload(observation: dict[str, Any]) -> dict[str, Any]:
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    map_state = observation.get("map") if isinstance(observation.get("map"), dict) else {}
    global_map = observation.get("globalMap") if isinstance(observation.get("globalMap"), dict) else {}
    critters = [entry for entry in observation.get("critters", []) if isinstance(entry, dict)]
    chosen_id = chosen.get("id")
    visible_others = [entry for entry in critters if entry.get("id") != chosen_id]
    visible_players = [entry for entry in visible_others if entry.get("controlledByPlayer")]
    visible_npcs = [entry for entry in visible_others if not entry.get("controlledByPlayer")]
    map_items = [entry for entry in observation.get("mapItems", []) if isinstance(entry, dict)]
    inventory = [entry for entry in observation.get("inventory", []) if isinstance(entry, dict)]
    dialog = observation.get("dialog") if isinstance(observation.get("dialog"), dict) else {}
    screen = observation_screen_state(observation)

    return {
        "mode": "global" if global_map.get("active") else "map" if observation.get("hasMap") else "ui",
        "map": map_state or None,
        "globalMap": {
            "active": bool(global_map.get("active")),
            "pos": global_map.get("pos"),
            "targetPos": global_map.get("targetPos"),
            "isMoving": global_map.get("isMoving"),
            "interestCount": len(global_map.get("interests", [])) if isinstance(global_map.get("interests"), list) else 0,
        },
        "chosen": {
            "id": chosen.get("id"),
            "name": chosen.get("name", ""),
            "hex": chosen.get("hex"),
            "alive": chosen.get("alive"),
            "inCombat": chosen.get("inCombat"),
            "level": chosen.get("level"),
            "experience": chosen.get("experience"),
            "nextLevelExperience": chosen.get("nextLevelExperience"),
            "experienceToNextLevel": chosen.get("experienceToNextLevel"),
            "health": {"current": chosen.get("curHealth"), "max": chosen.get("maxHealth")},
            "stamina": {"current": chosen.get("curStamina"), "max": chosen.get("maxStamina")},
        },
        "counts": {
            "visibleCritters": len(visible_others),
            "visiblePlayers": len(visible_players),
            "visibleNpcs": len(visible_npcs),
            "mapItems": len(map_items),
            "inventory": len(inventory),
            "dialogAnswers": len(dialog.get("answers", [])) if isinstance(dialog.get("answers"), list) else 0,
        },
        "dialogActive": bool(dialog.get("active")),
        "screen": screen.get("active"),
        "screenModalActive": modal_screen_active(observation),
        "activeModalScreen": active_modal_screen_name(observation),
    }


def recent_changes_payload(events_payload: dict[str, Any]) -> dict[str, Any]:
    events = events_payload.get("events") if isinstance(events_payload, dict) else []
    changes: dict[str, Any] = {
        "counts": {},
        "speech": [],
        "critters": [],
        "items": [],
        "progression": [],
        "ui": [],
        "commands": [],
        "environment": [],
        "diagnostics": [],
        "other": [],
    }
    if not isinstance(events, list):
        return changes

    for entry in events:
        if not isinstance(entry, dict):
            continue
        event = entry.get("event") if isinstance(entry.get("event"), dict) else {}
        event_type = str(event.get("type", ""))
        compact = compact_event_entry(entry)
        changes["counts"][event_type] = int(changes["counts"].get(event_type, 0)) + 1
        if event_type == "say_received":
            changes["speech"].append(
                {
                    **compact,
                    "speakerId": event.get("speakerId"),
                    "speakerName": event.get("speakerName"),
                    "listenerName": event.get("listenerName"),
                    "distance": event.get("distance"),
                }
            )
        elif event_type.startswith("critter_") or event_type in {"critter_in", "critter_out", "critter_action", "critter_action_ex"}:
            changes["critters"].append(compact)
        elif "item" in event_type or event_type in {"receive_items"}:
            changes["items"].append(compact)
        elif event_type == "level_changed":
            changes["progression"].append(
                {
                    **compact,
                    "level": event.get("level"),
                    "previousLevel": event.get("previousLevel"),
                    "experience": event.get("experience"),
                    "experienceToNextLevel": event.get("experienceToNextLevel"),
                }
            )
        elif event_type.startswith("dialog_") or "screen" in event_type or event_type in {"generation_ready", "tutorial_finished"}:
            changes["ui"].append(compact)
        elif event_type == "command_completed":
            changes["commands"].append({**compact, "commandSeq": event.get("commandSeq"), "success": event.get("success")})
        elif event_type == "environment_query_result":
            changes["environment"].append(compact)
        elif event_type == "runtime_exception":
            changes["diagnostics"].append(
                {
                    **compact,
                    "level": event.get("level"),
                    "category": event.get("category"),
                    "message": event.get("message"),
                }
            )
        else:
            changes["other"].append(compact)

    return changes


def attention_payload(events_payload: dict[str, Any], social: dict[str, Any], observation: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    events = events_payload.get("events") if isinstance(events_payload, dict) else []
    budget = max(1, min(int_arg(arguments, "maxAttentionEvents", int_arg(arguments, "attentionBudget", 5)), 20))
    if not isinstance(events, list):
        return {"budget": budget, "focus": [], "deferredCount": 0, "guidance": "No event list was available for attention scoring."}

    speech_by_seq = {
        entry.get("seq"): entry
        for entry in social.get("heardSpeech", []) if isinstance(entry, dict)
    } if isinstance(social.get("heardSpeech"), list) else {}
    scored: list[dict[str, Any]] = []
    for index, entry in enumerate(events):
        if not isinstance(entry, dict):
            continue
        event = entry.get("event") if isinstance(entry.get("event"), dict) else {}
        score, category, reasons = attention_score_event(entry, event, speech_by_seq.get(entry.get("seq")), observation)
        compact = compact_event_entry(entry)
        focus = {
            **compact,
            "category": category,
            "score": score,
            "reasons": reasons,
            "order": index,
        }
        speech = speech_by_seq.get(entry.get("seq"))
        if isinstance(speech, dict):
            focus["speech"] = {
                "addressedToAgent": speech.get("addressedToAgent"),
                "intent": speech.get("intent"),
                "needsResponse": speech.get("needsResponse"),
                "selfSpeech": speech.get("selfSpeech"),
            }
        scored.append(focus)

    scored.sort(key=lambda item: (-int(item.get("score", 0)), int(item.get("order", 0))))
    focus = [{key: value for key, value in item.items() if key != "order"} for item in scored[:budget]]
    return {
        "budget": budget,
        "focus": focus,
        "deferredCount": max(0, len(scored) - len(focus)),
        "totalEvents": len(scored),
        "guidance": "Review focus entries first; deferred events are still available in events/changes when deeper context is needed.",
    }


def attention_score_event(entry: dict[str, Any], event: dict[str, Any], speech: dict[str, Any] | None, observation: dict[str, Any]) -> tuple[int, str, list[str]]:
    event_type = str(event.get("type", ""))
    reasons: list[str] = []
    category = "other"
    score = 10

    if event_type == "say_received":
        category = "speech"
        score = 60
        reasons.append("visible speech")
        if isinstance(speech, dict):
            if bool(speech.get("selfSpeech")):
                score -= 80
                reasons.append("own speech")
            if speech.get("addressedToAgent") == "likely":
                score += 25
                reasons.append("addressed to agent")
            elif speech.get("addressedToAgent") == "possible":
                score += 10
                reasons.append("possibly addressed")
            if bool(speech.get("needsResponse")):
                score += 35
                reasons.append("needs response")
            if speech.get("intent") in {"request", "question"}:
                score += 10
                reasons.append(str(speech.get("intent")))
        return max(0, score), category, reasons

    if event_type == "command_completed":
        category = "command"
        score = 95 if event.get("success") is False else 50
        reasons.append("command completed")
        if event.get("success") is False:
            reasons.append("command failed")
        return score, category, reasons

    if event_type.startswith("dialog_") or event_type in {"generation_ready", "tutorial_finished", "roster_state", "roster_action_result"}:
        category = "ui"
        score = 80
        reasons.append("dialog/generation/roster state changed")
        return score, category, reasons

    if event_type == "environment_query_result":
        category = "environment"
        score = 70 if event.get("success") is False else 45
        reasons.append("environment query result")
        if event.get("success") is False:
            reasons.append("query failed")
        return score, category, reasons

    if event_type == "level_changed":
        category = "progression"
        score = 90
        reasons.append("chosen level changed")
        if event.get("level") is not None:
            reasons.append("level " + str(event.get("level")))
        return score, category, reasons

    if event_type == "runtime_exception":
        category = "diagnostic"
        score = 100
        reasons.append("runtime exception/error in log")
        if event.get("category"):
            reasons.append(str(event.get("category")))
        return score, category, reasons

    if event_type.startswith("critter_") or event_type in {"critter_in", "critter_out", "critter_action", "critter_action_ex"}:
        category = "critter"
        score = 65 if "damag" in event_type or event_type in {"critter_action", "critter_action_ex"} else 45
        reasons.append("visible critter state changed")
        return score, category, reasons

    if "item" in event_type or event_type in {"receive_items"}:
        category = "item"
        score = 35
        reasons.append("visible item/inventory state changed")
        return score, category, reasons

    if event_type.startswith(("mouse_", "touch_", "key_")):
        category = "raw_input"
        score = 5
        reasons.append("raw input diagnostic event")
        return score, category, reasons

    reasons.append("low-priority visible event")
    return score, category, reasons


def visible_interactables_payload(observation: dict[str, Any], action_suggestions: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    actions = action_map_from_suggestions(action_suggestions)
    result: dict[str, Any] = {
        "counts": {},
        "critters": interactable_entries(actions, ("talk_to", "attack_entity", "loot_critter")),
        "items": interactable_entries(actions, ("pick_item", "pick_hex")),
        "inventory": interactable_entries(actions, ("use_item", "reload", "unload", "drop_item", "move_item")),
        "dialog": interactable_entries(actions, ("dialog_answer",)),
        "global": interactable_entries(actions, ("global_enter_interest", "global_move_to")),
        "utility": interactable_entries(actions, ("operate_container", "toggle_sneak", "set_overwatch", "request_roster", "roster_switch", "roster_create", "roster_delete")),
    }
    for key, value in result.items():
        if isinstance(value, list):
            result["counts"][key] = len(value)
    result["note"] = "Interactables are advisory candidates derived from visible observation; normal command validation still applies."
    return result


def item_tags(entry: dict[str, Any]) -> list[str]:
    text = f"{entry.get('protoId', '')} {entry.get('name', '')}".lower()
    slot = str(entry.get("slot", "")).lower()
    tags: set[str] = set()

    for kind, keywords in ITEM_KIND_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            tags.add(kind)

    if slot and slot not in {"inventory", "none", "null"}:
        tags.add("equipped")
        if "armor" in slot:
            tags.add("armor")
        if "main" in slot or "ext" in slot or "hand" in slot:
            tags.add("weapon")

    if entry.get("canUse"):
        tags.add("usable")
    if entry.get("canDrop"):
        tags.add("droppable")
    if entry.get("canPickUp"):
        tags.add("pickable")
    if entry.get("hasDoor"):
        tags.add("door")
    if entry.get("hasContainer"):
        tags.add("container")
    if entry.get("hasLocker"):
        tags.add("locker")
    if entry.get("opened") is True:
        tags.add("opened")
    elif entry.get("opened") is False and (entry.get("hasDoor") or entry.get("hasContainer") or entry.get("hasLocker")):
        tags.add("closed")
    if entry.get("lockerLocked") is True:
        tags.add("locked")
    if entry.get("isGag") is True:
        tags.add("gag")
    if entry.get("noHighlight") is True:
        tags.add("no_highlight")
    if entry.get("hasStaticScript") is True:
        tags.add("static_script")
    if not tags:
        tags.add("misc")

    return sorted(tags)


def classified_item(entry: dict[str, Any]) -> dict[str, Any]:
    item = {
        key: entry.get(key)
        for key in (
            "id",
            "protoId",
            "name",
            "count",
            "ownership",
            "slot",
            "hex",
            "canUse",
            "canPickUp",
            "canDrop",
            "static",
            "isStatic",
            "hasDoor",
            "hasContainer",
            "hasLocker",
            "opened",
            "canOpen",
            "isGag",
            "noHighlight",
            "hasStaticScript",
            "isStatic",
            "lockerLocked",
            "lockerNoOpen",
        )
        if key in entry
    }
    item["tags"] = item_tags(entry)
    return item


def inventory_items(observation: dict[str, Any]) -> list[dict[str, Any]]:
    return [classified_item(entry) for entry in observation.get("inventory", []) if isinstance(entry, dict)]


def map_item_entries(observation: dict[str, Any]) -> list[dict[str, Any]]:
    return [classified_item(entry) for entry in observation.get("mapItems", []) if isinstance(entry, dict)]


def item_has_tag(item: dict[str, Any], tag: str) -> bool:
    tags = item.get("tags")
    return isinstance(tags, list) and tag in tags


def equipment_target_slot(item: dict[str, Any]) -> int | None:
    if item_has_tag(item, "weapon"):
        return CRITTER_ITEM_SLOT_MAIN
    if item_has_tag(item, "armor"):
        return CRITTER_ITEM_SLOT_ARMOR
    return None


def item_text(item: dict[str, Any]) -> str:
    return f"{item.get('protoId', '')} {item.get('name', '')}".casefold()


def item_reloadable_weapon(item: dict[str, Any]) -> bool:
    if not item_has_tag(item, "weapon"):
        return False

    text = item_text(item)
    if any(marker in text for marker in MELEE_WEAPON_MARKERS):
        return False
    return any(marker in text for marker in RELOADABLE_WEAPON_MARKERS)


def item_melee_weapon(item: dict[str, Any]) -> bool:
    if not item_has_tag(item, "weapon"):
        return False
    return any(marker in item_text(item) for marker in MELEE_WEAPON_MARKERS)


def item_ranged_weapon(item: dict[str, Any]) -> bool:
    return item_has_tag(item, "weapon") and not item_melee_weapon(item)


def combat_equipped_items_for_slot(observation: dict[str, Any], target_slot: int) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in inventory_items(observation):
        if not item_has_tag(item, "equipped"):
            continue
        if target_slot == CRITTER_ITEM_SLOT_MAIN and item_has_tag(item, "weapon"):
            result.append(item)
        elif target_slot == CRITTER_ITEM_SLOT_ARMOR and item_has_tag(item, "armor"):
            result.append(item)
    return result


def combat_equipment_option_allowed(observation: dict[str, Any], option: dict[str, Any], combat_active: bool) -> bool:
    if not combat_active:
        return True

    item = option.get("item") if isinstance(option.get("item"), dict) else {}
    target_slot = option.get("targetSlot")
    if not isinstance(target_slot, int):
        target_slot = equipment_target_slot(item)

    if target_slot == CRITTER_ITEM_SLOT_ARMOR and combat_equipped_items_for_slot(observation, CRITTER_ITEM_SLOT_ARMOR):
        return False

    if target_slot != CRITTER_ITEM_SLOT_MAIN:
        return True

    equipped_weapons = combat_equipped_items_for_slot(observation, CRITTER_ITEM_SLOT_MAIN)
    if not equipped_weapons:
        return True

    if item_ranged_weapon(item) and all(item_melee_weapon(equipped) for equipped in equipped_weapons):
        return True

    return False


def item_score(item: dict[str, Any], profile: dict[str, Any], context: str) -> int:
    style = str(profile.get("lootStyle", "practical")).lower()
    score = 20
    tags = item.get("tags") if isinstance(item.get("tags"), list) else []

    if "healing" in tags:
        score += 45
    if "ammo" in tags:
        score += 35
    if "weapon" in tags:
        score += 40
    if "armor" in tags:
        score += 35
    if "currency" in tags:
        score += 30
    if "food" in tags:
        score += 20
    if "usable" in tags:
        score += 10
    if "junk" in tags:
        score -= 15

    if style in {"survival", "practical"}:
        if "healing" in tags or "food" in tags:
            score += 15
    if style in {"combat", "test-relevant"}:
        if "weapon" in tags or "ammo" in tags or "armor" in tags:
            score += 20
    if style in {"valuable", "trader"}:
        if "currency" in tags:
            score += 25
    if style in {"minimal", "none"}:
        score -= 20
        if "healing" in tags or "ammo" in tags:
            score += 20
    if context == "healing" and "healing" in tags:
        score += 30
    if context == "reload" and "ammo" in tags:
        score += 20

    return max(0, min(score, 100))


def item_option(item: dict[str, Any], tool: str, arguments: dict[str, Any], reason: str, score: int, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "item": item,
        "score": score,
        "tool": tool,
        "arguments": arguments,
        "reason": reason,
    }
    if extra:
        result.update(extra)
    return result


def inventory_summary_payload(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    items = inventory_items(observation)
    categories = {
        "equipped": [item for item in items if item_has_tag(item, "equipped")],
        "weapons": [item for item in items if item_has_tag(item, "weapon")],
        "ammo": [item for item in items if item_has_tag(item, "ammo")],
        "healing": [item for item in items if item_has_tag(item, "healing")],
        "armor": [item for item in items if item_has_tag(item, "armor")],
        "usable": [item for item in items if item_has_tag(item, "usable")],
        "droppable": [item for item in items if item_has_tag(item, "droppable")],
        "misc": [item for item in items if item_has_tag(item, "misc") or item_has_tag(item, "junk")],
    }
    limit = result_limit(arguments)
    actions = action_map_from_suggestions(action_suggestions)
    return {
        "style": profile.get("lootStyle"),
        "counts": {key: len(value) for key, value in categories.items()} | {"total": len(items)},
        "items": sorted(items, key=lambda item: item_score(item, profile, "inventory"), reverse=True)[:limit],
        "categories": {key: value[:limit] for key, value in categories.items()},
        "quickOptions": {
            "healing": healing_options_payload(observation, action_suggestions, profile, arguments)["options"][:5],
            "reload": reload_options_payload(observation, action_suggestions, profile, arguments)["options"][:5],
            "equip": equip_options_payload(observation, action_suggestions, profile, arguments)["options"][:5],
            "drop": interactable_entries(actions, ("drop_item",))[:5],
        },
        "guidance": "Inventory classification is heuristic and uses only visible item fields such as protoId, slot, canUse, and canDrop. Execute through normal item tools.",
    }


def loot_options_payload(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    actions = action_map_from_suggestions(action_suggestions)
    pickups: list[dict[str, Any]] = []
    map_items_by_id = {str(item.get("id")): item for item in map_item_entries(observation) if item.get("id") is not None}

    for entry in interactable_entries(actions, ("pick_item", "pick_hex")):
        item = map_items_by_id.get(str(entry.get("id")), classified_item({"id": entry.get("id"), "protoId": entry.get("protoId"), "hex": entry.get("hex")}))
        pickups.append(
            {
                **entry,
                "item": item,
                "score": item_score(item, profile, "loot"),
                "reason": entry.get("reason") or "visible pickup candidate",
                "postAction": loot_collection_post_action(),
            }
        )

    corpses = [
        {
            **entry,
            "score": 55 if profile.get("lootStyle") not in {"minimal", "none"} else 25,
            "reason": entry.get("reason") or "visible dead or lootable critter",
            "postAction": loot_collection_post_action(),
        }
        for entry in interactable_entries(actions, ("loot_critter",))
    ]
    containers = container_options_payload(observation, action_suggestions, profile, arguments)["options"]
    options = [*pickups, *corpses, *containers]
    options.sort(key=lambda item: int(item.get("score", 0)), reverse=True)
    limit = result_limit(arguments)
    return {
        "style": profile.get("lootStyle"),
        "options": options[:limit],
        "pickups": pickups[:limit],
        "corpses": corpses[:limit],
        "containers": containers[:limit],
        "guidance": "Loot options are visible candidates only. Use tla_nav_plan before approaching blocked or occupied item/corpse hexes.",
    }


def loot_collection_post_action() -> dict[str, Any]:
    return {
        "afterQueuedCommand": "poll tla_observe/tla_next_events; command_completed only means the action was queued",
        "waitForAny": ["observation.activeCollection.active=true", "receive_items", "screen.modalActive=true"],
        "nextTool": "tla_container_options",
        "then": "execute tla_operate_container when it is offered, usually with take=true and all=true; close the modal before world actions",
    }


def equip_options_payload(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    options: list[dict[str, Any]] = []
    for item in inventory_items(observation):
        if not (item_has_tag(item, "weapon") or item_has_tag(item, "armor")):
            continue
        if item_has_tag(item, "equipped"):
            continue
        if item.get("canUse"):
            options.append(item_option(item, "tla_use_item", {"itemId": item.get("id")}, "usable equipment-like item", item_score(item, profile, "equip")))
        else:
            target_slot = equipment_target_slot(item)
            move_arguments = {"itemId": item.get("id")}
            extra: dict[str, Any] = {}
            if target_slot is not None:
                move_arguments["slot"] = target_slot
                extra["targetSlot"] = target_slot
            else:
                extra["requiresSlot"] = True
            options.append(
                item_option(
                    item,
                    "tla_move_item",
                    move_arguments,
                    "equipment-like item; move to the default combat equipment slot" if target_slot is not None else "equipment-like item; choose CritterItemSlot before executing tla_move_item",
                    item_score(item, profile, "equip") - 10,
                    extra,
                )
            )
    options.sort(key=lambda item: int(item.get("score", 0)), reverse=True)
    limit = max(1, min(int(arguments.get("maxResults", 20)), 100))
    return {
        "options": options[:limit],
        "equipped": [item for item in inventory_items(observation) if item_has_tag(item, "equipped")],
        "guidance": "Use tla_use_item when the client marks equipment as usable; otherwise tla_move_item can ready weapon-like items in Main and armor-like items in Armor when a default slot is known.",
    }


def ammo_options_payload(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    items = inventory_items(observation)
    ammo = [item for item in items if item_has_tag(item, "ammo")]
    weapons = [item for item in items if item_has_tag(item, "weapon")]
    reload_actions = reload_options_payload(observation, action_suggestions, profile, arguments)["options"]
    limit = max(1, min(int(arguments.get("maxResults", 20)), 100))
    return {
        "ammo": sorted(ammo, key=lambda item: item_score(item, profile, "reload"), reverse=True)[:limit],
        "weapons": sorted(weapons, key=lambda item: item_score(item, profile, "reload"), reverse=True)[:limit],
        "reloadOptions": reload_actions[:limit],
        "guidance": "Ammo/weapon matching is advisory; tla_reload remains server/client validated.",
    }


def bounded_ratio_argument(arguments: dict[str, Any], key: str, default: float) -> float:
    try:
        value = float(arguments.get(key, default))
    except (TypeError, ValueError):
        return default
    if value > 1.0:
        value /= 100.0
    return max(0.0, min(value, 1.0))


def stamina_state_payload(chosen: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    current = chosen.get("curStamina")
    maximum = chosen.get("maxStamina")
    ratio: float | None = None
    if isinstance(current, (int, float)) and isinstance(maximum, (int, float)) and maximum > 0:
        ratio = float(current) / float(maximum)
    threshold = bounded_ratio_argument(arguments, "staminaThreshold", 0.35)
    critical_threshold = bounded_ratio_argument(arguments, "criticalStaminaThreshold", 0.15)
    critical = ratio is not None and (ratio < critical_threshold or (isinstance(current, (int, float)) and current <= 0))
    needs_recovery = ratio is not None and ratio < threshold
    return {
        "current": current,
        "max": maximum,
        "ratio": ratio,
        "threshold": threshold,
        "criticalThreshold": critical_threshold,
        "needsRecovery": needs_recovery,
        "critical": critical,
    }


def healing_options_payload(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    current = chosen.get("curHealth")
    maximum = chosen.get("maxHealth")
    ratio: float | None = None
    if isinstance(current, (int, float)) and isinstance(maximum, (int, float)) and maximum > 0:
        ratio = float(current) / float(maximum)

    threshold = float(arguments.get("healthThreshold", 0.75))
    needs_healing = ratio is not None and ratio < threshold
    options: list[dict[str, Any]] = []
    for item in inventory_items(observation):
        if not item.get("canUse"):
            continue
        if item_has_tag(item, "healing"):
            reason = "healing-like visible item"
            score = item_score(item, profile, "healing") + (20 if needs_healing else 0)
        else:
            reason = "usable item; not classified as healing"
            score = 20
        options.append(item_option(item, "tla_use_item", {"itemId": item.get("id")}, reason, min(score, 100)))

    options.sort(key=lambda item: int(item.get("score", 0)), reverse=True)
    limit = max(1, min(int(arguments.get("maxResults", 20)), 100))
    return {
        "health": {"current": current, "max": maximum, "ratio": ratio, "threshold": threshold, "needsHealing": needs_healing},
        "options": options[:limit],
        "guidance": "Prefer model judgment for non-healing usable items; tla_use_item performs the real client/server validation.",
    }


def ally_healing_options_payload(observation: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    chosen_id = chosen.get("id")
    threshold = float(arguments.get("allyHealthThreshold", 0.45))
    healing_items = [item for item in inventory_items(observation) if item.get("canUse") and item_has_tag(item, "healing")]
    options: list[dict[str, Any]] = []

    if not healing_items:
        return {"healthThreshold": threshold, "options": [], "guidance": "No visible usable healing-like inventory item is available for ally support."}

    for critter in observation.get("critters", []) if isinstance(observation.get("critters"), list) else []:
        if not isinstance(critter, dict):
            continue
        if critter.get("id") == chosen_id or bool(critter.get("controlledByPlayer")) or not bool(critter.get("alive", True)):
            continue
        attitude = str(critter.get("attitude") or "").casefold()
        if attitude not in {"ally", "friendly"} and not critter_support_ally(critter):
            continue
        current = critter.get("curHealth")
        maximum = critter.get("maxHealth")
        ratio: float | None = None
        if isinstance(current, (int, float)) and isinstance(maximum, (int, float)) and maximum > 0:
            ratio = float(current) / float(maximum)
        if ratio is None or ratio >= threshold:
            continue

        item = healing_items[0]
        options.append(
            item_option(
                item,
                "tla_use_item",
                {"itemId": item.get("id"), "targetId": critter.get("id")},
                "visible ally is below the configured ally healing threshold",
                min(100, item_score(item, profile, "healing") + 35),
                {
                    "target": {
                        "id": critter.get("id"),
                        "protoId": critter.get("protoId"),
                        "name": critter.get("name"),
                        "hex": critter.get("hex"),
                    },
                    "allyHealth": {"current": current, "max": maximum, "ratio": ratio, "threshold": threshold},
                },
            )
        )

    options.sort(key=lambda option: (float(option.get("allyHealth", {}).get("ratio", 1.0)), -int(option.get("score", 0))))
    limit = max(1, min(int(arguments.get("maxResults", 20)), 100))
    return {
        "healthThreshold": threshold,
        "options": options[:limit],
        "guidance": "Ally healing is inferred from visible ally health and usable healing-like inventory; tla_use_item still validates the target on the live client/server path.",
    }


def container_options_payload(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    actions = action_map_from_suggestions(action_suggestions)
    active_collection = observation.get("activeCollection") if isinstance(observation.get("activeCollection"), dict) else {}
    collection_active = bool(active_collection.get("active"))
    received_count = active_collection_received_count(active_collection)
    options: list[dict[str, Any]] = []
    for entry in interactable_entries(actions, ("operate_container",)):
        blocked_by = list(entry.get("blockedBy", [])) if isinstance(entry.get("blockedBy"), list) else []
        if not collection_active and "observation.activeCollection.active=false" not in blocked_by:
            blocked_by.append("observation.activeCollection.active=false")
        if received_count is not None and received_count <= 0 and "observation.activeCollection.receivedCount=0" not in blocked_by:
            blocked_by.append("observation.activeCollection.receivedCount=0")
        options.append(
            {
                **entry,
                "score": 90 if collection_active and not blocked_by else 10,
                "blockedBy": blocked_by,
                "requiresOpenCollection": True,
                "reason": "active collection is open with visible received items; move items before closing the modal"
                if collection_active and (received_count is None or received_count > 0)
                else "wait for received loot items or close the empty collection before trying another target"
                if collection_active
                else "open a loot/container UI first, then call tla_operate_container",
                "postAction": container_operate_post_action(),
            }
        )
    close_action = actions.get("close_screen")
    if collection_active and received_count is not None and received_count <= 0 and isinstance(close_action, dict):
        close_blockers = list(close_action.get("blockedBy", [])) if isinstance(close_action.get("blockedBy"), list) else []
        options.append(
            {
                "type": "close_screen",
                "tool": close_action.get("tool", "tla_close_screen"),
                "label": "close empty collection",
                "arguments": close_action.get("example", {}) if isinstance(close_action.get("example"), dict) else {},
                "score": 85 if not close_blockers else 15,
                "blockedBy": close_blockers,
                "reason": "active collection is empty after transfer; close the modal before choosing another world target",
            }
        )
    if not options:
        options.append(
            {
                "type": "operate_container",
                "tool": "tla_operate_container",
                "label": "take all",
                "arguments": {"take": True, "all": True},
                "score": 10,
                "blockedBy": ["operate_container not listed in current action suggestions"],
                "reason": "open a loot/container UI first, then call tla_operate_container",
                "postAction": container_operate_post_action(),
            }
        )
    limit = max(1, min(int(arguments.get("maxResults", 20)), 100))
    return {
        "activeCollection": active_collection if collection_active else {"active": False},
        "options": options[:limit],
        "guidance": "Container operations require the normal loot/container UI to be open, usually after tla_pick_item, tla_pick_hex, or tla_loot_critter.",
    }


def container_operate_post_action() -> dict[str, Any]:
    return {
        "afterQueuedCommand": "poll tla_observe/tla_next_events; command_completed only means the container operation was accepted",
        "waitForAny": ["receive_items", "observation.activeCollection.receivedCount changes", "observation.activeCollection.active=false", "screen.modalActive=false"],
        "then": "do not repeat tla_operate_container until the received item count, active collection state, or screen state changes",
    }


def reload_options_payload(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    items = inventory_items(observation)
    ammo = [item for item in items if item_has_tag(item, "ammo")]
    weapons = [item for item in items if item_reloadable_weapon(item)]
    actions = action_map_from_suggestions(action_suggestions)
    reload_candidates = interactable_entries(actions, ("reload",))
    if "reload" not in actions:
        limit = max(1, min(int(arguments.get("maxResults", 20)), 100))
        return {
            "options": [],
            "ammo": sorted(ammo, key=lambda item: item_score(item, profile, "reload"), reverse=True)[:limit],
            "guidance": "Reload is not listed in the current visible action suggestions; do not issue tla_reload from this observation.",
        }
    if not weapons:
        candidate_ids = {str(entry.get("id")) for entry in reload_candidates if entry.get("id") is not None}
        excluded_tags = {"ammo", "healing", "armor", "food", "currency", "junk"}
        weapons = [
            item
            for item in items
            if str(item.get("id")) in candidate_ids
            and item_reloadable_weapon(item)
            and not any(item_has_tag(item, tag) for tag in excluded_tags)
        ]

    options: list[dict[str, Any]] = []
    for weapon in weapons:
        args = {"itemId": weapon.get("id"), "full": True}
        if ammo:
            args["auxId"] = ammo[0].get("id")
        options.append(
            item_option(
                weapon,
                "tla_reload",
                args,
                "reloadable weapon-like item; optional auxId points at the highest-ranked visible ammo stack" if ammo else "reloadable weapon-like item; no visible ammo stack was classified",
                item_score(weapon, profile, "reload"),
                {"ammoSuggestions": ammo[:5]},
            )
        )

    options.sort(key=lambda item: int(item.get("score", 0)), reverse=True)
    limit = max(1, min(int(arguments.get("maxResults", 20)), 100))
    return {
        "options": options[:limit],
        "ammo": sorted(ammo, key=lambda item: item_score(item, profile, "reload"), reverse=True)[:limit],
        "guidance": "Reload options are inferred from visible ranged-weapon-like item tags and reload candidates; melee weapons are excluded and tla_reload validates actual compatibility.",
    }


def combat_options_payload(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    actions = action_map_from_suggestions(action_suggestions)
    modal_blocker = modal_screen_blocker(observation) if modal_screen_active(observation) else ""
    target_options = target_options_payload(observation, action_suggestions, profile, arguments)
    reload_options = reload_options_payload(observation, action_suggestions, profile, arguments)
    healing_options = healing_options_payload(observation, action_suggestions, profile, arguments)
    ally_healing_options = ally_healing_options_payload(observation, profile, arguments)
    retreat_options = retreat_options_payload(observation, action_suggestions, profile, arguments)
    cover_options = cover_options_payload(observation, action_suggestions, profile, arguments)
    ally_combat = visible_ally_combat_state(observation)
    priorities: list[dict[str, Any]] = []

    health = healing_options.get("health") if isinstance(healing_options.get("health"), dict) else {}
    stamina = stamina_state_payload(chosen, arguments)
    if modal_blocker:
        modal_tool = "tla_container_options" if gui_screen_kind(active_modal_screen_name(observation)) in {"PickUp", "Barter"} else "tla_task_options"
        priority = {"intent": "handle_modal", "score": 100, "tool": modal_tool, "reason": modal_blocker}
        modal_action = modal_action_hint(observation, action_suggestions, profile, arguments)
        if modal_action:
            priority["action"] = modal_action
        priorities.append(priority)
    if health.get("needsHealing"):
        priorities.append({"intent": "heal", "score": 95, "tool": "tla_healing_options", "reason": "chosen health is below configured threshold"})
    if ally_healing_options.get("options"):
        priorities.append({"intent": "heal_ally", "score": 94, "tool": "tla_use_item", "arguments": ally_healing_options["options"][0].get("arguments", {}), "reason": "visible ally is badly hurt and a healing item is available"})
    if stamina.get("needsRecovery"):
        recover_tool: str | None = None
        recover_arguments: dict[str, Any] = {}
        if retreat_options.get("options"):
            recover_tool = "tla_retreat_options"
            recover_arguments = {"maxResults": int(arguments.get("maxResults", 5))}
        elif action_executable(actions.get("clear_actions", {})):
            recover_tool = "tla_clear_actions"
        priorities.append(
            {
                "intent": "recover_stamina",
                "score": 93 if stamina.get("critical") else 86,
                "tool": recover_tool,
                "arguments": recover_arguments,
                "reason": "chosen stamina is low; withdraw, pause, or clear queued actions before attacking again",
            }
        )
    if not modal_blocker and target_options.get("options"):
        attack_score = 80 if chosen.get("inCombat") else 55
        attack_reason = "visible attack candidates exist"
        if ally_combat.get("active"):
            attack_score = max(attack_score, 92 if ally_combat.get("critical") else 86)
            attack_reason = "visible ally is in combat; assess targets before looting or wandering"
        priorities.append({"intent": "attack_or_assess_target", "score": attack_score, "tool": "tla_target_options", "reason": attack_reason})
    if reload_options.get("options"):
        priorities.append({"intent": "reload", "score": 65, "tool": "tla_reload_options", "reason": "weapon-like item and ammo/reload candidates exist"})
    if retreat_options.get("options"):
        priorities.append({"intent": "reposition", "score": 60 if chosen.get("inCombat") else 35, "tool": "tla_retreat_options", "reason": "visible movement candidates can be checked for safer positions"})
    if cover_options.get("options"):
        priorities.append({"intent": "find_cover", "score": 55, "tool": "tla_cover_options", "reason": "cover scan can rank visible blockers"})

    priorities.sort(key=lambda item: int(item.get("score", 0)), reverse=True)
    return {
        "style": profile.get("combatStyle"),
        "state": {
            "inCombat": chosen.get("inCombat"),
            "alive": chosen.get("alive"),
            "health": health,
            "stamina": stamina,
            "modalBlocker": modal_blocker,
            "allyInCombat": ally_combat,
            "visibleTargets": len(target_options.get("options", [])) if isinstance(target_options.get("options"), list) else 0,
        },
        "priorities": priorities,
        "targets": target_options,
        "reload": reload_options,
        "healing": healing_options,
        "allyHealing": ally_healing_options,
        "retreat": retreat_options,
        "cover": cover_options,
        "guidance": "Combat options are tactical advice from client-visible state. Use env trace/path/cover tools before movement or shooting decisions when position matters.",
    }


def target_options_payload(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    actions = action_map_from_suggestions(action_suggestions)
    if modal_screen_active(observation):
        blocker = modal_screen_blocker(observation)
        blocked: dict[str, Any] = {"reason": blocker, "tool": "tla_container_options" if gui_screen_kind(active_modal_screen_name(observation)) in {"PickUp", "Barter"} else "tla_task_options"}
        modal_action = modal_action_hint(observation, action_suggestions, profile, arguments)
        if modal_action:
            blocked["action"] = modal_action
        return {
            "options": [],
            "blocked": [blocked],
            "screen": compact_screen_state(observation_screen_state(observation)),
            "guidance": "Do not attack while a modal screen is active; handle or close the visible modal first.",
        }

    critters = [entry for entry in observation.get("critters", []) if isinstance(entry, dict)]
    critters_by_id = {str(entry.get("id")): entry for entry in critters if entry.get("id") is not None}
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    chosen_id = str(chosen.get("id")) if chosen.get("id") is not None else ""
    ally_combat = visible_ally_combat_state(observation)
    ally_hexes = [safe_hex_value_xy(ally.get("hex")) for ally in ally_combat.get("allies", []) if isinstance(ally, dict)]
    ally_hexes = [hex_xy for hex_xy in ally_hexes if hex_xy is not None]
    options: list[dict[str, Any]] = []

    for entry in interactable_entries(actions, ("attack_entity", "attack_hex")):
        critter = critters_by_id.get(str(entry.get("id")), {})
        controlled_by_player = bool(critter.get("controlledByPlayer"))
        score = 75
        reasons = [entry.get("reason") or "visible attack candidate"]
        if critter.get("inCombat"):
            score += 10
            reasons.append("target is in combat")
        if critter_dangerous(critter):
            score += 15
            reasons.append("target looks dangerous by visible proto/name")
        target_xy = safe_hex_value_xy(critter.get("hex"))
        if ally_hexes and target_xy is not None:
            ally_distance = min(approximate_hex_distance(target_xy, ally_xy) for ally_xy in ally_hexes)
            if ally_distance <= 2:
                score += 30
                reasons.append("target is next to a visible ally in combat")
            elif ally_distance <= 6:
                score += 15
                reasons.append("target is near a visible ally in combat")
            elif ally_distance <= 16:
                score += 8
                reasons.append("target is on the route toward a visible ally in combat")
        if controlled_by_player:
            score -= 35
            reasons.append("player-controlled target; avoid unless explicitly intended")
        if critter_support_ally(critter):
            score -= 45
            reasons.append("visible ally/support NPC; avoid friendly fire unless explicitly allowed")
        protected_nonhostile = critter_protected_nonhostile(critter)
        if protected_nonhostile:
            score -= 65
            reasons.append("visible neutral/social NPC; avoid unless the host explicitly allows neutral targets")
        if str(critter.get("id")) == chosen_id:
            continue
        option = {
            **entry,
            "score": max(0, min(score, 100)),
            "critter": {
                key: critter.get(key)
                for key in ("id", "protoId", "name", "hex", "controlledByPlayer", "alive", "dead", "inCombat", "curHealth", "maxHealth", "dialogId", "notTalkable", "teamId", "allyTeams", "hasTrader")
                if key in critter
            },
            "reasons": reasons,
            "recommendedChecks": ["tla_env_trace", "tla_nav_plan"],
        }
        if protected_nonhostile:
            option["protectedNonHostile"] = True
        if ally_hexes and target_xy is not None:
            option["allyDistance"] = ally_distance
        options.append(option)

    options.sort(key=lambda item: (int(item.get("score", 0)), -int(item.get("allyDistance", 999))), reverse=True)
    limit = max(1, min(int(arguments.get("maxResults", 20)), 100))
    return {
        "options": options[:limit],
        "guidance": "Targets are attack affordances, not moral/social permission. Avoid player targets unless the role/test explicitly calls for it.",
    }


def critter_dangerous(critter: dict[str, Any]) -> bool:
    text = f"{critter.get('protoId', '')} {critter.get('name', '')}".casefold()
    return any(marker in text for marker in DANGEROUS_TARGET_MARKERS)


def critter_support_ally(critter: dict[str, Any]) -> bool:
    text = f"{critter.get('protoId', '')} {critter.get('name', '')}".casefold()
    return any(marker in text for marker in ALLY_TARGET_MARKERS)


def critter_protected_nonhostile(critter: dict[str, Any]) -> bool:
    if bool(critter.get("controlledByPlayer")) or bool(critter.get("isChosen")):
        return True
    if critter_support_ally(critter):
        return True
    if bool(critter.get("hasTrader")):
        return True

    text_parts = [str(critter.get("protoId") or ""), str(critter.get("name") or ""), str(critter.get("dialogId") or "")]
    team_id = str(critter.get("teamId") or "")
    text_parts.append(team_id)
    ally_teams = critter.get("allyTeams")
    if isinstance(ally_teams, list):
        text_parts.extend(str(team) for team in ally_teams)
    text = " ".join(text_parts).casefold()
    teams_text = " ".join([team_id, *(str(team) for team in ally_teams if team is not None)]).casefold() if isinstance(ally_teams, list) else team_id.casefold()

    if any(marker in teams_text for marker in PROTECTED_TARGET_TEAM_MARKERS):
        return True
    if any(marker in text for marker in PROTECTED_TARGET_MARKERS):
        return True

    dialog_id = critter.get("dialogId")
    has_dialog = isinstance(dialog_id, str) and bool(dialog_id.strip()) and not bool(critter.get("notTalkable"))
    # A talkable, non-combat NPC is protected from default attacks even when its name matches a
    # dangerous marker (e.g. a player's own guard NPC_Dog / dialog dogs). A dialog NPC that is
    # actually fighting (inCombat) is not protected.
    return has_dialog and not bool(critter.get("inCombat"))


def visible_ally_combat_state(observation: dict[str, Any]) -> dict[str, Any]:
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    chosen_id = chosen.get("id")
    allies: list[dict[str, Any]] = []
    critical = False
    for critter in observation.get("critters", []) if isinstance(observation.get("critters"), list) else []:
        if not isinstance(critter, dict):
            continue
        if critter.get("id") == chosen_id or bool(critter.get("controlledByPlayer")) or not bool(critter.get("alive", True)) or not bool(critter.get("inCombat")):
            continue
        if critter_dangerous(critter) and not critter_support_ally(critter):
            continue
        ratio: float | None = None
        try:
            max_health = float(critter.get("maxHealth") or 0)
            cur_health = float(critter.get("curHealth") or 0)
            if max_health > 0:
                ratio = cur_health / max_health
                if ratio <= 0.4:
                    critical = True
        except (TypeError, ValueError):
            ratio = None
        allies.append(
            {
                "id": critter.get("id"),
                "protoId": critter.get("protoId"),
                "name": critter.get("name"),
                "hex": critter.get("hex"),
                "healthRatio": ratio,
            }
        )
    return {"active": bool(allies), "count": len(allies), "critical": critical, "allies": allies[:5]}


def retreat_options_payload(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    actions = action_map_from_suggestions(action_suggestions)
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    chosen_xy = safe_hex_value_xy(chosen.get("hex"))
    threat_hexes = visible_threat_hexes(observation)
    current_threat_distance = nearest_threat_distance(chosen_xy, threat_hexes)
    options: list[dict[str, Any]] = []
    if threat_hexes:
        options.append(
            {
                "tool": "tla_find_safe_step",
                "arguments": {"maxCandidates": int(arguments.get("maxCandidates", 6))},
                "score": 82,
                "recommendedChecks": ["tla_find_safe_step", "tla_env_tactical_path"],
                "reason": "visible threats exist; ask the tactical planner for a reachable standing hex before retreating",
            }
        )
    for entry in interactable_entries(actions, ("move_to_hex",)):
        if retreat_entry_is_landmark(entry):
            continue
        target_xy = safe_hex_value_xy(entry.get("hex"))
        target_threat_distance = nearest_threat_distance(target_xy, threat_hexes)
        distance_delta = None
        score = 50
        reasons = [entry.get("reason") or "movement candidate; validate tactical safety before retreating"]
        if current_threat_distance is not None and target_threat_distance is not None:
            distance_delta = target_threat_distance - current_threat_distance
            score += max(-30, min(35, distance_delta * 12))
            if distance_delta > 0:
                reasons.append("candidate increases distance from visible threat(s)")
            elif distance_delta < 0:
                reasons.append("candidate moves closer to visible threat(s)")
            else:
                reasons.append("candidate keeps the same visible-threat distance")
        options.append(
            {
                **entry,
                "score": max(0, min(score, 100)),
                "threatDistance": target_threat_distance,
                "currentThreatDistance": current_threat_distance,
                "distanceDelta": distance_delta,
                "recommendedChecks": ["tla_find_safe_step", "tla_env_tactical_path"],
                "reason": "; ".join(reasons),
            }
        )
    if not options:
        options.append(
            {
                "tool": "tla_find_safe_step",
                "arguments": {"maxCandidates": int(arguments.get("maxCandidates", 6))},
                "score": 30,
                "recommendedChecks": ["tla_find_safe_step"],
                "reason": "ask the tactical planner for safe visible movement candidates",
            }
        )
    options.sort(key=lambda item: int(item.get("score", 0)), reverse=True)
    limit = max(1, min(int(arguments.get("maxResults", 20)), 100))
    return {"options": options[:limit], "threats": len(threat_hexes), "guidance": "Retreat options should be path-checked immediately before movement."}


def retreat_entry_is_landmark(entry: dict[str, Any]) -> bool:
    text = f"{entry.get('label', '')} {entry.get('reason', '')}".casefold()
    return "map item " in text or "visible critter " in text


def cover_options_payload(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    chosen_id = chosen.get("id")
    threats = [
        critter
        for critter in observation.get("critters", [])
        if isinstance(critter, dict) and critter.get("id") != chosen_id and critter.get("alive", True) and not critter.get("dead")
    ]
    radius = int(arguments.get("radius", 6))
    option = {
        "tool": "tla_find_cover",
        "arguments": {"radius": radius, "maxResults": int(arguments.get("maxResults", 20))},
        "score": 55,
        "reason": "scan visible nearby blockers and line-of-fire obstacles",
    }
    if threats:
        option["visibleThreatCandidates"] = len(threats)
    return {
        "options": [option],
        "guidance": "tla_cover_options does not scan by itself; call tla_find_cover for current obstacle anchors, then validate standing hexes with tla_nav_plan.",
    }


def dialog_answer_intent(text: str) -> tuple[str, list[str], int]:
    lower_text = text.lower()
    reasons: list[str] = []
    for intent, markers in ANSWER_INTENT_MARKERS.items():
        if any(marker in lower_text for marker in markers):
            reasons.append(f"{intent} marker")
            score = {
                "accept": 85,
                "question": 70,
                "trade": 68,
                "healing": 66,
                "leave": 35,
                "refuse": 30,
                "hostile": 20,
            }.get(intent, 50)
            return intent, reasons, score
    return "roleplay", ["no strong marker"], 50


def dialog_options_payload(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    actions = action_map_from_suggestions(action_suggestions)
    dialog = observation.get("dialog") if isinstance(observation.get("dialog"), dict) else {}
    answers = dialog.get("answers") if isinstance(dialog.get("answers"), list) else []
    candidates = interactable_entries(actions, ("dialog_answer",))
    dialog_action = actions.get("dialog_answer") if isinstance(actions.get("dialog_answer"), dict) else {}
    candidate_by_index = {
        str(candidate.get("arguments", {}).get("answerIndex")): candidate
        for candidate in candidates
        if isinstance(candidate.get("arguments"), dict) and candidate.get("arguments", {}).get("answerIndex") is not None
    }
    options: list[dict[str, Any]] = []

    for answer in answers:
        if not isinstance(answer, dict):
            continue
        index = answer.get("index")
        text = str(answer.get("text", ""))
        intent, reasons, base_score = dialog_answer_intent(text)
        candidate = candidate_by_index.get(str(index), {})
        score = base_score
        if intent == "hostile" and str(profile.get("combatStyle", "")).lower() not in {"aggressive", "hostile"}:
            score = min(score, 25)
            reasons.append("hostile answer lowered by non-aggressive profile")
        if intent == "trade" and str(profile.get("role", "")).lower().find("trader") >= 0:
            score += 10
            reasons.append("trader role")
        blocked_by: list[str] = []
        if not dialog_action:
            blocked_by.append("dialog_answer action unavailable")
        elif not candidate:
            blocked_by.append("answer missing from current action candidates")
        options.append(
            {
                "index": index,
                "text": text,
                "intent": intent,
                "score": max(0, min(score, 100)),
                "tool": "tla_dialog_answer",
                "arguments": {"answerIndex": index},
                "candidate": candidate,
                "executable": not blocked_by,
                "blockedBy": blocked_by,
                "reasons": reasons,
            }
        )

    options.sort(key=lambda item: int(item.get("score", 0)), reverse=True)
    limit = max(1, min(int(arguments.get("maxResults", 20)), 100))
    return {
        "active": bool(dialog.get("active")),
        "dialogId": dialog.get("dialogId"),
        "talkerId": dialog.get("talkerId"),
        "text": dialog.get("text"),
        "durationMs": dialog.get("durationMs"),
        "options": options[:limit],
        "counts": {"answers": len(answers), "options": min(len(options), limit), "totalOptions": len(options)},
        "guidance": "Dialog options classify visible answer text only. The model should choose according to role, quest context, and risk; tla_dialog_answer remains the executed command.",
    }


def quest_summary_payload(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    dialog = dialog_options_payload(observation, action_suggestions, profile, arguments)
    limit = max(1, min(int(arguments.get("maxResults", 20)), 100))
    visible_surfaces = visible_quest_surfaces(observation, limit)
    hints: list[dict[str, Any]] = []
    hints.extend(quest_hints_from_surfaces(visible_surfaces, limit))
    for option in dialog.get("options", []) if isinstance(dialog.get("options"), list) else []:
        if option.get("intent") in {"accept", "question", "trade", "healing"}:
            hints.append(
                {
                    "source": "dialog",
                    "intent": option.get("intent"),
                    "text": option.get("text"),
                    "arguments": option.get("arguments"),
                    "reason": "active visible dialog answer may advance or clarify a task",
                }
            )
    has_visible_quest_data = bool(visible_surfaces)
    return {
        "available": has_visible_quest_data,
        "questDataExported": has_visible_quest_data,
        "visibleSurfaces": visible_surfaces,
        "hints": hints[:limit],
        "guidance": "Client-visible quest/PDA surfaces were found in observation; use them as visible player knowledge only."
        if has_visible_quest_data
        else "No dedicated client-visible quest/PDA summary is exported yet. Use active dialog text, visible map/global state, speech, and normal commands; add AiControl observation/events when quest/PDA data becomes client-visible.",
    }


def visible_quest_surfaces(observation: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    surfaces: list[dict[str, Any]] = []

    for field in QUEST_SURFACE_FIELDS:
        if field in observation:
            append_visible_quest_surface(surfaces, f"observation.{field}", observation.get(field), limit)

    pda = observation.get("pda") if isinstance(observation.get("pda"), dict) else {}
    for field in PDA_QUEST_SURFACE_FIELDS:
        if field in pda:
            append_visible_quest_surface(surfaces, f"observation.pda.{field}", pda.get(field), limit)

    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    for field in ("visibleQuests", "questLog", "pdaQuests"):
        if field in chosen:
            append_visible_quest_surface(surfaces, f"observation.chosen.{field}", chosen.get(field), limit)

    return surfaces


def append_visible_quest_surface(surfaces: list[dict[str, Any]], source: str, value: Any, limit: int) -> None:
    compact = compact_visible_quest_surface(value, limit)
    if compact is None:
        return
    surfaces.append({"source": source, **compact})


def compact_visible_quest_surface(value: Any, limit: int) -> dict[str, Any] | None:
    if isinstance(value, list):
        return {"kind": "list", "count": len(value), "entries": [compact_visible_quest_entry(entry) for entry in value[:limit]]}
    if isinstance(value, dict):
        for field in ("entries", "quests", "items", "notifications"):
            entries = value.get(field)
            if isinstance(entries, list):
                result = {key: safe_json_scalar(value.get(key)) for key in QUEST_ENTRY_FIELDS if key in value and safe_json_scalar(value.get(key)) is not None}
                result.update({"kind": "object", "count": len(entries), "entries": [compact_visible_quest_entry(entry) for entry in entries[:limit]]})
                return result
        entry = compact_visible_quest_entry(value)
        if entry:
            return {"kind": "object", "count": 1, "entry": entry}
        keys = [str(key) for key, inner_value in value.items() if safe_json_scalar(inner_value) is not None]
        return {"kind": "object", "count": len(value), "keys": sorted(keys)[:limit]}
    scalar = safe_json_scalar(value)
    if scalar is not None:
        return {"kind": "scalar", "count": 1, "entry": {"value": scalar}}
    return None


def compact_visible_quest_entry(entry: Any) -> dict[str, Any]:
    if isinstance(entry, dict):
        return {key: safe_json_scalar(entry.get(key)) for key in QUEST_ENTRY_FIELDS if key in entry and safe_json_scalar(entry.get(key)) is not None}
    scalar = safe_json_scalar(entry)
    if scalar is not None:
        return {"value": scalar}
    return {}


def safe_json_scalar(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return None


def quest_hints_from_surfaces(surfaces: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    hints: list[dict[str, Any]] = []
    for surface in surfaces:
        entries: list[Any] = []
        if isinstance(surface.get("entries"), list):
            entries.extend(surface["entries"])
        elif isinstance(surface.get("entry"), dict):
            entries.append(surface["entry"])
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            text = quest_entry_text(entry)
            hints.append(
                {
                    "source": "quest_surface",
                    "surface": surface.get("source"),
                    "id": entry.get("id", entry.get("questId")),
                    "text": text,
                    "status": entry.get("status", entry.get("state")),
                    "reason": "client-visible quest/PDA surface",
                }
            )
            if len(hints) >= limit:
                return hints
    return hints


def quest_entry_text(entry: dict[str, Any]) -> str:
    for field in ("objective", "title", "name", "text", "description", "status", "state", "value"):
        value = entry.get(field)
        if value is not None and str(value).strip():
            return str(value)
    return "visible quest/PDA entry"


def global_interest_entry(interest: dict[str, Any]) -> dict[str, Any]:
    entry = {key: interest.get(key) for key in ("type", "typeEnum", "id", "pos", "radius", "distance", "enterable", "inRange", "enterArguments") if key in interest}
    interest_type = observed_interest_type_name(interest)
    if interest_type and not entry.get("type"):
        entry["type"] = interest_type
    enter_arguments = interest.get("enterArguments") if isinstance(interest.get("enterArguments"), dict) else {}
    if not enter_arguments:
        enter_arguments = {"interestType": interest_type, "interestId": interest.get("id")}
    executable_enter = False
    if interest.get("enterable") and interest.get("inRange") and interest_type != "unknown_place":
        try:
            typed_command_payload("tla_global_enter_interest", enter_arguments)
            executable_enter = True
        except (TypeError, ValueError):
            executable_enter = False
    if executable_enter:
        entry["tool"] = "tla_global_enter_interest"
        entry["arguments"] = dict(enter_arguments)
        entry["score"] = 95
        entry["reason"] = "in-range enterable global-map interest"
    elif isinstance(interest.get("pos"), dict):
        pos = interest["pos"]
        entry["tool"] = "tla_global_move_to"
        entry["arguments"] = {"x": get_hex_value(pos, "x"), "y": get_hex_value(pos, "y")}
        distance = interest.get("distance")
        entry["score"] = max(10, 80 - min(int(distance), 70)) if isinstance(distance, int) else 45
        entry["reason"] = "visible global-map interest position; travel first"
    else:
        entry["score"] = 5
        entry["reason"] = "global interest lacks a visible position"
    return entry


def global_options_payload(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    global_map = observation.get("globalMap") if isinstance(observation.get("globalMap"), dict) else {}
    actions = action_map_from_suggestions(action_suggestions)
    interests = [global_interest_entry(interest) for interest in global_map.get("interests", []) if isinstance(interest, dict)]
    interests.sort(key=lambda entry: (not bool(entry.get("inRange")), not bool(entry.get("enterable")), int(entry.get("distance", 1_000_000)) if isinstance(entry.get("distance"), int) else 1_000_000))
    moves = interactable_entries(actions, ("global_move_to",))
    enters = interactable_entries(actions, ("global_enter_interest",))
    limit = max(1, min(int(arguments.get("maxResults", 20)), 100))
    return {
        "active": bool(global_map.get("active")),
        "pos": global_map.get("pos"),
        "targetPos": global_map.get("targetPos"),
        "isMoving": global_map.get("isMoving"),
        "size": global_map.get("size"),
        "interests": interests[:limit],
        "moveOptions": moves[:limit],
        "enterOptions": enters[:limit],
        "counts": {"interests": len(interests), "moveOptions": len(moves), "enterOptions": len(enters)},
        "guidance": "Global options are client-visible travel/entry candidates. Use tla_travel_plan for a single next step, then execute through tla_global_move_to or tla_global_enter_interest.",
    }


def selected_global_interest(global_map: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any] | None:
    interests = [interest for interest in global_map.get("interests", []) if isinstance(interest, dict)]
    if "interestId" in arguments:
        wanted_id = str(arguments.get("interestId"))
        wanted_type = str(arguments.get("interestType", ""))
        for interest in interests:
            if str(interest.get("id")) != wanted_id:
                continue
            if wanted_type and observed_interest_type_name(interest) != wanted_type:
                continue
            return interest
    index_argument = "globalOptionIndex" if "globalOptionIndex" in arguments else "targetIndex" if "targetIndex" in arguments else ""
    if index_argument:
        index = int(arguments.get(index_argument, 0))
        if index < 0 or index >= len(interests):
            raise ValueError(f"globalOptionIndex out of range; have {len(interests)} interests")
        return interests[index]
    if interests:
        sorted_interests = sorted(interests, key=lambda interest: (not bool(interest.get("inRange")), not bool(interest.get("enterable")), int(interest.get("distance", 1_000_000)) if isinstance(interest.get("distance"), int) else 1_000_000))
        return sorted_interests[0]
    return None


def travel_plan_payload(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    global_map = observation.get("globalMap") if isinstance(observation.get("globalMap"), dict) else {}
    if not global_map.get("active"):
        return {"active": False, "plan": None, "guidance": "Chosen is not on the global map; no global travel plan is available from current observation."}

    explicit_pos = explicit_global_pos(arguments)
    target_interest = None if explicit_pos is not None else selected_global_interest(global_map, arguments)
    if explicit_pos is not None:
        plan = {"step": "move", "tool": "tla_global_move_to", "arguments": explicit_pos, "reason": "explicit global position target"}
    elif isinstance(target_interest, dict):
        entry = global_interest_entry(target_interest)
        plan = {"step": "enter" if entry.get("tool") == "tla_global_enter_interest" else "move", "tool": entry.get("tool"), "arguments": entry.get("arguments", {}), "interest": entry, "reason": entry.get("reason")}
    else:
        options = global_options_payload(observation, action_suggestions, profile, arguments)
        move_options = options.get("moveOptions") if isinstance(options.get("moveOptions"), list) else []
        plan = {"step": "move", "tool": "tla_global_move_to", "arguments": move_options[0].get("arguments", {}) if move_options else {}, "reason": "fallback global movement option"} if move_options else None

    return {
        "active": True,
        "currentPos": global_map.get("pos"),
        "targetPos": global_map.get("targetPos"),
        "isMoving": global_map.get("isMoving"),
        "plan": plan,
        "guidance": "Travel plans are one-step advice: move toward a visible coordinate or enter an in-range interest. Poll observation after execution.",
    }


def explicit_global_pos(arguments: dict[str, Any]) -> dict[str, int] | None:
    if "x" in arguments or "y" in arguments:
        if "x" not in arguments or "y" not in arguments:
            raise ValueError("x and y must be passed together")
        return {"x": int(arguments["x"]), "y": int(arguments["y"])}
    return None


def enter_options_payload(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    options = global_options_payload(observation, action_suggestions, profile, arguments)
    enterable = [entry for entry in options.get("interests", []) if isinstance(entry, dict) and entry.get("tool") == "tla_global_enter_interest"]
    blocked = [
        {
            **entry,
            "blockedBy": global_interest_blockers(entry),
        }
        for entry in options.get("interests", [])
        if isinstance(entry, dict) and entry.get("tool") != "tla_global_enter_interest"
    ]
    limit = max(1, min(int(arguments.get("maxResults", 20)), 100))
    return {
        "active": options.get("active"),
        "options": enterable[:limit],
        "blocked": blocked[:limit],
        "guidance": "Only in-range enterable non-unknown interests are executable through tla_global_enter_interest. Use tla_travel_plan or tla_global_move_to for out-of-range interests.",
    }


def global_interest_blockers(entry: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not entry.get("enterable"):
        blockers.append("enterable=false")
    if not entry.get("inRange"):
        blockers.append("inRange=false")
    if entry.get("type") == "unknown_place":
        blockers.append("unknown_place cannot be entered directly")
    if not blockers:
        blockers.append("no executable enter tool for this interest")
    return blockers


def map_transition_options_payload(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    global_map = observation.get("globalMap") if isinstance(observation.get("globalMap"), dict) else {}
    if global_map.get("active"):
        enter = enter_options_payload(observation, action_suggestions, profile, arguments)
        travel = travel_plan_payload(observation, action_suggestions, profile, arguments)
        return {
            "mode": "global",
            "options": enter.get("options", []),
            "blocked": enter.get("blocked", []),
            "travelPlan": travel.get("plan"),
            "guidance": "On the global map, transitions are enterable interests; otherwise move toward visible interests first.",
        }

    actions = action_map_from_suggestions(action_suggestions)
    options = local_map_exit_options(observation)
    options.extend(local_elevator_trigger_options(observation, arguments))
    options.extend(interactable_entries(actions, ("global_enter_interest", "global_move_to")))
    if str(arguments.get("targetMapProtoId") or "").strip():
        options.sort(key=lambda entry: int(entry.get("score", 0)), reverse=True)
    return {
        "mode": "map" if observation.get("hasMap") else "ui",
        "options": options,
        "blocked": [] if options else [{"reason": "no client-visible map transition affordance in current observation"}],
        "guidance": "On local maps, visible MapExit items and authored elevator triggers are normal movement targets: move onto the target hex and let server validation decide whether transfer is allowed.",
    }


def local_map_exit_options(observation: dict[str, Any]) -> list[dict[str, Any]]:
    if not observation.get("hasMap"):
        return []

    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    chosen_xy = safe_hex_value_xy(chosen.get("hex"))
    result: list[dict[str, Any]] = []
    for item in observation.get("mapItems", []) if isinstance(observation.get("mapItems"), list) else []:
        if not isinstance(item, dict) or not item.get("hasMapExit") or not isinstance(item.get("hex"), dict):
            continue
        hex_value = item["hex"]
        exit_xy = safe_hex_value_xy(hex_value)
        distance = approximate_hex_distance(chosen_xy, exit_xy) if chosen_xy is not None and exit_xy is not None else None
        result.append(
            {
                "kind": "local_map_exit",
                "tool": "tla_move_to_hex",
                "arguments": {"x": get_hex_value(hex_value, "x"), "y": get_hex_value(hex_value, "y")},
                "item": {key: item.get(key) for key in ("id", "protoId", "name", "hex", "hasMapEntry", "mapEntryName") if key in item},
                "distance": distance,
                "score": max(30, 90 - min(int(distance or 0), 60)),
                "reason": "visible local map exit; move onto the exit hex",
            }
        )

    result.sort(key=lambda entry: (int(entry.get("distance", 1_000_000)) if isinstance(entry.get("distance"), int) else 1_000_000, str(entry.get("item", {}).get("protoId", ""))))
    return result


def local_elevator_trigger_options(observation: dict[str, Any], arguments: dict[str, Any]) -> list[dict[str, Any]]:
    if not observation.get("hasMap"):
        return []

    map_info = observation.get("map") if isinstance(observation.get("map"), dict) else {}
    map_proto_id = str(map_info.get("protoId") or "").strip()
    if not map_proto_id:
        return []

    triggers = authored_elevator_triggers_for_map(map_proto_id)
    if not triggers:
        return []

    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    chosen_xy = safe_hex_value_xy(chosen.get("hex"))
    target_map_proto_id = str(arguments.get("targetMapProtoId") or "").strip()
    result: list[dict[str, Any]] = []
    for trigger in triggers:
        hexes = trigger.get("hexes") if isinstance(trigger.get("hexes"), list) else []
        trigger_hex = nearest_authored_hex(hexes, chosen_xy)
        if trigger_hex is None:
            continue
        trigger_xy = safe_hex_value_xy(trigger_hex)
        distance = approximate_hex_distance(chosen_xy, trigger_xy) if chosen_xy is not None and trigger_xy is not None else None
        levels = [str(level) for level in trigger.get("levels", []) if str(level)]
        follow_up: dict[str, Any] = {
            "tool": "tla_ui_answer",
            "options": [{"answerId": level, "mapProtoId": level, "preferred": bool(target_map_proto_id and level == target_map_proto_id)} for level in levels],
        }
        if target_map_proto_id and target_map_proto_id in levels and target_map_proto_id != map_proto_id:
            follow_up["arguments"] = {"answerId": target_map_proto_id}
        entry_score = 86 if target_map_proto_id and target_map_proto_id in levels else 78
        if isinstance(distance, int):
            entry_score = max(62, entry_score - min(distance // 8, 20))
        result.append(
            {
                "kind": "local_elevator_trigger",
                "tool": "tla_move_to_hex",
                "arguments": {"x": trigger_hex["x"], "y": trigger_hex["y"]},
                "distance": distance,
                "score": entry_score,
                "reason": "authored elevator trigger; move onto the trigger hex to open the elevator prompt",
                "trigger": {
                    "mapProtoId": map_proto_id,
                    "triggerEntry": trigger.get("triggerEntry"),
                    "hex": trigger.get("hex"),
                    "levels": levels,
                    "targetMapProtoId": target_map_proto_id or None,
                },
                "followUp": follow_up,
            }
        )

    result.sort(
        key=lambda entry: (
            0 if target_map_proto_id and target_map_proto_id in entry.get("trigger", {}).get("levels", []) else 1,
            int(entry.get("distance", 1_000_000)) if isinstance(entry.get("distance"), int) else 1_000_000,
            str(entry.get("trigger", {}).get("triggerEntry", "")),
        )
    )
    return result


def nearest_authored_hex(hexes: list[Any], origin: tuple[int, int] | None) -> dict[str, int] | None:
    normalized: list[dict[str, int]] = []
    seen: set[tuple[int, int]] = set()
    for hex_value in hexes:
        xy = safe_hex_value_xy(hex_value)
        if xy is None or xy in seen:
            continue
        seen.add(xy)
        normalized.append({"x": xy[0], "y": xy[1]})
    if not normalized:
        return None
    if origin is None:
        return normalized[0]
    return min(normalized, key=lambda item: approximate_hex_distance(origin, (item["x"], item["y"])))


def authored_map_file(map_proto_id: str) -> Path | None:
    if not map_proto_id or not MAPS_ROOT.exists():
        return None
    for path in MAPS_ROOT.rglob(f"{map_proto_id}.fomap"):
        return path
    return None


def authored_elevator_triggers_for_map(map_proto_id: str) -> list[dict[str, Any]]:
    if map_proto_id in AUTHORED_ELEVATOR_TRIGGER_CACHE:
        return [copy_authored_elevator_trigger(trigger) for trigger in AUTHORED_ELEVATOR_TRIGGER_CACHE[map_proto_id]]

    path = authored_map_file(map_proto_id)
    if path is None:
        AUTHORED_ELEVATOR_TRIGGER_CACHE[map_proto_id] = []
        return []

    triggers = parse_authored_elevator_triggers(path)
    AUTHORED_ELEVATOR_TRIGGER_CACHE[map_proto_id] = triggers
    return [copy_authored_elevator_trigger(trigger) for trigger in triggers]


def copy_authored_elevator_trigger(trigger: dict[str, Any]) -> dict[str, Any]:
    return {
        "triggerEntry": trigger.get("triggerEntry"),
        "hex": dict(trigger.get("hex")) if isinstance(trigger.get("hex"), dict) else None,
        "hexes": [dict(hex_value) for hex_value in trigger.get("hexes", []) if isinstance(hex_value, dict)],
        "levels": list(trigger.get("levels", [])) if isinstance(trigger.get("levels"), list) else [],
    }


def parse_authored_elevator_triggers(path: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    in_item = False
    item_proto = ""
    item_trigger_script = ""
    item_trigger_entry = ""
    item_levels: list[str] = []
    item_hex: dict[str, int] | None = None
    item_hexes: list[dict[str, int]] = []

    def flush_item() -> None:
        if item_proto != "Trigger" or item_trigger_script != "Elevator::ShowElevator" or not item_levels or item_hex is None:
            return
        hexes: list[dict[str, int]] = []
        seen: set[tuple[int, int]] = set()
        for hex_value in [item_hex, *item_hexes]:
            key = (hex_value["x"], hex_value["y"])
            if key in seen:
                continue
            seen.add(key)
            hexes.append(dict(hex_value))
        result.append({"triggerEntry": item_trigger_entry, "hex": dict(item_hex), "hexes": hexes, "levels": list(item_levels)})

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line == "[Item]":
            if in_item:
                flush_item()
            in_item = True
            item_proto = ""
            item_trigger_script = ""
            item_trigger_entry = ""
            item_levels = []
            item_hex = None
            item_hexes = []
            continue
        if line.startswith("[") and line.endswith("]"):
            if in_item:
                flush_item()
            in_item = False
            continue
        if not in_item:
            continue

        if line.startswith("$Proto"):
            item_proto = line.split("=", 1)[1].strip() if "=" in line else ""
            continue
        if line.startswith("TriggerScript"):
            item_trigger_script = line.split("=", 1)[1].strip() if "=" in line else ""
            continue
        if line.startswith("TriggerEntry"):
            item_trigger_entry = line.split("=", 1)[1].strip() if "=" in line else ""
            continue
        if line.startswith("ElevatorLevels"):
            value = line.split("=", 1)[1].strip() if "=" in line else ""
            item_levels = [token for token in value.split() if token]
            continue

        hex_match = FOMAP_HEX_VALUE_RE.match(line)
        if hex_match is not None:
            item_hex = {"x": int(hex_match.group(1)), "y": int(hex_match.group(2))}
            continue

        multihex_match = FOMAP_MULTIHEX_VALUE_RE.search(line)
        if multihex_match is not None:
            item_hexes.append({"x": int(multihex_match.group(1)), "y": int(multihex_match.group(2))})

    if in_item:
        flush_item()
    return result


def modal_task_options(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> list[dict[str, Any]]:
    if not modal_screen_active(observation):
        return []

    screen = observation_screen_state(observation)
    screen_name = active_modal_screen_name(observation)
    screen_kind = gui_screen_kind(screen_name)
    tasks: list[dict[str, Any]] = []

    ui_prompt = ui_prompt_options_payload(observation, action_suggestions, profile, arguments)
    ui_prompt_option = first_executable_option(ui_prompt.get("options", []) if isinstance(ui_prompt.get("options"), list) else [], {"tla_ui_answer"})
    if ui_prompt_option is not None:
        tasks.append(
            task_option(
                "ui_prompt",
                int(ui_prompt_option.get("score", 82)),
                f"answer active {ui_prompt.get('kind', 'ui')} prompt before issuing world actions",
                "tla_ui_answer",
                ui_prompt_option.get("arguments", {}) if isinstance(ui_prompt_option.get("arguments"), dict) else {},
                {"screen": compact_screen_state(screen), "uiPrompt": ui_prompt.get("prompt"), "button": ui_prompt_option},
            )
        )
        return tasks

    if screen_kind in {"PickUp", "Barter"}:
        container = container_options_payload(observation, action_suggestions, profile, arguments)
        option = first_executable_option(container.get("options", []), {"tla_operate_container"})
        if option is not None:
            tasks.append(
                task_option(
                    "modal_container",
                    86,
                    f"operate active {screen_kind} collection before issuing world actions",
                    "tla_operate_container",
                    option.get("arguments", {}),
                    {"screen": compact_screen_state(screen), "container": option},
                )
            )

    dialog = observation.get("dialog") if isinstance(observation.get("dialog"), dict) else {}
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    if screen_kind == "Dialog" and dialog.get("active"):
        answers = dialog.get("answers") if isinstance(dialog.get("answers"), list) else []
        if answers:
            return tasks

    if screen_kind in {"Registration", "Character"}:
        progression = progression_options_payload(observation, action_suggestions, profile, {**arguments, "maxResults": 3})
        option = first_executable_option(progression.get("options", []) if isinstance(progression.get("options"), list) else [], {"tla_change_skill", "tla_change_ability"})
        if option is not None:
            tasks.append(
                task_option(
                    "modal_progression",
                    88,
                    f"handle active {screen_kind} progression controls before closing the modal screen",
                    option.get("tool"),
                    option.get("arguments", {}) if isinstance(option.get("arguments"), dict) else {},
                    {"screen": compact_screen_state(screen), "progression": option, "unspent": progression.get("unspent")},
                )
            )

    if screen_kind == "Character" and int(chosen.get("unspentStatPoints") or 0) > 0:
        return tasks
    if screen_kind == "Registration" and chosen.get("isBodyGenerated") is False:
        return tasks

    terminal_dialog = screen_kind == "Dialog" and bool(dialog.get("active")) and not (dialog.get("answers") if isinstance(dialog.get("answers"), list) else [])
    actions = action_map_from_suggestions(action_suggestions)
    close_action = actions.get("close_screen")
    if isinstance(close_action, dict) and not close_action.get("blockedBy"):
        close_extra: dict[str, Any] = {"screen": compact_screen_state(screen)}
        if terminal_dialog:
            close_extra["dialog"] = {"dialogId": dialog.get("dialogId"), "text": dialog.get("text"), "answers": 0}
        tasks.append(
            task_option(
                "dialog_close" if terminal_dialog else "modal_screen",
                86 if terminal_dialog else 84,
                "close active terminal dialog with no visible answers" if terminal_dialog else f"close or otherwise handle active modal screen {screen_name or '<unknown>'}",
                "tla_close_screen",
                {},
                close_extra,
            )
        )
    else:
        blocked_extra: dict[str, Any] = {"screen": compact_screen_state(screen), "blockedBy": close_action.get("blockedBy", []) if isinstance(close_action, dict) else ["close_screen unavailable"]}
        if terminal_dialog:
            blocked_extra["dialog"] = {"dialogId": dialog.get("dialogId"), "text": dialog.get("text"), "answers": 0}
        tasks.append(
            task_option(
                "dialog_blocked" if terminal_dialog else "modal_screen_blocked",
                60,
                "active terminal dialog has no visible answers but close_screen is not currently executable" if terminal_dialog else f"active modal screen {screen_name or '<unknown>'} needs UI handling but close_screen is not currently executable",
                None,
                {},
                blocked_extra,
            )
        )

    return tasks


def ui_prompt_options_payload(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    ui_prompt = observation.get("uiPrompt") if isinstance(observation.get("uiPrompt"), dict) else {}
    actions = action_map_from_suggestions(action_suggestions)
    ui_action = actions.get("ui_answer") if isinstance(actions.get("ui_answer"), dict) else {}
    options: list[dict[str, Any]] = []
    target_map_proto_id = str(arguments.get("targetMapProtoId") or "").strip()

    if not ui_prompt.get("active"):
        return {"active": False, "options": [], "blocked": [{"reason": "observation.uiPrompt.active=false"}]}

    for candidate in action_candidate_entries(ui_action):
        candidate_args = candidate.get("arguments") if isinstance(candidate.get("arguments"), dict) else {}
        role = str(candidate.get("role") or "").strip().lower()
        dangerous = bool(candidate.get("dangerous"))
        enabled = candidate.get("enabled", True) is not False
        score = ui_prompt_role_score(str(ui_prompt.get("kind") or ""), role, dangerous, enabled)
        if target_map_proto_id and str(candidate_args.get("answerId") or candidate.get("id") or "") == target_map_proto_id:
            score += 32
        blocked_by = list(ui_action.get("blockedBy", []) if isinstance(ui_action.get("blockedBy"), list) else [])
        if not enabled:
            blocked_by.append("uiPrompt.button.enabled=false")
        options.append(
            {
                "kind": "ui_prompt",
                "label": candidate.get("label"),
                "role": role,
                "tool": "tla_ui_answer",
                "arguments": candidate_args,
                "score": score,
                "reason": candidate.get("reason") or "visible semantic GUI prompt button",
                "blockedBy": blocked_by,
                "dangerous": dangerous,
                "preferred": bool(target_map_proto_id and str(candidate_args.get("answerId") or candidate.get("id") or "") == target_map_proto_id),
            }
        )

    options.sort(key=lambda option: int(option.get("score", 0)), reverse=True)
    limit = max(1, min(int(arguments.get("maxResults", 20)), 100))
    return {
        "active": True,
        "kind": ui_prompt.get("kind"),
        "screen": ui_prompt.get("screen"),
        "prompt": {
            key: ui_prompt.get(key)
            for key in ("screen", "kind", "title", "text", "dialogId", "dialogBoxAnswerIndex", "currentMapProtoId")
            if key in ui_prompt
        },
        "options": options[:limit],
        "guidance": "Use tla_ui_answer for semantic GUI prompts; avoid confirming dangerous prompts unless the role/task explicitly needs it.",
    }


def ui_prompt_role_score(kind: str, role: str, dangerous: bool, enabled: bool) -> int:
    if not enabled:
        return 5
    if dangerous:
        return 12
    if role in {"cancel"}:
        return 68 if kind == "confirm" else 48
    if role in {"no"}:
        return 54
    if role in {"yes", "confirm", "answer", "select"}:
        return 72
    return 60


def modal_action_hint(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    option = first_executable_option(
        modal_task_options(observation, action_suggestions, profile, arguments),
        {"tla_ui_answer", "tla_close_screen", "tla_operate_container", "tla_change_skill", "tla_change_ability"},
    )
    if option is None:
        return {}
    return {
        "kind": option.get("kind"),
        "tool": option.get("tool"),
        "arguments": dict(option.get("arguments", {})) if isinstance(option.get("arguments"), dict) else {},
        "reason": option.get("reason"),
    }


def compact_screen_state(screen: dict[str, Any]) -> dict[str, Any]:
    return {
        key: screen.get(key)
        for key in ("active", "modalActive", "activeModal", "activeScreens", "modalScreens")
        if key in screen
    }


def progression_options_payload(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    actions = action_map_from_suggestions(action_suggestions)
    favored_skills = progression_favored_skills(observation)
    include_refunds = bool(arguments.get("includeRefundOptions", False))
    options: list[dict[str, Any]] = []
    allow_unsafe_progression = bool(arguments.get("allowUnsafeProgression", False))
    threats = [] if allow_unsafe_progression else visible_progression_threats(observation)
    if threats:
        return {
            "unspent": {
                "stats": chosen.get("unspentStatPoints"),
                "skills": chosen.get("unspentSkillPoints"),
                "abilities": chosen.get("unspentAbilityPoints"),
            },
            "favoredSkills": sorted(favored_skills),
            "options": [],
            "blocked": [{"reason": "visible hostile-looking critters are nearby; resolve survival/combat before spending progression", "threats": threats[:5]}],
            "guidance": "Progression is intentionally blocked while visible hostile-looking critters or combatants are nearby.",
        }

    skill_action = actions.get("change_skill") if isinstance(actions.get("change_skill"), dict) else {}
    for candidate in action_candidate_entries(skill_action):
        candidate_args = candidate.get("arguments") if isinstance(candidate.get("arguments"), dict) else {}
        skill = str(candidate_args.get("skill") or candidate.get("id") or "")
        increasing = bool(candidate_args.get("increase", True))
        if not increasing and not include_refunds:
            continue
        score = 72 if increasing else 34
        reasons = [str(candidate.get("reason") or "visible skill progression candidate")]
        if skill in favored_skills:
            score += 12
            reasons.append("skill matches current equipment or survival context")
        elif skill in COMBAT_SKILL_NAMES and not favored_skills:
            score += 6
            reasons.append("combat skill is broadly useful for a fresh hostile map")
        options.append(
            {
                "kind": "change_skill",
                "label": candidate.get("label") or skill,
                "skill": skill,
                "tool": "tla_change_skill",
                "arguments": candidate_args,
                "score": max(0, min(score, 100)),
                "reason": "; ".join(reasons),
                "blockedBy": skill_action.get("blockedBy", []),
            }
        )

    ability_action = actions.get("change_ability") if isinstance(actions.get("change_ability"), dict) else {}
    for candidate in action_candidate_entries(ability_action):
        candidate_args = candidate.get("arguments") if isinstance(candidate.get("arguments"), dict) else {}
        proto_id = str(candidate_args.get("protoId") or candidate.get("protoId") or candidate.get("id") or "")
        adding = bool(candidate_args.get("add", True))
        if not adding and not include_refunds:
            continue
        ability = progression_ability_entry(chosen, proto_id)
        try:
            skill = skill_property_name(ability.get("skill"))
        except ValueError:
            skill = str(ability.get("skill") or "")
        score = 70 if adding else 32
        reasons = [str(candidate.get("reason") or "visible ability progression candidate")]
        if skill in favored_skills:
            score += 10
            reasons.append("ability belongs to a currently relevant skill")
        options.append(
            {
                "kind": "change_ability",
                "label": candidate.get("label") or proto_id,
                "protoId": proto_id,
                "skill": skill,
                "tool": "tla_change_ability",
                "arguments": candidate_args,
                "score": max(0, min(score, 100)),
                "reason": "; ".join(reasons),
                "blockedBy": ability_action.get("blockedBy", []),
            }
        )

    options.sort(key=lambda option: int(option.get("score", 0)), reverse=True)
    limit = max(1, min(int(arguments.get("maxResults", 20)), 100))
    return {
        "unspent": {
            "stats": chosen.get("unspentStatPoints"),
            "skills": chosen.get("unspentSkillPoints"),
            "abilities": chosen.get("unspentAbilityPoints"),
        },
        "favoredSkills": sorted(favored_skills),
        "options": options[:limit],
        "unsafeProgressionOverride": allow_unsafe_progression,
        "guidance": "Progression options use normal character-generation/progression server calls. Prefer spending points while safe, before extending combat.",
    }


def progression_favored_skills(observation: dict[str, Any]) -> set[str]:
    favored: set[str] = set()
    for item in inventory_items(observation):
        text = f"{item.get('protoId', '')} {item.get('slot', '')}".casefold()
        if item_has_tag(item, "healing"):
            favored.add("SkillMedicine")
        if not item_has_tag(item, "weapon"):
            continue
        if any(marker in text for marker in ("knife", "spear", "melee", "blade", "club")):
            favored.add("SkillMelee")
        elif any(marker in text for marker in ("pistol", "rifle", "shotgun", "smg", "gun", "9mm")):
            favored.add("SkillSmallGuns")
        elif any(marker in text for marker in ("bazooka", "rocket", "biggun", "minigun")):
            favored.add("SkillBigGuns")
        elif any(marker in text for marker in ("grenade", "mine", "explos")):
            favored.add("SkillExplosions")
    return favored


def visible_progression_threats(observation: dict[str, Any]) -> list[dict[str, Any]]:
    if not observation.get("hasMap"):
        return []

    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    chosen_id = chosen.get("id")
    threats: list[dict[str, Any]] = []
    for critter in observation.get("critters", []) if isinstance(observation.get("critters"), list) else []:
        if not isinstance(critter, dict):
            continue
        if critter.get("id") == chosen_id or bool(critter.get("controlledByPlayer")):
            continue
        if critter.get("alive") is False or bool(critter.get("dead")):
            continue
        if critter_support_ally(critter):
            continue
        if not bool(critter.get("inCombat")) and not critter_dangerous(critter):
            continue
        threats.append({key: critter.get(key) for key in ("id", "protoId", "name", "hex", "inCombat", "curHealth", "maxHealth") if key in critter})
    return threats


def progression_ability_entry(chosen: dict[str, Any], proto_id: str) -> dict[str, Any]:
    abilities = chosen.get("abilities") if isinstance(chosen.get("abilities"), dict) else {}
    available = abilities.get("available") if isinstance(abilities.get("available"), list) else []
    for entry in available:
        if isinstance(entry, dict) and str(entry.get("protoId") or "") == proto_id:
            return entry
    return {}


def xp_source_plan_payload(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    progress = xp_progress_payload(chosen, arguments)
    sources: list[dict[str, Any]] = []
    include_blocked = bool(arguments.get("includeBlocked", False))
    allow_combat = bool(arguments.get("allowCombat", True))

    if modal_screen_active(observation):
        modal_option = first_executable_option(
            modal_task_options(observation, action_suggestions, profile, arguments),
            {"tla_ui_answer", "tla_close_screen", "tla_operate_container", "tla_change_skill", "tla_change_ability"},
        )
        blocker = modal_screen_blocker(observation)
        sources.append(
            xp_source_option(
                "modal_gate",
                100,
                blocker or "active modal screen must be handled before XP actions",
                modal_option.get("tool") if modal_option else None,
                modal_option.get("arguments", {}) if modal_option else {},
                estimated_xp=0,
                risk="blocking",
                evidence={"screen": compact_screen_state(observation_screen_state(observation))},
                blocked_by=[] if modal_option else [blocker or "modal action unavailable"],
            )
        )

    sources.extend(xp_progression_sources(observation, action_suggestions, profile, arguments))
    sources.extend(xp_quest_sources(observation, action_suggestions, profile, arguments))
    if allow_combat:
        sources.extend(xp_combat_sources(observation, action_suggestions, profile, arguments))
    else:
        targets = target_options_payload(observation, action_suggestions, profile, {**arguments, "maxResults": 1})
        if targets.get("options"):
            sources.append(
                xp_source_option(
                    "combat_blocked",
                    48,
                    "visible hostile XP source exists, but combat is disabled for this plan",
                    None,
                    {},
                    estimated_xp=None,
                    risk="blocked",
                    evidence={"visibleTargets": len(targets.get("options", [])) if isinstance(targets.get("options"), list) else 0},
                    blocked_by=["allowCombat=false"],
                )
            )
    sources.extend(xp_loot_supply_sources(observation, action_suggestions, profile, arguments))
    sources.extend(xp_global_sources(observation, action_suggestions, profile, arguments))
    sources.extend(xp_transition_sources(observation, action_suggestions, profile, arguments))
    sources.extend(xp_explore_sources(observation, action_suggestions, profile, arguments))

    if not include_blocked:
        sources = [source for source in sources if not source.get("blockedBy")]
    sources.sort(key=lambda source: int(source.get("score", 0)), reverse=True)
    limit = max(1, min(int(arguments.get("maxResults", 20)), 100))
    return {
        "progress": progress,
        "sources": sources[:limit],
        "counts": {"total": len(sources), "returned": min(len(sources), limit)},
        "guidance": "XP source planning ranks client-visible ways to make level progress. Exact rewards remain server/gameplay authority; use recommended checks before risky movement or combat.",
    }


def xp_progression_sources(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> list[dict[str, Any]]:
    progression = progression_options_payload(observation, action_suggestions, profile, {**arguments, "maxResults": 4})
    sources: list[dict[str, Any]] = []
    for option in progression.get("options", []) if isinstance(progression.get("options"), list) else []:
        if not isinstance(option, dict):
            continue
        sources.append(
            xp_source_option(
                "progression_spend",
                min(96, int(option.get("score", 70)) + 18),
                str(option.get("reason") or "spend visible progression points before taking more XP risk"),
                option.get("tool"),
                option.get("arguments", {}) if isinstance(option.get("arguments"), dict) else {},
                estimated_xp=0,
                risk="low",
                evidence={"intent": option.get("kind"), "unspent": progression.get("unspent"), "favoredSkills": progression.get("favoredSkills", [])},
                blocked_by=option.get("blockedBy") if isinstance(option.get("blockedBy"), list) else [],
            )
        )
    for blocked in progression.get("blocked", []) if isinstance(progression.get("blocked"), list) else []:
        if isinstance(blocked, dict):
            sources.append(
                xp_source_option(
                    "progression_blocked",
                    42,
                    str(blocked.get("reason") or "progression spending is blocked"),
                    None,
                    {},
                    estimated_xp=0,
                    risk="blocked",
                    evidence={"unspent": progression.get("unspent"), "blocked": blocked},
                    blocked_by=[str(blocked.get("reason") or "blocked")],
                )
            )
    return sources


def xp_quest_sources(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> list[dict[str, Any]]:
    actions = action_map_from_suggestions(action_suggestions)
    sources: list[dict[str, Any]] = []
    dialog = dialog_options_payload(observation, action_suggestions, profile, {**arguments, "maxResults": 5})
    for option in dialog.get("options", []) if isinstance(dialog.get("options"), list) else []:
        if not isinstance(option, dict) or option.get("intent") not in {"accept", "question", "trade", "healing"}:
            continue
        sources.append(
            xp_source_option(
                "quest_dialog",
                88 if option.get("intent") == "accept" else 80,
                f"active dialog answer may advance or reveal a quest: {option.get('intent')}",
                "tla_dialog_answer",
                option.get("arguments", {}) if isinstance(option.get("arguments"), dict) else {},
                estimated_xp=None,
                risk="low",
                evidence={"dialogId": dialog.get("dialogId"), "text": dialog.get("text"), "answer": option.get("text")},
                blocked_by=option.get("blockedBy") if isinstance(option.get("blockedBy"), list) else [],
            )
        )

    quest_summary = quest_summary_payload(observation, action_suggestions, profile, {**arguments, "maxResults": 6})
    for hint in quest_summary.get("hints", []) if isinstance(quest_summary.get("hints"), list) else []:
        if not isinstance(hint, dict) or hint.get("source") == "dialog":
            continue
        sources.append(
            xp_source_option(
                "active_quest",
                82,
                str(hint.get("text") or "visible quest objective can lead to XP"),
                None,
                {},
                estimated_xp=None,
                risk="unknown",
                evidence={"quest": hint},
                recommended_checks=["tla_quest_summary", "tla_task_memory"],
                blocked_by=["quest objective is advisory; no direct visible command"] if not bool(arguments.get("includeAdvisorySources", True)) else [],
            )
        )

    for entry in interactable_entries(actions, ("talk_to",)):
        sources.append(
            xp_source_option(
                "quest_talker",
                76,
                str(entry.get("reason") or "visible talkable NPC may start or advance a quest"),
                entry.get("tool"),
                entry.get("arguments", {}) if isinstance(entry.get("arguments"), dict) else {},
                estimated_xp=None,
                risk="low",
                evidence={"label": entry.get("label"), "id": entry.get("id"), "protoId": entry.get("protoId"), "hex": entry.get("hex")},
                recommended_checks=["tla_dialog_options", "tla_quest_summary"],
                blocked_by=entry.get("blockedBy") if isinstance(entry.get("blockedBy"), list) else [],
            )
        )
    return sources


def xp_combat_sources(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> list[dict[str, Any]]:
    targets = target_options_payload(observation, action_suggestions, profile, {**arguments, "maxResults": 8})
    sources: list[dict[str, Any]] = []
    for option in targets.get("options", []) if isinstance(targets.get("options"), list) else []:
        if not isinstance(option, dict):
            continue
        critter = option.get("critter") if isinstance(option.get("critter"), dict) else {}
        blocked_by = list(option.get("blockedBy", [])) if isinstance(option.get("blockedBy"), list) else []
        if bool(option.get("protectedNonHostile")):
            blocked_by.append("protected neutral/social target")
        if bool(critter.get("controlledByPlayer")):
            blocked_by.append("player-controlled target")
        score = min(90, 54 + int(option.get("score", 0)) // 2)
        if bool(critter.get("inCombat")):
            score += 6
        risk = "medium"
        if bool(critter.get("inCombat")):
            risk = "active_combat"
        if critter_dangerous(critter):
            risk = "high"
        sources.append(
            xp_source_option(
                "safe_hunt" if not blocked_by else "hunt_blocked",
                min(score, 95),
                str(option.get("reason") or "visible hostile-looking target can grant XP when defeated"),
                option.get("tool"),
                option.get("arguments", {}) if isinstance(option.get("arguments"), dict) else {},
                estimated_xp=None,
                risk=risk,
                evidence={"target": critter, "targetScore": option.get("score"), "label": option.get("label")},
                recommended_checks=option.get("recommendedChecks", ["tla_env_trace", "tla_nav_plan"]),
                blocked_by=blocked_by,
            )
        )
    return sources


def xp_loot_supply_sources(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> list[dict[str, Any]]:
    loot = loot_options_payload(observation, action_suggestions, profile, {**arguments, "maxResults": 10})
    sources: list[dict[str, Any]] = []
    for option in loot.get("options", []) if isinstance(loot.get("options"), list) else []:
        if not isinstance(option, dict):
            continue
        item = option.get("item") if isinstance(option.get("item"), dict) else {}
        if option.get("tool") == "tla_loot_critter":
            supply = True
        else:
            supply = any(item_has_tag(item, tag) for tag in ("weapon", "ammo", "healing", "armor", "container", "food"))
        if not supply:
            continue
        sources.append(
            xp_source_option(
                "xp_supply",
                min(72, int(option.get("score", 45)) + 8),
                str(option.get("reason") or "visible supply can enable safer XP actions"),
                option.get("tool"),
                option.get("arguments", {}) if isinstance(option.get("arguments"), dict) else {},
                estimated_xp=0,
                risk="low",
                evidence={"item": item, "type": option.get("type"), "label": option.get("label")},
                blocked_by=option.get("blockedBy") if isinstance(option.get("blockedBy"), list) else [],
            )
        )
    return sources[:3]


def xp_global_sources(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> list[dict[str, Any]]:
    global_options = global_options_payload(observation, action_suggestions, profile, arguments)
    if not global_options.get("active"):
        return []
    sources: list[dict[str, Any]] = []
    for entry in global_options.get("interests", []) if isinstance(global_options.get("interests"), list) else []:
        if not isinstance(entry, dict):
            continue
        interest_type = str(entry.get("type") or entry.get("typeEnum") or "")
        if interest_type in {"self", "group"}:
            continue
        score = xp_global_interest_score(entry)
        risk = "medium" if interest_type == "encounter" else "low" if interest_type in {"quest_giver", "known_place", "camp"} else "unknown"
        blocked_by = global_interest_blockers(entry) if entry.get("tool") != "tla_global_enter_interest" and not entry.get("pos") else []
        if entry.get("tool") == "tla_global_enter_interest" and interest_type not in INTEREST_TYPE_VALUES:
            blocked_by.append("unsupported global interest type for tla_global_enter_interest")
        sources.append(
            xp_source_option(
                "global_xp_interest",
                score,
                xp_global_interest_reason(entry),
                entry.get("tool"),
                entry.get("arguments", {}) if isinstance(entry.get("arguments"), dict) else {},
                estimated_xp=None,
                risk=risk,
                evidence={"interest": {key: entry.get(key) for key in ("type", "typeEnum", "id", "pos", "distance", "enterable", "inRange") if key in entry}},
                recommended_checks=["tla_travel_plan", "tla_enter_options"] if entry.get("tool") != "tla_global_enter_interest" else ["tla_enter_options"],
                blocked_by=blocked_by,
            )
        )
    return sources[:6]


def xp_global_interest_score(entry: dict[str, Any]) -> int:
    interest_type = str(entry.get("type") or entry.get("typeEnum") or "")
    base = {
        "quest_giver": 92,
        "known_place": 82,
        "camp": 78,
        "encounter": 76,
        "self": 35,
        "group": 35,
        "unknown_place": 18,
    }.get(interest_type, 55)
    if entry.get("tool") == "tla_global_enter_interest":
        base += 8
    distance = int_or_default(entry.get("distance"), 0)
    if distance > 0:
        base -= min(distance // 8, 18)
    return max(5, min(base, 98))


def xp_global_interest_reason(entry: dict[str, Any]) -> str:
    interest_type = str(entry.get("type") or entry.get("typeEnum") or "global interest")
    if interest_type == "quest_giver":
        return "visible quest-giver global interest is likely a strong XP lead"
    if interest_type == "encounter":
        return "visible encounter can provide combat XP if supplies and risk are acceptable"
    if interest_type == "known_place":
        return "known place may contain quests, enemies, or progression opportunities"
    if entry.get("tool") == "tla_global_enter_interest":
        return "enterable global interest may contain XP opportunities"
    return "visible global interest can be travelled toward while looking for XP"


def xp_transition_sources(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> list[dict[str, Any]]:
    if not observation.get("hasMap") or modal_screen_active(observation):
        return []
    transitions = map_transition_options_payload(observation, action_suggestions, profile, arguments)
    sources: list[dict[str, Any]] = []
    for option in transitions.get("options", []) if isinstance(transitions.get("options"), list) else []:
        if not isinstance(option, dict):
            continue
        sources.append(
            xp_source_option(
                "leave_for_xp",
                int(option.get("score", 60)),
                "current local map has no better visible XP source; leave through a visible transition",
                option.get("tool"),
                option.get("arguments", {}) if isinstance(option.get("arguments"), dict) else {},
                estimated_xp=0,
                risk="low",
                evidence={"transition": option},
                recommended_checks=["tla_env_path", "tla_map_transition_options"],
                blocked_by=option.get("blockedBy") if isinstance(option.get("blockedBy"), list) else [],
            )
        )
    return sources[:3]


def xp_explore_sources(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> list[dict[str, Any]]:
    nav = nav_options_payload(observation, action_suggestions, {**arguments, "maxResults": 6}, profile, None)
    sources: list[dict[str, Any]] = []
    for option in nav.get("options", []) if isinstance(nav.get("options"), list) else []:
        if not isinstance(option, dict):
            continue
        tool = option.get("tool") or option.get("suggestedTool")
        if tool not in {"tla_move_to_hex", "tla_global_move_to", "tla_global_enter_interest"}:
            continue
        option_arguments = option.get("arguments", {}) if isinstance(option.get("arguments"), dict) else {}
        if tool == "tla_global_enter_interest" and str(option_arguments.get("interestType") or "") in {"self", "group"}:
            continue
        sources.append(
            xp_source_option(
                "explore_for_xp",
                min(58, int(option.get("adjustedScore", option.get("score", 45)))),
                str(option.get("reason") or "explore visible navigation lead to reveal XP sources"),
                tool,
                option_arguments,
                estimated_xp=0,
                risk="unknown",
                evidence={"targetType": option.get("targetType"), "label": option.get("label"), "hex": option.get("hex"), "pos": option.get("pos")},
                recommended_checks=option.get("recommendedChecks", ["tla_nav_plan"]),
                blocked_by=option.get("blockedBy") if isinstance(option.get("blockedBy"), list) else [],
            )
        )
    return sources[:2]


def task_options_payload(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    tasks: list[dict[str, Any]] = []
    account = observation.get("account") if isinstance(observation.get("account"), dict) else {}
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    actions = action_map_from_suggestions(action_suggestions)

    if account.get("agreementAccepted") is False:
        tasks.append(task_option("account_gate", 100, "accept pending account agreement", "tla_accept_agreement", {}))
    if chosen.get("isBodyGenerated") is False:
        tasks.append(task_option("generation_gate", 98, "confirm generated body", "tla_generate_critter", {}))
    if int(chosen.get("unspentStatPoints") or 0) > 0:
        tasks.append(task_option("generation_gate", 96, "finish starting stat allocation", "tla_finish_generation", {}))

    dialog = dialog_options_payload(observation, action_suggestions, profile, arguments)
    if dialog.get("active"):
        dialog_options = dialog.get("options") if isinstance(dialog.get("options"), list) else []
        dialog_summary = {"dialogId": dialog.get("dialogId"), "text": dialog.get("text"), "answers": dialog.get("counts", {}).get("answers") if isinstance(dialog.get("counts"), dict) else None}
        if dialog_options:
            executable_dialog = first_executable_option(dialog_options, {"tla_dialog_answer"})
            if executable_dialog is not None:
                tasks.append(task_option("dialog", int(executable_dialog.get("score", 80)), f"answer active dialog as {executable_dialog.get('intent')}", "tla_dialog_answer", executable_dialog.get("arguments", {}), {"dialog": dialog_summary}))
            else:
                top = dialog_options[0]
                tasks.append(task_option("dialog_blocked", min(int(top.get("score", 80)), 75), "active dialog has no currently executable answer action", None, {}, {"dialog": dialog_summary, "blockedBy": top.get("blockedBy", ["dialog answer unavailable"])}))
        else:
            close_action = actions.get("close_screen") if isinstance(actions.get("close_screen"), dict) else {}
            close_blocked_by = close_action.get("blockedBy") if isinstance(close_action.get("blockedBy"), list) else []
            if close_action and not close_blocked_by:
                tasks.append(task_option("dialog_close", 82, "close active terminal dialog with no visible answers", "tla_close_screen", {}, {"dialog": dialog_summary}))
            else:
                blocked_by = list(close_blocked_by)
                if not blocked_by:
                    blocked_by = ["dialog has no visible answers", "close_screen unavailable"]
                tasks.append(task_option("dialog_blocked", 65, "active dialog has no visible answers and cannot be closed yet", None, {}, {"dialog": dialog_summary, "blockedBy": blocked_by}))

    tasks.extend(modal_task_options(observation, action_suggestions, profile, arguments))

    for quest_task in quest_task_options(observation, arguments):
        tasks.append(quest_task)

    progression = progression_options_payload(observation, action_suggestions, profile, arguments)
    for option in progression.get("options", [])[:2] if isinstance(progression.get("options"), list) else []:
        if isinstance(option, dict):
            tasks.append(
                task_option(
                    "progression",
                    int(option.get("score", 50)),
                    str(option.get("reason", "")),
                    option.get("tool"),
                    option.get("arguments", {}) if isinstance(option.get("arguments"), dict) else {},
                    {"intent": option.get("kind"), "unspent": progression.get("unspent"), "favoredSkills": progression.get("favoredSkills", [])},
                )
            )

    if xp_planning_requested(arguments):
        xp_plan = xp_source_plan_payload(observation, action_suggestions, profile, arguments)
        for source in xp_plan.get("sources", [])[:2] if isinstance(xp_plan.get("sources"), list) else []:
            if not isinstance(source, dict) or not source.get("tool"):
                continue
            tasks.append(
                task_option(
                    "xp_source",
                    int(source.get("score", 50)),
                    str(source.get("reason") or "visible XP source"),
                    source.get("tool"),
                    source.get("arguments", {}) if isinstance(source.get("arguments"), dict) else {},
                    {
                        "xpSource": {
                            key: source.get(key)
                            for key in ("kind", "risk", "estimatedXp", "recommendedChecks")
                            if key in source
                        },
                        "progress": xp_plan.get("progress"),
                    },
                )
            )

    if not modal_screen_active(observation):
        combat = combat_options_payload(observation, action_suggestions, profile, arguments)
        for priority in combat.get("priorities", [])[:2] if isinstance(combat.get("priorities"), list) else []:
            if isinstance(priority, dict):
                tasks.append(
                    task_option(
                        "combat",
                        int(priority.get("score", 50)),
                        str(priority.get("reason", "")),
                        priority.get("tool"),
                        priority.get("arguments", {}) if isinstance(priority.get("arguments"), dict) else {},
                        {"intent": priority.get("intent")},
                    )
                )

    global_options = global_options_payload(observation, action_suggestions, profile, arguments)
    if global_options.get("active"):
        travel = travel_plan_payload(observation, action_suggestions, profile, arguments)
        plan = travel.get("plan") if isinstance(travel.get("plan"), dict) else {}
        if plan:
            tasks.append(task_option("global_travel", 70, str(plan.get("reason", "global travel")), plan.get("tool"), plan.get("arguments", {}), {"plan": plan}))
    else:
        transitions = map_transition_options_payload(observation, action_suggestions, profile, arguments)
        option = first_executable_option(transitions.get("options", []) if isinstance(transitions.get("options"), list) else [], {"tla_move_to_hex"})
        if option is not None:
            tasks.append(
                task_option(
                    "map_transition",
                    int(option.get("score", 62)),
                    str(option.get("reason", "visible local map exit")),
                    option.get("tool"),
                    option.get("arguments", {}) if isinstance(option.get("arguments"), dict) else {},
                    {"transition": option},
                )
            )

    for command_type, score in (("talk_to", 64), ("pick_item", 55), ("loot_critter", 50), ("request_roster", 35)):
        action = actions.get(command_type)
        if isinstance(action, dict) and isinstance(action.get("example"), dict):
            entries = interactable_entries(actions, (command_type,))
            if command_type == "pick_item" and entries:
                for index, entry in enumerate(entries[:4]):
                    tasks.append(
                        task_option(
                            command_type,
                            score - index,
                            str(entry.get("reason", action.get("description", command_type))),
                            entry.get("tool"),
                            entry.get("arguments", {}),
                            {"target": compact_task_target(entry)},
                        )
                    )
            else:
                target = task_target_for_example(entries, action.get("example", {}))
                extra = {"target": compact_task_target(target)} if target is not None else None
                tasks.append(task_option(command_type, score, str(action.get("description", command_type)), action.get("tool"), action.get("example", {}), extra))

    tasks.sort(key=lambda task: int(task.get("score", 0)), reverse=True)
    limit = max(1, min(int(arguments.get("maxResults", 20)), 100))
    return {
        "options": tasks[:limit],
        "counts": {"total": len(tasks), "returned": min(len(tasks), limit)},
        "guidance": "Task options are a compact priority list from visible gates, dialogs, combat, global travel, and current action suggestions. They do not execute commands.",
    }


def xp_planning_requested(arguments: dict[str, Any]) -> bool:
    if bool(arguments.get("planXpSources", False)) or "targetLevel" in arguments:
        return True
    return goal_has_xp_marker(str(arguments.get("goal") or "").casefold())


def quest_task_options(observation: dict[str, Any], arguments: dict[str, Any]) -> list[dict[str, Any]]:
    limit = max(1, min(int(arguments.get("maxResults", 20)), 100))
    surfaces = visible_quest_surfaces(observation, limit)
    tasks: list[dict[str, Any]] = []
    for hint in quest_hints_from_surfaces(surfaces, limit):
        text = str(hint.get("text") or "visible quest/PDA entry")
        reason = f"visible quest/PDA objective: {text}"
        tasks.append(task_option("quest", 68, reason, None, {}, {"quest": hint}))
    return tasks


def interactable_entries(actions: dict[str, dict[str, Any]], command_types: tuple[str, ...]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for command_type in command_types:
        action = actions.get(command_type)
        if not isinstance(action, dict):
            continue
        for candidate in action.get("candidates", []) if isinstance(action.get("candidates"), list) else []:
            if not isinstance(candidate, dict):
                continue
            entries.append(
                {
                    "type": command_type,
                    "tool": action.get("tool"),
                    "label": candidate.get("label"),
                    "id": candidate.get("id"),
                    "protoId": candidate.get("protoId"),
                    "hex": candidate.get("hex"),
                    "pos": candidate.get("pos"),
                    "reason": candidate.get("reason", action.get("description", "")),
                    "arguments": candidate.get("arguments", {}),
                    "blockedBy": action.get("blockedBy", []),
                    **{
                        key: candidate.get(key)
                        for key in (
                            "canUse",
                            "canPickUp",
                            "hasDoor",
                            "hasContainer",
                            "hasLocker",
                            "hasMapExit",
                            "hasMapEntry",
                            "opened",
                            "canOpen",
                            "isGag",
                            "noHighlight",
                            "hasStaticScript",
                            "isStatic",
                            "lockerLocked",
                            "lockerNoOpen",
                        )
                        if key in candidate
                    },
                }
            )
    return entries


def task_target_for_example(entries: list[dict[str, Any]], example: dict[str, Any]) -> dict[str, Any] | None:
    for entry in entries:
        arguments = entry.get("arguments") if isinstance(entry.get("arguments"), dict) else {}
        if arguments == example:
            return entry
    if entries:
        return entries[0]
    return None


def compact_task_target(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        key: entry.get(key)
        for key in (
            "type",
            "id",
            "protoId",
            "label",
            "hex",
            "static",
            "canUse",
            "canPickUp",
            "hasDoor",
            "hasContainer",
            "hasLocker",
            "hasMapExit",
            "hasMapEntry",
            "opened",
            "canOpen",
            "isGag",
            "noHighlight",
            "hasStaticScript",
            "isStatic",
            "lockerLocked",
            "lockerNoOpen",
        )
        if key in entry
    }


def interest_points_payload(observation: dict[str, Any], action_suggestions: dict[str, Any], arguments: dict[str, Any]) -> list[dict[str, Any]]:
    points: list[dict[str, Any]] = []
    actions = action_map_from_suggestions(action_suggestions)
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    account = observation.get("account") if isinstance(observation.get("account"), dict) else {}
    dialog = observation.get("dialog") if isinstance(observation.get("dialog"), dict) else {}

    if account.get("agreementAccepted") is False:
        points.append(interest_point("account_gate", "accept agreement", 100, "fresh account agreement is pending", "tla_accept_agreement", {}))
    if chosen.get("isBodyGenerated") is False:
        points.append(interest_point("generation_gate", "generate critter", 100, "chosen body generation is pending", "tla_generate_critter", {}))
    if int(chosen.get("unspentStatPoints") or 0) > 0:
        points.append(interest_point("generation_gate", "finish generation", 98, "unspent stat points block map progression", "tla_finish_generation", {}))
    if dialog.get("active"):
        points.append(interest_point("dialog", "active dialog", 95, "dialog is waiting for an answer", "tla_dialog_answer", action_example_from_actions(actions, "dialog_answer")))

    for entry in interactable_entries(actions, ("attack_entity", "talk_to", "loot_critter", "pick_item", "global_enter_interest", "use_item")):
        score = {
            "attack_entity": 88,
            "talk_to": 72,
            "loot_critter": 60,
            "pick_item": 52,
            "global_enter_interest": 78,
            "use_item": 48,
        }.get(str(entry.get("type")), 40)
        points.append(
            interest_point(
                str(entry.get("type")),
                str(entry.get("label") or entry.get("id") or entry.get("type")),
                score,
                str(entry.get("reason", "")),
                entry.get("tool"),
                entry.get("arguments", {}),
                entry.get("hex"),
                entry.get("pos"),
            )
        )

    points.sort(key=lambda item: int(item.get("score", 0)), reverse=True)
    limit = max(1, min(int(arguments.get("maxResults", 20)), 100))
    return points[:limit]


def interest_point(kind: str, label: str, score: int, reason: str, tool: Any, tool_arguments: dict[str, Any], hex_value: Any = None, pos: Any = None) -> dict[str, Any]:
    result: dict[str, Any] = {"kind": kind, "label": label, "score": score, "reason": reason, "suggestedTool": tool, "arguments": tool_arguments}
    if hex_value is not None:
        result["hex"] = hex_value
    if pos is not None:
        result["pos"] = pos
    return result


def action_example_from_actions(actions: dict[str, dict[str, Any]], command_type: str) -> dict[str, Any]:
    action = actions.get(command_type)
    if isinstance(action, dict) and isinstance(action.get("example"), dict):
        return dict(action["example"])
    return {}


def nav_options_payload(
    observation: dict[str, Any],
    action_suggestions: dict[str, Any],
    arguments: dict[str, Any],
    profile: dict[str, Any] | None = None,
    memory: dict[str, Any] | None = None,
) -> dict[str, Any]:
    actions = action_map_from_suggestions(action_suggestions)
    options: list[dict[str, Any]] = []

    for entry in interactable_entries(actions, ("global_enter_interest", "global_move_to")):
        options.append(
            nav_option(
                "global",
                entry,
                "global-map travel/entry option",
                [],
                observation,
                profile,
                memory,
                arguments,
            )
        )

    for entry in interactable_entries(actions, ("move_to_hex",)):
        options.append(
            nav_option(
                "move",
                entry,
                "map movement option; verify reachability first",
                ["tla_env_path", "tla_env_tactical_path"],
                observation,
                profile,
                memory,
                arguments,
            )
        )

    for entry in interactable_entries(actions, ("talk_to", "pick_item", "loot_critter", "attack_entity")):
        checks = ["tla_env_path"]
        if entry.get("type") in {"attack_entity"}:
            checks.append("tla_env_trace")
        options.append(
            nav_option(
                "approach",
                entry,
                f"approach candidate for {entry.get('type')}",
                checks,
                observation,
                profile,
                memory,
                arguments,
            )
        )

    options.sort(
        key=lambda item: (
            int(item.get("adjustedScore", item.get("score", 0))),
            int(item.get("score", 0)),
        ),
        reverse=True,
    )
    limit = max(1, min(int(arguments.get("maxResults", 20)), 100))
    return {
        "options": options[:limit],
        "counts": {"options": min(len(options), limit), "total": len(options)},
        "memoryAware": bool(arguments.get("memoryAware", True)),
        "guidance": (
            "Navigation options are not path-validated here. Use tla_env_path/tla_env_tactical_path or nav planning before issuing movement; "
            "routeMemory is advisory endpoint-local memory only."
        ),
    }


def nav_option(
    kind: str,
    entry: dict[str, Any],
    reason: str,
    recommended_checks: list[str],
    observation: dict[str, Any] | None = None,
    profile: dict[str, Any] | None = None,
    memory: dict[str, Any] | None = None,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    score = base_nav_option_score(kind, entry)
    option: dict[str, Any] = {
        "kind": kind,
        "targetType": entry.get("type"),
        "label": entry.get("label"),
        "suggestedTool": entry.get("tool"),
        "arguments": entry.get("arguments", {}),
        "score": score,
        "adjustedScore": score,
        "reason": reason,
        "recommendedChecks": recommended_checks,
        "blockedBy": entry.get("blockedBy", []),
    }
    if entry.get("id") is not None:
        option["id"] = entry.get("id")
    if entry.get("protoId") is not None:
        option["protoId"] = entry.get("protoId")
    if entry.get("hex") is not None:
        option["hex"] = entry.get("hex")
    if entry.get("pos") is not None:
        option["pos"] = entry.get("pos")
    if (
        observation is not None
        and profile is not None
        and memory is not None
        and bool((arguments or {}).get("memoryAware", True))
    ):
        assessment = nav_route_memory_assessment(
            observation,
            profile,
            memory,
            entry.get("hex"),
            entry.get("type"),
            arguments or {},
            entry.get("id"),
        )
        if assessment.get("available"):
            penalty = int(assessment.get("penalty", 0))
            option["routeMemory"] = assessment
            option["adjustedScore"] = max(0, min(100, score - penalty))
    return option


def base_nav_option_score(kind: str, entry: dict[str, Any]) -> int:
    command_type = str(entry.get("type", ""))
    score = {
        "global_enter_interest": 78,
        "global_move_to": 62,
        "move_to_hex": 48,
        "talk_to": 70,
        "pick_item": 54,
        "loot_critter": 58,
        "attack_entity": 42,
    }.get(command_type, 45)
    if kind == "global":
        score += 4
    if entry.get("blockedBy"):
        score -= 25
    return max(0, min(score, 100))


def nav_route_memory_assessment(
    observation: dict[str, Any],
    profile: dict[str, Any],
    memory: dict[str, Any],
    target_hex: Any,
    target_type: Any,
    arguments: dict[str, Any],
    target_id: Any = None,
) -> dict[str, Any]:
    target_xy = safe_hex_value_xy(target_hex)
    risk_tolerance = str(profile.get("riskTolerance", "normal")).strip().lower() or "normal"
    multiplier = NAV_RISK_TOLERANCE_MULTIPLIER.get(risk_tolerance, 1.0)
    if target_xy is None:
        return {
            "available": False,
            "riskTolerance": risk_tolerance,
            "penalty": 0,
            "recentFailures": 0,
            "rememberedHazards": 0,
            "nearestHazardDistance": None,
            "crowding": 0,
            "reasons": [],
        }

    now = unix_ms()
    failure_window_ms = max(0, int(arguments.get("failureMemoryMs", NAV_ROUTE_FAILURE_RECENCY_MS)))
    hazard_radius = max(0, min(int(arguments.get("hazardRadius", NAV_ROUTE_HAZARD_RADIUS)), 30))
    crowding_radius = max(0, min(int(arguments.get("crowdingRadius", NAV_ROUTE_CROWDING_RADIUS)), 30))
    reasons: list[str] = []
    recent_failures = 0
    remembered_hazards = 0
    nearest_hazard_distance: int | None = None

    for point in remembered_route_points(memory, now, failure_window_ms):
        point_xy = point.get("xy")
        if not isinstance(point_xy, tuple):
            continue
        distance = approximate_hex_distance(target_xy, point_xy)
        if point.get("kind") == "failed_action" and bool(point.get("recent")) and distance <= 1:
            recent_failures += 1
        if distance <= hazard_radius:
            remembered_hazards += 1
            nearest_hazard_distance = distance if nearest_hazard_distance is None else min(nearest_hazard_distance, distance)

    if recent_failures:
        reasons.append(f"{recent_failures} recent failed route/action near target")
    if remembered_hazards:
        reasons.append(f"{remembered_hazards} remembered hazard point(s) within {hazard_radius} hexes")

    crowding = visible_route_crowding(observation, target_xy, crowding_radius, target_id)
    if crowding:
        reasons.append(f"{crowding} visible critter(s) crowd target hex")

    penalty = recent_failures * 24 + remembered_hazards * 8 + crowding * 4
    if nearest_hazard_distance is not None:
        penalty += max(0, hazard_radius + 1 - nearest_hazard_distance) * 6
    adjusted_penalty = int(round(penalty * multiplier))
    if adjusted_penalty and multiplier > 1.0:
        reasons.append(f"{risk_tolerance} risk tolerance raises memory penalty")
    elif adjusted_penalty and multiplier < 1.0:
        reasons.append(f"{risk_tolerance} risk tolerance softens memory penalty")

    return {
        "available": True,
        "targetType": target_type,
        "riskTolerance": risk_tolerance,
        "penalty": max(0, adjusted_penalty),
        "recentFailures": recent_failures,
        "rememberedHazards": remembered_hazards,
        "nearestHazardDistance": nearest_hazard_distance,
        "crowding": crowding,
        "reasons": reasons,
    }


def remembered_route_points(memory: dict[str, Any], now: int, failure_window_ms: int) -> list[dict[str, Any]]:
    points: list[dict[str, Any]] = []
    for entry in memory.get("failedActions", []) if isinstance(memory.get("failedActions"), list) else []:
        if not isinstance(entry, dict):
            continue
        xy = memory_entry_hex(entry)
        if xy is None:
            continue
        recent = memory_entry_is_recent(entry, now, failure_window_ms)
        if recent:
            points.append({"xy": xy, "kind": "failed_action", "recent": True})

    for entry in memory.get("facts", []) if isinstance(memory.get("facts"), list) else []:
        if not isinstance(entry, dict) or not memory_entry_marks_hazard(entry):
            continue
        xy = memory_entry_hex(entry)
        if xy is not None:
            points.append({"xy": xy, "kind": "fact", "recent": False})

    places = memory.get("places") if isinstance(memory.get("places"), dict) else {}
    for entry in places.values():
        if not isinstance(entry, dict) or not memory_entry_marks_hazard(entry):
            continue
        xy = memory_entry_hex(entry)
        if xy is not None:
            points.append({"xy": xy, "kind": "place", "recent": False})
    return points


def memory_entry_hex(entry: dict[str, Any]) -> tuple[int, int] | None:
    for source in memory_entry_sources(entry):
        xy = extract_hex_from_mapping(source)
        if xy is not None:
            return xy
    return None


def memory_entry_sources(entry: dict[str, Any]) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = [entry]
    properties = entry.get("properties")
    if isinstance(properties, dict):
        sources.append(properties)
    for source in list(sources):
        for name in ("arguments", "commandArguments", "target", "place"):
            nested = source.get(name)
            if isinstance(nested, dict):
                sources.append(nested)
    return sources


def extract_hex_from_mapping(mapping: dict[str, Any]) -> tuple[int, int] | None:
    for name in ("hex", "targetHex", "hazardHex", "dangerHex", "lastHex"):
        xy = safe_hex_value_xy(mapping.get(name))
        if xy is not None:
            return xy
    if "x" in mapping and "y" in mapping:
        return safe_xy_pair(mapping.get("x"), mapping.get("y"))
    if "toX" in mapping and "toY" in mapping:
        return safe_xy_pair(mapping.get("toX"), mapping.get("toY"))
    return None


def safe_xy_pair(x_value: Any, y_value: Any) -> tuple[int, int] | None:
    try:
        return int(x_value), int(y_value)
    except (TypeError, ValueError):
        return None


def safe_hex_value_xy(hex_value: Any) -> tuple[int, int] | None:
    try:
        return hex_value_xy(hex_value)
    except (TypeError, ValueError):
        return None


def memory_entry_is_recent(entry: dict[str, Any], now: int, window_ms: int) -> bool:
    if window_ms <= 0:
        return True
    timestamp = entry.get("time", entry.get("updatedAt"))
    if not isinstance(timestamp, int):
        return True
    return now - timestamp <= window_ms


def memory_entry_marks_hazard(entry: dict[str, Any]) -> bool:
    properties = entry.get("properties") if isinstance(entry.get("properties"), dict) else entry
    for name in ("hazard", "danger", "avoid", "unsafe", "blocked"):
        if bool(properties.get(name)):
            return True
    tags = normalize_string_list(entry.get("tags"))
    if any(tag.lower() in {"hazard", "danger", "avoid", "unsafe", "опасно", "обходить"} for tag in tags):
        return True
    text = str(entry.get("text") or entry.get("note") or "").lower()
    return any(marker in text for marker in ("danger", "hazard", "avoid", "unsafe", "unreachable", "blocked", "опас", "обход"))


def visible_route_crowding(observation: dict[str, Any], target_xy: tuple[int, int], radius: int, target_id: Any = None) -> int:
    if radius <= 0:
        return 0
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    chosen_id = chosen.get("id")
    count = 0
    for critter in observation.get("critters", []) if isinstance(observation.get("critters"), list) else []:
        if not isinstance(critter, dict):
            continue
        if critter.get("id") == chosen_id or (target_id is not None and critter.get("id") == target_id):
            continue
        if critter.get("alive") is False or critter.get("dead"):
            continue
        xy = safe_hex_value_xy(critter.get("hex"))
        if xy is not None and approximate_hex_distance(target_xy, xy) <= radius:
            count += 1
    return count


def visible_threat_hexes(observation: dict[str, Any]) -> list[tuple[int, int]]:
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    chosen_id = chosen.get("id")
    threat_hexes: list[tuple[int, int]] = []
    for critter in observation.get("critters", []) if isinstance(observation.get("critters"), list) else []:
        if not isinstance(critter, dict) or critter.get("id") == chosen_id:
            continue
        if critter.get("alive") is False or critter.get("dead"):
            continue
        xy = safe_hex_value_xy(critter.get("hex"))
        if xy is not None:
            threat_hexes.append(xy)
    return threat_hexes


def nearest_threat_distance(origin: tuple[int, int] | None, threat_hexes: list[tuple[int, int]]) -> int | None:
    if origin is None or not threat_hexes:
        return None
    return min(approximate_hex_distance(origin, threat) for threat in threat_hexes)


def approximate_hex_distance(left: tuple[int, int], right: tuple[int, int]) -> int:
    # Faithful port of GeometryHelper::GetDistance (HEXAGONAL_GEOMETRY) so client-side proximity
    # heuristics match FOnline offset-hex geometry instead of square-grid Chebyshev (which disagrees
    # on ~4% of nearby adjacency decisions). Authoritative range/path checks still run server-side.
    x1, y1 = left
    x2, y2 = right
    dx = abs(x1 - x2)
    if x1 % 2 == 0:
        rx = (y1 - y2 - dx // 2) if y2 <= y1 else (y2 - y1 - (dx + 1) // 2)
    else:
        rx = (y2 - y1 - dx // 2) if y2 >= y1 else (y1 - y2 - (dx + 1) // 2)
    return dx + (rx if rx > 0 else 0)


def nav_plan_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    selected_bridge, observe_error, observation_payload, observation, action_suggestions = observe_with_action_suggestions(bridge, arguments)
    if observe_error is not None:
        return observe_error
    key = agent_profile_key(selected_bridge)
    profile = agent_profile_for_target(selected_bridge)
    memory = agent_memory_for_key(selected_bridge, key)
    target = resolve_nav_target(observation, action_suggestions, arguments)

    if not target.get("hex"):
        raise ValueError("tla_nav_plan needs a map hex target; pass toX/toY, x/y, targetId/itemId, or choose a visible map candidate")

    query_type = "path" if bool(arguments.get("simplePath")) else "tactical_path"
    query_args = nav_query_arguments(arguments, target, query_type)
    query_response = environment_query(selected_bridge, query_type, query_args)
    if "error" in query_response:
        return query_response

    query_payload = query_response.get("result", {}) if isinstance(query_response.get("result"), dict) else {}
    route = query_payload.get("result") if isinstance(query_payload.get("result"), dict) else {}
    route = route_with_query(route, query_type)
    target_route = route
    target_query_payload = query_payload
    approach_payload: dict[str, Any] | None = None
    if nav_target_needs_standing_hex(target, route):
        approach_payload = find_approach_standing_route(selected_bridge, arguments, target, observation)
        if isinstance(approach_payload, dict) and "error" in approach_payload:
            return approach_payload
        if approach_payload is not None and approach_payload.get("usedStandingHex") and isinstance(approach_payload.get("standingHex"), dict):
            standing_hex = approach_payload.get("standingHex")
            route = approach_payload.get("route") if isinstance(approach_payload.get("route"), dict) else route
            query_payload = approach_payload.get("routeQuery") if isinstance(approach_payload.get("routeQuery"), dict) else query_payload
            target = {
                **target,
                "movementHex": standing_hex,
                "approachTargetHex": target.get("hex"),
                "defaultCut": 0,
            }
    route_memory = nav_route_memory_assessment(
        observation,
        profile,
        memory,
        target.get("hex"),
        target.get("targetType"),
        arguments,
        target.get("id"),
    )
    trace_payload: dict[str, Any] | None = None
    if bool(arguments.get("includeTrace")) or target.get("targetType") in {"attack_entity", "attack_hex"}:
        trace_response = environment_query(selected_bridge, "trace", nav_query_arguments(arguments, target, "trace"))
        if "error" in trace_response:
            return trace_response
        trace_payload = trace_response.get("result", {}) if isinstance(trace_response.get("result"), dict) else {}

    result = {
        "endpoint": getattr(selected_bridge, "endpoint", None),
        "observationSeq": observation_payload.get("observationSeq") if isinstance(observation_payload, dict) else observation.get("seq"),
        "target": target,
        "plan": {
            "query": query_type,
            "reachable": route_reachable(route),
            "score": route_score(route),
            "adjustedScore": adjusted_route_score(route, route_memory),
            "routeMemory": route_memory,
            "movement": nav_movement_step(target) if route_reachable(route) else {},
            "followUp": nav_follow_up(target) if route_reachable(route) else None,
            "route": route,
            "routeQuery": query_payload,
            "targetRoute": target_route,
            "targetRouteQuery": target_query_payload,
            "approach": approach_payload,
            "trace": trace_payload.get("result") if isinstance(trace_payload, dict) and isinstance(trace_payload.get("result"), dict) else None,
            "traceQuery": trace_payload,
            "guidance": "Execute movement through tla_move_to_hex only after reviewing route/trace; then use followUp if still valid in a fresh observation.",
        },
    }
    return {"jsonrpc": "2.0", "id": None, "result": result}


def find_nearest_reachable_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    selected_bridge, observe_error, observation_payload, observation, action_suggestions = observe_with_action_suggestions(bridge, arguments)
    if observe_error is not None:
        return observe_error
    key = agent_profile_key(selected_bridge)
    profile = agent_profile_for_target(selected_bridge)
    memory = agent_memory_for_key(selected_bridge, key)
    candidates = query_ordered_nav_candidates(filtered_nav_candidates(observation, action_suggestions, arguments), observation, arguments)
    max_candidates = max(1, min(int(arguments.get("maxCandidates", 8)), 50))
    checks: list[dict[str, Any]] = []

    for candidate in candidates[:max_candidates]:
        query_args = nav_query_arguments(arguments, candidate, "path")
        query_args["includeDirections"] = False
        response = environment_query(selected_bridge, "path", query_args)
        if "error" in response:
            return response
        payload = response.get("result", {}) if isinstance(response.get("result"), dict) else {}
        route = payload.get("result") if isinstance(payload.get("result"), dict) else {}
        route = route_with_query(route, "path")
        assessment_target = candidate
        assessment_route = route
        assessment_payload = payload
        approach_payload: dict[str, Any] | None = None
        if nav_target_needs_standing_hex(candidate, route):
            approach_payload = find_approach_standing_route(selected_bridge, arguments, candidate, observation)
            if isinstance(approach_payload, dict) and "error" in approach_payload:
                return approach_payload
            if approach_payload is not None and approach_payload.get("usedStandingHex") and isinstance(approach_payload.get("standingHex"), dict):
                assessment_target = {
                    **candidate,
                    "movementHex": approach_payload.get("standingHex"),
                    "approachTargetHex": candidate.get("hex"),
                    "defaultCut": 0,
                }
                assessment_route = approach_payload.get("route") if isinstance(approach_payload.get("route"), dict) else route
                assessment_payload = approach_payload.get("routeQuery") if isinstance(approach_payload.get("routeQuery"), dict) else payload

        assessment = nav_candidate_assessment(assessment_target, assessment_route, assessment_payload, observation, profile, memory, arguments)
        if approach_payload is not None:
            assessment["targetRoute"] = route
            assessment["targetQuery"] = payload
            assessment["approach"] = approach_payload
        checks.append(assessment)

    reachable = [entry for entry in checks if entry.get("reachable")]
    reachable.sort(
        key=lambda entry: (
            int(entry.get("adjustedScore", entry.get("pathLength", 1_000_000))),
            int(entry.get("pathLength", 1_000_000)),
            int(entry.get("directDistance", 1_000_000)),
        )
    )
    return {
        "jsonrpc": "2.0",
        "id": None,
        "result": {
            "endpoint": getattr(selected_bridge, "endpoint", None),
            "observationSeq": observation_payload.get("observationSeq") if isinstance(observation_payload, dict) else observation.get("seq"),
            "best": reachable[0] if reachable else None,
            "candidates": checks,
            "checked": len(checks),
            "totalCandidates": len(candidates),
            "guidance": "Use best.movement for approach movement, then refresh observation before executing best.followUp.",
        },
    }


def find_safe_step_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    selected_bridge, observe_error, observation_payload, observation, action_suggestions = observe_with_action_suggestions(bridge, arguments)
    if observe_error is not None:
        return observe_error
    key = agent_profile_key(selected_bridge)
    profile = agent_profile_for_target(selected_bridge)
    memory = agent_memory_for_key(selected_bridge, key)
    candidates = local_safe_step_candidates(observation, arguments)
    if bool(arguments.get("useVisibleLandmarks", False)) or not candidates:
        safe_filter_args = {
            key: value
            for key, value in arguments.items()
            if key not in {"targetType", "targetTypes", "types", "id", "targetId", "itemId"}
        }
        safe_filter_args["targetTypes"] = ["move_to_hex"]
        candidates = query_ordered_nav_candidates(
            [entry for entry in filtered_nav_candidates(observation, action_suggestions, safe_filter_args) if entry.get("hex")],
            observation,
            arguments,
        )
    max_candidates = max(1, min(int(arguments.get("maxCandidates", 6)), 30))
    checks: list[dict[str, Any]] = []

    threat_hexes = visible_threat_hexes(observation)
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    current_threat_distance = nearest_threat_distance(safe_hex_value_xy(chosen.get("hex")), threat_hexes)

    for candidate in candidates[:max_candidates]:
        # Each candidate is a discrete local step hex, so evaluate it by the direct path + threat
        # risk to it; a per-candidate detour search (searchRadius>0) adds ~8 extra A* pathfinds per
        # candidate (~8ms each on a large map), which made one safe-step scan overrun the synchronous
        # AiControl loop in combat. The detour route to a one-step move is irrelevant here.
        candidate_query = nav_query_arguments(arguments, candidate, "tactical_path")
        candidate_query["searchRadius"] = 0
        response = environment_query(selected_bridge, "tactical_path", candidate_query)
        if "error" in response:
            return response
        payload = response.get("result", {}) if isinstance(response.get("result"), dict) else {}
        route = payload.get("result") if isinstance(payload.get("result"), dict) else {}
        route = route_with_query(route, "tactical_path")
        assessment = nav_candidate_assessment(candidate, route, payload, observation, profile, memory, arguments)
        if candidate.get("source") == "local_safe_step":
            apply_safe_step_threat_adjustment(assessment, candidate, current_threat_distance, threat_hexes)
        checks.append(assessment)

    reachable = [entry for entry in checks if entry.get("reachable")]
    reachable.sort(
        key=lambda entry: (
            int(entry.get("adjustedScore", entry.get("score", 1_000_000))),
            int(entry.get("score", 1_000_000)),
            int(entry.get("pathLength", 1_000_000)),
        )
    )
    return {
        "jsonrpc": "2.0",
        "id": None,
        "result": {
            "endpoint": getattr(selected_bridge, "endpoint", None),
            "observationSeq": observation_payload.get("observationSeq") if isinstance(observation_payload, dict) else observation.get("seq"),
            "best": reachable[0] if reachable else None,
            "candidates": checks,
            "checked": len(checks),
            "totalCandidates": len(candidates),
            "guidance": "Safe-step candidates are local reachable hexes by default and are scored with tla_env_tactical_path; pass useVisibleLandmarks for the legacy landmark mode.",
        },
    }


def local_safe_step_candidates(observation: dict[str, Any], arguments: dict[str, Any]) -> list[dict[str, Any]]:
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    origin_xy = safe_hex_value_xy(chosen.get("hex"))
    if origin_xy is None:
        return []
    radius = max(1, min(int(arguments.get("localRadius", arguments.get("radius", 3))), 8))
    threat_hexes = visible_threat_hexes(observation)
    candidates: list[dict[str, Any]] = []
    for xy in nearby_hex_candidates(origin_xy, origin_xy, radius):
        candidates.append(
            {
                "targetType": "move_to_hex",
                "label": f"nearby hex {xy[0]}:{xy[1]}",
                "hex": {"x": xy[0], "y": xy[1]},
                "arguments": {"x": xy[0], "y": xy[1]},
                "defaultCut": 0,
                "source": "local_safe_step",
            }
        )
    if threat_hexes:
        candidates.sort(
            key=lambda candidate: (
                -(nearest_threat_distance(safe_hex_value_xy(candidate.get("hex")), threat_hexes) or -1),
                approximate_hex_distance(origin_xy, safe_hex_value_xy(candidate.get("hex")) or origin_xy),
            )
        )
    return candidates


def apply_safe_step_threat_adjustment(assessment: dict[str, Any], candidate: dict[str, Any], current_threat_distance: int | None, threat_hexes: list[tuple[int, int]]) -> None:
    if current_threat_distance is None or not threat_hexes:
        return
    target_threat_distance = nearest_threat_distance(safe_hex_value_xy(candidate.get("hex")), threat_hexes)
    if target_threat_distance is None:
        return
    distance_delta = target_threat_distance - current_threat_distance
    base_score = assessment.get("adjustedScore")
    if not isinstance(base_score, int):
        base_score = assessment.get("score")
    if isinstance(base_score, int):
        assessment["adjustedScore"] = base_score - max(0, distance_delta) * 20 + max(0, -distance_delta) * 25
    assessment["threatDistance"] = target_threat_distance
    assessment["currentThreatDistance"] = current_threat_distance
    assessment["distanceDelta"] = distance_delta


def find_cover_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    selected_bridge = target_bridge(bridge, arguments)
    response = environment_query(selected_bridge, "obstacles", dict(arguments))
    if "error" in response:
        return response

    payload = response.get("result", {}) if isinstance(response.get("result"), dict) else {}
    result = payload.get("result") if isinstance(payload.get("result"), dict) else {}
    anchors = cover_anchor_entries(result)
    limit = max(1, min(int(arguments.get("maxResults", 20)), 100))
    return {
        "jsonrpc": "2.0",
        "id": None,
        "result": {
            "endpoint": getattr(selected_bridge, "endpoint", None),
            "center": result.get("center"),
            "radius": result.get("radius"),
            "coverAnchors": anchors[:limit],
            "totalAnchors": len(anchors),
            "obstacles": result,
            "query": payload,
            "guidance": "Cover anchors are visible blockers, not guaranteed standing hexes. Use tla_nav_plan or tla_env_path to validate a movement position near an anchor.",
        },
    }


def find_vantage_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    selected_bridge, observe_error, observation_payload, observation, action_suggestions = observe_with_action_suggestions(bridge, arguments)
    if observe_error is not None:
        return observe_error
    candidates = filtered_vantage_targets(observation, action_suggestions, arguments)
    max_candidates = max(1, min(int(arguments.get("maxCandidates", 8)), 50))
    checks: list[dict[str, Any]] = []

    for candidate in candidates[:max_candidates]:
        response = environment_query(selected_bridge, "trace", nav_query_arguments(arguments, candidate, "trace"))
        if "error" in response:
            return response
        payload = response.get("result", {}) if isinstance(response.get("result"), dict) else {}
        trace = payload.get("result") if isinstance(payload.get("result"), dict) else {}
        checks.append(vantage_assessment(candidate, trace, payload))

    checks.sort(key=lambda entry: (not bool(entry.get("lineOfSight")), int(entry.get("directDistance", 1_000_000))))
    return {
        "jsonrpc": "2.0",
        "id": None,
        "result": {
            "endpoint": getattr(selected_bridge, "endpoint", None),
            "observationSeq": observation_payload.get("observationSeq") if isinstance(observation_payload, dict) else observation.get("seq"),
            "best": checks[0] if checks else None,
            "vantage": checks,
            "checked": len(checks),
            "totalCandidates": len(candidates),
            "guidance": "This checks current or explicit fromX/fromY line quality to visible targets. Use cover/nav tools to move before re-checking a new vantage.",
        },
    }


def explore_options_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    selected_bridge, observe_error, observation_payload, observation, action_suggestions = observe_with_action_suggestions(bridge, arguments)
    if observe_error is not None:
        return observe_error
    key = agent_profile_key(selected_bridge)
    profile = agent_profile_for_target(selected_bridge)
    memory = agent_memory_for_key(selected_bridge, key)
    interests = interest_points_payload(observation, action_suggestions, arguments)
    nav = nav_options_payload(observation, action_suggestions, arguments, profile, memory)
    options: list[dict[str, Any]] = []

    for point in interests:
        if point.get("hex") or point.get("pos") or point.get("suggestedTool") in {
            "tla_global_move_to",
            "tla_global_enter_interest",
            "tla_talk_to",
            "tla_pick_item",
        }:
            options.append(
                {
                    "kind": point.get("kind"),
                    "label": point.get("label"),
                    "score": point.get("score"),
                    "reason": point.get("reason"),
                    "suggestedTool": point.get("suggestedTool"),
                    "arguments": point.get("arguments", {}),
                    "hex": point.get("hex"),
                    "pos": point.get("pos"),
                }
            )

    if bool(arguments.get("validatePaths")):
        validated: list[dict[str, Any]] = []
        for candidate in filtered_nav_candidates(observation, action_suggestions, arguments)[
            : max(1, min(int(arguments.get("maxCandidates", 6)), 30))
        ]:
            response = environment_query(selected_bridge, "path", nav_query_arguments(arguments, candidate, "path"))
            if "error" in response:
                return response
            payload = response.get("result", {}) if isinstance(response.get("result"), dict) else {}
            route = payload.get("result") if isinstance(payload.get("result"), dict) else {}
            route = route_with_query(route, "path")
            validated.append(nav_candidate_assessment(candidate, route, payload, observation, profile, memory, arguments))
        options.extend({"kind": "validated_nav", **entry} for entry in validated)

    limit = max(1, min(int(arguments.get("maxResults", 20)), 100))
    options.sort(
        key=lambda item: int(item.get("adjustedScore", item.get("score", 0)))
        if isinstance(item.get("adjustedScore", item.get("score", 0)), int)
        else 0,
        reverse=True,
    )
    return {
        "jsonrpc": "2.0",
        "id": None,
        "result": {
            "endpoint": getattr(selected_bridge, "endpoint", None),
            "observationSeq": observation_payload.get("observationSeq") if isinstance(observation_payload, dict) else observation.get("seq"),
            "area": area_summary_payload(observation),
            "options": options[:limit],
            "nav": nav,
            "guidance": "Explore options are client-visible leads. Set validatePaths=true for lightweight reachability checks before moving.",
        },
    }


def observe_with_action_suggestions(bridge: Any, arguments: dict[str, Any]) -> tuple[TargetBridge, dict[str, Any] | None, dict[str, Any], dict[str, Any], dict[str, Any]]:
    selected_bridge, observe_error, observation_payload, observation = observe_target_payload(bridge, arguments)
    if observe_error is not None:
        return selected_bridge, observe_error, {}, {}, {}
    observation = unwrap_observation_payload(observation_payload)
    action_suggestions = available_actions_payload(observation_payload, observation, arguments)
    return selected_bridge, None, observation_payload, observation, action_suggestions


def resolve_nav_target(observation: dict[str, Any], action_suggestions: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    explicit_hex = explicit_target_hex(arguments)
    if explicit_hex is not None:
        target_type = str(arguments.get("targetType", "hex"))
        return {
            "targetType": target_type,
            "label": str(arguments.get("label", f"hex {explicit_hex['x']}:{explicit_hex['y']}")),
            "hex": explicit_hex,
            "arguments": {"x": explicit_hex["x"], "y": explicit_hex["y"]},
            "defaultCut": default_nav_cut(target_type),
            "source": "explicit",
        }

    candidates = filtered_nav_candidates(observation, action_suggestions, arguments)
    if not candidates:
        raise ValueError("no visible map navigation candidates match the requested target")

    index = int(arguments.get("navOptionIndex", 0))
    if index < 0 or index >= len(candidates):
        raise ValueError(f"navOptionIndex out of range; have {len(candidates)} candidates")
    return candidates[index]


def explicit_target_hex(arguments: dict[str, Any]) -> dict[str, int] | None:
    if "toX" in arguments or "toY" in arguments:
        if "toX" not in arguments or "toY" not in arguments:
            raise ValueError("toX and toY must be passed together")
        return {"x": int(arguments["toX"]), "y": int(arguments["toY"])}
    if "x" in arguments or "y" in arguments:
        if "x" not in arguments or "y" not in arguments:
            raise ValueError("x and y must be passed together")
        return {"x": int(arguments["x"]), "y": int(arguments["y"])}
    return None


def filtered_nav_candidates(observation: dict[str, Any], action_suggestions: dict[str, Any], arguments: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = map_nav_candidate_entries(action_suggestions)
    filters = nav_target_type_filters(arguments)
    target_ids = nav_target_id_filters(arguments)

    result: list[dict[str, Any]] = []
    for candidate in candidates:
        candidate_type = str(candidate.get("targetType", candidate.get("type", "")))
        if filters and candidate_type not in filters:
            continue
        if target_ids and str(candidate.get("id")) not in target_ids:
            continue
        result.append(candidate)

    if not result and target_ids:
        result = visible_entity_nav_candidates(observation, target_ids, filters)
    return result


def query_ordered_nav_candidates(candidates: list[dict[str, Any]], observation: dict[str, Any], arguments: dict[str, Any]) -> list[dict[str, Any]]:
    if bool(arguments.get("preserveCandidateOrder", False)):
        return candidates

    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    origin_xy = safe_hex_value_xy(chosen.get("hex"))
    if origin_xy is None:
        return candidates

    def key(candidate: dict[str, Any]) -> tuple[int, int]:
        candidate_xy = safe_hex_value_xy(candidate.get("hex"))
        distance = approximate_hex_distance(origin_xy, candidate_xy) if candidate_xy is not None else 1_000_000
        return (distance, nav_query_target_priority(candidate))

    return sorted(candidates, key=key)


def nav_query_target_priority(candidate: dict[str, Any]) -> int:
    target_type = str(candidate.get("targetType", candidate.get("type", "")))
    return {
        "move_to_hex": 0,
        "attack_entity": 1,
        "attack_hex": 1,
        "talk_to": 2,
        "pick_item": 3,
        "loot_critter": 3,
    }.get(target_type, 5)


def map_nav_candidate_entries(action_suggestions: dict[str, Any]) -> list[dict[str, Any]]:
    actions = action_map_from_suggestions(action_suggestions)
    entries = interactable_entries(actions, NAV_MAP_TARGET_TYPES)
    result: list[dict[str, Any]] = []
    seen: set[tuple[str, str, int, int]] = set()

    for entry in entries:
        hex_xy = hex_value_xy(entry.get("hex"))
        if hex_xy is None:
            continue
        candidate_type = str(entry.get("type", "hex"))
        candidate = {
            **entry,
            "targetType": candidate_type,
            "hex": {"x": hex_xy[0], "y": hex_xy[1]},
            "defaultCut": default_nav_cut(candidate_type),
            "source": "action_suggestion",
        }
        key = (candidate_type, str(candidate.get("id")), hex_xy[0], hex_xy[1])
        if key in seen:
            continue
        seen.add(key)
        result.append(candidate)
    return result


def visible_entity_nav_candidates(observation: dict[str, Any], target_ids: set[str], filters: set[str]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for critter in observation.get("critters", []) if isinstance(observation.get("critters"), list) else []:
        if not isinstance(critter, dict) or str(critter.get("id")) not in target_ids:
            continue
        if filters and not ({"attack_entity", "talk_to"} & filters):
            continue
        hex_xy = hex_value_xy(critter.get("hex"))
        if hex_xy is None:
            continue
        result.append(
            {
                "targetType": "visible_critter",
                "label": critter.get("name") or critter.get("protoId") or str(critter.get("id")),
                "id": critter.get("id"),
                "protoId": critter.get("protoId"),
                "hex": {"x": hex_xy[0], "y": hex_xy[1]},
                "arguments": {"targetId": critter.get("id")},
                "defaultCut": 1,
                "source": "visible_critter",
            }
        )
    for item in observation.get("mapItems", []) if isinstance(observation.get("mapItems"), list) else []:
        if not isinstance(item, dict) or str(item.get("id")) not in target_ids:
            continue
        if filters and "pick_item" not in filters:
            continue
        hex_xy = hex_value_xy(item.get("hex"))
        if hex_xy is None:
            continue
        result.append(
            {
                "targetType": "visible_item",
                "label": item.get("protoId") or str(item.get("id")),
                "id": item.get("id"),
                "protoId": item.get("protoId"),
                "hex": {"x": hex_xy[0], "y": hex_xy[1]},
                "arguments": {"itemId": item.get("id")},
                "defaultCut": 1,
                "source": "visible_item",
            }
        )
    return result


def filtered_vantage_targets(observation: dict[str, Any], action_suggestions: dict[str, Any], arguments: dict[str, Any]) -> list[dict[str, Any]]:
    explicit_hex = explicit_target_hex(arguments)
    if explicit_hex is not None:
        return [
            {
                "targetType": str(arguments.get("targetType", "hex")),
                "label": str(arguments.get("label", f"hex {explicit_hex['x']}:{explicit_hex['y']}")),
                "hex": explicit_hex,
                "arguments": {"x": explicit_hex["x"], "y": explicit_hex["y"]},
                "defaultCut": 0,
                "source": "explicit",
            }
        ]

    filters = nav_target_type_filters(arguments)
    if not filters:
        filters = {"attack_entity", "attack_hex"}
    candidates = filtered_nav_candidates(observation, action_suggestions, {**arguments, "targetTypes": list(filters)})
    if candidates:
        return candidates

    result: list[dict[str, Any]] = []
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    chosen_id = chosen.get("id")
    target_ids = nav_target_id_filters(arguments)
    for critter in observation.get("critters", []) if isinstance(observation.get("critters"), list) else []:
        if not isinstance(critter, dict) or critter.get("id") == chosen_id or not critter.get("alive", True):
            continue
        if target_ids and str(critter.get("id")) not in target_ids:
            continue
        hex_xy = hex_value_xy(critter.get("hex"))
        if hex_xy is None:
            continue
        result.append(
            {
                "targetType": "visible_critter",
                "label": critter.get("name") or critter.get("protoId") or str(critter.get("id")),
                "id": critter.get("id"),
                "protoId": critter.get("protoId"),
                "hex": {"x": hex_xy[0], "y": hex_xy[1]},
                "arguments": {"targetId": critter.get("id")},
                "defaultCut": 0,
                "source": "visible_critter",
            }
        )
    return result


def nav_target_type_filters(arguments: dict[str, Any]) -> set[str]:
    values: list[str] = []
    for name in ("targetType", "targetTypes", "types"):
        value = arguments.get(name)
        if isinstance(value, list):
            values.extend(str(entry) for entry in value)
        elif isinstance(value, str) and value.strip():
            values.extend(part.strip() for part in value.split(","))
    return {value for value in values if value}


def nav_target_id_filters(arguments: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for name in ("id", "targetId", "itemId"):
        if name in arguments and arguments.get(name) is not None:
            result.add(str(arguments[name]))
    return result


def hex_value_xy(hex_value: Any) -> tuple[int, int] | None:
    if not isinstance(hex_value, dict):
        return None
    if "x" not in hex_value or "y" not in hex_value:
        return None
    return int(hex_value["x"]), int(hex_value["y"])


def default_nav_cut(target_type: Any) -> int:
    return 1 if str(target_type) in NAV_APPROACH_TYPES else 0


def nav_query_arguments(arguments: dict[str, Any], target: dict[str, Any], query_type: str) -> dict[str, Any]:
    hex_xy = hex_value_xy(target.get("hex"))
    if hex_xy is None:
        raise ValueError("navigation target has no hex")

    result: dict[str, Any] = {"toX": hex_xy[0], "toY": hex_xy[1]}
    for name in NAV_QUERY_OPTION_NAMES:
        if name in arguments:
            if name == "maxCandidates" and query_type != "tactical_path":
                continue
            result[name] = arguments[name]
    if "cut" not in result and query_type in {"path", "tactical_path"}:
        result["cut"] = int(target.get("defaultCut", 0))
    if query_type == "path" and "includeDirections" not in result:
        result["includeDirections"] = False
    return result


def nav_target_needs_standing_hex(target: dict[str, Any], route: dict[str, Any]) -> bool:
    if str(target.get("targetType")) not in NAV_APPROACH_STANDING_TYPES:
        return False
    if route.get("toMovable") is False:
        return True
    if route.get("query") == "tactical_path" and int(target.get("defaultCut", 0) or 0) > 0 and route.get("toMovable") is not True:
        return True
    return not route_reachable(route)


def find_approach_standing_route(selected_bridge: Any, arguments: dict[str, Any], target: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any] | None:
    target_xy = hex_value_xy(target.get("hex"))
    if target_xy is None:
        return None

    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    origin_xy = safe_hex_value_xy(chosen.get("hex"))
    radius = max(1, min(int(arguments.get("approachRadius", 1)), 3))
    max_candidates = max(1, min(int(arguments.get("maxApproachCandidates", 12)), 24))
    checks: list[dict[str, Any]] = []

    for xy in nearby_hex_candidates(target_xy, origin_xy, radius)[:max_candidates]:
        standing_target = {**target, "hex": {"x": xy[0], "y": xy[1]}, "targetType": "move_to_hex", "defaultCut": 0}
        query_args = nav_query_arguments({**arguments, "cut": 0}, standing_target, "path")
        query_args["includeDirections"] = False
        query_args.setdefault("timeoutMs", int(arguments.get("pathTimeoutMs", arguments.get("timeoutMs", DEFAULT_ENVIRONMENT_QUERY_TIMEOUT_MS))))
        query_args.setdefault("pollIntervalMs", int(arguments.get("pollIntervalMs", 100)))
        response = environment_query(selected_bridge, "path", query_args)
        if "error" in response:
            return response
        payload = response.get("result", {}) if isinstance(response.get("result"), dict) else {}
        route = payload.get("result") if isinstance(payload.get("result"), dict) else {}
        route = route_with_query(route, "path")
        check = {
            "hex": {"x": xy[0], "y": xy[1]},
            "reachable": route_reachable(route),
            "toMovable": route.get("toMovable"),
            "pathLength": route_path_length(route),
            "score": route_score(route),
        }
        checks.append(check)
        if route_reachable(route) and route.get("toMovable") is not False:
            return {
                "usedStandingHex": True,
                "reason": "target hex is occupied, blocked, or unreachable; move to a reachable adjacent standing hex first",
                "targetHex": target.get("hex"),
                "standingHex": {"x": xy[0], "y": xy[1]},
                "reachable": True,
                "toMovable": route.get("toMovable"),
                "pathLength": route_path_length(route),
                "score": route_score(route),
                "checks": checks,
                "route": route,
                "routeQuery": payload,
            }

    return {
        "usedStandingHex": False,
        "reason": "target hex looked unsuitable for direct movement, but no adjacent reachable standing hex was found",
        "targetHex": target.get("hex"),
        "checks": checks,
    }


def nearby_hex_candidates(center: tuple[int, int], origin: tuple[int, int] | None, radius: int) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            if dx == 0 and dy == 0:
                continue
            xy = (center[0] + dx, center[1] + dy)
            if approximate_hex_distance(center, xy) <= radius:
                result.append(xy)

    def sort_key(xy: tuple[int, int]) -> tuple[int, int, int, int, int, int]:
        origin_distance = approximate_hex_distance(origin, xy) if origin is not None else approximate_hex_distance(center, xy)
        center_distance = approximate_hex_distance(center, xy)
        return origin_distance, center_distance, abs(xy[1] - center[1]), abs(xy[0] - center[0]), xy[0], xy[1]

    result.sort(key=sort_key)
    return result


def route_with_query(route: dict[str, Any], query_type: str) -> dict[str, Any]:
    if not route or route.get("query"):
        return route
    return {**route, "query": query_type}


def route_reachable(route: dict[str, Any]) -> bool:
    if "reachable" in route:
        return bool(route.get("reachable"))
    if route.get("query") == "path" or ("pathLength" in route and "bestPathLength" not in route):
        if route.get("toMovable") is False:
            return False
        if route_path_length(route) == 0 and not route_from_equals_to(route):
            return route.get("toMovable") is True
        score = route_score(route)
        length = route_path_length(route)
        return score is not None and score >= 0 and length is not None and length >= 0
    if route.get("query") == "tactical_path" and route_path_length(route) == 0 and not route_from_equals_to(route):
        return False
    score = route_score(route)
    length = route_path_length(route)
    return score is not None and score >= 0 and length is not None and length >= 0


def route_from_equals_to(route: dict[str, Any]) -> bool:
    from_xy = hex_value_xy(route.get("from"))
    to_xy = hex_value_xy(route.get("to"))
    return from_xy is not None and to_xy is not None and from_xy == to_xy


def route_path_length(route: dict[str, Any]) -> int | None:
    for name in ("bestPathLength", "pathLength", "basePathLength", "directDistance"):
        value = route.get(name)
        if isinstance(value, int):
            return value
    return None


def route_score(route: dict[str, Any]) -> int | None:
    for name in ("bestScore", "score", "pathLength", "bestPathLength"):
        value = route.get(name)
        if isinstance(value, int):
            return value
    return None


def adjusted_route_score(route: dict[str, Any], route_memory: dict[str, Any] | None) -> int | None:
    score = route_score(route)
    if score is None:
        score = route_path_length(route)
    if score is None:
        return None
    penalty = int(route_memory.get("penalty", 0)) if isinstance(route_memory, dict) else 0
    return score + max(0, penalty)


def nav_movement_step(target: dict[str, Any]) -> dict[str, Any]:
    movement_hex = target.get("movementHex") if isinstance(target.get("movementHex"), dict) else target.get("hex")
    hex_xy = hex_value_xy(movement_hex)
    if hex_xy is None:
        return {}
    return {"tool": "tla_move_to_hex", "arguments": {"x": hex_xy[0], "y": hex_xy[1]}, "cut": int(target.get("defaultCut", 0))}


def nav_follow_up(target: dict[str, Any]) -> dict[str, Any] | None:
    tool = target.get("tool")
    if not tool or target.get("targetType") == "move_to_hex":
        return None
    return {"tool": tool, "arguments": target.get("arguments", {}), "targetType": target.get("targetType")}


def nav_candidate_assessment(
    candidate: dict[str, Any],
    route: dict[str, Any],
    query_payload: dict[str, Any],
    observation: dict[str, Any] | None = None,
    profile: dict[str, Any] | None = None,
    memory: dict[str, Any] | None = None,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    route_memory = (
        nav_route_memory_assessment(
            observation,
            profile,
            memory,
            candidate.get("hex"),
            candidate.get("targetType"),
            arguments or {},
            candidate.get("id"),
        )
        if observation is not None
        and profile is not None
        and memory is not None
        and bool((arguments or {}).get("memoryAware", True))
        else None
    )
    return {
        "target": {
            key: candidate.get(key)
            for key in (
                "targetType",
                "label",
                "id",
                "protoId",
                "hex",
                "reason",
                "source",
                "hasDoor",
                "hasContainer",
                "hasLocker",
                "opened",
                "canOpen",
                "isGag",
                "noHighlight",
                "hasStaticScript",
                "static",
                "isStatic",
            )
            if key in candidate
        },
        "reachable": route_reachable(route),
        "pathLength": route_path_length(route),
        "directDistance": route.get("directDistance"),
        "risk": route.get("bestRisk", route.get("baseRisk")),
        "score": route_score(route),
        "adjustedScore": adjusted_route_score(route, route_memory),
        "routeMemory": route_memory,
        "usesDetour": route.get("usesDetour"),
        "bestVia": route.get("bestVia"),
        "movement": nav_movement_step(candidate) if route_reachable(route) else {},
        "followUp": nav_follow_up(candidate) if route_reachable(route) else None,
        "route": route,
        "query": query_payload,
    }


def cover_anchor_entries(obstacles_result: dict[str, Any]) -> list[dict[str, Any]]:
    obstacles = obstacles_result.get("obstacles") if isinstance(obstacles_result.get("obstacles"), list) else []
    anchors: list[dict[str, Any]] = []
    for obstacle in obstacles:
        if not isinstance(obstacle, dict):
            continue
        movable = bool(obstacle.get("movable"))
        shootable = bool(obstacle.get("shootable"))
        if movable and shootable:
            continue
        score = 50
        reasons: list[str] = []
        if not shootable:
            score += 30
            reasons.append("blocks shooting/line of fire")
        if not movable:
            score += 10
            reasons.append("blocks movement")
        critter_count = int(obstacle.get("critterCount") or 0)
        item_count = int(obstacle.get("itemCount") or 0)
        if critter_count:
            score -= 15
            reasons.append("occupied by critter")
        if item_count:
            reasons.append("contains item")
        anchors.append(
            {
                "hex": obstacle.get("hex"),
                "score": score,
                "movable": movable,
                "shootable": shootable,
                "critterCount": critter_count,
                "itemCount": item_count,
                "reason": "; ".join(reasons),
                "obstacle": obstacle,
            }
        )
    anchors.sort(key=lambda entry: int(entry.get("score", 0)), reverse=True)
    return anchors


def vantage_assessment(candidate: dict[str, Any], trace: dict[str, Any], query_payload: dict[str, Any]) -> dict[str, Any]:
    line_of_sight = bool(trace.get("reachedTarget")) and not bool(trace.get("blocked"))
    score = 100 if line_of_sight else 20
    direct_distance = trace.get("directDistance")
    if isinstance(direct_distance, int):
        score -= min(direct_distance, 40)
    return {
        "target": {key: candidate.get(key) for key in ("targetType", "label", "id", "protoId", "hex", "source") if key in candidate},
        "lineOfSight": line_of_sight,
        "score": score,
        "directDistance": direct_distance,
        "traceHex": trace.get("traceHex"),
        "traceHexShootable": trace.get("traceHexShootable"),
        "crittersInPath": trace.get("crittersInPath", []),
        "trace": trace,
        "query": query_payload,
    }


def next_agent_decision_id(bridge: Any) -> int:
    owner = bridge_owner(bridge)
    value = int(getattr(owner, "next_agent_decision_id", 1))
    setattr(owner, "next_agent_decision_id", value + 1)
    return value


def agent_decisions_for_key(bridge: Any, key: str, limit: int = 20) -> list[dict[str, Any]]:
    decisions = ensure_agent_decisions(bridge)
    entries = decisions.get(key)
    if not isinstance(entries, list):
        entries = []
        decisions[key] = entries
    if limit <= 0:
        return []
    return entries[-min(limit, 200):]


def record_agent_decision(bridge: Any, key: str, decision: dict[str, Any]) -> None:
    decisions = ensure_agent_decisions(bridge)
    entries = decisions.get(key)
    if not isinstance(entries, list):
        entries = []
        decisions[key] = entries
    append_bounded(entries, decision, 200)


def agent_status_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    endpoint = resolve_target_endpoint(bridge, arguments)
    key = agent_profile_key(bridge, endpoint)
    memory = agent_memory_for_key(bridge, key)
    runtime = agent_runtime_for_key(bridge, key)
    profile = normalized_agent_profile({}, ensure_agent_profiles(bridge).get(key))
    return {
        "jsonrpc": "2.0",
        "id": None,
        "result": {
            "endpoint": endpoint,
            "key": key,
            "profile": profile,
            "runtime": runtime,
            "memory": agent_memory_summary(memory),
            "recentDecisions": agent_decisions_for_key(bridge, key, int(arguments.get("limit", 10))),
            "mode": "advisory",
        },
    }


def set_agent_paused_state(bridge: Any, arguments: dict[str, Any], paused: bool) -> dict[str, Any]:
    endpoint = resolve_target_endpoint(bridge, arguments)
    key = agent_profile_key(bridge, endpoint)
    runtime = agent_runtime_for_key(bridge, key)
    runtime["paused"] = paused
    if not paused:
        runtime["stopped"] = False
    runtime["updatedAt"] = unix_ms()
    if "reason" in arguments:
        runtime["pauseReason" if paused else "resumeReason"] = str(arguments.get("reason", "")).strip()
    return {"jsonrpc": "2.0", "id": None, "result": {"endpoint": endpoint, "key": key, "runtime": runtime}}


def stop_agent_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    endpoint = resolve_target_endpoint(bridge, arguments)
    key = agent_profile_key(bridge, endpoint)
    runtime = agent_runtime_for_key(bridge, key)
    reason = str(arguments.get("reason", "agent stopped by host")).strip() or "agent stopped by host"
    runtime["paused"] = True
    runtime["stopped"] = True
    runtime["stopReason"] = reason
    runtime["updatedAt"] = unix_ms()
    return {"jsonrpc": "2.0", "id": None, "result": {"endpoint": endpoint, "key": key, "runtime": runtime}}


def stop_all_agents_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    owner = bridge_owner(bridge)
    runtime = ensure_agent_runtime(owner)
    reason = str(arguments.get("reason", "all agents stopped by host")).strip() or "all agents stopped by host"
    now = unix_ms()
    stopped: list[str] = []
    for key, state in runtime.items():
        if not isinstance(state, dict):
            continue
        state["paused"] = True
        state["stopped"] = True
        state["stopReason"] = reason
        state["updatedAt"] = now
        stopped.append(str(key))
    return {"jsonrpc": "2.0", "id": None, "result": {"stopped": stopped, "reason": reason, "runtimeCount": len(stopped)}}


def normalized_agent_policy_value(value: Any, allowed: set[str], default: str) -> str:
    text = str(value or "").strip().lower().replace("-", "_")
    return text if text in allowed else default


def agent_run_policy(arguments: dict[str, Any]) -> dict[str, Any]:
    deployment_mode = normalized_agent_policy_value(arguments.get("deploymentMode"), AGENT_DEPLOYMENT_MODES, AGENT_POLICY_DEFAULT_DEPLOYMENT_MODE)
    permission_mode = normalized_agent_policy_value(arguments.get("permissionMode"), AGENT_PERMISSION_MODES, AGENT_POLICY_DEFAULT_PERMISSION_MODE)
    agent_disclosure = bool(arguments.get("agentDisclosure", deployment_mode in {"test_only", "private_qa"}))
    out_of_band_requested = bool(arguments.get("outOfBandCoordination", permission_mode == "qa_out_of_band"))
    out_of_band_allowed = permission_mode == "qa_out_of_band" and deployment_mode in {"test_only", "private_qa"}
    out_of_band = out_of_band_requested and out_of_band_allowed

    warnings: list[str] = []
    blockers: list[str] = []
    markers: list[str] = []
    enforced: list[str] = []

    if deployment_mode in {"marked_bot", "production_npc", "supervised_agent"} and not agent_disclosure:
        blockers.append("agentDisclosure is required for marked/supervised/production deployment modes")
    if permission_mode == "qa_out_of_band" and deployment_mode not in {"test_only", "private_qa"}:
        blockers.append("qa_out_of_band permission mode is restricted to test_only/private_qa deployment")
    if out_of_band:
        markers.append("out_of_band_coordination")
    elif out_of_band_requested:
        markers.append("out_of_band_requested")
        enforced.append("out-of-band coordination disabled outside qa_out_of_band test/private QA mode")
    if bool(arguments.get("allowRawInput", False)):
        markers.append("raw_input_requested")
        if permission_mode not in {"raw_input_fallback", "qa_out_of_band"}:
            enforced.append("raw input disabled by permissionMode")
    if permission_mode == "observe_only":
        enforced.append("execute disabled by observe_only permissionMode")
    if deployment_mode in {"test_only", "private_qa"}:
        markers.append("qa_context")
    if permission_mode == "raw_input_fallback":
        warnings.append("raw_input_fallback should be used only when typed tools are insufficient and the host can supervise the client")
    if deployment_mode == "production_npc":
        warnings.append("production_npc mode must stay visibly/operationally marked by the host and use only client-visible data")

    return {
        "deploymentMode": deployment_mode,
        "permissionMode": permission_mode,
        "agentDisclosure": agent_disclosure,
        "outOfBandCoordination": out_of_band,
        "policyNote": str(arguments.get("policyNote", "")).strip(),
        "markers": sorted(set(markers)),
        "warnings": warnings,
        "blockers": blockers,
        "enforced": enforced,
        "readiness": {
            "canExecute": not blockers,
            "clientVisibleOnly": True,
            "decisionTraceRequired": True,
            "auditRequired": True,
            "humanLikeMeans": "believable client behavior, not deceptive real-user impersonation",
        },
    }


def agent_run_effective_arguments(arguments: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    effective = dict(arguments)
    permission_mode = str(policy.get("permissionMode") or AGENT_POLICY_DEFAULT_PERMISSION_MODE)
    effective["deploymentMode"] = policy.get("deploymentMode")
    effective["permissionMode"] = permission_mode
    if permission_mode == "observe_only":
        effective["execute"] = False
        effective["maxActions"] = 0
    if bool(effective.get("allowRawInput", False)) and permission_mode not in {"raw_input_fallback", "qa_out_of_band"}:
        effective["allowRawInput"] = False
    return effective


def policy_blocked_agent_run_result(selected_bridge: Any, key: str, runtime: dict[str, Any], policy: dict[str, Any], started_at: int) -> dict[str, Any]:
    runtime["lastRunAt"] = unix_ms()
    runtime["lastRunActions"] = 0
    runtime["lastRunSteps"] = 0
    runtime["lastRunStoppedReason"] = "policy_not_ready"
    return {
        "jsonrpc": "2.0",
        "id": None,
        "result": {
            "endpoint": getattr(selected_bridge, "endpoint", None),
            "key": key,
            "startedAt": started_at,
            "finishedAt": runtime["lastRunAt"],
            "execute": False,
            "steps": [],
            "actionsExecuted": 0,
            "stoppedReason": "policy_not_ready",
            "runtime": runtime,
            "policy": policy,
        },
    }


def agent_tick_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    selected_bridge = target_bridge(bridge, arguments)
    key = agent_profile_key(selected_bridge)
    runtime = agent_runtime_for_key(selected_bridge, key)
    now = unix_ms()

    step_response = step_state(selected_bridge, arguments)
    if "error" in step_response:
        return step_response

    step_result = step_response.get("result", step_response)
    if not isinstance(step_result, dict):
        return step_response

    memory = agent_memory_for_key(selected_bridge, key)
    update_agent_memory_from_step(selected_bridge, memory, step_result, now)
    profile = agent_profile_for_target(selected_bridge)
    decision = build_agent_decision(selected_bridge, key, profile, memory, runtime, step_result, arguments, now)
    apply_agent_humanization(decision, profile, memory, runtime, arguments, now)
    remember_agent_reply_decision(runtime, decision, now)
    remember_agent_idle_decision(runtime, decision, now)
    runtime["lastTickAt"] = now
    runtime["lastDecisionId"] = decision.get("decisionId")
    record_agent_decision(selected_bridge, key, decision)

    result: dict[str, Any] = {
        "endpoint": getattr(selected_bridge, "endpoint", None),
        "key": key,
        "profile": profile,
        "runtime": runtime,
        "memory": agent_memory_summary(memory),
        "decision": decision,
        "policy": {
            "mode": "advisory",
            "executesCommands": False,
            "authority": "client-visible MCP tools only; no hidden server state",
        },
    }
    if bool(arguments.get("includeStep", True)):
        result["step"] = step_result

    return {"jsonrpc": "2.0", "id": None, "result": result}


def agent_run_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    selected_bridge = target_bridge(bridge, arguments)
    key = agent_profile_key(selected_bridge)
    runtime = agent_runtime_for_key(selected_bridge, key)
    started_at = unix_ms()
    policy = agent_run_policy(arguments)
    if bool(arguments.get("execute", False)) and not bool(policy.get("readiness", {}).get("canExecute", False)):
        return policy_blocked_agent_run_result(selected_bridge, key, runtime, policy, started_at)

    run_arguments = agent_run_effective_arguments(arguments, policy)
    max_steps = max(1, min(int(run_arguments.get("maxSteps", 1)), 20))
    max_actions = max(0, min(int(run_arguments.get("maxActions", max_steps)), max_steps))
    execute = bool(run_arguments.get("execute", False))
    steps: list[dict[str, Any]] = []
    actions_executed = 0
    stopped_reason = ""
    loop_detection_enabled = bool(run_arguments.get("enableLoopDetection", True))

    for index in range(max_steps):
        tick_arguments = agent_run_tick_arguments(run_arguments)
        tick_arguments["includeStep"] = True
        tick_response = agent_tick_state(selected_bridge, tick_arguments)
        if "error" in tick_response:
            return tick_response

        tick = tick_response.get("result", tick_response)
        if not isinstance(tick, dict):
            return tick_response

        decision = tick.get("decision") if isinstance(tick.get("decision"), dict) else {}
        step: dict[str, Any] = {"index": index, "decision": decision, "execution": None}
        step_state = agent_run_step_state(tick)
        if step_state:
            step["state"] = step_state

        distress = agent_run_distress_signal(tick, run_arguments) if bool(run_arguments.get("stopOnDistress", False)) else {}
        if distress:
            step["distress"] = distress
            step["execution"] = {"executed": False, "blocked": True, "blockedBy": ["player distress keyword"], "reason": "visible speech requested stop"}
            stopped_reason = "player_distress"
            runtime["paused"] = True
            runtime["stopped"] = True
            runtime["stopReason"] = "player distress keyword"
            runtime["updatedAt"] = unix_ms()
        elif execute and actions_executed < max_actions:
            scheduler = agent_run_scheduler_gate(runtime, decision, run_arguments, unix_ms())
            if not bool(scheduler.get("allowed", True)):
                execution = {
                    "executed": False,
                    "blocked": False,
                    "throttled": True,
                    "reason": "scheduler back-pressure",
                    "scheduler": scheduler,
                }
                step["execution"] = execution
                if bool(run_arguments.get("stopOnSchedulerWait", True)):
                    stopped_reason = "scheduler_wait"
                elif bool(run_arguments.get("stopOnNoAction", True)):
                    stopped_reason = "no_action"
                steps.append(step)
                if stopped_reason:
                    break
                continue

            execution = execute_agent_run_decision(selected_bridge, key, decision, tick, run_arguments)
            step["execution"] = execution
            if bool(execution.get("executed")):
                actions_executed += 1
                remember_agent_run_action(runtime, execution, unix_ms())
            if bool(run_arguments.get("stopOnBlocked", True)) and execution.get("blocked"):
                stopped_reason = "blocked"
            elif bool(run_arguments.get("stopOnNoAction", True)) and not execution.get("executed"):
                stopped_reason = "no_action"
        elif execute and actions_executed >= max_actions:
            step["execution"] = {"executed": False, "blocked": True, "blockedBy": ["maxActions reached"]}
            stopped_reason = "max_actions"
        else:
            step["execution"] = {"executed": False, "dryRun": True, "reason": "execute=false"}
            if bool(run_arguments.get("stopOnNoAction", True)):
                stopped_reason = "dry_run"

        steps.append(step)

        if loop_detection_enabled:
            loop = agent_run_loop_detection(steps, run_arguments)
            if loop.get("detected"):
                step["loop"] = loop
                if bool(run_arguments.get("stopOnLoop", True)):
                    stopped_reason = str(loop.get("stoppedReason", "loop"))

        if stopped_reason:
            break

        if bool(run_arguments.get("respectDelay", False)) and index + 1 < max_steps:
            delay_ms = int(decision.get("suggestedDelayMs") or 0)
            max_sleep_ms = max(0, min(int(run_arguments.get("maxSleepMs", 1500)), 5000))
            if delay_ms > 0 and max_sleep_ms > 0:
                time.sleep(min(delay_ms, max_sleep_ms) / 1000.0)

    runtime["lastRunAt"] = unix_ms()
    runtime["lastRunActions"] = actions_executed
    runtime["lastRunSteps"] = len(steps)
    runtime["lastRunStoppedReason"] = stopped_reason or "completed"

    return {
        "jsonrpc": "2.0",
        "id": None,
        "result": {
            "endpoint": getattr(selected_bridge, "endpoint", None),
            "key": key,
            "startedAt": started_at,
            "finishedAt": runtime["lastRunAt"],
            "execute": execute,
            "steps": steps,
            "actionsExecuted": actions_executed,
            "stoppedReason": runtime["lastRunStoppedReason"],
            "runtime": runtime,
            "policy": {
                **policy,
                "authority": "commands execute only through normal typed MCP tools and server validation",
                "effectiveExecute": execute,
                "rawInputAllowed": bool(run_arguments.get("allowRawInput", False)),
                "combatAllowed": bool(run_arguments.get("allowCombat", False)),
                "pathValidation": bool(run_arguments.get("validatePath", True)),
                "loopDetection": loop_detection_enabled,
                "scheduler": agent_run_scheduler_policy(run_arguments),
            },
        },
    }


def agent_run_scheduler_policy(arguments: dict[str, Any]) -> dict[str, Any]:
    return {
        "minActionIntervalMs": max(0, min(int(arguments.get("minActionIntervalMs", 0)), 60000)),
        "maxActionsPerMinute": max(0, min(int(arguments.get("maxActionsPerMinute", 0)), 600)),
        "schedulerJitterMs": max(0, min(int(arguments.get("schedulerJitterMs", 0)), 10000)),
        "allowHighPriorityInterrupt": bool(arguments.get("allowHighPriorityInterrupt", True)),
        "stopOnSchedulerWait": bool(arguments.get("stopOnSchedulerWait", True)),
    }


def agent_run_scheduler_gate(runtime: dict[str, Any], decision: dict[str, Any], arguments: dict[str, Any], now: int) -> dict[str, Any]:
    policy = agent_run_scheduler_policy(arguments)
    tool_name = str(decision.get("suggestedTool") or "")
    priority = str(decision.get("priority") or "").lower()
    if not tool_name:
        return {"allowed": True, **policy, "reason": "no suggested tool"}

    required_interval_ms = int(policy["minActionIntervalMs"])
    jitter_ms = int(policy["schedulerJitterMs"])
    if jitter_ms > 0:
        seed = int(arguments.get("schedulerSeed", decision.get("decisionId") or 1))
        required_interval_ms += deterministic_jitter_ms(seed, jitter_ms)

    last_action_at = runtime.get("lastActionAt")
    if isinstance(last_action_at, int) and required_interval_ms > 0:
        elapsed_ms = now - last_action_at
        if elapsed_ms < required_interval_ms:
            if priority == "high" and bool(policy.get("allowHighPriorityInterrupt", True)):
                # A high-priority decision may interrupt minActionIntervalMs, but it must NOT
                # bypass the maxActionsPerMinute hard back-pressure cap.
                max_per_minute = int(policy["maxActionsPerMinute"])
                recent_actions = recent_agent_run_actions(runtime, now, 60_000)
                if max_per_minute > 0 and len(recent_actions) >= max_per_minute:
                    oldest = recent_actions[0]
                    oldest_time = int(oldest.get("time", now)) if isinstance(oldest, dict) else now
                    return {
                        "allowed": False,
                        **policy,
                        "recentActions": len(recent_actions),
                        "remainingMs": max(0, 60_000 - (now - oldest_time)),
                        "reason": "maxActionsPerMinute",
                    }
                return {
                    "allowed": True,
                    **policy,
                    "interruptedCooldown": True,
                    "elapsedMs": elapsed_ms,
                    "requiredIntervalMs": required_interval_ms,
                    "reason": "high-priority decision interrupts minActionIntervalMs",
                }
            return {
                "allowed": False,
                **policy,
                "elapsedMs": elapsed_ms,
                "remainingMs": required_interval_ms - elapsed_ms,
                "requiredIntervalMs": required_interval_ms,
                "reason": "minActionIntervalMs",
            }

    max_per_minute = int(policy["maxActionsPerMinute"])
    recent_actions = recent_agent_run_actions(runtime, now, 60_000)
    if max_per_minute > 0 and len(recent_actions) >= max_per_minute:
        oldest = recent_actions[0]
        oldest_time = int(oldest.get("time", now)) if isinstance(oldest, dict) else now
        return {
            "allowed": False,
            **policy,
            "recentActions": len(recent_actions),
            "remainingMs": max(0, 60_000 - (now - oldest_time)),
            "reason": "maxActionsPerMinute",
        }

    return {
        "allowed": True,
        **policy,
        "recentActions": len(recent_actions),
        "requiredIntervalMs": required_interval_ms,
        "reason": "allowed",
    }


def deterministic_jitter_ms(seed: int, maximum: int) -> int:
    if maximum <= 0:
        return 0
    return abs(seed * 1103515245 + 12345) % (maximum + 1)


def recent_agent_run_actions(runtime: dict[str, Any], now: int, window_ms: int) -> list[dict[str, Any]]:
    history = runtime.get("actionHistory")
    if not isinstance(history, list):
        return []
    return [
        entry
        for entry in history
        if isinstance(entry, dict) and isinstance(entry.get("time"), int) and now - int(entry["time"]) <= window_ms
    ]


def remember_agent_run_action(runtime: dict[str, Any], execution: dict[str, Any], now: int) -> None:
    history = runtime.get("actionHistory")
    if not isinstance(history, list):
        history = []
        runtime["actionHistory"] = history
    entry = {
        "time": now,
        "tool": execution.get("tool"),
        "accepted": execution.get("accepted"),
        "arguments": execution.get("arguments") if isinstance(execution.get("arguments"), dict) else {},
    }
    append_bounded(history, entry, 200)
    runtime["lastActionAt"] = now
    runtime["lastActionTool"] = execution.get("tool")


def agent_run_step_state(tick: dict[str, Any]) -> dict[str, Any]:
    step_result = tick.get("step") if isinstance(tick.get("step"), dict) else {}
    decision = tick.get("decision") if isinstance(tick.get("decision"), dict) else {}
    decision_arguments = decision.get("arguments") if isinstance(decision.get("arguments"), dict) else {}
    observation_payload = step_result.get("observation") if isinstance(step_result.get("observation"), dict) else {}
    observation = unwrap_observation_payload(observation_payload) if observation_payload else {}
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    global_map = observation.get("globalMap") if isinstance(observation.get("globalMap"), dict) else {}
    dialog = observation.get("dialog") if isinstance(observation.get("dialog"), dict) else {}
    state: dict[str, Any] = {
        "hasMap": observation.get("hasMap"),
        "hasChosen": observation.get("hasChosen"),
        "mapId": observation.get("mapId"),
        "mapProtoId": observation.get("map", {}).get("protoId") if isinstance(observation.get("map"), dict) else None,
        "chosenId": chosen.get("id") if isinstance(chosen, dict) else None,
        "chosenHex": chosen.get("hex") if isinstance(chosen.get("hex"), dict) else None,
        "level": chosen.get("level") if isinstance(chosen, dict) else None,
        "experience": chosen.get("experience") if isinstance(chosen, dict) else None,
        "experienceToNextLevel": chosen.get("experienceToNextLevel") if isinstance(chosen, dict) else None,
        "unspentSkillPoints": chosen.get("unspentSkillPoints") if isinstance(chosen, dict) else None,
        "unspentAbilityPoints": chosen.get("unspentAbilityPoints") if isinstance(chosen, dict) else None,
    }
    skills = chosen.get("skills") if isinstance(chosen.get("skills"), list) else []
    if skills:
        state["skills"] = [
            {
                "id": skill_property_name(skill.get("id")),
                "value": skill.get("value"),
            }
            for skill in skills
            if isinstance(skill, dict) and skill.get("id") is not None and skill.get("value") is not None
        ][:20]
    if isinstance(global_map, dict) and global_map:
        state["globalMapActive"] = global_map.get("active")
        state["globalPosition"] = global_map.get("position") if isinstance(global_map.get("position"), dict) else None
    if bool(dialog.get("active")):
        answers = dialog.get("answers") if isinstance(dialog.get("answers"), list) else []
        state["dialogId"] = dialog.get("dialogId")
        state["dialogText"] = dialog.get("text")
        state["dialogAnswers"] = [str(answer.get("text") or "") for answer in answers if isinstance(answer, dict)][:5]
    target_id = decision_arguments.get("targetId")
    if target_id is not None:
        for critter in observation.get("critters", []) if isinstance(observation.get("critters"), list) else []:
            if not isinstance(critter, dict) or str(critter.get("id")) != str(target_id):
                continue
            state["targetCritter"] = {
                key: critter.get(key)
                for key in ("id", "protoId", "name", "hex", "alive", "dead", "curHealth", "maxHealth", "inCombat")
                if critter.get(key) is not None
            }
            break
    return {key: value for key, value in state.items() if value is not None}


def agent_run_distress_signal(tick: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    keywords = normalize_string_list(arguments.get("distressKeywords")) or list(AGENT_DISTRESS_KEYWORDS)
    lowered_keywords = [keyword.lower() for keyword in keywords if keyword.strip()]
    if not lowered_keywords:
        return {}

    step_result = tick.get("step") if isinstance(tick.get("step"), dict) else {}
    social = step_result.get("social") if isinstance(step_result.get("social"), dict) else {}
    heard = social.get("heardSpeech") if isinstance(social.get("heardSpeech"), list) else []
    for speech in heard:
        if not isinstance(speech, dict) or bool(speech.get("selfSpeech")):
            continue
        text = str(speech.get("text", "")).strip()
        lowered = text.lower()
        if not lowered:
            continue
        matched = [keyword for keyword in lowered_keywords if keyword in lowered]
        if matched:
            return {
                "detected": True,
                "keyword": matched[0],
                "text": text,
                "speaker": speech.get("speaker"),
                "addressedToAgent": speech.get("addressedToAgent"),
                "intent": speech.get("intent"),
            }
    return {}


def agent_run_loop_detection(steps: list[dict[str, Any]], arguments: dict[str, Any]) -> dict[str, Any]:
    repeated_limit = max(2, min(int(arguments.get("repeatedDecisionLimit", 3)), 20))
    failed_limit = max(2, min(int(arguments.get("failedActionLimit", 3)), 20))
    stuck_movement_limit = max(2, min(int(arguments.get("stuckMovementLimit", 3)), 20))

    failed_count = consecutive_failed_action_count(steps)
    if failed_count >= failed_limit:
        failed_signature_count = consecutive_matching_failed_action_count(steps)
        kind = "over_aggressive_retry" if failed_signature_count >= failed_limit else "failed_action_burst"
        return {
            "detected": True,
            "kind": kind,
            "count": failed_count,
            "limit": failed_limit,
            "tool": agent_run_step_tool(steps[-1]),
            "intent": agent_run_step_intent(steps[-1]),
            "failedSignature": agent_run_failed_action_signature(steps[-1]),
            "sameFailureCount": failed_signature_count,
            "stoppedReason": "loop_over_aggressive_retry" if kind == "over_aggressive_retry" else "loop_failed_actions",
        }

    stuck_movement_count = consecutive_stuck_movement_count(steps)
    if stuck_movement_count >= stuck_movement_limit:
        return {
            "detected": True,
            "kind": "stuck_movement",
            "count": stuck_movement_count,
            "limit": stuck_movement_limit,
            "tool": agent_run_step_tool(steps[-1]),
            "intent": agent_run_step_intent(steps[-1]),
            "fromHex": agent_run_step_chosen_hex(steps[-1]),
            "targetHex": agent_run_step_target_hex(steps[-1]),
            "stoppedReason": "loop_stuck_movement",
        }

    repeated_count = consecutive_matching_count(steps, agent_run_step_signature)
    if repeated_count >= repeated_limit:
        if agent_run_repeated_wait_allowed(steps[-1]):
            return {"detected": False}
        if agent_run_repeated_action_allowed(steps[-1]):
            return {"detected": False}
        kind = agent_run_repeated_loop_kind(steps[-1])
        return {
            "detected": True,
            "kind": kind,
            "count": repeated_count,
            "limit": repeated_limit,
            "signature": agent_run_step_signature(steps[-1]),
            "tool": agent_run_step_tool(steps[-1]),
            "intent": agent_run_step_intent(steps[-1]),
            "stoppedReason": agent_run_loop_stopped_reason(kind),
        }

    return {"detected": False}


def agent_run_repeated_wait_allowed(step: dict[str, Any]) -> bool:
    decision = step.get("decision") if isinstance(step.get("decision"), dict) else {}
    if decision.get("intent") == "idle_observe" and decision.get("source") == "combat_movement_guard":
        return True
    if decision.get("intent") == "modal_screen_wait" and decision.get("source") == "modal_screen":
        return True
    if decision.get("intent") == "heal_wait" and decision.get("source") == "combat_options":
        return True
    return decision.get("intent") == "recover_stamina_wait" and decision.get("source") == "combat_options"


def agent_run_repeated_action_allowed(step: dict[str, Any]) -> bool:
    tool_name = agent_run_step_tool(step)
    execution = step.get("execution") if isinstance(step.get("execution"), dict) else {}
    return tool_name in {"tla_attack_entity", "tla_attack_hex"} and bool(execution.get("accepted"))


def consecutive_matching_count(steps: list[dict[str, Any]], signature_builder: Any) -> int:
    if not steps:
        return 0
    current = signature_builder(steps[-1])
    count = 0
    for step in reversed(steps):
        if signature_builder(step) != current:
            break
        count += 1
    return count


def agent_run_step_signature(step: dict[str, Any]) -> str:
    return json.dumps(agent_run_step_signature_payload(step), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def agent_run_step_signature_payload(step: dict[str, Any]) -> dict[str, Any]:
    decision = step.get("decision") if isinstance(step.get("decision"), dict) else {}
    arguments = decision.get("arguments") if isinstance(decision.get("arguments"), dict) else {}
    tool_name = decision.get("suggestedTool") or decision.get("tool")
    payload = {
        "intent": decision.get("intent"),
        "tool": tool_name,
        "arguments": arguments,
    }
    if decision.get("intent") == "dialog_answer" or tool_name == "tla_dialog_answer":
        state = step.get("state") if isinstance(step.get("state"), dict) else {}
        payload["dialogContext"] = {
            key: state.get(key)
            for key in ("dialogId", "dialogText", "dialogAnswers")
            if state.get(key) not in (None, "", [])
        }
    if tool_name == "tla_say" or decision.get("intent") in {"say", "reply_to_speech"}:
        # The reply text lives in decision["speech"], not decision["arguments"], so without this
        # branch distinct replies to different speakers collapse to one signature and trip the
        # repeated-speech loop detector. Mirror agent_reply_signature (speaker id + casefolded text).
        speech = decision.get("speech") if isinstance(decision.get("speech"), dict) else {}
        speaker = speech.get("speaker") if isinstance(speech.get("speaker"), dict) else {}
        payload["speechContext"] = {
            key: value
            for key, value in {
                "speakerId": speaker.get("id"),
                "text": str(speech.get("text", "")).strip().casefold() or None,
                "intent": speech.get("intent"),
            }.items()
            if value is not None
        }
    if tool_name == "tla_change_skill" or decision.get("intent") == "change_skill":
        state = step.get("state") if isinstance(step.get("state"), dict) else {}
        skill = str(arguments.get("skill") or "")
        payload["progressionState"] = {
            "unspentSkillPoints": state.get("unspentSkillPoints"),
            "skillValue": state_skill_value(state, skill),
        }
    if tool_name == "tla_change_ability" or decision.get("intent") == "change_ability":
        state = step.get("state") if isinstance(step.get("state"), dict) else {}
        payload["progressionState"] = {
            "unspentAbilityPoints": state.get("unspentAbilityPoints"),
        }
    if tool_name == "tla_move_to_hex":
        state = step.get("state") if isinstance(step.get("state"), dict) else {}
        execution = step.get("execution") if isinstance(step.get("execution"), dict) else {}
        path = execution.get("path") if isinstance(execution.get("path"), dict) else {}
        payload["movementState"] = {
            key: value
            for key, value in {
                "chosenHex": state.get("chosenHex"),
                "pathLength": path.get("pathLength"),
                "directDistance": path.get("directDistance"),
            }.items()
            if value is not None
        }
    if tool_name in {"tla_attack_entity", "tla_attack_hex"}:
        state = step.get("state") if isinstance(step.get("state"), dict) else {}
        target = state.get("targetCritter") if isinstance(state.get("targetCritter"), dict) else {}
        payload["combatState"] = {
            key: value
            for key, value in {
                "chosenHex": state.get("chosenHex"),
                "targetHex": target.get("hex"),
                "targetAlive": target.get("alive"),
                "targetDead": target.get("dead"),
                "targetHealth": target.get("curHealth"),
                "targetInCombat": target.get("inCombat"),
            }.items()
            if value is not None
        }
    return payload


def state_skill_value(state: dict[str, Any], skill: str) -> Any:
    try:
        normalized = skill_property_name(skill)
    except ValueError:
        normalized = skill
    skills = state.get("skills") if isinstance(state.get("skills"), list) else []
    for entry in skills:
        if not isinstance(entry, dict):
            continue
        try:
            entry_id = skill_property_name(entry.get("id"))
        except ValueError:
            entry_id = str(entry.get("id") or "")
        if entry_id == normalized:
            return entry.get("value")
    return None


def agent_run_step_tool(step: dict[str, Any]) -> str:
    decision = step.get("decision") if isinstance(step.get("decision"), dict) else {}
    execution = step.get("execution") if isinstance(step.get("execution"), dict) else {}
    return str(execution.get("tool") or decision.get("suggestedTool") or "")


def agent_run_step_intent(step: dict[str, Any]) -> str:
    decision = step.get("decision") if isinstance(step.get("decision"), dict) else {}
    return str(decision.get("intent") or "")


def agent_run_repeated_loop_kind(step: dict[str, Any]) -> str:
    tool_name = agent_run_step_tool(step)
    intent = agent_run_step_intent(step)
    if tool_name == "tla_say" or intent in {"say", "reply_to_speech"}:
        return "repeated_speech"
    if not tool_name or intent in {"observe", "paused"} or intent.startswith("idle_"):
        return "empty_idle_loop"
    if agent_run_step_failed(step):
        return "over_aggressive_retry"
    return "repeated_decision"


def agent_run_loop_stopped_reason(kind: str) -> str:
    return {
        "repeated_speech": "loop_repeated_speech",
        "empty_idle_loop": "loop_empty_idle",
        "over_aggressive_retry": "loop_over_aggressive_retry",
        "failed_action_burst": "loop_failed_actions",
        "stuck_movement": "loop_stuck_movement",
    }.get(kind, "loop_repeated_decision")


def consecutive_failed_action_count(steps: list[dict[str, Any]]) -> int:
    count = 0
    for step in reversed(steps):
        if agent_run_step_failed(step):
            count += 1
            continue
        break
    return count


def consecutive_matching_failed_action_count(steps: list[dict[str, Any]]) -> int:
    if not steps or not agent_run_step_failed(steps[-1]):
        return 0
    current = agent_run_failed_action_signature(steps[-1])
    count = 0
    for step in reversed(steps):
        if not agent_run_step_failed(step):
            break
        if agent_run_failed_action_signature(step) != current:
            break
        count += 1
    return count


def agent_run_step_failed(step: dict[str, Any]) -> bool:
    execution = step.get("execution") if isinstance(step.get("execution"), dict) else {}
    return bool(execution.get("blocked")) or execution.get("accepted") is False


def agent_run_failed_action_signature(step: dict[str, Any]) -> str:
    execution = step.get("execution") if isinstance(step.get("execution"), dict) else {}
    path = execution.get("path") if isinstance(execution.get("path"), dict) else {}
    return json.dumps(
        {
            "decision": agent_run_step_signature_payload(step),
            "tool": agent_run_step_tool(step),
            "accepted": execution.get("accepted"),
            "blockedBy": execution.get("blockedBy") if isinstance(execution.get("blockedBy"), list) else [],
            "path": {
                "reachable": path.get("reachable"),
                "blockedBy": path.get("blockedBy") if isinstance(path.get("blockedBy"), list) else [],
            }
            if path
            else None,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def consecutive_stuck_movement_count(steps: list[dict[str, Any]]) -> int:
    if not steps or agent_run_step_tool(steps[-1]) != "tla_move_to_hex":
        return 0
    if not agent_run_step_movement_issued(steps[-1]):
        return 0

    current_hex = agent_run_step_chosen_hex_key(steps[-1])
    if not current_hex:
        return 0

    count = 0
    for step in reversed(steps):
        if agent_run_step_tool(step) != "tla_move_to_hex":
            break
        if not agent_run_step_movement_issued(step):
            break
        if agent_run_step_failed(step):
            break
        if agent_run_step_chosen_hex_key(step) != current_hex:
            break
        count += 1
    return count


def agent_run_step_movement_issued(step: dict[str, Any]) -> bool:
    execution = step.get("execution") if isinstance(step.get("execution"), dict) else {}
    return bool(execution.get("executed")) and execution.get("accepted") is not False


def agent_run_step_chosen_hex(step: dict[str, Any]) -> dict[str, Any] | None:
    state = step.get("state") if isinstance(step.get("state"), dict) else {}
    hex_value = state.get("chosenHex") if isinstance(state.get("chosenHex"), dict) else None
    return dict(hex_value) if hex_value is not None else None


def agent_run_step_chosen_hex_key(step: dict[str, Any]) -> str:
    hex_value = agent_run_step_chosen_hex(step)
    if hex_value is None:
        return ""
    return f"{hex_value.get('x')}:{hex_value.get('y')}"


def agent_run_step_target_hex(step: dict[str, Any]) -> dict[str, Any] | None:
    decision = step.get("decision") if isinstance(step.get("decision"), dict) else {}
    arguments = decision.get("arguments") if isinstance(decision.get("arguments"), dict) else {}
    if "x" not in arguments or "y" not in arguments:
        return None
    return {"x": arguments.get("x"), "y": arguments.get("y")}


def agent_run_tick_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in arguments.items() if key not in AGENT_RUN_META_ARGUMENTS or key in AGENT_RUN_DECISION_ARGUMENTS}


def execute_agent_run_decision(bridge: Any, key: str, decision: dict[str, Any], tick: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    tool_name = str(decision.get("suggestedTool") or "")
    if not tool_name:
        return {"executed": False, "blocked": False, "reason": "decision has no suggested tool"}

    blocked_by = agent_run_tool_blockers(tool_name, arguments)
    if blocked_by:
        return {"executed": False, "blocked": True, "tool": tool_name, "blockedBy": blocked_by}

    command_arguments = agent_run_command_arguments(tool_name, decision, arguments)
    if tool_name == "tla_say" and "text" not in command_arguments:
        if arguments.get("speechText") is not None:
            command_arguments["text"] = str(arguments.get("speechText", "")).strip()
        elif bool(arguments.get("autoReply", False)):
            command_arguments["text"] = auto_agent_reply_text(tick, decision)

    if tool_name == "tla_say" and not str(command_arguments.get("text", "")).strip():
        return {"executed": False, "blocked": True, "tool": tool_name, "blockedBy": ["speech requires text or autoReply=true"]}

    path_validation = agent_run_path_validation(bridge, tool_name, command_arguments, arguments)
    if isinstance(path_validation, dict) and path_validation.get("blocked"):
        remember_agent_run_failure(bridge, key, decision, tool_name, command_arguments, ", ".join(str(item) for item in path_validation.get("blockedBy", [])))
        if agent_run_soft_path_skip(decision):
            return {
                "executed": False,
                "blocked": False,
                "tool": tool_name,
                "arguments": command_arguments,
                "path": path_validation,
                "skipped": True,
                "reason": "path validation skipped unsafe low-priority movement",
            }
        return {"executed": False, "blocked": True, "tool": tool_name, "arguments": command_arguments, "path": path_validation, "blockedBy": path_validation.get("blockedBy", [])}

    try:
        response = execute_agent_run_tool(bridge, tool_name, command_arguments, arguments, agent_run_decision_in_combat(tick))
    except ValueError as exc:
        remember_agent_run_failure(bridge, key, decision, tool_name, command_arguments, str(exc))
        return {"executed": False, "blocked": True, "tool": tool_name, "arguments": command_arguments, "path": path_validation, "blockedBy": [str(exc)]}

    accepted = action_response_accepted(response)
    if not accepted:
        remember_agent_run_failure(bridge, key, decision, tool_name, command_arguments, "command rejected or completed with failure")

    # A building-entry door-open auto-approaches and toggles the door; wait for it to actually read
    # open before the next decision so the heuristic does not re-issue the open and toggle it shut.
    if accepted and str(decision.get("intent")) == "enter_building":
        door_settle_ms = int(arguments.get("enterBuildingForLootMs", 0) or 0)
        door_id = command_arguments.get("itemId")
        if door_settle_ms > 0 and door_id is not None:
            wait_for_door_open(bridge, door_id, door_settle_ms)

    compact = compact_action_response(response)
    execution = {
        "executed": True,
        "blocked": False,
        "tool": tool_name,
        "arguments": command_arguments,
        "accepted": accepted,
        "response": compact,
    }
    if path_validation is not None:
        execution["path"] = path_validation
    return execution


def agent_run_tool_blockers(tool_name: str, arguments: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if agent_run_forbidden_tool(tool_name):
        blockers.append("admin/hidden/generated surfaces are forbidden for autonomous execution")
    if tool_name not in typed_command_tool_names():
        blockers.append("suggested tool is not a typed command tool")

    allowed_tools = normalize_string_list(arguments.get("allowedTools"))
    if allowed_tools and tool_name not in allowed_tools:
        blockers.append("tool is not in allowedTools")

    blocked_tools = set(normalize_string_list(arguments.get("blockedTools")))
    if tool_name in blocked_tools:
        blockers.append("tool is listed in blockedTools")

    if tool_name in AGENT_RUN_RAW_TOOLS and not bool(arguments.get("allowRawInput", False)):
        blockers.append("raw input is disabled")
    if tool_name in AGENT_RUN_COMBAT_TOOLS and not bool(arguments.get("allowCombat", False)):
        blockers.append("combat actions are disabled")
    if tool_name in AGENT_RUN_DESTRUCTIVE_TOOLS and not bool(arguments.get("allowRosterDelete", False)):
        blockers.append("destructive roster actions are disabled")
    if tool_name == "tla_say" and not bool(arguments.get("allowSpeech", True)):
        blockers.append("visible speech is disabled")
    return blockers


def agent_run_soft_path_skip(decision: dict[str, Any]) -> bool:
    priority = str(decision.get("priority") or "").lower()
    intent = str(decision.get("intent") or "")
    return priority == "low" and intent in {"move_to_hex", "explore", "explore_unknown"}


def agent_run_forbidden_tool(tool_name: str) -> bool:
    if tool_name in AGENT_RUN_FORBIDDEN_TOOLS:
        return True
    return any(tool_name.startswith(prefix) for prefix in AGENT_RUN_FORBIDDEN_PREFIXES)


def agent_run_command_arguments(tool_name: str, decision: dict[str, Any], run_arguments: dict[str, Any]) -> dict[str, Any]:
    command_arguments = dict(decision.get("arguments", {})) if isinstance(decision.get("arguments"), dict) else {}
    command_arguments.setdefault("waitForCompletion", True)
    command_arguments.setdefault("timeoutMs", int(run_arguments.get("commandTimeoutMs", run_arguments.get("timeoutMs", 15000))))
    command_arguments.setdefault("pollIntervalMs", int(run_arguments.get("pollIntervalMs", 100)))
    if bool(run_arguments.get("syncAfterAction", True)):
        command_arguments.setdefault("syncAfterCompletion", True)
        command_arguments.setdefault("includeObservation", True)
    if tool_name == "tla_say":
        command_arguments.setdefault("sayType", "normal")
    return command_arguments


def agent_run_path_validation(bridge: Any, tool_name: str, command_arguments: dict[str, Any], run_arguments: dict[str, Any]) -> dict[str, Any] | None:
    if tool_name != "tla_move_to_hex" or not bool(run_arguments.get("validatePath", True)):
        return None

    if "x" not in command_arguments or "y" not in command_arguments:
        return {"blocked": True, "blockedBy": ["movement decision has no target hex"]}

    query_arguments = {
        "toX": int(command_arguments["x"]),
        "toY": int(command_arguments["y"]),
        "cut": int(run_arguments.get("pathCut", command_arguments.get("cut", 0))),
        "timeoutMs": int(run_arguments.get("pathTimeoutMs", 5000)),
        "pollIntervalMs": int(run_arguments.get("pollIntervalMs", 100)),
    }
    response = environment_query(bridge, "path", query_arguments)
    result = response.get("result") if isinstance(response.get("result"), dict) else {}
    path_result = result.get("result") if isinstance(result.get("result"), dict) else {}
    validation = {
        "completed": bool(result.get("completed")),
        "timedOut": bool(result.get("timedOut")),
        "reachable": path_result.get("reachable"),
        "pathLength": path_result.get("pathLength"),
        "directDistance": path_result.get("directDistance"),
        "fromMovable": path_result.get("fromMovable"),
        "toMovable": path_result.get("toMovable"),
        "queryId": result.get("queryId"),
        "blocked": False,
        "blockedBy": [],
    }
    blocked_by: list[str] = []
    if not validation["completed"]:
        blocked_by.append("path validation did not complete")
    if path_result.get("reachable") is False:
        blocked_by.append("path unreachable")
    if path_result.get("toMovable") is False:
        blocked_by.append("target hex is not movable")
    validation["blockedBy"] = blocked_by
    validation["blocked"] = bool(blocked_by)
    return validation


def dialog_state_signature(dialog: dict[str, Any]) -> tuple[str, tuple[str, ...]] | None:
    if not isinstance(dialog, dict) or not dialog.get("active"):
        return None
    answers = dialog.get("answers") if isinstance(dialog.get("answers"), list) else []
    return (
        normalize_dialog_text(dialog.get("text")),
        tuple(normalize_dialog_text(answer.get("text")) for answer in answers if isinstance(answer, dict)),
    )


def wait_for_dialog_transition(bridge: Any, prev_signature: tuple[str, tuple[str, ...]] | None, settle_ms: int, poll_ms: int = 120) -> None:
    """Block until the active dialog actually advances to a new line (or closes), bounded by settle_ms.

    Dialog answers are dispatched async: the next observation can still show the line we just
    answered, so a fire-and-forget planner re-answers the stale line and spins. Waiting for the
    client-visible dialog state to change before the next decision makes the agent take exactly
    one answer per line and walk a multi-line conversation to completion.
    """
    deadline = unix_ms() + max(0, int(settle_ms))
    while unix_ms() < deadline:
        time.sleep(min(max(poll_ms, 1), 250) / 1000.0)
        observation = observe_for_agent_run_memory(bridge)
        dialog = observation.get("dialog") if isinstance(observation.get("dialog"), dict) else {}
        if not dialog.get("active"):
            return
        if dialog_state_signature(dialog) != prev_signature:
            return


def agent_run_decision_in_combat(tick: dict[str, Any]) -> bool:
    if not isinstance(tick, dict):
        return False
    step = tick.get("step") if isinstance(tick.get("step"), dict) else {}
    observation = unwrap_observation_payload(step.get("observation")) if isinstance(step.get("observation"), dict) else {}
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    return bool(chosen.get("inCombat"))


def wait_for_move_settle(bridge: Any, settle_ms: int, poll_ms: int = 150) -> None:
    """Block until an issued local move arrives/stops (or combat starts), bounded by settle_ms.

    Movement is async too: a fire-and-forget planner re-observes mid-walk, sees it is still
    moving, and spends the run's step budget on `idle_moving` waits, so a single 20-step window
    never reaches the destination. Waiting for the chosen hex to stop changing (arrival or a
    blocked path) before the next decision lets the agent actually get somewhere. Returns
    immediately if the chosen enters combat so the agent reacts to a fight instead of finishing
    the walk, or if the chosen snapshot disappears (map transition) so the next decision re-reads.
    """
    deadline = unix_ms() + max(0, int(settle_ms))
    last_xy: tuple[int, int] | None = None
    stable_polls = 0
    while unix_ms() < deadline:
        time.sleep(min(max(poll_ms, 1), 250) / 1000.0)
        observation = observe_for_agent_run_memory(bridge)
        chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
        if not chosen:
            return
        if bool(chosen.get("inCombat")):
            return
        xy = safe_hex_value_xy(chosen.get("hex"))
        if xy is not None and xy == last_xy:
            stable_polls += 1
            if stable_polls >= 2:
                return
        else:
            stable_polls = 0
            last_xy = xy


def wait_for_door_open(bridge: Any, door_id: Any, settle_ms: int, poll_ms: int = 150) -> None:
    """Block until a just-opened door reports opened (or leaves view), bounded by settle_ms.

    Opening a door (tla_pick_item) is async like dialog/movement: the next observation can still
    show it closed, and re-issuing the open toggles it shut again — endless churn. Waiting for the
    door's opened state to flip before the next decision lets the building-entry behavior open the
    door once and then route through it.
    """
    deadline = unix_ms() + max(0, int(settle_ms))
    while unix_ms() < deadline:
        time.sleep(min(max(poll_ms, 1), 250) / 1000.0)
        observation = observe_for_agent_run_memory(bridge)
        door = None
        for item in observation.get("mapItems", []) if isinstance(observation.get("mapItems"), list) else []:
            if isinstance(item, dict) and item.get("id") == door_id:
                door = item
                break
        if door is None or door.get("opened") is True:
            return


def execute_agent_run_tool(bridge: Any, tool_name: str, command_arguments: dict[str, Any], run_arguments: dict[str, Any] | None = None, in_combat: bool = False) -> dict[str, Any]:
    run_arguments = run_arguments if isinstance(run_arguments, dict) else {}
    if tool_name == "tla_dialog_answer":
        observation = observe_for_agent_run_memory(bridge)
        prev_signature = dialog_state_signature(observation.get("dialog") if isinstance(observation.get("dialog"), dict) else {})
        response = act_with_optional_wait(bridge, typed_command_payload("tla_dialog_answer", command_arguments), command_arguments)
        key = agent_profile_key(bridge)
        remember_dialog_choice(agent_memory_for_key(bridge, key), observation, command_arguments.get("answerIndex"), unix_ms(), response)
        dialog_settle_ms = int(run_arguments.get("dialogSettleMs", 0) or 0)
        if dialog_settle_ms > 0 and action_response_accepted(response):
            wait_for_dialog_transition(bridge, prev_signature, dialog_settle_ms)
        return response
    if tool_name == "tla_move_to_hex":
        response = act_with_optional_wait(bridge, typed_command_payload("tla_move_to_hex", command_arguments), command_arguments)
        move_settle_ms = int(run_arguments.get("moveSettleMs", 0) or 0)
        # Only settle navigation moves. A combat reposition is a micro-step the agent re-decides
        # immediately, and settling it would add a slow in-combat observe per reposition for no
        # benefit, so skip it when the chosen was already in combat at decision time.
        if move_settle_ms > 0 and not in_combat and action_response_accepted(response):
            wait_for_move_settle(bridge, move_settle_ms)
        return response
    if tool_name == "tla_global_move_to":
        observation = observe_for_agent_run_memory(bridge)
        response = act_with_optional_wait(bridge, typed_command_payload("tla_global_move_to", command_arguments), command_arguments)
        key = agent_profile_key(bridge)
        memory = agent_memory_for_key(bridge, key)
        now = unix_ms()
        remember_global_map_state(memory, observation, now, "before_global_move")
        remember_map_transition_state(memory, observation, now, "before_global_move")
        remember_global_move_attempt(memory, observation, command_arguments, now, response)
        return response
    if tool_name == "tla_global_enter_interest":
        observation = observe_for_agent_run_memory(bridge)
        response = act_with_optional_wait(bridge, typed_command_payload("tla_global_enter_interest", command_arguments), command_arguments)
        key = agent_profile_key(bridge)
        memory = agent_memory_for_key(bridge, key)
        now = unix_ms()
        remember_global_map_state(memory, observation, now, "before_global_enter")
        remember_map_transition_state(memory, observation, now, "before_global_enter")
        remember_global_enter_attempt(memory, observation, command_arguments, now, response)
        return response
    return act_with_optional_wait(bridge, typed_command_payload(tool_name, command_arguments), command_arguments)


def observe_for_agent_run_memory(bridge: Any) -> dict[str, Any]:
    observe_response = bridge.request("observe")
    if "error" in observe_response:
        return {}
    observation_payload = observe_response.get("result", observe_response)
    return unwrap_observation_payload(observation_payload)


def auto_agent_reply_text(tick: dict[str, Any], decision: dict[str, Any]) -> str:
    profile = tick.get("profile") if isinstance(tick.get("profile"), dict) else {}
    role = str(profile.get("role", "")).casefold()
    language = str(profile.get("language", "russ")).casefold()
    if language.startswith("eng"):
        if "guard" in role:
            return "Understood. I will stay close."
        if "trader" in role:
            return "Understood. We can talk trade."
        if "helper" in role:
            return "Understood. I can help."
        return "Understood."
    if "guard" in role or "охран" in role:
        return "Принял. Держусь рядом."
    if "trader" in role or "торгов" in role:
        return "Понял, можем обсудить обмен."
    if "helper" in role or "помощ" in role:
        return "Понял, помогу."
    speech = decision.get("speech") if isinstance(decision.get("speech"), dict) else {}
    intent = str(speech.get("intent", ""))
    if intent == "greeting":
        return "Привет."
    return "Понял."


def compact_action_response(response: dict[str, Any]) -> dict[str, Any]:
    result = response.get("result") if isinstance(response.get("result"), dict) else response
    if not isinstance(result, dict):
        return {"raw": result}
    compact: dict[str, Any] = {
        "success": result.get("success"),
        "accepted": result.get("accepted"),
        "message": result.get("message"),
        "commandSeq": result.get("commandSeq"),
    }
    completion = result.get("completion") if isinstance(result.get("completion"), dict) else {}
    if completion:
        event = completion.get("event") if isinstance(completion.get("event"), dict) else {}
        compact["completion"] = {
            "completed": completion.get("completed"),
            "timedOut": completion.get("timedOut"),
            "message": event.get("message"),
            "success": event.get("success"),
            "type": event.get("type"),
        }
    if isinstance(result.get("sync"), dict):
        compact["sync"] = {"included": True}
    return {key: value for key, value in compact.items() if value is not None}


def remember_agent_run_failure(bridge: Any, key: str, decision: dict[str, Any], tool_name: str, command_arguments: dict[str, Any], message: str) -> None:
    memory = agent_memory_for_key(bridge, key)
    failed = ensure_memory_list(memory, "failedActions")
    append_bounded(
        failed,
        {
            "time": unix_ms(),
            "decisionId": decision.get("decisionId"),
            "intent": decision.get("intent"),
            "tool": tool_name,
            "arguments": command_arguments,
            "message": message,
        },
        100,
    )


def update_agent_memory_from_step(bridge: Any, memory: dict[str, Any], step_result: dict[str, Any], now: int) -> None:
    events_payload = step_result.get("events") if isinstance(step_result.get("events"), dict) else {}
    observation_payload = step_result.get("observation")
    observation = unwrap_observation_payload(observation_payload) if isinstance(observation_payload, dict) else {}
    memory["lastStepAt"] = now
    memory["lastObservation"] = compact_observation_summary(observation)

    events = events_payload.get("events") if isinstance(events_payload, dict) else []
    if isinstance(events, list):
        for entry in events:
            if isinstance(entry, dict):
                compact = compact_event_entry(entry)
                append_bounded(memory["recentEvents"], compact, 100)
                event = entry.get("event") if isinstance(entry.get("event"), dict) else {}
                event_type = str(event.get("type", ""))
                if event_type == "say_received":
                    speaker_id = event.get("speakerId")
                    if speaker_id is not None:
                        remember_known_person(
                            memory,
                            str(speaker_id),
                            {
                                "id": speaker_id,
                                "name": event.get("speakerName", ""),
                                "protoId": event.get("speakerProtoId", ""),
                                "lastHex": event.get("speakerHex"),
                                "lastSpeech": event.get("text", ""),
                                "lastSeenAt": now,
                            },
                        )
                elif event_type == "dialog_updated":
                    dialog = event.get("dialog") if isinstance(event.get("dialog"), dict) else {}
                    remember_dialog_snapshot(memory, dialog, now, "event")
                    remember_task_hints_from_dialog(memory, dialog, now, "dialog_event")
                elif event_type == "dialog_closed":
                    remember_dialog_closed(memory, event.get("dialogId"), now)
                remember_episode_from_event(memory, event, event_type, now)

    dialog = observation.get("dialog") if isinstance(observation.get("dialog"), dict) else {}
    if dialog.get("active"):
        remember_dialog_snapshot(memory, dialog, now, "observation")
        remember_task_hints_from_dialog(memory, dialog, now, "dialog_observation")

    for critter in observation.get("critters", []) if isinstance(observation.get("critters"), list) else []:
        if isinstance(critter, dict) and critter.get("id") is not None:
            remember_known_person(
                memory,
                str(critter["id"]),
                {
                    "id": critter.get("id"),
                    "name": critter.get("name", ""),
                    "protoId": critter.get("protoId", ""),
                    "lastHex": critter.get("hex"),
                    "controlledByPlayer": bool(critter.get("controlledByPlayer")),
                    "alive": bool(critter.get("alive", True)),
                    "lastSeenAt": now,
                },
            )

    for item in observation.get("inventory", []) if isinstance(observation.get("inventory"), list) else []:
        if isinstance(item, dict):
            remember_useful_item(memory, item, now, "inventory")
    for item in observation.get("mapItems", []) if isinstance(observation.get("mapItems"), list) else []:
        if isinstance(item, dict) and (item.get("canPickUp") is not False or item.get("canUse")):
            remember_useful_item(memory, item, now, "map")

    map_state = observation.get("map") if isinstance(observation.get("map"), dict) else {}
    if map_state:
        map_id = str(map_state.get("protoId") or map_state.get("id") or map_state.get("name") or "current_map")
        remember_known_place(memory, map_id, {"id": map_state.get("id"), "protoId": map_state.get("protoId"), "name": map_state.get("name", ""), "lastSeenAt": now})
        chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
        chosen_hex = chosen.get("hex") if isinstance(chosen.get("hex"), dict) else None
        if chosen_hex is not None:
            remember_local_map_position(memory, map_id, chosen_hex, now, chosen)

    global_map = observation.get("globalMap") if isinstance(observation.get("globalMap"), dict) else {}
    if global_map.get("active"):
        remember_known_place(memory, "global_map", {"lastPos": global_map.get("pos"), "targetPos": global_map.get("targetPos"), "lastSeenAt": now})
        remember_global_map_state(memory, observation, now, "step")
    remember_map_transition_state(memory, observation, now, "step")


def remember_episode_from_event(memory: dict[str, Any], event: dict[str, Any], event_type: str, now: int) -> None:
    if event_type in {"critter_action", "critter_action_ex"}:
        critter = event.get("critter") if isinstance(event.get("critter"), dict) else {}
        entry = {
            "time": now,
            "type": event_type,
            "action": event.get("action"),
            "actionData": event.get("actionData"),
            "critter": {"id": critter.get("id"), "protoId": critter.get("protoId"), "name": critter.get("name"), "hex": critter.get("hex"), "isChosen": critter.get("isChosen")},
        }
        append_bounded(memory["combatEncounters"], entry, 100)
        if isinstance(critter.get("hex"), dict):
            remember_known_hazard(memory, "combat:" + memory_hex_key(critter.get("hex")), "combat activity observed", critter.get("hex"), now, {"eventType": event_type, "action": event.get("action")})
        return

    if event_type == "receive_items":
        collection = {"active": True, "time": now, "updatedAt": now, "type": event_type, "count": event.get("count"), "context": event.get("context"), "source": "receive_items"}
        memory["activeCollection"] = collection
        append_bounded(memory["lootContainers"], collection, 100)
        append_bounded(memory["interactions"], {"time": now, "kind": "container_open", "count": event.get("count"), "context": event.get("context")}, 150)
        return

    if event_type in {"item_map_in", "item_map_out", "item_inv_in", "item_inv_out", "chosen_look_on_item", "barter_item", "roster_action_result"}:
        append_bounded(memory["interactions"], {"time": now, "kind": event_type, "event": compact_event_payload_for_memory(event)}, 150)
        return

    if event_type == "command_completed" and event.get("success") is False:
        entry = {"time": now, "kind": "command_failed", "message": event.get("message"), "commandSeq": event.get("commandSeq"), "retryAfterMs": 10_000}
        append_bounded(memory["doNotRetry"], entry, 100)
        append_bounded(memory["failedActions"], {"time": now, "text": str(event.get("message") or "command failed"), "source": "command_completed", "properties": entry}, 200)
        return

    if event_type == "environment_query_result" and event.get("success") is False:
        entry = {"time": now, "kind": "environment_query_failed", "query": event.get("query"), "message": event.get("message"), "retryAfterMs": 10_000}
        append_bounded(memory["doNotRetry"], entry, 100)


def remember_local_map_position(memory: dict[str, Any], map_id: str, chosen_hex: dict[str, Any], now: int, chosen: dict[str, Any]) -> None:
    x, y = safe_hex_value_xy(chosen_hex)
    if x is None or y is None:
        return
    hex_payload = {"x": x, "y": y}
    entry = {"time": now, "map": map_id, "hex": hex_payload}
    append_bounded(memory["visited"], entry, 200)
    append_unique_bounded(memory["recentPath"], entry, 50, ("map", "hex"))

    areas = memory.get("visitedAreas")
    if not isinstance(areas, dict):
        areas = {}
        memory["visitedAreas"] = areas
    area_key = f"{map_id}:{x // 10}:{y // 10}"
    area = dict(areas.get(area_key, {})) if isinstance(areas.get(area_key), dict) else {}
    area["key"] = area_key
    area["map"] = map_id
    area["cluster"] = {"x": x // 10, "y": y // 10}
    area["lastHex"] = hex_payload
    area["lastSeenAt"] = now
    area["visits"] = int(area.get("visits", 0)) + 1
    areas[area_key] = area
    evict_oldest_dict_bounded(areas, area_key, 500)

    if chosen.get("inCombat"):
        remember_known_hazard(memory, "combat:" + memory_hex_key(hex_payload), "chosen was in combat here", hex_payload, now, {"map": map_id})


def remember_known_hazard(memory: dict[str, Any], key: str, reason: str, hex_value: Any, now: int, properties: dict[str, Any] | None = None) -> None:
    hazards = memory.get("knownHazards")
    if not isinstance(hazards, dict):
        hazards = {}
        memory["knownHazards"] = hazards
    entry = dict(hazards.get(key, {})) if isinstance(hazards.get(key), dict) else {}
    entry.update(properties or {})
    entry["key"] = key
    entry["reason"] = reason
    entry["hex"] = hex_value
    entry["lastSeenAt"] = now
    entry["count"] = int(entry.get("count", 0)) + 1
    hazards[key] = entry
    evict_oldest_dict_bounded(hazards, key, 500)


def compact_event_payload_for_memory(event: dict[str, Any]) -> dict[str, Any]:
    result = {"type": event.get("type")}
    for key in ("id", "itemId", "count", "context", "action", "rosterIndex", "accepted", "message"):
        if key in event:
            result[key] = event.get(key)
    if isinstance(event.get("item"), dict):
        item = event["item"]
        result["item"] = {"id": item.get("id"), "protoId": item.get("protoId"), "count": item.get("count"), "hex": item.get("hex")}
    return result


def memory_hex_key(hex_value: Any) -> str:
    x, y = safe_hex_value_xy(hex_value)
    return f"{x}:{y}" if x is not None and y is not None else "unknown"


def remember_useful_item(memory: dict[str, Any], item: dict[str, Any], now: int, source: str) -> None:
    proto_id = str(item.get("protoId") or item.get("id") or "").strip()
    if not proto_id:
        return
    useful = item.get("canUse") is not False or item.get("canPickUp") is not False or source == "inventory"
    if not useful:
        return
    items = memory.get("usefulItems")
    if not isinstance(items, dict):
        items = {}
        memory["usefulItems"] = items
    entry = dict(items.get(proto_id, {})) if isinstance(items.get(proto_id), dict) else {}
    entry.update(
        {
            "key": proto_id,
            "protoId": item.get("protoId"),
            "lastItemId": item.get("id"),
            "count": item.get("count"),
            "slot": item.get("slot"),
            "hex": item.get("hex"),
            "canUse": item.get("canUse"),
            "canPickUp": item.get("canPickUp"),
            "source": source,
            "lastSeenAt": now,
            "seenCount": int(entry.get("seenCount", 0)) + 1,
        }
    )
    items[proto_id] = entry


def remember_known_person(memory: dict[str, Any], key: str, data: dict[str, Any]) -> None:
    people = memory.get("people")
    if not isinstance(people, dict):
        people = {}
        memory["people"] = people
    entry = dict(people.get(key, {})) if isinstance(people.get(key), dict) else {}
    entry.update({k: v for k, v in data.items() if v is not None})
    entry["key"] = key
    people[key] = entry
    evict_oldest_dict_bounded(people, key, 500)


def remember_known_place(memory: dict[str, Any], key: str, data: dict[str, Any]) -> None:
    places = memory.get("places")
    if not isinstance(places, dict):
        places = {}
        memory["places"] = places
    entry = dict(places.get(key, {})) if isinstance(places.get(key), dict) else {}
    entry.update({k: v for k, v in data.items() if v is not None})
    entry["key"] = key
    places[key] = entry
    evict_oldest_dict_bounded(places, key, 500)


def global_pos_signature(pos: Any) -> str:
    if isinstance(pos, dict):
        return f"{get_hex_value(pos, 'x')}:{get_hex_value(pos, 'y')}"
    return str(pos or "")


def global_interest_memory_key(interest: dict[str, Any]) -> str:
    interest_type = str(interest.get("type") or interest.get("typeEnum") or "unknown")
    interest_id = interest.get("id")
    if interest_id is not None and str(interest_id) != "":
        return f"global:{interest_type}:{interest_id}"
    pos = interest.get("pos") if isinstance(interest.get("pos"), dict) else None
    if pos is not None:
        return f"global:{interest_type}:pos:{global_pos_signature(pos)}"
    return f"global:{interest_type}:unknown"


def ensure_memory_list(memory: dict[str, Any], field: str) -> list[Any]:
    entries = memory.get(field)
    if not isinstance(entries, list):
        entries = []
        memory[field] = entries
    return entries


def ensure_memory_dict(memory: dict[str, Any], field: str) -> dict[str, Any]:
    entries = memory.get(field)
    if not isinstance(entries, dict):
        entries = {}
        memory[field] = entries
    return entries


def route_history_signature(entry: dict[str, Any]) -> tuple[str, str, str, str, str, str]:
    return (
        str(entry.get("action", "")),
        global_pos_signature(entry.get("fromPos") if "fromPos" in entry else entry.get("pos")),
        global_pos_signature(entry.get("targetPos")),
        str(entry.get("isMoving", entry.get("wasMoving", ""))),
        str(entry.get("interestKey", "")),
        str(entry.get("accepted", "")),
    )


def append_route_history(memory: dict[str, Any], entry: dict[str, Any], limit: int = 200) -> None:
    history = ensure_memory_list(memory, "travelHistory")
    if history:
        last = history[-1]
        if isinstance(last, dict) and route_history_signature(last) == route_history_signature(entry):
            last["updatedAt"] = entry.get("time")
            return
    append_bounded(history, entry, limit)


def map_transition_signature(entry: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(entry.get("mode", "")),
        str(entry.get("mapId", "")),
        str(entry.get("mapProtoId", "")),
        global_pos_signature(entry.get("globalPos")),
    )


def append_map_transition(memory: dict[str, Any], entry: dict[str, Any], limit: int = 200) -> None:
    transitions = ensure_memory_list(memory, "mapTransitions")
    if transitions:
        last = transitions[-1]
        if isinstance(last, dict) and map_transition_signature(last) == map_transition_signature(entry):
            last["updatedAt"] = entry.get("time")
            return
    append_bounded(transitions, entry, limit)


def remember_global_interest(memory: dict[str, Any], interest: dict[str, Any], now: int, source: str) -> str:
    interests = ensure_memory_dict(memory, "globalInterests")
    key = global_interest_memory_key(interest)
    entry = dict(interests.get(key, {})) if isinstance(interests.get(key), dict) else {}
    entry.update(
        {
            "key": key,
            "type": interest.get("type"),
            "typeEnum": interest.get("typeEnum"),
            "id": interest.get("id"),
            "pos": interest.get("pos"),
            "radius": interest.get("radius"),
            "distance": interest.get("distance"),
            "enterable": interest.get("enterable"),
            "inRange": interest.get("inRange"),
            "enterArguments": interest.get("enterArguments"),
            "firstSeenAt": entry.get("firstSeenAt", now),
            "lastSeenAt": now,
            "lastSource": source,
            "seenCount": int(entry.get("seenCount") or 0) + 1,
        }
    )
    interests[key] = {field: value for field, value in entry.items() if value is not None}
    evict_oldest_dict_bounded(interests, key, 500)

    if isinstance(interest.get("pos"), dict):
        remember_known_place(
            memory,
            f"global_interest:{key}",
            {
                "id": interest.get("id"),
                "type": interest.get("type"),
                "pos": interest.get("pos"),
                "enterable": interest.get("enterable"),
                "lastSeenAt": now,
            },
        )
    return key


def remember_global_map_state(memory: dict[str, Any], observation: dict[str, Any], now: int, source: str) -> None:
    global_map = observation.get("globalMap") if isinstance(observation.get("globalMap"), dict) else {}
    if not global_map.get("active"):
        return

    remember_known_place(
        memory,
        "global_map",
        {
            "lastPos": global_map.get("pos"),
            "targetPos": global_map.get("targetPos"),
            "tripId": global_map.get("tripId"),
            "lastSeenAt": now,
        },
    )
    for interest in global_map.get("interests", []) if isinstance(global_map.get("interests"), list) else []:
        if isinstance(interest, dict):
            remember_global_interest(memory, interest, now, source)

    append_route_history(
        memory,
        {
            "time": now,
            "source": source,
            "action": "observe",
            "tripId": global_map.get("tripId"),
            "pos": global_map.get("pos"),
            "targetPos": global_map.get("targetPos"),
            "isMoving": bool(global_map.get("isMoving")),
            "interestCount": len(global_map.get("interests", [])) if isinstance(global_map.get("interests"), list) else 0,
        },
    )


def remember_map_transition_state(memory: dict[str, Any], observation: dict[str, Any], now: int, source: str) -> None:
    global_map = observation.get("globalMap") if isinstance(observation.get("globalMap"), dict) else {}
    if global_map.get("active"):
        append_map_transition(
            memory,
            {
                "time": now,
                "source": source,
                "mode": "global",
                "globalPos": global_map.get("pos"),
                "targetPos": global_map.get("targetPos"),
                "tripId": global_map.get("tripId"),
            },
        )
        return

    map_state = observation.get("map") if isinstance(observation.get("map"), dict) else {}
    if map_state:
        append_map_transition(
            memory,
            {
                "time": now,
                "source": source,
                "mode": "map",
                "mapId": map_state.get("id"),
                "mapProtoId": map_state.get("protoId"),
                "mapName": map_state.get("name"),
            },
        )


def find_observed_global_interest(global_map: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any] | None:
    interests = global_map.get("interests") if isinstance(global_map.get("interests"), list) else []
    wanted_id = str(arguments.get("interestId", ""))
    wanted_type = str(arguments.get("interestType", ""))
    for interest in interests:
        if not isinstance(interest, dict):
            continue
        if wanted_id and str(interest.get("id")) != wanted_id:
            continue
        if wanted_type and str(interest.get("type")) != wanted_type and str(interest.get("typeEnum")) != wanted_type:
            continue
        return interest
    return None


def remember_global_move_attempt(memory: dict[str, Any], observation: dict[str, Any], arguments: dict[str, Any], now: int, response: dict[str, Any]) -> None:
    global_map = observation.get("globalMap") if isinstance(observation.get("globalMap"), dict) else {}
    append_route_history(
        memory,
        {
            "time": now,
            "source": "command",
            "action": "move",
            "fromPos": global_map.get("pos"),
            "targetPos": {"x": int(arguments.get("x", 0)), "y": int(arguments.get("y", 0))},
            "wasMoving": global_map.get("isMoving"),
            "accepted": action_response_accepted(response),
        },
    )


def remember_global_enter_attempt(memory: dict[str, Any], observation: dict[str, Any], arguments: dict[str, Any], now: int, response: dict[str, Any]) -> None:
    global_map = observation.get("globalMap") if isinstance(observation.get("globalMap"), dict) else {}
    interest = find_observed_global_interest(global_map, arguments)
    interest_key = remember_global_interest(memory, interest, now, "enter_command") if isinstance(interest, dict) else ""
    accepted = action_response_accepted(response)
    append_route_history(
        memory,
        {
            "time": now,
            "source": "command",
            "action": "enter",
            "fromPos": global_map.get("pos"),
            "interestKey": interest_key,
            "interestType": arguments.get("interestType"),
            "interestId": arguments.get("interestId"),
            "enterable": interest.get("enterable") if isinstance(interest, dict) else None,
            "inRange": interest.get("inRange") if isinstance(interest, dict) else None,
            "accepted": accepted,
        },
    )

    if interest_key:
        interests = ensure_memory_dict(memory, "globalInterests")
        entry = interests.get(interest_key)
        if isinstance(entry, dict):
            entry["lastEnterAttempt"] = {"time": now, "accepted": accepted}


def dialog_memory_key(dialog: dict[str, Any]) -> str:
    dialog_id = str(dialog.get("dialogId", "")).strip()
    if dialog_id:
        return f"dialog:{dialog_id}"
    talker_id = dialog.get("talkerId")
    if talker_id is not None:
        return f"talker:{talker_id}"
    return "dialog:active"


def dialog_answer_memory_entries(dialog: dict[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    answers = dialog.get("answers") if isinstance(dialog.get("answers"), list) else []
    for answer in answers:
        if not isinstance(answer, dict):
            continue
        text = str(answer.get("text", ""))
        intent, reasons, score = dialog_answer_intent(text)
        entries.append(
            {
                "index": answer.get("index"),
                "text": text,
                "intent": intent,
                "score": score,
                "reasons": reasons,
            }
        )
    return entries


def remember_dialog_snapshot(memory: dict[str, Any], dialog: dict[str, Any], now: int, source: str) -> None:
    if not isinstance(dialog, dict) or not dialog.get("active"):
        return
    dialogs = memory.get("dialogs")
    if not isinstance(dialogs, dict):
        dialogs = {}
        memory["dialogs"] = dialogs
    key = dialog_memory_key(dialog)
    entry = dict(dialogs.get(key, {})) if isinstance(dialogs.get(key), dict) else {}
    entry.update(
        {
            "key": key,
            "dialogId": dialog.get("dialogId"),
            "talkerId": dialog.get("talkerId"),
            "text": dialog.get("text"),
            "answers": dialog_answer_memory_entries(dialog),
            "durationMs": dialog.get("durationMs"),
            "active": True,
            "lastSeenAt": now,
            "lastSource": source,
            "seenCount": int(entry.get("seenCount") or 0) + 1,
        }
    )
    dialogs[key] = entry
    evict_oldest_dict_bounded(dialogs, key, 300)


def remember_dialog_closed(memory: dict[str, Any], dialog_id: Any, now: int) -> None:
    dialog_id_text = str(dialog_id or "").strip()
    if not dialog_id_text:
        return
    dialogs = memory.get("dialogs")
    if not isinstance(dialogs, dict):
        return
    key = f"dialog:{dialog_id_text}"
    entry = dialogs.get(key)
    if isinstance(entry, dict):
        entry["active"] = False
        entry["lastClosedAt"] = now


def remember_task_hints_from_dialog(memory: dict[str, Any], dialog: dict[str, Any], now: int, source: str) -> None:
    hints = memory.get("taskHints")
    if not isinstance(hints, list):
        hints = []
        memory["taskHints"] = hints
    key = dialog_memory_key(dialog)
    for answer in dialog_answer_memory_entries(dialog):
        if answer.get("intent") not in {"accept", "question", "trade", "healing"}:
            continue
        hint = {
            "time": now,
            "source": source,
            "dialogKey": key,
            "dialogId": dialog.get("dialogId"),
            "talkerId": dialog.get("talkerId"),
            "intent": answer.get("intent"),
            "text": answer.get("text"),
            "arguments": {"answerIndex": answer.get("index")},
        }
        append_unique_bounded(hints, hint, 200, ("dialogKey", "intent", "text"))


def remember_task_hints_from_options(memory: dict[str, Any], task_options: dict[str, Any], now: int, source: str) -> None:
    hints = memory.get("taskHints")
    if not isinstance(hints, list):
        hints = []
        memory["taskHints"] = hints
    options = task_options.get("options") if isinstance(task_options.get("options"), list) else []
    for option in options:
        if not isinstance(option, dict):
            continue
        kind = str(option.get("kind", ""))
        if kind not in {"account_gate", "generation_gate", "dialog", "global_travel", "talk_to"}:
            continue
        hint = {
            "time": now,
            "source": source,
            "kind": kind,
            "reason": option.get("reason"),
            "tool": option.get("tool"),
            "arguments": option.get("arguments", {}),
        }
        dialog = option.get("dialog") if isinstance(option.get("dialog"), dict) else {}
        if dialog:
            hint["dialogId"] = dialog.get("dialogId")
            hint["text"] = dialog.get("text")
        append_unique_bounded(hints, hint, 200, ("kind", "tool", "reason", "dialogId"))


def remember_dialog_choice(memory: dict[str, Any], observation: dict[str, Any], answer_index: Any, now: int, response: dict[str, Any]) -> None:
    dialog = observation.get("dialog") if isinstance(observation.get("dialog"), dict) else {}
    answer_text = ""
    intent = "unknown"
    score = 0
    answers = dialog.get("answers") if isinstance(dialog.get("answers"), list) else []
    for answer in answers:
        if not isinstance(answer, dict) or str(answer.get("index")) != str(answer_index):
            continue
        answer_text = str(answer.get("text", ""))
        intent, _reasons, score = dialog_answer_intent(answer_text)
        break

    choices = memory.get("dialogChoices")
    if not isinstance(choices, list):
        choices = []
        memory["dialogChoices"] = choices
    choice = {
        "time": now,
        "dialogKey": dialog_memory_key(dialog) if isinstance(dialog, dict) else "dialog:unknown",
        "dialogId": dialog.get("dialogId") if isinstance(dialog, dict) else None,
        "talkerId": dialog.get("talkerId") if isinstance(dialog, dict) else None,
        "speechText": dialog.get("text") if isinstance(dialog, dict) else None,
        "answerIndex": answer_index,
        "text": answer_text,
        "intent": intent,
        "score": score,
        "accepted": action_response_accepted(response),
    }
    append_bounded(choices, choice, 200)
    if isinstance(dialog, dict) and dialog.get("active"):
        remember_dialog_snapshot(memory, dialog, now, "choice")
        dialogs = memory.get("dialogs") if isinstance(memory.get("dialogs"), dict) else {}
        entry = dialogs.get(choice["dialogKey"]) if isinstance(dialogs, dict) else None
        if isinstance(entry, dict):
            entry["lastChoice"] = choice


def action_response_accepted(response: dict[str, Any]) -> bool:
    if "error" in response:
        return False
    result = response.get("result") if isinstance(response.get("result"), dict) else response
    if not isinstance(result, dict):
        return True
    if result.get("accepted") is False or result.get("success") is False:
        return False
    completion = result.get("completion") if isinstance(result.get("completion"), dict) else {}
    event = completion.get("event") if isinstance(completion.get("event"), dict) else {}
    if event.get("success") is False:
        return False
    return True


def compact_observation_summary(observation: dict[str, Any]) -> dict[str, Any]:
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    map_state = observation.get("map") if isinstance(observation.get("map"), dict) else {}
    global_map = observation.get("globalMap") if isinstance(observation.get("globalMap"), dict) else {}
    return {
        "seq": observation.get("seq"),
        "connected": bool(observation.get("connected")),
        "hasMap": bool(observation.get("hasMap")),
        "hasChosen": bool(observation.get("hasChosen")),
        "map": map_state.get("protoId", map_state.get("name")) if isinstance(map_state, dict) else None,
        "globalActive": bool(global_map.get("active")) if isinstance(global_map, dict) else False,
        "chosen": {
            "id": chosen.get("id"),
            "name": chosen.get("name", ""),
            "hex": chosen.get("hex"),
            "alive": chosen.get("alive"),
            "inCombat": chosen.get("inCombat"),
            "curHealth": chosen.get("curHealth"),
            "maxHealth": chosen.get("maxHealth"),
        },
        "visibleCritters": len(observation.get("critters", [])) if isinstance(observation.get("critters"), list) else 0,
        "visibleItems": len(observation.get("mapItems", [])) if isinstance(observation.get("mapItems"), list) else 0,
        "inventoryItems": len(observation.get("inventory", [])) if isinstance(observation.get("inventory"), list) else 0,
        "screen": observation.get("screen", {}).get("active") if isinstance(observation.get("screen"), dict) else None,
    }


def compact_event_entry(entry: dict[str, Any]) -> dict[str, Any]:
    event = entry.get("event") if isinstance(entry.get("event"), dict) else {}
    compact = {"seq": entry.get("seq"), "type": event.get("type")}
    for key in ("message", "text", "speakerName", "listenerName", "query", "success"):
        if key in event:
            compact[key] = event[key]
    return compact


def agent_reply_signature(speech: dict[str, Any]) -> str:
    speaker = speech.get("speaker") if isinstance(speech.get("speaker"), dict) else {}
    payload = {
        "speakerId": speaker.get("id"),
        "text": str(speech.get("text", "")).strip().casefold(),
        "intent": speech.get("intent"),
        "addressedToAgent": speech.get("addressedToAgent"),
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def agent_reply_cooldown_ms(profile: dict[str, Any], arguments: dict[str, Any]) -> int:
    if "replyCooldownMs" in arguments:
        return max(0, min(int(arguments.get("replyCooldownMs") or 0), 60000))

    role = normalized_team_role(profile, 0)
    activity = str(profile.get("activityLevel", "")).casefold()
    reaction = str(profile.get("reactionProfile", "")).casefold()
    if role in {"guard", "leader"} or activity in {"watchful", "busy"}:
        base = 1000
    elif activity in {"social"}:
        base = 1800
    elif activity in {"hesitant", "calm", "methodical"}:
        base = 2600
    else:
        base = 1500
    if reaction == "fast":
        base -= 300
    elif reaction == "slow":
        base += 600
    return max(300, base)


def agent_reply_pacing_gate(runtime: dict[str, Any], profile: dict[str, Any], speech: dict[str, Any], arguments: dict[str, Any], now: int) -> dict[str, Any]:
    cooldown_ms = agent_reply_cooldown_ms(profile, arguments)
    if cooldown_ms <= 0:
        return {"allowed": True, "cooldownMs": 0}
    signature = agent_reply_signature(speech)
    last_signature = str(runtime.get("lastReplyDecisionSignature", ""))
    last_at = runtime.get("lastReplyDecisionAt")
    if signature and signature == last_signature and isinstance(last_at, int):
        elapsed_ms = now - last_at
        if elapsed_ms < cooldown_ms:
            return {
                "allowed": False,
                "cooldownMs": cooldown_ms,
                "elapsedMs": elapsed_ms,
                "remainingMs": cooldown_ms - elapsed_ms,
                "signature": signature,
            }
    return {"allowed": True, "cooldownMs": cooldown_ms, "signature": signature}


def remember_agent_reply_decision(runtime: dict[str, Any], decision: dict[str, Any], now: int) -> None:
    if decision.get("suggestedTool") != "tla_say" or decision.get("intent") != "reply_to_speech":
        return
    speech = decision.get("speech") if isinstance(decision.get("speech"), dict) else {}
    runtime["lastReplyDecisionAt"] = now
    runtime["lastReplyDecisionSignature"] = agent_reply_signature(speech)


def agent_idle_cooldown_ms(profile: dict[str, Any], arguments: dict[str, Any]) -> int:
    if "idleCooldownMs" in arguments:
        return max(0, min(int(arguments.get("idleCooldownMs") or 0), 60000))
    activity = str(profile.get("activityLevel", "")).casefold()
    if activity in {"hesitant", "calm"}:
        return 1800
    if activity in {"methodical", "watchful"}:
        return 2400
    if activity == "social":
        return 3000
    return 1500


def agent_idle_allowed(runtime: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any], now: int) -> dict[str, Any]:
    cooldown_ms = agent_idle_cooldown_ms(profile, arguments)
    if cooldown_ms <= 0:
        return {"allowed": True, "cooldownMs": 0}
    last_at = runtime.get("lastIdleDecisionAt")
    if isinstance(last_at, int):
        elapsed_ms = now - last_at
        if elapsed_ms < cooldown_ms:
            return {"allowed": False, "cooldownMs": cooldown_ms, "elapsedMs": elapsed_ms, "remainingMs": cooldown_ms - elapsed_ms}
    return {"allowed": True, "cooldownMs": cooldown_ms}


def remember_agent_idle_decision(runtime: dict[str, Any], decision: dict[str, Any], now: int) -> None:
    if not str(decision.get("intent", "")).startswith("idle_"):
        return
    runtime["lastIdleDecisionAt"] = now
    runtime["lastIdleIntent"] = decision.get("intent")


def apply_agent_humanization(
    decision: dict[str, Any],
    profile: dict[str, Any],
    memory: dict[str, Any],
    runtime: dict[str, Any],
    arguments: dict[str, Any],
    now: int,
) -> None:
    skill = normalized_agent_skill(profile)
    original_delay = int(decision.get("suggestedDelayMs") or 0)
    seed = int(arguments.get("humanizationSeed", decision.get("decisionId") or 1))
    cadence = agent_skill_cadence(skill)
    forced = str(arguments.get("humanizedMistake", "")).strip().lower()
    if forced and forced not in AGENT_HUMANIZED_MISTAKES:
        forced = ""

    high_priority = str(decision.get("priority", "")).lower() == "high"
    has_tool = bool(decision.get("suggestedTool"))
    mistake_policy = "enabled" if bool(arguments.get("allowHumanizedMistakes", False)) else "metadata_only"
    triggers = {
        "cautious_hesitation": forced == "cautious_hesitation" or cadence_trigger(seed, cadence.get("hesitationEvery", 0)),
        "forget_low_priority": forced == "forget_low_priority" or cadence_trigger(seed, cadence.get("forgetEvery", 0)),
        "non_optimal_route": forced == "non_optimal_route" or cadence_trigger(seed, cadence.get("nonOptimalEvery", 0)),
    }
    delay_adjustment = int(cadence.get("delayAdjustmentMs", 0))
    if triggers["cautious_hesitation"] and not high_priority:
        delay_adjustment += int(cadence.get("hesitationDelayMs", 0))

    decision["suggestedDelayMs"] = max(100, min(original_delay + delay_adjustment, 60000))
    humanization: dict[str, Any] = {
        "skillLevel": skill,
        "seed": seed,
        "policy": mistake_policy,
        "baseDelayMs": original_delay,
        "delayAdjustmentMs": delay_adjustment,
        "suggestedDelayMs": decision["suggestedDelayMs"],
        "triggers": triggers,
        "appliedMistake": None,
        "reasons": agent_humanization_reasons(skill, triggers, delay_adjustment),
    }

    if bool(arguments.get("allowHumanizedMistakes", False)) and has_tool and not high_priority:
        applied = humanized_mistake_to_apply(decision, triggers, forced)
        if applied:
            humanization["appliedMistake"] = applied
            humanization["originalDecision"] = {
                "intent": decision.get("intent"),
                "priority": decision.get("priority"),
                "suggestedTool": decision.get("suggestedTool"),
                "arguments": decision.get("arguments"),
                "source": decision.get("source"),
            }
            apply_humanized_mistake(decision, applied)

    decision["humanization"] = humanization


def normalized_agent_skill(profile: dict[str, Any]) -> str:
    skill = str(profile.get("skillLevel", "average")).strip().lower()
    if skill in {"novice", "newbie", "beginner", "low"}:
        return "novice"
    if skill in {"expert", "veteran", "pro", "high"}:
        return "expert"
    return "average"


def agent_skill_cadence(skill: str) -> dict[str, int]:
    if skill == "novice":
        return {"delayAdjustmentMs": 300, "hesitationDelayMs": 500, "hesitationEvery": 2, "forgetEvery": 5, "nonOptimalEvery": 4}
    if skill == "expert":
        return {"delayAdjustmentMs": -100, "hesitationDelayMs": 0, "hesitationEvery": 0, "forgetEvery": 0, "nonOptimalEvery": 0}
    return {"delayAdjustmentMs": 0, "hesitationDelayMs": 250, "hesitationEvery": 9, "forgetEvery": 13, "nonOptimalEvery": 11}


def cadence_trigger(seed: int, every: int) -> bool:
    return every > 0 and seed > 0 and seed % every == 0


def agent_humanization_reasons(skill: str, triggers: dict[str, bool], delay_adjustment: int) -> list[str]:
    reasons = [f"{skill} skill humanization profile"]
    if delay_adjustment > 0:
        reasons.append("reaction delay increased by skill/hesitation model")
    elif delay_adjustment < 0:
        reasons.append("reaction delay reduced by expert skill model")
    for name, enabled in triggers.items():
        if enabled:
            reasons.append(name.replace("_", " "))
    return reasons


def humanized_mistake_to_apply(decision: dict[str, Any], triggers: dict[str, bool], forced: str) -> str:
    tool = str(decision.get("suggestedTool") or "")
    intent = str(decision.get("intent") or "")
    if forced:
        return forced
    if triggers.get("forget_low_priority") and (intent.find("loot") >= 0 or tool in {"tla_pick_item", "tla_pick_hex", "tla_loot_critter"}):
        return "forget_low_priority"
    if triggers.get("cautious_hesitation") and tool in {"tla_move_to_hex", "tla_attack_entity", "tla_attack_hex", "tla_global_move_to"}:
        return "cautious_hesitation"
    if triggers.get("non_optimal_route") and tool in {"tla_move_to_hex", "tla_global_move_to"}:
        return "non_optimal_route"
    return ""


def apply_humanized_mistake(decision: dict[str, Any], mistake: str) -> None:
    if mistake == "forget_low_priority":
        decision["intent"] = "humanized_forget_low_priority"
        decision["priority"] = "low"
        decision["suggestedTool"] = None
        decision["arguments"] = {}
        decision["source"] = "humanization"
        decision["reasons"].append("humanized mistake: skips a low-priority visible pickup/action this tick")
        return
    if mistake == "cautious_hesitation":
        decision["intent"] = "humanized_hesitate"
        decision["priority"] = "low"
        decision["suggestedTool"] = None
        decision["arguments"] = {}
        decision["source"] = "humanization"
        decision["reasons"].append("humanized mistake: hesitates before a risky or movement-like action")
        return
    if mistake == "non_optimal_route":
        decision["reasons"].append("humanized mistake: host may choose a non-optimal route candidate when executing manually")


def build_agent_decision(
    bridge: Any,
    key: str,
    profile: dict[str, Any],
    memory: dict[str, Any],
    runtime: dict[str, Any],
    step_result: dict[str, Any],
    arguments: dict[str, Any],
    now: int,
) -> dict[str, Any]:
    decision_id = next_agent_decision_id(bridge)
    goal = str(arguments.get("goal", "")).strip()
    if not goal:
        goals = normalize_string_list(profile.get("goals"))
        goal = goals[0] if goals else "observe and choose a safe next action"

    decision: dict[str, Any] = {
        "decisionId": decision_id,
        "time": now,
        "goal": goal,
        "intent": "observe",
        "priority": "low",
        "suggestedTool": None,
        "arguments": {},
        "reasons": [],
        "requiresModelText": False,
        "suggestedDelayMs": agent_reaction_delay_ms(profile),
        "execute": False,
        "dryRun": True,
        "mode": "advisory",
    }

    if bool(runtime.get("paused")):
        decision["intent"] = "paused"
        decision["priority"] = "none"
        decision["reasons"].append("agent runtime is paused")
        return decision

    observation_payload = step_result.get("observation")
    observation = unwrap_observation_payload(observation_payload) if isinstance(observation_payload, dict) else {}
    account = observation.get("account") if isinstance(observation.get("account"), dict) else {}
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    social = step_result.get("social") if isinstance(step_result.get("social"), dict) else {}
    action_suggestions = step_result.get("actionSuggestions") if isinstance(step_result.get("actionSuggestions"), dict) else {}
    actions = action_map_from_suggestions(action_suggestions)
    pending = social.get("pendingResponses") if isinstance(social.get("pendingResponses"), list) else []

    if pending:
        speech = pending[0] if isinstance(pending[0], dict) else {}
        if chosen.get("inCombat") and not bool(arguments.get("skipCombatDecision", False)):
            combat_interrupt = agent_combat_decision(decision, observation, action_suggestions, profile, arguments, runtime, now, bridge)
            if combat_interrupt is not None:
                combat_interrupt["interruptedSpeech"] = {
                    "speaker": speech.get("speaker"),
                    "text": speech.get("text"),
                    "intent": speech.get("intent"),
                    "addressedToAgent": speech.get("addressedToAgent"),
                }
                combat_interrupt["reasons"].append("visible combat takes priority over replying to speech this tick")
                return combat_interrupt
        pacing = agent_reply_pacing_gate(runtime, profile, speech, arguments, now)
        if pacing and not bool(pacing.get("allowed", True)):
            decision["intent"] = "listen_wait"
            decision["priority"] = "low"
            decision["pacing"] = pacing
            decision["speech"] = speech
            decision["suggestedDelayMs"] = max(int(decision.get("suggestedDelayMs") or 0), int(pacing.get("remainingMs") or 0))
            decision["reasons"].append("same visible speech was already selected for reply; wait for reply cooldown")
            return decision
        decision.update(
            {
                "intent": "reply_to_speech",
                "priority": "high",
                "suggestedTool": "tla_say",
                "arguments": {"sayType": "normal"},
                "requiresModelText": True,
                "speech": speech,
                "pacing": pacing,
            }
        )
        decision["reasons"].append("visible speech is addressed to the agent and needs a response")
        return decision

    if account and account.get("agreementAccepted") is False and "accept_agreement" in actions:
        return agent_tool_decision(decision, "accept_agreement", actions["accept_agreement"], "fresh account agreement is pending", "high")
    if chosen and chosen.get("isBodyGenerated") is False and "generate_critter" in actions:
        return agent_tool_decision(decision, "generate_critter", actions["generate_critter"], "chosen body generation is pending", "high")
    if chosen and int(chosen.get("unspentStatPoints") or 0) > 0 and "finish_generation" in actions:
        return agent_tool_decision(decision, "finish_generation", actions["finish_generation"], "unspent generation stat points block normal progress", "high")

    dialog = observation.get("dialog") if isinstance(observation.get("dialog"), dict) else {}
    if dialog.get("active") and "dialog_answer" in actions:
        dialog_plan = agent_dialog_decision(decision, observation, action_suggestions, profile, memory, arguments, now)
        if dialog_plan is not None:
            return dialog_plan
        return agent_tool_decision(decision, "dialog_answer", actions["dialog_answer"], "active dialog is waiting for an answer", "high")

    modal_plan = agent_modal_decision(decision, observation, action_suggestions, profile, runtime, arguments, now)
    if modal_plan is not None:
        return modal_plan

    pending_move = agent_pending_move_wait_decision(decision, runtime, arguments, now)
    if pending_move is not None:
        return pending_move

    urgent_goal_plan = agent_goal_decision(bridge, decision, observation, action_suggestions, profile, memory, arguments, urgent_only=True)
    if urgent_goal_plan is not None:
        return urgent_goal_plan

    progression_plan = agent_progression_decision(decision, observation, action_suggestions, profile, runtime, arguments, now)
    if progression_plan is not None:
        return progression_plan

    combat_prep_plan = agent_combat_preparation_decision(bridge, decision, observation, action_suggestions, profile, runtime, arguments, now)
    if combat_prep_plan is not None:
        return combat_prep_plan

    if not bool(arguments.get("skipCombatDecision", False)):
        combat_plan = agent_combat_decision(decision, observation, action_suggestions, profile, arguments, runtime, now, bridge)
        if combat_plan is not None:
            return combat_plan

    building_entry_plan = agent_building_entry_decision(bridge, decision, observation, action_suggestions, profile, runtime, arguments, now)
    if building_entry_plan is not None:
        return building_entry_plan

    goal_plan = agent_goal_decision(bridge, decision, observation, action_suggestions, profile, memory, arguments)
    if goal_plan is not None:
        return goal_plan

    social_plan = agent_social_action_decision(decision, actions, profile)
    if social_plan is not None:
        return social_plan

    loot_plan = agent_loot_decision(bridge, decision, observation, action_suggestions, profile, runtime, arguments, now)
    if loot_plan is not None:
        return loot_plan

    global_plan = agent_global_decision(decision, observation, action_suggestions, profile, arguments)
    if global_plan is not None:
        return global_plan

    if agent_generic_movement_blocked_by_combat(observation, profile, arguments):
        decision["intent"] = "idle_observe"
        decision["priority"] = "low"
        decision["source"] = "combat_movement_guard"
        decision["reasons"].append("combat or visible threats are active; skip generic map movement unless a combat, retreat, or explicit goal option selected it")
        return decision

    idle_plan = agent_idle_decision(decision, observation, action_suggestions, profile, runtime, arguments, now)
    if idle_plan is not None:
        return idle_plan

    if "global_enter_interest" in actions:
        return agent_tool_decision(decision, "global_enter_interest", actions["global_enter_interest"], "global-map interest is enterable", "normal")
    if "global_move_to" in actions:
        return agent_tool_decision(decision, "global_move_to", actions["global_move_to"], "global-map movement is available", "normal")
    movement_plan = agent_movement_decision(decision, observation, action_suggestions, profile, memory, arguments)
    if movement_plan is not None:
        return movement_plan

    if "say" in actions and profile.get("activityLevel") == "social" and agent_unsolicited_speech_allowed(runtime, arguments, now):
        return agent_tool_decision(decision, "say", actions["say"], "social role may start light visible interaction", "low")

    decision["intent"] = "idle_observe"
    decision["reasons"].append("no urgent social, dialog, generation, combat, loot, or movement action was selected")
    return decision


def agent_modal_decision(
    decision: dict[str, Any],
    observation: dict[str, Any],
    action_suggestions: dict[str, Any],
    profile: dict[str, Any],
    runtime: dict[str, Any],
    arguments: dict[str, Any],
    now: int,
) -> dict[str, Any] | None:
    options = modal_task_options(observation, action_suggestions, profile, arguments)
    option = first_executable_option(options, {"tla_ui_answer", "tla_close_screen", "tla_operate_container", "tla_change_skill", "tla_change_ability"})
    if option is None:
        return None
    intent = str(option.get("kind") or "modal_screen")
    if str(option.get("tool") or option.get("suggestedTool") or "") == "tla_close_screen":
        close_cooldown_ms = max(0, min(int(arguments.get("modalCloseCooldownMs", 1500)), 60000))
        if recent_same_tool_action(runtime, "tla_close_screen", now, close_cooldown_ms):
            decision["intent"] = "modal_screen_wait"
            decision["priority"] = "low"
            decision["source"] = "modal_screen"
            decision["modalWait"] = {"cooldownMs": close_cooldown_ms}
            decision["reasons"].append("recent close_screen command was accepted; wait briefly for modal state to settle before closing again")
            return decision
    return agent_option_decision(decision, intent, option, "active modal GUI screen needs handling before ordinary world actions", "high", "modal_screen")


def agent_pending_move_wait_decision(decision: dict[str, Any], runtime: dict[str, Any], arguments: dict[str, Any], now: int) -> dict[str, Any] | None:
    pending = recent_pending_move_action(runtime, arguments, now)
    if pending is None:
        return None

    decision["intent"] = "idle_moving"
    decision["priority"] = "low"
    decision["source"] = "movement_pacing"
    decision["suggestedTool"] = None
    decision["arguments"] = {}
    decision["movementWait"] = pending
    decision["suggestedDelayMs"] = max(int(decision.get("suggestedDelayMs") or 0), int(pending.get("remainingMs") or 0))
    decision["reasons"].append("recent movement command was accepted; wait briefly for movement/observation to advance before reissuing navigation")
    return decision


def agent_generic_movement_blocked_by_combat(observation: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> bool:
    if bool(arguments.get("allowGenericMovementInCombat", False)):
        return False

    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    if bool(chosen.get("inCombat")):
        return True
    if bool(visible_ally_combat_state(observation).get("active")):
        return True
    if visible_threat_hexes(observation) and (profile_requests_combat(profile, arguments) or bool(arguments.get("allowCombat", False))):
        return True
    return False


def recent_pending_move_action(runtime: dict[str, Any], arguments: dict[str, Any], now: int) -> dict[str, Any] | None:
    if not bool(arguments.get("waitForPendingMovement", True)):
        return None
    # When the run waits for move arrival in execution (moveSettleMs), the chosen has already
    # stopped (or combat started) before the next decision, so this timer-based pacing would only
    # stack redundant idle_moving ticks on top of the real wait. Let the settle own movement pacing.
    if int(arguments.get("moveSettleMs", 0) or 0) > 0:
        return None

    cooldown_ms = max(0, min(int(arguments.get("movementReissueCooldownMs", 1200)), 10000))
    if cooldown_ms <= 0:
        return None

    history = runtime.get("actionHistory") if isinstance(runtime.get("actionHistory"), list) else []
    for entry in reversed(history):
        if not isinstance(entry, dict):
            continue
        if entry.get("accepted") is False:
            return None
        if entry.get("tool") != "tla_move_to_hex":
            return None

        try:
            age_ms = now - int(entry.get("time") or 0)
        except (TypeError, ValueError):
            return None
        if age_ms < 0 or age_ms > cooldown_ms:
            return None

        entry_arguments = entry.get("arguments") if isinstance(entry.get("arguments"), dict) else {}
        return {
            "tool": "tla_move_to_hex",
            "arguments": entry_arguments,
            "ageMs": age_ms,
            "cooldownMs": cooldown_ms,
            "remainingMs": max(cooldown_ms - age_ms, 0),
            "targetHex": {"x": entry_arguments.get("x"), "y": entry_arguments.get("y")}
            if "x" in entry_arguments and "y" in entry_arguments
            else None,
        }

    return None


def agent_goal_decision(
    bridge: Any,
    decision: dict[str, Any],
    observation: dict[str, Any],
    action_suggestions: dict[str, Any],
    profile: dict[str, Any],
    memory: dict[str, Any],
    arguments: dict[str, Any],
    urgent_only: bool = False,
) -> dict[str, Any] | None:
    tags = agent_goal_tags(str(decision.get("goal", "")), arguments)
    if not tags:
        return None

    decision["goalTags"] = tags
    if urgent_only:
        if not ({"retreat", "keep_distance", "avoid_threats"} & set(tags)):
            return None
        return agent_retreat_goal_decision(decision, observation, action_suggestions, profile, arguments)

    if "move_to_hex" in tags:
        explicit = explicit_target_hex(arguments)
        if explicit is not None:
            option = {
                "kind": "goal_move_to_hex",
                "tool": "tla_move_to_hex",
                "arguments": {"x": explicit["x"], "y": explicit["y"]},
                "score": 72,
                "reason": "explicit goal hex from tla_agent_tick/run arguments",
                "hex": explicit,
            }
            return agent_option_decision(decision, "move_to_hex", option, "goal requests movement to an explicit map hex", "normal", "goal_navigation")

    if "approach" in tags:
        approach = agent_approach_goal_decision(bridge, decision, observation, action_suggestions, arguments)
        if approach is not None:
            return approach

    if "find_exit" in tags:
        exit_plan = agent_exit_goal_decision(decision, observation, action_suggestions, profile, arguments)
        if exit_plan is not None:
            return exit_plan

    if "leveling" in tags:
        xp_plan = agent_xp_source_decision(decision, observation, action_suggestions, profile, arguments)
        if xp_plan is not None:
            return xp_plan

    if "explore" in tags:
        explore_plan = agent_explore_goal_decision(decision, observation, action_suggestions, profile, memory, arguments)
        if explore_plan is not None:
            return explore_plan

    if "follow" in tags:
        follow_plan = agent_follow_goal_decision(bridge, decision, observation, action_suggestions, arguments)
        if follow_plan is not None:
            return follow_plan

    return None


def agent_goal_tags(goal: str, arguments: dict[str, Any]) -> list[str]:
    text = goal.casefold()
    tags: list[str] = []
    if goal_has_marker(text, AGENT_GOAL_RETREAT_MARKERS):
        tags.extend(["retreat", "keep_distance", "avoid_threats"])
    if goal_has_marker(text, AGENT_GOAL_EXIT_MARKERS):
        tags.append("find_exit")
    if goal_has_marker(text, AGENT_GOAL_EXPLORE_MARKERS):
        tags.append("explore")
    if goal_has_marker(text, AGENT_GOAL_FOLLOW_MARKERS):
        tags.append("follow")
    if goal_has_xp_marker(text):
        tags.append("leveling")
    if goal_has_marker(text, AGENT_GOAL_MOVE_MARKERS) or explicit_target_hex(arguments) is not None:
        tags.append("move_to_hex")
    if goal_has_marker(text, AGENT_GOAL_APPROACH_MARKERS) or any(name in arguments for name in ("targetId", "itemId", "id")):
        tags.append("approach")
    return sorted(set(tags), key=tags.index)


def goal_has_marker(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text for marker in markers)


def agent_retreat_goal_decision(
    decision: dict[str, Any],
    observation: dict[str, Any],
    action_suggestions: dict[str, Any],
    profile: dict[str, Any],
    arguments: dict[str, Any],
) -> dict[str, Any] | None:
    retreat = retreat_options_payload(observation, action_suggestions, profile, {**arguments, "maxResults": 8})
    option = first_executable_option(retreat.get("options") if isinstance(retreat.get("options"), list) else [], {"tla_move_to_hex"})
    if option is None:
        return None
    result = agent_option_decision(decision, "retreat", option, "goal requests fleeing, threat avoidance, or keeping distance", "high", "goal_retreat")
    result["goalPlan"] = {"kind": "retreat", "threats": retreat.get("threats"), "recommendedChecks": option.get("recommendedChecks", [])}
    return result


def agent_approach_goal_decision(
    bridge: Any,
    decision: dict[str, Any],
    observation: dict[str, Any],
    action_suggestions: dict[str, Any],
    arguments: dict[str, Any],
) -> dict[str, Any] | None:
    target_types = agent_approach_target_types(decision, arguments)
    candidates = [
        candidate
        for candidate in filtered_nav_candidates(observation, action_suggestions, {**arguments, "targetTypes": list(target_types)})
        if not nav_candidate_is_redundant_approach(candidate, observation)
    ]
    candidates = sorted_approach_candidates(candidates, observation)
    if not candidates:
        return None
    max_targets = max(1, min(int(arguments.get("maxApproachTargets", AGENT_APPROACH_DEFAULT_MAX_TARGETS)), 20))
    approach_arguments = {
        "maxApproachCandidates": AGENT_APPROACH_DEFAULT_MAX_CANDIDATES,
        "pathTimeoutMs": AGENT_APPROACH_DEFAULT_PATH_TIMEOUT_MS,
        **arguments,
    }

    for candidate in candidates[:max_targets]:
        target = candidate
        approach_payload: dict[str, Any] | None = None
        if str(candidate.get("targetType", candidate.get("type", ""))) in NAV_APPROACH_STANDING_TYPES:
            approach_payload = find_approach_standing_route(bridge, approach_arguments, candidate, observation)
            if isinstance(approach_payload, dict) and "error" in approach_payload:
                continue
            if isinstance(approach_payload, dict) and approach_payload.get("usedStandingHex") and isinstance(approach_payload.get("standingHex"), dict):
                target = {
                    **candidate,
                    "movementHex": approach_payload.get("standingHex"),
                    "approachTargetHex": candidate.get("hex"),
                    "defaultCut": 0,
                }
            elif nav_candidate_requires_standing_approach(candidate):
                continue

        movement = nav_movement_step(target)
        if not movement:
            continue
        chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
        chosen_xy = safe_hex_value_xy(chosen.get("hex"))
        movement_xy = safe_hex_value_xy(movement.get("arguments"))
        if chosen_xy is not None and movement_xy == chosen_xy:
            continue
        option = {
            "kind": "goal_approach",
            "tool": movement.get("tool"),
            "arguments": movement.get("arguments", {}),
            "score": 68,
            "reason": f"approach visible {candidate.get('targetType', 'target')}; refresh observation before follow-up",
            "label": candidate.get("label"),
            "hex": candidate.get("hex"),
            "target": {key: candidate.get(key) for key in ("targetType", "id", "protoId", "source") if key in candidate},
            "recommendedChecks": ["tla_nav_plan", "tla_env_path"],
        }
        if approach_payload is not None:
            option["approach"] = {
                key: approach_payload.get(key)
                for key in ("usedStandingHex", "standingHex", "targetHex")
                if key in approach_payload
            }
        return agent_option_decision(decision, "approach", option, "goal requests approaching a visible entity or item", "normal", "goal_navigation")

    return None


def agent_approach_target_types(decision: dict[str, Any], arguments: dict[str, Any]) -> set[str]:
    explicit_filters = nav_target_type_filters(arguments)
    if explicit_filters:
        return explicit_filters
    if bool(arguments.get("allowCombatApproach", False)):
        return NAV_APPROACH_TYPES
    goal = str(decision.get("goal", "")).casefold()
    if goal_has_marker(goal, AGENT_GOAL_COMBAT_APPROACH_MARKERS):
        return NAV_APPROACH_TYPES
    return NAV_APPROACH_NONCOMBAT_TYPES


def sorted_approach_candidates(candidates: list[dict[str, Any]], observation: dict[str, Any]) -> list[dict[str, Any]]:
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    chosen_xy = safe_hex_value_xy(chosen.get("hex"))

    def sort_key(entry: tuple[int, dict[str, Any]]) -> tuple[int, int, int, str]:
        index, candidate = entry
        candidate_xy = safe_hex_value_xy(candidate.get("hex"))
        distance = approximate_hex_distance(chosen_xy, candidate_xy) if chosen_xy is not None and candidate_xy is not None else 1_000_000
        candidate_type = str(candidate.get("targetType", candidate.get("type", "")))
        priority = AGENT_APPROACH_TYPE_PRIORITY.get(candidate_type, 10)
        return distance, priority, index, str(candidate.get("id") or candidate.get("label") or "")

    return [candidate for _index, candidate in sorted(enumerate(candidates), key=sort_key)]


def nav_candidate_is_redundant_approach(candidate: dict[str, Any], observation: dict[str, Any] | None = None) -> bool:
    if str(candidate.get("targetType", candidate.get("type", ""))) != "pick_item":
        return False
    item = nav_candidate_item_state(candidate, observation)
    if (item.get("hasDoor") or item.get("hasContainer") or item.get("hasLocker")) and item.get("opened") is True:
        return True
    return False


def nav_candidate_item_state(candidate: dict[str, Any], observation: dict[str, Any] | None = None) -> dict[str, Any]:
    result = dict(candidate)
    if observation is None:
        return result
    candidate_id = str(candidate.get("id") or "")
    arguments = candidate.get("arguments") if isinstance(candidate.get("arguments"), dict) else {}
    item_id = str(arguments.get("itemId") or candidate_id)
    if not item_id:
        return result
    for item in observation.get("mapItems", []) if isinstance(observation.get("mapItems"), list) else []:
        if not isinstance(item, dict) or str(item.get("id") or "") != item_id:
            continue
        for key in (
            "static",
            "isStatic",
            "canUse",
            "canPickUp",
            "hasDoor",
            "hasContainer",
            "hasLocker",
            "opened",
            "canOpen",
            "isGag",
            "noHighlight",
            "hasStaticScript",
            "lockerLocked",
            "lockerNoOpen",
        ):
            if key in item and key not in result:
                result[key] = item.get(key)
        return result
    return result


def nav_candidate_requires_standing_approach(candidate: dict[str, Any]) -> bool:
    candidate_type = str(candidate.get("targetType", candidate.get("type", "")))
    if candidate_type in {"talk_to", "loot_critter", "attack_entity", "attack_hex", "visible_critter"}:
        return True
    if candidate_type in {"pick_item", "visible_item"}:
        return bool(
            candidate.get("hasDoor")
            or candidate.get("hasLocker")
            or candidate.get("hasContainer")
            or (candidate.get("canUse") and not candidate.get("canPickUp"))
        )
    return False


def agent_exit_goal_decision(
    decision: dict[str, Any],
    observation: dict[str, Any],
    action_suggestions: dict[str, Any],
    profile: dict[str, Any],
    arguments: dict[str, Any],
) -> dict[str, Any] | None:
    transitions = map_transition_options_payload(observation, action_suggestions, profile, {**arguments, "maxResults": 8})
    options = transitions.get("options") if isinstance(transitions.get("options"), list) else []
    option = first_executable_option(options, {"tla_global_enter_interest", "tla_global_move_to", "tla_move_to_hex"})
    if option is None:
        travel_plan = transitions.get("travelPlan") if isinstance(transitions.get("travelPlan"), dict) else {}
        if travel_plan:
            option = {"kind": "goal_find_exit", "tool": travel_plan.get("tool"), "arguments": travel_plan.get("arguments", {}), "score": 65, "reason": travel_plan.get("reason")}
    if option is not None:
        result = agent_option_decision(decision, "find_exit", option, "goal requests finding or taking a map/global transition", "normal", "goal_transition")
        result["goalPlan"] = {"kind": "find_exit", "mode": transitions.get("mode")}
        return result
    explore = agent_explore_goal_decision(decision, observation, action_suggestions, profile, {}, arguments)
    if explore is not None:
        explore["reasons"].append("no explicit exit affordance is visible; explore to discover one")
        return explore
    return None


def agent_explore_goal_decision(
    decision: dict[str, Any],
    observation: dict[str, Any],
    action_suggestions: dict[str, Any],
    profile: dict[str, Any],
    memory: dict[str, Any],
    arguments: dict[str, Any],
) -> dict[str, Any] | None:
    local_memory = local_map_memory_payload(memory, observation, 6) if memory else {}
    for frontier in local_memory.get("unexploredFrontier", []) if isinstance(local_memory.get("unexploredFrontier"), list) else []:
        if not isinstance(frontier, dict):
            continue
        hex_value = frontier.get("approxHex") if isinstance(frontier.get("approxHex"), dict) else {}
        xy = safe_hex_value_xy(hex_value)
        if xy is None:
            continue
        option = {
            "kind": "goal_explore_frontier",
            "tool": "tla_move_to_hex",
            "arguments": {"x": xy[0], "y": xy[1]},
            "score": 64,
            "reason": frontier.get("reason", "move toward an unvisited adjacent area cluster"),
            "hex": {"x": xy[0], "y": xy[1]},
            "recommendedChecks": ["tla_env_path", "tla_env_tactical_path"],
        }
        return agent_option_decision(decision, "explore_unknown", option, "goal requests exploration of unknown local area", "low", "goal_explore")

    nav = nav_options_payload(observation, action_suggestions, {**arguments, "maxResults": 8}, profile, memory)
    option = first_executable_option(
        nav.get("options") if isinstance(nav.get("options"), list) else [],
        {"tla_move_to_hex", "tla_global_move_to", "tla_global_enter_interest"},
    )
    if option is None:
        return None
    return agent_option_decision(decision, "explore", option, "goal requests exploration using the best visible navigation lead", "low", "goal_explore")


def agent_follow_goal_decision(
    bridge: Any,
    decision: dict[str, Any],
    observation: dict[str, Any],
    action_suggestions: dict[str, Any],
    arguments: dict[str, Any],
) -> dict[str, Any] | None:
    if any(name in arguments for name in ("targetId", "id")):
        return agent_approach_goal_decision(bridge, decision, observation, action_suggestions, arguments)
    return None


def agent_xp_source_decision(
    decision: dict[str, Any],
    observation: dict[str, Any],
    action_suggestions: dict[str, Any],
    profile: dict[str, Any],
    arguments: dict[str, Any],
) -> dict[str, Any] | None:
    plan_arguments = {**arguments, "maxResults": max(8, int(arguments.get("maxResults", 8)))}
    if not agent_combat_attack_selection_allowed(arguments):
        plan_arguments["allowCombat"] = False
    plan = xp_source_plan_payload(observation, action_suggestions, profile, plan_arguments)
    allowed_tools = {
        "tla_ui_answer",
        "tla_close_screen",
        "tla_operate_container",
        "tla_change_skill",
        "tla_change_ability",
        "tla_dialog_answer",
        "tla_talk_to",
        "tla_pick_item",
        "tla_loot_critter",
        "tla_global_enter_interest",
        "tla_global_move_to",
        "tla_move_to_hex",
    }
    if agent_combat_attack_selection_allowed(arguments):
        allowed_tools.update({"tla_attack_entity", "tla_attack_hex"})
    option = first_executable_option(plan.get("sources") if isinstance(plan.get("sources"), list) else [], allowed_tools)
    if option is None:
        return None
    result = agent_option_decision(decision, str(option.get("kind") or "xp_source"), option, "goal requests XP/level progress; choose the best visible XP source", "normal", "xp_source_plan")
    result["xpPlan"] = {"progress": plan.get("progress"), "source": {key: option.get(key) for key in ("kind", "score", "risk", "estimatedXp", "recommendedChecks") if key in option}}
    return result


def agent_dialog_decision(decision: dict[str, Any], observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], memory: dict[str, Any], arguments: dict[str, Any], now: int) -> dict[str, Any] | None:
    dialog_obs = observation.get("dialog") if isinstance(observation.get("dialog"), dict) else {}
    dialog = dialog_options_payload(observation, action_suggestions, profile, {**arguments, "maxResults": 30})
    options = dialog.get("options") if isinstance(dialog.get("options"), list) else []
    candidates = executable_options(options, {"tla_dialog_answer"})
    if not candidates:
        return None

    # Loop-aware completion: a guide-style hub keeps re-offering the same question
    # answers, and the per-tick ranking always picks the highest-scored question, so a
    # pure-ranking planner re-asks forever and never selects the lower-scored advance/exit
    # answer. Remember which answers were already chosen at this same dialog line (this
    # conversation) and prefer a fresh one; once the line's answers are exhausted (or a
    # turn cap is hit) deliberately advance/close so the dialog actually completes.
    chosen_texts, turns = dialog_session_chosen_texts(memory, dialog_obs, now)
    max_turns = max(2, min(int(arguments.get("maxDialogTurns", 24)), 80))
    fresh = [option for option in candidates if normalize_dialog_text(option.get("text")) not in chosen_texts]

    if fresh and turns < max_turns:
        option = fresh[0]
        intent = str(option.get("intent") or "dialog_answer")
        reason = f"active dialog answer selected as {intent}"
    else:
        option = dialog_advance_option(candidates)
        intent = str(option.get("intent") or "dialog_answer")
        reason = (
            "dialog turn cap reached; advancing/closing the conversation"
            if fresh
            else "dialog loop guard: every visible answer at this line was already chosen; advancing/closing the conversation"
        )
    return agent_option_decision(decision, "dialog_answer", option, reason, "high", "dialog_options")


def normalize_dialog_text(text: Any) -> str:
    return " ".join(str(text or "").strip().casefold().split())


def dialog_session_chosen_texts(memory: dict[str, Any], dialog: dict[str, Any], now: int, gap_ms: int = 45000) -> tuple[set[str], int]:
    """Answer texts already chosen at the current dialog line in this continuous conversation.

    Reads executed-and-accepted choices recorded by `remember_dialog_choice`, walking back
    from now and stopping at the first gap larger than `gap_ms` so a later re-talk of the same
    NPC starts a fresh session. Only choices made while the same speech line was visible count,
    so legitimate distinct lines (or counter-style dialogs) are not over-suppressed.
    """
    choices = memory.get("dialogChoices") if isinstance(memory.get("dialogChoices"), list) else []
    if not choices:
        return set(), 0
    key = dialog_memory_key(dialog) if isinstance(dialog, dict) else None
    speech_text = normalize_dialog_text(dialog.get("text")) if isinstance(dialog, dict) else ""
    chosen: set[str] = set()
    turns = 0
    prev_time = now
    for choice in reversed(choices):
        if not isinstance(choice, dict):
            continue
        try:
            choice_time = int(choice.get("time") or 0)
        except (TypeError, ValueError):
            continue
        if prev_time - choice_time > gap_ms:
            break
        prev_time = choice_time
        if key is not None and choice.get("dialogKey") != key:
            continue
        turns += 1
        if not bool(choice.get("accepted", True)):
            continue
        if normalize_dialog_text(choice.get("speechText")) != speech_text:
            continue
        text = normalize_dialog_text(choice.get("text"))
        if text:
            chosen.add(text)
    return chosen, turns


def dialog_advance_option(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """Pick the answer most likely to advance or end the conversation when fresh answers ran out.

    Prefer an explicit farewell, then a neutral advance ("understood"/roleplay/statement),
    then non-committal refusals, and only fall back to questions/accepts; never a hostile line.
    """
    intent_rank = {"leave": 0, "roleplay": 1, "statement": 1, "refuse": 2, "healing": 3, "trade": 4, "question": 5, "accept": 5, "hostile": 9}
    return min(candidates, key=lambda option: (intent_rank.get(str(option.get("intent") or ""), 5), int(option.get("score", 50))))


def agent_progression_decision(
    decision: dict[str, Any],
    observation: dict[str, Any],
    action_suggestions: dict[str, Any],
    profile: dict[str, Any],
    runtime: dict[str, Any],
    arguments: dict[str, Any],
    now: int,
) -> dict[str, Any] | None:
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    if bool(chosen.get("inCombat")):
        return None
    ally_combat = visible_ally_combat_state(observation)
    if bool(ally_combat.get("active")):
        return None
    if not bool(arguments.get("allowUnsafeProgression", False)) and visible_progression_threats(observation):
        return None
    max_progression_actions = max(0, min(int(arguments.get("maxProgressionActions", 3)), 20))
    if recent_progression_action_count(runtime, now) >= max_progression_actions:
        return None
    progression = progression_options_payload(observation, action_suggestions, profile, {**arguments, "maxResults": 5})
    options = progression.get("options") if isinstance(progression.get("options"), list) else []
    options = [
        option
        for option in options
        if isinstance(option, dict)
        and not recent_same_progression_action(runtime, str(option.get("tool") or ""), option.get("arguments") if isinstance(option.get("arguments"), dict) else {}, now)
    ]
    option = first_executable_option(options, {"tla_change_skill", "tla_change_ability"})
    if option is None:
        return None
    intent = str(option.get("kind") or "progression")
    return agent_option_decision(decision, intent, option, "unspent progression points can improve the character before more risk", "normal", "progression_options")


def recent_progression_action_count(runtime: dict[str, Any], now: int, window_ms: int = 600000) -> int:
    history = runtime.get("actionHistory") if isinstance(runtime.get("actionHistory"), list) else []
    count = 0
    for entry in reversed(history):
        if not isinstance(entry, dict):
            continue
        try:
            age = now - int(entry.get("time") or 0)
        except (TypeError, ValueError):
            age = window_ms + 1
        if age > window_ms:
            break
        if entry.get("tool") in {"tla_change_skill", "tla_change_ability"}:
            count += 1
    return count


def recent_same_progression_action(runtime: dict[str, Any], tool_name: str, arguments: dict[str, Any], now: int, window_ms: int = 3000) -> bool:
    if tool_name not in {"tla_change_skill", "tla_change_ability"}:
        return False
    history = runtime.get("actionHistory") if isinstance(runtime.get("actionHistory"), list) else []
    for entry in reversed(history):
        if not isinstance(entry, dict):
            continue
        try:
            age = now - int(entry.get("time") or 0)
        except (TypeError, ValueError):
            age = window_ms + 1
        if age > window_ms:
            break
        if entry.get("tool") != tool_name:
            continue
        entry_args = entry.get("arguments") if isinstance(entry.get("arguments"), dict) else {}
        if progression_action_arguments_match(tool_name, entry_args, arguments):
            return True
    return False


def progression_action_arguments_match(tool_name: str, left: dict[str, Any], right: dict[str, Any]) -> bool:
    if tool_name == "tla_change_skill":
        try:
            left_skill = skill_property_name(left.get("skill"))
            right_skill = skill_property_name(right.get("skill"))
        except ValueError:
            left_skill = str(left.get("skill") or "")
            right_skill = str(right.get("skill") or "")
        return left_skill == right_skill and bool(left.get("increase", True)) == bool(right.get("increase", True))
    if tool_name == "tla_change_ability":
        return str(left.get("protoId") or "") == str(right.get("protoId") or "") and bool(left.get("add", True)) == bool(right.get("add", True))
    return False


def agent_combat_preparation_decision(
    bridge: Any,
    decision: dict[str, Any],
    observation: dict[str, Any],
    action_suggestions: dict[str, Any],
    profile: dict[str, Any],
    runtime: dict[str, Any],
    arguments: dict[str, Any],
    now: int,
) -> dict[str, Any] | None:
    if not combat_preparation_requested(profile, arguments):
        return None

    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    if bool(chosen.get("inCombat")):
        return None

    ally_combat = visible_ally_combat_state(observation)
    if bool(ally_combat.get("active")):
        return None

    if combat_ready_equipment_visible(observation):
        return None

    equip_payload = equip_options_payload(observation, action_suggestions, profile, {**arguments, "maxResults": 3})
    equip_cooldown_ms = max(0, min(int(arguments.get("equipActionCooldownMs", 3000)), 60000))
    equip_options = [
        option
        for option in equip_payload.get("options", []) if isinstance(option, dict)
        if not recent_same_equip_action(runtime, str(option.get("tool") or ""), option.get("arguments") if isinstance(option.get("arguments"), dict) else {}, now, equip_cooldown_ms)
        and combat_equipment_option_allowed(observation, option, True)
    ]
    equip_option = first_executable_option(equip_options, {"tla_use_item", "tla_move_item"})
    if equip_option is not None:
        return agent_option_decision(decision, "combat_prepare_equip", equip_option, "combat goal is active and usable equipment can be readied before taking more risk", "normal", "combat_preparation")

    if combat_preparation_supplies_satisfied(observation, action_suggestions, profile, arguments):
        return None

    options = combat_preparation_loot_options(observation, action_suggestions, profile, arguments)
    cooldown_ms = max(0, min(int(arguments.get("lootRetryCooldownMs", 3000)), 60000))
    for option in options:
        tool_name = str(option.get("tool") or "")
        option_arguments = option.get("arguments") if isinstance(option.get("arguments"), dict) else {}
        if tool_name not in {"tla_pick_item", "tla_pick_hex", "tla_loot_critter", "tla_operate_container"}:
            continue
        if option.get("blockedBy") or not option_arguments:
            continue
        if recent_same_loot_action(runtime, tool_name, option_arguments, now, cooldown_ms):
            continue
        approach_option = agent_loot_approach_option(bridge, observation, option, arguments)
        if isinstance(approach_option, dict):
            if approach_option.get("skip"):
                continue
            result = agent_option_decision(
                decision,
                "combat_prepare_approach_loot",
                approach_option,
                "combat goal is active, no weapon is ready, and useful combat supplies need an adjacent standing hex",
                "normal",
                "combat_preparation",
            )
            if ally_combat.get("active"):
                result["allySupport"] = ally_combat
            return result
        result = agent_option_decision(
            decision,
            str(option.get("type") or "combat_prepare_loot"),
            option,
            "combat goal is active and no weapon is ready; gather visible combat supplies before starting avoidable fights",
            "normal",
            "combat_preparation",
        )
        if ally_combat.get("active"):
            result["allySupport"] = ally_combat
        return result

    return None


def combat_preparation_requested(profile: dict[str, Any], arguments: dict[str, Any]) -> bool:
    if bool(arguments.get("skipCombatPreparation", False)):
        return False
    goal_text = str(arguments.get("goal") or "").casefold()
    preparation_markers = ("prepare", "supplies", "armed", "вооруж", "припас", "подготов")
    has_preparation_marker = any(marker in goal_text for marker in preparation_markers)
    if ("approach" in agent_goal_tags(goal_text, arguments) or any(name in arguments for name in ("targetId", "itemId", "id"))) and not has_preparation_marker:
        return False
    combat_style = str(profile.get("combatStyle", "")).casefold()
    loot_style = str(profile.get("lootStyle", "")).casefold()
    if combat_style in {"aggressive", "hostile"} and not has_preparation_marker:
        return False
    if loot_style in {"combat", "survival", "practical", "test-relevant"} and profile_requests_combat(profile, arguments):
        return True
    text = " ".join(
        [
            str(arguments.get("goal") or ""),
            str(profile.get("role") or ""),
            str(profile.get("preset") or ""),
            *normalize_string_list(profile.get("goals")),
        ]
    ).casefold()
    return profile_requests_combat(profile, arguments) and any(marker in text for marker in preparation_markers)


def combat_ready_equipment_visible(observation: dict[str, Any]) -> bool:
    for item in inventory_items(observation):
        if item_has_tag(item, "equipped") and item_has_tag(item, "weapon"):
            return True
    return False


def combat_preparation_supplies_satisfied(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> bool:
    if not any(item_has_tag(item, "healing") for item in inventory_items(observation)):
        return False
    targets = target_options_payload(observation, action_suggestions, profile, {**arguments, "maxResults": 1})
    if not targets.get("options"):
        return False
    if any(item_has_tag(item, "weapon") for item in inventory_items(observation)):
        return True
    for option in combat_preparation_loot_options(observation, action_suggestions, profile, arguments):
        tool_name = str(option.get("tool") or "")
        if tool_name in {"tla_pick_item", "tla_pick_hex", "tla_loot_critter", "tla_operate_container"} and not option.get("blockedBy"):
            return False
    return True


def combat_preparation_loot_options(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> list[dict[str, Any]]:
    loot = loot_options_payload(observation, action_suggestions, profile, {**arguments, "maxResults": max(30, int(arguments.get("maxResults", 5)))})
    options: list[dict[str, Any]] = []
    for option in loot.get("options", []) if isinstance(loot.get("options"), list) else []:
        if not isinstance(option, dict):
            continue
        prepared = dict(option)
        item = prepared.get("item") if isinstance(prepared.get("item"), dict) else {}
        tool_name = str(prepared.get("tool") or "")
        if tool_name == "tla_operate_container":
            prepared["score"] = max(int(prepared.get("score", 0)), 95)
            prepared["reason"] = "active collection is open; take visible supplies before combat"
            options.append(prepared)
            continue
        if tool_name == "tla_loot_critter":
            prepared["score"] = max(int(prepared.get("score", 0)), 65)
            prepared["reason"] = "visible corpse may contain combat supplies"
            options.append(prepared)
            continue
        if not combat_preparation_item_candidate(item):
            continue
        prepared["score"] = min(100, int(prepared.get("score", 0)) + combat_preparation_item_bonus(item))
        prepared["reason"] = "visible combat-preparation item or container"
        options.append(prepared)

    options.sort(key=lambda item: int(item.get("score", 0)), reverse=True)
    return options


def combat_preparation_item_candidate(item: dict[str, Any]) -> bool:
    return any(item_has_tag(item, tag) for tag in ("weapon", "armor", "healing", "ammo", "container", "locker", "door"))


def combat_preparation_item_bonus(item: dict[str, Any]) -> int:
    bonus = 0
    for tag, value in (("weapon", 35), ("healing", 25), ("armor", 20), ("ammo", 15), ("container", 30), ("locker", 30), ("door", 25)):
        if item_has_tag(item, tag):
            bonus += value
    return min(bonus, 55)


def agent_combat_decision(
    decision: dict[str, Any],
    observation: dict[str, Any],
    action_suggestions: dict[str, Any],
    profile: dict[str, Any],
    arguments: dict[str, Any],
    runtime: dict[str, Any] | None = None,
    now: int | None = None,
    bridge: Any | None = None,
) -> dict[str, Any] | None:
    runtime = runtime if isinstance(runtime, dict) else {}
    now = unix_ms() if now is None else now
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    actions = action_map_from_suggestions(action_suggestions)
    combat = combat_options_payload(observation, action_suggestions, profile, {**arguments, "maxResults": 5})
    health = combat.get("state", {}).get("health") if isinstance(combat.get("state"), dict) and isinstance(combat.get("state", {}).get("health"), dict) else {}
    stamina = combat.get("state", {}).get("stamina") if isinstance(combat.get("state"), dict) and isinstance(combat.get("state", {}).get("stamina"), dict) else {}
    ally_combat = combat.get("state", {}).get("allyInCombat") if isinstance(combat.get("state"), dict) and isinstance(combat.get("state", {}).get("allyInCombat"), dict) else {}
    healing = combat.get("healing") if isinstance(combat.get("healing"), dict) else {}
    healing_cooldown_ms = max(0, min(int(arguments.get("healingActionCooldownMs", 1000)), 60000))
    raw_healing_options = healing.get("options") if isinstance(healing.get("options"), list) else []
    recent_healing_skipped = False
    healing_options: list[dict[str, Any]] = []
    for option in raw_healing_options:
        if not isinstance(option, dict):
            continue
        option_item = option.get("item") if isinstance(option.get("item"), dict) else {}
        if not item_has_tag(option_item, "healing"):
            continue
        if recent_same_equip_action(runtime, str(option.get("tool") or ""), option.get("arguments") if isinstance(option.get("arguments"), dict) else {}, now, healing_cooldown_ms):
            recent_healing_skipped = True
            continue
        healing_options.append(option)
    healing_option = first_executable_option(healing_options, {"tla_use_item"})
    if health.get("needsHealing") and healing_option is not None:
        return agent_option_decision(decision, "heal", healing_option, "chosen health is low and a visible healing-like item is usable", "high", "combat_options")
    if health.get("needsHealing") and recent_healing_skipped:
        decision["intent"] = "heal_wait"
        decision["priority"] = "low"
        decision["source"] = "combat_options"
        decision["healingWait"] = {"cooldownMs": healing_cooldown_ms}
        decision["reasons"].append("recent healing command used the visible healing option; wait briefly for inventory and health observation to settle")
        return decision

    ally_healing = combat.get("allyHealing") if isinstance(combat.get("allyHealing"), dict) else {}
    ally_healing_option = first_executable_option(ally_healing.get("options") if isinstance(ally_healing.get("options"), list) else [], {"tla_use_item"})
    if ally_healing_option is not None:
        return agent_option_decision(decision, "heal_ally", ally_healing_option, "visible ally is low on health and a visible healing-like item can be used on them", "high", "combat_options")

    ratio = health.get("ratio")
    retreat_payload = combat.get("retreat") if isinstance(combat.get("retreat"), dict) else {}
    retreat_option = first_executable_option(retreat_payload.get("options") if isinstance(retreat_payload.get("options"), list) else [], {"tla_move_to_hex"})
    if isinstance(ratio, (int, float)) and float(ratio) < 0.35 and retreat_option is not None:
        return agent_option_decision(decision, "retreat", retreat_option, "chosen health is critically low and no healing action was selected", "high", "combat_options")

    if stamina.get("needsRecovery"):
        safe_step_option = agent_safe_step_move_option(bridge, arguments)
        if safe_step_option is not None:
            result = agent_option_decision(decision, "recover_stamina", safe_step_option, "chosen stamina is low; use a reachable safe-step before more attacks", "high", "combat_options")
            result["recovery"] = {"stamina": stamina, "mode": "safe_step"}
            return result
        if retreat_option is not None and bridge is None:
            result = agent_option_decision(decision, "recover_stamina", retreat_option, "chosen stamina is low; move away before more attacks", "high", "combat_options")
            result["recovery"] = {"stamina": stamina, "mode": "retreat"}
            return result
        clear_action = actions.get("clear_actions") if isinstance(actions.get("clear_actions"), dict) else {}
        if action_executable(clear_action):
            clear_cooldown_ms = max(0, min(int(arguments.get("staminaClearActionCooldownMs", 3000)), 60000))
            if recent_same_tool_action(runtime, "tla_clear_actions", now, clear_cooldown_ms):
                decision["intent"] = "recover_stamina_wait"
                decision["priority"] = "low"
                decision["source"] = "combat_options"
                decision["recovery"] = {"stamina": stamina, "mode": "wait", "cooldownMs": clear_cooldown_ms}
                decision["reasons"].append("recent clear_actions recovery command was accepted; wait briefly for stamina before sending another command")
                return decision
            clear_option = {
                "kind": "recover_stamina",
                "tool": clear_action.get("tool") or "tla_clear_actions",
                "arguments": clear_action.get("example", {}) if isinstance(clear_action.get("example"), dict) else {},
                "score": 90 if stamina.get("critical") else 82,
                "reason": "clear queued actions and wait for stamina recovery before attacking",
            }
            result = agent_option_decision(decision, "recover_stamina", clear_option, "chosen stamina is low and no safer retreat command is currently executable", "high", "combat_options")
            result["recovery"] = {"stamina": stamina, "mode": "clear_actions"}
            return result
        if stamina.get("critical"):
            decision["intent"] = "recover_stamina"
            decision["priority"] = "high"
            decision["source"] = "combat_options"
            decision["recovery"] = {"stamina": stamina, "mode": "wait"}
            decision["reasons"].append("chosen stamina is exhausted; do not attack until a retreat or pause action becomes available")
            return decision

    reload_payload = combat.get("reload") if isinstance(combat.get("reload"), dict) else {}
    reload_option = first_executable_option(reload_payload.get("options") if isinstance(reload_payload.get("options"), list) else [], {"tla_reload"})
    if chosen.get("inCombat") and reload_option is not None:
        return agent_option_decision(decision, "reload", reload_option, "chosen is in combat and reload option is available", "normal", "combat_options")

    equip_payload = equip_options_payload(observation, action_suggestions, profile, {**arguments, "maxResults": 3})
    equip_cooldown_ms = max(0, min(int(arguments.get("equipActionCooldownMs", 3000)), 60000))
    equip_options = [
        option
        for option in equip_payload.get("options", []) if isinstance(option, dict)
        if not recent_same_equip_action(runtime, str(option.get("tool") or ""), option.get("arguments") if isinstance(option.get("arguments"), dict) else {}, now, equip_cooldown_ms)
        and combat_equipment_option_allowed(observation, option, bool(chosen.get("inCombat") or ally_combat.get("active")))
    ]
    equip_option = first_executable_option(equip_options, {"tla_use_item", "tla_move_item"})
    if (chosen.get("inCombat") or ally_combat.get("active")) and equip_option is not None and not combat_ready_equipment_visible(observation):
        return agent_option_decision(decision, "equip", equip_option, "combat is active nearby and a visible equipment-like item can be readied", "normal", "combat_options")

    if not agent_combat_attack_selection_allowed(arguments):
        return None

    target_payload = combat.get("targets") if isinstance(combat.get("targets"), dict) else {}
    combat_cooldown_ms = max(0, min(int(arguments.get("combatActionCooldownMs", 1200)), 60000))
    target_option = first_executable_option(
        [
            option
            for option in target_payload.get("options", []) if isinstance(option, dict)
            if attack_option_allowed(option, observation, arguments)
            and (
                bool(ally_combat.get("active"))
                or not recent_same_combat_action(runtime, str(option.get("tool") or ""), option.get("arguments") if isinstance(option.get("arguments"), dict) else {}, now, combat_cooldown_ms)
            )
        ],
        {"tla_attack_entity", "tla_attack_hex"},
    )
    combat_style = str(profile.get("combatStyle", "")).casefold()
    role = normalized_team_role(profile, 0)
    wants_attack = bool(chosen.get("inCombat")) or bool(ally_combat.get("active")) or profile_requests_combat(profile, arguments) or combat_style in {"aggressive", "hostile"} or role in {"guard", "leader"}
    if wants_attack and target_option is not None:
        priority = "high" if chosen.get("inCombat") or ally_combat.get("active") else "normal"
        reason = "visible ally is in combat; support them with the best visible hostile target" if ally_combat.get("active") else "combat profile or goal selected a visible non-player target"
        result = agent_option_decision(decision, "attack_entity", target_option, reason, priority, "combat_options")
        if ally_combat.get("active"):
            result["allySupport"] = ally_combat
        return result

    if wants_attack and visible_threat_hexes(observation):
        if retreat_option is not None:
            return agent_option_decision(
                decision,
                "reposition",
                retreat_option,
                "visible threats remain but no attack is currently selectable; keep distance instead of idling in danger",
                "normal",
                "combat_options",
            )
        safe_step_option = agent_safe_step_move_option(bridge, arguments)
        if safe_step_option is not None:
            return agent_option_decision(
                decision,
                "reposition",
                safe_step_option,
                "visible threats remain but no attack is currently selectable; use the tactical safe-step helper before idling",
                "normal",
                "combat_options",
            )

    return None


def agent_safe_step_move_option(bridge: Any | None, arguments: dict[str, Any]) -> dict[str, Any] | None:
    if bridge is None:
        return None
    response = find_safe_step_state(bridge, {**arguments, "maxCandidates": int(arguments.get("safeStepMaxCandidates", 8))})
    payload = response.get("result") if isinstance(response.get("result"), dict) else {}
    best = payload.get("best") if isinstance(payload.get("best"), dict) else {}
    movement = best.get("movement") if isinstance(best.get("movement"), dict) else {}
    if movement.get("tool") != "tla_move_to_hex" or not isinstance(movement.get("arguments"), dict):
        return None
    return {
        "kind": "safe_step",
        "tool": "tla_move_to_hex",
        "arguments": dict(movement.get("arguments", {})),
        "score": best.get("adjustedScore", best.get("score", 60)),
        "reason": "tactical safe-step helper found a reachable movement candidate",
    }


def profile_requests_combat(profile: dict[str, Any], arguments: dict[str, Any]) -> bool:
    values = [
        str(profile.get("preset") or ""),
        str(profile.get("role") or ""),
        str(profile.get("combatStyle") or ""),
        str(arguments.get("goal") or ""),
    ]
    values.extend(normalize_string_list(profile.get("goals")))
    text = " ".join(values).casefold()
    if "avoidant" in text or "pacifist" in text:
        return False
    if normalized_team_role(profile, 0) in {"guard", "leader"}:
        return True
    return any(marker in text for marker in COMBAT_GOAL_MARKERS)


def recent_same_combat_action(runtime: dict[str, Any], tool_name: str, arguments: dict[str, Any], now: int, window_ms: int = 1200) -> bool:
    if window_ms <= 0 or tool_name not in {"tla_attack_entity", "tla_attack_hex"}:
        return False
    history = runtime.get("actionHistory") if isinstance(runtime.get("actionHistory"), list) else []
    for entry in reversed(history):
        if not isinstance(entry, dict):
            continue
        try:
            age = now - int(entry.get("time") or 0)
        except (TypeError, ValueError):
            age = window_ms + 1
        if age > window_ms:
            break
        if entry.get("tool") != tool_name:
            continue
        entry_args = entry.get("arguments") if isinstance(entry.get("arguments"), dict) else {}
        if combat_action_arguments_match(tool_name, entry_args, arguments):
            return True
    return False


def combat_action_arguments_match(tool_name: str, left: dict[str, Any], right: dict[str, Any]) -> bool:
    if tool_name == "tla_attack_entity":
        return str(left.get("targetId") or "") == str(right.get("targetId") or "")
    if tool_name == "tla_attack_hex":
        return safe_xy_pair(left.get("x"), left.get("y")) == safe_xy_pair(right.get("x"), right.get("y"))
    return False


def recent_same_equip_action(runtime: dict[str, Any], tool_name: str, arguments: dict[str, Any], now: int, window_ms: int = 3000) -> bool:
    if window_ms <= 0 or tool_name not in {"tla_use_item", "tla_move_item"}:
        return False
    history = runtime.get("actionHistory") if isinstance(runtime.get("actionHistory"), list) else []
    for entry in reversed(history):
        if not isinstance(entry, dict):
            continue
        try:
            age = now - int(entry.get("time") or 0)
        except (TypeError, ValueError):
            age = window_ms + 1
        if age > window_ms:
            break
        if entry.get("tool") != tool_name:
            continue
        entry_args = entry.get("arguments") if isinstance(entry.get("arguments"), dict) else {}
        if equip_action_arguments_match(tool_name, entry_args, arguments):
            return True
    return False


def recent_same_tool_action(runtime: dict[str, Any], tool_name: str, now: int, window_ms: int = 3000) -> bool:
    history = runtime.get("actionHistory") if isinstance(runtime.get("actionHistory"), list) else []
    for entry in reversed(history):
        if not isinstance(entry, dict):
            continue
        try:
            age = now - int(entry.get("time") or 0)
        except (TypeError, ValueError):
            age = window_ms + 1
        if age > window_ms:
            break
        if entry.get("tool") == tool_name:
            return True
    return False


def equip_action_arguments_match(tool_name: str, left: dict[str, Any], right: dict[str, Any]) -> bool:
    if str(left.get("itemId") or "") != str(right.get("itemId") or ""):
        return False
    if tool_name == "tla_move_item":
        return str(left.get("slot") or "") == str(right.get("slot") or "")
    if tool_name == "tla_use_item":
        return (
            str(left.get("targetId") or "") == str(right.get("targetId") or "")
            and str(left.get("auxId") or "") == str(right.get("auxId") or "")
            and str(left.get("useMode") or "") == str(right.get("useMode") or "")
        )
    return False


def agent_combat_attack_selection_allowed(arguments: dict[str, Any]) -> bool:
    if bool(arguments.get("allowCombat", False)):
        return True
    if "allowCombat" in arguments or "allowedTools" in arguments or "blockedTools" in arguments:
        return False
    return True


def attack_option_allowed(option: dict[str, Any], observation: dict[str, Any], arguments: dict[str, Any]) -> bool:
    if bool(arguments.get("allowPlayerTargets", False)):
        return True
    critter = option.get("critter") if isinstance(option.get("critter"), dict) else {}
    if bool(critter.get("controlledByPlayer")):
        return False
    if critter_support_ally(critter) and not bool(arguments.get("allowFriendlyTargets", False)):
        return False
    if critter_protected_nonhostile(critter) and not bool(arguments.get("allowNeutralTargets", False)) and not bool(arguments.get("allowFriendlyTargets", False)):
        return False
    if str(option.get("tool")) == "tla_attack_hex" and attack_hex_near_player(option, observation):
        return False
    return True


def attack_hex_near_player(option: dict[str, Any], observation: dict[str, Any]) -> bool:
    target_xy = safe_hex_value_xy(option.get("hex"))
    if target_xy is None and isinstance(option.get("arguments"), dict):
        target_xy = safe_xy_pair(option["arguments"].get("x"), option["arguments"].get("y"))
    if target_xy is None:
        return False
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    chosen_id = chosen.get("id")
    for critter in observation.get("critters", []) if isinstance(observation.get("critters"), list) else []:
        if not isinstance(critter, dict) or critter.get("id") == chosen_id:
            continue
        if not bool(critter.get("controlledByPlayer")):
            continue
        xy = safe_hex_value_xy(critter.get("hex"))
        if xy is not None and approximate_hex_distance(target_xy, xy) <= 1:
            return True
    return False


def agent_social_action_decision(decision: dict[str, Any], actions: dict[str, dict[str, Any]], profile: dict[str, Any]) -> dict[str, Any] | None:
    action = actions.get("talk_to")
    if not isinstance(action, dict) or not action_executable(action):
        return None

    role = normalized_team_role(profile, 0)
    activity = str(profile.get("activityLevel", "")).casefold()
    if role not in {"talker", "trader", "leader"} and activity not in {"social", "busy"}:
        return None

    return agent_tool_decision(decision, "talk_to", action, "role/activity prefers visible conversation before looting or wandering", "normal")


def agent_unsolicited_speech_allowed(runtime: dict[str, Any], arguments: dict[str, Any], now: int) -> bool:
    cooldown_ms = max(0, min(int(arguments.get("unsolicitedSpeechCooldownMs", 30000)), 300000))
    if cooldown_ms == 0:
        return True
    history = runtime.get("actionHistory") if isinstance(runtime.get("actionHistory"), list) else []
    for entry in reversed(history):
        if not isinstance(entry, dict):
            continue
        try:
            age = now - int(entry.get("time") or 0)
        except (TypeError, ValueError):
            age = cooldown_ms + 1
        if age > cooldown_ms:
            break
        if entry.get("tool") == "tla_say":
            return False
    return True


def agent_movement_decision(
    decision: dict[str, Any],
    observation: dict[str, Any],
    action_suggestions: dict[str, Any],
    profile: dict[str, Any],
    memory: dict[str, Any],
    arguments: dict[str, Any],
) -> dict[str, Any] | None:
    nav = nav_options_payload(observation, action_suggestions, {**arguments, "maxResults": 12}, profile, memory)
    option = first_executable_option(nav.get("options") if isinstance(nav.get("options"), list) else [], {"tla_move_to_hex"})
    if option is None:
        return None
    return agent_option_decision(decision, "move_to_hex", option, "map movement is available; verify with environment queries before moving", "low", "nav_options")


BUILDING_ENTRY_MAX_DOOR_ATTEMPTS = 8
BUILDING_ENTRY_MAX_DOOR_DISTANCE = 12


def closed_openable_doors(observation: dict[str, Any]) -> list[dict[str, Any]]:
    """Visible doors that are closed, unlocked, and openable by the chosen right now.

    `canOpen` is the discriminator: a starter-shack interior is full of containers that also
    report `hasLocker`, but only the real entry door reports `hasDoor` AND `canOpen=True`.
    """
    doors: list[dict[str, Any]] = []
    for item in observation.get("mapItems", []) if isinstance(observation.get("mapItems"), list) else []:
        if not isinstance(item, dict) or not isinstance(item.get("hex"), dict) or item.get("id") is None:
            continue
        if not bool(item.get("hasDoor")) or item.get("opened") is True or item.get("canOpen") is not True:
            continue
        if item.get("lockerLocked") is True or item.get("lockerNoOpen") is True:
            continue
        doors.append(item)
    return doors


def building_loot_targets(observation: dict[str, Any]) -> list[dict[str, Any]]:
    """Unopened visible loot containers, nearest first."""
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    origin_xy = safe_hex_value_xy(chosen.get("hex"))
    targets: list[dict[str, Any]] = []
    for item in observation.get("mapItems", []) if isinstance(observation.get("mapItems"), list) else []:
        if not isinstance(item, dict) or not isinstance(item.get("hex"), dict):
            continue
        if not bool(item.get("hasContainer")) or item.get("opened") is True:
            continue
        item_xy = safe_hex_value_xy(item.get("hex"))
        if item_xy is None:
            continue
        targets.append({"id": item.get("id"), "protoId": item.get("protoId"), "hex": item.get("hex"), "xy": item_xy,
                        "canUse": bool(item.get("canUse")), "canPickUp": bool(item.get("canPickUp")),
                        "dist": approximate_hex_distance(origin_xy, item_xy) if origin_xy is not None else 0})
    targets.sort(key=lambda entry: int(entry.get("dist", 0)))
    return targets


def building_path_reachable(bridge: Any, arguments: dict[str, Any], hex_dict: dict[str, Any], cut: int) -> bool | None:
    """Single path probe: can the chosen reach within `cut` hexes of `hex_dict`? None on error."""
    if not isinstance(hex_dict, dict):
        return None
    probe_target = {"hex": hex_dict, "targetType": "move_to_hex", "defaultCut": cut}
    query_args = nav_query_arguments({**arguments, "cut": cut}, probe_target, "path")
    query_args["includeDirections"] = False
    query_args.setdefault("timeoutMs", int(arguments.get("pathTimeoutMs", arguments.get("timeoutMs", DEFAULT_ENVIRONMENT_QUERY_TIMEOUT_MS))))
    query_args.setdefault("pollIntervalMs", int(arguments.get("pollIntervalMs", 100)))
    response = environment_query(bridge, "path", query_args)
    if "error" in response:
        return None
    payload = response.get("result", {}) if isinstance(response.get("result"), dict) else {}
    route = payload.get("result") if isinstance(payload.get("result"), dict) else {}
    return route_reachable(route_with_query(route, "path"))


def agent_building_entry_decision(
    bridge: Any,
    decision: dict[str, Any],
    observation: dict[str, Any],
    action_suggestions: dict[str, Any],
    profile: dict[str, Any],
    runtime: dict[str, Any],
    arguments: dict[str, Any],
    now: int,
) -> dict[str, Any] | None:
    """Open a closed door to reach loot that is otherwise enclosed (e.g. the intro upper building).

    Opt-in via `enterBuildingForLootMs`. Fires only when the nearest unopened loot container is
    path-unreachable AND a reachable closed openable door exists: it opens that door with
    tla_pick_item (which auto-approaches), and once the door reports opened the container becomes
    reachable on a later tick so the normal approach/loot path resumes. Each closed door is opened
    at most once (opened doors leave `closed_openable_doors`), so a multi-door shack terminates;
    a per-(target,door) attempt cap stops a door whose open never lands.
    """
    if int(arguments.get("enterBuildingForLootMs", 0) or 0) <= 0:
        return None
    if str(profile.get("lootStyle", "")).casefold() in {"minimal", "none"}:
        return None
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    if bool(chosen.get("inCombat")):
        return None
    targets = building_loot_targets(observation)
    if not targets:
        return None

    # Once inside, an adjacent usable unopened container is opened directly here (the goal-approach
    # would otherwise oscillate forever trying to step onto the non-movable container hex). Opening
    # it surfaces the collection modal, which the modal handler drains with tla_operate_container.
    chosen_xy = safe_hex_value_xy(chosen.get("hex"))
    if chosen_xy is not None:
        for container in targets:
            if not container.get("canUse"):
                continue
            if approximate_hex_distance(chosen_xy, container["xy"]) > 1:
                continue
            if recent_same_loot_action(runtime, "tla_pick_item", {"itemId": container.get("id")}, now, 3000):
                continue
            option = {
                "kind": "loot_container",
                "tool": "tla_pick_item",
                "arguments": {"itemId": container.get("id")},
                "score": 74,
                "reason": "adjacent unopened loot container; open it to collect the contents",
                "entry": {key: container.get(key) for key in ("id", "protoId", "hex") if container.get(key) is not None},
                "recommendedChecks": ["tla_operate_container"],
            }
            return agent_option_decision(decision, "loot_container", option, "open the adjacent loot container", "normal", "building_entry")

    doors = closed_openable_doors(observation)
    if not doors:
        return None

    target = targets[0]
    # If the nearest loot container is already reachable, let the normal approach/loot path take it.
    if building_path_reachable(bridge, arguments, target["hex"], 1) is not False:
        return None

    target_key = f"{target['hex'].get('x')}:{target['hex'].get('y')}"
    attempts = runtime.setdefault("buildingEntryAttempts", {})
    # Only the entrance near the loot is a real candidate — a door across the map can be "reachable"
    # yet irrelevant, and walking to it abandons the lead. Rank by, and cap on, distance to the loot.
    door_candidates = sorted(
        (door for door in doors if approximate_hex_distance(safe_hex_value_xy(door.get("hex")) or (0, 0), target["xy"]) <= BUILDING_ENTRY_MAX_DOOR_DISTANCE),
        key=lambda door: approximate_hex_distance(safe_hex_value_xy(door.get("hex")) or (0, 0), target["xy"]),
    )
    for door in door_candidates:
        attempt_key = f"{target_key}|{door.get('id')}"
        if int(attempts.get(attempt_key, 0)) >= BUILDING_ENTRY_MAX_DOOR_ATTEMPTS:
            continue
        if building_path_reachable(bridge, arguments, door["hex"], 1) is not True:
            continue
        attempts[attempt_key] = int(attempts.get(attempt_key, 0)) + 1
        option = {
            "kind": "building_entry",
            "tool": "tla_pick_item",
            "arguments": {"itemId": door.get("id")},
            "score": 72,
            "reason": "loot is sealed behind a closed door; open it to reach the containers inside",
            "entry": {key: door.get(key) for key in ("id", "protoId", "hex") if door.get(key) is not None},
            "targetHex": target.get("hex"),
            "recommendedChecks": ["tla_env_path"],
        }
        return agent_option_decision(decision, "enter_building", option, "loot is enclosed; open the building door blocking the way in", "normal", "building_entry")
    return None


def agent_loot_decision(
    bridge: Any,
    decision: dict[str, Any],
    observation: dict[str, Any],
    action_suggestions: dict[str, Any],
    profile: dict[str, Any],
    runtime: dict[str, Any],
    arguments: dict[str, Any],
    now: int,
) -> dict[str, Any] | None:
    if str(profile.get("lootStyle", "")).casefold() in {"minimal", "none"}:
        return None
    loot = loot_options_payload(observation, action_suggestions, profile, {**arguments, "maxResults": 5})
    options = loot.get("options") if isinstance(loot.get("options"), list) else []
    min_score = loot_decision_min_score(profile)
    cooldown_ms = max(0, min(int(arguments.get("lootRetryCooldownMs", 3000)), 60000))
    for option in options:
        if not isinstance(option, dict):
            continue
        tool_name = str(option.get("tool") or "")
        option_arguments = option.get("arguments") if isinstance(option.get("arguments"), dict) else {}
        if tool_name not in {"tla_pick_item", "tla_pick_hex", "tla_loot_critter", "tla_operate_container"}:
            continue
        if option.get("blockedBy") or not option_arguments:
            continue
        if int(option.get("score", 0)) < min_score:
            continue
        if recent_same_loot_action(runtime, tool_name, option_arguments, now, cooldown_ms):
            continue
        approach_option = agent_loot_approach_option(bridge, observation, option, arguments)
        if isinstance(approach_option, dict):
            if approach_option.get("skip"):
                continue
            return agent_option_decision(decision, "approach_loot", approach_option, "loot target is visible but needs an adjacent standing hex before interaction", "normal", "loot_options")
        return agent_option_decision(decision, str(option.get("type") or "loot"), option, "loot style permits the highest-scored visible loot option", "normal", "loot_options")
    return None


def recent_same_loot_action(runtime: dict[str, Any], tool_name: str, arguments: dict[str, Any], now: int, window_ms: int = 3000) -> bool:
    if window_ms <= 0 or tool_name not in {"tla_pick_item", "tla_pick_hex", "tla_loot_critter", "tla_operate_container"}:
        return False
    history = runtime.get("actionHistory") if isinstance(runtime.get("actionHistory"), list) else []
    for entry in reversed(history):
        if not isinstance(entry, dict):
            continue
        try:
            age = now - int(entry.get("time") or 0)
        except (TypeError, ValueError):
            age = window_ms + 1
        if age > window_ms:
            break
        if entry.get("tool") != tool_name:
            continue
        entry_args = entry.get("arguments") if isinstance(entry.get("arguments"), dict) else {}
        if loot_action_arguments_match(tool_name, entry_args, arguments):
            return True
    return False


def loot_action_arguments_match(tool_name: str, left: dict[str, Any], right: dict[str, Any]) -> bool:
    if tool_name == "tla_pick_item":
        return str(left.get("itemId") or "") == str(right.get("itemId") or "")
    if tool_name == "tla_pick_hex":
        return safe_xy_pair(left.get("x"), left.get("y")) == safe_xy_pair(right.get("x"), right.get("y"))
    if tool_name == "tla_loot_critter":
        return str(left.get("targetId") or "") == str(right.get("targetId") or "")
    if tool_name == "tla_operate_container":
        return (
            bool(left.get("take", True)) == bool(right.get("take", True))
            and bool(left.get("all", False)) == bool(right.get("all", False))
            and int(left.get("count") or 0) == int(right.get("count") or 0)
        )
    return False


def agent_loot_approach_option(bridge: Any, observation: dict[str, Any], option: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any] | None:
    if not loot_option_requires_approach(observation, option):
        return None

    target_hex = loot_option_target_hex(option)
    if target_hex is None:
        return None

    target = {
        "targetType": str(option.get("type") or "pick_item"),
        "label": option.get("label"),
        "id": option.get("id"),
        "protoId": option.get("protoId"),
        "hex": target_hex,
        "defaultCut": 1,
    }
    approach_payload = find_approach_standing_route(bridge, arguments, target, observation)
    if not isinstance(approach_payload, dict):
        return {"skip": True}
    if "error" in approach_payload:
        return {"skip": True, "blockedBy": ["environment query failed while resolving loot approach"], "error": approach_payload.get("error")}
    if approach_payload.get("usedStandingHex") and isinstance(approach_payload.get("standingHex"), dict):
        standing_hex = approach_payload["standingHex"]
        return {
            "kind": "loot_approach",
            "type": option.get("type"),
            "label": option.get("label"),
            "tool": "tla_move_to_hex",
            "arguments": {"x": standing_hex.get("x"), "y": standing_hex.get("y")},
            "score": option.get("score"),
            "reason": approach_payload.get("reason"),
            "target": {key: target.get(key) for key in ("targetType", "id", "protoId", "hex") if target.get(key) is not None},
            "approach": {
                key: approach_payload.get(key)
                for key in ("usedStandingHex", "standingHex", "targetHex", "pathLength")
                if key in approach_payload
            },
            "recommendedChecks": ["tla_env_path", "tla_nav_plan"],
        }
    return {
        "skip": True,
        "blockedBy": ["no reachable adjacent standing hex for loot target"],
        "target": {key: target.get(key) for key in ("targetType", "id", "protoId", "hex") if target.get(key) is not None},
    }


def loot_option_requires_approach(observation: dict[str, Any], option: dict[str, Any]) -> bool:
    tool_name = str(option.get("tool") or "")
    if tool_name not in {"tla_pick_item", "tla_pick_hex", "tla_loot_critter"}:
        return False
    target_xy = safe_hex_value_xy(loot_option_target_hex(option))
    if target_xy is None:
        return False
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    origin_xy = safe_hex_value_xy(chosen.get("hex"))
    if origin_xy is None or approximate_hex_distance(origin_xy, target_xy) <= 1:
        return False
    if tool_name == "tla_loot_critter":
        return True
    item = option.get("item") if isinstance(option.get("item"), dict) else {}
    tags = item.get("tags") if isinstance(item.get("tags"), list) else []
    return any(tag in tags for tag in ("door", "container", "locker"))


def loot_option_target_hex(option: dict[str, Any]) -> dict[str, Any] | None:
    if isinstance(option.get("hex"), dict):
        return option["hex"]
    item = option.get("item") if isinstance(option.get("item"), dict) else {}
    if isinstance(item.get("hex"), dict):
        return item["hex"]
    arguments = option.get("arguments") if isinstance(option.get("arguments"), dict) else {}
    if "x" in arguments and "y" in arguments:
        return {"x": arguments.get("x"), "y": arguments.get("y")}
    return None


def loot_decision_min_score(profile: dict[str, Any]) -> int:
    style = str(profile.get("lootStyle", "practical")).casefold()
    if style in {"test-relevant", "combat", "survival"}:
        return 15
    if style in {"valuable", "trader"}:
        return 30
    return 20


def agent_global_decision(decision: dict[str, Any], observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any] | None:
    travel = travel_plan_payload(observation, action_suggestions, profile, arguments)
    plan = travel.get("plan") if isinstance(travel.get("plan"), dict) else {}
    if not plan:
        return None
    option = {"tool": plan.get("tool"), "arguments": plan.get("arguments", {}), "score": 70, "reason": plan.get("reason"), "kind": "global_travel"}
    return agent_option_decision(decision, "global_travel", option, str(plan.get("reason") or "global-map travel plan selected"), "normal", "travel_plan")


def agent_idle_decision(
    decision: dict[str, Any],
    observation: dict[str, Any],
    action_suggestions: dict[str, Any],
    profile: dict[str, Any],
    runtime: dict[str, Any],
    arguments: dict[str, Any],
    now: int,
) -> dict[str, Any] | None:
    activity = str(profile.get("activityLevel", "")).casefold()
    role = normalized_team_role(profile, 0)
    if not bool(arguments.get("preferIdle", False)) and activity not in {"hesitant", "calm", "methodical", "watchful"} and role not in {"guard"}:
        return None

    pacing = agent_idle_allowed(runtime, profile, arguments, now)
    if not bool(pacing.get("allowed", True)):
        return None

    options_payload = idle_options_payload(observation, action_suggestions, profile, arguments)
    options = options_payload.get("options") if isinstance(options_payload.get("options"), list) else []
    option = first_executable_option(options, {"tla_clear_actions", "tla_move_to_hex", "tla_toggle_sneak", "tla_say"})
    if option is None:
        return None

    intent = str(option.get("kind") or "idle")
    result = agent_option_decision(decision, intent, option, str(option.get("reason") or "idle behavior selected"), "low", "idle_options")
    result["pacing"] = pacing
    return result


def idle_options_state(bridge: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    selected_bridge = target_bridge(bridge, arguments)
    response = selected_bridge.request("observe")
    if "error" in response:
        return response
    payload = response.get("result", response)
    observation = unwrap_observation_payload(payload)
    action_suggestions = available_actions_payload(payload, observation, arguments)
    profile = agent_profile_for_target(selected_bridge)
    return {"jsonrpc": "2.0", "id": None, "result": idle_options_payload(observation, action_suggestions, profile, arguments)}


def idle_options_payload(observation: dict[str, Any], action_suggestions: dict[str, Any], profile: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    actions = action_map_from_suggestions(action_suggestions)
    activity = str(profile.get("activityLevel", "")).casefold()
    role = normalized_team_role(profile, 0)
    max_results = max(1, min(int(arguments.get("maxResults", 5)), 20))
    options: list[dict[str, Any]] = []

    if "clear_actions" in actions and action_executable(actions["clear_actions"]):
        score = 80 if activity in {"hesitant", "calm", "methodical"} else 60
        options.append(
            {
                "kind": "idle_pause",
                "label": "pause and clear queued actions",
                "tool": "tla_clear_actions",
                "arguments": {},
                "score": score,
                "reason": "human-like pause; avoid chaining unnecessary actions while reassessing",
            }
        )

    if "move_to_hex" in actions:
        for candidate in action_candidate_entries(actions["move_to_hex"])[:3]:
            arguments_payload = candidate.get("arguments") if isinstance(candidate.get("arguments"), dict) else {}
            if not arguments_payload:
                continue
            score = 45 if activity in {"calm", "methodical"} else 35
            options.append(
                {
                    "kind": "idle_wander",
                    "label": candidate.get("label", "short wander"),
                    "tool": "tla_move_to_hex",
                    "arguments": arguments_payload,
                    "score": score,
                    "reason": "small visible repositioning while idle; validate path before execution",
                    "hex": candidate.get("hex"),
                }
            )

    if "toggle_sneak" in actions and action_executable(actions["toggle_sneak"]) and (role in {"guard"} or activity in {"watchful", "methodical"}):
        options.append(
            {
                "kind": "idle_toggle_sneak",
                "label": "toggle sneak",
                "tool": "tla_toggle_sneak",
                "arguments": {},
                "score": 35,
                "reason": "watchful/cautious role can adjust stance while idle",
            }
        )

    if "say" in actions and action_executable(actions["say"]) and activity == "social":
        options.append(
            {
                "kind": "idle_small_talk",
                "label": "short visible social line",
                "tool": "tla_say",
                "arguments": {"sayType": "normal"},
                "score": 30,
                "reason": "social role may make a short visible idle remark if allowed by speech policy",
                "requiresModelText": True,
            }
        )

    options.append(
        {
            "kind": "idle_observe",
            "label": "observe quietly",
            "tool": None,
            "arguments": {},
            "score": 20,
            "reason": "no safe low-pressure idle command is required",
        }
    )
    options.sort(key=lambda entry: int(entry.get("score", 0)), reverse=True)
    return {
        "profile": {key: profile.get(key) for key in ("preset", "role", "activityLevel", "reactionProfile", "socialPolicy")},
        "options": options[:max_results],
        "guidance": "Idle options are advisory. Execute only through normal typed tools; keep visible speech role-consistent and non-spammy.",
    }


def action_executable(action: dict[str, Any]) -> bool:
    return not action.get("blockedBy") and ("example" in action or bool(action.get("candidates")))


def action_candidate_entries(action: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = action.get("candidates")
    return [entry for entry in candidates if isinstance(entry, dict)] if isinstance(candidates, list) else []


def option_is_executable(option: Any, allowed_tools: set[str] | None = None) -> bool:
    if not isinstance(option, dict):
        return False
    tool = str(option.get("tool") or option.get("suggestedTool") or "")
    if allowed_tools is not None and tool not in allowed_tools:
        return False
    if tool not in typed_command_tool_names():
        return False
    if option.get("blockedBy"):
        return False
    if option.get("requiresSlot"):
        return False
    route_memory = option.get("routeMemory") if isinstance(option.get("routeMemory"), dict) else {}
    if int(route_memory.get("recentFailures") or 0) > 0:
        return False
    if not isinstance(option.get("arguments"), dict):
        return False
    return True


def first_executable_option(options: list[Any], allowed_tools: set[str] | None = None) -> dict[str, Any] | None:
    for option in options:
        if option_is_executable(option, allowed_tools):
            return option
    return None


def executable_options(options: list[Any], allowed_tools: set[str] | None = None) -> list[dict[str, Any]]:
    return [option for option in options if option_is_executable(option, allowed_tools)]


def agent_option_decision(decision: dict[str, Any], intent: str, option: dict[str, Any], reason: str, priority: str, source: str) -> dict[str, Any]:
    decision["intent"] = intent
    decision["priority"] = priority
    decision["suggestedTool"] = option.get("tool") or option.get("suggestedTool")
    decision["arguments"] = dict(option.get("arguments", {})) if isinstance(option.get("arguments"), dict) else {}
    decision["source"] = source
    decision["option"] = {
        key: option.get(key)
        for key in ("kind", "type", "intent", "label", "score", "reason", "text", "blockedBy")
        if key in option
    }
    decision["reasons"].append(reason)
    if option.get("reasons"):
        decision["reasons"].extend(str(item) for item in option.get("reasons", [])[:4])
    if option.get("blockedBy"):
        decision["reasons"].append("option has blockers: " + ", ".join(str(item) for item in option.get("blockedBy", [])))
    return decision


def agent_tool_decision(decision: dict[str, Any], command_type: str, action: dict[str, Any], reason: str, priority: str) -> dict[str, Any]:
    decision["intent"] = command_type
    decision["priority"] = priority
    decision["suggestedTool"] = action.get("tool")
    decision["arguments"] = dict(action.get("example", {})) if isinstance(action.get("example"), dict) else {}
    decision["action"] = {key: action.get(key) for key in ("type", "description", "blockedBy") if key in action}
    decision["reasons"].append(reason)
    if action.get("blockedBy"):
        decision["reasons"].append("action has blockers: " + ", ".join(str(item) for item in action.get("blockedBy", [])))
    return decision


def action_map_from_suggestions(action_suggestions: dict[str, Any]) -> dict[str, dict[str, Any]]:
    actions = action_suggestions.get("actions") if isinstance(action_suggestions, dict) else []
    if not isinstance(actions, list):
        return {}
    return {str(action.get("type")): action for action in actions if isinstance(action, dict) and action.get("type")}


def agent_reaction_delay_ms(profile: dict[str, Any]) -> int:
    reaction = str(profile.get("reactionProfile", "normal")).strip().lower()
    activity = str(profile.get("activityLevel", "normal")).strip().lower()
    if reaction == "fast":
        base = 350
    elif reaction == "slow":
        base = 1400
    else:
        base = 800
    if activity in {"hesitant", "calm", "methodical"}:
        base += 350
    if activity in {"busy", "watchful"}:
        base -= 150
    return max(150, base)


def social_context_payload(bridge: Any, events_payload: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
    profile = agent_profile_for_target(bridge)
    heard = [analyze_speech_entry(entry, observation, profile) for entry in speech_event_entries(events_payload)]
    pending = [entry for entry in heard if entry.get("needsResponse")]
    return {
        "profile": profile,
        "heardSpeech": heard,
        "pendingResponses": pending,
        "guidance": "Use tla_say for a visible role-consistent reply when pendingResponses is not empty; avoid replying to your own speech.",
    }


def speech_event_entries(events_payload: dict[str, Any]) -> list[dict[str, Any]]:
    entries = events_payload.get("events") if isinstance(events_payload, dict) else []
    result: list[dict[str, Any]] = []
    if not isinstance(entries, list):
        return result

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        event = entry.get("event")
        if isinstance(event, dict) and event.get("type") == "say_received":
            result.append(entry)
    return result


def analyze_speech_entry(entry: dict[str, Any], observation: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    event = entry.get("event") if isinstance(entry.get("event"), dict) else {}
    speaker = event.get("critter") if isinstance(event.get("critter"), dict) else {}
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    account = observation.get("account") if isinstance(observation.get("account"), dict) else {}
    text = str(event.get("text", ""))
    say_type = str(event.get("sayType", ""))
    speaker_id = event.get("speakerId", speaker.get("id"))
    chosen_id = chosen.get("id")
    self_speech = speaker_id is not None and chosen_id is not None and str(speaker_id) == str(chosen_id)
    agent_names = agent_address_names(profile, observation)
    lower_text = text.casefold()

    mentioned_names = [name for name in agent_names if contains_phrase(lower_text, name.casefold())]
    second_person = has_marker(lower_text, SECOND_PERSON_MARKERS)
    question = has_marker(lower_text, QUESTION_MARKERS)
    request = has_marker(lower_text, REQUEST_MARKERS)
    greeting = has_marker(lower_text, GREETING_MARKERS)
    intent, intent_reasons = speech_intent(say_type, question, request, greeting)
    addressing, addressing_reasons = speech_addressing(self_speech, mentioned_names, second_person, intent, observation)
    topics = speech_topics(lower_text)
    tone = speech_emotional_tone(lower_text, say_type)
    needs_response = addressing == "likely" and (intent in {"question", "request", "greeting"} or tone.get("tone") == "hostile")
    pending_request = speech_pending_request_payload(intent, needs_response, topics, text)
    promise = speech_promise_payload(lower_text, text)

    result = {
        "seq": entry.get("seq"),
        "speaker": {
            "id": speaker_id,
            "name": event.get("speakerName", speaker.get("name", "")),
            "protoId": event.get("speakerProtoId", speaker.get("protoId", "")),
            "hex": event.get("speakerHex", speaker.get("hex")),
            "isChosen": bool(event.get("speakerIsChosen", self_speech)),
        },
        "listener": {
            "id": event.get("listenerId", chosen.get("id")),
            "name": event.get("listenerName", chosen.get("name", account.get("playerName", ""))),
        },
        "distance": event.get("distance"),
        "sayType": say_type,
        "onHeadOnly": bool(event.get("onHeadOnly")),
        "text": text,
        "selfSpeech": self_speech,
        "addressedToAgent": addressing,
        "intent": intent,
        "topics": topics,
        "emotionalTone": tone,
        "needsResponse": needs_response,
        "reasons": addressing_reasons + intent_reasons,
        "response": {
            "tool": "tla_say",
            "sayType": "normal",
            "instruction": "Answer according to the configured agent role and current situation." if needs_response else "No reply required unless your role or current objective calls for it.",
        },
    }
    if pending_request is not None:
        result["pendingRequest"] = pending_request
    if promise is not None:
        result["promise"] = promise
    return result


def agent_address_names(profile: dict[str, Any], observation: dict[str, Any]) -> list[str]:
    names: list[str] = []
    chosen = observation.get("chosen") if isinstance(observation.get("chosen"), dict) else {}
    account = observation.get("account") if isinstance(observation.get("account"), dict) else {}
    names.extend(normalize_string_list(profile.get("name")))
    names.extend(normalize_string_list(profile.get("aliases")))
    names.extend(normalize_string_list(chosen.get("name")))
    names.extend(normalize_string_list(account.get("playerName")))
    names.extend(normalize_string_list(account.get("autoLoginName")))

    result: list[str] = []
    for name in names:
        if len(name) < 2:
            continue
        if name.casefold() in {entry.casefold() for entry in result}:
            continue
        result.append(name)
    return result


def contains_phrase(text: str, phrase: str) -> bool:
    if not phrase:
        return False
    if len(phrase) <= 4 and " " not in phrase and re.fullmatch(r"\w+", phrase, flags=re.UNICODE):
        return re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", text, flags=re.UNICODE) is not None
    return phrase in text


def has_marker(text: str, markers: tuple[str, ...]) -> bool:
    return any(contains_phrase(text, marker.casefold()) for marker in markers)


def speech_intent(say_type: str, question: bool, request: bool, greeting: bool) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if say_type.endswith("Emote") or say_type.casefold() == "emote":
        return "emote", ["say type is emote"]
    if request:
        reasons.append("request/help marker")
        return "request", reasons
    if question:
        reasons.append("question marker")
        return "question", reasons
    if greeting:
        reasons.append("greeting marker")
        return "greeting", reasons
    return "statement", reasons


def speech_topics(lower_text: str) -> list[str]:
    topics: list[str] = []
    for topic, markers in SOCIAL_TOPIC_MARKERS.items():
        if has_marker(lower_text, markers):
            topics.append(topic)
    return topics


def speech_emotional_tone(lower_text: str, say_type: str) -> dict[str, Any]:
    reasons: list[str] = []
    if say_type.endswith("Emote") or say_type.casefold() == "emote":
        reasons.append("say type is emote")
    if has_marker(lower_text, HOSTILE_TONE_MARKERS):
        reasons.append("hostile marker")
        return {"tone": "hostile", "reasons": reasons}
    if has_marker(lower_text, WORRIED_TONE_MARKERS):
        reasons.append("worry/danger marker")
        return {"tone": "worried", "reasons": reasons}
    if has_marker(lower_text, POSITIVE_TONE_MARKERS) or has_marker(lower_text, GREETING_MARKERS):
        reasons.append("positive/greeting marker")
        return {"tone": "friendly", "reasons": reasons}
    return {"tone": "neutral", "reasons": reasons}


def speech_pending_request_payload(intent: str, needs_response: bool, topics: list[str], text: str) -> dict[str, Any] | None:
    if intent not in {"request", "question"} or not needs_response:
        return None
    return {
        "status": "open",
        "intent": intent,
        "topics": topics,
        "text": text,
        "requiresResponse": True,
    }


def speech_promise_payload(lower_text: str, text: str) -> dict[str, Any] | None:
    if not has_marker(lower_text, PROMISE_MARKERS):
        return None
    return {
        "status": "heard",
        "text": text,
        "topics": speech_topics(lower_text),
    }


def speech_addressing(self_speech: bool, mentioned_names: list[str], second_person: bool, intent: str, observation: dict[str, Any]) -> tuple[str, list[str]]:
    if self_speech:
        return "self", ["speaker is the controlled critter"]

    reasons: list[str] = []
    if mentioned_names:
        reasons.append("mentions agent name/alias: " + ", ".join(mentioned_names))
        return "likely", reasons

    if second_person:
        reasons.append("uses second-person wording")
        if visible_player_count(observation) <= 2 or intent in {"question", "request"}:
            return "likely", reasons
        return "possible", reasons

    if intent == "greeting":
        reasons.append("nearby visible greeting")
        return "possible", reasons

    return "unlikely", reasons


def visible_player_count(observation: dict[str, Any]) -> int:
    count = 1 if isinstance(observation.get("chosen"), dict) else 0
    critters = observation.get("critters")
    if not isinstance(critters, list):
        return count
    for critter in critters:
        if isinstance(critter, dict) and critter.get("controlledByPlayer") and not critter.get("isChosen"):
            count += 1
    return count


def launch_recipe_arguments(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    return launch_launch_recipe_arguments(name, arguments)


def build_scene_launch_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    return launch_build_scene_launch_arguments(arguments)


def build_accounts_launch_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    return launch_build_accounts_launch_arguments(arguments)


def build_two_players_launch_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    return launch_build_two_players_launch_arguments(arguments)


def copy_launch_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    return launch_copy_launch_arguments(arguments)


def set_launch_setting(arguments: dict[str, Any], name: str, value: Any) -> None:
    launch_set_launch_setting(arguments, name, value)


def launch_recipe_tool_names() -> set[str]:
    return {"tla_launch_scene", "tla_launch_accounts", "tla_launch_two_players"}


def launch_common_properties() -> dict[str, Any]:
    return {
        "role": {"type": "string", "enum": list(LAUNCH_ROLES), "description": "Process role to launch; defaults to server_headless for recipes."},
        "binaryPath": {"type": "string", "description": "Optional explicit binary path."},
        "workingDirectory": {"type": "string", "description": "Optional process working directory; defaults to workspace root."},
        "subConfig": {"type": "string", "description": "Optional -ApplySubConfig value; recipes choose a default when omitted."},
        "settings": {"type": "object", "description": "Additional engine settings passed as command-line overrides."},
        "clientCount": {"type": "integer", "minimum": 0, "maximum": 16, "description": "Embedded clients for server/server_headless launches."},
        "autoLoginName": {"type": "string", "description": "Shortcut for Auth.AutoLoginName."},
        "autoLoginPassword": {"type": "string", "description": "Shortcut for Auth.AutoLoginPassword."},
        "accounts": launch_accounts_schema(),
        "enableAiControl": {"type": "boolean", "description": "Set AiControl.Enabled and endpoint settings for launched clients."},
        "aiControlHost": {"type": "string", "description": "Shortcut for AiControl.Host."},
        "aiControlPort": {"type": "integer", "minimum": 1, "maximum": 65535, "description": "Shortcut for AiControl.Port."},
        "aiControlToken": {"type": "string", "description": "Shortcut for AiControl.Token."},
        "aiControlPortStride": {"type": "integer", "minimum": 1, "maximum": 1024, "description": "Shortcut for AiControl.PortStride."},
        "aiControl": {"type": "object", "description": "Optional object with host, port, token, and portStride."},
        "waitForBridge": {"type": "boolean", "description": "Probe launched AI bridge endpoints before returning."},
        "timeoutMs": {"type": "integer", "minimum": 0, "maximum": 120000},
        "probeIntervalMs": {"type": "integer", "minimum": 50, "maximum": 5000},
        "selectFirstEndpoint": {"type": "boolean", "description": "Select the first launched endpoint for subsequent control tools."},
    }


def launch_accounts_schema() -> dict[str, Any]:
    return {
        "type": "array",
        "description": "Explicit per-client accounts. Entries may be strings or objects with name/login/accountId and optional password.",
        "items": {
            "oneOf": [
                {"type": "string"},
                {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "login": {"type": "string"},
                        "accountId": {"type": "string"},
                        "password": {"type": "string"},
                    },
                },
            ]
        },
    }


def team_tool_properties() -> dict[str, Any]:
    return {
        "teamId": {"type": "string", "description": "Adapter-local shared team memory key."},
        "processId": {"type": "integer", "minimum": 1, "description": "Restrict the team to endpoints owned by a managed process."},
        "endpointIds": {"type": "array", "items": {"type": "string"}, "description": "Restrict the team to these endpoint ids."},
        "leaderEndpointId": {"type": "string", "description": "Endpoint id to use as the leader/rendezvous target."},
        "followerEndpointId": {"type": "string", "description": "Endpoint id that should follow the leader."},
        "followDistance": {"type": "integer", "minimum": 0, "maximum": 20, "description": "Hold instead of moving when follower is already this close by rough visible distance."},
        "validatePath": {"type": "boolean", "description": "For local-map follow/rendezvous, run tla_env_path from follower to leader before suggesting movement."},
        "pathCut": {"type": "integer", "minimum": 0, "maximum": 1000, "description": "Path query cut value; defaults to followDistance."},
        "pathTimeoutMs": {"type": "integer", "minimum": 0, "maximum": 60000, "description": "Timeout for follow path validation."},
        "execute": {"type": "boolean", "description": "When true, queue the returned follow movement through the normal typed command path."},
        "includeObservation": {"type": "boolean", "description": "Read current observations for each endpoint; default true."},
        "probeStatus": {"type": "boolean", "description": "Also read bridge status from each endpoint; default false."},
    }


def tool_list() -> list[dict[str, Any]]:
    return [
        {
            "name": "tla_launch_options",
            "title": "Read Launch Options",
            "description": "Return project-derived launch roles, subconfigs, startup scenes, and base settings available to tla_launch.",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "tla_launch_scene",
            "title": "Launch Scene",
            "description": "Launch a local server/client flow for a specific Scene.Startup value.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene": {"type": "string", "description": "Scene.Startup id, such as Intro or DevTest."},
                    **launch_common_properties(),
                },
                "required": ["scene"],
            },
        },
        {
            "name": "tla_launch_accounts",
            "title": "Launch Accounts",
            "description": "Launch local embedded clients for explicit accounts, optionally on a specific scene.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene": {"type": "string", "description": "Optional Scene.Startup id."},
                    **launch_common_properties(),
                },
                "required": ["accounts"],
            },
        },
        {
            "name": "tla_launch_two_players",
            "title": "Launch Two Players",
            "description": "Launch the two-player scene profile with two embedded controlled clients.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scene": {"type": "string", "description": "Scene.Startup id; defaults to Intro."},
                    **launch_common_properties(),
                },
            },
        },
        {
            "name": "tla_launch",
            "title": "Launch Local Game Process",
            "description": "Launch a local The Life After server/client process with command-line setting overrides and optional AI bridge probing.",
            "inputSchema": {
                "type": "object",
                "properties": launch_common_properties(),
            },
        },
        {
            "name": "tla_processes",
            "title": "List Managed Processes",
            "description": "List local processes launched by this MCP adapter instance.",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "tla_logs",
            "title": "Read Process Log Tail",
            "description": "Read the tail of a workspace or managed-process log file for bug hunting.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "processId": {"type": "integer", "minimum": 1, "description": "Optional managed process id; defaults to the workspace root."},
                    "logName": {"type": "string", "description": "Log file name such as TLA_ServerHeadless.log; paths are rejected."},
                    "lines": {"type": "integer", "minimum": 1, "maximum": 2000},
                    "maxBytes": {"type": "integer", "minimum": 1024, "maximum": 1048576},
                },
            },
        },
        {
            "name": "tla_window_screenshot",
            "title": "Capture Process Window",
            "description": "Diagnostic-only PNG screenshot of a local OS window for visual QA of particles, shaders, and GUI state. Windows local processes only.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "processId": {"type": "integer", "minimum": 1, "description": "Managed process id returned by tla_launch. Defaults to the selected managed endpoint's process when available."},
                    "endpointId": {"type": "string", "description": "Managed endpoint id returned by tla_launch or tla_endpoints; resolves to its owning process window."},
                    "osPid": {"type": "integer", "minimum": 1, "description": "Direct OS process id when the process was not launched by this adapter."},
                    "path": {"type": "string", "description": "Optional .png path inside the workspace; defaults to Workspace/AiControlScreenshots/<timestamp>-pidN.png."},
                    "mode": {
                        "type": "string",
                        "enum": ["auto", "screenClient", "screen", "printWindow"],
                        "description": "auto tries visible client-area capture before fallbacks; screenClient copies the visible client area; screen copies the visible window; printWindow asks Windows to render the window even if covered.",
                    },
                    "delayMs": {"type": "integer", "minimum": 0, "maximum": 10000, "description": "Optional delay before capture, useful after moving or opening a modal."},
                    "includeBase64": {"type": "boolean", "description": "Return base64 PNG data when the file is not larger than maxBase64Bytes; default false."},
                    "maxBase64Bytes": {"type": "integer", "minimum": 1, "maximum": 5242880, "description": "Largest PNG file to inline when includeBase64 is true; default 262144."},
                },
            },
        },
        {
            "name": "tla_save_screenshot",
            "title": "Save Engine Screenshot",
            "description": "Ask the controlled client to write its composed frame (scene + GUI, exactly what the player sees) to a .tga via the engine's own render-target readback. Unlike tla_window_screenshot this works headless and over Direct3D. Pass waitForCompletion to block until the file is written; the path is relative to the client working directory (repo root).",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Output .tga path, e.g. Workspace/AiControlScreenshots/frame.tga."}},
                "required": ["path"],
            }),
        },
        {
            "name": "tla_set_mouse_pos",
            "title": "Set Mouse Position",
            "description": "Pin the controlled client's GUI cursor at a screen pixel. The engine warps the cursor and holds it (it survives the per-frame input reset), so this is the reliable way to deterministically hover a widget — e.g. before tla_save_screenshot to capture a hover tooltip. screenX/screenY are in the client's render resolution.",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {"screenX": {"type": "integer"}, "screenY": {"type": "integer"}},
                "required": ["screenX", "screenY"],
            }),
        },
        {
            "name": "tla_show_screen",
            "title": "Show GUI Screen",
            "description": "Open a GUI screen on the controlled client by its GuiScreen enum value name (e.g. \"GameOptions\", \"Pda\", \"Character\", \"MiniMap\"). The reliable way to QA a screen's layout: open it, then tla_save_screenshot, without hunting for the button that opens it. The name is resolved via Game.TryParseEnum; an unknown name returns success=false. Screens that require parameters (Barter, Split, PickUp) are better opened through their real flow.",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {"screen": {"type": "string", "description": "GuiScreen value name, e.g. GameOptions, Pda, Character, MiniMap."}},
                "required": ["screen"],
            }),
        },
        {
            "name": "tla_hide_screen",
            "title": "Hide GUI Screen",
            "description": "Close a GUI screen on the controlled client by its GuiScreen enum value name (counterpart of tla_show_screen), e.g. to reset state between QA captures.",
            "inputSchema": with_action_wait({
                "type": "object",
                "properties": {"screen": {"type": "string", "description": "GuiScreen value name to hide."}},
                "required": ["screen"],
            }),
        },
        {
            "name": "tla_endpoints",
            "title": "List Controlled Client Endpoints",
            "description": "List bridge endpoints known to this adapter, including stable endpoint ids and per-endpoint cursors.",
            "inputSchema": {"type": "object", "properties": {"probe": {"type": "boolean", "description": "Also ping each endpoint."}}},
        },
        {
            "name": "tla_status_all",
            "title": "Read All Endpoint Statuses",
            "description": "Read bridge status from all known endpoints for multi-account orchestration.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "processId": {"type": "integer", "minimum": 1, "description": "Only read endpoints owned by this managed process."},
                    "endpointIds": {"type": "array", "items": {"type": "string"}, "description": "Only read these registered endpoint ids."},
                    "probe": {"type": "boolean", "description": "When false, only return registered endpoints."},
                },
            },
        },
        {
            "name": "tla_team_status",
            "title": "Read Team Status",
            "description": "Read profiles, runtime/memory summaries, and optional observations for a set of controlled endpoints.",
            "inputSchema": {"type": "object", "properties": team_tool_properties()},
        },
        {
            "name": "tla_team_memory",
            "title": "Read Team Memory",
            "description": "Read adapter-local shared QA/coordination memory for a team or process.",
            "inputSchema": {"type": "object", "properties": team_tool_properties()},
        },
        {
            "name": "tla_team_remember",
            "title": "Write Team Memory",
            "description": "Record an adapter-local shared team note, fact, bug, or task.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    **team_tool_properties(),
                    "kind": {"type": "string", "enum": ["note", "fact", "bug", "task"]},
                    "text": {"type": "string"},
                    "source": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "severity": {"type": "string"},
                    "properties": {"type": "object"},
                },
            },
        },
        {
            "name": "tla_team_forget",
            "title": "Clear Team Memory",
            "description": "Clear adapter-local shared team memory by kind.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    **team_tool_properties(),
                    "kind": {"type": "string", "enum": ["all", "notes", "facts", "bugs", "tasks"]},
                },
            },
        },
        {
            "name": "tla_team_assign_roles",
            "title": "Assign Team Roles",
            "description": "Set endpoint-local agent profiles for multiple controlled endpoints in one MCP call.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    **team_tool_properties(),
                    "assignments": {
                        "type": "array",
                        "description": "Per-endpoint profile assignments. Entries accept endpointId/processId+endpointIndex plus normal tla_set_agent_profile fields.",
                        "items": {"type": "object", "additionalProperties": True},
                    },
                },
                "required": ["assignments"],
            },
        },
        {
            "name": "tla_team_plan",
            "title": "Plan Team Coordination",
            "description": "Return advisory endpoint roles and a rendezvous plan without executing commands.",
            "inputSchema": {"type": "object", "properties": team_tool_properties()},
        },
        {
            "name": "tla_team_tasks",
            "title": "Plan Team Tasks",
            "description": "Return role-aware advisory task arbitration across controlled endpoints.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    **team_tool_properties(),
                    "maxResults": {"type": "integer", "minimum": 1, "maximum": 50},
                    "assignmentLimit": {"type": "integer", "minimum": 1, "maximum": 50},
                },
            },
        },
        {
            "name": "tla_group_rendezvous",
            "title": "Plan Group Rendezvous",
            "description": "Return per-endpoint typed-tool suggestions for gathering followers near the leader.",
            "inputSchema": {"type": "object", "properties": team_tool_properties()},
        },
        {
            "name": "tla_follow_agent",
            "title": "Follow Agent",
            "description": "Plan or execute one follower endpoint moving toward a leader endpoint through normal typed commands.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    **team_tool_properties(),
                    **action_wait_properties(),
                    **action_sync_properties(),
                },
                "required": ["leaderEndpointId", "followerEndpointId"],
            },
        },
        {
            "name": "tla_wait_ready",
            "title": "Wait For Endpoint Readiness",
            "description": "Poll one endpoint observation until connected/map/chosen readiness requirements are satisfied.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    **endpoint_target_properties(),
                    **readiness_properties(),
                },
            },
        },
        {
            "name": "tla_wait_all_ready",
            "title": "Wait For All Endpoint Readiness",
            "description": "Poll registered or process endpoints until all satisfy connected/map/chosen readiness requirements.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "processId": {"type": "integer", "minimum": 1, "description": "Wait all endpoints owned by this managed process."},
                    "endpointIds": {"type": "array", "items": {"type": "string"}, "description": "Specific registered endpoint ids to wait."},
                    **readiness_properties(),
                },
            },
        },
        {
            "name": "tla_select_endpoint",
            "title": "Select Controlled Client",
            "description": "Select which AI bridge endpoint subsequent observation/control tools use.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "endpointId": {"type": "string"},
                    "processId": {"type": "integer", "minimum": 1},
                    "endpointIndex": {"type": "integer", "minimum": 0},
                    "host": {"type": "string"},
                    "port": {"type": "integer", "minimum": 1, "maximum": 65535},
                    "token": {"type": "string"},
                },
            },
        },
        {
            "name": "tla_stop_process",
            "title": "Stop Managed Process",
            "description": "Terminate one process launched by this adapter, or all managed processes.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "processId": {"type": "integer", "minimum": 1},
                    "all": {"type": "boolean"},
                    "timeoutMs": {"type": "integer", "minimum": 0, "maximum": 60000},
                },
            },
        },
        {
            "name": "tla_observe",
            "title": "Read Current Game Observation",
            "description": "Return the latest structured client-side The Life After observation.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": {}}),
        },
        {
            "name": "tla_available_actions",
            "title": "Read Available Action Suggestions",
            "description": "Return advisory typed-tool suggestions and candidate arguments derived from the current observation.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "includeRawFallbacks": {"type": "boolean", "description": "Include mouse/key raw input fallback tools."},
                    "includeBlocked": {"type": "boolean", "description": "Include actions with no current candidates or known blockers; default true."},
                },
            }),
        },
        {
            "name": "tla_explain_action",
            "title": "Explain Action",
            "description": "Explain a command/tool and optionally include current-state candidate arguments from observation.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": [command["type"] for command in COMMAND_CATALOG], "description": "Command type from tla_schema commands."},
                    "commandType": {"type": "string", "enum": [command["type"] for command in COMMAND_CATALOG]},
                    "tool": {"type": "string", "description": "Typed MCP tool name, such as tla_talk_to."},
                    "staticOnly": {"type": "boolean", "description": "Return only static schema/explanation without reading observation."},
                    "includeToolSchema": {"type": "boolean", "description": "Include the typed tool input schema; default true."},
                },
            }),
        },
        {
            "name": "tla_set_agent_profile",
            "title": "Set Agent Profile",
            "description": "Set the endpoint-local AI role/persona used by MCP social context and conversation prompts.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "In-character agent name used for address detection."},
                    "displayName": {"type": "string", "description": "Optional report/display label."},
                    "aliases": {"type": "array", "items": {"type": "string"}, "description": "Other names players may use for this agent."},
                    "preset": {"type": "string", "enum": sorted(AGENT_PROFILE_PRESETS), "description": "Optional profile preset; explicit fields override preset values."},
                    "role": {"type": "string", "description": "Role/persona such as scout, trader, guard, tester, or companion."},
                    "faction": {"type": "string", "description": "Optional in-world affiliation."},
                    "stance": {"type": "string", "description": "Role stance such as neutral, friendly, cautious, or hostile."},
                    "goals": {"type": "array", "items": {"type": "string"}, "description": "Short role goals for response decisions."},
                    "taboos": {"type": "array", "items": {"type": "string"}, "description": "Role boundaries and actions to avoid."},
                    "conversationStyle": {"type": "string", "description": "Tone and length guidance for replies."},
                    "responsePolicy": {"type": "string", "description": "When the agent should answer or stay quiet."},
                    "speechStyle": {"type": "string", "description": "Visible speech style guidance."},
                    "socialPolicy": {"type": "string", "description": "Higher-level social turn-taking policy."},
                    "riskTolerance": {"type": "string", "description": "Risk preference used by advisory planners."},
                    "combatStyle": {"type": "string", "description": "Combat posture used by advisory planners."},
                    "lootStyle": {"type": "string", "description": "Loot preference used by advisory planners."},
                    "activityLevel": {"type": "string", "description": "Pacing and idle behavior tendency."},
                    "reactionProfile": {"type": "string", "description": "fast, normal, or slow reaction baseline."},
                    "skillLevel": {"type": "string", "description": "Role competence label, such as novice, average, or expert."},
                    "language": {"type": "string", "description": "Preferred reply language; russ is the project default."},
                },
            }),
        },
        {
            "name": "tla_agent_profile",
            "title": "Read Agent Profile",
            "description": "Return the endpoint-local AI role/persona used by MCP social context.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": {}}),
        },
        {
            "name": "tla_agent_memory",
            "title": "Read Agent Memory",
            "description": "Return endpoint-local advisory agent memory derived from observations/events and explicit host notes.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "includeDecisions": {"type": "boolean", "description": "Also include recent decision trace entries."},
                    "limit": {"type": "integer", "minimum": 0, "maximum": 200, "description": "Decision trace limit when includeDecisions=true."},
                },
            }),
        },
        {
            "name": "tla_agent_remember",
            "title": "Write Agent Memory",
            "description": "Add a host-provided note/fact/failure/person/place to endpoint-local agent memory.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "kind": {"type": "string", "enum": ["note", "fact", "failed_action", "person", "place", "dialog", "task_hint"]},
                    "text": {"type": "string", "description": "Text for note/fact/failed_action, or a note on person/place."},
                    "key": {"type": "string", "description": "Stable key for person/place memory."},
                    "dialogId": {"type": "string", "description": "Dialog id for dialog memory."},
                    "talkerId": {"type": ["integer", "string"], "description": "Talker id for dialog memory."},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "source": {"type": "string", "description": "Source label; defaults to manual."},
                    "properties": {"type": "object", "description": "Additional structured memory fields."},
                },
            }),
        },
        {
            "name": "tla_agent_forget",
            "title": "Clear Agent Memory",
            "description": "Clear endpoint-local memory by kind or reset all memory and decision trace.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "kind": {
                        "type": "string",
                        "enum": [
                            "all",
                            "notes",
                            "facts",
                            "people",
                            "places",
                            "dialogs",
                            "globalInterests",
                            "recentEvents",
                            "visited",
                            "visitedAreas",
                            "recentPath",
                            "knownHazards",
                            "usefulItems",
                            "interactions",
                            "combatEncounters",
                            "lootContainers",
                            "activeCollection",
                            "conversationThreads",
                            "pendingRequests",
                            "promises",
                            "doNotRetry",
                            "failedActions",
                            "dialogChoices",
                            "taskHints",
                            "travelHistory",
                            "mapTransitions",
                            "decisions",
                        ],
                    },
                    "key": {"type": "string", "description": "Optional person/place key to delete."},
                },
            }),
        },
        {
            "name": "tla_agent_memory_save",
            "title": "Save Agent Memory",
            "description": "Persist endpoint-local agent memory to Workspace/AiMemory for long QA runs.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Optional stable memory file name; defaults to the endpoint key."},
                },
            }),
        },
        {
            "name": "tla_agent_memory_load",
            "title": "Load Agent Memory",
            "description": "Load endpoint-local agent memory from Workspace/AiMemory.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Optional stable memory file name; defaults to the endpoint key."},
                },
            }),
        },
        {
            "name": "tla_agent_memory_files",
            "title": "List Saved Agent Memories",
            "description": "List JSON memory snapshots under Workspace/AiMemory.",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "tla_agent_known_people",
            "title": "Read Known People",
            "description": "Return endpoint-local people memory gathered from visible critters/speech and explicit notes.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": {}}),
        },
        {
            "name": "tla_agent_known_places",
            "title": "Read Known Places",
            "description": "Return endpoint-local place memory gathered from visible map/global-map state and explicit notes.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": {}}),
        },
        {
            "name": "tla_agent_known_dialogs",
            "title": "Read Known Dialogs",
            "description": "Return endpoint-local dialog memory and recent visible dialog choices.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": {"limit": {"type": "integer", "minimum": 0, "maximum": 200}}}),
        },
        {
            "name": "tla_idle_options",
            "title": "Read Idle Options",
            "description": "Return low-pressure advisory idle behaviors such as pause, short wander, stance adjustment, or small talk.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "includeRawFallbacks": {"type": "boolean"},
                    "includeBlocked": {"type": "boolean"},
                    "maxResults": {"type": "integer", "minimum": 1, "maximum": 20},
                },
            }),
        },
        {
            "name": "tla_agent_tick",
            "title": "Run Advisory Agent Tick",
            "description": "Read a normal tla_step, update endpoint-local memory, and return a dry-run decision trace without executing commands.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "goal": {"type": "string", "description": "Optional current goal override for this tick."},
                    **nav_target_properties(),
                    "includeStep": {"type": "boolean", "description": "Include the underlying tla_step payload; default true."},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                    "reset": {"type": "boolean", "description": "Reset the endpoint event cursor before reading."},
                    "seekLatest": {"type": "boolean", "description": "Skip retained events before reading observation."},
                    "includeStatus": {"type": "boolean", "description": "Also include bridge status inside the underlying step."},
                    "includeRawFallbacks": {"type": "boolean", "description": "Include raw fallback action suggestions in the underlying step."},
                    "includeBlocked": {"type": "boolean", "description": "Include blocked action suggestions in the underlying step; default true."},
                    "replyCooldownMs": {"type": "integer", "minimum": 0, "maximum": 60000, "description": "Cooldown for repeated replies to the same visible speech; default is role/profile based."},
                    "unsolicitedSpeechCooldownMs": {"type": "integer", "minimum": 0, "maximum": 300000, "description": "Cooldown for agent-initiated visible small talk; default 30000."},
                    "idleCooldownMs": {"type": "integer", "minimum": 0, "maximum": 60000, "description": "Cooldown for low-pressure idle actions; default is role/profile based."},
                    "preferIdle": {"type": "boolean", "description": "Allow idle behavior to outrank low-priority movement even for non-idle profiles."},
                    "maxProgressionActions": {"type": "integer", "minimum": 0, "maximum": 20, "description": "Maximum recent skill/ability changes before progression stops outranking world actions; default 3."},
                    "lootRetryCooldownMs": {"type": "integer", "minimum": 0, "maximum": 60000, "description": "Cooldown before retrying the same loot/container command; default 3000."},
                    "equipActionCooldownMs": {"type": "integer", "minimum": 0, "maximum": 60000, "description": "Cooldown before retrying the same equipment use/move command; default 3000."},
                    "combatActionCooldownMs": {"type": "integer", "minimum": 0, "maximum": 60000, "description": "Cooldown before retrying the same attack target/hex; default 1200."},
                    "humanizationSeed": {"type": "integer", "minimum": 1, "description": "Deterministic seed for skill-level hesitation/mistake cadence; default decisionId."},
                    "allowHumanizedMistakes": {"type": "boolean", "description": "Allow the skill model to suppress/alter low-priority decisions; default false keeps metadata only."},
                    "humanizedMistake": {"type": "string", "enum": sorted(AGENT_HUMANIZED_MISTAKES), "description": "Force one humanized mistake kind for deterministic tests when allowHumanizedMistakes=true."},
                    "maxAttentionEvents": {"type": "integer", "minimum": 1, "maximum": 20, "description": "Maximum high-priority focus entries in underlying tla_step attention output; default 5."},
                },
            }),
        },
        {
            "name": "tla_agent_run",
            "title": "Run Agent Loop",
            "description": "Run bounded observe/decide ticks and optionally execute the selected normal typed tools behind safety gates.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "execute": {"type": "boolean", "description": "When true, execute selected typed tools; default false."},
                    "maxSteps": {"type": "integer", "minimum": 1, "maximum": 20, "description": "Maximum observe/decide iterations; default 1."},
                    "maxActions": {"type": "integer", "minimum": 0, "maximum": 20, "description": "Maximum executed commands; default maxSteps."},
                    "goal": {"type": "string", "description": "Optional current goal override for these ticks."},
                    **nav_target_properties(),
                    "deploymentMode": {"type": "string", "enum": sorted(AGENT_DEPLOYMENT_MODES), "description": "Host-declared deployment/readiness context; default private_qa."},
                    "permissionMode": {"type": "string", "enum": sorted(AGENT_PERMISSION_MODES), "description": "Execution permission envelope; observe_only forces dry-run, raw_input_fallback is required before raw input can be enabled."},
                    "agentDisclosure": {"type": "boolean", "description": "Whether the host has marked/disclosed this agent for the selected deployment mode."},
                    "outOfBandCoordination": {"type": "boolean", "description": "Telemetry marker for QA-only coordination outside visible speech/gameplay."},
                    "policyNote": {"type": "string", "description": "Optional host note copied into policy telemetry."},
                    "stopOnNoAction": {"type": "boolean", "description": "Stop after a tick that does not execute; default true."},
                    "stopOnBlocked": {"type": "boolean", "description": "Stop after a safety/path block; default true."},
                    "respectDelay": {"type": "boolean", "description": "Sleep up to maxSleepMs between ticks using suggestedDelayMs; default false."},
                    "maxSleepMs": {"type": "integer", "minimum": 0, "maximum": 5000, "description": "Delay cap when respectDelay=true; default 1500."},
                    "minActionIntervalMs": {"type": "integer", "minimum": 0, "maximum": 60000, "description": "Minimum wall-clock gap between executed agent actions; default 0 disables this gate."},
                    "maxActionsPerMinute": {"type": "integer", "minimum": 0, "maximum": 600, "description": "Runtime back-pressure cap over the last minute; default 0 disables this gate."},
                    "schedulerJitterMs": {"type": "integer", "minimum": 0, "maximum": 10000, "description": "Deterministic extra interval added to minActionIntervalMs from schedulerSeed/decisionId."},
                    "schedulerSeed": {"type": "integer", "minimum": 1, "description": "Deterministic seed for scheduler jitter; default decisionId."},
                    "allowHighPriorityInterrupt": {"type": "boolean", "description": "Let high-priority decisions interrupt minActionIntervalMs (never the maxActionsPerMinute cap); default true."},
                    "stopOnSchedulerWait": {"type": "boolean", "description": "Stop the run when scheduler back-pressure asks the agent to wait; default true."},
                    "commandTimeoutMs": {"type": "integer", "minimum": 0, "maximum": 60000, "description": "Timeout for executed commands; default 15000."},
                    "syncAfterAction": {"type": "boolean", "description": "Sync observation after completed commands; default true."},
                    "validatePath": {"type": "boolean", "description": "Run tla_env_path before local movement; default true."},
                    "pathTimeoutMs": {"type": "integer", "minimum": 0, "maximum": 60000, "description": "Path validation timeout; default 5000."},
                    "pathCut": {"type": "integer", "minimum": 0, "description": "Optional movement cut for path validation."},
                    "allowRawInput": {"type": "boolean", "description": "Allow raw mouse/key fallback tools; default false."},
                    "allowCombat": {"type": "boolean", "description": "Allow attack tools selected by the agent; default false."},
                    "allowSpeech": {"type": "boolean", "description": "Allow visible speech when text is provided or autoReply=true; default true."},
                    "allowRosterDelete": {"type": "boolean", "description": "Allow roster deletion if ever selected; default false."},
                    "autoReply": {"type": "boolean", "description": "Use a short deterministic fallback reply for model-required speech; default false."},
                    "speechText": {"type": "string", "description": "Host-provided text for a model-required speech decision."},
                    "allowedTools": {"type": "array", "items": {"type": "string"}, "description": "Optional typed-tool allowlist."},
                    "blockedTools": {"type": "array", "items": {"type": "string"}, "description": "Optional typed-tool denylist."},
                    "enableLoopDetection": {"type": "boolean", "description": "Detect repeated decisions, repeated speech, empty idle loops, failed-action bursts, and over-aggressive retries; default true."},
                    "stopOnLoop": {"type": "boolean", "description": "Stop the run when a loop detector fires; default true."},
                    "repeatedDecisionLimit": {"type": "integer", "minimum": 2, "maximum": 20, "description": "Consecutive identical decision signatures before loop detection; default 3."},
                    "failedActionLimit": {"type": "integer", "minimum": 2, "maximum": 20, "description": "Consecutive blocked/rejected actions before loop detection; default 3."},
                    "stuckMovementLimit": {"type": "integer", "minimum": 2, "maximum": 20, "description": "Consecutive move decisions observed from the same chosen hex before stuck movement detection; default 3."},
                    "stopOnDistress": {"type": "boolean", "description": "Stop/pause the endpoint if visible speech contains a stop/distress keyword; default false."},
                    "distressKeywords": {"type": "array", "items": {"type": "string"}, "description": "Optional keyword override for stopOnDistress."},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                    "reset": {"type": "boolean"},
                    "seekLatest": {"type": "boolean"},
                    "includeStep": {"type": "boolean"},
                    "includeStatus": {"type": "boolean"},
                    "includeRawFallbacks": {"type": "boolean"},
                    "includeBlocked": {"type": "boolean"},
                    "replyCooldownMs": {"type": "integer", "minimum": 0, "maximum": 60000},
                    "unsolicitedSpeechCooldownMs": {"type": "integer", "minimum": 0, "maximum": 300000},
                    "idleCooldownMs": {"type": "integer", "minimum": 0, "maximum": 60000},
                    "preferIdle": {"type": "boolean"},
                    "maxProgressionActions": {"type": "integer", "minimum": 0, "maximum": 20},
                    "lootRetryCooldownMs": {"type": "integer", "minimum": 0, "maximum": 60000},
                    "equipActionCooldownMs": {"type": "integer", "minimum": 0, "maximum": 60000},
                    "combatActionCooldownMs": {"type": "integer", "minimum": 0, "maximum": 60000},
                    "humanizationSeed": {"type": "integer", "minimum": 1},
                    "allowHumanizedMistakes": {"type": "boolean"},
                    "humanizedMistake": {"type": "string", "enum": sorted(AGENT_HUMANIZED_MISTAKES)},
                    "maxAttentionEvents": {"type": "integer", "minimum": 1, "maximum": 20},
                },
            }),
        },
        {
            "name": "tla_agent_status",
            "title": "Read Agent Runtime Status",
            "description": "Return endpoint-local profile, runtime pause state, memory summary, and recent decisions.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "minimum": 0, "maximum": 200, "description": "Recent decision count; defaults to 10."},
                },
            }),
        },
        {
            "name": "tla_agent_decisions",
            "title": "Read Agent Decision Trace",
            "description": "Return recent endpoint-local advisory decisions produced by tla_agent_tick.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "minimum": 0, "maximum": 200},
                },
            }),
        },
        {
            "name": "tla_agent_pause",
            "title": "Pause Agent Runtime",
            "description": "Mark endpoint-local advisory agent runtime as paused. Future tla_agent_tick calls still observe but select no action.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "reason": {"type": "string"},
                },
            }),
        },
        {
            "name": "tla_agent_resume",
            "title": "Resume Agent Runtime",
            "description": "Resume endpoint-local advisory agent ticks after tla_agent_pause.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "reason": {"type": "string"},
                },
            }),
        },
        {
            "name": "tla_agent_stop",
            "title": "Stop Agent Runtime",
            "description": "Stop one endpoint-local advisory agent by marking it stopped and paused until resumed.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "reason": {"type": "string"},
                },
            }),
        },
        {
            "name": "tla_agent_stop_all",
            "title": "Stop All Agent Runtimes",
            "description": "Stop all endpoint-local advisory agent runtimes known to this adapter.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "reason": {"type": "string"},
                },
            },
        },
        {
            "name": "tla_world_summary",
            "title": "Read World Summary",
            "description": "Return a compact world model: recent changes, area, local memory, interactables, interest points, navigation options, and social counts.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                    "reset": {"type": "boolean", "description": "Reset the endpoint event cursor before reading."},
                    "seekLatest": {"type": "boolean", "description": "Skip retained events before reading observation."},
                    "includeStep": {"type": "boolean", "description": "Include the underlying tla_step payload; default false."},
                    "includeStatus": {"type": "boolean", "description": "Also include bridge status inside the underlying step."},
                    "includeRawFallbacks": {"type": "boolean"},
                    "includeBlocked": {"type": "boolean"},
                    "maxResults": {"type": "integer", "minimum": 1, "maximum": 100, "description": "Maximum interest/nav entries to return."},
                    "memoryLimit": {"type": "integer", "minimum": 1, "maximum": 50, "description": "Maximum local-memory entries per section; default 8."},
                    "maxAttentionEvents": {"type": "integer", "minimum": 1, "maximum": 20, "description": "Maximum high-priority focus entries in attention output; default 5."},
                },
            }),
        },
        {
            "name": "tla_area_summary",
            "title": "Read Area Summary",
            "description": "Return compact current map/global/chosen/counts state from the latest observation.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": {}}),
        },
        {
            "name": "tla_recent_changes",
            "title": "Read Recent World Changes",
            "description": "Return categorized bridge events from the endpoint cursor.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                    "reset": {"type": "boolean"},
                    "seekLatest": {"type": "boolean"},
                    "includeEvents": {"type": "boolean", "description": "Include raw consumed events; default true."},
                },
            }),
        },
        {
            "name": "tla_visible_interactables",
            "title": "Read Visible Interactables",
            "description": "Group visible action candidates into critters, items, inventory, dialog, global, and utility interactables.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "includeRawFallbacks": {"type": "boolean"},
                    "includeBlocked": {"type": "boolean"},
                },
            }),
        },
        {
            "name": "tla_interest_points",
            "title": "Read Interest Points",
            "description": "Return prioritized visible points of interest derived from gates, dialogs, critters, items, global interests, and usable inventory.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "includeRawFallbacks": {"type": "boolean"},
                    "includeBlocked": {"type": "boolean"},
                    "maxResults": {"type": "integer", "minimum": 1, "maximum": 100},
                    "memoryAware": {"type": "boolean", "description": "Apply endpoint-local failed-route/hazard/crowding memory to advisory scores; default true."},
                    "failureMemoryMs": {"type": "integer", "minimum": 0, "description": "Recent failed-action window used by memory-aware route scoring; default 30 minutes."},
                    "hazardRadius": {"type": "integer", "minimum": 0, "maximum": 30, "description": "Approximate remembered-hazard radius for advisory route scoring."},
                    "crowdingRadius": {"type": "integer", "minimum": 0, "maximum": 30, "description": "Visible-critter crowding radius around route targets."},
                },
            }),
        },
        {
            "name": "tla_nav_options",
            "title": "Read Navigation Options",
            "description": "Return advisory navigation/approach/global movement options from current visible action candidates.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "includeRawFallbacks": {"type": "boolean"},
                    "includeBlocked": {"type": "boolean"},
                    "maxResults": {"type": "integer", "minimum": 1, "maximum": 100},
                },
            }),
        },
        {
            "name": "tla_nav_plan",
            "title": "Plan Navigation",
            "description": "Resolve a visible or explicit map target and run client-side path/tactical/optional trace checks without executing movement.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": nav_planner_properties()}),
        },
        {
            "name": "tla_find_nearest_reachable",
            "title": "Find Nearest Reachable Target",
            "description": "Path-check visible map candidates and return the nearest reachable target/follow-up.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": nav_planner_properties()}),
        },
        {
            "name": "tla_find_safe_step",
            "title": "Find Safe Step",
            "description": "Score nearby local movement hexes with tactical path risk and return the safest current step option.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    **nav_planner_properties(),
                    "localRadius": {"type": "integer", "minimum": 1, "maximum": 8, "description": "Local hex radius around the chosen critter; default 3."},
                    "useVisibleLandmarks": {"type": "boolean", "description": "Use legacy visible move_to_hex landmarks instead of generated nearby hexes."},
                },
            }),
        },
        {
            "name": "tla_find_cover",
            "title": "Find Cover Anchors",
            "description": "Scan nearby visible obstacles and rank line-of-fire/movement blockers as cover anchors.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    **environment_from_to_properties(require_to=False),
                    "radius": {"type": "integer", "minimum": 0, "maximum": 30},
                    "maxResults": {"type": "integer", "minimum": 1, "maximum": 300},
                    **environment_query_wait_properties(),
                },
            }),
        },
        {
            "name": "tla_find_vantage",
            "title": "Find Vantage Lines",
            "description": "Trace line quality from the current or explicit source hex to visible target candidates.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    **nav_planner_properties(),
                    "maxDistance": {"type": "integer", "minimum": 0, "maximum": 200},
                    "angle": {"type": "integer", "minimum": -60, "maximum": 60},
                    "maxCritters": {"type": "integer", "minimum": 0, "maximum": 80},
                },
            }),
        },
        {
            "name": "tla_explore_options",
            "title": "Read Explore Options",
            "description": "Return client-visible exploration leads from interest points/navigation options, with optional path validation.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    **nav_planner_properties(),
                    "validatePaths": {"type": "boolean", "description": "Run tla_env_path against candidate map leads before returning them."},
                    "maxResults": {"type": "integer", "minimum": 1, "maximum": 100},
                },
            }),
        },
        {
            "name": "tla_inventory_summary",
            "title": "Read Inventory Summary",
            "description": "Group visible inventory items by heuristic tags and expose healing/reload/equip/drop quick options.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": advisory_option_properties()}),
        },
        {
            "name": "tla_loot_options",
            "title": "Read Loot Options",
            "description": "Rank visible pickup, corpse-loot, and active container options using the current agent loot style.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": advisory_option_properties()}),
        },
        {
            "name": "tla_equip_options",
            "title": "Read Equip Options",
            "description": "Suggest visible inventory equipment actions through normal use/move item tools.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": advisory_option_properties()}),
        },
        {
            "name": "tla_ammo_options",
            "title": "Read Ammo Options",
            "description": "Group visible ammo and weapon-like inventory items and show reload suggestions.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": advisory_option_properties()}),
        },
        {
            "name": "tla_healing_options",
            "title": "Read Healing Options",
            "description": "Suggest visible usable healing-like items based on current chosen health.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": advisory_option_properties()}),
        },
        {
            "name": "tla_container_options",
            "title": "Read Container Options",
            "description": "Show active container/loot UI operate options or the normal precondition to open one first.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": advisory_option_properties()}),
        },
        {
            "name": "tla_combat_options",
            "title": "Read Combat Options",
            "description": "Summarize visible combat priorities: targets, reload, healing, retreat, and cover advice.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": advisory_option_properties()}),
        },
        {
            "name": "tla_target_options",
            "title": "Read Target Options",
            "description": "Rank visible attack candidates and attach safety notes for player-controlled targets.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": advisory_option_properties()}),
        },
        {
            "name": "tla_retreat_options",
            "title": "Read Retreat Options",
            "description": "Suggest visible movement candidates or safe-step checks for tactical withdrawal.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": advisory_option_properties()}),
        },
        {
            "name": "tla_reload_options",
            "title": "Read Reload Options",
            "description": "Suggest tla_reload arguments from visible weapon-like and ammo-like inventory items.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": advisory_option_properties()}),
        },
        {
            "name": "tla_cover_options",
            "title": "Read Cover Options",
            "description": "Return the next cover-scanning command and guidance for validating standing hexes.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": advisory_option_properties()}),
        },
        {
            "name": "tla_dialog_options",
            "title": "Read Dialog Options",
            "description": "Classify visible active-dialog answers and expose tla_dialog_answer suggestions.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": advisory_option_properties()}),
        },
        {
            "name": "tla_quest_summary",
            "title": "Read Quest Summary",
            "description": "Return visible quest/task hints and explicitly report whether dedicated quest/PDA observation is exported.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": advisory_option_properties()}),
        },
        {
            "name": "tla_task_options",
            "title": "Read Task Options",
            "description": "Prioritize visible account gates, dialogs, combat, global travel, and ordinary action candidates.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": advisory_option_properties()}),
        },
        {
            "name": "tla_xp_source_plan",
            "title": "Plan XP Sources",
            "description": "Rank visible XP sources across progression spending, quests/dialogs, safe combat, supplies, travel, and exploration.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": xp_source_plan_properties()}),
        },
        {
            "name": "tla_map_transition_options",
            "title": "Read Map Transition Options",
            "description": "Summarize visible map/global transition candidates and current export gaps.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": global_advisory_properties()}),
        },
        {
            "name": "tla_global_options",
            "title": "Read Global Map Options",
            "description": "Summarize global-map interests, movement candidates, and enter candidates.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": global_advisory_properties()}),
        },
        {
            "name": "tla_travel_plan",
            "title": "Plan Global Travel",
            "description": "Select one global-map move or enter step for a visible interest or explicit position.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": global_advisory_properties()}),
        },
        {
            "name": "tla_enter_options",
            "title": "Read Global Enter Options",
            "description": "List executable in-range global-map enters and blocked visible interests.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": global_advisory_properties()}),
        },
        {
            "name": "tla_dialog_memory",
            "title": "Read Dialog Memory",
            "description": "Read/update endpoint-local memory of visible dialogs, dialog hints, and recent chosen answers.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    **advisory_option_properties(),
                    "limit": {"type": "integer", "minimum": 0, "maximum": 200},
                },
            }),
        },
        {
            "name": "tla_task_memory",
            "title": "Read Task Memory",
            "description": "Read/update endpoint-local visible task hints and current task priorities.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    **advisory_option_properties(),
                    "limit": {"type": "integer", "minimum": 0, "maximum": 200},
                },
            }),
        },
        {
            "name": "tla_route_memory",
            "title": "Read Route Memory",
            "description": "Read/update endpoint-local memory of visible global-map interests, travel attempts, and map/global transitions.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    **global_advisory_properties(),
                    "limit": {"type": "integer", "minimum": 0, "maximum": 200},
                },
            }),
        },
        {
            "name": "tla_env_path",
            "title": "Query Path Length",
            "description": "Compute client-side direct distance, path length, reachability, optional path directions, and optional path hexes between map hexes.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    **environment_from_to_properties(),
                    "cut": {"type": "integer", "minimum": 0, "maximum": 1000, "description": "Stop path this many hexes before the target; 0 means exact target."},
                    "includeDirections": {"type": "boolean", "description": "Include path direction steps; default true."},
                    "maxDirections": {"type": "integer", "minimum": 0, "maximum": 240},
                    **environment_query_wait_properties(),
                },
                "required": ["toX", "toY"],
            }),
        },
        {
            "name": "tla_env_trace",
            "title": "Trace Line",
            "description": "Trace a client-side line toward a target hex and report the last reached hex plus visible critters in path.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    **environment_from_to_properties(),
                    "maxDistance": {"type": "integer", "minimum": 0, "maximum": 200, "description": "Trace distance; defaults to direct distance."},
                    "angle": {"type": "integer", "minimum": -60, "maximum": 60, "description": "Trace angle offset in degrees."},
                    "maxCritters": {"type": "integer", "minimum": 0, "maximum": 80},
                    **environment_query_wait_properties(),
                },
                "required": ["toX", "toY"],
            }),
        },
        {
            "name": "tla_env_obstacles",
            "title": "Scan Obstacles",
            "description": "Scan nearby map hexes for movement/shooting blockers, critters, and items.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    **environment_from_to_properties(require_to=False),
                    "radius": {"type": "integer", "minimum": 0, "maximum": 30, "description": "Hex radius to scan; defaults to 6."},
                    "maxResults": {"type": "integer", "minimum": 1, "maximum": 300},
                    **environment_query_wait_properties(),
                },
            }),
        },
        {
            "name": "tla_env_tactical_path",
            "title": "Query Tactical Path",
            "description": "Estimate path length and route risk around visible hostile-looking critters, with a bounded detour search.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    **environment_from_to_properties(),
                    "cut": {"type": "integer", "minimum": 0, "maximum": 1000},
                    "avoidRadius": {"type": "integer", "minimum": 0, "maximum": 30, "description": "Threat influence radius; defaults to 6."},
                    "searchRadius": {"type": "integer", "minimum": 0, "maximum": 25, "description": "Waypoint search radius around route midpoint; defaults to 10."},
                    "hazardWeight": {"type": "integer", "minimum": 0, "maximum": 100, "description": "Score multiplier for risk; defaults to 4."},
                    "maxCandidates": {"type": "integer", "minimum": 1, "maximum": 500, "description": "Maximum movable waypoint candidates checked during detour search; defaults to 64."},
                    "avoidPlayers": {"type": "boolean", "description": "Treat visible player-controlled critters as avoid threats too; default false."},
                    "maxThreats": {"type": "integer", "minimum": 0, "maximum": 80},
                    **environment_query_wait_properties(),
                },
                "required": ["toX", "toY"],
            }),
        },
        {
            "name": "tla_sync",
            "title": "Read Events And Observation",
            "description": "Return next events, a fresh observation, and speech-focused social context in one MCP call.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                    "reset": {"type": "boolean", "description": "Reset the adapter event cursor to 0 before reading."},
                    "seekLatest": {"type": "boolean", "description": "Advance the adapter event cursor to the latest bridge sequence before reading observation."},
                    "includeStatus": {"type": "boolean", "description": "Also include bridge status."},
                    "maxAttentionEvents": {"type": "integer", "minimum": 1, "maximum": 20, "description": "Maximum high-priority focus entries in attention output; default 5."},
                    **endpoint_target_properties(),
                },
            },
        },
        {
            "name": "tla_social_context",
            "title": "Read Social Context",
            "description": "Return speech-focused address/intent analysis from visible say_received events and the configured agent profile.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                    "reset": {"type": "boolean", "description": "Reset the adapter event cursor to 0 before reading."},
                    "seekLatest": {"type": "boolean", "description": "Advance the adapter event cursor to the latest bridge sequence before reading observation."},
                    "includeEvents": {"type": "boolean", "description": "Include the consumed raw event payload; default true."},
                    "includeObservation": {"type": "boolean", "description": "Include the fresh observation payload; default true."},
                    **endpoint_target_properties(),
                },
            },
        },
        {
            "name": "tla_conversation_state",
            "title": "Read Conversation State",
            "description": "Build conversation threads, pending replies, and relation context from visible speech events.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                    "reset": {"type": "boolean"},
                    "seekLatest": {"type": "boolean"},
                    "includeEvents": {"type": "boolean", "description": "Include consumed raw events; default true."},
                    "includeObservation": {"type": "boolean", "description": "Include fresh observation; default true."},
                    "updateMemory": {"type": "boolean", "description": "Remember visible speakers in endpoint-local memory; default true."},
                    "maxThreads": {"type": "integer", "minimum": 1, "maximum": 100},
                },
            }),
        },
        {
            "name": "tla_reply_options",
            "title": "Read Reply Options",
            "description": "Return advisory role-aware reply options for the selected or highest-priority visible conversation thread.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                    "reset": {"type": "boolean"},
                    "seekLatest": {"type": "boolean"},
                    "threadId": {"type": "string"},
                    "sayType": {"type": "string", "enum": list(SAY_TYPE_VALUES)},
                    "updateMemory": {"type": "boolean"},
                    "maxThreads": {"type": "integer", "minimum": 1, "maximum": 100},
                },
            }),
        },
        {
            "name": "tla_relation_note",
            "title": "Remember Relation Note",
            "description": "Store or update endpoint-local relationship memory for a visible speaker/player/NPC.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Stable relation key; speakerId/targetId may be used instead."},
                    "speakerId": {"type": ["integer", "string"]},
                    "targetId": {"type": ["integer", "string"]},
                    "name": {"type": "string"},
                    "attitude": {"type": "string"},
                    "trust": {"type": ["integer", "number", "string"]},
                    "hostility": {"type": ["integer", "number", "string"]},
                    "relation": {"type": "string"},
                    "note": {"type": "string"},
                    "text": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "source": {"type": "string"},
                },
            }),
        },
        {
            "name": "tla_agent_say_planned",
            "title": "Say Planned Reply",
            "description": "Wrap tla_say with conversation metadata, optional dry-run, and optional host-controlled delay.",
            "inputSchema": with_endpoint_target({
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "sayType": {"type": "string", "enum": list(SAY_TYPE_VALUES)},
                    "threadId": {"type": "string"},
                    "reason": {"type": "string"},
                    "decisionId": {"type": ["integer", "string"]},
                    "delayMs": {"type": "integer", "minimum": 0, "maximum": 60000},
                    "suggestedDelayMs": {"type": "integer", "minimum": 0, "maximum": 60000},
                    "dryRun": {"type": "boolean"},
                    "respectDelay": {"type": "boolean", "description": "Sleep up to 5s before sending; default false."},
                    **action_wait_properties(),
                    **action_sync_properties(),
                },
                "required": ["text"],
            }),
        },
        {
            "name": "tla_step",
            "title": "Read Agent Step",
            "description": "Return next events, a fresh observation, action suggestions, and speech-focused social context in one MCP call.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                    "reset": {"type": "boolean", "description": "Reset the adapter event cursor to 0 before reading."},
                    "seekLatest": {"type": "boolean", "description": "Advance the adapter event cursor to the latest bridge sequence before reading observation."},
                    "includeStatus": {"type": "boolean", "description": "Also include bridge status."},
                    "includeRawFallbacks": {"type": "boolean", "description": "Include mouse/key raw input fallback tools in actionSuggestions."},
                    "includeBlocked": {"type": "boolean", "description": "Include actions with no current candidates or known blockers; default true."},
                    "maxAttentionEvents": {"type": "integer", "minimum": 1, "maximum": 20, "description": "Maximum high-priority focus entries in attention output; default 5."},
                    **endpoint_target_properties(),
                },
            },
        },
        {
            "name": "tla_events",
            "title": "Read Game Events",
            "description": "Return AI bridge events after a sequence number.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "afterSeq": {"type": "integer", "minimum": 0},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                    **endpoint_target_properties(),
                },
            },
        },
        {
            "name": "tla_next_events",
            "title": "Read Next Game Events",
            "description": "Return game events after the adapter's remembered cursor and advance that cursor.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                    "reset": {"type": "boolean", "description": "Reset the adapter event cursor to 0 before reading."},
                    "seekLatest": {"type": "boolean", "description": "Advance the adapter event cursor to the latest bridge sequence without returning retained events."},
                    **endpoint_target_properties(),
                },
            },
        },
        {
            "name": "tla_wait_command",
            "title": "Wait For Command Completion",
            "description": "Poll game events until the requested command_completed event arrives or a timeout elapses.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "commandSeq": {"type": "integer", "minimum": 1},
                    "timeoutMs": {"type": "integer", "minimum": 0, "maximum": 60000},
                    "pollIntervalMs": {"type": "integer", "minimum": 0, "maximum": 5000},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                    "includeEvents": {"type": "boolean", "description": "Include events consumed while waiting in the result."},
                    "maxReturnedEvents": {"type": "integer", "minimum": 0, "maximum": 1000},
                    **endpoint_target_properties(),
                },
                "required": ["commandSeq"],
            },
        },
        *typed_command_tools(),
        {
            "name": "tla_act_and_sync",
            "title": "Queue Command And Sync",
            "description": "Queue a semantic command, wait for completion, then return a fresh observation/status snapshot.",
            "inputSchema": act_input_schema(),
        },
        {
            "name": "tla_act",
            "title": "Queue Game Command",
            "description": "Queue a semantic command for the connected The Life After client.",
            "inputSchema": act_input_schema(),
        },
        {
            "name": "tla_schema",
            "title": "Read Protocol Schema",
            "description": "Return static descriptions of command, observation, event, and bridge protocol formats.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "section": {
                        "type": "string",
                        "enum": ["all", "protocol", "commands", "observation", "events", "social", "agent", "world", "environment", "orchestration", "team"],
                        "description": "Schema section to return.",
                    }
                },
            },
        },
        {
            "name": "tla_status",
            "title": "Read Bridge Status",
            "description": "Return bridge status and queue sizes.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": {}}),
        },
        {
            "name": "tla_ping",
            "title": "Ping Bridge",
            "description": "Check whether the game bridge is reachable.",
            "inputSchema": with_endpoint_target({"type": "object", "properties": {}}),
        },
    ]


def resource_list() -> list[dict[str, str]]:
    return [
        {
            "uri": OPERATOR_GUIDE_URI,
            "name": "operator_guide",
            "title": "AI Operator Guide",
            "description": "Short host-facing guide for controlling the client through MCP.",
            "mimeType": "text/markdown",
        },
        {
            "uri": AGENT_EXAMPLES_URI,
            "name": "agent_examples",
            "title": "Agent Authoring Examples",
            "description": "Ready-to-adapt QA, wanderer, social helper, combat scout, and trader profiles.",
            "mimeType": "text/markdown",
        },
        {
            "uri": "tla://schema/all",
            "name": "schema_all",
            "title": "AI Control Schema",
            "description": "Static protocol, command, observation, and event schema.",
            "mimeType": "application/json",
        },
        {
            "uri": "tla://schema/protocol",
            "name": "schema_protocol",
            "title": "Bridge Protocol Schema",
            "description": "Static bridge and MCP protocol description.",
            "mimeType": "application/json",
        },
        {
            "uri": "tla://schema/commands",
            "name": "schema_commands",
            "title": "Command Schema",
            "description": "Static command catalog and argument meanings.",
            "mimeType": "application/json",
        },
        {
            "uri": "tla://schema/observation",
            "name": "schema_observation",
            "title": "Observation Schema",
            "description": "Static observation field descriptions.",
            "mimeType": "application/json",
        },
        {
            "uri": "tla://schema/events",
            "name": "schema_events",
            "title": "Event Schema",
            "description": "Static event catalog and payload meanings.",
            "mimeType": "application/json",
        },
        {
            "uri": "tla://schema/social",
            "name": "schema_social",
            "title": "Social Context Schema",
            "description": "Static conversation-awareness profile, speech, address, and intent schema.",
            "mimeType": "application/json",
        },
        {
            "uri": "tla://schema/agent",
            "name": "schema_agent",
            "title": "Agent Runtime Schema",
            "description": "Static advisory agent profile, memory, runtime, and decision-trace schema.",
            "mimeType": "application/json",
        },
        {
            "uri": "tla://schema/world",
            "name": "schema_world",
            "title": "World Model Schema",
            "description": "Static world summary, recent changes, interactables, interest points, and navigation option schema.",
            "mimeType": "application/json",
        },
        {
            "uri": "tla://schema/environment",
            "name": "schema_environment",
            "title": "Environment Query Schema",
            "description": "Static map geometry, path, trace, obstacle, and tactical-path query schema.",
            "mimeType": "application/json",
        },
        {
            "uri": "tla://schema/orchestration",
            "name": "schema_orchestration",
            "title": "Launch Orchestration Schema",
            "description": "Static local launch and endpoint-selection schema.",
            "mimeType": "application/json",
        },
        {
            "uri": "tla://schema/team",
            "name": "schema_team",
            "title": "Team Coordination Schema",
            "description": "Static multi-endpoint team status, role assignment, and rendezvous schema.",
            "mimeType": "application/json",
        },
        {
            "uri": "tla://launch/options",
            "name": "launch_options",
            "title": "Project Launch Options",
            "description": "Project-derived subconfigs, startup scenes, and launch defaults for tla_launch.",
            "mimeType": "application/json",
        },
        {
            "uri": "tla://observation/current",
            "name": "current_observation",
            "title": "Current Observation",
            "description": "Latest structured The Life After client observation.",
            "mimeType": "application/json",
        },
        {
            "uri": "tla://events/recent",
            "name": "recent_events",
            "title": "Recent Events",
            "description": "Recent bridge events.",
            "mimeType": "application/json",
        },
        {
            "uri": "tla://status",
            "name": "status",
            "title": "Bridge Status",
            "description": "AI control bridge status.",
            "mimeType": "application/json",
        },
        {
            "uri": "tla://endpoints",
            "name": "endpoints",
            "title": "Controlled Endpoints",
            "description": "Registered AI bridge endpoints and selected endpoint id.",
            "mimeType": "application/json",
        },
    ]


def prompt_list() -> list[dict[str, Any]]:
    return [
        {
            "name": OPERATOR_GUIDE_PROMPT,
            "title": "The Life After AI Operator Guide",
            "description": "Bootstrap instructions for using the The Life After AI control MCP tools.",
            "arguments": [],
        },
        {
            "name": CONVERSATION_GUIDE_PROMPT,
            "title": "The Life After Conversation Guide",
            "description": "Role-aware instructions for hearing nearby speech and replying in character.",
            "arguments": [
                {"name": "agentName", "description": "Optional in-character agent name.", "required": False},
                {"name": "agentRole", "description": "Optional role/persona to follow.", "required": False},
                {"name": "goals", "description": "Optional short role goals.", "required": False},
                {"name": "conversationStyle", "description": "Optional reply tone/length guidance.", "required": False},
            ],
        },
        {
            "name": AGENT_EXAMPLES_PROMPT,
            "title": "The Life After Agent Examples",
            "description": AGENT_EXAMPLES_PROMPT_DESCRIPTION,
            "arguments": [],
        },
    ]


def handle_request(bridge: Bridge, request: dict[str, Any]) -> dict[str, Any] | None:
    request_id = request.get("id")
    method = request.get("method")

    if request_id is None and isinstance(method, str) and method.startswith("notifications/"):
        return None

    if method == "initialize":
        params = request.get("params", {})
        return mcp_result(
            request_id,
            {
                "protocolVersion": params.get("protocolVersion", MCP_VERSION),
                "capabilities": {
                    "tools": {"listChanged": False},
                    "resources": {"subscribe": False, "listChanged": False},
                    "prompts": {"listChanged": False},
                },
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        )

    if method == "ping":
        return mcp_result(request_id, {})

    if method == "tools/list":
        return mcp_result(request_id, {"tools": tool_list()})

    if method == "resources/list":
        return mcp_result(request_id, {"resources": resource_list()})

    if method == "resources/read":
        uri = request.get("params", {}).get("uri")
        schema_prefix = "tla://schema/"
        if isinstance(uri, str) and uri.startswith(schema_prefix):
            payload = schema_payload(uri.removeprefix(schema_prefix))
        elif uri == OPERATOR_GUIDE_URI:
            return mcp_result(
                request_id,
                {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "text/markdown",
                            "text": operator_guide_text(),
                        }
                    ]
                },
            )
        elif uri == AGENT_EXAMPLES_URI:
            return mcp_result(
                request_id,
                {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "text/markdown",
                            "text": agent_examples_text(),
                        }
                    ]
                },
            )
        elif uri == "tla://observation/current":
            response = target_bridge(bridge, {}).request("observe")
            payload = response.get("error") if "error" in response else response.get("result", response)
        elif uri == "tla://events/recent":
            response = target_bridge(bridge, {}).request("events", {"afterSeq": 0, "limit": 100})
            payload = response.get("error") if "error" in response else response.get("result", response)
        elif uri == "tla://status":
            response = target_bridge(bridge, {}).request("status")
            payload = response.get("error") if "error" in response else response.get("result", response)
        elif uri == "tla://endpoints":
            payload = endpoint_summary(bridge)
        elif uri == "tla://launch/options":
            payload = build_launch_options(workspace_root_for_bridge(bridge))
        else:
            return mcp_error(request_id, -32602, f"Unknown resource uri: {uri}")

        return mcp_result(
            request_id,
            {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(payload, ensure_ascii=False, indent=2),
                    }
                ]
            },
        )

    if method == "prompts/list":
        return mcp_result(request_id, {"prompts": prompt_list()})

    if method == "prompts/get":
        params = request.get("params", {})
        name = params.get("name")
        arguments = params.get("arguments") if isinstance(params.get("arguments"), dict) else {}
        if name not in {OPERATOR_GUIDE_PROMPT, CONVERSATION_GUIDE_PROMPT, AGENT_EXAMPLES_PROMPT}:
            return mcp_error(request_id, -32602, f"Unknown prompt: {name}")

        if name == CONVERSATION_GUIDE_PROMPT:
            text = conversation_guide_text(
                str(arguments.get("agentName", "")),
                str(arguments.get("agentRole", "")),
                str(arguments.get("goals", "")),
                str(arguments.get("conversationStyle", "")),
            )
            description = "Role-aware instructions for hearing nearby speech and replying in character."
        elif name == AGENT_EXAMPLES_PROMPT:
            text = agent_examples_text()
            description = AGENT_EXAMPLES_PROMPT_DESCRIPTION
        else:
            text = operator_guide_text()
            description = "Bootstrap instructions for using the The Life After AI control MCP tools."

        return mcp_result(
            request_id,
            {
                "description": description,
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": text,
                        },
                    }
                ],
            },
        )

    if method == "tools/call":
        params = request.get("params", {})
        name = params.get("name")
        arguments = params.get("arguments") or {}

        if name == "tla_launch_options":
            response = {"jsonrpc": "2.0", "id": None, "result": build_launch_options(workspace_root_for_bridge(bridge))}
        elif name in launch_recipe_tool_names():
            try:
                response = {"jsonrpc": "2.0", "id": None, "result": require_orchestrator(bridge).launch(bridge, launch_recipe_arguments(str(name), arguments))}
            except (FileNotFoundError, ValueError) as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_launch":
            try:
                response = {"jsonrpc": "2.0", "id": None, "result": require_orchestrator(bridge).launch(bridge, arguments)}
            except (FileNotFoundError, ValueError) as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_processes":
            response = {"jsonrpc": "2.0", "id": None, "result": {"processes": require_orchestrator(bridge).list_processes()}}
        elif name == "tla_logs":
            try:
                response = process_log_tail(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_window_screenshot":
            try:
                response = process_window_screenshot(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
            except OSError as exc:
                return mcp_error(request_id, -32000, str(exc))
        elif name == "tla_save_screenshot":
            try:
                screenshot_path = non_empty_string(arguments.get("path"), "path")
                response = act_with_optional_wait(
                    target_bridge(bridge, arguments), {"type": "save_screenshot", "stringArg": screenshot_path}, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_set_mouse_pos":
            try:
                require_arguments(arguments, "screenX", "screenY")
                response = act_with_optional_wait(
                    target_bridge(bridge, arguments),
                    {"type": "set_mouse_pos", "screenX": arguments["screenX"], "screenY": arguments["screenY"]}, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_show_screen":
            try:
                screen_name = non_empty_string(arguments.get("screen"), "screen")
                response = act_with_optional_wait(
                    target_bridge(bridge, arguments), {"type": "show_screen", "stringArg": screen_name}, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_hide_screen":
            try:
                screen_name = non_empty_string(arguments.get("screen"), "screen")
                response = act_with_optional_wait(
                    target_bridge(bridge, arguments), {"type": "hide_screen", "stringArg": screen_name}, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_endpoints":
            response = {"jsonrpc": "2.0", "id": None, "result": endpoint_summary(bridge, bool(arguments.get("probe", False)))}
        elif name == "tla_status_all":
            try:
                response = {"jsonrpc": "2.0", "id": None, "result": status_all_endpoints(bridge, arguments)}
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_team_status":
            try:
                response = team_status_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_team_memory":
            try:
                response = read_team_memory_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_team_remember":
            try:
                response = remember_team_memory_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_team_forget":
            try:
                response = forget_team_memory_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_team_assign_roles":
            try:
                response = team_assign_roles_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_team_plan":
            try:
                response = team_plan_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_team_tasks":
            try:
                response = team_tasks_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_group_rendezvous":
            try:
                response = group_rendezvous_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_follow_agent":
            try:
                response = follow_agent_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_wait_ready":
            try:
                response = wait_ready(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_wait_all_ready":
            try:
                response = wait_all_ready(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_select_endpoint":
            try:
                orchestrator = getattr(bridge, "orchestrator", None)
                if isinstance(orchestrator, Orchestrator):
                    select_result = orchestrator.select_endpoint(bridge, arguments)
                else:
                    if "endpointId" in arguments:
                        select_result = {"selectedEndpoint": select_bridge_endpoint(bridge, resolve_target_endpoint(bridge, arguments))}
                    elif "processId" in arguments:
                        raise ValueError("Managed process endpoint selection requires launch orchestration")
                    elif "port" not in arguments:
                        raise ValueError("Pass processId + endpointIndex or direct host/port")
                    else:
                        endpoint = {
                            "host": str(arguments.get("host", getattr(bridge, "host", "127.0.0.1"))),
                            "port": int(arguments["port"]),
                            "token": str(arguments.get("token", getattr(bridge, "token", ""))),
                        }
                        select_result = {"selectedEndpoint": select_bridge_endpoint(bridge, endpoint)}
                response = {"jsonrpc": "2.0", "id": None, "result": select_result}
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_stop_process":
            try:
                process_id = int(arguments["processId"]) if "processId" in arguments else None
                response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "result": require_orchestrator(bridge).stop(process_id, bool(arguments.get("all")), int(arguments.get("timeoutMs", 5000))),
                }
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_observe":
            try:
                response = target_bridge(bridge, arguments).request("observe")
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_available_actions":
            try:
                response = available_actions(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
            except OSError as exc:
                return mcp_error(request_id, -32000, str(exc))
        elif name == "tla_explain_action":
            try:
                response = explain_action(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_set_agent_profile":
            try:
                response = {"jsonrpc": "2.0", "id": None, "result": set_agent_profile(bridge, arguments)}
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_agent_profile":
            try:
                response = {"jsonrpc": "2.0", "id": None, "result": read_agent_profile(bridge, arguments)}
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_agent_memory":
            try:
                response = {"jsonrpc": "2.0", "id": None, "result": read_agent_memory(bridge, arguments)}
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_agent_remember":
            try:
                response = {"jsonrpc": "2.0", "id": None, "result": remember_agent_memory(bridge, arguments)}
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_agent_forget":
            try:
                response = {"jsonrpc": "2.0", "id": None, "result": forget_agent_memory(bridge, arguments)}
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_agent_memory_save":
            try:
                response = {"jsonrpc": "2.0", "id": None, "result": save_agent_memory(bridge, arguments)}
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_agent_memory_load":
            try:
                response = {"jsonrpc": "2.0", "id": None, "result": load_agent_memory(bridge, arguments)}
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_agent_memory_files":
            try:
                response = {"jsonrpc": "2.0", "id": None, "result": list_agent_memory_files(bridge, arguments)}
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_agent_known_people":
            try:
                response = {"jsonrpc": "2.0", "id": None, "result": agent_known_people(bridge, arguments)}
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_agent_known_places":
            try:
                response = {"jsonrpc": "2.0", "id": None, "result": agent_known_places(bridge, arguments)}
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_agent_known_dialogs":
            try:
                response = {"jsonrpc": "2.0", "id": None, "result": agent_known_dialogs(bridge, arguments)}
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_idle_options":
            try:
                response = idle_options_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_agent_tick":
            try:
                response = agent_tick_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_agent_run":
            try:
                response = agent_run_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_agent_status":
            try:
                response = agent_status_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_agent_decisions":
            try:
                endpoint = resolve_target_endpoint(bridge, arguments)
                key = agent_profile_key(bridge, endpoint)
                response = {"jsonrpc": "2.0", "id": None, "result": {"endpoint": endpoint, "key": key, "decisions": agent_decisions_for_key(bridge, key, int(arguments.get("limit", 20)))}}
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_agent_pause":
            try:
                response = set_agent_paused_state(bridge, arguments, True)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_agent_resume":
            try:
                response = set_agent_paused_state(bridge, arguments, False)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_agent_stop":
            try:
                response = stop_agent_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_agent_stop_all":
            try:
                response = stop_all_agents_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_world_summary":
            try:
                response = world_summary_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_area_summary":
            try:
                response = area_summary_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_recent_changes":
            try:
                response = recent_changes_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_visible_interactables":
            try:
                response = visible_interactables_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_interest_points":
            try:
                response = interest_points_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_nav_options":
            try:
                response = nav_options_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_nav_plan":
            try:
                response = nav_plan_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_find_nearest_reachable":
            try:
                response = find_nearest_reachable_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_find_safe_step":
            try:
                response = find_safe_step_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_find_cover":
            try:
                response = find_cover_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_find_vantage":
            try:
                response = find_vantage_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_explore_options":
            try:
                response = explore_options_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_inventory_summary":
            try:
                response = inventory_summary_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_loot_options":
            try:
                response = loot_options_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_equip_options":
            try:
                response = equip_options_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_ammo_options":
            try:
                response = ammo_options_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_healing_options":
            try:
                response = healing_options_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_container_options":
            try:
                response = container_options_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_combat_options":
            try:
                response = combat_options_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_target_options":
            try:
                response = target_options_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_retreat_options":
            try:
                response = retreat_options_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_reload_options":
            try:
                response = reload_options_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_cover_options":
            try:
                response = cover_options_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_dialog_options":
            try:
                response = dialog_options_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_quest_summary":
            try:
                response = quest_summary_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_task_options":
            try:
                response = task_options_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_xp_source_plan":
            try:
                response = xp_source_plan_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_map_transition_options":
            try:
                response = map_transition_options_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_global_options":
            try:
                response = global_options_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_travel_plan":
            try:
                response = travel_plan_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_enter_options":
            try:
                response = enter_options_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_dialog_memory":
            try:
                response = dialog_memory_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_task_memory":
            try:
                response = task_memory_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_route_memory":
            try:
                response = route_memory_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name in {"tla_env_path", "tla_env_trace", "tla_env_obstacles", "tla_env_tactical_path"}:
            try:
                response = environment_query(target_bridge(bridge, arguments), environment_query_type_for_tool(str(name)), arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_sync":
            try:
                response = sync_state(target_bridge(bridge, arguments), arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_social_context":
            try:
                response = social_context_state(target_bridge(bridge, arguments), arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_conversation_state":
            try:
                response = conversation_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_reply_options":
            try:
                response = reply_options_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_relation_note":
            try:
                response = relation_note_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_agent_say_planned":
            try:
                response = agent_say_planned_state(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_step":
            try:
                response = step_state(target_bridge(bridge, arguments), arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_events":
            try:
                response = target_bridge(bridge, arguments).request("events", {key: value for key, value in arguments.items() if key not in ENDPOINT_TARGET_ARGUMENTS})
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_next_events":
            try:
                selected_bridge = target_bridge(bridge, arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
            if arguments.get("reset"):
                selected_bridge.events_cursor = 0
            after_seq = 9223372036854775807 if arguments.get("seekLatest") else selected_bridge.events_cursor
            response = selected_bridge.request("events", {"afterSeq": after_seq, "limit": arguments.get("limit", 100)})
            advance_events_cursor(selected_bridge, response)
        elif name == "tla_wait_command":
            try:
                response = wait_command_completion(target_bridge(bridge, arguments), arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_act_and_sync":
            try:
                action_arguments = dict(arguments)
                action_arguments.setdefault("waitForCompletion", True)
                action_arguments.setdefault("syncAfterCompletion", True)
                response = act_with_optional_wait(target_bridge(bridge, action_arguments), action_command_payload(action_arguments), action_arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_act":
            try:
                response = act_with_optional_wait(target_bridge(bridge, arguments), action_command_payload(arguments), arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name in typed_command_tool_names():
            try:
                if name == "tla_dialog_answer":
                    response = dialog_answer_with_memory(bridge, arguments)
                elif name == "tla_global_move_to":
                    response = global_move_with_memory(bridge, arguments)
                elif name == "tla_global_enter_interest":
                    response = global_enter_with_memory(bridge, arguments)
                else:
                    response = act_with_optional_wait(target_bridge(bridge, arguments), typed_command_payload(name, arguments), arguments)
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_schema":
            section = arguments.get("section", "all")
            return mcp_result(request_id, {"content": [{"type": "text", "text": json.dumps(schema_payload(section), ensure_ascii=False, indent=2)}]})
        elif name == "tla_status":
            try:
                response = target_bridge(bridge, arguments).request("status")
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        elif name == "tla_ping":
            try:
                response = target_bridge(bridge, arguments).request("ping")
            except ValueError as exc:
                return mcp_error(request_id, -32602, str(exc))
        else:
            return mcp_error(request_id, -32602, f"Unknown tool: {name}")

        return mcp_result(request_id, bridge_text_result(response))

    return mcp_error(request_id, -32601, f"Unknown method: {method}")


def configure_stdio() -> None:
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


def main() -> int:
    configure_stdio()

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.environ.get("TLA_AI_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("TLA_AI_PORT", "43011")))
    parser.add_argument("--token", default=os.environ.get("TLA_AI_TOKEN", ""))
    parser.add_argument("--timeout", type=float, default=float(os.environ.get("TLA_AI_TIMEOUT", "3")))
    parser.add_argument("--workspace-root", default=os.environ.get("TLA_WORKSPACE_ROOT", str(DEFAULT_WORKSPACE_ROOT)))
    args = parser.parse_args()

    bridge = Bridge(args.host, args.port, args.token, args.timeout, Path(args.workspace_root))

    for line in sys.stdin:
        if not line.strip():
            continue

        try:
            request = json.loads(line)
            response = handle_request(bridge, request)
        except Exception as exc:  # noqa: BLE001 - MCP adapters should keep stdio alive.
            response = mcp_error(None, -32000, str(exc))

        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
            sys.stdout.flush()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
