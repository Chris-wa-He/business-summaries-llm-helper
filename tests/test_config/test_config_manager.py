"""
ConfigManager单元测试 / ConfigManager Unit Tests

测试配置管理器的各项功能，包括配置加载、验证和AWS凭证管理
Test various functions of configuration manager, including config loading, validation and AWS credentials management
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound

from src.config.config_manager import ConfigManager, ConfigurationError, AWSCredentialsError


class TestConfigManager:
    """ConfigManager测试类 / ConfigManager test class"""
    
    def setup_method(self):
        """测试方法设置 / Test method setup"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.yaml"
        
    def create_test_config(self, config_data: dict):
        """创建测试配置文件 / Create test configuration file"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
    
    def get_minimal_valid_models(self):
        """获取最小有效模型配置 / Get minimal valid models configuration"""
        return {
            'claude': [{'id': 'test-model', 'name': 'Test Model'}]
        }
    
    def test_load_valid_config(self):
        """测试加载有效配置 / Test loading valid configuration"""
        config_data = {
            'aws': {
                'auth_method': 'profile',
                'profile_name': 'default',
                'region': 'us-east-1'
            },
            'models': {
                'claude': [{'id': 'test-model', 'name': 'Test Model'}]
            },
            'system_prompt': 'Test prompt',
            'history_folder': './test_history',
            'app': {
                'title': 'Test App',
                'max_tokens': 1000,
                'temperature': 0.5
            }
        }
        
        self.create_test_config(config_data)
        config_manager = ConfigManager(str(self.config_path))
        
        loaded_config = config_manager.load_config()
        assert loaded_config == config_data
    
    def test_load_config_file_not_exists(self):
        """测试配置文件不存在时的处理 / Test handling when config file doesn't exist"""
        non_existent_path = Path(self.temp_dir) / "non_existent.yaml"
        config_manager = ConfigManager(str(non_existent_path))
        
        # 应该创建默认配置文件 / Should create default config file
        config_manager.load_config()
        assert non_existent_path.exists()
    
    def test_validate_config_missing_section(self):
        """测试缺少必要配置节的验证 / Test validation with missing required sections"""
        config_data = {
            'aws': {
                'auth_method': 'profile',
                'profile_name': 'default',
                'region': 'us-east-1'
            }
            # 缺少其他必要节 / Missing other required sections
        }
        
        self.create_test_config(config_data)
        config_manager = ConfigManager(str(self.config_path))
        
        with pytest.raises(ConfigurationError, match="缺少必要配置节"):
            config_manager.load_config()
    
    def test_validate_invalid_auth_method(self):
        """测试无效的认证方式 / Test invalid authentication method"""
        config_data = {
            'aws': {
                'auth_method': 'invalid_method',
                'region': 'us-east-1'
            },
            'models': self.get_minimal_valid_models(),
            'system_prompt': 'test',
            'history_folder': './test',
            'app': {}
        }
        
        self.create_test_config(config_data)
        config_manager = ConfigManager(str(self.config_path))
        
        with pytest.raises(ConfigurationError, match="无效的AWS认证方式"):
            config_manager.load_config()
    
    def test_validate_ak_sk_missing_credentials(self):
        """测试AK/SK方式缺少凭证 / Test missing credentials for AK/SK method"""
        config_data = {
            'aws': {
                'auth_method': 'ak_sk',
                'access_key_id': '',  # 空凭证 / Empty credentials
                'secret_access_key': '',
                'region': 'us-east-1'
            },
            'models': self.get_minimal_valid_models(),
            'system_prompt': 'test',
            'history_folder': './test',
            'app': {}
        }
        
        self.create_test_config(config_data)
        config_manager = ConfigManager(str(self.config_path))
        
        with pytest.raises(ConfigurationError, match="access_key_id和secret_access_key不能为空"):
            config_manager.load_config()
    
    def test_get_aws_credentials_profile_method(self):
        """测试获取Profile方式的AWS凭证 / Test getting AWS credentials with profile method"""
        config_data = {
            'aws': {
                'auth_method': 'profile',
                'profile_name': 'test-profile',
                'region': 'us-west-2'
            },
            'models': self.get_minimal_valid_models(),
            'system_prompt': 'test',
            'history_folder': './test',
            'app': {}
        }
        
        self.create_test_config(config_data)
        config_manager = ConfigManager(str(self.config_path))
        config_manager.load_config()
        
        credentials = config_manager.get_aws_credentials()
        
        assert credentials['auth_method'] == 'profile'
        assert credentials['profile_name'] == 'test-profile'
        assert credentials['region'] == 'us-west-2'
    
    def test_get_aws_credentials_ak_sk_method(self):
        """测试获取AK/SK方式的AWS凭证 / Test getting AWS credentials with AK/SK method"""
        config_data = {
            'aws': {
                'auth_method': 'ak_sk',
                'access_key_id': 'test-access-key',
                'secret_access_key': 'test-secret-key',
                'region': 'eu-west-1'
            },
            'models': self.get_minimal_valid_models(),
            'system_prompt': 'test',
            'history_folder': './test',
            'app': {}
        }
        
        self.create_test_config(config_data)
        config_manager = ConfigManager(str(self.config_path))
        config_manager.load_config()
        
        credentials = config_manager.get_aws_credentials()
        
        assert credentials['auth_method'] == 'ak_sk'
        assert credentials['access_key_id'] == 'test-access-key'
        assert credentials['secret_access_key'] == 'test-secret-key'
        assert credentials['region'] == 'eu-west-1'
    
    @patch('boto3.Session')
    def test_validate_aws_credentials_success(self, mock_session):
        """测试AWS凭证验证成功 / Test successful AWS credentials validation"""
        # 模拟成功的STS调用 / Mock successful STS call
        mock_sts_client = MagicMock()
        mock_sts_client.get_caller_identity.return_value = {'Account': '123456789012'}
        mock_session.return_value.client.return_value = mock_sts_client
        
        config_data = {
            'aws': {
                'auth_method': 'profile',
                'profile_name': 'default',
                'region': 'us-east-1'
            },
            'models': self.get_minimal_valid_models(),
            'system_prompt': 'test',
            'history_folder': './test',
            'app': {}
        }
        
        self.create_test_config(config_data)
        config_manager = ConfigManager(str(self.config_path))
        config_manager.load_config()
        
        result = config_manager.validate_aws_credentials()
        assert result is True
    
    @patch('boto3.Session')
    def test_validate_aws_credentials_profile_not_found(self, mock_session):
        """测试AWS Profile未找到 / Test AWS profile not found"""
        mock_session.side_effect = ProfileNotFound(profile='test-profile')
        
        config_data = {
            'aws': {
                'auth_method': 'profile',
                'profile_name': 'test-profile',
                'region': 'us-east-1'
            },
            'models': self.get_minimal_valid_models(),
            'system_prompt': 'test',
            'history_folder': './test',
            'app': {}
        }
        
        self.create_test_config(config_data)
        config_manager = ConfigManager(str(self.config_path))
        config_manager.load_config()
        
        with pytest.raises(AWSCredentialsError, match="AWS Profile未找到"):
            config_manager.validate_aws_credentials()
    
    @patch('boto3.Session')
    def test_validate_aws_credentials_no_credentials(self, mock_session):
        """测试AWS凭证未配置 / Test AWS credentials not configured"""
        mock_sts_client = MagicMock()
        mock_sts_client.get_caller_identity.side_effect = NoCredentialsError()
        mock_session.return_value.client.return_value = mock_sts_client
        
        config_data = {
            'aws': {
                'auth_method': 'ak_sk',
                'access_key_id': 'invalid-key',
                'secret_access_key': 'invalid-secret',
                'region': 'us-east-1'
            },
            'models': self.get_minimal_valid_models(),
            'system_prompt': 'test',
            'history_folder': './test',
            'app': {}
        }
        
        self.create_test_config(config_data)
        config_manager = ConfigManager(str(self.config_path))
        config_manager.load_config()
        
        with pytest.raises(AWSCredentialsError, match="AWS凭证未配置或无效"):
            config_manager.validate_aws_credentials()
    
    @patch('boto3.Session')
    def test_get_boto3_session_profile(self, mock_session):
        """测试获取boto3 session (Profile方式) / Test getting boto3 session (profile method)"""
        config_data = {
            'aws': {
                'auth_method': 'profile',
                'profile_name': 'test-profile',
                'region': 'us-east-1'
            },
            'models': self.get_minimal_valid_models(),
            'system_prompt': 'test',
            'history_folder': './test',
            'app': {}
        }
        
        self.create_test_config(config_data)
        config_manager = ConfigManager(str(self.config_path))
        config_manager.load_config()
        
        session = config_manager.get_boto3_session()
        
        mock_session.assert_called_with(
            profile_name='test-profile',
            region_name='us-east-1'
        )
    
    @patch('boto3.Session')
    def test_get_boto3_session_ak_sk(self, mock_session):
        """测试获取boto3 session (AK/SK方式) / Test getting boto3 session (AK/SK method)"""
        config_data = {
            'aws': {
                'auth_method': 'ak_sk',
                'access_key_id': 'test-key',
                'secret_access_key': 'test-secret',
                'region': 'us-west-2'
            },
            'models': self.get_minimal_valid_models(),
            'system_prompt': 'test',
            'history_folder': './test',
            'app': {}
        }
        
        self.create_test_config(config_data)
        config_manager = ConfigManager(str(self.config_path))
        config_manager.load_config()
        
        session = config_manager.get_boto3_session()
        
        mock_session.assert_called_with(
            aws_access_key_id='test-key',
            aws_secret_access_key='test-secret',
            region_name='us-west-2'
        )
    
    def test_get_system_prompt(self):
        """测试获取系统提示词 / Test getting system prompt"""
        custom_prompt = "这是自定义的系统提示词"
        config_data = {
            'aws': {
                'auth_method': 'profile',
                'profile_name': 'default',
                'region': 'us-east-1'
            },
            'models': self.get_minimal_valid_models(),
            'system_prompt': custom_prompt,
            'history_folder': './test',
            'app': {}
        }
        
        self.create_test_config(config_data)
        config_manager = ConfigManager(str(self.config_path))
        config_manager.load_config()
        
        prompt = config_manager.get_system_prompt()
        assert prompt == custom_prompt
    
    def test_get_history_folder(self):
        """测试获取历史文件夹路径 / Test getting history folder path"""
        config_data = {
            'aws': {
                'auth_method': 'profile',
                'profile_name': 'default',
                'region': 'us-east-1'
            },
            'models': self.get_minimal_valid_models(),
            'system_prompt': 'test',
            'history_folder': './custom_history',
            'app': {}
        }
        
        self.create_test_config(config_data)
        config_manager = ConfigManager(str(self.config_path))
        config_manager.load_config()
        
        folder = config_manager.get_history_folder()
        assert folder == './custom_history'
    
    def test_get_models_config(self):
        """测试获取模型配置 / Test getting models configuration"""
        models_config = {
            'claude': [{'id': 'claude-test', 'name': 'Claude Test'}],
            'nova': [{'id': 'nova-test', 'name': 'Nova Test'}]
        }
        config_data = {
            'aws': {
                'auth_method': 'profile',
                'profile_name': 'default',
                'region': 'us-east-1'
            },
            'models': models_config,
            'system_prompt': 'test',
            'history_folder': './test',
            'app': {}
        }
        
        self.create_test_config(config_data)
        config_manager = ConfigManager(str(self.config_path))
        config_manager.load_config()
        
        models = config_manager.get_models_config()
        assert models == models_config
    
    def test_get_app_config(self):
        """测试获取应用配置 / Test getting application configuration"""
        app_config = {
            'title': 'Custom Title',
            'max_tokens': 2000,
            'temperature': 0.8
        }
        config_data = {
            'aws': {
                'auth_method': 'profile',
                'profile_name': 'default',
                'region': 'us-east-1'
            },
            'models': self.get_minimal_valid_models(),
            'system_prompt': 'test',
            'history_folder': './test',
            'app': app_config
        }
        
        self.create_test_config(config_data)
        config_manager = ConfigManager(str(self.config_path))
        config_manager.load_config()
        
        app = config_manager.get_app_config()
        assert app == app_config
