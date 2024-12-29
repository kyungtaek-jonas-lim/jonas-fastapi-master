from enum import Enum
from fastapi import APIRouter, HTTPException
from cryptography.hazmat.primitives import hashes, serialization, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asymmetric_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import os
import bcrypt
from pydantic import BaseModel, Field


router = APIRouter()

# =========================================================
# Information
# =========================================================
'''
- SHA256
    : Cryptographic hash function, used for integrity checks and creating fixed-length hashes from data.
- BCRYPT
    : Password hashing algorithm, designed to be slow and computationally expensive to resist brute-force attacks.
- AES256
    : Symmetric encryption algorithm, used for securely encrypting data with a 256-bit key.
- RS256
    : Digital signature algorithm that uses RSA and SHA-256, commonly used in authentication and API security (e.g., JWT).


1. Hash vs Encrypt
    - Hash:
        - One-way: Cannot be reversed to get the original value.
        - Used for verifying data integrity (e.g., passwords).
        - Examples: Bcrypt, SHA256.

    - Encrypt:
        - Two-way: Can be reversed using a decryption key to get the original value.
        - Used for secure communication or data storage.
        - Examples: AES256, RSA

2. The usage of Public Key and Private Key in Asymmetric Encryption:
    This is standard for asymmetric encryption:
        - Public Key: Encrypt
        - Private Key: Decrypt

3. Salt vs OAEP Padding
    - OAEP Padding vs Salt:
        - Salt and OAEP padding are similar in that they both add randomness to make the output different for the same input. However, their purposes are different:
            - Salt is mainly used with hash functions (e.g., bcrypt, SHA256) to prevent identical values from generating the same hash.
            - OAEP padding is used in RSA encryption to add randomness and protect the encrypted data, ensuring that the same plaintext generates different ciphertexts.

    - Removing OAEP Padding and Identical Output:
        - If you remove the OAEP padding, the encryption will no longer have randomness, and the encrypted value will always be the same for the same input. This is because, without padding, the encryption is deterministic.
        - However, removing padding reduces security, as it makes the encryption vulnerable to attacks, so it's not recommended.

'''
    

# =========================================================
# API Request
# =========================================================

# Hash Request Params
class HashRequest(BaseModel):
    value: str = Field(..., min_length=1)
class HashSha256Request(HashRequest):
    pass
class HashBryptRequest(HashRequest):
    pass
class HashBryptCompareRequest(HashRequest):
    hashed_value: str = Field(..., min_length=1)

# Encrpyt Request Params
class EncryptRequest(BaseModel):
    value: str = Field(..., min_length=1)
class EncryptSymmetricRequest(EncryptRequest):
    key: str = Field(..., min_length=16)
class EncryptSymmetricWithSaltRequest(EncryptSymmetricRequest):
    salt: str = Field(..., min_length=1)
class EncryptAsymmetricRequest(EncryptRequest):
    pass
    
class DecryptRequest(BaseModel):
    encrypted_value: str = Field(..., min_length=1)
class DecryptSymmetricRequest(DecryptRequest):
    key: str = Field(..., min_length=16)
class DecryptSymmetricWithSaltRequest(DecryptSymmetricRequest):
    salt: str = Field(..., min_length=1)
class DecryptAsymmetricRequest(DecryptRequest):
    pass


# =========================================================
# Unidirectional (Hashing)
# =========================================================

# SHA256 Hashing
# Params: value
# return: hashed_value
def sha256_hash(value: str) -> str:
    digest = hashes.Hash(hashes.SHA256())
    digest.update(value.encode())
    return digest.finalize().hex()


# Bcrypt (Password Hashing)
# Params: value
# return: hashed_value
# Bcrypt uses salting by default. Every time you hash a password with Bcrypt, it automatically generates a unique salt and appends it to the hash.
# Bcrypt internally uses the Blowfish encryption algorithm to generate the hash.
def bcrypt_hash(value: str) -> str:
    hashed_value = bcrypt.hashpw(value.encode(), bcrypt.gensalt())
    return hashed_value.decode()


# Bcrypt (Password Compare)
# Params: value, hashed_value
# return: is_valid
def bcrypt_compare(value: str, hashed_value: str) -> bool:
    """Compares the input value with the hashed value."""
    return bcrypt.checkpw(value.encode(), hashed_value.encode())


# --------------
# API
# SHA256 Endpoint
@router.post("/hash/sha256")
async def sha256_endpoint(request: HashSha256Request):
    try:
        hashed_value = sha256_hash(request.value)
        return {"hashed_value": hashed_value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hash/bcrypt")
async def bcrypt_endpoint(request: HashBryptRequest):
    try:
        hashed_value = bcrypt_hash(request.value)
        return {"hashed_value": hashed_value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare/bcrypt")
async def bcrypt_compare_endpoint(request: HashBryptCompareRequest):
    try:
        is_valid = bcrypt_compare(request.value, request.hashed_value)
        return {"is_valid": is_valid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# =========================================================
# Symmetric (AES256)
# =========================================================

# AES256 Encryption
# Params: key, value
# return: encrypted_value
def aes256_encrypt(key: str, value: str) -> str:

    # Make the key 16/24/32
    if len(key) < 24:
        key = key[:16]
    elif len(key) < 32:
        key = key[:24]

    key = key.encode()[:32]  # Ensure 32-byte key
    iv = os.urandom(16)  # Random initialization vector to increase security
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()

    # Pad value to match AES block size
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(value.encode()) + padder.finalize()
    encrypted_value = encryptor.update(padded_data) + encryptor.finalize()
    
    # Return base64 encoded encrypted value
    return base64.b64encode(iv + encrypted_value).decode() # Base64 encode (Base64 encodes binary data into text, making it easier to handle and transfer.)


# AES256 Decryption
# Params: key, encrypted_value
# return: decrypted_value
def aes256_decrypt(key: str, encrypted_value: str) -> str:

    # Make the key 16/24/32
    if len(key) < 24:
        key = key[:16]
    elif len(key) < 32:
        key = key[:24]

    encrypted_value = base64.b64decode(encrypted_value)
    iv = encrypted_value[:16]
    encrypted_value = encrypted_value[16:]

    key = key.encode()[:32]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()

    padded_data = decryptor.update(encrypted_value) + decryptor.finalize()

    # Unpad decrypted data
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted_value = unpadder.update(padded_data) + unpadder.finalize()

    return decrypted_value.decode() # Base64 encode (Base64 encodes binary data into text, making it easier to handle and transfer.)


# AES256 Encryption with Salt
# Params: key, value, salt
# return: encrypted_with_salt_value
def aes256_encrypt_with_salt(key: str, value: str, salt: str) -> str:
    key = (salt + key).encode()[:32]
    return aes256_encrypt(key.decode(), value)


# AES256 Decryption with Salt
# Params: key, encrypted_value, salt
# return: decrypted_value
def aes256_decrypt_with_salt(key: str, encrypted_value: str, salt: str) -> str:
    key = (salt + key).encode()[:32]
    return aes256_decrypt(key.decode(), encrypted_value)


# --------------
# API
@router.post("/encrypt/aes256")
async def aes256_encrypt_endpoint(request: EncryptSymmetricRequest):
    try:
        encrypted_value = aes256_encrypt(request.key, request.value)
        return {"encrypted_value": encrypted_value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/decrypt/aes256")
async def aes256_decrypt_endpoint(request: DecryptSymmetricRequest):
    try:
        decrypted_value = aes256_decrypt(request.key, request.encrypted_value)
        return {"decrypted_value": decrypted_value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/encrypt/aes256/salt")
async def aes256_encrypt_with_salt_endpoint(request: EncryptSymmetricWithSaltRequest):
    try:
        encrypted_value = aes256_encrypt_with_salt(request.key, request.value, request.salt)
        return {"encrypted_value": encrypted_value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/decrypt/aes256/salt")
async def aes256_decrypt_with_salt_endpoint(request: DecryptSymmetricWithSaltRequest):
    try:
        decrypted_value = aes256_decrypt_with_salt(request.key, request.encrypted_value, request.salt)
        return {"decrypted_value": decrypted_value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# =========================================================
# Asymmetric (RS256)
# =========================================================

# RS256 Encryption
# Params: value
# return: encrypted_value
def rs256_encrypt(value: str) -> str:

    # -------------------------------------
    # Opt #1) With Public Key
    with open("keys/public.pem", "rb") as key_file:
        public_key = serialization.load_pem_public_key(key_file.read())
    encrypted = public_key.encrypt(
        value.encode(),
        asymmetric_padding.OAEP(
            mgf=asymmetric_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ), # Uses OAEP Padding - Encrpyted_values from the same value are different (The same role as salt's but technically different usage methods)
    )
    return base64.b64encode(encrypted).decode()  # Encode encrypted value in Base64

    # -------------------------------------
    # Opt #2) With Private Key
    # # Load the private key for encryption
    # with open("keys/private.pem", "rb") as key_file:
    #     private_key = serialization.load_pem_private_key(key_file.read(), password=None)
    #     '''
    #      The password parameter is used to decrypt the private key if it is password-protected.
    #         - If the private key is not protected by a password, you can pass None.
    #         - If it is protected, provide the password as a bytes object (e.g., b"mypassword").
    #     '''
    
    # encrypted_value = private_key.encrypt(
    #     value.encode(),
    #     padding.OAEP(
    #         mgf=padding.MGF1(algorithm=hashes.SHA256()),
    #         algorithm=hashes.SHA256(),
    #         label=None
    #     )
    # )
    
    # # Return base64 encoded encrypted value
    # return base64.b64encode(encrypted_value).decode()


# RS256 Get Public Key
# return: RS256 public key (from a file - 'key/private.pem')
def rs256_get_public_key() -> str:
    with open("keys/public.pem", "rb") as key_file:
        public_key = key_file.read()
    return public_key.decode()  # Return the public key as a string


# RS256 Decryption (encrypted with public key)
# Params: encrypted_value
# return: decrypted_value
def rs256_decrypt(encrypted_value: str) -> str:
    encrypted_value = base64.b64decode(encrypted_value)
    
    with open("keys/private.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(key_file.read(), password=None)
        '''
         The password parameter is used to decrypt the private key if it is password-protected.
            - If the private key is not protected by a password, you can pass None.
            - If it is protected, provide the password as a bytes object (e.g., b"mypassword").
        '''

    decrypted_value = private_key.decrypt(
        encrypted_value,
        asymmetric_padding.OAEP(
            mgf=asymmetric_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        ) # Uses The same OAEP Padding as the one used when encrypted - to get the real value cause it was encrypted with a padding.
    )
    
    return decrypted_value.decode()



# --------------
# API
@router.post("/encrypt/rs256")
async def rs256_encrypt_endpoint(request: EncryptAsymmetricRequest):
    try:
        encrypted_value = rs256_encrypt(request.value)
        return {"encrypted_value": encrypted_value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/public-key/rs256")
async def rs256_get_public_key_endpoint():
    try:
        public_key = rs256_get_public_key()
        return {"public_key": public_key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/decrypt/rs256")
async def rs256_decrypt_endpoint(request: DecryptAsymmetricRequest):
    try:
        decrypted_value = rs256_decrypt(request.encrypted_value)
        return {"decrypted_value": decrypted_value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))