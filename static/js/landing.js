const CHAT_SESSION_KEY = 'nexmart_chat_session_id';

function getChatSessionId() {
  let sessionId = localStorage.getItem(CHAT_SESSION_KEY);
  if (!sessionId) {
    sessionId = `landing-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
    localStorage.setItem(CHAT_SESSION_KEY, sessionId);
  }
  return sessionId;
}

function appendUserMessage(container, text) {
  const row = document.createElement('div');
  row.style.cssText = 'text-align: right; margin-bottom: 12px;';

  const bubble = document.createElement('div');
  bubble.style.cssText = 'display: inline-block; background: var(--gradient-main); color: #fff; padding: 12px 16px; border-radius: 18px 18px 6px 18px; max-width: 85%; font-size: 15px; white-space: pre-wrap;';
  bubble.textContent = text;

  row.appendChild(bubble);
  container.appendChild(row);
}

function createAITypingBubble(container) {
  const wrapper = document.createElement('div');
  wrapper.style.cssText = 'display: flex; align-items: flex-start; gap: 8px; margin-bottom: 12px;';

  const avatar = document.createElement('div');
  avatar.style.cssText = 'width: 36px; height: 36px; border-radius: 50%; background: var(--gradient-main); display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0;';
  avatar.textContent = '🤖';

  const bubble = document.createElement('div');
  bubble.style.cssText = 'background: rgba(255,255,255,.05); padding: 12px 16px; border-radius: 18px; border: 1px solid rgba(255,255,255,.1); max-width: 96%; white-space: pre-wrap;';
  bubble.innerHTML = '<div style="color: var(--cyan);">Đang tư vấn...</div>';

  wrapper.appendChild(avatar);
  wrapper.appendChild(bubble);
  container.appendChild(wrapper);
  return bubble;
}

function appendAssistantMessage(container, text) {
  const wrapper = document.createElement('div');
  wrapper.style.cssText = 'display: flex; align-items: flex-start; gap: 8px; margin-bottom: 12px;';

  const avatar = document.createElement('div');
  avatar.style.cssText = 'width: 36px; height: 36px; border-radius: 50%; background: var(--gradient-main); display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0;';
  avatar.textContent = '🤖';

  const bubble = document.createElement('div');
  bubble.style.cssText = 'background: rgba(255,255,255,.05); padding: 12px 16px; border-radius: 18px; border: 1px solid rgba(255,255,255,.1); max-width: 96%; white-space: pre-wrap;';
  bubble.textContent = text;

  wrapper.appendChild(avatar);
  wrapper.appendChild(bubble);
  container.appendChild(wrapper);
}

function escapeHtml(text) {
  return String(text || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function formatAssistantText(text) {
  return escapeHtml(text)
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>');
}

function pickAdvantages(product) {
  const tags = Array.isArray(product?.tags) ? product.tags.filter(Boolean).slice(0, 3) : [];
  if (tags.length) return tags;

  const fallback = [];
  if (product?.brand) fallback.push(`Thương hiệu ${product.brand}`);
  if (product?.discount && Number(product.discount) > 0) fallback.push(`Giảm ${Number(product.discount)}%`);
  if (product?.category) fallback.push(`Thuộc nhóm ${product.category}`);
  return fallback.slice(0, 3);
}

function popularityLabel(product) {
  const reviews = Number(product?.reviews || 0);
  if (reviews >= 5000) return 'Được dùng rất nhiều';
  if (reviews >= 1000) return 'Được dùng nhiều';
  if (reviews >= 200) return 'Phổ biến tốt';
  return 'Nhu cầu ổn định';
}

function recommendationScore(product) {
  const rating = Number(product?.rating || 0);
  const reviews = Number(product?.reviews || 0);
  const discount = Number(product?.discount || 0);
  return (rating * 20) + Math.log10(reviews + 1) * 10 + discount;
}

function renderTopRecommendationsHtml(products) {
  const list = Array.isArray(products) ? products.slice() : [];
  if (!list.length) return '';

  const ranked = list
    .sort((a, b) => recommendationScore(b) - recommendationScore(a))
    .slice(0, 3);

  const cards = ranked.map((product, index) => {
    const currentPrice = product?.price_formatted || formatPriceVND(product?.price);
    const originalPrice = product?.original_price_formatted || formatPriceVND(product?.original_price || 0);
    const discount = Number(product?.discount || 0);
    const rating = Number(product?.rating || 0).toFixed(1);
    const reviews = compactNumber(product?.reviews || 0);
    const advantages = pickAdvantages(product).map((item) => `<li>${escapeHtml(item)}</li>`).join('');

    return `
      <div class="chat-rec-card">
        <div class="chat-rec-rank">#${index + 1}</div>
        <div class="chat-rec-name">${escapeHtml(product?.name || 'Sản phẩm')}</div>
        <div class="chat-rec-row"><span>💰 Giá:</span> <strong>${escapeHtml(currentPrice)}</strong> <span class="chat-rec-muted">(Gốc: ${escapeHtml(originalPrice)}, -${discount}%)</span></div>
        <div class="chat-rec-row"><span>⭐ Đánh giá:</span> <strong>${rating}/5</strong> <span class="chat-rec-muted">(${reviews} lượt)</span></div>
        <div class="chat-rec-row"><span>🔥 Phổ biến:</span> <strong>${popularityLabel(product)}</strong></div>
        <div class="chat-rec-row"><span>✅ Ưu điểm:</span></div>
        <ul class="chat-rec-advantages">${advantages || '<li>Hiệu năng và mức giá cân đối</li>'}</ul>
      </div>
    `;
  }).join('');

  return `
    <div class="chat-rec-wrap">
      <div class="chat-rec-title">🎯 Top sản phẩm phù hợp nhất</div>
      <div class="chat-rec-grid">${cards}</div>
    </div>
  `;
}

function renderAssistantResponseIntoBubble(bubbleEl, data) {
  const answer = (data && data.response) ? data.response : 'AI chưa có phản hồi phù hợp.';
  const recHtml = renderTopRecommendationsHtml(data?.relevant_products || []);
  bubbleEl.innerHTML = `${formatAssistantText(answer)}${recHtml}`;
}

function formatPriceVND(price) {
  const value = Number(price || 0);
  return `${value.toLocaleString('vi-VN')}đ`;
}

function compactNumber(value) {
  const num = Number(value || 0);
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1).replace('.0', '')}M+`;
  if (num >= 1_000) return `${(num / 1_000).toFixed(1).replace('.0', '')}K+`;
  return `${num}`;
}

function getCategoryEmoji(category) {
  const cat = (category || '').toLowerCase();
  if (cat.includes('điện thoại') || cat.includes('dien thoai')) return '📱';
  if (cat.includes('laptop')) return '💻';
  if (cat.includes('đồng hồ') || cat.includes('dong ho')) return '⌚';
  if (cat.includes('máy ảnh') || cat.includes('may anh')) return '📷';
  if (cat.includes('phụ kiện') || cat.includes('phu kien')) return '🎧';
  if (cat.includes('máy tính bảng') || cat.includes('may tinh bang')) return '📲';
  return '🛍️';
}

async function callAI(message) {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      session_id: getChatSessionId()
    })
  });

  if (!res.ok) {
    let errMsg = 'Không thể kết nối AI. Vui lòng thử lại sau.';
    try {
      const errData = await res.json();
      if (errData && errData.error) errMsg = errData.error;
    } catch (_) {}
    throw new Error(errMsg);
  }

  return res.json();
}

async function demoAI() {
  const input = document.getElementById('demo-input');
  const response = document.getElementById('demo-response');
  const q = input.value.trim();
  if (!q) return;
  input.value = '';
  input.disabled = true;
  const demoButton = document.querySelector('.ai-demo-btn');
  if (demoButton) demoButton.disabled = true;
  response.innerHTML = '<i class="fas fa-spinner fa-spin"></i> AI đang tư vấn...';

  try {
    const data = await callAI(q);
    response.innerHTML = formatAssistantText(data?.response || 'AI chưa có phản hồi phù hợp.');
  } catch (err) {
    response.textContent = `⚠️ ${err.message || 'Có lỗi xảy ra khi gọi AI.'}`;
  } finally {
    input.disabled = false;
    if (demoButton) demoButton.disabled = false;
    input.focus();
  }
}

function prefillAndFocusChat(message) {
  const section = document.getElementById('chat-widget');
  const input = document.getElementById('ai-chat-input');
  section.scrollIntoView({ behavior: 'smooth', block: 'start' });
  input.value = message;
  setTimeout(() => input.focus(), 300);
}

function askProductDetail(productName, category) {
  prefillAndFocusChat(`Tư vấn chi tiết ${productName} trong danh mục ${category}, so sánh giúp mình với lựa chọn tương tự.`);
}

function renderFeaturedProducts(products) {
  const grid = document.getElementById('featured-products-grid');
  if (!Array.isArray(products) || products.length === 0) {
    grid.innerHTML = '<div class="product-card-lp" style="grid-column: 1/-1; text-align: center; padding: 24px; color: var(--text-dim);">Chưa có dữ liệu sản phẩm nổi bật.</div>';
    return;
  }

  grid.innerHTML = '';
  products.forEach((product, idx) => {
    const card = document.createElement('div');
    card.className = 'product-card-lp';
    const badge = idx < 2 ? '<div class="product-badge-lp">HOT</div>' : '';
    const price = product.price_formatted || formatPriceVND(product.price);
    const scoreText = product.rating ? `Đánh giá ${product.rating}/5 (${product.reviews || 0})` : 'AI đề xuất theo xu hướng';

    card.innerHTML = `
      <div class="product-img-lp">
        <span>${getCategoryEmoji(product.category)}</span>
        ${badge}
      </div>
      <div class="product-info-lp">
        <h3 class="product-name-lp"></h3>
        <div class="product-price-lp">${price}</div>
        <div class="product-ai-tag">
          <i class="fas fa-brain"></i> ${scoreText}
        </div>
        <button class="btn-primary consult-btn" style="width: 100%; margin-top: 16px;">Tư vấn chi tiết</button>
      </div>
    `;

    card.querySelector('.product-name-lp').textContent = product.name || 'Sản phẩm';
    card.querySelector('.consult-btn').addEventListener('click', () => {
      askProductDetail(product.name || 'sản phẩm này', product.category || 'phù hợp');
    });
    grid.appendChild(card);
  });
}

async function loadFeaturedProducts() {
  const grid = document.getElementById('featured-products-grid');
  try {
    const res = await fetch('/api/products/top?n=8');
    if (!res.ok) throw new Error('Không tải được sản phẩm nổi bật');
    const data = await res.json();
    renderFeaturedProducts(data.products || []);
  } catch (_) {
    grid.innerHTML = '<div class="product-card-lp" style="grid-column: 1/-1; text-align: center; padding: 24px; color: var(--text-dim);">Không thể tải sản phẩm. Vui lòng thử lại sau.</div>';
  }
}

async function loadStats() {
  try {
    const res = await fetch('/api/stats');
    if (!res.ok) throw new Error('Không tải được thống kê');
    const data = await res.json();
    const ordersEl = document.getElementById('stat-orders');
    const ratingEl = document.getElementById('stat-rating');
    const productsEl = document.getElementById('stat-products');
    if (ordersEl) ordersEl.textContent = compactNumber(data.total_orders || 0);
    if (ratingEl) ratingEl.textContent = `${Number(data.avg_rating || 0).toFixed(1)}/5`;
    if (productsEl) productsEl.textContent = compactNumber(data.total_products || 0);
  } catch (_) {
    const ordersEl = document.getElementById('stat-orders');
    const ratingEl = document.getElementById('stat-rating');
    const productsEl = document.getElementById('stat-products');
    if (ordersEl) ordersEl.textContent = 'N/A';
    if (ratingEl) ratingEl.textContent = 'N/A';
    if (productsEl) productsEl.textContent = 'N/A';
  }
}

function setChip(el, ok, text) {
  if (!el) return;
  el.textContent = text;
  el.classList.remove('ok', 'bad');
  el.classList.add(ok ? 'ok' : 'bad');
}

async function loadLiveDashboard() {
  const aiReadyEl = document.getElementById('dash-ai-ready');
  const aiChipEl = document.getElementById('dash-ai-chip');
  const vectorCountEl = document.getElementById('dash-vector-count');
  const vectorChipEl = document.getElementById('dash-vector-chip');
  const modelCountEl = document.getElementById('dash-model-count');
  const dataSourceEl = document.getElementById('dash-data-source');
  const ordersChipEl = document.getElementById('dash-orders-chip');
  const reviewsEl = document.getElementById('dash-reviews');
  const behaviorChipEl = document.getElementById('dash-behavior-chip');
  const topCategoryEl = document.getElementById('dash-top-category');
  const productsChipEl = document.getElementById('dash-products-chip');

  try {
    const [healthRes, dbRes, statsRes] = await Promise.all([
      fetch('/api/ai/health'),
      fetch('/api/db/counts'),
      fetch('/api/stats'),
    ]);

    const health = healthRes.ok ? await healthRes.json() : null;
    const db = dbRes.ok ? await dbRes.json() : null;
    const stats = statsRes.ok ? await statsRes.json() : null;

    const aiReady = !!health?.ready;
    if (aiReadyEl) aiReadyEl.textContent = aiReady ? 'READY' : 'DEGRADED';
    setChip(aiChipEl, aiReady, aiReady ? 'all systems go' : 'partial available');

    const vectors = Number(health?.components?.vector_search?.vectors || 0);
    if (vectorCountEl) vectorCountEl.textContent = compactNumber(vectors);
    const vectorOk = !!health?.components?.vector_search?.ready;
    setChip(vectorChipEl, vectorOk, vectorOk ? 'vector online' : 'vector offline');

    const models = health?.components?.recommender?.models || [];
    if (modelCountEl) modelCountEl.textContent = String(models.length);

    const counts = db?.counts || {};
    const dataSource = db?.source || health?.data?.source || 'unknown';
    if (dataSourceEl) dataSourceEl.textContent = String(dataSource).toUpperCase();
    setChip(ordersChipEl, true, `orders: ${compactNumber(counts.orders || 0)}`);

    if (reviewsEl) reviewsEl.textContent = compactNumber(counts.reviews || 0);
    setChip(behaviorChipEl, true, `behavior: ${compactNumber(counts.behavior_logs || 0)}`);

    if (stats?.categories && typeof stats.categories === 'object') {
      const sorted = Object.entries(stats.categories).sort((a, b) => Number(b[1]) - Number(a[1]));
      const topCat = sorted.length ? sorted[0][0] : 'N/A';
      if (topCategoryEl) topCategoryEl.textContent = topCat;
    } else if (topCategoryEl) {
      topCategoryEl.textContent = 'N/A';
    }
    setChip(productsChipEl, true, `products: ${compactNumber(counts.products || stats?.total_products || 0)}`);
  } catch (_) {
    if (aiReadyEl) aiReadyEl.textContent = 'N/A';
    if (vectorCountEl) vectorCountEl.textContent = 'N/A';
    if (modelCountEl) modelCountEl.textContent = 'N/A';
    if (dataSourceEl) dataSourceEl.textContent = 'N/A';
    if (reviewsEl) reviewsEl.textContent = 'N/A';
    if (topCategoryEl) topCategoryEl.textContent = 'N/A';
    setChip(aiChipEl, false, 'api unavailable');
    setChip(vectorChipEl, false, 'api unavailable');
    setChip(ordersChipEl, false, 'orders: N/A');
    setChip(behaviorChipEl, false, 'behavior: N/A');
    setChip(productsChipEl, false, 'products: N/A');
  }
}

async function sendAIChat() {
  const input = document.getElementById('ai-chat-input');
  const msgs = document.getElementById('ai-chat-messages');
  const q = input.value.trim();
  if (!q) return;

  appendUserMessage(msgs, q);
  input.value = '';
  input.disabled = true;
  msgs.scrollTop = msgs.scrollHeight;

  const aiBubble = createAITypingBubble(msgs);
  msgs.scrollTop = msgs.scrollHeight;

  try {
    const data = await callAI(q);
    renderAssistantResponseIntoBubble(aiBubble, data);
    msgs.scrollTop = msgs.scrollHeight;
  } catch (err) {
    aiBubble.textContent = `⚠️ ${err.message || 'Có lỗi xảy ra khi gọi AI.'}`;
    msgs.scrollTop = msgs.scrollHeight;
  } finally {
    input.disabled = false;
    input.focus();
  }
}

window.addEventListener('load', () => {
  document.getElementById('demo-input').focus();
  const chatMessages = document.getElementById('ai-chat-messages');
  appendAssistantMessage(chatMessages, 'Xin chào! Mình là AI tư vấn NexMart. Bạn đang cần mua sản phẩm nào và tầm giá bao nhiêu?');

  document.getElementById('ai-chat-input').addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      sendAIChat();
    }
  });

  document.querySelectorAll('[data-ask]').forEach((link) => {
    link.addEventListener('click', (event) => {
      event.preventDefault();
      const askText = link.getAttribute('data-ask') || 'Tư vấn giúp mình sản phẩm phù hợp';
      prefillAndFocusChat(askText);
    });
  });

  loadFeaturedProducts();
  loadStats();
});
