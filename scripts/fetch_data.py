import requests
import csv
import time
import os

# --- Configuration ---
# The API endpoint for the official Compound V2 subgraph
SUBGRAPH_URL = 'https://api.thegraph.com/subgraphs/name/graphprotocol/compound-v2'
# Path to the input file containing wallet addresses
WALLET_FILE_PATH = os.path.join('data', 'input', 'wallets.txt')
# Path to the output CSV file
OUTPUT_CSV_PATH = os.path.join('data', 'output', 'wallet_transactions.csv')

# --- GraphQL Query ---
# Fetches borrow, repay, and liquidation history for a wallet
QUERY = """
query getWalletHistory($wallet_id: ID!) {
  account(id: $wallet_id) {
    id
    borrows(first: 1000, orderBy: timestamp, orderDirection: desc) {
      id
      amount
      timestamp
      underlyingSymbol
    }
    repays(first: 1000, orderBy: timestamp, orderDirection: desc) {
      id
      amount
      timestamp
      underlyingSymbol
    }
    liquidations(first: 100, orderBy: timestamp, orderDirection: desc) {
      id
      amount
      timestamp
      underlyingSymbol
    }
  }
}
"""

def fetch_wallet_data(wallet_address):
    """Fetches data for a single wallet address from The Graph."""
    variables = {'wallet_id': wallet_address.lower()}
    try:
        response = requests.post(SUBGRAPH_URL, json={'query': QUERY, 'variables': variables})
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {wallet_address}: {e}")
        return None

def main():
    """Main function to read wallets, fetch data, and write to CSV."""
    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_CSV_PATH), exist_ok=True)

    # Prepare the CSV file
    csv_headers = ['wallet_id', 'transaction_id', 'type', 'amount', 'symbol', 'timestamp']
    with open(OUTPUT_CSV_PATH, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)

    print(f"Reading wallet addresses from {WALLET_FILE_PATH}...")
    try:
        with open(WALLET_FILE_PATH, 'r') as f:
            wallet_addresses = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: {WALLET_FILE_PATH} not found. Please create it and add wallet addresses.")
        return

    print(f"Found {len(wallet_addresses)} wallets. Starting data fetch...")

    # Process each wallet
    for i, address in enumerate(wallet_addresses):
        print(f"({i+1}/{len(wallet_addresses)}) Fetching data for: {address}")
        data = fetch_wallet_data(address)

        if data and 'data' in data and data['data']['account']:
            account_data = data['data']['account']
            all_transactions = []

            # Combine borrows, repays, and liquidations
            for tx_type in ['borrows', 'repays', 'liquidations']:
                if account_data.get(tx_type):
                    for tx in account_data[tx_type]:
                        all_transactions.append({
                            'wallet_id': address,
                            'transaction_id': tx['id'],
                            'type': tx_type[:-1],
                            'amount': tx['amount'],
                            'symbol': tx['underlyingSymbol'],
                            'timestamp': tx['timestamp']
                        })
            
            # Append transactions to CSV
            with open(OUTPUT_CSV_PATH, 'a', newline='') as f:
                writer = csv.writer(f)
                for tx in all_transactions:
                    writer.writerow(tx.values())
        else:
            print(f"No data found or error for wallet: {address}")

        time.sleep(0.5) # Be polite to the API

    print(f"\n✅ Data fetch complete! All data saved to {OUTPUT_CSV_PATH}")

if __name__ == '__main__':
    main()