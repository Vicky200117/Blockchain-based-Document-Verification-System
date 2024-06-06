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
3. ** Install Truffle and Ganache:
      Install Truffle globally:
   ```sh
   npm install -g truffle
   ```
   Download and install Ganache from the official website.
4.** Compile and deploy the smart contract:
  Start Ganache.
  In the backend directory, run:
  ```sh
  truffle migrate --reset
  ```

5. **Run the Flask app**:
    ```sh
    python app.py
    ```
## Usage
1.Open the application:
  Navigate to https://127.0.0.1:5000 in your web browser.

2.Register and login:
  - Create a new account.
  - Log in using your credentials.

3.Upload a document:
  - Navigate to the upload page.
  - Upload a document by providing the necessary details.

4.Verify a document:
  - Navigate to the verify page.
  - Enter the document hash to verify its existence on the blockchain.


