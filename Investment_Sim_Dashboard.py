import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date, datetime
import warnings
import requests
import json
warnings.filterwarnings('ignore')

# Configure Streamlit page
st.set_page_config(
    page_title="Investment Regret Simulator",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
<style>
.main-header {
    text-align: left;
    color: #1f77b4;
    padding: 1rem 0;
    margin-bottom: 2rem;
    border-bottom: 2px solid #e0e0e0;
}

.metric-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.positive-return {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.negative-return {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.info-box {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #1f77b4;
    margin: 1rem 0;
}

.stButton > button {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 5px;
    font-weight: 500;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
    border: none;
}

.stSelectbox > div > div > div {
    background-color: white;
}
</style>
""", unsafe_allow_html=True)

def get_popular_tickers():
    """Return a dictionary of popular tickers and their company names"""
    return {
        # Tech giants
        "AAPL": "Apple Inc.",
        "MSFT": "Microsoft Corporation",
        "GOOGL": "Alphabet Inc. (Google)",
        "AMZN": "Amazon.com Inc.",
        "TSLA": "Tesla Inc.",
        "META": "Meta Platforms Inc.",
        "NVDA": "NVIDIA Corporation",
        "NFLX": "Netflix Inc.",
        "CRM": "Salesforce Inc.",
        "ADBE": "Adobe Inc.",
        
        # Finance & Banks
        "JPM": "JPMorgan Chase & Co.",
        "BAC": "Bank of America Corp.",
        "WFC": "Wells Fargo & Company",
        "GS": "Goldman Sachs Group Inc.",
        "MS": "Morgan Stanley",
        "V": "Visa Inc.",
        "MA": "Mastercard Inc.",
        "PYPL": "PayPal Holdings Inc.",
        
        # Consumer & Retail
        "WMT": "Walmart Inc.",
        "HD": "Home Depot Inc.",
        "PG": "Procter & Gamble Co.",
        "KO": "Coca-Cola Company",
        "PEP": "PepsiCo Inc.",
        "MCD": "McDonald's Corporation",
        "SBUX": "Starbucks Corporation",
        "NKE": "Nike Inc.",
        "DIS": "Walt Disney Company",
        
        # Healthcare & Pharma
        "JNJ": "Johnson & Johnson",
        "UNH": "UnitedHealth Group Inc.",
        "PFE": "Pfizer Inc.",
        "ABT": "Abbott Laboratories",
        "TMO": "Thermo Fisher Scientific",
        "MDT": "Medtronic PLC",
        "BMY": "Bristol Myers Squibb Co.",
        
        # Energy & Utilities
        "XOM": "Exxon Mobil Corporation",
        "CVX": "Chevron Corporation",
        "COP": "ConocoPhillips",
        "NEE": "NextEra Energy Inc.",
        
        # Industrial & Materials
        "BA": "Boeing Company",
        "CAT": "Caterpillar Inc.",
        "GE": "General Electric Company",
        "MMM": "3M Company",
        "HON": "Honeywell International",
        
        # ETFs
        "SPY": "SPDR S&P 500 ETF Trust",
        "QQQ": "Invesco QQQ Trust",
        "VTI": "Vanguard Total Stock Market ETF",
        "VOO": "Vanguard S&P 500 ETF",
        "IWM": "iShares Russell 2000 ETF",
        "VEA": "Vanguard FTSE Developed Markets ETF",
        "VWO": "Vanguard FTSE Emerging Markets ETF",
        "BND": "Vanguard Total Bond Market ETF",
        "GLD": "SPDR Gold Shares",
        "SLV": "iShares Silver Trust"
    }

# Check for existing ticker info in session state
if 'ticker_info_cache' not in st.session_state:
    st.session_state.ticker_info_cache = {}

def validate_ticker_with_cache(ticker):
    """Validate ticker with caching to avoid repeated API calls"""
    if ticker in st.session_state.ticker_info_cache:
        return st.session_state.ticker_info_cache[ticker]
    
    try:
        stock_info = yf.Ticker(ticker)
        info = stock_info.info
        
        if info and info.get('shortName'):
            result = {
                'valid': True,
                'name': info.get('shortName', 'N/A'),
                'sector': info.get('sector', 'N/A')
            }
        else:
            result = {'valid': False, 'name': None, 'sector': None}
        
        st.session_state.ticker_info_cache[ticker] = result
        return result
    except:
        result = {'valid': False, 'name': None, 'sector': None}
        st.session_state.ticker_info_cache[ticker] = result
        return result

def call_investment_api(ticker, start_date, end_date, monthly_investment_amount, starting_amount, day_of_investment, api_base_url="http://localhost:8001"):
    """Call the FastAPI backend for investment simulation"""
    try:
        payload = {
            "ticker": ticker,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "monthly_investment_amount": monthly_investment_amount,
            "starting_amount": starting_amount,
            "day_of_investment": day_of_investment
        }
        
        response = requests.post(f"{api_base_url}/simulate", json=payload, timeout=30)
        
        if response.status_code == 200:
            return response.json(), None
        else:
            error_detail = response.json().get("detail", "Unknown error")
            return None, f"API Error ({response.status_code}): {error_detail}"
            
    except requests.exceptions.ConnectionError:
        return None, "Could not connect to FastAPI server. Make sure it's running on http://localhost:8001"
    except requests.exceptions.Timeout:
        return None, "API request timed out. The server might be overloaded."
    except Exception as e:
        return None, f"Error calling API: {str(e)}"

# App title
st.markdown('<h1 class="main-header">📈 Historical Investment Regret Simulator Dashboard</h1>', unsafe_allow_html=True)
st.markdown("**Understand how much money you could have had today. Simulate Dollar-Cost Averaging (DCA) investment strategies with real stock data**")
st.markdown("**Please Note: This is not investment advice!!!**")

# Input section - organized in left column format
st.markdown("### Input Parameters")

# Create main layout: inputs on left, results on right
input_col, result_col = st.columns([1, 2])

with input_col:
    st.markdown("#### 📊 How could you have invested?")
    
    # API backend info
    st.info("🚀 Using FastAPI backend (http://localhost:8001)")
    
    # Row 1: Stock ticker search and selection
    ticker_col1, ticker_col2 = st.columns(2)
    
    with ticker_col1:
        # Manual ticker input first (more prominent)
        ticker = st.text_input("Stock Ticker", "", placeholder="e.g., AAPL", key="manual_ticker_primary")
    
    with ticker_col2:
        # Get popular tickers for selectbox
        popular_tickers = get_popular_tickers()
        ticker_options = ["Select popular..."] + [f"{k} - {v[:20]}..." if len(v) > 20 else f"{k} - {v}" for k, v in popular_tickers.items()]
        
        selected_option = st.selectbox(
            "Or Select Popular", 
            options=ticker_options,
            index=0,
            key="ticker_dropdown_secondary"
        )
        
        # Extract ticker from selection if no manual input
        if not ticker and selected_option != "Select popular...":
            ticker = selected_option.split(" - ")[0]
    
    # Default ticker if nothing selected
    ticker = ticker.upper() if ticker else "AAPL"
    
    # Row 2: Start and End dates
    st.markdown("---")
    date_col1, date_col2 = st.columns(2)
    
    with date_col1:
        today = date.today()
        default_start = today - pd.Timedelta(days=365)
        
        if 'start_date_value' not in st.session_state:
            st.session_state.start_date_value = default_start
        
        start_date = st.date_input("Start Date", 
                                  value=st.session_state.start_date_value,
                                  max_value=today)
        
        if start_date != st.session_state.start_date_value:
            st.session_state.start_date_value = start_date
    
    with date_col2:
        if 'end_date_value' not in st.session_state:
            st.session_state.end_date_value = today
        
        end_date = st.date_input("End Date", 
                                value=st.session_state.end_date_value,
                                max_value=today)
        
        if end_date != st.session_state.end_date_value:
            st.session_state.end_date_value = end_date
    
    # Row 3: Quick date options
    quick_col1, quick_col2 = st.columns(2)
    
    with quick_col1:
        st.markdown("**Quick Start:**")
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        with btn_col1:
            if st.button("1Y", help="1 year ago", key="1y_button", type="secondary"):
                st.session_state.start_date_value = today - pd.Timedelta(days=365)
                st.rerun()
        with btn_col2:
            if st.button("2Y", help="2 years ago", key="2y_button", type="secondary"):
                st.session_state.start_date_value = today - pd.Timedelta(days=730)
                st.rerun()
        with btn_col3:
            if st.button("5Y", help="5 years ago", key="5y_button", type="secondary"):
                st.session_state.start_date_value = today - pd.Timedelta(days=1825)
                st.rerun()
    
    with quick_col2:
        st.markdown("**Quick End:**")
        if st.button("Today", 
                    help="Set end date to today", 
                    key="today_button",
                    type="secondary",
                    use_container_width=True):
            st.session_state.end_date_value = today
            st.rerun()
    
    # Row 4: Investment amounts
    st.markdown("---")
    amount_col1, amount_col2 = st.columns(2)
    
    with amount_col1:
        starting_amount = st.number_input("Starting Amount ($)", min_value=0, value=1000, step=500)
    
    with amount_col2:
        monthly_investment_amount = st.number_input("Monthly Investment ($)", min_value=0, value=1000, step=500)
    
    # Row 5: Investment day
    day_of_investment = st.number_input("Investment Day of Month", min_value=1, max_value=30, value=1, 
                                       help="Day of month for monthly investments (1-30)")
    
    # Row 6: Simulate button
    st.markdown("---")
    simulate_button = st.button("🔮 Simulate", type="primary", use_container_width=True)

    # Display ticker validation in input column
    if ticker and ticker != "":
        with st.expander("ℹ️ Ticker Info", expanded=False):
            ticker_info = validate_ticker_with_cache(ticker)
            if ticker_info['valid']:
                st.success(f"✅ **{ticker.upper()}**")
                st.caption(f"{ticker_info['name']}")
                st.caption(f"**Sector:** {ticker_info['sector']}")
            else:
                st.warning(f"⚠️ Could not validate '{ticker.upper()}'")

# Input validation
with input_col:
    if start_date >= end_date:
        st.error("❌ Start date must be before end date")
        st.stop()

    if end_date > date.today():
        st.error("❌ End date cannot be in the future")
        st.stop()

    if not ticker or ticker.strip() == "":
        st.error("❌ Please select or enter a ticker symbol")
        st.stop()

# Results section in right column
with result_col:
    st.markdown("### 📈 Investment Results")
    
    if simulate_button:
        try:
            # Clean the ticker input provided by user
            ticker = ticker.strip().upper()
            
            if not ticker:
                st.error("❌ Please enter a ticker symbol")
                st.stop()
            
            # Call FastAPI backend
            with st.spinner('🚀 Calling FastAPI backend...'):
                api_result, api_error = call_investment_api(
                    ticker, start_date, end_date, monthly_investment_amount, 
                    starting_amount, day_of_investment
                )
                
                if api_error:
                    st.error(f"❌ {api_error}")
                    st.stop()
                
                # Extract results from API response
                total_invested_amount = api_result['total_invested_amount']
                final_investment_value = api_result['final_investment_value']
                total_return = api_result['total_return']
                percentage_return = api_result['percentage_return']
                cagr = api_result['cagr']
                num_months = api_result['num_months']
                
                # For charting, we still need to fetch the stock data locally
                # (API doesn't return detailed time series data in the current format)
                with st.spinner('📊 Fetching chart data...'):
                    stock_data = yf.download(ticker, start=start_date - pd.Timedelta(days=7), end=end_date)
                    if not stock_data.empty and 'Close' in stock_data.columns:
                        # Prepare data for charting (simplified version)
                        stock_data = stock_data[['Close']].round(2)
                        date_range = pd.date_range(start=start_date - pd.Timedelta(days=7), end=end_date)
                        stock_data = stock_data.reindex(date_range)
                        stock_data.fillna(method='ffill', inplace=True)
                        stock_data = stock_data[(stock_data.index >= pd.to_datetime(start_date)) & (stock_data.index <= pd.to_datetime(end_date))]
                        stock_data.columns = ['Close']
                        
                        # Reconstruct investment data for charting
                        stock_data['mnth_inv_amt'] = 0.0
                        for date_idx in stock_data.index:
                            if date_idx.day == day_of_investment:
                                stock_data.at[date_idx, 'mnth_inv_amt'] = monthly_investment_amount
                        stock_data.at[stock_data.index[0], 'mnth_inv_amt'] += starting_amount
                        
                        stock_data['stocks_purchased'] = stock_data['mnth_inv_amt'] / stock_data['Close']
                        stock_data['cumulative_stocks'] = stock_data['stocks_purchased'].cumsum()
                        stock_data['total_value'] = stock_data['cumulative_stocks'] * stock_data['Close']
                        stock_data['total_investment'] = stock_data['mnth_inv_amt'].cumsum()
            
            # Calculate num_years for display
            num_years = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days / 365.25

            # Current Output Layout: Charts on left, metrics on right
            chart_col, metrics_col = st.columns([2, 1])
            
            with chart_col:
                st.markdown("### 📊 Investment Return Analysis")
                
                # Create the investment return chart
                fig, ax = plt.subplots(figsize=(12, 8))
                
                # Plot both lines
                ax.plot(stock_data.index, stock_data['total_investment'], 
                       label='Total Invested', linewidth=2, color='#ff6b6b', linestyle='--')
                ax.plot(stock_data.index, stock_data['total_value'], 
                       label='Portfolio Value', linewidth=3, color='#4ecdc4')
                
                # Formatting
                ax.set_xlabel('Date', fontsize=12, fontweight='bold')
                ax.set_ylabel('Value ($)', fontsize=12, fontweight='bold')
                ax.set_title(f'{ticker.upper()} Investment Growth Over Time', 
                           fontsize=14, fontweight='bold', pad=20)
                
                # Format x-axis dates
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
                ax.xaxis.set_major_locator(mdates.MonthLocator(interval=max(1, num_months//6)))
                plt.xticks(rotation=45)
                
                # Format y-axis with currency
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
                
                # Add grid and legend
                ax.grid(True, alpha=0.3)
                ax.legend(loc='upper left', fontsize=10)
                
                # Add fill between lines to show gain/loss
                ax.fill_between(stock_data.index, stock_data['total_investment'], stock_data['total_value'], 
                              alpha=0.3, color='green' if total_return >= 0 else 'red')
                
                plt.tight_layout()
                st.pyplot(fig)
                
                # Additional chart info
                st.info(f"""
                **Chart Legend:**
                - **Red dashed line**: Your cumulative investments (${total_invested_amount:,.2f})
                - **Teal solid line**: Your portfolio value (${final_investment_value:,.2f})
                - **Shaded area**: {'Profit' if total_return >= 0 else 'Loss'} visualization
                """)
                
            with metrics_col:
                st.markdown("### 💰 Key Metrics")
                
                # Return metrics with color coding
                return_color = "normal" if total_return >= 0 else "inverse"
                
                st.metric(
                    label="🌰 Total Cash Invested",
                    value=f"${total_invested_amount:,.2f}"
                )
                
                st.metric(
                    label="🌳 Final Portfolio Value",
                    value=f"${final_investment_value:,.2f}"
                )
                
                st.metric(
                    label="🌱 Total Return",
                    value=f"${total_return:,.2f}",
                    delta=f"{percentage_return:+.2f}%",
                    delta_color=return_color
                )

                st.metric(
                    label="🌱 Compounded Annual Growth Rate (CAGR)",
                    value=f"{cagr:+.2f}%",
                    help="Compound Annual Growth Rate"
                )
                
                # Additional investment details
                total_shares = stock_data['cumulative_stocks'].iloc[-1]
                avg_cost_per_share = total_invested_amount / total_shares if total_shares > 0 else 0
                current_price = stock_data['Close'].iloc[-1]
                
                st.markdown("---")
                st.markdown("### 📋 Investment Details")
                st.markdown(f"""
                **Investment Summary:**
                - Period: **{start_date.strftime('%b %d, %Y')} to {end_date.strftime('%b %d, %Y')}**
                - Duration: **{num_years:.1f} years ({num_months} months)**
                - Investment Day: **{day_of_investment}{'st' if day_of_investment == 1 else 'nd' if day_of_investment == 2 else 'rd' if day_of_investment == 3 else 'th'} of each month**
                
                **Portfolio Breakdown:**
                - Total Shares Owned: **{total_shares:.2f}**
                - Average Cost per Share: **${avg_cost_per_share:.2f}**
                - Current Share Price: **${current_price:.2f}**
                """)
                
                if total_return > 0:
                    st.success(f"📈 Your investments could have generated a positive return of ${total_return:,.2f}, Great success !")
                else:
                    st.warning(f"📉 Your investments could have had a loss of ${abs(total_return):,.2f}")

        except Exception as e:
            # Enhanced error handling for ticker-related issues
            error_message = str(e).lower()
            
            if "no data found" in error_message or "not found" in error_message:
                st.error(f"❌ **Ticker '{ticker}' not found or has no data.**")
                st.info("💡 **Please try:**")
                st.info("• Double-check the ticker symbol spelling")
                st.info("• Select from the popular tickers dropdown")
                st.info("• Ensure the company trades on major US exchanges")
                st.info("• Try a different date range")
            elif "network" in error_message or "connection" in error_message:
                st.error("❌ **Network error occurred while fetching data.**")
                st.info("💡 Please check your internet connection and try again.")
            else:
                st.error(f"❌ **Error occurred during simulation:** {str(e)}")
                st.info("💡 Please check your inputs and try again. If the problem persists, try a different ticker or date range.")
    
    else:
        # Display placeholder content when not simulating
        st.markdown("### 📊 Ready to regret?")
        st.info("👈 Configure your investment parameters on the left and click 'Simulate Investment' to see how much you could have had!")
        
        # Show sample metrics as placeholders
        st.markdown("#### Sample Metrics Display:")
        placeholder_col1, placeholder_col2, placeholder_col3 = st.columns(3)
        
        with placeholder_col1:
            st.metric(
                label="Total Invested",
                value="$--,---.--",
                delta=None
            )
        
        with placeholder_col2:
            st.metric(
                label="Current Value",
                value="$--,---.--", 
                delta="+-.-%"
            )
        
        with placeholder_col3:
            st.metric(
                label="Total Return",
                value="$--,---.--",
                delta="+-.-%"
            )