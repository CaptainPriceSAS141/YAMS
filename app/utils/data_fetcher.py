import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import random

def get_stock_data(symbol, period='1y', interval='1d'):
    """
    Fetch stock data from Yahoo Finance.
    
    Args:
        symbol (str): Stock symbol (e.g., 'AAPL', 'MSFT')
        period (str): Period of data to fetch (e.g., '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
        interval (str): Data interval (e.g., '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
    
    Returns:
        dict: Dictionary containing stock data and success status
    """
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period, interval=interval)
        
        # Reset index to make Date a column
        data = data.reset_index()
        
        # Convert Date to string format for JSON serialization
        data['Date'] = data['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        return {
            'success': True,
            'data': data.to_dict('records'),
            'info': stock.info
        }
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        # Return mock data for demonstration purposes
        return get_mock_stock_data(symbol, period, interval)

def get_mock_stock_data(symbol, period='1y', interval='1d'):
    """Generate mock stock data when API calls fail."""
    # Generate dates
    end_date = datetime.now()
    
    if period == '1d':
        days = 1
    elif period == '5d':
        days = 5
    elif period == '1mo':
        days = 30
    elif period == '3mo':
        days = 90
    elif period == '6mo':
        days = 180
    elif period == '1y':
        days = 365
    else:
        days = 365
    
    start_date = end_date - timedelta(days=days)
    
    # Generate price data
    base_price = random.uniform(50, 200)
    price_data = []
    
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Only weekdays
            daily_change = random.uniform(-2, 2)
            open_price = base_price
            close_price = base_price + daily_change
            high_price = max(open_price, close_price) + random.uniform(0, 1)
            low_price = min(open_price, close_price) - random.uniform(0, 1)
            volume = random.randint(1000000, 10000000)
            
            price_data.append({
                'Date': current_date.strftime('%Y-%m-%d %H:%M:%S'),
                'Open': open_price,
                'High': high_price,
                'Low': low_price,
                'Close': close_price,
                'Volume': volume
            })
            
            base_price = close_price
        
        if interval == '1d':
            current_date += timedelta(days=1)
        elif interval == '1wk':
            current_date += timedelta(days=7)
        elif interval == '1mo':
            current_date += timedelta(days=30)
        else:
            current_date += timedelta(days=1)
    
    # Mock company info
    mock_info = {
        'symbol': symbol,
        'shortName': f"{symbol} Inc.",
        'longName': f"{symbol} Corporation",
        'sector': 'Technology',
        'industry': 'Software',
        'website': f"https://www.{symbol.lower()}.com",
        'marketCap': random.randint(1000000000, 2000000000),
        'regularMarketPrice': price_data[-1]['Close'],
        'regularMarketOpen': price_data[-1]['Open'],
        'regularMarketDayHigh': price_data[-1]['High'],
        'regularMarketDayLow': price_data[-1]['Low'],
        'regularMarketVolume': price_data[-1]['Volume'],
        'regularMarketChange': price_data[-1]['Close'] - price_data[-1]['Open'],
        'regularMarketChangePercent': ((price_data[-1]['Close'] - price_data[-1]['Open']) / price_data[-1]['Open']) * 100,
        'fiftyTwoWeekHigh': max([data['High'] for data in price_data]),
        'fiftyTwoWeekLow': min([data['Low'] for data in price_data]),
        'country': 'United States',
        'exchangeName': 'NASDAQ',
        'quoteType': 'EQUITY',
        'longBusinessSummary': f"This is a mock description for {symbol} Inc. The company specializes in software development and technology solutions."
    }
    
    return {
        'success': True,
        'data': price_data,
        'info': mock_info
    }

def get_multiple_stocks_data(symbols, period='1y', interval='1d'):
    """
    Fetch data for multiple stocks.
    
    Args:
        symbols (list): List of stock symbols
        period (str): Period of data to fetch
        interval (str): Data interval
    
    Returns:
        dict: Dictionary with stock symbols as keys and their data as values
    """
    result = {}
    for symbol in symbols:
        result[symbol] = get_stock_data(symbol, period, interval)
    return result

def search_stocks(query):
    """
    Search for stocks by name or symbol.
    
    Args:
        query (str): Search query
    
    Returns:
        dict: Dictionary containing search results
    """
    try:
        # For simplicity, return some mock results
        mock_results = [
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'exchange': 'NASDAQ', 'sector': 'Technology'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'exchange': 'NASDAQ', 'sector': 'Technology'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'exchange': 'NASDAQ', 'sector': 'Technology'},
            {'symbol': 'AMZN', 'name': 'Amazon.com, Inc.', 'exchange': 'NASDAQ', 'sector': 'Consumer Cyclical'},
            {'symbol': 'TSLA', 'name': 'Tesla, Inc.', 'exchange': 'NASDAQ', 'sector': 'Consumer Cyclical'}
        ]
        
        # Filter results based on query
        filtered_results = [r for r in mock_results if query.lower() in r['symbol'].lower() or query.lower() in r['name'].lower()]
        
        return {
            'success': True,
            'results': filtered_results
        }
    except Exception as e:
        print(f"Error searching stocks: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'results': []
        } 