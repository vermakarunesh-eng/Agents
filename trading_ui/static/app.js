const state = {
  symbol: "AAPL",
  quote: null,
  bars: [],
  refreshTimer: null,
  autoExecutionTimer: null,
};

const els = {
  form: document.querySelector("#symbolForm"),
  symbolInput: document.querySelector("#symbolInput"),
  lastPrice: document.querySelector("#lastPrice"),
  changeValue: document.querySelector("#changeValue"),
  marketState: document.querySelector("#marketState"),
  updatedAt: document.querySelector("#updatedAt"),
  chartTitle: document.querySelector("#chartTitle"),
  feedSource: document.querySelector("#feedSource"),
  status: document.querySelector("#status"),
  canvas: document.querySelector("#priceChart"),
  actionBadge: document.querySelector("#actionBadge"),
  confidence: document.querySelector("#confidence"),
  entry: document.querySelector("#entry"),
  stopLoss: document.querySelector("#stopLoss"),
  takeProfit: document.querySelector("#takeProfit"),
  shares: document.querySelector("#shares"),
  rationale: document.querySelector("#rationale"),
  capital: document.querySelector("#capital"),
  riskPct: document.querySelector("#riskPct"),
  maxPositionPct: document.querySelector("#maxPositionPct"),
  horizon: document.querySelector("#horizon"),
  executionForm: document.querySelector("#executionForm"),
  brokerStatus: document.querySelector("#brokerStatus"),
  minConfidence: document.querySelector("#minConfidence"),
  cooldownSeconds: document.querySelector("#cooldownSeconds"),
  autoSeconds: document.querySelector("#autoSeconds"),
  executionArmed: document.querySelector("#executionArmed"),
  autoExecution: document.querySelector("#autoExecution"),
  feedSummary: document.querySelector("#feedSummary"),
  executionsBody: document.querySelector("#executionsBody"),
};

els.form.addEventListener("submit", (event) => {
  event.preventDefault();
  loadSymbol(els.symbolInput.value.trim() || "AAPL");
});

[els.capital, els.riskPct, els.maxPositionPct, els.horizon].forEach((input) => {
  input.addEventListener("change", () => loadRecommendation());
});

els.executionForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await executeAgentTrade();
});

els.autoExecution.addEventListener("change", scheduleAutoExecution);
els.executionArmed.addEventListener("change", scheduleAutoExecution);
els.autoSeconds.addEventListener("change", scheduleAutoExecution);

window.addEventListener("resize", () => drawChart(state.bars.length ? state.bars : quotePointsToBars()));

loadSymbol(state.symbol);
loadBrokerStatus();
loadExecutions();

function scheduleQuoteRefresh() {
  window.clearInterval(state.refreshTimer);
  state.refreshTimer = window.setInterval(() => loadQuote(false), 15000);
}

function scheduleAutoExecution() {
  window.clearInterval(state.autoExecutionTimer);
  state.autoExecutionTimer = null;
  if (!els.autoExecution.checked || !els.executionArmed.checked) return;
  const seconds = Math.max(60, Number(els.autoSeconds.value) || 300);
  state.autoExecutionTimer = window.setInterval(() => executeAgentTrade(), seconds * 1000);
  setStatus(`Auto every ${seconds}s`);
}

async function loadSymbol(symbol) {
  state.symbol = symbol.toUpperCase();
  els.symbolInput.value = state.symbol;
  els.chartTitle.textContent = state.symbol;
  setStatus("Loading");
  await Promise.all([loadQuote(true), loadRecommendation()]);
  scheduleQuoteRefresh();
  setStatus("Live");
}

async function loadQuote(drawOnlyWhenNoBars) {
  try {
    const quote = await getJson(`/api/quote?symbol=${encodeURIComponent(state.symbol)}`);
    state.quote = quote;
    renderQuote(quote);
    if (drawOnlyWhenNoBars || !state.bars.length) {
      drawChart(quotePointsToBars());
    }
  } catch (error) {
    setStatus(error.message);
  }
}

async function loadRecommendation() {
  try {
    const params = new URLSearchParams({
      symbol: state.symbol,
      capital: els.capital.value,
      riskPct: els.riskPct.value,
      maxPositionPct: els.maxPositionPct.value,
      horizon: els.horizon.value,
    });
    const payload = await getJson(`/api/recommendation?${params.toString()}`);
    state.bars = payload.bars || [];
    renderRecommendation(payload.recommendation);
    renderFeedSummary(payload.feedSummary);
    drawChart(state.bars);
  } catch (error) {
    setStatus(error.message);
  }
}

async function executeAgentTrade() {
  try {
    if (!els.executionArmed.checked) {
      setStatus("Execution not armed");
      return;
    }
    const payload = {
      symbol: state.symbol,
      capital: Number(els.capital.value),
      riskPct: Number(els.riskPct.value),
      maxPositionPct: Number(els.maxPositionPct.value),
      horizon: Number(els.horizon.value),
      minConfidence: Number(els.minConfidence.value) / 100,
      cooldownSeconds: Number(els.cooldownSeconds.value),
    };
    const decision = await postJson("/api/execute", payload);
    await loadExecutions();
    setStatus(decision.status);
    scheduleAutoExecution();
  } catch (error) {
    setStatus(error.message);
  }
}

async function loadBrokerStatus() {
  const status = await getJson("/api/execution/status");
  const configured = status.configured ? "configured" : "not configured";
  const enabled = status.live_enabled ? "live enabled" : "live disabled";
  els.brokerStatus.textContent = `Alpaca ${configured}; ${enabled}; ${status.base_url || "no endpoint"}`;
}

async function loadExecutions() {
  const payload = await getJson("/api/executions");
  els.executionsBody.innerHTML = (payload.executions || [])
    .map(
      (event) => `
        <tr>
          <td>${escapeHtml(event.created_at || "")}</td>
          <td class="${event.submitted ? "positive" : "negative"}">${escapeHtml(event.status || "")}</td>
          <td>${escapeHtml(event.symbol || "")}</td>
          <td>${escapeHtml(event.recommendation?.action || "")}</td>
          <td>${escapeHtml(event.reason || "")}</td>
          <td>${escapeHtml(event.order?.broker || "")}</td>
        </tr>
      `,
    )
    .join("");
}

function renderQuote(quote) {
  els.lastPrice.textContent = `${formatMoney(quote.price)} ${quote.currency || ""}`.trim();
  els.changeValue.textContent = `${quote.change >= 0 ? "+" : ""}${quote.change.toFixed(2)} (${quote.change_pct.toFixed(2)}%)`;
  els.changeValue.className = quote.change >= 0 ? "positive" : "negative";
  els.marketState.textContent = quote.market_state;
  els.updatedAt.textContent = quote.regular_market_time || "Delayed";
  els.feedSource.textContent = `${quote.source.toUpperCase()} feed`;
}

function renderRecommendation(payload) {
  const rec = payload || {};
  const action = rec.action || "HOLD";
  els.actionBadge.textContent = action;
  els.actionBadge.className = `badge ${action.toLowerCase()}`;
  els.confidence.textContent = rec.confidence ? `${Math.round(rec.confidence * 100)}%` : "--";
  els.entry.textContent = formatMoney(rec.entry);
  els.stopLoss.textContent = formatMoney(rec.stop_loss);
  els.takeProfit.textContent = formatMoney(rec.take_profit);
  els.shares.textContent = rec.shares ?? "--";
  els.rationale.innerHTML = (rec.rationale || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("");
}

function renderFeedSummary(summary) {
  if (!summary) {
    els.feedSummary.innerHTML = metricItem("Status", "--");
    return;
  }
  els.feedSummary.innerHTML = [
    metricItem("Status", summary.status),
    metricItem("Bars", summary.history_bars),
    metricItem("Recent", `${summary.recent_return_pct}%`),
    metricItem("Start", summary.start),
    metricItem("End", summary.end),
  ].join("");
}

function drawChart(rows) {
  const canvas = els.canvas;
  const ctx = canvas.getContext("2d");
  const rect = canvas.getBoundingClientRect();
  const ratio = window.devicePixelRatio || 1;
  canvas.width = Math.max(640, Math.floor(rect.width * ratio));
  canvas.height = Math.max(300, Math.floor(rect.height * ratio));
  ctx.scale(ratio, ratio);

  const width = canvas.width / ratio;
  const height = canvas.height / ratio;
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = "#0b0d0f";
  ctx.fillRect(0, 0, width, height);

  const data = rows.filter((row) => Number.isFinite(Number(row.close)));
  if (data.length < 2) {
    drawEmpty(ctx, width, height);
    return;
  }

  const padding = { top: 22, right: 54, bottom: 36, left: 54 };
  const closes = data.map((row) => Number(row.close));
  const min = Math.min(...closes);
  const max = Math.max(...closes);
  const span = max - min || 1;
  const xFor = (index) => padding.left + (index / (data.length - 1)) * (width - padding.left - padding.right);
  const yFor = (value) => padding.top + ((max - value) / span) * (height - padding.top - padding.bottom);

  ctx.strokeStyle = "rgba(221, 230, 217, 0.08)";
  ctx.lineWidth = 1;
  for (let i = 0; i < 5; i += 1) {
    const y = padding.top + (i / 4) * (height - padding.top - padding.bottom);
    ctx.beginPath();
    ctx.moveTo(padding.left, y);
    ctx.lineTo(width - padding.right, y);
    ctx.stroke();
  }

  const rising = closes[closes.length - 1] >= closes[0];
  ctx.strokeStyle = rising ? "#7ce0a3" : "#ff8f8f";
  ctx.lineWidth = 2.5;
  ctx.beginPath();
  closes.forEach((close, index) => {
    const x = xFor(index);
    const y = yFor(close);
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  const gradient = ctx.createLinearGradient(0, padding.top, 0, height - padding.bottom);
  gradient.addColorStop(0, rising ? "rgba(124, 224, 163, 0.22)" : "rgba(255, 143, 143, 0.2)");
  gradient.addColorStop(1, "rgba(124, 224, 163, 0)");
  ctx.lineTo(xFor(closes.length - 1), height - padding.bottom);
  ctx.lineTo(xFor(0), height - padding.bottom);
  ctx.closePath();
  ctx.fillStyle = gradient;
  ctx.fill();

  ctx.fillStyle = "#aeb8b0";
  ctx.font = "12px Inter, sans-serif";
  ctx.fillText(formatMoney(max), width - padding.right + 10, yFor(max) + 4);
  ctx.fillText(formatMoney(min), width - padding.right + 10, yFor(min) + 4);
  ctx.fillText(labelFor(data[0]), padding.left, height - 12);
  ctx.fillText(labelFor(data[data.length - 1]), Math.max(padding.left, width - padding.right - 90), height - 12);
}

function quotePointsToBars() {
  return (state.quote?.points || []).map((point) => ({ date: point.time, close: Number(point.close) }));
}

function drawEmpty(ctx, width, height) {
  ctx.fillStyle = "#aeb8b0";
  ctx.font = "15px Inter, sans-serif";
  ctx.fillText("Waiting for market data", 24, height / 2);
}

async function getJson(url) {
  const response = await fetch(url);
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || response.statusText);
  return payload;
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || response.statusText);
  return body;
}

function setStatus(value) {
  els.status.textContent = value;
}

function metricItem(label, value) {
  return `<div><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(String(value))}</dd></div>`;
}

function labelFor(row) {
  if (typeof row.date === "string") return row.date;
  if (typeof row.time === "string") return row.time;
  return "";
}

function formatMoney(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "--";
  return number.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
