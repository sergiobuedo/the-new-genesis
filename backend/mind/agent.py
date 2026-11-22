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
        "reproduction_mode": "Harmonic Resonance Cocoon",
        "palettes": [("#38bdf8", "#bae6fd"), ("#2dd4bf", "#ccfbf1"), ("#818cf8", "#e0e7ff")],
        "ColdBias": 0.0,
        "SpeedMul": 1.04,
    },
    "Lithokin": {
        "prefix": "L",
        "reproduction_mode": "Geothermal Spore-Clutch",
        "palettes": [("#f59e0b", "#fef3c7"), ("#f97316", "#ffedd5"), ("#eab308", "#fef9c3")],
        "ColdBias": 3.5,
        "SpeedMul": 0.90,
    },
    "Vespera": {
        "prefix": "V",
        "reproduction_mode": "Kinship Fission-Bloom",
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
        "share",
        "pool_nest",
        "confront",
        "tinker",
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

        lineage = p1.lineage if rng.random() < 0.5 else p2.lineage
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

    # Homeostasis & Psychology (0..100)
    energy: float = 84.0
    warmth: float = 88.0
    rest: float = 88.0
    integrity: float = 100.0
    stress: float = 10.0
    age_days: float = 0.0

    # Smooth Locomotion Steering State (Eliminates 100% of spinning/jitter!)
    heading: float = 0.0
    steer_side: float = 1.0  # Persistent obstacle-avoidance side (+1 or -1)
    pause_ticks: int = 0

    # Cognitive & Social State
    inventory: List[str] = field(default_factory=list)
    trust_bonds: Dict[str, float] = field(default_factory=dict)
    personal_lexicon: Dict[str, str] = field(default_factory=dict)
    insight_map: Dict[str, int] = field(default_factory=dict)
    memories: List[str] = field(default_factory=list)

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
    def life_stage(self) -> str:
        if self.age_days < 4.0:
            return "Newborn"
        if self.age_days < 11.0:
            return "Juvenile"
        if self.age_days < 70.0:
            return "Adult"
        return "Elder"

    @property
    def body_scale(self) -> float:
        if self.age_days < 11.0:
            return round(0.52 + (self.age_days / 11.0) * 0.48, 2)
        if self.age_days > 70.0:
            return 1.07
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
        return "composite_tool" in self.inventory

    def live_biography_summary(self) -> str:
        held = BLIND_MATERIALS[self.held_item].observer_label if self.held_item else "empty hands"
        allies = sum(1 for v in self.trust_bonds.values() if v >= 0.25)
        rivals = sum(1 for v in self.trust_bonds.values() if v <= -0.35)
        return (
            f"{self.id} · {self.life_stage} {self.lineage} (Gen {self.generation}, age {self.age_days:.0f}d) — "
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
        light_feel = "starlit night" if world.is_night else "sunlit day"
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
                f"{a.id} ({'same kind' if a.lineage == self.lineage else 'other kind'}, "
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

        prompt = (
            "Raw sensory impressions:\n"
            f"- Sky: {light_feel}. Air: {temp_feel}.\n"
            f"- Body: nourishment={self.energy:.0f}/100, warmth={self.warmth:.0f}/100, "
            f"tension={self.stress:.0f}/100, health={self.integrity:.0f}/100.\n"
            f"- Inner drives: curiosity={self.genome.curiosity}, empathy={self.genome.empathy}, "
            f"fierceness={self.genome.aggression}, hive_collectivism={self.genome.collectivism}.\n"
            f"- Holding: {inv_desc}. Ground: {ground_desc}.\n"
            f"- Structures: {struct_desc}. Wild creatures: {fauna_desc}.\n"
            f"{corpse_line}"
            f"- Other beings: {others_desc}.\n"
            f"- Memories: {recent_mem}.\n\n"
            "Nothing is forbidden or commanded—follow your own drives freely: "
            "forage, warm_up, socialize, share, pool_nest, confront, tinker, hunt, migrate, rest, "
            "vigil (stand beside a fallen body), leave_offering (drop held item by fallen body), or bury_cairn (cover fallen body with stone).\n"
            "Use zero modern, mechanical, or artificial concepts. Reply ONLY with valid JSON:\n"
            '{"thought": "brief first-person inner thought (max 20 words)", '
            '"intent": "forage|warm_up|socialize|share|pool_nest|confront|tinker|hunt|migrate|rest|vigil|leave_offering|bury_cairn", '
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
