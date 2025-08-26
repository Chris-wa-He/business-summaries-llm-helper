"""
配置管理器系统提示词功能单元测试 / Configuration Manager System Prompts Unit Tests
"""

import pytest
import tempfile
import shutil
import yaml
from pathlib import Path
from src.config.config_manager import ConfigManager, ConfigurationError


class TestConfigManagerSystemPrompts:
    """配置管理器系统提示词功能测试类 / Configuration Manager System Prompts Test Class"""
    
    def setup_method(self):
        """测试前设置 / Setup before each test"""
        # 创建临时目录和配置文件 / Create temporary directory and config file
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.yaml"
        
        # 创建基础配置 / Create basic configuration
        self.base_config = {
            'aws': {
                'auth_method': 'profile',
                'profile_name': 'default',
                'region': 'us-east-1'
            },
            'models': {
                'claude': [{'id': 'claude-3', 'name': 'Claude 3'}]
            },
            'system_prompt': 'Default prompt',
            'history_folder': './history_references',
            'app': {
                'title': 'Test App',
                'max_tokens': 4000,
                'temperature': 0.7
            }
        }
    
    def teardown_method(self):
        """测试后清理 / Cleanup after each test"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def _create_config_file(self, config_data: dict):
        """创建配置文件 / Create configuration file"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
    
    def test_get_app_config_with_default_system_prompts(self):
        """测试获取包含默认系统提示词配置的应用配置 / Test getting app config with default system prompts"""
        # 创建不包含system_prompts的配置 / Create config without system_prompts
        self._create_config_file(self.base_config)
        
        config_manager = ConfigManager(str(self.config_path))
        config_manager.load_config()
        
        app_config = config_manager.get_app_config()
        
        # 验证system_prompts配置被自动添加 / Verify system_prompts config was automatically added
        assert 'system_prompts' in app_config
        system_prompts_config = app_config['system_prompts']
        
        assert system_prompts_config['prompts_folder'] == './system_prompts'
        assert system_prompts_config['active_prompt'] == 'default'
        assert system_prompts_config['auto_create_history_folders'] is True
        assert system_prompts_config['prompt_file_extension'] == '.md'
    
    def test_get_app_config_with_custom_system_prompts(self):
        """测试获取包含自定义系统提示词配置的应用配置 / Test getting app config with custom system prompts"""
        # 添加自定义system_prompts配置 / Add custom system_prompts config
        custom_config = self.base_config.copy()
        custom_config['app']['system_prompts'] = {
            'prompts_folder': './custom_prompts',
            'active_prompt': 'custom',
            'auto_create_history_folders': False,
            'prompt_file_extension': '.txt'
        }
        
        self._create_config_file(custom_config)
        
        config_manager = ConfigManager(str(self.config_path))
        config_manager.load_config()
        
        app_config = config_manager.get_app_config()
        system_prompts_config = app_config['system_prompts']
        
        # 验证自定义配置被保留 / Verify custom config is preserved
        assert system_prompts_config['prompts_folder'] == './custom_prompts'
        assert system_prompts_config['active_prompt'] == 'custom'
        assert system_prompts_config['auto_create_history_folders'] is False
        assert system_prompts_config['prompt_file_extension'] == '.txt'
    
    def test_create_default_config_includes_system_prompts(self):
        """测试创建默认配置时包含系统提示词配置 / Test default config creation includes system prompts"""
        config_manager = ConfigManager(str(self.config_path))
        config_manager.load_config()  # 这会创建默认配置 / This will create default config
        
        # 读取创建的配置文件 / Read the created config file
        with open(self.config_path, 'r', encoding='utf-8') as f:
            created_config = yaml.safe_load(f)
        
        # 验证system_prompts配置存在 / Verify system_prompts config exists
        assert 'system_prompts' in created_config['app']
        system_prompts_config = created_config['app']['system_prompts']
        
        assert system_prompts_config['prompts_folder'] == './system_prompts'
        assert system_prompts_config['active_prompt'] == 'default'
        assert system_prompts_config['auto_create_history_folders'] is True
        assert system_prompts_config['prompt_file_extension'] == '.md'
    
    def test_validate_system_prompts_config_valid(self):
        """测试有效的系统提示词配置验证 / Test valid system prompts config validation"""
        valid_config = self.base_config.copy()
        valid_config['app']['system_prompts'] = {
            'prompts_folder': './test_prompts',
            'active_prompt': 'test',
            'auto_create_history_folders': True,
            'prompt_file_extension': '.md'
        }
        
        self._create_config_file(valid_config)
        
        config_manager = ConfigManager(str(self.config_path))
        # 应该不抛出异常 / Should not raise exception
        config_manager.load_config()
    
    def test_validate_system_prompts_config_invalid_type(self):
        """测试无效类型的系统提示词配置验证 / Test invalid type system prompts config validation"""
        invalid_config = self.base_config.copy()
        invalid_config['app']['system_prompts'] = "invalid_string"  # 应该是字典 / Should be dict
        
        self._create_config_file(invalid_config)
        
        config_manager = ConfigManager(str(self.config_path))
        with pytest.raises(ConfigurationError, match="system_prompts配置必须是字典类型"):
            config_manager.load_config()
    
    def test_validate_system_prompts_config_invalid_prompts_folder(self):
        """测试无效prompts_folder的系统提示词配置验证 / Test invalid prompts_folder system prompts config validation"""
        invalid_config = self.base_config.copy()
        invalid_config['app']['system_prompts'] = {
            'prompts_folder': 123,  # 应该是字符串 / Should be string
            'active_prompt': 'test'
        }
        
        self._create_config_file(invalid_config)
        
        config_manager = ConfigManager(str(self.config_path))
        with pytest.raises(ConfigurationError, match="prompts_folder必须是字符串类型"):
            config_manager.load_config()
    
    def test_validate_system_prompts_config_invalid_active_prompt(self):
        """测试无效active_prompt的系统提示词配置验证 / Test invalid active_prompt system prompts config validation"""
        invalid_config = self.base_config.copy()
        invalid_config['app']['system_prompts'] = {
            'prompts_folder': './prompts',
            'active_prompt': 123  # 应该是字符串 / Should be string
        }
        
        self._create_config_file(invalid_config)
        
        config_manager = ConfigManager(str(self.config_path))
        with pytest.raises(ConfigurationError, match="active_prompt必须是字符串类型"):
            config_manager.load_config()
    
    def test_validate_system_prompts_config_invalid_auto_create(self):
        """测试无效auto_create_history_folders的系统提示词配置验证 / Test invalid auto_create_history_folders system prompts config validation"""
        invalid_config = self.base_config.copy()
        invalid_config['app']['system_prompts'] = {
            'prompts_folder': './prompts',
            'active_prompt': 'test',
            'auto_create_history_folders': 'yes'  # 应该是布尔值 / Should be boolean
        }
        
        self._create_config_file(invalid_config)
        
        config_manager = ConfigManager(str(self.config_path))
        with pytest.raises(ConfigurationError, match="auto_create_history_folders必须是布尔类型"):
            config_manager.load_config()
    
    def test_validate_system_prompts_config_invalid_extension(self):
        """测试无效prompt_file_extension的系统提示词配置验证 / Test invalid prompt_file_extension system prompts config validation"""
        invalid_config = self.base_config.copy()
        invalid_config['app']['system_prompts'] = {
            'prompts_folder': './prompts',
            'active_prompt': 'test',
            'prompt_file_extension': 123  # 应该是字符串 / Should be string
        }
        
        self._create_config_file(invalid_config)
        
        config_manager = ConfigManager(str(self.config_path))
        with pytest.raises(ConfigurationError, match="prompt_file_extension必须是字符串类型"):
            config_manager.load_config()
    
    def test_validate_system_prompts_config_extension_without_dot(self):
        """测试不以点开头的prompt_file_extension验证 / Test prompt_file_extension validation without dot"""
        invalid_config = self.base_config.copy()
        invalid_config['app']['system_prompts'] = {
            'prompts_folder': './prompts',
            'active_prompt': 'test',
            'prompt_file_extension': 'md'  # 应该以点开头 / Should start with dot
        }
        
        self._create_config_file(invalid_config)
        
        config_manager = ConfigManager(str(self.config_path))
        with pytest.raises(ConfigurationError, match="prompt_file_extension必须以点开头"):
            config_manager.load_config()
    
    def test_partial_system_prompts_config(self):
        """测试部分系统提示词配置与默认值合并 / Test partial system prompts config merging with defaults"""
        partial_config = self.base_config.copy()
        partial_config['app']['system_prompts'] = {
            'prompts_folder': './custom_prompts'  # 只设置部分配置 / Only set partial config
        }
        
        self._create_config_file(partial_config)
        
        config_manager = ConfigManager(str(self.config_path))
        config_manager.load_config()
        
        app_config = config_manager.get_app_config()
        system_prompts_config = app_config['system_prompts']
        
        # 验证自定义配置被保留，其他使用默认值 / Verify custom config is preserved, others use defaults
        assert system_prompts_config['prompts_folder'] == './custom_prompts'
        assert system_prompts_config['active_prompt'] == 'default'  # 默认值 / Default value
        assert system_prompts_config['auto_create_history_folders'] is True  # 默认值 / Default value
        assert system_prompts_config['prompt_file_extension'] == '.md'  # 默认值 / Default value