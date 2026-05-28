from app.engine import analyze_risk, build_world_state, decide, select_goal
from app.protocol import HostileMob, Observation, Position


def test_low_risk_observation_explores() -> None:
    observation = Observation(
        position=Position(x=0, y=64, z=0),
        biome="plains",
        health=20,
        hunger=20,
        time_of_day=6000,
        light_level=15,
    )

    state, risk, goal, command = decide(observation)

    assert state.hostile_count == 0
    assert risk.score == 0
    assert goal.name == "explore"
    assert command.command == "explore"


def test_high_risk_observation_flees() -> None:
    observation = Observation(
        position=Position(x=10, y=64, z=10),
        biome="forest",
        health=6,
        hunger=9,
        time_of_day=14000,
        light_level=4,
        nearby_lava=True,
        nearby_cliff=True,
        nearby_hostiles=[
            HostileMob(kind="zombie", position=Position(x=12, y=64, z=12), distance=4)
        ],
    )

    state = build_world_state(observation)
    risk = analyze_risk(state)
    goal = select_goal(state, risk)

    assert risk.score == 100
    assert goal.name == "flee"


def test_pathfinding_error_idles() -> None:
    observation = Observation(
        position=Position(x=0, y=64, z=0),
        biome="plains",
        health=20,
        hunger=20,
        time_of_day=6000,
        light_level=15,
        pathfinding_error="No path",
    )

    _, _, goal, command = decide(observation)

    assert goal.name == "idle"
    assert command.command == "idle"

