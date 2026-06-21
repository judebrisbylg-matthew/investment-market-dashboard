const signalClass = {
  '绿灯': 'ok',
  '正常绿灯': 'ok',
  '黄灯': 'watch',
  '预警黄灯': 'watch',
  '红灯': 'danger',
  '危险红灯': 'danger',
  '继续观察': 'ok',
  '观察等待': 'watch',
  '暂不加仓': 'danger',
  '止盈跟踪': 'watch',
  '等待': 'watch',
  '防守': 'danger',
  '进攻': 'ok',
  '低': 'ok',
  '中': 'watch',
  '中高': 'warn',
  '高': 'danger',
  '谨慎': 'watch',
  '分散': 'watch',
  '风险校验': 'danger',
  '优质观察': 'ok',
  '跟踪验证': 'watch',
  '宏观分散': 'watch',
  '节奏参考': 'warn',
  '待核验': 'watch',
  '无新增可靠观点': 'muted',
  '建议加仓': 'ok',
  '利多': 'ok',
  '利空': 'danger',
  '中性': 'watch',
  '中高': 'warn'
};

let dashboardData;
let activeIndustry = 0;

const coreRiskOrder = [
  '10年期美债收益率',
  '国际油价（美元/桶）',
  '美元指数',
  '实际利率',
  '信用利差',
  'VIX',
  'A股成交额',
  '估值分位'
];

function getCoreRiskItems(items) {
  const byName = new Map(items.map((item) => [item.name, item]));
  return coreRiskOrder.map((name) => byName.get(name)).filter(Boolean);
}

function $(id) {
  return document.getElementById(id);
}

function setupCanvas(id) {
  const canvas = $(id);
  const rect = canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  canvas.width = Math.max(1, rect.width * dpr);
  canvas.height = Math.max(1, rect.height * dpr);
  const ctx = canvas.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return { ctx, width: rect.width, height: rect.height };
}

function isCompactCanvas(width) {
  return width < 520;
}

function clear(ctx, width, height) {
  ctx.clearRect(0, 0, width, height);
}

function drawText(ctx, text, x, y, options = {}) {
  ctx.fillStyle = options.color || '#cbd5e1';
  ctx.font = `${options.weight || 500} ${options.size || 12}px Inter, "PingFang SC", sans-serif`;
  ctx.textAlign = options.align || 'left';
  ctx.fillText(text, x, y);
}

function formatIndustryLabel(name, compact) {
  const simplified = name
    .replace('/中国科技资产', '/中国科技')
    .replace('/智能制造', '/智造')
    .replace('/数据中心能源', '/数据中心')
    .replace('/中国顺周期', '/顺周期');
  const maxChars = compact ? 7 : 9;
  return simplified.length > maxChars ? `${simplified.slice(0, maxChars)}…` : simplified;
}

function industryScore(item) {
  return Math.round(item.prosperity * .45 + item.heat * .3 + (100 - item.risk) * .25);
}

function sortIndustriesByTierAndScore(items) {
  const tierOrder = { '核心主线': 0, '候补轮动': 1 };
  return [...items].sort((a, b) => {
    const tierDiff = (tierOrder[a.tier] ?? 9) - (tierOrder[b.tier] ?? 9);
    if (tierDiff !== 0) return tierDiff;
    return industryScore(b) - industryScore(a);
  });
}

function drawGauge(items) {
  const coreItems = getCoreRiskItems(items);
  const score = Math.round(coreItems.reduce((sum, item) => sum + item.score, 0) / coreItems.length);
  const { ctx, width, height } = setupCanvas('riskGauge');
  clear(ctx, width, height);
  const cx = width / 2;
  const cy = height / 2 + 42;
  const radius = Math.min(width, height) * 0.35;
  ctx.lineWidth = 18;
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.strokeStyle = '#1e293b';
  ctx.arc(cx, cy, radius, Math.PI, Math.PI * 2);
  ctx.stroke();
  const grad = ctx.createLinearGradient(cx - radius, cy, cx + radius, cy);
  grad.addColorStop(0, '#22c55e');
  grad.addColorStop(.58, '#facc15');
  grad.addColorStop(1, '#ef4444');
  ctx.beginPath();
  ctx.strokeStyle = grad;
  ctx.arc(cx, cy, radius, Math.PI, Math.PI + Math.PI * score / 100);
  ctx.stroke();
  drawText(ctx, String(score), cx, cy - 8, { size: 42, weight: 800, align: 'center', color: '#f8fafc' });
  drawText(ctx, '风险温度', cx, cy + 24, { size: 13, align: 'center', color: '#94a3b8' });
  drawText(ctx, score >= 70 ? '偏热' : score >= 45 ? '可控偏谨慎' : '低风险', cx, cy + 48, { size: 12, align: 'center', color: score >= 70 ? '#ef4444' : '#facc15' });
}

function drawRadar(items) {
  const { ctx, width, height } = setupCanvas('riskRadar');
  clear(ctx, width, height);
  const coreItems = getCoreRiskItems(items);
  const names = coreItems.map((item) => item.name.replace('10年期', '').replace('（美元/桶）', '').replace('成交额', '成交'));
  const values = coreItems.map((item) => item.score);
  const cx = width / 2;
  const cy = height / 2;
  const radius = Math.min(width, height) * .32;
  const n = values.length;
  ctx.strokeStyle = '#223047';
  ctx.lineWidth = 1;
  for (let ring = 1; ring <= 4; ring++) {
    ctx.beginPath();
    for (let i = 0; i < n; i++) {
      const a = -Math.PI / 2 + i * Math.PI * 2 / n;
      const r = radius * ring / 4;
      const x = cx + Math.cos(a) * r;
      const y = cy + Math.sin(a) * r;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.stroke();
  }
  ctx.beginPath();
  values.forEach((value, i) => {
    const a = -Math.PI / 2 + i * Math.PI * 2 / n;
    const r = radius * value / 100;
    const x = cx + Math.cos(a) * r;
    const y = cy + Math.sin(a) * r;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.closePath();
  ctx.fillStyle = 'rgba(56, 189, 248, .2)';
  ctx.strokeStyle = '#38bdf8';
  ctx.lineWidth = 2;
  ctx.fill();
  ctx.stroke();
  names.forEach((name, i) => {
    const a = -Math.PI / 2 + i * Math.PI * 2 / n;
    const x = cx + Math.cos(a) * (radius + 18);
    const y = cy + Math.sin(a) * (radius + 18);
    drawText(ctx, name.slice(0, 6), x, y, {
      size: 11,
      align: Math.cos(a) > .2 ? 'left' : Math.cos(a) < -.2 ? 'right' : 'center',
      color: '#94a3b8'
    });
  });
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('\"', '&quot;')
    .replaceAll("'", '&#39;');
}

function drawIndustryBars(items) {
  const sortedItems = sortIndustriesByTierAndScore(items);
  const { ctx, width, height } = setupCanvas('industryBars');
  clear(ctx, width, height);
  const compact = isCompactCanvas(width);
  const pad = compact ? 24 : 34;
  const labelWidth = compact ? 74 : 132;
  const barX = 10 + labelWidth;
  const rowH = (height - pad * 2) / sortedItems.length;
  sortedItems.forEach((item, i) => {
    const y = pad + i * rowH;
    const label = formatIndustryLabel(item.name, compact);
    drawText(ctx, label, 10, y + 14, { size: compact ? 10 : 11, color: '#cbd5e1' });
    const maxW = width - barX - 24;
    const totalScore = industryScore(item);
    ctx.fillStyle = 'rgba(148, 163, 184, .12)';
    ctx.fillRect(barX, y + 5, maxW, 12);
    const grad = ctx.createLinearGradient(barX, 0, barX + maxW, 0);
    if (item.tier === '核心主线') {
      grad.addColorStop(0, '#facc15');
      grad.addColorStop(.62, '#fb923c');
      grad.addColorStop(1, '#ef4444');
    } else {
      grad.addColorStop(0, '#38bdf8');
      grad.addColorStop(1, '#22c55e');
    }
    ctx.fillStyle = grad;
    ctx.fillRect(barX, y + 5, maxW * totalScore / 100, 12);
    drawText(ctx, `${totalScore}`, width - 18, y + 14, { size: compact ? 11 : 12, align: 'right', color: '#f8fafc' });
  });
}

function drawPie(id, data, colors, options = {}) {
  const { ctx, width, height } = setupCanvas(id);
  clear(ctx, width, height);
  const compact = isCompactCanvas(width);
  const total = data.reduce((sum, item) => sum + item.value, 0) || 1;
  const centered = options.centered === true;
  const stackedLegend = options.stackedLegend === true;
  const cx = compact || centered ? width / 2 : width * .34;
  const cy = compact ? height * .29 : (stackedLegend ? height * .32 : (centered ? height * .37 : height / 2));
  const radius = Math.min(width, height) * (compact ? .22 : (stackedLegend ? .22 : (centered ? .28 : .32)));
  let start = -Math.PI / 2;
  data.forEach((item, i) => {
    const end = start + Math.PI * 2 * item.value / total;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.fillStyle = colors[i % colors.length];
    ctx.arc(cx, cy, radius, start, end);
    ctx.closePath();
    ctx.fill();
    const mid = (start + end) / 2;
    const pct = Math.round(item.value / total * 100);
    const labelX = cx + Math.cos(mid) * radius * .62;
    const labelY = cy + Math.sin(mid) * radius * .62 + 4;
    if (pct >= 10) {
      drawText(ctx, `${pct}%`, labelX, labelY, {
        size: 12,
        weight: 800,
        align: 'center',
        color: '#0b1020'
      });
    }
    start = end;
  });
  const legendItems = data.map((item) => {
    const pct = (item.value / total * 100).toFixed(0);
    return { ...item, label: `${item.name} ${item.value} | ${pct}%` };
  });
  const legendFontSize = compact ? 11 : 12;
  const legendFontWeight = stackedLegend ? 700 : 500;
  ctx.font = `${legendFontWeight} ${legendFontSize}px Inter, "PingFang SC", Arial, sans-serif`;
  const legendWidth = stackedLegend
    ? Math.min(
        width - 28,
        Math.max(...legendItems.map((item) => ctx.measureText(item.label).width)) + 30
      )
    : 0;
  legendItems.forEach((item, i) => {
    const legendRows = Math.ceil(legendItems.length / (centered && !compact && !stackedLegend ? 2 : 1));
    const legendTop = compact ? height * .73 : (stackedLegend ? height * .76 : (centered ? height * .68 : 52));
    const row = centered && !compact && !stackedLegend ? i % legendRows : i;
    const col = centered && !compact && !stackedLegend ? Math.floor(i / legendRows) : 0;
    const x = compact
      ? Math.max(18, (width - legendWidth) / 2)
      : (stackedLegend ? (width - legendWidth) / 2 : (centered ? width * (.22 + col * .34) : width * .66));
    const y = legendTop + row * (compact ? 18 : 22);
    ctx.fillStyle = colors[i % colors.length];
    ctx.fillRect(x, y - 10, 10, 10);
    drawText(ctx, item.label, x + 18, y, { size: legendFontSize, color: '#cbd5e1', weight: legendFontWeight });
  });
}

function fundPerformanceValue(fund) {
  return Number.isFinite(fund.day) ? fund.day : fund.week;
}

function sortFundsByPerformance(funds) {
  return [...funds].sort((a, b) => fundPerformanceValue(b) - fundPerformanceValue(a));
}

function drawFundPerformance(funds) {
  const { ctx, width, height } = setupCanvas('fundPerformance');
  clear(ctx, width, height);
  const compact = isCompactCanvas(width);
  const shortTheme = {
    'AI/互联网': 'AI互联',
    '先进制造': '先进制造',
    '航空航天': '航空航天',
    '绿色电力': '绿色电力',
    '成长/动力': '成长动力',
    '通信/设备': '通信设备',
    '消费电子': '消费电子',
    '新能源车/电池': compact ? '新能源' : '新能源车',
    '有色金属': '有色金属',
    '全球科技互联网': '全球科技',
    'A股宽基': 'A股宽基',
    'AI/半导体': 'AI半导体'
  };
  const sorted = sortFundsByPerformance(funds);
  const pad = compact ? 24 : 32;
  const zeroY = height / 2;
  const max = Math.max(...sorted.map((fund) => Math.abs(fundPerformanceValue(fund))), 1);
  ctx.strokeStyle = '#263448';
  ctx.beginPath();
  ctx.moveTo(pad, zeroY);
  ctx.lineTo(width - pad, zeroY);
  ctx.stroke();
  const step = (width - pad * 2) / sorted.length;
  sorted.forEach((fund, i) => {
    const day = fundPerformanceValue(fund);
    const x = pad + i * step + step * .22;
    const barW = step * .56;
    const h = Math.abs(day) / max * (height * .36);
    const y = day >= 0 ? zeroY - h : zeroY;
    ctx.fillStyle = day >= 0 ? '#ef4444' : '#22c55e';
    ctx.fillRect(x, y, barW, h);
    drawText(ctx, shortTheme[fund.theme] || fund.theme, x + barW / 2, height - 28, { size: compact ? 8 : 9, align: 'center', color: '#cbd5e1', weight: 700 });
    drawText(ctx, compact ? fund.code.slice(-4) : fund.code, x + barW / 2, height - 12, { size: compact ? 8 : 10, align: 'center', color: '#94a3b8' });
    drawText(ctx, `${day}%`, x + barW / 2, day >= 0 ? y - 7 : y + h + 15, { size: compact ? 9 : 10, align: 'center', color: day >= 0 ? '#fca5a5' : '#86efac' });
  });
}

function renderHeader(data) {
  const daily = data.daily;
  $('summary').textContent = daily.marketJudgement;
  $('asOf').textContent = daily.asOf;
  $('todaySignal').textContent = daily.signal;
  $('todaySignal').className = `signal-pill ${signalClass[daily.signal] || 'watch'}`;
  $('todayAction').textContent = daily.action;
  $('marketJudgement').textContent = daily.marketJudgement;
  $('positionAdvice').textContent = daily.positionAdvice;
  $('needAction').textContent = daily.needAction;
  $('actionReason').textContent = daily.actionReason;
  $('riskPoint').textContent = daily.riskPoint;
  $('nextReview').textContent = daily.nextReview;
}

function renderRiskMatrix(items) {
  const coreItems = getCoreRiskItems(items);
  const shortNames = {
    '10年期美债收益率': '美债收益率',
    '国际油价（美元/桶）': '国际油价',
    '国际油价': '国际油价',
    '美元指数': 'DXY',
    '实际利率': '实际利率',
    '信用利差': '信用利差',
    'VIX': 'VIX',
    'A股成交额': 'A股成交',
    '港股成交额': '港股成交',
    '估值分位': '估值分位'
  };
  $('riskSummary').textContent = `绿灯 ${coreItems.filter((item) => item.signal.includes('绿')).length} / 黄灯 ${coreItems.filter((item) => item.signal.includes('黄')).length}`;
  $('riskMatrix').innerHTML = coreItems.map((item) => `
    <article class="risk-item">
      <header>
        <span title="${item.name}">${shortNames[item.name] || item.name}</span>
        <b class="badge ${signalClass[item.signal] || 'watch'}">${item.signal.replace('正常', '').replace('预警', '').replace('危险', '')}</b>
      </header>
      <strong>${item.value}</strong>
      <small>正常：${item.normal}</small>
    </article>
  `).join('');
}

function renderIndustryCards(items) {
  const sortedItems = sortIndustriesByTierAndScore(items);
  $('industryGrid').innerHTML = sortedItems.map((item, index) => `
    <article class="industry-card ${item.tier === '核心主线' ? 'core-card' : 'candidate-card'} ${index === activeIndustry ? 'active' : ''}" data-index="${index}">
      <header>
        <span class="tier-pill ${item.tier === '核心主线' ? 'core' : 'candidate'}">${item.tier}</span>
        <b class="badge ${signalClass[item.operation] || 'watch'}">${item.operation}</b>
      </header>
      <h3>${item.name}</h3>
      <p>${item.news}</p>
      <div class="metric-row">
        <label>景气度 <span class="bar-track"><i style="width:${item.prosperity}%"></i></span></label>
        <label>资金热度 <span class="bar-track"><i style="width:${item.heat}%"></i></span></label>
        <label>风险压力 <span class="bar-track"><i class="risk" style="width:${item.risk}%"></i></span></label>
      </div>
    </article>
  `).join('');
  document.querySelectorAll('.industry-card').forEach((card) => {
    card.addEventListener('click', () => {
      activeIndustry = Number(card.dataset.index);
      renderIndustryCards(sortedItems);
      renderIndustryDetail(sortedItems[activeIndustry]);
    });
  });
}

function renderIndustryDetail(item) {
  $('detailTitle').textContent = item.name;
  $('detailBadge').textContent = item.operation;
  $('detailBadge').className = signalClass[item.operation] || 'watch';
  $('industryDetail').innerHTML = `
    <h3>${item.name}</h3>
    <p><span class="tier-pill ${item.tier === '核心主线' ? 'core' : 'candidate'}">${item.tier}</span></p>
    <p>${item.reason}</p>
    <dl>
      <div><dt>估值约束</dt><dd>${item.valuation}</dd></div>
      <div><dt>重点跟踪信号</dt><dd>${item.nextSignal}</dd></div>
      <div><dt>操作语言</dt><dd><span class="badge ${signalClass[item.operation] || 'watch'}">${item.operation}</span></dd></div>
    </dl>
  `;
}

function renderExperts(experts) {
  const displayStanceOf = (expert) => {
    if (expert.stance) return expert.stance;
    return '待核验';
  };
  const counts = experts.reduce((acc, item) => {
    const stance = displayStanceOf(item);
    acc[stance] = (acc[stance] || 0) + 1;
    return acc;
  }, {});
  const stanceOrder = ['无新增可靠观点', '跟踪验证', '优质观察', '风险校验', '宏观分散', '节奏参考', '待核验'];
  const stanceColors = ['#64748b', '#facc15', '#22c55e', '#ef4444', '#38bdf8', '#fb923c', '#a78bfa'];
  const stanceData = stanceOrder
    .filter((name) => counts[name])
    .map((name) => ({ name, value: counts[name] }));
  drawPie('expertPie', stanceData, stanceColors, { centered: true, stackedLegend: true });
  $('expertCards').innerHTML = experts.map((expert) => `
    <article class="expert-card">
      <header>
        <span>${expert.style}</span>
        <b class="badge ${signalClass[displayStanceOf(expert)] || 'watch'}">${displayStanceOf(expert)}</b>
      </header>
      <h3>${expert.name}</h3>
      <p>${expert.view}</p>
      <footer>${expert.assets} | 证据 ${expert.strength}</footer>
    </article>
  `).join('');
}

function renderFunds(funds) {
  const validFunds = funds.filter((fund) => Number.isFinite(fund.day) || Number.isFinite(fund.week));
  const sortedFunds = sortFundsByPerformance(validFunds);
  const counts = validFunds.reduce((acc, fund) => {
    acc[fund.risk] = (acc[fund.risk] || 0) + 1;
    return acc;
  }, {});
  const highRisk = validFunds.filter((fund) => fund.risk.includes('高')).length;
  const avgDay = validFunds.reduce((sum, fund) => sum + fundPerformanceValue(fund), 0) / Math.max(validFunds.length, 1);
  $('fundSummary').textContent = `${validFunds.length}只基金 | 高风险${highRisk}只 | 平均日涨跌 ${avgDay.toFixed(2)}%`;
  drawPie('fundRiskPie', Object.entries(counts).map(([name, value]) => ({ name, value })), ['#22c55e', '#facc15', '#fb923c', '#ef4444'], { centered: true, stackedLegend: true });
  drawFundPerformance(sortedFunds);
  $('fundActions').innerHTML = sortedFunds
    .map((fund) => {
      const day = fundPerformanceValue(fund);
      return `
        <article class="fund-action">
          <header>
            <span>${fund.code}</span>
            <b class="badge ${signalClass[fund.decision] || 'watch'}">${fund.decision}</b>
          </header>
          <h3>${fund.name}</h3>
          <p>${fund.theme} | 日涨跌 <span class="${day >= 0 ? 'cn-up' : 'cn-down'}">${day}%</span> | ${fund.reason}</p>
        </article>
      `;
    }).join('');
}


function renderNews(news) {
  if (!Array.isArray(news) || news.length === 0) {
    $('newsSummary').textContent = '暂无新闻数据';
    $('newsGrid').innerHTML = '<article class="news-card"><h3>暂无新闻</h3><p>等待下一次自动同步。</p></article>';
    return;
  }
  const included = news.filter((item) => item.included === '是').length;
  const highImpact = news.filter((item) => item.impact.includes('高')).length;
  $('newsSummary').textContent = `${news[0].date} | ${news.length}条新闻 | 高影响${highImpact}条 | 入简报${included}条`;
  $('newsGrid').innerHTML = news.map((item, index) => `
    <article class="news-card ${item.included === '是' ? 'included' : ''}">
      <header>
        <span>${index + 1}. ${escapeHtml(item.category)}</span>
        <b class="badge ${signalClass[item.direction] || signalClass[item.impact] || 'watch'}">${escapeHtml(item.direction)} / ${escapeHtml(item.impact)}</b>
      </header>
      <h3>${escapeHtml(item.title)}</h3>
      <p>${escapeHtml(item.meaning || item.content)}</p>
      <footer>
        <span>${escapeHtml(item.horizon)}</span>
        <span>${escapeHtml(item.action)}</span>
        <span>${escapeHtml(item.source)}</span>
      </footer>
    </article>
  `).join('');
}

function renderAll() {
  renderHeader(dashboardData);
  renderRiskMatrix(dashboardData.riskDashboard);
  const sortedIndustries = sortIndustriesByTierAndScore(dashboardData.industryWatch);
  renderIndustryCards(sortedIndustries);
  renderIndustryDetail(sortedIndustries[activeIndustry]);
  renderExperts(dashboardData.expertViews);
  renderFunds(dashboardData.fundHoldings);
  renderNews(dashboardData.financeNews);
  drawGauge(dashboardData.riskDashboard);
  drawRadar(dashboardData.riskDashboard);
  drawIndustryBars(dashboardData.industryWatch);
}

async function boot() {
  const response = await fetch(`./data/market-data.json?t=${Date.now()}`, { cache: 'no-store' });
  if (!response.ok) throw new Error(`数据文件读取失败：${response.status}`);
  dashboardData = await response.json();
  renderAll();
}

window.addEventListener('resize', () => {
  if (dashboardData) renderAll();
});

boot().catch((error) => {
  $('summary').textContent = `加载失败：${error.message}`;
});
