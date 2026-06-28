# Drone Racing Leaderboard

Processes an XLSX race timing sheet into a clean JSON dataset and a standalone interactive HTML dashboard.

## Quick start

```bash
python3 -m venv venv
source venv/bin/activate
pip install openpyxl
python3 process_data.py
python3 build_html.py
open index.html
```

## How it works

### 1. Filtering false laps (three layers)

| Layer | What it removes |
|---|---|
| **XLSX Valid column** | Laps already marked `False` in the sheet (sensor mistriggers, duplicate entries) |
| **Hard min/max cutoff** | Physically impossible lap times. The track's best possible time is ~10s, so anything below is a sensor glitch. Laps above the max (crashes/recoveries) are also stripped. |
| **IQR outlier detection** | Statistical outliers removed per try using the interquartile range method |

### 2. Grouping by tries

Laps are grouped by **(pilot, round, race)** — each group is one *try*. Consecutive laps only make sense within the same try, so best‑3‑consecutive is computed per try, then the best across all tries is taken for each pilot.

### 3. Computed stats

- **Best lap** — fastest single lap overall
- **Average / Median** — across all clean laps
- **Best 3 consecutive** — fastest 3-lap stretch within a single try (laps must be numbered sequentially within that try)

### 4. HTML dashboard

A single self-contained `index.html` with:
- Dark cyberpunk theme, no server needed
- Ranked leaderboard table
- Pilot cards with per‑try lap‑time bar charts
- Instant custom tooltips on hover (lap time + BEST3 marker)
- Responsive layout

## Configuration

Edit the defaults in `process_data.py` line 89:

```python
def process(filepath="27.06.xlsx", min_lap_time=10.0, max_lap_time=70.0):
```

| Param | Default | Meaning |
|---|---|---|
| `min_lap_time` | 10.0s | Lap times below this are physically impossible |
| `max_lap_time` | 70.0s | Lap times above this are crashes, not racing laps |

Adjust these to match your track.

## Files

| File | Purpose |
|---|---|
| `27.06.xlsx` | Source timing data (input) |
| `process_data.py` | Reads XLSX → filters → computes stats → writes `data.json` |
| `build_html.py` | Injects `data.json` into HTML template → writes `index.html` |
| `data.json` | Intermediate JSON (auto-generated) |
| `index.html` | Standalone dashboard (auto-generated, open in any browser) |
| `venv/` | Python virtual environment |
