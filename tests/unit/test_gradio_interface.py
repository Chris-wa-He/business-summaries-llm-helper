"""
Gradio界面单元测试 / Gradio Interface Unit Tests

测试Gradio界面的各项功能
Test various functions of Gradio interface
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.ui.gradio_interface import GradioInterface
from src.services.app_controller import CaseSummaryError


class TestGradioInterface:
    """GradioInterface测试类 / GradioInterface test class"""
    
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
    
    @patch('src.ui.gradio_interface.gr')
    def test_create_interface(self, mock_gr):
        """测试创建界面 / Test creating interface"""
        # 设置mock / Setup mock
        mock_blocks = Mock()
        mock_gr.Blocks.return_value.__enter__.return_value = mock_blocks
        
        interface = GradioInterface(self.mock_app_controller)
        result = interface.create_interface()
        
        # 验证Gradio组件被创建 / Verify Gradio components are created
        mock_gr.Blocks.assert_called_once()
        mock_gr.Markdown.assert_called()
        mock_gr.Textbox.assert_called()
        mock_gr.Dropdown.assert_called()
        mock_gr.Button.assert_called()
        
        assert interface.interface == mock_blocks
    
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
    
    def test_generate_summary_unknown_error(self):
        """测试未知错误 / Test unknown error"""
        # 设置mock抛出未知异常 / Setup mock to throw unknown exception
        self.mock_app_controller.process_case_summary.side_effect = Exception("Unknown error")
        
        interface = GradioInterface(self.mock_app_controller)
        
        result_summary, result_status = interface._generate_summary(
            case_input="Test case input",
            model_id="test-model-id",
            system_prompt=""
        )
        
        assert result_summary == ""
        assert "未知错误" in result_status or "Unknown error" in result_status
    
    @patch('src.ui.gradio_interface.gr')
    def test_refresh_models_success(self, mock_gr):
        """测试成功刷新模型 / Test successful model refresh"""
        # 设置mock返回值 / Setup mock return values
        self.mock_app_controller.refresh_models.return_value = {}
        self.mock_app_controller.get_models_for_ui.return_value = [
            {'label': '  Claude 3 Sonnet', 'value': 'claude-sonnet', 'disabled': False},
            {'label': '  Nova Pro', 'value': 'nova-pro', 'disabled': False}
        ]
        self.mock_app_controller.get_default_model.return_value = 'claude-sonnet'
        
        interface = GradioInterface(self.mock_app_controller)
        
        dropdown, status = interface._refresh_models()
        
        # 验证调用 / Verify calls
        self.mock_app_controller.refresh_models.assert_called_once()
        self.mock_app_controller.get_models_for_ui.assert_called_once()
        self.mock_app_controller.get_default_model.assert_called_once()
        
        # 验证状态 / Verify status
        assert "刷新" in status or "refreshed" in status
    
    @patch('src.ui.gradio_interface.gr')
    def test_refresh_models_error(self, mock_gr):
        """测试刷新模型错误 / Test model refresh error"""
        # 设置mock抛出异常 / Setup mock to throw exception
        self.mock_app_controller.refresh_models.side_effect = Exception("Refresh error")
        
        interface = GradioInterface(self.mock_app_controller)
        
        dropdown, status = interface._refresh_models()
        
        # 验证错误状态 / Verify error status
        assert "失败" in status or "failed" in status
        assert "Refresh error" in status
    
    @patch('src.ui.gradio_interface.gr')
    def test_initialize_models_success(self, mock_gr):
        """测试成功初始化模型 / Test successful model initialization"""
        # 设置mock返回值 / Setup mock return values
        self.mock_app_controller.initialize_models.return_value = {}
        self.mock_app_controller.get_models_for_ui.return_value = [
            {'label': '  Claude 3 Sonnet', 'value': 'claude-sonnet', 'disabled': False}
        ]
        self.mock_app_controller.get_default_model.return_value = 'claude-sonnet'
        
        interface = GradioInterface(self.mock_app_controller)
        
        dropdown, status = interface._initialize_models()
        
        # 验证调用 / Verify calls
        self.mock_app_controller.initialize_models.assert_called_once()
        self.mock_app_controller.get_models_for_ui.assert_called_once()
        self.mock_app_controller.get_default_model.assert_called_once()
        
        # 验证状态 / Verify status
        assert "初始化" in status or "initialization" in status
    
    @patch('src.ui.gradio_interface.gr')
    def test_initialize_models_error(self, mock_gr):
        """测试初始化模型错误 / Test model initialization error"""
        # 设置mock抛出异常 / Setup mock to throw exception
        self.mock_app_controller.initialize_models.side_effect = Exception("Init error")
        
        interface = GradioInterface(self.mock_app_controller)
        
        dropdown, status = interface._initialize_models()
        
        # 验证错误状态 / Verify error status
        assert "失败" in status or "failed" in status
        assert "Init error" in status
    
    @patch('src.ui.gradio_interface.gr')
    def test_launch_creates_interface_if_none(self, mock_gr):
        """测试启动时创建界面（如果不存在）/ Test launch creates interface if none exists"""
        # 设置mock / Setup mock
        mock_blocks = Mock()
        mock_gr.Blocks.return_value.__enter__.return_value = mock_blocks
        
        interface = GradioInterface(self.mock_app_controller)
        
        # 确保interface为None / Ensure interface is None
        assert interface.interface is None
        
        # 调用launch / Call launch
        interface.launch()
        
        # 验证interface被创建 / Verify interface is created
        assert interface.interface == mock_blocks
        mock_blocks.launch.assert_called_once()
    
    @patch('src.ui.gradio_interface.gr')
    def test_launch_with_existing_interface(self, mock_gr):
        """测试启动已存在的界面 / Test launch with existing interface"""
        # 设置mock / Setup mock
        mock_blocks = Mock()
        
        interface = GradioInterface(self.mock_app_controller)
        interface.interface = mock_blocks
        
        # 调用launch / Call launch
        interface.launch(
            server_name="0.0.0.0",
            server_port=8080,
            share=True,
            debug=True
        )
        
        # 验证launch参数 / Verify launch parameters
        mock_blocks.launch.assert_called_once_with(
            server_name="0.0.0.0",
            server_port=8080,
            share=True,
            debug=True,
            show_error=True
        )
