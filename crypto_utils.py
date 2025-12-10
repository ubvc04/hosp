"""
Hospital Patient Portal - Cryptography Utilities
=================================================
This module implements RSA-4096 asymmetric encryption for securing sensitive patient data.

HOW ENCRYPTION WORKS:
--------------------
1. RSA Key Generation:
   - On first run, a 4096-bit RSA key pair is generated
   - Private key is stored securely (should be in env vars or secure storage in production)
   - Public key is used for encrypting data before storage

2. Encryption Process:
   - Sensitive data (medical history, diagnosis, etc.) is encrypted using the PUBLIC key
   - Only the server with the PRIVATE key can decrypt this data
   - RSA has a size limit, so for large data we use hybrid encryption:
     a) Generate a random AES key
     b) Encrypt the data with AES
     c) Encrypt the AES key with RSA
     d) Store both encrypted AES key + encrypted data

3. Decryption Process:
   - Load the private key (stored securely)
   - For hybrid encryption: decrypt AES key with RSA, then decrypt data with AES
   - Return plaintext data for authorized viewing

SECURITY NOTES:
--------------
- Private key should NEVER be exposed in code, logs, or frontend
- In production, use HSM (Hardware Security Module) or cloud key management
- Keys are loaded from files but could be loaded from environment variables
"""

import os
import base64
import json
from typing import Optional, Tuple
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidKey


class CryptoManager:
    """
    Manages RSA-4096 asymmetric encryption for the hospital portal.
    
    This class handles:
    - Key generation and storage
    - Hybrid encryption (RSA + AES) for large data
    - Secure encryption/decryption of patient data
    """
    
    def __init__(self, private_key_path: str, public_key_path: str, key_size: int = 4096):
        """
        Initialize the CryptoManager.
        
        Args:
            private_key_path: Path to store/load the private key
            public_key_path: Path to store/load the public key
            key_size: RSA key size in bits (default 4096)
        """
        self.private_key_path = private_key_path
        self.public_key_path = public_key_path
        self.key_size = key_size
        self._private_key = None
        self._public_key = None
        
        # Ensure keys directory exists
        os.makedirs(os.path.dirname(private_key_path), exist_ok=True)
        
        # Load or generate keys
        self._initialize_keys()
    
    def _initialize_keys(self) -> None:
        """
        Load existing keys or generate new ones if they don't exist.
        
        This ensures the application always has valid encryption keys.
        In production, keys should be pre-generated and stored securely.
        """
        if os.path.exists(self.private_key_path) and os.path.exists(self.public_key_path):
            self._load_keys()
        else:
            self._generate_keys()
    
    def _generate_keys(self) -> None:
        """
        Generate a new RSA-4096 key pair.
        
        The private key is stored with no encryption for development.
        In PRODUCTION: Use a passphrase or HSM for private key protection!
        """
        print(f"Generating new RSA-{self.key_size} key pair...")
        
        # Generate private key
        self._private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.key_size,
            backend=default_backend()
        )
        
        # Extract public key
        self._public_key = self._private_key.public_key()
        
        # Save private key (PEM format)
        # WARNING: In production, encrypt with a passphrase!
        private_pem = self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        with open(self.private_key_path, 'wb') as f:
            f.write(private_pem)
        
        # Restrict private key file permissions (Unix systems)
        try:
            os.chmod(self.private_key_path, 0o600)
        except (OSError, AttributeError):
            pass  # Windows doesn't support chmod the same way
        
        # Save public key (PEM format)
        public_pem = self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        with open(self.public_key_path, 'wb') as f:
            f.write(public_pem)
        
        print(f"Keys generated and saved successfully!")
    
    def _load_keys(self) -> None:
        """Load existing keys from files."""
        # Load private key
        with open(self.private_key_path, 'rb') as f:
            self._private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
        
        # Load public key
        with open(self.public_key_path, 'rb') as f:
            self._public_key = serialization.load_pem_public_key(
                f.read(),
                backend=default_backend()
            )
    
    def _generate_aes_key(self) -> bytes:
        """Generate a random 256-bit AES key."""
        return os.urandom(32)  # 256 bits
    
    def _generate_iv(self) -> bytes:
        """Generate a random initialization vector for AES."""
        return os.urandom(16)  # 128 bits
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext using hybrid encryption (RSA + AES).
        
        Hybrid encryption process:
        1. Generate a random AES-256 key
        2. Generate a random IV (initialization vector)
        3. Encrypt the plaintext with AES-256-CBC
        4. Encrypt the AES key with RSA-OAEP
        5. Combine and encode as base64 JSON
        
        Args:
            plaintext: The string to encrypt
            
        Returns:
            Base64 encoded JSON containing encrypted key, IV, and ciphertext
        """
        if not plaintext:
            return ""
        
        # Convert plaintext to bytes
        plaintext_bytes = plaintext.encode('utf-8')
        
        # Generate AES key and IV
        aes_key = self._generate_aes_key()
        iv = self._generate_iv()
        
        # Pad plaintext to be multiple of 16 bytes (AES block size)
        padding_length = 16 - (len(plaintext_bytes) % 16)
        padded_plaintext = plaintext_bytes + bytes([padding_length] * padding_length)
        
        # Encrypt data with AES-256-CBC
        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_plaintext) + encryptor.finalize()
        
        # Encrypt AES key with RSA-OAEP
        encrypted_key = self._public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Combine all parts into a JSON structure
        result = {
            'key': base64.b64encode(encrypted_key).decode('utf-8'),
            'iv': base64.b64encode(iv).decode('utf-8'),
            'data': base64.b64encode(encrypted_data).decode('utf-8')
        }
        
        # Return as base64-encoded JSON
        return base64.b64encode(json.dumps(result).encode('utf-8')).decode('utf-8')
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext using hybrid decryption (RSA + AES).
        
        Decryption process:
        1. Decode base64 JSON
        2. Extract encrypted key, IV, and ciphertext
        3. Decrypt AES key with RSA private key
        4. Decrypt data with AES
        5. Remove padding and return plaintext
        
        Args:
            ciphertext: The base64 encoded encrypted data
            
        Returns:
            Decrypted plaintext string
        """
        if not ciphertext:
            return ""
        
        try:
            # Decode the base64 JSON
            json_data = json.loads(base64.b64decode(ciphertext).decode('utf-8'))
            
            encrypted_key = base64.b64decode(json_data['key'])
            iv = base64.b64decode(json_data['iv'])
            encrypted_data = base64.b64decode(json_data['data'])
            
            # Decrypt AES key with RSA private key
            aes_key = self._private_key.decrypt(
                encrypted_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Decrypt data with AES
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            padded_plaintext = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # Remove PKCS7 padding
            padding_length = padded_plaintext[-1]
            plaintext = padded_plaintext[:-padding_length]
            
            return plaintext.decode('utf-8')
            
        except Exception as e:
            # Log error in production, return empty for security
            print(f"Decryption error: {e}")
            return ""
    
    def encrypt_dict(self, data: dict, fields_to_encrypt: list) -> dict:
        """
        Encrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary containing the data
            fields_to_encrypt: List of field names to encrypt
            
        Returns:
            Dictionary with specified fields encrypted
        """
        result = data.copy()
        for field in fields_to_encrypt:
            if field in result and result[field]:
                result[field] = self.encrypt(str(result[field]))
        return result
    
    def decrypt_dict(self, data: dict, fields_to_decrypt: list) -> dict:
        """
        Decrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary containing encrypted data
            fields_to_decrypt: List of field names to decrypt
            
        Returns:
            Dictionary with specified fields decrypted
        """
        result = data.copy()
        for field in fields_to_decrypt:
            if field in result and result[field]:
                result[field] = self.decrypt(str(result[field]))
        return result


# Global crypto manager instance (initialized in app factory)
crypto_manager: Optional[CryptoManager] = None


def init_crypto(app) -> CryptoManager:
    """
    Initialize the crypto manager with application configuration.
    
    Args:
        app: Flask application instance
        
    Returns:
        Initialized CryptoManager instance
    """
    global crypto_manager
    
    crypto_manager = CryptoManager(
        private_key_path=app.config['PRIVATE_KEY_PATH'],
        public_key_path=app.config['PUBLIC_KEY_PATH'],
        key_size=app.config.get('RSA_KEY_SIZE', 4096)
    )
    
    return crypto_manager


def get_crypto() -> CryptoManager:
    """
    Get the global crypto manager instance.
    
    Returns:
        CryptoManager instance
        
    Raises:
        RuntimeError: If crypto manager is not initialized
    """
    if crypto_manager is None:
        raise RuntimeError("CryptoManager not initialized. Call init_crypto() first.")
    return crypto_manager
