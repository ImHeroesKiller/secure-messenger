from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

def encrypt_message(plain_text: str, key: str) -> str:
    key_bytes = key.encode('utf-8')[:32].ljust(32, b'0')
    nonce = get_random_bytes(12)  # 96-bit nonce untuk GCM
    
    cipher = AES.new(key_bytes, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plain_text.encode('utf-8'))
    
    # Gabungkan nonce + ciphertext + tag
    encrypted_data = nonce + ciphertext + tag
    return base64.b64encode(encrypted_data).decode('utf-8')

def decrypt_message(encrypted_text: str, key: str) -> str:
    key_bytes = key.encode('utf-8')[:32].ljust(32, b'0')
    encrypted_data = base64.b64decode(encrypted_text)
    
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:-16]
    tag = encrypted_data[-16:]
    
    cipher = AES.new(key_bytes, AES.MODE_GCM, nonce=nonce)
    decrypted = cipher.decrypt_and_verify(ciphertext, tag)
    return decrypted.decode('utf-8')
