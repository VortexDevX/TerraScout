from app.protocol import Observation, Position
from app.storage import EventStore


def test_event_store_appends_and_reads_recent(tmp_path) -> None:
    store = EventStore(tmp_path / "events.sqlite3")
    observation = Observation(
        position=Position(x=1, y=64, z=2),
        biome="plains",
        health=20,
        hunger=18,
        time_of_day=6000,
        light_level=12,
    )

    event_id = store.append("observation", observation)
    events = store.recent()

    assert event_id == 1
    assert events[0]["event_type"] == "observation"
    assert events[0]["payload"]["biome"] == "plains"

