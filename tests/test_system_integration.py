"""
系统集成测试 / System Integration Tests

测试交互式内容优化功能与现有系统的完整集成
Test complete integration of interactive content refinement with existing system
"""

import pytest
from unittest.mock import Mock, patch
from src.services.app_controller import AppController, CaseSummaryError


class TestSystemIntegration:
    """系统集成测试类 / System Integration Test Class"""
    
    def setup_method(self):
        """设置测试环境 / Setup test environment"""
        self.config_path = "test_config.yaml"
        
    @patch('src.services.app_controller.ConfigManager')
    @patch('src.services.app_controller.HistoryProcessor')
    @patch('src.services.app_controller.BedrockClient')
    @patch('src.services.app_controller.ModelManager')
    @patch('src.services.app_controller.SystemPromptManager')
    def test_app_controller_initialization_with_refinement(
        self, mock_spm, mock_mm, mock_bc, mock_hp, mock_cm
    ):
        """测试AppController初始化包含优化功能 / Test AppController initialization with refinement features"""
        
        # 设置模拟对象
        self._setup_mocks(mock_cm, mock_hp, mock_bc, mock_mm, mock_spm)
        
        # 创建AppController实例
        app_controller = AppController(self.config_path)
        
        # 验证初始化状态
        assert app_controller.is_initialized is True
        assert app_controller.refinement_controller is None  # 延迟初始化
        
        # 验证组件初始化
        mock_cm.assert_called_once_with(self.config_path)
        mock_hp.assert_called_once()
        mock_bc.assert_called_once()
        mock_mm.assert_called_once()
        mock_spm.assert_called_once()
    
    @patch('src.services.app_controller.ConfigManager')
    @patch('src.services.app_controller.HistoryProcessor')
    @patch('src.services.app_controller.BedrockClient')
    @patch('src.services.app_controller.ModelManager')
    @patch('src.services.app_controller.SystemPromptManager')
    def test_refinement_controller_lazy_initialization(
        self, mock_spm, mock_mm, mock_bc, mock_hp, mock_cm
    ):
        """测试RefinementController延迟初始化 / Test RefinementController lazy initialization"""
        
        # 设置模拟对象
        self._setup_mocks(mock_cm, mock_hp, mock_bc, mock_mm, mock_spm)
        
        # 创建AppController实例
        app_controller = AppController(self.config_path)
        
        # 验证RefinementController未初始化
        assert app_controller.refinement_controller is None
        
        # 模拟RefinementController
        with patch('src.services.refinement_controller.RefinementController') as mock_rc:
            mock_refinement_controller = Mock()
            mock_rc.return_value = mock_refinement_controller
            
            # 获取RefinementController（触发延迟初始化）
            result = app_controller.get_refinement_controller()
            
            # 验证初始化
            assert result == mock_refinement_controller
            assert app_controller.refinement_controller == mock_refinement_controller
            mock_rc.assert_called_once_with(app_controller)
    
    @patch('src.services.app_controller.ConfigManager')
    @patch('src.services.app_controller.HistoryProcessor')
    @patch('src.services.app_controller.BedrockClient')
    @patch('src.services.app_controller.ModelManager')
    @patch('src.services.app_controller.SystemPromptManager')
    def test_start_refinement_session_integration(
        self, mock_spm, mock_mm, mock_bc, mock_hp, mock_cm
    ):
        """测试启动优化会话的集成 / Test refinement session start integration"""
        
        # 设置模拟对象
        self._setup_mocks(mock_cm, mock_hp, mock_bc, mock_mm, mock_spm)
        
        # 创建AppController实例
        app_controller = AppController(self.config_path)
        
        # 模拟RefinementController
        with patch('src.services.refinement_controller.RefinementController') as mock_rc:
            mock_refinement_controller = Mock()
            mock_refinement_controller.start_refinement_session.return_value = "session_123"
            mock_rc.return_value = mock_refinement_controller
            
            # 启动优化会话
            session_id = app_controller.start_refinement_session(
                initial_content="测试内容",
                user_id="test_user"
            )
            
            # 验证结果
            assert session_id == "session_123"
            mock_refinement_controller.start_refinement_session.assert_called_once_with(
                "测试内容", "test_user"
            )
    
    @patch('src.services.app_controller.ConfigManager')
    @patch('src.services.app_controller.HistoryProcessor')
    @patch('src.services.app_controller.BedrockClient')
    @patch('src.services.app_controller.ModelManager')
    @patch('src.services.app_controller.SystemPromptManager')
    def test_process_refinement_message_integration(
        self, mock_spm, mock_mm, mock_bc, mock_hp, mock_cm
    ):
        """测试处理优化消息的集成 / Test refinement message processing integration"""
        
        # 设置模拟对象
        self._setup_mocks(mock_cm, mock_hp, mock_bc, mock_mm, mock_spm)
        
        # 创建AppController实例
        app_controller = AppController(self.config_path)
        
        # 模拟RefinementController
        with patch('src.services.refinement_controller.RefinementController') as mock_rc:
            mock_refinement_controller = Mock()
            expected_result = {
                'success': True,
                'response': '已处理您的请求',
                'modified_content': '修改后的内容'
            }
            mock_refinement_controller.process_user_message.return_value = expected_result
            mock_rc.return_value = mock_refinement_controller
            
            # 处理优化消息
            result = app_controller.process_refinement_message(
                message="请添加更多细节",
                session_id="session_123"
            )
            
            # 验证结果
            assert result == expected_result
            mock_refinement_controller.process_user_message.assert_called_once_with(
                "请添加更多细节", "session_123"
            )
    
    @patch('src.services.app_controller.ConfigManager')
    @patch('src.services.app_controller.HistoryProcessor')
    @patch('src.services.app_controller.BedrockClient')
    @patch('src.services.app_controller.ModelManager')
    @patch('src.services.app_controller.SystemPromptManager')
    def test_existing_functionality_compatibility(
        self, mock_spm, mock_mm, mock_bc, mock_hp, mock_cm
    ):
        """测试现有功能兼容性 / Test existing functionality compatibility"""
        
        # 设置模拟对象
        self._setup_mocks(mock_cm, mock_hp, mock_bc, mock_mm, mock_spm)
        
        # 设置模型管理器模拟
        mock_model_manager = mock_mm.return_value
        mock_model_manager.refresh_available_models.return_value = {
            "claude": [{"id": "claude-3", "name": "Claude 3"}]
        }
        mock_model_manager.is_model_available.return_value = True
        mock_model_manager.get_models_for_ui.return_value = [
            {"label": "Claude 3", "value": "claude-3", "disabled": False}
        ]
        mock_model_manager.get_default_model.return_value = "claude-3"
        
        # 设置历史处理器模拟
        mock_history_processor = mock_hp.return_value
        mock_history_processor.load_history_files.return_value = []
        mock_history_processor.process_history_content.return_value = ""
        mock_history_processor.filter_relevant_history.return_value = ""
        
        # 设置Bedrock客户端模拟
        mock_bedrock_client = mock_bc.return_value
        mock_bedrock_client.format_messages.return_value = [{"role": "user", "content": "test"}]
        mock_bedrock_client.converse.return_value = "生成的总结内容"
        
        # 设置系统提示词管理器模拟
        mock_system_prompt_manager = mock_spm.return_value
        mock_system_prompt_manager.get_active_prompt.return_value = None  # 返回None以使用默认提示词
        
        # 设置配置管理器模拟
        mock_config_manager = mock_cm.return_value
        mock_config_manager.get_app_config.return_value = {
            "max_tokens": 4000,
            "temperature": 0.7
        }
        mock_config_manager.get_system_prompt.return_value = "默认系统提示词"
        
        # 创建AppController实例
        app_controller = AppController(self.config_path)
        
        # 测试现有功能：初始化模型
        models = app_controller.initialize_models()
        assert "claude" in models
        
        # 测试现有功能：获取UI模型列表
        ui_models = app_controller.get_models_for_ui()
        assert len(ui_models) > 0
        assert ui_models[0]["label"] == "Claude 3"
        
        # 测试现有功能：获取默认模型
        default_model = app_controller.get_default_model()
        assert default_model == "claude-3"
        
        # 测试现有功能：处理案例总结
        summary = app_controller.process_case_summary(
            case_input="测试案例内容",
            model_id="claude-3"
        )
        assert summary == "生成的总结内容"
        
        # 验证现有功能调用
        mock_model_manager.refresh_available_models.assert_called()
        mock_bedrock_client.converse.assert_called_once()
    
    @patch('src.services.app_controller.ConfigManager')
    @patch('src.services.app_controller.HistoryProcessor')
    @patch('src.services.app_controller.BedrockClient')
    @patch('src.services.app_controller.ModelManager')
    @patch('src.services.app_controller.SystemPromptManager')
    def test_error_handling_integration(
        self, mock_spm, mock_mm, mock_bc, mock_hp, mock_cm
    ):
        """测试错误处理集成 / Test error handling integration"""
        
        # 设置模拟对象
        self._setup_mocks(mock_cm, mock_hp, mock_bc, mock_mm, mock_spm)
        
        # 创建AppController实例
        app_controller = AppController(self.config_path)
        
        # 测试RefinementController初始化失败
        with patch('src.services.refinement_controller.RefinementController') as mock_rc:
            mock_rc.side_effect = Exception("初始化失败")
            
            with pytest.raises(CaseSummaryError) as exc_info:
                app_controller.get_refinement_controller()
            
            assert "交互式优化控制器初始化失败" in str(exc_info.value)
        
        # 测试优化消息处理失败
        with patch('src.services.refinement_controller.RefinementController') as mock_rc:
            mock_refinement_controller = Mock()
            mock_refinement_controller.process_user_message.side_effect = Exception("处理失败")
            mock_rc.return_value = mock_refinement_controller
            
            result = app_controller.process_refinement_message("test", "session_123")
            
            assert result['success'] is False
            assert "处理失败" in result['error']
    
    def _setup_mocks(self, mock_cm, mock_hp, mock_bc, mock_mm, mock_spm):
        """设置通用模拟对象 / Setup common mock objects"""
        # 配置管理器模拟
        mock_config_manager = Mock()
        mock_config_manager.load_config.return_value = None
        mock_config_manager.validate_aws_credentials.return_value = True
        mock_config_manager.get_history_folder.return_value = "./test_history"
        mock_config_manager.get_boto3_session.return_value = Mock()
        mock_config_manager.config_data = {"models": {}}
        mock_config_manager.get_app_config.return_value = {
            "title": "测试应用",
            "max_tokens": 4000,
            "temperature": 0.7
        }
        mock_cm.return_value = mock_config_manager
        
        # 其他组件模拟
        mock_hp.return_value = Mock()
        mock_bc.return_value = Mock()
        mock_mm.return_value = Mock()
        mock_spm.return_value = Mock()


if __name__ == "__main__":
    pytest.main([__file__])