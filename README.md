# Customer Segmentation Using RFM Analysis

This repository contains a small Python implementation for customer segmentation via RFM (Recency, Frequency, Monetary) analysis.

## What is included
- A reusable implementation of RFM scoring in [src/rfm_analysis.py](src/rfm_analysis.py)
- A regression test covering the expected output shape in [tests/test_rfm_analysis.py](tests/test_rfm_analysis.py)
- A minimal dependency list in [requirements.txt](requirements.txt)

## How to run
1. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
2. Run the tests:
   ```bash
   python -m pytest -q
   ```

The analysis expects a CSV file with at least these columns:
- CustomerID
- InvoiceDate
- Revenue
