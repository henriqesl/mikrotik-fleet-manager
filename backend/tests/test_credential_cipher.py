import pytest
from cryptography.fernet import Fernet

from app.core.credential_cipher import (
    CredentialCipher,
    CredentialDecryptionError,
    CredentialEncryptionError,
)


def create_cipher() -> CredentialCipher:
    key = Fernet.generate_key().decode("utf-8")

    return CredentialCipher(key)


def test_encrypt_and_decrypt_credential() -> None:
    cipher = create_cipher()

    plaintext = "SecurePassword123!"
    ciphertext = cipher.encrypt(plaintext)

    assert ciphertext != plaintext
    assert cipher.decrypt(ciphertext) == plaintext


def test_encrypt_rejects_empty_credential() -> None:
    cipher = create_cipher()

    with pytest.raises(CredentialEncryptionError):
        cipher.encrypt("")


def test_decrypt_rejects_invalid_ciphertext() -> None:
    cipher = create_cipher()

    with pytest.raises(CredentialDecryptionError):
        cipher.decrypt("invalid-ciphertext")