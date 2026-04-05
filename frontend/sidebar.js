/* Shared sidebar HTML — injected by sidebar.js into every page */
const SIDEBAR_HTML = `
<aside class="sidebar" id="sidebar">
  <div class="sb-logo">
    <div class="sb-logo-icon">🏪</div>
    <span class="sb-logo-text">RetailOS</span>
  </div>
  <nav class="sb-nav">
    <div class="sb-section">Main</div>
    <a href="dashboard.html" class="nav-item"><span class="nav-icon">📊</span><span class="nav-lbl">Dashboard</span></a>
    <a href="inventory.html" class="nav-item"><span class="nav-icon">📦</span><span class="nav-lbl">Inventory</span></a>
    <a href="billing.html"   class="nav-item"><span class="nav-icon">🧾</span><span class="nav-lbl">Billing / POS</span></a>
    <div class="sb-section">Management</div>
    <a href="suppliers.html" class="nav-item"><span class="nav-icon">🏭</span><span class="nav-lbl">Suppliers</span></a>
    <a href="purchases.html" class="nav-item"><span class="nav-icon">🛒</span><span class="nav-lbl">Procurement</span></a>
    <a href="reports.html"   class="nav-item"><span class="nav-icon">📈</span><span class="nav-lbl">Reports</span></a>
    <div class="sb-section">Tools</div>
    <a href="chatbot.html"   class="nav-item"><span class="nav-icon">🤖</span><span class="nav-lbl">AI Assistant</span></a>
  </nav>
  <div class="sb-foot">
    <button class="sb-toggle"><span class="nav-icon">◀</span><span class="nav-lbl">Collapse</span></button>
    <a class="nav-item" data-action="logout" style="cursor:pointer;margin-top:4px"><span class="nav-icon">🚪</span><span class="nav-lbl">Logout</span></a>
  </div>
</aside>
<div class="sidebar-overlay"></div>
`;

document.addEventListener('DOMContentLoaded', () => {
  // Insert sidebar before .main
  const main = document.querySelector('.main');
  if (main) main.insertAdjacentHTML('beforebegin', SIDEBAR_HTML);
});
