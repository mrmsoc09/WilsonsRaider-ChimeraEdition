import gnupg
import os
from ..ui import UIManager

class OPSECManager:
    """Manages operational security, primarily data encryption."""

    def __init__(self, config: dict, ui_manager: UIManager):
        self.ui = ui_manager
        self.gpg_home = os.path.expanduser(config.get('opsec', {}).get('gpg_home', '~/.gnupg'))
        self.gpg = gnupg.GPG(gnupghome=self.gpg_home)
        self.ui.print(f"[grey50]OPSECManager initialized. GPG home: {self.gpg_home}[/grey50]")
        # In a real app, you would need to ensure keys exist.

    def encrypt_data(self, data_to_encrypt: str, recipient_key_fingerprint: str) -> str | None:
        """
        Encrypts a string of data using GPG for a specific recipient.

        Args:
            data_to_encrypt (str): The data to encrypt.
            recipient_key_fingerprint (str): The fingerprint of the recipient's GPG key.

        Returns:
            str | None: The ASCII-armored encrypted data, or None on failure.
        """
        encrypted_data = self.gpg.encrypt(data_to_encrypt, recipient_key_fingerprint, always_trust=True)
        
        if encrypted_data.ok:
            self.ui.print(f"  -> Data successfully encrypted for recipient {recipient_key_fingerprint[:16]}...")
            return str(encrypted_data)
        else:
            self.ui.print(f"[bold red]  -> GPG Encryption failed: {encrypted_data.status}[/bold red]")
            self.ui.print(f"[bold red]  -> Stderr: {encrypted_data.stderr}[/bold red]")
            return None

    def decrypt_data(self, encrypted_data: str, passphrase: str = None) -> str | None:
        """
        Decrypts a GPG-encrypted string.

        Args:
            encrypted_data (str): The ASCII-armored encrypted data.
            passphrase (str, optional): The passphrase for the private key.

        Returns:
            str | None: The decrypted data, or None on failure.
        """
        decrypted_data = self.gpg.decrypt(encrypted_data, passphrase=passphrase)
        
        if decrypted_data.ok:
            self.ui.print("  -> Data successfully decrypted.")
            return str(decrypted_data)
        else:
            self.ui.print(f"[bold red]  -> GPG Decryption failed: {decrypted_data.status}[/bold red]")
            self.ui.print(f"[bold red]  -> Stderr: {decrypted_data.stderr}[/bold red]")
            return None

