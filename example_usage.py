from pathlib import Path

from src.rfm_analysis import compute_rfm_segments, load_transactions

if __name__ == "__main__":
    sample_data = Path("sample_transactions.csv")
    if sample_data.exists():
        transactions = load_transactions(sample_data)
        result = compute_rfm_segments(transactions, snapshot_date="2024-03-20")
        print(result.head())
    else:
        print("Sample data file not found. Add sample_transactions.csv to run this example.")
