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
const fmt = (n, d) => n.toLocaleString("fr-FR", {minimumFractionDigits: d || 0, maximumFractionDigits: d || 0});
const millions = n => (n / 1e6).toLocaleString("fr-FR", {maximumFractionDigits: 0}) + " M";
const dscr = n => n.toFixed(2) + "x";

/* ───────────────────────── render ───────────────────────── */
const el = id => document.getElementById(id);

function readInputs() {
  return {
    shock: +el("shock").value / 100,
    coverage: +el("cov").value / 100,
    cost: +el("cost").value / 100,
    threshold: +el("thr").value
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
  el("k-dscr-sub").textContent = "Seuil choisi : " + i.threshold.toFixed(2) + "×";
  el("k-cost").textContent = cost > 0 ? millions(cost) : "0";
  el("k-cost").className = cost > 0 ? "warn" : "mute";

  drawChart(rows, i.threshold);
  drawOtherCharts(rows,i,noShock,serviceUn,serviceHg,cost);

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


}

/* Four linked SVG visuals; no external runtime or market feed. */
const BLUE = '#3875cd', TEAL = '#008575', AMBER = '#9b6900';
function axes(max, suffix, ticks) {
  let s = '';
  for (let k = 0; k <= 4; k++) {
    const v = max * k / 4, y = 190 - k * 39;
    s += `<line class="gl" x1="48" x2="580" y1="${y}" y2="${y}"/><text x="2" y="${y+4}">${v.toFixed(suffix==='×'?1:0)}${suffix}</text>`;
  }
  ticks.forEach(([x,label]) => s += `<text text-anchor="middle" x="${x}" y="211">${label}</text>`);
  return s;
}
function poly(values, max, color, title) {
  const points = values.map((v,k) => [48+k*532/(values.length-1),190-v/max*156]);
  return `<polyline fill="none" stroke="${color}" stroke-width="2.5" points="${points.map(p=>p.join(',')).join(' ')}"/>` + points.map(([x,y],k)=>`<circle cx="${x}" cy="${y}" r="3" fill="${color}" tabindex="0"><title>${title(k,values[k])}</title></circle>`).join('');
}
function thresholdLine(threshold,max) {
  const y=190-threshold/max*156;
  return `<line class="thr" x1="48" x2="580" y1="${y}" y2="${y}"/><text x="490" y="${y-6}">Seuil ${threshold.toFixed(2)}×</text>`;
}
function drawChart(rows, threshold) {
  const max = Math.max(threshold,...rows.flatMap(r=>[r.dscrUn,r.dscrHg]))*1.15;
  let s=axes(max,'×',[1,5,10,15].map(n=>[48+(n-1)*532/14,'An '+n]));
  s+=thresholdLine(threshold,max);
  s+=poly(rows.map(r=>r.dscrUn),max,BLUE,(k,v)=>`Année ${k+1}, sans protection : ${v.toFixed(2)}×`);
  s+=poly(rows.map(r=>r.dscrHg),max,TEAL,(k,v)=>`Année ${k+1}, avec protection : ${v.toFixed(2)}×`);
  el('chart-inner').innerHTML=s;
}
function drawOtherCharts(rows,i,noShock,serviceUn,serviceHg,cost) {
  const max=Math.max(...rows.flatMap(r=>[r.uncovered,r.hedged]))/1e6*1.15;
  let s=axes(max,'',[1,5,10,15].map(n=>[60+(n-1)*35,'An '+n]));
  rows.forEach((r,k)=>{
    [r.uncovered,r.hedged].forEach((v,j)=>{const h=v/1e6/max*156;s+=`<rect x="${49+k*35+j*13}" y="${190-h}" width="11" height="${h}" fill="${j?TEAL:BLUE}" tabindex="0"><title>Année ${r.year}, ${j?'avec':'sans'} protection : ${fmt(v)} XAF</title></rect>`;});
  });
  el('service-chart').innerHTML=s;
  // True cumulative waterfall: baseline + FX shock - gross protection + fee = hedged total.
  const gross=serviceUn-serviceHg+cost;
  const steps=[['Sans choc',0,noShock,BLUE],['Choc FX',noShock,serviceUn,'#c99338'],['Protection',serviceUn,serviceUn-gross,TEAL],['Frais',serviceUn-gross,serviceHg,'#bc7e45'],['Total protégé',0,serviceHg,TEAL]];
  const wm=Math.max(serviceUn,serviceHg,noShock)/1e6*1.2;
  s=axes(wm,'',steps.map((r,k)=>[98+k*105,r[0]]));
  steps.forEach(([label,a,b,color],k)=>{const x=65+k*105,y=190-Math.max(a,b)/1e6/wm*156,h=Math.abs(b-a)/1e6/wm*156; s+=`<rect x="${x}" y="${y}" width="65" height="${Math.max(h,1)}" fill="${color}" tabindex="0"><title>${label} : ${fmt(b-a)} XAF</title></rect><text text-anchor="middle" x="${x+32}" y="${y-6}">${b-a>0?'+':''}${fmt((b-a)/1e6)}</text>`;
  });el('bridge-chart').innerHTML=s;
  const shocks=Array.from({length:17},(_,k)=>k*.05);
  const series=shocks.map(d=>{const rr=simulate(d,i.coverage,i.cost,CASE.rate);return [Math.min(...rr.map(r=>r.dscrUn)),Math.min(...rr.map(r=>r.dscrHg))];});
  const sm=Math.max(i.threshold,...series.flat())*1.15;
  s=axes(sm,'×',[0,20,40,60,80].map(v=>[48+v/80*532,v+' %']));
  s+=thresholdLine(i.threshold,sm);
  [0,1].forEach(j=>s+=poly(series.map(r=>r[j]),sm,j?TEAL:BLUE,(k,v)=>`Choc ${k*5} %, ${j?'avec':'sans'} protection : ${v.toFixed(2)}×`));
  const current=rows[0];[current.dscrUn,current.dscrHg].forEach((v,j)=>s+=`<circle cx="${48+i.shock/.8*532}" cy="${190-v/sm*156}" r="5" fill="${j?TEAL:BLUE}" stroke="white" stroke-width="2"><title>Choix actuel : ${v.toFixed(2)}×</title></circle>`);
  el('sensitivity-chart').innerHTML=s;
  const min=Math.min(...rows.map(r=>r.dscrHg));
  const status=min<1?'La trésorerie reste insuffisante pour rembourser.':min<i.threshold?'Le projet rembourse, mais reste sous votre seuil de sécurité.':'Le projet atteint votre seuil de sécurité.';
  el('insight').textContent=`${status} Écart net de la protection : ${fmt((serviceUn-serviceHg)/1e6,1)} M XAF ${serviceUn>=serviceHg?'économisés':'de surcoût (valeur négative)'} sur 15 ans.`;
}

/* wire the sliders */
['shock','cov','cost','thr'].forEach(id=>el(id).addEventListener('input',render));
el('reset').addEventListener('click',()=>{['shock','cov','cost','thr'].forEach((id,k)=>el(id).value=[20,50,0,1.2][k]);render();});
render();
if (typeof window !== 'undefined') window.mcSimulate=simulate;
