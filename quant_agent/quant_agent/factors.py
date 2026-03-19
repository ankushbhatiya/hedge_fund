import pandas as pd
import numpy as np

class FactorModel:
    def __init__(self):
        pass
        
    def calculate_momentum_factor(self, price_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates 12-month minus 1-month momentum.
        Formula: (Price(t-21) / Price(t-252)) - 1
        This avoids the short-term mean reversion effect of the last month.
        """
        # Shift 21 days (approx 1 month) and divide by shift 252 days (approx 1 year)
        momentum = (price_data.shift(21) / price_data.shift(252)) - 1
        return momentum
        
    def calculate_low_volatility_factor(self, price_data: pd.DataFrame, window: int = 63) -> pd.DataFrame:
        """
        Calculates the inverse of the annualized volatility over the last 3 months (63 trading days).
        Higher score = Lower volatility.
        """
        returns = price_data.pct_change()
        volatility = returns.rolling(window=window).std() * np.sqrt(252)
        # Inverse volatility (we want to reward low vol)
        # Add small epsilon to avoid division by zero
        low_vol_score = 1.0 / (volatility + 1e-6)
        return low_vol_score
        
    def calculate_technical_indicators(self, price_data: pd.DataFrame) -> dict:
        """
        Calculates custom implementations of RSI, Bollinger Bands, and EMAs.
        Returns a dictionary of DataFrames.
        """
        indicators = {}
        
        # 1. EMA (Exponential Moving Average)
        indicators['EMA_50'] = price_data.ewm(span=50, adjust=False).mean()
        indicators['EMA_200'] = price_data.ewm(span=200, adjust=False).mean()
        
        # Trend filter: 1 if EMA_50 > EMA_200 else 0
        indicators['Trend_Bullish'] = (indicators['EMA_50'] > indicators['EMA_200']).astype(int)
        
        # 2. RSI (14-day)
        delta = price_data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-6)
        indicators['RSI_14'] = 100 - (100 / (1 + rs))
        
        # 3. Bollinger Bands (20-day, 2 std dev)
        sma_20 = price_data.rolling(window=20).mean()
        std_20 = price_data.rolling(window=20).std()
        indicators['BB_Upper'] = sma_20 + (std_20 * 2)
        indicators['BB_Lower'] = sma_20 - (std_20 * 2)
        # Position within bands: 0 = at lower band, 1 = at upper band
        bb_width = indicators['BB_Upper'] - indicators['BB_Lower']
        indicators['BB_Position'] = (price_data - indicators['BB_Lower']) / (bb_width + 1e-6)
        
        return indicators
        
    def combine_factors(self, price_data: pd.DataFrame) -> pd.DataFrame:
        """
        Combines Momentum and Low Volatility into a single Z-scored alpha signal.
        """
        # Calculate raw factors
        mom = self.calculate_momentum_factor(price_data)
        low_vol = self.calculate_low_volatility_factor(price_data)
        
        # Cross-sectional Z-score each day (normalize across the active universe)
        def z_score(df):
            mean = df.mean(axis=1)
            std = df.std(axis=1)
            return df.sub(mean, axis=0).div(std + 1e-6, axis=0)
            
        mom_z = z_score(mom)
        vol_z = z_score(low_vol)
        
        # Blend factors (e.g., 60% Momentum, 40% Low Volatility)
        combined_score = (0.6 * mom_z) + (0.4 * vol_z)
        return combined_score
        
    def normalize_sentiment(self, sentiment_scores: pd.Series) -> pd.Series:
        """Normalizes the Analyst Agent's sentiment scores into a -1 to +1 range."""
        z_scores = (sentiment_scores - sentiment_scores.mean()) / (sentiment_scores.std() + 1e-6)
        return np.tanh(z_scores)

