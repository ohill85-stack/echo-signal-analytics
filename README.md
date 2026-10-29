# ECHO Signal Analytics

A Python + SQL pipeline that scores my trading scanner's signals against the S&P 500 to find out which setups actually have an edge.

## Why
My scanner (ECHO) flags Fibonacci and breakout setups and sends me alerts.  . I wanted proof of what works, not gut feel.

 ## What it does
1. Loads the scanner's signal history into SQLite
2. Validates every logged price against that day's real trading range
3. Removes duplicate alerts (keeps the first signal per ticker per day)
4. Measures each signal's 5-trading-day return vs. SPY over the same window
5. Reports average return, edge vs. SPY, and how often signals beat SPY, by conviction level and scanner type
6. Lists the 3 best and 3 worst signals by edge

## What I found
- Validation exposed bad early test data (prices outside the day's real range, signals dated on a Saturday). Those rows had made high-conviction signals look like +35% winners. With clean data, that edge disappeared.
- Breakout signals beat SPY in 5 of 6 trades (+2.0% average edge). Fibonacci "Standard" signals lagged SPY.
- Sample sizes are still small. The whole analysis re-runs with one command as new signals come in.

## Skills
Python, SQL (GROUP BY, CASE WHEN, subqueries, views), SQLite, pandas, yfinance, data validation

## Run it
    pip install yfinance
    python pipeline.py

Signal data is not included; the pipeline expects a `signal_history.json` export from the scanner.

*Personal project for learning. Not financial advice.*