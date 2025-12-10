"""
Blockchain Integration Module for Hospital Patient Portal
==========================================================
Connects Flask application to Ganache local blockchain.
Provides functions to store and verify medical record hashes.
"""

import json
import hashlib
import os
from datetime import datetime
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from eth_account import Account
from dotenv import load_dotenv

load_dotenv()


class BlockchainManager:
    """
    Manages blockchain interactions for medical records.
    Uses Ganache local blockchain for development.
    """
    
    def __init__(self, ganache_url=None, contract_address=None, private_key=None):
        """
        Initialize blockchain connection.
        
        Args:
            ganache_url: URL of Ganache instance (default: http://127.0.0.1:7545)
            contract_address: Deployed contract address
            private_key: Private key for signing transactions
        """
        self.ganache_url = ganache_url or os.environ.get('GANACHE_URL', 'http://127.0.0.1:7545')
        self.contract_address = contract_address or os.environ.get('CONTRACT_ADDRESS')
        self.private_key = private_key or os.environ.get('BLOCKCHAIN_PRIVATE_KEY')
        
        # Initialize Web3 connection
        self.w3 = Web3(Web3.HTTPProvider(self.ganache_url))
        
        # Add middleware for POA chains (Ganache)
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        
        # Contract ABI (will be loaded from compiled contract)
        self.contract_abi = None
        self.contract = None
        
        # Load contract if address is provided
        if self.contract_address:
            self._load_contract()
    
    def is_connected(self):
        """Check if connected to Ganache."""
        try:
            return self.w3.is_connected()
        except Exception:
            return False
    
    def get_accounts(self):
        """Get all available accounts from Ganache."""
        try:
            return self.w3.eth.accounts
        except Exception as e:
            print(f"Error getting accounts: {e}")
            return []
    
    def get_balance(self, address):
        """Get ETH balance of an address."""
        try:
            balance_wei = self.w3.eth.get_balance(address)
            return self.w3.from_wei(balance_wei, 'ether')
        except Exception as e:
            print(f"Error getting balance: {e}")
            return 0
    
    def _load_contract(self):
        """Load the deployed smart contract."""
        try:
            # Load ABI from compiled contract
            abi_path = os.path.join(os.path.dirname(__file__), 'contracts', 'PatientRecords.json')
            if os.path.exists(abi_path):
                with open(abi_path, 'r') as f:
                    contract_json = json.load(f)
                    self.contract_abi = contract_json.get('abi', contract_json)
            else:
                # Use embedded ABI if file not found
                self.contract_abi = self._get_embedded_abi()
            
            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contract_address),
                abi=self.contract_abi
            )
            return True
        except Exception as e:
            print(f"Error loading contract: {e}")
            return False
    
    def _get_embedded_abi(self):
        """Return embedded contract ABI."""
        return [
            {
                "inputs": [],
                "stateMutability": "nonpayable",
                "type": "constructor"
            },
            {
                "inputs": [{"name": "patientId", "type": "uint256"}, {"name": "dataHash", "type": "bytes32"}, {"name": "recordType", "type": "string"}],
                "name": "addRecord",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "patientId", "type": "uint256"}, {"name": "recordIndex", "type": "uint256"}, {"name": "dataHash", "type": "bytes32"}],
                "name": "verifyRecord",
                "outputs": [{"name": "", "type": "bool"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"name": "patientId", "type": "uint256"}, {"name": "recordIndex", "type": "uint256"}],
                "name": "getRecord",
                "outputs": [
                    {"name": "dataHash", "type": "bytes32"},
                    {"name": "timestamp", "type": "uint256"},
                    {"name": "createdBy", "type": "address"},
                    {"name": "recordType", "type": "string"},
                    {"name": "isActive", "type": "bool"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"name": "patientId", "type": "uint256"}],
                "name": "getPatientRecords",
                "outputs": [
                    {"name": "hashes", "type": "bytes32[]"},
                    {"name": "timestamps", "type": "uint256[]"},
                    {"name": "recordTypes", "type": "string[]"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"name": "patientId", "type": "uint256"}],
                "name": "patientRecordCount",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"name": "provider", "type": "address"}],
                "name": "authorizeProvider",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "provider", "type": "address"}],
                "name": "revokeProvider",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "", "type": "address"}],
                "name": "authorizedProviders",
                "outputs": [{"name": "", "type": "bool"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "owner",
                "outputs": [{"name": "", "type": "address"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "getAuditLogCount",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"name": "index", "type": "uint256"}],
                "name": "getAuditLog",
                "outputs": [
                    {"name": "patientId", "type": "uint256"},
                    {"name": "accessor", "type": "address"},
                    {"name": "action", "type": "string"},
                    {"name": "timestamp", "type": "uint256"},
                    {"name": "recordHash", "type": "bytes32"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"name": "patientId", "type": "uint256"}],
                "name": "getPatientAuditLogs",
                "outputs": [
                    {"name": "accessors", "type": "address[]"},
                    {"name": "actions", "type": "string[]"},
                    {"name": "timestamps", "type": "uint256[]"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"name": "patientId", "type": "uint256"}, {"name": "action", "type": "string"}, {"name": "recordHash", "type": "bytes32"}],
                "name": "logAccess",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
    
    def set_contract_address(self, address):
        """Set contract address and load it."""
        self.contract_address = address
        return self._load_contract()
    
    @staticmethod
    def generate_hash(data):
        """
        Generate SHA-256 hash of data for blockchain storage.
        
        Args:
            data: Can be string, dict, or bytes
            
        Returns:
            bytes32 hash suitable for blockchain
        """
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True, default=str)
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        hash_bytes = hashlib.sha256(data).digest()
        return hash_bytes
    
    @staticmethod
    def hash_to_hex(hash_bytes):
        """Convert hash bytes to hex string."""
        return '0x' + hash_bytes.hex()
    
    def add_record(self, patient_id, data, record_type, account_address=None):
        """
        Add a medical record hash to blockchain.
        
        Args:
            patient_id: Patient ID from database
            data: Medical record data (will be hashed)
            record_type: Type of record (VISIT, BILL, REPORT, PATIENT_INFO)
            account_address: Address to send transaction from
            
        Returns:
            dict with transaction hash and data hash
        """
        if not self.contract:
            raise Exception("Contract not loaded. Deploy contract first.")
        
        # Generate hash of the data
        data_hash = self.generate_hash(data)
        
        # Use first Ganache account if none specified
        if not account_address:
            account_address = self.w3.eth.accounts[0]
        
        try:
            # Build transaction
            tx = self.contract.functions.addRecord(
                patient_id,
                data_hash,
                record_type
            ).build_transaction({
                'from': account_address,
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(account_address)
            })
            
            # Sign and send transaction
            if self.private_key:
                signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            else:
                # For Ganache, accounts are unlocked by default
                tx_hash = self.w3.eth.send_transaction(tx)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                'success': True,
                'transaction_hash': tx_hash.hex(),
                'data_hash': self.hash_to_hex(data_hash),
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_record(self, patient_id, record_index, data):
        """
        Verify if a record matches what's stored on blockchain.
        
        Args:
            patient_id: Patient ID
            record_index: Index of the record on blockchain
            data: Data to verify
            
        Returns:
            bool: True if data matches blockchain record
        """
        if not self.contract:
            raise Exception("Contract not loaded")
        
        data_hash = self.generate_hash(data)
        
        try:
            is_valid = self.contract.functions.verifyRecord(
                patient_id,
                record_index,
                data_hash
            ).call()
            return is_valid
        except Exception as e:
            print(f"Verification error: {e}")
            return False
    
    def get_patient_records(self, patient_id, account_address=None):
        """
        Get all records for a patient from blockchain.
        
        Args:
            patient_id: Patient ID
            account_address: Address making the call
            
        Returns:
            list of records with hashes and timestamps
        """
        if not self.contract:
            raise Exception("Contract not loaded")
        
        if not account_address:
            account_address = self.w3.eth.accounts[0]
        
        try:
            hashes, timestamps, record_types = self.contract.functions.getPatientRecords(
                patient_id
            ).call({'from': account_address})
            
            records = []
            for i in range(len(hashes)):
                records.append({
                    'hash': '0x' + hashes[i].hex(),
                    'timestamp': datetime.fromtimestamp(timestamps[i]).isoformat(),
                    'record_type': record_types[i]
                })
            
            return records
        except Exception as e:
            print(f"Error getting records: {e}")
            return []
    
    def get_record_count(self, patient_id):
        """Get total record count for a patient."""
        if not self.contract:
            return 0
        
        try:
            return self.contract.functions.patientRecordCount(patient_id).call()
        except Exception:
            return 0
    
    def get_audit_logs(self, patient_id=None, account_address=None):
        """
        Get audit logs from blockchain.
        
        Args:
            patient_id: Optional patient ID to filter by
            account_address: Address making the call
            
        Returns:
            list of audit log entries
        """
        if not self.contract:
            raise Exception("Contract not loaded")
        
        if not account_address:
            account_address = self.w3.eth.accounts[0]
        
        try:
            if patient_id:
                accessors, actions, timestamps = self.contract.functions.getPatientAuditLogs(
                    patient_id
                ).call({'from': account_address})
                
                logs = []
                for i in range(len(accessors)):
                    logs.append({
                        'patient_id': patient_id,
                        'accessor': accessors[i],
                        'action': actions[i],
                        'timestamp': datetime.fromtimestamp(timestamps[i]).isoformat()
                    })
                return logs
            else:
                # Get all logs
                count = self.contract.functions.getAuditLogCount().call()
                logs = []
                for i in range(count):
                    pid, accessor, action, timestamp, record_hash = self.contract.functions.getAuditLog(
                        i
                    ).call({'from': account_address})
                    logs.append({
                        'patient_id': pid,
                        'accessor': accessor,
                        'action': action,
                        'timestamp': datetime.fromtimestamp(timestamp).isoformat(),
                        'record_hash': '0x' + record_hash.hex()
                    })
                return logs
        except Exception as e:
            print(f"Error getting audit logs: {e}")
            return []
    
    def is_provider_authorized(self, address):
        """Check if an address is an authorized provider."""
        if not self.contract:
            return False
        
        try:
            return self.contract.functions.authorizedProviders(
                Web3.to_checksum_address(address)
            ).call()
        except Exception:
            return False
    
    def get_contract_owner(self):
        """Get the contract owner address."""
        if not self.contract:
            return None
        
        try:
            return self.contract.functions.owner().call()
        except Exception:
            return None


# Singleton instance for Flask app
blockchain_manager = None


def init_blockchain(app=None):
    """
    Initialize blockchain manager for Flask app.
    
    Args:
        app: Flask application instance
        
    Returns:
        BlockchainManager instance
    """
    global blockchain_manager
    
    ganache_url = None
    contract_address = None
    private_key = None
    
    if app:
        ganache_url = app.config.get('GANACHE_URL')
        contract_address = app.config.get('CONTRACT_ADDRESS')
        private_key = app.config.get('BLOCKCHAIN_PRIVATE_KEY')
    
    blockchain_manager = BlockchainManager(
        ganache_url=ganache_url,
        contract_address=contract_address,
        private_key=private_key
    )
    
    return blockchain_manager


def get_blockchain():
    """Get the blockchain manager instance."""
    global blockchain_manager
    if blockchain_manager is None:
        blockchain_manager = BlockchainManager()
    return blockchain_manager
