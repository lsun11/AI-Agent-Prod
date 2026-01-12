import yfinance as yf
from typing import Dict, Any


class StockService:
    def __init__(self):
        # Simple in-memory cache: { "SPY": { "data": {...}, "expires": 1709... } }
        self._cache: Dict[str, Dict[str, Any]] = {}

        # ✅ CACHE DURATION: Only fetch new data from Yahoo every 15 seconds
        self.CACHE_TTL = 15

    def get_stock_data(self, ticker: str) -> Dict[str, Any]:
        """
        Fetches real-time data for a single ticker using Yahoo Finance.
        """
        try:
            # 1. Fetch Ticker
            stock = yf.Ticker(ticker)

            # 2. Get Fast Info (Real-time price)
            # 'fast_info' is often faster than .history() for current price
            current_price = stock.fast_info.last_price
            prev_close = stock.fast_info.previous_close

            if not current_price:
                # Fallback to history if fast_info fails
                hist = stock.history(period="1d")
                if not hist.empty:
                    current_price = hist["Close"].iloc[-1]
                else:
                    return self._get_mock_error_data(ticker)

            # 3. Calculate Change
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100

            return {
                "symbol": ticker.upper(),
                "price": round(current_price, 2),
                "change": round(change, 2),
                "percent": round(change_percent, 2),
                "currency": stock.fast_info.currency,
                "market_cap": stock.fast_info.market_cap
            }

        except Exception as e:
            print(f"[StockService] Error fetching {ticker}: {e}")
            return self._get_mock_error_data(ticker)

    def get_stock_history(self, ticker: str, range_key: str) -> Dict[str, Any]:
        """
        Fetches historical candle data for the chart.
        """
        ticker = ticker.upper()

        # Map UI Range -> YFinance Parameters
        # 1D = 1 day history, 5 min interval
        # 1W = 5 day history, 15 min interval
        # 1M = 1 month history, 1 day interval (or 60m)
        # 1Y = 1 year history, 1 day interval
        params = {
            "1D": {"period": "1d", "interval": "5m"},
            "1W": {"period": "5d", "interval": "15m"},
            "1M": {"period": "1mo", "interval": "1d"},
            "6M": {"period": "6mo", "interval": "1d"},
            "1Y": {"period": "1y", "interval": "1d"},
        }

        # Default to 1D if unknown
        p = params.get(range_key, params["1D"])

        try:
            print(f"[Stock] 📈 Fetching history for {ticker} ({range_key})...")
            stock = yf.Ticker(ticker)

            # Fetch DataFrame
            hist = stock.history(period=p["period"], interval=p["interval"])

            if hist.empty:
                return {"symbol": ticker, "history": []}

            # Convert DataFrame to List of Dicts
            # Reset index to get 'Date' or 'Datetime' as a column
            hist = hist.reset_index()

            history_data = []
            for _, row in hist.iterrows():
                # YFinance Date column name varies (Date vs Datetime)
                date_val = row.get("Datetime") or row.get("Date")

                # Convert to JS timestamp (milliseconds)
                ts = int(date_val.timestamp() * 1000)

                history_data.append({
                    "time": ts,
                    "price": round(row["Close"], 2),
                    "vol": int(row["Volume"])
                })

            return {
                "symbol": ticker,
                "range": range_key,
                "history": history_data
            }

        except Exception as e:
            print(f"[StockService] History error {ticker}: {e}")
            return {"symbol": ticker, "history": []}


    def _get_mock_error_data(self, ticker: str):
        """Fallback only if API fails completely."""
        return {
            "symbol": ticker.upper(),
            "price": 0.00,
            "change": 0.00,
            "percent": 0.00,
            "error": "Data Unavailable"
        }