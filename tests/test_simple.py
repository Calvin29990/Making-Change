"""Parity test: the single-file HTML dashboard must agree with model.py.

`simple/index.html` carries its own 20-line copy of the engine so that it can run
by double-click, with no server and no install. That duplication is the one thing
that could silently drift, so this test extracts the JavaScript, runs it under
node, and compares every row against the Python engine.

Skipped (not failed) when node is unavailable, so the suite still runs anywhere.
"""
import json
import shutil
import subprocess
import unittest
from pathlib import Path

from model import Inputs, simulate

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "simple" / "index.html"
NODE = shutil.which("node")

CASE = {"principal": 10e6, "years": 15, "interest": 0.05, "rate": 655.957, "cfads": 850e6}


def js_rows(shock, coverage, cost, forward=655.957):
    """Run the dashboard's own simulate() in node and return its rows as JSON."""
    source = HTML.read_text()
    start = source.index("function simulate(")
    end = source.index("/* ───────────────────────── formatting", start)
    fn = source[start:end]

    script = (
        "const CASE = " + json.dumps(CASE) + ";\n"
        + fn
        + "\nconst rows = simulate(%r, %r, %r, %r);\n" % (shock, coverage, cost, forward)
        + "process.stdout.write(JSON.stringify(rows));\n"
    )
    out = subprocess.run([NODE, "-e", script], capture_output=True, text=True, timeout=30)
    if out.returncode != 0:
        raise AssertionError("node failed: " + out.stderr[:500])
    return json.loads(out.stdout)


@unittest.skipIf(NODE is None, "node is not available")
class DashboardParityTests(unittest.TestCase):
    def compare(self, shock, coverage, cost):
        rows = js_rows(shock, coverage, cost)
        x = Inputs(
            principal=CASE["principal"], annual_interest=CASE["interest"],
            years=CASE["years"], rate=CASE["rate"], annual_cfads=CASE["cfads"],
            depreciation=shock, coverage=coverage, forward_rate=655.957,
            annual_cost_rate=cost,
        )
        py = simulate(x)
        self.assertEqual(len(rows), len(py))
        for js, p in zip(rows, py):
            self.assertEqual(js["year"], p["Année"])
            for js_key, py_key in (
                ("service", "Service dette (devise)"),
                ("rateStressed", "Taux scénario"),
                ("uncovered", "Service sans couverture (local)"),
                ("hedged", "Service avec couverture (local)"),
                ("cost", "Coût couverture (local)"),
                ("dscrUn", "DSCR sans couverture"),
                ("dscrHg", "DSCR avec couverture"),
            ):
                self.assertAlmostEqual(js[js_key], p[py_key], places=4,
                                       msg=f"{js_key} year {js['year']}")

    def test_no_shock_no_hedge(self):
        self.compare(0.0, 0.0, 0.0)

    def test_default_case(self):
        self.compare(0.20, 0.50, 0.0)

    def test_hedge_with_cost(self):
        self.compare(0.35, 0.75, 0.02)

    def test_full_shock_full_hedge(self):
        self.compare(0.80, 1.0, 0.05)

    def test_zero_coverage_ignores_cost(self):
        rows = js_rows(0.30, 0.0, 0.05)
        self.assertTrue(all(r["cost"] == 0 for r in rows))


GH_PAGES = ROOT / "docs" / "index.html"


class GitHubPagesTests(unittest.TestCase):
    """docs/ is what GitHub Pages serves: it must stay in step with simple/."""

    def test_assets_exist(self):
        self.assertTrue(GH_PAGES.exists())
        self.assertTrue((ROOT / "docs" / "dashboard.css").exists())
        self.assertTrue((ROOT / "docs" / "dashboard.js").exists())

    def test_page_has_no_external_runtime_dependency(self):
        html = GH_PAGES.read_text()
        self.assertNotIn("http://", html)
        import re
        self.assertFalse(re.search(r'(?:src|href)="https?://[^" ]+"', "\n".join(re.findall(r"<(?:script|link)[^>]*>", html))))
        self.assertIn("dashboard.css", html)
        self.assertIn("dashboard.js", html)

    def test_script_matches_the_single_file_version(self):
        """The published script must be byte-identical to the tested one."""
        src = HTML.read_text()
        embedded = src[src.index('<script>\n"use strict";') + len("<script>"): src.rindex("</script>")].strip()
        published = (ROOT / "docs" / "dashboard.js").read_text().strip()
        self.assertEqual(embedded, published)

    def test_published_script_computes_the_same_rows(self):
        script = (ROOT / "docs" / "dashboard.js").read_text()
        fn_start = script.index("function simulate(")
        fn_end = script.index("/* ───────────────────────── formatting", fn_start)
        runner = (
            "const CASE = " + json.dumps(CASE) + ";\n"
            + script[fn_start:fn_end]
            + "\nprocess.stdout.write(JSON.stringify(simulate(0.2,0.5,0.0,655.957)));"
        )
        out = subprocess.run([NODE, "-e", runner], capture_output=True, text=True, timeout=30)
        self.assertEqual(out.returncode, 0, out.stderr[:400])
        rows = json.loads(out.stdout)
        self.assertEqual(rows[0]["year"], 1)
        self.assertAlmostEqual(rows[0]["rateStressed"], 655.957 / 0.8, places=6)


class DashboardFileTests(unittest.TestCase):
    def test_single_file_no_external_dependency(self):
        html = HTML.read_text()
        # no CDN, no framework, no build artefact
        for forbidden in ("http://", "https://cdn", "src=\"http", "@import"):
            self.assertNotIn(forbidden, html, forbidden)

    def test_no_personal_name(self):
        html = HTML.read_text().lower()
        for name in ("calvin", "edwin", "zinsou", "minang", "ayundi", "ayundy"):
            self.assertNotIn(name, html)

    def test_disclaimers_present(self):
        flat = " ".join(HTML.read_text().lower().split())
        self.assertIn("hypothetical break of the parity", flat)
        self.assertIn("not advice", flat)
        self.assertIn("what this does not say", flat)

    def test_page_script_runs_and_renders(self):
        """Execute the whole inline script against a tiny DOM stub.

        Catches typos in render() that a pure-parity test would miss: the page
        must produce numbers, not an exception, on first paint.
        """
        html = HTML.read_text()
        script = html[html.index('"use strict";'): html.rindex("</script>")]
        stub = r"""
const state = {values:{shock:"20",cov:"50",cost:"0",thr:"1.2",co2:"12000"}, text:{}, cls:{}};
function node(id){
  return {
    id, value: state.values[id] || "0", style: {},
    min:"0", max: id==="thr"?"2.5":"100",
    set textContent(v){ state.text[id]=v; }, get textContent(){ return state.text[id]||""; },
    set innerHTML(v){ state.text[id+"-html"]=v; }, get innerHTML(){ return state.text[id+"-html"]||""; },
    set className(v){ state.cls[id]=v; }, get className(){ return state.cls[id]||""; },
    addEventListener(){}, querySelector(){ return node("tbody"); }
  };
}
global.document = {
  getElementById: node,
  querySelectorAll: () => [],
};
global.window = {};
"""
        check = r"""
const out = {
  extra: state.text["k-extra"], dscrUn: state.text["k-dscr-un"],
  dscrHg: state.text["k-dscr-hg"], cost: state.text["k-cost"],
  green: state.text["g-service"], chart: (state.text["chart-inner-html"]||"").length,
  rows: (state.text["tbody-html"]||"").split("<tr>").length - 1
};
process.stdout.write(JSON.stringify(out));
"""
        out = subprocess.run([NODE, "-e", stub + script + check],
                             capture_output=True, text=True, timeout=30)
        self.assertEqual(out.returncode, 0, out.stderr[:800])
        result = json.loads(out.stdout)
        self.assertTrue(result["extra"].startswith("+"), result["extra"])
        self.assertTrue(result["dscrUn"].endswith("x"))
        self.assertTrue(result["dscrHg"].endswith("x"))
        self.assertGreater(result["chart"], 500, "chart should draw bars")
        self.assertEqual(result["rows"], CASE["years"])
        self.assertNotIn('id="co2"', html)
        self.assertIn("constructed teaching case", html)


if __name__ == "__main__":
    unittest.main()
