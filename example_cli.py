#!/usr/bin/env python3
"""
Command-line example for GeoLift testing pipeline
Run this script to see a complete workflow
"""

from geolift import GeoLift
from generate_sample_data import generate_sample_data
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for command line
import matplotlib.pyplot as plt

def main():
    print("\n" + "="*80)
    print("GEOLIFT TESTING PIPELINE - COMMAND LINE EXAMPLE")
    print("="*80 + "\n")

    # Step 1: Generate sample data
    print("STEP 1: Generating sample data...")
    print("-" * 80)
    df = generate_sample_data(
        n_locations=10,
        n_days=180,
        treatment_locations=['chicago', 'houston'],
        treatment_start_day=120,
        treatment_lift=0.15,  # 15% lift
        output_file='sample_data.csv'
    )

    # Step 2: Initialize GeoLift and load data
    print("\n\nSTEP 2: Loading data into GeoLift...")
    print("-" * 80)
    gl = GeoLift()
    gl.load_data('sample_data.csv')

    # Step 3: Data exploration
    print("\n\nSTEP 3: Data exploration...")
    print("-" * 80)
    summary = gl.summary_stats()

    # Step 4: Analyze pre-treatment fit
    print("\n\nSTEP 4: Analyzing pre-treatment fit...")
    print("-" * 80)
    treatment_locs = ['chicago', 'houston']
    fit_results = gl.analyze_fit(
        treatment_locations=treatment_locs,
        pre_period_end='2024-04-30'
    )

    # Step 5: Power analysis
    print("\n\nSTEP 5: Power analysis...")
    print("-" * 80)
    print("\nEstimating MDE for different test durations:\n")

    durations = [14, 30, 45, 60]
    for duration in durations:
        result = gl.estimate_mde(
            treatment_locations=treatment_locs,
            test_duration_days=duration,
            pre_period_end='2024-04-30'
        )

    # Step 6: Run test
    print("\n\nSTEP 6: Running synthetic control test...")
    print("-" * 80)
    results = gl.run_test(
        treatment_locations=['chicago', 'houston'],
        treatment_start='2024-05-01',
        treatment_end='2024-06-29'
    )

    # Step 7: Results summary
    print("\n\nSTEP 7: Test results...")
    print("-" * 80)
    summary_results = gl.summary()

    # Step 8: Export results
    print("\n\nSTEP 8: Exporting results...")
    print("-" * 80)
    gl.export_results('geolift_results.csv')

    # Step 9: Save plots
    print("\nSTEP 9: Saving visualizations...")
    print("-" * 80)

    # Save trends plot
    gl.plot_trends()
    plt.savefig('geolift_trends.png', dpi=150, bbox_inches='tight')
    print("✓ Saved trends plot: geolift_trends.png")
    plt.close()

    # Save results plot
    gl.plot_results()
    plt.savefig('geolift_results.png', dpi=150, bbox_inches='tight')
    print("✓ Saved results plot: geolift_results.png")
    plt.close()

    # Final summary
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print("\nGenerated files:")
    print("  - sample_data.csv         : Input data")
    print("  - geolift_results.csv     : Detailed results")
    print("  - geolift_trends.png      : Time series visualization")
    print("  - geolift_results.png     : Synthetic control analysis")
    print("\nKey Results:")
    print(f"  - Cumulative Lift:        ${summary_results['cumulative_effect']:,.2f}")
    print(f"  - 95% CI:                 [${summary_results['confidence_interval'][0]:,.2f}, "
          f"${summary_results['confidence_interval'][1]:,.2f}]")
    print(f"  - Relative Effect:        {summary_results['relative_effect_pct']:.2f}%")
    print(f"  - P-value:                {summary_results['p_value']:.4f}")
    print(f"  - Significant:            {summary_results['significant']}")
    print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    main()
