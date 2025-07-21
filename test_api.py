import requests
import json
from datetime import date

# Test the FastAPI endpoint
def test_investment_api():
    url = "http://localhost:8000/simulate"
    
    payload = {
        "ticker": "AAPL",
        "start_date": "2021-01-01",
        "end_date": "2022-01-01",
        "monthly_investment_amount": 1000.0,
        "starting_amount": 1000.0,
        "day_of_investment": 1
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        print("API Response:")
        print(json.dumps(result, indent=2))
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        return None

if __name__ == "__main__":
    # Test the API
    print("Testing Investment Simulator API...")
    result = test_investment_api()
    
    if result:
        print(f"\nSummary:")
        print(f"Ticker: {result['ticker']}")
        print(f"Total Invested: ${result['total_invested_amount']:,.2f}")
        print(f"Final Value: ${result['final_investment_value']:,.2f}")
        print(f"Total Return: ${result['total_return']:,.2f}")
        print(f"Percentage Return: {result['percentage_return']:.2f}%")
        print(f"CAGR: {result['cagr']:.2f}%")
