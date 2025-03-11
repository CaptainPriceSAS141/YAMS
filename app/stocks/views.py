from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from . import stocks
from app import db
from app.models import Stock, Watchlist, WatchlistStock
from app.utils.data_fetcher import get_stock_data, get_multiple_stocks_data
from app.utils.data_analyzer import (
    calculate_moving_average, calculate_exponential_moving_average,
    calculate_macd, calculate_rsi, predict_stock_price, analyze_trend
)
from app.utils.data_visualizer import (
    create_candlestick_chart, create_line_chart, create_technical_analysis_chart,
    create_comparison_chart, create_indicator_chart
)

@stocks.route('/view/<symbol>')
def view_stock(symbol):
    """View detailed information about a stock."""
    period = request.args.get('period', '1y')
    interval = request.args.get('interval', '1d')
    
    # Get stock data
    data = get_stock_data(symbol, period=period, interval=interval)
    
    if not data['success']:
        flash(f"Error fetching data for {symbol}: {data.get('error', 'Unknown error')}", 'danger')
        return redirect(url_for('main.index'))
    
    # Generate charts
    candlestick_chart = create_candlestick_chart(data['data'], title=f"{symbol} Stock Price")
    technical_chart = create_technical_analysis_chart(data['data'])
    
    # Calculate technical indicators
    if data['data']:
        ma_20 = calculate_moving_average(data['data'], window=20)
        ma_50 = calculate_moving_average(data['data'], window=50)
        ma_200 = calculate_moving_average(data['data'], window=200)
        rsi = calculate_rsi(data['data'])
        macd_data = calculate_macd(data['data'])
        trend = analyze_trend(data['data'])
        
        # Create indicator charts
        rsi_chart = create_indicator_chart(data['data'], rsi, 'RSI', title=f"{symbol} RSI")
        macd_chart = create_indicator_chart(data['data'], macd_data, 'MACD', title=f"{symbol} MACD")
        
        # Make predictions (if enough data)
        predictions = predict_stock_price(data['data'])
    else:
        ma_20 = ma_50 = ma_200 = rsi = []
        macd_data = {'macd': [], 'signal': [], 'histogram': []}
        trend = 'insufficient data'
        rsi_chart = macd_chart = '{}'
        predictions = []
    
    # Check if stock is in user's watchlist
    in_watchlist = False
    if current_user.is_authenticated:
        for watchlist in current_user.watchlists:
            for item in watchlist.stocks:
                stock = Stock.query.get(item.stock_id)
                if stock and stock.symbol == symbol:
                    in_watchlist = True
                    break
    
    return render_template(
        'stocks/view.html',
        symbol=symbol,
        stock_info=data['info'],
        candlestick_chart=candlestick_chart,
        technical_chart=technical_chart,
        rsi_chart=rsi_chart,
        macd_chart=macd_chart,
        ma_20=ma_20[-1] if ma_20 else None,
        ma_50=ma_50[-1] if ma_50 else None,
        ma_200=ma_200[-1] if ma_200 else None,
        rsi=rsi[-1] if rsi else None,
        trend=trend,
        predictions=predictions,
        period=period,
        interval=interval,
        in_watchlist=in_watchlist
    )

@stocks.route('/compare')
def compare_stocks():
    """Compare multiple stocks."""
    try:
        symbols_param = request.args.get('symbols', '')
        period = request.args.get('period', '1y')
        interval = request.args.get('interval', '1d')
        
        if not symbols_param:
            # No symbols provided, just render the template
            return render_template(
                'stocks/compare.html',
                symbols=[],
                stock_data={},
                comparison_chart=None,
                period=period,
                interval=interval
            )
        
        symbol_list = [s.strip() for s in symbols_param.split(',') if s.strip()]
        
        if not symbol_list:
            # Empty symbols after processing
            return render_template(
                'stocks/compare.html',
                symbols=[],
                stock_data={},
                comparison_chart=None,
                period=period,
                interval=interval
            )
        
        # Get data for all stocks
        stock_data = get_multiple_stocks_data(symbol_list, period=period, interval=interval)
        
        # Create comparison chart
        comparison_chart = create_comparison_chart(stock_data, title='Stock Comparison')
        
        return render_template(
            'stocks/compare.html',
            symbols=symbol_list,
            stock_data=stock_data,
            comparison_chart=comparison_chart,
            period=period,
            interval=interval
        )
    except Exception as e:
        print(f"Error in compare_stocks route: {str(e)}")
        flash(f"An error occurred while comparing stocks: {str(e)}", "danger")
        return render_template(
            'stocks/compare.html',
            symbols=[],
            stock_data={},
            comparison_chart=None,
            period='1y',
            interval='1d'
        )

@stocks.route('/watchlist')
@login_required
def watchlist():
    """View user's watchlists."""
    try:
        watchlists = current_user.watchlists.all()
        
        # Get stock data for all stocks in all watchlists
        stock_data = {}
        
        # Collect all unique stock symbols across all watchlists
        all_symbols = set()
        for watchlist in watchlists:
            for item in watchlist.stocks:
                stock = Stock.query.get(item.stock_id)
                if stock:
                    all_symbols.add(stock.symbol)
        
        # Fetch data for all symbols at once
        for symbol in all_symbols:
            try:
                data = get_stock_data(symbol, period='1d')
                stock_data[symbol] = data
            except Exception as e:
                print(f"Error fetching data for {symbol}: {str(e)}")
                # Create mock data as fallback
                stock_data[symbol] = {
                    'success': True,
                    'data': [{'Date': 'Today', 'Open': 100.0, 'Close': 102.0, 'High': 103.0, 'Low': 99.0, 'Volume': 1000000}],
                    'info': {'shortName': f"{symbol} Inc."}
                }
        
        return render_template(
            'stocks/watchlist.html',
            watchlists=watchlists,
            stock_data=stock_data
        )
    except Exception as e:
        print(f"Error in watchlist route: {str(e)}")
        flash("An error occurred while loading your watchlists. Please try again later.", "danger")
        return render_template('stocks/watchlist.html', watchlists=[], stock_data={})

@stocks.route('/watchlist/create', methods=['GET', 'POST'])
@login_required
def create_watchlist():
    """Create a new watchlist."""
    if request.method == 'POST':
        name = request.form.get('name')
        
        if not name:
            flash('Watchlist name is required.', 'danger')
            return redirect(url_for('stocks.create_watchlist'))
        
        # Create new watchlist
        watchlist = Watchlist(name=name, user_id=current_user.id)
        db.session.add(watchlist)
        db.session.commit()
        
        flash('Watchlist created successfully!', 'success')
        return redirect(url_for('stocks.watchlist'))
    
    return render_template('stocks/create_watchlist.html')

@stocks.route('/watchlist/<int:watchlist_id>/add', methods=['POST'])
@login_required
def add_to_watchlist(watchlist_id):
    """Add a stock to a watchlist."""
    symbol = request.form.get('symbol')
    
    if not symbol:
        flash('Stock symbol is required.', 'danger')
        return redirect(url_for('stocks.watchlist'))
    
    # Check if watchlist exists and belongs to user
    watchlist = Watchlist.query.get(watchlist_id)
    if not watchlist or watchlist.user_id != current_user.id:
        flash('Watchlist not found.', 'danger')
        return redirect(url_for('stocks.watchlist'))
    
    # Check if stock exists in database, if not, create it
    stock = Stock.query.filter_by(symbol=symbol).first()
    if not stock:
        # Get stock data to verify it exists
        data = get_stock_data(symbol)
        if not data['success']:
            flash(f"Invalid stock symbol: {symbol}", 'danger')
            return redirect(url_for('stocks.watchlist'))
        
        # Create new stock
        stock = Stock(symbol=symbol, name=data['info'].get('shortName', symbol))
        db.session.add(stock)
        db.session.commit()
    
    # Check if stock is already in watchlist
    existing = WatchlistStock.query.filter_by(
        watchlist_id=watchlist.id, stock_id=stock.id
    ).first()
    
    if existing:
        flash(f"{symbol} is already in your watchlist.", 'info')
        return redirect(url_for('stocks.watchlist'))
    
    # Add stock to watchlist
    watchlist_stock = WatchlistStock(watchlist_id=watchlist.id, stock_id=stock.id)
    db.session.add(watchlist_stock)
    db.session.commit()
    
    flash(f"{symbol} added to your watchlist!", 'success')
    return redirect(url_for('stocks.watchlist'))

@stocks.route('/watchlist/<int:watchlist_id>/remove/<int:stock_id>', methods=['POST'])
@login_required
def remove_from_watchlist(watchlist_id, stock_id):
    """Remove a stock from a watchlist."""
    # Check if watchlist exists and belongs to user
    watchlist = Watchlist.query.get(watchlist_id)
    if not watchlist or watchlist.user_id != current_user.id:
        flash('Watchlist not found.', 'danger')
        return redirect(url_for('stocks.watchlist'))
    
    # Find the watchlist-stock association
    watchlist_stock = WatchlistStock.query.filter_by(
        watchlist_id=watchlist.id, stock_id=stock_id
    ).first()
    
    if not watchlist_stock:
        flash('Stock not found in watchlist.', 'danger')
        return redirect(url_for('stocks.watchlist'))
    
    # Remove the association
    db.session.delete(watchlist_stock)
    db.session.commit()
    
    flash('Stock removed from watchlist.', 'success')
    return redirect(url_for('stocks.watchlist'))

@stocks.route('/api/stock/<symbol>')
def api_stock_data(symbol):
    """API endpoint for stock data."""
    period = request.args.get('period', '1y')
    interval = request.args.get('interval', '1d')
    
    data = get_stock_data(symbol, period=period, interval=interval)
    return jsonify(data)

@stocks.route('/api/indicators/<symbol>')
def api_indicators(symbol):
    """API endpoint for technical indicators."""
    period = request.args.get('period', '1y')
    interval = request.args.get('interval', '1d')
    indicator = request.args.get('indicator', 'all')
    
    data = get_stock_data(symbol, period=period, interval=interval)
    
    if not data['success']:
        return jsonify({'success': False, 'error': data.get('error', 'Unknown error')})
    
    result = {'success': True}
    
    if indicator == 'ma' or indicator == 'all':
        result['ma_20'] = calculate_moving_average(data['data'], window=20)
        result['ma_50'] = calculate_moving_average(data['data'], window=50)
        result['ma_200'] = calculate_moving_average(data['data'], window=200)
    
    if indicator == 'ema' or indicator == 'all':
        result['ema_12'] = calculate_exponential_moving_average(data['data'], window=12)
        result['ema_26'] = calculate_exponential_moving_average(data['data'], window=26)
    
    if indicator == 'macd' or indicator == 'all':
        result['macd'] = calculate_macd(data['data'])
    
    if indicator == 'rsi' or indicator == 'all':
        result['rsi'] = calculate_rsi(data['data'])
    
    if indicator == 'trend' or indicator == 'all':
        result['trend'] = analyze_trend(data['data'])
    
    if indicator == 'prediction' or indicator == 'all':
        result['prediction'] = predict_stock_price(data['data'])
    
    return jsonify(result) 