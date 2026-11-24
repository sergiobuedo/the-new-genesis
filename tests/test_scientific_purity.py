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


def test_human_like_sexual_reproduction_gestation_and_family_inheritance():
    """Verify chromosomal ♂/♀ sex, pair-bonding, pregnancy gestation, and cumulative parental cultural inheritance."""
    from backend.mirofish_lab.observer import PopulationSimulation

    sim = PopulationSimulation(seed=4201, founders_per_lineage=4, enable_culture=True)
    males = [a for a in sim.living_agents if a.sex == "M"]
    females = [a for a in sim.living_agents if a.sex == "F"]
    assert len(males) >= 4 and len(females) >= 4

    fem = females[0]
    mal = next(m for m in males if m.lineage != fem.lineage)
    fem.x, fem.y = -135.0, -115.0
    mal.x, mal.y = -134.2, -115.0
    fem.born_day = -15
    mal.born_day = -15
    fem.trust_bonds[mal.id] = 0.85
    mal.trust_bonds[fem.id] = 0.85
    fem.insight_map["fire_lore"] = 2
    mal.insight_map["bronze_lore"] = 1
    fem.personal_lexicon["food"] = "nara"
    mal.personal_lexicon["kin"] = "sola"

    # Trigger courtship & conception
    for _ in range(15):
        sim._check_species_reproduction()
        if fem.is_pregnant:
            break
    assert fem.is_pregnant is True
    assert fem.partner_id == mal.id and mal.partner_id == fem.id
    # Spouses share insights & vocabulary upon pair-bonding
    assert fem.insight_map.get("bronze_lore") == 1 and mal.insight_map.get("fire_lore") == 2

    # Complete pregnancy gestation -> live birth
    pop_before = len(sim.living_agents)
    sim._deliver_live_birth(fem)
    assert fem.is_pregnant is False
    assert len(sim.living_agents) > pop_before
    child_id = fem.children_ids[-1]
    child = sim.agents[child_id]
    assert child.sex in ("M", "F")
    assert child.parents == (fem.id, mal.id)
    assert sim._are_close_kin(fem, child) is True
    assert child.insight_map.get("fire_lore") == 2 and child.insight_map.get("bronze_lore") == 1
    assert child.personal_lexicon.get("food") == "nara" and child.personal_lexicon.get("kin") == "sola"


def test_era_scaled_human_lifespan_diseases_and_emergent_cures():
    """Verify Paleolithic-to-Modern era lifespan scaling, natural pathology, empirical cures, and acquired immunity."""
    from backend.mirofish_lab.observer import PopulationSimulation
    from backend.world.physics import CosmosWorld

    sim = PopulationSimulation(seed=4201, founders_per_lineage=3, enable_culture=True)
    paleo_yrs = sim.compute_era_lifespan_years(0.5)
    assert 30.0 <= paleo_yrs <= 42.0

    # Unlocking fire, shelter, farming, herbal, antiseptic & clinical medicine scales life expectancy to modern human range!
    sim.discoveries.update({
        "struct_hearth": 10,
        "struct_shelter": 20,
        "first_agriculture": 30,
        "first_herbal_medicine": 40,
        "craft_antiseptic_balm": 50,
        "craft_clinical_cure": 60,
    })
    modern_yrs = sim.compute_era_lifespan_years(0.5)
    assert modern_yrs >= 80.0

    # Empirical compounding of herbal_remedy -> antiseptic_balm -> clinical_cure
    world = CosmosWorld(seed=4201)
    insights = {}
    rem, _, k1, _ = world.attempt_empirical_experiment("medicinal_herb", "orb_sweet", ["medicinal_herb", "orb_sweet"], insights, 0.0, 0.0, "S-001")
    assert k1 == "breakthrough" and rem == "herbal_remedy"
    balm, _, k2, _ = world.attempt_empirical_experiment("herbal_remedy", "resin_gold", ["herbal_remedy", "resin_gold"], insights, 0.0, 0.0, "S-001")
    assert k2 == "breakthrough" and balm == "antiseptic_balm"
    serum, _, k3, _ = world.attempt_empirical_experiment("antiseptic_balm", "silica_glass", ["antiseptic_balm", "silica_glass"], insights, 0.0, 0.0, "S-001")
    assert k3 == "breakthrough" and serum == "clinical_cure"

    # Sick agent cures themselves with clinical_cure & gains acquired immunity
    ag = sim.living_agents[0]
    ag.illness = "camp_plague"
    ag.illness_severity = 65.0
    ag.inventory.append("clinical_cure")
    sim._act_step(ag, [], [], [], [], [], int(ag.x), int(ag.y))
    assert ag.illness == ""
    assert "camp_plague" in ag.antibodies


def test_earth_solar_timezones_proto_writing_and_human_parity_metrics():
    """Verify Earth-like longitude solar timezones, 23.4° seasonal daylight, clay tablet proto-writing & vocations."""
    from backend.world.physics import CosmosWorld
    from backend.mirofish_lab.observer import MiroFishObservatory
    import tempfile
    from pathlib import Path

    world = CosmosWorld(seed=4201)
    # East & West continents have distinct local solar phases
    west_p = world.local_solar_phase_at(-150.0, -100.0)
    east_p = world.local_solar_phase_at(150.0, -100.0)
    assert abs(west_p - east_p) > 0.2
    # Boreal latitude daylight duration shifts realistically across 365-day Earth seasons
    world.tick_count = 91 * 24  # Summer peak (Day 92)
    summer_hrs = world.daylight_hours_at(145.0, -150.0)
    world.tick_count = 274 * 24  # Winter (Day 275)
    winter_hrs = world.daylight_hours_at(145.0, -150.0)
    assert summer_hrs > winter_hrs

    # Expanded Earth biosphere: 42 wild fauna species & 22 flora species
    from backend.world.physics import FAUNA_CATALOG, FLORA_SPECIES, DAYS_PER_YEAR, TICKS_PER_DAY
    assert DAYS_PER_YEAR == 365 and TICKS_PER_DAY == 24
    assert len(FAUNA_CATALOG) >= 42 and len(FLORA_SPECIES) >= 22

    # Empirical proto-writing clay tablet (reed/bone stylus + soft clay)
    insights = {"build_lore": 2}
    world.attempt_empirical_experiment("clay_gray", "ivory_horn", ["clay_gray", "ivory_horn"], insights, 0.0, 0.0, "S-001")
    tab, _, k_t, _ = world.attempt_empirical_experiment("clay_gray", "ivory_horn", ["clay_gray", "ivory_horn"], insights, 0.0, 0.0, "S-001")
    assert k_t == "breakthrough" and tab == "clay_tablet"

    # Default speed is x20 & metrics expose clan_leaders, vocations, diplomacy, macro_population
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
        obs = MiroFishObservatory(ledger_dir=Path(td), seed=4201, founders_per_lineage=3)
        assert obs.speed_multiplier == 20
        m = obs.compute_scientific_metrics()
        assert "vocations" in m and "diplomacy_es" in m and "macro_population" in m
        # Pure 1:1 Verifiable Reality: reported macro_population MUST equal exact living count (zero multiplier!)
        assert m["macro_population"] == m["live_population"]


def test_pure_1to1_reality_earth_geography_and_open_combinatorics():
    """Verify real Earth (lat, lon) region mapping and open-ended combinatorial material synthesis."""
    from backend.world.earth_geography import earth_location_summary
    from backend.world.combinatorics import synthesize_open_compound

    geo = earth_location_summary(42.0, 10.0)
    assert -90.0 <= geo["lat"] <= 90.0 and -180.0 <= geo["lon"] <= 180.0
    assert geo["continent"] and geo["region"]

    # Open-ended synthesis produces deterministic novel compounds with zero hardcoded recipes
    comp = synthesize_open_compound("ivory_horn", "fiber_dry", "bind", ambient_temp_c=22.0)
    assert comp is not None
    assert comp.compound_id.startswith("CMP-")
    assert comp.utility_score >= 0.58
    comp_rev = synthesize_open_compound("fiber_dry", "ivory_horn", "bind", ambient_temp_c=22.0)
    assert comp_rev is not None and comp_rev.compound_id == comp.compound_id





