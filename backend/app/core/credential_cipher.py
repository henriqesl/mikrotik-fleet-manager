from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


class CredentialEncryptionError(RuntimeError):
    """Raised when a credential cannot be encrypted."""


class CredentialDecryptionError(RuntimeError):
    """Raised when a credential cannot be decrypted."""


class CredentialCipher:
    """Encrypt and decrypt sensitive router credentials."""

    def __init__(self, encryption_key: str) -> None:
        try:
            self._fernet = Fernet(
                encryption_key.encode("utf-8")
            )
        except (TypeError, ValueError) as exc:
            raise CredentialEncryptionError(
                "Invalid credential encryption key."
            ) from exc

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a credential before database storage."""

        if plaintext == "":
            raise CredentialEncryptionError(
                "Credential cannot be empty."
            )

        try:
            encrypted_value = self._fernet.encrypt(
                plaintext.encode("utf-8")
            )
        except Exception as exc:
            raise CredentialEncryptionError(
                "Unable to encrypt credential."
            ) from exc

        return encrypted_value.decode("utf-8")

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a credential for internal RouterOS communication."""

        if ciphertext == "":
            raise CredentialDecryptionError(
                "Encrypted credential cannot be empty."
            )

        try:
            decrypted_value = self._fernet.decrypt(
                ciphertext.encode("utf-8")
            )

            return decrypted_value.decode("utf-8")

        except (InvalidToken, UnicodeDecodeError) as exc:
            raise CredentialDecryptionError(
                "Unable to decrypt credential."
            ) from exc


@lru_cache
def get_credential_cipher() -> CredentialCipher:
    """Return the shared credential cipher instance."""

    return CredentialCipher(
        settings.credential_encryption_key.get_secret_value()
    )