"use strict";

/* ───────────────────────── the model ─────────────────────────
   Mirrors model.py exactly. Kept in 20 readable lines so a reader can
   check it against the Python engine (tests/test_simple.py asserts parity).
   Rate convention: local units per 1 unit of debt currency. A depreciation d
   means the local currency loses d of its value, so the rate becomes S/(1-d).
   ───────────────────────────────────────────────────────────── */
const CASE = {
  principal: 10e6,     // EUR
  years: 15,
  interest: 0.05,      // per year, on the opening balance
  rate: 655.957,       // XAF per EUR at start
  cfads: 850e6         // XAF available for debt service per year, constant
};

function simulate(shock, coverage, costRate, forward) {
  const rateStressed = CASE.rate / (1 - shock);
  const principalSlice = CASE.principal / CASE.years;
  const rows = [];
  for (let year = 1; year <= CASE.years; year++) {
    const opening = CASE.principal - (year - 1) * principalSlice;
    const interest = opening * CASE.interest;
    const service = principalSlice + interest;          // in EUR
    const uncovered = service * rateStressed;           // XAF
    const cost = service * coverage * forward * costRate;
    const hedged = service * ((1 - coverage) * rateStressed + coverage * forward) + cost;
    rows.push({
      year, service, rateStressed, uncovered, hedged, cost,
      dscrUn: CASE.cfads / uncovered,
      dscrHg: CASE.cfads / hedged
    });
  }
  return rows;
}

/* ───────────────────────── formatting ───────────────────────── */
const fmt = (n, d) => n.toLocaleString("en-US", {minimumFractionDigits: d || 0, maximumFractionDigits: d || 0});
const millions = n => (n / 1e6).toLocaleString("en-US", {maximumFractionDigits: 0}) + " M";
const dscr = n => n.toFixed(2) + "x";

/* ───────────────────────── render ───────────────────────── */
const el = id => document.getElementById(id);

function readInputs() {
  return {
    shock: +el("shock").value / 100,
    coverage: +el("cov").value / 100,
    cost: +el("cost").value / 100,
    threshold: +el("thr").value,
    co2: +el("co2").value
  };
}

function paintRange(input) {
  const min = +input.min, max = +input.max;
  const pct = ((+input.value - min) / (max - min)) * 100;
  input.style.background =
    "linear-gradient(to right,var(--mint) 0%,var(--mint) " + pct +
    "%,var(--line) " + pct + "%,var(--line) 100%)";
}

function render() {
  const i = readInputs();

  // labels
  el("shock-val").textContent = Math.round(i.shock * 100);
  el("cov-val").textContent = Math.round(i.coverage * 100);
  el("cost-val").textContent = (i.cost * 100).toFixed(2);
  el("thr-val").textContent = i.threshold.toFixed(2);
  el("co2-val").textContent = fmt(i.co2);
  document.querySelectorAll("input[type=range]").forEach(paintRange);

  // engine: the explicit hedge is the forward rate at spot (a flat forward,
  // stated in the text below the KPIs)
  const forward = CASE.rate;
  const rows = simulate(i.shock, i.coverage, i.cost, forward);

  const minUn = Math.min(...rows.map(r => r.dscrUn));
  const minHg = Math.min(...rows.map(r => r.dscrHg));
  const serviceUn = rows.reduce((a, r) => a + r.uncovered, 0);
  const serviceHg = rows.reduce((a, r) => a + r.hedged, 0);
  const cost = rows.reduce((a, r) => a + r.cost, 0);
  const noShock = simulate(0, 0, 0, forward).reduce((a, r) => a + r.uncovered, 0);
  const extra = serviceUn - noShock;

  el("k-extra").textContent = "+" + millions(extra);
  el("k-dscr-un").textContent = dscr(minUn);
  el("k-dscr-un").className = minUn < i.threshold ? "bad" : "good";
  el("k-dscr-hg").textContent = dscr(minHg);
  el("k-dscr-hg").className = minHg < i.threshold ? "bad" : "good";
  el("k-dscr-sub").textContent = "threshold " + i.threshold.toFixed(2) + "x";
  el("k-cost").textContent = cost > 0 ? millions(cost) : "0";
  el("k-cost").className = cost > 0 ? "warn" : "mute";

  drawChart(rows, i.threshold);

  // table
  el("table").querySelector("tbody").innerHTML = rows.map(r => `
    <tr>
      <th>${r.year}</th>
      <td>${fmt(r.service)}</td>
      <td>${r.rateStressed.toFixed(3)}</td>
      <td>${fmt(r.uncovered)}</td>
      <td>${fmt(r.hedged)}</td>
      <td class="${r.dscrUn < i.threshold ? "ko" : "ok"}">${r.dscrUn.toFixed(2)}</td>
      <td class="${r.dscrHg < i.threshold ? "ko" : "ok"}">${r.dscrHg.toFixed(2)}</td>
    </tr>`).join("");

  // green
  const totalCo2 = i.co2 * CASE.years;
  el("g-service").textContent = totalCo2 ? fmt(serviceUn / totalCo2) : "—";
  el("g-shock").textContent = totalCo2 ? fmt(extra / totalCo2) : "—";
  const saving = Math.max(serviceUn - serviceHg, 0);
  el("g-hedge").textContent = totalCo2 ? fmt(saving / totalCo2) : "—";
}

/* SVG chart, hand-drawn: two bars per year, plus the threshold line. */
function drawChart(rows, threshold) {
  const W = 720, H = 210, left = 40, base = 172, h = 148;
  const slot = (W - left - 14) / rows.length;
  const values = rows.flatMap(r => [r.dscrUn, r.dscrHg]);
  const max = Math.max(...values, threshold) * 1.2;

  let s = "";
  [0, .25, .5, .75, 1].forEach(f => {
    const y = base - f * h;
    s += `<line class="gl" x1="${left}" x2="${W - 10}" y1="${y}" y2="${y}"/>`;
    s += `<text class="yl" x="0" y="${y + 3}">${(f * max).toFixed(2)}x</text>`;
  });

  const yThr = base - (threshold / max) * h;
  s += `<line class="thr" x1="${left}" x2="${W - 10}" y1="${yThr}" y2="${yThr}"/>`;
  s += `<text class="tlab" x="${left + 4}" y="${yThr - 4}">threshold ${threshold.toFixed(2)}x</text>`;

  rows.forEach((r, idx) => {
    const x = left + 4 + idx * slot;
    const bw = Math.max(slot * 0.32, 5);
    const yUn = base - (r.dscrUn / max) * h;
    const yHg = base - (r.dscrHg / max) * h;
    s += `<rect class="un" x="${x}" y="${yUn}" width="${bw}" height="${base - yUn}"/>`;
    s += `<rect class="hg ${r.dscrHg >= threshold ? "hot" : ""}" x="${x + bw + 1}" y="${yHg}" width="${bw}" height="${base - yHg}"/>`;
    if (idx === 0 || idx === rows.length - 1 || (idx + 1) % 3 === 0) {
      s += `<text class="xl" x="${x + bw}" y="${base + 14}">${r.year}</text>`;
    }
  });
  s += `<line class="gl" x1="${left}" x2="${W - 10}" y1="${base}" y2="${base}"/>`;
  el("chart-inner").innerHTML = s;
}

/* wire the sliders */
["shock", "cov", "cost", "thr", "co2"].forEach(id => {
  el(id).addEventListener("input", render);
});
render();

/* expose the engine for a one-line check in the console or from Node */
if (typeof window !== "undefined") window.mcSimulate = simulate;
