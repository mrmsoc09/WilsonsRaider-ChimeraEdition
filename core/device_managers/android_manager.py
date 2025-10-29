import yaml
import asyncio
import os
from core import ui
from secret_manager import SecretManager
from core.config_manager import ConfigManager

class AndroidManager:
    """Manages a fleet of Android devices running Termux for distributed scanning."""

    def __init__(self):
        self.secrets = SecretManager()
        self.config = ConfigManager()
        self.devices_config_path = self.config.get('paths.devices_config')
        self.devices = self._load_device_config()
        self.ssh_keys = self._load_ssh_keys()
        if self.devices:
            ui.print_info(f"AndroidManager initialized with {len(self.devices)} devices.")

    def _load_device_config(self):
        try:
            with open(self.devices_config_path, 'r') as f:
                return yaml.safe_load(f).get('android_devices', [])
        except FileNotFoundError:
            ui.print_warning(f"{self.devices_config_path} not found. No Android devices will be managed.")
            return []

    def _load_ssh_keys(self):
        """Loads required SSH private keys from Vault and stores them locally for use."""
        keys = {}
        for device in self.devices:
            key_name = device.get('ssh_key_name')
            if key_name and key_name not in keys:
                private_key = self.secrets.get_secret('wilsons-raiders/ssh_keys', key_name)
                if private_key:
                    key_path = f"/tmp/{key_name}"
                    try:
                        with open(key_path, 'w') as f:
                            f.write(private_key)
                        os.chmod(key_path, 0o600)
                        keys[key_name] = key_path
                        ui.print_info(f"Loaded SSH key '{key_name}' for Android devices.")
                    except IOError as e:
                        ui.print_error(f"Failed to write SSH key '{key_name}' to /tmp: {e}")
                else:
                    ui.print_error(f"Could not load SSH key '{key_name}' from Vault.")
        return keys

    async def get_available_nodes(self) -> list:
        """Returns a list of all configured devices. Future versions will add health checks."""
        return self.devices

    async def execute_job_on_node(self, node_id: str, job: dict) -> dict:
        """Constructs and executes a job on a specific Android device."""
        target = job.get('target')
        scan_type = job.get('scan_type', 'nuclei')
        
        command_to_run = f"cd wilsons-raiders && python3 device_agent.py --scan {scan_type} --target {target}"
        
        return await self.execute_command(node_id, command_to_run)

    async def execute_command(self, device_id: str, command: str, timeout: int = 600) -> dict:
        """
        Executes a shell command on a specific Android device via SSH using asyncio.
        """
        device = next((d for d in self.devices if d['id'] == device_id), None)
        if not device:
            return {"status": "error", "stderr": f"Device with ID '{device_id}' not found."}

        key_name = device.get('ssh_key_name')
        key_path = self.ssh_keys.get(key_name)
        if not key_path:
            return {"status": "error", "stderr": f"SSH key '{key_name}' not available for device '{device_id}'."}

        ssh_command = [
            'ssh',
            '-i', key_path,
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            f"{device['ssh_user']}@{device['ip_address']}",
            command
        ]

        ui.print_info(f"Executing on '{device_id}': {command}")
        try:
            proc = await asyncio.create_subprocess_exec(
                *ssh_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            
            if proc.returncode == 0:
                return {"status": "success", "stdout": stdout.decode(), "stderr": stderr.decode()}
            else:
                return {"status": "error", "stdout": stdout.decode(), "stderr": stderr.decode(), "exit_code": proc.returncode}
        except Exception as e:
            ui.print_error(f"Failed to execute command on '{device_id}': {e}")
            return {"status": "error", "stderr": str(e)}
