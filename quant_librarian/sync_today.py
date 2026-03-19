import os
import sys
from datetime import datetime
from pathlib import Path

# Ensure quant_librarian is in the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from quant_librarian import QuantLibrarian, DataFetcher

def sync_universe(name, data_dir, date_str):
    print("\n========================================")
    print(f"Syncing {name} for {date_str}")
    print(f"========================================")
    
    # Resolve the data directory relative to the workspace root
    full_data_dir = Path(__file__).parent.parent / data_dir
    
    librarian = QuantLibrarian(data_dir=str(full_data_dir))
    fetcher = DataFetcher(librarian)
    fetcher.fetch_daily_sync(date_str)

if __name__ == "__main__":
    # Example sync for a target date
    target_date = "2026-03-13"
    
    # Configure your target universes here
    universes = {
        "SP500": "sp500/data",
        "NASDAQ100": "nasdaq100/data"
    }
    
    for name, data_path in universes.items():
        sync_universe(name, data_path, target_date)
