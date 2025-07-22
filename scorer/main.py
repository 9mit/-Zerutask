import os
from scorer.pipeline import generate_ml_scores

if __name__ == '__main__':
    # =========================================================================
    # ▼▼▼ HIGHLIGHT: PROVIDE THE PATH TO YOUR JSON FILE HERE ▼▼▼
    # =========================================================================
    
    # Instructions:
    # 1. Place your large JSON data file into the 'data/' directory.
    # 2. Replace 'your_transactions_file.json' with the actual name of your file.
    
    YOUR_FILENAME = 'user-wallet-transactions.json' 

    # =========================================================================
    
    # This builds the full path to the file
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(project_root, 'data', YOUR_FILENAME)

    # Run the entire ML scoring pipeline
    scores = generate_ml_scores(file_path)

    # Print results in a readable format
    if scores:
        print("\n--- Machine Learning Based Credit Scores ---")
        sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        for address, score in sorted_scores:
            print(f"Wallet: {address:<42} -> Score: {score}")
        print("------------------------------------------")