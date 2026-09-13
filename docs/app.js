const AGENTS = [
  { id: "market_scout", num: "01", name: "Market Scout", icon: "🔭" },
  { id: "technical", num: "02", name: "Technical Analyst", icon: "📈" },
  { id: "fundamental", num: "03", name: "Fundamental Analyst", icon: "📊" },
  { id: "news", num: "04", name: "News Analyst", icon: "📰" },
  { id: "quant", num: "05", name: "Quant Analyst", icon: "🧮" },
  { id: "risk", num: "06", name: "Risk Manager", icon: "🛡️" },
  { id: "portfolio", num: "07", name: "Portfolio Manager", icon: "📋" },
];

const SAMPLE_FILES = {
  tsla: "./sample-analysis.json",
  nvda: "./sample-nvda.json",
  reject: "./sample-reject.json",
};

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
};

let activeExampleId = "tsla";
let galleryMeta = [];

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

function toneClass(text) {
  const t = (text || "").toUpperCase();
  if (t.includes("BUY") || t.includes("APPROVE") || t.includes("BULL")) return "bull";
  if (t.includes("SELL") || t.includes("REJECT") || t.includes("PASS") || t.includes("AVOID") || t.includes("BEAR")) return "bear";
  return "";
}

function renderSkeleton(status = "pending") {
  els.stack.innerHTML = AGENTS.map((a) => agentCardHtml(a, {
    status,
    verdict: { label: "—", detail: "Waiting…", tone: "neutral" },
    rationale: "",
  })).join("");
  bindCardToggles();
}

function renderAgents(agents) {
  const byId = Object.fromEntries((agents || []).map((a) => [a.id, a]));
  els.stack.innerHTML = AGENTS.map((meta) => {
    const a = byId[meta.id] || { status: "pending", verdict: { label: "—", detail: "", tone: "neutral" }, rationale: "" };
    return agentCardHtml(meta, a);
  }).join("");
  bindCardToggles();
  const first = els.stack.querySelector('.agent-card[data-status="done"]');
  if (first) first.classList.add("open");
}

function renderMemo(data) {
  const memo = data.memo || {};
  const quote = data.quote || {};
  const ticker = data.ticker || "—";
  const rec = memo.recommendation || "—";
  const rejected = Boolean(memo.trade_rejected) || /REJECT|PASS \(RISK/i.test(rec);

  els.memoHero.classList.add("filled");
  els.memoHero.classList.toggle("rejected", rejected);
  els.memoHero.innerHTML = `
    <div>
      <p class="ticker-lg">${escapeHtml(ticker)}</p>
      <p class="quote-line">${escapeHtml(quote.name || "")} · $${quote.price ?? "—"} · ${quote.change_pct ?? "—"}%</p>
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
  els.mExp.className = Number(memo.expected_return) >= 0 ? "bull" : Number(memo.expected_return) < 0 ? "bear" : "";

  if (memo.thesis || memo.rejection_reason) {
    els.blockThesis.hidden = false;
    const bits = [];
    if (memo.rejection_reason) {
      bits.push(`Risk rejection: ${memo.rejection_reason}`);
    }
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

function exampleCardHtml(ex, active) {
  const chips = (ex.chips || [])
    .map(
      (c) =>
        `<span class="ex-chip ${c.tone || "neutral"}"><em>${escapeHtml(c.agent)}</em>${escapeHtml(c.label)}</span>`
    )
    .join("");
  return `
    <button type="button" class="example-card ${active ? "active" : ""} tone-${ex.tone || "neutral"}" data-example="${escapeHtml(ex.id)}" aria-pressed="${active ? "true" : "false"}">
      <div class="example-top">
        <span class="example-letter">${escapeHtml((ex.title || "").split("—")[0].trim() || "Sample")}</span>
        <span class="bias-badge ${ex.tone || "neutral"}">${escapeHtml(ex.badge || "—")}</span>
      </div>
      <h3><span class="ex-ticker">${escapeHtml(ex.ticker)}</span> <span class="ex-name">${escapeHtml(ex.name || "")}</span></h3>
      <p class="example-summary">${escapeHtml(ex.summary || "")}</p>
      <div class="ex-chips" aria-label="Agent verdicts">${chips}</div>
      <div class="memo-callout ${ex.tone || "neutral"}">${escapeHtml(ex.memo_callout || "")}</div>
    </button>
  `;
}

function renderGallery(examples) {
  if (!els.examplesGrid) return;
  galleryMeta = examples || [];
  els.examplesGrid.innerHTML = galleryMeta
    .map((ex) => exampleCardHtml(ex, ex.id === activeExampleId))
    .join("");
  els.examplesGrid.querySelectorAll(".example-card").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.getAttribute("data-example");
      if (id) loadSample(id, { scroll: true });
    });
  });
}

function setActiveCard(id) {
  if (!els.examplesGrid) return;
  els.examplesGrid.querySelectorAll(".example-card").forEach((btn) => {
    const on = btn.getAttribute("data-example") === id;
    btn.classList.toggle("active", on);
    btn.setAttribute("aria-pressed", on ? "true" : "false");
  });
}

async function loadGallery() {
  if (!els.examplesGrid) return;
  try {
    const res = await fetch("./sample-examples.json", { cache: "no-cache" });
    if (!res.ok) throw new Error("Could not load sample-examples.json");
    const data = await res.json();
    renderGallery(data.examples || []);
  } catch (err) {
    els.examplesGrid.innerHTML = `<p class="muted">Sample gallery unavailable: ${escapeHtml(err.message)}</p>`;
  }
}

async function loadSample(exampleId = "tsla", opts = {}) {
  const id = SAMPLE_FILES[exampleId] ? exampleId : "tsla";
  activeExampleId = id;
  setActiveCard(id);
  const file = SAMPLE_FILES[id];
  const meta = galleryMeta.find((e) => e.id === id);
  els.status.textContent = `Loading ${meta ? meta.ticker : id} sample…`;
  if (els.demoBannerDetail) {
    els.demoBannerDetail.textContent = meta
      ? `${meta.title}. ${meta.summary}`
      : "Bundled demo sample — not live data.";
  }
  renderSkeleton("running");
  try {
    const res = await fetch(file, { cache: "no-cache" });
    if (!res.ok) throw new Error(`Could not load ${file}`);
    const data = await res.json();
    renderAgents(data.agents);
    renderMemo(data);
    els.modePill.textContent = "SAMPLE DEMO";
    els.modePill.dataset.mode = "SAMPLE DEMO";
    const title = data.example_title || (meta && meta.title) || `Sample — ${data.ticker}`;
    els.status.textContent = `${title} · bundled demo data, not live`;
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
