import os
from app import create_app

# Get the configuration from environment variable or use default
config_name = os.environ.get('FLASK_ENV', 'default')
app = create_app(config_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 