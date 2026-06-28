"""Generate HTML dashboard with embedded JSON data."""
import json

HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Drone Racing Leaderboard</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;800;900&family=Inter:wght@300;400;500;600;700&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');

  :root {
    --bg-primary: #0a0a0f;
    --bg-secondary: #111118;
    --bg-card: #16161f;
    --bg-card-hover: #1c1c28;
    --border: #252535;
    --text-primary: #e8e8f0;
    --text-secondary: #9090a8;
    --text-dim: #585870;
    --neon-cyan: #00f0ff;
    --neon-green: #39ff14;
    --neon-orange: #ff6b35;
    --neon-pink: #ff2d95;
    --neon-purple: #b44dff;
    --neon-yellow: #ffe600;
    --neon-blue: #4488ff;
    --gold: #ffd700;
    --silver: #c0c0c0;
    --bronze: #cd7f32;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--bg-primary);
    color: var(--text-primary);
    font-family: 'Inter', system-ui, sans-serif;
    min-height: 100vh;
    overflow-x: hidden;
  }

  /* Background animated grid */
  body::before {
    content: '';
    position: fixed;
    inset: 0;
    opacity: 0.04;
    background-image:
      linear-gradient(rgba(0,240,255,0.3) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,240,255,0.3) 1px, transparent 1px);
    background-size: 60px 60px;
    pointer-events: none;
    z-index: 0;
  }

  /* Scanline effect */
  body::after {
    content: '';
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0,0,0,0.03) 2px,
      rgba(0,0,0,0.03) 4px
    );
    pointer-events: none;
    z-index: 9999;
  }

  .container { max-width: 1400px; margin: 0 auto; padding: 20px; position: relative; z-index: 1; }

  /* Header */
  .header {
    text-align: center;
    padding: 40px 20px 30px;
    position: relative;
  }
  .header-icon {
    font-size: 56px;
    margin-bottom: 12px;
    animation: hover 3s ease-in-out infinite;
  }
  @keyframes hover {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
  }
  .header h1 {
    font-family: 'Orbitron', monospace;
    font-size: clamp(2rem, 5vw, 3.2rem);
    font-weight: 900;
    letter-spacing: 2px;
    background: linear-gradient(135deg, var(--neon-cyan), var(--neon-purple), var(--neon-pink));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .header .subtitle {
    color: var(--text-secondary);
    font-size: 0.95rem;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 8px;
    letter-spacing: 3px;
    text-transform: uppercase;
  }
  .header .meta-badges {
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 20px;
  }
  .badge {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 0.8rem;
    font-family: 'JetBrains Mono', monospace;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .badge .dot {
    width: 8px; height: 8px; border-radius: 50%;
  }
  .dot.green { background: var(--neon-green); box-shadow: 0 0 6px var(--neon-green); }
  .dot.cyan { background: var(--neon-cyan); box-shadow: 0 0 6px var(--neon-cyan); }
  .dot.purple { background: var(--neon-purple); box-shadow: 0 0 6px var(--neon-purple); }

  /* Leaderboard Table */
  .section-title {
    font-family: 'Orbitron', monospace;
    font-size: 1.3rem;
    font-weight: 700;
    margin: 30px 0 16px;
    padding-left: 16px;
    border-left: 3px solid var(--neon-cyan);
    letter-spacing: 1px;
  }

  .table-wrap {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 40px;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
  }
  thead { background: var(--bg-secondary); }
  thead th {
    padding: 14px 16px;
    text-transform: uppercase;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 2px;
    color: var(--text-dim);
    text-align: left;
    border-bottom: 1px solid var(--border);
  }
  thead th.right { text-align: right; }
  tbody td {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
  }
  tbody td.right { text-align: right; }
  tbody tr {
    transition: background 0.2s;
  }
  tbody tr:hover { background: var(--bg-card-hover); }
  .rank-cell {
    font-family: 'Orbitron', monospace;
    font-weight: 700;
    font-size: 1.1rem;
    text-align: center;
    width: 50px;
  }
  .rank-1 { color: var(--gold); }
  .rank-2 { color: var(--silver); }
  .rank-3 { color: var(--bronze); }
  .pilot-cell {
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .pilot-avatar {
    width: 32px; height: 32px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.85rem; color: #111;
    text-transform: uppercase;
  }
  .best-time { color: var(--neon-green); font-weight: 700; }
  .highlight-b3 { color: var(--neon-cyan); font-weight: 600; }

  /* Pilot detail cards */
  .cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
  }
  .pilot-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    transition: all 0.3s;
    position: relative;
    overflow: hidden;
  }
  .pilot-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--neon-purple), var(--neon-cyan), var(--neon-pink));
    opacity: 0;
    transition: opacity 0.3s;
  }
  .pilot-card:hover { transform: translateY(-2px); box-shadow: 0 8px 32px rgba(0,0,0,0.4); }
  .pilot-card:hover::before { opacity: 1; }

  .card-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 20px;
  }
  .card-avatar {
    width: 44px; height: 44px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 1rem; color: #111;
    font-family: 'Orbitron', monospace;
  }
  .card-pilot-name {
    font-family: 'Orbitron', monospace;
    font-size: 1.2rem;
    font-weight: 700;
  }
  .card-rank {
    margin-left: auto;
    font-family: 'Orbitron', monospace;
    font-size: 1.5rem;
    font-weight: 900;
    opacity: 0.3;
  }

  .stat-row {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    flex-wrap: wrap;
  }
  .stat {
    background: var(--bg-secondary);
    border-radius: 12px;
    padding: 12px 16px;
    flex: 1;
    min-width: 100px;
    text-align: center;
  }
  .stat-label {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--text-dim);
    margin-bottom: 6px;
  }
  .stat-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.15rem;
    font-weight: 700;
  }
  .stat-value.green { color: var(--neon-green); }
  .stat-value.cyan { color: var(--neon-cyan); }
  .stat-value.pink { color: var(--neon-pink); }
  .stat-value.yellow { color: var(--neon-yellow); }

  /* Try rows */
  .tries-section {
    margin-top: 18px;
  }
  .tries-section-label {
    font-size: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--text-dim);
    margin-bottom: 10px;
  }
  .try-row {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 6px;
  }
  .try-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: var(--text-dim);
    min-width: 36px;
    text-align: right;
    flex-shrink: 0;
  }
  .try-bars {
    display: flex;
    gap: 2px;
    align-items: flex-end;
    height: 36px;
    flex: 1;
    position: relative;
  }
  .try-b3-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.55rem;
    color: var(--neon-cyan);
    min-width: 44px;
    flex-shrink: 0;
    opacity: 0;
  }
  .try-b3-badge.visible { opacity: 1; }
  .lap-bar {
    flex: 1;
    min-width: 3px;
    border-radius: 2px 2px 0 0;
    transition: all 0.2s;
    position: relative;
  }
  .lap-bar:hover {
    filter: brightness(1.4);
    transform: scaleY(1.08);
    transform-origin: bottom;
    z-index: 2;
  }
  .lap-bar:hover::after {
    content: attr(data-tooltip);
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    background: var(--bg-card);
    color: var(--text-primary);
    border: 1px solid var(--neon-cyan);
    border-radius: 6px;
    padding: 4px 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    white-space: nowrap;
    pointer-events: none;
    z-index: 100;
    margin-bottom: 4px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.6), 0 0 12px rgba(0,240,255,0.15);
    animation: tooltipIn 0.1s ease-out;
  }
  @keyframes tooltipIn {
    from { opacity: 0; transform: translateX(-50%) translateY(3px); }
    to { opacity: 1; transform: translateX(-50%) translateY(0); }
  }
  .lap-bar.highlight-b3 { background: var(--neon-cyan) !important; box-shadow: 0 0 6px var(--neon-cyan); }
  .lap-bar.highlight-b3:hover::after {
    border-color: var(--neon-cyan);
    box-shadow: 0 4px 16px rgba(0,0,0,0.6), 0 0 16px rgba(0,240,255,0.3);
  }

  .best3-detail {
    margin-top: 14px;
    padding: 12px 16px;
    background: rgba(0,240,255,0.06);
    border: 1px solid rgba(0,240,255,0.2);
    border-radius: 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--neon-cyan);
  }
  .best3-detail .b3-label {
    font-family: 'Orbitron', monospace;
    font-size: 0.65rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--neon-cyan);
    margin-bottom: 6px;
  }

  /* Summary section */
  .summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
    margin-bottom: 40px;
  }
  .summary-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
  }
  .summary-value {
    font-family: 'Orbitron', monospace;
    font-size: 2rem;
    font-weight: 900;
    background: linear-gradient(135deg, var(--neon-cyan), var(--neon-purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .summary-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--text-dim);
    margin-top: 6px;
  }

  /* Footer */
  .footer {
    text-align: center;
    padding: 30px;
    color: var(--text-dim);
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
  }

  @media (max-width: 768px) {
    .cards-grid { grid-template-columns: 1fr; }
    .stat-row { flex-direction: column; }
    .lap-bars { height: 50px; }
    .header { padding: 20px 10px; }
    table { font-size: 0.7rem; }
    thead th, tbody td { padding: 8px 10px; }
  }
</style>
</head>
<body>

<div class="container">

  <!-- Header -->
  <div class="header">
    <div class="header-icon">🏁</div>
    <h1>DRONE RACING</h1>
    <p class="subtitle">Leaderboard &amp; Telemetry</p>
    <div class="meta-badges" id="metaBadges"></div>
  </div>

  <!-- Race Summary -->
  <div class="summary-grid" id="summaryGrid"></div>

  <!-- Leaderboard -->
  <h2 class="section-title">🏆 Leaderboard</h2>
  <div class="table-wrap" id="tableWrap"></div>

  <!-- Pilot Detail Cards -->
  <h2 class="section-title">📊 Pilot Telemetry</h2>
  <div class="cards-grid" id="cardsGrid"></div>

  <div class="footer">
    &#9670; TRACKSIDE TIMING SYSTEM &#9670; Generated from 27.06.xlsx &#9670;
  </div>

</div>

<script>
const PALETTE = [
  '#00f0ff','#ff2d95','#39ff14','#ff6b35','#b44dff','#4488ff','#ffe600','#ff4444',
  '#44ff88','#ff8844','#44ffff','#ff44ff','#88ff44','#ff4488','#4488ff'
];

const DATA = __DATA_PLACEHOLDER__;

// Build summary
(function buildSummary() {
  const results = DATA.results;
  const allTimes = results.flatMap(r => r.tries.flatMap(t => t.laps.map(l => l.time)));
  const fastestLap = Math.min(...allTimes);
  const totalLaps = results.reduce((s, r) => s + r.total_laps, 0);
  const totalTries = results.reduce((s, r) => s + r.total_tries, 0);
  const bestAvg = results[0]?.avg_lap || 0;

  const badges = [
    [Math.round(fastestLap * 1000), 'ms', 'Fastest Lap', 'green'],
    [totalLaps, '', 'Clean Laps', 'cyan'],
    [DATA.pilots, '', 'Pilots', 'purple'],
  ];

  document.getElementById('metaBadges').innerHTML = badges.map(([v, u]) =>
    `<div class="badge"><span class="dot ${badges[0][3]}"></span>${v}${u}</div>`
  ).join('');

  document.getElementById('summaryGrid').innerHTML = [
    {v: totalLaps, l: 'Clean Laps Analyzed'},
    {v: totalTries, l: 'Total Tries (Races)'},
    {v: DATA.pilots, l: 'Pilots on Track'},
    {v: fastestLap.toFixed(3) + 's', l: 'Fastest Single Lap'},
  ].map(s => `<div class="summary-card"><div class="summary-value">${s.v}</div><div class="summary-label">${s.l}</div></div>`).join('');
})();

// Build leaderboard table
(function buildTable() {
  const results = DATA.results;
  const medals = {0: '🥇', 1: '🥈', 2: '🥉'};

  const rows = results.map((r, i) => {
    const b3 = r.best_consecutive_3;
    const color = PALETTE[i % PALETTE.length];
    const initials = r.pilot.substring(0, 2).toUpperCase();
    return `
    <tr>
      <td class="rank-cell rank-${i+1}">${medals[i] || '#'+(i+1)}</td>
      <td>
        <div class="pilot-cell">
          <div class="pilot-avatar" style="background:${color}">${initials}</div>
          ${r.pilot}
        </div>
      </td>
      <td class="right">${r.total_tries}</td>
      <td class="right">${r.total_laps}</td>
      <td class="right best-time">${r.best_lap.toFixed(3)}s</td>
      <td class="right">${r.avg_lap.toFixed(3)}s</td>
      <td class="right highlight-b3">${b3 ? b3.avg.toFixed(3) + 's' : '—'}</td>
    </tr>`;
  }).join('');

  document.getElementById('tableWrap').innerHTML = `
  <table>
    <thead>
      <tr>
        <th class="right">#</th>
        <th>Pilot</th>
        <th class="right">Tries</th>
        <th class="right">Laps</th>
        <th class="right">Best Lap</th>
        <th class="right">Avg</th>
        <th class="right">Best 3 Consec</th>
      </tr>
    </thead>
    <tbody>${rows}</tbody>
  </table>`;
})();

// Build pilot cards
(function buildCards() {
  const results = DATA.results;
  // Max time across all laps in all tries for bar scaling
  const allTimes = results.flatMap(r => r.tries.flatMap(t => t.laps.map(l => l.time)));
  const maxTime = Math.max(...allTimes);

  const cards = results.map((r, i) => {
    const color = PALETTE[i % PALETTE.length];
    const initials = r.pilot.substring(0, 2).toUpperCase();
    const b3 = r.best_consecutive_3;
    const b3Try = r.best_consecutive_3_try || '';
    const medals = {0: '1st', 1: '2nd', 2: '3rd'};

    // Get b3 lap numbers as set for highlighting
    const b3Laps = new Set();
    if (b3) b3.laps.forEach(l => b3Laps.add(l.lap));

    // Build try rows
    const tryRows = r.tries.map(t => {
      const tryHasB3 = t.best_consecutive_3 && t.best_consecutive_3.avg === (b3 && b3.avg);
      const bars = t.laps.map(l => {
        const h = Math.max(4, (l.time / maxTime) * 100);
        const isB3 = tryHasB3 && b3Laps.has(l.lap);
        const b3label = isB3 ? ' ⚡BEST3' : '';
        return `<div class="lap-bar ${isB3 ? 'highlight-b3' : ''}"
          style="height:${h}%;background:${color};opacity:${isB3 ? 1 : 0.45}"
          data-tooltip="Lap ${l.lap}: ${l.time.toFixed(3)}s${b3label}"></div>`;
      }).join('');
      const b3avg = t.best_consecutive_3 ? t.best_consecutive_3.avg.toFixed(3) + 's' : '';
      return `
      <div class="try-row">
        <div class="try-label">R${t.round}</div>
        <div class="try-bars">${bars}</div>
        <div class="try-b3-badge ${tryHasB3 ? 'visible' : ''}">${tryHasB3 ? '⚡'+b3avg : ''}</div>
      </div>`;
    }).join('');

    return `
    <div class="pilot-card">
      <div class="card-header">
        <div class="card-avatar" style="background:${color}">${initials}</div>
        <div class="card-pilot-name">${r.pilot}</div>
        <div class="card-rank">${medals[i] || '#'+(i+1)}</div>
      </div>

      <div class="stat-row">
        <div class="stat">
          <div class="stat-label">Tries</div>
          <div class="stat-value yellow">${r.total_tries}</div>
        </div>
        <div class="stat">
          <div class="stat-label">Laps</div>
          <div class="stat-value">${r.total_laps}</div>
        </div>
        <div class="stat">
          <div class="stat-label">Best Lap</div>
          <div class="stat-value green">${r.best_lap.toFixed(3)}s</div>
        </div>
        <div class="stat">
          <div class="stat-label">Average</div>
          <div class="stat-value pink">${r.avg_lap.toFixed(3)}s</div>
        </div>
        <div class="stat">
          <div class="stat-label">Median</div>
          <div class="stat-value cyan">${r.median_lap.toFixed(3)}s</div>
        </div>
      </div>

      <div class="tries-section">
        <div class="tries-section-label">Laps by Try</div>
        ${tryRows}
      </div>

      ${b3 ? `
      <div class="best3-detail">
        <div class="b3-label">⚡ Best 3 Consecutive — ${b3Try}</div>
        Laps ${b3.laps.map(l => l.lap).join(' → ')} &nbsp;|&nbsp;
        Times ${b3.laps.map(l => l.time.toFixed(3)+'s').join('  ')}<br>
        Sum: ${b3.sum.toFixed(3)}s &nbsp;|&nbsp; Avg: ${b3.avg.toFixed(3)}s
      </div>` : ''}
    </div>`;
  }).join('');

  document.getElementById('cardsGrid').innerHTML = cards;
})();
</script>

</body>
</html>'''


def build_html(data_file="data.json", output_file="index.html"):
    with open(data_file, encoding="utf-8") as f:
        data = json.load(f)

    html = HTML_TEMPLATE.replace("__DATA_PLACEHOLDER__", json.dumps(data, ensure_ascii=False))

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated {output_file} ({len(html):,} bytes)")


if __name__ == "__main__":
    build_html()
