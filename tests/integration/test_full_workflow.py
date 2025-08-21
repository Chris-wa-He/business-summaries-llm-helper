"""
完整工作流集成测试 / Full Workflow Integration Tests

测试完整的用户流程和组件集成
Test complete user workflow and component integration
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, Mock

from src.services.app_controller import AppController, CaseSummaryError


class TestFullWorkflow:
    """完整工作流测试类 / Full workflow test class"""
    
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

models:
  claude:
    - id: "anthropic.claude-3-sonnet-20240229-v1:0"
      name: "Claude 3 Sonnet"
  nova:
    - id: "amazon.nova-pro-v1:0"
      name: "Nova Pro"

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
# 支付系统故障

## 问题描述
支付接口响应超时，导致订单状态异常。

## 分析过程
- 检查支付网关状态
- 分析日志文件
- 确认数据库连接

## 解决措施
- 重启支付服务
- 修复数据不一致问题
- 加强监控机制
"""
        
        with open(category1_dir / "login_issue.md", 'w', encoding='utf-8') as f:
            f.write(case1_content)
        
        with open(category1_dir / "payment_issue.txt", 'w', encoding='utf-8') as f:
            f.write(case2_content)
    
    @patch('src.config.config_manager.ConfigManager.validate_aws_credentials')
    @patch('src.config.config_manager.ConfigManager.get_boto3_session')
    @patch('src.clients.bedrock_client.BedrockClient')
    def test_complete_workflow_with_mocked_aws(self, mock_bedrock_client, mock_get_session, mock_validate_credentials):
        """测试完整工作流（模拟AWS）/ Test complete workflow with mocked AWS"""
        # 设置mock / Setup mocks
        mock_validate_credentials.return_value = True
        mock_get_session.return_value = Mock()
        
        # 模拟Bedrock客户端 / Mock Bedrock client
        mock_client_instance = Mock()
        mock_bedrock_client.return_value = mock_client_instance
        
        # 模拟模型列表 / Mock model list
        mock_client_instance.list_foundation_models.return_value = [
            {
                'modelId': 'anthropic.claude-3-sonnet-20240229-v1:0',
                'modelName': 'Claude 3 Sonnet'
            }
        ]
        
        mock_client_instance.filter_models_by_provider.return_value = {
            'claude': [{'modelId': 'anthropic.claude-3-sonnet-20240229-v1:0', 'modelName': 'Claude 3 Sonnet'}],
            'nova': [],
            'deepseek': [],
            'openai': []
        }
        
        mock_client_instance.is_supported_model.return_value = True
        mock_client_instance.get_model_display_name.return_value = "Claude 3 Sonnet"
        mock_client_instance.format_messages.return_value = [
            {'role': 'user', 'content': [{'text': 'test prompt'}]}
        ]
        mock_client_instance.converse.return_value = "这是生成的案例总结内容。"
        
        # 初始化应用控制器 / Initialize app controller
        app_controller = AppController(str(self.config_path))
        
        # 验证初始化状态 / Verify initialization status
        is_initialized, status_message = app_controller.get_initialization_status()
        assert is_initialized is True
        
        # 初始化模型 / Initialize models
        models = app_controller.initialize_models()
        assert 'claude' in models
        
        # 测试案例总结生成 / Test case summary generation
        test_case = """
用户反映系统登录时出现异常，具体表现为：
1. 输入正确的用户名和密码
2. 点击登录按钮后页面无响应
3. 等待约30秒后显示"网络超时"错误

请分析问题并提供解决方案。
"""
        
        summary = app_controller.process_case_summary(
            case_input=test_case,
            model_id='anthropic.claude-3-sonnet-20240229-v1:0'
        )
        
        # 验证结果 / Verify results
        assert summary == "这是生成的案例总结内容。"
        
        # 验证历史信息被正确处理 / Verify history information is processed correctly
        mock_client_instance.converse.assert_called_once()
        call_args = mock_client_instance.converse.call_args
        
        # 验证调用参数 / Verify call parameters
        assert call_args[1]['model_id'] == 'anthropic.claude-3-sonnet-20240229-v1:0'
        assert call_args[1]['max_tokens'] == 1000
        assert call_args[1]['temperature'] == 0.5
    
    @patch('src.config.config_manager.ConfigManager.validate_aws_credentials')
    def test_configuration_loading_integration(self, mock_validate_credentials):
        """测试配置加载集成 / Test configuration loading integration"""
        mock_validate_credentials.return_value = True
        
        with patch('src.clients.bedrock_client.BedrockClient'):
            app_controller = AppController(str(self.config_path))
            
            # 验证配置被正确加载 / Verify configuration is loaded correctly
            app_config = app_controller.get_app_config()
            assert app_config['title'] == "Test Case Summary Generator"
            assert app_config['max_tokens'] == 1000
            assert app_config['temperature'] == 0.5
    
    @patch('src.config.config_manager.ConfigManager.validate_aws_credentials')
    def test_history_processing_integration(self, mock_validate_credentials):
        """测试历史信息处理集成 / Test history processing integration"""
        mock_validate_credentials.return_value = True
        
        with patch('src.clients.bedrock_client.BedrockClient'):
            app_controller = AppController(str(self.config_path))
            
            # 测试历史处理器 / Test history processor
            history_processor = app_controller.history_processor
            
            # 加载历史文件 / Load history files
            history_files = history_processor.load_history_files()
            assert len(history_files) == 2  # 应该有2个测试文件 / Should have 2 test files
            
            # 验证文件内容 / Verify file content
            file_names = {f['name'] for f in history_files}
            assert 'login_issue.md' in file_names
            assert 'payment_issue.txt' in file_names
            
            # 处理历史内容 / Process history content
            processed_content = history_processor.process_history_content(history_files)
            assert '登录问题案例' in processed_content
            assert '支付系统故障' in processed_content
    
    def test_error_handling_integration(self):
        """测试错误处理集成 / Test error handling integration"""
        # 测试无效配置文件 / Test invalid config file
        invalid_config_path = Path(self.temp_dir) / "invalid_config.yaml"
        
        with open(invalid_config_path, 'w') as f:
            f.write("invalid: yaml: content:")
        
        with pytest.raises(CaseSummaryError):
            AppController(str(invalid_config_path))
    
    def test_input_validation_integration(self):
        """测试输入验证集成 / Test input validation integration"""
        with patch('src.config.config_manager.ConfigManager.validate_aws_credentials') as mock_validate:
            mock_validate.return_value = True
            
            with patch('src.clients.bedrock_client.BedrockClient'):
                app_controller = AppController(str(self.config_path))
                
                # 测试空输入验证 / Test empty input validation
                with pytest.raises(CaseSummaryError, match="输入验证失败"):
                    app_controller.process_case_summary(
                        case_input="",
                        model_id="test-model"
                    )
                
                # 测试过短输入验证 / Test too short input validation
                with pytest.raises(CaseSummaryError, match="输入验证失败"):
                    app_controller.process_case_summary(
                        case_input="短",
                        model_id="test-model"
                    )
