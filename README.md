# Historical Investment Regret Simulator Dashboard

Ever wondered how much money you would have had right now if you had only regularly invested a portion of your paycheck? Well this tool is for you !

This Dashboard is an investment simulation tool that helps users understand the potential growth investments could have had over time using Dollar-Cost Averaging (DCA) strategy

Please note: This is not investment advice !!! This dashboard is used to simulate what potentially could have happened historically, and should not be considered for making any financial decisions.

<img width="1741" height="927" alt="image" src="https://github.com/user-attachments/assets/342a6c03-293e-4fa1-9b2d-f5fbca5ad48f" />

## Features

- **Streamlit Dashboard**: Interactive web interface for investment simulation
- **FastAPI Backend**: RESTful API for programmatic access
- **Docker Support**: Containerized deployment for easy scaling
- **Investment Analysis**: Calculate CAGR, total returns, and visualize growth over time

## Project Structure

```
Investment-Simulator-Dashboard/
├── Investment_Sim_Dashboard.py    # Streamlit web interface
├── main.py                        # FastAPI backend
├── test_api.py                    # API testing script
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker container configuration
├── docker-compose.yml             # Multi-service orchestration
└── README.md                      # This file
```

## Quick Start

### Option 1: Run Streamlit Dashboard Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the Streamlit app:
   ```bash
   streamlit run Investment_Sim_Dashboard.py
   ```

3. Open your browser to `http://localhost:8501`

### Option 2: Run FastAPI Backend

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

3. Access the API documentation at `http://localhost:8000/docs`

### Option 3: Docker Deployment

1. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

2. Access services:
   - FastAPI: `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`
   - MLflow UI: `http://localhost:5000` (optional)

## API Usage

### Simulate Investment

**POST** `/simulate`

```json
{
  "ticker": "AAPL",
  "start_date": "2021-01-01",
  "end_date": "2022-01-01",
  "monthly_investment_amount": 1000.0,
  "starting_amount": 1000.0,
  "day_of_investment": 1
}
```

**Response:**
```json
{
  "ticker": "AAPL",
  "total_invested_amount": 13000.0,
  "final_investment_value": 15234.56,
  "total_return": 2234.56,
  "percentage_return": 17.19,
  "cagr": 17.19,
  "num_months": 12,
  "simulation_data": {
    "dates": ["2021-01-01", "2021-01-02", "..."],
    "close_prices": [132.69, 131.96, "..."],
    "total_value": [1000.0, 1005.2, "..."],
    "total_investment": [1000.0, 1000.0, "..."]
  }
}
```

## Testing

Test the API endpoints:

```bash
python test_api.py
```

## Deployment Architecture

### Why FastAPI?
- **High Performance**: Fast, modern web framework
- **Auto Documentation**: Swagger UI and ReDoc integration
- **Type Safety**: Pydantic models for request/response validation
- **Async Support**: Handle concurrent requests efficiently

### Why Docker?
- **Consistency**: Same environment across dev/test/prod
- **Scalability**: Easy horizontal scaling with orchestration
- **Isolation**: Dependencies contained within containers
- **Portability**: Deploy anywhere Docker runs

### Real-World Applications

1. **Financial Planning Tools**: Integrate with wealth management platforms
2. **Robo-Advisors**: Backend service for automated investment recommendations
3. **Educational Platforms**: Help users understand investment strategies
4. **Portfolio Analysis**: Compare different investment approaches

## Key Metrics Calculated

- **Total Return**: Absolute profit/loss from investments
- **Percentage Return**: Return as percentage of total invested
- **CAGR**: Compound Annual Growth Rate for annualized returns
- **Investment Timeline**: Month-by-month portfolio growth

## Future Enhancements

- [ ] MLflow integration for experiment tracking
- [ ] Multiple investment strategies (lump sum, value averaging)
- [ ] Portfolio diversification across multiple stocks
- [ ] Risk metrics (Sharpe ratio, maximum drawdown)
- [ ] Kubernetes deployment manifests
- [ ] CI/CD pipeline integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Disclaimer
This project was developed with assistance from AI tools such as GitHub Copilot and Claude.
