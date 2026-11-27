"""Hedge managers, in the ShockDesk sense: a named strategy is a Python file.

Each manager answers one question — *given my exposure and this risk view, what
fraction of the debt service should be locked in, and why?* — and returns a
trace so the page shows the reasoning instead of a magic number.

Managers never touch the loan arithmetic: the engine passes them a
``dscr_with(coverage)`` callable, so a manager can be read, tested and replaced
in isolation.

The published managers are deliberately simple: a student, a jury member, or a
treasurer should be able to audit any of them in a minute. None of them is a
recommendation — a manager is a scenario of behaviour.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .market import Rate


@dataclass
class HedgeView:
    """What a manager is allowed to see. No future knowledge, by construction."""

    years: int
    capacity: float                 # max share hedgeable, 0..1
    shock: float                    # the scenario being played, 0..1
    spot: Rate                      # local per foreign, with its provenance
    forward: float                  # user- or scenario-supplied hedged rate
    annual_cost_rate: float         # cost per year on the hedged share
    dscr_threshold: float
    dscr_with: Callable[[float], float]   # (coverage) -> minimum DSCR over the loan


@dataclass
class Proposal:
    coverage: float
    rationale: str
    trace: list[tuple[str, str]]


class Manager:
    key = "base"
    name = "Base manager"
    tagline = ""
    family = "custom"
    file = ""

    def propose(self, v: HedgeView) -> Proposal:  # pragma: no cover - interface
        raise NotImplementedError

    def as_dict(self) -> dict:
        return {"key": self.key, "name": self.name, "tagline": self.tagline,
                "family": self.family, "file": self.file}


class NoHedge(Manager):
    key = "none"
    name = "No hedge (reference)"
    tagline = "Bear the exposure in full: the counterfactual every other manager is judged against."
    family = "reference"
    file = "managers/no-hedge.py"

    def propose(self, v: HedgeView) -> Proposal:
        return Proposal(0.0, "Exposure left open by construction: this is the baseline.",
                        [("coverage", "0 %"), ("cost", "0")])


class FullHedge(Manager):
    key = "full"
    name = "Full hedge"
    tagline = "Lock the whole schedule: removes the shock and the flexibility at once."
    family = "static"
    file = "managers/full-hedge.py"

    def propose(self, v: HedgeView) -> Proposal:
        share = min(1.0, v.capacity)
        return Proposal(share, "Everything is locked: maximum certainty, maximum committed cost.",
                        [("coverage", f"{share:.0%}"),
                         ("cost", f"{share * v.annual_cost_rate:.2%}/yr")])


class ThresholdSeeker(Manager):
    key = "threshold"
    name = "Covenant threshold seeker"
    tagline = "Smallest hedge that holds your minimum DSCR: the cheapest protection that works."
    family = "optimiser"
    file = "managers/threshold-seeker.py"

    def propose(self, v: HedgeView) -> Proposal:
        c = 0.0
        while c <= v.capacity + 1e-9:
            if v.dscr_with(c) >= v.dscr_threshold:
                return Proposal(
                    c,
                    f"At a {v.shock:.0%} shock, {c:.0%} is the first step that holds "
                    f"{v.dscr_threshold:.2f}x, so it is the least cost that clears the covenant.",
                    [("shock played", f"{v.shock:.0%}"),
                     ("first passing step", f"{c:.0%}"),
                     ("cost", f"{c * v.annual_cost_rate:.2%}/yr")],
                )
            c = round(c + 0.05, 2)
        return Proposal(
            v.capacity,
            "No step inside the hedgeable capacity holds the covenant: the project fails even fully "
            "hedged at the supplied hedged rate. The binding constraint is not the hedge.",
            [("shock played", f"{v.shock:.0%}"), ("capacity used", f"{v.capacity:.0%}")],
        )


class EqualSlice(Manager):
    key = "slice"
    name = "Equal slices ladder"
    tagline = "Cover progressively more of the schedule: a classic layering ladder."
    family = "ladder"
    file = "managers/equal-slices.py"

    def propose(self, v: HedgeView) -> Proposal:
        share = round(min(v.capacity, 0.6), 2)
        return Proposal(
            share,
            "A ladder of five equal slices covers the front, most expensive years first and leaves "
            "the back of the schedule flexible.",
            [("target share", f"{share:.0%}"), ("layers", "5"),
             ("cost", f"{share * v.annual_cost_rate:.2%}/yr")],
        )


class CarryAware(Manager):
    key = "carry"
    name = "Carry-aware manager"
    tagline = "If the hedged rate already embeds the shock, hedging buys nothing: it is a transfer."
    family = "tactical"
    file = "managers/carry-aware.py"

    def propose(self, v: HedgeView) -> Proposal:
        if not v.forward or not v.spot.value:
            return Proposal(0.0, "No hedged rate supplied: nothing can be compared, so nothing is bought.",
                            [("forward", "n/a")])
        carry = v.forward / v.spot.value - 1
        if carry >= v.shock * 0.8:
            return Proposal(
                0.0,
                "The hedged rate already embeds most of the simulated depreciation: paying the carry "
                "would buy protection you are unlikely to need.",
                [("implied carry", f"{carry:.1%}"), ("shock played", f"{v.shock:.0%}"),
                 ("verdict", "carry ≥ 80 % of shock")],
            )
        share = round(min(v.capacity, 0.5), 2)
        return Proposal(
            share,
            "The forward is flat to spot relative to the simulated shock, so cover is cheap in "
            "expectation and half the schedule is locked.",
            [("implied carry", f"{carry:.1%}"), ("shock played", f"{v.shock:.0%}"),
             ("verdict", "carry below the shock")],
        )


MANAGERS: dict[str, Manager] = {
    m.key: m for m in (NoHedge(), ThresholdSeeker(), EqualSlice(), CarryAware(), FullHedge())
}

DEFAULT_MANAGER = "threshold"


def get(key: str) -> Manager:
    return MANAGERS.get(key, MANAGERS[DEFAULT_MANAGER])


def all_managers() -> list[Manager]:
    return list(MANAGERS.values())
