// Tab navigation
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(btn.dataset.tab).classList.add('active');
  });
});

// 自動生成模型顏色
const colorPalette = [
  { border: '#3fb950', bg: 'rgba(63, 185, 80, 0.2)', rgb: '63, 185, 80' },    // 綠
  { border: '#a855f7', bg: 'rgba(168, 85, 247, 0.2)', rgb: '168, 85, 247' },  // 紫
  { border: '#58a6ff', bg: 'rgba(88, 166, 255, 0.2)', rgb: '88, 166, 255' },  // 藍
  { border: '#d29922', bg: 'rgba(210, 153, 34, 0.2)', rgb: '210, 153, 34' },  // 黃
  { border: '#f85149', bg: 'rgba(248, 81, 73, 0.2)', rgb: '248, 81, 73' },    // 紅
  { border: '#f0883e', bg: 'rgba(240, 136, 62, 0.2)', rgb: '240, 136, 62' },  // 橙
  { border: '#39d353', bg: 'rgba(57, 211, 83, 0.2)', rgb: '57, 211, 83' },    // 亮綠
  { border: '#79c0ff', bg: 'rgba(121, 192, 255, 0.2)', rgb: '121, 192, 255' },// 淡藍
  { border: '#d2a8ff', bg: 'rgba(210, 168, 255, 0.2)', rgb: '210, 168, 255' },// 淡紫
  { border: '#ffa657', bg: 'rgba(255, 166, 87, 0.2)', rgb: '255, 166, 87' },  // 淡橙
];

function getModelColor(model, index) {
  return colorPalette[index % colorPalette.length];
}

async function initDashboard() {
  try {
    const response = await fetch('./data/tokens.json');
    const data = await response.json();
    
    // Update footer
    const updated = new Date(data.updated).toLocaleString('zh-TW', { 
      timeZone: 'Asia/Taipei',
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit'
    });
    document.querySelector('footer p').innerHTML = `最後更新: ${updated} | <a href="https://amangames002-pixel-office.surge.sh" target="_blank">Pixel Office</a>`;
    
    // ========== 1. 總覽頁面 ==========
    const dailyData = data.dailyUsage || [];
    
    // 獲取所有模型
    let allModels = data.allModels || [...new Set(dailyData.map(d => d.model))];
    const modelIndex = {};
    allModels.forEach((m, i) => modelIndex[m] = i);
    
    // 日期範圍（過去 7 天）
    const today = new Date().toISOString().slice(0, 10);
    const dates = [...new Set(dailyData.map(d => d.date))].sort().slice(-7);
    
    // 計算今日/本週/本月用量
    const todayUsage = dailyData.filter(d => d.date === today);
    const todayTotal = todayUsage.reduce((sum, d) => sum + d.input + d.output, 0);
    document.getElementById('todayUsage').textContent = todayTotal > 0 ? (todayTotal / 1000).toFixed(0) + 'K' : '0';
    
    // 本週（過去 7 天）
    const weekTotal = dailyData
      .filter(d => dates.includes(d.date))
      .reduce((sum, d) => sum + d.input + d.output, 0);
    document.getElementById('weekUsage').textContent = weekTotal > 0 ? (weekTotal / 1000).toFixed(0) + 'K' : '0';
    
    // 本月
    const monthDates = [...new Set(dailyData.map(d => d.date))].sort().slice(-30);
    const monthTotal = dailyData
      .filter(d => monthDates.includes(d.date))
      .reduce((sum, d) => sum + d.input + d.output, 0);
    document.getElementById('monthUsage').textContent = monthTotal > 0 ? (monthTotal / 1000).toFixed(0) + 'K' : '0';
    
    // 趨勢圖
    const trendCtx = document.getElementById('trendChart');
    if (trendCtx) {
      const models = [...new Set(dailyData.map(d => d.model))];
      const trendDatasets = models.map((model, idx) => {
        const modelData = dailyData.filter(d => d.model === model);
        const color = getModelColor(model, modelIndex[model]);
        return {
          label: model,
          data: dates.map(date => {
            const entry = modelData.find(d => d.date === date);
            return entry ? entry.input + entry.output : 0;
          }),
          borderColor: color.border,
          backgroundColor: color.bg,
          fill: true,
          tension: 0.3
        };
      });
      
      new Chart(trendCtx, {
        type: 'line',
        data: { labels: dates.map(d => d.slice(5)), datasets: trendDatasets },
        options: {
          responsive: true,
          plugins: { 
            legend: { 
              position: 'top', 
              labels: { color: '#8b949e' } 
            } 
          },
          scales: {
            y: { 
              ticks: { color: '#8b949e' }, 
              grid: { color: '#30363d' },
              title: { display: true, text: 'Tokens', color: '#8b949e' }
            },
            x: { ticks: { color: '#8b949e' }, grid: { color: '#30363d' } }
          }
        }
      });
    }
    
    // 模型卡片
    const modelStats = data.modelStats || [];
    const maxTotal = Math.max(...modelStats.map(m => m.total), 1);
    
    const container = document.getElementById('modelCards');
    if (container) {
      container.innerHTML = '';
      
      modelStats.forEach((stat, idx) => {
        const percent = Math.round((stat.total / maxTotal) * 100);
        const color = getModelColor(stat.model, idx);
        
        const card = document.createElement('div');
        card.className = 'model-card';
        card.style.borderLeftColor = color.border;
        
        card.innerHTML = `
          <span class="model-name">${stat.model}</span>
          <div class="model-bar" style="width: ${percent}%; background: ${color.border}"></div>
          <span class="model-value">${(stat.total / 1000).toFixed(1)}K</span>
        `;
        container.appendChild(card);
      });
      
      const countEl = document.getElementById('modelCount');
      if (countEl) {
        countEl.textContent = `共 ${allModels.length} 個模型`;
      }
    }
    
    // ========== 2. 詳細用量頁面 ==========
    renderDetailedStats(data, allModels);
    
  } catch (error) {
    console.error('Failed to load token data:', error);
  }
}

async function renderDetailedStats(data, allModels) {
  const container = document.getElementById('detailedStats');
  if (!container) return;
  
  const dailyData = data.dailyUsage || [];
  const dates = [...new Set(dailyData.map(d => d.date))].sort().reverse().slice(0, 7);
  
  let html = '';
  
  // 每日用量表格
  html += `<div class="stats-section">
    <h3><i class="fas fa-calendar-day"></i> 每日用量</h3>
    <div class="table-scroll">
    <table class="detail-table">
      <thead><tr><th>日期</th>`;
  
  allModels.forEach(m => html += `<th>${m}</th>`);
  html += `<th>總計</th></tr></thead><tbody>`;
  
  dates.forEach(date => {
    html += `<tr><td>${date}</td>`;
    let dayTotal = 0;
    allModels.forEach(model => {
      const entry = dailyData.find(d => d.date === date && d.model === model);
      const val = entry ? entry.total : 0;
      dayTotal += val;
      html += `<td>${val ? (val/1000).toFixed(0) + 'K' : '-'}</td>`;
    });
    html += `<td><strong>${(dayTotal/1000).toFixed(0)}K</strong></td></tr>`;
  });
  html += `</tbody></table></div></div>`;
  
  // 模型統計
  const modelStats = data.modelStats || [];
  html += `<div class="stats-section">
    <h3><i class="fas fa-chart-pie"></i> 模型使用分布</h3>
    <div class="analysis-grid">`;
  
  const totalUsage = modelStats.reduce((sum, m) => sum + m.total, 0);
  
  modelStats.forEach((stat, idx) => {
    const color = getModelColor(stat.model, idx);
    const percent = totalUsage > 0 ? Math.round((stat.total / totalUsage) * 100) : 0;
    html += `<div class="analysis-card">
      <h4>${stat.model}</h4>
      <div class="progress-bar">
        <div class="progress-fill" style="width: ${percent}%; background: ${color.border}"></div>
      </div>
      <div class="stat-row">
        <span>Input:</span>
        <span>${(stat.totalInput/1000).toFixed(1)}K</span>
      </div>
      <div class="stat-row">
        <span>Output:</span>
        <span>${(stat.totalOutput/1000).toFixed(1)}K</span>
      </div>
      <div class="stat-row total">
        <span>Total:</span>
        <span>${(stat.total/1000).toFixed(1)}K (${percent}%)</span>
      </div>
    </div>`;
  });
  
  html += `</div></div>`;
  
  container.innerHTML = html;
}

// Initialize
initDashboard();
loadXDaily();

// Folder expand/collapse
document.querySelectorAll('.folder-item').forEach(folder => {
  folder.addEventListener('click', () => folder.classList.toggle('expanded'));
});

// ========== X Daily 載入 ==========
async function loadXDaily() {
  const container = document.getElementById('xdaily-list');
  if (!container) return;
  
  try {
    // 從 GitHub Pages 獲取 X Daily 列表
    const indexUrl = 'https://amangames002-ctrl.github.io/';
    const response = await fetch(indexUrl);
    const html = await response.text();
    
    // 解析日期連結
    const dateRegex = /(\d{4}-\d{2}-\d{2})\.html/g;
    const dates = [];
    let match;
    while ((match = dateRegex.exec(html)) !== null) {
      dates.push(match[1]);
    }
    
    // 去重並排序（最新的在前）
    const uniqueDates = [...new Set(dates)].sort().reverse().slice(0, 14);
    
    if (uniqueDates.length === 0) {
      container.innerHTML = '<p style="color:#8b949e;text-align:center;">尚無資料</p>';
      return;
    }
    
    // 生成卡片
    let cardsHtml = '';
    for (const date of uniqueDates) {
      const dateObj = new Date(date);
      const twDate = dateObj.toLocaleDateString('zh-TW', { 
        year: 'numeric', month: 'long', day: 'numeric' 
      });
      const dayOfWeek = ['日', '一', '二', '三', '四', '五', '六'][dateObj.getDay()];
      
      // 從 index.html 抓取該日期的推文數
      let count = '查看';
      try {
        const dayResp = await fetch(`${indexUrl}${date}.html`);
        const dayHtml = await dayResp.text();
        const countMatch = dayHtml.match(/(\d+)\s+則推文/);
        if (countMatch) {
          count = countMatch[1] + ' 則';
        }
      } catch (e) {}
      
      cardsHtml += `
        <a href="${indexUrl}${date}.html" target="_blank" class="xdaily-card">
          <div class="date">📅 ${twDate}</div>
          <div class="count">${count}</div>
          <span class="xdaily-link">查看推文 →</span>
        </a>
      `;
    }
    
    container.innerHTML = cardsHtml;
  } catch (error) {
    console.error('Failed to load X Daily:', error);
    container.innerHTML = '<p style="color:#f85149;text-align:center;">載入失敗，請稍後重試</p>';
  }
}
