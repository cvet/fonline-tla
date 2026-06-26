#!/usr/bin/env python3
"""Shared advisory helpers for the The Life After AI-control MCP adapter."""

from __future__ import annotations

import re
from typing import Any


XP_GOAL_MARKERS = (
    "level up",
    "level-up",
    "level to",
    "reach level",
    "target level",
    "lvl",
    "experience",
    "gain exp",
    "grind",
    "прокач",
    "уров",
    "опыт",
    "эксп",
)


def clamp_score(score: Any) -> int:
    return max(0, min(int_or_default(score, 0), 100))


def int_or_default(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def result_limit(arguments: dict[str, Any], default: int = 20, maximum: int = 100) -> int:
    return max(1, min(int_or_default(arguments.get("maxResults", default), default), maximum))


def task_option(kind: str, score: int, reason: str, tool: Any, tool_arguments: dict[str, Any], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"kind": kind, "score": clamp_score(score), "reason": reason, "tool": tool, "arguments": tool_arguments}
    if extra:
        result.update(extra)
    return result


def xp_source_option(
    kind: str,
    score: int,
    reason: str,
    tool: Any,
    tool_arguments: dict[str, Any],
    *,
    estimated_xp: Any,
    risk: str,
    evidence: dict[str, Any] | None = None,
    recommended_checks: list[str] | None = None,
    blocked_by: list[str] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "kind": kind,
        "score": clamp_score(score),
        "reason": reason,
        "tool": tool,
        "arguments": tool_arguments,
        "estimatedXp": estimated_xp,
        "risk": risk,
    }
    if evidence:
        result["evidence"] = evidence
    if recommended_checks:
        result["recommendedChecks"] = recommended_checks
    if blocked_by:
        result["blockedBy"] = [str(item) for item in blocked_by if str(item)]
    return result


def xp_progress_payload(chosen: dict[str, Any], arguments: dict[str, Any]) -> dict[str, Any]:
    level = int_or_default(chosen.get("level"), 0)
    level_cap = int_or_default(chosen.get("levelCap"), 0)
    experience = int_or_default(chosen.get("experience"), 0)
    default_target = level + 1 if level > 0 else 1
    target_level = int_or_default(arguments.get("targetLevel"), default_target)
    if level_cap > 0:
        target_level = min(target_level, level_cap)
    target_level = max(target_level, level)
    next_level_experience = int_or_default(chosen.get("nextLevelExperience"), next_level_need_exp(level))
    experience_to_next = int_or_default(chosen.get("experienceToNextLevel"), max(next_level_experience - experience, 0))
    if target_level <= level:
        target_experience = experience
    elif target_level == level + 1:
        target_experience = next_level_experience
    else:
        target_experience = next_level_need_exp(target_level - 1)
    return {
        "level": level,
        "targetLevel": target_level,
        "levelCap": level_cap or None,
        "experience": experience,
        "nextLevelExperience": next_level_experience,
        "experienceToNextLevel": max(experience_to_next, 0),
        "targetLevelExperience": target_experience,
        "estimatedExperienceToTarget": max(target_experience - experience, 0),
    }


def next_level_need_exp(level: int) -> int:
    value = (level * level // 2 + 1) if level % 2 != 0 else (level * level // 2 + level // 2)
    return max(value * 100, 1)


def goal_has_xp_marker(text: str) -> bool:
    return any(marker in text for marker in XP_GOAL_MARKERS) or re.search(r"(^|[^a-z0-9])xp([^a-z0-9]|$)", text) is not None

