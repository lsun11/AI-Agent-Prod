from fastapi import APIRouter, HTTPException
from src.stock_app.service import StockService

router = APIRouter()
service = StockService()


@router.get("/stock/{ticker}")
async def get_stock(ticker: str):
    """
    Endpoint to fetch live stock data.
    Usage: GET /api/stock/SPY
    """
    data = service.get_stock_data(ticker)

    # If the service returns an explicit error key (from our mock fallback)
    if "error" in data and data["error"] != "Data Unavailable":
        raise HTTPException(status_code=500, detail=data["error"])

    return data


@router.get("/stock/{ticker}/history")
async def get_stock_history(ticker: str, range: str = "1D"):
    """
    Get chart data.
    Usage: /api/stock/SPY/history?range=1W
    """
    return service.get_stock_history(ticker, range)