"""
Gradio界面系统提示词集成测试 / Gradio Interface System Prompt Integration Tests
"""

import pytest
from unittest.mock import Mock, patch

from src.ui.gradio_interface import GradioInterface


class TestGradioInterfaceIntegration:
    """Gradio界面系统提示词集成测试类 / Gradio Interface System Prompt Integration Test Class"""
    
    @pytest.fixture
    def mock_app_controller(self):
        """创建模拟的应用控制器 / Create mock app controller"""
        controller = Mock()
        controller.get_app_config.return_value = {
            'title': 'Test App',
            'max_tokens': 4000,
            'temperature': 0.7
        }
        controller.config_manager.get_system_prompt.return_value = "Default system prompt"
        controller.get_models_for_ui.return_value = [
            {'label': 'Claude 3.5 Sonnet', 'value': 'claude-3-5-sonnet', 'disabled': False}
        ]
        controller.get_default_model.return_value = 'claude-3-5-sonnet'
        controller.initialize_models.return_value = {}
        controller.refresh_models.return_value = {}
        controller.process_case_summary.return_value = "Generated summary"
        return controller
    
    @pytest.fixture
    def gradio_interface(self, mock_app_controller):
        """创建Gradio界面实例 / Create Gradio interface instance"""
        return GradioInterface(mock_app_controller)
    
    def test_initialization_with_prompt_ui(self, gradio_interface, mock_app_controller):
        """测试初始化时包含提示词UI组件 / Test initialization includes prompt UI components"""
        assert gradio_interface.app_controller == mock_app_controller
        assert gradio_interface.prompt_ui is not None
        assert hasattr(gradio_interface.prompt_ui, 'prompt_manager')
    
    @patch('gradio.Blocks')
    @patch('gradio.Markdown')
    @patch('gradio.Row')
    @patch('gradio.Column')
    @patch('gradio.Group')
    @patch('gradio.Textbox')
    @patch('gradio.Dropdown')
    @patch('gradio.Button')
    def test_create_interface_includes_prompt_components(self, mock_button, mock_dropdown, 
                                                       mock_textbox, mock_group, mock_column, 
                                                       mock_row, mock_markdown, mock_blocks, 
                                                       gradio_interface):
        """测试创建界面包含提示词管理组件 / Test create interface includes prompt management components"""
        # 配置模拟 / Configure mocks
        mock_blocks_instance = Mock()
        mock_blocks.return_value.__enter__.return_value = mock_blocks_instance
        
        with patch.object(gradio_interface.prompt_ui, 'create_prompt_selector') as mock_selector, \
             patch.object(gradio_interface.prompt_ui, 'create_prompt_editor') as mock_editor, \
             patch.object(gradio_interface.prompt_ui, 'create_prompt_management_panel') as mock_panel, \
             patch.object(gradio_interface.prompt_ui, 'create_new_prompt_dialog') as mock_dialog:
            
            mock_selector.return_value = Mock()
            mock_editor.return_value = Mock()
            mock_panel.return_value = (Mock(), Mock(), Mock(), Mock(), Mock())
            mock_dialog.return_value = (Mock(), Mock(), Mock(), Mock(), Mock())
            
            # 调用方法 / Call method
            interface = gradio_interface.create_interface()
            
            # 验证提示词UI组件被调用 / Verify prompt UI components were called
            mock_selector.assert_called_once()
            mock_editor.assert_called_once()
            mock_panel.assert_called_once()
            mock_dialog.assert_called_once()
    
    def test_generate_summary_uses_prompt_content(self, gradio_interface, mock_app_controller):
        """测试生成总结使用提示词内容 / Test generate summary uses prompt content"""
        # 调用方法 / Call method
        result, status = gradio_interface._generate_summary("Test case", "test-model", "Custom prompt")
        
        # 验证调用 / Verify calls
        mock_app_controller.process_case_summary.assert_called_once_with(
            case_input="Test case",
            model_id="test-model",
            custom_system_prompt="Custom prompt"
        )
        assert result == "Generated summary"
        assert "成功" in status or "successfully" in status
    
    def test_generate_summary_empty_prompt(self, gradio_interface, mock_app_controller):
        """测试生成总结时提示词为空 / Test generate summary with empty prompt"""
        # 调用方法 / Call method
        result, status = gradio_interface._generate_summary("Test case", "test-model", "")
        
        # 验证调用时custom_system_prompt为None / Verify custom_system_prompt is None
        mock_app_controller.process_case_summary.assert_called_once_with(
            case_input="Test case",
            model_id="test-model",
            custom_system_prompt=None
        )
    
    def test_save_current_prompt(self, gradio_interface):
        """测试保存当前提示词 / Test save current prompt"""
        with patch.object(gradio_interface.prompt_ui, 'handle_prompt_update') as mock_update:
            mock_update.return_value = "Success message"
            
            # 调用方法 / Call method
            result = gradio_interface._save_current_prompt("test_prompt", "Updated content")
            
            # 验证调用 / Verify calls
            mock_update.assert_called_once_with("test_prompt", "Updated content")
            assert result == "Success message"
    
    def test_generate_summary_validation_errors(self, gradio_interface):
        """测试生成总结的输入验证错误 / Test generate summary input validation errors"""
        # 测试空案例输入 / Test empty case input
        result, status = gradio_interface._generate_summary("", "test-model", "prompt")
        assert result == ""
        assert "案例输入不能为空" in status or "Case input cannot be empty" in status
        
        # 测试空模型ID / Test empty model ID
        result, status = gradio_interface._generate_summary("Test case", "", "prompt")
        assert result == ""
        assert "请选择一个模型" in status or "Please select a model" in status
    
    def test_generate_summary_exception_handling(self, gradio_interface, mock_app_controller):
        """测试生成总结的异常处理 / Test generate summary exception handling"""
        # 配置模拟抛出异常 / Configure mock to raise exception
        mock_app_controller.process_case_summary.side_effect = Exception("Test error")
        
        # 调用方法 / Call method
        result, status = gradio_interface._generate_summary("Test case", "test-model", "prompt")
        
        # 验证结果 / Verify results
        assert result == ""
        assert "Test error" in status
        assert "未知错误" in status or "Unknown error" in status