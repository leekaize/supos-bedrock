"""
Tests for setup_wizard.py
Run: pytest tests/test_setup_wizard.py -v
"""

import pytest
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add master directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'master'))

import setup_wizard


class TestFirstRun:
    """Test first-run detection."""
    
    def test_is_first_run_no_config(self, tmp_path, monkeypatch):
        """Should return True when config doesn't exist."""
        config_path = tmp_path / "config.json"
        monkeypatch.setattr(setup_wizard, 'CONFIG_FILE', str(config_path))
        
        assert setup_wizard.is_first_run() is True
    
    def test_is_first_run_with_config(self, tmp_path, monkeypatch):
        """Should return False when config exists."""
        config_path = tmp_path / "config.json"
        config_path.write_text('{"setup_complete": true}')
        monkeypatch.setattr(setup_wizard, 'CONFIG_FILE', str(config_path))
        
        assert setup_wizard.is_first_run() is False


class TestConfigManagement:
    """Test config loading and saving."""
    
    def test_load_config_default_structure(self, tmp_path, monkeypatch):
        """Should return default config when none exists."""
        config_path = tmp_path / "config.json"
        monkeypatch.setattr(setup_wizard, 'CONFIG_FILE', str(config_path))
        
        config = setup_wizard.load_config()
        
        assert config["setup_complete"] is False
        assert "admin" in config
        assert "system" in config
        assert "network" in config
        assert "services" in config
    
    def test_save_and_load_config(self, tmp_path, monkeypatch):
        """Should save and reload config correctly."""
        config_path = tmp_path / "config.json"
        monkeypatch.setattr(setup_wizard, 'CONFIG_FILE', str(config_path))
        
        test_config = {"setup_complete": True, "test": "data"}
        setup_wizard.save_config(test_config)
        
        loaded = setup_wizard.load_config()
        assert loaded["setup_complete"] is True
        assert loaded["test"] == "data"


class TestSystemValidation:
    """Test system requirements validation."""
    
    @patch('setup_wizard.docker.from_env')
    @patch('setup_wizard.psutil.virtual_memory')
    @patch('setup_wizard.psutil.disk_usage')
    @patch('setup_wizard.psutil.cpu_count')
    def test_validate_system_all_pass(self, mock_cpu, mock_disk, mock_ram, mock_docker):
        """Should pass when all requirements met."""
        # Mock sufficient resources
        mock_docker.return_value.ping.return_value = True
        mock_ram.return_value.total = 8 * 1024**3  # 8GB
        mock_disk.return_value.free = 50 * 1024**3  # 50GB
        mock_cpu.return_value = 4
        
        valid, issues, warnings = setup_wizard.validate_system_requirements()
        
        assert valid is True
        assert len(issues) == 0
    
    @patch('setup_wizard.docker.from_env')
    @patch('setup_wizard.psutil.virtual_memory')
    @patch('setup_wizard.psutil.disk_usage')
    @patch('setup_wizard.psutil.cpu_count')
    def test_validate_system_insufficient_ram(self, mock_cpu, mock_disk, mock_ram, mock_docker):
        """Should fail when RAM insufficient."""
        mock_docker.return_value.ping.return_value = True
        mock_ram.return_value.total = 2 * 1024**3  # 2GB (below minimum)
        mock_disk.return_value.free = 50 * 1024**3
        mock_cpu.return_value = 4
        
        valid, issues, warnings = setup_wizard.validate_system_requirements()
        
        assert valid is False
        assert any("RAM" in issue for issue in issues)
    
    @patch('setup_wizard.docker.from_env')
    def test_validate_system_docker_unavailable(self, mock_docker):
        """Should fail when Docker socket inaccessible."""
        mock_docker.side_effect = Exception("Cannot connect")
        
        with patch('setup_wizard.psutil.virtual_memory') as mock_ram, \
             patch('setup_wizard.psutil.disk_usage') as mock_disk, \
             patch('setup_wizard.psutil.cpu_count') as mock_cpu:
            
            mock_ram.return_value.total = 8 * 1024**3
            mock_disk.return_value.free = 50 * 1024**3
            mock_cpu.return_value = 4
            
            valid, issues, warnings = setup_wizard.validate_system_requirements()
            
            assert valid is False
            assert any("Docker" in issue for issue in issues)


class TestDomainValidation:
    """Test domain/IP validation."""
    
    def test_validate_domain_localhost_ip(self):
        """Should accept 127.0.0.1 with warning."""
        valid, message = setup_wizard.validate_domain("127.0.0.1")
        assert valid is True
        assert "Local dev" in message
    
    def test_validate_domain_lan_ip(self):
        """Should accept LAN IPs."""
        valid, message = setup_wizard.validate_domain("192.168.1.100")
        assert valid is True
        assert "LAN" in message
        
        valid, message = setup_wizard.validate_domain("10.0.0.1")
        assert valid is True
    
    def test_validate_domain_localhost_string(self):
        """Should reject 'localhost' string."""
        valid, message = setup_wizard.validate_domain("localhost")
        assert valid is False
        assert "127.0.0.1" in message
    
    def test_validate_domain_proper_domain(self):
        """Should accept proper domain names."""
        valid, message = setup_wizard.validate_domain("example.com")
        assert valid is True
        
        valid, message = setup_wizard.validate_domain("supos.company.local")
        assert valid is True
    
    def test_validate_domain_empty(self):
        """Should reject empty domain."""
        valid, message = setup_wizard.validate_domain("")
        assert valid is False


class TestPortValidation:
    """Test port validation."""
    
    def test_validate_port_valid_range(self):
        """Should accept ports 1024-65535."""
        valid, message = setup_wizard.validate_port(8088)
        assert valid is True
        
        valid, message = setup_wizard.validate_port(1024)
        assert valid is True
        
        valid, message = setup_wizard.validate_port(65535)
        assert valid is True
    
    def test_validate_port_privileged(self):
        """Should reject ports < 1024."""
        valid, message = setup_wizard.validate_port(80)
        assert valid is False
        assert "root" in message.lower()
    
    def test_validate_port_out_of_range(self):
        """Should reject invalid port numbers."""
        valid, message = setup_wizard.validate_port(0)
        assert valid is False
        
        valid, message = setup_wizard.validate_port(70000)
        assert valid is False
    
    def test_validate_port_non_numeric(self):
        """Should reject non-numeric ports."""
        valid, message = setup_wizard.validate_port("abc")
        assert valid is False


class TestAdminUserCreation:
    """Test admin user creation and validation."""
    
    def test_create_admin_user_valid(self):
        """Should create user with hashed password."""
        user = setup_wizard.create_admin_user(
            username="admin",
            email="admin@example.com",
            password="secure_password_123"
        )
        
        assert user["username"] == "admin"
        assert user["email"] == "admin@example.com"
        assert user["password_hash"] != "secure_password_123"
        assert len(user["password_hash"]) > 20  # Hashed
    
    def test_create_admin_user_short_username(self):
        """Should reject username < 3 chars."""
        with pytest.raises(ValueError, match="at least 3 characters"):
            setup_wizard.create_admin_user("ab", "test@test.com", "password123")
    
    def test_create_admin_user_invalid_email(self):
        """Should reject invalid email."""
        with pytest.raises(ValueError, match="Invalid email"):
            setup_wizard.create_admin_user("admin", "notanemail", "password123")
    
    def test_create_admin_user_short_password(self):
        """Should reject password < 8 chars."""
        with pytest.raises(ValueError, match="at least 8 characters"):
            setup_wizard.create_admin_user("admin", "test@test.com", "short")


class TestPasswordGeneration:
    """Test secure password generation."""
    
    def test_generate_secure_password_default_length(self):
        """Should generate 16 char password by default."""
        password = setup_wizard.generate_secure_password()
        assert len(password) == 16
    
    def test_generate_secure_password_custom_length(self):
        """Should generate password of specified length."""
        password = setup_wizard.generate_secure_password(24)
        assert len(password) == 24
    
    def test_generate_service_passwords(self):
        """Should generate passwords for all services."""
        passwords = setup_wizard.generate_service_passwords()
        
        assert "postgres" in passwords
        assert "keycloak_admin" in passwords
        assert "emqx_admin" in passwords
        assert len(passwords["postgres"]) == 16
        assert len(passwords["minio_secret"]) == 24
    
    def test_generate_passwords_unique(self):
        """Generated passwords should be unique."""
        passwords = setup_wizard.generate_service_passwords()
        values = list(passwords.values())
        assert len(values) == len(set(values))  # All unique


class TestVolumesPath:
    """Test volumes path validation."""
    
    def test_validate_volumes_path_creates_directory(self, tmp_path):
        """Should create directory if it doesn't exist."""
        test_path = tmp_path / "volumes" / "data"
        
        valid, message = setup_wizard.validate_volumes_path(str(test_path))
        
        assert valid is True
        assert test_path.exists()
    
    def test_validate_volumes_path_write_permission(self, tmp_path):
        """Should test write permissions."""
        test_path = tmp_path / "writable"
        test_path.mkdir()
        
        valid, message = setup_wizard.validate_volumes_path(str(test_path))
        
        assert valid is True
        assert "ready" in message.lower()
    
    @patch('pathlib.Path.mkdir')
    def test_validate_volumes_path_no_permission(self, mock_mkdir, tmp_path):
        """Should fail when no write permission."""
        mock_mkdir.side_effect = PermissionError("Access denied")
        test_path = tmp_path / "noperm"
        
        valid, message = setup_wizard.validate_volumes_path(str(test_path))
        
        assert valid is False
        assert "permission" in message.lower()


class TestSetupCompletion:
    """Test setup completion."""
    
    def test_complete_setup(self, tmp_path, monkeypatch):
        """Should mark setup complete and save config."""
        config_path = tmp_path / "config.json"
        monkeypatch.setattr(setup_wizard, 'CONFIG_FILE', str(config_path))
        
        config = setup_wizard.load_config()
        assert config["setup_complete"] is False
        
        result = setup_wizard.complete_setup(config)
        
        assert result is True
        
        saved_config = setup_wizard.load_config()
        assert saved_config["setup_complete"] is True


# Fixtures
@pytest.fixture
def mock_docker_client():
    """Mock Docker client."""
    client = MagicMock()
    client.ping.return_value = True
    return client


@pytest.fixture
def mock_system_resources():
    """Mock system resources with sufficient capacity."""
    with patch('setup_wizard.psutil.virtual_memory') as mock_ram, \
         patch('setup_wizard.psutil.disk_usage') as mock_disk, \
         patch('setup_wizard.psutil.cpu_count') as mock_cpu:
        
        mock_ram.return_value.total = 8 * 1024**3  # 8GB
        mock_disk.return_value.free = 50 * 1024**3  # 50GB
        mock_cpu.return_value = 4
        
        yield {
            'ram': mock_ram,
            'disk': mock_disk,
            'cpu': mock_cpu
        }