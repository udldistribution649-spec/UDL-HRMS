
from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


def get_fernet() -> Fernet:
    key = settings.SOURCE_DB_ENCRYPTION_KEY.encode("utf-8")
    return Fernet(key)


def encrypt_credential(plain_text: str) -> str:
    if not plain_text:
        raise ValueError("Credential cannot be empty.")

    encrypted = get_fernet().encrypt(
        plain_text.encode("utf-8")
    )

    return encrypted.decode("utf-8")


def decrypt_credential(encrypted_text: str) -> str:
    if not encrypted_text:
        raise ValueError("Encrypted credential cannot be empty.")

    try:
        decrypted = get_fernet().decrypt(
            encrypted_text.encode("utf-8")
        )
        return decrypted.decode("utf-8")

    except InvalidToken:
        raise ValueError(
            "Credential decryption failed. Check the encryption key."
        ) from None
