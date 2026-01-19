# GeoLift Analysis Workflow

## Visual Guide: What Happens Step-by-Step

```
┌─────────────────────────────────────────────────────────────────┐
│  START: You Have Geo Experiment Data                           │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Prepare Your Data                                     │
├─────────────────────────────────────────────────────────────────┤
│  • Export data to CSV                                           │
│  • Columns: date, location, revenue (or conversions)           │
│  • Format dates as YYYY-MM-DD                                   │
│  • Save as my_data.csv                                          │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Load Data                                             │
├─────────────────────────────────────────────────────────────────┤
│  Python: gl = GeoLift()                                         │
│          gl.load_data('my_data.csv')                            │
│                                                                 │
│  What happens: Validates format, converts dates, pivots data   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Explore Your Data (Optional but Recommended)          │
├─────────────────────────────────────────────────────────────────┤
│  Python: gl.summary_stats()  # See metrics per location        │
│          gl.plot_trends()    # Visualize time series           │
│                                                                 │
│  Why: Spot outliers, check data quality, understand patterns   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Pre-Test Analysis (Optional but Recommended)          │
├─────────────────────────────────────────────────────────────────┤
│  A) Check if controls match treatment well:                    │
│     gl.analyze_fit(treatment_locations=['chicago'],            │
│                    pre_period_end='2024-01-14')                │
│                                                                 │
│  B) Estimate minimum detectable effect:                        │
│     gl.estimate_mde(treatment_locations=['chicago'],           │
│                     test_duration_days=30)                     │
│                                                                 │
│  Why: Validate test design before running full analysis        │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: Run Synthetic Control Analysis                        │
├─────────────────────────────────────────────────────────────────┤
│  Python: gl.run_test(                                           │
│              treatment_locations=['chicago', 'houston'],        │
│              treatment_start='2024-01-15',                      │
│              treatment_end='2024-02-15'                         │
│          )                                                      │
│                                                                 │
│  What happens:                                                  │
│  1. Splits data into pre-period and post-period                │
│  2. Builds synthetic control from control locations            │
│  3. Calculates lift = actual - synthetic                       │
│  4. Computes confidence intervals and p-values                 │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: View Results                                          │
├─────────────────────────────────────────────────────────────────┤
│  Python: gl.plot_results()  # See visualizations               │
│          gl.summary()       # See statistical summary          │
│                                                                 │
│  You get:                                                       │
│  • Cumulative lift (total incremental revenue)                 │
│  • Confidence intervals (95% CI)                               │
│  • P-value (is it significant?)                                │
│  • Relative effect (% increase)                                │
│  • Charts (actual vs synthetic, effects, cumulative)           │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 7: Export & Share                                        │
├─────────────────────────────────────────────────────────────────┤
│  Python: gl.export_results('results.csv')                       │
│                                                                 │
│  Output: CSV with daily actual, synthetic, and effects         │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 8: Compare with Haus (if applicable)                     │
├─────────────────────────────────────────────────────────────────┤
│  • Upload same CSV to Haus                                      │
│  • Use same treatment locations and dates                      │
│  • Compare cumulative lift, relative effect, p-value           │
│  • Results should be within 10-20%                             │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  DONE! You have validated geo lift results                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Behind the Scenes: How Synthetic Control Works

```
PRE-PERIOD                    POST-PERIOD (Treatment)
(Training)                    (Analysis)

Treatment Location:
  ████████████               🚀 ████████████
  Actual data                   Actual data
                                (with treatment effect)

Control Locations:
  ▓▓▓▓▓▓▓▓▓▓▓▓               ▓▓▓▓▓▓▓▓▓▓▓▓
  Actual data                   Actual data
                                (no treatment)

         ↓                            ↓

  Find optimal weights          Apply same weights
  to match treatment            to predict what treatment
  using controls                WOULD have been
                                without treatment

         ↓                            ↓

  Synthetic Control             Synthetic Control
  (weighted avg of controls)    (counterfactual)
  ════════════                  ════════════

                                     ↓

                            Compare:
                            Actual - Synthetic = LIFT
                            ████████████
                            - ════════════
                            = ▲▲▲▲ (lift)
```

---

## Decision Tree: Which Method to Use?

```
Do you have your own data?
│
├─ YES → Use run_my_analysis.py
│         (Edit configuration section, run it)
│
└─ NO (just testing) → Use example_cli.py
          (Generates sample data and runs full analysis)

Do you prefer command line or interactive?
│
├─ Interactive → Use Jupyter notebook
│                (jupyter notebook example_usage.ipynb)
│
└─ Command line → Use Python scripts
                  (python run_my_analysis.py)

Do you want quick results or detailed analysis?
│
├─ Quick → Run test directly
│          gl.run_test(...) → gl.summary()
│
└─ Detailed → Do full workflow
              Load → Explore → Pre-test → Test → Export
```

---

## What Each File Does

| File | Purpose | When to Use |
|------|---------|-------------|
| `geolift.py` | Core analysis engine | Import this in your scripts |
| `run_my_analysis.py` | Template for your data | Copy & edit for custom analysis |
| `example_cli.py` | Complete working example | Test installation/learn workflow |
| `example_usage.ipynb` | Interactive tutorial | Learn step-by-step visually |
| `generate_sample_data.py` | Creates test data | Generate fake data for testing |
| `requirements.txt` | List of dependencies | Install packages: pip install -r requirements.txt |
| `BEGINNER_GUIDE.md` | Detailed instructions | First time using Python/GeoLift |
| `QUICK_START.md` | Condensed steps | Know Python, want quick start |
| `README.md` | Full documentation | API reference, methodology |

---

## Common Scenarios

### Scenario 1: "I just want to test if this works"
```bash
python example_cli.py
```

### Scenario 2: "I have my own data and know the basics"
1. Edit `run_my_analysis.py` (change file name and dates)
2. Run `python run_my_analysis.py`

### Scenario 3: "I want to learn interactively"
```bash
jupyter notebook example_usage.ipynb
```

### Scenario 4: "I need to compare with Haus"
1. Use exact same CSV for both platforms
2. Run GeoLift analysis
3. Run Haus analysis
4. Compare: cumulative lift, relative effect, p-value

### Scenario 5: "I want complete control"
1. Read README.md for API reference
2. Write custom Python script
3. Import GeoLift class and use specific methods

---

## Timeline: How Long Does Each Step Take?

| Step | Time (First Time) | Time (After Setup) |
|------|-------------------|-------------------|
| Install Python | 10 min | - |
| Download code | 2 min | - |
| Install packages | 5 min | - |
| Prepare data | 10-30 min | 5 min |
| Run analysis | 1-2 min | 1 min |
| Review results | 10-20 min | 5 min |
| **TOTAL** | **40-70 min** | **10-15 min** |

---

## Next Steps After Your First Analysis

1. ✅ Run example with sample data
2. ✅ Try with your own data
3. ✅ Compare with Haus results
4. ✅ Experiment with different control locations
5. ✅ Test sensitivity with different pre-periods
6. ✅ Export results for presentations
7. ✅ Automate for multiple tests
