import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import json

def create_candlestick_chart(data, title='Stock Price'):
    """
    Create a candlestick chart for stock data.
    
    Args:
        data (dict): Dictionary containing stock data
        title (str): Chart title
    
    Returns:
        dict: JSON representation of the chart
    """
    try:
        if not data['success'] or not data['data']:
            return json.dumps({'data': [], 'layout': {'title': 'No data available'}})
        
        # Convert to DataFrame if it's a list of dictionaries
        if isinstance(data['data'], list):
            df = pd.DataFrame(data['data'])
        else:
            df = data['data']
        
        # Create candlestick chart
        fig = go.Figure(data=[go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price'
        )])
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title='Date',
            yaxis_title='Price',
            xaxis_rangeslider_visible=False,
            template='plotly_white'
        )
        
        return json.dumps(fig.to_dict())
    except Exception as e:
        print(f"Error creating candlestick chart: {str(e)}")
        return json.dumps({'data': [], 'layout': {'title': 'Error creating chart'}})

def create_line_chart(data, y_column='Close', title='Stock Price'):
    """
    Create a line chart for stock data.
    
    Args:
        data (dict): Dictionary containing stock data
        y_column (str): Column to plot on y-axis
        title (str): Chart title
    
    Returns:
        dict: JSON representation of the chart
    """
    try:
        if not data['success'] or not data['data']:
            return json.dumps({'data': [], 'layout': {'title': 'No data available'}})
        
        # Convert to DataFrame if it's a list of dictionaries
        if isinstance(data['data'], list):
            df = pd.DataFrame(data['data'])
        else:
            df = data['data']
        
        # Create line chart
        fig = go.Figure(data=[go.Scatter(
            x=df['Date'],
            y=df[y_column],
            mode='lines',
            name=y_column
        )])
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title='Date',
            yaxis_title=y_column,
            template='plotly_white'
        )
        
        return json.dumps(fig.to_dict())
    except Exception as e:
        print(f"Error creating line chart: {str(e)}")
        return json.dumps({'data': [], 'layout': {'title': 'Error creating chart'}})

def create_technical_analysis_chart(data, ma_periods=[20, 50, 200], include_volume=True):
    """
    Create a technical analysis chart with moving averages and volume.
    
    Args:
        data (dict): Dictionary containing stock data
        ma_periods (list): List of periods for moving averages
        include_volume (bool): Whether to include volume subplot
    
    Returns:
        dict: JSON representation of the chart
    """
    try:
        if not data['success'] or not data['data']:
            return json.dumps({'data': [], 'layout': {'title': 'No data available'}})
        
        # Convert to DataFrame if it's a list of dictionaries
        if isinstance(data['data'], list):
            df = pd.DataFrame(data['data'])
        else:
            df = data['data']
        
        # Calculate moving averages
        for period in ma_periods:
            df[f'MA_{period}'] = df['Close'].rolling(window=period).mean()
        
        # Create figure
        if include_volume:
            fig = go.Figure()
            
            # Add price line
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['Close'],
                mode='lines',
                name='Close Price',
                line=dict(color='#2c7be5', width=2)
            ))
            
            # Add moving averages
            colors = ['#e63946', '#f1c40f', '#2ecc71']
            for i, period in enumerate(ma_periods):
                fig.add_trace(go.Scatter(
                    x=df['Date'],
                    y=df[f'MA_{period}'],
                    mode='lines',
                    name=f'MA {period}',
                    line=dict(color=colors[i % len(colors)], width=1.5)
                ))
            
            # Create volume subplot
            fig.add_trace(go.Bar(
                x=df['Date'],
                y=df['Volume'],
                name='Volume',
                marker=dict(color='rgba(44, 123, 229, 0.3)'),
                yaxis='y2'
            ))
            
            # Update layout
            fig.update_layout(
                title='Technical Analysis',
                xaxis_title='Date',
                yaxis_title='Price',
                template='plotly_white',
                yaxis=dict(
                    domain=[0.3, 1]
                ),
                yaxis2=dict(
                    domain=[0, 0.2],
                    title='Volume'
                ),
                legend=dict(
                    orientation='h',
                    y=1.1
                )
            )
        else:
            fig = go.Figure()
            
            # Add price line
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['Close'],
                mode='lines',
                name='Close Price',
                line=dict(color='#2c7be5', width=2)
            ))
            
            # Add moving averages
            colors = ['#e63946', '#f1c40f', '#2ecc71']
            for i, period in enumerate(ma_periods):
                fig.add_trace(go.Scatter(
                    x=df['Date'],
                    y=df[f'MA_{period}'],
                    mode='lines',
                    name=f'MA {period}',
                    line=dict(color=colors[i % len(colors)], width=1.5)
                ))
            
            # Update layout
            fig.update_layout(
                title='Technical Analysis',
                xaxis_title='Date',
                yaxis_title='Price',
                template='plotly_white',
                legend=dict(
                    orientation='h',
                    y=1.1
                )
            )
        
        return json.dumps(fig.to_dict())
    except Exception as e:
        print(f"Error creating technical analysis chart: {str(e)}")
        return json.dumps({'data': [], 'layout': {'title': 'Error creating chart'}})

def create_comparison_chart(data_dict, title='Stock Comparison'):
    """
    Create a comparison chart for multiple stocks.
    
    Args:
        data_dict (dict): Dictionary with stock symbols as keys and their data as values
        title (str): Chart title
    
    Returns:
        dict: JSON representation of the chart
    """
    try:
        fig = go.Figure()
        
        # Process each stock
        for symbol, data in data_dict.items():
            if not data['success'] or not data['data']:
                continue
            
            # Convert to DataFrame if it's a list of dictionaries
            if isinstance(data['data'], list):
                df = pd.DataFrame(data['data'])
            else:
                df = data['data']
            
            # Normalize prices to percentage change from first day
            first_price = df['Close'].iloc[0]
            df['Normalized'] = (df['Close'] / first_price - 1) * 100
            
            # Add to chart
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['Normalized'],
                mode='lines',
                name=symbol
            ))
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title='Date',
            yaxis_title='Percentage Change (%)',
            template='plotly_white',
            legend=dict(
                orientation='h',
                y=1.1
            )
        )
        
        return json.dumps(fig.to_dict())
    except Exception as e:
        print(f"Error creating comparison chart: {str(e)}")
        return json.dumps({'data': [], 'layout': {'title': 'Error creating chart'}})

def create_indicator_chart(data, indicator_data, indicator_name, title='Technical Indicator'):
    """
    Create a chart for a technical indicator.
    
    Args:
        data (dict): Dictionary containing stock data
        indicator_data (list or dict): Indicator data
        indicator_name (str): Name of the indicator
        title (str): Chart title
    
    Returns:
        dict: JSON representation of the chart
    """
    try:
        if not data['success'] or not data['data']:
            return json.dumps({'data': [], 'layout': {'title': 'No data available'}})
        
        # Convert to DataFrame if it's a list of dictionaries
        if isinstance(data['data'], list):
            df = pd.DataFrame(data['data'])
        else:
            df = data['data']
        
        # Create figure with subplots
        fig = go.Figure()
        
        # Add price subplot
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color='#2c7be5', width=2)
        ))
        
        # Handle different indicator types
        if indicator_name.lower() == 'rsi':
            # Add RSI subplot
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=[indicator_data] * len(df),  # Use the same value for all dates
                mode='lines',
                name='RSI',
                yaxis='y2',
                line=dict(color='#e63946', width=2)
            ))
            
            # Add overbought/oversold lines
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=[70] * len(df),
                mode='lines',
                name='Overbought (70)',
                yaxis='y2',
                line=dict(color='rgba(231, 76, 60, 0.5)', width=1, dash='dash')
            ))
            
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=[30] * len(df),
                mode='lines',
                name='Oversold (30)',
                yaxis='y2',
                line=dict(color='rgba(46, 204, 113, 0.5)', width=1, dash='dash')
            ))
            
            # Update layout
            fig.update_layout(
                title=title,
                xaxis_title='Date',
                yaxis_title='Price',
                template='plotly_white',
                yaxis=dict(
                    domain=[0.3, 1]
                ),
                yaxis2=dict(
                    domain=[0, 0.2],
                    title='RSI',
                    range=[0, 100]
                ),
                legend=dict(
                    orientation='h',
                    y=1.1
                )
            )
        elif indicator_name.lower() == 'macd':
            # Add MACD subplot
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=[indicator_data['macd']] * len(df),
                mode='lines',
                name='MACD',
                yaxis='y2',
                line=dict(color='#3498db', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=[indicator_data['signal']] * len(df),
                mode='lines',
                name='Signal',
                yaxis='y2',
                line=dict(color='#e67e22', width=2)
            ))
            
            # Update layout
            fig.update_layout(
                title=title,
                xaxis_title='Date',
                yaxis_title='Price',
                template='plotly_white',
                yaxis=dict(
                    domain=[0.3, 1]
                ),
                yaxis2=dict(
                    domain=[0, 0.2],
                    title='MACD'
                ),
                legend=dict(
                    orientation='h',
                    y=1.1
                )
            )
        else:
            # Generic indicator
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=[indicator_data] * len(df),
                mode='lines',
                name=indicator_name,
                yaxis='y2',
                line=dict(color='#e63946', width=2)
            ))
            
            # Update layout
            fig.update_layout(
                title=title,
                xaxis_title='Date',
                yaxis_title='Price',
                template='plotly_white',
                yaxis=dict(
                    domain=[0.3, 1]
                ),
                yaxis2=dict(
                    domain=[0, 0.2],
                    title=indicator_name
                ),
                legend=dict(
                    orientation='h',
                    y=1.1
                )
            )
        
        return json.dumps(fig.to_dict())
    except Exception as e:
        print(f"Error creating indicator chart: {str(e)}")
        return json.dumps({'data': [], 'layout': {'title': 'Error creating chart'}}) 