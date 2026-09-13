const AGENTS = [
  { id: "market_scout", num: "01", name: "Market Scout", icon: "🔭" },
  { id: "technical", num: "02", name: "Technical", icon: "📈" },
  { id: "fundamental", num: "03", name: "Fundamental", icon: "📊" },
  { id: "news", num: "04", name: "News", icon: "📰" },
  { id: "quant", num: "05", name: "Quant", icon: "🧮" },
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
  const score =
    verdict.score !== null && verdict.score !== undefined
      ? ` · score ${verdict.score}`
      : "";
  return `
    <article class="agent-card" data-id="${meta.id}" data-status="${status}">
      <button type="button" class="agent-head" aria-expanded="false">
        <div style="display:flex;align-items:center;gap:0.75rem;">
          <span class="agent-num">${meta.num}</span>
          <span class="agent-icon" aria-hidden="true">${meta.icon}</span>
          <div class="agent-meta">
            <strong>${meta.name}</strong>
            <span>${verdict.detail || ""}${score}</span>
          </div>
        </div>
        <div class="agent-side">
          <span class="status-chip ${status}">${status}</span>
          <span class="verdict-chip ${verdict.tone || "neutral"}">${verdict.label || "—"}</span>
        </div>
      </button>
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
