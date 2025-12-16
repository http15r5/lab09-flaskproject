document.addEventListener('DOMContentLoaded', () => {

  const $ = id => document.getElementById(id);
  const safe = (id, cb) => { const el = $(id); if (el) try { cb(el); } catch(e){console.error(e)} };

  function showMessage(text, type = 'info') {
    const container = $('message');
    if (container) {
      container.textContent = text;
      container.className = type + ' show';
      setTimeout(() => container.classList.remove('show'), 4000);
      return;
    }
    const box = document.createElement('div');
    box.className = 'flash-msg fixed top-5 right-5 p-4 rounded-lg shadow-lg text-white text-sm z-50';
    if (type === 'success') box.style.background = 'rgba(34,197,94,0.9)';
    if (type === 'error') box.style.background = 'rgba(239,68,68,0.9)';
    box.innerHTML = `<span>${text}</span> <button style="background:none;border:0;color:#fff;font-weight:bold;cursor:pointer">✕</button>`;
    box.querySelector('button').addEventListener('click', () => box.remove());
    document.body.appendChild(box);
    setTimeout(() => box.remove(), 2500);
  }

  /* ===================== MENU ===================== */
  (function initMenus(){
    const menus = [
      { btn: 'mainMenuButton', menu: 'mainMenu' },
      { btn: 'userMenuButton', menu: 'userMenu' }
    ];
    menus.forEach(({btn, menu}) => {
      const b = $(btn), m = $(menu);
      if (!b || !m) return;
      b.addEventListener('click', e => {
        e.stopPropagation();
        menus.forEach(x => $(x.menu)?.classList.remove('show'));
        m.classList.toggle('show');
      });
    });
    document.addEventListener('click', () =>
      document.querySelectorAll('.dropdown-menu').forEach(m => m.classList.remove('show'))
    );
  })();

  /* ===================== TOGGLES ===================== */
  function setupToggle(btnId, sectionId, iconId) {
    const btn = $(btnId), section = $(sectionId), icon = $(iconId);
    if (!btn || !section) return;
    btn.addEventListener('click', () => {
      const open = section.classList.toggle('open');
      section.style.maxHeight = open ? section.scrollHeight + 'px' : '0';
      if (icon) icon.style.transform = open ? 'rotate(180deg)' : 'rotate(0deg)';
    });
  }

  setupToggle('toggleProducts', 'sectionProducts', 'iconProducts');
  setupToggle('toggleOrders', 'sectionOrders', 'iconOrders');
  setupToggle('toggleFeedback', 'sectionFeedback', 'iconFeedback');

  /* ===================== API ===================== */
  const API_BASE = '/api/v1';

  async function safeFetchJson(url, opts) {
    const r = await fetch(url, opts);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  }

  async function loadProducts() {
    try {
      const list = $('products-list');
      if (!list) return;
      list.innerHTML = '';
      const data = await safeFetchJson(`${API_BASE}/products`);
      data.forEach(p => list.innerHTML += `<div><b>${p.name}</b> — ${p.price} грн</div>`);
    } catch(e){ showMessage(e.message,'error'); }
  }

  async function loadFeedback() {
    try {
      const list = $('feedback-list');
      if (!list) return;
      list.innerHTML = '';
      const data = await safeFetchJson(`${API_BASE}/feedback`);
      data.forEach(f => {
        const el = document.createElement('div');
        el.innerHTML = `${f.name}: ${f.message} <button>🗑️</button>`;
        el.querySelector('button').onclick = () => deleteFeedback(f.id);
        list.appendChild(el);
      });
    } catch(e){ showMessage(e.message,'error'); }
  }

  async function deleteFeedback(id) {
    await fetch(`${API_BASE}/feedback/${id}`, {method:'DELETE'});
    loadFeedback();
  }

  async function loadOrders() {
    try {
      const list = $('orders-list');
      if (!list) return;
      list.innerHTML = '';
      const data = await safeFetchJson(`${API_BASE}/orders`);
      data.forEach(o => {
        list.innerHTML += `
          <div id="order-${o.id}">
            ${o.email} — ${o.status}
            <select onchange="changeOrderStatus(${o.id}, this.value)">
              <option value="">Статус</option>
              <option>Новий</option>
              <option>В обробці</option>
              <option>Відправлено</option>
            </select>
            <button onclick="deleteOrder(${o.id})">🗑️</button>
          </div>`;
      });
    } catch(e){ showMessage(e.message,'error'); }
  }

  async function changeOrderStatus(id, status) {
    if (!status) return;
    await fetch(`${API_BASE}/orders/${id}`, {
      method:'PUT',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({status})
    });
    loadOrders();
  }

  async function deleteOrder(id) {
    await fetch(`${API_BASE}/orders/${id}`, {method:'DELETE'});
    loadOrders();
  }

  /* ======= ГЛОБАЛЬНІ (КРИТИЧНО ДЛЯ HTML) ======= */
  window.changeOrderStatus = changeOrderStatus;
  window.deleteOrder = deleteOrder;

  /* ===================== INIT ===================== */
  if ($('products-list')) loadProducts();
  if ($('feedback-list')) loadFeedback();
  if ($('orders-list')) loadOrders();

});
