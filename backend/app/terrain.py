from __future__ import annotations

import hashlib
from collections import Counter

from app.protocol import Observation, TerrainFeature, TerrainReport, TerrainSample


def _clamp_score(value: float) -> int:
    return max(0, min(100, round(value)))


def _fallback_sample(observation: Observation) -> TerrainSample:
    block = observation.floor_block or observation.feet_block or "unknown"
    return TerrainSample(
        position=observation.position,
        top_block=block,
        biome=observation.biome,
        elevation_delta=0,
        is_water=block == "water",
        is_lava=block == "lava",
        is_passable=block not in {"lava", "water", "fire", "cactus", "unknown"},
    )


def _name_landmark(observation: Observation, personality: str, elevation_range: float, water_ratio: float) -> str:
    biome = observation.biome.replace("_", " ").title()
    if water_ratio >= 0.25:
        form = "Basin"
    elif elevation_range >= 10:
        form = "Ridge"
    elif elevation_range >= 5:
        form = "Rise"
    else:
        form = "Field"
    return f"{biome} {personality} {form}"


def analyze_terrain(observation: Observation) -> TerrainReport:
    samples = observation.terrain_samples or [_fallback_sample(observation)]
    elevations = [sample.elevation_delta for sample in samples]
    block_counts = Counter(sample.top_block for sample in samples)
    biome_counts = Counter(sample.biome for sample in samples)

    sample_count = len(samples)
    elevation_range = max(elevations) - min(elevations) if elevations else 0
    mean = sum(elevations) / sample_count
    ruggedness = sum(abs(elevation - mean) for elevation in elevations) / sample_count
    water_ratio = sum(1 for sample in samples if sample.is_water) / sample_count
    lava_ratio = sum(1 for sample in samples if sample.is_lava) / sample_count
    passable_ratio = sum(1 for sample in samples if sample.is_passable) / sample_count
    biome_variety = len(biome_counts)
    block_variety = len(block_counts)

    path_iq = _clamp_score(100 - ruggedness * 7 - elevation_range * 2 - water_ratio * 35 - lava_ratio * 80)
    base_score = _clamp_score(passable_ratio * 55 + path_iq * 0.25 + min(water_ratio, 0.2) * 60 - lava_ratio * 80)
    wonder_score = _clamp_score(elevation_range * 6 + ruggedness * 8 + biome_variety * 10 + block_variety * 2 + water_ratio * 25)

    features: list[TerrainFeature] = [
        TerrainFeature(name="PathIQ", score=path_iq, detail="terrain traversal difficulty inverse"),
        TerrainFeature(name="BaseRank", score=base_score, detail="flatness, passability, water, hazard balance"),
        TerrainFeature(name="WonderHunter", score=wonder_score, detail="ruggedness, variety, water, elevation contrast"),
    ]
    if biome_variety >= 2:
        features.append(
            TerrainFeature(name="Biome Boundary", score=_clamp_score(40 + biome_variety * 15), detail=f"{biome_variety} biomes in local probe")
        )
    if elevation_range >= 8:
        features.append(
            TerrainFeature(name="Mountain Intelligence", score=_clamp_score(elevation_range * 8), detail=f"{elevation_range:.1f} block local relief")
        )
    if water_ratio >= 0.2:
        features.append(
            TerrainFeature(name="RiverMind", score=_clamp_score(water_ratio * 100), detail="surface water present in probe")
        )

    if wonder_score >= 75:
        personality = "Wondrous"
    elif base_score >= 75:
        personality = "Settler"
    elif path_iq <= 35:
        personality = "Hostile"
    elif water_ratio >= 0.25:
        personality = "Watershed"
    elif elevation_range >= 8:
        personality = "Highland"
    else:
        personality = "Calm"

    chunk_x = int(observation.position.x // 16)
    chunk_z = int(observation.position.z // 16)
    signature = "|".join(
        [
            observation.biome,
            ",".join(f"{name}:{count}" for name, count in sorted(block_counts.items())),
            f"relief:{round(elevation_range, 1)}",
            f"water:{round(water_ratio, 2)}",
            f"lava:{round(lava_ratio, 2)}",
            f"path:{path_iq}",
        ]
    )
    fingerprint = hashlib.sha1(signature.encode("utf-8")).hexdigest()[:16]
    vector = [
        round(elevation_range, 3),
        round(ruggedness, 3),
        round(water_ratio, 3),
        round(lava_ratio, 3),
        round(passable_ratio, 3),
        float(biome_variety),
        float(block_variety),
        float(path_iq),
        float(base_score),
        float(wonder_score),
    ]

    return TerrainReport(
        chunk_key=f"{chunk_x},{chunk_z}",
        fingerprint=fingerprint,
        sample_count=sample_count,
        elevation_range=round(elevation_range, 2),
        ruggedness=round(ruggedness, 2),
        water_ratio=round(water_ratio, 3),
        lava_ratio=round(lava_ratio, 3),
        passable_ratio=round(passable_ratio, 3),
        path_iq=path_iq,
        base_score=base_score,
        wonder_score=wonder_score,
        personality=personality,
        landmark_name=_name_landmark(observation, personality, elevation_range, water_ratio),
        terrain_vector=vector,
        features=features,
    )
