import json
import pandas as pd
from datetime import datetime
import xgboost as xgb
import numpy as np
from collections import defaultdict

def generate_ml_scores(transactions_file: str) -> dict:
    """
    Develops a machine learning model to score wallets based on transaction history.

    Args:
        transactions_file: Path to the JSON file of user transactions.

    Returns:
        A dictionary mapping wallet addresses to a credit score (0-1000).
    """
    try:
        with open(transactions_file, 'r', encoding='utf-8') as f:
            raw_transactions_list = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {transactions_file} was not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {transactions_file}. Check file format.")
        return {}

    # --- FIX #1: Change the key used to identify the wallet address ---
    address_key = 'userWallet' # Changed from 'wallet_address' to 'userWallet'

    all_transactions = defaultdict(list)
    for tx in raw_transactions_list:
        if address_key in tx:
            all_transactions[tx[address_key]].append(tx)
        else:
            print(f"Warning: Transaction missing '{address_key}' key. Skipping: {tx}")
    
    # 1. Feature Engineering
    features_list = []
    for address, transactions in all_transactions.items():
        if not transactions: continue

        # --- FIX #2: Adapt to the nested data structure and data types ---
        # The script now correctly handles nested 'actionData' and converts string amounts/prices to numbers.

        # Helper function to safely extract and convert nested data
        def get_amount_usd(tx):
            action_data = tx.get('actionData', {})
            # LiquidationCall might have a different structure
            if tx.get('action') == 'liquidationcall':
                collateral_amount = float(action_data.get('collateralAmount', 0))
                collateral_price = float(action_data.get('collateralAssetPriceUSD', 0))
                return collateral_amount * collateral_price

            amount = float(action_data.get('amount', 0))
            price_usd = float(action_data.get('assetPriceUSD', 0))
            return amount * price_usd

        def get_action_type(tx):
            return tx.get('action') # The action type is at the top level

        deposits = [tx for tx in transactions if get_action_type(tx) == 'deposit']
        borrows = [tx for tx in transactions if get_action_type(tx) == 'borrow']
        repays = [tx for tx in transactions if get_action_type(tx) == 'repay']
        redeems = [tx for tx in transactions if get_action_type(tx) == 'redeemunderlying']
        liquidations = [tx for tx in transactions if get_action_type(tx) == 'liquidationcall']

        total_deposited = sum(get_amount_usd(d) for d in deposits)
        total_redeemed = sum(get_amount_usd(r) for r in redeems)
        total_borrowed = sum(get_amount_usd(b) for b in borrows)
        total_repaid = sum(get_amount_usd(r) for r in repays)

        repayment_ratio = min(total_repaid / total_borrowed, 1.0) if total_borrowed > 0 else 1.0
        net_collateral = total_deposited - total_redeemed
        net_debt = total_borrowed - total_repaid
        current_debt_ratio = net_debt / net_collateral if net_collateral > 0 else float('inf')

        # Use the top-level 'timestamp' which is an integer (epoch time)
        timestamps = [t['timestamp'] for t in transactions]
        wallet_age_days = (datetime.now().timestamp() - min(timestamps)) / (60 * 60 * 24) if timestamps else 0
        transaction_frequency = len(transactions) / wallet_age_days if wallet_age_days > 0 else 0
        
        is_risky = 1 if len(liquidations) > 0 else 0
        
        features_list.append({
            'wallet_address': address,
            'total_borrowed_usd': total_borrowed,
            'repayment_ratio': repayment_ratio,
            'current_debt_ratio': current_debt_ratio,
            'max_borrow_size': max([get_amount_usd(b) for b in borrows] or [0]),
            'wallet_age_days': wallet_age_days,
            'transaction_frequency': transaction_frequency,
            'has_borrowed': 1 if total_borrowed > 0 else 0,
            'is_risky': is_risky
        })

    if not features_list: return {}

    # 2. Data Preparation for ML
    df = pd.DataFrame(features_list)
    df.replace([np.inf, -np.inf], 99999, inplace=True) # Handle infinities

    train_df = df[df['has_borrowed'] == 1].copy()

    if len(train_df) < 10 or len(train_df['is_risky'].unique()) < 2:
        print("Warning: Not enough diverse data to train a model. Returning rule-based scores.")
        scores = {}
        for _, row in df.iterrows():
            if not row['has_borrowed']:
                scores[row['wallet_address']] = 750
            else:
                score = (row['repayment_ratio'] * 800) + (100 if not row['is_risky'] else 0)
                scores[row['wallet_address']] = int(min(score, 1000))
        return scores

    feature_names = [
        'total_borrowed_usd', 'repayment_ratio', 'current_debt_ratio',
        'max_borrow_size', 'wallet_age_days', 'transaction_frequency'
    ]
    X_train = train_df[feature_names]
    y_train = train_df['is_risky']

    # 3. Model Training
    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', objective='binary:logistic')
    model.fit(X_train, y_train)

    # 4. Scoring All Wallets
    all_wallets_features = df[feature_names]
    risk_probabilities = model.predict_proba(all_wallets_features)[:, 1]
    df['credit_score'] = (1 - risk_probabilities) * 1000

    final_scores = {}
    for _, row in df.iterrows():
        if not row['has_borrowed']:
            final_scores[row['wallet_address']] = 750
        else:
            final_scores[row['wallet_address']] = int(row['credit_score'])

    return final_scores