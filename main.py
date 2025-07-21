from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, date
import pandas as pd
import yfinance as yf
from typing import Optional
import uvicorn

app = FastAPI(
    title="Investment Simulator API",
    description="API for simulating stock investment strategies",
    version="1.0.0"
)

class InvestmentRequest(BaseModel):
    ticker: str
    start_date: date
    end_date: date
    monthly_investment_amount: float
    starting_amount: float
    day_of_investment: int

class InvestmentResponse(BaseModel):
    ticker: str
    total_invested_amount: float
    final_investment_value: float
    total_return: float
    percentage_return: float
    cagr: float
    num_months: int
    simulation_data: Optional[dict] = None

def simulate_investment(
    ticker: str,
    start_date: date,
    end_date: date,
    monthly_investment_amount: float,
    starting_amount: float,
    day_of_investment: int
):
    """Core investment simulation logic extracted from Streamlit app"""
    try:
        # Download stock data
        stock_data = yf.download(ticker, start=pd.to_datetime(start_date) - pd.Timedelta(days=7), end=end_date)
        
        if stock_data.empty:
            raise ValueError(f"No data found for ticker {ticker}")
        
        # Prepare data
        stock_data = stock_data[['Close']].round(2)
        date_range = pd.date_range(start=pd.to_datetime(start_date) - pd.Timedelta(days=7), end=end_date)
        stock_data = stock_data.reindex(date_range)
        stock_data.fillna(method='ffill', inplace=True)
        stock_data = stock_data[(stock_data.index >= pd.to_datetime(start_date)) & (stock_data.index <= pd.to_datetime(end_date))]
        stock_data.columns = ['Close']

        # Add investment columns
        stock_data['start_inv_amt'] = starting_amount
        stock_data['mnth_inv_amt'] = 0.0
        for date_idx in stock_data.index:
            if date_idx.day == day_of_investment:
                stock_data.at[date_idx, 'mnth_inv_amt'] = monthly_investment_amount
        stock_data.at[stock_data.index[0], 'mnth_inv_amt'] += starting_amount

        # Calculate performance metrics
        stock_data['stocks_purchased'] = stock_data['mnth_inv_amt'] / stock_data['Close']
        stock_data['cumulative_stocks'] = stock_data['stocks_purchased'].cumsum()
        stock_data['total_value'] = stock_data['cumulative_stocks'] * stock_data['Close']
        stock_data['total_investment'] = stock_data['mnth_inv_amt'].cumsum()

        # Calculate summary metrics
        total_invested_amount = stock_data['total_investment'].iloc[-1]
        final_investment_value = stock_data['total_value'].iloc[-1]
        total_return = final_investment_value - total_invested_amount
        percentage_return = (total_return / total_invested_amount) * 100
        num_years = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days / 365.25
        cagr = ((final_investment_value / total_invested_amount) ** (1 / num_years) - 1) * 100
        num_months = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days // 30

        # Prepare time series data for response
        simulation_data = {
            "dates": stock_data.index.strftime('%Y-%m-%d').tolist(),
            "close_prices": stock_data['Close'].tolist(),
            "total_value": stock_data['total_value'].tolist(),
            "total_investment": stock_data['total_investment'].tolist(),
            "cumulative_stocks": stock_data['cumulative_stocks'].tolist()
        }

        return {
            "total_invested_amount": float(total_invested_amount),
            "final_investment_value": float(final_investment_value),
            "total_return": float(total_return),
            "percentage_return": float(percentage_return),
            "cagr": float(cagr),
            "num_months": int(num_months),
            "simulation_data": simulation_data
        }

    except Exception as e:
        raise ValueError(f"Simulation failed: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Investment Simulator API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/simulate", response_model=InvestmentResponse)
async def simulate_investment_endpoint(request: InvestmentRequest):
    """
    Simulate investment strategy for a given stock ticker and parameters
    """
    try:
        # Validate inputs
        if request.start_date >= request.end_date:
            raise HTTPException(status_code=400, detail="Start date must be before end date")
        
        if request.day_of_investment < 1 or request.day_of_investment > 31:
            raise HTTPException(status_code=400, detail="Day of investment must be between 1 and 31")
        
        if request.monthly_investment_amount < 0 or request.starting_amount < 0:
            raise HTTPException(status_code=400, detail="Investment amounts must be positive")

        # Run simulation
        result = simulate_investment(
            ticker=request.ticker.upper(),
            start_date=request.start_date,
            end_date=request.end_date,
            monthly_investment_amount=request.monthly_investment_amount,
            starting_amount=request.starting_amount,
            day_of_investment=request.day_of_investment
        )

        return InvestmentResponse(
            ticker=request.ticker.upper(),
            **result
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
