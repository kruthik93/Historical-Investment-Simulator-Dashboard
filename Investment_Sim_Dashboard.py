import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

st.title("Investment Regret Simulator Dashboard")

ticker = st.text_input("Enter the ticker symbol (e.g., AAPL for Apple):", "AAPL")
start_date = st.date_input("Start date:", pd.to_datetime("2021-01-01"))
end_date = st.date_input("End date:", pd.to_datetime("2022-01-01"))
monthly_investment_amount = st.number_input("Monthly investment amount:", min_value=0.0, value=1000.0)
starting_amount = st.number_input("Starting amount:", min_value=0.0, value=1000.0)
day_of_investment = st.number_input("Day of month for investment (1-31):", min_value=1, max_value=31, value=1)

if st.button("Simulate"):
    stock_data = yf.download(ticker, start=start_date - pd.Timedelta(days=7), end=end_date)
    stock_data = stock_data[['Close']].round(2)
    date_range = pd.date_range(start=start_date - pd.Timedelta(days=7), end=end_date)
    stock_data = stock_data.reindex(date_range)
    stock_data.fillna(method='ffill', inplace=True)
    stock_data = stock_data[(stock_data.index >= pd.to_datetime(start_date)) & (stock_data.index <= pd.to_datetime(end_date))]
    stock_data.columns = ['Close']

    stock_data['start_inv_amt'] = starting_amount
    stock_data['mnth_inv_amt'] = 0.0
    for date in stock_data.index:
        if date.day == day_of_investment:
            stock_data.at[date, 'mnth_inv_amt'] = monthly_investment_amount
    stock_data.at[stock_data.index[0], 'mnth_inv_amt'] += starting_amount

    stock_data['stocks_purchased'] = stock_data['mnth_inv_amt'] / stock_data['Close']
    stock_data['cumulative_stocks'] = stock_data['stocks_purchased'].cumsum()
    stock_data['total_value'] = stock_data['cumulative_stocks'] * stock_data['Close']
    stock_data['total_investment'] = stock_data['mnth_inv_amt'].cumsum()

    st.line_chart(stock_data[['total_value', 'total_investment']])

    total_invested_amount = stock_data['total_investment'].iloc[-1]
    final_investment_value = stock_data['total_value'].iloc[-1]
    total_return = final_investment_value - total_invested_amount
    percentage_return = (total_return / total_invested_amount) * 100
    num_years = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days / 365.25
    cagr = ((final_investment_value / total_invested_amount) ** (1 / num_years) - 1) * 100
    num_months = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days // 30

    st.write(f"Total Invested Amount: ${total_invested_amount:.2f}")
    st.write(f"Final Investment Value: ${final_investment_value:.2f}")
    st.write(f"Total Return on Investment: ${total_return:.2f}")
    st.write(f"Percentage Return on Investment: {percentage_return:.2f}%")
    st.write(f"CAGR (Compound Annual Growth Rate): {cagr:.2f}%")
    st.write(f"Number of Months of Investment: {num_months}")
