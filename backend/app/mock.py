from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

from app.protocol import HostileMob, Observation, Position


async def mock_observations(interval_ms: int) -> AsyncIterator[Observation]:
    step = 0
    while True:
        hostile = step % 6 in {3, 4}
        lava = step % 10 == 7
        cliff = step % 8 == 5
        yield Observation(
            bot_id="mock-terrascout",
            position=Position(x=step * 2, y=64, z=step * 2),
            biome="plains" if step % 5 else "forest",
            health=20 if step % 9 else 7,
            hunger=18 if step % 7 else 6,
            time_of_day=6000 if step % 4 else 14000,
            light_level=12 if step % 4 else 5,
            nearby_hostiles=[
                HostileMob(
                    kind="zombie",
                    position=Position(x=step * 2 + 3, y=64, z=step * 2 + 2),
                    distance=5,
                )
            ]
            if hostile
            else [],
            nearby_lava=lava,
            nearby_cliff=cliff,
            nearby_deep_water=step % 11 == 6,
        )
        step += 1
        await asyncio.sleep(interval_ms / 1000)

