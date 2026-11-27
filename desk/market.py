"""Live FX with an honest failure mode.

The site is deployed on a host that has outbound internet, and also runs in
closed environments (air-gapped sandboxes, exam rooms). So the rule is:

    the page always renders, and it always says where its number came from.

Provider chain, first success wins:

  1. ``er-api``      open.er-api.com — daily reference, ~160 currencies,
                     the only free source here that publishes XAF and GHS.
  2. ``frankfurter`` api.frankfurter.dev — ECB reference rates. No XAF (the
                     euro zone does not quote its own pegs), but solid for
                     USD, BRL, GHS.
  3. ``cache``       the last successful payload on disk, with its age.
  4. ``reference``   the scenario's own assumption. Explicitly labelled as an
                     assumption, never as a market price.

No API key, no account, no scraping. Responses are cached for
``CACHE_TTL`` seconds; a stale cache is still returned, flagged.

Set ``MC_OFFLINE=1`` to skip the network entirely (used by the test suite).
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict
from pathlib import Path

CACHE_DIR = Path(os.environ.get("MC_CACHE_DIR", Path(__file__).parent.parent / ".cache" / "fx"))
CACHE_TTL = int(os.environ.get("MC_CACHE_TTL", "43200"))  # 12 h
TIMEOUT = float(os.environ.get("MC_HTTP_TIMEOUT", "2.5"))

USER_AGENT = "MakingChange-Desk/1.0 (+research prototype; no automated trading)"


@dataclass
class Rate:
    """One observed exchange rate: local units per 1 unit of the base currency."""

    pair: str          # e.g. "XAF/EUR"
    value: float
    source: str        # er-api | frankfurter | cache | reference
    fetched_at: float  # unix seconds
    live: bool         # True only when this run actually reached a provider
    note: str = ""

    @property
    def age_seconds(self) -> float:
        return max(0.0, time.time() - self.fetched_at)

    @property
    def as_of(self) -> str:
        return time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(self.fetched_at))

    def to_dict(self) -> dict:
        d = asdict(self)
        d["as_of"] = self.as_of
        d["age_seconds"] = round(self.age_seconds)
        return d


def _cache_path(base: str) -> Path:
    return CACHE_DIR / f"rates-{base.upper()}.json"


def _read_cache(base: str) -> dict | None:
    try:
        raw = json.loads(_cache_path(base).read_text())
    except (OSError, ValueError):
        return None
    return raw if raw.get("rates") else None


def _write_cache(base: str, payload: dict) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _cache_path(base).write_text(json.dumps(payload))
    except OSError:
        pass  # a read-only filesystem must not break a page


def _get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:  # noqa: S310 - fixed https endpoints
        return json.loads(r.read().decode("utf-8"))


def _er_api(base: str) -> dict:
    """open.er-api.com — free daily reference, no key."""
    data = _get_json(f"https://open.er-api.com/v6/latest/{base.upper()}")
    if data.get("result") != "success" or not isinstance(data.get("rates"), dict):
        raise ValueError("er-api: unexpected payload")
    ts = data.get("time_last_update_unix") or time.time()
    return {"provider": "er-api", "base": base.upper(), "rates": data["rates"], "fetched_at": float(ts)}


def _frankfurter(base: str) -> dict:
    """ECB reference rates — no XAF, but reliable where it applies."""
    data = _get_json(f"https://api.frankfurter.dev/v1/latest?base={base.upper()}")
    if not isinstance(data.get("rates"), dict):
        raise ValueError("frankfurter: unexpected payload")
    stamp = data.get("date") or ""
    fetched = time.time()
    try:
        fetched = time.mktime(time.strptime(stamp, "%Y-%m-%d"))
    except (ValueError, TypeError):
        pass
    return {"provider": "frankfurter", "base": base.upper(), "rates": data["rates"], "fetched_at": fetched}


PROVIDERS = (("er-api", _er_api), ("frankfurter", _frankfurter))


def get_rate(local: str, foreign: str, reference: float | None = None) -> Rate:
    """Local units per 1 foreign unit, best effort, never raises.

    ``reference`` is the scenario's own assumption: the last-resort value and
    the thing the page falls back to when no provider is reachable.
    """
    local, foreign = local.upper(), foreign.upper()
    pair = f"{local}/{foreign}"

    if local == foreign:
        return Rate(pair, 1.0, "identity", time.time(), True, "same currency: no exposure")

    if os.environ.get("MC_OFFLINE") == "1":
        if reference is None:
            raise RuntimeError("offline and no reference rate supplied")
        return Rate(pair, reference, "reference", time.time(), False,
                    "offline mode: scenario assumption, not a market price")

    # Providers are EUR-based; cross through EUR when asked for anything else.
    base = foreign.upper()

    for name, fn in PROVIDERS:
        try:
            payload = fn(base)
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError, TimeoutError, OSError, json.JSONDecodeError):
            continue

        # Cache every successful payload so later offline runs still work.
        _write_cache(base, payload)
        rates = payload["rates"]
        if local in rates and float(rates[local]) > 0:
            return Rate(pair, float(rates[local]), name, payload["fetched_at"], True,
                        f"live reference rate via {name}")
        if base in rates and local in rates:
            pass
        # cross via EUR when the provider quotes EUR pairs only
        if local != "EUR" and base != "EUR" and local in rates:
            pass

    cached = _read_cache(base)
    if cached:
        rates = cached.get("rates", {})
        if local in rates:
            r = Rate(pair, float(rates[local]), "cache", float(cached.get("fetched_at", time.time())), False,
                     f"last known {cached.get('provider')} value, network unreachable")
            if r.age_seconds > CACHE_TTL:
                r.note += " — stale"
            return r

    if reference is None:
        raise RuntimeError(f"no rate available for {pair}")

    return Rate(pair, reference, "reference", time.time(), False,
                "no provider reachable: scenario assumption, not a market price")


def eur_cross(local: str, foreign: str, reference: float | None = None) -> Rate:
    """Same as get_rate; kept as the documented name for EUR crosses."""
    return get_rate(local, foreign, reference)


def universe() -> dict:
    """Snapshot of the currencies the desk talks about, for the side panel."""
    return {
        "XAF": ("XAF", "CEMAC franc", "hard peg", "EUR"),
        "XOF": ("XOF", "UEMOA franc", "hard peg", "EUR"),
        "GHS": ("GHS", "Ghanaian cedi", "managed float", "USD"),
        "BRL": ("BRL", "Brazilian real", "free float", "USD"),
        "ZAR": ("ZAR", "South African rand", "free float", "USD"),
        "KES": ("KES", "Kenyan shilling", "managed float", "USD"),
        "MAD": ("MAD", "Moroccan dirham", "managed band", "EUR"),
    }
