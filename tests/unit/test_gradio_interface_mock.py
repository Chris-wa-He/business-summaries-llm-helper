"""
Gradio界面模拟测试 / Gradio Interface Mock Tests

使用模拟对象测试Gradio界面的核心逻辑
Test core logic of Gradio interface using mock objects
"""

import pytest
from unittest.mock import Mock, patch

# 模拟gradio模块 / Mock gradio module
mock_gradio = Mock()
with patch.dict('sys.modules', {'gradio': mock_gradio}):
    from src.ui.gradio_interface import GradioInterface
    from src.services.app_controller import CaseSummaryError


class TestGradioInterfaceMock:
    """GradioInterface模拟测试类 / GradioInterface mock test class"""
    
    def setup_method(self):
        """测试方法设置 / Test method setup"""
        self.mock_app_controller = Mock()
        self.mock_app_controller.get_app_config.return_value = {
            'title': 'Test Case Summary Generator',
            'max_tokens': 4000,
            'temperature': 0.7
        }
        
    def test_init(self):
        """测试初始化 / Test initialization"""
        interface = GradioInterface(self.mock_app_controller)
        
        assert interface.app_controller == self.mock_app_controller
        assert interface.app_config['title'] == 'Test Case Summary Generator'
        assert interface.interface is None
    
    def test_generate_summary_success(self):
        """测试成功生成总结 / Test successful summary generation"""
        # 设置mock返回值 / Setup mock return values
        self.mock_app_controller.process_case_summary.return_value = "Generated summary content"
        
        interface = GradioInterface(self.mock_app_controller)
        
        result_summary, result_status = interface._generate_summary(
            case_input="Test case input",
            model_id="test-model-id",
            system_prompt="Test system prompt"
        )
        
        assert result_summary == "Generated summary content"
        assert "成功" in result_status or "successfully" in result_status
        
        # 验证调用参数 / Verify call parameters
        self.mock_app_controller.process_case_summary.assert_called_once_with(
            case_input="Test case input",
            model_id="test-model-id",
            custom_system_prompt="Test system prompt"
        )
    
    def test_generate_summary_empty_input(self):
        """测试空输入生成总结 / Test summary generation with empty input"""
        interface = GradioInterface(self.mock_app_controller)
        
        result_summary, result_status = interface._generate_summary(
            case_input="",
            model_id="test-model-id",
            system_prompt=""
        )
        
        assert result_summary == ""
        assert "错误" in result_status or "Error" in result_status
        assert "不能为空" in result_status or "cannot be empty" in result_status
        
        # 不应该调用处理方法 / Should not call processing method
        self.mock_app_controller.process_case_summary.assert_not_called()
    
    def test_generate_summary_no_model(self):
        """测试未选择模型生成总结 / Test summary generation without model selection"""
        interface = GradioInterface(self.mock_app_controller)
        
        result_summary, result_status = interface._generate_summary(
            case_input="Test case input",
            model_id="",
            system_prompt=""
        )
        
        assert result_summary == ""
        assert "错误" in result_status or "Error" in result_status
        assert "选择" in result_status or "select" in result_status
        
        # 不应该调用处理方法 / Should not call processing method
        self.mock_app_controller.process_case_summary.assert_not_called()
    
    def test_generate_summary_case_summary_error(self):
        """测试案例总结错误 / Test case summary error"""
        # 设置mock抛出异常 / Setup mock to throw exception
        self.mock_app_controller.process_case_summary.side_effect = CaseSummaryError("Test error")
        
        interface = GradioInterface(self.mock_app_controller)
        
        result_summary, result_status = interface._generate_summary(
            case_input="Test case input",
            model_id="test-model-id",
            system_prompt=""
        )
        
        assert result_summary == ""
        assert "失败" in result_status or "failed" in result_status
        assert "Test error" in result_status
    
    def test_generate_summary_with_empty_system_prompt(self):
        """测试空系统提示词生成总结 / Test summary generation with empty system prompt"""
        # 设置mock返回值 / Setup mock return values
        self.mock_app_controller.process_case_summary.return_value = "Generated summary"
        
        interface = GradioInterface(self.mock_app_controller)
        
        result_summary, result_status = interface._generate_summary(
            case_input="Test case input",
            model_id="test-model-id",
            system_prompt="   "  # 空白字符串 / Whitespace string
        )
        
        # 验证调用时传入None / Verify None is passed for empty prompt
        self.mock_app_controller.process_case_summary.assert_called_once_with(
            case_input="Test case input",
            model_id="test-model-id",
            custom_system_prompt=None
        )
    
    def test_refresh_models_success(self):
        """测试成功刷新模型 / Test successful model refresh"""
        # 设置mock返回值 / Setup mock return values
        self.mock_app_controller.refresh_models.return_value = {}
        self.mock_app_controller.get_models_for_ui.return_value = [
            {'label': '  Claude 3 Sonnet', 'value': 'claude-sonnet', 'disabled': False},
            {'label': '  Nova Pro', 'value': 'nova-pro', 'disabled': False}
        ]
        self.mock_app_controller.get_default_model.return_value = 'claude-sonnet'
        
        interface = GradioInterface(self.mock_app_controller)
        
        with patch('src.ui.gradio_interface.gr') as mock_gr:
            dropdown, status = interface._refresh_models()
        
        # 验证调用 / Verify calls
        self.mock_app_controller.refresh_models.assert_called_once()
        self.mock_app_controller.get_models_for_ui.assert_called_once()
        self.mock_app_controller.get_default_model.assert_called_once()
        
        # 验证状态 / Verify status
        assert "刷新" in status or "refreshed" in status
    
    def test_initialize_models_success(self):
        """测试成功初始化模型 / Test successful model initialization"""
        # 设置mock返回值 / Setup mock return values
        self.mock_app_controller.initialize_models.return_value = {}
        self.mock_app_controller.get_models_for_ui.return_value = [
            {'label': '  Claude 3 Sonnet', 'value': 'claude-sonnet', 'disabled': False}
        ]
        self.mock_app_controller.get_default_model.return_value = 'claude-sonnet'
        
        interface = GradioInterface(self.mock_app_controller)
        
        with patch('src.ui.gradio_interface.gr') as mock_gr:
            dropdown, status = interface._initialize_models()
        
        # 验证调用 / Verify calls
        self.mock_app_controller.initialize_models.assert_called_once()
        self.mock_app_controller.get_models_for_ui.assert_called_once()
        self.mock_app_controller.get_default_model.assert_called_once()
        
        # 验证状态 / Verify status
        assert "初始化" in status or "initialization" in status
