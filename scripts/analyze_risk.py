import pandas as pd
import numpy as np
from datetime import datetime
import os

# --- Configuration ---
INPUT_CSV_PATH = os.path.join('data', 'output', 'wallet_transactions.csv')
OUTPUT_CSV_PATH = os.path.join('data', 'output', 'risk_scores.csv')

def calculate_features(df):
    """Calculates risk features for each wallet."""
    print("Calculating risk features for each wallet...")
    df['timestamp'] = pd.to_numeric(df['timestamp'])
    wallets = df.groupby('wallet_id')

    features = []
    for wallet_id, group in wallets:
        # Features
        liquidation_count = (group['type'] == 'liquidation').sum()
        interaction_count = len(group)
        first_tx_timestamp = group['timestamp'].min()
        wallet_age_days = (datetime.now().timestamp() - first_tx_timestamp) / 86400
        unique_assets_supplied = group['symbol'].nunique()
        borrow_count = (group['type'] == 'borrow').sum()
        repay_count = (group['type'] == 'repay').sum()
        borrow_to_repay_ratio = borrow_count / repay_count if repay_count > 0 else borrow_count * 2

        features.append({
            'wallet_id': wallet_id,
            'liquidation_count': liquidation_count,
            'interaction_count': interaction_count,
            'wallet_age_days': wallet_age_days,
            'unique_assets_supplied': unique_assets_supplied,
            'borrow_to_repay_ratio': borrow_to_repay_ratio
        })
    return pd.DataFrame(features)

def normalize_features(df):
    """Normalizes features using Min-Max scaling."""
    print("Normalizing features...")
    for column in df.columns[1:]:
        min_val, max_val = df[column].min(), df[column].max()
        if max_val - min_val > 0:
            df[column] = (df[column] - min_val) / (max_val - min_val)
        else:
            df[column] = 0
    return df

def calculate_risk_score(df):
    """Applies weighted scoring logic."""
    print("Applying scoring logic...")
    weights = {
        'liquidation_count': 0.50, 'borrow_to_repay_ratio': 0.20,
        'wallet_age_days': 0.15, 'unique_assets_supplied': 0.10,
        'interaction_count': 0.05
    }

    df['score'] = (
        df['liquidation_count'] * weights['liquidation_count'] +
        df['borrow_to_repay_ratio'] * weights['borrow_to_repay_ratio'] +
        (1 - df['wallet_age_days']) * weights['wallet_age_days'] +
        (1 - df['unique_assets_supplied']) * weights['unique_assets_supplied'] +
        (1 - df['interaction_count']) * weights['interaction_count']
    )
    df['score'] = (df['score'] * 1000).round().astype(int)
    return df[['wallet_id', 'score']]

def main():
    """Main function to run the analysis pipeline."""
    try:
        transactions_df = pd.read_csv(INPUT_CSV_PATH)
    except FileNotFoundError:
        print(f"Error: '{INPUT_CSV_PATH}' not found. Run fetch_data.py first.")
        return

    if transactions_df.empty:
        print("Transaction file is empty. No scores to generate.")
        return

    feature_df = calculate_features(transactions_df)
    normalized_df = normalize_features(feature_df.copy())
    final_scores_df = calculate_risk_score(normalized_df)

    final_scores_df.to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"\n✅ Analysis complete! Final scores saved to '{OUTPUT_CSV_PATH}'.")

if __name__ == '__main__':
    main()