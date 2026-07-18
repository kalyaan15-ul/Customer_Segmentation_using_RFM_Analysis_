import pandas as pd

from src.rfm_analysis import compute_rfm_segments, load_transactions


def test_compute_rfm_segments_returns_expected_columns(tmp_path):
    csv_path = tmp_path / "transactions.csv"
    pd.DataFrame(
        {
            "CustomerID": [1, 1, 2, 2, 2, 3],
            "InvoiceDate": [
                "2024-01-01",
                "2024-01-15",
                "2024-02-01",
                "2024-02-20",
                "2024-03-05",
                "2024-03-10",
            ],
            "Revenue": [10, 15, 20, 25, 30, 5],
        }
    ).to_csv(csv_path, index=False)

    transactions = load_transactions(csv_path)
    rfm = compute_rfm_segments(transactions, snapshot_date="2024-03-20")

    assert set(["CustomerID", "Recency", "Frequency", "Monetary", "R_Score", "F_Score", "M_Score", "Segment"]).issubset(rfm.columns)
    assert not rfm.empty
    assert rfm["Segment"].notna().all()


def test_load_transactions_infers_revenue_from_unit_price_and_quantity(tmp_path):
    excel_path = tmp_path / "online_retail.xlsx"
    pd.DataFrame(
        {
            "CustomerID": [1, 1, 2],
            "InvoiceDate": ["2024-01-01", "2024-01-10", "2024-02-01"],
            "UnitPrice": [2.0, 3.0, 4.0],
            "Quantity": [3, 2, 1],
        }
    ).to_excel(excel_path, index=False)

    transactions = load_transactions(excel_path)

    assert transactions["Revenue"].tolist() == [6.0, 6.0, 4.0]
