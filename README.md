# GeoLift Testing Pipeline

A Python implementation of synthetic control analysis for geo experiments, designed to validate results against platforms like Haus.

## Features

- **Data Validation & Exploration**: Load CSV data, validate format, and visualize pre-period trends
- **Market Selection**: Calculate pre-treatment fit and correlation between locations
- **Power Analysis**: Estimate Minimum Detectable Effect (MDE) for different test durations
- **Synthetic Control Analysis**: Build synthetic controls using weighted combinations of control locations
- **Statistical Output**: Lift estimates with confidence intervals, p-values, and cumulative effects
- **Visualization**: Time series plots comparing actual vs synthetic counterfactual

## Installation

### Prerequisites

Python 3.7 or higher

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Dependencies

- `numpy` - Numerical computing
- `pandas` - Data manipulation
- `matplotlib` - Plotting
- `seaborn` - Statistical visualizations
- `scipy` - Statistical functions
- `scikit-learn` - Machine learning tools
- `statsmodels` - Statistical models
- `causalimpact` - Bayesian causal inference (optional but recommended)
- `jupyter` - Jupyter notebook support

## Quick Start

### 1. Prepare Your Data

Create a CSV file with the following columns:

- `date` (YYYY-MM-DD format)
- `location` (city/state/DMA name)
- `revenue` (or conversions - your metric of interest)
- `spend` (optional)

Example:
```csv
date,location,revenue,spend
2024-01-01,chicago,12500.50,2800.00
2024-01-01,houston,10200.30,2100.00
2024-01-02,chicago,13100.20,2900.00
```

### 2. Basic Usage

```python
from geolift import GeoLift

# Initialize
gl = GeoLift()

# Load data
gl.load_data("my_data.csv")

# Explore data
gl.summary_stats()
gl.plot_trends()

# Run test
gl.run_test(
    treatment_locations=["chicago", "houston"],
    treatment_start="2024-01-15",
    treatment_end="2024-02-15"
)

# View results
gl.plot_results()
gl.summary()
```

## Detailed Usage

### Data Loading

```python
# Load with default column names
gl.load_data("data.csv")

# Load with custom column names
gl.load_data(
    "data.csv",
    date_col="date",
    location_col="city",
    metric_col="conversions",
    spend_col="media_spend"
)
```

### Pre-Test Analysis

#### Market Selection
```python
# Analyze fit between treatment and control locations
fit_results = gl.analyze_fit(
    treatment_locations=["chicago", "houston"],
    pre_period_end="2024-01-14"  # Before treatment starts
)
```

#### Power Analysis
```python
# Estimate Minimum Detectable Effect
mde_results = gl.estimate_mde(
    treatment_locations=["chicago", "houston"],
    test_duration_days=30,
    alpha=0.05,  # 95% confidence
    power=0.8,   # 80% power
    pre_period_end="2024-01-14"
)

print(f"MDE: {mde_results['mde_relative_pct']:.2f}%")
```

### Running Tests

#### Basic Test
```python
results = gl.run_test(
    treatment_locations=["chicago", "houston"],
    treatment_start="2024-01-15",
    treatment_end="2024-02-15"
)
```

#### Test with Specific Controls
```python
results = gl.run_test(
    treatment_locations=["chicago", "houston"],
    treatment_start="2024-01-15",
    treatment_end="2024-02-15",
    control_locations=["new_york", "los_angeles", "phoenix"]
)
```

### Results & Visualization

```python
# Plot results (actual vs synthetic, effects, cumulative)
gl.plot_results()

# Print summary statistics
summary = gl.summary()

# Access specific metrics
cumulative_lift = summary['cumulative_effect']
confidence_interval = summary['confidence_interval']
p_value = summary['p_value']
is_significant = summary['significant']

# Export results to CSV
gl.export_results("geolift_results.csv")
```

## Example Workflow

### Using the Jupyter Notebook

```bash
jupyter notebook example_usage.ipynb
```

### Using the Command Line Script

```python
python generate_sample_data.py
```

This generates sample data with a known treatment effect for testing.

### Sample Output

```
GEOLIFT TEST RESULTS SUMMARY
================================================================================
Treatment locations: chicago, houston
Control locations: new_york, los_angeles, phoenix, philadelphia, san_diego
Test period: 2024-01-15 to 2024-02-15 (32 days)
--------------------------------------------------------------------------------

CUMULATIVE RESULTS:
  Incremental Lift:     45,231.50
  95% CI:               [32,450.20, 58,012.80]
  Relative Effect:      14.85%
  Average Daily Lift:   1,413.48

STATISTICAL SIGNIFICANCE:
  P-value:              0.0023
  Result:               ✓ STATISTICALLY SIGNIFICANT (p < 0.05)

SYNTHETIC CONTROL WEIGHTS:
  new_york                      : 0.3521
  los_angeles                   : 0.2847
  phoenix                       : 0.2104
  philadelphia                  : 0.0893
  san_diego                     : 0.0635

MODEL FIT (PRE-PERIOD):
  R²:                   0.9234
  RMSE:                 892.45
================================================================================
```

## Methodology

### Synthetic Control Method

The pipeline implements synthetic control analysis using:

1. **Pre-period model training**: Learns optimal weights to combine control locations
2. **Synthetic control construction**: Creates a weighted average of controls that best matches treatment locations
3. **Post-period comparison**: Compares actual treatment metrics vs synthetic counterfactual
4. **Statistical inference**: Calculates confidence intervals and p-values

### Implementation Options

- **CausalImpact** (recommended): Uses Bayesian structural time-series when available
- **Custom Implementation**: Falls back to Ridge regression-based synthetic control

Both methods follow standard synthetic control methodology compatible with platforms like Haus.

## Validating Against Haus

To compare results with Haus:

1. **Use identical data**: Input the same CSV to both platforms
2. **Match parameters**: Use the same treatment locations, dates, and control groups
3. **Compare metrics**:
   - Cumulative lift estimate
   - 95% confidence intervals
   - P-values
   - Relative effect percentages
4. **Check methodology**: Both platforms should use synthetic control/ASCM approaches

Expected differences:
- Minor variations due to different optimization algorithms
- Different Bayesian priors in CausalImpact vs Haus
- Control weight distributions may differ slightly

The core lift estimates and statistical significance should align closely.

## API Reference

### GeoLift Class

#### `load_data(filepath, date_col='date', location_col='location', metric_col='revenue', spend_col=None)`
Load and validate data from CSV

#### `summary_stats()`
Show summary statistics per location

#### `plot_trends(locations=None, figsize=(14, 6))`
Visualize time series trends across locations

#### `analyze_fit(treatment_locations, pre_period_end=None)`
Calculate pre-treatment fit between treatment and control locations

#### `estimate_mde(treatment_locations, test_duration_days=30, alpha=0.05, power=0.8, pre_period_end=None)`
Estimate Minimum Detectable Effect (MDE)

#### `run_test(treatment_locations, treatment_start, treatment_end, control_locations=None, alpha=0.05)`
Run synthetic control analysis

#### `plot_results(figsize=(14, 10))`
Plot synthetic control results

#### `summary()`
Print summary of test results

#### `export_results(filepath)`
Export results to CSV

## Troubleshooting

### CausalImpact Installation Issues

If `causalimpact` fails to install:

```bash
pip install causalimpact --no-cache-dir
```

Or use the fallback implementation (automatically used if CausalImpact is unavailable).

### Memory Issues with Large Datasets

For datasets with many locations or long time periods:

1. Filter to relevant date ranges before loading
2. Reduce number of control locations
3. Use the custom implementation instead of CausalImpact

### Poor Model Fit

If pre-period R² is low (<0.7):

1. Check for missing data or outliers
2. Ensure sufficient pre-period data (recommended: 60+ days)
3. Verify control locations are good matches (high correlation)
4. Consider different control location combinations

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License

## References

- Abadie, A., Diamond, A., & Hainmueller, J. (2010). Synthetic control methods for comparative case studies.
- Brodersen, K. H., et al. (2015). Inferring causal impact using Bayesian structural time-series models.
- Google's CausalImpact package: https://github.com/google/CausalImpact

## Support

For questions or issues, please open an issue on GitHub or contact the maintainers.
