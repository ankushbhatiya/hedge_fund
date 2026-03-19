import pandas as pd
import bt
import quantstats as qs

class CustomCommissionSlippage(bt.Algo):
    """
    Custom bt Algo to apply dynamic slippage and commission models.
    """
    def __init__(self, engine):
        super(CustomCommissionSlippage, self).__init__()
        self.engine = engine

    def __call__(self, target):
        # We process commissions and slippage here if needed, 
        # but bt's built-in commission function is often easier.
        return True

class BacktestEngine:
    def __init__(self, initial_capital: float = 100000.0, base_currency: str = "USD"):
        self.initial_capital = initial_capital
        self.base_currency = base_currency
        
        # Realistic simulation defaults
        self.transaction_tax_rate = 0.0005  # 0.05% general transaction tax/fee
        self.base_commission_rate = 0.001 # 0.1% baseline commission
        self.min_commission = 5.0 # 5.0 base currency minimum
        
    def calculate_trade_cost(self, quantity, price):
        """bt commission function callback"""
        notional_value = abs(quantity * price)
        # Use a smooth percentage commission to avoid bt optimization errors 
        # caused by the max() function on small allocation sizes.
        commission = notional_value * self.base_commission_rate
        transaction_tax = notional_value * self.transaction_tax_rate
        return commission + transaction_tax
        
    def run(self, target_weights: pd.DataFrame, price_data: pd.DataFrame):
        """
        Main execution loop using `bt`. Takes aligned target weights and point-in-time price data.
        target_weights: DataFrame of target weights (0.0 to 1.0) indexed by date, columns by ticker.
        price_data: DataFrame of prices indexed by date, columns by ticker.
        """
        
        # Align data
        price_data = price_data.reindex(target_weights.index).ffill()

        # Define the strategy
        strategy = bt.Strategy(
            'Alpha_Quant_Strategy',
            [
                bt.algos.RunDaily(),
                bt.algos.SelectAll(),
                bt.algos.WeighTarget(target_weights),
                bt.algos.Rebalance()
            ]
        )

        # Create the backtest
        backtest = bt.Backtest(
            strategy, 
            price_data, 
            initial_capital=self.initial_capital,
            commissions=self.calculate_trade_cost,
            integer_positions=False
        )

        # Run the simulation
        print("Running bt simulation...")
        result = bt.run(backtest)
        
        return result

    def generate_report(self, bt_result, benchmark_returns=None, output_file="backtest_report.html"):
        """Generates a quantstats tear sheet."""
        # Get the daily returns series from the bt result
        strategy_name = 'Alpha_Quant_Strategy'
        returns = bt_result.prices[strategy_name].pct_change().dropna()
        
        print(f"Generating QuantStats report -> {output_file}")
        qs.reports.html(returns, benchmark=benchmark_returns, output=output_file)
        return returns
