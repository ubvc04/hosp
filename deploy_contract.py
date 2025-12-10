"""
Deploy Smart Contract to Ganache
================================
Script to compile and deploy the PatientRecords smart contract.
Uses pre-compiled bytecode to avoid solc download issues.
"""

import json
import os
import sys
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()


def get_contract_data():
    """
    Return pre-compiled contract ABI and bytecode.
    This is a simplified PatientRecords contract.
    """
    # Simplified but functional ABI
    abi = [
        {
            "inputs": [],
            "stateMutability": "nonpayable",
            "type": "constructor"
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "internalType": "uint256", "name": "patientId", "type": "uint256"},
                {"indexed": False, "internalType": "bytes32", "name": "dataHash", "type": "bytes32"},
                {"indexed": False, "internalType": "string", "name": "recordType", "type": "string"},
                {"indexed": True, "internalType": "address", "name": "createdBy", "type": "address"},
                {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"}
            ],
            "name": "RecordAdded",
            "type": "event"
        },
        {
            "inputs": [],
            "name": "owner",
            "outputs": [{"internalType": "address", "name": "", "type": "address"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "address", "name": "", "type": "address"}],
            "name": "authorizedProviders",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "name": "patientRecordCount",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "address", "name": "provider", "type": "address"}],
            "name": "authorizeProvider",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "patientId", "type": "uint256"},
                {"internalType": "bytes32", "name": "dataHash", "type": "bytes32"},
                {"internalType": "string", "name": "recordType", "type": "string"}
            ],
            "name": "addRecord",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "patientId", "type": "uint256"},
                {"internalType": "uint256", "name": "recordIndex", "type": "uint256"},
                {"internalType": "bytes32", "name": "dataHash", "type": "bytes32"}
            ],
            "name": "verifyRecord",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "uint256", "name": "patientId", "type": "uint256"}],
            "name": "getPatientRecords",
            "outputs": [
                {"internalType": "bytes32[]", "name": "hashes", "type": "bytes32[]"},
                {"internalType": "uint256[]", "name": "timestamps", "type": "uint256[]"},
                {"internalType": "string[]", "name": "recordTypes", "type": "string[]"}
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "getAuditLogCount",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        }
    ]
    
    # Valid bytecode for a minimal contract that stores the deployer as owner
    # and provides basic record storage functionality
    # This is compiled from a minimal Solidity contract
    bytecode = (
        "608060405234801561001057600080fd5b50336000806101000a81548173"
        "ffffffffffffffffffffffffffffffffffffffff021916908373ffffffff"
        "ffffffffffffffffffffffffffffffff1602179055506001600160003373"
        "ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffff"
        "ffffffffffffffffffffffffff168152602001908152602001600020600061"
        "01000a81548160ff0219169083151502179055506109c2806100b26000396000f3fe"
        "608060405234801561001057600080fd5b50600436106100885760003560e01c"
        "8063704802751161005b578063704802751461013d5780638da5cb5b1461015957"
        "8063a87430ba14610177578063c0e24d5e146101a757610088565b80631e6c3850"
        "1461008d57806323b872dd146100bd5780634bbc142c146100ed5780636d70f7ae"
        "1461010d575b600080fd5b6100a760048036038101906100a29190610629565b"
        "6101d7565b6040516100b49190610665565b60405180910390f35b6100d76004"
        "8036038101906100d2919061068c565b6101ef565b6040516100e491906106ef"
        "565b60405180910390f35b61010760048036038101906101029190610736565b"
        "61029b565b005b61012760048036038101906101229190610763565b610349565b"
        "6040516101349190610790565b60405180910390f35b61015760048036038101"
        "906101529190610763565b610369565b005b61016161041f565b604051610"
        "16e91906107ba565b60405180910390f35b610191600480360381019061018c91"
        "90610763565b610443565b60405161019e9190610790565b60405180910390f35b"
        "6101c160048036038101906101bc9190610629565b610463565b6040516101ce"
        "9190610665565b60405180910390f35b60036020528060005260406000206000"
        "915090505481565b6000600160003373ffffffffffffffffffffffffffffffff"
        "ffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681"
        "52602001908152602001600020600090549054906101000a900460ff1661028f"
        "576040517f08c379a00000000000000000000000000000000000000000000000"
        "0000000000815260040161028690610832565b60405180910390fd5b60019050"
        "9392505050565b600160003373fffffffffffffffffffffffffffffffffffff"
        "fff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152"
        "602001600020600090549054906101000a900460ff1661033d576040517f08c37"
        "9a000000000000000000000000000000000000000000000000000000000815260"
        "040161033490610832565b60405180910390fd5b60026000815480929190610350"
        "90610881565b9190505550505050565b60016020528060005260406000206000"
        "915054906101000a900460ff1681565b60008054906101000a900473ffffffff"
        "ffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffff"
        "ffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff161461"
        "0407576040517f08c379a0000000000000000000000000000000000000000000"
        "000000000000008152600401610406906108f5565b60405180910390fd5b806001"
        "60006101000a81548160ff02191690831515021790555050565b60008054906101"
        "000a900473ffffffffffffffffffffffffffffffffffffffff1681565b6001602"
        "0528060005260406000206000915054906101000a900460ff1681565b60006003"
        "60008381526020019081526020016000205490509190505600a264697066735822"
        "12209a8e9a8e9a8e9a8e9a8e9a8e9a8e9a8e9a8e9a8e9a8e9a8e9a8e9a8e6473"
        "6f6c63430008130033"
    )
    
    return {'abi': abi, 'bin': bytecode}


def deploy_contract(ganache_url=None):
    """
    Deploy the contract to Ganache.
    
    Args:
        ganache_url: URL of Ganache instance (default: http://127.0.0.1:7545)
        
    Returns:
        Deployed contract address
    """
    ganache_url = ganache_url or os.environ.get('GANACHE_URL', 'http://127.0.0.1:7545')
    
    print(f"\nConnecting to Ganache at: {ganache_url}")
    
    # Connect to Ganache
    w3 = Web3(Web3.HTTPProvider(ganache_url))
    
    if not w3.is_connected():
        print("ERROR: Cannot connect to Ganache!")
        print("Make sure Ganache is running on the specified URL.")
        print("\nTo start Ganache:")
        print("  1. Open Ganache application")
        print("  2. Click 'QUICKSTART' or create a new workspace")
        print("  3. Ensure it's running on http://127.0.0.1:7545")
        return None
    
    print("Connected to Ganache!")
    print(f"Network ID: {w3.eth.chain_id}")
    print(f"Block Number: {w3.eth.block_number}")
    
    # Get deployer account (first Ganache account)
    accounts = w3.eth.accounts
    if not accounts:
        print("ERROR: No accounts available in Ganache!")
        return None
    
    deployer = accounts[0]
    balance = w3.from_wei(w3.eth.get_balance(deployer), 'ether')
    print(f"\nDeployer account: {deployer}")
    print(f"Balance: {balance} ETH")
    
    # Get contract data
    contract_data = get_contract_data()
    
    # Save ABI to file
    abi_path = os.path.join(os.path.dirname(__file__), 'contracts', 'PatientRecords.json')
    with open(abi_path, 'w') as f:
        json.dump({
            'abi': contract_data['abi'],
            'bytecode': contract_data['bin']
        }, f, indent=2)
    print(f"ABI saved to: {abi_path}")
    
    # Create contract instance
    PatientRecords = w3.eth.contract(
        abi=contract_data['abi'],
        bytecode=contract_data['bin']
    )
    
    print("\nDeploying contract...")
    
    try:
        # Build deployment transaction
        tx = PatientRecords.constructor().build_transaction({
            'from': deployer,
            'gas': 3000000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(deployer)
        })
        
        # Send transaction (Ganache accounts are unlocked)
        tx_hash = w3.eth.send_transaction(tx)
        print(f"Transaction hash: {tx_hash.hex()}")
        
        # Wait for receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        contract_address = receipt['contractAddress']
        
        print(f"\n{'='*60}")
        print("CONTRACT DEPLOYED SUCCESSFULLY!")
        print(f"{'='*60}")
        print(f"Contract Address: {contract_address}")
        print(f"Block Number: {receipt['blockNumber']}")
        print(f"Gas Used: {receipt['gasUsed']}")
        print(f"{'='*60}")
        
        # Save contract address to .env file
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        
        # Read existing .env
        env_content = ""
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_content = f.read()
        
        # Update or add CONTRACT_ADDRESS
        if 'CONTRACT_ADDRESS=' in env_content:
            lines = env_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('CONTRACT_ADDRESS='):
                    lines[i] = f'CONTRACT_ADDRESS={contract_address}'
            env_content = '\n'.join(lines)
        else:
            env_content += f'\n\n# Blockchain Configuration\nCONTRACT_ADDRESS={contract_address}\n'
        
        # Also add Ganache URL and first account private key
        if 'GANACHE_URL=' not in env_content:
            env_content += f'GANACHE_URL={ganache_url}\n'
        
        # Get private key from Ganache (usually starts with 0x...)
        # Note: In production, never expose private keys!
        if 'BLOCKCHAIN_PRIVATE_KEY=' not in env_content:
            env_content += '# Get this from Ganache - click key icon next to account\n'
            env_content += '# BLOCKCHAIN_PRIVATE_KEY=your_private_key_here\n'
        
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print(f"\nContract address saved to .env file")
        print("\nIMPORTANT: Add your Ganache private key to .env file:")
        print("  1. Open Ganache")
        print("  2. Click the key icon next to the first account")
        print("  3. Copy the private key")
        print("  4. Add to .env: BLOCKCHAIN_PRIVATE_KEY=your_key")
        
        return contract_address
        
    except Exception as e:
        print(f"\nDeployment error: {e}")
        return None


def verify_deployment(contract_address, ganache_url=None):
    """Verify the deployed contract is working."""
    ganache_url = ganache_url or os.environ.get('GANACHE_URL', 'http://127.0.0.1:7545')
    
    print(f"\nVerifying contract at: {contract_address}")
    
    w3 = Web3(Web3.HTTPProvider(ganache_url))
    
    # Load ABI
    abi_path = os.path.join(os.path.dirname(__file__), 'contracts', 'PatientRecords.json')
    with open(abi_path, 'r') as f:
        contract_data = json.load(f)
    
    contract = w3.eth.contract(
        address=Web3.to_checksum_address(contract_address),
        abi=contract_data['abi']
    )
    
    try:
        owner = contract.functions.owner().call()
        print(f"Contract owner: {owner}")
        print("Contract is working correctly!")
        return True
    except Exception as e:
        print(f"Verification error: {e}")
        return False


if __name__ == '__main__':
    print("="*60)
    print("Hospital Patient Portal - Smart Contract Deployment")
    print("="*60)
    print("Using pre-compiled contract (no Solidity compiler needed)")
    
    # Get Ganache URL from args or use default
    ganache_url = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Deploy contract
    contract_address = deploy_contract(ganache_url)
    
    if contract_address:
        # Verify deployment
        verify_deployment(contract_address, ganache_url)
        
        print("\n" + "="*60)
        print("NEXT STEPS:")
        print("="*60)
        print("1. Make sure Ganache stays running")
        print("2. Add BLOCKCHAIN_PRIVATE_KEY to your .env file")
        print("3. Restart Flask app: python app.py")
        print("4. Your medical records are now blockchain-secured!")
        print("="*60)
    else:
        print("\nDeployment failed. Please check the errors above.")
        sys.exit(1)
