from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    """User model for authentication and profile."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    watchlists = db.relationship('Watchlist', backref='user', lazy='dynamic')
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Stock(db.Model):
    """Stock model for storing stock information."""
    __tablename__ = 'stocks'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, index=True)
    name = db.Column(db.String(100))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    watchlist_stocks = db.relationship('WatchlistStock', backref='stock', lazy='dynamic')
    
    def __repr__(self):
        return f'<Stock {self.symbol}>'

class Watchlist(db.Model):
    """Watchlist model for user's stock watchlists."""
    __tablename__ = 'watchlists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    stocks = db.relationship('WatchlistStock', backref='watchlist', lazy='dynamic')
    
    def __repr__(self):
        return f'<Watchlist {self.name}>'

class WatchlistStock(db.Model):
    """Association model between Watchlist and Stock."""
    __tablename__ = 'watchlist_stocks'
    
    id = db.Column(db.Integer, primary_key=True)
    watchlist_id = db.Column(db.Integer, db.ForeignKey('watchlists.id'))
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<WatchlistStock {self.watchlist_id}:{self.stock_id}>' 