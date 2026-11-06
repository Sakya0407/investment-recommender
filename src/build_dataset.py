"""
Build a monthly returns table for the investment recommendation project.

Put your downloaded files in data/raw/ (see README.md for the exact columns), then run:

    python src/build_dataset.py

Outputs (data/processed/):
    monthly_returns.csv   one row per month, one column per asset
    asset_summary.csv     annualised return, volatility and months of data per asset
    correlation.csv       correlation of monthly returns between assets
"""
from pathlib import Path
import pandas as pd

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
OUT = Path(__file__).resolve().parent.parent / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)


def month_end(series_dates):
    return pd.to_datetime(series_dates).dt.to_period("M").dt.to_timestamp("M")


def load_price_series(path, value_col):
    """Daily or monthly prices -> month-end price."""
    df = pd.read_csv(path)
    df["month"] = month_end(df["date"])
    df = df.sort_values("date")
    return df.groupby("month")[value_col].last()


def main():
    assets = {}

    # FD: AWFDR is a yearly percentage rate, so the monthly return is roughly rate / 12
    p = RAW / "fd_rates.csv"
    if p.exists():
        fd = pd.read_csv(p)
        fd["month"] = month_end(fd["date"])
        fd = fd.groupby("month")["awfdr"].last()
        assets["FD"] = fd / 100 / 12
    else:
        print("Missing data/raw/fd_rates.csv")

    # Gold: price in LKR (any consistent unit), daily or monthly
    p = RAW / "gold.csv"
    if p.exists():
        assets["Gold"] = load_price_series(p, "price_lkr").pct_change()
    else:
        print("Missing data/raw/gold.csv")

    # Stocks: ASPI closing value
    p = RAW / "aspi.csv"
    if p.exists():
        assets["Stocks_ASPI"] = load_price_series(p, "close").pct_change()
    else:
        print("Missing data/raw/aspi.csv")

    # Unit trusts (optional): date, fund, category, nav  -> equal-weight average per category
    p = RAW / "unit_trust.csv"
    if p.exists():
        ut = pd.read_csv(p)
        ut["month"] = month_end(ut["date"])
        ut = ut.sort_values("date").groupby(["category", "fund", "month"])["nav"].last().reset_index()
        ut["ret"] = ut.groupby(["category", "fund"])["nav"].pct_change()
        cat = ut.groupby(["category", "month"])["ret"].mean().unstack(0)
        for c in cat.columns:
            assets[f"UT_{c}"] = cat[c]
    else:
        print("No data/raw/unit_trust.csv (optional - add it later if you get enough history)")

    if not assets:
        raise SystemExit("No input files found in data/raw/")

    returns = pd.DataFrame(assets).sort_index().dropna(how="all")
    returns.to_csv(OUT / "monthly_returns.csv", index_label="month")

    summary = pd.DataFrame({
        "months_of_data": returns.count(),
        "first_month": returns.apply(lambda s: s.first_valid_index()),
        "last_month": returns.apply(lambda s: s.last_valid_index()),
        "annualised_return": returns.mean() * 12,
        "annualised_volatility": returns.std() * (12 ** 0.5),
    })
    summary.to_csv(OUT / "asset_summary.csv", index_label="asset")
    returns.corr().to_csv(OUT / "correlation.csv")

    num = ["annualised_return", "annualised_volatility"]
    summary[num] = summary[num].round(4)
    print(summary.to_string())
    print("\nSaved to", OUT)


if __name__ == "__main__":
    main()
