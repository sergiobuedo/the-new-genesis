"""Universe XXV (v3.0) — Symmetric Zero-Bias Sentient Lineages (`Sylphid`,
`Lithokin`, `Vespera`), Smooth Persistent Heading, Ontogenetic Growth & Hybrid Cortex.
"""

from __future__ import annotations

import asyncio
import json
import math
import os
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import httpx

from backend.mind.epistemic_guard import (
    assert_prompt_purity,
    normalize_phonetic_utterance,
    sanitize_inner_thought,
)
from backend.world.physics import BLIND_MATERIALS, CosmosWorld

LINEAGE_SPECS = {
    "Sylphid": {
        "prefix": "S",
        "reproduction_mode": "Viviparous Sexual Union (♂+♀)",
        "palettes": [("#38bdf8", "#bae6fd"), ("#2dd4bf", "#ccfbf1"), ("#818cf8", "#e0e7ff")],
        "ColdBias": 0.0,
        "SpeedMul": 1.04,
    },
    "Lithokin": {
        "prefix": "L",
        "reproduction_mode": "Viviparous Sexual Union (♂+♀)",
        "palettes": [("#f59e0b", "#fef3c7"), ("#f97316", "#ffedd5"), ("#eab308", "#fef9c3")],
        "ColdBias": 3.5,
        "SpeedMul": 0.90,
    },
    "Vespera": {
        "prefix": "V",
        "reproduction_mode": "Viviparous Sexual Union (♂+♀)",
        "palettes": [("#c084fc", "#f3e8ff"), ("#fb7185", "#ffe4e6"), ("#34d399", "#d1fae5")],
        "ColdBias": 1.0,
        "SpeedMul": 1.10,
    },
}

VALID_INTENTS = frozenset(
    {
        "forage",
        "warm_up",
        "socialize",
        "court",
        "share",
        "barter",
        "plant_seed",
        "pool_nest",
        "confront",
        "tinker",
        "excavate",
        "hunt",
        "migrate",
        "rest",
        "vigil",
        "leave_offering",
        "bury_cairn",
    }
)


@dataclass
class KobGenome:
    lineage: str
    curiosity: float
    sociability: float
    empathy: float
    aggression: float
    collectivism: float  # Enables emergent hive/communal vs individualistic divergence!
    caution: float
    vitality: float
    body_color: str
    accent_color: str
    crest_variant: int

    @classmethod
    def random_founder(cls, rng: random.Random, lineage: str = "Sylphid") -> "KobGenome":
        """100% symmetric uniform [0.05..0.95] trait initialization — zero moral bias!"""
        if lineage not in LINEAGE_SPECS:
            LINEAGE_SPECS[lineage] = {
                "prefix": "H",
                "reproduction_mode": "Viviparous Sexual Union (♂+♀)",
                "palettes": [("#34d399", "#fef3c7"), ("#38bdf8", "#f3e8ff")],
                "ColdBias": 1.2,
                "SpeedMul": 1.02,
            }
        spec = LINEAGE_SPECS[lineage]
        body_c, acc_c = rng.choice(spec["palettes"])
        return cls(
            lineage=lineage,
            curiosity=round(rng.uniform(0.08, 0.95), 2),
            sociability=round(rng.uniform(0.08, 0.95), 2),
            empathy=round(rng.uniform(0.05, 0.95), 2),
            aggression=round(rng.uniform(0.05, 0.95), 2),
            collectivism=round(rng.uniform(0.05, 0.95), 2),
            caution=round(rng.uniform(0.10, 0.92), 2),
            vitality=round(rng.uniform(0.45, 0.95), 2),
            body_color=body_c,
            accent_color=acc_c,
            crest_variant=rng.randint(0, 2),
        )

    @classmethod
    def crossover(cls, p1: "KobGenome", p2: "KobGenome", rng: random.Random) -> "KobGenome":
        def mix(a: float, b: float) -> float:
            val = (a + b) * 0.5 + rng.gauss(0.0, 0.075)
            return round(min(0.99, max(0.02, val)), 2)

        if p1.lineage != p2.lineage:
            pair = sorted([p1.lineage[:4], p2.lineage[:4]])
            if pair[0] == pair[1]:
                lineage = p1.lineage if "-" in p1.lineage else p2.lineage
            else:
                lineage = f"{pair[0]}-{pair[1]}"
            if lineage not in LINEAGE_SPECS:
                s1 = LINEAGE_SPECS.get(p1.lineage, LINEAGE_SPECS["Sylphid"])
                s2 = LINEAGE_SPECS.get(p2.lineage, LINEAGE_SPECS["Vespera"])
                LINEAGE_SPECS[lineage] = {
                    "prefix": "H",
                    "reproduction_mode": "Symbiotic Hybrid Genesis",
                    "palettes": [(p1.body_color, p2.accent_color), (p2.body_color, p1.accent_color)],
                    "ColdBias": round((s1["ColdBias"] + s2["ColdBias"]) * 0.5, 2),
                    "SpeedMul": round((s1["SpeedMul"] + s2["SpeedMul"]) * 0.5, 2),
                }
            palette = (p1.body_color, p2.accent_color)
        else:
            lineage = p1.lineage
            palette = (
                (p1.body_color, p1.accent_color)
                if rng.random() < 0.5
                else (p2.body_color, p2.accent_color)
            )
        return cls(
            lineage=lineage,
            curiosity=mix(p1.curiosity, p2.curiosity),
            sociability=mix(p1.sociability, p2.sociability),
            empathy=mix(p1.empathy, p2.empathy),
            aggression=mix(p1.aggression, p2.aggression),
            collectivism=mix(p1.collectivism, p2.collectivism),
            caution=mix(p1.caution, p2.caution),
            vitality=mix(p1.vitality, p2.vitality),
            body_color=palette[0],
            accent_color=palette[1],
            crest_variant=p1.crest_variant if rng.random() < 0.5 else p2.crest_variant,
        )


@dataclass
class KobAgent:
    id: str
    generation: int
    born_day: int
    x: float
    y: float
    genome: KobGenome
    parents: Tuple[str, str] = ("ORIGIN", "ORIGIN")
    alive: bool = True
    death_day: Optional[int] = None
    cause_of_death: str = ""

    # Biological Sex, Pair-Bonding, Gestation & Family Kinship (Human-Identical Reproductive Biology!)
    sex: str = "F"  # "M" (♂ Macho/Male) or "F" (♀ Hembra/Female)
    partner_id: str = ""
    is_pregnant: bool = False
    gestation_ticks: int = 0
    pregnancy_father_id: str = ""
    pregnancy_father_genome: Optional[KobGenome] = None
    children_ids: List[str] = field(default_factory=list)

    # Homeostasis, Pathology & Psychology (0..100)
    energy: float = 84.0
    hydration: float = 90.0
    warmth: float = 88.0
    rest: float = 88.0
    integrity: float = 100.0
    stress: float = 10.0
    age_days: float = 0.0
    illness: str = ""  # "" | "cold_fever" | "wound_sepsis" | "toxin_sickness" | "camp_plague"
    illness_severity: float = 0.0  # 0..100
    antibodies: List[str] = field(default_factory=list)  # Acquired immunity after natural recovery!

    # Smooth Locomotion Steering State (Eliminates 100% of spinning/jitter!)
    heading: float = 0.0
    steer_side: float = 1.0  # Persistent obstacle-avoidance side (+1 or -1)
    pause_ticks: int = 0

    # Cognitive, Cultural & Emergent Social State (0% scripted — earned purely through lived actions!)
    inventory: List[str] = field(default_factory=list)
    trust_bonds: Dict[str, float] = field(default_factory=dict)
    personal_lexicon: Dict[str, str] = field(default_factory=dict)
    insight_map: Dict[str, int] = field(default_factory=dict)
    memories: List[str] = field(default_factory=list)
    cultural_lore: List[str] = field(default_factory=list)  # Oral traditions, myths & clan history passed down!
    skill_xp: Dict[str, float] = field(default_factory=dict)  # Earned organically: hunting, healing, crafting, trading, farming, building
    prestige: float = 0.0  # Emergent social respect earned through altruism, survival, defense, or invention!

    mood: str = "curious"
    current_intent: str = "forage"
    action_label: str = "Awakening in the valley"
    is_sleeping: bool = False
    cortex_experiment_ready: bool = False
    inner_thought: str = "Sunlight warms my body; unfamiliar shapes move across the valley."
    last_utterance: str = ""
    last_referent: str = ""
    utterance_ttl: int = 0
    target_xy: Optional[Tuple[float, float]] = None
    pending_cortex: bool = False
    last_cortex_tick: int = -999
    existential_reflections: int = 0

    @property
    def lineage(self) -> str:
        return self.genome.lineage

    @property
    def age_years(self) -> float:
        return round(self.age_days / 40.0, 1)

    @property
    def life_stage(self) -> str:
        if self.age_days < 6.0:
            return "Newborn"
        if self.age_days < 14.0:
            return "Juvenile"
        if self.age_days < 1000.0:
            return "Adult"
        return "Elder"

    @property
    def body_scale(self) -> float:
        if self.age_days < 14.0:
            return round(0.52 + (self.age_days / 14.0) * 0.48, 2)
        if self.age_days >= 1000.0:
            return 1.04
        return 1.0

    def add_memory(self, text: str, day: int) -> None:
        entry = f"[Day {day}] {text}"
        if not self.memories or self.memories[-1] != entry:
            self.memories.append(entry)
            if len(self.memories) > 14:
                self.memories.pop(0)

    @property
    def held_item(self) -> Optional[str]:
        return self.inventory[-1] if self.inventory else None

    @property
    def has_cloak(self) -> bool:
        return "warm_cloak" in self.inventory

    @property
    def has_tool(self) -> bool:
        return "composite_tool" in self.inventory or "bronze_tool" in self.inventory

    @property
    def has_cart(self) -> bool:
        return "wheeled_cart" in self.inventory

    @property
    def emergent_vocation(self) -> str:
        """Purely descriptive vocation earned from what the being actually chose to practice (never pre-assigned!)."""
        if not self.skill_xp:
            return "Forager"
        top_skill, val = max(self.skill_xp.items(), key=lambda kv: kv[1])
        if val < 2.0:
            return "Forager"
        return {
            "hunting": "Hunter",
            "healing": "Healer",
            "crafting": "Artisan",
            "trading": "Trader",
            "farming": "Farmer",
            "building": "Builder",
            "teaching": "Elder Sage",
        }.get(top_skill, "Forager")

    def live_biography_summary(self) -> str:
        held = BLIND_MATERIALS[self.held_item].observer_label if self.held_item else "empty hands"
        allies = sum(1 for v in self.trust_bonds.values() if v >= 0.25)
        rivals = sum(1 for v in self.trust_bonds.values() if v <= -0.35)
        sex_sym = "♂ Male" if self.sex == "M" else "♀ Female"
        mate_info = f" · ❤️ Mate: {self.partner_id}" if self.partner_id else ""
        preg_info = f" · 🤰 Pregnant ({min(100, int(self.gestation_ticks * 100 / 220))}%)" if self.is_pregnant else ""
        kids_info = f" · 👶 Offspring: {len(self.children_ids)}" if self.children_ids else ""
        sick_info = f" · 🤒 Ill ({self.illness.replace('_', ' ')}, {self.illness_severity:.0f}%)" if self.illness else ""
        voc_info = f" · 🛠️ {self.emergent_vocation}" if self.emergent_vocation != "Forager" else ""
        return (
            f"{self.id} ({sex_sym}) · {self.life_stage} {self.lineage} (Gen {self.generation}, {self.age_years:.1f} yrs / {self.age_days:.0f}d){voc_info}{mate_info}{preg_info}{kids_info}{sick_info} — "
            f"{self.action_label}. Holding: {held}. "
            f"Emotion: {self.mood}. Allies: {allies}, Rivals: {rivals}."
        )

    def build_phenomenological_prompt(
        self,
        world: CosmosWorld,
        nearby_agents: List["KobAgent"],
        nearby_fauna: List[str],
        nearby_items: List[str],
        nearby_structures: List[str],
        nearby_corpses: Optional[List[str]] = None,
    ) -> str:
        """100% neutral sensory stream — prescribes neither peace, hive, nor violence."""
        local_temp = world.local_temperature_at(self.x, self.y)
        temp_feel = (
            "numbing frost"
            if local_temp < 2
            else "crisp chill"
            if local_temp < 11
            else "pleasant warmth"
            if local_temp < 25
            else "dry heat"
        )
        local_night = world.is_night_at(self.x, self.y)
        if local_night:
            light_feel = (
                "bright silver full-moon night"
                if world.lunar_illumination > 0.78
                else "pitch-dark moonless night"
                if world.lunar_illumination < 0.18
                else "starlit crescent-moon night"
            )
        else:
            light_feel = "sunlit day"
        weather_feel = {
            "clear": "clear breeze",
            "rain": "steady falling rain",
            "storm": "flashing thunder and gusting wind",
            "fog": "drifting cool mist",
            "snow": "swirling white frost-flakes",
            "drought": "parched shimmering heat",
        }.get(world.weather, "calm air")
        near_cave = any(math.hypot(self.x - cv.x, self.y - cv.y) <= 6.5 for cv in world.caves.values())
        cave_note = " A dark sheltered rock cavern opens nearby." if near_cave else ""
        inv_desc = (
            ", ".join(BLIND_MATERIALS[c].sensory_name for c in self.inventory if c in BLIND_MATERIALS)
            or "empty hands"
        )
        ground_desc = (
            ", ".join(BLIND_MATERIALS[c].sensory_name for c in nearby_items[:4] if c in BLIND_MATERIALS)
            or "grass and soil"
        )
        others_desc = (
            "; ".join(
                f"{a.id} ({'male' if a.sex == 'M' else 'female'}, {'same kind' if a.lineage == self.lineage else 'other kind'}, "
                f"bond {self.trust_bonds.get(a.id, 0.0):+.1f}"
                + (f", sound «{a.last_utterance}»" if a.last_utterance else "")
                + ")"
                for a in nearby_agents[:4]
            )
            or "alone"
        )
        fauna_desc = ", ".join(nearby_fauna[:3]) or "none near"
        struct_desc = ", ".join(nearby_structures[:3]) or "open land"
        corpse_line = (
            f"- Motionless cold bodies on ground: {', '.join(nearby_corpses[:2])}.\n"
            if nearby_corpses
            else ""
        )
        recent_mem = " | ".join(self.memories[-3:]) or "newly awakened"
        sex_word = "male" if self.sex == "M" else "female"
        preg_word = ", carrying an unborn child within" if self.is_pregnant else ""
        sick_word = ", aching with burning chills and weak limbs" if self.illness else ""

        prompt = (
            "Raw sensory impressions:\n"
            f"- Sky: {light_feel} ({weather_feel}). Air: {temp_feel}.{cave_note}\n"
            f"- Body ({sex_word}{preg_word}{sick_word}): nourishment={self.energy:.0f}/100, hydration={self.hydration:.0f}/100, warmth={self.warmth:.0f}/100, "
            f"tension={self.stress:.0f}/100, health={self.integrity:.0f}/100.\n"
            f"- Inner drives: curiosity={self.genome.curiosity}, empathy={self.genome.empathy}, "
            f"fierceness={self.genome.aggression}, hive_collectivism={self.genome.collectivism}.\n"
            f"- Holding: {inv_desc}. Ground: {ground_desc}.\n"
            f"- Structures: {struct_desc}. Wild creatures: {fauna_desc}.\n"
            f"{corpse_line}"
            f"- Other beings: {others_desc}.\n"
            f"- Memories: {recent_mem}.\n\n"
            "Nothing is forbidden or commanded—follow your own drives freely: "
            "forage, warm_up, socialize, share, barter, plant_seed, "
            "pool_nest, confront, tinker, hunt, migrate, rest, vigil, leave_offering, or bury_cairn.\n"
            "Use zero modern, mechanical, or artificial concepts. Reply ONLY with valid JSON:\n"
            '{"thought": "brief first-person inner thought (max 20 words)", '
            '"intent": "forage|warm_up|socialize|share|barter|plant_seed|pool_nest|confront|tinker|hunt|migrate|rest|vigil|leave_offering|bury_cairn", '
            '"utterance": "1 or 2 invented syllables like ka-ru or lu-ma", '
            '"referent": "food|cold|warmth|kin|stranger|hive|beast|craft|death|wonder", '
            '"wonder": true or false if questioning stars, death, nature, or existence itself}'
        )
        assert_prompt_purity(prompt)
        return prompt


class OllamaCortex:
    """Sequential low-latency System 2 Cortex supporting Local Ollama AND 24/7 Cloud LLM APIs."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        preferred_model: Optional[str] = None,
    ) -> None:
        self.cloud_api_base = os.getenv("LLM_API_BASE", "").rstrip("/")
        self.cloud_api_key = os.getenv("LLM_API_KEY", "")
        self.base_url = (base_url or os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")).rstrip("/")
        self.model = preferred_model or os.getenv("LLM_MODEL", "qwen2.5:3b")
        self.available: bool = bool(self.cloud_api_base and self.cloud_api_key)
        self.provider_label: str = "Cloud API" if self.available else "Ollama GPU"
        self.total_calls: int = 0
        self.epistemic_scrubs: int = 0
        self._sem = asyncio.Semaphore(1)
        self._client = httpx.AsyncClient(timeout=12.0)

    async def probe(self) -> bool:
        if self.cloud_api_base and self.cloud_api_key:
            self.available = True
            self.provider_label = f"Cloud ({self.model})"
            return True
        try:
            resp = await self._client.get(f"{self.base_url}/api/tags")
            if resp.status_code == 200:
                models = [m.get("name", "") for m in resp.json().get("models", [])]
                if any(self.model in m for m in models):
                    self.available = True
                    self.provider_label = f"GPU ({self.model})"
                    return True
                local_models = [m for m in models if "cloud" not in m]
                if local_models:
                    self.model = local_models[0]
                    self.available = True
                    self.provider_label = f"GPU ({self.model})"
                    return True
        except Exception:
            self.available = False
        return False

    async def deliberate(self, agent: KobAgent, prompt: str, tick_seed: int) -> Optional[Dict]:
        if not self.available:
            await self.probe()
        if not self.available:
            return None

        async with self._sem:
            try:
                if self.cloud_api_base and self.cloud_api_key:
                    resp = await self._client.post(
                        f"{self.cloud_api_base}/chat/completions",
                        headers={"Authorization": f"Bearer {self.cloud_api_key}"},
                        json={
                            "model": self.model,
                            "messages": [{"role": "user", "content": prompt}],
                            "response_format": {"type": "json_object"},
                            "temperature": 0.78,
                            "max_tokens": 130,
                        },
                    )
                    if resp.status_code != 200:
                        return None
                    raw_text = resp.json()["choices"][0]["message"]["content"]
                else:
                    resp = await self._client.post(
                        f"{self.base_url}/api/generate",
                        json={
                            "model": self.model,
                            "prompt": prompt,
                            "format": "json",
                            "stream": False,
                            "options": {
                                "temperature": 0.78,
                                "num_ctx": 1536,
                                "num_predict": 140,
                            },
                        },
                    )
                    if resp.status_code != 200:
                        return None
                    raw_text = resp.json().get("response", "{}")

                parsed = json.loads(raw_text)
                thought_raw = str(parsed.get("thought") or "")
                thought_clean, scrubbed = sanitize_inner_thought(thought_raw)
                if scrubbed:
                    self.epistemic_scrubs += 1
                intent = str(parsed.get("intent") or "forage").lower()
                if intent not in VALID_INTENTS:
                    intent = "forage"
                referent = str(parsed.get("referent") or "wonder").lower()[:12]
                utterance = normalize_phonetic_utterance(
                    str(parsed.get("utterance") or ""),
                    fallback_seed=tick_seed + hash(agent.id),
                )
                wonder = bool(parsed.get("wonder", False))
                self.total_calls += 1
                return {
                    "thought": thought_clean or agent.inner_thought,
                    "intent": intent,
                    "utterance": utterance,
                    "referent": referent,
                    "wonder": wonder,
                }
            except Exception:
                return None

    async def close(self) -> None:
        await self._client.aclose()
