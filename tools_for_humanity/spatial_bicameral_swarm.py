"""Standalone O(1) Spatial-Hash & Bicameral GPU Scheduler for Embodied Agent Swarms.

Origin: Invented & refined during Project Universe XXV (Dr. Sergio Buedo Martínez)
to eliminate O(N^2) neighbor bottlenecks and GPU context thrashing when scaling
autonomous multi-species populations across planetary coordinate grids.
"""

from __future__ import annotations

import asyncio
import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Dict, Generic, Iterable, List, Optional, Tuple, TypeVar

T = TypeVar("T")


class SpatialHashGrid(Generic[T]):
    """2D O(1) spatial hash index for fast local perception in massive agent worlds."""

    def __init__(self, cell_size: float = 6.0) -> None:
        self.cell_size = cell_size
        self._buckets: Dict[Tuple[int, int], List[Tuple[float, float, T]]] = defaultdict(list)

    def clear(self) -> None:
        self._buckets.clear()

    def _cell(self, x: float, y: float) -> Tuple[int, int]:
        return int(math.floor(x / self.cell_size)), int(math.floor(y / self.cell_size))

    def insert(self, x: float, y: float, item: T) -> None:
        self._buckets[self._cell(x, y)].append((x, y, item))

    def query_radius(self, x: float, y: float, radius: float) -> List[T]:
        span = int(math.ceil(radius / self.cell_size))
        cx, cy = self._cell(x, y)
        r2 = radius * radius
        found: List[T] = []
        for dy in range(-span, span + 1):
            for dx in range(-span, span + 1):
                for ix, iy, item in self._buckets.get((cx + dx, cy + dy), ()):
                    if (ix - x) ** 2 + (iy - y) ** 2 <= r2:
                        found.append(item)
        return found


@dataclass
class SalienceEvent(Generic[T]):
    agent: T
    priority: float
    prompt: str


class BicameralCortexScheduler(Generic[T]):
    """Decouples 60Hz System-1 homeostatic physics from System-2 LLM deliberation."""

    def __init__(self, max_gpu_concurrency: int = 1) -> None:
        self._sem = asyncio.Semaphore(max_gpu_concurrency)
        self._inflight: set = set()

    def dispatch_highest_salience(
        self,
        candidates: Iterable[SalienceEvent[T]],
        infer_fn: Callable[[T, str], asyncio.Future],
        max_per_tick: int = 1,
    ) -> int:
        ranked = sorted(candidates, key=lambda e: e.priority, reverse=True)[:max_per_tick]
        dispatched = 0
        for ev in ranked:
            task = asyncio.create_task(self._run_guarded(ev.agent, ev.prompt, infer_fn))
            self._inflight.add(task)
            task.add_done_callback(self._inflight.discard)
            dispatched += 1
        return dispatched

    async def _run_guarded(
        self, agent: T, prompt: str, infer_fn: Callable[[T, str], asyncio.Future]
    ) -> Optional[object]:
        async with self._sem:
            return await infer_fn(agent, prompt)
