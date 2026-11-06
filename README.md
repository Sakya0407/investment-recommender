# Investment Recommendation Application (Sri Lanka)

Final year project. The app asks a few questions, works out a risk profile, and suggests a mix of FD, gold, stocks and (if data allows) unit trusts using past Sri Lankan data.

## Step 1: collect the data (put CSV files in `data/raw/`)

| File | Columns | Where to get it |
|---|---|---|
| `fd_rates.csv` | `date`, `awfdr` (percent per year) | CBSL Data Library, monthly interest rates |
| `gold.csv` | `date`, `price_lkr` | CBSL gold price in LKR, or world gold price (USD) x USD/LKR rate |
| `aspi.csv` | `date`, `close` | ASPI month-end or daily values (CBSL daily economic indicators, CSE) |
| `unit_trust.csv` (optional) | `date`, `fund`, `category`, `nav` | UTASL monthly reports / fund manager websites |

Dates can be `2020-01-31` or `2020-01`. Use the same time range (about 2018 to 2025) for all files.

## Step 2: build the monthly table

    pip install pandas
    python src/build_dataset.py

This creates `data/processed/monthly_returns.csv`, `asset_summary.csv` and `correlation.csv`.

## Step 3: check the data before going further
- At least 4 to 5 years of monthly data for three or more assets.
- Look at asset_summary.csv: do the returns and risk look sensible (FD low risk, stocks high)?
- Write down the source and download date of every file (needed for the report).

## Next steps
1. Risk questionnaire and scoring rules (version 1).
2. Portfolio optimisation on the monthly returns (version 2).
3. Streamlit web app.
4. Backtest: compare suggested mixes with an FD-only plan.

Disclaimer: the app gives educational suggestions based on past data, not financial advice.
