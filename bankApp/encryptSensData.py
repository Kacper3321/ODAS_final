from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from os import environ
from dotenv import load_dotenv
import os

load_dotenv()
aesKey = environ.get('aes_key')

def encrypt_aes(data, key):
     # przeksztalcam klucz i dane do postaci bajtów, jeśli są typu string
    if isinstance(key, str):
        key = key.encode()
    if isinstance(data, str):
        data = data.encode()

    # Generuje losowy wektor inicjalizujący (IV)
    iv = os.urandom(16)

    # Tworzę obiekt szyfrujący
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Szyfruje dane
    encrypted_data = encryptor.update(data) + encryptor.finalize()

    # Zwracam zaszyfrowane dane z dodanym na poczatku IV, ktorego potrzebuje do odszyfrowania
    return iv + encrypted_data

def decrypt_aes(encrypted_data_with_iv, key):
    iv = encrypted_data_with_iv[:16]
    encrypted_data = encrypted_data_with_iv[16:]

    # przeksztalcam klucza do postaci bajtów, jeśli jest typu string
    if isinstance(key, str):
        key = key.encode()

    # Tworze obiekt deszyfrujący
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # pobieram dane i je deszyfruje
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()

    # Zwracam odszyfrowane dane
    return decrypted_data.decode()
