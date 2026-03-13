const fmt = new Intl.NumberFormat('en-US');
let dashboard = null;
let activeRange = 'daily';

function n(v) { return fmt.format(Number(v || 0)); }
function esc(s) { return String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

function renderSummary(data) {
  const s = data.summary;
  document.getElementById('updatedAt').textContent = `更新時間：${data.updated}`;
  document.getElementById('grandTotal').textContent = n(s.grandTotal);
  document.getElementById('grandInput').textContent = n(s.grandInput);
  document.getElementById('grandOutput').textContent = n(s.grandOutput);
  document.getElementById('uniqueModels').textContent = n(s.uniqueModels);
  document.getElementById('uniqueProviders').textContent = n(s.uniqueProviders);
  document.getElementById('totalSessions').textContent = n(s.totalSessions);
  document.getElementById('totalMessages').textContent = n(s.totalMessages);
  document.getElementById('activeDays').textContent = n(s.activeDays);
}

function renderPeriodTable() {
  const rows = dashboard[activeRange].total;
  document.getElementById('periodTable').innerHTML = rows.map(r => `
    <tr>
      <td>${esc(r.period)}</td>
      <td class="num">${n(r.total)}</td>
      <td class="num">${n(r.input)}</td>
      <td class="num">${n(r.output)}</td>
      <td class="num">${n(r.count)}</td>
    </tr>`).join('');
}

function renderModelsTable(filter='') {
  const q = filter.trim().toLowerCase();
  const rows = dashboard.models.filter(r => !q || r.modelKey.toLowerCase().includes(q));
  document.getElementById('modelsTable').innerHTML = rows.map((r, i) => `
    <tr>
      <td class="num">${i + 1}</td>
      <td><span class="model-key">${esc(r.modelKey)}</span></td>
      <td class="num">${n(r.total)}</td>
      <td class="num">${n(r.input)}</td>
      <td class="num">${n(r.output)}</td>
      <td class="num">${n(r.count)}</td>
    </tr>`).join('');
}

function renderProvidersTable() {
  document.getElementById('providersTable').innerHTML = dashboard.providers.map(r => `
    <tr>
      <td><span class="model-key">${esc(r.provider)}</span></td>
      <td class="num">${n(r.total)}</td>
      <td class="num">${n(r.input)}</td>
      <td class="num">${n(r.output)}</td>
      <td class="num">${n(r.count)}</td>
    </tr>`).join('');
}

function renderPeriodModelTable(filter='') {
  const q = filter.trim().toLowerCase();
  const rows = dashboard[activeRange].byModel.filter(r => !q || (`${r.period} ${r.modelKey}`).toLowerCase().includes(q));
  document.getElementById('periodModelTable').innerHTML = rows.map(r => `
    <tr>
      <td>${esc(r.period)}</td>
      <td><span class="model-key">${esc(r.modelKey)}</span></td>
      <td class="num">${n(r.total)}</td>
      <td class="num">${n(r.input)}</td>
      <td class="num">${n(r.output)}</td>
      <td class="num">${n(r.count)}</td>
    </tr>`).join('');
}

function bindEvents() {
  document.querySelectorAll('.tab').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
      btn.classList.add('active');
      activeRange = btn.dataset.range;
      renderPeriodTable();
      renderPeriodModelTable(document.getElementById('periodModelSearch').value);
    });
  });
  document.getElementById('modelSearch').addEventListener('input', e => renderModelsTable(e.target.value));
  document.getElementById('periodModelSearch').addEventListener('input', e => renderPeriodModelTable(e.target.value));
}

async function main() {
  const res = await fetch('./data/tokens.json');
  dashboard = await res.json();
  renderSummary(dashboard);
  renderPeriodTable();
  renderModelsTable();
  renderProvidersTable();
  renderPeriodModelTable();
  bindEvents();
}

main().catch(err => {
  console.error(err);
  document.getElementById('updatedAt').textContent = '載入失敗';
});
