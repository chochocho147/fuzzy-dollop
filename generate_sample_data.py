"""
Generate sample data for GeoLift testing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data(
    n_locations: int = 10,
    n_days: int = 180,
    treatment_locations: list = ['chicago', 'houston'],
    treatment_start_day: int = 120,
    treatment_lift: float = 0.15,
    output_file: str = 'sample_data.csv'
):
    """
    Generate synthetic geo experiment data

    Parameters:
    -----------
    n_locations : int
        Number of locations
    n_days : int
        Number of days
    treatment_locations : list
        Locations that receive treatment
    treatment_start_day : int
        Day when treatment starts (0-indexed)
    treatment_lift : float
        Relative lift from treatment (e.g., 0.15 = 15% lift)
    output_file : str
        Output CSV filename
    """

    # Generate location names
    cities = ['new_york', 'los_angeles', 'chicago', 'houston', 'phoenix',
              'philadelphia', 'san_antonio', 'san_diego', 'dallas', 'san_jose',
              'austin', 'jacksonville', 'fort_worth', 'columbus', 'charlotte']

    locations = cities[:n_locations]

    # Generate dates
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(n_days)]

    # Generate data
    data = []

    for location in locations:
        # Base revenue level (different for each location)
        base_revenue = np.random.uniform(5000, 15000)

        # Trend component (slight upward trend)
        trend = np.linspace(0, base_revenue * 0.1, n_days)

        # Seasonal component (weekly seasonality)
        seasonal = base_revenue * 0.15 * np.sin(np.arange(n_days) * 2 * np.pi / 7)

        # Random noise
        noise = np.random.normal(0, base_revenue * 0.1, n_days)

        # Generate revenue
        revenue = base_revenue + trend + seasonal + noise

        # Add treatment effect if applicable
        if location in treatment_locations:
            treatment_effect = np.zeros(n_days)
            treatment_effect[treatment_start_day:] = revenue[treatment_start_day:] * treatment_lift
            revenue = revenue + treatment_effect

        # Add spend (correlated with revenue)
        spend = revenue * np.random.uniform(0.15, 0.25) + np.random.normal(0, 200, n_days)

        # Create records
        for i, date in enumerate(dates):
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'location': location,
                'revenue': max(0, revenue[i]),  # Ensure non-negative
                'spend': max(0, spend[i])
            })

    # Create DataFrame
    df = pd.DataFrame(data)

    # Save to CSV
    df.to_csv(output_file, index=False)

    print(f"✓ Sample data generated: {output_file}")
    print(f"  - Locations: {n_locations}")
    print(f"  - Days: {n_days}")
    print(f"  - Treatment locations: {', '.join(treatment_locations)}")
    print(f"  - Treatment start: Day {treatment_start_day} ({dates[treatment_start_day].strftime('%Y-%m-%d')})")
    print(f"  - Treatment lift: {treatment_lift*100:.1f}%")

    return df

if __name__ == '__main__':
    # Generate sample data
    df = generate_sample_data(
        n_locations=10,
        n_days=180,
        treatment_locations=['chicago', 'houston'],
        treatment_start_day=120,
        treatment_lift=0.15,
        output_file='sample_data.csv'
    )

    print(f"\nFirst few rows:")
    print(df.head(20))
