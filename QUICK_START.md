# Quick Start - 5 Minutes to Your First Analysis

## For the Absolute Beginner

### Step 1: Install Python (5 minutes, one-time setup)
- **Windows:** Download from https://python.org → Check "Add to PATH" → Install
- **Mac:** Open Terminal → Run `brew install python`

### Step 2: Download This Code (1 minute)
```bash
# Download and enter the folder
git clone https://github.com/chochocho147/fuzzy-dollop.git
cd fuzzy-dollop
git checkout claude/geolift-testing-pipeline-1d0DT
```

### Step 3: Install Required Packages (2 minutes)
```bash
pip install -r requirements.txt
```

### Step 4: Run Example (1 minute)
```bash
python example_cli.py
```

**Done!** You'll see results printed and 3 files created:
- `sample_data.csv` - example data
- `geolift_results.csv` - detailed results
- `geolift_results.png` - charts

---

## Use Your Own Data (3 Steps)

### 1. Prepare Your CSV

Save as `my_data.csv` with these columns:
```
date,location,revenue
2024-01-01,chicago,12500
2024-01-01,houston,10200
2024-01-02,chicago,13100
...
```

### 2. Create `run_my_test.py`

```python
from geolift import GeoLift

gl = GeoLift()
gl.load_data('my_data.csv')
gl.run_test(
    treatment_locations=['chicago', 'houston'],  # ← Your treatment cities
    treatment_start='2024-01-15',                 # ← Your test start date
    treatment_end='2024-02-15'                    # ← Your test end date
)
gl.plot_results()
gl.summary()
gl.export_results('results.csv')
```

### 3. Run It

```bash
python run_my_test.py
```

---

## Compare with Haus

1. Use the **same CSV** in both tools
2. Use the **same treatment locations and dates**
3. Compare these numbers:

| Metric | Where to Find |
|--------|---------------|
| Total Lift | "Incremental Lift" in output |
| % Effect | "Relative Effect" in output |
| Significant? | "P-value" (< 0.05 = yes) |

They should be similar (within 10-20%).

---

## Common Errors & Fixes

| Error | Fix |
|-------|-----|
| "No module named pandas" | Run `pip install -r requirements.txt` |
| "No such file my_data.csv" | Put CSV in same folder as script |
| "KeyError: date" | Your CSV needs columns: date, location, revenue |
| Date format error | Use YYYY-MM-DD format (2024-01-15) |
| "AttributeError: ... 'summary_data'" | Wrong package! Run: `pip uninstall causalimpact && pip install tfcausalimpact` |

---

## Need More Detail?

→ See **BEGINNER_GUIDE.md** for complete step-by-step instructions

→ See **README.md** for full documentation

→ Open **example_usage.ipynb** in Jupyter for interactive tutorial
