/* Stock Analysis — Frontend JS */

function fmt(val, prefix = '$', suffix = '', decimals = 1) {
    if (val == null || isNaN(val)) return 'N/A';
    const abs = Math.abs(val);
    let str;
    if (abs >= 1e12) str = `${prefix}${(val / 1e12).toFixed(decimals)}T${suffix}`;
    else if (abs >= 1e9) str = `${prefix}${(val / 1e9).toFixed(decimals)}B${suffix}`;
    else if (abs >= 1e6) str = `${prefix}${(val / 1e6).toFixed(decimals)}M${suffix}`;
    else str = `${prefix}${val.toLocaleString(undefined, {maximumFractionDigits: 2})}${suffix}`;
    return str;
}

function pct(val) {
    if (val == null || isNaN(val)) return 'N/A';
    const v = parseFloat(val);
    const sign = v >= 0 ? '+' : '';
    return `${sign}${(v * 100).toFixed(1)}%`;
}

function fmtNum(val, decimals = 2) {
    if (val == null || isNaN(val)) return 'N/A';
    return parseFloat(val).toFixed(decimals);
}

function scoreColor(score) {
    if (score >= 70) return 'var(--green)';
    if (score >= 50) return 'var(--yellow)';
    return 'var(--red)';
}

function ratingColors(rating) {
    const r = (rating || '').toLowerCase();
    if (r.includes('strong buy')) return { bg: 'rgba(16,185,129,.15)', color: 'var(--green)', border: 'var(--green)' };
    if (r.includes('buy')) return { bg: 'rgba(59,130,246,.15)', color: 'var(--accent)', border: 'var(--accent)' };
    if (r.includes('hold')) return { bg: 'rgba(245,158,11,.1)', color: 'var(--yellow)', border: 'var(--yellow)' };
    return { bg: 'rgba(239,68,68,.1)', color: 'var(--red)', border: 'var(--red)' };
}

function initAnalysis(symbol) {
    const cached = sessionStorage.getItem('analysisData_' + symbol);
    if (cached) {
        try {
            const data = JSON.parse(cached);
            renderAll(data);
            return;
        } catch (e) {}
    }

    fetch(`/api/analyze/${symbol}`)
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                document.getElementById('initialLoader').innerHTML =
                    `<div style="color:var(--red);text-align:center;padding:40px">
                        <h2>Error</h2><p>${data.error}</p>
                        <a href="/" class="btn-primary">Go Back</a>
                    </div>`;
                return;
            }
            sessionStorage.setItem('analysisData_' + symbol, JSON.stringify(data));
            renderAll(data);
        })
        .catch(err => {
            document.getElementById('initialLoader').innerHTML =
                `<div style="color:var(--red);text-align:center;padding:40px">
                    <h2>Network Error</h2><p>${err.message}</p>
                    <a href="/" class="btn-primary">Go Back</a>
                </div>`;
        });
}

function renderAll(data) {
    document.getElementById('initialLoader').classList.add('hidden');
    document.getElementById('analysisContent').classList.remove('hidden');

    renderHeader(data.overview, data.financials);
    renderScores(data.scores);
    setupTabs();

    renderPriceChart(data.prices, data.overview.symbol);
    renderKeyMetrics(data.overview, data.valuation, data.financials);
    renderAnalyst(data.analyst_ratings);
    renderEarnings(data.earnings_history);
    renderAbout(data.overview);

    renderRevenueTrend(data.revenue_trend, data.ni_trend);
    renderIncome(data.financials);
    renderMargins(data.financials);
    renderBalance(data.financials);

    renderMultiples(data.valuation);
    renderDCF(data.dcf_result, data.overview.price);
    renderSensitivity(data.sensitivity, data.overview.price);
    renderFairValue(data.fair_value_band, data.graham_number, data.overview.price);
    renderDCFChart(data.dcf_result);

    renderSEC(data.sec_filings);
    renderNews(data.news);
    renderAI(data.ai_analysis);

    setupPeriodButtons(data.overview.symbol);
}

/* ─── Header ──────────────────────────────────────────────── */
function renderHeader(ov, fin) {
    const change = ov.change_pct || 0;
    const updown = change >= 0 ? 'up' : 'down';
    const arrow = change >= 0 ? '▲' : '▼';
    document.getElementById('stockHeader').innerHTML = `
        <div class="header-left">
            <div class="header-symbol">${ov.symbol}</div>
            <div class="header-name">${ov.name}</div>
            <div class="header-meta">${ov.sector || ''} · ${ov.exchange || ''} · ${ov.country || ''}</div>
        </div>
        <div class="header-right">
            <div class="header-price">$${fmtNum(ov.price)}</div>
            <div class="header-change ${updown}">${arrow} ${Math.abs(change).toFixed(2)}% today</div>
            <div class="header-volume">Vol: ${ov.volume ? ov.volume.toLocaleString() : 'N/A'} · Mkt Cap: ${fmt(ov.market_cap)}</div>
        </div>
    `;
}

/* ─── Scores ──────────────────────────────────────────────── */
function renderScores(scores) {
    const total = scores.total || 0;
    const rating = scores.rating || '';
    const c = scoreColor(total);
    const rc = ratingColors(rating);

    const pillars = [
        { name: 'Growth', key: 'growth', max: 20 },
        { name: 'Profit', key: 'profitability', max: 20 },
        { name: 'Value', key: 'value', max: 20 },
        { name: 'Health', key: 'financial_health', max: 20 },
        { name: 'Momentum', key: 'momentum', max: 20 },
    ];

    const pillarsHtml = pillars.map(p => {
        const val = scores[p.key] || 0;
        const width = (val / p.max) * 100;
        return `<div class="pillar">
            <div class="pillar-name">${p.name}</div>
            <div class="pillar-bar-wrap"><div class="pillar-bar" style="width:${width}%;background:${scoreColor(val / p.max * 100)}"></div></div>
            <div class="pillar-val">${val}/20</div>
        </div>`;
    }).join('');

    document.getElementById('scoreSection').innerHTML = `
        <div class="score-total-wrap">
            <div class="score-circle" style="color:${c};border-color:${c}">${total}</div>
            <div class="score-label">Score</div>
        </div>
        <div class="score-pillars">${pillarsHtml}</div>
        <div class="score-rating">
            <div class="rating-badge" style="background:${rc.bg};color:${rc.color};border:2px solid ${rc.border}">${rating}</div>
        </div>
    `;
}

/* ─── Tabs ────────────────────────────────────────────────── */
function setupTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
        });
    });
}

/* ─── Price Chart ─────────────────────────────────────────── */
function renderPriceChart(prices, symbol) {
    if (!prices || !prices.length) {
        document.getElementById('priceChart').innerHTML = '<p class="text-muted">No price data available.</p>';
        return;
    }
    drawPriceChart(prices, symbol);
}

function drawPriceChart(prices, symbol) {
    const dates = prices.map(p => p.date);
    const closes = prices.map(p => p.close);
    const opens = prices.map(p => p.open);
    const highs = prices.map(p => p.high);
    const lows = prices.map(p => p.low);
    const volumes = prices.map(p => p.volume);

    const isUp = closes[closes.length - 1] >= closes[0];
    const lineColor = isUp ? '#10b981' : '#ef4444';
    const fillColor = isUp ? 'rgba(16,185,129,.1)' : 'rgba(239,68,68,.1)';

    const trace = {
        x: dates, y: closes,
        type: 'scatter', mode: 'lines',
        name: symbol,
        line: { color: lineColor, width: 2 },
        fill: 'tozeroy', fillcolor: fillColor,
    };

    const layout = {
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        margin: { t: 10, r: 10, b: 40, l: 60 },
        xaxis: { color: '#64748b', gridcolor: '#2a2f3e', showgrid: false },
        yaxis: { color: '#64748b', gridcolor: '#2a2f3e', tickprefix: '$' },
        font: { color: '#94a3b8', size: 12 },
        hovermode: 'x unified',
        showlegend: false,
    };

    Plotly.newPlot('priceChart', [trace], layout, { responsive: true, displayModeBar: false });
}

function setupPeriodButtons(symbol) {
    document.querySelectorAll('.period-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const period = btn.dataset.period;
            fetch(`/api/price/${symbol}?period=${period}`)
                .then(r => r.json())
                .then(prices => { drawPriceChart(prices, symbol); });
        });
    });
    // Set 1y as default active
    document.querySelector('[data-period="1y"]')?.classList.add('active');
}

/* ─── Key Metrics ─────────────────────────────────────────── */
function renderKeyMetrics(ov, val, fin) {
    const rows = [
        ['52-Week High', `$${fmtNum(ov['52w_high'])}`],
        ['52-Week Low', `$${fmtNum(ov['52w_low'])}`],
        ['Beta', fmtNum(ov.beta)],
        ['Market Cap', fmt(ov.market_cap)],
        ['Enterprise Value', fmt(ov.enterprise_value)],
        ['P/E (Trailing)', val.pe_trailing ? `${fmtNum(val.pe_trailing)}x` : 'N/A'],
        ['P/E (Forward)', val.pe_forward ? `${fmtNum(val.pe_forward)}x` : 'N/A'],
        ['PEG Ratio', fmtNum(val.peg_ratio)],
        ['Price/Book', val.price_to_book ? `${fmtNum(val.price_to_book)}x` : 'N/A'],
        ['EV/EBITDA', val.ev_to_ebitda ? `${fmtNum(val.ev_to_ebitda)}x` : 'N/A'],
        ['Div Yield', fin.dividend_yield ? pct(fin.dividend_yield) : 'N/A'],
        ['EPS (FWD)', fin.eps_forward ? `$${fmtNum(fin.eps_forward)}` : 'N/A'],
        ['Employees', ov.employees ? ov.employees.toLocaleString() : 'N/A'],
    ];

    document.getElementById('keyMetrics').innerHTML = `
        <table class="metric-table">
            ${rows.map(([l, v]) => `<tr><td>${l}</td><td>${v}</td></tr>`).join('')}
        </table>`;
}

/* ─── Analyst ─────────────────────────────────────────────── */
function renderAnalyst(ar) {
    if (!ar) { document.getElementById('analystSection').innerHTML = '<p class="text-muted">No analyst data.</p>'; return; }

    const rec = (ar.recommendation || 'N/A').toUpperCase();
    const rc = ratingColors(ar.recommendation);

    document.getElementById('analystSection').innerHTML = `
        <div class="consensus-badge" style="background:${rc.bg};color:${rc.color};border:2px solid ${rc.border}">
            ${rec}
        </div>
        <div class="text-muted" style="font-size:.85rem">${ar.num_analysts || 'N/A'} analyst${ar.num_analysts !== 1 ? 's' : ''}</div>
        <div class="target-grid">
            <div class="target-cell"><div class="target-label">Low</div><div class="target-value">$${fmtNum(ar.target_low)}</div></div>
            <div class="target-cell"><div class="target-label">Mean</div><div class="target-value">$${fmtNum(ar.target_mean)}</div></div>
            <div class="target-cell"><div class="target-label">High</div><div class="target-value">$${fmtNum(ar.target_high)}</div></div>
        </div>
        ${ar.recent_upgrades_downgrades && ar.recent_upgrades_downgrades.length ? `
            <div style="margin-top:16px">
                <div class="card-title">Recent Analyst Actions</div>
                ${ar.recent_upgrades_downgrades.slice(0,4).map(u => `
                    <div style="padding:6px 0;border-bottom:1px solid var(--border);font-size:.85rem">
                        <strong>${u.firm}</strong> — ${u.action} → <span style="color:var(--accent)">${u.to_grade}</span>
                    </div>`).join('')}
            </div>` : ''}
    `;
}

/* ─── Earnings ────────────────────────────────────────────── */
function renderEarnings(earnings) {
    if (!earnings || !earnings.length) {
        document.getElementById('earningsSection').innerHTML = '<p class="text-muted">No earnings data available.</p>';
        return;
    }
    const rows = earnings.map(e => {
        const surprise = parseFloat(e.surprise_pct);
        const cls = isNaN(surprise) ? '' : surprise >= 0 ? 'beat' : 'miss';
        return `<tr>
            <td>${e.quarter || 'N/A'}</td>
            <td>$${fmtNum(e.eps_estimate)}</td>
            <td>$${fmtNum(e.eps_actual)}</td>
            <td class="${cls}">${isNaN(surprise) ? 'N/A' : `${surprise >= 0 ? '+' : ''}${surprise.toFixed(1)}%`}</td>
        </tr>`;
    }).join('');
    document.getElementById('earningsSection').innerHTML = `
        <table class="earnings-table">
            <thead><tr><th>Quarter</th><th>Est.</th><th>Actual</th><th>Surprise</th></tr></thead>
            <tbody>${rows}</tbody>
        </table>`;
}

/* ─── About ───────────────────────────────────────────────── */
function renderAbout(ov) {
    document.getElementById('aboutSection').innerHTML = `
        <p style="color:var(--text2);line-height:1.7">${ov.description || 'No company description available.'}</p>
        ${ov.website ? `<p style="margin-top:8px"><a href="${ov.website}" target="_blank" rel="noopener" style="color:var(--accent)">${ov.website}</a></p>` : ''}
    `;
}

/* ─── Revenue / NI Trend (EDGAR) ──────────────────────────── */
function renderRevenueTrend(revData, niData) {
    if (revData && revData.length) {
        const sorted = [...revData].sort((a, b) => a.year - b.year);
        const trace = {
            x: sorted.map(r => r.year),
            y: sorted.map(r => r.value / 1e9),
            type: 'bar',
            marker: { color: 'rgba(59,130,246,.7)' },
            name: 'Revenue ($B)',
        };
        Plotly.newPlot('revenueChart', [trace], chartLayout('Revenue ($B)'), { responsive: true, displayModeBar: false });
    } else {
        document.getElementById('revenueChart').innerHTML = '<p class="text-muted">No EDGAR revenue data.</p>';
    }

    if (niData && niData.length) {
        const sorted = [...niData].sort((a, b) => a.year - b.year);
        const colors = sorted.map(r => r.value >= 0 ? 'rgba(16,185,129,.7)' : 'rgba(239,68,68,.7)');
        const trace = {
            x: sorted.map(r => r.year),
            y: sorted.map(r => r.value / 1e9),
            type: 'bar',
            marker: { color: colors },
            name: 'Net Income ($B)',
        };
        Plotly.newPlot('niChart', [trace], chartLayout('Net Income ($B)'), { responsive: true, displayModeBar: false });
    } else {
        document.getElementById('niChart').innerHTML = '<p class="text-muted">No EDGAR net income data.</p>';
    }
}

function chartLayout(ytitle) {
    return {
        paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
        margin: { t: 10, r: 10, b: 40, l: 60 },
        xaxis: { color: '#64748b', gridcolor: '#2a2f3e', type: 'category' },
        yaxis: { color: '#64748b', gridcolor: '#2a2f3e', title: ytitle },
        font: { color: '#94a3b8', size: 12 },
        showlegend: false,
    };
}

/* ─── Income ──────────────────────────────────────────────── */
function renderIncome(fin) {
    const rows = [
        ['Revenue (TTM)', fmt(fin.revenue_ttm)],
        ['Gross Profit', fmt(fin.gross_profit)],
        ['EBITDA', fmt(fin.ebitda)],
        ['Net Income', fmt(fin.net_income)],
        ['EPS (Trailing)', fin.eps_trailing ? `$${fmtNum(fin.eps_trailing)}` : 'N/A'],
        ['EPS (Forward)', fin.eps_forward ? `$${fmtNum(fin.eps_forward)}` : 'N/A'],
        ['Revenue Growth', pct(fin.revenue_growth_yoy)],
        ['Earnings Growth', pct(fin.earnings_growth_yoy)],
    ];
    document.getElementById('incomeSection').innerHTML = `<table class="metric-table">${rows.map(([l, v]) => `<tr><td>${l}</td><td>${v}</td></tr>`).join('')}</table>`;
}

/* ─── Margins ─────────────────────────────────────────────── */
function renderMargins(fin) {
    const margins = [
        ['Gross Margin', fin.gross_margin],
        ['Operating Margin', fin.operating_margin],
        ['Net Margin', fin.profit_margin],
        ['FCF Margin', fin.free_cash_flow && fin.revenue_ttm ? fin.free_cash_flow / fin.revenue_ttm : null],
        ['ROE', fin.return_on_equity],
        ['ROA', fin.return_on_assets],
    ];
    const bars = margins.map(([name, val]) => {
        if (val == null) return `<div style="margin-bottom:12px"><div style="display:flex;justify-content:space-between;font-size:.88rem;margin-bottom:4px"><span style="color:var(--text2)">${name}</span><span>N/A</span></div></div>`;
        const pctVal = val * 100;
        const color = pctVal >= 20 ? 'var(--green)' : pctVal >= 5 ? 'var(--yellow)' : 'var(--red)';
        const width = Math.max(0, Math.min(100, pctVal));
        return `
            <div style="margin-bottom:14px">
                <div style="display:flex;justify-content:space-between;font-size:.88rem;margin-bottom:5px">
                    <span style="color:var(--text2)">${name}</span>
                    <span style="color:${color};font-weight:700">${(pctVal).toFixed(1)}%</span>
                </div>
                <div style="background:var(--bg3);border-radius:99px;height:6px;overflow:hidden">
                    <div style="width:${width}%;height:100%;background:${color};border-radius:99px"></div>
                </div>
            </div>`;
    }).join('');
    document.getElementById('marginsSection').innerHTML = bars;
}

/* ─── Balance Sheet ───────────────────────────────────────── */
function renderBalance(fin) {
    const rows = [
        ['Total Cash', fmt(fin.total_cash)],
        ['Total Debt', fmt(fin.total_debt)],
        ['Net Cash Position', fmt(fin.net_cash)],
        ['FCF', fmt(fin.free_cash_flow)],
        ['Operating Cash Flow', fmt(fin.operating_cash_flow)],
        ['Current Ratio', fmtNum(fin.current_ratio)],
        ['Quick Ratio', fmtNum(fin.quick_ratio)],
        ['Debt/Equity', fmtNum(fin.debt_to_equity)],
        ['Dividend Yield', fin.dividend_yield ? pct(fin.dividend_yield) : 'N/A'],
        ['Payout Ratio', fin.payout_ratio ? pct(fin.payout_ratio) : 'N/A'],
    ];
    document.getElementById('balanceSection').innerHTML = `<table class="metric-table">${rows.map(([l, v]) => `<tr><td>${l}</td><td>${v}</td></tr>`).join('')}</table>`;
}

/* ─── Multiples ───────────────────────────────────────────── */
function renderMultiples(val) {
    const rows = [
        ['P/E (Trailing)', val.pe_trailing ? `${fmtNum(val.pe_trailing)}x` : 'N/A'],
        ['P/E (Forward)', val.pe_forward ? `${fmtNum(val.pe_forward)}x` : 'N/A'],
        ['PEG Ratio', fmtNum(val.peg_ratio)],
        ['Price/Book', val.price_to_book ? `${fmtNum(val.price_to_book)}x` : 'N/A'],
        ['Price/Sales', val.price_to_sales ? `${fmtNum(val.price_to_sales)}x` : 'N/A'],
        ['EV/Revenue', val.ev_to_revenue ? `${fmtNum(val.ev_to_revenue)}x` : 'N/A'],
        ['EV/EBITDA', val.ev_to_ebitda ? `${fmtNum(val.ev_to_ebitda)}x` : 'N/A'],
        ['Earnings Yield', val.earnings_yield ? `${fmtNum(val.earnings_yield)}%` : 'N/A'],
        ['Book Value/Share', val.book_value_per_share ? `$${fmtNum(val.book_value_per_share)}` : 'N/A'],
        ['Revenue/Share', val.revenue_per_share ? `$${fmtNum(val.revenue_per_share)}` : 'N/A'],
    ];
    document.getElementById('multiplesSection').innerHTML = `<table class="metric-table">${rows.map(([l, v]) => `<tr><td>${l}</td><td>${v}</td></tr>`).join('')}</table>`;
}

/* ─── DCF ─────────────────────────────────────────────────── */
function renderDCF(dcf, currentPrice) {
    if (!dcf || dcf.error) {
        document.getElementById('dcfSection').innerHTML = `<p class="text-muted">${dcf?.error || 'DCF data unavailable.'}</p>`;
        return;
    }
    const iv = dcf.intrinsic_value_per_share;
    let mosHtml = '';
    if (iv && currentPrice) {
        const mos = ((currentPrice / iv) - 1) * 100;
        const cls = mos <= 0 ? 'mos-positive' : 'mos-negative';
        const label = mos <= 0 ? `${Math.abs(mos).toFixed(1)}% Undervalued — Margin of Safety` : `${mos.toFixed(1)}% Overvalued vs DCF`;
        mosHtml = `<div class="margin-of-safety ${cls}" style="margin-top:16px">${label}</div>`;
    }
    const rows = [
        ['Base FCF', fmt(dcf.base_fcf, '$', '', 2)],
        ['Phase 1 Growth', `${(dcf.assumptions.phase1_growth * 100).toFixed(1)}%`],
        ['Phase 2 Growth', `${(dcf.assumptions.phase2_growth * 100).toFixed(1)}%`],
        ['Terminal Growth', `${(dcf.assumptions.terminal_growth_rate * 100).toFixed(1)}%`],
        ['Discount Rate', `${(dcf.assumptions.discount_rate * 100).toFixed(1)}%`],
        ['PV of Cash Flows', fmt(dcf.pv_cash_flows?.reduce((a, b) => a + b, 0))],
        ['PV Terminal Value', fmt(dcf.pv_terminal_value)],
        ['Total PV', fmt(dcf.total_pv_operations)],
        ['Intrinsic Value/Share', iv ? `$${fmtNum(iv)}` : 'N/A'],
        ['Current Price', currentPrice ? `$${fmtNum(currentPrice)}` : 'N/A'],
    ];
    document.getElementById('dcfSection').innerHTML = `
        ${rows.map(([l, v]) => `<div class="dcf-metric"><span class="dcf-label">${l}</span><span class="dcf-value">${v}</span></div>`).join('')}
        ${mosHtml}`;
}

/* ─── Sensitivity Matrix ──────────────────────────────────── */
function renderSensitivity(sens, currentPrice) {
    if (!sens) {
        document.getElementById('sensitivitySection').innerHTML = '<p class="text-muted">Insufficient data for sensitivity analysis.</p>';
        return;
    }
    const { growth_rates, discount_rates, matrix } = sens;
    let html = `<table class="sensitivity-table"><thead><tr>
        <th>Growth \\ Discount</th>
        ${discount_rates.map(d => `<th>${d}</th>`).join('')}
    </tr></thead><tbody>`;

    growth_rates.forEach(g => {
        html += `<tr><th>${g}</th>`;
        discount_rates.forEach(d => {
            const val = matrix[g]?.[d];
            let cls = 'cell-neutral';
            if (val && currentPrice) {
                const diff = val - currentPrice;
                cls = diff > currentPrice * 0.1 ? 'cell-green' : diff < -currentPrice * 0.1 ? 'cell-red' : 'cell-neutral';
            }
            html += `<td class="${cls}">${val ? '$' + fmtNum(val) : 'N/A'}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody></table>';
    html += `<p style="font-size:.8rem;color:var(--text3);margin-top:10px">Green = >10% upside vs current price. Red = >10% downside. Current price: $${fmtNum(currentPrice)}</p>`;
    document.getElementById('sensitivitySection').innerHTML = html;
}

/* ─── Fair Value ──────────────────────────────────────────── */
function renderFairValue(fvb, graham, price) {
    let html = '';
    if (fvb) {
        html += `
            <div class="card-title">P/E-Based Fair Value Band (Forward EPS)</div>
            <div class="fair-value-grid">
                <div class="fv-cell fv-bear"><div class="fv-label">Bear (15x)</div><div class="fv-value text-red">$${fmtNum(fvb.bear)}</div></div>
                <div class="fv-cell fv-base"><div class="fv-label">Base (20x)</div><div class="fv-value text-yellow">$${fmtNum(fvb.base)}</div></div>
                <div class="fv-cell fv-bull"><div class="fv-label">Bull (25x)</div><div class="fv-value text-green">$${fmtNum(fvb.bull)}</div></div>
            </div>`;
    }
    if (graham) {
        html += `<div style="margin-top:16px;padding:14px;background:var(--bg3);border-radius:8px">
            <div class="card-title">Graham Number</div>
            <div style="font-size:1.4rem;font-weight:800;color:${graham > (price || 0) ? 'var(--green)' : 'var(--red)'}">$${fmtNum(graham)}</div>
            <div style="font-size:.82rem;color:var(--text3);margin-top:4px">sqrt(22.5 × EPS × Book Value) — Benjamin Graham's intrinsic value</div>
        </div>`;
    }
    if (!html) html = '<p class="text-muted">Insufficient EPS/book value data.</p>';
    document.getElementById('fairValueSection').innerHTML = html;
}

/* ─── DCF Chart ───────────────────────────────────────────── */
function renderDCFChart(dcf) {
    if (!dcf || dcf.error || !dcf.projected_cash_flows) {
        document.getElementById('dcfChartSection').innerHTML = '<p class="text-muted">No DCF projection data.</p>';
        return;
    }
    const years = dcf.projected_cash_flows.map((_, i) => `Year ${i + 1}`);
    const fcf = dcf.projected_cash_flows.map(v => v / 1e9);
    const pv = dcf.pv_cash_flows.map(v => v / 1e9);

    Plotly.newPlot('dcfChartSection', [
        { x: years, y: fcf, type: 'bar', name: 'Projected FCF ($B)', marker: { color: 'rgba(59,130,246,.6)' } },
        { x: years, y: pv, type: 'scatter', mode: 'lines+markers', name: 'PV FCF ($B)', line: { color: '#10b981', width: 2 } },
    ], chartLayout('$B'), { responsive: true, displayModeBar: false });
}

/* ─── SEC Filings ─────────────────────────────────────────── */
function renderSEC(filings) {
    if (!filings || !filings.length) {
        document.getElementById('secSection').innerHTML = '<p class="text-muted">No SEC filing data available. Company may not be publicly listed or EDGAR lookup failed.</p>';
        return;
    }
    const items = filings.map(f => {
        const badgeClass = f.form_type === '10-K' ? 'badge-10k' : f.form_type.startsWith('10-Q') ? 'badge-10q' : f.form_type === '8-K' ? 'badge-8k' : 'badge-other';
        return `
            <div class="filing-item">
                <span class="filing-badge ${badgeClass}">${f.form_type}</span>
                <span class="filing-date">${f.filing_date}</span>
                <span class="filing-link"><a href="${f.document_url}" target="_blank" rel="noopener">View Filing ↗</a></span>
            </div>`;
    }).join('');
    document.getElementById('secSection').innerHTML = `<div class="filing-list">${items}</div>`;
}

/* ─── News ────────────────────────────────────────────────── */
function renderNews(articles) {
    if (!articles || !articles.length) {
        document.getElementById('newsSection').innerHTML = '<p class="text-muted">No recent news found.</p>';
        return;
    }
    const items = articles.map(a => `
        <div class="news-item">
            <div class="news-title"><a href="${a.url}" target="_blank" rel="noopener">${a.title}</a></div>
            <div class="news-meta">
                <span class="news-source">${a.source}</span>
                <span>${a.published}</span>
            </div>
            ${a.summary ? `<div class="news-summary">${a.summary.slice(0, 200)}${a.summary.length > 200 ? '...' : ''}</div>` : ''}
        </div>`).join('');
    document.getElementById('newsSection').innerHTML = `<div class="news-list">${items}</div>`;
}

/* ─── AI Analysis ─────────────────────────────────────────── */
function renderAI(aiResult) {
    const el = document.getElementById('aiAnalysisSection');
    if (!aiResult) {
        el.innerHTML = '<div class="ai-error">AI analysis data not available.</div>';
        return;
    }
    if (aiResult.error) {
        el.innerHTML = `<div class="ai-error">
            <strong>AI Analysis Unavailable</strong><br>${aiResult.error}
            <br><br><small>Set ANTHROPIC_API_KEY in your .env file to enable this feature.</small>
        </div>`;
        return;
    }
    if (aiResult.analysis) {
        const html = marked.parse(aiResult.analysis);
        el.innerHTML = `
            <div class="ai-content">${html}</div>
            <div class="ai-meta">
                Generated by ${aiResult.model} ·
                ${aiResult.input_tokens?.toLocaleString()} input tokens ·
                ${aiResult.output_tokens?.toLocaleString()} output tokens
            </div>`;
    }
}
