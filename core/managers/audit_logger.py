import logging
import os
import json
from datetime import datetime

class AuditLogger:
    """
    A class for creating structured, JSON-formatted audit logs.
    """
    def __init__(self, log_dir: str = None, logger_name: str = 'AuditLogger'):
        self.log_dir = log_dir or os.getenv('AUDIT_LOG_DIR', '/tmp/wilsons-raiders/logs')
        os.makedirs(self.log_dir, exist_ok=True)
        
        log_file = os.path.join(self.log_dir, 'audit.log')
        
        # Prevent duplicate handlers if the logger is instantiated multiple times
        self.logger = logging.getLogger(logger_name)
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter('%(message)s') # We will format the message as JSON ourselves
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log(self, event_name: str, component: str, details: dict = None):
        """
        Creates a structured log entry.

        Args:
            event_name (str): The name of the event (e.g., 'hunt_started', 'asset_prioritized').
            component (str): The name of the manager or agent logging the event.
            details (dict, optional): A dictionary of relevant details about the event.
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event': event_name,
            'component': component,
            'details': details or {}
        }
        self.logger.info(json.dumps(log_entry))