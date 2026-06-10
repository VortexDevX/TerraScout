from app.protocol import Observation, Position, TerrainSample
from app.terrain import analyze_terrain


def test_terrain_report_scores_rugged_boundary_as_wonder() -> None:
    observation = Observation(
        position=Position(x=32, y=80, z=-16),
        biome="plains",
        health=20,
        hunger=20,
        time_of_day=6000,
        light_level=15,
        terrain_samples=[
            TerrainSample(position=Position(x=32, y=80, z=-16), top_block="grass_block", biome="plains", elevation_delta=0),
            TerrainSample(position=Position(x=38, y=88, z=-16), top_block="stone", biome="stony_peaks", elevation_delta=8),
            TerrainSample(position=Position(x=44, y=92, z=-16), top_block="snow_block", biome="stony_peaks", elevation_delta=12),
            TerrainSample(position=Position(x=32, y=79, z=-10), top_block="water", biome="river", elevation_delta=-1, is_water=True),
        ],
    )

    report = analyze_terrain(observation)

    assert report.sample_count == 4
    assert report.elevation_range == 13
    assert report.wonder_score > report.base_score
    assert report.fingerprint
    assert any(feature.name == "Biome Boundary" for feature in report.features)


def test_terrain_report_fallback_works_without_probe() -> None:
    observation = Observation(
        position=Position(x=0, y=64, z=0),
        biome="plains",
        health=20,
        hunger=20,
        time_of_day=6000,
        light_level=15,
        floor_block="grass_block",
    )

    report = analyze_terrain(observation)

    assert report.sample_count == 1
    assert report.personality in {"Calm", "Settler"}
