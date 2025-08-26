"""
端到端测试基础类 / End-to-End Test Base Class

提供端到端测试的基础设施和通用功能。
Provides infrastructure and common functionality for end-to-end tests.
"""

import tempfile
import shutil
import yaml
from pathlib import Path
from unittest.mock import Mock, patch
from src.config.config_manager import ConfigManager
from src.processors.history_processor import HistoryProcessor
from src.services.system_prompt_manager import SystemPromptManager


class E2ETestBase:
    """端到端测试基础类 / End-to-End Test Base Class"""
    
    def setup_method(self):
        """设置测试环境 / Setup test environment"""
        # 创建临时目录 / Create temporary directories
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_file = self.temp_dir / "config.yaml"
        self.prompts_dir = self.temp_dir / "system_prompts"
        self.history_dir = self.temp_dir / "history_references"
        
        # 创建目录结构 / Create directory structure
        self.prompts_dir.mkdir(parents=True)
        self.history_dir.mkdir(parents=True)
        
        # 创建测试配置文件 / Create test configuration file
        self.create_test_config()
        
        # 创建测试历史文件 / Create test history files
        self.create_test_history_files()
    
    def teardown_method(self):
        """清理测试环境 / Cleanup test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_config(self):
        """创建测试配置文件 / Create test configuration file"""
        config_data = {
            'aws': {
                'auth_method': 'profile',
                'profile_name': 'test-profile',
                'region': 'us-east-1'
            },
            'system_prompts': {
                'prompts_folder': str(self.prompts_dir),
                'active_prompt': 'default'
            },
            'history_folder': str(self.history_dir),
            'app': {
                'title': 'Test Case Summary Generator',
                'max_tokens': 4000,
                'temperature': 0.7
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
    
    def create_test_history_files(self):
        """创建测试历史文件 / Create test history files"""
        # 创建默认历史文件夹 / Create default history folder
        default_history = self.history_dir / "default"
        default_history.mkdir(exist_ok=True)
        
        # 创建示例历史文件 / Create sample history files
        (default_history / "case1.txt").write_text(
            "案例1：系统性能优化\n"
            "问题：系统响应缓慢\n"
            "解决方案：优化数据库查询，增加缓存机制\n"
            "结果：响应时间提升50%",
            encoding='utf-8'
        )
        
        (default_history / "case2.md").write_text(
            "# 案例2：安全漏洞修复\n\n"
            "## 问题描述\n"
            "发现SQL注入漏洞\n\n"
            "## 解决方案\n"
            "使用参数化查询，输入验证\n\n"
            "## 结果\n"
            "成功修复安全漏洞，通过安全审计",
            encoding='utf-8'
        )
    
    def create_mock_config_manager(self):
        """创建模拟配置管理器 / Create mock configuration manager"""
        mock_config = Mock(spec=ConfigManager)
        mock_config.get_app_config.return_value = {
            'system_prompts': {
                'prompts_folder': str(self.prompts_dir),
                'active_prompt': 'default'
            },
            'history_folder': str(self.history_dir)
        }
        return mock_config
    
    def create_mock_history_processor(self):
        """创建模拟历史处理器 / Create mock history processor"""
        mock_history = Mock(spec=HistoryProcessor)
        mock_history.set_history_folder = Mock()
        return mock_history
    
    def create_system_prompt_manager(self):
        """创建系统提示词管理器 / Create system prompt manager"""
        mock_config = self.create_mock_config_manager()
        mock_history = self.create_mock_history_processor()
        return SystemPromptManager(mock_config, mock_history)
