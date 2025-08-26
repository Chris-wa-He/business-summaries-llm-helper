"""
应用控制器系统提示词集成测试 / App Controller System Prompt Integration Tests
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.services.app_controller import AppController, CaseSummaryError


class TestAppControllerPromptIntegration:
    """应用控制器系统提示词集成测试类 / App Controller System Prompt Integration Test Class"""
    
    @pytest.fixture
    def mock_dependencies(self):
        """创建模拟依赖 / Create mock dependencies"""
        with patch('src.services.app_controller.ConfigManager') as mock_config, \
             patch('src.services.app_controller.HistoryProcessor') as mock_history, \
             patch('src.services.app_controller.BedrockClient') as mock_bedrock, \
             patch('src.services.app_controller.ModelManager') as mock_model, \
             patch('src.services.app_controller.SystemPromptManager') as mock_prompt:
            
            # 配置模拟对象 / Configure mock objects
            mock_config_instance = Mock()
            mock_config_instance.load_config.return_value = None
            mock_config_instance.validate_aws_credentials.return_value = True
            mock_config_instance.get_history_folder.return_value = "./history_references"
            mock_config_instance.get_boto3_session.return_value = Mock()
            mock_config_instance.config_data = {}
            mock_config_instance.get_system_prompt.return_value = "Default system prompt"
            mock_config_instance.get_app_config.return_value = {
                'title': 'Test App',
                'max_tokens': 4000,
                'temperature': 0.7
            }
            mock_config.return_value = mock_config_instance
            
            mock_history_instance = Mock()
            mock_history.return_value = mock_history_instance
            
            mock_bedrock_instance = Mock()
            mock_bedrock.return_value = mock_bedrock_instance
            
            mock_model_instance = Mock()
            mock_model_instance.is_model_available.return_value = True
            mock_model.return_value = mock_model_instance
            
            mock_prompt_instance = Mock()
            mock_prompt_instance.list_prompts.return_value = [
                {'name': 'default', 'content': 'Default prompt'},
                {'name': 'technical', 'content': 'Technical prompt'}
            ]
            mock_prompt_instance.get_active_prompt.return_value = {'name': 'default', 'content': 'Active prompt content'}
            mock_prompt_instance.set_active_prompt.return_value = True
            mock_prompt_instance.create_prompt.return_value = True
            mock_prompt_instance.update_prompt.return_value = True
            mock_prompt_instance.delete_prompt.return_value = True
            mock_prompt.return_value = mock_prompt_instance
            
            yield {
                'config': mock_config_instance,
                'history': mock_history_instance,
                'bedrock': mock_bedrock_instance,
                'model': mock_model_instance,
                'prompt': mock_prompt_instance
            }
    
    @pytest.fixture
    def app_controller(self, mock_dependencies):
        """创建应用控制器实例 / Create app controller instance"""
        return AppController()
    
    def test_system_prompt_manager_initialization(self, app_controller, mock_dependencies):
        """测试系统提示词管理器初始化 / Test system prompt manager initialization"""
        assert app_controller.system_prompt_manager is not None
        assert app_controller.is_initialized is True
    
    def test_get_available_prompts_success(self, app_controller, mock_dependencies):
        """测试成功获取可用提示词 / Test successful get available prompts"""
        prompts = app_controller.get_available_prompts()
        
        assert len(prompts) == 2
        assert prompts[0]['name'] == 'default'
        assert prompts[1]['name'] == 'technical'
        mock_dependencies['prompt'].list_prompts.assert_called_once()
    
    def test_get_available_prompts_not_initialized(self):
        """测试未初始化时获取提示词 / Test get prompts when not initialized"""
        with patch('src.services.app_controller.ConfigManager') as mock_config:
            mock_config.side_effect = Exception("Init failed")
            
            # 初始化失败时应该抛出异常 / Should raise exception when initialization fails
            with pytest.raises(Exception):
                app_controller = AppController()
    
    def test_get_active_prompt_success(self, app_controller, mock_dependencies):
        """测试成功获取激活提示词 / Test successful get active prompt"""
        active_prompt = app_controller.get_active_prompt()
        
        assert active_prompt is not None
        assert active_prompt['name'] == 'default'
        assert active_prompt['content'] == 'Active prompt content'
        mock_dependencies['prompt'].get_active_prompt.assert_called_once()
    
    def test_get_active_prompt_none(self, app_controller, mock_dependencies):
        """测试获取激活提示词返回None / Test get active prompt returns None"""
        mock_dependencies['prompt'].get_active_prompt.return_value = None
        
        active_prompt = app_controller.get_active_prompt()
        
        assert active_prompt is None
    
    def test_set_active_prompt_success(self, app_controller, mock_dependencies):
        """测试成功设置激活提示词 / Test successful set active prompt"""
        result = app_controller.set_active_prompt('technical')
        
        assert result is True
        mock_dependencies['prompt'].set_active_prompt.assert_called_once_with('technical')
    
    def test_set_active_prompt_failure(self, app_controller, mock_dependencies):
        """测试设置激活提示词失败 / Test set active prompt failure"""
        mock_dependencies['prompt'].set_active_prompt.return_value = False
        
        result = app_controller.set_active_prompt('nonexistent')
        
        assert result is False
    
    def test_create_prompt_success(self, app_controller, mock_dependencies):
        """测试成功创建提示词 / Test successful create prompt"""
        result = app_controller.create_prompt('new_prompt', 'New content')
        
        assert result is True
        mock_dependencies['prompt'].create_prompt.assert_called_once_with('new_prompt', 'New content')
    
    def test_create_prompt_failure(self, app_controller, mock_dependencies):
        """测试创建提示词失败 / Test create prompt failure"""
        mock_dependencies['prompt'].create_prompt.return_value = False
        
        result = app_controller.create_prompt('invalid', 'content')
        
        assert result is False
    
    def test_update_prompt_success(self, app_controller, mock_dependencies):
        """测试成功更新提示词 / Test successful update prompt"""
        result = app_controller.update_prompt('existing', 'Updated content')
        
        assert result is True
        mock_dependencies['prompt'].update_prompt.assert_called_once_with('existing', 'Updated content')
    
    def test_update_prompt_failure(self, app_controller, mock_dependencies):
        """测试更新提示词失败 / Test update prompt failure"""
        mock_dependencies['prompt'].update_prompt.return_value = False
        
        result = app_controller.update_prompt('nonexistent', 'content')
        
        assert result is False
    
    def test_delete_prompt_success(self, app_controller, mock_dependencies):
        """测试成功删除提示词 / Test successful delete prompt"""
        result = app_controller.delete_prompt('to_delete')
        
        assert result is True
        mock_dependencies['prompt'].delete_prompt.assert_called_once_with('to_delete')
    
    def test_delete_prompt_failure(self, app_controller, mock_dependencies):
        """测试删除提示词失败 / Test delete prompt failure"""
        mock_dependencies['prompt'].delete_prompt.return_value = False
        
        result = app_controller.delete_prompt('nonexistent')
        
        assert result is False
    
    def test_process_case_summary_uses_active_prompt(self, app_controller, mock_dependencies):
        """测试案例总结使用激活的提示词 / Test case summary uses active prompt"""
        # 配置模拟 / Configure mocks
        mock_dependencies['history'].load_history_files.return_value = []
        mock_dependencies['history'].process_history_content.return_value = ""
        mock_dependencies['history'].filter_relevant_history.return_value = ""
        
        with patch.object(app_controller.prompt_builder, 'build_prompt') as mock_build, \
             patch.object(app_controller.bedrock_client, 'format_messages') as mock_format, \
             patch.object(app_controller.bedrock_client, 'converse') as mock_converse:
            
            mock_build.return_value = "Built prompt"
            mock_format.return_value = [{"role": "user", "content": "Built prompt"}]
            mock_converse.return_value = "Generated summary"
            
            # 调用方法 / Call method
            result = app_controller.process_case_summary("Test case", "test-model")
            
            # 验证使用了激活的提示词 / Verify active prompt was used
            mock_build.assert_called_once()
            call_args = mock_build.call_args[1]
            assert call_args['system_prompt'] == 'Active prompt content'
            assert result == "Generated summary"
    
    def test_process_case_summary_uses_custom_prompt(self, app_controller, mock_dependencies):
        """测试案例总结使用自定义提示词 / Test case summary uses custom prompt"""
        # 配置模拟 / Configure mocks
        mock_dependencies['history'].load_history_files.return_value = []
        mock_dependencies['history'].process_history_content.return_value = ""
        mock_dependencies['history'].filter_relevant_history.return_value = ""
        
        with patch.object(app_controller.prompt_builder, 'build_prompt') as mock_build, \
             patch.object(app_controller.bedrock_client, 'format_messages') as mock_format, \
             patch.object(app_controller.bedrock_client, 'converse') as mock_converse:
            
            mock_build.return_value = "Built prompt"
            mock_format.return_value = [{"role": "user", "content": "Built prompt"}]
            mock_converse.return_value = "Generated summary"
            
            # 调用方法 / Call method
            result = app_controller.process_case_summary("Test case", "test-model", "Custom prompt")
            
            # 验证使用了自定义提示词 / Verify custom prompt was used
            mock_build.assert_called_once()
            call_args = mock_build.call_args[1]
            assert call_args['system_prompt'] == 'Custom prompt'
            assert result == "Generated summary"
    
    def test_process_case_summary_fallback_to_config_prompt(self, app_controller, mock_dependencies):
        """测试案例总结回退到配置提示词 / Test case summary fallback to config prompt"""
        # 配置模拟：没有激活的提示词 / Configure mocks: no active prompt
        mock_dependencies['prompt'].get_active_prompt.return_value = None
        mock_dependencies['history'].load_history_files.return_value = []
        mock_dependencies['history'].process_history_content.return_value = ""
        mock_dependencies['history'].filter_relevant_history.return_value = ""
        
        with patch.object(app_controller.prompt_builder, 'build_prompt') as mock_build, \
             patch.object(app_controller.bedrock_client, 'format_messages') as mock_format, \
             patch.object(app_controller.bedrock_client, 'converse') as mock_converse:
            
            mock_build.return_value = "Built prompt"
            mock_format.return_value = [{"role": "user", "content": "Built prompt"}]
            mock_converse.return_value = "Generated summary"
            
            # 调用方法 / Call method
            result = app_controller.process_case_summary("Test case", "test-model")
            
            # 验证使用了配置文件中的提示词 / Verify config prompt was used
            mock_build.assert_called_once()
            call_args = mock_build.call_args[1]
            assert call_args['system_prompt'] == 'Default system prompt'
            assert result == "Generated summary"
    
    def test_exception_handling_in_prompt_methods(self, app_controller, mock_dependencies):
        """测试提示词方法中的异常处理 / Test exception handling in prompt methods"""
        # 配置模拟抛出异常 / Configure mock to raise exception
        mock_dependencies['prompt'].list_prompts.side_effect = Exception("Test error")
        mock_dependencies['prompt'].get_active_prompt.side_effect = Exception("Test error")
        mock_dependencies['prompt'].set_active_prompt.side_effect = Exception("Test error")
        mock_dependencies['prompt'].create_prompt.side_effect = Exception("Test error")
        mock_dependencies['prompt'].update_prompt.side_effect = Exception("Test error")
        mock_dependencies['prompt'].delete_prompt.side_effect = Exception("Test error")
        
        # 测试所有方法都能正确处理异常 / Test all methods handle exceptions correctly
        assert app_controller.get_available_prompts() == []
        assert app_controller.get_active_prompt() is None
        assert app_controller.set_active_prompt('test') is False
        assert app_controller.create_prompt('test', 'content') is False
        assert app_controller.update_prompt('test', 'content') is False
        assert app_controller.delete_prompt('test') is False