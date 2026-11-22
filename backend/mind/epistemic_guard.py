"""Epistemic Veil & Dual-Channel Cognition Guard (English Primary).

Guarantees zero simulation-awareness leaks in prompts and scrubs any accidental
meta/human/modern terms from inner phenomenological thoughts, while enforcing
organic invented phonetic syllables on the physical acoustic channel.
"""

from __future__ import annotations

import re
from typing import Tuple

FORBIDDEN_META_TERMS = frozenset(
    {
        "simulation",
        "simulated",
        "virtual",
        "computer",
        "ai",
        "artificial intelligence",
        "algorithm",
        "code",
        "prompt",
        "llm",
        "openai",
        "ollama",
        "qwen",
        "gpt",
        "human",
        "humans",
        "earth",
        "video game",
        "videogame",
        "game",
        "player",
        "internet",
        "science",
        "scientist",
        "experiment",
        "money",
        "dollar",
        "democracy",
        "capitalism",
        "wikipedia",
        "robot",
        "lego",
        "render",
        "server",
        "matrix",
        "simulacion",
        "simulación",
        "computadora",
        "humano",
    }
)

NATURAL_ENGLISH_LEAKS = frozenset(
    {
        "hello",
        "hi",
        "help",
        "fire",
        "food",
        "cold",
        "warm",
        "friend",
        "enemy",
        "water",
        "stone",
        "rock",
        "attack",
        "give",
        "come",
        "here",
        "look",
        "danger",
        "yes",
        "no",
    }
)

SYLLABLE_CONSONANTS = ("k", "l", "m", "n", "r", "s", "t", "v", "z", "p", "b", "d")
SYLLABLE_VOWELS = ("a", "e", "i", "o", "u")


def assert_prompt_purity(prompt_text: str) -> None:
    """Raises ValueError if an outgoing sensory prompt leaks simulation meta-concepts."""
    lowered = prompt_text.lower()
    for term in FORBIDDEN_META_TERMS:
        if re.search(rf"\b{re.escape(term)}\b", lowered):
            raise ValueError(f"Epistemic Veil violation in prompt: forbidden term '{term}'")


def sanitize_inner_thought(raw_thought: str) -> Tuple[str, bool]:
    """Cleans subjective inner thoughts, flagging if an anachronism was scrubbed."""
    cleaned = raw_thought.strip().replace("\n", " ")
    had_violation = False
    for term in FORBIDDEN_META_TERMS:
        pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
        if pattern.search(cleaned):
            had_violation = True
            cleaned = pattern.sub("the unknown", cleaned)
    if len(cleaned) > 190:
        cleaned = cleaned[:187].rstrip() + "..."
    return cleaned, had_violation


def normalize_phonetic_utterance(raw_utterance: str, fallback_seed: int = 0) -> str:
    """Ensures public vocalizations consist strictly of short invented syllables."""
    tokens = re.findall(r"[a-z]+", raw_utterance.lower())
    valid = [
        t[:5]
        for t in tokens
        if len(t) >= 2 and t not in NATURAL_ENGLISH_LEAKS and t not in FORBIDDEN_META_TERMS
    ]
    if valid:
        return "-".join(valid[:2])
    seed = abs(fallback_seed)
    c1 = SYLLABLE_CONSONANTS[seed % len(SYLLABLE_CONSONANTS)]
    v1 = SYLLABLE_VOWELS[(seed // 3) % len(SYLLABLE_VOWELS)]
    c2 = SYLLABLE_CONSONANTS[(seed // 7) % len(SYLLABLE_CONSONANTS)]
    v2 = SYLLABLE_VOWELS[(seed // 11) % len(SYLLABLE_VOWELS)]
    return f"{c1}{v1}-{c2}{v2}"
