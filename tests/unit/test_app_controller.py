"""
应用控制器单元测试 / App Controller Unit Tests

测试应用控制器的各项功能
Test various functions of app controller
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.services.app_controller import AppController, CaseSummaryError


class TestAppController:
    """AppController测试类 / AppController test class"""
    
    @patch('src.services.app_controller.ConfigManager')
    @patch('src.services.app_controller.HistoryProcessor')
    @patch('src.services.app_controller.BedrockClient')
    @patch('src.services.app_controller.ModelManager')
    def test_init_success(self, mock_model_manager, mock_bedrock_client, mock_history_processor, mock_config_manager):
        """测试成功初始化 / Test successful initialization"""
        # 设置mock / Setup mocks
        mock_config_instance = Mock()
        mock_config_manager.return_value = mock_config_instance
        mock_config_instance.load_config.return_value = {}
        mock_config_instance.validate_aws_credentials.return_value = True
        mock_config_instance.get_history_folder.return_value = './history'
        mock_config_instance.get_boto3_session.return_value = Mock()
        mock_config_instance.config_data = {}
        
        controller = AppController()
        
        assert controller.is_initialized is True
        mock_config_instance.load_config.assert_called_once()
        mock_config_instance.validate_aws_credentials.assert_called_once()
    
    @patch('src.services.app_controller.ConfigManager')
    def test_init_failure(self, mock_config_manager):
        """测试初始化失败 / Test initialization failure"""
        # 设置mock抛出异常 / Setup mock to throw exception
        mock_config_instance = Mock()
        mock_config_manager.return_value = mock_config_instance
        mock_config_instance.load_config.side_effect = Exception("Config error")
        
        with pytest.raises(CaseSummaryError, match="应用初始化失败"):
            AppController()
    
    def test_initialize_models_not_initialized(self):
        """测试未初始化时调用initialize_models / Test initialize_models when not initialized"""
        with patch('src.services.app_controller.ConfigManager') as mock_config_manager:
            mock_config_instance = Mock()
            mock_config_manager.return_value = mock_config_instance
            mock_config_instance.load_config.side_effect = Exception("Config error")
            
            controller = None
            try:
                controller = AppController()
            except CaseSummaryError:
                # 创建一个部分初始化的控制器用于测试 / Create partially initialized controller for testing
                controller = object.__new__(AppController)
                controller.is_initialized = False
            
            with pytest.raises(CaseSummaryError, match="应用未初始化"):
                controller.initialize_models()
    
    @patch('src.services.app_controller.ConfigManager')
    @patch('src.services.app_controller.HistoryProcessor')
    @patch('src.services.app_controller.BedrockClient')
    @patch('src.services.app_controller.ModelManager')
    def test_initialize_models_success(self, mock_model_manager, mock_bedrock_client, mock_history_processor, mock_config_manager):
        """测试成功初始化模型 / Test successful model initialization"""
        # 设置mock / Setup mocks
        self._setup_successful_mocks(mock_config_manager, mock_history_processor, mock_bedrock_client, mock_model_manager)
        
        mock_model_manager_instance = mock_model_manager.return_value
        mock_models = {
            'claude': [{'modelId': 'claude-test', 'displayName': 'Claude Test'}],
            'nova': [{'modelId': 'nova-test', 'displayName': 'Nova Test'}]
        }
        mock_model_manager_instance.refresh_available_models.return_value = mock_models
        
        controller = AppController()
        result = controller.initialize_models()
        
        assert result == mock_models
        assert controller.available_models == mock_models
    
    @patch('src.services.app_controller.ConfigManager')
    @patch('src.services.app_controller.HistoryProcessor')
    @patch('src.services.app_controller.BedrockClient')
    @patch('src.services.app_controller.ModelManager')
    def test_process_case_summary_success(self, mock_model_manager, mock_bedrock_client, mock_history_processor, mock_config_manager):
        """测试成功处理案例总结 / Test successful case summary processing"""
        # 设置mock / Setup mocks
        self._setup_successful_mocks(mock_config_manager, mock_history_processor, mock_bedrock_client, mock_model_manager)
        
        # 设置特定的mock返回值 / Setup specific mock return values
        mock_model_manager_instance = mock_model_manager.return_value
        mock_model_manager_instance.is_model_available.return_value = True
        
        mock_history_processor_instance = mock_history_processor.return_value
        mock_history_processor_instance.load_history_files.return_value = [
            {'name': 'test.txt', 'content': 'test content', 'category': 'test', 'path': '/test.txt'}
        ]
        mock_history_processor_instance.process_history_content.return_value = "processed history"
        mock_history_processor_instance.filter_relevant_history.return_value = "relevant history"
        
        mock_bedrock_client_instance = mock_bedrock_client.return_value
        mock_bedrock_client_instance.format_messages.return_value = [{'role': 'user', 'content': [{'text': 'test'}]}]
        mock_bedrock_client_instance.converse.return_value = "Generated summary"
        
        controller = AppController()
        
        result = controller.process_case_summary(
            case_input="This is a test case input",
            model_id="test-model-id"
        )
        
        assert result == "Generated summary"
        mock_bedrock_client_instance.converse.assert_called_once()
    
    def test_validate_input_empty(self):
        """测试验证空输入 / Test validating empty input"""
        with patch('src.services.app_controller.ConfigManager'):
            try:
                controller = AppController()
            except:
                pass
            
            assert controller.validate_input("") is False
            assert controller.validate_input("   ") is False
    
    def test_validate_input_too_short(self):
        """测试验证过短输入 / Test validating too short input"""
        with patch('src.services.app_controller.ConfigManager'):
            try:
                controller = AppController()
            except:
                pass
            
            assert controller.validate_input("ab") is False
    
    def test_validate_input_valid(self):
        """测试验证有效输入 / Test validating valid input"""
        with patch('src.services.app_controller.ConfigManager'):
            try:
                controller = AppController()
            except:
                pass
            
            assert controller.validate_input("This is a valid input") is True
    
    @patch('src.services.app_controller.ConfigManager')
    @patch('src.services.app_controller.HistoryProcessor')
    @patch('src.services.app_controller.BedrockClient')
    @patch('src.services.app_controller.ModelManager')
    def test_refresh_models(self, mock_model_manager, mock_bedrock_client, mock_history_processor, mock_config_manager):
        """测试刷新模型列表 / Test refreshing model list"""
        # 设置mock / Setup mocks
        self._setup_successful_mocks(mock_config_manager, mock_history_processor, mock_bedrock_client, mock_model_manager)
        
        mock_model_manager_instance = mock_model_manager.return_value
        mock_models = {'claude': [{'modelId': 'claude-new', 'displayName': 'Claude New'}]}
        mock_model_manager_instance.refresh_available_models.return_value = mock_models
        
        controller = AppController()
        result = controller.refresh_models()
        
        assert result == mock_models
        assert controller.available_models == mock_models
    
    @patch('src.services.app_controller.ConfigManager')
    @patch('src.services.app_controller.HistoryProcessor')
    @patch('src.services.app_controller.BedrockClient')
    @patch('src.services.app_controller.ModelManager')
    def test_get_models_for_ui(self, mock_model_manager, mock_bedrock_client, mock_history_processor, mock_config_manager):
        """测试获取UI模型列表 / Test getting UI model list"""
        # 设置mock / Setup mocks
        self._setup_successful_mocks(mock_config_manager, mock_history_processor, mock_bedrock_client, mock_model_manager)
        
        mock_model_manager_instance = mock_model_manager.return_value
        mock_ui_models = [
            {'value': 'claude-test', 'label': 'Claude Test', 'disabled': False}
        ]
        mock_model_manager_instance.get_models_for_ui.return_value = mock_ui_models
        
        controller = AppController()
        result = controller.get_models_for_ui()
        
        assert result == mock_ui_models
    
    def test_get_models_for_ui_not_initialized(self):
        """测试未初始化时获取UI模型列表 / Test getting UI model list when not initialized"""
        with patch('src.services.app_controller.ConfigManager') as mock_config_manager:
            mock_config_instance = Mock()
            mock_config_manager.return_value = mock_config_instance
            mock_config_instance.load_config.side_effect = Exception("Config error")
            
            controller = None
            try:
                controller = AppController()
            except CaseSummaryError:
                # 创建一个部分初始化的控制器用于测试 / Create partially initialized controller for testing
                controller = object.__new__(AppController)
                controller.is_initialized = False
            
            result = controller.get_models_for_ui()
            
            assert result == []
    
    @patch('src.services.app_controller.ConfigManager')
    @patch('src.services.app_controller.HistoryProcessor')
    @patch('src.services.app_controller.BedrockClient')
    @patch('src.services.app_controller.ModelManager')
    def test_get_default_model(self, mock_model_manager, mock_bedrock_client, mock_history_processor, mock_config_manager):
        """测试获取默认模型 / Test getting default model"""
        # 设置mock / Setup mocks
        self._setup_successful_mocks(mock_config_manager, mock_history_processor, mock_bedrock_client, mock_model_manager)
        
        mock_model_manager_instance = mock_model_manager.return_value
        mock_model_manager_instance.get_default_model.return_value = 'test-default-model'
        
        controller = AppController()
        result = controller.get_default_model()
        
        assert result == 'test-default-model'
    
    @patch('src.services.app_controller.ConfigManager')
    @patch('src.services.app_controller.HistoryProcessor')
    @patch('src.services.app_controller.BedrockClient')
    @patch('src.services.app_controller.ModelManager')
    def test_get_app_config(self, mock_model_manager, mock_bedrock_client, mock_history_processor, mock_config_manager):
        """测试获取应用配置 / Test getting app configuration"""
        # 设置mock / Setup mocks
        self._setup_successful_mocks(mock_config_manager, mock_history_processor, mock_bedrock_client, mock_model_manager)
        
        mock_config_instance = mock_config_manager.return_value
        mock_app_config = {
            'title': 'Test App',
            'max_tokens': 2000,
            'temperature': 0.5
        }
        mock_config_instance.get_app_config.return_value = mock_app_config
        
        controller = AppController()
        result = controller.get_app_config()
        
        assert result == mock_app_config
    
    @patch('src.services.app_controller.ConfigManager')
    @patch('src.services.app_controller.HistoryProcessor')
    @patch('src.services.app_controller.BedrockClient')
    @patch('src.services.app_controller.ModelManager')
    def test_get_initialization_status(self, mock_model_manager, mock_bedrock_client, mock_history_processor, mock_config_manager):
        """测试获取初始化状态 / Test getting initialization status"""
        # 设置mock / Setup mocks
        self._setup_successful_mocks(mock_config_manager, mock_history_processor, mock_bedrock_client, mock_model_manager)
        
        controller = AppController()
        is_initialized, message = controller.get_initialization_status()
        
        assert is_initialized is True
        assert "成功" in message or "successfully" in message
    
    def _setup_successful_mocks(self, mock_config_manager, mock_history_processor, mock_bedrock_client, mock_model_manager):
        """设置成功的mock对象 / Setup successful mock objects"""
        # ConfigManager mock
        mock_config_instance = Mock()
        mock_config_manager.return_value = mock_config_instance
        mock_config_instance.load_config.return_value = {}
        mock_config_instance.validate_aws_credentials.return_value = True
        mock_config_instance.get_history_folder.return_value = './history'
        mock_config_instance.get_boto3_session.return_value = Mock()
        mock_config_instance.config_data = {}
        mock_config_instance.get_system_prompt.return_value = "Test system prompt"
        mock_config_instance.get_app_config.return_value = {
            'title': 'Test App',
            'max_tokens': 4000,
            'temperature': 0.7
        }
        
        # HistoryProcessor mock
        mock_history_instance = Mock()
        mock_history_processor.return_value = mock_history_instance
        
        # BedrockClient mock
        mock_bedrock_instance = Mock()
        mock_bedrock_client.return_value = mock_bedrock_instance
        
        # ModelManager mock
        mock_model_instance = Mock()
        mock_model_manager.return_value = mock_model_instance
