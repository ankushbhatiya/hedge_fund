import json
import os
import stat
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

class QuantLibrarian:
    def __init__(self, data_dir: str):
        """
        Initializes the Librarian for a specific universe directory.
        Expects a constituents.json file inside data_dir.
        """
        self.data_dir = Path(data_dir)
        self.master_dir = self.data_dir / "master"
        self.raw_dir = self.data_dir / "raw"
        self.constituents_file = self.data_dir / "constituents.json"
        
        # Ensure directory structure exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.master_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def get_universe(self, as_of_date: str) -> dict:
        """Returns constituents as of a specific date from constituents.json."""
        if not self.constituents_file.exists():
            raise FileNotFoundError(f"{self.constituents_file} is missing. Please create it first.")
            
        with open(self.constituents_file) as f:
            data = json.load(f)

        target_date = datetime.strptime(as_of_date, "%Y-%m-%d")
        snapshots = data.get("constituents_by_date", [])
        # Sort so newest is first
        snapshots.sort(key=lambda x: datetime.strptime(x["effective_date"], "%Y-%m-%d"), reverse=True)

        for snapshot in snapshots:
            snap_date = datetime.strptime(snapshot["effective_date"], "%Y-%m-%d")
            if target_date >= snap_date:
                return {
                    "effective_from": snapshot["effective_date"],
                    "count": len(snapshot["constituents"]),
                    "constituents": snapshot["constituents"],
                    "notes": snapshot.get("notes", "")
                }
                
        # If requested date is older than our oldest snapshot, return the oldest
        if snapshots:
            oldest = snapshots[-1]
            return {
                "effective_from": oldest["effective_date"],
                "count": len(oldest["constituents"]),
                "constituents": oldest["constituents"],
                "notes": "WARNING: Requested date pre-dates oldest snapshot."
            }
            
        return {"effective_from": None, "count": 0, "constituents": []}

    def get_ticker_info(self, ticker: str) -> Optional[dict]:
        """Get metadata for a specific ticker."""
        if not self.constituents_file.exists():
            return None
        with open(self.constituents_file) as f:
            data = json.load(f)
        return data.get("ticker_mapping", {}).get(ticker)

    def get_yf_ticker(self, ticker: str) -> str:
        """Get the Yahoo Finance symbol for a ticker, defaulting to the ticker itself."""
        info = self.get_ticker_info(ticker)
        if info and "yf_ticker" in info:
            return info["yf_ticker"]
        return ticker

    def list_master_files(self) -> List[str]:
        """List available EOD master data files."""
        return [f.stem for f in self.master_dir.glob("*.json")]

    def get_eod_master(self, ticker: str) -> Optional[dict]:
        """Load EOD data for a specific ticker from master directory."""
        filepath = self.master_dir / f"{ticker}.json"
        if not filepath.exists():
            return None
        with open(filepath) as f:
            return json.load(f)

    def merge_snapshot_to_master(self, ticker: str, snapshot_date: str) -> tuple[bool, str]:
        """
        Appends a daily raw snapshot to the master file.
        Ensures no duplicates and maintains chronological order.
        """
        raw_path = self.raw_dir / snapshot_date / f"{ticker}.json"
        if not raw_path.exists():
            return False, "Raw snapshot not found"

        with open(raw_path) as f:
            snapshot = json.load(f)
        
        if not snapshot.get("data"):
            return False, "Snapshot contains no data"

        new_record = snapshot["data"][0] 
        
        master_data = self.get_eod_master(ticker)
        if not master_data:
            master_data = {
                "ticker": ticker,
                "yf_ticker": snapshot.get("yf_ticker"),
                "source": "vault_sync",
                "mapping": snapshot.get("mapping", {}),
                "data": []
            }

        existing_dates = {r["date"] for r in master_data["data"]}
        if new_record["date"] in existing_dates:
            return True, "Date already exists in master (skipped)"

        master_data["data"].append(new_record)
        master_data["data"].sort(key=lambda x: x["date"])

        master_path = self.master_dir / f"{ticker}.json"
        with open(master_path, "w") as f:
            json.dump(master_data, f, indent=2)
        
        return True, "Successfully merged to master"

    def audit_database(self) -> dict:
        """Basic audit to count records in the master database."""
        files = self.list_master_files()
        results = {"tickers_checked": len(files), "details": {}}
        for ticker in files:
            data = self.get_eod_master(ticker)
            if data and data.get("data"):
                record_count = len(data["data"])
                results["details"][ticker] = {"records": record_count}
        return results
