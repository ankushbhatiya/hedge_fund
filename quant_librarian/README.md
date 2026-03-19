# Quant Librarian

A generic, architecture-driven Python library for managing financial data universes. It implements the "Vault" architecture, ensuring data immutability, auditability, and easy retrieval for quantitative analysis.

## Core Concepts

1. **Constituents Map (`constituents.json`)**: The point-in-time reference database defining what tickers belong to the universe at any given time, along with their data source mappings.
2. **The Vault (`raw/`)**: Daily, immutable, read-only snapshots of EOD (End of Day) data. Protects against upstream data corruption.
3. **The Master (`master/`)**: Consolidated, chronological history of each ticker built safely from the Vault. Used directly for backtesting.

## Installation

You can use this locally by including it in your project path. It requires `yfinance` and `pandas`.

```bash
pip install yfinance pandas
```

## Directory Structure
To use the Librarian, you need a base data directory with a `constituents.json` file. The Librarian will automatically create the `raw` and `master` directories.

```text
my_index_data/
├── constituents.json
├── master/
└── raw/
```

## Usage

### 1. Daily Multi-Universe Sync (Recommended)
You can sync all your configured universes (e.g., SP500, NASDAQ100) at once using the included sync script.

```bash
cd quant_librarian
python3 sync_today.py
```
*Note: You may need to edit `sync_today.py` to change `target_date` if you want it to run for a specific day's close.*

### 2. Programmatic Usage
You can also use the library inside your own Python scripts:

```python
from quant_librarian import QuantLibrarian, DataFetcher

# Initialize for a specific universe (e.g., SP500)
# This directory must contain a valid `constituents.json`
librarian = QuantLibrarian(data_dir="../sp500/data")

# Get the universe as of a specific date
universe = librarian.get_universe("2026-03-15")
print(f"Constituents count: {universe['count']}")

# Fetch and sync data into the Vault & Master
fetcher = DataFetcher(librarian)
fetcher.fetch_daily_sync("2026-03-15")

# Audit the health of your master database
audit_report = librarian.audit_database()
print(audit_report)
```
