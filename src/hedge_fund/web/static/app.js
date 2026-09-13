const AGENTS = [
  { id: "market_scout", num: "01", name: "Market Scout", icon: "🔭" },
  { id: "technical", num: "02", name: "Technical Analyst", icon: "📈" },
  { id: "fundamental", num: "03", name: "Fundamental Analyst", icon: "📊" },
  { id: "news", num: "04", name: "News Analyst", icon: "📰" },
  { id: "quant", num: "05", name: "Quant Analyst", icon: "🧮" },
  { id: "risk", num: "06", name: "Risk Manager", icon: "🛡️" },
  { id: "portfolio", num: "07", name: "Portfolio Manager", icon: "📋" },
];

const els = {
  form: document.getElementById("analyze-form"),
  ticker: document.getElementById("ticker"),
  demo: document.getElementById("demo"),
  analyzeBtn: document.getElementById("btn-analyze"),
  scanBtn: document.getElementById("btn-scan"),
  stack: document.getElementById("agent-stack"),
  status: document.getElementById("status-line"),
  modePill: document.getElementById("mode-pill"),
  memoHero: document.getElementById("memo-hero"),
  memoGrid: document.getElementById("memo-grid"),
  blockThesis: document.getElementById("block-thesis"),
  blockScenarios: document.getElementById("block-scenarios"),
  blockLists: document.getElementById("block-lists"),
  blockFull: document.getElementById("block-full"),
  scanBlock: document.getElementById("scan-block"),
  scanList: document.getElementById("scan-list"),
  mRec: document.getElementById("m-rec"),
  mAlloc: document.getElementById("m-alloc"),
  mEdge: document.getElementById("m-edge"),
  mExp: document.getElementById("m-exp"),
  mThesis: document.getElementById("m-thesis"),
  mScenarios: document.getElementById("m-scenarios"),
  mCatalysts: document.getElementById("m-catalysts"),
  mRisks: document.getElementById("m-risks"),
  mFull: document.getElementById("m-full"),
};

function initFromQuery() {
  const q = new URLSearchParams(window.location.search);
  if (q.has("demo")) {
    const v = q.get("demo");
    els.demo.checked = !(v === "0" || v === "false");
  }
  if (q.get("ticker")) els.ticker.value = q.get("ticker").toUpperCase();
}

function renderSkeleton(status = "pending") {
  els.stack.innerHTML = AGENTS.map((a) => agentCardHtml(a, {
    status,
    verdict: { label: "—", detail: "Waiting…", tone: "neutral" },
    rationale: "",
  })).join("");
  bindCardToggles();
}

function agentCardHtml(meta, agent) {
  const status = agent.status || "pending";
  const verdict = agent.verdict || {};
  const mon = synthesizeMonitor(meta, agent);
  const tone = verdict.tone || "neutral";
  return `
    <article class="agent-card monitor-card" data-id="${meta.id}" data-status="${status}" data-tone="${tone}">
      <button type="button" class="agent-head" aria-expanded="false">
        <div class="floor-id">
          <span class="agent-num">${meta.num}</span>
          <span class="agent-icon" aria-hidden="true">${meta.icon}</span>
        </div>
        <div class="agent-meta">
          <strong>${meta.name}</strong>
          <span class="screen-title">${escapeHtml(mon.screen_title || "")}</span>
        </div>
        <div class="agent-side">
          <span class="status-chip ${status}">${status}</span>
          <span class="verdict-chip ${tone}">${escapeHtml(verdict.label || "—")}</span>
        </div>
      </button>
      <div class="monitor-screen">
        <div class="monitor-top">
          <span class="monitor-dot"></span>
          <span class="monitor-dot"></span>
          <span class="monitor-dot"></span>
          <em>${escapeHtml(mon.screen_title || "MONITOR")}</em>
        </div>
        <div class="monitor-body">
          <div class="monitor-chart">${chartHtml(mon.chart, tone)}</div>
          <div class="monitor-side">
            ${gaugeSvg(mon.gauge)}
            <div class="metric-rows">${metricsHtml(mon.metrics)}</div>
          </div>
        </div>
        <div class="monitor-pills">${pillsHtml(mon.pills)}</div>
        <p class="monitor-rationale">${escapeHtml(mon.rationale_short || "")}</p>
      </div>
      <div class="agent-body">
        <pre class="rationale">${escapeHtml(agent.rationale || "No rationale yet.")}</pre>
      </div>
    </article>
  `;
}

function bindCardToggles() {
  els.stack.querySelectorAll(".agent-head").forEach((btn) => {
    btn.addEventListener("click", () => {
      const card = btn.closest(".agent-card");
      const open = card.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}



function sparklineSvg(points, opts = {}) {
  const pts = (points || []).map(Number).filter((n) => !Number.isNaN(n));
  if (pts.length < 2) return "";
  const w = opts.w || 160;
  const h = opts.h || 48;
  const min = Math.min(...pts);
  const max = Math.max(...pts);
  const span = max - min || 1;
  const step = w / (pts.length - 1);
  const coords = pts
    .map((p, i) => {
      const x = i * step;
      const y = h - ((p - min) / span) * (h - 6) - 3;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
  const last = pts[pts.length - 1];
  const first = pts[0];
  const up = last >= first;
  const stroke = opts.stroke || (up ? "#3dcf7a" : "#ff5a5a");
  const fill = opts.fill || (up ? "rgba(61,207,122,0.18)" : "rgba(255,90,90,0.15)");
  const area = `0,${h} ${coords} ${w},${h}`;
  return `<svg class="spark" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" aria-hidden="true"><polygon points="${area}" fill="${fill}"/><polyline points="${coords}" fill="none" stroke="${stroke}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
}

function candlesSvg(candles, opts = {}) {
  const rows = candles || [];
  if (!rows.length) return "";
  const w = opts.w || 160;
  const h = opts.h || 52;
  const pad = 4;
  const all = rows.flatMap((c) => [c.h, c.l]);
  const min = Math.min(...all);
  const max = Math.max(...all);
  const span = max - min || 1;
  const slot = (w - pad * 2) / rows.length;
  const y = (v) => h - pad - ((v - min) / span) * (h - pad * 2);
  const bars = rows
    .map((c, i) => {
      const x = pad + i * slot + slot / 2;
      const up = c.c >= c.o;
      const color = up ? "#3dcf7a" : "#ff5a5a";
      const y1 = y(c.h);
      const y2 = y(c.l);
      const yo = y(c.o);
      const yc = y(c.c);
      const top = Math.min(yo, yc);
      const bh = Math.max(2, Math.abs(yc - yo));
      const bw = Math.max(2, slot * 0.45);
      return `<line x1="${x}" y1="${y1}" x2="${x}" y2="${y2}" stroke="${color}" stroke-width="1"/><rect x="${x - bw / 2}" y="${top}" width="${bw}" height="${bh}" fill="${color}"/>`;
    })
    .join("");
  return `<svg class="spark candles" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" aria-hidden="true">${bars}</svg>`;
}

function barsSvg(bars, opts = {}) {
  const rows = bars || [];
  if (!rows.length) return "";
  const w = opts.w || 160;
  const h = opts.h || 52;
  const max = Math.max(...rows.map((b) => Number(b.v) || 0), 1);
  const slot = w / rows.length;
  const rects = rows
    .map((b, i) => {
      const v = Number(b.v) || 0;
      const bh = Math.max(4, (v / max) * (h - 14));
      const x = i * slot + slot * 0.18;
      const bw = slot * 0.64;
      const tone = v >= 55 ? "#3dcf7a" : v >= 45 ? "#ff9a3c" : "#ff5a5a";
      return `<rect x="${x}" y="${h - bh - 2}" width="${bw}" height="${bh}" rx="2" fill="${tone}"/><text x="${x + bw / 2}" y="${h}" text-anchor="middle" fill="#9a8f82" font-size="7">${escapeHtml(b.t || "")}</text>`;
    })
    .join("");
  return `<svg class="spark bars" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" aria-hidden="true">${rects}</svg>`;
}

function donutSvg(value, opts = {}) {
  const v = Math.max(0, Math.min(100, Number(value) || 0));
  const size = opts.size || 56;
  const r = 20;
  const c = 2 * Math.PI * r;
  const dash = (v / 100) * c;
  const color = v >= 65 ? "#3dcf7a" : v >= 50 ? "#ff9a3c" : "#ff5a5a";
  return `<svg class="donut" viewBox="0 0 56 56" width="${size}" height="${size}" aria-hidden="true"><circle cx="28" cy="28" r="${r}" fill="none" stroke="#3a3028" stroke-width="6"/><circle cx="28" cy="28" r="${r}" fill="none" stroke="${color}" stroke-width="6" stroke-linecap="round" stroke-dasharray="${dash} ${c - dash}" transform="rotate(-90 28 28)"/><text x="28" y="31" text-anchor="middle" fill="#fff8f0" font-size="11" font-weight="700">${Math.round(v)}%</text></svg>`;
}

function gaugeSvg(gauge) {
  if (!gauge) return "";
  const max = gauge.max || 100;
  const v = Math.max(0, Math.min(max, Number(gauge.value) || 0));
  const pct = (v / max) * 100;
  const invert = gauge.invert;
  const color = invert
    ? pct >= 60
      ? "#ff5a5a"
      : pct >= 40
        ? "#ff9a3c"
        : "#3dcf7a"
    : pct >= 65
      ? "#3dcf7a"
      : pct >= 45
        ? "#ff9a3c"
        : "#ff5a5a";
  return `<div class="gauge" title="${escapeHtml(gauge.label || "")}"><div class="gauge-ring" style="--pct:${pct};--gcolor:${color}"><strong>${Math.round(v)}</strong></div><span>${escapeHtml(gauge.label || "")}</span></div>`;
}

function chartHtml(chart, tone) {
  if (!chart) return sparklineSvg([40, 42, 41, 45, 48, 47, 52, 50]);
  const kind = chart.kind || "sparkline";
  if (kind === "candles" && chart.candles) return candlesSvg(chart.candles);
  if ((kind === "bars" || kind === "donut") && chart.bars && chart.bars.length) {
    const left = barsSvg(chart.bars);
    const right = chart.donut ? donutSvg(chart.donut.value) : "";
    return `<div class="chart-combo">${left}${right}</div>`;
  }
  if (kind === "donut" && chart.donut) {
    return `<div class="chart-combo">${sparklineSvg(chart.points)}${donutSvg(chart.donut.value)}</div>`;
  }
  if (kind === "drawdown") return sparklineSvg(chart.points, { stroke: "#ff5a5a", fill: "rgba(255,90,90,0.16)" });
  if (chart.feed && chart.feed.length) {
    const feed = chart.feed
      .slice(0, 2)
      .map((f) => `<div class="feed-row"><span>${escapeHtml(f.t)}</span><em>${escapeHtml(f.when)}</em></div>`)
      .join("");
    return `<div class="feed-panel">${feed}${sparklineSvg(chart.points, { w: 140, h: 28 })}</div>`;
  }
  const stroke = tone === "bear" ? "#ff5a5a" : tone === "bull" ? "#3dcf7a" : "#ff9a3c";
  return sparklineSvg(chart.points, { stroke });
}

function metricsHtml(metrics) {
  return (metrics || [])
    .map((m) => `<div class="metric"><span>${escapeHtml(m.k)}</span><strong>${escapeHtml(m.v)}</strong></div>`)
    .join("");
}

function pillsHtml(pills) {
  return (pills || [])
    .map((p) => `<span class="bias-pill ${p.tone || "neutral"}">${escapeHtml(p.label)}</span>`)
    .join("");
}

function synthesizeMonitor(meta, agent) {
  if (agent.monitor) return agent.monitor;
  const verdict = agent.verdict || {};
  const score = verdict.score;
  const tone = verdict.tone || "neutral";
  const seed = (meta.num || "01").charCodeAt(1) + (score || 40);
  const points = Array.from({ length: 12 }, (_, i) => 40 + ((seed * (i + 3)) % 17) - 6 + i * 0.4);
  return {
    screen_title: (meta.name || "AGENT").toUpperCase(),
    chart: { kind: "sparkline", points },
    metrics: [
      { k: "Status", v: agent.status || "—" },
      { k: "Detail", v: String(verdict.detail || "—").slice(0, 18) },
      { k: "Score", v: score != null ? String(score) : "—" },
    ],
    gauge: score != null ? { value: Number(score), max: 100, label: "Score" } : null,
    pills: [{ label: verdict.label || "—", tone }],
    rationale_short: String(agent.rationale || "Agent output.").split("\n")[0].slice(0, 110),
  };
}

function setBusy(busy, label = "Running pipeline…") {
  els.analyzeBtn.disabled = busy;
  els.scanBtn.disabled = busy;
  els.modePill.textContent = busy ? "RUNNING" : els.modePill.dataset.mode || "IDLE";
  els.modePill.classList.toggle("busy", busy);
  if (busy) els.status.textContent = label;
}

function toneClass(text) {
  const t = (text || "").toUpperCase();
  if (t.includes("BUY") || t.includes("APPROVE") || t.includes("BULL")) return "bull";
  if (t.includes("SELL") || t.includes("REJECT") || t.includes("PASS") || t.includes("AVOID") || t.includes("BEAR")) return "bear";
  return "";
}

function renderAgents(agents) {
  const byId = Object.fromEntries((agents || []).map((a) => [a.id, a]));
  els.stack.innerHTML = AGENTS.map((meta) => {
    const a = byId[meta.id] || { status: "pending", verdict: { label: "—", detail: "", tone: "neutral" }, rationale: "" };
    return agentCardHtml(meta, a);
  }).join("");
  bindCardToggles();
  // auto-open portfolio + first done agent lightly
  const first = els.stack.querySelector('.agent-card[data-status="done"]');
  if (first) first.classList.add("open");
}

function pct(v, digits = 2) {
  if (v === null || v === undefined || Number.isNaN(Number(v))) return "—";
  return `${(Number(v) * (Math.abs(Number(v)) <= 1 ? 100 : 1)).toFixed(digits)}%`;
}

function renderMemo(data) {
  const memo = data.memo || {};
  const quote = data.quote || {};
  const ticker = data.ticker || "—";
  const rec = memo.recommendation || "—";

  els.memoHero.classList.add("filled");
  els.memoHero.innerHTML = `
    <div>
      <p class="ticker-lg">${escapeHtml(ticker)}</p>
      <p class="quote-line">${escapeHtml(quote.name || "")} · $${quote.price ?? "—"} · ${quote.change_pct ?? "—"}%</p>
    </div>
    <div class="rec-badge">${escapeHtml(rec)}</div>
  `;

  els.memoGrid.hidden = false;
  els.mRec.textContent = rec;
  els.mRec.className = toneClass(rec);
  const allocPct = memo.allocation_pct;
  const allocDollars = memo.allocation_dollars;
  els.mAlloc.textContent =
    allocPct || allocPct === 0
      ? `${(Number(allocPct) * 100).toFixed(2)}% · $${Number(allocDollars || 0).toLocaleString()}`
      : "—";
  els.mEdge.textContent =
    memo.edge_score != null ? `${memo.edge_score} / ${memo.win_probability ?? "—"}%` : "—";
  els.mExp.textContent = memo.expected_return != null ? `${memo.expected_return}%` : "—";
  els.mExp.className = Number(memo.expected_return) >= 0 ? "bull" : Number(memo.expected_return) < 0 ? "bear" : "";

  if (memo.thesis) {
    els.blockThesis.hidden = false;
    els.mThesis.textContent = memo.thesis;
  } else {
    els.blockThesis.hidden = true;
  }

  const scenarios = memo.scenarios || {};
  const keys = ["bull", "base", "bear"].filter((k) => scenarios[k]);
  if (keys.length) {
    els.blockScenarios.hidden = false;
    els.mScenarios.innerHTML = keys
      .map((k) => {
        const s = scenarios[k];
        return `<div class="scenario ${k}"><span class="tag">${k.toUpperCase()}</span><span>$${s.price} (${s.return_pct}%)</span><span>${s.prob ?? "—"}%</span></div>`;
      })
      .join("");
  } else {
    els.blockScenarios.hidden = true;
  }

  const cats = memo.catalysts || [];
  const risks = memo.risks || [];
  if (cats.length || risks.length) {
    els.blockLists.hidden = false;
    els.mCatalysts.innerHTML = cats.length ? cats.map((c) => `<li>${escapeHtml(c)}</li>`).join("") : "<li>—</li>";
    els.mRisks.innerHTML = risks.length ? risks.map((r) => `<li>${escapeHtml(r)}</li>`).join("") : "<li>—</li>";
  } else {
    els.blockLists.hidden = true;
  }

  if (memo.full_memo) {
    els.blockFull.hidden = false;
    els.mFull.textContent = memo.full_memo;
  } else {
    els.blockFull.hidden = true;
  }

  if (data.scan_ranking && data.scan_ranking.length) {
    els.scanBlock.hidden = false;
    els.scanList.innerHTML = data.scan_ranking
      .slice(0, 8)
      .map(
        (o) => `<div class="scan-row"><span class="rank">#${o.rank}</span><span class="sym">${escapeHtml(o.ticker)}</span><span>score ${o.opportunity_score}</span><span>${o.change_pct}%</span></div>`
      )
      .join("");
  } else {
    els.scanBlock.hidden = true;
  }
}

async function runAnalyze(e) {
  if (e) e.preventDefault();
  const ticker = (els.ticker.value || "").trim().toUpperCase();
  if (!ticker) {
    els.status.textContent = "Please enter a ticker.";
    return;
  }
  els.ticker.value = ticker;
  setBusy(true, `Analyzing ${ticker}…`);
  renderSkeleton("running");
  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticker, demo: els.demo.checked }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Analyze failed");
    renderAgents(data.agents);
    renderMemo(data);
    const mode = data.demo ? "DEMO" : "LIVE";
    els.modePill.textContent = mode;
    els.modePill.dataset.mode = mode;
    els.modePill.classList.toggle("live", !data.demo);
    els.status.textContent = `Done — ${data.ticker} · ${data.agents.filter((a) => a.status === "done").length}/7 agents`;
  } catch (err) {
    els.status.textContent = `Error: ${err.message}`;
    els.modePill.textContent = "ERROR";
    renderSkeleton("pending");
  } finally {
    setBusy(false);
  }
}

async function runScan() {
  setBusy(true, "Scanning universe…");
  renderSkeleton("running");
  try {
    const res = await fetch("/api/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ demo: els.demo.checked }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Scan failed");
    if (data.ticker) els.ticker.value = data.ticker;
    renderAgents(data.agents);
    renderMemo(data);
    const mode = data.demo ? "DEMO SCAN" : "LIVE SCAN";
    els.modePill.textContent = mode;
    els.modePill.dataset.mode = mode;
    els.modePill.classList.toggle("live", !data.demo);
    els.status.textContent = `Scan complete — deep-dive on ${data.ticker}`;
  } catch (err) {
    els.status.textContent = `Error: ${err.message}`;
    els.modePill.textContent = "ERROR";
    renderSkeleton("pending");
  } finally {
    setBusy(false);
  }
}

els.form.addEventListener("submit", runAnalyze);
els.scanBtn.addEventListener("click", runScan);
initFromQuery();
renderSkeleton("pending");

// Auto-run if ?autorun=1 or demo query with ticker
const q = new URLSearchParams(window.location.search);
if (q.get("autorun") === "1") {
  runAnalyze();
}

document.getElementById("cta-demo")?.addEventListener("click", (event) => {
  event.preventDefault();
  document.getElementById("demo")?.scrollIntoView({ behavior: "smooth", block: "start" });
  runAnalyze();
});

document.getElementById("btn-copy-share")?.addEventListener("click", async () => {
  const text = document.getElementById("share-text")?.textContent?.trim() || "";
  try {
    await navigator.clipboard.writeText(text);
    showToast("Share text copied");
  } catch {
    showToast("Copy failed — select the share line instead");
  }
});

function showToast(msg) {
  const existing = document.querySelector(".toast");
  if (existing) existing.remove();
  const t = document.createElement("div");
  t.className = "toast";
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 2200);
}
