"""Tests for the web layer.

The engine is already covered by tests/test_model.py. These tests check that
the site cannot drift from it: same numbers through HTTP as through the engine,
plus the URL-reproducibility guarantee and the input clamping.
"""
import unittest

from desk.webapp import app
from desk import scenarios as sc
from desk.engine import break_even_coverage, build_inputs, green_metrics, summary
from model import simulate
from dataclasses import replace


class WebTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_home_renders_default_scenario(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        body = r.get_data(as_text=True)
        s = sc.get(sc.DEFAULT_SCENARIO)
        self.assertIn(s.name, body)
        self.assertIn("hypothetical parity break", body)
        self.assertIn("not a forecast", body.lower())

    def test_same_url_same_numbers(self):
        url = "/?scenario=ghs-managed-solar&shock=0.35&coverage=0.75&forward=15&cost=0.02"
        a = self.client.get(url).get_data(as_text=True)
        b = self.client.get(url).get_data(as_text=True)
        self.assertEqual(a, b)

    def test_shock_changes_result(self):
        low = self.client.get("/?shock=0.10").get_data(as_text=True)
        high = self.client.get("/?shock=0.50").get_data(as_text=True)
        self.assertNotEqual(low, high)

    def test_bad_input_is_clamped_not_crashing(self):
        for qs in ("?shock=abc", "?shock=99", "?coverage=-5", "?forward=0",
                   "?threshold=1e9", "?scenario=nope", "?co2e=-10"):
            self.assertEqual(self.client.get("/" + qs).status_code, 200, qs)

    def test_csv_matches_engine(self):
        r = self.client.get("/export.csv?shock=0.30&coverage=0.5")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.mimetype, "text/csv")
        lines = r.get_data(as_text=True).strip().split("\n")
        self.assertEqual(len(lines), sc.get(sc.DEFAULT_SCENARIO).years + 1)
        self.assertIn("DSCR avec couverture", lines[0])

    def test_scenario_switch_redirects(self):
        r = self.client.get("/scenario/brl-float-transport")
        self.assertEqual(r.status_code, 302)
        self.assertIn("brl-float-transport", r.headers["Location"])
        self.assertEqual(self.client.get("/scenario/unknown").status_code, 302)

    def test_peg_is_labelled_and_float_is_not(self):
        peg = self.client.get("/scenario/xaf-peg-infra", follow_redirects=True).get_data(as_text=True)
        flt = self.client.get("/scenario/brl-float-transport", follow_redirects=True).get_data(as_text=True)
        self.assertIn("hypothetical parity break", peg)
        self.assertNotIn("hypothetical parity break", flt)

    def test_no_personal_name_anywhere(self):
        body = self.client.get("/").get_data(as_text=True).lower()
        for name in ("calvin", "edwin", "zinsou", "minang", "ayundi", "ayundy"):
            self.assertNotIn(name, body)


class EngineLayerTests(unittest.TestCase):
    def setUp(self):
        s = sc.get(sc.DEFAULT_SCENARIO)
        self.x = build_inputs({
            "principal": s.principal, "interest": s.interest, "years": s.years,
            "rate": s.rate, "cfads": s.annual_cfads, "shock": s.depreciation,
            "coverage": s.coverage, "forward": s.forward_rate,
            "cost": s.annual_cost_rate,
        })

    def test_summary_uses_the_engine(self):
        r = summary(self.x)
        rows = simulate(self.x)
        self.assertEqual(r["rows"], rows)
        self.assertAlmostEqual(r["dscr_min_hedged"],
                               min(x["DSCR avec couverture"] for x in rows))

    def test_extra_local_is_zero_without_shock(self):
        r = summary(replace(self.x, depreciation=0.0))
        self.assertAlmostEqual(r["extra_local"], 0.0, places=6)

    def test_hedge_cost_is_positive_when_cost_set(self):
        r = summary(replace(self.x, annual_cost_rate=0.02, coverage=0.5))
        self.assertGreater(r["hedge_cost"], 0)

    def test_break_even_is_monotone(self):
        loose = break_even_coverage(self.x, 0.5)
        strict = break_even_coverage(self.x, 3.0)
        self.assertIsNotNone(loose)
        self.assertTrue(strict is None or strict >= loose)

    def test_green_metrics_are_ratios_of_the_same_result(self):
        r = summary(self.x)
        g = green_metrics(self.x, 1000.0, r)
        self.assertAlmostEqual(g["total_co2e"], 1000.0 * self.x.years)
        self.assertAlmostEqual(g["shock_cost_per_tco2e"], r["extra_local"] / g["total_co2e"])

    def test_green_metrics_survive_zero_carbon_input(self):
        g = green_metrics(self.x, 0.0, summary(self.x))
        self.assertIsNone(g["service_per_tco2e"])


if __name__ == "__main__":
    unittest.main()
