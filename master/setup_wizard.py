"""
First-run setup wizard for supOS Bedrock.
Validates system requirements and configures initial settings.
"""

import json
import os
import secrets
import string
import psutil
from pathlib import Path
from werkzeug.security import generate_password_hash
import docker

CONFIG_FILE = "/app/config.json"
DEFAULT_VOLUMES_PATH = "/volumes/supos/data"


def is_first_run():
    """Check if this is first run (no config exists)."""
    return not os.path.exists(CONFIG_FILE)


def load_config():
    """Load existing config or return default structure."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    
    # Return default config structure
    return {
        "setup_complete": False,
        "admin": {"username": "", "email": "", "password_hash": ""},
        "system": {
            "platform_type": "linux",
            "resource_spec": "4c8g",
            "name": "supOS-CE",
            "version": "V1.1.0.0-M",
            "volumes_path": DEFAULT_VOLUMES_PATH
        },
        "network": {"protocol": "http", "domain": "", "port": 8088},
        "localization": {"language": "en-US"},
        "mqtt": {
            "tcp_port": 1883,
            "websocket_tls_port": 8084,
            "use_alias_as_topic": False
        },
        "authentication": {
            "enabled": True,
            "login_path": "/supos-login",
            "oauth": {
                "realm": "supos",
                "client_name": "supos",
                "client_id": "supos",
                "client_secret": "VaOS2makbDhJJsLlYPt4Wl87bo9VzXiO",
                "grant_type": "authorization_code",
                "issuer_uri": "http://keycloak:8080",
                "refresh_token_time": 60
            }
        },
        "llm": {
            "type": "ollama",
            "openai_api_key": "",
            "openai_api_model": "gpt-4o",
            "langsmith_api_key": ""
        },
        "ldap": {"enabled": False, "url": "", "sync_user_enabled": False},
        "services": {
            "postgres": {"password": "postgres"},
            "keycloak": {"admin_username": "admin", "admin_password": "supos"},
            "emqx": {"admin_username": "admin", "admin_password": "public", "node_cookie": "secretcookie"},
            "minio": {"access_key": "admin", "secret_key": "adminpassword"},
            "portainer": {"admin_password_hash": "$$2y$$05$$ZTAqF7Tn.hil8X.ifVmQTuKiJQoZDiKDW3t1lRR2/VPR06QoHv4AC"},
            "grafana": {"admin_password": "supos"},
            "kong": {"db_password": "postgres"}
        },
        "mcp": {
            "enabled": False,
            "deployment_url": "http://mcpclient:8123",
            "supos_api_key": "4174348a-9222-4e81-b33e-5d72d2fd7f1e"
        },
        "elasticsearch": {"version": "7.10.2", "timehorizon_days": 60},
        "features": {"lazy_tree": False, "chat2db_enabled": True},
        "update_check": {"enabled": True, "interval_hours": 6, "last_check": None}
    }


def save_config(config):
    """Save config to persistent storage."""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def validate_system_requirements():
    """
    Validate system meets minimum requirements.
    Returns: (bool, list of messages)
    """
    issues = []
    warnings = []
    
    # Check Docker socket
    try:
        client = docker.from_env()
        client.ping()
    except Exception as e:
        issues.append(f"Docker socket inaccessible: {e}")
    
    # Check RAM (minimum 4GB recommended)
    ram_gb = psutil.virtual_memory().total / (1024**3)
    if ram_gb < 4:
        issues.append(f"Insufficient RAM: {ram_gb:.1f}GB (minimum 4GB)")
    elif ram_gb < 8:
        warnings.append(f"RAM is {ram_gb:.1f}GB. 8GB+ recommended for full stack.")
    
    # Check disk space (minimum 10GB free)
    disk = psutil.disk_usage('/')
    disk_free_gb = disk.free / (1024**3)
    if disk_free_gb < 10:
        issues.append(f"Insufficient disk: {disk_free_gb:.1f}GB free (minimum 10GB)")
    elif disk_free_gb < 20:
        warnings.append(f"Disk has {disk_free_gb:.1f}GB free. 20GB+ recommended.")
    
    # Check CPU cores (minimum 2)
    cpu_count = psutil.cpu_count()
    if cpu_count < 2:
        issues.append(f"Insufficient CPU: {cpu_count} cores (minimum 2)")
    elif cpu_count < 4:
        warnings.append(f"CPU has {cpu_count} cores. 4+ recommended for production.")
    
    return len(issues) == 0, issues, warnings


def validate_domain(domain):
    """
    Validate domain format and provide guidance.
    Returns: (bool, str) - (is_valid, message)
    """
    if not domain:
        return False, "Domain cannot be empty."
    
    # Allow 127.0.0.1 with warning
    if domain == "127.0.0.1":
        return True, "⚠️ Local dev only. Won't work from other machines."
    
    # Allow LAN IPs
    if domain.startswith("192.168.") or domain.startswith("10.") or domain.startswith("172."):
        return True, "✓ LAN IP. Accessible from local network."
    
    # Block 'localhost' string
    if "localhost" in domain.lower():
        return False, "Use 127.0.0.1 instead of 'localhost'."
    
    # Allow proper domains
    if "." in domain and not domain.replace(".", "").replace("-", "").isdigit():
        return True, "✓ Domain configured."
    
    return False, "Invalid domain format. Use IP or domain name."


def validate_port(port):
    """Validate port is in valid range and not privileged."""
    try:
        port = int(port)
        if port < 1 or port > 65535:
            return False, "Port must be between 1-65535."
        if port < 1024:
            return False, "Port < 1024 requires root privileges."
        return True, f"✓ Port {port} is valid."
    except ValueError:
        return False, "Port must be a number."


def generate_secure_password(length=16):
    """Generate cryptographically secure password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def create_admin_user(username, email, password):
    """
    Create admin user with hashed password.
    Returns: dict with user info
    """
    if not username or len(username) < 3:
        raise ValueError("Username must be at least 3 characters.")
    
    if not email or '@' not in email:
        raise ValueError("Invalid email address.")
    
    if not password or len(password) < 8:
        raise ValueError("Password must be at least 8 characters.")
    
    return {
        "username": username,
        "email": email,
        "password_hash": generate_password_hash(password)
    }


def generate_service_passwords():
    """
    Generate secure passwords for all services.
    Returns: dict with service passwords
    """
    return {
        "postgres": generate_secure_password(),
        "keycloak_admin": generate_secure_password(),
        "emqx_admin": generate_secure_password(),
        "minio_secret": generate_secure_password(24),
        "kong_db": generate_secure_password()
    }


def validate_volumes_path(path):
    """
    Validate volumes path exists and is writable.
    Returns: (bool, str) - (is_valid, message)
    """
    try:
        path_obj = Path(path)
        
        # Create if doesn't exist
        path_obj.mkdir(parents=True, exist_ok=True)
        
        # Test write permissions
        test_file = path_obj / ".write_test"
        test_file.touch()
        test_file.unlink()
        
        return True, f"✓ Volumes path {path} is ready."
    except PermissionError:
        return False, f"No write permission for {path}."
    except Exception as e:
        return False, f"Error with path {path}: {e}"


def complete_setup(config):
    """Mark setup as complete and save config."""
    config["setup_complete"] = True
    save_config(config)
    return True