#!/usr/bin/env python3
"""
TEMPLATE: Run Your Own GeoLift Analysis

Instructions:
1. Save your data as CSV in this folder
2. Edit the CONFIGURATION section below with your values
3. Run: python run_my_analysis.py
"""

from geolift import GeoLift
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION - EDIT THESE VALUES
# ============================================================================

# Your data file
DATA_FILE = 'my_data.csv'  # ← Change this to your CSV filename

# Column names (if different from defaults)
DATE_COLUMN = 'date'       # Column with dates (YYYY-MM-DD format)
LOCATION_COLUMN = 'location'  # Column with city/DMA names
METRIC_COLUMN = 'revenue'  # Column with your metric (revenue/conversions)
SPEND_COLUMN = None        # Column with spend (or None if you don't have it)

# Treatment configuration
TREATMENT_LOCATIONS = ['chicago', 'houston']  # ← Your treatment cities
TREATMENT_START = '2024-01-15'  # ← When did the test start?
TREATMENT_END = '2024-02-15'    # ← When did the test end?

# Control locations (optional - leave as None to use all non-treatment locations)
CONTROL_LOCATIONS = None  # Example: ['new_york', 'los_angeles', 'phoenix']

# Pre-period end (for pre-test analysis)
PRE_PERIOD_END = '2024-01-14'  # ← Day before test started

# Output file
OUTPUT_FILE = 'my_geolift_results.csv'

# ============================================================================
# ANALYSIS - NO NEED TO EDIT BELOW THIS LINE
# ============================================================================

def main():
    print("\n" + "="*80)
    print("GEOLIFT ANALYSIS")
    print("="*80 + "\n")

    # Initialize GeoLift
    print("Step 1: Loading data...")
    print("-"*80)
    gl = GeoLift()
    gl.load_data(
        DATA_FILE,
        date_col=DATE_COLUMN,
        location_col=LOCATION_COLUMN,
        metric_col=METRIC_COLUMN,
        spend_col=SPEND_COLUMN
    )

    # Summary statistics
    print("\n\nStep 2: Summary statistics...")
    print("-"*80)
    gl.summary_stats()

    # Visualize trends
    print("\n\nStep 3: Visualizing trends...")
    print("-"*80)
    gl.plot_trends()

    # Pre-treatment fit analysis
    print("\n\nStep 4: Analyzing pre-treatment fit...")
    print("-"*80)
    gl.analyze_fit(
        treatment_locations=TREATMENT_LOCATIONS,
        pre_period_end=PRE_PERIOD_END
    )

    # Power analysis
    print("\n\nStep 5: Power analysis...")
    print("-"*80)
    test_days = (
        pd.to_datetime(TREATMENT_END) - pd.to_datetime(TREATMENT_START)
    ).days + 1

    gl.estimate_mde(
        treatment_locations=TREATMENT_LOCATIONS,
        test_duration_days=test_days,
        pre_period_end=PRE_PERIOD_END
    )

    # Run test
    print("\n\nStep 6: Running synthetic control test...")
    print("-"*80)
    results = gl.run_test(
        treatment_locations=TREATMENT_LOCATIONS,
        treatment_start=TREATMENT_START,
        treatment_end=TREATMENT_END,
        control_locations=CONTROL_LOCATIONS
    )

    # Plot results
    print("\n\nStep 7: Visualizing results...")
    print("-"*80)
    gl.plot_results()

    # Summary
    print("\n\nStep 8: Summary...")
    print("-"*80)
    summary = gl.summary()

    # Export
    print("\n\nStep 9: Exporting results...")
    print("-"*80)
    gl.export_results(OUTPUT_FILE)

    # Final summary
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print(f"\nResults saved to: {OUTPUT_FILE}")
    print("\nKey Findings:")
    print(f"  Cumulative Lift:     ${summary['cumulative_effect']:,.2f}")
    print(f"  Relative Effect:     {summary['relative_effect_pct']:.2f}%")
    print(f"  P-value:             {summary['p_value']:.4f}")
    print(f"  Significant:         {summary['significant']}")
    print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    import pandas as pd
    main()
