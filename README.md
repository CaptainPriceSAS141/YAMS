# Stock Market Trend Analysis Website

A web application for analyzing stock market trends, visualizing stock data, and making predictions using machine learning.

## Features

- Real-time stock data fetching using yfinance
- Interactive stock charts and visualizations
- Technical indicators (Moving Averages, MACD, RSI, etc.)
- User authentication and personalized watchlists
- Stock price prediction using machine learning

## Prerequisites

- Python 3.8+
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/stock-market-analysis.git
cd stock-market-analysis
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - On Windows:
   ```bash
   venv\Scripts\activate
   ```
   - On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. Install the required packages:
```bash
pip install -r requirements.txt
```

5. Set up environment variables:
```bash
cp .env.example .env
```
Then edit the `.env` file with your configuration.

## Running the Application

1. Initialize the database:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

2. Run the development server:
```bash
flask run
```

3. Open your browser and navigate to `http://127.0.0.1:5000/`

## Project Structure

```
stock-market-analysis/
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── templates/
│   ├── static/
│   └── utils/
│
├── migrations/
├── tests/
├── .env
├── .gitignore
├── requirements.txt
├── config.py
└── run.py
```

## Deployment

Instructions for deploying to Heroku:

1. Create a Heroku account and install the Heroku CLI
2. Login to Heroku:
```bash
heroku login
```
3. Create a new Heroku app:
```bash
heroku create your-app-name
```
4. Add a Procfile:
```
web: gunicorn run:app
```
5. Push to Heroku:
```bash
git push heroku main
```

## License

MIT

## Acknowledgements

- [yfinance](https://github.com/ranaroussi/yfinance) for providing stock data
- [Plotly](https://plotly.com/) for interactive visualizations
- [Flask](https://flask.palletsprojects.com/) for the web framework 