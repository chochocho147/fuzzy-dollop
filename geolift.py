"""
GeoLift Testing Pipeline
A Python implementation for synthetic control analysis in geo experiments
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import List, Optional, Dict, Tuple
from scipy import stats
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_squared_error
import warnings

warnings.filterwarnings('ignore')

# Try to import causalimpact, fallback to manual implementation if not available
try:
    from causalimpact import CausalImpact
    CAUSALIMPACT_AVAILABLE = True
except ImportError:
    CAUSALIMPACT_AVAILABLE = False
    print("Warning: causalimpact not available. Using fallback synthetic control implementation.")


class GeoLift:
    """
    GeoLift class for geo experiment analysis using synthetic control methods
    """

    def __init__(self):
        self.data = None
        self.data_pivoted = None
        self.treatment_locations = None
        self.control_locations = None
        self.treatment_start = None
        self.treatment_end = None
        self.pre_period = None
        self.post_period = None
        self.results = None
        self.model = None
        self.weights = None
        self.synthetic_control = None

    def load_data(self, filepath: str, date_col: str = 'date',
                  location_col: str = 'location', metric_col: str = 'revenue',
                  spend_col: Optional[str] = None) -> pd.DataFrame:
        """
        Load and validate data from CSV

        Parameters:
        -----------
        filepath : str
            Path to CSV file
        date_col : str
            Name of date column
        location_col : str
            Name of location column
        metric_col : str
            Name of metric column (revenue/conversions)
        spend_col : Optional[str]
            Name of spend column if available

        Returns:
        --------
        pd.DataFrame
            Loaded and validated dataframe
        """
        print(f"Loading data from {filepath}...")

        # Load data
        df = pd.read_csv(filepath)

        # Validate required columns
        required_cols = [date_col, location_col, metric_col]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Standardize column names
        df = df.rename(columns={
            date_col: 'date',
            location_col: 'location',
            metric_col: 'metric'
        })

        if spend_col and spend_col in df.columns:
            df = df.rename(columns={spend_col: 'spend'})

        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])

        # Sort by location and date
        df = df.sort_values(['location', 'date']).reset_index(drop=True)

        # Store original data
        self.data = df

        # Create pivoted version for analysis
        self.data_pivoted = df.pivot(index='date', columns='location', values='metric')

        print(f"✓ Data loaded successfully")
        print(f"  - Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"  - Total locations: {df['location'].nunique()}")
        print(f"  - Total days: {df['date'].nunique()}")
        print(f"  - Metric: {metric_col}")

        return df

    def summary_stats(self) -> pd.DataFrame:
        """
        Show summary statistics per location

        Returns:
        --------
        pd.DataFrame
            Summary statistics by location
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")

        summary = self.data.groupby('location').agg({
            'metric': ['mean', 'std', 'sum', 'count'],
            'date': ['min', 'max']
        }).round(2)

        summary.columns = ['avg_daily_metric', 'std_dev', 'total_metric', 'days', 'start_date', 'end_date']
        summary = summary.reset_index()

        print("\n" + "="*80)
        print("SUMMARY STATISTICS BY LOCATION")
        print("="*80)
        print(summary.to_string(index=False))
        print("="*80 + "\n")

        return summary

    def plot_trends(self, locations: Optional[List[str]] = None,
                   figsize: Tuple[int, int] = (14, 6)):
        """
        Visualize time series trends across locations

        Parameters:
        -----------
        locations : Optional[List[str]]
            Specific locations to plot. If None, plots all locations
        figsize : Tuple[int, int]
            Figure size
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")

        if locations is None:
            locations = self.data['location'].unique()

        fig, ax = plt.subplots(figsize=figsize)

        for loc in locations:
            loc_data = self.data[self.data['location'] == loc]
            ax.plot(loc_data['date'], loc_data['metric'], label=loc, linewidth=2, alpha=0.7)

        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Metric', fontsize=12)
        ax.set_title('Time Series Trends by Location', fontsize=14, fontweight='bold')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

    def analyze_fit(self, treatment_locations: List[str],
                   pre_period_end: Optional[str] = None) -> pd.DataFrame:
        """
        Calculate pre-treatment fit between treatment and control locations

        Parameters:
        -----------
        treatment_locations : List[str]
            List of treatment location names
        pre_period_end : Optional[str]
            End date for pre-period. If None, uses all available data

        Returns:
        --------
        pd.DataFrame
            Correlation matrix showing fit between locations
        """
        if self.data_pivoted is None:
            raise ValueError("No data loaded. Call load_data() first.")

        # Filter to pre-period if specified
        if pre_period_end:
            data = self.data_pivoted[self.data_pivoted.index <= pd.to_datetime(pre_period_end)]
        else:
            data = self.data_pivoted

        # Calculate correlation matrix
        corr_matrix = data.corr()

        # Extract correlations with treatment locations
        treatment_corr = corr_matrix.loc[treatment_locations, :].T
        treatment_corr = treatment_corr[~treatment_corr.index.isin(treatment_locations)]
        treatment_corr = treatment_corr.sort_values(by=treatment_corr.columns[0], ascending=False)

        print("\n" + "="*80)
        print("PRE-TREATMENT FIT ANALYSIS")
        print("="*80)
        print(f"Treatment locations: {', '.join(treatment_locations)}")
        print(f"\nCorrelation with control locations:")
        print(treatment_corr.to_string())
        print("="*80 + "\n")

        # Visualize correlation heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm',
                   center=0, vmin=-1, vmax=1, ax=ax, square=True)
        ax.set_title('Location Correlation Matrix', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()

        return treatment_corr

    def estimate_mde(self, treatment_locations: List[str],
                    test_duration_days: int = 30,
                    alpha: float = 0.05,
                    power: float = 0.8,
                    pre_period_end: Optional[str] = None) -> Dict:
        """
        Estimate Minimum Detectable Effect (MDE) for different test parameters

        Parameters:
        -----------
        treatment_locations : List[str]
            Treatment location names
        test_duration_days : int
            Expected test duration in days
        alpha : float
            Significance level (default 0.05 for 95% confidence)
        power : float
            Statistical power (default 0.8)
        pre_period_end : Optional[str]
            End date for pre-period

        Returns:
        --------
        Dict
            MDE estimates and parameters
        """
        if self.data_pivoted is None:
            raise ValueError("No data loaded. Call load_data() first.")

        # Filter to pre-period
        if pre_period_end:
            data = self.data_pivoted[self.data_pivoted.index <= pd.to_datetime(pre_period_end)]
        else:
            data = self.data_pivoted

        # Get treatment data
        treatment_data = data[treatment_locations].sum(axis=1)

        # Calculate baseline statistics
        baseline_mean = treatment_data.mean()
        baseline_std = treatment_data.std()

        # Calculate standard error for test period
        se = baseline_std / np.sqrt(test_duration_days)

        # MDE formula: (Z_alpha/2 + Z_power) * SE
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_power = stats.norm.ppf(power)

        mde_absolute = (z_alpha + z_power) * se
        mde_relative = (mde_absolute / baseline_mean) * 100

        results = {
            'test_duration_days': test_duration_days,
            'baseline_mean': baseline_mean,
            'baseline_std': baseline_std,
            'mde_absolute': mde_absolute,
            'mde_relative_pct': mde_relative,
            'alpha': alpha,
            'power': power
        }

        print("\n" + "="*80)
        print("MINIMUM DETECTABLE EFFECT (MDE) ANALYSIS")
        print("="*80)
        print(f"Treatment locations: {', '.join(treatment_locations)}")
        print(f"Test duration: {test_duration_days} days")
        print(f"Significance level (α): {alpha}")
        print(f"Statistical power: {power}")
        print(f"\nBaseline daily metric: {baseline_mean:.2f} ± {baseline_std:.2f}")
        print(f"MDE (absolute): {mde_absolute:.2f}")
        print(f"MDE (relative): {mde_relative:.2f}%")
        print("="*80 + "\n")

        return results

    def run_test(self, treatment_locations: List[str],
                treatment_start: str, treatment_end: str,
                control_locations: Optional[List[str]] = None,
                alpha: float = 0.05) -> Dict:
        """
        Run synthetic control analysis

        Parameters:
        -----------
        treatment_locations : List[str]
            Treatment location names
        treatment_start : str
            Treatment start date (YYYY-MM-DD)
        treatment_end : str
            Treatment end date (YYYY-MM-DD)
        control_locations : Optional[List[str]]
            Control locations. If None, uses all non-treatment locations
        alpha : float
            Significance level

        Returns:
        --------
        Dict
            Test results including lift estimate, confidence intervals, p-value
        """
        if self.data_pivoted is None:
            raise ValueError("No data loaded. Call load_data() first.")

        # Store test parameters
        self.treatment_locations = treatment_locations
        self.treatment_start = pd.to_datetime(treatment_start)
        self.treatment_end = pd.to_datetime(treatment_end)

        # Determine control locations
        all_locations = self.data_pivoted.columns.tolist()
        if control_locations is None:
            self.control_locations = [loc for loc in all_locations
                                     if loc not in treatment_locations]
        else:
            self.control_locations = control_locations

        # Define periods
        self.pre_period = [self.data_pivoted.index.min(), self.treatment_start - pd.Timedelta(days=1)]
        self.post_period = [self.treatment_start, self.treatment_end]

        print("\n" + "="*80)
        print("RUNNING SYNTHETIC CONTROL ANALYSIS")
        print("="*80)
        print(f"Treatment locations: {', '.join(self.treatment_locations)}")
        print(f"Control locations: {', '.join(self.control_locations)}")
        print(f"Pre-period: {self.pre_period[0].date()} to {self.pre_period[1].date()}")
        print(f"Post-period: {self.post_period[0].date()} to {self.post_period[1].date()}")
        print("="*80 + "\n")

        # Aggregate treatment data
        treatment_ts = self.data_pivoted[self.treatment_locations].sum(axis=1)
        control_ts = self.data_pivoted[self.control_locations]

        # Use CausalImpact if available, otherwise use custom implementation
        if CAUSALIMPACT_AVAILABLE:
            results = self._run_causalimpact(treatment_ts, control_ts)
        else:
            results = self._run_synthetic_control(treatment_ts, control_ts)

        self.results = results
        return results

    def _run_causalimpact(self, treatment_ts: pd.Series,
                         control_ts: pd.DataFrame) -> Dict:
        """
        Run analysis using CausalImpact library
        """
        # Prepare data for CausalImpact
        data = pd.concat([treatment_ts, control_ts], axis=1)
        data.columns = ['y'] + [f'x{i}' for i in range(len(control_ts.columns))]

        # Define periods
        pre_period = [self.pre_period[0], self.pre_period[1]]
        post_period = [self.post_period[0], self.post_period[1]]

        # Run CausalImpact
        ci = CausalImpact(data, pre_period, post_period, prior_level_sd=0.01)

        # Extract results
        summary = ci.summary_data

        results = {
            'actual': ci.data['y'],
            'predicted': ci.data['y'] - ci.data['point_effect'],
            'point_effect': ci.data['point_effect'],
            'lower_bound': ci.data['point_effect_lower'],
            'upper_bound': ci.data['point_effect_upper'],
            'cumulative_effect': summary['average']['cum_effect'][0],
            'cumulative_lower': summary['average']['cum_effect_lower'][0],
            'cumulative_upper': summary['average']['cum_effect_upper'][0],
            'p_value': summary['average'].get('p_value', [None])[0],
            'relative_effect': summary['average']['rel_effect'][0],
            'causalimpact_object': ci
        }

        return results

    def _run_synthetic_control(self, treatment_ts: pd.Series,
                              control_ts: pd.DataFrame) -> Dict:
        """
        Run synthetic control using custom implementation (fallback)
        """
        # Split into pre and post periods
        pre_mask = (treatment_ts.index >= self.pre_period[0]) & (treatment_ts.index <= self.pre_period[1])
        post_mask = (treatment_ts.index >= self.post_period[0]) & (treatment_ts.index <= self.post_period[1])

        y_pre = treatment_ts[pre_mask].values
        X_pre = control_ts[pre_mask].values

        y_post = treatment_ts[post_mask].values
        X_post = control_ts[post_mask].values

        # Fit Ridge regression on pre-period to find optimal weights
        model = Ridge(alpha=0.1, fit_intercept=True, positive=True)
        model.fit(X_pre, y_pre)

        # Store model and weights
        self.model = model
        self.weights = model.coef_

        # Generate predictions
        y_pre_pred = model.predict(X_pre)
        y_post_pred = model.predict(X_post)

        # Calculate effects
        point_effect_post = y_post - y_post_pred
        cumulative_effect = point_effect_post.sum()

        # Calculate standard error and confidence intervals
        residuals_pre = y_pre - y_pre_pred
        sigma = np.std(residuals_pre)
        n_post = len(y_post)

        # Standard error for cumulative effect
        se_cum = sigma * np.sqrt(n_post)

        # 95% confidence intervals
        z_score = stats.norm.ppf(1 - 0.025)
        cumulative_lower = cumulative_effect - z_score * se_cum
        cumulative_upper = cumulative_effect + z_score * se_cum

        # P-value (two-tailed test)
        t_stat = cumulative_effect / se_cum
        p_value = 2 * (1 - stats.norm.cdf(abs(t_stat)))

        # Relative effect
        avg_post_pred = y_post_pred.mean()
        relative_effect = (cumulative_effect / (avg_post_pred * n_post)) * 100 if avg_post_pred != 0 else 0

        # Build full time series
        y_full = treatment_ts.values
        X_full = control_ts.values
        y_pred_full = model.predict(X_full)
        point_effect_full = y_full - y_pred_full

        results = {
            'actual': treatment_ts,
            'predicted': pd.Series(y_pred_full, index=treatment_ts.index),
            'point_effect': pd.Series(point_effect_full, index=treatment_ts.index),
            'lower_bound': pd.Series(point_effect_full - 1.96 * sigma, index=treatment_ts.index),
            'upper_bound': pd.Series(point_effect_full + 1.96 * sigma, index=treatment_ts.index),
            'cumulative_effect': cumulative_effect,
            'cumulative_lower': cumulative_lower,
            'cumulative_upper': cumulative_upper,
            'p_value': p_value,
            'relative_effect': relative_effect,
            'weights': self.weights,
            'control_locations': self.control_locations,
            'r2_pre': r2_score(y_pre, y_pre_pred),
            'rmse_pre': np.sqrt(mean_squared_error(y_pre, y_pre_pred))
        }

        return results

    def plot_results(self, figsize: Tuple[int, int] = (14, 10)):
        """
        Plot synthetic control results

        Parameters:
        -----------
        figsize : Tuple[int, int]
            Figure size
        """
        if self.results is None:
            raise ValueError("No results available. Run run_test() first.")

        fig, axes = plt.subplots(3, 1, figsize=figsize)

        # Plot 1: Actual vs Synthetic
        ax1 = axes[0]
        actual = self.results['actual']
        predicted = self.results['predicted']

        ax1.plot(actual.index, actual.values, 'ko-', label='Actual', linewidth=2, markersize=4)
        ax1.plot(predicted.index, predicted.values, 'b--', label='Synthetic Control', linewidth=2)
        ax1.axvline(x=self.treatment_start, color='red', linestyle='--', linewidth=2, alpha=0.7)
        ax1.axvspan(self.treatment_start, self.treatment_end, alpha=0.1, color='red', label='Treatment Period')
        ax1.set_ylabel('Metric', fontsize=11)
        ax1.set_title('Actual vs Synthetic Control', fontsize=13, fontweight='bold')
        ax1.legend(loc='best', fontsize=10)
        ax1.grid(True, alpha=0.3)

        # Plot 2: Point-wise effect
        ax2 = axes[1]
        point_effect = self.results['point_effect']
        lower = self.results['lower_bound']
        upper = self.results['upper_bound']

        ax2.plot(point_effect.index, point_effect.values, 'g-', linewidth=2, label='Point Effect')
        ax2.fill_between(point_effect.index, lower.values, upper.values,
                        alpha=0.2, color='green', label='95% CI')
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
        ax2.axvline(x=self.treatment_start, color='red', linestyle='--', linewidth=2, alpha=0.7)
        ax2.axvspan(self.treatment_start, self.treatment_end, alpha=0.1, color='red')
        ax2.set_ylabel('Effect', fontsize=11)
        ax2.set_title('Point-wise Causal Effect', fontsize=13, fontweight='bold')
        ax2.legend(loc='best', fontsize=10)
        ax2.grid(True, alpha=0.3)

        # Plot 3: Cumulative effect
        ax3 = axes[2]
        post_mask = (point_effect.index >= self.treatment_start) & (point_effect.index <= self.treatment_end)
        cumulative = point_effect[post_mask].cumsum()

        ax3.plot(cumulative.index, cumulative.values, 'purple', linewidth=2.5, label='Cumulative Effect')
        ax3.fill_between(cumulative.index, 0, cumulative.values, alpha=0.3, color='purple')
        ax3.axhline(y=0, color='black', linestyle='-', linewidth=1)
        ax3.set_xlabel('Date', fontsize=11)
        ax3.set_ylabel('Cumulative Effect', fontsize=11)
        ax3.set_title('Cumulative Causal Effect', fontsize=13, fontweight='bold')
        ax3.legend(loc='best', fontsize=10)
        ax3.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    def summary(self):
        """
        Print summary of test results
        """
        if self.results is None:
            raise ValueError("No results available. Run run_test() first.")

        cum_effect = self.results['cumulative_effect']
        cum_lower = self.results['cumulative_lower']
        cum_upper = self.results['cumulative_upper']
        p_value = self.results['p_value']
        rel_effect = self.results['relative_effect']

        # Calculate average daily effect
        n_days = (self.treatment_end - self.treatment_start).days + 1
        avg_daily_effect = cum_effect / n_days

        print("\n" + "="*80)
        print("GEOLIFT TEST RESULTS SUMMARY")
        print("="*80)
        print(f"Treatment locations: {', '.join(self.treatment_locations)}")
        print(f"Control locations: {', '.join(self.control_locations)}")
        print(f"Test period: {self.treatment_start.date()} to {self.treatment_end.date()} ({n_days} days)")
        print("-" * 80)
        print(f"\nCUMULATIVE RESULTS:")
        print(f"  Incremental Lift:     {cum_effect:,.2f}")
        print(f"  95% CI:               [{cum_lower:,.2f}, {cum_upper:,.2f}]")
        print(f"  Relative Effect:      {rel_effect:.2f}%")
        print(f"  Average Daily Lift:   {avg_daily_effect:,.2f}")
        print(f"\nSTATISTICAL SIGNIFICANCE:")
        print(f"  P-value:              {p_value:.4f}")

        if p_value < 0.05:
            print(f"  Result:               ✓ STATISTICALLY SIGNIFICANT (p < 0.05)")
        else:
            print(f"  Result:               ✗ NOT SIGNIFICANT (p >= 0.05)")

        # Print weights if available
        if 'weights' in self.results:
            print(f"\nSYNTHETIC CONTROL WEIGHTS:")
            weights_dict = dict(zip(self.control_locations, self.results['weights']))
            # Sort by weight descending
            weights_sorted = sorted(weights_dict.items(), key=lambda x: x[1], reverse=True)
            for loc, weight in weights_sorted[:10]:  # Show top 10
                if weight > 0.01:  # Only show meaningful weights
                    print(f"  {loc:30s}: {weight:.4f}")

            if 'r2_pre' in self.results:
                print(f"\nMODEL FIT (PRE-PERIOD):")
                print(f"  R²:                   {self.results['r2_pre']:.4f}")
                print(f"  RMSE:                 {self.results['rmse_pre']:.2f}")

        print("="*80 + "\n")

        return {
            'cumulative_effect': cum_effect,
            'confidence_interval': (cum_lower, cum_upper),
            'relative_effect_pct': rel_effect,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'avg_daily_effect': avg_daily_effect
        }

    def export_results(self, filepath: str):
        """
        Export results to CSV

        Parameters:
        -----------
        filepath : str
            Output file path
        """
        if self.results is None:
            raise ValueError("No results available. Run run_test() first.")

        # Create results dataframe
        results_df = pd.DataFrame({
            'date': self.results['actual'].index,
            'actual': self.results['actual'].values,
            'synthetic_control': self.results['predicted'].values,
            'point_effect': self.results['point_effect'].values,
            'lower_bound': self.results['lower_bound'].values,
            'upper_bound': self.results['upper_bound'].values
        })

        # Add treatment indicator
        results_df['is_treatment_period'] = (
            (results_df['date'] >= self.treatment_start) &
            (results_df['date'] <= self.treatment_end)
        )

        results_df.to_csv(filepath, index=False)
        print(f"✓ Results exported to {filepath}")
