"""Making Change — FX exposure desk.

Design language borrowed from ShockDesk: dark surface, mint accent, URL bar in
monospace, tabs, KPI cards, thin-bordered panels. Everything the analyst changes
lives in the query string, so a screen can be pasted into a thesis footnote.

Routes
------
GET  /                        desk: shock, hedge, DSCR, grid, green reading
GET  /scenarios/<key>         switch the dated case (redirects to /)
GET  /managers/<key>          switch the hedge manager (redirects to /)
GET  /market                  live FX panel and provider status
GET  /code                    the managers as source, ShockDesk-style
GET  /api/simulate?…          the same numbers as JSON
GET  /export.csv              the annual table

No database, no session, no write path. No market execution.
"""
from __future__ import annotations

import os

from flask import Flask, Response, jsonify, redirect, render_template, request, url_for

from . import managers as mg
from . import market
from . import scenarios as sc
from .engine import (
    break_even_coverage,
    build_inputs,
    comparison_grid,
    green_metrics,
    summary,
)
from dataclasses import replace

from model import Inputs, simulate

app = Flask(__name__)

DEFAULTS = {"co2e": None, "threshold": 1.20, "manager": mg.DEFAULT_MANAGER, "live": None}


def _num(args, name, fallback, lo, hi):
    try:
        v = float(args.get(name, ""))
    except (TypeError, ValueError):
        return fallback
    return max(lo, min(hi, v))


def read_params(args) -> dict:
    key = args.get("scenario", sc.DEFAULT_SCENARIO)
    if key not in sc.SCENARIOS:
        key = sc.DEFAULT_SCENARIO
    s = sc.get(key)

    live_flag = args.get("live")
    live = None if live_flag is None else live_flag in ("1", "on", "true")

    return {
        "scenario_key": key,
        "scenario": s,
        "shock": _num(args, "shock", s.depreciation, 0.0, 0.95),
        "coverage": _num(args, "coverage", s.coverage, 0.0, 1.0),
        "forward": _num(args, "forward", s.forward_rate, 1e-6, 1e9),
        "cost": _num(args, "cost", s.annual_cost_rate, 0.0, 1.0),
        "threshold": _num(args, "threshold", DEFAULTS["threshold"], 0.0, 10.0),
        "co2e": _num(args, "co2e", s.co2e_per_year, 0.0, 1e9),
        "principal": _num(args, "principal", s.principal, 1.0, 1e12),
        "rate_override": (
            _num(args, "rate", s.rate, 1e-6, 1e9) if "rate" in args else None
        ),
        "manager": mg.get(args.get("manager", DEFAULTS["manager"])).key,
        "live": live,
    }


def resolve_spot(p: dict) -> market.Rate:
    """Spot rate for this page view: live if asked, else the scenario assumption."""
    s = p["scenario"]
    want_live = p["live"]
    if want_live is None:
        want_live = os.environ.get("MC_LIVE_DEFAULT", "0") == "1"
    if not want_live:
        return market.Rate(f"{s.local}/{s.foreign}", s.rate, "reference", sc.SCENARIO_DATE_TS,
                           False, "scenario assumption (no network call)")
    try:
        r = market.get_rate(s.local, s.foreign, reference=s.rate)
    except RuntimeError:
        r = market.Rate(f"{s.local}/{s.foreign}", s.rate, "reference", sc.SCENARIO_DATE_TS,
                        False, "no provider reachable: scenario assumption")
    if p["rate_override"]:
        r = market.Rate(r.pair, p["rate_override"], r.source + "+override", r.fetched_at,
                        r.live, r.note + " — overridden from the URL")
    return r


def build_page(p: dict, spot: market.Rate):
    s = p["scenario"]
    rate = spot.value if p["rate_override"] is None else p["rate_override"]
    x = build_inputs({
        "principal": p["principal"],
        "interest": s.interest,
        "years": s.years,
        "rate": rate,
        "cfads": s.annual_cfads,
        "shock": p["shock"],
        "coverage": p["coverage"],
        "forward": p["forward"],
        "cost": p["cost"],
    })
    return x


def manager_view(x: Inputs, p: dict, spot: market.Rate) -> mg.Proposal:
    manager = mg.get(p["manager"])

    def dscr_with(coverage: float) -> float:
        rows = simulate(replace(x, coverage=coverage))
        return min(r["DSCR avec couverture"] for r in rows)

    view = mg.HedgeView(
        years=x.years,
        capacity=1.0,
        shock=x.depreciation,
        spot=spot,
        forward=x.forward_rate,
        annual_cost_rate=x.annual_cost_rate,
        dscr_threshold=p["threshold"],
        dscr_with=dscr_with,
    )
    return manager.propose(view)


# ── pages ─────────────────────────────────────────────────────────────────────

@app.context_processor
def inject_helpers():
    """``qs_url(**overrides)`` = this page with a few parameters changed."""

    def qs_url(**overrides):
        args = request.args.to_dict()
        args.update({k: v for k, v in overrides.items() if v is not None})
        return url_for("desk", **args)

    return {"qs_url": qs_url}


@app.get("/")
def desk():
    p = read_params(request.args)
    spot = resolve_spot(p)
    x = build_page(p, spot)
    result = summary(x)
    green = green_metrics(x, p["co2e"], result)
    proposal = manager_view(x, p, spot)
    grid = comparison_grid(x, shocks=[r[0] for r in sc.SHOCK_PRESETS], coverages=[0.0, 0.25, 0.5, 0.75, 1.0])
    be = break_even_coverage(x, p["threshold"])
    ceiling = min(r["DSCR avec couverture"] for r in simulate(replace(x, coverage=1.0)))

    qs = request.args.to_dict()
    return render_template(
        "desk.html",
        p=p,
        s=p["scenario"],
        regime=p["scenario"].regime_obj,
        spot=spot,
        result=result,
        green=green,
        grid=grid,
        presets=sc.SHOCK_PRESETS,
        scenarios=sc.all_scenarios(),
        managers=mg.all_managers(),
        manager=mg.get(p["manager"]),
        proposal=proposal,
        break_even=be,
        ceiling=ceiling,
        csv_url=url_for("export_csv", **qs),
        api_url=url_for("api_simulate", **qs),
        query_string=request.query_string.decode() or "scenario=" + sc.DEFAULT_SCENARIO,
        universe=market.universe(),
        target=_target(request.args),
    )


@app.get("/scenarios/<key>")
def pick(key):
    if key not in sc.SCENARIOS:
        return redirect(url_for("desk"))
    return redirect(url_for("desk", scenario=key))


@app.get("/managers/<key>")
def pick_manager(key):
    args = request.args.to_dict()
    args["manager"] = mg.get(key).key
    return redirect(url_for("desk", **args))


@app.get("/simple")
def simple_page():
    """Serve the one-file dashboard from the Flask app, same origin as the desk."""
    from pathlib import Path as _Path

    return Response(
        (_Path(__file__).parent.parent / "simple" / "index.html").read_text(),
        mimetype="text/html",
    )


@app.get("/market")
def market_page():
    s = sc.get(request.args.get("scenario", sc.DEFAULT_SCENARIO))
    rows = []
    for code, (sym, label, regime, base) in market.universe().items():
        try:
            r = market.get_rate(code, base, reference=s.rate if code == s.local else None)
        except RuntimeError:
            r = market.Rate(f"{code}/{base}", 0.0, "unavailable", 0, False, "no provider reachable")
        rows.append((sym, label, regime, r))
    return render_template(
        "market.html",
        rows=rows,
        s=s,
        scenarios=sc.all_scenarios(),
        live=any(r.live for _, _, _, r in rows),
    )


@app.get("/code")
def code_page():
    import inspect

    blocks = []
    for m in mg.all_managers():
        src = inspect.getsource(type(m))
        blocks.append((m, src))
    return render_template("code.html", blocks=blocks, manager=mg.get(DEFAULTS["manager"]))


@app.get("/api/managers")
def api_managers():
    return jsonify([m.as_dict() for m in mg.all_managers()])


@app.get("/api/simulate")
def api_simulate():
    p = read_params(request.args)
    spot = resolve_spot(p)
    x = build_page(p, spot)
    result = summary(x)
    green = green_metrics(x, p["co2e"], result)
    proposal = manager_view(x, p, spot)
    return jsonify({
        "scenario": p["scenario"].key,
        "regime": p["scenario"].regime,
        "shock_label": p["scenario"].regime_obj.shock_label,
        "spot": spot.to_dict(),
        "coverage": x.coverage,
        "manager": {"key": mg.get(p["manager"]).key, "proposal": proposal.coverage,
                    "rationale": proposal.rationale},
        "dscr": {"min_unhedged": result["dscr_min_unhedged"],
                 "min_hedged": result["dscr_min_hedged"]},
        "local_currency": {"unhedged": result["service_unhedged"],
                           "hedged": result["service_hedged"],
                           "hedge_cost": result["hedge_cost"],
                           "shock_extra": result["extra_local"]},
        "green": green,
        "rows": result["rows"],
        "disclaimer": "Illustrative simulation. Not a forecast, not a quote, not advice.",
    })


@app.get("/export.csv")
def export_csv():
    p = read_params(request.args)
    spot = resolve_spot(p)
    x = build_page(p, spot)
    rows = summary(x)["rows"]
    header = list(rows[0].keys())
    lines = [",".join(header)] + [",".join(str(r[h]) for h in header) for r in rows]
    return Response(
        "\n".join(lines) + "\n",
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=making-change-{p['scenario'].key}.csv"},
    )


@app.get("/healthz")
def healthz():
    return {"ok": True, "live_default": os.environ.get("MC_LIVE_DEFAULT", "0")}


def _target(args) -> str:
    t = args.get("tab", "desk")
    return t if t in ("desk", "backtest", "grid", "green", "api") else "desk"


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
        debug=False,
        use_reloader=False,
    )
