# Blockchain-based Document Verification System

This project is a blockchain-based document verification system built with Flask and Solidity. The system allows for the secure storage and verification of documents such as academic certificates and legal contracts.

## Features

- User registration and login
- Document upload and storage
- Document verification
- Secure communication protocols and data encryption

## Prerequisites

- Python 3.x
- Node.js and npm
- Ganache (for local Ethereum blockchain)
- Truffle

## Installation

1. **Clone the repository**:
   ```sh
   git clone https://github.com/Vicky200117/Blockchain-based-Document-Verification-System.git
   cd Blockchain-based-Document-Verification-System
   ```
 2. **Install backend dependencies**:
    ```sh
    cd backend
    pip install -r requirements.txt
    ```
3. **Deploy Smart Contracts**:
    ```sh
    truffle migrate --reset
    ```
4. **Run the Flask app**:
    ```sh
    python app.py
    ```
## Usage
Open the application:
Navigate to https://127.0.0.1:5000 in your web browser.

Register and login:
Create a new account and log in.

Upload a document:
Navigate to the upload page and upload a document.

Verify a document:
Navigate to the verify page and enter the document hash to verify its existence.

## Contributing
Contributions are welcome! Please fork this repository and submit pull requests.

## License
This project is licensed under the MIT License.

