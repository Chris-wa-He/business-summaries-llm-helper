"""
组件集成测试 / Component Integration Tests

测试各组件之间的集成，不依赖外部AWS服务
Test integration between components without external AWS dependencies
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, Mock

from src.config.config_manager import ConfigManager
from src.processors.history_processor import HistoryProcessor
from src.services.prompt_builder import PromptBuilder


class TestComponentIntegration:
    """组件集成测试类 / Component integration test class"""
    
    def setup_method(self):
        """测试方法设置 / Test method setup"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.yaml"
        self.history_dir = Path(self.temp_dir) / "history"
        self.history_dir.mkdir(exist_ok=True)
        
        # 创建测试配置文件 / Create test config file
        self.create_test_config()
        
        # 创建测试历史文件 / Create test history files
        self.create_test_history_files()
    
    def create_test_config(self):
        """创建测试配置文件 / Create test configuration file"""
        config_content = f"""
aws:
  auth_method: "profile"
  profile_name: "default"
  region: "us-east-1"

system_prompt: |
  你是专业的案例总结助手。请生成结构化的案例总结。

history_folder: "{self.history_dir}"

app:
  title: "Test Case Summary Generator"
  max_tokens: 1000
  temperature: 0.5
"""
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
    
    def create_test_history_files(self):
        """创建测试历史文件 / Create test history files"""
        # 创建类别目录 / Create category directories
        category1_dir = self.history_dir / "technical_issues"
        category1_dir.mkdir(exist_ok=True)
        
        # 技术问题案例 / Technical issue cases
        case1_content = """
# 登录问题案例

## 问题描述
用户无法登录系统，提示认证失败。

## 解决方案
1. 检查用户名和密码
2. 重置用户凭证
3. 验证系统状态

## 结果
问题已解决，用户可以正常登录。
"""
        
        case2_content = """
# 网络超时问题

## 问题描述
系统响应缓慢，经常出现超时错误。

## 分析过程
- 检查网络连接
- 分析服务器负载
- 查看数据库性能

## 解决措施
- 优化数据库查询
- 增加服务器资源
- 实施缓存策略
"""
        
        with open(category1_dir / "login_issue.md", 'w', encoding='utf-8') as f:
            f.write(case1_content)
        
        with open(category1_dir / "timeout_issue.txt", 'w', encoding='utf-8') as f:
            f.write(case2_content)
    
    def test_config_and_history_integration(self):
        """测试配置管理器和历史处理器集成 / Test config manager and history processor integration"""
        # 初始化配置管理器 / Initialize config manager
        config_manager = ConfigManager(str(self.config_path))
        
        # 验证配置加载 / Verify configuration loading
        system_prompt = config_manager.get_system_prompt().strip()
        assert "你是专业的案例总结助手" in system_prompt
        assert config_manager.get_history_folder() == str(self.history_dir)
        
        # 初始化历史处理器 / Initialize history processor
        history_processor = HistoryProcessor(config_manager.get_history_folder())
        
        # 加载历史文件 / Load history files
        history_files = history_processor.load_history_files()
        assert len(history_files) == 2  # 应该有2个测试文件 / Should have 2 test files
        
        # 验证文件内容 / Verify file content
        file_names = {f['name'] for f in history_files}
        assert 'login_issue.md' in file_names
        assert 'timeout_issue.txt' in file_names
        
        # 处理历史内容 / Process history content
        processed_content = history_processor.process_history_content(history_files)
        assert '登录问题案例' in processed_content
        assert '网络超时问题' in processed_content
    
    def test_history_and_prompt_integration(self):
        """测试历史处理器和Prompt构建器集成 / Test history processor and prompt builder integration"""
        # 初始化组件 / Initialize components
        config_manager = ConfigManager(str(self.config_path))
        history_processor = HistoryProcessor(config_manager.get_history_folder())
        prompt_builder = PromptBuilder()
        
        # 加载和处理历史信息 / Load and process history information
        history_files = history_processor.load_history_files()
        history_reference = history_processor.process_history_content(history_files)
        
        # 构建prompt / Build prompt
        case_input = """
用户反映系统登录时出现异常，具体表现为：
1. 输入正确的用户名和密码
2. 点击登录按钮后页面无响应
3. 等待约30秒后显示"网络超时"错误

请分析问题并提供解决方案。
"""
        
        system_prompt = config_manager.get_system_prompt()
        
        user_prompt = prompt_builder.build_prompt(
            case_input=case_input,
            history_reference=history_reference,
            system_prompt=system_prompt
        )
        
        # 验证prompt内容 / Verify prompt content
        assert '历史参考信息' in user_prompt
        assert '登录问题案例' in user_prompt
        assert '网络超时问题' in user_prompt
        assert case_input.strip() in user_prompt
        assert 'Generate a structured and professional case summary' in user_prompt
    
    def test_configuration_validation_integration(self):
        """测试配置验证集成 / Test configuration validation integration"""
        # 测试有效配置 / Test valid configuration
        config_manager = ConfigManager(str(self.config_path))
        app_config = config_manager.get_app_config()
        assert "Test Case Summary Generator" in app_config['title']
        assert app_config['max_tokens'] == 1000
        assert app_config['temperature'] == 0.5
        
        # 测试无效配置文件 / Test invalid configuration file
        invalid_config_path = Path(self.temp_dir) / "invalid_config.yaml"
        with open(invalid_config_path, 'w') as f:
            f.write("invalid: yaml: content:")
        
        with pytest.raises(Exception):  # 应该抛出配置错误 / Should raise configuration error
            ConfigManager(str(invalid_config_path))
    
    def test_history_filtering_integration(self):
        """测试历史信息筛选集成 / Test history filtering integration"""
        # 初始化组件 / Initialize components
        config_manager = ConfigManager(str(self.config_path))
        history_processor = HistoryProcessor(config_manager.get_history_folder())
        
        # 加载历史文件 / Load history files
        history_files = history_processor.load_history_files()
        
        # 测试相关性筛选 / Test relevance filtering
        case_input_login = "用户登录问题"
        filtered_content_login = history_processor.filter_relevant_history(
            case_input_login, 
            history_processor.process_history_content(history_files)
        )
        
        # 验证筛选结果 / Verify filtering results
        assert '登录问题案例' in filtered_content_login
        
        case_input_timeout = "系统响应超时"
        filtered_content_timeout = history_processor.filter_relevant_history(
            case_input_timeout,
            history_processor.process_history_content(history_files)
        )
        
        # 验证筛选结果 / Verify filtering results
        assert '网络超时问题' in filtered_content_timeout
    
    def test_end_to_end_component_flow(self):
        """测试端到端组件流程 / Test end-to-end component flow"""
        # 初始化所有组件 / Initialize all components
        config_manager = ConfigManager(str(self.config_path))
        history_processor = HistoryProcessor(config_manager.get_history_folder())
        prompt_builder = PromptBuilder()
        
        # 模拟完整流程 / Simulate complete workflow
        case_input = """
用户反映系统登录时出现异常，具体表现为：
1. 输入正确的用户名和密码
2. 点击登录按钮后页面无响应
3. 等待约30秒后显示"网络超时"错误

请分析问题并提供解决方案。
"""
        
        # 步骤1: 加载历史参考信息 / Step 1: Load history reference information
        history_files = history_processor.load_history_files()
        history_reference = history_processor.process_history_content(history_files)
        
        # 步骤2: 筛选相关历史信息 / Step 2: Filter relevant history information
        filtered_history = history_processor.filter_relevant_history(case_input, history_reference)
        
        # 步骤3: 获取系统提示词 / Step 3: Get system prompt
        system_prompt = config_manager.get_system_prompt()
        
        # 步骤4: 构建最终prompt / Step 4: Build final prompt
        final_prompt = prompt_builder.build_prompt(
            case_input=case_input,
            history_reference=filtered_history,
            system_prompt=system_prompt
        )
        
        # 验证最终结果 / Verify final result
        assert len(final_prompt) > 0
        assert '历史参考信息' in final_prompt
        assert case_input.strip() in final_prompt
        assert '登录问题案例' in final_prompt or '网络超时问题' in final_prompt
        
        # 验证应用配置可以正确获取 / Verify app configuration can be retrieved correctly
        app_config = config_manager.get_app_config()
        assert app_config['max_tokens'] == 1000
        assert app_config['temperature'] == 0.5
