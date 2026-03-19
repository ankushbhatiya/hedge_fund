import json
import os
import stat
from datetime import datetime, timedelta
from pathlib import Path

try:
    import yfinance as yf
except ImportError:
    pass

from .core import QuantLibrarian

class DataFetcher:
    def __init__(self, librarian: QuantLibrarian):
        self.lib = librarian

    def fetch_eod_yfinance(self, ticker: str, start: str, end: str) -> dict:
        """Fetch EOD data for a single ticker using yfinance."""
        yf_ticker = self.lib.get_yf_ticker(ticker)

        try:
            stock = yf.Ticker(yf_ticker)
            hist = stock.history(start=start, end=end, auto_adjust=False)

            if hist.empty:
                return {
                    "ticker": ticker,
                    "yf_ticker": yf_ticker,
                    "data": [],
                    "error": "No data found",
                }

            records = []
            for date, row in hist.iterrows():
                records.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]),
                })

            return {"ticker": ticker, "yf_ticker": yf_ticker, "source": "yfinance", "data": records}

        except Exception as e:
            return {"ticker": ticker, "yf_ticker": yf_ticker, "data": [], "error": str(e)}

    def save_raw_snapshot(self, ticker: str, data: dict, snapshot_date: str):
        """Save EOD data to raw directory and make it READ-ONLY."""
        day_dir = self.lib.raw_dir / snapshot_date
        day_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = day_dir / f"{ticker}.json"
        
        if filepath.exists():
            os.chmod(filepath, stat.S_IWRITE | stat.S_IREAD)

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        # Set to READ-ONLY (mode 0o444)
        os.chmod(filepath, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
        return filepath

    def fetch_daily_sync(self, as_of_date: str = None):
        """Fetches the latest trading day and automatically merges to master."""
        if not as_of_date:
            target_date = datetime.now() - timedelta(days=1)
            as_of_date = target_date.strftime("%Y-%m-%d")
        
        start_str = as_of_date
        end_dt = datetime.strptime(as_of_date, "%Y-%m-%d") + timedelta(days=1)
        end_str = end_dt.strftime("%Y-%m-%d")

        universe_info = self.lib.get_universe(as_of_date)
        constituents = universe_info.get("constituents", [])

        print(f"--- Vault Daily Sync: {as_of_date} ---")
        
        for c in constituents:
            ticker = c["ticker"]
            print(f"  -> {ticker}", end=" ", flush=True)
            
            result = self.fetch_eod_yfinance(ticker, start_str, end_str)
            
            if result.get("data"):
                self.save_raw_snapshot(ticker, result, as_of_date)
                success, msg = self.lib.merge_snapshot_to_master(ticker, as_of_date)
                print(f"[OK: {msg}]")
            else:
                print(f"[SKIP: {result.get('error', 'No data')}]")
