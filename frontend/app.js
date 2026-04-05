/* RetailOS — Global App JavaScript */

// ─── CONFIG ──────────────────────────────────────────────────────
const CONFIG = {
  API_BASE: (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://localhost:8000'
    : 'https://your-backend.onrender.com',  // ← replace with your Render URL
  SUPABASE_URL:      'https://your-project.supabase.co',  // ← replace
  SUPABASE_KEY: 'sb_publishable_HYO8fR5JHxTF2tIbo_QDrA_1Su4lnqT'
};

// ─── API CLIENT ──────────────────────────────────────────────────
const API = {
  async req(method, endpoint, body = null) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    const tok = sessionStorage.getItem('sb_token');
    if (tok) opts.headers['Authorization'] = `Bearer ${tok}`;
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(CONFIG.API_BASE + endpoint, opts);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || data.error || `HTTP ${res.status}`);
    return data;
  },
  get:   (ep)       => API.req('GET', ep),
  post:  (ep, body) => API.req('POST', ep, body),
  put:   (ep, body) => API.req('PUT', ep, body),
  del:   (ep)       => API.req('DELETE', ep),
  patch: (ep, body) => API.req('PATCH', ep, body),
};

// ─── AUTH ────────────────────────────────────────────────────────
const Auth = {
  init() {
    const path = window.location.pathname.split('/').pop();
    if (path === 'index.html' || path === '') return;
    const u = Auth.getUser();
    if (!u) { window.location.href = 'index.html'; return; }
    const av = document.querySelector('.avatar');
    if (av) av.textContent = (u.email || 'A')[0].toUpperCase();
  },
  getUser()          { try { return JSON.parse(sessionStorage.getItem('sb_user')); } catch { return null; } },
  setUser(u, tok)    { sessionStorage.setItem('sb_user', JSON.stringify(u)); if (tok) sessionStorage.setItem('sb_token', tok); },
  logout()           { sessionStorage.clear(); window.location.href = 'index.html'; }
};

// ─── TOAST ───────────────────────────────────────────────────────
const Toast = {
  get ct() { return document.getElementById('toast-ct') || (() => { const d = document.createElement('div'); d.id = 'toast-ct'; document.body.appendChild(d); return d; })(); },
  show(title, msg='', type='info', ms=4000) {
    const icons = {success:'✅',error:'❌',warning:'⚠️',info:'ℹ️'};
    const cls   = {success:'ts',error:'te',warning:'tw',info:'ti'};
    const el = document.createElement('div');
    el.className = `toast ${cls[type]||'ti'}`;
    el.innerHTML = `<span class="t-icon">${icons[type]||'ℹ️'}</span><div class="t-body"><div class="t-title">${title}</div>${msg?`<div class="t-msg">${msg}</div>`:''}</div>`;
    this.ct.appendChild(el);
    setTimeout(() => { el.classList.add('removing'); setTimeout(() => el.remove(), 300); }, ms);
  },
  success:(t,m)=>Toast.show(t,m,'success'), error:(t,m)=>Toast.show(t,m,'error'),
  warning:(t,m)=>Toast.show(t,m,'warning'), info:(t,m)=>Toast.show(t,m,'info'),
};

// ─── SIDEBAR ─────────────────────────────────────────────────────
const Sidebar = {
  init() {
    const sb   = document.querySelector('.sidebar');
    const main = document.querySelector('.main');
    if (!sb) return;
    const collapsed = localStorage.getItem('sb_col') === '1';
    if (collapsed) { sb.classList.add('collapsed'); main?.classList.add('expanded'); }

    document.querySelector('.sb-toggle')?.addEventListener('click', () => {
      const c = sb.classList.toggle('collapsed');
      main?.classList.toggle('expanded', c);
      localStorage.setItem('sb_col', c ? '1' : '0');
    });

    // Mobile burger + overlay
    const burger  = document.querySelector('.burger');
    const overlay = document.querySelector('.sidebar-overlay');
    burger?.addEventListener('click', () => { sb.classList.toggle('mob-open'); overlay?.classList.toggle('active'); });
    overlay?.addEventListener('click', () => { sb.classList.remove('mob-open'); overlay?.classList.remove('active'); });

    // Active nav item
    const cur = window.location.pathname.split('/').pop() || 'dashboard.html';
    document.querySelectorAll('.nav-item').forEach(a => {
      if (a.getAttribute('href') === cur) a.classList.add('active');
    });
  }
};

// ─── MODAL ───────────────────────────────────────────────────────
const Modal = {
  open(id)    { const el=document.getElementById(id); if(el){el.classList.add('active'); document.body.style.overflow='hidden';} },
  close(id)   { const el=document.getElementById(id); if(el){el.classList.remove('active'); document.body.style.overflow='';} },
  closeAll()  { document.querySelectorAll('.modal-ov.active').forEach(e=>e.classList.remove('active')); document.body.style.overflow=''; }
};
document.addEventListener('keydown', e => { if(e.key==='Escape') Modal.closeAll(); });

// ─── FORMATTERS ──────────────────────────────────────────────────
const Fmt = {
  cur:  n => '₹' + (+n||0).toLocaleString('en-IN',{minimumFractionDigits:2,maximumFractionDigits:2}),
  num:  n => (+n||0).toLocaleString('en-IN'),
  date: d => d ? new Date(d).toLocaleDateString('en-IN',{day:'2-digit',month:'short',year:'numeric'}) : '—',
  dt:   d => d ? new Date(d).toLocaleString ('en-IN',{day:'2-digit',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit'}) : '—',
  pct:  n => (+n||0).toFixed(1)+'%',
};

// ─── HELPERS ─────────────────────────────────────────────────────
function emptyRow(tbody, cols, msg='No records found') {
  tbody.innerHTML = `<tr><td colspan="${cols}" style="padding:48px 20px;text-align:center;color:var(--t3)">
    <div style="font-size:2.2rem;margin-bottom:10px;opacity:.4">📋</div>
    <div style="font-weight:600;color:var(--t2);margin-bottom:4px">${msg}</div>
    <div style="font-size:.8rem">Try adjusting filters or add new records</div>
  </td></tr>`;
}

function loadingRow(tbody, cols) {
  tbody.innerHTML = `<tr><td colspan="${cols}" style="padding:44px;text-align:center">
    <div class="spin" style="width:24px;height:24px;margin:0 auto 10px"></div>
    <div style="color:var(--t3);font-size:.85rem">Loading...</div>
  </td></tr>`;
}

function stockBadge(qty, thr) {
  if (qty === 0) return '<span class="badge bd">Out of Stock</span>';
  if (qty <= thr) return `<span class="badge bw">Low: ${qty}</span>`;
  return `<span class="badge bs">${qty}</span>`;
}

function payBadge(m) {
  const map={cash:'bs',card:'bi',upi:'bt',credit:'bw'};
  return `<span class="badge ${map[m]||'bm'}">${(m||'cash').toUpperCase()}</span>`;
}

function confirmDel(msg, onConfirm) {
  const id = '_confirm';
  let ov = document.getElementById(id);
  if (!ov) {
    ov = document.createElement('div');
    ov.id = id; ov.className = 'modal-ov';
    ov.innerHTML = `<div class="modal" style="max-width:380px">
      <div class="modal-head"><span class="modal-title">⚠️ Confirm Delete</span></div>
      <div class="modal-body"><p id="_cmsg" style="color:var(--t2);font-size:.9rem;line-height:1.5"></p></div>
      <div class="modal-foot">
        <button class="btn btn-secondary" onclick="Modal.close('_confirm')">Cancel</button>
        <button class="btn btn-danger" id="_cok">Delete</button>
      </div></div>`;
    document.body.appendChild(ov);
    ov.addEventListener('click', e => { if(e.target===ov) Modal.close(id); });
  }
  document.getElementById('_cmsg').textContent = msg;
  const ok = document.getElementById('_cok');
  const nok = ok.cloneNode(true); ok.parentNode.replaceChild(nok, ok);
  nok.addEventListener('click', () => { Modal.close(id); onConfirm(); });
  Modal.open(id);
}

function localSearch(data, fields, q) {
  if (!q) return data;
  const ql = q.toLowerCase();
  return data.filter(r => fields.some(f => String(r[f]||'').toLowerCase().includes(ql)));
}

// ─── CHART DEFAULTS ──────────────────────────────────────────────
function applyChartDefaults() {
  if (typeof Chart === 'undefined') return;
  Chart.defaults.color = '#94A3B8';
  Chart.defaults.borderColor = 'rgba(255,255,255,0.06)';
  Chart.defaults.font.family = "'Outfit', sans-serif";
  Chart.defaults.font.size = 12;
}

// ─── INIT ─────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  Auth.init();
  Sidebar.init();
  applyChartDefaults();
  document.querySelectorAll('.mc').forEach(btn => {
    btn.addEventListener('click', () => { const ov = btn.closest('.modal-ov'); if(ov) Modal.close(ov.id); });
  });
  document.querySelectorAll('[data-action="logout"]').forEach(b => b.addEventListener('click', Auth.logout));
});
