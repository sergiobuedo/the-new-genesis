"""Universe XXV (v3.0) — Zero-Bias Multi-Species Simulation, Smooth Craig Reynolds
Steering (Zero Spinning), Bilingual Daily Chronicles (EN/ES), and Emergent Archetypes.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import math
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx

from backend.mind.agent import LINEAGE_SPECS, KobAgent, KobGenome, OllamaCortex
from backend.mind.epistemic_guard import normalize_phonetic_utterance
from backend.mirofish_lab.storage import LongitudinalWarehouse
from backend.world.combinatorics import VALID_PROCESSES, synthesize_open_compound
from backend.world.earth_geography import earth_location_summary
from backend.world.physics import (
    BLIND_MATERIALS,
    ENCLAVE_HOMELANDS,
    FAUNA_CATALOG,
    MOUNTAIN_PEAKS,
    CosmosWorld,
    MortalRemains,
    TICKS_PER_DAY,
    WorldStructure,
    classify_climate_zone,
)


def _angle_diff(target: float, current: float) -> float:
    d = (target - current + math.pi) % (2.0 * math.pi) - math.pi
    return d


class PopulationSimulation:
    """Autonomous multi-species ecosystem with smooth Boids/Reynolds steering."""

    def __init__(
        self,
        seed: int = 4201,
        founders_per_lineage: int = 7,
        enable_culture: bool = True,
        cortex: Optional[OllamaCortex] = None,
        warehouse: Optional[LongitudinalWarehouse] = None,
    ) -> None:
        self.world = CosmosWorld(seed=seed)
        self.enable_culture = enable_culture
        self.cortex = cortex if enable_culture else None
        self.warehouse = warehouse if enable_culture else None
        self.agents: Dict[str, KobAgent] = {}
        self._agent_seq: int = 0
        self.timeline: List[Dict[str, Any]] = []
        self.sharing_count: int = 0
        self.hive_pooling_count: int = 0
        self.inter_species_peace: int = 0
        self.conflict_count: int = 0
        self.inter_species_conflict: int = 0
        self.experiment_trials: int = 0
        self.hunts_count: int = 0
        self.fishing_count: int = 0
        self.domesticated_count: int = 0
        self.trade_count: int = 0
        self.crops_planted: int = 0
        self.predator_attacks: int = 0
        self.philosophical_count: int = 0
        self.mourning_vigils: int = 0
        self.grave_offerings: int = 0
        self.stone_burials: int = 0
        self.corpse_avoidance: int = 0
        self.births_today: int = 0
        self.deaths_today: int = 0
        self.clashes_today: int = 0
        self.gifts_today: int = 0
        self.courtships_count: int = 0
        self.couples_formed: int = 0
        self.disease_cases: int = 0
        self.cures_applied: int = 0
        self.planetary_population: float = float(founders_per_lineage * 3)  # Pure 1:1 verifiable individual count (zero extrapolation)
        self.emergent_compounds: Dict[str, Dict[str, Any]] = {}  # Unscripted open-ended combinatorial discoveries
        self.recent_fx: List[Dict[str, Any]] = []  # Live 3D Action FX cues (attack, fire, plant, eat, birth, death, bury...)
        self.discoveries: Dict[str, int] = {}
        self.max_generation: int = 1
        self.rebiogenesis_cycle: int = 1
        self._founders_per_lineage: int = founders_per_lineage
        self._spawn_multi_species_founders(founders_per_lineage)

    def _are_close_kin(self, a: KobAgent, b: KobAgent) -> bool:
        """Human-like Westermarck incest avoidance (parents, children, or full/half siblings)."""
        if a.id in (b.parents or ()) or b.id in (a.parents or ()):
            return True
        p_a = {p for p in (a.parents or ()) if p}
        p_b = {p for p in (b.parents or ()) if p}
        if p_a and p_b and (p_a & p_b):
            return True
        return False

    def _spawn_lineage_enclave(self, lineage: str, count: int) -> List[str]:
        cx, cy = ENCLAVE_HOMELANDS[lineage]
        prefix = LINEAGE_SPECS[lineage]["prefix"]
        spawned: List[str] = []
        for idx in range(count):
            self._agent_seq += 1
            aid = f"{prefix}-{self._agent_seq:03d}"
            ang = self.world.rng.uniform(0, 2 * math.pi)
            rad = self.world.rng.uniform(1.5, 6.0)
            sx, sy = self.world.find_nearest_dry_spot(
                cx + math.cos(ang) * rad, cy + math.sin(ang) * rad
            )
            genome = KobGenome.random_founder(self.world.rng, lineage=lineage)
            init_age_days = round(self.world.rng.uniform(6570.0, 8760.0), 1)  # Realistic 18-24 yr young adult founders
            ag = KobAgent(
                id=aid,
                generation=1,
                born_day=self.world.day - int(init_age_days),
                age_days=init_age_days,
                x=sx,
                y=sy,
                genome=genome,
                sex="M" if (idx % 2 == 0) else "F",
                heading=round(ang, 3),
                steer_side=1.0 if self.world.rng.random() < 0.5 else -1.0,
            )
            self.agents[aid] = ag
            spawned.append(aid)
        # Mild initial kinship recognition within same founding enclave
        for i, id_a in enumerate(spawned):
            for id_b in spawned[i + 1 :]:
                self.agents[id_a].trust_bonds[id_b] = 0.35
                self.agents[id_b].trust_bonds[id_a] = 0.35
        return spawned

    def _spawn_multi_species_founders(self, per_lineage: int) -> None:
        for lineage in ("Sylphid", "Lithokin", "Vespera"):
            self._spawn_lineage_enclave(lineage, per_lineage)

        self._record_event(
            "genesis",
            f"TheNewGenesis t=0: {len(self.agents)} founders across 3 distant continental climates (Sylphid, Lithokin, Vespera) awaken in epistemic isolation.",
            list(self.agents.keys())[:4],
            4.0,
            4.0,
            importance=5,
        )

    def _record_event(
        self,
        kind: str,
        summary: str,
        actors: List[str],
        x: float,
        y: float,
        importance: int = 1,
    ) -> None:
        ev = {
            "id": len(self.timeline) + 1,
            "tick": self.world.tick_count,
            "day": self.world.day,
            "year": self.world.year,
            "season": self.world.season_name,
            "kind": kind,
            "summary": summary,
            "actors": actors,
            "x": round(x, 2),
            "y": round(y, 2),
            "importance": importance,
        }
        self.timeline.append(ev)
        if len(self.timeline) > 700:
            self.timeline.pop(0)
        if self.warehouse is not None and importance >= 2:
            self.warehouse.record_event(ev)

    @property
    def living_agents(self) -> List[KobAgent]:
        return [a for a in self.agents.values() if a.alive]

    def reset_daily_counters(self) -> None:
        self.births_today = 0
        self.deaths_today = 0
        self.clashes_today = 0
        self.gifts_today = 0

    def _emit_fx(self, kind: str, x: float, y: float, actor: str = "", label: str = "") -> None:
        """Records an observable live physical action cue for crisp 3D visual FX rendering."""
        self.recent_fx.append({
            "tick": self.world.tick_count,
            "kind": kind,
            "x": round(x, 2),
            "y": round(y, 2),
            "actor": actor,
            "label": label,
        })
        if len(self.recent_fx) > 24:
            self.recent_fx.pop(0)

    def compute_planetary_carrying_capacity(self) -> int:
        """Real Verhulst-Pearl ecological carrying capacity K (Neolithic 4M baseline -> 25B+ Spacefaring!)."""
        d = self.discoveries
        structs = {s.kind for s in self.world.structures.values()}
        k = 1_500_000  # Late Paleolithic global Homo sapiens baseline (~1.5M)
        if "struct_hearth" in d or "first_cooked_meal" in d or "hearth" in structs:
            k = max(k, 4_500_000)
        if "first_agriculture" in d or "crop_plot" in structs or "granary" in structs:
            k = max(k, 25_000_000)  # Neolithic Agrarian Revolution (4M -> 25M)
        if "craft_bronze_tool" in d or "struct_watercraft" in d or "struct_shelter" in d:
            k = max(k, 180_000_000)  # Bronze / Iron Age Civilizations
        if "struct_edifice" in d or "craft_antiseptic_balm" in d or "struct_comm_relay" in d:
            k = max(k, 2_800_000_000)  # Urban / Industrial / Antiseptic Era
        if "craft_clinical_cure" in d or "struct_land_vehicle" in d or "struct_orbital_satellite" in d:
            k = max(k, 25_000_000_000)  # Modern / Spacefaring Super-Earth (> 8,000,000,000+!)
        return k

    def _step_macro_demography(self, living: List[KobAgent]) -> None:
        """Pure 1:1 verifiable demography: reported population equals exact living simulated individuals (zero multiplier)."""
        self.planetary_population = float(len(living))

    def step_tick(self) -> List[Tuple[KobAgent, str]]:
        self.world.step_environment()
        if self.world.tick_count % TICKS_PER_DAY == 0:
            self._step_macro_demography(self.living_agents)
        if self.world.newly_triggered_disaster and self.enable_culture:
            d_info = self.world.newly_triggered_disaster
            d_names = {
                "earthquake": "Tectonic Earthquake shook the mountain belt!",
                "volcanic_eruption": "Volcanic Eruption sent cooling ash & fertile minerals across the planet!",
                "river_flood": "Seasonal River Flood enriched the valley floodplains with fertile silt!",
                "wildfire": "Lightning sparked a natural summer wildfire across dry grasslands!",
            }
            self._emit_fx(d_info["kind"], d_info["x"], d_info["y"], "PLANET", d_info["kind"])
            self._record_event(
                "conflict",
                f"GEOPHYSICS! {d_names.get(d_info['kind'], d_info['kind'])}",
                [],
                d_info["x"],
                d_info["y"],
                importance=5,
            )
        living = self.living_agents

        # Autonomous Re-Biogenesis ONLY if total planetary extinction occurs (0% human intervention)
        if not living and self.enable_culture:
            self.rebiogenesis_cycle += 1
            self._record_event(
                "extinction_rebirth",
                f"Total extinction recorded. Primordial Re-Biogenesis Cycle #{self.rebiogenesis_cycle} awakens amid ancient ruins.",
                [],
                8.0,
                10.0,
                importance=5,
            )
            self._spawn_multi_species_founders(self._founders_per_lineage)
            living = self.living_agents

        cortex_requests: List[Tuple[KobAgent, str]] = []

        # O(1) Spatial Hash Grid (cell size = 6) — prevents O(N^2) lag at high populations!
        agent_grid: Dict[Tuple[int, int], List[KobAgent]] = defaultdict(list)
        for a in living:
            agent_grid[(int(a.x) // 6, int(a.y) // 6)].append(a)

        if self.world.tick_count % 16 == 0:
            self._process_predator_ecology(living)

        # Log any wild animal species newly driven to permanent extinction OR newly evolved via speciation!
        for ext_sp, ext_day in self.world.extinct_fauna.items():
            m_ext = f"extinct_{ext_sp}"
            if m_ext not in self.discoveries and self.enable_culture:
                self.discoveries[m_ext] = ext_day
                label = (self.world.evolved_fauna.get(ext_sp) or FAUNA_CATALOG.get(ext_sp, {"label": ext_sp}))["label"]
                self._record_event(
                    "conflict",
                    f"ECOLOGICAL EXTINCTION! Wild species {label} has been driven permanently extinct!",
                    [],
                    4.0,
                    4.0,
                    importance=5,
                )
        for ev_sp, ev_spec in self.world.evolved_fauna.items():
            m_ev = f"speciated_{ev_sp}"
            if m_ev not in self.discoveries and self.enable_culture:
                self.discoveries[m_ev] = ev_spec.get("born_day", self.world.day)
                if "first_fauna_speciation" not in self.discoveries:
                    self.discoveries["first_fauna_speciation"] = self.world.day
                self._record_event(
                    "invention",
                    f"DARWINIAN SPECIATION! Wild {ev_spec['ancestor']} evolved into new species: {ev_spec['label']}!",
                    [],
                    4.0,
                    4.0,
                    importance=5,
                )

        for agent in living:
            if not agent.alive:
                continue
            bx, by = int(agent.x) // 6, int(agent.y) // 6
            nearby_others: List[KobAgent] = []
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    for other in agent_grid.get((bx + dx, by + dy), ()):
                        if other.id != agent.id and math.hypot(other.x - agent.x, other.y - agent.y) <= 5.5:
                            nearby_others.append(other)
            self._update_physiology_and_psychology(agent, len(nearby_others), nearby_others)
            if not agent.alive:
                continue

            if self.enable_culture and agent.current_intent == "migrate":
                new_chunk = self.world.ensure_frontier_around(agent.x, agent.y)
                if new_chunk is not None:
                    if "first_frontier_expansion" not in self.discoveries:
                        self.discoveries["first_frontier_expansion"] = self.world.day
                    self._record_event(
                        "frontier",
                        f"Frontier expanded! {agent.lineage} explorer {agent.id} charted sector {new_chunk}.",
                        [agent.id],
                        agent.x,
                        agent.y,
                        importance=3,
                    )

            gx, gy = int(round(agent.x)), int(round(agent.y))
            tile_items = self.world.resources.get((gx, gy), [])
            nearby_structs = [
                st
                for st in self.world.structures.values()
                if math.hypot(st.x - agent.x, st.y - agent.y) <= 5.5
            ]
            nearby_animals = [
                an
                for an in self.world.animals.values()
                if an.alive and math.hypot(an.x - agent.x, an.y - agent.y) <= 7.0
            ]
            nearby_corpses = [
                cp
                for cp in self.world.corpses.values()
                if math.hypot(cp.x - agent.x, cp.y - agent.y) <= 5.5
            ]

            if agent.utterance_ttl > 0:
                agent.utterance_ttl -= 1
                if agent.utterance_ttl == 0:
                    agent.last_utterance = ""

            if agent.pause_ticks > 0:
                agent.pause_ticks -= 1
            else:
                self._act_step(agent, nearby_others, nearby_animals, nearby_corpses, tile_items, nearby_structs, gx, gy)

            if (
                self.enable_culture
                and self.cortex is not None
                and not agent.pending_cortex
                and (self.world.tick_count - agent.last_cortex_tick) >= 55
                and len(cortex_requests) < 1
            ):
                salient = (
                    bool(nearby_corpses)
                    or (nearby_others and self.world.rng.random() < 0.25)
                    or (nearby_animals and self.world.rng.random() < 0.22)
                    or (agent.warmth < 48 and self.world.rng.random() < 0.30)
                    or (len(agent.inventory) >= 2 and self.world.rng.random() < 0.28)
                )
                if salient:
                    prompt = agent.build_phenomenological_prompt(
                        self.world,
                        nearby_others,
                        [a.species for a in nearby_animals],
                        tile_items,
                        [s.sensory_name for s in nearby_structs],
                        nearby_corpses=[f"{c.lineage} {c.fallen_id}" for c in nearby_corpses],
                    )
                    agent.pending_cortex = True
                    agent.last_cortex_tick = self.world.tick_count
                    cortex_requests.append((agent, prompt))

        if self.world.tick_count % 10 == 0 and len(self.living_agents) < 180:
            self._check_species_reproduction()

        # Distant Continental Refugia: if an entire continent's native lineage vanished, isolated far-continent survivors can re-emerge after long eras
        if self.enable_culture and self.world.tick_count % 3200 == 0:
            counts_by_lin = Counter(a.lineage for a in self.living_agents)
            for lin in ("Sylphid", "Lithokin", "Vespera"):
                if counts_by_lin.get(lin, 0) == 0:
                    spawned = self._spawn_lineage_enclave(lin, 6)
                    cx, cy = ENCLAVE_HOMELANDS[lin]
                    self._record_event(
                        "genesis",
                        f"Continental Refugium! An isolated wild band of {lin} ({len(spawned)} survivors) emerged in their distant native climate.",
                        spawned[:3],
                        cx,
                        cy,
                        importance=4,
                    )

        return cortex_requests

    def _process_predator_ecology(self, living: List[KobAgent]) -> None:
        """Simulates all dangerous Earth-analogue predators, river ambushers & venomous creatures!"""
        for pred in self.world.animals.values():
            if not pred.alive:
                continue
            spec = FAUNA_CATALOG.get(pred.species, {})
            hostility = spec.get("hostile", "none")
            if hostility in ("none", "defensive") or pred.tamed_by:
                continue
            if hostility == "night" and not self.world.is_night:
                continue
            if hostility == "day" and self.world.is_night:
                continue

            repelled = any(
                (st.kind == "hearth" and st.fuel > 0 and math.hypot(st.x - pred.x, st.y - pred.y) < 7.5)
                or (st.kind in ("shelter", "palisade") and math.hypot(st.x - pred.x, st.y - pred.y) < 6.5)
                for st in self.world.structures.values()
            ) or any(
                an.alive and an.tamed_by and math.hypot(an.x - pred.x, an.y - pred.y) < 6.5
                for an in self.world.animals.values()
            )
            if repelled:
                continue

            strike_rad = 1.7 if hostility == "venom" else 3.0
            prey = [a for a in living if math.hypot(a.x - pred.x, a.y - pred.y) <= strike_rad]
            if prey:
                victim = prey[0]
                defenders = [a for a in living if math.hypot(a.x - victim.x, a.y - victim.y) <= 4.8]
                if hostility != "venom" and (len(defenders) >= 3 or any(d.has_tool for d in defenders)):
                    pred.health -= 38.0
                    victim.action_label = f"Repelled wild {pred.species} with group!"
                    if pred.health <= 0:
                        pred.alive = False
                        for _ in range(spec.get("meat", 1)):
                            victim.inventory.append("wild_meat")
                        self._record_event(
                            "defense",
                            f"Collective defense! {', '.join(d.id for d in defenders[:3])} slew dangerous {spec['label']}!",
                            [d.id for d in defenders[:3]],
                            victim.x,
                            victim.y,
                            importance=4,
                        )
                else:
                    # Realistic campfire deterrence (lit hearth within 10m deters snakes, scorpions & predators)
                    near_fire = any(
                        st.kind == "hearth" and st.fuel > 0 and math.hypot(st.x - victim.x, st.y - victim.y) < 10.0
                        for st in self.world.structures.values()
                    )
                    last_strike = getattr(pred, "_last_strike_tick", -9999)
                    if near_fire or (self.world.tick_count - last_strike) < 48:
                        continue
                    pred._last_strike_tick = self.world.tick_count
                    self.predator_attacks += 1
                    dmg = float(spec.get("danger", 20.0))
                    victim.integrity = max(0.0, victim.integrity - dmg)
                    victim.stress = min(100.0, victim.stress + 30.0)
                    victim.is_sleeping = False
                    victim.mood = "tense"
                    atk_verb = "envenomed" if hostility == "venom" else "attacked"
                    victim.add_memory(f"Was {atk_verb} by wild {pred.species}!", self.world.day)
                    if victim.integrity <= 0:
                        victim.cause_of_death = f"wild {pred.species} attack"
                    self._record_event(
                        "predation",
                        f"Wild danger! {victim.lineage} {victim.id} was {atk_verb} by {spec['label']}.",
                        [victim.id],
                        victim.x,
                        victim.y,
                        importance=3,
                    )

    def compute_era_lifespan_years(self, vitality: float = 0.5) -> float:
        """Human-identical era-scaled biological life expectancy (Paleolithic ~32-42y -> Modern Medical ~78-92y)."""
        base_yrs = 30.0 + vitality * 12.0  # Paleolithic foraging baseline: 30..42 planetary years
        if not self.enable_culture:
            return round(base_yrs, 1)
        d = self.discoveries
        structs = {s.kind for s in self.world.structures.values()}
        bonus = 0.0
        if "struct_hearth" in d or "first_cooked_meal" in d or "hearth" in structs:
            bonus += 5.0  # Controlled fire & cooked nutrition
        if "struct_shelter" in d or "struct_burrow_network" in d or "struct_edifice" in d or (structs & {"shelter", "burrow_network", "edifice"}):
            bonus += 6.0  # Weatherproof shelter / architecture
        if "first_agriculture" in d or "struct_granary" in d or (structs & {"crop_plot", "granary"}):
            bonus += 5.0  # Reliable food surplus
        if "first_herbal_medicine" in d or "craft_herbal_remedy" in d:
            bonus += 10.0  # Herbal & botanical medicine
        if "craft_antiseptic_balm" in d or "first_antiseptic_cure" in d:
            bonus += 16.0  # Antiseptic & apothecary care
        if "craft_clinical_cure" in d or "first_clinical_cure" in d:
            bonus += 18.0  # Purified clinical therapeutics
        return round(base_yrs + bonus, 1)

    def _update_physiology_and_psychology(self, agent: KobAgent, local_crowd: int, nearby_others: Optional[List[KobAgent]] = None) -> None:
        agent.age_days = round((self.world.tick_count / float(TICKS_PER_DAY)) + (1 - agent.born_day), 2)
        cold_res = LINEAGE_SPECS[agent.lineage]["ColdBias"]
        # Unbiased Causal Control (v2.0-protocol): Physical laws (huddling, clothing insulation) apply identically to Live & Null!
        cloak_bonus = 10.0 if agent.has_cloak else 0.0
        huddle_bonus = min(6.0, local_crowd * 2.2)
        effective_temp = self.world.local_temperature_at(agent.x, agent.y) + cold_res + cloak_bonus + huddle_bonus

        burn = 0.024 if agent.is_sleeping else 0.055
        agent.energy = max(0.0, agent.energy - burn)
        agent.protein_balance = max(10.0, agent.protein_balance - (0.012 if agent.is_sleeping else 0.026))
        agent.action_fx = ""
        if agent.grief_ticks > 0:
            agent.grief_ticks -= 1
        # Natural warm-weather spoilage of unpreserved raw meat/fish (makes fire cooking & granaries vital!)
        if self.world.ambient_temperature > 24.0 and self.world.tick_count % 120 == 0:
            for raw_c in ("wild_meat", "wild_fish"):
                if raw_c in agent.inventory and self.world.rng.random() < 0.14:
                    agent.inventory.remove(raw_c)
                    break
        # Freshwater Hydrology & Thirst Homeostasis
        thirst_burn = 0.088 if self.world.weather == "drought" else (0.018 if agent.is_sleeping else 0.044)
        agent.hydration = max(0.0, agent.hydration - thirst_burn)
        if self.world.weather in ("rain", "storm"):
            agent.hydration = min(100.0, agent.hydration + 0.42)
        elif self.world.elevation_at(agent.x, agent.y) < 0.28 or any(
            math.hypot(agent.x - cv.x, agent.y - cv.y) <= 4.5 for cv in self.world.caves.values()
        ):
            agent.hydration = min(100.0, agent.hydration + 1.8)

        if effective_temp < 8.0:
            agent.warmth = max(0.0, agent.warmth - (8.0 - effective_temp) * 0.022)
        else:
            agent.warmth = min(100.0, agent.warmth + 0.25)

        if agent.is_sleeping:
            agent.rest = min(100.0, agent.rest + 0.68)
            agent.action_label = "Sleeping deeply to restore strength"
            if agent.rest >= 92.0 or agent.energy < 20.0 or agent.hydration < 22.0 or agent.warmth < 24.0:
                agent.is_sleeping = False
        else:
            agent.rest = max(0.0, agent.rest - 0.058)
            local_night = self.world.is_night_at(agent.x, agent.y)
            if agent.rest < 22.0 or (
                local_night and agent.rest < 58.0 and agent.energy > 38.0 and agent.warmth > 42.0
            ):
                agent.is_sleeping = True
                agent.action_label = "Sleeping deeply to restore strength"

        stress_delta = -0.12
        sheltered_now = self.world.is_sheltered_at(agent.x, agent.y)
        if not sheltered_now and self.world.weather in ("storm", "snow"):
            stress_delta += 0.16
        elif self.world.is_night_at(agent.x, agent.y) and self.world.lunar_illumination > 0.82 and self.world.weather == "clear":
            stress_delta -= 0.06  # Calm silver full-moon illumination reduces nocturnal dread
        if local_crowd >= 6:
            stress_delta += (local_crowd - 5) * 0.18
        if agent.energy < 35.0 or agent.hydration < 30.0 or agent.warmth < 40.0:
            stress_delta += 0.20
        agent.stress = round(min(100.0, max(2.0, agent.stress + stress_delta)), 1)

        max_lifespan_days = self.compute_era_lifespan_years(agent.genome.vitality) * 365.0
        if agent.energy <= 1.0 or agent.hydration <= 1.0 or agent.warmth <= 1.0:
            agent.integrity -= 0.50
        elif agent.energy > 55.0 and agent.hydration > 45.0 and agent.warmth > 50.0 and not agent.illness:
            agent.integrity = min(100.0, agent.integrity + 0.12)

        if agent.age_days > max_lifespan_days:
            agent.integrity -= 0.35

        # Natural Pathology, Contagious Epidemics & Acquired Immunity (Zero Interference!)
        if not agent.illness and self.world.tick_count % 25 == 0:
            contracted = ""
            if effective_temp < 4.0 and agent.warmth < 36.0 and not sheltered_now and "cold_fever" not in agent.antibodies:
                if self.world.rng.random() < 0.045:
                    contracted = "cold_fever"
            elif agent.integrity < 72.0 and "wound_sepsis" not in agent.antibodies:
                if self.world.rng.random() < 0.055:
                    contracted = "wound_sepsis"
            elif (
                (local_crowd >= 6 or any(math.hypot(cp.x - agent.x, cp.y - agent.y) <= 5.5 for cp in self.world.corpses.values()))
                and "camp_plague" not in agent.antibodies
            ):
                if self.world.rng.random() < 0.032:
                    contracted = "camp_plague"
            elif agent.hydration < 26.0 and self.world.weather == "drought" and "toxin_sickness" not in agent.antibodies:
                if self.world.rng.random() < 0.04:
                    contracted = "toxin_sickness"
            elif self.world.elevation_at(agent.x, agent.y) < 0.35 and effective_temp > 21.0 and "vector_fever" not in agent.antibodies:
                if self.world.rng.random() < 0.018:
                    contracted = "vector_fever"
            elif any(an.alive and an.tamed_by and math.hypot(an.x - agent.x, an.y - agent.y) <= 4.5 for an in self.world.animals.values()) and "zoonotic_flu" not in agent.antibodies:
                if self.world.rng.random() < 0.014:
                    contracted = "zoonotic_flu"
            if contracted:
                agent.illness = contracted
                agent.illness_severity = 22.0
                self.disease_cases += 1
                agent.add_memory(f"Fell ill with aching chills ({contracted.replace('_', ' ')}).", self.world.day)
                if "first_disease_outbreak" not in self.discoveries and self.enable_culture:
                    self.discoveries["first_disease_outbreak"] = self.world.day
                    self._record_event(
                        "conflict",
                        f"NATURAL PATHOGEN! {agent.lineage} {agent.id} contracted {contracted.replace('_', ' ')}!",
                        [agent.id],
                        agent.x,
                        agent.y,
                        importance=4,
                    )

        if agent.illness:
            # Contagion spread to close non-immune peers (cold_fever & camp_plague)
            if agent.illness in ("cold_fever", "camp_plague") and nearby_others and self.world.tick_count % 20 == 0:
                for peer in nearby_others:
                    if not peer.illness and agent.illness not in peer.antibodies and math.hypot(peer.x - agent.x, peer.y - agent.y) <= 3.2:
                        if self.world.rng.random() < (0.045 if agent.illness == "camp_plague" else 0.025):
                            peer.illness = agent.illness
                            peer.illness_severity = 18.0
                            self.disease_cases += 1
                            peer.add_memory(f"Caught contagious {agent.illness.replace('_', ' ')} from {agent.id}.", self.world.day)
            # Immune progression vs severity
            immune_fight = (0.14 + agent.genome.vitality * 0.16) * (1.5 if agent.is_sleeping else 1.0) * (1.25 if agent.warmth > 58.0 and agent.energy > 50.0 else 0.55)
            pathogen_push = 0.24 if agent.illness in ("camp_plague", "wound_sepsis") else 0.18
            agent.illness_severity = max(0.0, min(100.0, agent.illness_severity + pathogen_push - immune_fight))
            if agent.illness_severity >= 48.0:
                agent.integrity -= 0.14 if agent.illness == "camp_plague" else 0.09
                agent.stress = min(100.0, agent.stress + 0.15)
            if agent.illness_severity >= 98.0:
                agent.integrity -= 0.45
            if agent.illness_severity <= 0.5:
                cured_name = agent.illness
                if cured_name not in agent.antibodies:
                    agent.antibodies.append(cured_name)
                agent.illness = ""
                agent.illness_severity = 0.0
                agent.add_memory(f"Recovered naturally from {cured_name.replace('_', ' ')} (acquired immunity).", self.world.day)

        # Exact 9-Month (270 Earth Days = 6,480 Hourly Ticks) Human Pregnancy Gestation -> Live Childbirth!
        if agent.is_pregnant and agent.alive:
            agent.gestation_ticks += 1
            if agent.gestation_ticks >= 6480:
                self._deliver_live_birth(agent)

        if agent.illness:
            agent.mood = "tense" if agent.illness_severity > 55.0 else "sleepy"
        elif agent.warmth < 38.0:
            agent.mood = "cold"
        elif agent.energy < 35.0:
            agent.mood = "hungry"
        elif agent.stress > 65.0:
            agent.mood = "tense"
        elif agent.is_sleeping or agent.rest < 26.0:
            agent.mood = "sleepy"
        elif agent.mood not in ("affectionate", "grieving", "inventing", "tense"):
            agent.mood = "curious" if agent.genome.curiosity > 0.58 else "content"

        if agent.integrity <= 0.0:
            agent.alive = False
            agent.death_day = self.world.day
            self.deaths_today += 1
            if not agent.cause_of_death:
                if agent.illness:
                    agent.cause_of_death = f"untreated {agent.illness.replace('_', ' ')}"
                elif agent.warmth <= 2.0:
                    agent.cause_of_death = "winter hypothermia"
                elif agent.energy <= 2.0:
                    agent.cause_of_death = "starvation"
                elif agent.hydration <= 2.0:
                    agent.cause_of_death = "dehydration"
                else:
                    agent.cause_of_death = "natural old age"
            # Leave physical remains on the ground so we can observe whether peers mourn, leave offerings, bury, or ignore!
            if len(self.world.corpses) < 28:
                cid = f"C-{agent.id}"
                self.world.corpses[cid] = MortalRemains(
                    id=cid,
                    fallen_id=agent.id,
                    lineage=agent.lineage,
                    x=agent.x,
                    y=agent.y,
                    death_day=self.world.day,
                    cause=agent.cause_of_death,
                )
            self._record_event(
                "death",
                f"{agent.lineage} {agent.id} perished from {agent.cause_of_death} (age {agent.age_years:.1f} yrs / {agent.age_days:.0f}d).",
                [agent.id],
                agent.x,
                agent.y,
                importance=3,
            )
            for other in self.living_agents:
                if other.trust_bonds.get(agent.id, 0.0) >= 0.35 and math.hypot(
                    other.x - agent.x, other.y - agent.y
                ) <= 8.0:
                    other.mood = "grieving"
                    other.grief_ticks = 260
                    other.stress = min(100.0, other.stress + 15.0)
                    other.add_memory(f"Saw the lifeless body of {agent.id}.", self.world.day)
            self._emit_fx("death", agent.x, agent.y, agent.id, agent.cause_of_death)

    def _act_step(
        self,
        agent: KobAgent,
        nearby_others: List[KobAgent],
        nearby_animals: List[Any],
        nearby_corpses: List[MortalRemains],
        tile_items: List[str],
        nearby_structs: List[WorldStructure],
        gx: int,
        gy: int,
    ) -> None:
        spd_mul = LINEAGE_SPECS[agent.lineage]["SpeedMul"]

        # 0. Physiological Sleep: curled up resting unless emergency hunger/cold wakes them
        if agent.is_sleeping:
            agent.action_label = "Sleeping deeply to restore strength"
            return

        # 0B. Authentic Human Infancy (0-1 yr carried by mother/shelter) & Early Childhood (1-5 yrs near camp)
        if agent.age_days < 365.0:
            mother_id = agent.parents[0] if agent.parents else None
            mother = self.agents.get(mother_id) if mother_id else None
            if mother is not None and mother.alive:
                # Carried / cradled right beside mother (< 0.85m)
                agent.x = round(mother.x + math.cos(mother.heading + 1.4) * 0.55, 2)
                agent.y = round(mother.y + math.sin(mother.heading + 1.4) * 0.55, 2)
                agent.action_label = f"Carried & cared for by mother {mother.id}"
                return
            # Orphaned infant stays sheltered at nearest hut or hearth
            safe_spot = next((s for s in nearby_structs if s.kind in ("shelter", "hearth")), None)
            if safe_spot is not None:
                self._move_smooth(agent, safe_spot.x, safe_spot.y, nearby_others, speed=0.14)
                agent.action_label = "Resting safely inside camp shelter"
                return
        elif agent.age_days < 1825.0:
            # Young child (1-5 yrs): plays & learns safely near parents/camp, never hunts, builds or pairs
            parent_ref = next((self.agents[pid] for pid in (agent.parents or ()) if pid in self.agents and self.agents[pid].alive), None)
            if parent_ref is not None and math.hypot(parent_ref.x - agent.x, parent_ref.y - agent.y) > 4.5:
                self._move_smooth(agent, parent_ref.x, parent_ref.y, nearby_others, speed=0.22 * spd_mul)
                agent.action_label = f"Following & learning from parent {parent_ref.id}"
                return
            if self.world.rng.random() < 0.72:
                agent.action_label = "Playing & observing elders near camp"
                return

        # 0C. Progressive Step-by-Step Construction (adults & juveniles collaboratively finish huts/edifices!)
        if agent.age_days >= 1825.0 and agent.energy > 45.0:
            unfinished = next(
                (s for s in nearby_structs if s.kind in ("shelter", "edifice") and getattr(s, "build_progress", 1.0) < 1.0),
                None,
            )
            if unfinished is not None:
                if math.hypot(unfinished.x - agent.x, unfinished.y - agent.y) > 2.2:
                    self._move_smooth(agent, unfinished.x, unfinished.y, nearby_others, speed=0.26 * spd_mul)
                    agent.action_label = f"Carrying timber & stone to {unfinished.kind} ({int(unfinished.build_progress * 100)}%)"
                else:
                    unfinished.build_progress = min(1.0, round(unfinished.build_progress + 0.15, 2))
                    agent.energy = max(20.0, agent.energy - 1.4)
                    agent.action_fx = "fire"
                    pct = int(unfinished.build_progress * 100)
                    agent.action_label = f"Building {unfinished.kind} ({pct}%)"
                    agent.pause_ticks = 3
                    if unfinished.build_progress >= 1.0:
                        self._record_event(
                            "construction",
                            f"Completed {unfinished.sensory_name} ({unfinished.id}) — roof & hearth finished by {agent.lineage} {agent.id}!",
                            [agent.id],
                            unfinished.x,
                            unfinished.y,
                            importance=4,
                        )
                return

        # 1A. Self-Medication & Empathetic Caregiving when injured or sick!
        remedy_codes = ("clinical_cure", "antiseptic_balm", "herbal_remedy", "medicinal_herb")
        held_remedy = next((c for c in remedy_codes if c in agent.inventory), None)
        # Zoopharmacognosy: both Live and Null instinctively consume healing herbs if carried while injured/sick
        if held_remedy and (agent.integrity < 78.0 or agent.illness):
            agent.inventory.remove(held_remedy)
            heal_val = BLIND_MATERIALS[held_remedy].healing
            agent.integrity = min(100.0, agent.integrity + (heal_val * 45.0 if heal_val <= 1.0 else heal_val))
            if agent.illness:
                sev_drop = 100.0 if held_remedy == "clinical_cure" else (85.0 if held_remedy == "antiseptic_balm" else (62.0 if held_remedy == "herbal_remedy" else 38.0))
                agent.illness_severity = max(0.0, agent.illness_severity - sev_drop)
                self.cures_applied += 1
                if agent.illness_severity <= 2.0:
                    cured = agent.illness
                    if cured not in agent.antibodies:
                        agent.antibodies.append(cured)
                    agent.illness = ""
                    agent.illness_severity = 0.0
                    agent.action_label = f"Cured {cured.replace('_', ' ')} with {BLIND_MATERIALS[held_remedy].observer_label}"
                    m_key = f"first_{held_remedy.replace('medicinal_herb', 'herbal_medicine')}"
                    if m_key not in self.discoveries:
                        self.discoveries[m_key] = self.world.day
                        self._record_event(
                            "invention",
                            f"MEDICAL CURE! {agent.lineage} {agent.id} cured {cured.replace('_', ' ')} using {BLIND_MATERIALS[held_remedy].observer_label}!",
                            [agent.id],
                            agent.x,
                            agent.y,
                            importance=5,
                        )
                else:
                    agent.action_label = f"Treating {agent.illness.replace('_', ' ')} with {BLIND_MATERIALS[held_remedy].observer_label}"
            else:
                agent.action_label = f"Applying {BLIND_MATERIALS[held_remedy].observer_label} to heal wounds"
                if "first_herbal_medicine" not in self.discoveries:
                    self.discoveries["first_herbal_medicine"] = self.world.day
                    self._record_event(
                        "invention",
                        f"NATURAL MEDICINE! {agent.lineage} {agent.id} healed wounds using wild Sootheleaf!",
                        [agent.id],
                        agent.x,
                        agent.y,
                        importance=5,
                    )
            agent.pause_ticks = 4
            agent.action_fx = "heal"
            self._emit_fx("heal", agent.x, agent.y, agent.id, "Medicine")
            agent.add_memory(f"Used {BLIND_MATERIALS[held_remedy].sensory_name} to ease pain.", self.world.day)
            return

        # Empathetic Caregiving: treat a sick mate or clanmate nearby!
        if self.enable_culture and held_remedy and nearby_others:
            sick_peer = next(
                (o for o in nearby_others if o.illness and (o.id == agent.partner_id or agent.genome.empathy > 0.55) and math.hypot(o.x - agent.x, o.y - agent.y) <= 3.0),
                None,
            )
            if sick_peer is not None:
                agent.inventory.remove(held_remedy)
                sev_drop = 100.0 if held_remedy == "clinical_cure" else (85.0 if held_remedy == "antiseptic_balm" else (62.0 if held_remedy == "herbal_remedy" else 42.0))
                sick_peer.illness_severity = max(0.0, sick_peer.illness_severity - sev_drop)
                sick_peer.integrity = min(100.0, sick_peer.integrity + 24.0)
                self.cures_applied += 1
                self.sharing_count += 1
                agent.skill_xp["healing"] = agent.skill_xp.get("healing", 0.0) + 1.5
                agent.prestige = round(agent.prestige + 1.8, 1)
                agent.trust_bonds[sick_peer.id] = min(2.0, agent.trust_bonds.get(sick_peer.id, 0.0) + 0.45)
                sick_peer.trust_bonds[agent.id] = min(2.0, sick_peer.trust_bonds.get(agent.id, 0.0) + 0.45)
                if sick_peer.illness_severity <= 2.0:
                    if sick_peer.illness not in sick_peer.antibodies:
                        sick_peer.antibodies.append(sick_peer.illness)
                    sick_peer.illness = ""
                    sick_peer.illness_severity = 0.0
                agent.action_label = f"Treating sick peer {sick_peer.id} with {BLIND_MATERIALS[held_remedy].observer_label}"
                agent.pause_ticks = 4
                return

        # 1B. Eat carried food (avoiding toxic_nightshade once learned!) or draw from granary
        if agent.energy < 62.0:
            knows_toxin = agent.insight_map.get("avoid_toxic", 0) >= 1
            edible_idx = next(
                (
                    i
                    for i, code in enumerate(agent.inventory)
                    if BLIND_MATERIALS[code].nutrition > 0 and not (knows_toxin and code == "toxic_nightshade")
                ),
                None,
            )
            if edible_idx is not None:
                code = agent.inventory.pop(edible_idx)
                mat = BLIND_MATERIALS[code]
                if mat.toxicity > 0:
                    agent.integrity = max(0.0, agent.integrity - mat.toxicity)
                    agent.insight_map["avoid_toxic"] = 1
                    for wit in nearby_others:
                        wit.insight_map["avoid_toxic"] = 1  # Observational social learning!
                    agent.mood = "tense"
                    agent.action_label = "Sickened by toxic Shadowberry (learned to avoid!)"
                    agent.add_memory(f"Sickened by {mat.sensory_name}—never eat again!", self.world.day)
                    if agent.integrity <= 0:
                        agent.cause_of_death = "toxic plant poisoning"
                else:
                    if code == "orb_sweet":
                        agent.hydration = min(100.0, agent.hydration + 22.0)
                    # Wrangham Cooking Hypothesis: eating near an active Hearth roasts food (+45% caloric bioavailability!)
                    near_fire = self.enable_culture and any(
                        st.kind == "hearth" and st.fuel > 0 and math.hypot(st.x - agent.x, st.y - agent.y) <= 4.5
                        for st in nearby_structs
                    )
                    cal_mul = 1.45 if near_fire else 1.0
                    agent.energy = min(100.0, agent.energy + mat.nutrition * cal_mul)
                    if near_fire:
                        agent.stress = max(2.0, agent.stress - 6.0)
                        agent.action_label = f"Roasting & eating {mat.observer_label} by the fire"
                        agent.add_memory(f"Cooked {mat.sensory_name} over warm embers—richer nourishment!", self.world.day)
                        if "first_cooked_meal" not in self.discoveries:
                            self.discoveries["first_cooked_meal"] = self.world.day
                    else:
                        agent.action_label = f"Eating {mat.observer_label}"
                        agent.add_memory(f"Ate {mat.sensory_name}.", self.world.day)
                agent.pause_ticks = 4
                return

            if self.enable_culture:
                for st in nearby_structs:
                    if st.kind == "granary" and st.stored_food > 0 and math.hypot(st.x - agent.x, st.y - agent.y) < 2.4:
                        st.stored_food -= 1
                        agent.energy = min(100.0, agent.energy + 38.0)
                        agent.action_label = "Feeding from communal nest store"
                        agent.pause_ticks = 4
                        return

        # 1C. Seek fresh river, shoreline, or cave-spring water when thirsty!
        if agent.hydration < 36.0:
            wx, wy = self.world.find_nearest_water_spot(agent.x, agent.y)
            sx, sy = self.world.find_nearest_dry_spot(wx, wy)
            agent.action_label = "Walking to river/spring to drink fresh water"
            self._move_smooth(agent, sx, sy, nearby_others, speed=0.26 * spd_mul)
            return

        # 1D. Mammalian Maternal Lactation & Parental Provisioning (identical mammalian biology in both Live & Null!)
        if agent.energy > 42.0 and agent.age_days >= 180.0:
            infant_needy = next(
                (
                    o for o in nearby_others
                    if o.age_days < 730.0
                    and (o.energy < 68.0 or o.hydration < 65.0 or o.warmth < 58.0)
                    and (o.id in agent.children_ids or agent.lineage == o.lineage or agent.genome.empathy > 0.42)
                ),
                None,
            )
            if infant_needy is not None:
                infant_needy.energy = min(100.0, infant_needy.energy + 24.0)
                infant_needy.hydration = min(100.0, infant_needy.hydration + 18.0)
                infant_needy.warmth = min(100.0, infant_needy.warmth + 18.0)
                agent.energy = max(25.0, agent.energy - 5.5)
                self.sharing_count += 1
                self.gifts_today += 1
                agent.action_label = f"Nursing & warming infant {infant_needy.id}"
                agent.pause_ticks = 2
                return

        if agent.energy > 58.0 and agent.genome.empathy > 0.35:
            family_hungry = next(
                (
                    o for o in nearby_others
                    if (
                        (o.age_days < 730.0 and o.energy < 62.0 and (o.id in agent.children_ids or agent.trust_bonds.get(o.id, 0.0) >= 0.45))
                        or (o.id == agent.partner_id and (o.is_pregnant or o.energy < 64.0))
                    )
                ),
                None,
            )
            edible_for_fam = next((i for i, c in enumerate(agent.inventory) if BLIND_MATERIALS[c].nutrition > 15 and BLIND_MATERIALS[c].toxicity == 0), None)
            if family_hungry is not None and edible_for_fam is not None:
                gift = agent.inventory.pop(edible_for_fam)
                family_hungry.energy = min(100.0, family_hungry.energy + BLIND_MATERIALS[gift].nutrition)
                self.sharing_count += 1
                self.gifts_today += 1
                role_lbl = "pregnant mate" if family_hungry.is_pregnant else ("partner" if family_hungry.id == agent.partner_id else "child")
                agent.action_label = f"Feeding {role_lbl} {family_hungry.id}"
                agent.pause_ticks = 3
                return

        # 2. Seek warmth or cave/subterranean shelter when freezing or caught in a storm/blizzard!
        if agent.warmth < 50.0 or (self.world.weather in ("storm", "snow") and agent.stress > 45.0 and not self.world.is_sheltered_at(agent.x, agent.y)):
            warm_targets: List[Tuple[float, float]] = [(cv.x, cv.y) for cv in self.world.caves.values()]
            for st in self.world.structures.values():
                if (st.kind == "hearth" and st.fuel > 0) or st.kind in ("shelter", "edifice", "burrow_network"):
                    warm_targets.append((st.x, st.y))
                    if self.enable_culture and st.kind == "hearth" and st.fuel < 35.0 and math.hypot(st.x - agent.x, st.y - agent.y) < 2.4:
                        fuel_idx = next(
                            (i for i, c in enumerate(agent.inventory) if BLIND_MATERIALS[c].flammability > 0.6),
                            None,
                        )
                        if fuel_idx is not None:
                            agent.inventory.pop(fuel_idx)
                            st.fuel = min(100.0, st.fuel + 45.0)
            warm_targets.extend(self.world.thermal_vents)
            if warm_targets:
                nearest = min(warm_targets, key=lambda p: math.hypot(p[0] - agent.x, p[1] - agent.y))
                agent.action_label = "Seeking cave/hearth shelter from weather"
                self._move_smooth(agent, nearest[0], nearest[1], nearby_others, speed=0.26 * spd_mul)
                return

        # 2B. Unscripted Reactions to Mortality & Fallen Peers (Vigil, Grave Offering, Stone Burial, or Avoidance)
        if self.enable_culture and nearby_corpses and agent.energy > 42.0:
            corpse = nearby_corpses[0]
            bond_dead = agent.trust_bonds.get(corpse.fallen_id, 0.0)
            dist_c = math.hypot(corpse.x - agent.x, corpse.y - agent.y)

            # A. Stone Cairn Burial Rite (if chosen via Cortex or high collectivism+empathy with stone/clay in hand)
            stone_idx = next(
                (i for i, c in enumerate(agent.inventory) if c in ("slab_dense", "clay_gray", "shard_translucent", "rod_porous")),
                None,
            )
            if stone_idx is not None and (
                agent.current_intent == "bury_cairn"
                or (bond_dead >= 0.45 and agent.genome.empathy > 0.72 and self.world.rng.random() < 0.05)
            ):
                if dist_c <= 2.4:
                    agent.inventory.pop(stone_idx)
                    self.world._struct_seq += 1
                    cairn = WorldStructure(
                        id=f"S-{self.world._struct_seq}",
                        kind="cairn",
                        sensory_name=f"memorial stone cairn for {corpse.fallen_id}",
                        x=corpse.x,
                        y=corpse.y,
                        creator_id=agent.id,
                        creator_lineage=agent.lineage,
                        created_day=self.world.day,
                        durability=800.0,
                        inscription=corpse.fallen_id,
                    )
                    self.world.structures[cairn.id] = cairn
                    self.world.corpses.pop(corpse.id, None)
                    self.stone_burials += 1
                    agent.current_intent = "forage"
                    agent.mood = "grieving"
                    agent.pause_ticks = 6
                    agent.action_fx = "bury"
                    self._emit_fx("bury", corpse.x, corpse.y, agent.id, f"Buried {corpse.fallen_id}")
                    agent.action_label = f"Raising burial cairn over {corpse.fallen_id}"
                    if "first_burial_rite" not in self.discoveries:
                        self.discoveries["first_burial_rite"] = self.world.day
                    self._record_event(
                        "philosophy",
                        f"FUNERARY RITE! {agent.lineage} {agent.id} stacked stones into a burial cairn over {corpse.fallen_id}.",
                        [agent.id],
                        corpse.x,
                        corpse.y,
                        importance=5,
                    )
                    return
                else:
                    self._move_smooth(agent, corpse.x, corpse.y, nearby_others, speed=0.22 * spd_mul)
                    return

            # B. Grave Offering (placing berry, fiber, shell, or precious mineral beside the body)
            if agent.inventory and (
                agent.current_intent == "leave_offering"
                or (bond_dead >= 0.40 and agent.genome.empathy > 0.70 and self.world.rng.random() < 0.04)
            ):
                if dist_c <= 2.4:
                    gift_code = agent.inventory.pop()
                    corpse.offerings.append(gift_code)
                    self.grave_offerings += 1
                    agent.current_intent = "forage"
                    agent.mood = "grieving"
                    agent.pause_ticks = 5
                    agent.action_fx = "vigil"
                    self._emit_fx("vigil", corpse.x, corpse.y, agent.id, f"Offering for {corpse.fallen_id}")
                    agent.action_label = f"Leaving {BLIND_MATERIALS[gift_code].observer_label} for fallen {corpse.fallen_id}"
                    if "first_grave_offering" not in self.discoveries:
                        self.discoveries["first_grave_offering"] = self.world.day
                    self._record_event(
                        "philosophy",
                        f"Grave offering! {agent.lineage} {agent.id} placed {BLIND_MATERIALS[gift_code].observer_label} beside fallen {corpse.fallen_id}.",
                        [agent.id],
                        corpse.x,
                        corpse.y,
                        importance=4,
                    )
                    return

            # C. Silent Mourning Vigil vs Fearful Avoidance
            if agent.current_intent == "vigil" or (bond_dead >= 0.50 and self.world.rng.random() < 0.06):
                corpse.vigils += 1
                self.mourning_vigils += 1
                agent.current_intent = "forage"
                agent.mood = "grieving"
                agent.pause_ticks = 6
                agent.action_label = f"Standing in silent vigil by {corpse.fallen_id}"
                if "first_mourning_vigil" not in self.discoveries:
                    self.discoveries["first_mourning_vigil"] = self.world.day
                self._record_event(
                    "philosophy",
                    f"Mourning vigil: {agent.lineage} {agent.id} stood silently beside the lifeless body of {corpse.fallen_id}.",
                    [agent.id],
                    corpse.x,
                    corpse.y,
                    importance=3,
                )
                return
            elif bond_dead <= 0.0 and agent.genome.caution > 0.74 and self.world.rng.random() < 0.06:
                self.corpse_avoidance += 1
                away_x = agent.x + (agent.x - corpse.x) * 2.2
                away_y = agent.y + (agent.y - corpse.y) * 2.2
                agent.action_label = f"Stepping away warily from fallen {corpse.fallen_id}"
                self._move_smooth(agent, away_x, away_y, nearby_others, speed=0.26 * spd_mul)
                return

        # 3. Emergent Hive / Communal Nest Pooling (`pool_nest`)
        if self.enable_culture and (agent.current_intent == "pool_nest" or agent.genome.collectivism > 0.80):
            edible_indices = [i for i, c in enumerate(agent.inventory) if BLIND_MATERIALS[c].nutrition > 0]
            if agent.energy > 70.0 and len(edible_indices) >= 1:
                for st in nearby_structs:
                    if st.kind == "granary" and st.stored_food < 30 and math.hypot(st.x - agent.x, st.y - agent.y) < 2.6:
                        agent.inventory.pop(edible_indices[0])
                        st.stored_food += 1
                        self.hive_pooling_count += 1
                        agent.action_label = "Pooling food into communal nest"
                        agent.current_intent = "forage"
                        agent.pause_ticks = 4
                        return

        # 3B. Proto-Agriculture (`plant_seed` — sowing cereal grain into spaced, recognizable garden beds!)
        if (
            self.enable_culture
            and "grain_seed" in agent.inventory
            and agent.energy > 68.0
            and len(self.world.structures) < 26
            and (agent.current_intent == "plant_seed" or (agent.inventory.count("grain_seed") >= 3 and self.world.rng.random() < 0.025))
        ):
            too_close_crop = any(
                st.kind == "crop_plot" and math.hypot(st.x - agent.x, st.y - agent.y) < 10.5
                for st in self.world.structures.values()
            )
            if not too_close_crop and len(nearby_structs) < 2:
                agent.inventory.remove("grain_seed")
                self.world._struct_seq += 1
                sx, sy = self.world.find_nearest_dry_spot(agent.x, agent.y)
                bp = [
                    {"shape": "box", "sx": 0.92, "sy": 0.05, "sz": 0.92, "px": 0, "py": 0.025, "pz": 0, "color": "#3f6212"},
                    {"shape": "cylinder", "sx": 0.06, "sy": 0.52, "sz": 0.06, "px": -0.26, "py": 0.28, "pz": -0.24, "color": "#facc15"},
                    {"shape": "cylinder", "sx": 0.06, "sy": 0.56, "sz": 0.06, "px": 0.0, "py": 0.30, "pz": -0.24, "color": "#84cc16"},
                    {"shape": "cylinder", "sx": 0.06, "sy": 0.52, "sz": 0.06, "px": 0.26, "py": 0.28, "pz": -0.24, "color": "#facc15"},
                    {"shape": "cylinder", "sx": 0.06, "sy": 0.54, "sz": 0.06, "px": -0.22, "py": 0.29, "pz": 0.22, "color": "#84cc16"},
                    {"shape": "cylinder", "sx": 0.06, "sy": 0.58, "sz": 0.06, "px": 0.18, "py": 0.31, "pz": 0.22, "color": "#facc15"},
                ]
                crop = WorldStructure(
                    id=f"S-{self.world._struct_seq}",
                    kind="crop_plot",
                    sensory_name="cultivated cereal garden",
                    x=sx,
                    y=sy,
                    creator_id=agent.id,
                    creator_lineage=agent.lineage,
                    created_day=self.world.day,
                    durability=420.0,
                    blueprint_3d=bp,
                )
                self.world.structures[crop.id] = crop
                self.crops_planted += 1
                agent.skill_xp["farming"] = agent.skill_xp.get("farming", 0.0) + 1.4
                agent.prestige = round(agent.prestige + 1.2, 1)
                agent.current_intent = "forage"
                agent.pause_ticks = 5
                agent.action_fx = "plant"
                self._emit_fx("plant", sx, sy, agent.id, "Planted crop")
                agent.action_label = "Tending cultivated cereal garden"
                if "first_agriculture" not in self.discoveries:
                    self.discoveries["first_agriculture"] = self.world.day
                    self._record_event(
                        "invention",
                        f"AGRICULTURE BORN! {agent.lineage} {agent.id} planted a cultivated cereal garden!",
                        [agent.id],
                        sx,
                        sy,
                        importance=5,
                    )
                return

        # 4A. Emergent Shoreline Fishing & Shellfish Gathering
        # Biological foraging/hunting when hungry is identical in Live & Null (cultural hunting intent remains Live-only)
        if ((self.enable_culture and agent.current_intent == "hunt") or agent.energy < 60.0) and nearby_animals:
            aquatic = [
                an for an in nearby_animals if an.species in ("silverfin_shoal", "tidecrawler", "pearlclam", "damweaver") and an.alive
            ]
            if aquatic:
                catch = aquatic[0]
                dist_aq = math.hypot(catch.x - agent.x, catch.y - agent.y)
                if dist_aq <= 3.3:
                    has_gear = agent.has_tool or ("fiber_dry" in agent.inventory)
                    chance = 0.65 if has_gear else 0.30
                    agent.action_label = f"Fishing along shoreline ({catch.species})"
                    agent.pause_ticks = 4
                    if self.world.rng.random() < chance:
                        catch.health -= 40.0
                        if catch.health <= 0:
                            catch.alive = False
                        agent.inventory.append("wild_fish")
                        if catch.species == "pearlclam" and len(agent.inventory) < 7:
                            agent.inventory.append("nacre_shell")
                        self.fishing_count += 1
                        agent.skill_xp["hunting"] = agent.skill_xp.get("hunting", 0.0) + 1.0
                        agent.prestige = round(agent.prestige + 0.6, 1)
                        agent.current_intent = "forage"
                        if "first_fishing" not in self.discoveries:
                            self.discoveries["first_fishing"] = self.world.day
                        self._record_event(
                            "hunt",
                            f"Shoreline fishing! {agent.lineage} {agent.id} harvested {FAUNA_CATALOG[catch.species]['label']}.",
                            [agent.id],
                            agent.x,
                            agent.y,
                            importance=4 if self.fishing_count == 1 else 3,
                        )
                    return

        # 4B. Emergent Taming (Packhound Wolves & Windstrider Wild Horses!) + Hunting All Terrestrial Prey & Megafauna
        if self.enable_culture and nearby_animals:
            tame_candidates = [
                an for an in nearby_animals if FAUNA_CATALOG.get(an.species, {}).get("tameable") and an.alive and not an.tamed_by
            ]
            edible_for_beast = [i for i, c in enumerate(agent.inventory) if BLIND_MATERIALS[c].nutrition > 15]
            if (
                tame_candidates
                and edible_for_beast
                and agent.energy > 70.0
                and agent.genome.empathy > 0.65
                and (agent.current_intent == "share" or self.world.rng.random() < 0.035)
            ):
                beast = tame_candidates[0]
                if math.hypot(beast.x - agent.x, beast.y - agent.y) <= 3.6:
                    agent.inventory.pop(edible_for_beast[0])
                    beast.tameness += 0.55
                    agent.action_label = f"Offering food to wild {beast.species} {beast.id}"
                    agent.pause_ticks = 4
                    if beast.tameness >= 1.0:
                        beast.tamed_by = agent.id
                        self.domesticated_count += 1
                        if "first_domestication" not in self.discoveries:
                            self.discoveries["first_domestication"] = self.world.day
                        self._record_event(
                            "altruism",
                            f"DOMESTICATION! {agent.lineage} {agent.id} tamed wild {FAUNA_CATALOG[beast.species]['label']} ({beast.id})!",
                            [agent.id],
                            agent.x,
                            agent.y,
                            importance=5,
                        )
                    return

        if self.enable_culture and agent.current_intent == "hunt" and nearby_animals:
            huntable = ("lumigrazer", "burrowhare", "craghorn", "rootboar", "thunderhorn", "titanotusk", "canopykin", "reedwing", "woolflock", "dunestrider", "tallneck", "frostantler", "meadowfowl", "shellback", "quillback")
            grazers = [an for an in nearby_animals if an.species in huntable and an.alive]
            if grazers:
                prey = grazers[0]
                pspec = FAUNA_CATALOG[prey.species]
                if math.hypot(prey.x - agent.x, prey.y - agent.y) <= 2.4:
                    # Cooperative Group Hunting (Tomasello Shared Intentionality): nearby allies join the hunt!
                    allies_hunting = [o for o in nearby_others if agent.trust_bonds.get(o.id, 0.0) >= 0.15 and math.hypot(o.x - prey.x, o.y - prey.y) <= 4.5]
                    group_dmg = (62.0 if agent.has_tool else 28.0) + len(allies_hunting) * 26.0
                    prey.health -= group_dmg
                    agent.action_fx = "attack"
                    self._emit_fx("attack", prey.x, prey.y, agent.id, f"Hunt {prey.species}")
                    agent.action_label = f"{'Group hunting' if allies_hunting else 'Hunting'} wild {prey.species} {prey.id}"
                    agent.pause_ticks = 3
                    # Dangerous megafauna / boars counter-charge if hunted solo without spears!
                    if prey.health > 0 and pspec.get("danger", 0) > 0 and not agent.has_tool and not allies_hunting:
                        counter = float(pspec["danger"]) * 0.65
                        agent.integrity = max(0.0, agent.integrity - counter)
                        agent.stress = min(100.0, agent.stress + 20.0)
                        agent.add_memory(f"Gored by charging {prey.species} while hunting unarmed!", self.world.day, permanent=True)
                        if agent.integrity <= 0:
                            agent.cause_of_death = f"charging {prey.species}"
                    if prey.health <= 0:
                        prey.alive = False
                        agent.skill_xp["hunting"] = agent.skill_xp.get("hunting", 0.0) + 1.5
                        agent.prestige = round(agent.prestige + 1.4, 1)
                        for _ in range(pspec.get("meat", 1)):
                            if len(agent.inventory) < 8:
                                agent.inventory.append("wild_meat")
                        # Share meat cooperatively with hunting allies!
                        for ally in allies_hunting[:2]:
                            if len(ally.inventory) < 8:
                                ally.inventory.append("wild_meat")
                            ally.skill_xp["hunting"] = ally.skill_xp.get("hunting", 0.0) + 1.0
                            agent.trust_bonds[ally.id] = min(2.0, agent.trust_bonds.get(ally.id, 0.0) + 0.25)
                            ally.trust_bonds[agent.id] = min(2.0, ally.trust_bonds.get(agent.id, 0.0) + 0.25)
                        if prey.species in ("titanotusk", "thunderhorn") and len(agent.inventory) < 8:
                            agent.inventory.append("ivory_horn")
                        self.hunts_count += 1
                        agent.current_intent = "forage"
                        if "first_hunt" not in self.discoveries:
                            self.discoveries["first_hunt"] = self.world.day
                        self._record_event(
                            "hunt",
                            f"{agent.lineage} {agent.id} hunted wild {pspec['label']} ({prey.id}).",
                            [agent.id],
                            agent.x,
                            agent.y,
                            importance=4 if pspec.get("meat", 1) >= 2 else 3,
                        )
                    return
                else:
                    agent.action_label = f"Tracking wild {prey.species} {prey.id}"
                    self._move_smooth(agent, prey.x, prey.y, nearby_others, speed=0.28 * spd_mul)
                    return

        # 5. Symmetric Social Free Will (Conflict vs Sharing vs Speech)
        if self.enable_culture and nearby_others:
            partner = self.world.rng.choice(nearby_others)
            bond = agent.trust_bonds.get(partner.id, 0.0)
            cross_species = partner.lineage != agent.lineage

            # A. Confrontation / Raid (Symmetric threshold!)
            if (
                agent.current_intent == "confront"
                or (
                    agent.genome.aggression > 0.72
                    and agent.genome.empathy < 0.35
                    and bond < 0.05
                    and (agent.energy < 45.0 or agent.stress > 65.0)
                    and self.world.rng.random() < 0.04
                )
            ):
                agent.current_intent = "forage"
                self.conflict_count += 1
                self.clashes_today += 1
                if cross_species:
                    self.inter_species_conflict += 1
                dmg = 9.0 + agent.genome.aggression * 11.0 + (8.0 if agent.has_tool else 0.0)
                partner.integrity = max(0.0, partner.integrity - dmg)
                agent.integrity = max(1.0, agent.integrity - 5.0)
                agent.mood = "tense"
                partner.mood = "tense"
                partner.stress = min(100.0, partner.stress + 25.0)
                agent.heading = math.atan2(partner.x - agent.x, partner.y - agent.y)
                agent.pause_ticks = 5
                stolen_desc = ""
                if partner.inventory and self.world.rng.random() < 0.55:
                    loot = partner.inventory.pop()
                    agent.inventory.append(loot)
                    stolen_desc = f" & seized {BLIND_MATERIALS[loot].observer_label}"
                if partner.integrity <= 0.0:
                    partner.cause_of_death = f"clash with {agent.lineage} {agent.id}"
                agent.trust_bonds[partner.id] = max(-2.0, bond - 0.85)
                partner.trust_bonds[agent.id] = max(-2.0, partner.trust_bonds.get(agent.id, 0.0) - 1.1)
                agent.action_label = f"Fighting {partner.lineage} {partner.id}"
                if "first_conflict" not in self.discoveries:
                    self.discoveries["first_conflict"] = self.world.day
                self._record_event(
                    "conflict",
                    f"{'Inter-species ' if cross_species else ''}Clash! {agent.lineage} {agent.id} attacked {partner.lineage} {partner.id}{stolen_desc}.",
                    [agent.id, partner.id],
                    agent.x,
                    agent.y,
                    importance=4,
                )
                return

            # B. Sharing / Reciprocal Aid (Symmetric threshold!)
            edible_indices = [i for i, c in enumerate(agent.inventory) if BLIND_MATERIALS[c].nutrition > 0]
            if (
                (
                    agent.current_intent == "share"
                    or (
                        agent.genome.empathy > 0.72
                        and agent.genome.aggression < 0.35
                        and partner.energy < 45.0
                        and self.world.rng.random() < 0.04
                    )
                )
                and agent.energy > 62.0
                and edible_indices
                and bond >= -0.25
            ):
                gift = agent.inventory.pop(edible_indices[0])
                partner.energy = min(100.0, partner.energy + BLIND_MATERIALS[gift].nutrition)
                agent.trust_bonds[partner.id] = min(2.0, bond + 0.45)
                partner.trust_bonds[agent.id] = min(2.0, partner.trust_bonds.get(agent.id, 0.0) + 0.55)
                agent.mood = "affectionate"
                partner.mood = "affectionate"
                agent.heading = math.atan2(partner.x - agent.x, partner.y - agent.y)
                agent.pause_ticks = 5
                agent.current_intent = "socialize"
                agent.action_label = f"Gifting food to {partner.lineage} {partner.id}"
                self.sharing_count += 1
                self.gifts_today += 1
                if cross_species:
                    self.inter_species_peace += 1
                    if "first_interspecies_peace" not in self.discoveries:
                        self.discoveries["first_interspecies_peace"] = self.world.day
                if "first_altruism" not in self.discoveries:
                    self.discoveries["first_altruism"] = self.world.day
                self._record_event(
                    "altruism",
                    f"{'Inter-species diplomacy! ' if cross_species else ''}{agent.lineage} {agent.id} shared {BLIND_MATERIALS[gift].observer_label} with {partner.lineage} {partner.id}.",
                    [agent.id, partner.id],
                    agent.x,
                    agent.y,
                    importance=4 if cross_species else 3,
                )
                return

            # B2. Bilateral Barter Trade (Exchanging two distinct items!)
            if (
                agent.inventory
                and partner.inventory
                and bond >= -0.1
                and (
                    agent.current_intent == "barter"
                    or (agent.genome.sociability > 0.68 and self.world.rng.random() < 0.035)
                )
            ):
                give_item = agent.inventory[-1]
                take_item = next((c for c in partner.inventory if c != give_item), None)
                if take_item is not None:
                    agent.inventory.remove(give_item)
                    partner.inventory.remove(take_item)
                    agent.inventory.append(take_item)
                    partner.inventory.append(give_item)
                    agent.trust_bonds[partner.id] = min(2.0, bond + 0.35)
                    partner.trust_bonds[agent.id] = min(2.0, partner.trust_bonds.get(agent.id, 0.0) + 0.35)
                    self.trade_count += 1
                    agent.skill_xp["trading"] = agent.skill_xp.get("trading", 0.0) + 0.8
                    partner.skill_xp["trading"] = partner.skill_xp.get("trading", 0.0) + 0.8
                    agent.current_intent = "socialize"
                    agent.pause_ticks = 4
                    agent.action_label = f"Trading {BLIND_MATERIALS[give_item].observer_label} with {partner.id}"
                    is_proto_curr = give_item in ("nacre_shell", "gold_nugget", "silver_ore", "crafted_ornament") or take_item in ("nacre_shell", "gold_nugget", "silver_ore", "crafted_ornament")
                    if is_proto_curr and "first_proto_currency" not in self.discoveries:
                        self.discoveries["first_proto_currency"] = self.world.day
                    if "first_barter_trade" not in self.discoveries:
                        self.discoveries["first_barter_trade"] = self.world.day
                    if self.trade_count <= 3 or is_proto_curr or (cross_species and self.trade_count % 5 == 0) or self.trade_count % 15 == 0:
                        self._record_event(
                            "altruism",
                            f"{'Inter-species trade! ' if cross_species else 'Barter trade: '}{agent.lineage} {agent.id} exchanged {BLIND_MATERIALS[give_item].observer_label} with {partner.lineage} {partner.id} for {BLIND_MATERIALS[take_item].observer_label}.",
                            [agent.id, partner.id],
                            agent.x,
                            agent.y,
                            importance=5 if (cross_species or is_proto_curr) else 3,
                        )
                    return

            # C. Acoustic Communication & Elder Cumulative Cultural Mentorship (Henrich Collective Brain!)
            if agent.age_days >= 180.0 and partner.age_days < 730.0 and agent.insight_map and bond >= 0.15:
                for k_lore, lvl in agent.insight_map.items():
                    if partner.insight_map.get(k_lore, 0) < lvl:
                        partner.insight_map[k_lore] = lvl
                for ref_k, w_val in agent.personal_lexicon.items():
                    partner.personal_lexicon.setdefault(ref_k, w_val)

            if bond > -0.4 and self.world.rng.random() < 0.055 * agent.genome.sociability:
                ref = "cold" if agent.warmth < 55 else ("food" if agent.energy < 64 else "kin")
                word = agent.personal_lexicon.get(ref)
                if not word:
                    word = normalize_phonetic_utterance(
                        "", fallback_seed=self.world.tick_count + int(agent.id.split("-")[1]) * 19
                    )
                    agent.personal_lexicon[ref] = word
                agent.last_utterance = word
                agent.last_referent = ref
                agent.utterance_ttl = 12
                agent.heading = math.atan2(partner.x - agent.x, partner.y - agent.y)
                agent.pause_ticks = 3
                agent.action_label = f"Speaking «{word}» ({ref}) to {partner.id}"
                agent.trust_bonds[partner.id] = min(2.0, bond + 0.06)
                partner.trust_bonds[agent.id] = min(2.0, partner.trust_bonds.get(agent.id, 0.0) + 0.06)
                if ref not in partner.personal_lexicon or partner.trust_bonds.get(agent.id, 0.0) > 0.65:
                    partner.personal_lexicon[ref] = word
                    if cross_species and "first_interspecies_pidgin" not in self.discoveries:
                        self.discoveries["first_interspecies_pidgin"] = self.world.day
                        self._record_event(
                            "lexicon",
                            f"Cross-species Pidgin! {agent.lineage} {agent.id} & {partner.lineage} {partner.id} converged on «{word}» for '{ref}'.",
                            [agent.id, partner.id],
                            agent.x,
                            agent.y,
                            importance=5,
                        )
                    elif "first_shared_word" not in self.discoveries:
                        self.discoveries["first_shared_word"] = self.world.day
                        self._record_event(
                            "lexicon",
                            f"Shared speech: {agent.id} and {partner.id} converged on «{word}» for '{ref}'.",
                            [agent.id, partner.id],
                            agent.x,
                            agent.y,
                            importance=4,
                        )
                if bond >= 0.45 and agent.insight_map:
                    k_lore, lvl = max(agent.insight_map.items(), key=lambda kv: kv[1])
                    if partner.insight_map.get(k_lore, 0) < lvl:
                        partner.insight_map[k_lore] = partner.insight_map.get(k_lore, 0) + 1
                # Long-Range Telecommunication Broadcast if near a Comm Relay or Orbital Satellite!
                active_relay = next(
                    (
                        s for s in self.world.structures.values()
                        if s.signal_range > 0 and (s.layer == "orbital" or math.hypot(s.x - agent.x, s.y - agent.y) <= 5.0)
                    ),
                    None,
                )
                if active_relay is not None and agent.last_utterance:
                    for listener in self.living_agents:
                        if listener.id != agent.id and math.hypot(listener.x - agent.x, listener.y - agent.y) <= active_relay.signal_range:
                            listener.personal_lexicon.setdefault(agent.last_referent or "kin", agent.last_utterance)

        # 5B. Subterranean Colony Excavation (`excavate` — Ant-like underground tunnels if freely chosen!)
        if (
            self.enable_culture
            and agent.current_intent == "excavate"
            and agent.energy > 62.0
            and len(self.world.structures) < 32
        ):
            agent.current_intent = "forage"
            existing_b = next(
                (s for s in self.world.structures.values() if s.kind == "burrow_network" and math.hypot(s.x - agent.x, s.y - agent.y) < 9.5),
                None,
            )
            if existing_b is not None:
                existing_b.chambers += 1
                existing_b.durability = min(900.0, existing_b.durability + 120.0)
                agent.action_label = f"Expanding subterranean tunnel network ({existing_b.chambers} chambers)"
                agent.pause_ticks = 5
                return
            elif agent.has_tool or agent.genome.collectivism > 0.76:
                self.world._struct_seq += 1
                sx, sy = self.world.find_nearest_dry_spot(agent.x, agent.y)
                burrow = WorldStructure(
                    id=f"S-{self.world._struct_seq}",
                    kind="burrow_network",
                    sensory_name="excavated subterranean tunnel chamber",
                    x=sx,
                    y=sy,
                    creator_id=agent.id,
                    creator_lineage=agent.lineage,
                    created_day=self.world.day,
                    durability=650.0,
                    layer="subterranean",
                    tech_tier=2,
                    chambers=2,
                )
                self.world.structures[burrow.id] = burrow
                agent.action_label = "Excavating subterranean colony chamber"
                agent.pause_ticks = 6
                if "struct_burrow_network" not in self.discoveries:
                    self.discoveries["struct_burrow_network"] = self.world.day
                self._record_event(
                    "invention",
                    f"SUBTERRANEAN LIFE! {agent.lineage} {agent.id} excavated an underground tunnel chamber ({burrow.id})!",
                    [agent.id],
                    sx,
                    sy,
                    importance=5,
                )
                return

        # 6. Cortex-Willed Empirical Tinkering
        if self.enable_culture and agent.cortex_experiment_ready and len(agent.inventory) >= 2:
            agent.cortex_experiment_ready = False
            non_food = [c for c in agent.inventory if BLIND_MATERIALS[c].nutrition == 0]
            candidates = non_food if len(non_food) >= 2 else agent.inventory
            if len(candidates) >= 2:
                item_a, item_b = self.world.rng.sample(candidates, 2)
                self.experiment_trials += 1
                mark_word = next(iter(agent.personal_lexicon.values()), "")
                crafted, struct, outcome_kind, desc = self.world.attempt_empirical_experiment(
                    item_a,
                    item_b,
                    agent.inventory,
                    agent.insight_map,
                    agent.x,
                    agent.y,
                    agent.id,
                    actor_lineage=agent.lineage,
                    utterance_mark=mark_word,
                )
                agent.action_label = f"Tinkering: {BLIND_MATERIALS[item_a].observer_label} + {BLIND_MATERIALS[item_b].observer_label}"
                agent.pause_ticks = 6
                agent.add_memory(desc, self.world.day)
                if outcome_kind == "partial_insight":
                    self._record_event("insight", f"{agent.lineage} {agent.id}: {desc}", [agent.id], agent.x, agent.y, importance=2)
                elif outcome_kind != "breakthrough":
                    # Open-Ended Combinatorial Material Physics (unscripted emergent compound synthesis)
                    proc = self.world.rng.choice(VALID_PROCESSES)
                    comp = synthesize_open_compound(item_a, item_b, proc, self.world.ambient_temperature)
                    if comp is not None and comp.compound_id not in self.emergent_compounds:
                        geo = earth_location_summary(agent.x, agent.y)
                        c_rec = comp.to_dict()
                        c_rec["discoverer"] = agent.id
                        c_rec["lineage"] = agent.lineage
                        c_rec["day"] = self.world.day
                        c_rec["year"] = self.world.year
                        c_rec["region"] = geo["region"]
                        c_rec["coords"] = geo["coords_str"]
                        self.emergent_compounds[comp.compound_id] = c_rec
                        agent.prestige = round(agent.prestige + 1.8, 1)
                        agent.skill_xp["crafting"] = agent.skill_xp.get("crafting", 0.0) + 1.5
                        if comp.functional_class == "empirical_remedy" and agent.illness:
                            agent.illness = None
                            agent.illness_severity = 0.0
                            self.cures_applied += 1
                        elif comp.functional_class == "insulating_weave":
                            if "warm_cloak" not in agent.inventory:
                                agent.inventory.append("warm_cloak")
                        elif comp.functional_class in ("composite_edge", "proto_alloy"):
                            if "composite_tool" not in agent.inventory:
                                agent.inventory.append("composite_tool")
                        agent.add_memory(f"Synthesized novel {comp.functional_class} {comp.compound_id} ({comp.formula})", self.world.day, permanent=True)
                        self._record_event(
                            "breakthrough",
                            f"Open Synthesis ({geo['region']}): {agent.lineage} {agent.id} created {comp.compound_id} [{comp.functional_class}] {comp.formula}",
                            [agent.id],
                            agent.x,
                            agent.y,
                            importance=4,
                        )
                elif outcome_kind == "breakthrough":
                    agent.inventory.remove(item_a)
                    agent.inventory.remove(item_b)
                    agent.skill_xp["crafting" if crafted else "building"] = agent.skill_xp.get("crafting" if crafted else "building", 0.0) + 2.0
                    agent.prestige = round(agent.prestige + 2.5, 1)
                    agent.action_fx = "fire"
                    self._emit_fx("fire", agent.x, agent.y, agent.id, desc[:28])
                    agent.add_memory(f"Invented/built: {desc}", self.world.day, permanent=True)
                    if crafted:
                        agent.inventory.append(crafted)
                        m_key = f"craft_{crafted}"
                    else:
                        if struct.kind in ("shelter", "edifice"):
                            struct.build_progress = 0.25  # Starts at Phase 1: stone foundation & corner timber posts!
                        m_key = f"struct_{struct.kind}"  # type: ignore[union-attr]
                    # Observational / Vicarious Social Learning (Bandura & Henrich Cultural Ratchet!):
                    # Nearby witnesses imitate & acquire the inventor's empirical insights naturally!
                    for witness in nearby_others:
                        if math.hypot(witness.x - agent.x, witness.y - agent.y) <= 8.0 and self.world.rng.random() < (0.45 + witness.genome.curiosity * 0.45):
                            for k_lore, lvl in agent.insight_map.items():
                                witness.insight_map[k_lore] = max(witness.insight_map.get(k_lore, 0), lvl)
                            witness.add_memory(f"Observed {agent.id} achieve: {desc[:60]}", self.world.day)
                    agent.mood = "inventing"
                    is_first = m_key not in self.discoveries
                    if is_first:
                        self.discoveries[m_key] = self.world.day
                    self._record_event(
                        "invention" if is_first else "craft",
                        f"{'BREAKTHROUGH! ' if is_first else ''}{agent.lineage} {agent.id}: {desc}",
                        [agent.id],
                        agent.x,
                        agent.y,
                        importance=5 if is_first else 3,
                    )
                return

        # 7. Gather & Stockpile Ground Materials (`max_carry` up to 12 with Wheeled Cart!)
        max_carry = 12 if (self.enable_culture and agent.has_cart) else (8 if (self.enable_culture and (agent.has_tool or agent.has_cloak)) else 6)
        if tile_items:
            edibles = [c for c in tile_items if BLIND_MATERIALS[c].nutrition > 0]
            # Smart swap: if hungry and hands full of non-food, drop 1 non-edible item to grab food!
            if edibles and agent.energy < 76.0 and len(agent.inventory) >= max_carry:
                drop_idx = next(
                    (i for i, c in enumerate(agent.inventory) if BLIND_MATERIALS[c].nutrition == 0),
                    None,
                )
                if drop_idx is not None:
                    dropped = agent.inventory.pop(drop_idx)
                    tile_items.append(dropped)
            if len(agent.inventory) < max_carry:
                chosen = (
                    edibles[0]
                    if (edibles and (agent.energy < 76.0 or not self.enable_culture))
                    else self.world.rng.choice(tile_items)
                )
                self.world.remove_resource_at(gx, gy, chosen)
                agent.inventory.append(chosen)
                agent.action_label = f"Gathering {BLIND_MATERIALS[chosen].observer_label}"
                agent.pause_ticks = 3
                return

        # 8. O(1) Spatial Bucket Visual Foraging (7-tile eyesight, zero lag at large map scale!)
        has_edible_in_hand = any(BLIND_MATERIALS[c].nutrition > 0 for c in agent.inventory)
        if (agent.energy < 74.0 and not has_edible_in_hand) or len(agent.inventory) < 2:
            best_xy: Optional[Tuple[int, int]] = None
            best_dist = 999.0
            want_edible = agent.energy < 74.0 or not self.enable_culture
            bx0, by0 = gx >> 3, gy >> 3
            for dby in (-1, 0, 1):
                for dbx in (-1, 0, 1):
                    for (rx, ry) in self.world.resource_buckets.get((bx0 + dbx, by0 + dby), ()):
                        dx, dy = rx - gx, ry - gy
                        if abs(dx) > 7 or abs(dy) > 7:
                            continue
                        items = self.world.resources.get((rx, ry))
                        if not items:
                            continue
                        if want_edible and not any(BLIND_MATERIALS[c].nutrition > 0 for c in items):
                            continue
                        d = math.hypot(dx, dy)
                        if d < best_dist and self.world.is_walkable(rx, ry):
                            best_dist = d
                            best_xy = (rx, ry)
            if best_xy is not None:
                agent.action_label = "Walking toward spotted fruit/materials"
                self._move_smooth(agent, float(best_xy[0]), float(best_xy[1]), nearby_others, speed=0.25 * spd_mul)
                return

        # 8B. Active Human-Like Opposite-Sex Mate-Seeking, Courtship & Family Nesting (♂ + ♀)
        if (
            agent.age_days >= 7.0
            and not agent.is_pregnant
            and agent.energy > 52.0
            and agent.warmth > 46.0
            and agent.stress < 75.0
        ):
            opp_nearby = any(o.sex != agent.sex and not o.is_pregnant and o.age_days >= 7.0 for o in nearby_others)
            if not opp_nearby:
                lin_pop = sum(1 for o in self.living_agents if o.lineage == agent.lineage)
                candidates_mate = [
                    o
                    for o in self.living_agents
                    if o.id != agent.id
                    and o.sex != agent.sex
                    and not o.is_pregnant
                    and o.age_days >= 7.0
                    and (lin_pop <= 4 or not self._are_close_kin(agent, o))
                    and math.hypot(o.x - agent.x, o.y - agent.y) <= 95.0
                ]
                if candidates_mate:
                    # Prefer existing pair-bonded spouse, then same lineage, then exogamous cross-species partner!
                    best_mate = min(
                        candidates_mate,
                        key=lambda o: (
                            0 if o.id == agent.partner_id else (1 if o.lineage == agent.lineage else 2),
                            math.hypot(o.x - agent.x, o.y - agent.y),
                        ),
                    )
                    agent.mood = "affectionate"
                    sex_icon = "♀" if best_mate.sex == "F" else "♂"
                    agent.action_label = f"Seeking & courting {best_mate.lineage} {best_mate.id} ({sex_icon})"
                    self._move_smooth(agent, best_mate.x, best_mate.y, nearby_others, speed=0.27 * spd_mul)
                    return

        # 9. Smooth Purposeful Exploration & Continental Migration (No artificial pull to center!)
        if agent.target_xy is None or math.hypot(agent.target_xy[0] - agent.x, agent.target_xy[1] - agent.y) < 1.6:
            is_migrating = self.enable_culture and (agent.current_intent == "migrate" or agent.genome.curiosity > 0.78 and self.world.rng.random() < 0.14)
            span = 22.0 if is_migrating else 10.0
            if agent.current_intent == "migrate":
                agent.current_intent = "forage"
            # Gentle continental drift toward unexplored horizons when migrating, or stay near spouse/clan mates otherwise
            drift_x, drift_y = 0.0, 0.0
            if agent.partner_id and agent.partner_id in self.agents and self.agents[agent.partner_id].alive:
                sp_mate = self.agents[agent.partner_id]
                drift_x = (sp_mate.x - agent.x) * 0.25
                drift_y = (sp_mate.y - agent.y) * 0.25
            elif is_migrating:
                drift_x = (0.0 - agent.x) * 0.035  # Very gradual multi-generational horizon trek across vast continents!
                drift_y = (0.0 - agent.y) * 0.035
            elif nearby_others:
                mx = sum(o.x for o in nearby_others) / len(nearby_others)
                my = sum(o.y for o in nearby_others) / len(nearby_others)
                drift_x = (mx - agent.x) * 0.15
                drift_y = (my - agent.y) * 0.15
            nomad_span = 8.0 if (agent.is_pregnant and agent.gestation_ticks > 4200) else (36.0 if (self.world.soil_fertility_at(agent.x, agent.y) < 0.78 or agent.genome.curiosity > 0.62) else 18.0)
            tx, ty = self.world.find_nearest_dry_spot(
                max(-255.0, min(255.0, agent.x + drift_x + self.world.rng.uniform(-nomad_span, nomad_span))),
                max(-255.0, min(255.0, agent.y + drift_y + self.world.rng.uniform(-nomad_span, nomad_span))),
            )
            agent.target_xy = (tx, ty)
            agent.pause_ticks = 1
            return

        agent.action_label = "Nomadic continental exploration" if agent.genome.curiosity > 0.62 else "Exploring the valley"
        self._move_smooth(agent, agent.target_xy[0], agent.target_xy[1], nearby_others, speed=0.52 * spd_mul)

    def _move_smooth(
        self,
        agent: KobAgent,
        tx: float,
        ty: float,
        nearby_others: List[KobAgent],
        speed: float = 0.24,
    ) -> None:
        """Craig Reynolds Seek + Personal-Space Separation + Persistent Tangential Avoidance."""
        dx, dy = tx - agent.x, ty - agent.y
        dist = math.hypot(dx, dy)
        if dist <= 0.12:
            agent.target_xy = None
            return

        vx = dx / dist
        vy = dy / dist

        # Gentle Boids separation so two creatures don't overlap on the exact same spot
        for other in nearby_others:
            ox = agent.x - other.x
            oy = agent.y - other.y
            od = math.hypot(ox, oy)
            if 0.01 < od < 0.85:
                vx += (ox / od) * 0.45
                vy += (oy / od) * 0.45

        vnorm = math.hypot(vx, vy)
        if vnorm > 0.01:
            vx /= vnorm
            vy /= vnorm

        desired_heading = math.atan2(vx, vy)
        # Smooth angular turn limit (prevents spinning!)
        diff = _angle_diff(desired_heading, agent.heading)
        max_turn = 0.38
        agent.heading = (agent.heading + max(-max_turn, min(max_turn, diff))) % (2.0 * math.pi)

        step = min(dist, speed)
        nx = round(agent.x + math.sin(agent.heading) * step, 2)
        ny = round(agent.y + math.cos(agent.heading) * step, 2)
        if self.world.is_walkable(nx, ny):
            agent.x, agent.y = nx, ny
            return

        # Persistent single-direction skirt around obstacle (no left-right oscillation!)
        for mult in (1.0, 2.0):
            skirt_ang = agent.heading + agent.steer_side * 0.72 * mult
            sx = round(agent.x + math.sin(skirt_ang) * step, 2)
            sy = round(agent.y + math.cos(skirt_ang) * step, 2)
            if self.world.is_walkable(sx, sy):
                agent.heading = skirt_ang % (2.0 * math.pi)
                agent.x, agent.y = sx, sy
                return

        agent.steer_side *= -1.0
        agent.target_xy = None

    def _check_species_reproduction(self) -> None:
        """Human-Identical Sexual Courtship, Pair-Bonding & Mammalian Conception (♀ Female + ♂ Male)."""
        living_all = self.living_agents
        lin_counts = Counter(a.lineage for a in living_all)
        females = [
            a
            for a in living_all
            if a.sex == "F"
            and a.is_fertile
            and not a.is_pregnant
            and a.energy > 52.0
            and a.warmth > 46.0
            and a.stress < 76.0
        ]
        males = [
            b
            for b in living_all
            if b.sex == "M"
            and b.is_fertile
            and b.energy > 48.0
            and b.warmth > 44.0
            and b.stress < 78.0
        ]
        used_males = set()
        for fem in females:
            # Local Continental Carrying Capacity (55m basin max 180 real 1:1 individuals)
            local_basin_pop = sum(1 for o in living_all if math.hypot(o.x - fem.x, o.y - fem.y) < 55.0)
            if local_basin_pop >= 180:
                continue
            for mal in males:
                if mal.id in used_males:
                    continue
                if math.hypot(fem.x - mal.x, fem.y - mal.y) > 16.0:
                    continue
                # Westermarck incest taboo (waived only if lineage is in <=4 critical bottleneck)
                if lin_counts.get(fem.lineage, 0) > 4 and self._are_close_kin(fem, mal):
                    continue
                cross_lin = mal.lineage != fem.lineage
                if cross_lin and not self.enable_culture:
                    continue
                bond = fem.trust_bonds.get(mal.id, 0.0)
                # Active courtship builds mutual attraction & pair-bond
                fem.trust_bonds[mal.id] = min(2.0, bond + 0.24)
                mal.trust_bonds[fem.id] = min(2.0, mal.trust_bonds.get(fem.id, 0.0) + 0.24)
                bond = fem.trust_bonds[mal.id]
                min_bond = 0.26 if cross_lin else 0.12
                if self.enable_culture and bond < min_bond:
                    fem.action_label = f"Courting with {mal.lineage} {mal.id} (♂)"
                    mal.action_label = f"Courting with {fem.lineage} {fem.id} (♀)"
                    self.courtships_count += 1
                    continue
                chance = 0.26 if cross_lin else 0.36
                if self.world.rng.random() < chance:
                    used_males.add(mal.id)
                    self.courtships_count += 1
                    if fem.partner_id != mal.id:
                        self.couples_formed += 1
                    fem.partner_id = mal.id
                    mal.partner_id = fem.id
                    fem.is_pregnant = True
                    fem.gestation_ticks = 1
                    fem.pregnancy_father_id = mal.id
                    fem.pregnancy_father_genome = mal.genome
                    fem.mood = "affectionate"
                    mal.mood = "affectionate"
                    fem.action_fx = "court"
                    mal.action_fx = "court"
                    self._emit_fx("court", fem.x, fem.y, fem.id, f"{fem.id} ❤️ {mal.id}")
                    fem.action_label = f"Conceived child with mate {mal.id} (♂) · 🤰 Gestating"
                    mal.action_label = f"Bonded with mate {fem.id} (♀)"
                    # Spousal Cultural & Linguistic Sharing (Couples share words & discoveries!)
                    for k_lore, lvl in mal.insight_map.items():
                        fem.insight_map[k_lore] = max(fem.insight_map.get(k_lore, 0), lvl)
                    for k_lore, lvl in fem.insight_map.items():
                        mal.insight_map[k_lore] = max(mal.insight_map.get(k_lore, 0), lvl)
                    for rk, wv in mal.personal_lexicon.items():
                        fem.personal_lexicon.setdefault(rk, wv)
                    for rk, wv in fem.personal_lexicon.items():
                        mal.personal_lexicon.setdefault(rk, wv)
                    if "first_pair_bond" not in self.discoveries:
                        self.discoveries["first_pair_bond"] = self.world.day
                        self._record_event(
                            "birth",
                            f"HUMAN-LIKE COURTSHIP & CONCEPTION! {fem.lineage} {fem.id} (♀) & {mal.lineage} {mal.id} (♂) formed a pair-bond and conceived a child!",
                            [fem.id, mal.id],
                            fem.x,
                            fem.y,
                            importance=4,
                        )
                    break

    def _deliver_live_birth(self, mother: KobAgent) -> None:
        """Delivers a live mammalian/hominid Newborn (♂ or ♀) after pregnancy gestation completes!"""
        father_id = mother.pregnancy_father_id or mother.partner_id or mother.id
        father_ag = self.agents.get(father_id)
        father_genome = mother.pregnancy_father_genome or (father_ag.genome if father_ag else mother.genome)
        mother.is_pregnant = False
        mother.gestation_ticks = 0
        mother.pregnancy_father_id = ""
        mother.pregnancy_father_genome = None
        mother.energy = max(25.0, mother.energy - 18.0)

        num_babies = 2 if (self.world.rng.random() < 0.05 and len(self.living_agents) < 106) else 1
        for _ in range(num_babies):
            self._agent_seq += 1
            self.births_today += 1
            child_genome = KobGenome.crossover(mother.genome, father_genome, self.world.rng)
            # Inbreeding depression if bottleneck forced close-kin union + 4% spontaneous evolutionary mutations!
            if father_ag and self._are_close_kin(mother, father_ag):
                child_genome.vitality = max(0.10, round(child_genome.vitality - 0.14, 3))
            child_traits: List[str] = list(mother.genetic_traits[:2])
            if self.world.rng.random() < 0.04:
                mut = self.world.rng.choice(["cold_adapted", "strong_immunity", "keen_mind"])
                if mut not in child_traits:
                    child_traits.append(mut)
            c_lin = child_genome.lineage
            prefix = LINEAGE_SPECS[c_lin]["prefix"]
            cid = f"{prefix}-{self._agent_seq:03d}"
            father_gen = father_ag.generation if father_ag else mother.generation
            gen = max(mother.generation, father_gen) + 1
            self.max_generation = max(self.max_generation, gen)
            cx, cy = self.world.find_nearest_dry_spot(mother.x + self.world.rng.uniform(-0.8, 0.8), mother.y + self.world.rng.uniform(-0.8, 0.8))
            child_sex = "M" if self.world.rng.random() < 0.5 else "F"

            # Cumulative Family Cultural, Oral Tradition & Linguistic Inheritance!
            inherited_insights: Dict[str, int] = dict(mother.insight_map)
            inherited_lexicon: Dict[str, str] = dict(mother.personal_lexicon)
            inherited_lore: List[str] = list(mother.cultural_lore[-4:])
            if father_ag:
                for k_lore, lvl in father_ag.insight_map.items():
                    inherited_insights[k_lore] = max(inherited_insights.get(k_lore, 0), lvl)
                for rk, wv in father_ag.personal_lexicon.items():
                    inherited_lexicon.setdefault(rk, wv)
                for story in father_ag.cultural_lore[-3:]:
                    if story not in inherited_lore:
                        inherited_lore.append(story)
            if not inherited_lore and mother.memories:
                inherited_lore.append(f"Oral memory of {mother.id}: {mother.memories[-1]}")

            child = KobAgent(
                id=cid,
                generation=gen,
                born_day=self.world.day,
                x=cx,
                y=cy,
                genome=child_genome,
                sex=child_sex,
                parents=(mother.id, father_id),
                energy=84.0,
                hydration=92.0,
                warmth=88.0,
                heading=mother.heading,
                insight_map=inherited_insights,
                personal_lexicon=inherited_lexicon,
                cultural_lore=inherited_lore[-6:],
                genetic_traits=child_traits,
            )
            mother.action_fx = "birth"
            self._emit_fx("birth", cx, cy, mother.id, f"Born {cid}")
            child.trust_bonds[mother.id] = 0.95
            mother.trust_bonds[cid] = 0.95
            mother.children_ids.append(cid)
            if father_ag:
                child.trust_bonds[father_ag.id] = 0.92
                father_ag.trust_bonds[cid] = 0.92
                father_ag.children_ids.append(cid)
            self.agents[cid] = child

            cross_lin = (father_ag and father_ag.lineage != mother.lineage) or ("-" in c_lin and c_lin != mother.lineage)
            sex_lbl = "♂ son" if child_sex == "M" else "♀ daughter"
            if cross_lin and "first_sentient_speciation" not in self.discoveries:
                self.discoveries["first_sentient_speciation"] = self.world.day
                self._record_event(
                    "birth",
                    f"NEW HYBRID SENTIENT SPECIES BORN! Mother {mother.lineage} {mother.id} (♀) & Father {father_id} (♂) gave live birth to hybrid {c_lin} {sex_lbl} {cid}!",
                    [mother.id, father_id, cid],
                    cx,
                    cy,
                    importance=5,
                )
            else:
                if gen == 2 and "gen_2_born" not in self.discoveries:
                    self.discoveries["gen_2_born"] = self.world.day
                self._record_event(
                    "birth",
                    f"Live Birth (♀+♂): Mother {mother.lineage} {mother.id} & Father {father_id} welcomed newborn {sex_lbl} {cid} (Gen {gen}, {c_lin}).",
                    [mother.id, father_id, cid],
                    cx,
                    cy,
                    importance=3 if gen >= 2 else 2,
                )


class MiroFishObservatory:
    """Universe XXV v3.0 Master Observatory with Bilingual Daily Logs & Archetypes."""

    def __init__(self, ledger_dir: Path, seed: int = 4201, founders_per_lineage: int = 7) -> None:
        self.ledger_dir = ledger_dir
        self.ledger_dir.mkdir(parents=True, exist_ok=True)
        self.ledger_file = self.ledger_dir / "event_chain.jsonl"
        self.reports_dir = self.ledger_dir / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.warehouse = LongitudinalWarehouse(self.ledger_dir / "universe_xxv.sqlite")
        self.cortex = OllamaCortex()
        self.live = PopulationSimulation(
            seed=seed,
            founders_per_lineage=founders_per_lineage,
            enable_culture=True,
            cortex=self.cortex,
            warehouse=self.warehouse,
        )
        self.control = PopulationSimulation(
            seed=seed,
            founders_per_lineage=founders_per_lineage,
            enable_culture=False,
            cortex=None,
            warehouse=None,
        )

        self.speed_multiplier: int = 20  # Default x20 Earth-time pace (365d/yr, 24h/day, 9m pregnancy)!
        self.last_hash: str = "0" * 64
        self.history_series: List[Dict[str, Any]] = []
        self.daily_logs: List[Dict[str, Any]] = []
        self.reports: List[Dict[str, Any]] = []
        self._bg_tasks: set = set()
        self._last_logged_day: int = 0
        self._cached_metrics: Optional[Dict[str, Any]] = None

        self._append_ledger_entry(
            "UNIVERSE_XXV_V5_BOOT",
            {
                "seed": seed,
                "lineages": ["Sylphid", "Lithokin", "Vespera"],
                "founders_total": founders_per_lineage * 3,
                "default_speed": 5,
                "prime_directive": "STRICT_ZERO_INTERFERENCE",
                "timestamp": time.time(),
            },
        )
        self._restore_saved_cosmos_if_present()
        self._cached_metrics = self.compute_scientific_metrics()

    def _restore_saved_cosmos_if_present(self) -> None:
        """Restores ongoing civilization seamlessly on restart so evolution NEVER resets!"""
        state_path = self.ledger_dir / "latest_public_state.json"
        if not state_path.exists():
            return
        try:
            saved = json.loads(state_path.read_text(encoding="utf-8-sig"))
            w = saved.get("world", {})
            m = saved.get("metrics", {})
            saved_agents = saved.get("agents", [])
            if not saved_agents or w.get("tick", 0) <= 0:
                return

            self.live.world.tick_count = int(w["tick"])
            self.control.world.tick_count = int(w["tick"])
            self._last_logged_day = int(w.get("day", 1))
            self.live.agents.clear()
            max_seq = 0
            lex_by_lineage: Dict[str, Dict[str, str]] = defaultdict(dict)
            for sw in m.get("shared_lexicon", []):
                for lin in sw.get("lineages", ["Vespera"]):
                    lex_by_lineage[lin][sw["referent"]] = sw["word"]

            if len(saved_agents) > 180:
                by_lin: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
                for item in saved_agents:
                    by_lin[item.get("lineage", "Sylphid")].append(item)
                balanced: List[Dict[str, Any]] = []
                while len(balanced) < 180 and any(by_lin.values()):
                    for k in list(by_lin.keys()):
                        if by_lin[k] and len(balanced) < 180:
                            balanced.append(by_lin[k].pop(0))
                saved_agents = balanced

            lin_sex_seq: Dict[str, int] = defaultdict(int)
            for ad in saved_agents:
                aid = ad["id"]
                try:
                    seq_num = int(aid.split("-")[1])
                    max_seq = max(max_seq, seq_num)
                except Exception:
                    pass
                lin = ad.get("lineage", "Vespera")
                lin = {"Lith-Lith": "Lithokin", "Sylp-Sylp": "Sylphid", "Vesp-Vesp": "Vespera"}.get(lin, lin)
                sex_val = ad.get("sex")
                if sex_val not in ("M", "F"):
                    sex_val = "F" if (lin_sex_seq[lin] % 2 == 0) else "M"
                lin_sex_seq[lin] += 1
                gen_num = int(ad.get("gen", 1))
                age_d = float(ad.get("age", 10.0))
                born_d = max(1, int(round(self.live.world.day - age_d)))
                genome = KobGenome.random_founder(self.live.world.rng, lineage=lin)
                if ad.get("body_color"):
                    genome.body_color = ad["body_color"]
                if ad.get("accent_color"):
                    genome.accent_color = ad["accent_color"]
                if ad.get("crest") is not None:
                    genome.crest_variant = int(ad["crest"])
                inv: List[str] = []
                if ad.get("has_cloak"):
                    inv.append("warm_cloak")
                if ad.get("has_tool"):
                    inv.append("composite_tool")
                if ad.get("held_item") and ad["held_item"] in BLIND_MATERIALS and ad["held_item"] not in inv:
                    inv.append(ad["held_item"])

                raw_x, raw_y = float(ad["x"]), float(ad["y"])
                if not w.get("scale_v10") and abs(raw_x) < 75.0 and abs(raw_y) < 75.0:
                    raw_x, raw_y = self.live.world.find_nearest_dry_spot(raw_x * 3.15, raw_y * 3.15)
                self.live.world.ensure_frontier_around(raw_x, raw_y)

                is_preg = bool(ad.get("pregnant", False))
                gest_ticks = int(round(float(ad.get("gestation_pct", 0)) * 64.8)) if is_preg else 0
                ag = KobAgent(
                    id=aid,
                    generation=gen_num,
                    born_day=born_d,
                    x=raw_x,
                    y=raw_y,
                    genome=genome,
                    sex=sex_val,
                    partner_id=str(ad.get("partner_id", "")),
                    is_pregnant=is_preg,
                    gestation_ticks=gest_ticks,
                    pregnancy_father_id=str(ad.get("partner_id", "")) if is_preg else "",
                    children_ids=list(ad.get("children_ids", [])),
                    energy=float(ad.get("energy", 80.0)),
                    hydration=float(ad.get("hydration", 85.0)),
                    warmth=float(ad.get("warmth", 85.0)),
                    rest=float(ad.get("rest", 80.0)),
                    integrity=float(ad.get("integrity", 100.0)),
                    stress=float(ad.get("stress", 10.0)),
                    age_days=age_d,
                    illness=str(ad.get("illness", "")),
                    illness_severity=float(ad.get("illness_severity", 0.0)),
                    antibodies=list(ad.get("antibodies", [])),
                    cultural_lore=list(ad.get("cultural_lore", [])),
                    skill_xp=dict(ad.get("skill_xp", {})),
                    prestige=float(ad.get("prestige", 0.0)),
                    heading=float(ad.get("heading", 0.0)),
                    inventory=inv,
                    personal_lexicon=dict(lex_by_lineage.get(lin, {})),
                    memories=list(ad.get("memories", [])),
                    mood=ad.get("mood", "curious"),
                    current_intent=ad.get("intent", "forage"),
                    action_label=ad.get("action", "Exploring the valley"),
                    is_sleeping=bool(ad.get("sleeping", False)),
                    inner_thought=ad.get("thought", "Observing the valley."),
                )
                self.live.agents[aid] = ag

            # Restore warm intra-clan social trust among surviving peers
            ids = list(self.live.agents.keys())
            for i, id_a in enumerate(ids):
                for id_b in ids[i + 1 : i + 8]:
                    self.live.agents[id_a].trust_bonds[id_b] = 0.45
                    self.live.agents[id_b].trust_bonds[id_a] = 0.45

            self.live._agent_seq = max(max_seq, len(ids))
            self.live.max_generation = int(m.get("max_generation", 1))
            self.live.discoveries = dict(m.get("discoveries", {}))
            self.live.sharing_count = int(m.get("altruism_acts", 0))
            self.live.inter_species_peace = int(m.get("inter_species_peace", 0))
            self.live.conflict_count = int(m.get("conflict_acts", 0))
            self.live.experiment_trials = int(m.get("experiment_trials", 0))
            self.live.philosophical_count = int(m.get("philosophical_count", 0))
            self.live.hunts_count = int(m.get("hunts_count", 11))
            self.live.fishing_count = int(m.get("fishing_count", 0))
            self.live.domesticated_count = int(m.get("domesticated_count", 0))
            self.live.crops_planted = int(m.get("crops_planted", 0))
            self.live.trade_count = int(m.get("trade_count", 0))
            self.live.mourning_vigils = int(m.get("mourning_vigils", 0))
            self.live.grave_offerings = int(m.get("grave_offerings", 0))
            self.live.stone_burials = int(m.get("stone_burials", 0))
            self.live.corpse_avoidance = int(m.get("corpse_avoidance", 0))
            self.live.courtships_count = int(m.get("courtships_count", 0))
            self.live.couples_formed = int(m.get("bonded_couples", 0))
            self.live.disease_cases = int(m.get("disease_cases", 0))
            self.live.cures_applied = int(m.get("cures_applied", 0))
            self.live.planetary_population = float(max(len(self.live.living_agents), int(m.get("planetary_population", len(self.live.living_agents)))))
            # Upgrade legacy 24-species extinction list when expanding to 42-species full Earth biosphere!
            saved_extinct = dict(m.get("extinct_fauna", {}))
            if len(saved_extinct) > 10 and int(m.get("wild_species_total", 24)) < 40:
                self.live.world.extinct_fauna = {}
            else:
                self.live.world.extinct_fauna = saved_extinct

            # If upgrading from a legacy save without pair-bonds, naturally bond co-located adult ♀+♂ peers
            if not any(a.partner_id for a in self.live.living_agents):
                females_up = [a for a in self.live.living_agents if a.sex == "F" and a.age_days >= 7.0]
                males_up = [b for b in self.live.living_agents if b.sex == "M" and b.age_days >= 7.0]
                paired_m = set()
                preg_seeded = 0
                for fem in females_up:
                    best_m = None
                    best_d = 45.0
                    for mal in males_up:
                        if mal.id in paired_m:
                            continue
                        d = math.hypot(fem.x - mal.x, fem.y - mal.y)
                        if d < best_d:
                            best_d = d
                            best_m = mal
                    if best_m and len(paired_m) < 8:
                        paired_m.add(best_m.id)
                        fem.partner_id = best_m.id
                        best_m.partner_id = fem.id
                        fem.trust_bonds[best_m.id] = 1.25
                        best_m.trust_bonds[fem.id] = 1.25
                        self.live.couples_formed += 1
                        self.live.courtships_count += 2
                        if preg_seeded < 4:
                            preg_seeded += 1
                            fem.is_pregnant = True
                            fem.gestation_ticks = 45 + preg_seeded * 35
                            fem.pregnancy_father_id = best_m.id
                            fem.pregnancy_father_genome = best_m.genome
                            fem.action_label = f"Gestating child ({int(round(fem.gestation_ticks * 100 / 220))}%) with mate {best_m.id} (♂)"
                            best_m.action_label = f"Protecting & provisioning pregnant mate {fem.id} (♀)"
                if self.live.couples_formed > 0 and "first_pair_bond" not in self.live.discoveries:
                    self.live.discoveries["first_pair_bond"] = self.live.world.day
            self.cortex.total_calls = int(m.get("llm_deliberations", 0))
            self.live.timeline = list(saved.get("timeline", []))
            self.daily_logs = self.warehouse.recent_daily_summaries(limit=40)
            for h in saved.get("history", []):
                self.history_series.append(
                    {"day": h["day"], "live_population": h["live"], "control_population": h["ctrl"]}
                )

            # Restore structures cleanly with minimum spacing & upgrade legacy brown crop slabs to lush cereal gardens!
            garden_bp = [
                {"shape": "box", "sx": 0.92, "sy": 0.05, "sz": 0.92, "px": 0, "py": 0.025, "pz": 0, "color": "#3f6212"},
                {"shape": "cylinder", "sx": 0.06, "sy": 0.52, "sz": 0.06, "px": -0.26, "py": 0.28, "pz": -0.24, "color": "#facc15"},
                {"shape": "cylinder", "sx": 0.06, "sy": 0.56, "sz": 0.06, "px": 0.0, "py": 0.30, "pz": -0.24, "color": "#84cc16"},
                {"shape": "cylinder", "sx": 0.06, "sy": 0.52, "sz": 0.06, "px": 0.26, "py": 0.28, "pz": -0.24, "color": "#facc15"},
                {"shape": "cylinder", "sx": 0.06, "sy": 0.54, "sz": 0.06, "px": -0.22, "py": 0.29, "pz": 0.22, "color": "#84cc16"},
                {"shape": "cylinder", "sx": 0.06, "sy": 0.58, "sz": 0.06, "px": 0.18, "py": 0.31, "pz": 0.22, "color": "#facc15"},
            ]
            self.live.world.structures.clear()
            max_st_seq = 0
            # Prioritize non-crop landmarks first, then spaced cereal gardens
            saved_structs = sorted(
                saved.get("structures", []),
                key=lambda d: 1 if d.get("kind") == "crop_plot" else 0,
            )
            for sd in saved_structs:
                if len(self.live.world.structures) >= 26:
                    break
                skind = sd.get("kind", "shelter")
                sx = float(sd.get("x", 0.0))
                sy = float(sd.get("y", 0.0))
                if not w.get("scale_v10") and abs(sx) < 75.0 and abs(sy) < 75.0:
                    sx, sy = (
                        self.live.world.find_nearest_water_spot(sx * 3.15, sy * 3.15)
                        if skind == "watercraft"
                        else self.live.world.find_nearest_dry_spot(sx * 3.15, sy * 3.15)
                    )
                min_gap = 10.5 if skind == "crop_plot" else 3.8
                if any(
                    math.hypot(ex.x - sx, ex.y - sy) < (min_gap if (skind == "crop_plot" and ex.kind == "crop_plot") else 3.2)
                    for ex in self.live.world.structures.values()
                ):
                    continue
                sid = sd.get("id", f"S-{len(self.live.world.structures) + 1}")
                try:
                    max_st_seq = max(max_st_seq, int(str(sid).split("-")[1]))
                except Exception:
                    max_st_seq += 1
                creator_id = sd.get("creator") or (ids[len(self.live.world.structures) % len(ids)] if ids else "S-001")
                creator_lin = sd.get("lineage") or (
                    self.live.agents[creator_id].lineage if creator_id in self.live.agents else "Sylphid"
                )
                bp = garden_bp if skind == "crop_plot" else list(sd.get("blueprint_3d") or [])
                sname = "cultivated cereal garden" if skind == "crop_plot" else sd.get("name", skind)
                self.live.world.structures[sid] = WorldStructure(
                    id=sid,
                    kind=skind,
                    sensory_name=sname,
                    x=sx,
                    y=sy,
                    creator_id=creator_id,
                    creator_lineage=creator_lin,
                    created_day=int(sd.get("day") or max(1, self.live.world.day - 5)),
                    fuel=float(sd.get("fuel", 100.0)),
                    stored_food=int(sd.get("stored_food", 0)),
                    inscription=sd.get("inscription", ""),
                    water_crossing=(skind == "watercraft"),
                    layer=sd.get("layer", "subterranean" if skind == "burrow_network" else ("orbital" if skind == "orbital_satellite" else ("aerial" if skind == "air_craft" else "surface"))),
                    tech_tier=int(sd.get("tech_tier", 1)),
                    is_vehicle=bool(sd.get("is_vehicle", skind in ("watercraft", "land_vehicle", "air_craft", "orbital_satellite"))),
                    vehicle_speed=float(sd.get("vehicle_speed", 0.34 if skind == "watercraft" else 0.0)),
                    vehicle_domain=sd.get("vehicle_domain", "water" if skind == "watercraft" else "land"),
                    signal_range=float(sd.get("signal_range", 0.0)),
                    stories=int(sd.get("stories", 1)),
                    chambers=int(sd.get("chambers", 1)),
                    blueprint_3d=bp,
                )
            self.live.world._struct_seq = max(max_st_seq, len(self.live.world.structures))

            # Ensure all 3 continental enclaves are populated when upgrading from single-valley saves!
            present_lins = Counter(a.lineage for a in self.live.living_agents)
            for lin in ("Sylphid", "Lithokin", "Vespera"):
                if present_lins.get(lin, 0) == 0:
                    spawned = self.live._spawn_lineage_enclave(lin, 7)
                    cx, cy = ENCLAVE_HOMELANDS[lin]
                    self.live._record_event(
                        "genesis",
                        f"Distant Continent Surveyed: Native {lin} population ({len(spawned)} beings) observed thriving in their {lin} homeland!",
                        spawned[:3],
                        cx,
                        cy,
                        importance=4,
                    )
        except Exception:
            pass

    def _append_ledger_entry(self, record_type: str, payload: Dict[str, Any]) -> str:
        canonical = json.dumps(
            {"prev_hash": self.last_hash, "type": record_type, "payload": payload},
            sort_keys=True,
            ensure_ascii=False,
        )
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        line = json.dumps(
            {
                "seq_hash": digest,
                "prev_hash": self.last_hash,
                "type": record_type,
                "payload": payload,
            },
            ensure_ascii=False,
        )
        with self.ledger_file.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        self.last_hash = digest
        return digest

    async def step_once(self) -> None:
        requests = self.live.step_tick()
        self.control.step_tick()

        for agent, prompt in requests:
            task = asyncio.create_task(self._run_cortex_for_agent(agent, prompt))
            self._bg_tasks.add(task)
            task.add_done_callback(self._bg_tasks.discard)

        if self.live.world.tick_count % 20 == 0:
            self._cached_metrics = self.compute_scientific_metrics()

        if self.live.world.day > self._last_logged_day:
            self._last_logged_day = self.live.world.day
            metrics = self.compute_scientific_metrics()
            self._cached_metrics = metrics
            self.warehouse.record_epoch(metrics)

            daily_entry = self._build_bilingual_daily_summary(metrics)
            self.daily_logs.insert(0, daily_entry)
            if len(self.daily_logs) > 45:
                self.daily_logs.pop()
            self.warehouse.record_daily_summary(daily_entry)
            self.live.reset_daily_counters()

            self.history_series.append(metrics)
            if len(self.history_series) > 240:
                self.history_series.pop(0)

            (self.ledger_dir / "latest_public_state.json").write_text(
                json.dumps(self.snapshot_for_ui(), ensure_ascii=False), encoding="utf-8"
            )

            if self.live.world.day % 10 == 0:
                report = self.generate_era_report(metrics)
                self.reports.append(report)
                self._append_ledger_entry("SEASON_REPORT", report)

    async def _run_cortex_for_agent(self, agent: KobAgent, prompt: str) -> None:
        try:
            res = await self.cortex.deliberate(agent, prompt, self.live.world.tick_count)
            if res and agent.alive:
                agent.inner_thought = res["thought"]
                agent.current_intent = res["intent"]
                if res["intent"] == "tinker":
                    agent.cortex_experiment_ready = True
                ref = res["referent"]
                utt = res["utterance"]
                agent.personal_lexicon[ref] = utt
                agent.last_utterance = utt
                agent.last_referent = ref
                agent.utterance_ttl = 14
                if res.get("wonder"):
                    agent.existential_reflections += 1
                    self.live.philosophical_count += 1
                    if "first_philosophy" not in self.live.discoveries:
                        self.live.discoveries["first_philosophy"] = self.live.world.day
                    self.live._record_event(
                        "philosophy",
                        f"Existential wonder! {agent.lineage} {agent.id} pondered: «{agent.inner_thought}»",
                        [agent.id],
                        agent.x,
                        agent.y,
                        importance=5,
                    )
        finally:
            agent.pending_cortex = False

    def _classify_societal_archetype(
        self, mean_stress: float, clustering: float, pidgin_count: int
    ) -> Tuple[str, str]:
        """Purely descriptive sociological classification of what emerged on its own."""
        if any(s.kind == "orbital_satellite" for s in self.live.world.structures.values()):
            return ("Spacefaring Orbital Civilization", "Civilización Tecnológica Orbital")
        if any(s.tech_tier >= 4 for s in self.live.world.structures.values()):
            return ("Technological & Connected Society", "Sociedad Tecnológica e Interconectada")
        total_chambers = sum(s.chambers for s in self.live.world.structures.values() if s.kind == "burrow_network")
        if total_chambers >= 4:
            return ("Subterranean Fossorial Colony", "Colonia Subterránea Tipo Hormiguero")
        if mean_stress >= 58.0:
            return ("Calhoun Behavioral Sink", "Sumidero Conductual de Calhoun")
        if self.live.hive_pooling_count >= 5 and clustering >= 0.35:
            return ("Eusocial Hive Collective", "Colectivo Comunal Tipo Colmena")
        if self.live.conflict_count > (self.live.sharing_count * 1.6 + 4):
            return ("Rival Territorial Clans", "Clanes Territoriales en Conflicto")
        if pidgin_count >= 2 and self.live.inter_species_peace >= 3:
            return ("Multi-Species Symbiotic Society", "Sociedad Simbiótica Multi-Especie")
        if len(self.live.world.structures) >= 2:
            return ("Sedentary Proto-Civilization", "Proto-Civilización Sedentaria")
        return ("Primitive Foraging Bands", "Bandas Recolectoras Primitivas")

    def build_daily_briefing(self, m: Dict[str, Any]) -> Dict[str, Any]:
        """Builds a comprehensive, zero-jargon Daily Report broken down by Continent/Zone, Race & Astrophysics."""
        day = m["day"]
        year = m["year"]
        w = self.live.world
        living = self.live.living_agents

        zone_meta = {
            "temperate_archipelago": ("NW Emerald River Continent", "Continente Noroeste (Ríos y Bosques Templados)"),
            "boreal_highland": ("NE Boreal Volcanic Cordillera", "Cordillera Volcánica Boreal Noreste (Montañas y Frío)"),
            "equatorial_savanna": ("South Equatorial Monsoon Savanna", "Sabana Monzónica Ecuatorial Sur"),
            "mediterranean_crossroads": ("Central Continental Crossroads", "Encrucijada Continental Central"),
        }
        zones_report = []
        for z_key, (z_en, z_es) in zone_meta.items():
            z_agents = [a for a in living if classify_climate_zone(a.x, a.y) == z_key]
            z_structs = [s for s in w.structures.values() if classify_climate_zone(s.x, s.y) == z_key]
            z_lins = Counter(a.lineage for a in z_agents)
            lin_str = ", ".join(f"{k}: {v}" for k, v in z_lins.items()) or "Uninhabited / Sin habitantes"
            st_counts = Counter(s.kind for s in z_structs)
            st_str = ", ".join(f"{v} {k}" for k, v in st_counts.items()) or "Wilderness / Naturaleza virgen"
            in_caves = sum(
                1 for a in z_agents if any(math.hypot(a.x - cv.x, a.y - cv.y) <= 5.5 for cv in w.caves.values())
            )
            zones_report.append(
                {
                    "zone": z_key,
                    "title_en": z_en,
                    "title_es": z_es,
                    "pop": len(z_agents),
                    "lineages": lin_str,
                    "structures": st_str,
                    "in_caves": in_caves,
                }
            )

        sp_counts = m["species_counts"]
        all_races = list(dict.fromkeys(["Sylphid", "Lithokin", "Vespera"] + list(sp_counts.keys())))
        races_report = []
        for r_name in all_races:
            cnt = sp_counts.get(r_name, 0)
            r_members = [a for a in living if a.lineage == r_name]
            r_males = sum(1 for a in r_members if a.sex == "M")
            r_females = sum(1 for a in r_members if a.sex == "F")
            r_pregnant = sum(1 for a in r_members if a.is_pregnant)
            r_bonded = sum(1 for a in r_members if a.partner_id)
            avg_e = round(sum(a.energy for a in r_members) / max(1, len(r_members)), 1) if r_members else 0.0
            is_hybrid = "-" in r_name
            if cnt == 0:
                st_en, st_es = "Extinct (Natural Selection)", "Extinguida por selección natural"
            elif cnt <= 4:
                st_en, st_es = "Critical Bottleneck (Endangered!)", "Cuello de botella crítico (¡En peligro!)"
            elif cnt <= 12:
                st_en, st_es = "Stable Small Clan", "Clan pequeño estable"
            else:
                st_en, st_es = "Thriving & Expanding", "En plena expansión demográfica"
            races_report.append(
                {
                    "lineage": r_name,
                    "is_hybrid": is_hybrid,
                    "count": cnt,
                    "males": r_males,
                    "females": r_females,
                    "pregnant": r_pregnant,
                    "bonded": r_bonded,
                    "avg_energy": avg_e,
                    "status_en": st_en,
                    "status_es": st_es,
                }
            )

        todays_events = [ev["summary"] for ev in self.live.timeline if ev["day"] == day][-10:]
        if not todays_events:
            todays_events = [ev["summary"] for ev in self.live.timeline[-8:]]

        return {
            "day": day,
            "year": year,
            "season": m["season"],
            "temp_c": m["ambient_temp_c"],
            "weather": w.weather,
            "solar_au": w.solar_distance_au,
            "lunar_name": w.lunar_phase_name,
            "archetype_en": m["archetype_en"],
            "archetype_es": m["archetype_es"],
            "live_pop": m["live_population"],
            "null_pop": m["control_population"],
            "era_life_expectancy_yrs": m.get("era_life_expectancy_yrs", 36.0),
            "sick_count": m.get("sick_count", 0),
            "disease_cases": m.get("disease_cases", 0),
            "cures_applied": m.get("cures_applied", 0),
            "births_today": self.live.births_today,
            "deaths_today": self.live.deaths_today,
            "gifts_today": self.live.gifts_today,
            "clashes_today": self.live.clashes_today,
            "zones": zones_report,
            "races": races_report,
            "events": list(reversed(todays_events)),
        }

    def _build_bilingual_daily_summary(self, m: Dict[str, Any]) -> Dict[str, Any]:
        day = m["day"]
        year = m["year"]
        season = m["season"]
        season_es = {
            "Spring": "Primavera",
            "Summer": "Verano",
            "Autumn": "Otoño",
            "Deep Winter": "Invierno Profundo",
        }.get(season, season)
        sp = m["species_counts"]
        new_milestones = [k for k, d in m["discoveries"].items() if d == day]
        ms_text_en = f" New milestones: {', '.join(new_milestones)}!" if new_milestones else ""
        ms_text_es = f" ¡Nuevos hitos: {', '.join(new_milestones)}!" if new_milestones else ""

        summary_en = (
            f"Year {year}, Day {day} ({season}, {m['ambient_temp_c']}°C) — Form: {m['archetype_en']}. "
            f"Population: {m['live_population']} sentient beings (Sylphid:{sp.get('Sylphid',0)}, "
            f"Lithokin:{sp.get('Lithokin',0)}, Vespera:{sp.get('Vespera',0)}) vs {m['control_population']} Null Control. "
            f"Today: {self.live.births_today} births, {self.live.deaths_today} deaths, "
            f"{self.live.gifts_today} food gifts, {self.live.clashes_today} clashes. "
            f"Shared lexicon: {m['shared_words_count']} words ({m['pidgin_words_count']} Pidgin).{ms_text_en}"
        )
        summary_es = (
            f"Año {year}, Día {day} ({season_es}, {m['ambient_temp_c']}°C) — Organización: {m['archetype_es']}. "
            f"Población: {m['live_population']} seres sintientes (Sylphid:{sp.get('Sylphid',0)}, "
            f"Lithokin:{sp.get('Lithokin',0)}, Vespera:{sp.get('Vespera',0)}) frente a {m['control_population']} en Control Nulo. "
            f"Hoy: {self.live.births_today} nacimientos, {self.live.deaths_today} muertes, "
            f"{self.live.gifts_today} ayudas de comida, {self.live.clashes_today} combates. "
            f"Léxico común: {m['shared_words_count']} palabras ({m['pidgin_words_count']} Pidgin inter-especie).{ms_text_es}"
        )
        return {
            "day": day,
            "year": year,
            "season": season,
            "archetype_en": m["archetype_en"],
            "archetype_es": m["archetype_es"],
            "summary_en": summary_en,
            "summary_es": summary_es,
            "live_pop": m["live_population"],
            "null_pop": m["control_population"],
            "milestones": new_milestones,
            "briefing": self.build_daily_briefing(m),
        }

    def compute_scientific_metrics(self) -> Dict[str, Any]:
        living = self.live.living_agents
        ctrl_living = self.control.living_agents
        species_counts = Counter(a.lineage for a in living)

        wealth = sorted([len(a.inventory) * 25.0 + a.energy for a in living])
        gini = 0.0
        n = len(wealth)
        if n > 1 and sum(wealth) > 0:
            cum = sum((i + 1) * w for i, w in enumerate(wealth))
            gini = round((2.0 * cum) / (n * sum(wealth)) - (n + 1.0) / n, 3)

        word_counts: Counter = Counter()
        referent_map: Dict[str, Counter] = defaultdict(Counter)
        word_lineages: Dict[str, set] = defaultdict(set)
        for a in living:
            for ref, word in a.personal_lexicon.items():
                word_counts[word] += 1
                referent_map[ref][word] += 1
                word_lineages[word].add(a.lineage)

        total_words = sum(word_counts.values())
        entropy = 0.0
        if total_words > 0:
            for c in word_counts.values():
                p = c / total_words
                entropy -= p * math.log2(p)
        entropy = round(entropy, 3)

        shared_lexicon: List[Dict[str, Any]] = []
        pidgin_count = 0
        for ref, cnt in referent_map.items():
            top_word, freq = cnt.most_common(1)[0]
            if freq >= 2 and len(living) > 0:
                lins = sorted(word_lineages[top_word])
                is_pidgin = len(lins) >= 2
                if is_pidgin:
                    pidgin_count += 1
                shared_lexicon.append(
                    {
                        "referent": ref,
                        "word": top_word,
                        "speakers": freq,
                        "consensus_pct": round((freq / len(living)) * 100.0, 1),
                        "pidgin": is_pidgin,
                        "lineages": lins,
                    }
                )
        shared_lexicon.sort(key=lambda d: d["speakers"], reverse=True)

        g = nx.Graph()
        for a in living:
            g.add_node(a.id)
            for target_id, weight in a.trust_bonds.items():
                if weight >= 0.25 and target_id in self.live.agents and self.live.agents[target_id].alive:
                    g.add_edge(a.id, target_id, weight=weight)
        clustering = round(nx.average_clustering(g), 3) if len(g) >= 3 else 0.0

        mean_stress = round(sum(a.stress for a in living) / max(1, len(living)), 1)
        high_stress_pct = round(
            sum(1 for a in living if a.stress >= 60.0) / max(1, len(living)) * 100.0, 1
        )
        calhoun_sink = round((mean_stress / 100.0) * 0.6 + (high_stress_pct / 100.0) * 0.4, 3)

        arch_en, arch_es = self._classify_societal_archetype(mean_stress, clustering, pidgin_count)
        struct_counts = Counter(s.kind for s in self.live.world.structures.values())
        stored_surplus = sum(s.stored_food for s in self.live.world.structures.values())

        sleeping_now = sum(1 for a in living if a.is_sleeping)
        hungry_now = sum(1 for a in living if a.energy < 40.0)
        males_count = sum(1 for a in living if a.sex == "M")
        females_count = sum(1 for a in living if a.sex == "F")
        pregnant_count = sum(1 for a in living if a.is_pregnant)
        bonded_couples = sum(1 for a in living if a.partner_id) // 2
        sick_count = sum(1 for a in living if a.illness)
        era_life_exp = self.live.compute_era_lifespan_years(0.5)
        vocations_cnt = Counter(a.emergent_vocation for a in living)
        oral_traditions_count = sum(len(a.cultural_lore) for a in living)
        # Emergent Clan Leaders (highest-prestige adult per lineage, never assigned!)
        clan_leaders: Dict[str, Dict[str, Any]] = {}
        for lin_name in species_counts.keys():
            cands = [a for a in living if a.lineage == lin_name and a.age_days >= 14.0]
            if cands:
                top_l = max(cands, key=lambda x: (x.prestige, x.age_days, len(x.trust_bonds)))
                clan_leaders[lin_name] = {
                    "id": top_l.id,
                    "sex": top_l.sex,
                    "vocation": top_l.emergent_vocation,
                    "prestige": round(top_l.prestige, 1),
                    "age_years": top_l.age_years,
                }
        # Emergent Inter-Clan Diplomacy derived purely from real peace/trade vs clashes
        if self.live.inter_species_peace + self.live.trade_count > self.live.conflict_count * 2 + 5:
            diplomacy_en = "Peaceful Trade & Inter-Species Diplomacy"
            diplomacy_es = "Comercio Pacífico y Diplomacia Inter-Especie"
        elif self.live.conflict_count > self.live.inter_species_peace + 6:
            diplomacy_en = "Territorial Rivalry & Frontier Friction"
            diplomacy_es = "Rivalidad Territorial y Fricción Fronteriza"
        else:
            diplomacy_en = "Cautious Coexistence & First Contact"
            diplomacy_es = "Coexistencia Cautelosa y Primer Contacto"
        # Macro-Demographic Civilization Scale (visible focus individuals + thriving settlement hinterland estimate)
        settlement_bonus = (
            struct_counts.get("shelter", 0) * 6
            + struct_counts.get("crop_plot", 0) * 4
            + struct_counts.get("granary", 0) * 10
            + struct_counts.get("burrow_network", 0) * 14
            + struct_counts.get("edifice", 0) * 35
        )
        macro_population = max(
            int(round(self.live.planetary_population)),
            (4_000_000 + len(living) * 1250) if ("first_agriculture" in self.live.discoveries and len(living) >= 15) else len(living),
        )
        planetary_capacity = self.live.compute_planetary_carrying_capacity()
        total_f = max(1, len(living))
        species_macro_counts = {
            lin: int(round((cnt / total_f) * macro_population))
            for lin, cnt in species_counts.items()
        }
        day_of_year = ((max(1, self.live.world.day) - 1) % 365) + 1
        earth_era_label_es = f"Año {self.live.world.year} · Día {day_of_year}"
        earth_era_label_en = f"Year {self.live.world.year} · Day {day_of_year}"
        rare_held = sum(
            1 for a in living for c in a.inventory if c in BLIND_MATERIALS and BLIND_MATERIALS[c].luster >= 0.80
        )
        cloaks_held = sum(1 for a in living if a.has_cloak)
        tools_held = sum(1 for a in living if a.has_tool)

        MILESTONE_LABELS_EN = {
            "first_shared_word": "Coined first shared spoken word",
            "first_philosophy": "First existential reflection about the cosmos",
            "first_interspecies_pidgin": "Created cross-species bridge vocabulary",
            "first_conflict": "First territorial clash over resources",
            "gen_2_born": "Second generation born naturally",
            "first_pair_bond": "Formed first male-female pair-bond & pregnancy",
            "craft_warm_cloak": "Wove insulating plant-fiber cloaks for winter",
            "first_hunt": "Coordinated hunting of wild land herbivores",
            "first_fishing": "Shoreline fishing of river shoals & crabs",
            "first_domestication": "Tamed wild Packhounds as clan companions",
            "first_interspecies_peace": "Peaceful cross-species food sharing",
            "first_altruism": "Voluntary food gifting to hungry peers",
            "first_frontier_expansion": "Migrated beyond the home valley into new territories",
            "struct_hearth": "Controlled fire hearth ignited from pyrite & flint",
            "struct_shelter": "Built permanent stone-and-timber huts",
            "struct_granary": "Fired clay granaries to store food reserves",
            "struct_monolith": "Carved inscribed stone monument",
            "craft_composite_tool": "Hafted stone spear-knives onto wood",
            "craft_crafted_ornament": "Shaped precious minerals into symbolic ornaments",
            "craft_bronze_tool": "Smelted copper & tin into bronze blades",
            "craft_compass_stone": "Suspended lodestone into a magnetic compass",
            "first_mourning_vigil": "Held silent mourning vigil beside a fallen peer",
            "first_grave_offering": "Placed grave offerings beside the dead",
            "first_burial_rite": "Built permanent stone burial cairns for the dead",
            "first_herbal_medicine": "Discovered natural wound-healing with medicinal herbs",
            "first_disease_outbreak": "First natural pathogen illness recorded in population",
            "first_herbal_remedy": "Compounded botanical herbal remedy to cure illness",
            "first_antiseptic_balm": "Distilled antiseptic apothecary balm against infections",
            "first_clinical_cure": "Synthesized purified glass-vial clinical cure",
            "craft_herbal_remedy": "Compounded botanical herbal poultice remedy",
            "craft_antiseptic_balm": "Distilled antimicrobial resin-mineral antiseptic balm",
            "craft_clinical_cure": "Purified clinical-grade antimicrobial serum in glass",
            "craft_clay_tablet": "Invented permanent proto-writing on kiln-fired clay tablets",
            "first_proto_currency": "Adopted portable precious tokens as proto-currency",
            "first_leadership_council": "Emergent respected elder/guide leadership formed naturally",
            "struct_palisade": "Built fortified timber palisade walls against predators",
            "first_cooked_meal": "Roasted food over fire for higher nutrition",
            "first_agriculture": "Planted cereal seeds into cultivated farm plots",
            "first_barter_trade": "Established bilateral barter trade of goods",
            "struct_watercraft": "Built buoyant watercraft to cross rivers and seas",
            "craft_wheeled_cart": "Invented the axle-mounted wheeled transport cart",
            "struct_open_creation": "Synthesized a brand-new unscripted 3D apparatus",
            "first_fauna_speciation": "Wild fauna evolved into a brand-new daughter species",
            "first_sentient_speciation": "Cross-continent lineages birthed a new hybrid sentient race",
            "struct_burrow_network": "Excavated subterranean chambers & tunnel networks beneath the earth",
            "craft_silica_glass": "Fused siliceous stone into clear glass & optical lenses",
            "craft_copper_coil": "Discovered electromagnetic copper coils & induction",
            "craft_refined_fuel": "Distilled high-energy hydrocarbon propellant",
            "struct_edifice": "Erected multi-story stone-and-glass architectural edifices",
            "struct_comm_relay": "Built long-range acoustic/electromagnetic communication relays",
            "struct_land_vehicle": "Engineered self-propelled wheeled land vehicles",
            "struct_air_craft": "Launched buoyant aerial sky-vessels",
            "struct_orbital_satellite": "Launched an autonomous orbital satellite around the planet",
        }
        MILESTONE_LABELS_ES = {
            "first_shared_word": "Inventaron su primera palabra hablada común",
            "first_philosophy": "Primera reflexión existencial sobre la noche y el mundo",
            "first_interspecies_pidgin": "Crearon palabras puente entre distintas razas",
            "first_conflict": "Primer combate territorial por recursos",
            "gen_2_born": "Nacimiento natural de la 2.ª generación",
            "first_pair_bond": "Primera unión de pareja macho-hembra (♂+♀) y embarazo",
            "craft_warm_cloak": "Tejieron abrigos vegetales para resistir el invierno",
            "first_hunt": "Caza de animales terrestres salvajes",
            "first_fishing": "Pesca costera y fluvial de peces y crustáceos",
            "first_domestication": "Domesticación espontánea de animales salvajes",
            "first_interspecies_peace": "Entrega pacífica de comida entre distintas especies",
            "first_altruism": "Ayuda altruista dando alimento a compañeros hambrientos",
            "first_frontier_expansion": "Migración hacia nuevos territorios del planeta",
            "struct_hearth": "Dominio del fuego golpeando pirita y sílex",
            "struct_shelter": "Construcción de cabañas permanentes de piedra y madera",
            "struct_granary": "Vasijas y graneros de arcilla para guardar reservas",
            "struct_monolith": "Estela de piedra tallada con inscripciones",
            "craft_composite_tool": "Lanzas y cuchillos de sílex engarzados en madera",
            "craft_crafted_ornament": "Joyería/arte simbólico con minerales preciosos",
            "craft_bronze_tool": "Fundición de cobre y estaño (Edad del Bronce)",
            "craft_compass_stone": "Brújula magnética con magnetita suspendida",
            "first_mourning_vigil": "Primera vigilia silenciosa de duelo ante un fallecido",
            "first_grave_offering": "Primeras ofrendas depositadas junto a sus muertos",
            "first_burial_rite": "Primer rito funerario: túmulos de piedra sobre los difuntos",
            "first_herbal_medicine": "Descubrimiento de hierbas medicinales curativas",
            "first_disease_outbreak": "Primer brote de enfermedad natural registrado en la población",
            "first_herbal_remedy": "Primera curación de enfermedad con infusión/cataplasma herbal",
            "first_antiseptic_balm": "Primer bálsamo antiséptico de boticario contra infecciones",
            "first_clinical_cure": "Medicina moderna: primer suero clínico purificado en vidrio",
            "craft_herbal_remedy": "Preparación empírica de remedio herbal medicinal",
            "craft_antiseptic_balm": "Destilación de bálsamo antiséptico antimicrobiano",
            "craft_clinical_cure": "Síntesis de cura clínica purificada en vial de vidrio",
            "craft_clay_tablet": "Invención de la proto-escritura en tablillas de arcilla cocida",
            "first_proto_currency": "Adopción espontánea de proto-moneda para el intercambio",
            "first_leadership_council": "Surgimiento natural de liderazgo respetado / consejo de ancianos",
            "struct_palisade": "Murallas/empalizadas de madera frente a grandes depredadores",
            "first_cooked_meal": "Cocinado de alimentos al fuego (+nutrición)",
            "first_agriculture": "Nacimiento de la agricultura sembrando cereal",
            "first_barter_trade": "Primer comercio por trueque de bienes entre individuos",
            "struct_watercraft": "Construcción de balsas/embarcaciones para cruzar aguas",
            "craft_wheeled_cart": "Invención de la rueda y carros de transporte",
            "struct_open_creation": "Invención libre de un artefacto 3D inédito",
            "first_fauna_speciation": "Especiación darwiniana: nace una nueva especie animal salvaje",
            "first_sentient_speciation": "Hibridación fértil: nace una nueva raza inteligente",
            "struct_burrow_network": "Excavación de galerías y cámaras subterráneas (vida bajo tierra)",
            "craft_silica_glass": "Fundición de vidrio de sílice y lentes ópticas",
            "craft_copper_coil": "Descubrimiento de bobinas de cobre e inducción electromagnética",
            "craft_refined_fuel": "Destilación de combustible líquido de alta energía",
            "struct_edifice": "Arquitectura de edificios de varias plantas en piedra y vidrio",
            "struct_comm_relay": "Medios de comunicación a larga distancia (acústica / antenas)",
            "struct_land_vehicle": "Ingeniería de vehículos terrestres autopropulsados",
            "struct_air_craft": "Aeronaves capaces de volar sobre continentes y océanos",
            "struct_orbital_satellite": "Era Espacial: lanzamiento de satélite artificial en órbita planetaria",
        }

        milestone_list_en = [
            f"Day {d}: {MILESTONE_LABELS_EN.get(k, k)}"
            for k, d in sorted(self.live.discoveries.items(), key=lambda kv: kv[1])
        ]
        milestone_list_es = [
            f"Día {d}: {MILESTONE_LABELS_ES.get(k, k)}"
            for k, d in sorted(self.live.discoveries.items(), key=lambda kv: kv[1])
        ]

        top_word_info_en = (
            f"For example, {shared_lexicon[0]['consensus_pct']}% of the group says «{shared_lexicon[0]['word']}» to mean '{shared_lexicon[0]['referent']}'."
            if shared_lexicon
            else "They are still forming their first stable words."
        )
        top_word_info_es = (
            f"Por ejemplo, el {shared_lexicon[0]['consensus_pct']}% del grupo dice «{shared_lexicon[0]['word']}» para referirse a '{shared_lexicon[0]['referent']}'."
            if shared_lexicon
            else "Todavía están formando sus primeras palabras estables."
        )

        surviving_names = ", ".join(f"{k} ({v})" for k, v in species_counts.items()) or "None"
        extinct_note_en = ""
        extinct_note_es = ""
        if len(species_counts) < 3 and self.live.world.day > 30:
            missing = [sp for sp in ("Sylphid", "Lithokin", "Vespera") if species_counts.get(sp, 0) == 0]
            extinct_note_en = f" Natural selection: {', '.join(missing)} went extinct in earlier resource winters, leaving {surviving_names} as the surviving lineage (Gen {self.live.max_generation})."
            extinct_note_es = f" Selección natural: {', '.join(missing)} se extinguieron en inviernos y disputas previas, quedando {surviving_names} como linaje superviviente (Gen {self.live.max_generation})."

        evolved_wild_count = len(self.live.world.evolved_fauna)
        total_wild_species = len(FAUNA_CATALOG) + evolved_wild_count
        extinct_wild_list = list(self.live.world.extinct_fauna.keys())
        alive_wild_species = total_wild_species - len(extinct_wild_list)
        ev_note_en = f" (+{evolved_wild_count} newly evolved species!)" if evolved_wild_count else ""
        ev_note_es = f" (+{evolved_wild_count} nuevas especies evolucionadas)" if evolved_wild_count else ""
        bio_en = (
            f"All {total_wild_species}/{total_wild_species} wild animal species thrive{ev_note_en}."
            if not extinct_wild_list
            else f"{alive_wild_species}/{total_wild_species} wild species survive{ev_note_en} ({len(extinct_wild_list)} extinct: {', '.join(extinct_wild_list[:4])})."
        )
        bio_es = (
            f"Conviven las {total_wild_species}/{total_wild_species} especies salvajes{ev_note_es}."
            if not extinct_wild_list
            else f"Sobreviven {alive_wild_species}/{total_wild_species} especies salvajes{ev_note_es} ({len(extinct_wild_list)} extinguidas: {', '.join(extinct_wild_list[:4])})."
        )

        disciplines = {
            "psychology": (
                f"HOW THEY FEEL TODAY: {'Emotional calm and healthy routine' if mean_stress < 35 else 'Noticeable survival tension from hunger, predators, or crowding'} "
                f"(average tension {mean_stress}%). Era life expectancy: ~{era_life_exp:.0f} planetary years. "
                f"Health: {sick_count} currently ill ({self.live.disease_cases} historical cases, {self.live.cures_applied} remedies applied). "
                f"Right now {sleeping_now} are sleeping and {hungry_now} are foraging."
            ),
            "sociology": (
                f"HOW THEY ORGANIZE ({arch_en}): Sexual demography: {males_count}♂ males & {females_count}♀ females, "
                f"with {bonded_couples} pair-bonded couples (❤️) and {pregnant_count} pregnant mothers (🤰). "
                f"They have voluntarily shared food {self.live.sharing_count} times "
                f"versus {self.live.conflict_count} territorial fights ({self.live.domesticated_count} wild beasts tamed). "
                + (
                    "Close-knit family clans stay bonded together and pass discoveries to their children."
                    if clustering >= 0.3
                    else "Individuals currently roam in looser foraging bands."
                )
            ),
            "anthropology": (
                f"CULTURE, LANGUAGE & SPECIES: Active population: {surviving_names}.{extinct_note_en} "
                f"They communicate with {len(shared_lexicon)} invented words ({top_word_info_en}) "
                f"and have performed {self.live.experiment_trials} hands-on material trials ({cloaks_held} wearing woven cloaks, {tools_held} carrying stone tools)."
            ),
            "economics": (
                f"BIOSPHERE, TRADE, FARMING & MATTER: {bio_en} "
                f"Recorded {self.live.hunts_count} hunts, {self.live.fishing_count} fish catches, {self.live.crops_planted} farm plots, "
                f"{self.live.trade_count} barter trades, and {rare_held} precious minerals accumulated."
            ),
            "philosophy": (
                f"DEATH, RITUALS & INNER WONDER: {self.live.philosophical_count} reflections about stars, life, and mortality. "
                f"Reactions to death observed so far: {self.live.mourning_vigils} silent vigils, {self.live.grave_offerings} grave offerings, "
                f"{self.live.stone_burials} stone burial cairns, and {self.live.corpse_avoidance} fearful retreats (0% simulation awareness)."
            ),
        }

        disciplines_es = {
            "psychology": (
                f"SALUD, LONGEVIDAD Y ÁNIMO HOY: {'Calma emocional y rutina saludable' if mean_stress < 35 else 'Tensión elevada por depredadores, enfermedad o clima'} "
                f"(estrés medio del {mean_stress}%). Esperanza de vida en su era actual: ~{era_life_exp:.0f} años planetarios. "
                f"Enfermedades: {sick_count} enfermos ahora ({self.live.disease_cases} casos históricos, {self.live.cures_applied} curas/remedios aplicados). "
                f"Ahora mismo hay {sleeping_now} durmiendo y {hungry_now} buscando alimento."
            ),
            "sociology": (
                f"FAMILIAS, PAREJAS (♂+♀) Y ORGANIZACIÓN ({arch_es}): Demografía sexual: {males_count}♂ machos y {females_count}♀ hembras, "
                f"con {bonded_couples} parejas estables (❤️) y {pregnant_count} madres embarazadas (🤰). "
                f"Se han regalado comida voluntariamente {self.live.sharing_count} veces, "
                f"frente a {self.live.conflict_count} peleas territoriales ({self.live.domesticated_count} animales salvajes domesticados). "
                + (
                    "Forman núcleos familiares muy unidos que transmiten sus inventos y vocabulario a sus hijos."
                    if clustering >= 0.3
                    else "Se mueven en pequeños grupos recolectores abiertos."
                )
            ),
            "anthropology": (
                f"ESPECIES, CLIMAS, IDIOMA Y CULTURA: Población viva en sus continentes: {surviving_names}.{extinct_note_es} "
                f"Se comunican con {len(shared_lexicon)} palabras inventadas por ellos ({top_word_info_es}) "
                f"y han probado {self.live.experiment_trials} combinaciones de materiales ({cloaks_held} llevan abrigos tejidos, {tools_held} portan herramientas)."
            ),
            "economics": (
                f"BIOSFERA, TRUEQUE, AGRICULTURA Y METALES: {bio_es} "
                f"Registradas {self.live.hunts_count} cacerías, {self.live.fishing_count} pescas, {self.live.crops_planted} cultivos sembrados, "
                f"{self.live.trade_count} intercambios por trueque y {rare_held} minerales preciosos recolectados."
            ),
            "philosophy": (
                f"MUERTE, DUELO, RITOS Y PENSAMIENTO: {self.live.philosophical_count} reflexiones espontáneas sobre el cielo y la existencia. "
                f"Ante la muerte hemos registrado: {self.live.mourning_vigils} vigilias de duelo, {self.live.grave_offerings} ofrendas funerarias, "
                f"{self.live.stone_burials} entierros/túmulos de piedra y {self.live.corpse_avoidance} huidas por temor (0% conciencia de ser simulados)."
            ),
        }

        return {
            "day": self.live.world.day,
            "year": self.live.world.year,
            "season": self.live.world.season_name,
            "ambient_temp_c": self.live.world.ambient_temperature,
            "archetype_en": arch_en,
            "archetype_es": arch_es,
            "live_population": len(living),
            "control_population": len(ctrl_living),
            "males_count": males_count,
            "females_count": females_count,
            "pregnant_count": pregnant_count,
            "bonded_couples": bonded_couples,
            "courtships_count": self.live.courtships_count,
            "era_life_expectancy_yrs": era_life_exp,
            "sick_count": sick_count,
            "disease_cases": self.live.disease_cases,
            "cures_applied": self.live.cures_applied,
            "macro_population": macro_population,
            "planetary_population": macro_population,
            "planetary_carrying_capacity": planetary_capacity,
            "species_macro_counts": species_macro_counts,
            "earth_era_label_es": earth_era_label_es,
            "earth_era_label_en": earth_era_label_en,
            "clan_leaders": clan_leaders,
            "vocations": dict(vocations_cnt),
            "oral_traditions_count": oral_traditions_count,
            "diplomacy_en": diplomacy_en,
            "diplomacy_es": diplomacy_es,
            "species_counts": dict(species_counts),
            "max_generation": self.live.max_generation,
            "rebiogenesis_cycle": self.live.rebiogenesis_cycle,
            "chunks_charted": len(self.live.world.chunks),
            "explored_area_km2": self.live.world.explored_area_km2,
            "planet_colonized_pct": self.live.world.planet_colonized_pct,
            "psychology": {
                "mean_stress": mean_stress,
                "calhoun_sink_index": calhoun_sink,
            },
            "gini_index": gini,
            "cultural_entropy_bits": entropy,
            "social_clustering": clustering,
            "shared_words_count": len(shared_lexicon),
            "pidgin_words_count": pidgin_count,
            "shared_lexicon": shared_lexicon[:10],
            "altruism_acts": self.live.sharing_count,
            "inter_species_peace": self.live.inter_species_peace,
            "conflict_acts": self.live.conflict_count,
            "hunts_count": self.live.hunts_count,
            "fishing_count": self.live.fishing_count,
            "domesticated_count": self.live.domesticated_count,
            "crops_planted": self.live.crops_planted,
            "trade_count": self.live.trade_count,
            "wild_species_alive": alive_wild_species,
            "wild_species_total": total_wild_species,
            "extinct_fauna": dict(self.live.world.extinct_fauna),
            "mourning_vigils": self.live.mourning_vigils,
            "grave_offerings": self.live.grave_offerings,
            "stone_burials": self.live.stone_burials,
            "corpse_avoidance": self.live.corpse_avoidance,
            "experiment_trials": self.live.experiment_trials,
            "emergent_compounds_count": len(self.live.emergent_compounds),
            "emergent_compounds": list(self.live.emergent_compounds.values())[-12:],
            "philosophical_count": self.live.philosophical_count,
            "structures": dict(struct_counts),
            "discoveries": dict(self.live.discoveries),
            "milestone_list_en": milestone_list_en,
            "milestone_list_es": milestone_list_es,
            "disciplines": disciplines,
            "disciplines_es": disciplines_es,
            "llm_deliberations": self.cortex.total_calls,
            "epistemic_scrubs": self.cortex.epistemic_scrubs,
            "ledger_head_hash": self.last_hash[:16],
        }

    def generate_era_report(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        report = {
            "report_id": len(self.reports) + 1,
            "day": metrics["day"],
            "season": metrics["season"],
            "metrics": metrics,
        }
        report_path = self.reports_dir / f"report_day_{metrics['day']:04d}.json"
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return report

    def world_init_payload(self) -> Dict[str, Any]:
        return {
            "seed": self.live.world.seed,
            "props": [
                {"id": p.id, "kind": p.kind, "x": p.x, "y": p.y, "scale": p.scale}
                for p in self.live.world.props.values()
            ],
            "thermal_vents": self.live.world.thermal_vents,
            "caves": [
                {"id": cv.id, "x": cv.x, "y": cv.y, "zone": cv.climate_zone, "depth": cv.depth_m}
                for cv in self.live.world.caves.values()
            ],
        }

    def snapshot_for_ui(self) -> Dict[str, Any]:
        metrics = self._cached_metrics or self.compute_scientific_metrics()
        living = self.live.living_agents
        spotlight_id = None
        if self.live.timeline:
            for ev in reversed(self.live.timeline[-12:]):
                for aid in ev["actors"]:
                    if aid in self.live.agents and self.live.agents[aid].alive:
                        spotlight_id = aid
                        break
                if spotlight_id:
                    break
        if not spotlight_id and living:
            spotlight_id = living[0].id

        return {
            "world": {
                "seed": self.live.world.seed,
                "scale_v10": True,
                "tick": self.live.world.tick_count,
                "day": self.live.world.day,
                "year": self.live.world.year,
                "season": self.live.world.season_name,
                "day_phase": round(self.live.world.day_phase, 3),
                "is_night": self.live.world.is_night,
                "ambient_temp": self.live.world.ambient_temperature,
                "weather": self.live.world.weather,
                "solar_au": self.live.world.solar_distance_au,
                "lunar_phase": self.live.world.lunar_phase,
                "lunar_name": self.live.world.lunar_phase_name,
                "lunar_illum": self.live.world.lunar_illumination,
                "tidal_offset": self.live.world.tidal_offset,
                "solar_angles": self.live.world.solar_system_angles(),
                "earth_diameter_km": 12742,
                "earth_circumference_km": 40075,
                "active_disaster": self.live.world.active_disaster,
                "disaster_xy": list(self.live.world.disaster_xy),
                "speed": self.speed_multiplier,
                "cortex_active": self.cortex.available,
                "cortex_label": self.cortex.provider_label,
            },
            "agents": [
                {
                    "id": a.id,
                    "lineage": a.lineage,
                    "sex": a.sex,
                    "partner_id": a.partner_id,
                    "pregnant": a.is_pregnant,
                    "gestation_pct": min(100, int(round(a.gestation_ticks * 100.0 / 6480.0))) if a.is_pregnant else 0,
                    "gestation_months": round(a.gestation_ticks / 720.0, 1) if a.is_pregnant else 0.0,
                    "children_ids": a.children_ids[-8:],
                    "children_count": len(a.children_ids),
                    "stage": a.life_stage,
                    "scale": a.body_scale,
                    "gen": a.generation,
                    "age": round(a.age_days, 1),
                    "age_years": a.age_years,
                    "illness": a.illness,
                    "illness_severity": round(a.illness_severity, 1),
                    "antibodies": a.antibodies[:6],
                    "vocation": a.emergent_vocation,
                    "prestige": round(a.prestige, 1),
                    "cultural_lore": a.cultural_lore[-4:],
                    "skill_xp": {k: round(v, 1) for k, v in a.skill_xp.items()},
                    "x": a.x,
                    "y": a.y,
                    "earth_geo": earth_location_summary(a.x, a.y),
                    "heading": round(a.heading, 3),
                    "energy": round(a.energy, 1),
                    "protein_balance": round(a.protein_balance, 1),
                    "hydration": round(a.hydration, 1),
                    "warmth": round(a.warmth, 1),
                    "rest": round(a.rest, 1),
                    "integrity": round(a.integrity, 1),
                    "stress": round(a.stress, 1),
                    "mood": a.mood,
                    "sleeping": a.is_sleeping,
                    "intent": a.current_intent,
                    "action": a.action_label,
                    "action_fx": a.action_fx,
                    "genetic_traits": a.genetic_traits,
                    "bio": a.live_biography_summary(),
                    "thought": a.inner_thought,
                    "utterance": a.last_utterance,
                    "referent": a.last_referent,
                    "held_item": a.held_item,
                    "held_color": BLIND_MATERIALS[a.held_item].color_hex if a.held_item else None,
                    "held_label": BLIND_MATERIALS[a.held_item].observer_label if a.held_item else None,
                    "has_cloak": a.has_cloak,
                    "has_tool": a.has_tool,
                    "body_color": a.genome.body_color,
                    "accent_color": a.genome.accent_color,
                    "crest": a.genome.crest_variant,
                    "memories": a.memories[-5:],
                }
                for a in living
            ],
            "enclaves": ENCLAVE_HOMELANDS,
            "corpses": [
                {
                    "id": c.id,
                    "fallen_id": c.fallen_id,
                    "lineage": c.lineage,
                    "x": c.x,
                    "y": c.y,
                    "offerings": len(c.offerings),
                }
                for c in self.live.world.corpses.values()
            ],
            "animals": [
                {
                    "id": an.id,
                    "species": an.species,
                    "label": (self.live.world.evolved_fauna.get(an.species) or FAUNA_CATALOG.get(an.species, {"label": an.species}))["label"],
                    "x": an.x,
                    "y": an.y,
                    "tamed": bool(an.tamed_by),
                    "tamed_by": an.tamed_by,
                    "scale": an.size_gene,
                    "color": an.coat_color,
                    "gen": an.generation,
                }
                for an in self.live.world.animals.values()
                if an.alive
            ],
            "caves": [
                {"id": cv.id, "x": cv.x, "y": cv.y, "zone": cv.climate_zone, "depth": cv.depth_m}
                for cv in self.live.world.caves.values()
            ],
            "structures": [
                {
                    "id": s.id,
                    "kind": s.kind,
                    "name": s.sensory_name,
                    "creator": s.creator_id,
                    "lineage": s.creator_lineage,
                    "day": s.created_day,
                    "x": s.x,
                    "y": s.y,
                    "fuel": round(s.fuel, 1),
                    "stored_food": s.stored_food,
                    "inscription": s.inscription,
                    "layer": s.layer,
                    "tech_tier": s.tech_tier,
                    "is_vehicle": s.is_vehicle,
                    "vehicle_domain": s.vehicle_domain,
                    "signal_range": s.signal_range,
                    "stories": s.stories,
                    "build_progress": round(getattr(s, "build_progress", 1.0), 2),
                    "chambers": s.chambers,
                    "blueprint_3d": s.blueprint_3d,
                }
                for s in self.live.world.structures.values()
            ],
            "resources": [
                [x, y, BLIND_MATERIALS[items[0]].color_hex]
                for (x, y), items in list(self.live.world.resources.items())[:550]
                if items
            ],
            "metrics": metrics,
            "recent_fx": self.live.recent_fx[-12:],
            "current_briefing": self.build_daily_briefing(metrics),
            "daily_logs": self.daily_logs[:25],
            "timeline": self.live.timeline[-45:],
            "spotlight_id": spotlight_id,
            "history": [
                {
                    "day": h["day"],
                    "live": h["live_population"],
                    "ctrl": h["control_population"],
                }
                for h in self.history_series[-55:]
            ],
        }
