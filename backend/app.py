from flask import Flask, request, jsonify, send_from_directory, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from web3 import Web3
from cryptography.fernet import Fernet
import os
import logging
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Load the encryption key from environment variable
encryption_key = os.environ.get('ENCRYPTION_KEY')
if not encryption_key:
    raise ValueError("No ENCRYPTION_KEY set for Flask application")

cipher_suite = Fernet(encryption_key.encode())

# File upload configuration
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Connect to Ganache
web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
web3.eth.defaultAccount = web3.eth.accounts[0]


# Load the ABI
abi_path = r'C:\Users\vinay\doc_verification\build\contracts\DocumentVerification.json' 
try:
    with open(abi_path) as f:
         contract_data = json.load(f)
         contract_abi = contract_data['abi']
         contract_address = '0xa1610c0e93FA9bA085C879BF13695E8e2983c405'
except FileNotFoundError:
    logging.error(f"ABI file not found at path: {abi_path}")
    exit(1)
except json.JSONDecodeError:
    logging.error(f"Error decoding JSON from the ABI file: {abi_path}")
    exit(1)
except Exception as e:
    logging.error(f"An unexpected error occurred: {e}")
    exit(1)
   

    

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    sensitive_data = db.Column(db.String(500)) # Example sensitive data

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_sensitive_data(self, data):
        self.sensitive_data = cipher_suite.encrypt(data.encode())

    def get_sensitive_data(self):
        return cipher_suite.decrypt(self.sensitive_data).decode()

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    document_hash = db.Column(db.String(300), nullable=False)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(300), nullable=False)

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/upload')
@login_required
def upload_page():
    return send_from_directory('.', 'upload.html')

@app.route('/verify')
@login_required
def verify_page():
    if current_user.email != 'dev@gmail.com':
        return jsonify({'message': 'Access denied'}), 403
    return send_from_directory('.', 'verify.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']
    sensitive_info = data.get('sensitive_info', '')  # Assuming there's sensitive info in the request

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    password_hash = generate_password_hash(password)
    new_user = User(username=username, email=email, password_hash=password_hash)
    new_user.set_sensitive_data(sensitive_info)

    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify({'message': 'Logged in'})
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_document():
    data = request.get_json()
    document_hash = data['hash']
    
    # Check if the document already exists
    exists = contract.functions.verifyDocument(document_hash).call()
    if exists:
        return jsonify({'message': 'Document already exists'}), 400
    
    tx_hash = contract.functions.uploadDocument(document_hash).transact({
        'from': web3.eth.defaultAccount
    })
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    
    # Save document ownership
    new_document = Document(user_id=current_user.id, document_hash=document_hash)
    db.session.add(new_document)
    db.session.commit()
    
    # Add notification
    new_notification = Notification(message=f"New document uploaded with hash: {document_hash}")
    db.session.add(new_notification)
    db.session.commit()
    
    return jsonify({'message': 'Document uploaded', 'hash': document_hash, 'transaction_hash': receipt.transactionHash.hex()})

@app.route('/revoke', methods=['POST'])
@login_required
def revoke_document():
    data = request.get_json()
    document_hash = data['hash']
    
    # Check if the document exists and belongs to the current user
    document = Document.query.filter_by(document_hash=document_hash, user_id=current_user.id).first()
    if not document:
        return jsonify({'message': 'Document not found or access denied'}), 404
    
    tx_hash = contract.functions.revokeDocument(document_hash).transact({
        'from': web3.eth.defaultAccount
    })
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    
    # Remove document from database
    db.session.delete(document)
    db.session.commit()
    
    return jsonify({'message': 'Document revoked', 'transaction_hash': receipt.transactionHash.hex()})

@app.route('/verify_document', methods=['GET'])
@login_required
def verify_document():
    if current_user.email != 'dev@gmail.com':
        return jsonify({'message': 'Access denied'}), 403
    document_hash = request.args.get('hash')
    logging.debug(f"Verifying document with hash: {document_hash}")
    try:
        exists = contract.functions.verifyDocument(document_hash).call()
        logging.debug(f"Document exists: {exists}")
        return jsonify({'exists': exists})
    except Exception as e:
        logging.error(f"Error verifying document: {e}")
        return jsonify({'message': 'Verification failed'}), 500

@app.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    if current_user.email != 'dev@gmail.com':
        return jsonify({'message': 'Access denied'}), 403
    notifications = Notification.query.all()
    return jsonify({'notifications': [n.message for n in notifications]})

if __name__ == '__main__':
    app.run(debug=True, ssl_context=('C:\\Users\\vinay\\Downloads\\nginx-1.26.1\\nginx-selfsigned.crt', 'C:\\Users\\vinay\\Downloads\\nginx-1.26.1\\nginx-selfsigned.key'))