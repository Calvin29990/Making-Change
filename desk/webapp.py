"""Making Change — exploratory FX stress desk.

A deliberately small Flask site. The point is comprehension, not features:
one page explains the mechanism in four steps, and every result is a URL
the reader can replay, cite, or argue with.

No market data, no execution, no advice. See README.md and
docs/METHODOLOGIE.md for the limits, and UTILISATION-IA.md for AI traceability.
"""
import os

from flask import Flask, Response, redirect, render_template, request, url_for

from . import scenarios as sc
from .engine import (
    break_even_coverage,
    build_inputs,
    comparison_grid,
    green_metrics,
    summary,
)

app = Flask(__name__)

DEFAULTS = {
    "scenario": sc.DEFAULT_SCENARIO,
    "shock": None,
    "coverage": None,
    "forward": None,
    "cost": None,
    "threshold": 1.20,
    "co2e": None,
}


def _num(args, name, fallback, lo, hi):
    """Read a float from the query string, clamped — the URL is user input."""
    try:
        v = float(args.get(name, ""))
    except (TypeError, ValueError):
        return fallback
    return max(lo, min(hi, v))


def read_params(args) -> dict:
    """All state lives in the URL: same URL, same numbers, no session."""
    key = args.get("scenario", DEFAULTS["scenario"])
    if key not in sc.SCENARIOS:
        key = DEFAULTS["scenario"]
    s = sc.get(key)

    return {
        "scenario_key": key,
        "scenario": s,
        "shock": _num(args, "shock", s.depreciation, 0.0, 0.95),
        "coverage": _num(args, "coverage", s.coverage, 0.0, 1.0),
        "forward": _num(args, "forward", s.forward_rate, 0.000001, 1e9),
        "cost": _num(args, "cost", s.annual_cost_rate, 0.0, 1.0),
        "threshold": _num(args, "threshold", DEFAULTS["threshold"], 0.0, 10.0),
        "co2e": _num(args, "co2e", s.co2e_per_year, 0.0, 1e9),
    }


@app.get("/")
def desk():
    p = read_params(request.args)
    s = p["scenario"]

    x = build_inputs(
        {
            "principal": s.principal,
            "interest": s.interest,
            "years": s.years,
            "rate": s.rate,
            "cfads": s.annual_cfads,
            "shock": p["shock"],
            "coverage": p["coverage"],
            "forward": p["forward"],
            "cost": p["cost"],
        }
    )
    result = summary(x)
    green = green_metrics(x, p["co2e"], result)

    grid = comparison_grid(
        x,
        shocks=[r[0] for r in sc.SHOCK_PRESETS],
        coverages=[0.0, 0.25, 0.5, 1.0],
    )
    be = break_even_coverage(x, p["threshold"])

    qs = {k: v for k, v in request.args.items()}
    csv_url = url_for("export_csv", **qs) if qs else url_for("export_csv")

    return render_template(
        "desk.html",
        p=p,
        s=s,
        regime=s.regime_obj,
        result=result,
        green=green,
        grid=grid,
        presets=sc.SHOCK_PRESETS,
        regimes=sc.REGIMES,
        scenarios=sc.all_scenarios(),
        break_even=be,
        csv_url=csv_url,
        scenario_defaults={
            "shock": s.depreciation,
            "coverage": s.coverage,
            "forward": s.forward_rate,
            "cost": s.annual_cost_rate,
            "co2e": s.co2e_per_year,
        },
    )


@app.get("/scenario/<key>")
def pick(key):
    """Switching scenario resets overrides: assumptions differ per regime."""
    if key not in sc.SCENARIOS:
        return redirect(url_for("desk"))
    return redirect(url_for("desk", scenario=key))


@app.get("/export.csv")
def export_csv():
    """The annual table as CSV, generated from the same engine call."""
    p = read_params(request.args)
    s = p["scenario"]
    x = build_inputs(
        {
            "principal": s.principal,
            "interest": s.interest,
            "years": s.years,
            "rate": s.rate,
            "cfads": s.annual_cfads,
            "shock": p["shock"],
            "coverage": p["coverage"],
            "forward": p["forward"],
            "cost": p["cost"],
        }
    )
    rows = summary(x)["rows"]
    header = list(rows[0].keys())
    lines = [",".join(header)]
    for r in rows:
        lines.append(",".join(str(r[h]) for h in header))
    body = "\n".join(lines) + "\n"
    return Response(
        body,
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=making-change-{s.key}.csv"
        },
    )


@app.get("/healthz")
def healthz():
    return {"ok": True}


if __name__ == "__main__":
    # 0.0.0.0 so the sandbox preview can reach it; the Host header is not
    # allowlisted, and no origin check blocks the proxied preview frame.
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
        debug=False,
        use_reloader=False,
    )
