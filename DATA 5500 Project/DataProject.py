"""
Stock Market Trading Algorithm
==============================
Strategies: Mean Reversion, SMA Crossover, RSI (with trend filter)
"""

import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

# =============================================================================
# CONFIGURATION
# =============================================================================

LIVE_TRADING = False

# Alpaca Paper Trading API
ALPACA_API_KEY = "PKJSOXKR4ZYI3LJ4M2DZKN2FA3"
ALPACA_SECRET_KEY = "36qV6281N6KhziVNx2ndpqk5Ju9bMLgMCXNQkQSLvyhk"
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"  # "paper" in URL = paper trading
ALPACA_DATA_URL = "https://data.alpaca.markets"

# Trading parameters
START_DATE = "2020-01-01"
INITIAL_CAPITAL = 10000
POSITION_SIZE = 0.50

# Mean Reversion
MR_LOOKBACK, MR_Z_THRESHOLD, MR_STOP_LOSS, MR_TAKE_PROFIT = 25, 2.2, 0.05, 0.03

# SMA Crossover
SMA_SHORT, SMA_LONG, SMA_STOP_LOSS, SMA_TAKE_PROFIT = 10, 100, 0.04, 0.1

# RSI
RSI_PERIOD, RSI_OVERSOLD, RSI_OVERBOUGHT = 14, 45, 100
RSI_TREND_SMA, RSI_STOP_LOSS, RSI_TAKE_PROFIT = 150, 0.09, 0.2

# File paths
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
RESULTS_FILE = Path("results.json")

# Stocks
TICKERS = {
    "AAPL": "Tech", "NVDA": "Tech", "GOOG": "Tech", "META": "Tech",
    "FCX": "Materials", "GLD": "Materials", "SLV": "Materials",
    "CAT": "Industrials", "UPS": "Industrials", "LMT": "Industrials",
    "SPY": "ETF", "QQQ": "ETF",
    "AMD": "HighRisk", "PLTR": "HighRisk"
}

# =============================================================================
# DATA FUNCTIONS
# =============================================================================

def get_headers():
    return {"APCA-API-KEY-ID": ALPACA_API_KEY, "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY}


def fetch_from_api(symbol, start_date):
    url = f"{ALPACA_DATA_URL}/v2/stocks/{symbol}/bars"
    params = {
        "start": f"{start_date}T00:00:00Z",
        "end": f"{datetime.now().strftime('%Y-%m-%d')}T23:59:59Z",
        "timeframe": "1Day", "limit": 10000, "adjustment": "split"
    }
    
    try:
        resp = requests.get(url, headers=get_headers(), params=params)
        resp.raise_for_status()
        data = resp.json()
        
        if "bars" not in data or not data["bars"]:
            return None
        
        df = pd.DataFrame(data["bars"])
        df = df.rename(columns={"t": "Date", "o": "Open", "h": "High", 
                                "l": "Low", "c": "Close", "v": "Volume"})
        df["Date"] = pd.to_datetime(df["Date"])
        df.set_index("Date", inplace=True)
        df["Adj Close"] = df["Close"]
        return df
    except:
        return None


def get_stock_data(symbol):
    csv_path = DATA_DIR / f"{symbol}_historical.csv"
    
    if csv_path.exists():
        existing = pd.read_csv(csv_path, index_col="Date", parse_dates=True)
        start = (existing.index.max() + timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        existing = pd.DataFrame()
        start = START_DATE
    
    new_data = fetch_from_api(symbol, start)
    
    if new_data is not None and not new_data.empty:
        if not existing.empty:
            df = pd.concat([existing, new_data])
            df = df[~df.index.duplicated(keep='last')].sort_index()
        else:
            df = new_data
        df.to_csv(csv_path)
        print(f"Saved: {csv_path}")
        return df
    
    return existing if not existing.empty else None


# =============================================================================
# STRATEGIES
# =============================================================================

def run_mean_reversion(df):
    df = df.copy()
    price = df["Adj Close"]
    
    df["SMA"] = price.rolling(MR_LOOKBACK).mean()
    df["STD"] = price.rolling(MR_LOOKBACK).std()
    df["Z"] = (price - df["SMA"]) / df["STD"]
    
    capital, position, entry_price = INITIAL_CAPITAL, 0, 0
    trades, equity = [], [INITIAL_CAPITAL]
    last_signal = None
    
    for idx, row in df.iterrows():
        p, z = row["Adj Close"], row["Z"]
        if np.isnan(z):
            equity.append(equity[-1])
            continue
        
        if position != 0:
            pct = (p - entry_price) / entry_price if position > 0 else (entry_price - p) / entry_price
            if pct <= -MR_STOP_LOSS or pct >= MR_TAKE_PROFIT:
                profit = (p - entry_price) * position if position > 0 else (entry_price - p) * abs(position)
                capital += p * position if position > 0 else -p * abs(position)
                trades.append(profit)
                position, entry_price = 0, 0
        
        trade_size = int(capital * POSITION_SIZE / p)
        
        if position == 0 and trade_size > 0:
            if z < -MR_Z_THRESHOLD:
                capital -= p * trade_size
                position, entry_price = trade_size, p
                if idx == df.index[-1]: last_signal = "BUY"
            elif z > MR_Z_THRESHOLD:
                capital += p * trade_size
                position, entry_price = -trade_size, p
                if idx == df.index[-1]: last_signal = "SELL"
        elif position > 0 and z >= 0:
            profit = (p - entry_price) * position
            capital += p * position
            trades.append(profit)
            position = 0
        elif position < 0 and z <= 0:
            profit = (entry_price - p) * abs(position)
            capital -= p * abs(position)
            trades.append(profit)
            position = 0
        
        if position > 0:
            equity.append(capital + position * p)
        elif position < 0:
            equity.append(capital + (entry_price - p) * abs(position))
        else:
            equity.append(capital)
    
    final_p = price.iloc[-1]
    if position > 0:
        capital += final_p * position
        trades.append((final_p - entry_price) * position)
    elif position < 0:
        capital -= final_p * abs(position)
        trades.append((entry_price - final_p) * abs(position))
    
    return _calc_metrics(capital, price, equity, trades, last_signal)


def run_sma_crossover(df):
    df = df.copy()
    price = df["Adj Close"]
    
    df["SMA_S"] = price.rolling(SMA_SHORT).mean()
    df["SMA_L"] = price.rolling(SMA_LONG).mean()
    df["Signal"] = np.where(df["SMA_S"] > df["SMA_L"], 1, -1)
    df["Cross"] = df["Signal"].diff()
    
    capital, position, entry_price = INITIAL_CAPITAL, 0, 0
    trades, equity = [], [INITIAL_CAPITAL]
    last_signal = None
    
    for idx, row in df.iterrows():
        p, cross = row["Adj Close"], row["Cross"]
        if np.isnan(cross):
            equity.append(equity[-1])
            continue
        
        if position != 0:
            pct = (p - entry_price) / entry_price if position > 0 else (entry_price - p) / entry_price
            if pct <= -SMA_STOP_LOSS or pct >= SMA_TAKE_PROFIT:
                profit = (p - entry_price) * position if position > 0 else (entry_price - p) * abs(position)
                capital += p * position if position > 0 else -p * abs(position)
                trades.append(profit)
                position, entry_price = 0, 0
        
        trade_size = int(INITIAL_CAPITAL * POSITION_SIZE / p)
        
        if cross == 2:
            if position < 0:
                profit = (entry_price - p) * abs(position)
                capital -= p * abs(position)
                trades.append(profit)
                position = 0
            if position == 0 and trade_size > 0:
                capital -= p * trade_size
                position, entry_price = trade_size, p
                if idx == df.index[-1]: last_signal = "BUY"
        elif cross == -2:
            if position > 0:
                profit = (p - entry_price) * position
                capital += p * position
                trades.append(profit)
                position = 0
            if position == 0 and trade_size > 0:
                capital += p * trade_size
                position, entry_price = -trade_size, p
                if idx == df.index[-1]: last_signal = "SELL"
        
        if position > 0:
            equity.append(capital + position * p)
        elif position < 0:
            equity.append(capital + (entry_price - p) * abs(position))
        else:
            equity.append(capital)
    
    final_p = price.iloc[-1]
    if position > 0:
        capital += final_p * position
        trades.append((final_p - entry_price) * position)
    elif position < 0:
        capital -= final_p * abs(position)
        trades.append((entry_price - final_p) * abs(position))
    
    return _calc_metrics(capital, price, equity, trades, last_signal)


def run_rsi_strategy(df):
    df = df.copy()
    price = df["Adj Close"]
    
    delta = price.diff()
    gain = delta.where(delta > 0, 0).rolling(RSI_PERIOD).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(RSI_PERIOD).mean()
    df["RSI"] = 100 - (100 / (1 + gain / loss))
    df["Trend"] = price.rolling(RSI_TREND_SMA).mean()
    df["Uptrend"] = price > df["Trend"]
    
    capital, position, entry_price = INITIAL_CAPITAL, 0, 0
    trades, equity = [], [INITIAL_CAPITAL]
    last_signal = None
    
    for idx, row in df.iterrows():
        p, rsi, uptrend = row["Adj Close"], row["RSI"], row["Uptrend"]
        if np.isnan(rsi):
            equity.append(equity[-1])
            continue
        
        if position > 0:
            pct = (p - entry_price) / entry_price
            if pct <= -RSI_STOP_LOSS or pct >= RSI_TAKE_PROFIT or rsi > RSI_OVERBOUGHT:
                profit = (p - entry_price) * position
                capital += p * position
                trades.append(profit)
                position, entry_price = 0, 0
        
        if position == 0:
            trade_size = int(capital * POSITION_SIZE / p)
            if rsi < RSI_OVERSOLD and uptrend and trade_size > 0:
                capital -= p * trade_size
                position, entry_price = trade_size, p
                if idx == df.index[-1]: last_signal = "BUY"
        
        equity.append(capital + position * p if position > 0 else capital)
    
    final_p = price.iloc[-1]
    if position > 0:
        capital += final_p * position
        trades.append((final_p - entry_price) * position)
    
    return _calc_metrics(capital, price, equity, trades, last_signal)


def _calc_metrics(capital, price, equity, trades, last_signal):
    profit = capital - INITIAL_CAPITAL
    bh_profit = (price.iloc[-1] / price.iloc[0] * INITIAL_CAPITAL) - INITIAL_CAPITAL
    
    returns = pd.Series(equity).pct_change().dropna()
    sharpe = (returns.mean() / returns.std() * np.sqrt(252)) if len(returns) > 0 and returns.std() != 0 else 0
    win_rate = sum(1 for t in trades if t > 0) / len(trades) if trades else 0
    
    return {
        "profit": round(profit, 2),
        "bh_profit": round(bh_profit, 2),
        "sharpe": round(sharpe, 2),
        "win_rate": round(win_rate, 2),
        "num_trades": len(trades),
        "signal": last_signal
    }


# =============================================================================
# PAPER TRADING
# =============================================================================

def submit_order(symbol, side, qty=1):
    if not LIVE_TRADING:
        print(f"[TEST MODE] Would {side} {qty} {symbol}")
        return None
    
    url = f"{ALPACA_BASE_URL}/v2/orders"
    order = {"symbol": symbol, "qty": str(qty), "side": side, 
             "type": "market", "time_in_force": "day"}
    
    try:
        resp = requests.post(url, headers=get_headers(), json=order)
        resp.raise_for_status()
        print(f"Order submitted: {side.upper()} {qty} {symbol}")
        return resp.json()
    except Exception as e:
        print(f"Order failed: {e}")
        return None


def get_account():
    try:
        resp = requests.get(f"{ALPACA_BASE_URL}/v2/account", headers=get_headers())
        resp.raise_for_status()
        return resp.json()
    except:
        return None


# =============================================================================
# RESULTS
# =============================================================================

def save_results(results, best_stock, best_strategy, best_profit):
    output = {
        "timestamp": datetime.now().isoformat(),
        "best_performer": {"stock": best_stock, "strategy": best_strategy, "profit": best_profit},
        "summary": {
            strategy: {
                "total_profit": sum(r["profit"] for r in results if r["strategy"] == strategy),
                "avg_sharpe": round(np.mean([r["sharpe"] for r in results if r["strategy"] == strategy]), 2)
            }
            for strategy in ["Mean Reversion", "SMA Crossover", "RSI"]
        },
        "all_results": results
    }
    
    with open(RESULTS_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Saved: {RESULTS_FILE}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 60)
    print("STOCK TRADING ALGORITHM")
    print(f"Run Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    strategies = {
        "Mean Reversion": run_mean_reversion,
        "SMA Crossover": run_sma_crossover,
        "RSI": run_rsi_strategy
    }
    
    all_results = []
    signals = []
    
    # Process stocks
    print(f"\nLoading data for {len(TICKERS)} stocks...")
    print("-" * 40)
    
    for symbol, sector in TICKERS.items():
        df = get_stock_data(symbol)
        if df is None or df.empty:
            continue
        
        for name, func in strategies.items():
            try:
                result = func(df)
                result.update({"symbol": symbol, "sector": sector, "strategy": name})
                all_results.append(result)
                
                if result["signal"]:
                    signals.append({"symbol": symbol, "strategy": name, "signal": result["signal"]})
            except:
                pass
    
    # Trading signals
    if signals:
        print("\n" + "=" * 60)
        print("TRADING SIGNALS FOR TODAY")
        print("=" * 60)
        for s in signals:
            print(f"You should {s['signal']} {s['symbol']} today ({s['strategy']})")
            submit_order(s['symbol'], s['signal'].lower())
    else:
        print("\nNo trading signals for today")
    
    # Results
    if all_results:
        df_results = pd.DataFrame(all_results)
        best = max(all_results, key=lambda x: x["profit"])
        
        # Best performer
        print("\n" + "=" * 60)
        print("BEST PERFORMER")
        print("=" * 60)
        print(f"Stock: {best['symbol']}")
        print(f"Strategy: {best['strategy']}")
        print(f"Profit: ${best['profit']:,.2f}")
        
        # Summary by strategy
        print("\n" + "=" * 60)
        print("SUMMARY BY STRATEGY")
        print("=" * 60)
        strategy_summary = df_results.groupby("strategy").agg({
            "profit": "sum",
            "bh_profit": "sum",
            "sharpe": "mean",
            "win_rate": "mean",
            "num_trades": "sum"
        }).round(2)
        strategy_summary.columns = ["Profit", "Buy&Hold", "Avg Sharpe", "Avg Win Rate", "Trades"]
        print(strategy_summary.to_string())
        
        # Summary by sector
        print("\n" + "=" * 60)
        print("SUMMARY BY SECTOR")
        print("=" * 60)
        sector_summary = df_results.groupby("sector").agg({
            "profit": "sum",
            "bh_profit": "sum",
            "sharpe": "mean",
            "win_rate": "mean"
        }).sort_values("profit", ascending=False).round(2)
        sector_summary.columns = ["Profit", "Buy&Hold", "Avg Sharpe", "Avg Win Rate"]
        print(sector_summary.to_string())
        
        # Save results
        print("\n" + "-" * 40)
        save_results(all_results, best["symbol"], best["strategy"], best["profit"])
    
    print("\nCOMPLETE")


if __name__ == "__main__":
    main()