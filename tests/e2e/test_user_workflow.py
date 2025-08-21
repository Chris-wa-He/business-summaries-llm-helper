"""
端到端用户工作流测试 / End-to-End User Workflow Tests

测试完整的用户使用场景
Test complete user usage scenarios
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock

from src.services.app_controller import AppController
from src.ui.gradio_interface import GradioInterface


class TestUserWorkflow:
    """用户工作流测试类 / User workflow test class"""
    
    def setup_method(self):
        """测试方法设置 / Test method setup"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "e2e_config.yaml"
        self.history_dir = Path(self.temp_dir) / "history"
        self.history_dir.mkdir(exist_ok=True)
        
        self.create_e2e_config()
        self.create_sample_history()
    
    def create_e2e_config(self):
        """创建端到端测试配置 / Create E2E test configuration"""
        config_content = f"""
aws:
  auth_method: "profile"
  profile_name: "default"
  region: "us-east-1"

models:
  claude:
    - id: "anthropic.claude-3-5-sonnet-20241022-v2:0"
      name: "Claude 3.5 Sonnet"
    - id: "anthropic.claude-3-haiku-20240307-v1:0"
      name: "Claude 3 Haiku"
  nova:
    - id: "amazon.nova-pro-v1:0"
      name: "Nova Pro"

system_prompt: |
  你是一个专业的案例总结助手。请根据提供的历史参考信息和新的案例输入，生成一个结构化、专业的案例总结。
  
  总结应该包含：
  1. 案例概述
  2. 关键要点
  3. 分析结论
  4. 建议措施

history_folder: "{self.history_dir}"

app:
  title: "E2E Test Case Summary Generator"
  max_tokens: 2000
  temperature: 0.7
"""
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
    
    def create_sample_history(self):
        """创建示例历史文件 / Create sample history files"""
        # 创建业务问题类别 / Create business issues category
        business_dir = self.history_dir / "business_issues"
        business_dir.mkdir(exist_ok=True)
        
        # 客户服务问题 / Customer service issues
        customer_case = """
# 客户投诉处理案例

## 问题背景
客户对产品质量不满意，要求退款。

## 处理过程
1. 耐心倾听客户诉求
2. 详细了解问题细节
3. 提供解决方案选项
4. 跟进处理结果

## 处理结果
客户满意度提升，问题得到妥善解决。

## 经验总结
- 及时响应客户需求
- 保持专业和耐心的态度
- 提供多种解决方案
- 建立长期客户关系
"""
        
        # 技术支持案例 / Technical support case
        tech_case = """
# 系统故障排查案例

## 故障现象
用户报告系统响应缓慢，部分功能无法使用。

## 排查步骤
1. 检查系统资源使用情况
2. 分析应用日志文件
3. 监控数据库性能
4. 检查网络连接状态

## 根本原因
数据库查询效率低下，导致系统整体性能下降。

## 解决方案
- 优化数据库索引
- 调整查询语句
- 增加缓存机制
- 监控系统性能指标

## 预防措施
建立定期性能检查机制，及时发现潜在问题。
"""
        
        with open(business_dir / "customer_complaint.md", 'w', encoding='utf-8') as f:
            f.write(customer_case)
        
        with open(business_dir / "system_troubleshooting.txt", 'w', encoding='utf-8') as f:
            f.write(tech_case)
    
    @patch('src.config.config_manager.ConfigManager.validate_aws_credentials')
    @patch('src.clients.bedrock_client.BedrockClient')
    def test_complete_user_journey(self, mock_bedrock_client, mock_validate_credentials):
        """测试完整用户使用流程 / Test complete user journey"""
        # 设置mock / Setup mocks
        mock_validate_credentials.return_value = True
        
        mock_client_instance = Mock()
        mock_bedrock_client.return_value = mock_client_instance
        
        # 模拟模型API响应 / Mock model API responses
        mock_client_instance.list_foundation_models.return_value = [
            {
                'modelId': 'anthropic.claude-3-5-sonnet-20241022-v2:0',
                'modelName': 'Claude 3.5 Sonnet'
            },
            {
                'modelId': 'amazon.nova-pro-v1:0',
                'modelName': 'Nova Pro'
            }
        ]
        
        mock_client_instance.filter_models_by_provider.return_value = {
            'claude': [{'modelId': 'anthropic.claude-3-5-sonnet-20241022-v2:0', 'modelName': 'Claude 3.5 Sonnet'}],
            'nova': [{'modelId': 'amazon.nova-pro-v1:0', 'modelName': 'Nova Pro'}],
            'deepseek': [],
            'openai': []
        }
        
        mock_client_instance.is_supported_model.return_value = True
        mock_client_instance.get_model_display_name.side_effect = lambda x: {
            'anthropic.claude-3-5-sonnet-20241022-v2:0': 'Claude 3.5 Sonnet',
            'amazon.nova-pro-v1:0': 'Nova Pro'
        }.get(x, x)
        
        mock_client_instance.format_messages.return_value = [
            {'role': 'user', 'content': [{'text': 'formatted prompt'}]}
        ]
        
        # 模拟AI响应 / Mock AI response
        mock_ai_response = """
# 案例总结

## 案例概述
用户反映在线购物平台出现支付异常问题，需要紧急处理。

## 关键要点
1. 支付流程中断，用户体验受影响
2. 可能涉及第三方支付接口问题
3. 需要快速定位和解决问题

## 分析结论
根据历史类似案例，问题可能出现在支付网关配置或网络连接上。

## 建议措施
1. 立即检查支付接口状态
2. 联系第三方支付服务商
3. 准备备用支付方案
4. 及时通知用户处理进展
"""
        mock_client_instance.converse.return_value = mock_ai_response.strip()
        
        # 步骤1: 初始化应用 / Step 1: Initialize application
        app_controller = AppController(str(self.config_path))
        
        # 验证应用初始化成功 / Verify application initialization success
        is_initialized, status = app_controller.get_initialization_status()
        assert is_initialized is True
        
        # 步骤2: 初始化模型列表 / Step 2: Initialize model list
        models = app_controller.initialize_models()
        assert len(models['claude']) > 0
        assert len(models['nova']) > 0
        
        # 步骤3: 获取默认模型 / Step 3: Get default model
        default_model = app_controller.get_default_model()
        assert default_model == 'anthropic.claude-3-5-sonnet-20241022-v2:0'
        
        # 步骤4: 用户输入案例 / Step 4: User inputs case
        user_case = """
我们的在线购物平台今天出现了支付问题：

1. 多个用户反映无法完成支付
2. 支付页面显示"处理中"但长时间无响应
3. 部分用户的订单状态显示异常
4. 客服电话被打爆，用户情绪激动

这个问题从上午10点开始出现，到现在已经持续了2个小时。
我们需要快速分析问题原因并提供解决方案。
"""
        
        # 步骤5: 生成案例总结 / Step 5: Generate case summary
        summary = app_controller.process_case_summary(
            case_input=user_case,
            model_id=default_model
        )
        
        # 验证总结结果 / Verify summary result
        assert "案例概述" in summary
        assert "关键要点" in summary
        assert "分析结论" in summary
        assert "建议措施" in summary
        
        # 验证历史信息被使用 / Verify history information is used
        converse_call = mock_client_instance.converse.call_args
        user_prompt = converse_call[1]['messages'][0]['content'][0]['text']
        
        # 应该包含历史参考信息 / Should include historical reference information
        assert "历史参考信息" in user_prompt or "Historical Reference" in user_prompt
        
        # 步骤6: 测试UI组件集成 / Step 6: Test UI component integration
        with patch('src.ui.gradio_interface.gr') as mock_gr:
            gradio_interface = GradioInterface(app_controller)
            
            # 测试生成总结功能 / Test summary generation function
            result_summary, result_status = gradio_interface._generate_summary(
                case_input=user_case,
                model_id=default_model,
                system_prompt=""
            )
            
            assert result_summary == mock_ai_response.strip()
            assert "成功" in result_status or "successfully" in result_status
    
    @patch('src.config.config_manager.ConfigManager.validate_aws_credentials')
    @patch('src.clients.bedrock_client.BedrockClient')
    def test_model_switching_workflow(self, mock_bedrock_client, mock_validate_credentials):
        """测试模型切换工作流 / Test model switching workflow"""
        # 设置mock / Setup mocks
        mock_validate_credentials.return_value = True
        
        mock_client_instance = Mock()
        mock_bedrock_client.return_value = mock_client_instance
        
        # 模拟多个模型 / Mock multiple models
        mock_client_instance.list_foundation_models.return_value = [
            {'modelId': 'anthropic.claude-3-5-sonnet-20241022-v2:0', 'modelName': 'Claude 3.5 Sonnet'},
            {'modelId': 'amazon.nova-pro-v1:0', 'modelName': 'Nova Pro'}
        ]
        
        mock_client_instance.filter_models_by_provider.return_value = {
            'claude': [{'modelId': 'anthropic.claude-3-5-sonnet-20241022-v2:0', 'modelName': 'Claude 3.5 Sonnet'}],
            'nova': [{'modelId': 'amazon.nova-pro-v1:0', 'modelName': 'Nova Pro'}],
            'deepseek': [],
            'openai': []
        }
        
        mock_client_instance.is_supported_model.return_value = True
        mock_client_instance.get_model_display_name.side_effect = lambda x: x.split('.')[-1]
        mock_client_instance.format_messages.return_value = [{'role': 'user', 'content': [{'text': 'test'}]}]
        
        # 模拟不同模型的响应 / Mock different model responses
        def mock_converse(**kwargs):
            model_id = kwargs.get('model_id', '')
            if 'claude' in model_id:
                return "Claude模型生成的总结内容"
            elif 'nova' in model_id:
                return "Nova模型生成的总结内容"
            else:
                return "默认模型响应"
        
        mock_client_instance.converse.side_effect = mock_converse
        
        # 初始化应用 / Initialize application
        app_controller = AppController(str(self.config_path))
        app_controller.initialize_models()
        
        test_case = "这是一个测试案例，需要生成总结。"
        
        # 测试Claude模型 / Test Claude model
        claude_summary = app_controller.process_case_summary(
            case_input=test_case,
            model_id='anthropic.claude-3-5-sonnet-20241022-v2:0'
        )
        assert claude_summary == "Claude模型生成的总结内容"
        
        # 测试Nova模型 / Test Nova model
        nova_summary = app_controller.process_case_summary(
            case_input=test_case,
            model_id='amazon.nova-pro-v1:0'
        )
        assert nova_summary == "Nova模型生成的总结内容"
    
    @patch('src.config.config_manager.ConfigManager.validate_aws_credentials')
    def test_configuration_customization_workflow(self, mock_validate_credentials):
        """测试配置自定义工作流 / Test configuration customization workflow"""
        mock_validate_credentials.return_value = True
        
        with patch('src.clients.bedrock_client.BedrockClient'):
            # 测试自定义系统提示词 / Test custom system prompt
            app_controller = AppController(str(self.config_path))
            
            # 获取默认系统提示词 / Get default system prompt
            default_prompt = app_controller.config_manager.get_system_prompt()
            assert "专业的案例总结助手" in default_prompt
            
            # 获取应用配置 / Get app configuration
            app_config = app_controller.get_app_config()
            assert app_config['max_tokens'] == 2000
            assert app_config['temperature'] == 0.7
            assert app_config['title'] == "E2E Test Case Summary Generator"
