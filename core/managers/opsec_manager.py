"""OPSEC Manager - Operational Security and Stealth Controls

Manages rate limiting, proxy rotation, traffic obfuscation, and footprint minimization.
Version: 2.0.0
"""

import gnupg
import os
import time
import random
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class StealthLevel(Enum):
    """Operational security stealth levels."""
    AGGRESSIVE = 1  # Fast, noisy, detectable
    NORMAL = 2      # Balanced speed/stealth
    CAUTIOUS = 3    # Slow, careful, minimal footprint
    PARANOID = 4    # Maximum stealth, slowest

class OPSECManager:
    """Manages operational security controls and stealth mechanisms."""

    def __init__(self, config: dict, ui_manager=None):
        self.ui = ui_manager
        self.config = config

        # GPG encryption setup
        self.gpg_home = os.path.expanduser(config.get('opsec', {}).get('gpg_home', '~/.gnupg'))
        self.gpg = gnupg.GPG(gnupghome=self.gpg_home)

        # Rate limiting
        self.rate_limits = config.get('opsec', {}).get('rate_limits', {})
        self.request_timestamps = []
        self.max_requests_per_minute = self.rate_limits.get('max_per_minute', 30)

        # Proxy configuration
        self.proxy_list = config.get('opsec', {}).get('proxies', [])
        self.current_proxy_index = 0
        self.proxy_rotation_enabled = config.get('opsec', {}).get('rotate_proxies', True)

        # Stealth settings
        self.stealth_level = StealthLevel[config.get('opsec', {}).get('stealth_level', 'NORMAL')]
        self.user_agents = self._load_user_agents()
        self.current_ua_index = 0

        # Delay configuration based on stealth level
        self.delay_ranges = {
            StealthLevel.AGGRESSIVE: (0.1, 0.5),
            StealthLevel.NORMAL: (0.5, 2.0),
            StealthLevel.CAUTIOUS: (2.0, 5.0),
            StealthLevel.PARANOID: (5.0, 15.0)
        }

        logger.info(f"OPSECManager initialized: stealth={self.stealth_level.name}, proxies={len(self.proxy_list)}")
        if self.ui:
            self.ui.print(f"[grey50]OPSEC: {self.stealth_level.name} mode, {len(self.proxy_list)} proxies[/grey50]")

    def _load_user_agents(self) -> List[str]:
        """Load user agent strings for rotation."""
        default_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
        ]
        return self.config.get('opsec', {}).get('user_agents', default_agents)

    async def apply_rate_limit(self) -> bool:
        """Apply rate limiting before request."""
        now = datetime.utcnow()

        # Remove timestamps older than 1 minute
        cutoff = now - timedelta(minutes=1)
        self.request_timestamps = [ts for ts in self.request_timestamps if ts > cutoff]

        # Check if we've exceeded rate limit
        if len(self.request_timestamps) >= self.max_requests_per_minute:
            wait_time = (self.request_timestamps[0] - cutoff).total_seconds() + 1
            logger.warning(f"Rate limit reached, waiting {wait_time:.1f}s")
            if self.ui:
                self.ui.print(f"[yellow]  -> Rate limit: waiting {wait_time:.1f}s[/yellow]")
            await self._smart_delay(wait_time)
            return False

        # Add current request
        self.request_timestamps.append(now)
        return True

    async def apply_stealth_delay(self):
        """Apply randomized delay based on stealth level."""
        min_delay, max_delay = self.delay_ranges[self.stealth_level]
        delay = random.uniform(min_delay, max_delay)
        logger.debug(f"Applying stealth delay: {delay:.2f}s")
        await self._smart_delay(delay)

    async def _smart_delay(self, seconds: float):
        """Apply delay with jitter to appear more human."""
        import asyncio
        jitter = random.uniform(-0.1, 0.1) * seconds
        actual_delay = max(0, seconds + jitter)
        await asyncio.sleep(actual_delay)

    def get_proxy(self) -> Optional[Dict[str, str]]:
        """Get next proxy from rotation."""
        if not self.proxy_list or not self.proxy_rotation_enabled:
            return None

        proxy = self.proxy_list[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)

        logger.debug(f"Using proxy: {proxy.get('http', 'unknown')}")
        return proxy

    def get_user_agent(self) -> str:
        """Get next user agent from rotation."""
        ua = self.user_agents[self.current_ua_index]
        self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)
        return ua

    def get_headers(self) -> Dict[str, str]:
        """Generate randomized headers for requests."""
        return {
            'User-Agent': self.get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def encrypt_data(self, data_to_encrypt: str, recipient_key_fingerprint: str) -> Optional[str]:
        """Encrypt data using GPG."""
        try:
            encrypted_data = self.gpg.encrypt(
                data_to_encrypt,
                recipient_key_fingerprint,
                always_trust=True
            )

            if encrypted_data.ok:
                logger.info(f"Data encrypted for {recipient_key_fingerprint[:16]}...")
                if self.ui:
                    self.ui.print(f"  -> Encrypted for {recipient_key_fingerprint[:16]}...")
                return str(encrypted_data)
            else:
                logger.error(f"Encryption failed: {encrypted_data.status}")
                if self.ui:
                    self.ui.print(f"[red]  -> Encryption failed: {encrypted_data.status}[/red]")
                return None

        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return None

    def decrypt_data(self, encrypted_data: str, passphrase: Optional[str] = None) -> Optional[str]:
        """Decrypt GPG-encrypted data."""
        try:
            decrypted_data = self.gpg.decrypt(encrypted_data, passphrase=passphrase)

            if decrypted_data.ok:
                logger.info("Data decrypted successfully")
                if self.ui:
                    self.ui.print("  -> Data decrypted")
                return str(decrypted_data)
            else:
                logger.error(f"Decryption failed: {decrypted_data.status}")
                if self.ui:
                    self.ui.print(f"[red]  -> Decryption failed: {decrypted_data.status}[/red]")
                return None

        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return None

    def calculate_request_footprint(self, request_count: int, duration_seconds: float) -> Dict[str, Any]:
        """Calculate operational footprint metrics."""
        requests_per_second = request_count / duration_seconds if duration_seconds > 0 else 0

        # Determine detectability level
        if requests_per_second > 10:
            detectability = "HIGH"
        elif requests_per_second > 5:
            detectability = "MEDIUM"
        elif requests_per_second > 1:
            detectability = "LOW"
        else:
            detectability = "MINIMAL"

        return {
            'total_requests': request_count,
            'duration_seconds': duration_seconds,
            'requests_per_second': round(requests_per_second, 2),
            'detectability': detectability,
            'stealth_level': self.stealth_level.name
        }

    def obfuscate_target(self, target: str) -> str:
        """Obfuscate target identifier for logs."""
        if len(target) <= 8:
            return target[:2] + '***' + target[-2:]
        return target[:4] + '***' + target[-4:]

    def should_rotate_identity(self, requests_sent: int) -> bool:
        """Determine if identity rotation is needed."""
        rotation_thresholds = {
            StealthLevel.AGGRESSIVE: 500,
            StealthLevel.NORMAL: 200,
            StealthLevel.CAUTIOUS: 50,
            StealthLevel.PARANOID: 20
        }

        threshold = rotation_thresholds[self.stealth_level]
        return requests_sent >= threshold
