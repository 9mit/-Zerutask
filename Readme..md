# Wallet Risk Scoring From Scratch

This project analyzes transaction data from the Compound V2 protocol to assign a risk score (from 0 to 1000) to a given list of wallet addresses.

## How to Run

1.  **Setup Environment:** Install the required Python libraries.
    ```bash
    pip install -r requirements.txt
    ```

2.  **Add Wallets:** Place the wallet addresses to be analyzed in `data/input/wallets.txt`, with one address per line.

3.  **Fetch Data:** Run the data fetching script. This will query The Graph and create `data/output/wallet_transactions.csv`.
    ```bash
    python scripts/fetch_data.py
    ```

4.  **Analyze and Score:** Run the analysis script. This will process the downloaded data and generate the final `data/output/risk_scores.csv` file.
    ```bash
    python scripts/analyze_risk.py
    ```

---

## Methodology

### Data Collection Method

Transaction data for each wallet was retrieved from the **Compound V2 subgraph** using **The Graph** protocol. A Python script sends GraphQL queries to fetch all borrow, repay, and liquidation events associated with each wallet address. This method is efficient as it provides structured, pre-indexed data directly from the protocol's event logs.

### Feature Selection Rationale

The raw transaction data was aggregated into five key features for each wallet, chosen to reflect its financial health and behavior on the lending protocol:

1.  **`liquidation_count`**: The total number of times a wallet has been liquidated. This is the most direct indicator of past high-risk behavior and failure to manage debt.
2.  **`borrow_to_repay_ratio`**: The ratio of borrow transactions to repay transactions. A high ratio suggests a user is accumulating debt faster than they are paying it back.
3.  **`wallet_age_days`**: The time elapsed since the wallet's first recorded transaction on the protocol. A newer wallet is considered riskier due to a lack of historical data.
4.  **`unique_assets_supplied`**: The number of different asset types supplied as collateral. Low diversification is riskier, as a price drop in a single asset can more easily trigger a liquidation.
5.  **`interaction_count`**: The total number of transactions. Very low activity might indicate a "set-and-forget" approach, which is risky in volatile markets.

### Scoring Method

A weighted scoring model was developed to combine the features into a single risk score.

1.  **Normalization:** All features were normalized to a common scale of 0 to 1 using **Min-Max Scaling**. This ensures that each feature contributes fairly to the final score, regardless of its original scale. For features where a lower value indicates higher risk (e.g., wallet age), the normalized score was inverted (`1 - score`).

2.  **Scoring Logic:** The final risk score is a weighted sum of the normalized features. The weights are assigned based on the perceived importance of each risk indicator:

    * `liquidation_count`: **50%**
    * `borrow_to_repay_ratio`: **20%**
    * `wallet_age_days` (inverted): **15%**
    * `unique_assets_supplied` (inverted): **10%**
    * `interaction_count` (inverted): **5%**

    The resulting score (between 0 and 1) is then scaled to the required **0 to 1000** range.