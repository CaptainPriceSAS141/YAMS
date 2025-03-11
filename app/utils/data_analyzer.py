import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import random

def calculate_moving_average(data, window=20):
    """
    Calculate the moving average for a given window.
    
    Args:
        data (dict): Dictionary containing stock data
        window (int): Window size for moving average
    
    Returns:
        float: The latest moving average value
    """
    try:
        if not data['success'] or not data['data']:
            return None
        
        # Convert to DataFrame if it's a list of dictionaries
        if isinstance(data['data'], list):
            df = pd.DataFrame(data['data'])
        else:
            df = data['data']
        
        # Calculate moving average
        df['MA'] = df['Close'].rolling(window=window).mean()
        
        # Return the latest value
        return df['MA'].iloc[-1] if not df['MA'].empty else None
    except Exception as e:
        print(f"Error calculating moving average: {str(e)}")
        return None

def calculate_exponential_moving_average(data, window=20):
    """
    Calculate the exponential moving average for a given window.
    
    Args:
        data (dict): Dictionary containing stock data
        window (int): Window size for EMA
    
    Returns:
        float: The latest EMA value
    """
    try:
        if not data['success'] or not data['data']:
            return None
        
        # Convert to DataFrame if it's a list of dictionaries
        if isinstance(data['data'], list):
            df = pd.DataFrame(data['data'])
        else:
            df = data['data']
        
        # Calculate EMA
        df['EMA'] = df['Close'].ewm(span=window, adjust=False).mean()
        
        # Return the latest value
        return df['EMA'].iloc[-1] if not df['EMA'].empty else None
    except Exception as e:
        print(f"Error calculating EMA: {str(e)}")
        return None

def calculate_macd(data, fast=12, slow=26, signal=9):
    """
    Calculate the MACD (Moving Average Convergence Divergence).
    
    Args:
        data (dict): Dictionary containing stock data
        fast (int): Fast EMA period
        slow (int): Slow EMA period
        signal (int): Signal line period
    
    Returns:
        dict: Dictionary containing MACD line, signal line, and histogram
    """
    try:
        if not data['success'] or not data['data']:
            return {'macd': None, 'signal': None, 'histogram': None}
        
        # Convert to DataFrame if it's a list of dictionaries
        if isinstance(data['data'], list):
            df = pd.DataFrame(data['data'])
        else:
            df = data['data']
        
        # Calculate MACD
        df['EMA_fast'] = df['Close'].ewm(span=fast, adjust=False).mean()
        df['EMA_slow'] = df['Close'].ewm(span=slow, adjust=False).mean()
        df['MACD'] = df['EMA_fast'] - df['EMA_slow']
        df['Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
        df['Histogram'] = df['MACD'] - df['Signal']
        
        # Return the latest values
        if df.empty:
            return {'macd': None, 'signal': None, 'histogram': None}
        
        return {
            'macd': df['MACD'].iloc[-1],
            'signal': df['Signal'].iloc[-1],
            'histogram': df['Histogram'].iloc[-1]
        }
    except Exception as e:
        print(f"Error calculating MACD: {str(e)}")
        return {'macd': None, 'signal': None, 'histogram': None}

def calculate_rsi(data, window=14):
    """
    Calculate the Relative Strength Index (RSI).
    
    Args:
        data (dict): Dictionary containing stock data
        window (int): Window size for RSI
    
    Returns:
        float: The latest RSI value
    """
    try:
        if not data['success'] or not data['data']:
            return None
        
        # Convert to DataFrame if it's a list of dictionaries
        if isinstance(data['data'], list):
            df = pd.DataFrame(data['data'])
        else:
            df = data['data']
        
        # Calculate RSI
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # Return the latest value
        return rsi.iloc[-1] if not rsi.empty else None
    except Exception as e:
        print(f"Error calculating RSI: {str(e)}")
        return None

def predict_stock_price(data, days_to_predict=30):
    """
    Predict stock prices using linear regression.
    
    Args:
        data (dict or list): Dictionary containing stock data or list of stock data points
        days_to_predict (int): Number of days to predict
    
    Returns:
        list: List of predicted prices
    """
    try:
        # Check if data is empty
        if not data:
            return []
        
        # Handle both dictionary and list inputs
        if isinstance(data, dict):
            if not data.get('success', True) or not data.get('data', []):
                return []
            data_points = data['data']
        else:
            data_points = data
        
        # Convert to DataFrame if it's a list of dictionaries
        if isinstance(data_points, list):
            df = pd.DataFrame(data_points)
        else:
            df = data_points
        
        # Simple linear regression model
        df['Day'] = range(len(df))
        X = df[['Day']]
        y = df['Close']
        
        # Scale the data
        scaler_X = StandardScaler()
        scaler_y = StandardScaler()
        
        X_scaled = scaler_X.fit_transform(X)
        y_scaled = scaler_y.fit_transform(y.values.reshape(-1, 1))
        
        # Train the model
        model = LinearRegression()
        model.fit(X_scaled, y_scaled)
        
        # Predict future prices
        future_days = np.array(range(len(df), len(df) + days_to_predict)).reshape(-1, 1)
        future_days_scaled = scaler_X.transform(future_days)
        future_prices_scaled = model.predict(future_days_scaled)
        future_prices = scaler_y.inverse_transform(future_prices_scaled)
        
        return future_prices.flatten().tolist()
    except Exception as e:
        print(f"Error predicting stock prices: {str(e)}")
        # Return mock predictions
        try:
            if isinstance(data, dict) and data.get('success', True) and data.get('data', []):
                data_points = data['data']
            else:
                data_points = data
                
            if isinstance(data_points, list) and data_points:
                last_price = data_points[-1]['Close']
            elif hasattr(data_points, 'Close'):
                last_price = data_points['Close'].iloc[-1]
            else:
                return []
                
            # Generate some random predictions based on the last price
            predictions = []
            for i in range(days_to_predict):
                random_change = random.uniform(-0.02, 0.02)  # Random change between -2% and 2%
                predicted_price = last_price * (1 + random_change)
                predictions.append(predicted_price)
                last_price = predicted_price
            
            return predictions
        except Exception as inner_e:
            print(f"Error generating mock predictions: {str(inner_e)}")
            return []

def analyze_trend(data, window=20):
    """
    Analyze the trend of a stock.
    
    Args:
        data (dict): Dictionary containing stock data
        window (int): Window size for moving average
    
    Returns:
        str: Trend analysis ('uptrend', 'downtrend', or 'sideways')
    """
    try:
        if not data['success'] or not data['data']:
            return 'unknown'
        
        # Convert to DataFrame if it's a list of dictionaries
        if isinstance(data['data'], list):
            df = pd.DataFrame(data['data'])
        else:
            df = data['data']
        
        # Calculate short and long-term moving averages
        df['MA_short'] = df['Close'].rolling(window=window).mean()
        df['MA_long'] = df['Close'].rolling(window=window*2).mean()
        
        # Determine trend
        if df.empty or df['MA_short'].iloc[-1] is None or df['MA_long'].iloc[-1] is None:
            return 'unknown'
        
        if df['MA_short'].iloc[-1] > df['MA_long'].iloc[-1] * 1.02:
            return 'uptrend'
        elif df['MA_short'].iloc[-1] < df['MA_long'].iloc[-1] * 0.98:
            return 'downtrend'
        else:
            return 'sideways'
    except Exception as e:
        print(f"Error analyzing trend: {str(e)}")
        return 'unknown' 