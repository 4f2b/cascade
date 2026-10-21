import base64
import hashlib
import secrets
from typing import Optional

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False


class TokenManager:
    def __init__(self, master_password: Optional[str] = None):
        self.master_password = master_password
        self._cipher = None
        if master_password:
            if not HAS_CRYPTOGRAPHY:
                raise ImportError("cryptography package required for token encryption. Install with: pip install cryptography")
            self._initialize_cipher(master_password)
    
    def _initialize_cipher(self, password: str):
        salt = secrets.token_bytes(16)
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self._cipher = Fernet(key)
        self._salt = salt
    
    def encrypt_token(self, token: str) -> bytes:
        if not HAS_CRYPTOGRAPHY:
            raise ImportError("cryptography package required. Install with: pip install cryptography")
        if not self._cipher:
            raise ValueError("TokenManager not initialized with password")
        return self._cipher.encrypt(token.encode())
    
    def decrypt_token(self, encrypted_token: bytes) -> str:
        if not HAS_CRYPTOGRAPHY:
            raise ImportError("cryptography package required. Install with: pip install cryptography")
        if not self._cipher:
            raise ValueError("TokenManager not initialized with password")
        return self._cipher.decrypt(encrypted_token).decode()
    
    def hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()
    
    def mask_token(self, token: str, visible_chars: int = 4) -> str:
        if len(token) <= visible_chars * 2:
            return '*' * len(token)
        
        start = token[:visible_chars]
        end = token[-visible_chars:]
        masked_middle = '*' * (len(token) - visible_chars * 2)
        
        return f"{start}{masked_middle}{end}"
    
    def validate_token_format(self, token: str) -> bool:
        if not token or not isinstance(token, str):
            return False
        
        parts = token.split('.')
        if len(parts) != 3:
            return False
        
        try:
            user_id_encoded = parts[0]
            base64.urlsafe_b64decode(user_id_encoded + '==')
            return True
        except:
            return False
    
    @staticmethod
    def extract_user_id(token: str) -> Optional[int]:
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return None
            
            user_id_encoded = parts[0]
            padding = 4 - (len(user_id_encoded) % 4)
            user_id_encoded += '=' * padding
            
            user_id_bytes = base64.urlsafe_b64decode(user_id_encoded)
            return int(user_id_bytes.decode('utf-8'))
        except:
            return None
    
    def generate_session_token(self) -> str:
        return secrets.token_urlsafe(32)
    
    def constant_time_compare(self, a: str, b: str) -> bool:
        return secrets.compare_digest(a.encode(), b.encode())
