"""
Deploy Smart Contract to Ganache
================================
Script to compile and deploy the PatientRecords smart contract.
"""

import json
import os
import sys
from solcx import compile_source, install_solc, get_installed_solc_versions
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()


def install_solidity_compiler():
    """Install Solidity compiler if not already installed."""
    try:
        installed = get_installed_solc_versions()
        if not installed:
            print("Installing Solidity compiler v0.8.19...")
            install_solc('0.8.19')
            print("Solidity compiler installed successfully!")
        else:
            print(f"Solidity compiler versions installed: {installed}")
        return True
    except Exception as e:
        print(f"Error installing Solidity compiler: {e}")
        return False


def compile_contract():
    """Compile the Solidity smart contract."""
    contract_path = os.path.join(os.path.dirname(__file__), 'contracts', 'PatientRecords.sol')
    
    if not os.path.exists(contract_path):
        print(f"Contract file not found: {contract_path}")
        return None
    
    print(f"Reading contract from: {contract_path}")
    
    with open(contract_path, 'r') as f:
        contract_source = f.read()
    
    print("Compiling contract...")
    
    try:
        compiled = compile_source(
            contract_source,
            output_values=['abi', 'bin'],
            solc_version='0.8.19'
        )
        
        # Get the contract interface
        contract_id, contract_interface = compiled.popitem()
        
        print(f"Contract compiled successfully: {contract_id}")
        
        # Save ABI to file
        abi_path = os.path.join(os.path.dirname(__file__), 'contracts', 'PatientRecords.json')
        with open(abi_path, 'w') as f:
            json.dump({
                'abi': contract_interface['abi'],
                'bytecode': contract_interface['bin']
            }, f, indent=2)
        print(f"ABI saved to: {abi_path}")
        
        return contract_interface
    except Exception as e:
        print(f"Compilation error: {e}")
        return None


def deploy_contract(ganache_url=None):
    """
    Deploy the compiled contract to Ganache.
    
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
    
    # Compile contract
    contract_interface = compile_contract()
    if not contract_interface:
        return None
    
    # Create contract instance
    PatientRecords = w3.eth.contract(
        abi=contract_interface['abi'],
        bytecode=contract_interface['bin']
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
    
    # Install Solidity compiler
    if not install_solidity_compiler():
        print("Failed to install Solidity compiler. Exiting.")
        sys.exit(1)
    
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
