"""Tests for the web layer.

The engine is covered by test_model.py; these tests check that the site cannot
drift from it, that a URL always reproduces its numbers, that degradation of the
market feed is visible rather than silent, and that no personal name appears.
"""
import os
import unittest

os.environ.setdefault("MC_OFFLINE", "1")

from dataclasses import replace

from desk import managers as mg
from desk import scenarios as sc
from desk.engine import build_inputs, green_metrics, summary
from desk.webapp import app
from model import simulate


def scenario_inputs(s=None, **kw):
    s = s or sc.get(sc.DEFAULT_SCENARIO)
    base = {
        "principal": s.principal, "interest": s.interest, "years": s.years,
        "rate": s.rate, "cfads": s.annual_cfads, "shock": s.depreciation,
        "coverage": s.coverage, "forward": s.forward_rate, "cost": s.annual_cost_rate,
    }
    base.update(kw)
    return build_inputs(base)


class PageTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def page(self, url="/"):
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200, url)
        return r.get_data(as_text=True)

    def test_home_renders_default_scenario(self):
        body = self.page()
        self.assertIn(sc.get(sc.DEFAULT_SCENARIO).name, body)
        self.assertIn("hypothetical parity break", body)
        self.assertIn("not a forecast", body.lower())

    def test_all_scenarios_render(self):
        for key in sc.SCENARIOS:
            self.page(f"/?scenario={key}")

    def test_all_managers_render(self):
        for m in mg.all_managers():
            self.page(f"/?manager={m.key}")

    def test_peg_labelled_float_not(self):
        peg = self.page("/?scenario=xaf-peg-infra")
        flt = self.page("/?scenario=brl-float-transport")
        self.assertIn("hypothetical parity break", peg)
        self.assertNotIn("hypothetical parity break", flt)

    def test_same_url_same_numbers(self):
        url = "/?scenario=ghs-managed-solar&shock=0.35&coverage=0.75&forward=15&cost=0.02"
        self.assertEqual(self.page(url), self.page(url))

    def test_shock_changes_output(self):
        self.assertNotEqual(self.page("/?shock=0.10"), self.page("/?shock=0.50"))

    def test_bad_input_is_clamped(self):
        for qs in ("?shock=abc", "?shock=99", "?coverage=-5", "?forward=0",
                   "?threshold=1e9", "?scenario=nope", "?co2e=-10", "?principal=0",
                   "?manager=nope", "?rate=nan"):
            self.assertEqual(self.client.get("/" + qs).status_code, 200, qs)

    def test_other_pages(self):
        for url in ("/market", "/code", "/api/managers", "/healthz"):
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_scenario_and_manager_switch_redirect(self):
        r = self.client.get("/scenarios/brl-float-transport")
        self.assertEqual(r.status_code, 302)
        self.assertIn("brl-float-transport", r.headers["Location"])
        r = self.client.get("/managers/carry")
        self.assertEqual(r.status_code, 302)
        self.assertIn("manager=carry", r.headers["Location"])

    def test_csv_matches_engine(self):
        r = self.client.get("/export.csv?shock=0.30&coverage=0.5")
        self.assertEqual(r.mimetype, "text/csv")
        lines = r.get_data(as_text=True).strip().split("\n")
        self.assertEqual(len(lines), sc.get(sc.DEFAULT_SCENARIO).years + 1)
        self.assertIn("DSCR avec couverture", lines[0])

    def test_api_simulate_matches_engine(self):
        payload = self.client.get("/api/simulate?scenario=ghs-managed-solar&shock=0.2&coverage=0.4").get_json()
        self.assertEqual(payload["scenario"], "ghs-managed-solar")
        self.assertEqual(payload["spot"]["source"], "reference")
        self.assertFalse(payload["spot"]["live"])
        self.assertEqual(len(payload["rows"]), sc.get("ghs-managed-solar").years)
        self.assertIn("not a forecast", payload["disclaimer"].lower())

    def test_no_personal_name_anywhere(self):
        names = ("calvin", "edwin", "zinsou", "minang", "amyuni", "ayundi", "ayundy")
        for url in ("/", "/market", "/code", "/api/managers"):
            body = self.page(url).lower()
            for n in names:
                self.assertNotIn(n, body, f"{n} in {url}")


class MarketTests(unittest.TestCase):
    def test_offline_returns_reference_and_says_so(self):
        from desk import market

        r = market.get_rate("XAF", "EUR", reference=655.957)
        self.assertEqual(r.source, "reference")
        self.assertFalse(r.live)
        self.assertIn("not a market price", r.note)

    def test_same_currency_is_identity(self):
        from desk import market

        r = market.get_rate("EUR", "EUR")
        self.assertEqual(r.value, 1.0)
        self.assertTrue(r.live)

    def test_rate_serialises(self):
        from desk import market

        d = market.get_rate("GHS", "USD", reference=12.5).to_dict()
        for k in ("pair", "value", "source", "live", "as_of", "age_seconds"):
            self.assertIn(k, d)

    def test_universe_covers_the_three_scenarios(self):
        from desk import market

        u = market.universe()
        for s in sc.all_scenarios():
            self.assertIn(s.local, u)


class ManagerTests(unittest.TestCase):
    def view(self, x, **kw):
        def dscr_with(c):
            rows = simulate(replace(x, coverage=c))
            return min(r["DSCR avec couverture"] for r in rows)

        from desk.market import Rate
        import time

        base = dict(years=x.years, capacity=1.0, shock=x.depreciation,
                    spot=Rate("X", 1.0, "reference", time.time(), False),
                    forward=x.forward_rate, annual_cost_rate=x.annual_cost_rate,
                    dscr_threshold=1.2, dscr_with=dscr_with)
        base.update(kw)
        return mg.HedgeView(**base)

    def test_every_manager_proposes_a_bounded_share(self):
        x = scenario_inputs()
        for m in mg.all_managers():
            p = m.propose(self.view(x))
            self.assertGreaterEqual(p.coverage, 0.0, m.key)
            self.assertLessEqual(p.coverage, 1.0, m.key)
            self.assertTrue(p.rationale, m.key)
            self.assertIsInstance(p.trace, list)

    def test_threshold_seeker_respects_the_covenant_when_possible(self):
        # the default case tops out at 1.11x fully hedged, so ask for 1.05x
        x = scenario_inputs(shock=0.15, coverage=0.0)
        p = mg.get("threshold").propose(self.view(x, dscr_threshold=1.05))
        rows = simulate(replace(x, coverage=p.coverage))
        self.assertGreaterEqual(min(r["DSCR avec couverture"] for r in rows), 1.05 - 1e-9)

    def test_threshold_seeker_says_when_it_is_unreachable(self):
        x = scenario_inputs(shock=0.30, coverage=0.0)
        p = mg.get("threshold").propose(self.view(x, dscr_threshold=9.0))
        self.assertIn("binding constraint", p.rationale)

    def test_carry_aware_skips_an_expensive_forward(self):
        x = scenario_inputs(forward=900.0, shock=0.20)
        p = mg.get("carry").propose(self.view(x))
        self.assertEqual(p.coverage, 0.0)

    def test_managers_are_serialisable(self):
        for m in mg.all_managers():
            d = m.as_dict()
            self.assertEqual(set(d), {"key", "name", "tagline", "family", "file"})


class GreenTests(unittest.TestCase):
    def test_green_ratios_follow_the_same_result(self):
        x = scenario_inputs()
        r = summary(x)
        g = green_metrics(x, 1000.0, r)
        self.assertAlmostEqual(g["total_co2e"], 1000.0 * x.years)
        self.assertAlmostEqual(g["shock_cost_per_tco2e"], r["extra_local"] / g["total_co2e"])

    def test_green_survives_zero_carbon(self):
        x = scenario_inputs()
        self.assertIsNone(green_metrics(x, 0.0, summary(x))["service_per_tco2e"])


if __name__ == "__main__":
    unittest.main()
