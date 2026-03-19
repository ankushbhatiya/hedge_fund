import pandas as pd
import numpy as np
from datetime import datetime
from .backtest import BacktestEngine
from .factors import FactorModel

class QuantAgent:
    def __init__(self, librarian):
        """
        Initializes the Quant Agent.
        Requires a QuantLibrarian instance to access historical "ground truth" data.
        """
        self.librarian = librarian
        self.engine = BacktestEngine()
        self.factor_model = FactorModel()
        
    def _prepare_data(self):
        """
        Helper method to extract all master data from the Librarian into a 
        pandas DataFrame suitable for vectorized operations.
        """
        all_data = {}
        tickers = self.librarian.list_master_files()
        
        for ticker in tickers:
            data = self.librarian.get_eod_master(ticker)
            if data and data.get("data"):
                # Create a Series of closing prices indexed by date
                dates = [datetime.strptime(row["date"], "%Y-%m-%d") for row in data["data"]]
                closes = [row["close"] for row in data["data"]]
                all_data[ticker] = pd.Series(data=closes, index=dates)
                
        # Combine into a single DataFrame where rows are dates, columns are tickers
        df = pd.DataFrame(all_data)
        df.sort_index(inplace=True)
        # Forward fill missing values (e.g. trading holidays, suspensions)
        df.ffill(inplace=True)
        
        # Filter extreme outliers (e.g., data errors > 200% daily move)
        # This protects the backtest from "moonshot" data artifacts like MBTN in 2006
        returns = df.pct_change()
        # Create a mask of valid returns
        mask = (returns < 2.0) & (returns > -0.9)
        # Keep the first row intact
        mask.iloc[0] = True
        
        # Apply mask and ffill again to carry forward the pre-outlier price
        df = df[mask].ffill()
        
        return df

    def run_backtest(self, strategy_params: dict = None):
        """Executes a full historical simulation using the current strategy logic."""
        print("Preparing historical data from Librarian...")
        price_data = self._prepare_data()
        
        print("Generating Factor Scores...")
        # Use FactorModel to calculate Momentum & Low Volatility blended Z-scores
        combined_scores = self.factor_model.combine_factors(price_data)
        
        print("Generating target weights...")
        # Strategy: Go long the top quintile (or positive Z-scores)
        # We will keep only positive scores, set negative to 0, then normalize to sum to 1.0 per day
        long_only = combined_scores.where(combined_scores > 0, 0)
        target_weights = long_only.div(long_only.sum(axis=1), axis=0)
        
        # Fill NaN weights with 0
        target_weights = target_weights.fillna(0.0)
        
        print("Executing Backtest Engine...")
        result = self.engine.run(target_weights, price_data)
        
        print("Generating Report...")
        self.engine.generate_report(result)
        return result
        
    def optimize_factors(self, search_space: dict):
        """Performs a grid search or Bayesian optimization to find the best signal weights."""
        pass
        
    def calculate_metrics(self, returns_series: pd.Series):
        """Generates performance attribution: Alpha, Beta, Volatility, Drawdown, etc."""
        # Now handled by quantstats inside BacktestEngine.generate_report
        pass
        
    def stress_test_monte_carlo(self, returns_series: pd.Series, iterations: int = 1000):
        """Shuffles historical returns to check if the result is statistically significant."""
        pass
