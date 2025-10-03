from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for Chrome extension communication

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['GITHUB_CLIENT_ID'] = os.getenv('GITHUB_CLIENT_ID')
app.config['GITHUB_CLIENT_SECRET'] = os.getenv('GITHUB_CLIENT_SECRET')

# Import and register routes
from routes.github_routes import github_bp
app.register_blueprint(github_bp, url_prefix='/api/github')

@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
