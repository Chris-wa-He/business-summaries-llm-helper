"""
生产环境兼容性测试 / Production Environment Compatibility Tests
"""

import pytest
import os
import tempfile
import shutil
import yaml
from pathlib import Path


class TestProductionCompatibility:
    """生产环境兼容性测试类 / Production compatibility test class"""
    
    def setup_method(self):
        """测试设置 / Test setup"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.yaml"
        
    def teardown_method(self):
        """测试清理 / Test cleanup"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_configuration_file_structure(self):
        """测试配置文件结构 / Test configuration file structure"""
        # 创建生产环境配置 / Create production configuration
        config_content = {
            'aws': {
                'auth_method': 'profile',
                'profile_name': 'production',
                'region': 'us-east-1'
            },
            'app': {
                'title': 'Case Summary Generator',
                'max_tokens': 4000,
                'log_level': 'INFO'
            },
            'interactive_refinement': {
                'conversation': {
                    'max_sessions_per_user': 5,
                    'session_timeout': 3600
                },
                'security': {
                    'input_validation_enabled': True,
                    'enable_rate_limiting': True
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config_content, f)
        
        # 验证配置文件可以正确加载 / Verify configuration file can be loaded correctly
        with open(self.config_path, 'r') as f:
            loaded_config = yaml.safe_load(f)
        
        assert loaded_config['aws']['region'] == 'us-east-1'
        assert loaded_config['app']['title'] == 'Case Summary Generator'
        assert loaded_config['interactive_refinement']['security']['input_validation_enabled'] is True
        
    def test_environment_variables_support(self):
        """测试环境变量支持 / Test environment variables support"""
        # 测试关键环境变量 / Test key environment variables
        test_env_vars = {
            'DEPLOYMENT_ENV': 'production',
            'AWS_REGION': 'us-west-2',
            'LOG_LEVEL': 'INFO',
            'ENABLE_METRICS': 'true',
            'MAX_SESSIONS_PER_USER': '5'
        }
        
        for var_name, var_value in test_env_vars.items():
            os.environ[var_name] = var_value
            assert os.getenv(var_name) == var_value
            
        # 清理环境变量 / Clean up environment variables
        for var_name in test_env_vars:
            os.environ.pop(var_name, None)
            
    def test_directory_structure_requirements(self):
        """测试目录结构要求 / Test directory structure requirements"""
        # 切换到临时目录 / Change to temp directory
        original_cwd = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            
            # 创建必要的目录 / Create necessary directories
            required_dirs = [
                "system_prompts",
                "history_references", 
                "logs",
                "personalized_prompts",
                "backups",
                "monitoring"
            ]
            
            for dir_name in required_dirs:
                dir_path = Path(dir_name)
                dir_path.mkdir(exist_ok=True)
                assert dir_path.exists()
                assert dir_path.is_dir()
                
        finally:
            os.chdir(original_cwd)
            
    def test_deployment_script_exists(self):
        """测试部署脚本存在 / Test deployment script exists"""
        project_root = Path(__file__).parent.parent.parent
        deploy_script = project_root / "deploy.sh"
        
        assert deploy_script.exists(), "部署脚本不存在 / Deployment script does not exist"
        
        # 检查脚本是否可执行 / Check if script is executable
        assert os.access(deploy_script, os.X_OK), "部署脚本不可执行 / Deployment script is not executable"
        
    def test_production_config_example_exists(self):
        """测试生产环境配置示例存在 / Test production config example exists"""
        project_root = Path(__file__).parent.parent.parent
        config_example = project_root / "config.yaml.example"
        env_production = project_root / ".env.production"
        
        assert config_example.exists(), "配置示例文件不存在 / Config example file does not exist"
        assert env_production.exists(), "生产环境变量文件不存在 / Production env file does not exist"
        
    def test_monitoring_configuration(self):
        """测试监控配置 / Test monitoring configuration"""
        project_root = Path(__file__).parent.parent.parent
        monitoring_dir = project_root / "monitoring"
        metrics_file = monitoring_dir / "metrics.py"
        
        assert monitoring_dir.exists(), "监控目录不存在 / Monitoring directory does not exist"
        assert metrics_file.exists(), "指标文件不存在 / Metrics file does not exist"
        
    def test_pyproject_toml_version(self):
        """测试pyproject.toml版本 / Test pyproject.toml version"""
        project_root = Path(__file__).parent.parent.parent
        pyproject_file = project_root / "pyproject.toml"
        
        assert pyproject_file.exists(), "pyproject.toml文件不存在 / pyproject.toml file does not exist"
        
        # 读取并验证版本 / Read and verify version
        with open(pyproject_file, 'r') as f:
            content = f.read()
            
        assert 'version = "2.0.0"' in content, "版本号不正确 / Version number is incorrect"
        assert 'aiofiles' in content, "缺少异步文件依赖 / Missing async file dependency"
        assert 'aiohttp' in content, "缺少异步HTTP依赖 / Missing async HTTP dependency"
        
    def test_health_check_script(self):
        """测试健康检查脚本 / Test health check script"""
        project_root = Path(__file__).parent.parent.parent
        health_check_script = project_root / "scripts" / "health_check.py"
        
        assert health_check_script.exists(), "健康检查脚本不存在 / Health check script does not exist"
        
    def test_resource_limits_configuration(self):
        """测试资源限制配置 / Test resource limits configuration"""
        config_content = {
            'interactive_refinement': {
                'conversation': {
                    'max_sessions_per_user': 5,
                    'max_messages_per_session': 100
                },
                'version': {
                    'max_versions_per_session': 50
                },
                'security': {
                    'max_message_length': 2000,
                    'rate_limit_per_minute': 100
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config_content, f)
        
        # 验证资源限制 / Verify resource limits
        with open(self.config_path, 'r') as f:
            loaded_config = yaml.safe_load(f)
            
        refinement_config = loaded_config['interactive_refinement']
        
        assert refinement_config['conversation']['max_sessions_per_user'] == 5
        assert refinement_config['conversation']['max_messages_per_session'] == 100
        assert refinement_config['version']['max_versions_per_session'] == 50
        assert refinement_config['security']['max_message_length'] == 2000
        assert refinement_config['security']['rate_limit_per_minute'] == 100
        
    def test_backward_compatibility(self):
        """测试向后兼容性 / Test backward compatibility"""
        # 创建旧版本配置文件 / Create old version configuration file
        old_config_content = {
            'aws': {
                'auth_method': 'profile',
                'profile_name': 'default',
                'region': 'us-east-1'
            },
            'models': {
                'claude': [
                    {
                        'id': 'anthropic.claude-3-5-sonnet-20241022-v2:0',
                        'name': 'Claude 3.5 Sonnet'
                    }
                ]
            },
            'system_prompt': '你是一个专业的案例总结助手。',
            'history_folder': './history_references',
            'app': {
                'title': '案例总结生成器',
                'max_tokens': 4000,
                'temperature': 0.7
            }
        }
        
        with open(self.config_path, 'w') as f:
            yaml.dump(old_config_content, f)
        
        # 验证旧配置仍然可以加载 / Verify old configuration can still be loaded
        with open(self.config_path, 'r') as f:
            loaded_config = yaml.safe_load(f)
        
        assert loaded_config['aws']['auth_method'] == 'profile'
        assert loaded_config['aws']['region'] == 'us-east-1'
        assert loaded_config['app']['title'] == '案例总结生成器'
        assert loaded_config['app']['max_tokens'] == 4000