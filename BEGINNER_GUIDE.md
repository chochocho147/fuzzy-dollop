# Complete Beginner's Guide to GeoLift Testing

This guide assumes you have **zero experience** with Python or command-line tools. Follow each step carefully.

---

## Table of Contents
1. [Prerequisites](#step-1-prerequisites)
2. [Download the Code](#step-2-download-the-code)
3. [Set Up Python Environment](#step-3-set-up-python-environment)
4. [Prepare Your Data](#step-4-prepare-your-data)
5. [Run Your First Test](#step-5-run-your-first-test)
6. [Understanding Results](#step-6-understanding-results)
7. [Compare with Haus](#step-7-compare-with-haus)
8. [Troubleshooting](#troubleshooting)

---

## Step 1: Prerequisites

### Install Python

**Windows:**
1. Go to https://www.python.org/downloads/
2. Download Python 3.10 or later (click the big yellow button)
3. **IMPORTANT:** When installing, check the box "Add Python to PATH"
4. Click "Install Now"

**Mac:**
1. Open Terminal (search for "Terminal" in Spotlight)
2. Install Homebrew (package manager):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. Install Python:
   ```bash
   brew install python
   ```

**Verify Installation:**
Open your terminal/command prompt and type:
```bash
python --version
```
You should see something like `Python 3.10.0` or higher.

---

## Step 2: Download the Code

### Option A: Clone with Git (if you have Git installed)
```bash
git clone https://github.com/chochocho147/fuzzy-dollop.git
cd fuzzy-dollop
git checkout claude/geolift-testing-pipeline-1d0DT
```

### Option B: Download ZIP
1. Go to the GitHub repository
2. Click the green "Code" button
3. Click "Download ZIP"
4. Unzip the folder
5. Open terminal/command prompt and navigate to the folder:
   ```bash
   cd path/to/fuzzy-dollop
   ```

---

## Step 3: Set Up Python Environment

### 3.1 Open Terminal/Command Prompt

**Windows:**
- Press `Windows + R`
- Type `cmd` and press Enter

**Mac:**
- Press `Cmd + Space`
- Type "Terminal" and press Enter

### 3.2 Navigate to Project Folder

```bash
cd path/to/fuzzy-dollop
```
Example:
```bash
cd C:\Users\YourName\Downloads\fuzzy-dollop  # Windows
cd ~/Downloads/fuzzy-dollop                    # Mac
```

### 3.3 Create Virtual Environment (Optional but Recommended)

This keeps your project dependencies isolated.

```bash
python -m venv venv
```

### 3.4 Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` appear at the start of your command line.

### 3.5 Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all necessary packages (might take 2-5 minutes).

---

## Step 4: Prepare Your Data

### 4.1 Data Format

Create a CSV file with these exact columns:

| date       | location  | revenue   | spend   |
|------------|-----------|-----------|---------|
| 2024-01-01 | chicago   | 12500.50  | 2800.00 |
| 2024-01-01 | houston   | 10200.30  | 2100.00 |
| 2024-01-02 | chicago   | 13100.20  | 2900.00 |

**Requirements:**
- ✅ `date` column: Format YYYY-MM-DD
- ✅ `location` column: City/DMA names (lowercase, no spaces)
- ✅ `revenue` column: Your metric (can be conversions, revenue, etc.)
- ✅ `spend` column: Optional (if you have it)

### 4.2 Save Your Data

Save your CSV file as `my_data.csv` in the `fuzzy-dollop` folder.

### 4.3 Test with Sample Data First

Before using your own data, test with sample data:

```bash
python generate_sample_data.py
```

This creates `sample_data.csv` with fake data you can use to test.

---

## Step 5: Run Your First Test

You have **3 options** to run the analysis:

### **Option A: Quick Command-Line Test** (Easiest)

Run the example script:
```bash
python example_cli.py
```

This will:
- Generate sample data
- Run the analysis
- Create result files
- Save plots

**Output files created:**
- `sample_data.csv` - The input data
- `geolift_results.csv` - Detailed results
- `geolift_trends.png` - Time series chart
- `geolift_results.png` - Analysis charts

### **Option B: Jupyter Notebook** (Visual & Interactive)

1. Start Jupyter:
   ```bash
   jupyter notebook
   ```

2. Your web browser will open automatically

3. Click on `example_usage.ipynb`

4. Run each cell by clicking the "Run" button or pressing `Shift + Enter`

5. You'll see plots and results directly in the browser

### **Option C: Write Your Own Script** (Custom Analysis)

Create a new file called `my_analysis.py`:

```python
from geolift import GeoLift

# Step 1: Initialize
gl = GeoLift()

# Step 2: Load your data
gl.load_data('my_data.csv')

# Step 3: Explore your data
gl.summary_stats()
gl.plot_trends()

# Step 4: Analyze pre-treatment fit (BEFORE your test started)
gl.analyze_fit(
    treatment_locations=['chicago', 'houston'],
    pre_period_end='2024-01-14'  # Day before test
)

# Step 5: Estimate minimum detectable effect
gl.estimate_mde(
    treatment_locations=['chicago', 'houston'],
    test_duration_days=30,
    pre_period_end='2024-01-14'
)

# Step 6: Run the test
gl.run_test(
    treatment_locations=['chicago', 'houston'],
    treatment_start='2024-01-15',
    treatment_end='2024-02-15'
)

# Step 7: See results
gl.plot_results()
gl.summary()

# Step 8: Export results
gl.export_results('my_results.csv')
```

Run it:
```bash
python my_analysis.py
```

---

## Step 6: Understanding Results

### Reading the Summary Output

```
GEOLIFT TEST RESULTS SUMMARY
================================================================================
Treatment locations: chicago, houston
Control locations: new_york, los_angeles, phoenix
Test period: 2024-01-15 to 2024-02-15 (32 days)
--------------------------------------------------------------------------------

CUMULATIVE RESULTS:
  Incremental Lift:     45,231.50        ← Total extra revenue/conversions
  95% CI:               [32,450.20, 58,012.80]  ← Confidence range
  Relative Effect:      14.85%           ← Percentage increase
  Average Daily Lift:   1,413.48         ← Daily average increase

STATISTICAL SIGNIFICANCE:
  P-value:              0.0023           ← Lower is better (< 0.05 = significant)
  Result:               ✓ STATISTICALLY SIGNIFICANT
```

### What Each Metric Means

| Metric | What It Means | Good/Bad |
|--------|---------------|----------|
| **Incremental Lift** | Total extra revenue from the test | Higher is better |
| **95% CI** | Range where true effect likely falls | Narrower is better |
| **Relative Effect %** | Percentage increase over baseline | Higher is better |
| **P-value** | Probability result is due to chance | < 0.05 is significant |

### Understanding the Charts

**Chart 1: Actual vs Synthetic**
- Blue dashed line = What WOULD have happened without treatment
- Black solid line = What ACTUALLY happened
- Gap between them = Your lift

**Chart 2: Point-wise Effect**
- Shows the daily lift
- Green shaded area = confidence interval
- Above zero = positive effect

**Chart 3: Cumulative Effect**
- Shows total accumulated lift over time
- Purple area = total incremental value

---

## Step 7: Compare with Haus

### Prepare Data for Both Platforms

1. **Use the exact same CSV** for both GeoLift and Haus
2. **Use the same parameters:**
   - Same treatment locations
   - Same start/end dates
   - Same control locations (if you specified them)

### Run Both Analyses

**In GeoLift:**
```python
gl.run_test(
    treatment_locations=['chicago', 'houston'],
    treatment_start='2024-01-15',
    treatment_end='2024-02-15'
)
summary = gl.summary()
```

**In Haus:**
- Upload the same CSV
- Select same treatment markets
- Use same test dates

### Compare These Metrics

| Metric | Where to Find in GeoLift | What to Compare |
|--------|--------------------------|-----------------|
| Cumulative Lift | `summary['cumulative_effect']` | Should be similar (±10%) |
| Confidence Interval | `summary['confidence_interval']` | Ranges should overlap |
| Relative Effect % | `summary['relative_effect_pct']` | Should be close |
| P-value | `summary['p_value']` | Both should agree on significance |

### Expected Differences

✅ **Normal variations (OK):**
- Lift estimates differ by 5-15%
- Slightly different confidence intervals
- Different synthetic control weights

❌ **Red flags (investigate):**
- Opposite conclusions (one significant, one not)
- Lift estimates differ by >30%
- One shows positive lift, other shows negative

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'pandas'"

**Solution:** You didn't install dependencies. Run:
```bash
pip install -r requirements.txt
```

### Error: "FileNotFoundError: [Errno 2] No such file or directory: 'my_data.csv'"

**Solution:** Your CSV file is not in the right folder. Move it to the `fuzzy-dollop` directory.

### Error: "KeyError: 'date'"

**Solution:** Your CSV doesn't have a column named 'date'. Either:
1. Rename your column to 'date', OR
2. Specify the column name:
   ```python
   gl.load_data('my_data.csv', date_col='your_date_column_name')
   ```

### Error: "ValueError: time data '1/1/2024' does not match format '%Y-%m-%d'"

**Solution:** Your dates are not in YYYY-MM-DD format. In Excel:
1. Select date column
2. Format → Custom
3. Type: `yyyy-mm-dd`
4. Save as CSV again

### Error: "TypeError: CausalImpact.__init__() got an unexpected keyword argument 'prior_level_sd'"

**Solution:** This has been fixed in the latest version. Update your code:
```bash
git pull origin claude/geolift-testing-pipeline-1d0DT
```

If you still see this error, the pipeline will automatically fall back to the custom synthetic control implementation (which works just as well). You'll see:
```
Warning: causalimpact not available. Using fallback synthetic control implementation.
```

### Poor Model Fit (R² < 0.7)

**Possible causes:**
- Not enough pre-period data (need 60+ days)
- Control locations don't match treatment well
- Missing data or outliers

**Solutions:**
1. Add more pre-period data
2. Try different control locations
3. Check for data quality issues

### Plots Don't Show Up

**If using command line:**
- Plots are saved as PNG files instead of displaying
- Look for `geolift_results.png` in your folder

**If using Jupyter:**
- Make sure you run the cell with `gl.plot_results()`
- Try adding `%matplotlib inline` at the top of your notebook

### CausalImpact Installation Issues

If you get errors installing `causalimpact`:

**Option 1:** Skip it (the pipeline will use the backup method)
```bash
pip install -r requirements.txt --no-deps
pip install numpy pandas matplotlib seaborn scipy scikit-learn statsmodels jupyter notebook
```

**Option 2:** Install without cache
```bash
pip install causalimpact --no-cache-dir
```

---

## Quick Reference Commands

```bash
# Activate virtual environment
source venv/bin/activate          # Mac/Linux
venv\Scripts\activate              # Windows

# Generate sample data
python generate_sample_data.py

# Run example analysis
python example_cli.py

# Start Jupyter notebook
jupyter notebook

# Deactivate virtual environment when done
deactivate
```

---

## Need More Help?

1. **Check the main README.md** for API reference
2. **Look at example_usage.ipynb** for detailed workflow
3. **Run example_cli.py** to see a working example
4. **Open an issue** on GitHub if you're stuck

---

## Next Steps

Once you're comfortable with the basics:

1. ✅ Test with sample data (run `example_cli.py`)
2. ✅ Load your own data
3. ✅ Run pre-test analysis (`analyze_fit`, `estimate_mde`)
4. ✅ Run your geo test
5. ✅ Compare with Haus results
6. ✅ Export and share results

Good luck with your geo experiments! 🚀
