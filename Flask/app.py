from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import groq
from routes.cv import cv_bp
from routes.chat import chat_bp
from routes.auth import auth_bp

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app) # Consider more specific CORS origins for production

# Configure database
app.config['POSTGRES_URL'] = os.getenv('POSTGRES_URL')

# Configure Groq API
app.config['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')

# Configure a secret key for session management or JWT
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_default_secret_key') # Add a SECRET_KEY to your .env

# Register blueprints
app.register_blueprint(cv_bp, url_prefix='/api/cv')
app.register_blueprint(chat_bp, url_prefix='/api/chat')
app.register_blueprint(auth_bp, url_prefix='/api/auth')

@app.route('/')
def index():
    return jsonify({"message": "Welcome to the CV Chatbot API"})

# The get_db_connection function has been moved to db_utils.py
# def get_db_connection():
#     conn = psycopg2.connect(current_app.config['POSTGRES_URL'])
#     return conn

if __name__ == '__main__':
    app.run(debug=True)