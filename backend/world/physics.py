"""Universe XXV (v4.0) — 10x Super-Earth Planetary Scale (`5.10e9 km^2`),
100% Real Terrestrial Geochemistry & Periodic Compounds, and O(1) Spatial Grid.

Inhabitants perceive ONLY raw sensory properties (Epistemic Veil preserved), while
all underlying matter obeys real Earth chemistry, mineralogy, and thermodynamics:
SiO2 (flint), FeS2 (pyrite), Al2Si2O5(OH)4 (kaolin clay), Cu (malachite/copper),
SnO2 (cassiterite), Fe3O4 (magnetite lodestone), cellulose, lignin, and charcoal.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

CHUNK_SIZE = 16
EARTH_SURFACE_KM2 = 510_072_000.0
PLANET_SURFACE_KM2 = EARTH_SURFACE_KM2 * 10.0  # 5.10 billion km^2 Super-Earth!
KM2_PER_SECTOR = 25.0  # Each 16x16 local biome sector represents a 5km x 5km ecological basin


ENCLAVE_HOMELANDS: Dict[str, Tuple[float, float]] = {
    "Sylphid": (-38.0, -34.0),   # NW Temperate Emerald River Archipelago
    "Lithokin": (42.0, -34.0),   # NE Boreal Volcanic & Mineral Highlands
    "Vespera": (4.0, 38.0),      # South Equatorial Monsoon Savanna & Oasis
}


def terrain_height(x: float, y: float, seed: int = 4201) -> float:
    """Continuous multi-continent 3D elevation shared 1:1 with Three.js."""
    s = (seed % 997) * 0.013
    river_center = math.sin(y * 0.075 + s) * 9.5 - 6.0
    dist_river = abs(x - river_center)
    river_carve = -1.35 * math.exp(-(dist_river * dist_river) / 12.0)
    sea_strait = -1.25 * math.exp(-((y - math.sin(x * 0.06) * 8.0 + 10.0) ** 2) / 14.0)

    continents = math.sin(x * 0.038 + s) * math.cos(y * 0.038 - s) * 1.15
    hills = (
        math.sin(x * 0.085 + s) * math.cos(y * 0.085 - s) * 0.85
        + math.sin((x * 0.16 - y * 0.13) + s * 2.0) * 0.36
    )
    ridge_belt = max(0.0, math.sin(x * 0.055 - y * 0.045 + 0.8) - 0.52) * 3.1
    return round(0.55 + continents + hills + ridge_belt + river_carve + sea_strait * 0.55, 3)


def classify_climate_zone(x: float, y: float) -> str:
    """Real Earth-like latitudinal & regional climate bands across the round Super-Earth."""
    if y < -20.0 and x >= 8.0:
        return "boreal_highland"
    if y < -18.0 and x < 8.0:
        return "temperate_archipelago"
    if y > 22.0:
        return "equatorial_savanna"
    return "mediterranean_crossroads"


def classify_biome(x: float, y: float, seed: int = 4201) -> str:
    h = terrain_height(x, y, seed)
    if h < -0.05:
        return "water"
    if h < 0.22:
        return "riverbank"
    if h > 1.80:
        return "ridge"
    s = (seed % 997) * 0.013
    moisture = math.sin(x * 0.09 - s) + math.cos(y * 0.10 + s)
    zone = classify_climate_zone(x, y)
    if zone == "boreal_highland" and moisture < 0.15:
        return "tundra"
    if zone == "equatorial_savanna" and moisture < 0.35:
        return "savanna"
    if moisture > 0.48:
        return "forest"
    return "meadow"


@dataclass(frozen=True)
class BlindMaterial:
    code: str
    formula: str  # Real Earth chemical/mineralogical formula (for scientific papers)
    sensory_name: str  # Raw sensory description perceived by inhabitants (Epistemic Veil)
    observer_label: str  # Clear Earth label shown to human observers
    color_hex: str
    nutrition: float = 0.0
    hardness: float = 0.0  # Normalized Mohs scale
    sharpness: float = 0.0
    flammability: float = 0.0
    spark_potential: float = 0.0
    insulation: float = 0.0
    bindability: float = 0.0
    malleability: float = 0.0
    metallic: float = 0.0
    magnetic: float = 0.0
    luster: float = 0.0  # Physical optical reflectance/rarity (never labeled 'precious' to agents)


BLIND_MATERIALS: Dict[str, BlindMaterial] = {
    "orb_sweet": BlindMaterial(
        code="orb_sweet",
        formula="C6H12O6 + H2O (Wild Berry)",
        sensory_name="sweet amber berry",
        observer_label="Wild Berry (Fructose)",
        color_hex="#f59e0b",
        nutrition=35.0,
    ),
    "orb_root": BlindMaterial(
        code="orb_root",
        formula="(C6H10O5)n (Starch Tuber)",
        sensory_name="dense starchy root",
        observer_label="Wild Tuber (Starch)",
        color_hex="#b45309",
        nutrition=46.0,
        hardness=0.2,
    ),
    "wild_meat": BlindMaterial(
        code="wild_meat",
        formula="Amino Acids + Lipids",
        sensory_name="fresh warm flesh",
        observer_label="Game Meat (Protein)",
        color_hex="#e11d48",
        nutrition=62.0,
    ),
    "wild_fish": BlindMaterial(
        code="wild_fish",
        formula="Omega-3 Lipids + Myosin Protein",
        sensory_name="fresh silver-scaled catch",
        observer_label="Fresh River Fish (Protein)",
        color_hex="#38bdf8",
        nutrition=54.0,
    ),
    "fiber_dry": BlindMaterial(
        code="fiber_dry",
        formula="Cellulose (C6H10O5)n",
        sensory_name="dry supple plant-fiber",
        observer_label="Plant Fiber (Cellulose)",
        color_hex="#fde047",
        flammability=0.92,
        bindability=0.88,
        insulation=0.45,
    ),
    "rod_porous": BlindMaterial(
        code="rod_porous",
        formula="Lignin + Cellulose (Hardwood)",
        sensory_name="solid wooden branch",
        observer_label="Hardwood Timber",
        color_hex="#92400e",
        hardness=0.48,
        flammability=0.82,
        insulation=0.35,
    ),
    "resin_gold": BlindMaterial(
        code="resin_gold",
        formula="C10H16 Terpene Pitch",
        sensory_name="sticky golden sap",
        observer_label="Pine Resin (Terpene)",
        color_hex="#eab308",
        flammability=0.96,
        bindability=0.92,
    ),
    "shard_translucent": BlindMaterial(
        code="shard_translucent",
        formula="SiO2 (Cryptocrystalline Flint)",
        sensory_name="sharp fractured gray stone",
        observer_label="Flint / Chert (SiO2)",
        color_hex="#38bdf8",
        hardness=0.88,
        sharpness=0.94,
    ),
    "nodule_red": BlindMaterial(
        code="nodule_red",
        formula="FeS2 (Iron Pyrite)",
        sensory_name="heavy brassy spark-nodule",
        observer_label="Iron Pyrite (FeS2)",
        color_hex="#ef4444",
        hardness=0.85,
        spark_potential=0.95,
    ),
    "slab_dense": BlindMaterial(
        code="slab_dense",
        formula="CaCO3 / Mafic Silicate",
        sensory_name="flat dense quarry stone",
        observer_label="Limestone / Basalt",
        color_hex="#64748b",
        hardness=0.95,
        insulation=0.82,
    ),
    "clay_gray": BlindMaterial(
        code="clay_gray",
        formula="Al2Si2O5(OH)4 (Kaolinite)",
        sensory_name="cool plastic river-clay",
        observer_label="Kaolin Clay",
        color_hex="#94a3b8",
        malleability=0.94,
        insulation=0.72,
    ),
    "copper_ore": BlindMaterial(
        code="copper_ore",
        formula="Cu2CO3(OH)2 / Native Cu",
        sensory_name="green-veined heavy malleable rock",
        observer_label="Malachite / Native Copper (Cu)",
        color_hex="#10b981",
        hardness=0.55,
        malleability=0.78,
        metallic=0.90,
    ),
    "tin_ore": BlindMaterial(
        code="tin_ore",
        formula="SnO2 (Cassiterite)",
        sensory_name="dark heavy pebble-mineral",
        observer_label="Cassiterite Tin (SnO2)",
        color_hex="#475569",
        hardness=0.70,
        metallic=0.85,
    ),
    "magnetite_ore": BlindMaterial(
        code="magnetite_ore",
        formula="Fe3O4 (Magnetite Lodestone)",
        sensory_name="dark stone that tugs metal",
        observer_label="Magnetite Lodestone (Fe3O4)",
        color_hex="#1e293b",
        hardness=0.80,
        metallic=0.95,
        magnetic=1.0,
    ),
    # Rare & Precious Terrestrial Minerals (100% blind sensory descriptors — 0% value hints!)
    "native_gold": BlindMaterial(
        code="native_gold",
        formula="Au (Alluvial Native Gold)",
        sensory_name="heavy sun-yellow malleable nugget",
        observer_label="Native Gold Nugget (Au)",
        color_hex="#facc15",
        hardness=0.28,
        malleability=0.98,
        metallic=1.0,
        luster=0.98,
    ),
    "native_silver": BlindMaterial(
        code="native_silver",
        formula="Ag (Native Silver Vein)",
        sensory_name="pale mirror-bright metallic pebble",
        observer_label="Native Silver (Ag)",
        color_hex="#e2e8f0",
        hardness=0.32,
        malleability=0.92,
        metallic=1.0,
        luster=0.94,
    ),
    "rough_diamond": BlindMaterial(
        code="rough_diamond",
        formula="C (Octahedral Crystalline Diamond)",
        sensory_name="tiny clear crystal harder than any stone",
        observer_label="Rough Diamond (C)",
        color_hex="#e0f2fe",
        hardness=1.0,
        sharpness=1.0,
        luster=1.0,
    ),
    "fossil_amber": BlindMaterial(
        code="fossil_amber",
        formula="C10H16O (Polymerized Succinite Amber)",
        sensory_name="translucent honey-gold warm drop",
        observer_label="Fossil Amber",
        color_hex="#f59e0b",
        hardness=0.25,
        flammability=0.55,
        luster=0.86,
    ),
    "nephrite_jade": BlindMaterial(
        code="nephrite_jade",
        formula="Ca2(Mg,Fe)5Si8O22(OH)2 (Nephrite Jade)",
        sensory_name="dense smooth deep-green chime-stone",
        observer_label="Nephrite Jade",
        color_hex="#059669",
        hardness=0.78,
        luster=0.88,
    ),
    "nacre_shell": BlindMaterial(
        code="nacre_shell",
        formula="CaCO3 Aragonite Nacre",
        sensory_name="iridescent spiral shoreline shell",
        observer_label="Pearlescent Shell",
        color_hex="#fbcfe8",
        hardness=0.38,
        sharpness=0.42,
        luster=0.82,
    ),
    # Progressive Emergent Terrestrial Technologies
    "crafted_ornament": BlindMaterial(
        code="crafted_ornament",
        formula="Polished Precious Mineral + Cordage",
        sensory_name="strung gleaming pendant-token",
        observer_label="Crafted Precious Ornament (Symbolic Art!)",
        color_hex="#fde047",
        luster=1.0,
    ),
    "composite_tool": BlindMaterial(
        code="composite_tool",
        formula="SiO2 + Lignin + Cellulose",
        sensory_name="hafted flint spear-knife",
        observer_label="Hafted Flint Tool (Lithic Tech)",
        color_hex="#22d3ee",
        hardness=0.90,
        sharpness=0.95,
    ),
    "warm_cloak": BlindMaterial(
        code="warm_cloak",
        formula="Woven Cellulose Textile",
        sensory_name="woven plant-fiber tunic",
        observer_label="Woven Fiber Cloak (Textile Tech)",
        color_hex="#f472b6",
        insulation=0.95,
    ),
    "bronze_tool": BlindMaterial(
        code="bronze_tool",
        formula="Cu-Sn Alloy (Smelted Bronze)",
        sensory_name="gleaming cast golden-metal blade",
        observer_label="Smelted Bronze Tool (Metallurgy!)",
        color_hex="#d97706",
        hardness=0.97,
        sharpness=0.99,
        metallic=1.0,
    ),
    "compass_stone": BlindMaterial(
        code="compass_stone",
        formula="Suspended Fe3O4 Dipole",
        sensory_name="pivoting stone that points north",
        observer_label="Magnetic Compass (Navigation Tech!)",
        color_hex="#818cf8",
        magnetic=1.0,
    ),
}


@dataclass
class NaturalProp:
    id: str
    kind: str  # "tree" | "boulder" | "bush" | "crystal"
    x: float
    y: float
    scale: float
    radius: float


FAUNA_CATALOG = {
    "silverfin_shoal": {"domain": "water", "speed": 0.16, "hp": 35.0, "label": "Silverfin Fish Shoal"},
    "tidecrawler": {"domain": "shore", "speed": 0.10, "hp": 30.0, "label": "Tidecrawler Crab"},
    "lumigrazer": {"domain": "land", "speed": 0.20, "hp": 100.0, "label": "Lumigrazer Herd"},
    "burrowhare": {"domain": "land", "speed": 0.30, "hp": 40.0, "label": "Meadow Burrowhare"},
    "pollenwing": {"domain": "air", "speed": 0.26, "hp": 20.0, "label": "Pollenwing Flock"},
    "skyglider": {"domain": "air", "speed": 0.32, "hp": 45.0, "label": "Coastal Skyglider"},
    "packhound": {"domain": "land", "speed": 0.25, "hp": 80.0, "label": "Wild Packhound"},
    "shadowstalker": {"domain": "land", "speed": 0.30, "hp": 115.0, "label": "Nocturnal Shadowstalker"},
}


@dataclass
class WildAnimal:
    id: str
    species: str  # 8-species multi-niche terrestrial/aquatic/avian food web
    x: float
    y: float
    energy: float = 85.0
    health: float = 100.0
    alive: bool = True
    tameness: float = 0.0  # Rises ONLY if sentient beings voluntarily share food nearby
    tamed_by: str = ""
    target_xy: Optional[Tuple[float, float]] = None


@dataclass
class MortalRemains:
    id: str
    fallen_id: str
    lineage: str
    x: float
    y: float
    death_day: int
    cause: str
    ttl_ticks: int = 600  # Remains visible for 3 full days unless buried under a stone cairn
    offerings: List[str] = None  # type: ignore[assignment]
    vigils: int = 0

    def __post_init__(self) -> None:
        if self.offerings is None:
            self.offerings = []


@dataclass
class WorldStructure:
    id: str
    kind: str  # "hearth" | "shelter" | "granary" | "monolith" | "cairn"
    sensory_name: str
    x: float
    y: float
    creator_id: str
    creator_lineage: str
    created_day: int
    durability: float = 180.0
    fuel: float = 0.0
    stored_food: int = 0
    inscription: str = ""


SEASONS = ["Spring", "Summer", "Autumn", "Deep Winter"]
DAYS_PER_SEASON = 10
TICKS_PER_DAY = 200


class CosmosWorld:
    """10x Super-Earth Planetary Environment with O(1) Spatial Indexing & Real Chemistry."""

    def __init__(self, seed: int = 4201) -> None:
        self.seed = seed
        self.rng = random.Random(seed)
        self.tick_count: int = 0
        self.chunks: Dict[Tuple[int, int], bool] = {}
        self.newly_discovered_chunks: List[Tuple[int, int]] = []
        self.props: Dict[str, NaturalProp] = {}
        self._prop_seq: int = 0
        self.spatial_obstacles: Dict[Tuple[int, int], List[NaturalProp]] = {}
        self.resources: Dict[Tuple[int, int], List[str]] = {}
        # Spatial resource bucket (8x8 cells) for O(1) foraging eyesight!
        self.resource_buckets: Dict[Tuple[int, int], set] = {}
        self.structures: Dict[str, WorldStructure] = {}
        self._struct_seq: int = 0
        self.corpses: Dict[str, MortalRemains] = {}
        self.animals: Dict[str, WildAnimal] = {}
        self._animal_seq: int = 0
        self.thermal_vents: List[Tuple[float, float]] = []

        # Generate the Central Crossroads + all 3 distant Continental Homelands!
        seed_centers = [(0, 0), (-3, -2), (3, -2), (0, 2)]
        for bx, by in seed_centers:
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if (bx + dx, by + dy) not in self.chunks:
                        self._generate_chunk(bx + dx, by + dy)

        # Guarantee volcanic geothermal vents in the NE Boreal Lithokin Highlands
        for off_x, off_y in ((-3.0, 2.0), (4.0, -2.5)):
            vx, vy = self.find_nearest_dry_spot(42.0 + off_x, -34.0 + off_y)
            self.thermal_vents.append((vx, vy))

        self._spawn_initial_fauna()

    @property
    def day(self) -> int:
        return (self.tick_count // TICKS_PER_DAY) + 1

    @property
    def year(self) -> int:
        return ((self.day - 1) // (DAYS_PER_SEASON * 4)) + 1

    @property
    def season_index(self) -> int:
        return ((self.day - 1) // DAYS_PER_SEASON) % 4

    @property
    def season_name(self) -> str:
        return SEASONS[self.season_index]

    @property
    def day_phase(self) -> float:
        return (self.tick_count % TICKS_PER_DAY) / float(TICKS_PER_DAY)

    @property
    def is_night(self) -> bool:
        return self.day_phase >= 0.64 or self.day_phase < 0.08

    @property
    def ambient_temperature(self) -> float:
        season_base = [19.0, 25.5, 13.5, 5.2][self.season_index]
        diurnal = math.sin((self.day_phase - 0.08) * 2.0 * math.pi) * 4.6
        return round(season_base + diurnal, 2)

    @property
    def explored_area_km2(self) -> float:
        return round(len(self.chunks) * KM2_PER_SECTOR, 1)

    @property
    def planet_colonized_pct(self) -> float:
        return round((self.explored_area_km2 / PLANET_SURFACE_KM2) * 100.0, 8)

    @staticmethod
    def tile_to_chunk(tx: int, ty: int) -> Tuple[int, int]:
        return math.floor(tx / CHUNK_SIZE), math.floor(ty / CHUNK_SIZE)

    def elevation_at(self, x: float, y: float) -> float:
        return terrain_height(x, y, self.seed)

    def is_walkable(self, x: float, y: float) -> bool:
        if self.elevation_at(x, y) < -0.02:
            return False
        gx, gy = int(round(x)), int(round(y))
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                for prop in self.spatial_obstacles.get((gx + dx, gy + dy), ()):
                    if prop.radius > 0.35 and math.hypot(x - prop.x, y - prop.y) < prop.radius:
                        return False
        return True

    def find_nearest_dry_spot(self, x: float, y: float) -> Tuple[float, float]:
        if self.is_walkable(x, y):
            return round(x, 2), round(y, 2)
        for rad in range(1, 14):
            for step in range(12):
                ang = (step / 12.0) * 2.0 * math.pi
                nx = round(x + math.cos(ang) * rad, 2)
                ny = round(y + math.sin(ang) * rad, 2)
                if self.is_walkable(nx, ny):
                    return nx, ny
        return 8.0, 8.0

    def ensure_frontier_around(self, x: float, y: float) -> Optional[Tuple[int, int]]:
        """Unbounded continental expansion across the 10x Super-Earth!"""
        tx, ty = int(round(x)), int(round(y))
        for dy in (-3, 0, 3):
            for dx in (-3, 0, 3):
                cx, cy = self.tile_to_chunk(tx + dx, ty + dy)
                if (cx, cy) not in self.chunks and len(self.chunks) < 2500:
                    self._generate_chunk(cx, cy)
                    self.newly_discovered_chunks.append((cx, cy))
                    return (cx, cy)
        return None

    def _tile_rng(self, tx: int, ty: int) -> random.Random:
        h = ((tx * 73856093) ^ (ty * 19349663) ^ (self.seed * 83492791)) & 0xFFFFFFFF
        return random.Random(h)

    def _add_resource_at(self, tx: int, ty: int, code: str) -> None:
        items = self.resources.setdefault((tx, ty), [])
        if len(items) < 3:
            items.append(code)
            bx, by = tx >> 3, ty >> 3
            self.resource_buckets.setdefault((bx, by), set()).add((tx, ty))

    def remove_resource_at(self, tx: int, ty: int, code: str) -> None:
        items = self.resources.get((tx, ty))
        if not items or code not in items:
            return
        items.remove(code)
        if not items:
            self.resources.pop((tx, ty), None)
            bx, by = tx >> 3, ty >> 3
            bset = self.resource_buckets.get((bx, by))
            if bset:
                bset.discard((tx, ty))

    def _generate_chunk(self, cx: int, cy: int) -> None:
        self.chunks[(cx, cy)] = True
        for ly in range(0, CHUNK_SIZE, 2):
            ty = cy * CHUNK_SIZE + ly
            for lx in range(0, CHUNK_SIZE, 2):
                tx = cx * CHUNK_SIZE + lx
                biome = classify_biome(tx, ty, self.seed)
                if biome == "water":
                    continue
                trng = self._tile_rng(tx, ty)
                px = round(tx + trng.uniform(-0.45, 0.45), 2)
                py = round(ty + trng.uniform(-0.45, 0.45), 2)
                if self.elevation_at(px, py) < 0.04:
                    continue

                if biome == "forest" and trng.random() < 0.40:
                    if len(self.props) < 1800:
                        self._add_prop("tree", px, py, scale=round(trng.uniform(0.85, 1.45), 2), radius=0.65)
                    self._seed_tile_resources(tx, ty, biome, trng, initial=True)
                elif biome in ("meadow", "savanna") and trng.random() < 0.24:
                    if len(self.props) < 1800:
                        self._add_prop("bush", px, py, scale=round(trng.uniform(0.75, 1.15), 2), radius=0.0)
                    self._seed_tile_resources(tx, ty, biome, trng, initial=True)
                elif biome in ("ridge", "tundra") and trng.random() < 0.34:
                    if len(self.props) < 1800:
                        kind = "crystal" if trng.random() < 0.28 else "boulder"
                        self._add_prop(kind, px, py, scale=round(trng.uniform(0.8, 1.4), 2), radius=0.62)
                    self._seed_tile_resources(tx, ty, biome, trng, initial=True)
                elif biome == "riverbank" and trng.random() < 0.30:
                    self._seed_tile_resources(tx, ty, biome, trng, initial=True)

        crng = self._tile_rng(cx * 31, cy * 37)
        if (abs(cx) + abs(cy)) >= 2 and crng.random() < 0.24 and len(self.thermal_vents) < 24:
            vx = cx * CHUNK_SIZE + crng.uniform(3.0, CHUNK_SIZE - 3.0)
            vy = cy * CHUNK_SIZE + crng.uniform(3.0, CHUNK_SIZE - 3.0)
            if self.elevation_at(vx, vy) > 0.15:
                self.thermal_vents.append((round(vx, 1), round(vy, 1)))

    def _add_prop(self, kind: str, x: float, y: float, scale: float, radius: float) -> None:
        self._prop_seq += 1
        p = NaturalProp(id=f"P-{self._prop_seq}", kind=kind, x=x, y=y, scale=scale, radius=radius)
        self.props[p.id] = p
        if radius > 0:
            gx, gy = int(round(x)), int(round(y))
            self.spatial_obstacles.setdefault((gx, gy), []).append(p)

    def find_nearest_water_spot(self, x: float, y: float) -> Tuple[float, float]:
        if self.elevation_at(x, y) < -0.06:
            return round(x, 2), round(y, 2)
        for rad in range(1, 22):
            for step in range(16):
                ang = (step / 16.0) * 2.0 * math.pi
                nx = round(x + math.cos(ang) * rad, 2)
                ny = round(y + math.sin(ang) * rad, 2)
                if self.elevation_at(nx, ny) < -0.06:
                    return nx, ny
        return -5.0, 8.0

    def _spawn_initial_fauna(self) -> None:
        anchors = list(ENCLAVE_HOMELANDS.values()) + [(4.0, 4.0)]
        for cx, cy in anchors:
            for sp in ("silverfin_shoal", "silverfin_shoal", "tidecrawler", "lumigrazer", "lumigrazer", "burrowhare", "pollenwing", "skyglider", "packhound"):
                self._animal_seq += 1
                dom = FAUNA_CATALOG[sp]["domain"]
                if dom == "water":
                    ax, ay = self.find_nearest_water_spot(cx + self.rng.uniform(-12.0, 12.0), cy + self.rng.uniform(-12.0, 12.0))
                elif dom == "air":
                    ax, ay = round(cx + self.rng.uniform(-14.0, 14.0), 2), round(cy + self.rng.uniform(-14.0, 14.0), 2)
                else:
                    ax, ay = self.find_nearest_dry_spot(cx + self.rng.uniform(-12.0, 12.0), cy + self.rng.uniform(-12.0, 12.0))
                self.animals[f"W-{self._animal_seq:02d}"] = WildAnimal(
                    id=f"W-{self._animal_seq:02d}", species=sp, x=ax, y=ay, health=FAUNA_CATALOG[sp]["hp"]
                )
        for ang in (0.6, 2.7, 4.8):
            self._animal_seq += 1
            ax, ay = self.find_nearest_dry_spot(
                4.0 + math.cos(ang) * 26.0, 4.0 + math.sin(ang) * 26.0
            )
            self.animals[f"W-{self._animal_seq:02d}"] = WildAnimal(
                id=f"W-{self._animal_seq:02d}", species="shadowstalker", x=ax, y=ay, health=115.0
            )

    def _seed_tile_resources(
        self, tx: int, ty: int, biome: str, rng: random.Random, initial: bool = False
    ) -> None:
        if self.elevation_at(tx, ty) < 0.0:
            return
        existing = self.resources.get((tx, ty))
        if existing and len(existing) >= 2:
            return
        p = 1.0 if initial else 0.25
        if biome in ("meadow", "savanna"):
            if rng.random() < 0.52 * p:
                self._add_resource_at(tx, ty, "orb_sweet")
            if rng.random() < 0.24 * p:
                self._add_resource_at(tx, ty, "fiber_dry")
            if biome == "savanna" and rng.random() < 0.04 * p:
                self._add_resource_at(tx, ty, "fossil_amber")
        elif biome == "forest":
            if rng.random() < 0.40 * p:
                self._add_resource_at(tx, ty, "rod_porous")
            if rng.random() < 0.34 * p:
                self._add_resource_at(tx, ty, "orb_root")
            if rng.random() < 0.16 * p:
                self._add_resource_at(tx, ty, "resin_gold")
            if rng.random() < 0.045 * p:
                self._add_resource_at(tx, ty, "fossil_amber")
        elif biome == "ridge":
            # Real Earth geological ore & precious mineral veins
            r = rng.random()
            if r < 0.20 * p:
                self._add_resource_at(tx, ty, "shard_translucent")
            elif r < 0.35 * p:
                self._add_resource_at(tx, ty, "nodule_red")
            elif r < 0.50 * p:
                self._add_resource_at(tx, ty, "slab_dense")
            elif r < 0.62 * p:
                self._add_resource_at(tx, ty, "copper_ore")
            elif r < 0.71 * p:
                self._add_resource_at(tx, ty, "tin_ore")
            elif r < 0.78 * p:
                self._add_resource_at(tx, ty, "magnetite_ore")
            elif r < 0.83 * p:
                self._add_resource_at(tx, ty, "nephrite_jade")
            elif r < 0.87 * p:
                self._add_resource_at(tx, ty, "native_silver")
            elif r < 0.90 * p:
                self._add_resource_at(tx, ty, "native_gold")
            elif r < 0.918 * p:
                self._add_resource_at(tx, ty, "rough_diamond")
        elif biome == "riverbank":
            if rng.random() < 0.40 * p:
                self._add_resource_at(tx, ty, "clay_gray")
            if rng.random() < 0.34 * p:
                self._add_resource_at(tx, ty, "fiber_dry")
            if rng.random() < 0.26 * p:
                self._add_resource_at(tx, ty, "orb_sweet")
            if rng.random() < 0.10 * p:
                self._add_resource_at(tx, ty, "nacre_shell")
            if rng.random() < 0.035 * p:
                self._add_resource_at(tx, ty, "native_gold")  # Rare alluvial placer gold!
        else:
            # Boreal Tundra: rich in roots, flint, pyrite & copper veins!
            if rng.random() < 0.34 * p:
                self._add_resource_at(tx, ty, "orb_root")
            if rng.random() < 0.16 * p:
                self._add_resource_at(tx, ty, "shard_translucent")
            if rng.random() < 0.12 * p:
                self._add_resource_at(tx, ty, "nodule_red")

    def local_temperature_at(self, x: float, y: float) -> float:
        temp = self.ambient_temperature
        # Real Earth-like latitudinal climate gradient: North (y < 0) cooler, South (y > 0) warmer!
        zone = classify_climate_zone(x, y)
        if zone == "boreal_highland":
            temp -= 5.0
        elif zone == "temperate_archipelago":
            temp += 1.5
        elif zone == "equatorial_savanna":
            temp += 6.5
        elev = self.elevation_at(x, y)
        if elev > 1.8:
            temp -= (elev - 1.8) * 2.5
        for vx, vy in self.thermal_vents:
            d = math.hypot(x - vx, y - vy)
            if d < 6.5:
                temp += (6.5 - d) * 3.4
        for st in self.structures.values():
            d = math.hypot(x - st.x, y - st.y)
            if st.kind == "hearth" and st.fuel > 0 and d < 6.0:
                temp += (6.0 - d) * 4.5
            elif st.kind == "shelter" and d < 4.5:
                temp += (4.5 - d) * 3.0
        return round(temp, 2)

    def step_environment(self) -> None:
        self.tick_count += 1
        if self.tick_count % 22 == 0 and self.chunks:
            chunk_keys = list(self.chunks.keys())
            trials = 18 if self.season_index != 3 else 7
            for _ in range(trials):
                cx, cy = self.rng.choice(chunk_keys)
                tx = cx * CHUNK_SIZE + self.rng.randrange(0, CHUNK_SIZE)
                ty = cy * CHUNK_SIZE + self.rng.randrange(0, CHUNK_SIZE)
                biome = classify_biome(tx, ty, self.seed)
                if biome != "water":
                    self._seed_tile_resources(tx, ty, biome, self.rng, initial=False)

        # Replenish multi-niche biodiversity slowly so aquatic, land, and avian webs persist
        if self.tick_count % 320 == 0:
            counts: Dict[str, int] = {}
            for a in self.animals.values():
                if a.alive:
                    counts[a.species] = counts.get(a.species, 0) + 1
            quotas = {
                "silverfin_shoal": 6,
                "tidecrawler": 4,
                "lumigrazer": 7,
                "burrowhare": 4,
                "pollenwing": 3,
                "skyglider": 2,
                "packhound": 3,
            }
            for sp, min_q in quotas.items():
                if counts.get(sp, 0) < min_q:
                    self._animal_seq += 1
                    dom = FAUNA_CATALOG[sp]["domain"]
                    anchor = self.rng.choice(list(ENCLAVE_HOMELANDS.values()) + [(4.0, 4.0)])
                    if dom == "water":
                        ax, ay = self.find_nearest_water_spot(anchor[0] + self.rng.uniform(-14.0, 14.0), anchor[1] + self.rng.uniform(-14.0, 14.0))
                    elif dom == "air":
                        ax, ay = round(anchor[0] + self.rng.uniform(-16.0, 16.0), 2), round(anchor[1] + self.rng.uniform(-16.0, 16.0), 2)
                    else:
                        ax, ay = self.find_nearest_dry_spot(anchor[0] + self.rng.uniform(-14.0, 14.0), anchor[1] + self.rng.uniform(-14.0, 14.0))
                    self.animals[f"W-{self._animal_seq:02d}"] = WildAnimal(
                        id=f"W-{self._animal_seq:02d}",
                        species=sp,
                        x=ax,
                        y=ay,
                        health=FAUNA_CATALOG[sp]["hp"],
                    )
                    break

        for animal in list(self.animals.values()):
            if not animal.alive:
                continue
            spec = FAUNA_CATALOG.get(animal.species, FAUNA_CATALOG["lumigrazer"])
            dom = spec["domain"]
            # Pollinators naturally fertilize meadow berries underneath them
            if animal.species == "pollenwing" and self.tick_count % 90 == 0 and self.rng.random() < 0.28:
                gx, gy = int(round(animal.x)), int(round(animal.y))
                if classify_biome(gx, gy, self.seed) in ("meadow", "riverbank"):
                    self._add_resource_at(gx, gy, "orb_sweet")

            if animal.target_xy is None or math.hypot(animal.target_xy[0] - animal.x, animal.target_xy[1] - animal.y) < 1.2:
                span = 9.0 if dom in ("air", "land") else 5.5
                nx = max(-55.0, min(70.0, animal.x + self.rng.uniform(-span, span)))
                ny = max(-55.0, min(70.0, animal.y + self.rng.uniform(-span, span)))
                if dom == "water" and self.elevation_at(nx, ny) < -0.05:
                    animal.target_xy = (nx, ny)
                elif dom == "air":
                    animal.target_xy = (nx, ny)
                elif dom in ("land", "shore") and self.is_walkable(nx, ny):
                    animal.target_xy = (nx, ny)

            if animal.target_xy is not None:
                dx, dy = animal.target_xy[0] - animal.x, animal.target_xy[1] - animal.y
                dist = math.hypot(dx, dy)
                spd = spec["speed"]
                if animal.species == "shadowstalker" and not self.is_night:
                    spd *= 0.4
                if dist > 0.05:
                    nx = round(animal.x + (dx / dist) * min(dist, spd), 2)
                    ny = round(animal.y + (dy / dist) * min(dist, spd), 2)
                    if dom == "water":
                        if self.elevation_at(nx, ny) < -0.04:
                            animal.x, animal.y = nx, ny
                        else:
                            animal.target_xy = None
                    elif dom == "air":
                        animal.x, animal.y = nx, ny
                    else:
                        if self.is_walkable(nx, ny):
                            animal.x, animal.y = nx, ny
                        else:
                            animal.target_xy = None

        dead_ids: List[str] = []
        for sid, st in self.structures.items():
            if st.kind == "hearth" and st.fuel > 0:
                st.fuel = max(0.0, st.fuel - 0.08)
            st.durability -= 0.004 if st.kind != "monolith" else 0.0004
            if st.durability <= 0:
                dead_ids.append(sid)
        for sid in dead_ids:
            del self.structures[sid]

        expired_corpses = [cid for cid, c in self.corpses.items() if c.ttl_ticks <= 1]
        for cid, c in self.corpses.items():
            c.ttl_ticks -= 1
        for cid in expired_corpses:
            self.corpses.pop(cid, None)

    def attempt_empirical_experiment(
        self,
        code_a: str,
        code_b: str,
        inventory: List[str],
        insight_map: Dict[str, int],
        x: float,
        y: float,
        actor_id: str,
        actor_lineage: str = "Sylphid",
        utterance_mark: str = "",
    ) -> Tuple[Optional[str], Optional[WorldStructure], str, str]:
        """Real Earth Physics & Chemistry Progression (Stone Age -> Ceramic -> Bronze -> Compass)."""
        mat_a = BLIND_MATERIALS.get(code_a)
        mat_b = BLIND_MATERIALS.get(code_b)
        if not mat_a or not mat_b:
            return None, None, "inert", "Nothing perceptible happens."

        max_hard = max(mat_a.hardness, mat_b.hardness)
        max_spark = max(mat_a.spark_potential, mat_b.spark_potential)
        max_flam = max(mat_a.flammability, mat_b.flammability)
        max_sharp = max(mat_a.sharpness, mat_b.sharpness)
        max_bind = max(mat_a.bindability, mat_b.bindability)
        max_mall = max(mat_a.malleability, mat_b.malleability)
        max_insul = max(mat_a.insulation, mat_b.insulation)
        near_hearth = any(
            st.kind == "hearth" and st.fuel > 0 and math.hypot(st.x - x, st.y - y) <= 4.5
            for st in self.structures.values()
        )

        # 1. Bronze Metallurgy (Cu + SnO2 near active Hearth > 1085°C + >=3 smelting insights!)
        if near_hearth and {code_a, code_b} == {"copper_ore", "tin_ore"}:
            lvl = insight_map.get("metallurgy_lore", 0) + 1
            insight_map["metallurgy_lore"] = lvl
            if lvl < 3:
                return (
                    None,
                    None,
                    "partial_insight",
                    "Near the glowing embers, beads of molten golden metal sweat out of the green and dark ores!",
                )
            return (
                "bronze_tool",
                None,
                "breakthrough",
                "Smelted copper and tin ores in the hearth fire into a gleaming cast bronze blade!",
            )

        # 2. Magnetic Compass Discovery (Fe3O4 Magnetite + Fiber/Wood suspension)
        if max(mat_a.magnetic, mat_b.magnetic) >= 0.9 and max_bind >= 0.8:
            lvl = insight_map.get("magnet_lore", 0) + 1
            insight_map["magnet_lore"] = lvl
            if lvl < 2:
                return (
                    None,
                    None,
                    "partial_insight",
                    "Dangling on a plant fiber, the dark lodestone eerily twists to face the exact same horizon!",
                )
            return (
                "compass_stone",
                None,
                "breakthrough",
                "Suspended magnetite lodestone into a directional compass revealing planetary north!",
            )

        # 3. Fire Ignition (FeS2 Pyrite + SiO2 Flint + Cellulose Tinder + >=3 trials)
        if max_hard >= 0.8 and max_spark >= 0.8:
            lvl = insight_map.get("spark_lore", 0) + 1
            insight_map["spark_lore"] = lvl
            has_tinder = any(BLIND_MATERIALS[c].flammability >= 0.85 for c in inventory)
            if lvl < 3 or not has_tinder:
                return (
                    None,
                    None,
                    "partial_insight",
                    "Striking iron pyrite against flint throws hot sparks—dry plant fibers could catch them.",
                )
            self._struct_seq += 1
            sx, sy = self.find_nearest_dry_spot(x, y)
            st = WorldStructure(
                id=f"S-{self._struct_seq}",
                kind="hearth",
                sensory_name="crackling stone-ring hearth",
                x=sx,
                y=sy,
                creator_id=actor_id,
                creator_lineage=actor_lineage,
                created_day=self.day,
                durability=180.0,
                fuel=90.0,
            )
            self.structures[st.id] = st
            return (
                None,
                st,
                "breakthrough",
                "Ignited dry cellulose tinder with pyrite-flint sparks into a sustained hearth!",
            )

        # 4. Lithic Hafting (SiO2 Flint + Hardwood Timber / Pine Resin)
        if max_sharp >= 0.85 and (
            code_a in ("rod_porous", "fiber_dry", "resin_gold")
            or code_b in ("rod_porous", "fiber_dry", "resin_gold")
        ):
            lvl = insight_map.get("haft_lore", 0) + 1
            insight_map["haft_lore"] = lvl
            if lvl < 2:
                return (
                    None,
                    None,
                    "partial_insight",
                    "Pressed the fractured flint into the wooden shaft; resin or fiber binding will hold it tight.",
                )
            return (
                "composite_tool",
                None,
                "breakthrough",
                "Hafted fractured flint onto hardwood timber, creating a composite lithic spear-knife!",
            )

        # 5. Cellulose Textile Weaving
        if max_bind >= 0.80 and (mat_a.insulation + mat_b.insulation) >= 0.75:
            lvl = insight_map.get("weave_lore", 0) + 1
            insight_map["weave_lore"] = lvl
            if lvl < 2:
                return (
                    None,
                    None,
                    "partial_insight",
                    "Twisted plant fibers into strong two-ply cordage.",
                )
            return (
                "warm_cloak",
                None,
                "breakthrough",
                "Wove cellulose fibers into an insulating textile cloak!",
            )

        # 6. Masonry / Earthen Shelter
        if max_insul >= 0.72 and (max_hard >= 0.4 or max_mall >= 0.8):
            lvl = insight_map.get("build_lore", 0) + 1
            insight_map["build_lore"] = lvl
            if lvl < 2:
                return (
                    None,
                    None,
                    "partial_insight",
                    "Tested stone and clay load-bearing stability.",
                )
            self._struct_seq += 1
            sx, sy = self.find_nearest_dry_spot(x, y)
            st = WorldStructure(
                id=f"S-{self._struct_seq}",
                kind="shelter",
                sensory_name="stone-and-timber shelter hut",
                x=sx,
                y=sy,
                creator_id=actor_id,
                creator_lineage=actor_lineage,
                created_day=self.day,
                durability=240.0,
            )
            self.structures[st.id] = st
            return (
                None,
                st,
                "breakthrough",
                "Constructed a weatherproof stone-and-timber shelter hut!",
            )

        # 7. Kaolin Ceramic Storage Granary
        if max_mall >= 0.88 and (max_bind >= 0.75 or max_flam >= 0.7 or near_hearth):
            lvl = insight_map.get("vessel_lore", 0) + 1
            insight_map["vessel_lore"] = lvl
            if lvl < 2:
                return (
                    None,
                    None,
                    "partial_insight",
                    "Coiled kaolin clay into a hollow vessel; tempering and heat will harden it.",
                )
            self._struct_seq += 1
            sx, sy = self.find_nearest_dry_spot(x, y)
            st = WorldStructure(
                id=f"S-{self._struct_seq}",
                kind="granary",
                sensory_name="ceramic storage amphora-granary",
                x=sx,
                y=sy,
                creator_id=actor_id,
                creator_lineage=actor_lineage,
                created_day=self.day,
                durability=240.0,
                stored_food=3,
            )
            self.structures[st.id] = st
            return (
                None,
                st,
                "breakthrough",
                "Fired a kaolin ceramic storage granary for preserving food reserves!",
            )

        # 8. Epigraphic Stone Carving
        if max_sharp >= 0.85 and (code_a == "slab_dense" or code_b == "slab_dense") and utterance_mark:
            lvl = insight_map.get("carve_lore", 0) + 1
            insight_map["carve_lore"] = lvl
            if lvl < 2:
                return (
                    None,
                    None,
                    "partial_insight",
                    "Incised geometric strokes onto limestone.",
                )
            self._struct_seq += 1
            sx, sy = self.find_nearest_dry_spot(x, y)
            st = WorldStructure(
                id=f"S-{self._struct_seq}",
                kind="monolith",
                sensory_name=f"carved stone stele «{utterance_mark}»",
                x=sx,
                y=sy,
                creator_id=actor_id,
                creator_lineage=actor_lineage,
                created_day=self.day,
                durability=900.0,
                inscription=utterance_mark,
            )
            self.structures[st.id] = st
            return (
                None,
                st,
                "breakthrough",
                f"Carved a permanent stone stele inscribed with «{utterance_mark}»!",
            )

        # 9. Unprompted Symbolic Art / Precious Mineral Working (ONLY if they experiment on rare minerals!)
        max_luster = max(mat_a.luster, mat_b.luster)
        if max_luster >= 0.80 and (max_bind >= 0.75 or max_hard >= 0.78):
            lvl = insight_map.get("lapidary_lore", 0) + 1
            insight_map["lapidary_lore"] = lvl
            if lvl < 2:
                return (
                    None,
                    None,
                    "partial_insight",
                    "Rubbed and pierced the gleaming rare mineral; it catches sunlight without tarnishing.",
                )
            return (
                "crafted_ornament",
                None,
                "breakthrough",
                "Shaped and strung a rare gleaming mineral into a wearable symbolic ornament!",
            )

        return None, None, "inert", "Examined both terrestrial materials without reaction."
