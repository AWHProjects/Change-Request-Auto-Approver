from flask import Flask
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///change_requests.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

# Import db from models and initialize with app
from models import db, ChangeRequest, ApprovalRule, AuditLog
db.init_app(app)

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Import routes after db initialization
from routes import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Initialize default approval rules if none exist
        if not ApprovalRule.query.first():
            from utils import initialize_default_rules
            initialize_default_rules()
    
    app.run(debug=True)