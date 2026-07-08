const $ = (id) => document.getElementById(id);
const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});
const exactMoney = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 2,
});

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return response.json();
}

function pct(value, digits = 0) {
  return `${(Number(value || 0) * 100).toFixed(digits)}%`;
}

function signedMoney(value) {
  const amount = Number(value || 0);
  return `${amount >= 0 ? "+" : ""}${exactMoney.format(amount)}`;
}

function clsForAmount(value) {
  return Number(value || 0) >= 0 ? "positive" : "negative";
}

function setText(id, value) {
  $(id).textContent = value;
}

function render(snapshot) {
  const { session, portfolio, candidates, decision } = snapshot;
  const primary = decision.primary;
  const executed = snapshot.execution?.executed_action || primary.action;
  const confidence = Number(decision.directional_confidence_score || 0);

  setText("sessionStep", `${session.step} / ${session.max_steps}`);
  $("progressBar").style.width = `${Math.min(100, (session.step / session.max_steps) * 100)}%`;
  setText("portfolioValue", money.format(portfolio.portfolio_value));
  setText("buyingPower", money.format(portfolio.buying_power));
  setText("grossExposure", money.format(portfolio.gross_exposure));
  setText("netProfit", signedMoney(session.net_profit));
  $("netProfit").className = clsForAmount(session.net_profit);

  const actionBadge = $("actionBadge");
  actionBadge.textContent = executed;
  actionBadge.className = `action-badge ${String(executed).toLowerCase()}`;
  setText("primarySymbol", `${primary.symbol}`);
  setText("primaryRationale", primary.rationale);
  setText("confidenceValue", pct(confidence));
  $("confidenceArc").style.strokeDashoffset = 314 - confidence * 314;
  setText(
    "marketClock",
    `${decision.market.venue} · ${decision.market.remaining_steps} steps left`,
  );

  renderReasoning(decision.consensus_reasoning || []);
  renderCandidates(candidates, primary.symbol);
  renderAgents(decision.weighted_votes || []);
  renderCritiques(decision.critiques || []);
  renderEvidence(decision.evidence_used || []);
  renderPositions(portfolio.positions || {});
  renderTrades(snapshot.trade_history || []);
  renderDecisionLog(snapshot.decision_log || []);
}

function renderReasoning(items) {
  $("reasoning").innerHTML = items
    .slice(0, 3)
    .map((item) => `<div>${escapeHtml(item)}</div>`)
    .join("");
}

function renderCandidates(candidates, winner) {
  const sorted = Object.entries(candidates).sort(
    ([, a], [, b]) => Number(b.expected_return) - Number(a.expected_return),
  );
  $("candidateGrid").innerHTML = sorted
    .map(([symbol, item]) => {
      const score = Math.max(0, Math.min(1, Number(item.expected_return) / 0.34));
      const risk = Math.max(0, Math.min(1, Number(item.max_drawdown) / 0.28));
      const sentiment = Math.max(0, Math.min(1, (Number(item.news_sentiment) + 1) / 2));
      return `
        <article class="candidate">
          <header>
            <div>
              <h3>${symbol}</h3>
              <small>${escapeHtml(item.name)} · ${escapeHtml(item.sector)}</small>
            </div>
            <span class="pill">${winner === symbol ? "Lead" : exactMoney.format(item.price)}</span>
          </header>
          <div class="bars">
            ${bar("return", score, pct(item.expected_return, 1))}
            ${bar("risk", risk, pct(item.max_drawdown, 1))}
            ${bar("news", sentiment, pct(item.news_sentiment, 0))}
          </div>
        </article>`;
    })
    .join("");
}

function bar(label, value, shown) {
  return `<div class="bar"><span>${label}</span><i style="--w:${Math.round(value * 100)}%"></i><b>${shown}</b></div>`;
}

function renderAgents(votes) {
  $("agentWeights").innerHTML =
    votes
      .sort((a, b) => Number(b.weight) - Number(a.weight))
      .map(
        (item) => `
          <article class="agent-row">
            <div>
              <b>${title(item.agent_id)}</b>
              <span class="subtle">${item.action} ${item.symbol} · confidence ${pct(item.confidence)}</span>
            </div>
            <span class="pill">${Number(item.weight).toFixed(2)}</span>
          </article>`,
      )
      .join("") || `<div class="empty">No agent votes yet.</div>`;
}

function renderCritiques(critiques) {
  $("critiques").innerHTML =
    critiques
      .map(
        (item) => `
          <article>
            <b>${title(item.critic_id)} · severity ${pct(item.severity)}</b>
            ${escapeHtml(item.comment)}
          </article>`,
      )
      .join("") || `<div class="empty">Critic loop found no blocking concern.</div>`;
}

function renderEvidence(evidence) {
  $("evidence").innerHTML =
    evidence
      .slice(0, 5)
      .map(
        (item) => `
          <article>
            <b>${title(item.source)} · strength ${pct(item.strength)}</b>
            ${escapeHtml(item.summary)}
          </article>`,
      )
      .join("") || `<div class="empty">No evidence selected.</div>`;
}

function renderPositions(positions) {
  const rows = Object.entries(positions);
  $("positions").innerHTML =
    rows
      .map(
        ([symbol, item]) => `
          <div class="row">
            <div>
              <b>${symbol} · ${item.quantity} shares</b>
              <span class="subtle">avg ${exactMoney.format(item.average_price)} · last ${exactMoney.format(item.last_price)}</span>
            </div>
            <span class="${clsForAmount(item.unrealized_pl)}">${signedMoney(item.unrealized_pl)}</span>
          </div>`,
      )
      .join("") || `<div class="empty">No open positions. The committee is waiting for enough edge.</div>`;
}

function renderTrades(trades) {
  $("trades").innerHTML =
    trades
      .slice(0, 6)
      .map(
        (item) => `
          <div class="row">
            <div>
              <b>${item.action} ${item.symbol} · ${item.quantity}</b>
              <span class="subtle">${exactMoney.format(item.price)} · costs ${exactMoney.format(item.costs)}</span>
            </div>
            <span>${money.format(item.notional)}</span>
          </div>`,
      )
      .join("") || `<div class="empty">Trades will appear here after execution.</div>`;
}

function renderDecisionLog(logs) {
  $("decisionLog").innerHTML =
    logs
      .slice(0, 8)
      .map((item) => {
        const decision = item.decision;
        const primary = decision.primary;
        const alternatives = (decision.alternatives_considered || []).join(", ") || "none";
        return `
          <article>
            <b>Step ${item.step}: ${item.executed_action} · ${primary.symbol} · ${pct(decision.directional_confidence_score)}</b>
            <p>${escapeHtml(primary.rationale)}</p>
            <span class="subtle">Alternatives considered: ${escapeHtml(alternatives)} · Expected return ${pct(decision.expected_return, 1)} · Expected drawdown ${pct(decision.expected_drawdown, 1)}</span>
          </article>`;
      })
      .join("") || `<div class="empty">Decision history starts when you run the first committee cycle.</div>`;
}

function title(value) {
  return String(value || "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function load() {
  render(await api("/api/snapshot"));
}

$("stepBtn").addEventListener("click", async () => {
  $("stepBtn").disabled = true;
  $("stepBtn").textContent = "Thinking...";
  try {
    render(await api("/api/step", { method: "POST" }));
  } finally {
    $("stepBtn").disabled = false;
    $("stepBtn").textContent = "Run Next Decision";
  }
});

$("resetBtn").addEventListener("click", async () => {
  render(await api("/api/reset", { method: "POST" }));
});

load().catch((error) => {
  document.body.innerHTML = `<pre>${escapeHtml(error.stack || error.message)}</pre>`;
});
