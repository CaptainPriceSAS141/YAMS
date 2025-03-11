from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from . import main
from app.models import Stock
from app.utils.data_fetcher import get_stock_data, search_stocks

@main.route('/test')
def test():
    """Simple test route."""
    return "Hello, World! The Flask app is working."

@main.route('/')
def index():
    """Render the homepage."""
    try:
        # Use a list of popular stocks
        popular_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
        stock_data = {}
        
        # Create mock data for each stock to ensure we always have something to display
        for symbol in popular_stocks:
            # Default mock data
            stock_data[symbol] = {
                'price': 150.0,
                'change': 2.5,
                'name': f"{symbol} Inc."
            }
            
            # Try to get real data, but use mock data as fallback
            try:
                data = get_stock_data(symbol, period='1mo')
                if data['success'] and data['data'] and len(data['data']) > 0:
                    latest_data = data['data'][-1]
                    stock_data[symbol] = {
                        'price': latest_data.get('Close', 150.0),
                        'change': latest_data.get('Close', 150.0) - latest_data.get('Open', 147.5),
                        'name': data['info'].get('shortName', f"{symbol} Inc.")
                    }
            except Exception as e:
                print(f"Error getting data for {symbol}: {str(e)}")
                # Keep using the mock data
        
        return render_template('index.html', stock_data=stock_data)
    except Exception as e:
        print(f"Error in index route: {str(e)}")
        # Create simple mock data as a last resort
        mock_data = {
            'AAPL': {'price': 182.52, 'change': 1.25, 'name': 'Apple Inc.'},
            'MSFT': {'price': 417.88, 'change': 3.45, 'name': 'Microsoft Corporation'},
            'GOOGL': {'price': 175.35, 'change': 2.10, 'name': 'Alphabet Inc.'},
            'AMZN': {'price': 178.75, 'change': 2.18, 'name': 'Amazon.com, Inc.'},
            'TSLA': {'price': 175.34, 'change': -1.22, 'name': 'Tesla, Inc.'}
        }
        return render_template('index.html', stock_data=mock_data)

@main.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')

@main.route('/dashboard')
@login_required
def dashboard():
    """Render the user dashboard."""
    return render_template('dashboard.html')

@main.route('/search')
def search():
    """Search for stocks."""
    query = request.args.get('q', '')
    if not query:
        return render_template('search.html', results=None)
    
    try:
        results = search_stocks(query)
        return render_template('search.html', results=results, query=query)
    except Exception as e:
        print(f"Error in search route: {str(e)}")
        flash(f"An error occurred during search: {str(e)}", "danger")
        return render_template('search.html', results=None, query=query)

@main.route('/api/search')
def api_search():
    """API endpoint for stock search."""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'success': False, 'error': 'No query provided'})
    
    try:
        results = search_stocks(query)
        return jsonify(results)
    except Exception as e:
        print(f"Error in API search: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}) 