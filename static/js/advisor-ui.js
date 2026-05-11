const DASH_SESSION_KEY = 'techstore_ai_session_id';

let selectedCategory = 'Điện thoại';
let currentProducts = [];

function dashboardSessionId() {
  let value = localStorage.getItem(DASH_SESSION_KEY);
  if (!value) {
    value = `session-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    localStorage.setItem(DASH_SESSION_KEY, value);
  }
  return value;
}

function escapeHtml(text) {
  return String(text || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function compactNumber(value) {
  const num = Number(value || 0);
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1).replace('.0', '')}M`;
  if (num >= 1_000) return `${(num / 1_000).toFixed(1).replace('.0', '')}K`;
  return String(num);
}

function formatPrice(v) {
  const n = Number(v || 0);
  return `${n.toLocaleString('vi-VN')} đ`;
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function renderSuggestions(items) {
  const box = document.getElementById('suggestion-list');
  if (!box) return;
  if (!items.length) {
    box.innerHTML = `
      <div class="empty-state">
        <strong>Không tìm thấy gợi ý</strong>
        <span>Hãy thử chọn danh mục khác hoặc mở chat để tư vấn sâu hơn.</span>
      </div>
    `;
    return;
  }

  box.innerHTML = items.slice(0, 6).map((p) => `
    <div class="suggestion-item">
      <h3>${escapeHtml(p.name)}</h3>
      <div class="meta">${escapeHtml(p.category)} • ${escapeHtml(p.brand)} • ${escapeHtml(p.rating || '--')}/5</div>
      <div class="price">${escapeHtml(formatPrice(p.price))} <span class="meta">giảm ${escapeHtml(p.discount || 0)}%</span></div>
      <div class="desc">${escapeHtml(p.description || '')}</div>
    </div>
  `).join('');
}

async function loadOverview() {
  try {
    const [statsRes, healthRes] = await Promise.all([
      fetch('/api/stats'),
      fetch('/api/ai/health'),
    ]);
    const stats = statsRes.ok ? await statsRes.json() : {};
    const health = healthRes.ok ? await healthRes.json() : {};
    setText('ov-products', compactNumber(stats.summary?.total_products || 0));
    setText('ov-users', compactNumber(stats.summary?.total_users || 0));
    setText('ov-orders', compactNumber(stats.summary?.total_orders || 0));
    setText('ov-reviews', compactNumber(stats.summary?.avg_order_rating || 0));
    setText('ov-ai-status', health.ready ? 'READY' : 'DEGRADED');
    setText('ov-source', health?.data?.source || 'json');
    setText('ov-models', Array.isArray(health?.components?.recommender?.models) ? health.components.recommender.models.length : 0);
  } catch (_) {}
}

async function loadCategory(category) {
  selectedCategory = category;
  document.querySelectorAll('.category-btn').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.category === category);
  });

  const box = document.getElementById('suggestion-list');
  if (box) box.innerHTML = '<div class="empty-state"><strong>Đang tải gợi ý...</strong></div>';

  try {
    const params = new URLSearchParams({ category, n: '12', sort_by: 'rating' });
    const res = await fetch(`/api/products?${params.toString()}`);
    const payload = await res.json();
    currentProducts = payload.products || [];
    renderSuggestions(currentProducts);
  } catch (err) {
    if (box) {
      box.innerHTML = `<div class="empty-state"><strong>Lỗi tải gợi ý</strong><span>${escapeHtml(err.message || 'Không xác định')}</span></div>`;
    }
  }
}

function filterBySearch(value) {
  const query = (value || '').trim().toLowerCase();
  if (!query) {
    renderSuggestions(currentProducts);
    return;
  }
  const filtered = currentProducts.filter((p) => {
    const hay = `${p.name} ${p.category} ${p.brand} ${p.description}`.toLowerCase();
    return hay.includes(query);
  });
  renderSuggestions(filtered);
}

function openChat() {
  document.getElementById('chat-modal')?.classList.remove('hidden');
  document.getElementById('chat-query')?.focus();
}

function closeChat() {
  document.getElementById('chat-modal')?.classList.add('hidden');
}

async function runChat(message) {
  const sessionId = dashboardSessionId();
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      session_id: sessionId,
    }),
  });
  const payload = await res.json();
  return payload;
}

function appendChat(role, content, model) {
  const thread = document.getElementById('chat-thread');
  if (!thread) return;
  thread.querySelector('.chat-empty')?.remove();
  const el = document.createElement('div');
  el.className = `chat-message ${role}`;
  el.innerHTML = `
    <div class="meta">${escapeHtml(role === 'user' ? 'Bạn' : (model ? `Model: ${model}` : 'AI'))}</div>
    <div class="content">${escapeHtml(content).replace(/\n/g, '<br>')}</div>
  `;
  thread.appendChild(el);
  thread.scrollTop = thread.scrollHeight;
}

function setChatSessionLabels() {
  const sid = dashboardSessionId();
  setText('active-session-label', sid);
  setText('last-model-label', '--');
  const hidden = document.getElementById('session-id-input');
  if (hidden) hidden.value = sid;
}

function bindEvents() {
  document.querySelectorAll('.category-btn').forEach((btn) => {
    btn.addEventListener('click', () => loadCategory(btn.dataset.category));
  });

  document.getElementById('refresh-btn')?.addEventListener('click', () => loadCategory(selectedCategory));
  document.getElementById('chat-fab')?.addEventListener('click', openChat);
  document.getElementById('close-chat-btn')?.addEventListener('click', closeChat);
  document.getElementById('chat-modal')?.addEventListener('click', (e) => {
    if (e.target.id === 'chat-modal') closeChat();
  });
  document.getElementById('top-search')?.addEventListener('input', (e) => filterBySearch(e.target.value));
  document.getElementById('chat-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = document.getElementById('chat-query');
    const message = input?.value?.trim();
    if (!message) return;
    appendChat('user', message);
    input.value = '';
    try {
      const payload = await runChat(message);
      document.getElementById('last-model-label').textContent = payload.model_used || 'unknown';
      appendChat('assistant', payload.response || 'Không có phản hồi.', payload.model_used || 'unknown');
      if (payload.relevant_products?.length) {
        const note = payload.relevant_products.slice(0, 3).map((p) => `• ${p.name} (${p.price_formatted})`).join('\n');
        appendChat('assistant', `Gợi ý nhanh:\n${note}`, payload.model_used || 'unknown');
      }
    } catch (err) {
      appendChat('assistant', err.message || 'Chat API lỗi', 'error');
    }
  });

  document.getElementById('new-session-btn')?.addEventListener('click', () => {
    localStorage.setItem(DASH_SESSION_KEY, `session-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`);
    setChatSessionLabels();
    const thread = document.getElementById('chat-thread');
    if (thread) {
      thread.innerHTML = `
        <div class="chat-empty">
          <strong>Phiên mới sẵn sàng</strong>
          <span>Hãy nhập câu hỏi để bắt đầu tư vấn.</span>
        </div>
      `;
    }
  });

  document.getElementById('clear-history-btn')?.addEventListener('click', () => {
    const thread = document.getElementById('chat-thread');
    if (thread) {
      thread.innerHTML = `
        <div class="chat-empty">
          <strong>Lịch sử đã được xóa</strong>
          <span>Bạn có thể chat lại ngay.</span>
        </div>
      `;
    }
  });
}

window.addEventListener('load', async () => {
  setChatSessionLabels();
  bindEvents();
  await loadOverview();
  await loadCategory(selectedCategory);
});
