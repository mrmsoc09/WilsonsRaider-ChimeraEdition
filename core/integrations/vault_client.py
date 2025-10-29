"""HashiCorp Vault Client - Production-Grade Secret Management

Comprehensive Vault integration with multiple authentication methods,
secret caching, lease management, and audit logging.
Version: 2.0.0
"""

import os
import time
import logging
import threading
from typing import Any, Dict, Optional, Tuple
from datetime import datetime, timedelta
from functools import wraps

try:
    import hvac
    from hvac.exceptions import VaultError, InvalidPath
except ImportError:
    hvac = None
    VaultError = Exception
    InvalidPath = Exception

from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    retry_if_exception_type, before_sleep_log
)

logger = logging.getLogger(__name__)

class VaultNotConfigured(Exception):
    """Raised when Vault is not properly configured."""
    pass

class VaultAuthenticationError(Exception):
    """Raised when Vault authentication fails."""
    pass

class SecretCache:
    """Thread-safe secret cache with TTL."""
    
    def __init__(self, default_ttl: int = 300):
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.default_ttl = default_ttl
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached secret if not expired."""
        with self.lock:
            if key in self.cache:
                value, expiry = self.cache[key]
                if time.time() < expiry:
                    return value
                else:
                    del self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Cache secret with TTL."""
        with self.lock:
            expiry = time.time() + (ttl or self.default_ttl)
            self.cache[key] = (value, expiry)
    
    def invalidate(self, key: str) -> None:
        """Invalidate cached secret."""
        with self.lock:
            self.cache.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cached secrets."""
        with self.lock:
            self.cache.clear()

class VaultClient:
    """Production-grade HashiCorp Vault client."""
    
    def __init__(self, 
                 addr: Optional[str] = None,
                 token: Optional[str] = None,
                 namespace: Optional[str] = None,
                 cache_enabled: bool = True,
                 cache_ttl: int = 300,
                 audit_enabled: bool = True):
        
        if hvac is None:
            raise VaultNotConfigured(
                "hvac library not installed. Install with: pip install hvac"
            )
        
        # Configuration
        self.addr = addr or os.getenv("VAULT_ADDR")
        self.namespace = namespace or os.getenv("VAULT_NAMESPACE")
        self._token = token or os.getenv("VAULT_TOKEN")
        
        if not self.addr:
            raise VaultNotConfigured(
                "VAULT_ADDR not configured. Set via environment or constructor."
            )
        
        # Initialize client
        self.client = hvac.Client(
            url=self.addr,
            token=self._token,
            namespace=self.namespace,
            verify=True
        )
        
        # Features
        self.cache_enabled = cache_enabled
        self.audit_enabled = audit_enabled
        self.cache = SecretCache(default_ttl=cache_ttl) if cache_enabled else None
        
        # Token management
        self.token_ttl: Optional[int] = None
        self.token_renewable: bool = False
        self.renewal_thread: Optional[threading.Thread] = None
        
        logger.info(f"VaultClient initialized: addr={self.addr}")
        
        if not self.is_ready():
            logger.warning("Vault is not ready or not authenticated")
    
    def is_ready(self) -> bool:
        """Check Vault health and authentication status."""
        try:
            health = self.client.sys.read_health_status(method="GET")
            if health.get("sealed", True):
                logger.error("Vault is sealed")
                return False
            
            if self.client.token:
                self.client.auth.token.lookup_self()
                return True
            return False
        except Exception as e:
            logger.error(f"Vault health check failed: {e}")
            return False
    
    def authenticate_token(self, token: str) -> bool:
        """Authenticate with token."""
        try:
            self.client.token = token
            lookup = self.client.auth.token.lookup_self()
            self.token_ttl = lookup.get("data", {}).get("ttl")
            self.token_renewable = lookup.get("data", {}).get("renewable", False)
            logger.info(f"Token auth successful: ttl={self.token_ttl}")
            if self.token_renewable:
                self._start_token_renewal()
            self._audit_log("authenticate_token", "success")
            return True
        except Exception as e:
            logger.error(f"Token auth failed: {e}")
            self._audit_log("authenticate_token", "failure", str(e))
            raise VaultAuthenticationError(f"Token auth failed: {e}")
    
    def authenticate_approle(self, role_id: str, secret_id: str) -> bool:
        """Authenticate with AppRole."""
        try:
            response = self.client.auth.approle.login(role_id=role_id, secret_id=secret_id)
            self.client.token = response["auth"]["client_token"]
            self.token_ttl = response["auth"]["lease_duration"]
            self.token_renewable = response["auth"]["renewable"]
            logger.info(f"AppRole auth successful: ttl={self.token_ttl}")
            if self.token_renewable:
                self._start_token_renewal()
            self._audit_log("authenticate_approle", "success")
            return True
        except Exception as e:
            logger.error(f"AppRole auth failed: {e}")
            self._audit_log("authenticate_approle", "failure", str(e))
            raise VaultAuthenticationError(f"AppRole auth failed: {e}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10),
           retry=retry_if_exception_type(VaultError), before_sleep=before_sleep_log(logger, logging.WARNING))
    def get_secret(self, path: str, key: Optional[str] = None, mount_point: str = "secret", version: int = 2) -> Any:
        """Get secret from Vault with caching."""
        cache_key = f"{mount_point}/{path}/{key or 'all'}"
        if self.cache_enabled:
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached
        try:
            if version == 2:
                response = self.client.secrets.kv.v2.read_secret_version(path=path, mount_point=mount_point)
                data = response.get("data", {}).get("data", {})
            else:
                response = self.client.secrets.kv.v1.read_secret(path=path, mount_point=mount_point)
                data = response.get("data", {})
            result = data.get(key) if key else data
            if self.cache_enabled and result is not None:
                self.cache.set(cache_key, result)
            self._audit_log("get_secret", "success", path)
            return result
        except InvalidPath:
            logger.warning(f"Secret not found: {path}")
            self._audit_log("get_secret", "not_found", path)
            return None
        except Exception as e:
            logger.error(f"Failed to get secret {path}: {e}")
            self._audit_log("get_secret", "error", f"{path}: {e}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10),
           retry=retry_if_exception_type(VaultError))
    def put_secret(self, path: str, data: Dict[str, Any], mount_point: str = "secret", version: int = 2) -> None:
        """Put secret into Vault and invalidate cache."""
        try:
            if version == 2:
                self.client.secrets.kv.v2.create_or_update_secret(path=path, secret=data, mount_point=mount_point)
            else:
                self.client.secrets.kv.v1.create_or_update_secret(path=path, secret=data, mount_point=mount_point)
            if self.cache_enabled:
                self.cache.invalidate(f"{mount_point}/{path}/all")
                for k in data.keys():
                    self.cache.invalidate(f"{mount_point}/{path}/{k}")
            self._audit_log("put_secret", "success", path)
            logger.info(f"Secret written: {path}")
        except Exception as e:
            logger.error(f"Failed to put secret {path}: {e}")
            self._audit_log("put_secret", "error", f"{path}: {e}")
            raise
    
    def renew_token(self, increment: Optional[int] = None) -> bool:
        """Renew current token."""
        try:
            response = self.client.auth.token.renew_self(increment=increment)
            self.token_ttl = response["auth"]["lease_duration"]
            logger.info(f"Token renewed: ttl={self.token_ttl}")
            self._audit_log("renew_token", "success")
            return True
        except Exception as e:
            logger.error(f"Token renewal failed: {e}")
            self._audit_log("renew_token", "error", str(e))
            return False
    
    def _start_token_renewal(self) -> None:
        """Start background token renewal thread."""
        if self.renewal_thread and self.renewal_thread.is_alive():
            return
        self.renewal_thread = threading.Thread(target=self._renewal_loop, daemon=True)
        self.renewal_thread.start()
        logger.info("Token renewal thread started")
    
    def _renewal_loop(self) -> None:
        """Background loop for token renewal."""
        while True:
            if self.token_ttl and self.token_renewable:
                sleep_time = max(self.token_ttl * 0.5, 60)
                time.sleep(sleep_time)
                try:
                    self.renew_token()
                except Exception as e:
                    logger.error(f"Auto-renewal failed: {e}")
            else:
                break
    
    def _audit_log(self, operation: str, status: str, details: str = "") -> None:
        """Log audit trail for secret operations."""
        if not self.audit_enabled:
            return
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "status": status,
            "details": details
        }
        logger.info(f"AUDIT: {log_entry}")
    
    def get_health(self) -> Dict[str, Any]:
        """Get Vault health metrics."""
        try:
            health = self.client.sys.read_health_status(method="GET")
            return {
                "initialized": health.get("initialized", False),
                "sealed": health.get("sealed", True),
                "standby": health.get("standby", False),
                "version": health.get("version", "unknown")
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"error": str(e)}
    
    def close(self) -> None:
        """Cleanup resources."""
        if self.cache:
            self.cache.clear()
        logger.info("VaultClient closed")
