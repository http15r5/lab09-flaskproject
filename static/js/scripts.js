document.addEventListener('DOMContentLoaded', () => {

  const $ = id => document.getElementById(id);
  const safe = (id, cb) => { const el = $(id); if (el) try { cb(el); } catch(e){console.error(e)} };
  const exists = id => !!$(id);
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
    box.innerHTML = `<span style="margin-right:8px">${text}</span><button style="background:none;border:0;color:#fff;font-weight:bold;cursor:pointer">✕</button>`;
    box.querySelector('button').addEventListener('click', () => box.remove());
    document.body.appendChild(box);
    setTimeout(()=>{ box.style.opacity = '0'; box.style.transform = 'translateX(100%)'; setTimeout(()=>box.remove(),400) }, 2500);
  }

  
  setTimeout(() => {
    document.querySelectorAll('.flash-msg').forEach(msg => {
      try { msg.style.opacity = '0'; msg.style.transform = 'translateX(100%)'; setTimeout(()=>msg.remove(),400); } catch(e){}
    });
  }, 2500);

  
  (function initMenus(){
    try {
      const menus = [
        { btn: 'mainMenuButton', menu: 'mainMenu' },
        { btn: 'userMenuButton', menu: 'userMenu' }
      ];
      menus.forEach(({btn, menu}) => {
        const button = $(btn), dropdown = $(menu);
        if (!button || !dropdown) return;
        button.addEventListener('click', (e) => {
          e.stopPropagation();
          
          menus.forEach(({menu: otherMenu, btn: otherBtn}) => {
            if (otherMenu !== menu) {
              $(otherMenu)?.classList.remove('show');
              $(otherBtn)?.classList.remove('active');
            }
          });
          dropdown.classList.toggle('show');
          button.classList.toggle('active');
        });
      });
      document.addEventListener('click', () => {
        document.querySelectorAll('.dropdown-menu').forEach(m => m.classList.remove('show'));
        document.querySelectorAll('.menu-button').forEach(b => b.classList.remove('active'));
      });
    } catch(e) { console.error('initMenus', e); }
  })();

  
  function setupToggle(btnId, sectionId, iconId) {
    const btn = $(btnId), section = $(sectionId), icon = $(iconId);
    if (!btn || !section || !icon) return;
    btn.addEventListener('click', () => {
      const isOpen = section.classList.toggle('open');
      try {
        if (isOpen) section.style.maxHeight = section.scrollHeight + 'px';
        else section.style.maxHeight = '0px';
      } catch(e){}
      try { icon.style.transform = isOpen ? 'rotate(180deg)' : 'rotate(0deg)'; } catch(e){}
    });
  }


  setupToggle('toggleProducts', 'sectionProducts', 'iconProducts');
  setupToggle('toggleOrders', 'sectionOrders', 'iconOrders');
  setupToggle('toggleFeedback', 'sectionFeedback', 'iconFeedback');
  setupToggle('toggleProducts', 'productsSection', 'toggleIcon');
  setupToggle('toggleProducts', 'productsSection', 'iconProducts');
  setupToggle('toggleProducts', 'sectionProducts', 'toggleIcon');

  const API_BASE = '/api/v1';
  async function safeFetchJson(url, opts) {
    const res = await fetch(url, opts);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }

  // товари
  async function loadProducts() {
    try {
      const loading = $('loading-products'), list = $('products-list');
      if (!loading || !list) return;
      loading.classList.remove('hidden'); list.innerHTML = '';
      const products = await safeFetchJson(`${API_BASE}/products`);
      if (!products || products.length === 0) {
        list.innerHTML = "<p class='text-gray-600 text-center py-4'>Продуктів немає</p>";
      } else {
        products.forEach(p => {
          const div = document.createElement('div');
          div.className = 'bg-white border rounded-lg p-4 shadow hover:shadow-lg transition';
          div.innerHTML = `<span class="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">ID: ${p.id}</span>
            <h3 class="font-semibold text-lg mt-2">${p.name}</h3>
            <p class="text-blue-600 font-bold text-xl">${p.price} грн</p>`;
          list.appendChild(div);
        });
      }
      loading.classList.add('hidden');
    } catch(err){ $('loading-products')?.classList.add('hidden'); showMessage('❌ ' + err.message, 'error'); }
  }

  // фідбеки
  async function loadFeedback() {
    try {
      const loading = $('loading-feedback'), list = $('feedback-list');
      if (!loading || !list) return;
      loading.classList.remove('hidden'); list.innerHTML = '';
      const feedbacks = await safeFetchJson(`${API_BASE}/feedback`);
      if (!feedbacks || feedbacks.length===0) list.innerHTML = "<p class='text-gray-600 text-center py-4'>Відгуків ще немає</p>";
      else {
        feedbacks.forEach(f => {
          const wrap = document.createElement('div');
          wrap.className = 'bg-white border rounded-lg p-4 shadow flex justify-between';
          wrap.innerHTML = `<div><p class="font-semibold">${f.name}</p><p class="text-gray-500 text-sm">${f.email}</p><p class="mt-2 text-gray-700">${f.message}</p></div>`;
          const btn = document.createElement('button');
          btn.className = 'text-red-600 hover:bg-red-50 px-3 py-1 rounded';
          btn.textContent = '🗑️';
          btn.addEventListener('click', ()=> deleteFeedback(f.id));
          wrap.appendChild(btn);
          list.appendChild(wrap);
        });
      }
      loading.classList.add('hidden');
    } catch(err){ $('loading-feedback')?.classList.add('hidden'); showMessage('❌ '+err.message,'error'); }
  }

  async function addFeedback(name, email, message) {
    try {
      const res = await fetch(`${API_BASE}/feedback`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name,email,message}) });
      if (!res.ok) throw new Error('Помилка при додаванні');
      showMessage('✅ Відгук додано','success'); loadFeedback();
    } catch(err){ showMessage('❌ '+err.message,'error'); }
  }

  async function deleteFeedback(id) {
    try {
      if (!confirm('Видалити відгук?')) return;
      const res = await fetch(`${API_BASE}/feedback/${id}`, { method:'DELETE' });
      if (!res.ok) throw new Error('Не вдалося видалити');
      showMessage('🗑️ Відгук видалено','success'); loadFeedback();
    } catch(err){ showMessage('❌ '+err.message,'error'); }
  }

  // замовлення
  async function loadOrders() {
    try {
      const loading = $('loading-orders'), list = $('orders-list');
      if (!loading || !list) return;
      loading.classList.remove('hidden'); list.innerHTML = '';
      const orders = await safeFetchJson(`${API_BASE}/orders`);
      if (!orders || orders.length===0) list.innerHTML = "<p class='text-gray-600 text-center py-4'>Замовлень ще немає</p>";
      else {
        orders.forEach(o => {
          const div = document.createElement('div'); div.className = 'bg-white border rounded-lg p-4 shadow';
          div.innerHTML = `<div class="flex justify-between"><div><p><b>Email:</b> ${o.email}</p><p><b>Адреса:</b> ${o.address}</p><p><b>ID продукту:</b> ${o.product_id}</p><p><b>Кількість:</b> ${o.quantity}</p><p><b>Статус:</b> <span class="text-purple-700 font-semibold">${o.status||"Новий"}</span></p><p><b>Сума:</b> ${o.total_price ?? "?"} грн</p></div><div class="flex flex-col items-end gap-2"><select onchange="changeOrderStatus(${o.id}, this.value)" class="px-2 py-1 border rounded"><option value="">Змінити статус</option><option value="Новий">Новий</option><option value="В обробці">В обробці</option><option value="Відправлено">Відправлено</option><option value="Доставлено">Доставлено</option></select><button class="text-red-600 hover:bg-red-50 px-3 py-1 rounded" data-order-id="${o.id}">🗑️</button></div></div>`;
          list.appendChild(div);
          const delBtn = list.querySelector(`button[data-order-id="${o.id}"]`);
          delBtn?.addEventListener('click', ()=> deleteOrder(o.id));
        });
      }
      loading.classList.add('hidden');
    } catch(err){ $('loading-orders')?.classList.add('hidden'); showMessage('❌ '+err.message,'error'); }
  }

  async function addOrder(data) {
    try {
      const res = await fetch(`${API_BASE}/orders`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(data) });
      if (!res.ok) throw new Error('Не вдалося створити замовлення');
      showMessage('✅ Замовлення створено','success'); loadOrders();
    } catch(err){ showMessage('❌ '+err.message,'error'); }
  }

  async function changeOrderStatus(id, status) {
    if (!status) return;
    try {
      const res = await fetch(`${API_BASE}/orders/${id}`, { method:'PUT', headers:{'Content-Type':'application/json'}, body: JSON.stringify({status}) });
      if (!res.ok) throw new Error('Не вдалося змінити статус');
      showMessage('🔄 Статус оновлено','success'); loadOrders();
    } catch(err){ showMessage('❌ '+err.message,'error'); }
  }

  async function deleteOrder(id) {
    try {
      if (!confirm('Видалити замовлення?')) return;
      const res = await fetch(`${API_BASE}/orders/${id}`, { method:'DELETE' });
      if (!res.ok) throw new Error('Не вдалося видалити замовлення');
      showMessage('🗑️ Замовлення видалено','success'); loadOrders();
    } catch(err){ showMessage('❌ '+err.message,'error'); }
  }

  
  (function clientModals(){
    let currentOrderId = null, deleteOrderId = null;

    window.openDetailsModal = async function(orderId){
      try {
        const res = await fetch(`/order_details/${orderId}`);
        if (!res.ok) { showMessage('❌ Помилка завантаження деталей','error'); return; }
        const data = await res.json();
        if (!data.success) { showMessage('❌ Помилка','error'); return; }
        const o = data.order; currentOrderId = o.id;
        if ($('detailsContent')) {
          $('detailsContent').innerHTML = `<p><b>ID:</b> ${o.id}</p><p><b>Адреса:</b> ${o.address}</p><p><b>Ціна:</b> ${o.total_price} $</p><p><b>Статус:</b> ${o.status}</p><p><b>Дата:</b> ${o.date}</p><p><b>Промокод:</b> ${o.promo_code||'-'}</p>`;
        }
        if ($('productsList')) {
          $('productsList').innerHTML = '';
          if (o.products?.length>0) o.products.forEach(p=> $('productsList').innerHTML+=`<li>${p.name} — ${p.price} $ × ${p.quantity}</li>`);
          else $('productsList').innerHTML = '<li class="italic text-gray-500">Товари відсутні 😅</li>';
        }
        if ($('cancelInsideBtn') && $('deleteInsideBtn')) {
          if (o.status !== 'Скасовано' && o.status !== 'Очікує скасування') { $('cancelInsideBtn').classList.remove('hidden'); $('deleteInsideBtn').classList.add('hidden'); }
          else if (o.status === 'Скасовано') { $('cancelInsideBtn').classList.add('hidden'); $('deleteInsideBtn').classList.remove('hidden'); }
          else { $('cancelInsideBtn').classList.add('hidden'); $('deleteInsideBtn').classList.add('hidden'); }
        }
        $('detailsModal')?.classList.remove('hidden');
      } catch(e){ console.error(e); showMessage('❌ Ошибка','error'); }
    };

    window.closeDetailsModal = () => $('detailsModal')?.classList.add('hidden');
    safe('cancelInsideBtn', btn => btn.addEventListener('click', ()=>{ window.closeDetailsModal(); window.openCancelModal(currentOrderId); }));
    safe('deleteInsideBtn', btn => btn.addEventListener('click', ()=>{ window.closeDetailsModal(); window.openDeleteModal(currentOrderId); }));
    window.openCancelModal = (id) => { currentOrderId = id; $('cancelModal')?.classList.remove('hidden'); };
    window.closeCancelModal = () => $('cancelModal')?.classList.add('hidden');
    safe('confirmCancelBtn', btn => btn.addEventListener('click', async ()=> { if (!currentOrderId) return; const r = await fetch(`/cancel_order/${currentOrderId}`, {method:'POST'}); if (r.ok){ window.closeCancelModal(); setTimeout(()=>location.reload(),300); } }));
    window.openDeleteModal = (id) => { deleteOrderId = id; $('deleteModal')?.classList.remove('hidden'); };
    window.closeDeleteModal = () => $('deleteModal')?.classList.add('hidden');
    safe('confirmDeleteBtn', btn => btn.addEventListener('click', async ()=> { if (!deleteOrderId) return; const r = await fetch(`/delete_order/${deleteOrderId}`, {method:'POST'}); if (!r.ok) return; const data = await r.json(); if (data.success){ document.querySelector(`#order-${deleteOrderId}`)?.remove(); window.closeDeleteModal(); } }));
  })();

  safe('orderForm', form => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = $('order_email')?.value.trim() || '';
      const address = $('order_address')?.value.trim() || '';
      const product_id = Number($('order_product')?.value || 0);
      const quantity = Number($('order_quantity')?.value || 0);
      if (!email || !address || !product_id || !quantity) { showMessage('❌ Заповніть усі поля!','error'); return; }
      addOrder({ email, address, product_id, quantity });
      form.reset();
    });
  });

  safe('feedbackForm', form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = $('name')?.value.trim() || '';
      const email = $('email')?.value.trim() || '';
      const msg = ($('messageText')?.value || $('message')?.value || '').trim();
      if (!name || !email || !msg) { showMessage('❌ Заповніть усі поля!','error'); return; }
      const action = form.getAttribute('action') || form.action || '';
      if (action && action.trim()) {
        try {
          const res = await fetch(action, { method:'POST', body: new FormData(form) });
          if (res.ok) { $('thankYouModal')?.classList.remove('hidden'); form.reset(); } else { showMessage('⚠️ Помилка при відправці','error'); }
        } catch(e){ showMessage('⚠️ Помилка мережі','error'); }
      } else {
        await addFeedback(name, email, msg);
      }
    });
    safe('closeModal', btn => btn.addEventListener('click', ()=> $('thankYouModal')?.classList.add('hidden')));
  });
  
  if ($('products-list') || $('loading-products')) { loadProducts().catch(e => console.error(e)); }
  if ($('feedback-list') || $('loading-feedback')) { loadFeedback().catch(e => console.error(e)); }
  if ($('orders-list') || $('loading-orders')) { loadOrders().catch(e => console.error(e)); }
  window.changeOrderStatus = changeOrderStatus;
  window.deleteOrder = deleteOrder;
  window.addOrder = addOrder;
  window.openDetailsModal = window.openDetailsModal;
  window.openCancelModal = window.openCancelModal;
  window.openDeleteModal = window.openDeleteModal;
  window.closeDetailsModal = window.closeDetailsModal;
  window.closeCancelModal = window.closeCancelModal;
  window.closeDeleteModal = window.closeDeleteModal;
});
