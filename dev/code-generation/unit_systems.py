"""
Source of truth for displaying recipe quantities in a preferred unit system.

Every number here is resolved through Pint. The only hand-authored content is `SELECTION`:
which of Pint's units are kitchen units, and how many of each are needed before it takes over.
Ordering, base factors, dimensions, and the fraction flag are all derived.

This is build-time tooling, not application code. `gen_ts_unit_systems.py` emits the table
below to TypeScript so the client can render conversions without duplicating any factors; the
backend never evaluates it. If conversions ever need to happen server-side, this module moves
into `mealie/services/` and gains a caller — until then it stays out of the shipped package.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, Any

from mealie.schema.recipe.recipe_ingredient import StandardizedUnitType

if TYPE_CHECKING:
    from pint import UnitRegistry


class UnitDimension(StrEnum):
    MASS = "mass"
    VOLUME = "volume"


class UnitSystem(StrEnum):
    METRIC = "metric"
    US = "us"


#: The unit each dimension is measured in. This asserts nothing about Pint: Pint decides which
#: units share a dimension, and `dimension_of` asks it by comparing dimensionalities against
#: these. All this does is name the two dimensions we display and fix the scale of the emitted
#: numbers, so the generated table reads in grams and millilitres rather than Pint's own base
#: units of kilograms and cubic metres (where a cup is 2.4e-4).
BASE_UNITS: dict[UnitDimension, str] = {
    UnitDimension.MASS: "gram",
    UnitDimension.VOLUME: "milliliter",
}

#: Pint systems whose members are customary rather than metric, used to derive the fraction
#: flag. Both are listed because that is what "customary" means, not because both are offered
#: as ladders -- `ounce` and `pound` belong to either one.
#:
#: Naming them is unavoidable. Pint's `SI` system is just its root group -- 417 members,
#: including `cup`, `ounce` and `pound` -- so customary cannot be derived as the complement of
#: metric. These are Pint's own identifiers, and `get_system` raises on an unknown name, so a
#: typo fails the build rather than silently emitting a wrong table.
#:
#: There is no metric entry: metric kitchen units are generated from SI prefixes rather than
#: being members of any group, so `mks` holds `liter` but neither `milliliter` nor `kilogram`.
CUSTOMARY_PINT_SYSTEMS: tuple[str, ...] = ("US", "imperial")

#: The only hand-authored policy in this module: for each system and dimension, which Pint
#: units may be displayed, and the takeover multiple for each — how many whole units are
#: needed before it takes over from the rung below. 1.0 is the norm; cups take over at a
#: quarter cup, which is how US recipes are written.
#:
#: Order is not authored; rungs are sorted by magnitude, which Pint supplies.
#:
#: There is deliberately no imperial ladder. It would share `ounce` and `pound` with `us` — pint
#: puts both in either system — so it would only differ on volume, and essentially nobody cooks
#: in imperial: the UK weighs in grams, Australia and New Zealand are metric, and Canada follows
#: US customary. If a third ladder is ever wanted, metric-with-cups for AU/NZ is the likelier ask.
SELECTION: dict[tuple[UnitSystem, UnitDimension], dict[str, float]] = {
    (UnitSystem.METRIC, UnitDimension.MASS): {"gram": 1.0, "kilogram": 1.0},
    (UnitSystem.METRIC, UnitDimension.VOLUME): {"milliliter": 1.0, "liter": 1.0},
    (UnitSystem.US, UnitDimension.MASS): {"ounce": 1.0, "pound": 1.0},
    (UnitSystem.US, UnitDimension.VOLUME): {
        "teaspoon": 1.0,
        "tablespoon": 1.0,
        "cup": 0.25,
        "quart": 1.0,
        "gallon": 1.0,
    },
}


#: Display names are not authored here. They come from the ingredient unit seed data, which is
#: already translated into every locale Mealie ships and is managed in Crowdin. The frontend
#: loads the same files, so this only has to emit the key to look up.
SEED_UNITS_FILE = (
    Path(__file__).parents[2] / "mealie" / "repos" / "seed" / "resources" / "units" / "locales" / "en-US.json"
)


@dataclass(frozen=True)
class Rung:
    """A display unit, and the point at which it takes over from the rung below it."""

    unit: str
    """The Pint unit name. Doubles as the i18n key for the unit's display names."""

    base: float
    """How many base units (see `BASE_UNITS`) are in one of this unit."""

    takeover: float
    """Whole units needed before this rung takes over. Hand-authored; everything else is not."""

    fraction: bool
    """Whether to render as a fraction rather than a decimal."""

    seed_key: str
    """Key into the ingredient unit seed data, where this rung's translated names live."""


class UnitNotSupported(Exception):
    """Raised when a unit has no dimension we can display."""


@cache
def _registry() -> UnitRegistry:
    from pint import UnitRegistry

    return UnitRegistry()


@cache
def _customary_units() -> frozenset[str]:
    """Every unit belonging to a Pint system we treat as customary rather than metric.

    Used to decide whether a rung renders as a fraction. Derived rather than authored, so a
    metric rung sitting inside a customary ladder would correctly stay decimal.
    """

    registry = _registry()
    members: set[str] = set()
    for pint_system in CUSTOMARY_PINT_SYSTEMS:
        members |= set(registry.get_system(pint_system, create_if_needed=False).members)

    return frozenset(members)


def dimension_of(unit: str) -> UnitDimension:
    """The dimension of a Pint unit, or raise if it isn't one we can display.

    Pint answers this, by comparing the unit's dimensionality against each dimension's
    reference unit. Nothing here spells out what a mass or a volume is.
    """

    registry = _registry()
    try:
        dimensionality = registry(unit).dimensionality
    except Exception as e:
        raise UnitNotSupported(f"Unit '{unit}' not found in unit registry") from e

    for dimension, reference in BASE_UNITS.items():
        if dimensionality == registry(reference).dimensionality:
            return dimension

    raise UnitNotSupported(f"Unit '{unit}' has unsupported dimensionality '{dimensionality}'")


def base_factor(unit: str) -> tuple[UnitDimension, float]:
    """How many base units are in one of `unit`, alongside the dimension those are in.

    The dimension is read off the unit itself and the base chosen to match, so this can never
    convert across dimensions. Do not reimplement this in terms of `UnitConverter.convert`:
    that applies `_resolve_ounce`, which would silently read the mass unit `ounce` as
    `fluid_ounce` whenever the target is a volume, putting it on the volume ladder at 29.57 ml.
    """

    dimension = dimension_of(unit)
    registry = _registry()
    quantity = registry(unit).to(BASE_UNITS[dimension])
    return dimension, float(quantity.magnitude)


@cache
def _seed_unit_keys() -> frozenset[str]:
    """The keys available in the ingredient unit seed data."""

    with open(SEED_UNITS_FILE) as f:
        return frozenset(json.load(f))


def seed_key_for(unit: str) -> str:
    """The seed data key holding this unit's translated display names.

    Currently always the pint unit name, but kept distinct because it is a translation key
    rather than a physics identifier. The two diverge as soon as a ladder uses a qualified pint
    unit — `imperial_pint` would display under the seed data's unqualified `pint`.
    """

    if unit not in _seed_unit_keys():
        raise UnitNotSupported(f"Unit '{unit}' has no seed data, so it has no translated names")

    return unit


def rungs_for(system: UnitSystem, dimension: UnitDimension) -> list[Rung]:
    """The display ladder for a system and dimension, ordered smallest to largest."""

    customary = _customary_units()
    rungs = []
    for unit, takeover in SELECTION[(system, dimension)].items():
        unit_dimension, base = base_factor(unit)
        if unit_dimension != dimension:
            raise UnitNotSupported(f"Unit '{unit}' is {unit_dimension}, but was selected for {dimension}")

        rungs.append(
            Rung(
                unit=unit,
                base=base,
                takeover=takeover,
                fraction=unit in customary,
                seed_key=seed_key_for(unit),
            )
        )

    rungs.sort(key=lambda rung: rung.base)
    return rungs


def build_table() -> dict[str, Any]:
    """Resolve everything through Pint into a JSON-able table for the frontend.

    `units` maps each standardized unit an ingredient may be stored in to its dimension and
    base factor, which is what lets the client compute an ingredient's base magnitude.
    `systems` holds the display ladders.
    """

    units: dict[str, Any] = {}
    for standardized_unit in StandardizedUnitType:
        dimension, base = base_factor(standardized_unit.value)
        units[standardized_unit.value] = {"dimension": dimension.value, "base": base}

    systems: dict[str, Any] = {}
    for system in UnitSystem:
        systems[system.value] = {
            dimension.value: [asdict(rung) for rung in rungs_for(system, dimension)] for dimension in UnitDimension
        }

    return {"units": units, "systems": systems}
