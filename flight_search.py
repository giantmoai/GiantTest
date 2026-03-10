from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from itertools import product
from typing import Iterable, List, Sequence
from urllib.parse import urlencode


BASE_URL = "https://www.skyscanner.com/transport/flights"


@dataclass(frozen=True)
class SegmentPreference:
    """Single flight segment preferences.

    - origins/destinations accept multiple airport IATA codes.
    - date range supports flexible departure window.
    - via_airports are mandatory transit airports in preferred order.
    - allow_exit_transit controls whether user accepts leave-airport stopovers.
    """

    origins: Sequence[str]
    destinations: Sequence[str]
    depart_from: date
    depart_to: date
    via_airports: Sequence[str] = ()
    allow_exit_transit: bool = False

    def validate(self) -> None:
        if not self.origins:
            raise ValueError("origins must not be empty")
        if not self.destinations:
            raise ValueError("destinations must not be empty")
        if self.depart_from > self.depart_to:
            raise ValueError("depart_from must be <= depart_to")


@dataclass(frozen=True)
class SearchConfig:
    segments: Sequence[SegmentPreference]
    max_queries: int = 200

    def validate(self) -> None:
        if not self.segments:
            raise ValueError("at least one segment is required")
        if len(self.segments) > 4:
            raise ValueError("Skyscanner multi-city planner supports up to 4 segments in this tool")
        for seg in self.segments:
            seg.validate()
        if self.max_queries <= 0:
            raise ValueError("max_queries must be positive")


@dataclass(frozen=True)
class ConcreteLeg:
    origin: str
    destination: str
    depart_date: date
    via_airports: Sequence[str]
    allow_exit_transit: bool


@dataclass(frozen=True)
class ConcreteQuery:
    legs: Sequence[ConcreteLeg]

    def to_skyscanner_url(self) -> str:
        """Build a Skyscanner deeplink-style URL with human-readable constraints.

        Notes:
        - Skyscanner does not provide a stable public URL contract for all advanced
          constraints. We encode essentials in query params for convenience.
        - Mandatory via-airport and allow_exit_transit should be post-filter logic
          when reviewing search results.
        """

        path = "/".join(
            f"{leg.origin.lower()}/{leg.destination.lower()}/{leg.depart_date.isoformat()}"
            for leg in self.legs
        )
        via_text = [",".join(leg.via_airports) for leg in self.legs if leg.via_airports]
        params = {
            "adults": 1,
            "cabinclass": "economy",
            "allowExitTransit": "1" if all(leg.allow_exit_transit for leg in self.legs) else "0",
        }
        if via_text:
            params["mustVia"] = "|".join(via_text)
        return f"{BASE_URL}/{path}?{urlencode(params)}"


def _date_range(start: date, end: date) -> Iterable[date]:
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)


def generate_queries(config: SearchConfig) -> List[ConcreteQuery]:
    """Generate concrete multi-segment candidate searches.

    This expands:
    - origin multi-select
    - destination multi-select
    - date window

    Use max_queries to cap explosion.
    """

    config.validate()

    per_segment_options: List[List[ConcreteLeg]] = []
    for seg in config.segments:
        options: List[ConcreteLeg] = []
        for origin, destination, depart in product(
            seg.origins,
            seg.destinations,
            _date_range(seg.depart_from, seg.depart_to),
        ):
            options.append(
                ConcreteLeg(
                    origin=origin.upper(),
                    destination=destination.upper(),
                    depart_date=depart,
                    via_airports=tuple(code.upper() for code in seg.via_airports),
                    allow_exit_transit=seg.allow_exit_transit,
                )
            )
        per_segment_options.append(options)

    generated: List[ConcreteQuery] = []
    for candidate in product(*per_segment_options):
        generated.append(ConcreteQuery(legs=candidate))
        if len(generated) >= config.max_queries:
            break

    return generated


def explain_usage() -> str:
    return (
        "Skyscanner 便宜機票搜尋建議：\n"
        "1) 每段可設定多個出發/抵達機場與日期範圍。\n"
        "2) 多段行程最多 4 段。\n"
        "3) 每段可指定必經機場（via_airports），請在結果中人工或程式後過濾。\n"
        "4) allow_exit_transit 可標記是否接受中途出關停留。\n"
    )
