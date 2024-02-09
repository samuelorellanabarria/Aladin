import streamlit as st
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
import numpy as np
from scipy.optimize import minimize

class PortfolioOptimizer:
    def __init__(self):
        self.start_date = "2022-01-01"
        self.end_date = "2023-01-31"
        self.tickers = []
        self.portfolio_data = None

    def get_user_input(self):
        st.sidebar.header('Parámetros de entrada')
        self.start_date = st.sidebar.text_input("Fecha de inicio", "2022-01-01")
        self.end_date = st.sidebar.text_input("Fecha de fin", "2023-01-31") 
        tickers_input = st.sidebar.text_input("Tickers separados por comas", "AAPL,MSFT,GOOG,AMZN")
        self.tickers = tickers_input.split(',')
        #st.write('Tickers seleccionados:', self.tickers)

    def get_portfolio_data(self):
        data = yf.download(self.tickers, start=self.start_date, end=self.end_date)
        data = data["Adj Close"]
        returns_daily = data.pct_change()
        returns_annual = returns_daily.mean() * 250
        cov_daily = returns_daily.cov()
        cov_annual = cov_daily * 250

        num_assets = len(self.tickers)
        num_portfolios = 50000

        port_returns = []
        port_volatility = []
        stock_weights = []

        np.random.seed(101)

        for portfolio in range(num_portfolios):
            weights = np.random.random(num_assets)
            weights /= np.sum(weights)
            returns = np.dot(weights, returns_annual)
            volatility = np.sqrt(np.dot(weights.T, np.dot(cov_annual, weights)))
            port_returns.append(returns)
            port_volatility.append(volatility)
            stock_weights.append(weights)

        portfolio = {'Returns': port_returns, 'Volatility': port_volatility}

        for counter, symbol in enumerate(self.tickers):
            portfolio[symbol+' Weight'] = [Weight[counter] for Weight in stock_weights]

        self.portfolio_data = pd.DataFrame(portfolio)

    def display_results(self):
        min_volatility = self.portfolio_data['Volatility'].min()
        min_variance_port = self.portfolio_data.loc[self.portfolio_data['Volatility'] == min_volatility]

        #st.subheader('Cartera de mínima varianza')
        #st.write(min_variance_port.T)

        max_return = self.portfolio_data['Returns'].max() 
        max_return_port = self.portfolio_data.loc[self.portfolio_data['Returns'] == max_return]

        #st.subheader('Cartera de máximo retorno')
        #st.write(max_return_port.T)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader('Tickers seleccionados')
            st.write(self.tickers)

        with col2:
            st.subheader('Cartera de mínima varianza')
            st.write(min_variance_port.T)
            
        with col3:
            st.subheader('Cartera de máximo retorno')
            st.write(max_return_port.T)
            
        st.divider()

def main():
    st.title('Optimización de Carteras de Inversión')
    portfolio_optimizer = PortfolioOptimizer()
    portfolio_optimizer.get_user_input()
    portfolio_optimizer.get_portfolio_data()
    portfolio_optimizer.display_results()

if __name__ == "__main__":
    main()
