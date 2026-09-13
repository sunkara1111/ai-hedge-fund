const AGENTS = [
  { id: "market_scout", num: "01", name: "Market Scout", icon: "🔭", short: "Scout" },
  { id: "technical", num: "02", name: "Technical Analyst", icon: "📈", short: "Tech" },
  { id: "fundamental", num: "03", name: "Fundamental Analyst", icon: "📊", short: "Fund" },
  { id: "news", num: "04", name: "News Analyst", icon: "📰", short: "News" },
  { id: "quant", num: "05", name: "Quant Analyst", icon: "🧮", short: "Quant" },
  { id: "risk", num: "06", name: "Risk Manager", icon: "🛡️", short: "Risk" },
  { id: "portfolio", num: "07", name: "Portfolio Manager", icon: "📋", short: "PM" },
];

const SAMPLE_FILES = {
  tsla: "./sample-analysis.json?v=20260913b",
  nvda: "./sample-nvda.json?v=20260913b",
  reject: "./sample-reject.json?v=20260913b",
};

const CACHE_BUST = "20260913b";

const els = {
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
  examplesGrid: document.getElementById("examples-grid"),
  demoBannerDetail: document.getElementById("demo-banner-detail"),
  combinedBanner: document.getElementById("combined-banner"),
};

let activeExampleId = "tsla";
let galleryMeta = [];
const sampleCache = {};

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function toneClass(text) {
  const t = (text || "").toUpperCase();
  if (t.includes("BUY") || t.includes("APPROVE") || t.includes("BULL")) return "bull";
  if (t.includes("SELL") || t.includes("REJECT") || t.includes("PASS") || t.includes("AVOID") || t.includes("BEAR")) return "bear";
  return "neutral";
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

function defaultMonitor(meta, agent) {
  const verdict = agent.verdict || {};
  return {
    screen_title: meta.name.toUpperCase(),
    chart: { kind: "sparkline", points: [42, 44, 43, 47, 49, 48, 52, 51, 55] },
    metrics: [
      { k: "Status", v: agent.status || "—" },
      { k: "Detail", v: (verdict.detail || "—").slice(0, 18) },
      { k: "Score", v: verdict.score != null ? String(verdict.score) : "—" },
    ],
    gauge: verdict.score != null ? { value: Number(verdict.score), max: 100, label: "Score" } : null,
    pills: [{ label: verdict.label || "—", tone: verdict.tone || "neutral" }],
    rationale_short: (agent.rationale || "Waiting for agent output.").split("\n")[0].slice(0, 110),
  };
}

function agentCardHtml(meta, agent) {
  const status = agent.status || "pending";
  const verdict = agent.verdict || {};
  const mon = agent.monitor || defaultMonitor(meta, agent);
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

function renderSkeleton(status = "pending") {
  els.stack.innerHTML = AGENTS.map((a) =>
    agentCardHtml(a, {
      status,
      verdict: { label: "—", detail: "Waiting…", tone: "neutral" },
      rationale: "",
    })
  ).join("");
  bindCardToggles();
}

function renderAgents(agents) {
  const byId = Object.fromEntries((agents || []).map((a) => [a.id, a]));
  els.stack.innerHTML = AGENTS.map((meta) => {
    const a = byId[meta.id] || {
      status: "pending",
      verdict: { label: "—", detail: "", tone: "neutral" },
      rationale: "",
    };
    return agentCardHtml(meta, a);
  }).join("");
  bindCardToggles();
  const first = els.stack.querySelector('.agent-card[data-status="done"]');
  if (first) first.classList.add("open");
}

function renderCombinedBanner(data) {
  const banner = data.combined_banner;
  const host = els.combinedBanner;
  if (!host) return;
  if (!banner) {
    host.hidden = true;
    host.innerHTML = "";
    return;
  }
  const tone = banner.tone || toneClass(banner.recommendation);
  const stats = (banner.stats || [])
    .map((s) => `<div class="combo-stat"><span>${escapeHtml(s.k)}</span><strong>${escapeHtml(s.v)}</strong></div>`)
    .join("");
  host.hidden = false;
  host.className = `combined-banner tone-${tone}`;
  host.innerHTML = `
    <div class="combo-label">
      <span>COMBINED RESULT</span>
      <em>${escapeHtml(banner.subtitle || "Final memo")}</em>
    </div>
    <div class="combo-headline">
      <strong>${escapeHtml(banner.headline || "")}</strong>
      <span class="rec-badge ${tone}">${escapeHtml(banner.recommendation || "—")}</span>
    </div>
    <div class="combo-stats">${stats}</div>
  `;
}

function renderMemo(data) {
  const memo = data.memo || {};
  const quote = data.quote || {};
  const ticker = data.ticker || "—";
  const rec = memo.recommendation || "—";
  const rejected = Boolean(memo.trade_rejected) || /REJECT|PASS \(RISK/i.test(rec);

  els.memoHero.classList.add("filled");
  els.memoHero.classList.toggle("rejected", rejected);
  const chg = quote.change_pct;
  const chgCls = Number(chg) >= 0 ? "bull" : Number(chg) < 0 ? "bear" : "";
  els.memoHero.innerHTML = `
    <div>
      <p class="hero-kicker">Dinesh AI Fund · sample outcome</p>
      <p class="ticker-lg">${escapeHtml(ticker)}</p>
      <p class="quote-line">${escapeHtml(quote.name || "")} · $${quote.price ?? "—"} · <span class="${chgCls}">${chg ?? "—"}%</span></p>
    </div>
    <div class="rec-badge ${toneClass(rec)}">${escapeHtml(rec)}</div>
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
  els.mExp.className =
    Number(memo.expected_return) >= 0 ? "bull" : Number(memo.expected_return) < 0 ? "bear" : "";

  if (memo.thesis || memo.rejection_reason) {
    els.blockThesis.hidden = false;
    const bits = [];
    if (memo.rejection_reason) bits.push(`Risk rejection: ${memo.rejection_reason}`);
    if (memo.thesis) bits.push(memo.thesis);
    els.mThesis.textContent = bits.join("\n\n");
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
    els.mCatalysts.innerHTML = cats.length
      ? cats.map((c) => `<li>${escapeHtml(c)}</li>`).join("")
      : "<li>—</li>";
    els.mRisks.innerHTML = risks.length
      ? risks.map((r) => `<li>${escapeHtml(r)}</li>`).join("")
      : "<li>—</li>";
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
        (o) =>
          `<div class="scan-row"><span class="rank">#${o.rank}</span><span class="sym">${escapeHtml(o.ticker)}</span><span>score ${o.opportunity_score}</span><span>${o.change_pct}%</span></div>`
      )
      .join("");
  } else {
    els.scanBlock.hidden = true;
  }

  renderCombinedBanner(data);
}

function miniFloorHtml(chip, idx) {
  const num = String(idx + 1).padStart(2, "0");
  const tone = chip.tone || "neutral";
  return `
    <div class="mini-floor tone-${tone}">
      <div class="mini-floor-head">
        <span class="mini-num">${num}</span>
        <strong>${escapeHtml(chip.agent)}</strong>
      </div>
      <div class="mini-screen">
        <div class="mini-bars" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></div>
        <span class="bias-pill ${tone}">${escapeHtml(chip.label)}</span>
      </div>
    </div>
  `;
}

function exampleCardHtml(ex, active, sample) {
  const tone = ex.tone || "neutral";
  const price = ex.price != null ? `$${ex.price}` : "";
  const chg = ex.change_pct;
  const chgTxt = chg != null ? `${Number(chg) >= 0 ? "+" : ""}${chg}%` : "";
  const chgCls = Number(chg) >= 0 ? "bull" : "bear";
  const floors = (ex.chips || []).map((c, i) => miniFloorHtml(c, i)).join("");
  const agents = (sample && sample.agents) || [];
  let monitorStrip = "";
  if (agents.length) {
    monitorStrip = `<div class="ex-monitor-strip">${agents
      .map((a, i) => {
        const mon = a.monitor || {};
        const t = (a.verdict && a.verdict.tone) || "neutral";
        return `<div class="ex-mon tone-${t}">
          <div class="ex-mon-top"><span>${String(i + 1).padStart(2, "0")}</span><em>${escapeHtml((a.name || "").split(" ")[0])}</em></div>
          <div class="ex-mon-chart">${chartHtml(mon.chart, t)}</div>
          <span class="bias-pill ${t}">${escapeHtml((a.verdict && a.verdict.label) || "—")}</span>
        </div>`;
      })
      .join("")}</div>`;
  } else {
    monitorStrip = `<div class="mini-floors">${floors}</div>`;
  }

  const bannerTone = tone;
  const edge = ex.edge != null ? ex.edge : "";
  return `
    <article class="example-showcase ${active ? "active" : ""} tone-${tone}" data-example="${escapeHtml(ex.id)}" aria-pressed="${active ? "true" : "false"}">
      <button type="button" class="example-hit" data-example="${escapeHtml(ex.id)}" aria-label="Open ${escapeHtml(ex.ticker)} deep dive">
        <div class="ex-hero">
          <div class="ex-hero-left">
            <span class="ex-tag">${escapeHtml(ex.hero_tag || ex.title || "SAMPLE")}</span>
            <h3><span class="ex-ticker">${escapeHtml(ex.ticker)}</span> <span class="ex-name">${escapeHtml(ex.name || "")}</span></h3>
            <p class="ex-price">${escapeHtml(price)} <span class="${chgCls}">${escapeHtml(chgTxt)}</span>${edge !== "" ? ` · edge ${escapeHtml(String(edge))}` : ""}</p>
            <p class="example-summary">${escapeHtml(ex.story || ex.summary || "")}</p>
          </div>
          <div class="ex-hero-right">
            <span class="bias-badge ${tone}">${escapeHtml(ex.badge || "—")}</span>
            <span class="ex-flow">Ticker → 7 agents → memo</span>
          </div>
        </div>
        ${monitorStrip}
        <div class="ex-combined tone-${bannerTone}">
          <div>
            <span class="combo-kicker">COMBINED RESULT</span>
            <strong>${escapeHtml(ex.memo_callout || ex.badge || "")}</strong>
          </div>
          <span class="ex-cta">Open deep dive →</span>
        </div>
      </button>
    </article>
  `;
}

function renderGallery(examples) {
  if (!els.examplesGrid) return;
  galleryMeta = examples || [];
  els.examplesGrid.innerHTML = galleryMeta
    .map((ex) => exampleCardHtml(ex, ex.id === activeExampleId, sampleCache[ex.id]))
    .join("");
  els.examplesGrid.querySelectorAll(".example-hit").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.getAttribute("data-example");
      if (id) loadSample(id, { scroll: true });
    });
  });
}

function setActiveCard(id) {
  if (!els.examplesGrid) return;
  els.examplesGrid.querySelectorAll(".example-showcase").forEach((card) => {
    const on = card.getAttribute("data-example") === id;
    card.classList.toggle("active", on);
    card.setAttribute("aria-pressed", on ? "true" : "false");
  });
}

async function fetchSample(id) {
  if (sampleCache[id]) return sampleCache[id];
  const file = SAMPLE_FILES[id];
  if (!file) throw new Error("Unknown sample");
  const res = await fetch(file, { cache: "no-cache" });
  if (!res.ok) throw new Error(`Could not load ${file}`);
  const data = await res.json();
  sampleCache[id] = data;
  return data;
}

async function loadGallery() {
  if (!els.examplesGrid) return;
  try {
    const res = await fetch(`./sample-examples.json?v=${CACHE_BUST}`, { cache: "no-cache" });
    if (!res.ok) throw new Error("Could not load sample-examples.json");
    const data = await res.json();
    const examples = data.examples || [];
    await Promise.all(
      examples.map(async (ex) => {
        try {
          await fetchSample(ex.id);
        } catch (_) {
          /* gallery still works with chips */
        }
      })
    );
    renderGallery(examples);
  } catch (err) {
    els.examplesGrid.innerHTML = `<p class="muted">Sample gallery unavailable: ${escapeHtml(err.message)}</p>`;
  }
}

async function loadSample(exampleId = "tsla", opts = {}) {
  const id = SAMPLE_FILES[exampleId] ? exampleId : "tsla";
  activeExampleId = id;
  setActiveCard(id);
  const meta = galleryMeta.find((e) => e.id === id);
  els.status.textContent = `Loading ${meta ? meta.ticker : id} sample…`;
  if (els.demoBannerDetail) {
    els.demoBannerDetail.textContent = meta
      ? `${meta.title}. ${meta.story || meta.summary}`
      : "Bundled demo sample — not live data.";
  }
  renderSkeleton("running");
  try {
    const data = await fetchSample(id);
    renderAgents(data.agents);
    renderMemo(data);
    els.modePill.textContent = "SAMPLE DEMO";
    els.modePill.dataset.mode = "SAMPLE DEMO";
    const title = data.example_title || (meta && meta.title) || `Sample — ${data.ticker}`;
    els.status.textContent = `${title} · bundled demo data, not live`;
    renderGallery(galleryMeta);
    if (opts.scroll) {
      document.getElementById("demo")?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  } catch (err) {
    els.status.textContent = `Error: ${err.message}`;
    els.modePill.textContent = "ERROR";
    renderSkeleton("pending");
  }
}

function showToast(msg) {
  const existing = document.querySelector(".toast");
  if (existing) existing.remove();
  const t = document.createElement("div");
  t.className = "toast";
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 2200);
}

function bindCtas() {
  const scrollToExamples = (event) => {
    event.preventDefault();
    document.getElementById("examples")?.scrollIntoView({ behavior: "smooth", block: "start" });
  };
  document.getElementById("cta-demo")?.addEventListener("click", scrollToExamples);
  document.getElementById("cta-load")?.addEventListener("click", scrollToExamples);
}

document.getElementById("btn-copy-share")?.addEventListener("click", async () => {
  const text = document.getElementById("share-text")?.textContent?.trim() || "";
  try {
    await navigator.clipboard.writeText(text);
    showToast("Share text copied");
  } catch {
    showToast("Copy failed — select the share line instead");
  }
});

bindCtas();
renderSkeleton("pending");
loadGallery().then(() => loadSample("tsla"));

/* Honor ?q= from WebSite SearchAction — scroll to examples (static showcase). */
(function honorSearchQuery() {
  try {
    const q = new URLSearchParams(window.location.search).get("q");
    if (!q) return;
    const target = document.getElementById("examples") || document.getElementById("faq");
    if (target) {
      requestAnimationFrame(() => target.scrollIntoView({ behavior: "smooth", block: "start" }));
    }
  } catch (_) { /* ignore */ }
})();
