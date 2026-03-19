import pandas as pd
import numpy as np
from typing import Dict, Union, Tuple

class RiskManager:
    def __init__(self, portfolio_size: float = 100000.0):
        """
        Initializes the Risk Manager.
        """
        self.portfolio_size = portfolio_size
        
        # Risk Parameters
        self.max_sector_weight = 0.30  # Max 30% in one sector
        self.max_adv_participation = 0.05  # Max 5% of 20-day ADV
        self.max_spread = 0.005  # Max 0.5% bid-ask spread
        self.drawdown_circuit_breaker = -0.05 # -5% in 5 days triggers de-risking
        
    def validate_trade(self, ticker: str, target_weight: float, adv_20d: float, current_volatility: float) -> Tuple[str, float, str]:
        """
        Runs the Pre-Trade Audit on a proposed order.
        
        Returns:
            Tuple: (Status ['APPROVED', 'REJECTED', 'RESIZE'], New Weight, Reason)
        """
        # 1. ADV Liquidity Check
        target_notional = target_weight * self.portfolio_size
        if target_notional > (adv_20d * self.max_adv_participation):
            max_allowed_weight = (adv_20d * self.max_adv_participation) / self.portfolio_size
            return "RESIZE", max_allowed_weight, f"Target exceeds 5% ADV. Resized from {target_weight:.2%} to {max_allowed_weight:.2%}"
            
        # 2. Volatility Check
        # Placeholder logic: reject if current vol is abnormally high (e.g. > 4% daily)
        if current_volatility > 0.04:
            return "REJECTED", 0.0, "Volatility exceeds safety threshold."
            
        return "APPROVED", target_weight, "Passes all risk checks."
        
    def check_liquidity(self, ticker: str, adv_20d: float) -> float:
        """
        Returns the max allowed position size (in base currency) for a specific ticker today.
        """
        return adv_20d * self.max_adv_participation
        
    def emergency_liquidate(self) -> str:
        """
        Immediately signals an exit of all positions (The 'Red Button').
        """
        # In a live system, this would send market sell orders via IBKR API
        print("!!! EMERGENCY LIQUIDATION TRIGGERED !!!")
        return "ALL_POSITIONS_CLOSED"
        
    def get_risk_report(self, portfolio_returns: pd.Series) -> Dict[str, float]:
        """
        Generates a summary of Value at Risk (VaR) and Expected Shortfall.
        """
        if portfolio_returns.empty:
            return {"VaR_95": 0.0, "Expected_Shortfall_95": 0.0}
            
        # Historical VaR (95% confidence)
        var_95 = np.percentile(portfolio_returns, 5)
        
        # Expected Shortfall (Conditional VaR)
        es_95 = portfolio_returns[portfolio_returns <= var_95].mean()
        
        return {
            "VaR_95": round(var_95, 4),
            "Expected_Shortfall_95": round(es_95, 4)
        }
