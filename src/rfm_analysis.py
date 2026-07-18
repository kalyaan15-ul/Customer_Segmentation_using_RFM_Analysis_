from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_transactions(path: str | Path) -> pd.DataFrame:
    """Load transaction data from CSV or Excel and prepare common columns."""
    file_path = Path(path)
    suffix = file_path.suffix.lower()

    if suffix == ".csv":
        transactions = pd.read_csv(file_path)
    elif suffix in {".xlsx", ".xls"}:
        transactions = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {suffix or 'unknown'}")

    required_columns = {"CustomerID", "InvoiceDate"}
    missing = required_columns.difference(transactions.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    transactions = transactions.copy()
    transactions["InvoiceDate"] = pd.to_datetime(transactions["InvoiceDate"], errors="coerce")
    transactions = transactions.dropna(subset=["InvoiceDate"])

    if "Revenue" not in transactions.columns:
        if {"Quantity", "UnitPrice"}.issubset(transactions.columns):
            transactions["Revenue"] = transactions["Quantity"] * transactions["UnitPrice"]
        else:
            raise ValueError("Missing Revenue column and cannot infer it from Quantity/UnitPrice")

    transactions["Revenue"] = pd.to_numeric(transactions["Revenue"], errors="coerce")
    transactions = transactions.dropna(subset=["Revenue"])
    transactions = transactions.sort_values(["CustomerID", "InvoiceDate"])
    return transactions.reset_index(drop=True)


def compute_rfm_segments(transactions: pd.DataFrame, snapshot_date: str | pd.Timestamp | None = None) -> pd.DataFrame:
    """Compute RFM metrics and assign customer segments."""
    if snapshot_date is None:
        snapshot_date = pd.Timestamp.today().normalize()
    snapshot_date = pd.Timestamp(snapshot_date).normalize()

    if transactions.empty:
        return pd.DataFrame(columns=["CustomerID", "Recency", "Frequency", "Monetary", "R_Score", "F_Score", "M_Score", "Segment"])

    customer_metrics = (
        transactions.groupby("CustomerID")
        .agg(
            LastPurchaseDate=("InvoiceDate", "max"),
            Frequency=("InvoiceDate", "size"),
            Monetary=("Revenue", "sum"),
        )
        .reset_index()
    )

    customer_metrics["Recency"] = (snapshot_date - customer_metrics["LastPurchaseDate"]).dt.days
    customer_metrics["Monetary"] = customer_metrics["Monetary"].astype(float)

    def _score_series(series: pd.Series, ascending: bool = True) -> pd.Series:
        ranked = series.rank(method="first")
        if len(series) < 4:
            return pd.Series([4 if ascending else 1] * len(series), index=series.index, dtype=int)
        quantiles = pd.qcut(ranked, q=4, labels=[4, 3, 2, 1] if ascending else [1, 2, 3, 4])
        return quantiles.astype(int)

    customer_metrics["R_Score"] = _score_series(customer_metrics["Recency"], ascending=False)
    customer_metrics["F_Score"] = _score_series(customer_metrics["Frequency"], ascending=True)
    customer_metrics["M_Score"] = _score_series(customer_metrics["Monetary"], ascending=True)

    customer_metrics["Segment"] = (
        customer_metrics["R_Score"].astype(str)
        + customer_metrics["F_Score"].astype(str)
        + customer_metrics["M_Score"].astype(str)
    )

    return customer_metrics[["CustomerID", "Recency", "Frequency", "Monetary", "R_Score", "F_Score", "M_Score", "Segment"]]
