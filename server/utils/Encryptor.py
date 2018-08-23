__all__ = ['dict_decrypt', 'dict_encrypt', 'get_key32']

import base64
import json

from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes


def dict_encrypt(plain_attr: dict, key: bytes) -> str:
    cipher = ChaCha20.new(key=key)
    json_attr = json.dumps(plain_attr).encode()
    encrypted_data_bytes = cipher.encrypt(json_attr)

    nonce = base64.b64encode(cipher.nonce).decode()
    encrypted_data = base64.b64encode(encrypted_data_bytes).decode()

    return json.dumps({'nonce': nonce, 'ciphertext': encrypted_data})


def dict_decrypt(encrypted_json_str: str, key: bytes) -> dict:
    encrypted_json = json.loads(encrypted_json_str)
    cipher_text = base64.b64decode(encrypted_json['ciphertext'])
    nonce = base64.b64decode(encrypted_json['nonce'])
    cipher = ChaCha20.new(key=key, nonce=nonce)
    json_attr = cipher.decrypt(cipher_text)
    return json.loads(json_attr)


def get_key32() -> bytes:
    return get_random_bytes(32)
