const DASH_SESSION_KEY = 'nexmart_dashboard_session_id';
const AUTO_REFRESH_MS = 30_000;

let refreshInFlight = false;
let refreshTimer = null;
let chatHistory = [];
let activeSessionId = null;

function dashboardSessionId() {
  let value = localStorage.getItem(DASH_SESSION_KEY);
  if (!value) {
    value = `dashboard-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    localStorage.setItem(DASH_SESSION_KEY, value);
  }
  return value;
}

function compactNumber(value) {
  const num = Number(value || 0);
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1).replace('.0', '')}M`;
  if (num >= 1_000) return `${(num / 1_000).toFixed(1).replace('.0', '')}K`;
  return String(num);
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function setChip(id, isOk, text) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = text;
  el.classList.remove('ok', 'bad');
  el.classList.add(isOk ? 'ok' : 'bad');
}

function escapeHtml(text) {
  return String(text || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function renderSimpleList(containerId, items, rowBuilder) {
  const el = document.getElementById(containerId);
  if (!el) return;
  if (!Array.isArray(items) || !items.length) {
    el.innerHTML = '<li>Không có dữ liệu.</li>';
    return;
  }
  el.innerHTML = items.map(rowBuilder).join('');
}

function summarizeTrace(trace) {
  const sources = Array.isArray(trace.sources) ? trace.sources : [];
  return {
    sources: sources.length ? sources.join(', ') : 'chưa rõ',
    retrieved: Number(trace.retrieved_count ?? 0),
    returned: Number(trace.returned_count ?? 0),
    products: Array.isArray(trace.retrieved_products) ? trace.retrieved_products : [],
  };
}

function renderRecommendationResult(payload) {
  const box = document.getElementById('recommend-result');
  if (!box) return;
  if (payload.error) {
    box.innerHTML = `<div class="result-error">${escapeHtml(payload.error)}</div>`;
    return;
  }
  const recs = payload.recommendations || [];
  if (!recs.length) {
    box.innerHTML = '<div>Không có recommendation phù hợp.</div>';
    return;
  }
  box.innerHTML = recs.slice(0, 8).map((item, idx) => {
    const score = item.hybrid_score !== undefined ? ` | score: ${Number(item.hybrid_score).toFixed(4)}` : (item.ai_score !== undefined ? ` | score: ${Number(item.ai_score).toFixed(4)}` : '');
    return `<div class="result-row"><strong>#${idx + 1}</strong> ${escapeHtml(item.name)} <span class="result-muted">(${escapeHtml(item.category)} - ${escapeHtml(item.brand)})${score}</span></div>`;
  }).join('');
}

function renderSemanticResult(payload) {
  const box = document.getElementById('semantic-result');
  if (!box) return;
  if (payload.error) {
    box.innerHTML = `<div class="result-error">${escapeHtml(payload.error)}</div>`;
    return;
  }
  const results = payload.results || [];
  if (!results.length) {
    box.innerHTML = '<div>Không có kết quả semantic phù hợp.</div>';
    return;
  }
  box.innerHTML = results.slice(0, 8).map((item, idx) => {
    const sim = item.similarity_score !== undefined ? ` | sim: ${Number(item.similarity_score).toFixed(4)}` : '';
    return `<div class="result-row"><strong>#${idx + 1}</strong> ${escapeHtml(item.name)} <span class="result-muted">(${escapeHtml(item.category)} - ${escapeHtml(item.brand)})${sim}</span></div>`;
  }).join('');
}

function renderChatResult(payload) {
  const thread = document.getElementById('chat-thread');
  const sessionLabel = document.getElementById('active-session-label');
  const modelLabel = document.getElementById('last-model-label');
  if (!thread) return;

  if (payload.error) {
    thread.insertAdjacentHTML('beforeend', `<div class="chat-message assistant"><div class="meta">Error</div><div class="content">${escapeHtml(payload.error)}</div></div>`);
    return;
  }

  const sessionId = payload.session_id || activeSessionId || dashboardSessionId();
  activeSessionId = sessionId;
  if (sessionLabel) sessionLabel.textContent = sessionId;
  if (modelLabel) modelLabel.textContent = payload.model_used || 'unknown';

  const trace = payload.trace || payload.debug?.trace || {};
  const traceSources = Array.isArray(trace.sources) && trace.sources.length ? trace.sources.join(', ') : 'chưa rõ';
  const retrieved = Number(trace.retrieved_count ?? 0);
  const returned = Number(trace.returned_count ?? 0);
  const retrievedProducts = Array.isArray(trace.retrieved_products) ? trace.retrieved_products : [];
  const productsHtml = retrievedProducts.length
    ? `<div class="trace-products">${retrievedProducts.slice(0, 5).map((p, i) => `<div class="trace-product"><strong>#${i + 1} ${esc(p.name || p.id)}</strong><span>${esc(p.category || '')} • ${esc(p.brand || '')}${p.reasons?.length ? ` • ${esc(p.reasons.join(', '))}` : ''}</span></div>`).join('')}</div>`
    : '<div class="muted">Không có sản phẩm nào được retrieve.</div>';

  thread.querySelector('.chat-empty')?.remove();
  thread.insertAdjacentHTML('beforeend', `
    <div class="chat-message user">
      <div class="meta">You</div>
      <div class="content">${escapeHtml(payload.user_message || document.getElementById('chat-query')?.value || '')}</div>
    </div>
    <div class="chat-message assistant">
      <div class="meta">Model: ${escapeHtml(payload.model_used || 'unknown')} • Nguồn: ${escapeHtml(traceSources)} • retrieved=${retrieved} • returned=${returned}</div>
      <div class="content">${escapeHtml((payload.response || 'Không có phản hồi.')).replace(/\n/g, '<br>')}</div>
      <details class="trace-box">
        <summary>Xem nguồn dữ liệu</summary>
        ${productsHtml}
      </details>
    </div>
  `);
  thread.scrollTop = thread.scrollHeight;
  addChatToHistory(payload.user_message || '', payload.response || '', sessionId);
}

function addChatToHistory(userText, assistantText, sessionId) {
  if (!userText && !assistantText) return;
  const idx = chatHistory.findIndex((x) => x.session_id === sessionId);
  const item = {
    session_id: sessionId,
    title: (userText || 'Cuộc trò chuyện').slice(0, 44),
    preview: (assistantText || userText || '').slice(0, 80),
    updated_at: new Date().toISOString(),
  };
  if (idx >= 0) chatHistory[idx] = item;
  else chatHistory.unshift(item);
  renderChatHistoryList();
}

function renderChatHistoryList() {
  const box = document.getElementById('chat-history-list');
  if (!box) return;
  if (!chatHistory.length) {
    box.innerHTML = '<div class="history-empty">Chưa có cuộc trò chuyện nào.</div>';
    return;
  }
  box.innerHTML = chatHistory.map((item) => `
    <div class="history-item" data-session="${escapeHtml(item.session_id)}">
      <strong>${escapeHtml(item.title)}</strong>
      <span>${escapeHtml(item.preview)}</span>
    </div>
  `).join('');

  box.querySelectorAll('.history-item').forEach((el) => {
    el.addEventListener('click', async () => {
      const sid = el.getAttribute('data-session');
      if (sid) {
        document.getElementById('session-id-input').value = sid;
        activeSessionId = sid;
        document.getElementById('active-session-label').textContent = sid;
        await loadSessionHistory(sid);
      }
    });
  });
}

function setRefreshMeta(text) {
  const el = document.getElementById('dash-refresh-meta');
  if (el) el.textContent = text;
}

function formatTimeNow() {
  return new Date().toLocaleTimeString('vi-VN', { hour12: false });
}

function setSkeletonLoading(enabled) {
  const ids = ['ov-ai-status','ov-source','ov-models','ov-products','ov-users','ov-orders','ov-reviews','ov-behavior'];
  ids.forEach((id) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.toggle('skeleton-text', enabled);
    if (enabled) el.textContent = ' ';
  });
  const catList = document.getElementById('dash-cat-list');
  const trendList = document.getElementById('dash-trending-list');
  if (enabled && catList) catList.innerHTML = '<li class="skeleton-item"></li><li class="skeleton-item"></li><li class="skeleton-item"></li>';
  if (enabled && trendList) trendList.innerHTML = '<li class="skeleton-item"></li><li class="skeleton-item"></li><li class="skeleton-item"></li>';
}

async function loadOverview() {
  try {
    const [healthRes, countsRes, statsRes, modelsRes] = await Promise.all([
      fetch('/api/ai/health'),
      fetch('/api/db/counts'),
      fetch('/api/stats'),
      fetch('/api/models'),
    ]);
    const health = healthRes.ok ? await healthRes.json() : {};
    const countsData = countsRes.ok ? await countsRes.json() : {};
    const stats = statsRes.ok ? await statsRes.json() : {};
    const models = modelsRes.ok ? await modelsRes.json() : {};

    const source = countsData.source || health?.data?.source || 'unknown';
    const counts = countsData.counts || health?.data?.counts || {};
    const aiReady = Boolean(health.ready);
    setText('ov-ai-status', aiReady ? 'READY' : 'DEGRADED');
    setChip('ov-ai-chip', aiReady, aiReady ? 'all systems go' : 'partial available');
    setText('ov-source', String(source).toUpperCase());
    setText('ov-models', String(Array.isArray(health?.components?.recommender?.models) ? health.components.recommender.models.length : (Number(models.total_models || 0) - 1)));
    setText('ov-products', compactNumber(counts.products || stats.total_products || 0));
    setText('ov-users', compactNumber(counts.users || stats.total_users || 0));
    setText('ov-orders', compactNumber(counts.orders || stats.total_orders || 0));
    setText('ov-reviews', compactNumber(counts.reviews || 0));
    setText('ov-behavior', compactNumber(counts.behavior_logs || 0));
    const categories = stats.categories && typeof stats.categories === 'object' ? Object.entries(stats.categories).sort((a, b) => Number(b[1]) - Number(a[1])) : [];
    renderSimpleList('dash-cat-list', categories.slice(0, 8), ([name, count], idx) => `<li><span>#${idx + 1} ${escapeHtml(name)}</span><strong>${compactNumber(count)}</strong></li>`);
  } catch (err) {
    setText('ov-ai-status', 'N/A');
    setText('ov-source', 'N/A');
    setText('ov-models', 'N/A');
    setText('ov-products', 'N/A');
    setText('ov-users', 'N/A');
    setText('ov-orders', 'N/A');
    setText('ov-reviews', 'N/A');
    setText('ov-behavior', 'N/A');
    setChip('ov-ai-chip', false, 'api unavailable');
  }
}

async function loadTrending() {
  try {
    const res = await fetch('/api/products/trending?n=8');
    const payload = await res.json();
    const products = payload.products || [];
    renderSimpleList('dash-trending-list', products, (item, idx) => {
      const trend = item.trend_ratio !== undefined ? ` | trend ${Number(item.trend_ratio).toFixed(2)}` : '';
      return `<li><span>#${idx + 1} ${escapeHtml(item.name)}</span><strong>${escapeHtml(item.category)}${trend}</strong></li>`;
    });
  } catch (_) {
    renderSimpleList('dash-trending-list', [], () => '');
  }
}

async function refreshDashboard(isAuto = false) {
  if (refreshInFlight) return;
  refreshInFlight = true;
  setRefreshMeta(isAuto ? 'Auto-refresh mỗi 30s • Đang cập nhật...' : 'Đang cập nhật dữ liệu...');
  setSkeletonLoading(true);
  try {
    await loadOverview();
    await loadTrending();
    setRefreshMeta(`Auto-refresh mỗi 30s • Cập nhật lúc ${formatTimeNow()}`);
  } catch (_) {
    setRefreshMeta('Auto-refresh mỗi 30s • Không thể cập nhật');
  } finally {
    setSkeletonLoading(false);
    refreshInFlight = false;
  }
}

function startAutoRefresh() {
  if (refreshTimer) clearInterval(refreshTimer);
  refreshTimer = setInterval(() => refreshDashboard(true), AUTO_REFRESH_MS);
}

async function runRecommendationTest() {
  const method = document.getElementById('rec-method')?.value || 'hybrid';
  const userId = document.getElementById('rec-user-id')?.value?.trim() || '';
  const productId = document.getElementById('rec-product-id')?.value?.trim() || '';
  const category = document.getElementById('rec-category')?.value?.trim() || '';
  const n = document.getElementById('rec-top-n')?.value || '6';
  const params = new URLSearchParams({ method, n });
  if (userId) params.set('user_id', userId);
  if (productId) params.set('product_id', productId);
  if (category) params.set('category', category);
  const box = document.getElementById('recommend-result');
  if (box) box.textContent = 'Đang chạy recommendation...';
  try {
    const res = await fetch(`/api/recommend?${params.toString()}`);
    const payload = await res.json();
    if (!res.ok && !payload.error) payload.error = `HTTP ${res.status}`;
    renderRecommendationResult(payload);
  } catch (err) {
    renderRecommendationResult({ error: err.message || 'Recommendation API lỗi' });
  }
}

async function runSemanticTest() {
  const query = document.getElementById('semantic-query')?.value?.trim() || '';
  if (!query) {
    renderSemanticResult({ error: 'Vui lòng nhập truy vấn semantic.' });
    return;
  }
  const box = document.getElementById('semantic-result');
  if (box) box.textContent = 'Đang chạy semantic search...';
  try {
    const res = await fetch(`/api/products/semantic-search?q=${encodeURIComponent(query)}&top_k=8`);
    const payload = await res.json();
    if (!res.ok && !payload.error) payload.error = `HTTP ${res.status}`;
    renderSemanticResult(payload);
  } catch (err) {
    renderSemanticResult({ error: err.message || 'Semantic API lỗi' });
  }
}

async function loadSessionHistory(sessionId) {
  const sid = sessionId || document.getElementById('session-id-input')?.value?.trim() || dashboardSessionId();
  const thread = document.getElementById('chat-thread');
  if (!thread) return;
  thread.innerHTML = '<div class="chat-empty"><strong>Đang tải lịch sử...</strong></div>';
  try {
    const res = await fetch(`/api/history/${encodeURIComponent(sid)}`);
    const payload = await res.json();
    const messages = payload.messages || [];
    thread.innerHTML = '';
    if (!messages.length) {
      thread.innerHTML = '<div class="chat-empty"><strong>Chưa có lịch sử.</strong><span>Bắt đầu một cuộc trò chuyện mới nhé.</span></div>';
      return;
    }
    messages.forEach((msg) => {
      thread.insertAdjacentHTML('beforeend', `
        <div class="chat-message ${msg.role === 'user' ? 'user' : 'assistant'}">
          <div class="meta">${escapeHtml(msg.role)}${msg.created_at ? ` • ${escapeHtml(String(msg.created_at))}` : ''}</div>
          <div class="content">${escapeHtml(msg.content || '').replace(/\n/g, '<br>')}</div>
        </div>
      `);
    });
    thread.scrollTop = thread.scrollHeight;
    activeSessionId = sid;
    document.getElementById('active-session-label').textContent = sid;
  } catch (err) {
    thread.innerHTML = `<div class="chat-empty"><strong>Không tải được lịch sử.</strong><span>${escapeHtml(err.message || 'Lỗi không xác định')}</span></div>`;
  }
}

async function runChatSmokeTest() {
  const queryEl = document.getElementById('chat-query');
  const query = queryEl?.value?.trim() || '';
  if (!query) {
    renderChatResult({ error: 'Vui lòng nhập câu hỏi chat.' });
    return;
  }
  const sessionId = document.getElementById('session-id-input')?.value?.trim() || dashboardSessionId();
  const userId = document.getElementById('user-id-input')?.value?.trim() || '';
  document.getElementById('session-id-input').value = sessionId;
  activeSessionId = sessionId;
  const box = document.getElementById('chat-thread');
  if (box && !box.querySelector('.chat-empty')) {
    box.insertAdjacentHTML('beforeend', '<div class="chat-empty"><strong>Đang gọi AI chat...</strong></div>');
  }
  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: query,
        session_id: sessionId,
        user_id: userId || undefined,
      }),
    });
    const payload = await res.json();
    if (!res.ok && !payload.error) payload.error = `HTTP ${res.status}`;
    payload.user_message = query;
    renderChatResult(payload);
    queryEl.value = '';
  } catch (err) {
    renderChatResult({ error: err.message || 'Chat API lỗi' });
  }
}

async function clearHistory() {
  const sid = document.getElementById('session-id-input')?.value?.trim() || activeSessionId || dashboardSessionId();
  try {
    await fetch(`/api/history/${encodeURIComponent(sid)}`, { method: 'DELETE' });
    await loadSessionHistory(sid);
    chatHistory = chatHistory.filter((x) => x.session_id !== sid);
    renderChatHistoryList();
  } catch (_) {}
}

function bindEvents() {
  document.getElementById('dash-refresh-btn')?.addEventListener('click', async () => refreshDashboard(false));
  document.getElementById('run-recommend-btn')?.addEventListener('click', runRecommendationTest);
  document.getElementById('run-semantic-btn')?.addEventListener('click', runSemanticTest);
  document.getElementById('chat-form')?.addEventListener('submit', async (e) => { e.preventDefault(); await runChatSmokeTest(); });
  document.getElementById('load-history-btn')?.addEventListener('click', async () => await loadSessionHistory());
  document.getElementById('clear-history-btn')?.addEventListener('click', clearHistory);
  document.getElementById('new-session-btn')?.addEventListener('click', () => {
    const sid = `session-${Date.now()}`;
    document.getElementById('session-id-input').value = sid;
    activeSessionId = sid;
    document.getElementById('active-session-label').textContent = sid;
    const thread = document.getElementById('chat-thread');
    if (thread) thread.innerHTML = '<div class="chat-empty"><strong>Phiên mới đã sẵn sàng.</strong><span>Bạn có thể bắt đầu chat ngay.</span></div>';
  });
  document.getElementById('load-session-btn')?.addEventListener('click', async () => await loadSessionHistory());
  document.getElementById('go-chat-btn')?.addEventListener('click', () => document.getElementById('chat-query')?.focus());
}

window.addEventListener('load', async () => {
  const sid = dashboardSessionId();
  document.getElementById('session-id-input').value = sid;
  activeSessionId = sid;
  document.getElementById('active-session-label').textContent = sid;
  bindEvents();
  await refreshDashboard(false);
  await loadSessionHistory(sid);
  startAutoRefresh();
});
