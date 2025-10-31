import logging
import os
from datetime import datetime

log_dir = os.getenv('AUDIT_LOG_DIR', '/var/log/wilsons-raiders')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'audit.log')

logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def audit_log(event, user=None, agent=None, details=None):
    msg = f"EVENT={event} USER={user} AGENT={agent} DETAILS={details}"
    logging.info(msg)
