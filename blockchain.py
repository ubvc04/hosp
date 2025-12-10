"""
Blockchain Integration Module for Hospital Patient Portal
==========================================================
Connects Flask application to Ganache local blockchain.
Stores medical record hashes directly in transaction data.
"""

import json
import hashlib
import os
from datetime import datetime
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv

load_dotenv()


class BlockchainManager:
    """
    Manages blockchain interactions for medical records.
    Uses Ganache local blockchain - stores hashes in transaction data.
    """
    
    def __init__(self, ganache_url=None, contract_address=None, private_key=None):
        """Initialize blockchain connection."""
        self.ganache_url = ganache_url or os.environ.get('GANACHE_URL', 'http://127.0.0.1:7545')
        self.contract_address = contract_address or os.environ.get('CONTRACT_ADDRESS')
        self.private_key = private_key or os.environ.get('BLOCKCHAIN_PRIVATE_KEY')
        
        # Initialize Web3 connection
        self.w3 = Web3(Web3.HTTPProvider(self.ganache_url))
        
        # For compatibility - contract won't be used for storage
        self.contract = True if self.contract_address else None
        self.contract_abi = []
        
        # In-memory record tracking (for demo - in production use database)
        self._records_file = os.path.join(os.path.dirname(__file__), 'instance', 'blockchain_records.json')
        self._load_records()
    
    def _load_records(self):
        """Load records from file."""
        self._records = {
            'transactions': [],
            'patients': {},
            'audit_logs': []
        }
        try:
            if os.path.exists(self._records_file):
                with open(self._records_file, 'r') as f:
                    self._records = json.load(f)
        except:
            pass
    
    def _save_records(self):
        """Save records to file."""
        try:
            os.makedirs(os.path.dirname(self._records_file), exist_ok=True)
            with open(self._records_file, 'w') as f:
                json.dump(self._records, f, indent=2)
        except Exception as e:
            print(f"Error saving records: {e}")
    
    def is_connected(self):
        """Check if connected to Ganache."""
        try:
            return self.w3.is_connected()
        except:
            return False
    
    def get_accounts(self):
        """Get all available accounts from Ganache."""
        try:
            return self.w3.eth.accounts
        except:
            return []
    
    def get_balance(self, address):
        """Get ETH balance of an address."""
        try:
            balance_wei = self.w3.eth.get_balance(address)
            return float(self.w3.from_wei(balance_wei, 'ether'))
        except:
            return 0
    
    def get_contract_owner(self):
        """Get the first account as contract owner."""
        accounts = self.get_accounts()
        return accounts[0] if accounts else None
    
    @staticmethod
    def generate_hash(data):
        """Generate SHA-256 hash of data."""
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True, default=str)
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).digest()
    
    @staticmethod
    def hash_to_hex(hash_bytes):
        """Convert hash bytes to hex string."""
        if isinstance(hash_bytes, bytes):
            return '0x' + hash_bytes.hex()
        return hash_bytes
    
    def add_record(self, patient_id, data, record_type, account_address=None):
        """
        Add a medical record hash to blockchain.
        Stores hash in transaction data field.
        """
        if not self.is_connected():
            return {'success': False, 'error': 'Not connected to Ganache'}
        
        # Generate hash of the data
        data_hash = self.generate_hash(data)
        data_hash_hex = self.hash_to_hex(data_hash)
        
        # Get account
        if self.private_key:
            account = Account.from_key(self.private_key)
            from_address = account.address
        else:
            accounts = self.get_accounts()
            if not accounts:
                return {'success': False, 'error': 'No accounts available'}
            from_address = accounts[0]
        
        try:
            # Create transaction data
            tx_data = {
                'patient_id': patient_id,
                'record_type': record_type,
                'data_hash': data_hash_hex,
                'timestamp': datetime.now().isoformat()
            }
            tx_data_encoded = '0x' + json.dumps(tx_data).encode().hex()
            
            # Build transaction - send to contract address (or self if no contract)
            to_address = self.contract_address or from_address
            
            tx = {
                'from': from_address,
                'to': Web3.to_checksum_address(to_address),
                'value': 0,
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(from_address),
                'chainId': self.w3.eth.chain_id,
                'data': tx_data_encoded
            }
            
            # Sign and send transaction
            if self.private_key:
                signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
                # Handle different web3 versions
                raw_tx = getattr(signed_tx, 'rawTransaction', None) or getattr(signed_tx, 'raw_transaction', None)
                tx_hash = self.w3.eth.send_raw_transaction(raw_tx)
            else:
                tx_hash = self.w3.eth.send_transaction(tx)
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Store record locally for tracking
            record = {
                'patient_id': patient_id,
                'record_type': record_type,
                'data_hash': data_hash_hex,
                'tx_hash': tx_hash.hex(),
                'block_number': receipt['blockNumber'],
                'timestamp': datetime.now().isoformat(),
                'gas_used': receipt['gasUsed']
            }
            
            self._records['transactions'].append(record)
            
            # Track by patient
            pid_str = str(patient_id)
            if pid_str not in self._records['patients']:
                self._records['patients'][pid_str] = []
            self._records['patients'][pid_str].append(record)
            
            # Add audit log
            self._records['audit_logs'].append({
                'patient_id': patient_id,
                'action': f'ADD_{record_type}',
                'accessor': from_address,
                'timestamp': datetime.now().isoformat(),
                'tx_hash': tx_hash.hex()
            })
            
            self._save_records()
            
            return {
                'success': True,
                'transaction_hash': tx_hash.hex(),
                'data_hash': data_hash_hex,
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_record(self, patient_id, record_index, data):
        """Verify if a record matches what's stored."""
        pid_str = str(patient_id)
        if pid_str not in self._records['patients']:
            return False
        
        records = self._records['patients'][pid_str]
        if record_index >= len(records):
            return False
        
        stored_hash = records[record_index]['data_hash']
        data_hash = self.hash_to_hex(self.generate_hash(data))
        
        return stored_hash == data_hash
    
    def get_patient_records(self, patient_id):
        """Get all records for a patient."""
        pid_str = str(patient_id)
        records = self._records['patients'].get(pid_str, [])
        return [
            {
                'hash': r['data_hash'],
                'timestamp': r['timestamp'],
                'record_type': r['record_type'],
                'tx_hash': r['tx_hash'],
                'block_number': r['block_number']
            }
            for r in records
        ]
    
    def get_record_count(self, patient_id):
        """Get total record count for a patient."""
        pid_str = str(patient_id)
        return len(self._records['patients'].get(pid_str, []))
    
    def get_audit_logs(self, patient_id=None):
        """Get audit logs."""
        logs = self._records['audit_logs']
        if patient_id:
            logs = [l for l in logs if l['patient_id'] == patient_id]
        return logs
    
    def get_total_records(self):
        """Get total number of records on blockchain."""
        return len(self._records['transactions'])
    
    def get_total_patients(self):
        """Get number of patients with blockchain records."""
        return len(self._records['patients'])
    
    def get_all_transactions(self):
        """Get all blockchain transactions."""
        return self._records['transactions']
    
    def is_provider_authorized(self, address):
        """Check if provider is authorized (always true for demo)."""
        return True
    
    def get_transaction_from_blockchain(self, tx_hash):
        """Get transaction details from Ganache."""
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            # Decode data
            data_hex = tx.input.hex() if hasattr(tx.input, 'hex') else tx.input
            if data_hex.startswith('0x'):
                data_hex = data_hex[2:]
            
            try:
                data_json = bytes.fromhex(data_hex).decode('utf-8')
                data = json.loads(data_json)
            except:
                data = {'raw': data_hex[:100] + '...'}
            
            return {
                'hash': tx_hash if isinstance(tx_hash, str) else tx_hash.hex(),
                'from': tx['from'],
                'to': tx['to'],
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed'],
                'data': data,
                'status': 'Success' if receipt['status'] == 1 else 'Failed'
            }
        except Exception as e:
            return {'error': str(e)}


# Singleton instance
blockchain_manager = None


def init_blockchain(app=None):
    """Initialize blockchain manager for Flask app."""
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
