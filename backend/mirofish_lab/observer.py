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
from backend.world.physics import (
    BLIND_MATERIALS,
    ENCLAVE_HOMELANDS,
    FAUNA_CATALOG,
    CosmosWorld,
    MortalRemains,
    TICKS_PER_DAY,
    WorldStructure,
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
        self.discoveries: Dict[str, int] = {}
        self.max_generation: int = 1
        self.rebiogenesis_cycle: int = 1
        self._founders_per_lineage: int = founders_per_lineage
        self._spawn_multi_species_founders(founders_per_lineage)

    def _spawn_lineage_enclave(self, lineage: str, count: int) -> List[str]:
        cx, cy = ENCLAVE_HOMELANDS[lineage]
        prefix = LINEAGE_SPECS[lineage]["prefix"]
        spawned: List[str] = []
        for _ in range(count):
            self._agent_seq += 1
            aid = f"{prefix}-{self._agent_seq:03d}"
            ang = self.world.rng.uniform(0, 2 * math.pi)
            rad = self.world.rng.uniform(1.5, 6.0)
            sx, sy = self.world.find_nearest_dry_spot(
                cx + math.cos(ang) * rad, cy + math.sin(ang) * rad
            )
            genome = KobGenome.random_founder(self.world.rng, lineage=lineage)
            ag = KobAgent(
                id=aid,
                generation=1,
                born_day=self.world.day,
                x=sx,
                y=sy,
                genome=genome,
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

    def step_tick(self) -> List[Tuple[KobAgent, str]]:
        self.world.step_environment()
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
            self._update_physiology_and_psychology(agent, len(nearby_others))
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

        if self.world.tick_count % 36 == 0 and len(self.living_agents) < 120:
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

    def _update_physiology_and_psychology(self, agent: KobAgent, local_crowd: int) -> None:
        agent.age_days = round((self.world.tick_count / float(TICKS_PER_DAY)) + (1 - agent.born_day), 2)
        cold_res = LINEAGE_SPECS[agent.lineage]["ColdBias"]
        cloak_bonus = 10.0 if (self.enable_culture and agent.has_cloak) else 0.0
        huddle_bonus = min(6.0, local_crowd * 2.2) if self.enable_culture else 0.0
        effective_temp = self.world.local_temperature_at(agent.x, agent.y) + cold_res + cloak_bonus + huddle_bonus

        burn = 0.024 if agent.is_sleeping else 0.055
        agent.energy = max(0.0, agent.energy - burn)
        if effective_temp < 8.0:
            agent.warmth = max(0.0, agent.warmth - (8.0 - effective_temp) * 0.022)
        else:
            agent.warmth = min(100.0, agent.warmth + 0.25)

        if agent.is_sleeping:
            agent.rest = min(100.0, agent.rest + 0.68)
            agent.action_label = "Sleeping deeply to restore strength"
            if agent.rest >= 92.0 or agent.energy < 20.0 or agent.warmth < 24.0:
                agent.is_sleeping = False
        else:
            agent.rest = max(0.0, agent.rest - 0.058)
            if agent.rest < 22.0 or (
                self.world.is_night and agent.rest < 58.0 and agent.energy > 38.0 and agent.warmth > 42.0
            ):
                agent.is_sleeping = True
                agent.action_label = "Sleeping deeply to restore strength"

        stress_delta = -0.12
        if local_crowd >= 6:
            stress_delta += (local_crowd - 5) * 0.18
        if agent.energy < 35.0 or agent.warmth < 40.0:
            stress_delta += 0.20
        agent.stress = round(min(100.0, max(2.0, agent.stress + stress_delta)), 1)

        max_lifespan = 95.0 + agent.genome.vitality * 55.0
        if agent.energy <= 1.0 or agent.warmth <= 1.0:
            agent.integrity -= 0.50
        elif agent.energy > 55.0 and agent.warmth > 50.0:
            agent.integrity = min(100.0, agent.integrity + 0.12)

        if (self.world.day - agent.born_day) > max_lifespan:
            agent.integrity -= 0.40

        if agent.warmth < 38.0:
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
                if agent.warmth <= 2.0:
                    agent.cause_of_death = "winter hypothermia"
                elif agent.energy <= 2.0:
                    agent.cause_of_death = "starvation"
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
                f"{agent.lineage} {agent.id} perished from {agent.cause_of_death} (age {max(1, self.world.day - agent.born_day)}d).",
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
                    other.stress = min(100.0, other.stress + 15.0)
                    other.add_memory(f"Saw the lifeless body of {agent.id}.", self.world.day)

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

        # 1A. Herbal Self-Medication when injured/envenomed!
        if self.enable_culture and agent.integrity < 76.0 and "medicinal_herb" in agent.inventory:
            agent.inventory.remove("medicinal_herb")
            agent.integrity = min(100.0, agent.integrity + BLIND_MATERIALS["medicinal_herb"].healing)
            agent.action_label = "Chewing medicinal Sootheleaf to heal wounds"
            agent.pause_ticks = 4
            agent.add_memory("Healed pain with fragrant silver-veined leaf.", self.world.day)
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
                    agent.mood = "tense"
                    agent.action_label = "Sickened by toxic Shadowberry (learned to avoid!)"
                    agent.add_memory(f"Sickened by {mat.sensory_name}—never eat again!", self.world.day)
                    if agent.integrity <= 0:
                        agent.cause_of_death = "toxic plant poisoning"
                else:
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

        # 2. Seek warmth when freezing
        if agent.warmth < 50.0:
            warm_targets: List[Tuple[float, float]] = []
            if self.enable_culture:
                for st in self.world.structures.values():
                    if (st.kind == "hearth" and st.fuel > 0) or st.kind == "shelter":
                        warm_targets.append((st.x, st.y))
                        if st.kind == "hearth" and st.fuel < 35.0 and math.hypot(st.x - agent.x, st.y - agent.y) < 2.4:
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
                agent.action_label = "Seeking warmth near heat/shelter"
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

        # 3B. Proto-Agriculture (`plant_seed` — sowing cereal grain on fertile soil!)
        if (
            self.enable_culture
            and "grain_seed" in agent.inventory
            and agent.energy > 68.0
            and (agent.current_intent == "plant_seed" or (agent.inventory.count("grain_seed") >= 2 and self.world.rng.random() < 0.04))
        ):
            if len(nearby_structs) < 4:
                agent.inventory.remove("grain_seed")
                self.world._struct_seq += 1
                sx, sy = self.world.find_nearest_dry_spot(agent.x, agent.y)
                bp = [
                    {"shape": "box", "sx": 1.35, "sy": 0.06, "sz": 1.35, "px": 0, "py": 0.03, "pz": 0, "color": "#713f12"},
                    {"shape": "cylinder", "sx": 0.05, "sy": 0.45, "sz": 0.05, "px": -0.35, "py": 0.25, "pz": -0.3, "color": "#eab308"},
                    {"shape": "cylinder", "sx": 0.05, "sy": 0.48, "sz": 0.05, "px": 0.0, "py": 0.26, "pz": 0.0, "color": "#84cc16"},
                    {"shape": "cylinder", "sx": 0.05, "sy": 0.45, "sz": 0.05, "px": 0.35, "py": 0.25, "pz": 0.3, "color": "#eab308"},
                ]
                crop = WorldStructure(
                    id=f"S-{self.world._struct_seq}",
                    kind="crop_plot",
                    sensory_name="tilled golden seed-plot",
                    x=sx,
                    y=sy,
                    creator_id=agent.id,
                    creator_lineage=agent.lineage,
                    created_day=self.world.day,
                    durability=480.0,
                    blueprint_3d=bp,
                )
                self.world.structures[crop.id] = crop
                self.crops_planted += 1
                agent.current_intent = "forage"
                agent.pause_ticks = 5
                agent.action_label = "Sowing Golden Stalk seeds into fertile soil"
                if "first_agriculture" not in self.discoveries:
                    self.discoveries["first_agriculture"] = self.world.day
                self._record_event(
                    "invention",
                    f"AGRICULTURE BORN! {agent.lineage} {agent.id} sowed cereal seeds into a cultivated farm plot!",
                    [agent.id],
                    sx,
                    sy,
                    importance=5,
                )
                return

        # 4A. Emergent Shoreline Fishing & Shellfish Gathering
        if self.enable_culture and (agent.current_intent == "hunt" or agent.energy < 60.0) and nearby_animals:
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
            huntable = ("lumigrazer", "burrowhare", "craghorn", "rootboar", "thunderhorn", "titanotusk", "canopykin", "reedwing")
            grazers = [an for an in nearby_animals if an.species in huntable and an.alive]
            if grazers:
                prey = grazers[0]
                pspec = FAUNA_CATALOG[prey.species]
                if math.hypot(prey.x - agent.x, prey.y - agent.y) <= 2.1:
                    prey.health -= 62.0 if agent.has_tool else 28.0
                    agent.action_label = f"Hunting wild {prey.species} {prey.id}"
                    agent.pause_ticks = 3
                    # Dangerous megafauna / boars counter-charge if hunted solo without spears!
                    if prey.health > 0 and pspec.get("danger", 0) > 0 and not agent.has_tool and len(nearby_others) < 2:
                        counter = float(pspec["danger"]) * 0.65
                        agent.integrity = max(0.0, agent.integrity - counter)
                        agent.stress = min(100.0, agent.stress + 20.0)
                        agent.add_memory(f"Gored by charging {prey.species} while hunting unarmed!", self.world.day)
                        if agent.integrity <= 0:
                            agent.cause_of_death = f"charging {prey.species}"
                    if prey.health <= 0:
                        prey.alive = False
                        for _ in range(pspec.get("meat", 1)):
                            if len(agent.inventory) < 8:
                                agent.inventory.append("wild_meat")
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
                    agent.current_intent = "socialize"
                    agent.pause_ticks = 4
                    agent.action_label = f"Trading {BLIND_MATERIALS[give_item].observer_label} with {partner.id}"
                    if "first_barter_trade" not in self.discoveries:
                        self.discoveries["first_barter_trade"] = self.world.day
                    self._record_event(
                        "altruism",
                        f"{'Inter-species trade! ' if cross_species else 'Barter trade: '}{agent.lineage} {agent.id} exchanged {BLIND_MATERIALS[give_item].observer_label} with {partner.lineage} {partner.id} for {BLIND_MATERIALS[take_item].observer_label}.",
                        [agent.id, partner.id],
                        agent.x,
                        agent.y,
                        importance=5 if cross_species else 3,
                    )
                    return

            # C. Acoustic Communication & Elder Cumulative Cultural Mentorship (Henrich Collective Brain!)
            if agent.age_days >= 50.0 and partner.age_days < 20.0 and agent.insight_map and bond >= 0.15:
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
                elif outcome_kind == "breakthrough":
                    agent.inventory.remove(item_a)
                    agent.inventory.remove(item_b)
                    if crafted:
                        agent.inventory.append(crafted)
                        m_key = f"craft_{crafted}"
                    else:
                        m_key = f"struct_{struct.kind}"  # type: ignore[union-attr]
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

        # 9. Smooth Purposeful Exploration & Continental Migration (No artificial pull to center!)
        if agent.target_xy is None or math.hypot(agent.target_xy[0] - agent.x, agent.target_xy[1] - agent.y) < 1.6:
            is_migrating = self.enable_culture and (agent.current_intent == "migrate" or agent.genome.curiosity > 0.78 and self.world.rng.random() < 0.14)
            span = 22.0 if is_migrating else 10.0
            if agent.current_intent == "migrate":
                agent.current_intent = "forage"
            # Gentle continental drift toward unexplored horizons when migrating, or stay near clan mates otherwise
            drift_x, drift_y = 0.0, 0.0
            if is_migrating:
                drift_x = (4.0 - agent.x) * 0.12  # Gradual continental convergence toward crossroads!
                drift_y = (4.0 - agent.y) * 0.12
            elif nearby_others:
                mx = sum(o.x for o in nearby_others) / len(nearby_others)
                my = sum(o.y for o in nearby_others) / len(nearby_others)
                drift_x = (mx - agent.x) * 0.15
                drift_y = (my - agent.y) * 0.15
            tx, ty = self.world.find_nearest_dry_spot(
                max(-68.0, min(68.0, agent.x + drift_x + self.world.rng.uniform(-span, span))),
                max(-68.0, min(68.0, agent.y + drift_y + self.world.rng.uniform(-span, span))),
            )
            agent.target_xy = (tx, ty)
            agent.pause_ticks = 3
            return

        agent.action_label = "Exploring the valley"
        self._move_smooth(agent, agent.target_xy[0], agent.target_xy[1], nearby_others, speed=0.23 * spd_mul)

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
        eligible = [
            a
            for a in self.living_agents
            if a.energy > 68.0
            and a.warmth > 58.0
            and a.stress < 72.0
            and (self.world.day - a.born_day) >= 8
        ]
        used = set()
        for a in eligible:
            if a.id in used:
                continue
            for b in eligible:
                if b.id == a.id or b.id in used:
                    continue
                cross_lin = b.lineage != a.lineage
                if cross_lin and not self.enable_culture:
                    continue
                if math.hypot(a.x - b.x, a.y - b.y) <= 3.8:
                    bond = a.trust_bonds.get(b.id, 0.0)
                    # Same-species requires mild trust (>=0.18); cross-species hybridization requires deep mutual bond (>=0.65)!
                    min_bond = 0.65 if cross_lin else 0.18
                    if self.enable_culture and bond < min_bond:
                        continue
                    chance = 0.12 if cross_lin else 0.22
                    if self.world.rng.random() < chance:
                        used.add(a.id)
                        used.add(b.id)
                        a.energy -= 24.0
                        b.energy -= 24.0
                        self._agent_seq += 1
                        self.births_today += 1
                        child_genome = KobGenome.crossover(a.genome, b.genome, self.world.rng)
                        c_lin = child_genome.lineage
                        prefix = LINEAGE_SPECS[c_lin]["prefix"]
                        mode_name = LINEAGE_SPECS[c_lin]["reproduction_mode"]
                        cid = f"{prefix}-{self._agent_seq:03d}"
                        gen = max(a.generation, b.generation) + 1
                        self.max_generation = max(self.max_generation, gen)
                        cx, cy = self.world.find_nearest_dry_spot((a.x + b.x) * 0.5, (a.y + b.y) * 0.5)
                        child = KobAgent(
                            id=cid,
                            generation=gen,
                            born_day=self.world.day,
                            x=cx,
                            y=cy,
                            genome=child_genome,
                            parents=(a.id, b.id),
                            energy=78.0,
                            warmth=86.0,
                            heading=a.heading,
                        )
                        child.trust_bonds[a.id] = 0.85
                        child.trust_bonds[b.id] = 0.85
                        a.trust_bonds[cid] = 0.90
                        b.trust_bonds[cid] = 0.90
                        self.agents[cid] = child
                        if cross_lin and "first_sentient_speciation" not in self.discoveries:
                            self.discoveries["first_sentient_speciation"] = self.world.day
                            self._record_event(
                                "birth",
                                f"NEW SENTIENT SPECIES BORN! {a.lineage} {a.id} & {b.lineage} {b.id} gave rise to hybrid lineage {c_lin} ({cid})!",
                                [a.id, b.id, cid],
                                cx,
                                cy,
                                importance=5,
                            )
                        else:
                            if gen == 2 and "gen_2_born" not in self.discoveries:
                                self.discoveries["gen_2_born"] = self.world.day
                            self._record_event(
                                "birth",
                                f"{mode_name}: {a.lineage} {a.id} & {b.lineage} {b.id} welcomed hatchling {cid} (Gen {gen}).",
                                [a.id, b.id, cid],
                                cx,
                                cy,
                                importance=3 if gen >= 2 else 2,
                            )
                        break


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

        self.speed_multiplier: int = 5  # Default x5!
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
            saved = json.loads(state_path.read_text(encoding="utf-8"))
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

            for ad in saved_agents:
                aid = ad["id"]
                try:
                    seq_num = int(aid.split("-")[1])
                    max_seq = max(max_seq, seq_num)
                except Exception:
                    pass
                lin = ad.get("lineage", "Vespera")
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

                ag = KobAgent(
                    id=aid,
                    generation=gen_num,
                    born_day=born_d,
                    x=float(ad["x"]),
                    y=float(ad["y"]),
                    genome=genome,
                    energy=float(ad.get("energy", 80.0)),
                    warmth=float(ad.get("warmth", 85.0)),
                    rest=float(ad.get("rest", 80.0)),
                    integrity=float(ad.get("integrity", 100.0)),
                    stress=float(ad.get("stress", 10.0)),
                    age_days=age_d,
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
            self.live.mourning_vigils = int(m.get("mourning_vigils", 0))
            self.live.grave_offerings = int(m.get("grave_offerings", 0))
            self.live.stone_burials = int(m.get("stone_burials", 0))
            self.live.corpse_avoidance = int(m.get("corpse_avoidance", 0))
            self.cortex.total_calls = int(m.get("llm_deliberations", 0))
            self.live.timeline = list(saved.get("timeline", []))
            self.daily_logs = self.warehouse.recent_daily_summaries(limit=40)
            for h in saved.get("history", []):
                self.history_series.append(
                    {"day": h["day"], "live_population": h["live"], "control_population": h["ctrl"]}
                )

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
            "struct_palisade": "Built fortified timber palisade walls against predators",
            "first_cooked_meal": "Roasted food over fire for higher nutrition",
            "first_agriculture": "Planted cereal seeds into cultivated farm plots",
            "first_barter_trade": "Established bilateral barter trade of goods",
            "struct_watercraft": "Built buoyant watercraft to cross rivers and seas",
            "craft_wheeled_cart": "Invented the axle-mounted wheeled transport cart",
            "struct_open_creation": "Synthesized a brand-new unscripted 3D apparatus",
            "first_fauna_speciation": "Wild fauna evolved into a brand-new daughter species",
            "first_sentient_speciation": "Cross-continent lineages birthed a new hybrid sentient race",
        }
        MILESTONE_LABELS_ES = {
            "first_shared_word": "Inventaron su primera palabra hablada común",
            "first_philosophy": "Primera reflexión existencial sobre la noche y el mundo",
            "first_interspecies_pidgin": "Crearon palabras puente entre distintas razas",
            "first_conflict": "Primer combate territorial por recursos",
            "gen_2_born": "Nacimiento natural de la 2.ª generación",
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
            "struct_palisade": "Murallas/empalizadas de madera frente a grandes depredadores",
            "first_cooked_meal": "Cocinado de alimentos al fuego (+nutrición)",
            "first_agriculture": "Nacimiento de la agricultura sembrando cereal",
            "first_barter_trade": "Primer comercio por trueque de bienes entre individuos",
            "struct_watercraft": "Construcción de balsas/embarcaciones para cruzar aguas",
            "craft_wheeled_cart": "Invención de la rueda y carros de transporte",
            "struct_open_creation": "Invención libre de un artefacto 3D inédito",
            "first_fauna_speciation": "Especiación darwiniana: nace una nueva especie animal salvaje",
            "first_sentient_speciation": "Hibridación fértil: nace una nueva raza inteligente",
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
                f"(average tension {mean_stress}%). Right now {sleeping_now} beings are curled up sleeping, "
                f"and {hungry_now} are actively searching for food. They huddle together on cold nights to share body warmth."
            ),
            "sociology": (
                f"HOW THEY ORGANIZE ({arch_en}): Across history they have voluntarily shared food {self.live.sharing_count} times "
                f"versus {self.live.conflict_count} territorial fights over scarce items ({self.live.domesticated_count} wild beasts tamed). "
                + (
                    "Close-knit family clans stay bonded together."
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
                f"CÓMO SE ENCUENTRAN HOY: {'Calma emocional y rutina saludable' if mean_stress < 35 else 'Tensión elevada por depredadores, hambre o espacio'} "
                f"(estrés medio del {mean_stress}%). Ahora mismo hay {sleeping_now} individuos durmiendo para recuperar fuerzas "
                f"y {hungry_now} buscando comida con hambre. Por las noches se agrupan para darse calor."
            ),
            "sociology": (
                f"CONVIVENCIA Y ORGANIZACIÓN ({arch_es}): Se han regalado comida voluntariamente {self.live.sharing_count} veces, "
                f"frente a {self.live.conflict_count} peleas territoriales ({self.live.domesticated_count} animales salvajes domesticados). "
                + (
                    "Forman clanes familiares muy unidos entre sí."
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
            "wild_species_alive": alive_wild_species,
            "wild_species_total": total_wild_species,
            "extinct_fauna": dict(self.live.world.extinct_fauna),
            "mourning_vigils": self.live.mourning_vigils,
            "grave_offerings": self.live.grave_offerings,
            "stone_burials": self.live.stone_burials,
            "corpse_avoidance": self.live.corpse_avoidance,
            "experiment_trials": self.live.experiment_trials,
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
                "tick": self.live.world.tick_count,
                "day": self.live.world.day,
                "year": self.live.world.year,
                "season": self.live.world.season_name,
                "day_phase": round(self.live.world.day_phase, 3),
                "is_night": self.live.world.is_night,
                "ambient_temp": self.live.world.ambient_temperature,
                "speed": self.speed_multiplier,
                "cortex_active": self.cortex.available,
                "cortex_label": self.cortex.provider_label,
            },
            "agents": [
                {
                    "id": a.id,
                    "lineage": a.lineage,
                    "stage": a.life_stage,
                    "scale": a.body_scale,
                    "gen": a.generation,
                    "age": round(a.age_days, 1),
                    "x": a.x,
                    "y": a.y,
                    "heading": round(a.heading, 3),
                    "energy": round(a.energy, 1),
                    "warmth": round(a.warmth, 1),
                    "rest": round(a.rest, 1),
                    "integrity": round(a.integrity, 1),
                    "stress": round(a.stress, 1),
                    "mood": a.mood,
                    "sleeping": a.is_sleeping,
                    "intent": a.current_intent,
                    "action": a.action_label,
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
                    "x": an.x,
                    "y": an.y,
                    "tamed": bool(an.tamed_by),
                    "scale": an.size_gene,
                    "color": an.coat_color,
                }
                for an in self.live.world.animals.values()
                if an.alive
            ],
            "structures": [
                {
                    "id": s.id,
                    "kind": s.kind,
                    "name": s.sensory_name,
                    "x": s.x,
                    "y": s.y,
                    "fuel": round(s.fuel, 1),
                    "stored_food": s.stored_food,
                    "inscription": s.inscription,
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
