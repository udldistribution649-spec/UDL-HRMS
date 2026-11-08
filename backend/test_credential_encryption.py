from app.services.credential_encryption_service import (
    encrypt_credential,
    decrypt_credential,
)


def test_credential_encryption_round_trip():
    original_password = "Test_DB_Password_123!"

    encrypted = encrypt_credential(original_password)

    assert encrypted != original_password
    assert decrypt_credential(encrypted) == original_password


def test_different_encryption_each_time():
    password = "Test_DB_Password_123!"

    encrypted_1 = encrypt_credential(password)
    encrypted_2 = encrypt_credential(password)

    assert encrypted_1 != encrypted_2
    assert decrypt_credential(encrypted_1) == password
    assert decrypt_credential(encrypted_2) == password