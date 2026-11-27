"""Thin orchestration layer over model.py.

Nothing here reimplements a formula: everything is delegated to
`model.simulate` so the interface can never drift from the tested engine.
This module only adds what the interface needs: a scenario comparison grid
and the "green" reading of the result.
"""
from dataclasses import replace

from model import Inputs, simulate


def build_inputs(s: dict) -> Inputs:
    """Turn a flat dict of form values into the engine's Inputs."""
    return Inputs(
        principal=s["principal"],
        annual_interest=s["interest"],
        years=s["years"],
        rate=s["rate"],
        annual_cfads=s["cfads"],
        depreciation=s["shock"],
        coverage=s["coverage"],
        forward_rate=s["forward"],
        annual_cost_rate=s["cost"],
    )


def summary(x: Inputs) -> dict:
    """Headline figures for one simulation, read off the engine's own rows."""
    rows = simulate(x)
    first = rows[0]

    dscr_hedged = [r["DSCR avec couverture"] for r in rows]
    dscr_unhedged = [r["DSCR sans couverture"] for r in rows]
    service_unhedged = sum(r["Service sans couverture (local)"] for r in rows)
    service_hedged = sum(r["Service avec couverture (local)"] for r in rows)
    total_cost = sum(r["Coût couverture (local)"] for r in rows)

    return {
        "rows": rows,
        "rate_stressed": first["Taux scénario"],
        "rate_spot": x.rate,
        "dscr_min_hedged": min(dscr_hedged),
        "dscr_min_unhedged": min(dscr_unhedged),
        "dscr_year1_hedged": dscr_hedged[0],
        "dscr_year1_unhedged": dscr_unhedged[0],
        "service_unhedged": service_unhedged,
        "service_hedged": service_hedged,
        "extra_local": service_unhedged - _no_shock_service(x),
        "hedge_cost": total_cost,
        "hedge_saving": service_unhedged - service_hedged,
        "total_service_foreign": sum(r["Service dette (devise)"] for r in rows),
    }


def _no_shock_service(x: Inputs) -> float:
    """Service in local currency with no shock: the reference the user compares to."""
    rows = simulate(replace(x, depreciation=0.0, coverage=0.0, annual_cost_rate=0.0))
    return sum(r["Service sans couverture (local)"] for r in rows)


def green_metrics(x: Inputs, co2e_per_year: float, result: dict) -> dict:
    """Read the same result through a carbon lens.

    Deliberately narrow: it says what a tonne of avoided CO2e costs in debt
    service terms, and what an unhedged depreciation episode would add per
    tonne. It does not claim any causal or "green" effect of hedging.
    """
    years = max(x.years, 1)
    total_co2e = co2e_per_year * years
    return {
        "co2e_per_year": co2e_per_year,
        "total_co2e": total_co2e,
        "service_per_tco2e": result["service_unhedged"] / total_co2e if total_co2e else None,
        "shock_cost_per_tco2e": (
            result["extra_local"] / total_co2e if total_co2e else None
        ),
        "hedge_saving_per_tco2e": (
            max(result["hedge_saving"], 0.0) / total_co2e if total_co2e else None
        ),
        "hedge_cost_per_tco2e": (
            result["hedge_cost"] / total_co2e if total_co2e else None
        ),
    }


def comparison_grid(x: Inputs, shocks: list[float], coverages: list[float]) -> dict:
    """DSCR-minimum matrix: rows = shock, columns = coverage.

    Small by design (5 x 4 = 20 engine calls) so the page stays instant and
    the whole grid fits on one screen.
    """
    cells = []
    for shock in shocks:
        row = []
        for coverage in coverages:
            rows = simulate(replace(x, depreciation=shock, coverage=coverage))
            row.append(min(r["DSCR avec couverture"] for r in rows))
        cells.append({"shock": shock, "cells": row})
    return {"shocks": shocks, "coverages": coverages, "rows": cells}


def break_even_coverage(x: Inputs, threshold: float, step: float = 0.05) -> float | None:
    """Smallest coverage ratio that keeps the minimum DSCR at or above threshold."""
    c = 0.0
    while c <= 1.0 + 1e-9:
        rows = simulate(replace(x, coverage=min(c, 1.0)))
        if min(r["DSCR avec couverture"] for r in rows) >= threshold:
            return min(c, 1.0)
        c += step
    return None
