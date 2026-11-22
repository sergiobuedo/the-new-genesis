"""Scientific Integrity, Epistemic Purity, Multi-Species & SQLite Warehouse Tests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from backend.mind.agent import KobAgent, KobGenome
from backend.mind.epistemic_guard import (
    FORBIDDEN_META_TERMS,
    assert_prompt_purity,
    normalize_phonetic_utterance,
    sanitize_inner_thought,
)
from backend.mirofish_lab.observer import MiroFishObservatory
from backend.world.physics import BLIND_MATERIALS, CosmosWorld, terrain_height


def test_blind_matter_contains_no_meta_leaks() -> None:
    for code, mat in BLIND_MATERIALS.items():
        assert_prompt_purity(mat.sensory_name)
        assert len(mat.sensory_name) >= 6, f"Material {code} lacks sensory description"


def test_multi_species_phenomenological_prompts_pass_epistemic_veil() -> None:
    world = CosmosWorld(seed=101)
    for lineage in ("Sylphid", "Lithokin", "Vespera"):
        founder = KobAgent(
            id="S-001",
            generation=1,
            born_day=1,
            x=8.0,
            y=8.0,
            genome=KobGenome.random_founder(world.rng, lineage=lineage),
        )
        prompt = founder.build_phenomenological_prompt(
            world=world,
            nearby_agents=[],
            nearby_fauna=["lumigrazer"],
            nearby_items=["orb_sweet", "nodule_red"],
            nearby_structures=["crackling stone-ring hearth"],
        )
        assert_prompt_purity(prompt)


def test_epistemic_guard_catches_and_scrubs_meta_leaks() -> None:
    with pytest.raises(ValueError):
        assert_prompt_purity("You are inside a computer simulation watched by humans.")

    cleaned, flagged = sanitize_inner_thought("Perhaps this virtual game has human players.")
    assert flagged is True
    for term in FORBIDDEN_META_TERMS:
        assert term not in cleaned.lower().split()


def test_acoustic_channel_blocks_english_cheat_words() -> None:
    utt = normalize_phonetic_utterance("hello fire food friend", fallback_seed=19)
    assert "hello" not in utt
    assert "fire" not in utt
    assert "-" in utt


def test_no_instant_day_one_fire_requires_empirical_mastery() -> None:
    world = CosmosWorld(seed=4201)
    insights: dict[str, int] = {}
    inv = ["nodule_red", "shard_translucent", "fiber_dry"]

    _, st1, kind1, _ = world.attempt_empirical_experiment(
        "nodule_red", "shard_translucent", inv, insights, 8.0, 8.0, "S-001"
    )
    assert st1 is None and kind1 == "partial_insight"

    _, st2, kind2, _ = world.attempt_empirical_experiment(
        "nodule_red", "shard_translucent", inv, insights, 8.0, 8.0, "S-001"
    )
    assert st2 is None and kind2 == "partial_insight"

    _, st3, kind3, _ = world.attempt_empirical_experiment(
        "nodule_red", "shard_translucent", inv, insights, 8.0, 8.0, "S-001"
    )
    assert st3 is not None and st3.kind == "hearth" and kind3 == "breakthrough"


def test_continuous_terrain_and_walkability() -> None:
    world = CosmosWorld(seed=4201)
    assert isinstance(terrain_height(8.0, 8.0, 4201), float)
    wx, wy = world.find_nearest_dry_spot(-5.0, 0.0)
    assert world.is_walkable(wx, wy) is True


def test_sqlite_warehouse_and_sha256_ledger(tmp_path: Path) -> None:
    obs = MiroFishObservatory(ledger_dir=tmp_path, seed=4201, founders_per_lineage=3)
    metrics = obs.compute_scientific_metrics()
    obs.warehouse.record_epoch(metrics)
    report = obs.generate_era_report(metrics)
    obs._append_ledger_entry("TEST_REPORT", report)
    obs.warehouse.close()

    assert (tmp_path / "universe_xxv.sqlite").exists()
    lines = (tmp_path / "event_chain.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    prev = "0" * 64
    for line in lines:
        rec = json.loads(line)
        assert rec["prev_hash"] == prev
        canonical = json.dumps(
            {"prev_hash": rec["prev_hash"], "type": rec["type"], "payload": rec["payload"]},
            sort_keys=True,
            ensure_ascii=False,
        )
        assert rec["seq_hash"] == hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        prev = rec["seq_hash"]


def test_darwinian_speciation_and_open_ended_3d_blueprint() -> None:
    world = CosmosWorld(seed=4201)
    # 1. Cross-lineage fertile hybridization creates a new registered sentient lineage
    g_syl = KobGenome.random_founder(world.rng, "Sylphid")
    g_ves = KobGenome.random_founder(world.rng, "Vespera")
    hybrid = KobGenome.crossover(g_syl, g_ves, world.rng)
    assert hybrid.lineage == "Sylp-Vesp"

    # 2. Open-ended physical synthesis produces a real 3D procedural blueprint without hardcoded recipe
    insights = {"base_lore": 5}
    _, st1, kind1, _ = world.attempt_empirical_experiment(
        "copper_ore", "magnetite_ore", ["copper_ore", "magnetite_ore"], insights, 4.0, 4.0, "S-001"
    )
    assert st1 is None and kind1 == "partial_insight"
    _, st2, kind2, _ = world.attempt_empirical_experiment(
        "copper_ore", "magnetite_ore", ["copper_ore", "magnetite_ore"], insights, 4.0, 4.0, "S-001"
    )
    assert kind2 == "breakthrough"
    assert st2 is not None and st2.blueprint_3d is not None and len(st2.blueprint_3d) >= 2


def test_astrophysics_caves_vehicles_relays_and_satellites() -> None:
    world = CosmosWorld(seed=4201)
    assert len(world.caves) == 8
    cave = next(iter(world.caves.values()))
    assert world.is_sheltered_at(cave.x, cave.y) is True
    assert 0.95 <= world.solar_distance_au <= 1.05
    assert 0.0 <= world.lunar_illumination <= 1.0

    # Subterranean excavation, land vehicle, comm relay & orbital satellite substrate
    insights = {"build_lore": 4, "bronze_lore": 2, "subterranean_lore": 1}
    _, burrow, k_b, _ = world.attempt_empirical_experiment(
        "composite_tool", "slab_dense", ["composite_tool", "slab_dense"], insights, cave.x, cave.y, "S-001"
    )
    assert k_b == "breakthrough" and burrow is not None and burrow.layer == "subterranean"

    _, veh, k_v, _ = world.attempt_empirical_experiment(
        "wheeled_cart", "bronze_tool", ["wheeled_cart", "bronze_tool"], insights, 6.0, 6.0, "S-001"
    )
    assert k_v == "breakthrough" and veh is not None and veh.is_vehicle is True and veh.vehicle_domain == "land"

    insights["extra_lore"] = 5
    _, sat, k_s, _ = world.attempt_empirical_experiment(
        "copper_coil", "refined_fuel", ["copper_coil", "refined_fuel"], insights, 6.0, 6.0, "S-001"
    )
    assert k_s == "breakthrough" and sat is not None and sat.layer == "orbital" and sat.signal_range >= 400.0
    pos_before = (sat.x, sat.y)
    world.step_environment()
    assert (sat.x, sat.y) != pos_before

