from __future__ import annotations

from itertools import count

from app.config import settings
from app.policy import load_policy
from app.protocol import (
    ActionCommand,
    CommandType,
    GoalName,
    Observation,
    Position,
    RiskReport,
    RiskSource,
    SelectedGoal,
    WorldState,
)

_command_counter = count(1)


def _is_daytime(time_of_day: int) -> bool:
    return 0 <= time_of_day < 12300


def _is_surface_block(block_name: str | None) -> bool:
    if not block_name:
        return False
    return block_name in {
        "grass_block",
        "dirt",
        "coarse_dirt",
        "sand",
        "red_sand",
        "gravel",
        "stone",
        "snow_block",
        "podzol",
        "mycelium",
    }


def build_world_state(observation: Observation) -> WorldState:
    hazards: list[str] = []
    if observation.nearby_lava:
        hazards.append("lava")
    if observation.nearby_cliff:
        hazards.append("cliff")
    if observation.nearby_deep_water:
        hazards.append("deep_water")
    if observation.pathfinding_error:
        hazards.append("pathfinding_error")

    nearest = min((mob.distance for mob in observation.nearby_hostiles), default=None)
    policy = load_policy(settings.policy_path)
    likely_surface_day = (
        policy.ignore_daylight_darkness
        and _is_daytime(observation.time_of_day)
        and _is_surface_block(observation.floor_block)
    )
    return WorldState(
        bot_id=observation.bot_id,
        position=observation.position,
        biome=observation.biome,
        health=observation.health,
        hunger=observation.hunger,
        is_night=observation.time_of_day >= 13000,
        is_dark=observation.light_level <= 7 and not likely_surface_day,
        hostile_count=len(observation.nearby_hostiles),
        nearest_hostile_distance=nearest,
        hazards=hazards,
    )


def analyze_risk(state: WorldState) -> RiskReport:
    sources: list[RiskSource] = []

    if state.health <= 8:
        sources.append(RiskSource(name="low_health", score=25, detail=f"health={state.health}"))
    if state.hunger <= 8:
        sources.append(RiskSource(name="low_hunger", score=15, detail=f"hunger={state.hunger}"))
    if state.is_night:
        sources.append(RiskSource(name="night", score=15, detail="time_of_day is hostile"))
    if state.is_dark:
        sources.append(RiskSource(name="darkness", score=10, detail="light level is low"))
    if state.hostile_count:
        nearest = state.nearest_hostile_distance or 0
        score = 30 if nearest <= 8 else 20
        sources.append(RiskSource(name="hostiles", score=score, detail=f"{state.hostile_count} nearby"))
    if "lava" in state.hazards:
        sources.append(RiskSource(name="lava", score=25, detail="lava nearby"))
    if "cliff" in state.hazards:
        sources.append(RiskSource(name="cliff", score=20, detail="cliff nearby"))
    if "deep_water" in state.hazards:
        sources.append(RiskSource(name="deep_water", score=10, detail="deep water nearby"))
    if "pathfinding_error" in state.hazards:
        sources.append(RiskSource(name="pathfinding_error", score=20, detail="movement failed"))

    score = min(100, sum(source.score for source in sources))
    return RiskReport(score=score, sources=sources)


def select_goal(state: WorldState, risk: RiskReport) -> SelectedGoal:
    policy = load_policy(settings.policy_path)
    if "pathfinding_error" in state.hazards:
        return SelectedGoal(name=GoalName.idle, utility=1.0, reason="pathfinding failed")
    if risk.score >= 70 or state.health <= policy.min_safe_health:
        return SelectedGoal(name=GoalName.flee, utility=0.95, reason="risk too high")
    if risk.score >= 45:
        return SelectedGoal(name=GoalName.survive, utility=0.75, reason="moderate danger")
    if state.hunger <= 6:
        return SelectedGoal(name=GoalName.report, utility=0.65, reason="hunger low; food gathering out of MVP")
    return SelectedGoal(name=GoalName.explore, utility=0.7, reason="conditions safe enough")


def plan_command(state: WorldState, risk: RiskReport, goal: SelectedGoal) -> ActionCommand:
    command_id = f"cmd-{next(_command_counter)}"
    policy = load_policy(settings.policy_path)
    if goal.name == GoalName.flee:
        return ActionCommand(
            command_id=command_id,
            command=CommandType.flee,
            reason=goal.reason,
            radius=policy.flee_radius,
            max_duration_ms=4000,
        )
    if goal.name == GoalName.explore:
        return ActionCommand(
            command_id=command_id,
            command=CommandType.explore,
            reason=goal.reason,
            radius=policy.explore_radius,
            max_duration_ms=5000,
        )
    if goal.name == GoalName.report:
        return ActionCommand(
            command_id=command_id,
            command=CommandType.report_state,
            reason=goal.reason,
            max_duration_ms=1000,
        )
    return ActionCommand(
        command_id=command_id,
        command=CommandType.idle,
        reason=f"{goal.reason}; risk={risk.score}",
        max_duration_ms=1000,
    )


def decide(observation: Observation) -> tuple[WorldState, RiskReport, SelectedGoal, ActionCommand]:
    state = build_world_state(observation)
    risk = analyze_risk(state)
    goal = select_goal(state, risk)
    command = plan_command(state, risk, goal)
    return state, risk, goal, command
