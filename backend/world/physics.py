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
from typing import Any, Dict, List, Optional, Tuple

CHUNK_SIZE = 16
EARTH_RADIUS_KM = 6_371.0
EARTH_DIAMETER_KM = 12_742.0
EARTH_CIRCUMFERENCE_KM = 40_075.0
EARTH_SURFACE_KM2 = 510_072_000.0
PLANET_SURFACE_KM2 = EARTH_SURFACE_KM2  # Exact 1:1 Planet Earth (510.072M km², 12,742 km diameter, 40,075 km circumference!)
KM2_PER_SECTOR = 25.0

# Exact Real Solar System (Sun + 8 Planets + Moon — real orbital periods in Earth days, AU distances & diameters in km)
SOLAR_SYSTEM_BODIES: Dict[str, Dict[str, Any]] = {
    "Sun":     {"au": 0.0,   "period_days": 0.0,     "diameter_km": 1_392_700, "color": "#fde047"},
    "Mercury": {"au": 0.387, "period_days": 87.97,   "diameter_km": 4_879,     "color": "#94a3b8"},
    "Venus":   {"au": 0.723, "period_days": 224.70,  "diameter_km": 12_104,    "color": "#fde68a"},
    "Earth":   {"au": 1.000, "period_days": 365.25,  "diameter_km": 12_742,    "color": "#38bdf8"},
    "Moon":    {"au": 0.00257,"period_days": 29.53,  "diameter_km": 3_474,     "color": "#e2e8f0"},
    "Mars":    {"au": 1.524, "period_days": 686.98,  "diameter_km": 6_779,     "color": "#ef4444"},
    "Jupiter": {"au": 5.204, "period_days": 4332.59, "diameter_km": 139_820,   "color": "#d97706"},
    "Saturn":  {"au": 9.582, "period_days": 10759.2, "diameter_km": 116_460,   "color": "#eab308"},
    "Uranus":  {"au": 19.20, "period_days": 30688.5, "diameter_km": 50_724,    "color": "#67e8f9"},
    "Neptune": {"au": 30.05, "period_days": 60182.0, "diameter_km": 49_244,    "color": "#3b82f6"},
}


ENCLAVE_HOMELANDS: Dict[str, Tuple[float, float]] = {
    "Sylphid": (-135.0, -115.0),  # NW Temperate Emerald River Continent
    "Lithokin": (145.0, -115.0),  # NE Boreal Volcanic Cordillera
    "Vespera": (12.0, 145.0),     # South Equatorial Monsoon Savanna Continent
}

MOUNTAIN_PEAKS: Tuple[Tuple[float, float, float, float], ...] = (
    # (mx, my, height, sigma_radius) — Real 3D Mountain Massifs across all Continents!
    (-112.0, -96.0, 10.8, 16.0),
    (-158.0, -134.0, 11.6, 18.0),
    (122.0, -98.0, 12.8, 19.0),
    (168.0, -132.0, 13.4, 20.0),
    (-14.0, 126.0, 10.2, 16.0),
    (36.0, 162.0, 11.4, 18.0),
    (-22.0, -14.0, 11.2, 17.0),
    (28.0, 18.0, 10.6, 16.0),
)


def terrain_height(x: float, y: float, seed: int = 4201) -> float:
    """Continuous planetary multi-continent 3D elevation with real Mountain Massifs (1:1 with Three.js)."""
    s = (seed % 997) * 0.013
    river_center = math.sin(y * 0.026 + s) * 28.0 - 14.0
    dist_river = abs(x - river_center)
    river_carve = -1.55 * math.exp(-(dist_river * dist_river) / 38.0)
    sea_strait = -1.45 * math.exp(-((y - math.sin(x * 0.022) * 24.0 + 28.0) ** 2) / 52.0)

    continents = math.sin(x * 0.013 + s) * math.cos(y * 0.013 - s) * 1.45
    hills = (
        math.sin(x * 0.036 + s) * math.cos(y * 0.036 - s) * 0.92
        + math.sin((x * 0.075 - y * 0.065) + s * 2.0) * 0.38
    )
    ridge_belt = max(0.0, math.sin(x * 0.024 - y * 0.021 + 0.8) - 0.56) * 4.8

    mtn_boost = 0.0
    for mx, my, mh, mr in MOUNTAIN_PEAKS:
        d2 = (x - mx) ** 2 + (y - my) ** 2
        if d2 < (mr * 2.6) ** 2:
            mtn_boost += mh * math.exp(-d2 / (mr * mr))

    return round(0.62 + continents + hills + ridge_belt + mtn_boost + river_carve + sea_strait * 0.65, 3)


def classify_climate_zone(x: float, y: float) -> str:
    """Real Earth-like latitudinal & regional climate bands across the Super-Earth."""
    if y < -55.0 and x >= 20.0:
        return "boreal_highland"
    if y < -50.0 and x < 20.0:
        return "temperate_archipelago"
    if y > 60.0:
        return "equatorial_savanna"
    return "mediterranean_crossroads"


def classify_biome(x: float, y: float, seed: int = 4201) -> str:
    h = terrain_height(x, y, seed)
    if h < -0.05:
        return "water"
    if h < 0.24:
        return "riverbank"
    if h > 2.20:
        return "ridge"
    s = (seed % 997) * 0.013
    moisture = math.sin(x * 0.04 - s) + math.cos(y * 0.045 + s)
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
    healing: float = 0.0  # Natural phytochemical analgesia/tissue repair
    toxicity: float = 0.0  # Alkaloid/venomous hazard learned strictly by experience


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
    "grain_seed": BlindMaterial(
        code="grain_seed",
        formula="Amylose + Aleurone Cereal Grain",
        sensory_name="dry golden seed-panicle",
        observer_label="Golden Stalk Grain (Cereal)",
        color_hex="#eab308",
        nutrition=32.0,
    ),
    "medicinal_herb": BlindMaterial(
        code="medicinal_herb",
        formula="Salicin + Terpenoid Phytochemicals",
        sensory_name="fragrant silver-veined leaf",
        observer_label="Sootheleaf (Medicinal Herb)",
        color_hex="#2dd4bf",
        nutrition=10.0,
        healing=28.0,
    ),
    "toxic_nightshade": BlindMaterial(
        code="toxic_nightshade",
        formula="Tropane Alkaloid Berry",
        sensory_name="glossy dark-violet bitter berry",
        observer_label="Shadowberry (Toxic Flora!)",
        color_hex="#7e22ce",
        nutrition=4.0,
        toxicity=24.0,
    ),
    "ivory_horn": BlindMaterial(
        code="ivory_horn",
        formula="Hydroxyapatite Dentine Tusk",
        sensory_name="curved dense pale tusk-bone",
        observer_label="Megafauna Tusk-Bone",
        color_hex="#fef9c3",
        hardness=0.78,
        sharpness=0.74,
        luster=0.84,
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
    "wheeled_cart": BlindMaterial(
        code="wheeled_cart",
        formula="Axle-Mounted Timber & Stone Disks",
        sensory_name="rolling wooden frame on round disks",
        observer_label="Wheeled Transport Cart (Mechanical Tech!)",
        color_hex="#ca8a04",
        hardness=0.65,
    ),
    "silica_glass": BlindMaterial(
        code="silica_glass",
        formula="Fused Amorphous SiO2 Silicate",
        sensory_name="clear smooth fused pane",
        observer_label="Fused Silica Glass & Lens (Optics Tech!)",
        color_hex="#bae6fd",
        hardness=0.82,
        luster=0.96,
    ),
    "copper_coil": BlindMaterial(
        code="copper_coil",
        formula="Drawn Cu Conductor + Fe3O4 Core",
        sensory_name="spiraled gleaming wire that hums near lodestone",
        observer_label="Electromagnetic Copper Coil (Signal/Power Tech!)",
        color_hex="#34d399",
        hardness=0.72,
        metallic=1.0,
        magnetic=0.95,
    ),
    "refined_fuel": BlindMaterial(
        code="refined_fuel",
        formula="Pyrolyzed Terpene-Hydrocarbon Distillate",
        sensory_name="volatile warm dark-amber liquid",
        observer_label="Refined High-Energy Propellant (Energetic Tech!)",
        color_hex="#f97316",
        flammability=1.0,
        spark_potential=0.98,
    ),
    # Progressive Emergent Medicine & Cures (0% hints — discovered empirically from flora, resin & glass!)
    "herbal_remedy": BlindMaterial(
        code="herbal_remedy",
        formula="Steeped Phytochemical Botanical Infusion",
        sensory_name="soothing warm fragrant green-pulp poultice",
        observer_label="Herbal Remedy Poultice (Early Medicine)",
        color_hex="#2dd4bf",
        healing=0.82,
    ),
    "antiseptic_balm": BlindMaterial(
        code="antiseptic_balm",
        formula="Distilled Terpene-Resin & Cu-Ion Antiseptic",
        sensory_name="sharp cooling amber-teal salve",
        observer_label="Antiseptic Apothecary Balm (Apothecary Medicine)",
        color_hex="#14b8a6",
        healing=0.95,
    ),
    "clinical_cure": BlindMaterial(
        code="clinical_cure",
        formula="Purified Glass-Sealed Antimicrobial Serum",
        sensory_name="crystal-clear luminescent vial of tonic",
        observer_label="Purified Clinical Cure (Modern Medicine!)",
        color_hex="#38bdf8",
        healing=1.0,
        luster=0.90,
    ),
    "clay_tablet": BlindMaterial(
        code="clay_tablet",
        formula="Kiln-Fired Incised Kaolin Clay Tablet",
        sensory_name="hard baked clay slab etched with repeating marks",
        observer_label="Inscribed Clay Tablet (Proto-Writing!)",
        color_hex="#d97706",
        hardness=0.74,
        luster=0.35,
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


FLORA_SPECIES = {
    "ironbark_tree": "Oak (Quercus robur)",
    "boreal_conifer": "Scots Pine (Pinus sylvestris)",
    "monsoon_palm": "Date Palm (Phoenix dactylifera)",
    "amber_pine": "Resin Cedar (Cedrus libani)",
    "hollow_cane": "Giant Bamboo (Bambusa)",
    "amberberry_shrub": "Wild Blackberry (Rubus)",
    "golden_stalk": "Wild Einkorn Wheat (Triticum)",
    "sootheleaf": "White Willow / Medicinal Herb (Salix)",
    "shadowberry": "Deadly Nightshade (Atropa belladonna)",
    "weaver_reed": "Wild Flax (Linum usitatissimum)",
    "frost_lichen": "Reindeer Lichen (Cladonia)",
    "starch_bulb": "Wild Yam / Tuber (Dioscorea)",
    "oil_olive": "Wild Olive (Olea europaea)",
    "cloud_cotton": "Wild Cotton (Gossypium)",
    "cork_oak": "Cork Oak (Quercus suber)",
    "wild_vine_grape": "Wild Grapevine (Vitis vinifera)",
    "marsh_lotus": "Sacred Lotus (Nelumbo nucifera)",
    "juniper_cypress": "Alpine Juniper (Juniperus)",
    "honey_hive_tree": "Wild Honey-Acacia (Acacia)",
    "spiced_bark": "Bay Laurel (Laurus nobilis)",
    "giant_kelp": "Giant Sea Kelp (Macrocystis)",
    "cacao_pod": "Wild Cacao (Theobroma cacao)",
}

# 42 Real Earth & Pleistocene Wild Fauna Species across all Terrestrial, Aerial, Freshwater & Marine Niches!
FAUNA_CATALOG = {
    # Pleistocene Megafauna & Herd Ungulates (11)
    "titanotusk": {"domain": "land", "speed": 0.14, "hp": 260.0, "danger": 26.0, "hostile": "defensive", "cap": 5, "meat": 3, "label": "Woolly Mammoth (Mammuthus primigenius)"},
    "thunderhorn": {"domain": "land", "speed": 0.21, "hp": 165.0, "danger": 18.0, "hostile": "defensive", "cap": 7, "meat": 2, "label": "Steppe Bison (Bison priscus)"},
    "lumigrazer": {"domain": "land", "speed": 0.22, "hp": 95.0, "danger": 0.0, "hostile": "none", "cap": 10, "meat": 1, "label": "Red Deer (Cervus elaphus)"},
    "windstrider": {"domain": "land", "speed": 0.34, "hp": 110.0, "danger": 0.0, "hostile": "none", "cap": 7, "meat": 1, "tameable": True, "label": "Wild Horse (Equus ferus)"},
    "craghorn": {"domain": "land", "speed": 0.24, "hp": 85.0, "danger": 8.0, "hostile": "defensive", "cap": 6, "meat": 1, "tameable": True, "label": "Wild Goat / Ibex (Capra aegagrus)"},
    "woolflock": {"domain": "land", "speed": 0.20, "hp": 72.0, "danger": 0.0, "hostile": "none", "cap": 8, "meat": 1, "tameable": True, "label": "Wild Mouflon Sheep (Ovis gmelini)"},
    "rootboar": {"domain": "land", "speed": 0.23, "hp": 90.0, "danger": 15.0, "hostile": "defensive", "cap": 7, "meat": 1, "label": "Wild Boar (Sus scrofa)"},
    "dunestrider": {"domain": "land", "speed": 0.26, "hp": 145.0, "danger": 10.0, "hostile": "defensive", "cap": 5, "meat": 2, "tameable": True, "label": "Wild Bactrian Camel (Camelus ferus)"},
    "tallneck": {"domain": "land", "speed": 0.25, "hp": 175.0, "danger": 14.0, "hostile": "defensive", "cap": 5, "meat": 2, "label": "Savanna Giraffe (Giraffa camelopardalis)"},
    "riverbulk": {"domain": "shore", "speed": 0.17, "hp": 230.0, "danger": 28.0, "hostile": "defensive", "cap": 4, "meat": 3, "label": "Hippopotamus (Hippopotamus amphibius)"},
    "frostantler": {"domain": "land", "speed": 0.25, "hp": 115.0, "danger": 6.0, "hostile": "none", "cap": 7, "meat": 2, "tameable": True, "label": "Reindeer / Caribou (Rangifer tarandus)"},
    # Small Mammals, Primates & Reptiles (6)
    "burrowhare": {"domain": "land", "speed": 0.31, "hp": 35.0, "danger": 0.0, "hostile": "none", "cap": 9, "meat": 1, "label": "European Hare (Lepus europaeus)"},
    "damweaver": {"domain": "shore", "speed": 0.16, "hp": 50.0, "danger": 0.0, "hostile": "none", "cap": 6, "meat": 1, "label": "Eurasian Beaver (Castor fiber)"},
    "canopykin": {"domain": "land", "speed": 0.27, "hp": 55.0, "danger": 0.0, "hostile": "none", "cap": 6, "meat": 1, "label": "Chimpanzee (Pan troglodytes)"},
    "quillback": {"domain": "land", "speed": 0.14, "hp": 42.0, "danger": 12.0, "hostile": "defensive", "cap": 6, "meat": 1, "label": "Crested Porcupine (Hystrix cristata)"},
    "slyfox": {"domain": "land", "speed": 0.30, "hp": 48.0, "danger": 6.0, "hostile": "none", "cap": 6, "meat": 1, "label": "Red Fox (Vulpes vulpes)"},
    "shellback": {"domain": "shore", "speed": 0.08, "hp": 75.0, "danger": 0.0, "hostile": "none", "cap": 7, "meat": 1, "label": "Giant Tortoise (Testudo)"},
    # Apex Predators, Pleistocene Carnivores & Venomous Fauna (10)
    "shadowstalker": {"domain": "land", "speed": 0.30, "hp": 125.0, "danger": 22.0, "hostile": "night", "cap": 5, "meat": 1, "label": "Saber-Toothed Cat (Smilodon fatalis)"},
    "sunmane": {"domain": "land", "speed": 0.29, "hp": 140.0, "danger": 24.0, "hostile": "day", "cap": 5, "meat": 1, "label": "African Lion (Panthera leo)"},
    "stripeclaw": {"domain": "land", "speed": 0.31, "hp": 155.0, "danger": 26.0, "hostile": "night", "cap": 4, "meat": 2, "label": "Bengal Tiger (Panthera tigris)"},
    "frostmaw": {"domain": "land", "speed": 0.24, "hp": 195.0, "danger": 28.0, "hostile": "always", "cap": 4, "meat": 2, "label": "Cave / Brown Bear (Ursus arctos)"},
    "packhound": {"domain": "land", "speed": 0.26, "hp": 80.0, "danger": 14.0, "hostile": "pack", "cap": 8, "meat": 1, "tameable": True, "label": "Gray Wolf (Canis lupus)"},
    "bonecruncher": {"domain": "land", "speed": 0.27, "hp": 95.0, "danger": 17.0, "hostile": "pack", "cap": 6, "meat": 1, "label": "Spotted Hyena (Crocuta crocuta)"},
    "mirejaw": {"domain": "shore", "speed": 0.18, "hp": 150.0, "danger": 26.0, "hostile": "ambush", "cap": 5, "meat": 2, "label": "Nile Crocodile (Crocodylus niloticus)"},
    "venomcoil": {"domain": "land", "speed": 0.19, "hp": 28.0, "danger": 22.0, "hostile": "venom", "cap": 6, "meat": 1, "label": "King Cobra / Viper (Vipera)"},
    "stingshell": {"domain": "land", "speed": 0.15, "hp": 24.0, "danger": 16.0, "hostile": "venom", "cap": 6, "meat": 0, "label": "Deathstalker Scorpion (Leiurus)"},
    "scalejaw": {"domain": "land", "speed": 0.21, "hp": 115.0, "danger": 20.0, "hostile": "day", "cap": 4, "meat": 2, "label": "Komodo Monitor (Varanus komodoensis)"},
    # Marine & Freshwater Aquatic Life (8)
    "silverfin_shoal": {"domain": "water", "speed": 0.18, "hp": 35.0, "danger": 0.0, "hostile": "none", "cap": 10, "meat": 1, "label": "Atlantic Salmon (Salmo salar)"},
    "deepfin_tuna": {"domain": "water", "speed": 0.27, "hp": 55.0, "danger": 0.0, "hostile": "none", "cap": 8, "meat": 2, "label": "Bluefin Tuna (Thunnus thynnus)"},
    "abyssalfin": {"domain": "water", "speed": 0.28, "hp": 120.0, "danger": 21.0, "hostile": "ambush", "cap": 4, "meat": 2, "label": "Great White Shark (Carcharodon carcharias)"},
    "leviathansong": {"domain": "water", "speed": 0.14, "hp": 320.0, "danger": 0.0, "hostile": "none", "cap": 4, "meat": 3, "label": "Blue Whale (Balaenoptera musculus)"},
    "wavekin": {"domain": "water", "speed": 0.30, "hp": 90.0, "danger": 0.0, "hostile": "none", "cap": 6, "meat": 1, "label": "Bottlenose Dolphin (Tursiops truncatus)"},
    "inkweaver": {"domain": "water", "speed": 0.16, "hp": 45.0, "danger": 5.0, "hostile": "none", "cap": 6, "meat": 1, "label": "Common Octopus (Octopus vulgaris)"},
    "tidecrawler": {"domain": "shore", "speed": 0.10, "hp": 30.0, "danger": 0.0, "hostile": "none", "cap": 8, "meat": 1, "label": "Shore Crab (Carcinus maenas)"},
    "pearlclam": {"domain": "shore", "speed": 0.02, "hp": 20.0, "danger": 0.0, "hostile": "none", "cap": 7, "meat": 1, "label": "Pearl Oyster (Pinctada)"},
    # Avian, Poultry, Amphibians & Keystone Pollinators (7)
    "skyglider": {"domain": "air", "speed": 0.33, "hp": 45.0, "danger": 0.0, "hostile": "none", "cap": 6, "meat": 1, "label": "Golden Eagle (Aquila chrysaetos)"},
    "nightwing": {"domain": "air", "speed": 0.28, "hp": 36.0, "danger": 0.0, "hostile": "none", "cap": 6, "meat": 1, "label": "Eurasian Eagle-Owl (Bubo bubo)"},
    "reedwing": {"domain": "air", "speed": 0.25, "hp": 32.0, "danger": 0.0, "hostile": "none", "cap": 7, "meat": 1, "label": "Mallard Duck (Anas platyrhynchos)"},
    "meadowfowl": {"domain": "land", "speed": 0.21, "hp": 28.0, "danger": 0.0, "hostile": "none", "cap": 8, "meat": 1, "tameable": True, "label": "Red Junglefowl / Wild Chicken (Gallus gallus)"},
    "pollenwing": {"domain": "air", "speed": 0.26, "hp": 20.0, "danger": 0.0, "hostile": "none", "cap": 8, "meat": 0, "label": "Western Honeybee (Apis mellifera)"},
    "carrionwing": {"domain": "air", "speed": 0.30, "hp": 42.0, "danger": 0.0, "hostile": "none", "cap": 5, "meat": 1, "label": "Griffon Vulture (Gyps fulvus)"},
    "mistcroak": {"domain": "shore", "speed": 0.12, "hp": 18.0, "danger": 0.0, "hostile": "none", "cap": 7, "meat": 1, "label": "Common Frog (Rana temporaria)"},
}


@dataclass
class WildAnimal:
    id: str
    species: str  # 24-species + dynamically evolved daughter species!
    x: float
    y: float
    energy: float = 85.0
    health: float = 100.0
    alive: bool = True
    generation: int = 1
    size_gene: float = 1.0
    speed_gene: float = 1.0
    coat_color: str = ""
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
class CaveSite:
    id: str
    x: float
    y: float
    climate_zone: str
    depth_m: float = 28.0


@dataclass
class WorldStructure:
    id: str
    kind: str  # hearth|shelter|granary|monolith|cairn|palisade|watercraft|crop_plot|burrow_network|edifice|comm_relay|land_vehicle|air_craft|orbital_satellite|open_creation
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
    water_crossing: bool = False
    crop_timer: int = 0
    layer: str = "surface"  # "subterranean" | "surface" | "aerial" | "orbital"
    tech_tier: int = 1      # 1..5 cumulative civilizational tier
    is_vehicle: bool = False
    vehicle_speed: float = 0.0
    build_progress: float = 1.0  # 0.25 (foundation/posts) -> 1.0 (completed roofed dwelling)
    vehicle_domain: str = "land"  # "land" | "water" | "air" | "orbit"
    vehicle_target: Optional[Tuple[float, float]] = None
    signal_range: float = 0.0  # > 0 enables long-distance speech & lore transmission!
    stories: int = 1
    chambers: int = 1
    blueprint_3d: Optional[List[Dict[str, Any]]] = None


SEASONS = ["Spring", "Summer", "Autumn", "Deep Winter"]
DAYS_PER_YEAR = 365
DAYS_PER_SEASON = 91
TICKS_PER_DAY = 24  # Exact 1 tick = 1 Earth hour (24h/day, 365 days/year, 270-day 9-month pregnancy!)
LUNAR_CYCLE_DAYS = 29.5


class CosmosWorld:
    """10x Super-Earth Planetary Environment with Orbital Astrophysics, Lunar Tides, Caves & Unbounded Tech."""

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
        self.extinct_fauna: Dict[str, int] = {}  # Permanent extinction ledger (species -> day extinct)!
        self.evolved_fauna: Dict[str, Dict[str, Any]] = {}  # Newly speciated wild species!
        self.thermal_vents: List[Tuple[float, float]] = []
        self.caves: Dict[str, CaveSite] = {}
        # Stochastic Weather, Solar Anomaly & Earth Geophysics / Natural Disasters State
        self.weather: str = "clear"  # "clear" | "rain" | "storm" | "fog" | "snow" | "drought"
        self.weather_ticks_left: int = 90
        self.solar_anomaly_c: float = 0.0
        self.soil_fertility: Dict[Tuple[int, int], float] = {}  # 0.35..1.50 per chunk (Nile-like silt & depletion!)
        self.active_disaster: str = ""  # "" | "earthquake" | "volcanic_eruption" | "river_flood" | "wildfire"
        self.disaster_xy: Tuple[float, float] = (0.0, 0.0)
        self.disaster_ticks: int = 0
        self.newly_triggered_disaster: Optional[Dict[str, Any]] = None

        # Generate the Central Crossroads + all 3 distant Continental Homelands!
        seed_centers = [(0, 0), (-8, -7), (9, -7), (1, 9)]
        for bx, by in seed_centers:
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if (bx + dx, by + dy) not in self.chunks:
                        self._generate_chunk(bx + dx, by + dy)

        # Guarantee volcanic geothermal vents in the NE Boreal Lithokin Cordillera
        for off_x, off_y in ((-5.0, 4.0), (6.0, -4.5)):
            vx, vy = self.find_nearest_dry_spot(145.0 + off_x, -115.0 + off_y)
            self.thermal_vents.append((vx, vy))

        # Seed 8 Natural Mountain Caverns directly into the lower rocky flanks of MOUNTAIN_PEAKS!
        for idx, (mx, my, _mh, mr) in enumerate(MOUNTAIN_PEAKS, start=1):
            cx, cy = self.find_nearest_dry_spot(mx, my + mr * 0.62)
            cid = f"CAVE-{idx}"
            self.caves[cid] = CaveSite(
                id=cid,
                x=cx,
                y=cy,
                climate_zone=classify_climate_zone(cx, cy),
                depth_m=round(34.0 + (idx % 4) * 16.0, 1),
            )
            gx, gy = int(round(cx)), int(round(cy))
            self._add_resource_at(gx, gy, "slab_dense")
            self._add_resource_at(gx, gy, "nodule_red" if idx % 2 == 0 else "copper_ore")

        self._spawn_initial_fauna()

    @property
    def day(self) -> int:
        return (self.tick_count // TICKS_PER_DAY) + 1

    @property
    def year(self) -> int:
        return ((self.day - 1) // DAYS_PER_YEAR) + 1

    @property
    def day_of_year(self) -> int:
        return ((self.day - 1) % DAYS_PER_YEAR) + 1

    @property
    def season_index(self) -> int:
        return min(3, ((self.day - 1) % DAYS_PER_YEAR) // DAYS_PER_SEASON)

    @property
    def season_name(self) -> str:
        return SEASONS[self.season_index]

    @property
    def day_phase(self) -> float:
        return (self.tick_count % TICKS_PER_DAY) / float(TICKS_PER_DAY)

    def local_solar_phase_at(self, x: float, y: float) -> float:
        """Real Earth-like planetary longitude solar time (0.0=midnight .. 0.5=solar noon .. 1.0=midnight)."""
        lon_offset = (x / 310.0) * 0.5  # East-West continental time zones across the globe!
        return (self.day_phase + lon_offset) % 1.0

    def daylight_hours_at(self, x: float, y: float) -> float:
        """Real Earth 23.4° axial tilt daylight duration (12h at equator, longer summer / shorter winter at boreal latitudes)."""
        lat_norm = max(-1.0, min(1.0, -y / 220.0))  # +1 = Boreal North, 0 = Crossroads, -1 = Equatorial/South
        season_decl = math.sin(((self.day - 1) / float(DAYS_PER_YEAR)) * 2.0 * math.pi)
        # Earth-like photoperiod variation: ~12h at equator, ~8.5h..15.5h at mid-high latitudes
        return round(max(7.5, min(16.5, 12.0 + lat_norm * season_decl * 3.6)), 1)

    def is_night_at(self, x: float, y: float) -> bool:
        """True if local sun is below the horizon at longitude x & latitude y."""
        local_hr = self.local_solar_phase_at(x, y) * 24.0
        half_day = self.daylight_hours_at(x, y) * 0.5
        return not ((12.0 - half_day) <= local_hr <= (12.0 + half_day))

    @property
    def is_night(self) -> bool:
        return self.is_night_at(0.0, 0.0)

    @property
    def solar_distance_au(self) -> float:
        """Exact Earth elliptical orbit (0.983 AU perihelion .. 1.017 AU aphelion) + Jupiter/Venus gravitational resonance."""
        ang = ((self.day - 1) / float(DAYS_PER_YEAR)) * 2.0 * math.pi
        jup_pull = 0.0018 * math.cos((self.day / 4332.59) * 2.0 * math.pi)
        ven_pull = 0.0009 * math.cos((self.day / 224.70) * 2.0 * math.pi)
        return round(1.000 - 0.0167 * math.cos(ang + 0.6) + jup_pull + ven_pull, 4)

    def solar_system_angles(self) -> Dict[str, float]:
        """Exact real-time orbital longitudes (radians) of all 8 planets around the Sun!"""
        return {
            name: round(((self.day / spec["period_days"]) * 2.0 * math.pi) % (2.0 * math.pi), 3)
            for name, spec in SOLAR_SYSTEM_BODIES.items()
            if spec["period_days"] > 0
        }

    @property
    def lunar_phase(self) -> float:
        """28-day synodic lunar cycle [0.0=New Moon, 0.5=Full Moon]."""
        return round(((self.tick_count / float(TICKS_PER_DAY)) % LUNAR_CYCLE_DAYS) / LUNAR_CYCLE_DAYS, 3)

    @property
    def lunar_illumination(self) -> float:
        return round(0.5 * (1.0 - math.cos(self.lunar_phase * 2.0 * math.pi)), 3)

    @property
    def lunar_phase_name(self) -> str:
        p = self.lunar_phase
        if p < 0.08 or p >= 0.92:
            return "New Moon"
        if p < 0.22:
            return "Waxing Crescent"
        if p < 0.34:
            return "First Quarter"
        if p < 0.44:
            return "Waxing Gibbous"
        if p < 0.58:
            return "Full Moon"
        if p < 0.70:
            return "Waning Gibbous"
        if p < 0.82:
            return "Last Quarter"
        return "Waning Crescent"

    @property
    def tidal_offset(self) -> float:
        """Spring tides peak at New & Full Moon; modulates coastal shellfish deposition."""
        return round(0.14 * math.cos((self.lunar_phase * 4.0 + self.day_phase * 2.0) * math.pi), 3)

    @property
    def ambient_temperature(self) -> float:
        season_base = [19.0, 25.5, 13.5, 5.2][self.season_index]
        # Inverse-square solar flux effect from orbital eccentricity (~ +/- 2.6°C)
        orbital_delta = (1.0 / (self.solar_distance_au ** 2) - 1.0) * 34.0
        weather_delta = {
            "clear": 0.0,
            "rain": -2.0,
            "storm": -3.5,
            "fog": -1.0,
            "snow": -5.8,
            "drought": 4.2,
        }.get(self.weather, 0.0)
        diurnal = math.sin((self.day_phase - 0.08) * 2.0 * math.pi) * 4.6
        return round(season_base + orbital_delta + weather_delta + self.solar_anomaly_c + diurnal, 2)

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
            # Bridges, rafts & timber causeways built by inhabitants allow crossing rivers & straits!
            if any(st.water_crossing and math.hypot(st.x - x, st.y - y) <= 4.0 for st in self.structures.values()):
                return True
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

                zone = classify_climate_zone(tx, ty)
                if biome == "forest" and trng.random() < 0.42:
                    if len(self.props) < 1900:
                        t_kind = (
                            "boreal_conifer" if zone == "boreal_highland"
                            else "monsoon_palm" if zone == "equatorial_savanna"
                            else "amber_pine" if trng.random() < 0.3
                            else "tree"
                        )
                        self._add_prop(t_kind, px, py, scale=round(trng.uniform(0.85, 1.45), 2), radius=0.65)
                    self._seed_tile_resources(tx, ty, biome, trng, initial=True)
                elif biome in ("meadow", "savanna") and trng.random() < 0.28:
                    if len(self.props) < 1900:
                        b_kind = (
                            "golden_stalk" if trng.random() < 0.32
                            else "sootheleaf" if trng.random() < 0.14
                            else "shadowberry" if trng.random() < 0.08
                            else "bush"
                        )
                        self._add_prop(b_kind, px, py, scale=round(trng.uniform(0.75, 1.15), 2), radius=0.0)
                    self._seed_tile_resources(tx, ty, biome, trng, initial=True)
                elif biome in ("ridge", "tundra") and trng.random() < 0.34:
                    if len(self.props) < 1900:
                        kind = "crystal" if trng.random() < 0.28 else ("frost_lichen" if biome == "tundra" and trng.random() < 0.35 else "boulder")
                        self._add_prop(kind, px, py, scale=round(trng.uniform(0.8, 1.4), 2), radius=0.62 if kind != "frost_lichen" else 0.0)
                    self._seed_tile_resources(tx, ty, biome, trng, initial=True)
                elif biome == "riverbank" and trng.random() < 0.34:
                    if len(self.props) < 1900 and trng.random() < 0.45:
                        self._add_prop("hollow_cane", px, py, scale=round(trng.uniform(0.8, 1.25), 2), radius=0.0)
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
        """Populates all 24 wild animal species in their authentic terrestrial/aquatic/avian biomes!"""
        regional_guilds = [
            # NW Temperate Emerald River Basin (Sylphid Continent)
            ((-135.0, -115.0), ["lumigrazer", "lumigrazer", "rootboar", "burrowhare", "damweaver", "damweaver", "packhound", "packhound", "silverfin_shoal", "silverfin_shoal", "pearlclam", "reedwing", "pollenwing", "pollenwing", "shadowstalker"]),
            # NE Boreal Volcanic Cordillera (Lithokin Continent)
            ((145.0, -115.0), ["titanotusk", "thunderhorn", "craghorn", "craghorn", "craghorn", "frostmaw", "frostmaw", "packhound", "packhound", "burrowhare", "silverfin_shoal", "skyglider", "skyglider", "pollenwing"]),
            # South Equatorial Monsoon Savanna & Coast (Vespera Continent)
            ((12.0, 145.0), ["titanotusk", "thunderhorn", "windstrider", "windstrider", "canopykin", "canopykin", "sunmane", "sunmane", "mirejaw", "mirejaw", "venomcoil", "venomcoil", "stingshell", "tidecrawler", "tidecrawler", "pearlclam", "pollenwing", "pollenwing"]),
            # Central Mediterranean Crossroads & Deep Sea
            ((0.0, 0.0), ["titanotusk", "thunderhorn", "lumigrazer", "lumigrazer", "windstrider", "rootboar", "burrowhare", "canopykin", "damweaver", "sunmane", "frostmaw", "shadowstalker", "shadowstalker", "mirejaw", "venomcoil", "stingshell", "stingshell", "silverfin_shoal", "silverfin_shoal", "abyssalfin", "abyssalfin", "abyssalfin", "leviathansong", "leviathansong", "leviathansong", "tidecrawler", "pearlclam", "skyglider", "reedwing", "reedwing", "pollenwing"]),
        ]
        for (cx, cy), sp_list in regional_guilds:
            for sp in sp_list:
                self._animal_seq += 1
                dom = FAUNA_CATALOG[sp]["domain"]
                if dom == "water":
                    ax, ay = self.find_nearest_water_spot(cx + self.rng.uniform(-32.0, 32.0), cy + self.rng.uniform(-32.0, 32.0))
                elif dom == "air":
                    ax, ay = round(cx + self.rng.uniform(-38.0, 38.0), 2), round(cy + self.rng.uniform(-38.0, 38.0), 2)
                else:
                    ax, ay = self.find_nearest_dry_spot(cx + self.rng.uniform(-30.0, 30.0), cy + self.rng.uniform(-30.0, 30.0))
                self.animals[f"W-{self._animal_seq:03d}"] = WildAnimal(
                    id=f"W-{self._animal_seq:03d}", species=sp, x=ax, y=ay, health=FAUNA_CATALOG[sp]["hp"]
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
            if rng.random() < 0.44 * p:
                self._add_resource_at(tx, ty, "orb_sweet")
            if rng.random() < 0.24 * p:
                self._add_resource_at(tx, ty, "grain_seed")
            if rng.random() < 0.22 * p:
                self._add_resource_at(tx, ty, "fiber_dry")
            if rng.random() < 0.09 * p:
                self._add_resource_at(tx, ty, "medicinal_herb")
            if rng.random() < 0.045 * p:
                self._add_resource_at(tx, ty, "toxic_nightshade")
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

    def is_sheltered_at(self, x: float, y: float) -> bool:
        """True if inside a natural cave, subterranean burrow, shelter hut, or multi-story edifice."""
        for cv in self.caves.values():
            if math.hypot(x - cv.x, y - cv.y) <= 3.8:
                return True
        for st in self.structures.values():
            if st.kind in ("shelter", "edifice", "burrow_network") and math.hypot(x - st.x, y - st.y) <= 4.5:
                return True
        return False

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
        # Subterranean / Cave geothermal homeostasis (~15.5°C year-round!)
        in_cave_or_burrow = any(math.hypot(x - cv.x, y - cv.y) <= 3.8 for cv in self.caves.values()) or any(
            st.layer == "subterranean" and math.hypot(x - st.x, y - st.y) <= 4.8 for st in self.structures.values()
        )
        if in_cave_or_burrow:
            temp = temp * 0.35 + 15.5 * 0.65
        for vx, vy in self.thermal_vents:
            d = math.hypot(x - vx, y - vy)
            if d < 6.5:
                temp += (6.5 - d) * 3.4
        for st in self.structures.values():
            d = math.hypot(x - st.x, y - st.y)
            if st.kind == "hearth" and st.fuel > 0 and d < 6.0:
                temp += (6.0 - d) * 4.5
            elif st.kind in ("shelter", "edifice") and d < 4.8:
                temp += (4.8 - d) * (3.0 + st.stories * 0.4)
        return round(temp, 2)

    def soil_fertility_at(self, x: float, y: float) -> float:
        ck = self.tile_to_chunk(int(round(x)), int(round(y)))
        return round(self.soil_fertility.get(ck, 1.0), 2)

    def deplete_soil_at(self, x: float, y: float, amount: float = 0.03) -> None:
        ck = self.tile_to_chunk(int(round(x)), int(round(y)))
        self.soil_fertility[ck] = max(0.35, round(self.soil_fertility.get(ck, 1.0) - amount, 3))

    def step_environment(self) -> None:
        self.tick_count += 1
        self.newly_triggered_disaster = None
        if self.disaster_ticks > 0:
            self.disaster_ticks -= 1
            if self.disaster_ticks == 0:
                self.active_disaster = ""

        # Natural Earth Geophysics (Plate Tectonics, Volcanic Ash, Nile-Style River Floods & Lightning Wildfires)
        if not self.active_disaster and self.tick_count % 240 == 0 and self.rng.random() < 0.14:
            r_d = self.rng.random()
            if self.weather == "drought" and r_d < 0.45:
                self.active_disaster = "wildfire"
                self.disaster_xy = (self.rng.uniform(-45, 45), self.rng.uniform(70, 155))
                self.disaster_ticks = 65
            elif self.weather in ("rain", "storm") and r_d < 0.50:
                self.active_disaster = "river_flood"
                self.disaster_xy = (-12.0, self.rng.uniform(-120, 120))
                self.disaster_ticks = 75
                for ck in list(self.chunks.keys()):
                    self.soil_fertility[ck] = min(1.50, round(self.soil_fertility.get(ck, 1.0) + 0.18, 2))
            elif r_d < 0.78:
                self.active_disaster = "volcanic_eruption"
                self.disaster_xy = self.thermal_vents[0] if self.thermal_vents else (145.0, -115.0)
                self.disaster_ticks = 85
                self.solar_anomaly_c = max(-3.2, self.solar_anomaly_c - 1.4)  # Volcanic winter cooling!
                for ck in list(self.chunks.keys()):
                    self.soil_fertility[ck] = min(1.50, round(self.soil_fertility.get(ck, 1.0) + 0.22, 2))
            else:
                self.active_disaster = "earthquake"
                self.disaster_xy = (self.rng.uniform(-150, 150), self.rng.uniform(-130, 130))
                self.disaster_ticks = 35
                for st in self.structures.values():
                    if math.hypot(st.x - self.disaster_xy[0], st.y - self.disaster_xy[1]) < 45.0:
                        st.durability = max(20.0, st.durability - 35.0)
            self.newly_triggered_disaster = {
                "kind": self.active_disaster,
                "x": round(self.disaster_xy[0], 1),
                "y": round(self.disaster_xy[1], 1),
            }
        # Stochastic Weather & Solar Flux Evolution
        self.weather_ticks_left -= 1
        if self.weather_ticks_left <= 0:
            self.solar_anomaly_c = max(-2.2, min(2.4, round(self.solar_anomaly_c * 0.7 + self.rng.gauss(0.0, 0.65), 2)))
            s_idx = self.season_index
            r_w = self.rng.random()
            if s_idx == 3:  # Deep Winter
                self.weather = "snow" if r_w < 0.38 else ("storm" if r_w < 0.52 else ("fog" if r_w < 0.68 else "clear"))
            elif s_idx == 1:  # Summer (influenced by perihelion solar distance!)
                drought_p = 0.24 if self.solar_distance_au < 0.985 else 0.12
                self.weather = "drought" if r_w < drought_p else ("storm" if r_w < drought_p + 0.16 else ("rain" if r_w < drought_p + 0.36 else "clear"))
            else:  # Spring / Autumn
                self.weather = "rain" if r_w < 0.28 else ("fog" if r_w < 0.44 else ("storm" if r_w < 0.56 else "clear"))
            self.weather_ticks_left = self.rng.randint(75, 165)

        pollinator_pop = sum(1 for a in self.animals.values() if a.alive and a.species == "pollenwing")
        pollinator_factor = max(0.35, min(1.25, pollinator_pop / 5.0))
        weather_growth = 1.35 if self.weather == "rain" else (0.52 if self.weather in ("drought", "snow") else 1.0)

        if self.tick_count % 22 == 0 and self.chunks:
            chunk_keys = list(self.chunks.keys())
            base_trials = 22 if self.season_index != 3 else 9
            trials = max(4, int(round(base_trials * pollinator_factor * weather_growth)))
            for _ in range(trials):
                cx, cy = self.rng.choice(chunk_keys)
                tx = cx * CHUNK_SIZE + self.rng.randrange(0, CHUNK_SIZE)
                ty = cy * CHUNK_SIZE + self.rng.randrange(0, CHUNK_SIZE)
                biome = classify_biome(tx, ty, self.seed)
                if biome != "water" and self.rng.random() < min(1.0, self.soil_fertility.get((cx, cy), 1.0)):
                    self._seed_tile_resources(tx, ty, biome, self.rng, initial=False)
                # Lunar spring tides wash shells & nutrients onto riverbanks/shores!
                if biome == "riverbank" and abs(self.tidal_offset) > 0.11 and self.rng.random() < 0.22:
                    self._add_resource_at(tx, ty, "nacre_shell")

        # Subterranean Cave Mineral & Root Seepage + Rare Natural Storm Lightning Embers!
        if self.tick_count % 90 == 0:
            for cv in self.caves.values():
                if self.rng.random() < 0.35:
                    gx = int(round(cv.x + self.rng.uniform(-1.5, 1.5)))
                    gy = int(round(cv.y + self.rng.uniform(-1.5, 1.5)))
                    ore = self.rng.choice(("orb_root", "slab_dense", "nodule_red", "copper_ore", "tin_ore", "magnetite_ore"))
                    self._add_resource_at(gx, gy, ore)
            if self.weather == "storm" and len(self.structures) < 28 and self.chunks and self.rng.random() < 0.04:
                cx, cy = self.rng.choice(list(self.chunks.keys()))
                lx, ly = self.find_nearest_dry_spot(cx * CHUNK_SIZE + 8.0, cy * CHUNK_SIZE + 8.0)
                self._struct_seq += 1
                ember = WorldStructure(
                    id=f"S-{self._struct_seq}",
                    kind="hearth",
                    sensory_name="smoldering lightning-struck brush",
                    x=lx,
                    y=ly,
                    creator_id="NATURAL_LIGHTNING",
                    creator_lineage="Nature",
                    created_day=self.day,
                    durability=32.0,
                    fuel=38.0,
                )
                self.structures[ember.id] = ember

        # TRUE LOTKA-VOLTERRA TROPHIC WEB + DARWINIAN ALLOPATRIC SPECIATION!
        if self.tick_count % 220 == 0:
            by_species: Dict[str, List[WildAnimal]] = {}
            for a in self.animals.values():
                if a.alive:
                    by_species.setdefault(a.species, []).append(a)
            all_specs = {**FAUNA_CATALOG, **self.evolved_fauna}
            for sp, spec in list(all_specs.items()):
                living_sp = by_species.get(sp, [])
                if len(living_sp) == 0 and sp not in self.extinct_fauna:
                    self.extinct_fauna[sp] = self.day
                elif 2 <= len(living_sp) < spec["cap"] and self.rng.random() < 0.44:
                    p1, p2 = self.rng.sample(living_sp, 2)
                    if p1.energy < 42.0 or p2.energy < 42.0:
                        continue
                    p1.energy -= 14.0
                    p2.energy -= 14.0
                    zone = classify_climate_zone(p1.x, p1.y)
                    # Bergmann's & Allen's evolutionary pressure: larger in cold boreal, faster in open savanna
                    size_bias = 0.04 if zone == "boreal_highland" else (-0.02 if zone == "equatorial_savanna" else 0.0)
                    spd_bias = 0.04 if zone == "equatorial_savanna" else 0.0
                    child_size = round(max(0.55, min(1.65, (p1.size_gene + p2.size_gene) * 0.5 + self.rng.gauss(size_bias, 0.06))), 2)
                    child_spd = round(max(0.55, min(1.65, (p1.speed_gene + p2.speed_gene) * 0.5 + self.rng.gauss(spd_bias, 0.06))), 2)
                    child_gen = max(p1.generation, p2.generation) + 1
                    child_sp = sp
                    child_coat = p1.coat_color

                    # Allopatric Speciation when accumulated genetic divergence crosses threshold!
                    if (
                        sp in FAUNA_CATALOG
                        and child_gen >= 3
                        and (abs(child_size - 1.0) >= 0.22 or abs(child_spd - 1.0) >= 0.22)
                        and len(self.evolved_fauna) < 16
                    ):
                        prefix = "frost" if zone == "boreal_highland" else ("sun" if zone == "equatorial_savanna" else "emerald")
                        new_code = f"{prefix}_{sp}"
                        if new_code not in self.evolved_fauna and new_code not in FAUNA_CATALOG:
                            coat_palette = {"frost": "#bae6fd", "sun": "#fb923c", "emerald": "#4ade80"}[prefix]
                            new_spec = dict(spec)
                            new_spec["speed"] = round(spec["speed"] * child_spd, 2)
                            new_spec["hp"] = round(spec["hp"] * child_size, 1)
                            new_spec["cap"] = 6
                            new_spec["ancestor"] = sp
                            new_spec["born_day"] = self.day
                            new_spec["coat_color"] = coat_palette
                            new_spec["label"] = f"{prefix.capitalize()}-{sp.capitalize()} (Evolved Daughter Species!)"
                            self.evolved_fauna[new_code] = new_spec
                        if new_code in self.evolved_fauna:
                            child_sp = new_code
                            child_coat = self.evolved_fauna[new_code]["coat_color"]

                    self._animal_seq += 1
                    dom = spec["domain"]
                    if dom == "water":
                        ax, ay = self.find_nearest_water_spot(p1.x + self.rng.uniform(-4.0, 4.0), p1.y + self.rng.uniform(-4.0, 4.0))
                    elif dom == "air":
                        ax, ay = round(p1.x + self.rng.uniform(-5.0, 5.0), 2), round(p1.y + self.rng.uniform(-5.0, 5.0), 2)
                    else:
                        ax, ay = self.find_nearest_dry_spot(p1.x + self.rng.uniform(-4.0, 4.0), p1.y + self.rng.uniform(-4.0, 4.0))
                    self.animals[f"W-{self._animal_seq:03d}"] = WildAnimal(
                        id=f"W-{self._animal_seq:03d}",
                        species=child_sp,
                        x=ax,
                        y=ay,
                        energy=82.0,
                        health=round(spec["hp"] * child_size, 1),
                        generation=child_gen,
                        size_gene=child_size,
                        speed_gene=child_spd,
                        coat_color=child_coat,
                    )

        # Animal-on-Animal Trophic Chain (Carnivores hunt wild herbivores; herbivores graze flora!)
        if self.tick_count % 35 == 0:
            living_fauna = [a for a in self.animals.values() if a.alive]
            for an in living_fauna:
                spec = self.evolved_fauna.get(an.species) or FAUNA_CATALOG.get(an.species, FAUNA_CATALOG["lumigrazer"])
                an.energy = max(0.0, an.energy - 0.85)
                if an.energy <= 0.0:
                    an.alive = False  # Natural starvation if food web collapses!
                    continue
                if an.energy < 62.0:
                    hostility = spec.get("hostile", "none")
                    if hostility in ("night", "day", "always", "pack", "ambush"):
                        # Wild predator hunts wild prey within 18m (or scavenges wild small game in its biome!)
                        prey = next(
                            (
                                p for p in living_fauna
                                if p.alive and p.id != an.id
                                and (self.evolved_fauna.get(p.species) or FAUNA_CATALOG.get(p.species, {})).get("hostile") == "none"
                                and math.hypot(p.x - an.x, p.y - an.y) <= 18.0
                            ),
                            None,
                        )
                        if prey is not None:
                            prey.health -= 48.0
                            if prey.health <= 0:
                                prey.alive = False
                                an.energy = min(100.0, an.energy + 55.0)
                        elif self.rng.random() < 0.35:
                            an.energy = min(100.0, an.energy + 28.0)  # Wild small-game foraging prevents unrealistic starvation wipes!
                    else:
                        # Wild herbivore grazes local flora (or regenerates on lush grass)
                        gx, gy = int(round(an.x)), int(round(an.y))
                        items = self.resources.get((gx, gy), [])
                        plant = next((c for c in items if c in ("orb_sweet", "grain_seed", "orb_root")), None)
                        if plant:
                            self.remove_resource_at(gx, gy, plant)
                            an.energy = min(100.0, an.energy + 42.0)
                        elif classify_biome(gx, gy, self.seed) in ("meadow", "savanna", "forest", "water", "riverbank"):
                            an.energy = min(100.0, an.energy + 18.0)

        for animal in list(self.animals.values()):
            if not animal.alive:
                continue
            spec = self.evolved_fauna.get(animal.species) or FAUNA_CATALOG.get(animal.species, FAUNA_CATALOG["lumigrazer"])
            dom = spec["domain"]
            # Pollinators naturally fertilize meadow berries underneath them
            if animal.species == "pollenwing" and self.tick_count % 90 == 0 and self.rng.random() < 0.28:
                gx, gy = int(round(animal.x)), int(round(animal.y))
                if classify_biome(gx, gy, self.seed) in ("meadow", "riverbank"):
                    self._add_resource_at(gx, gy, "orb_sweet")

            if animal.target_xy is None or math.hypot(animal.target_xy[0] - animal.x, animal.target_xy[1] - animal.y) < 1.2:
                span = 14.0 if dom in ("air", "land") else 7.5
                nx = max(-245.0, min(245.0, animal.x + self.rng.uniform(-span, span)))
                ny = max(-245.0, min(245.0, animal.y + self.rng.uniform(-span, span)))
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
            elif st.kind == "crop_plot":
                st.crop_timer += 2 if self.weather == "rain" else 1
                if st.crop_timer >= 130:
                    st.crop_timer = 0
                    self._add_resource_at(int(round(st.x)), int(round(st.y)), "grain_seed")
            # Mobile Vehicles & Orbital Satellites move across their physical domain!
            if st.is_vehicle and st.vehicle_speed > 0.0:
                if st.vehicle_domain == "orbit":
                    ang = (self.tick_count * 0.035 + int(st.id.split("-")[1]) * 1.7) % (2.0 * math.pi)
                    st.x = round(math.cos(ang) * 155.0, 2)
                    st.y = round(math.sin(ang) * 155.0, 2)
                else:
                    if st.vehicle_target is None or math.hypot(st.vehicle_target[0] - st.x, st.vehicle_target[1] - st.y) < 1.5:
                        span = 26.0 if st.vehicle_domain == "air" else 16.0
                        tx = max(-245.0, min(245.0, st.x + self.rng.uniform(-span, span)))
                        ty = max(-245.0, min(245.0, st.y + self.rng.uniform(-span, span)))
                        if st.vehicle_domain == "water" and self.elevation_at(tx, ty) < -0.04:
                            st.vehicle_target = (tx, ty)
                        elif st.vehicle_domain == "air":
                            st.vehicle_target = (tx, ty)
                        elif st.vehicle_domain == "land" and self.is_walkable(tx, ty):
                            st.vehicle_target = (tx, ty)
                    if st.vehicle_target is not None:
                        dx, dy = st.vehicle_target[0] - st.x, st.vehicle_target[1] - st.y
                        dist = math.hypot(dx, dy)
                        if dist > 0.1:
                            nx = round(st.x + (dx / dist) * min(dist, st.vehicle_speed), 2)
                            ny = round(st.y + (dy / dist) * min(dist, st.vehicle_speed), 2)
                            if st.vehicle_domain == "water" and self.elevation_at(nx, ny) >= -0.02:
                                st.vehicle_target = None
                            elif st.vehicle_domain == "land" and not self.is_walkable(nx, ny):
                                st.vehicle_target = None
                            else:
                                st.x, st.y = nx, ny
            decay = 0.0002 if (st.kind in ("monolith", "cairn", "orbital_satellite") or st.tech_tier >= 3) else 0.004
            st.durability -= decay
            if st.durability <= 0:
                dead_ids.append(sid)
        for sid in dead_ids:
            del self.structures[sid]
        if len(self.structures) > 32:
            recyclable = [sid for sid, st in self.structures.items() if st.kind == "crop_plot" or (st.tech_tier <= 1 and st.kind not in ("monolith", "cairn"))]
            for sid in recyclable[: len(self.structures) - 32]:
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

        # 5B. Proto-Writing: Pressing a reed/bone stylus into soft kaolin clay -> permanent Clay Tablet!
        if "clay_gray" in (code_a, code_b) and ({code_a, code_b} & {"hollow_cane", "ivory_horn"}):
            lvl = insight_map.get("writing_lore", 0) + 1
            insight_map["writing_lore"] = lvl
            if lvl < 2:
                return (
                    None,
                    None,
                    "partial_insight",
                    "Pressed repeating geometric marks into soft clay with a pointed stylus.",
                )
            return (
                "clay_tablet",
                None,
                "breakthrough",
                "Incised repeating symbols into baked clay with a reed/bone stylus, inventing permanent proto-writing!",
            )

        has_adv_component = bool(
            {code_a, code_b} & {"composite_tool", "bronze_tool", "wheeled_cart", "silica_glass", "copper_coil", "refined_fuel"}
        )

        # 6. Masonry / Earthen Shelter
        if not has_adv_component and max_insul >= 0.72 and (max_hard >= 0.4 or max_mall >= 0.8) and {code_a, code_b} != {"rod_porous", "slab_dense"}:
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
        if not has_adv_component and max_mall >= 0.88 and (max_bind >= 0.75 or max_flam >= 0.7 or near_hearth):
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
        if not has_adv_component and max_luster >= 0.80 and (max_bind >= 0.75 or max_hard >= 0.78):
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

        # 9B. Defensive Timber Palisade Wall (Timber + Timber/Fiber — protects camp from predators!)
        if code_a == "rod_porous" and code_b in ("rod_porous", "fiber_dry", "resin_gold"):
            lvl = insight_map.get("palisade_lore", 0) + 1
            insight_map["palisade_lore"] = lvl
            if lvl < 2:
                return (
                    None,
                    None,
                    "partial_insight",
                    "Lashed upright hardwood stakes together into a sturdy defensive barrier test.",
                )
            self._struct_seq += 1
            sx, sy = self.find_nearest_dry_spot(x, y)
            st = WorldStructure(
                id=f"S-{self._struct_seq}",
                kind="palisade",
                sensory_name="fortified timber palisade wall",
                x=sx,
                y=sy,
                creator_id=actor_id,
                creator_lineage=actor_lineage,
                created_day=self.day,
                durability=320.0,
            )
            self.structures[st.id] = st
            return (
                None,
                st,
                "breakthrough",
                "Erected a fortified timber palisade wall protecting the settlement from dangerous beasts!",
            )

        # 10. Watercraft / River Bridge (Buoyant Timber + Fiber near River/Coast — unlocks ocean/river crossing!)
        near_water = any(
            self.elevation_at(x + dx, y + dy) < 0.0
            for dx in (-3.0, 0.0, 3.0)
            for dy in (-3.0, 0.0, 3.0)
        )
        if near_water and (
            {code_a, code_b} in ({"rod_porous", "fiber_dry"}, {"rod_porous", "resin_gold"})
        ):
            lvl = insight_map.get("naval_lore", 0) + 1
            insight_map["naval_lore"] = lvl
            if lvl >= 2:
                self._struct_seq += 1
                wx, wy = self.find_nearest_water_spot(x, y)
                bp = [
                    {"shape": "box", "sx": 1.6, "sy": 0.16, "sz": 1.1, "px": 0, "py": 0.08, "pz": 0, "color": "#92400e"},
                    {"shape": "cylinder", "sx": 0.06, "sy": 1.25, "sz": 0.06, "px": 0, "py": 0.7, "pz": 0, "color": "#78350f"},
                    {"shape": "box", "sx": 0.05, "sy": 0.75, "sz": 0.72, "px": 0.05, "py": 0.82, "pz": 0, "color": "#fde68a"},
                ]
                st = WorldStructure(
                    id=f"S-{self._struct_seq}",
                    kind="watercraft",
                    sensory_name="buoyant lashed-log sail raft",
                    x=wx,
                    y=wy,
                    creator_id=actor_id,
                    creator_lineage=actor_lineage,
                    created_day=self.day,
                    durability=420.0,
                    water_crossing=True,
                    tech_tier=2,
                    is_vehicle=True,
                    vehicle_speed=0.34,
                    vehicle_domain="water",
                    blueprint_3d=bp,
                )
                self.structures[st.id] = st
                return (
                    None,
                    st,
                    "breakthrough",
                    "Constructed a buoyant lashed-log watercraft capable of crossing rivers and seas!",
                )

        # 11. Wheeled Transport Cart (Hardwood Timber + Quarry Stone/Clay Disk)
        if {code_a, code_b} == {"rod_porous", "slab_dense"} and insight_map.get("build_lore", 0) >= 2:
            lvl = insight_map.get("wheel_lore", 0) + 1
            insight_map["wheel_lore"] = lvl
            if lvl >= 2:
                return (
                    "wheeled_cart",
                    None,
                    "breakthrough",
                    "Mounted carved stone disks onto a wooden axle, inventing the wheeled transport cart!",
                )

        # 12A. Subterranean Colony Excavation (Tool + Stone/Clay -> Underground Chamber & Tunnel Network!)
        if {code_a, code_b} & {"composite_tool", "bronze_tool"} and {code_a, code_b} & {"slab_dense", "clay_gray"}:
            lvl = insight_map.get("subterranean_lore", 0) + 1
            insight_map["subterranean_lore"] = lvl
            if lvl < 2:
                return (
                    None,
                    None,
                    "partial_insight",
                    "Chiseled into the dense subsoil; vaulted arches hold underground chambers without collapsing.",
                )
            existing_burrow = next(
                (s for s in self.structures.values() if s.kind == "burrow_network" and math.hypot(s.x - x, s.y - y) < 8.0),
                None,
            )
            if existing_burrow is not None:
                existing_burrow.chambers += 1
                existing_burrow.durability = min(900.0, existing_burrow.durability + 150.0)
                return (
                    None,
                    existing_burrow,
                    "breakthrough",
                    f"Expanded the subterranean tunnel colony into a {existing_burrow.chambers}-chamber underground network!",
                )
            self._struct_seq += 1
            sx, sy = self.find_nearest_dry_spot(x, y)
            st = WorldStructure(
                id=f"S-{self._struct_seq}",
                kind="burrow_network",
                sensory_name="excavated subterranean tunnel chamber",
                x=sx,
                y=sy,
                creator_id=actor_id,
                creator_lineage=actor_lineage,
                created_day=self.day,
                durability=650.0,
                layer="subterranean",
                tech_tier=2,
                chambers=2,
            )
            self.structures[st.id] = st
            return (
                None,
                st,
                "breakthrough",
                "Excavated a subterranean chamber & tunnel network sheltered beneath the earth!",
            )

        # 12B. High-Temperature Silica Glass, Electromagnetic Coils, Energetic Propellant & Emergent Medicine!
        if "medicinal_herb" in (code_a, code_b) and ({code_a, code_b} & {"orb_sweet", "fiber_dry", "clay_gray"}):
            lvl = insight_map.get("medical_lore", 0) + 1
            insight_map["medical_lore"] = lvl
            if lvl >= 1:
                return ("herbal_remedy", None, "breakthrough", "Steeped soothing leaves into a restorative herbal poultice!")
        if "herbal_remedy" in (code_a, code_b) and ({code_a, code_b} & {"resin_gold", "copper_ore", "nodule_red"}):
            lvl = insight_map.get("medical_lore", 0) + 1
            insight_map["medical_lore"] = lvl
            if lvl >= 2:
                return ("antiseptic_balm", None, "breakthrough", "Compounded herbal pulp with antimicrobial resin/mineral into an antiseptic balm!")
        if "antiseptic_balm" in (code_a, code_b) and "silica_glass" in (code_a, code_b):
            lvl = insight_map.get("medical_lore", 0) + 1
            insight_map["medical_lore"] = lvl
            if lvl >= 3:
                return ("clinical_cure", None, "breakthrough", "Purified and sealed a clinical-grade therapeutic serum in glass!")

        if near_hearth and {code_a, code_b} == {"shard_translucent", "clay_gray"}:
            lvl = insight_map.get("glass_lore", 0) + 1
            insight_map["glass_lore"] = lvl
            if lvl >= 2:
                return ("silica_glass", None, "breakthrough", "Fused siliceous stone and clay at high heat into clear silica glass & lenses!")
        if ({code_a, code_b} & {"copper_ore", "bronze_tool"}) and ({code_a, code_b} & {"magnetite_ore", "compass_stone"}) and insight_map.get("bronze_lore", 0) >= 1:
            lvl = insight_map.get("electromag_lore", 0) + 1
            insight_map["electromag_lore"] = lvl
            if lvl >= 2:
                return ("copper_coil", None, "breakthrough", "Wound conductive copper around magnetic lodestone, discovering electromagnetic induction!")
        if near_hearth and "resin_gold" in (code_a, code_b) and ({code_a, code_b} & {"fossil_amber", "nodule_red"}):
            lvl = insight_map.get("fuel_lore", 0) + 1
            insight_map["fuel_lore"] = lvl
            if lvl >= 2:
                return ("refined_fuel", None, "breakthrough", "Distilled resinous hydrocarbons into a high-energy liquid propellant!")

        # 12C. Multi-Story Architectural Edifice (Stone + Glass/Bronze/Clay at high masonry mastery)
        if "slab_dense" in (code_a, code_b) and ({code_a, code_b} & {"silica_glass", "bronze_tool"}) and insight_map.get("build_lore", 0) >= 2:
            self._struct_seq += 1
            sx, sy = self.find_nearest_dry_spot(x, y)
            floors = min(6, 2 + insight_map.get("build_lore", 2) // 2)
            st = WorldStructure(
                id=f"S-{self._struct_seq}",
                kind="edifice",
                sensory_name=f"{floors}-level stone-and-glass edifice",
                x=sx,
                y=sy,
                creator_id=actor_id,
                creator_lineage=actor_lineage,
                created_day=self.day,
                durability=820.0,
                tech_tier=3,
                stories=floors,
            )
            self.structures[st.id] = st
            return (None, st, "breakthrough", f"Erected a {floors}-story architectural edifice!")

        # 12D. Long-Range Communication Media (Acoustic Horn/Drum 42m -> Electromagnetic Relay Tower 240m!)
        if {code_a, code_b} == {"ivory_horn", "fiber_dry"} or ("copper_coil" in (code_a, code_b) and ({code_a, code_b} & {"silica_glass", "compass_stone", "rod_porous"})):
            is_em = "copper_coil" in (code_a, code_b)
            self._struct_seq += 1
            sx, sy = self.find_nearest_dry_spot(x, y)
            st = WorldStructure(
                id=f"S-{self._struct_seq}",
                kind="comm_relay",
                sensory_name="tall humming signal spire" if is_em else "hollow resonant signal drum-horn",
                x=sx,
                y=sy,
                creator_id=actor_id,
                creator_lineage=actor_lineage,
                created_day=self.day,
                durability=700.0,
                tech_tier=4 if is_em else 2,
                signal_range=240.0 if is_em else 42.0,
            )
            self.structures[st.id] = st
            return (
                None,
                st,
                "breakthrough",
                "Constructed an electromagnetic wireless communication spire!" if is_em else "Built a long-range acoustic resonance drum-horn!",
            )

        # 12E. Autonomous Land Vehicles, Aerial Craft & Planetary Orbital Satellites!
        if "wheeled_cart" in (code_a, code_b) and ({code_a, code_b} & {"bronze_tool", "refined_fuel"}):
            self._struct_seq += 1
            sx, sy = self.find_nearest_dry_spot(x, y)
            st = WorldStructure(
                id=f"S-{self._struct_seq}",
                kind="land_vehicle",
                sensory_name="self-propelled wheeled chassis",
                x=sx,
                y=sy,
                creator_id=actor_id,
                creator_lineage=actor_lineage,
                created_day=self.day,
                durability=680.0,
                tech_tier=4,
                is_vehicle=True,
                vehicle_speed=0.55,
                vehicle_domain="land",
            )
            self.structures[st.id] = st
            return (None, st, "breakthrough", "Engineered a mobile land vehicle capable of rapid continental travel!")

        if {code_a, code_b} == {"warm_cloak", "refined_fuel"}:
            self._struct_seq += 1
            sx, sy = self.find_nearest_dry_spot(x, y)
            st = WorldStructure(
                id=f"S-{self._struct_seq}",
                kind="air_craft",
                sensory_name="buoyant thermal sky-vessel",
                x=sx,
                y=sy,
                creator_id=actor_id,
                creator_lineage=actor_lineage,
                created_day=self.day,
                durability=640.0,
                layer="aerial",
                tech_tier=4,
                is_vehicle=True,
                vehicle_speed=0.72,
                vehicle_domain="air",
            )
            self.structures[st.id] = st
            return (None, st, "breakthrough", "Launched a buoyant aerial vessel capable of flying across oceans and mountains!")

        total_mastery = sum(insight_map.values())
        if {code_a, code_b} == {"copper_coil", "refined_fuel"} and total_mastery >= 8:
            self._struct_seq += 1
            st = WorldStructure(
                id=f"S-{self._struct_seq}",
                kind="orbital_satellite",
                sensory_name="high-altitude orbiting star-beacon",
                x=0.0,
                y=46.0,
                creator_id=actor_id,
                creator_lineage=actor_lineage,
                created_day=self.day,
                durability=9999.0,
                layer="orbital",
                tech_tier=5,
                is_vehicle=True,
                vehicle_speed=0.95,
                vehicle_domain="orbit",
                signal_range=500.0,
            )
            self.structures[st.id] = st
            return (None, st, "breakthrough", "SPACEFLIGHT ACHIEVED! Launched an autonomous orbital satellite around the planet!")

        # 13. Open-Ended Generative Creation Engine (Unbounded Physical Synthesis -> Real 3D Procedural Structure!)
        if total_mastery >= 4 and (mat_a.hardness + mat_b.hardness + mat_a.malleability + mat_b.bindability) >= 1.1:
            pair_key = f"open_{min(code_a, code_b)}_{max(code_a, code_b)}"
            lvl = insight_map.get(pair_key, 0) + 1
            insight_map[pair_key] = lvl
            if lvl < 2:
                return (
                    None,
                    None,
                    "partial_insight",
                    f"Tested physical resonance of {mat_a.sensory_name} with {mat_b.sensory_name}; structure taking form.",
                )
            self._struct_seq += 1
            sx, sy = self.find_nearest_dry_spot(x, y)
            tall = 0.7 + (mat_a.hardness + mat_b.hardness) * 0.65
            arch_shape = "cone" if (mat_a.luster + mat_b.luster) > 0.7 else ("cylinder" if mat_a.metallic > 0.5 else "box")
            bp = [
                {"shape": "cylinder", "sx": 0.62, "sy": 0.22, "sz": 0.62, "px": 0, "py": 0.11, "pz": 0, "color": mat_a.color_hex},
                {"shape": arch_shape, "sx": 0.36, "sy": round(tall, 2), "sz": 0.36, "px": 0, "py": round(0.22 + tall * 0.5, 2), "pz": 0, "color": mat_b.color_hex},
            ]
            if max(mat_a.luster, mat_b.luster, mat_a.metallic, mat_b.metallic) >= 0.8:
                bp.append({"shape": "torus", "sx": 0.34, "sy": 0.06, "sz": 0.34, "px": 0, "py": round(0.28 + tall, 2), "pz": 0, "color": "#fde047"})
            dyn_sig = 85.0 if (mat_a.magnetic + mat_b.magnetic) >= 0.9 and (mat_a.metallic + mat_b.metallic) >= 0.9 else 0.0
            dyn_veh = (mat_a.flammability + mat_b.flammability) >= 1.5 and (mat_a.hardness + mat_b.hardness) >= 0.8
            st = WorldStructure(
                id=f"S-{self._struct_seq}",
                kind="open_creation",
                sensory_name=f"novel {mat_a.sensory_name} & {mat_b.sensory_name} apparatus",
                x=sx,
                y=sy,
                creator_id=actor_id,
                creator_lineage=actor_lineage,
                created_day=self.day,
                durability=550.0,
                tech_tier=min(5, 2 + total_mastery // 5),
                is_vehicle=dyn_veh,
                vehicle_speed=0.42 if dyn_veh else 0.0,
                signal_range=dyn_sig,
                stories=max(1, int(round(tall))),
                blueprint_3d=bp,
            )
            self.structures[st.id] = st
            return (
                None,
                st,
                "breakthrough",
                f"OPEN-ENDED INVENTION! {actor_id} synthesized {mat_a.observer_label} + {mat_b.observer_label} into a novel 3D apparatus!",
            )

        return None, None, "inert", "Examined both terrestrial materials without reaction."
