"""
配置文件向后兼容性测试 / Configuration Backward Compatibility Tests

验证新的配置结构与旧版本的兼容性。
Verifies compatibility of new configuration structure with old versions.
"""

import tempfile
import yaml
from pathlib import Path
from src.config.config_manager import ConfigManager


class TestConfigCompatibility:
    """配置兼容性测试类 / Configuration Compatibility Test Class"""
    
    def test_old_config_format_compatibility(self):
        """测试旧配置格式兼容性 / Test old config format compatibility"""
        # 创建旧格式的配置文件 / Create old format config file
        old_config = {
            'aws': {
                'auth_method': 'profile',
                'profile_name': 'default',
                'region': 'us-east-1'
            },
            'models': {
                'claude': [
                    {'id': 'anthropic.claude-3-5-sonnet-20241022-v2:0', 'name': 'Claude 3.5 Sonnet'}
                ]
            },
            'system_prompt': '你是一个专业的案例总结助手。',  # 旧格式：单个系统提示词
            'history_folder': './history_references',
            'app': {
                'title': 'Case Summary Generator',
                'max_tokens': 4000,
                'temperature': 0.7
            }
        }
        
        # 写入临时配置文件 / Write to temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(old_config, f, default_flow_style=False, allow_unicode=True)
            config_path = f.name
        
        try:
            # 尝试加载旧格式配置 / Try to load old format config
            config_manager = ConfigManager(config_path)
            
            # 验证可以成功创建ConfigManager实例 / Verify ConfigManager can be created successfully
            assert config_manager is not None
            
            # 验证可以获取应用配置 / Verify can get app config
            app_config = config_manager.get_app_config()
            assert app_config is not None
            
            # 验证基本配置项存在 / Verify basic config items exist
            assert 'history_folder' in app_config
            assert app_config['history_folder'] == './history_references'
            
            print("✅ 旧配置格式兼容性测试通过")
            
        finally:
            # 清理临时文件 / Cleanup temporary file
            Path(config_path).unlink(missing_ok=True)
    
    def test_mixed_config_format(self):
        """测试混合配置格式 / Test mixed config format"""
        # 创建混合格式的配置文件（部分新，部分旧）/ Create mixed format config
        mixed_config = {
            'aws': {
                'auth_method': 'profile',
                'profile_name': 'default',
                'region': 'us-east-1'
            },
            'models': {
                'claude': [
                    {'id': 'anthropic.claude-3-5-sonnet-20241022-v2:0', 'name': 'Claude 3.5 Sonnet'}
                ]
            },
            # 新格式：系统提示词管理 / New format: system prompt management
            'system_prompts': {
                'prompts_folder': './system_prompts',
                'active_prompt': 'default'
            },
            # 同时保留旧格式 / Also keep old format
            'system_prompt': '你是一个专业的案例总结助手。',
            'history_folder': './history_references',
            'app': {
                'title': 'Case Summary Generator',
                'max_tokens': 4000,
                'temperature': 0.7
            }
        }
        
        # 写入临时配置文件 / Write to temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(mixed_config, f, default_flow_style=False, allow_unicode=True)
            config_path = f.name
        
        try:
            # 尝试加载混合格式配置 / Try to load mixed format config
            config_manager = ConfigManager(config_path)
            app_config = config_manager.get_app_config()
            
            # 验证新格式配置存在 / Verify new format config exists
            assert 'system_prompts' in app_config
            assert app_config['system_prompts']['prompts_folder'] == './system_prompts'
            
            # 验证基本配置项 / Verify basic config items
            assert 'history_folder' in app_config
            assert app_config['history_folder'] == './history_references'
            
            print("✅ 混合配置格式兼容性测试通过")
            
        finally:
            # 清理临时文件 / Cleanup temporary file
            Path(config_path).unlink(missing_ok=True)
    
    def test_new_config_format(self):
        """测试新配置格式 / Test new config format"""
        # 创建完整的新格式配置文件 / Create complete new format config
        new_config = {
            'aws': {
                'auth_method': 'profile',
                'profile_name': 'default',
                'region': 'us-east-1'
            },
            'models': {
                'claude': [
                    {'id': 'anthropic.claude-3-5-sonnet-20241022-v2:0', 'name': 'Claude 3.5 Sonnet'}
                ]
            },
            'system_prompts': {
                'prompts_folder': './system_prompts',
                'active_prompt': 'default',
                'auto_create_history_folders': True,
                'prompt_file_extension': '.md'
            },
            'history_folder': './history_references',
            'app': {
                'title': 'Case Summary Generator',
                'max_tokens': 4000,
                'temperature': 0.7
            }
        }
        
        # 写入临时配置文件 / Write to temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(new_config, f, default_flow_style=False, allow_unicode=True)
            config_path = f.name
        
        try:
            # 尝试加载新格式配置 / Try to load new format config
            config_manager = ConfigManager(config_path)
            app_config = config_manager.get_app_config()
            
            # 验证新配置结构 / Verify new config structure
            assert 'system_prompts' in app_config
            system_prompts_config = app_config['system_prompts']
            
            assert 'prompts_folder' in system_prompts_config
            assert 'active_prompt' in system_prompts_config
            assert 'auto_create_history_folders' in system_prompts_config
            assert 'prompt_file_extension' in system_prompts_config
            
            # 验证配置值 / Verify config values
            assert system_prompts_config['prompts_folder'] == './system_prompts'
            assert system_prompts_config['active_prompt'] == 'default'
            assert system_prompts_config['auto_create_history_folders'] is True
            assert system_prompts_config['prompt_file_extension'] == '.md'
            
            print("✅ 新配置格式测试通过")
            
        finally:
            # 清理临时文件 / Cleanup temporary file
            Path(config_path).unlink(missing_ok=True)
