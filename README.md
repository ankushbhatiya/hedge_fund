# 🌐 Multi-Agent Hedge Fund

```text
    __ __         __              ______                __
   / // /__  ____/ /___ ____     / ____/_  ______  ____/ /
  / __  / _ \/ __  / __ `/ _ \   / /_  / / / / __ \/ __  / 
 / / / /  __/ /_/ / /_/ /  __/  / __/ / /_/ / / / / /_/ /  
/_/ /_/\___/\__,_/\__, /\___/  /_/    \__,_/_/ /_/\__,_/   
                 /____/                                    
           Autonomous Multi-Agent Alpha Engine
```

An autonomous algorithmic trading system leveraging a collaborative multi-agent architecture to synthesize sentiment, mathematical rigor, and risk management across global equity markets.

---

## 🏗 System Architecture

The project is divided into four specialized agents, each operating as a distinct layer of the investment process:

### 1. 🔍 [The Analyst](./analyst_agent/Analyst_Agent.md) (Alpha & Sentiment Engine)
*   **Role:** Synthesizes unstructured news, earnings transcripts, and macro trends into directional sentiment scores.
*   **Specialty:** High-performance Natural Language Processing (NLP) across diverse financial news sources and regulatory filings.
*   **Output:** Sentiment Vectors and "Management Tone" delta scores.

### 2. 🔢 [The Quant](./quant_agent/Quant_Agent.md) (Strategy Architect)
*   **Role:** Transforms qualitative hypotheses into rigorous mathematical models.
*   **Specialty:** Vectorized backtesting across historical datasets, multi-factor modeling (Quality/Momentum/Low Vol), and multi-currency normalization.
*   **Output:** Optimized alpha signals and realistic performance attribution reports.

### 3. 🛡️ [The Risk Manager](./risk_manager/Risk_Manager_Agent.md) (Safety & Execution)
*   **Role:** Acts as the final veto on all trades, ensuring capital preservation and liquidity compliance.
*   **Specialty:** Concentration limits, Kelly Criterion position sizing, and automated drawdown circuits.
*   **Output:** Trade validation (Approved/Rejected/Resized) and VaR/Stress reports.

### 4. 📚 [The Librarian](./quant_librarian/README.md) (Data Ingestion)
*   **Role:** Manages the historical and real-time data pipeline.
*   **Specialty:** Syncing daily pricing data, earnings calendars, and index rebalancing events.
*   **Output:** Point-in-time datasets for the strategy engine.

---

## 🔄 The Collaborative Workflow

1.  **Ingestion:** **The Librarian** syncs today's market data and news.
2.  **Analysis:** **The Analyst** generates a sentiment heatmap for the active universe.
3.  **Synthesis:** **The Quant** filters technical signals through the Analyst's "Bias Filter" and optimizes factor weights.
4.  **Audit:** **The Risk Manager** checks the proposed trades against current portfolio concentration and liquidity.
5.  **Execution:** Validated trades are flagged for the broker interface.

---

## 🚀 Getting Started

### Prerequisites
*   Python 3.9+
*   API Keys for market data and news feeds (e.g., AlphaVantage, NewsAPI)

### Installation
```bash
git clone https://github.com/your-repo/hedge-fund.git
cd hedge-fund
pip install -r requirements.txt
```

### Syncing Data
Before running strategies, ensure the local data store is up-to-date:
```bash
python quant_librarian/sync_today.py
```

---

## ⚖️ Disclaimer
This software is for research purposes only. Trading in financial markets involves significant risk of loss. The authors are not responsible for any financial losses incurred through the use of this system.
