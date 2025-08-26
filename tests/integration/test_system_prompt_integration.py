"""
系统提示词管理集成测试 / System Prompt Management Integration Tests

测试配置管理、提示词管理、历史处理器的协同工作
Test coordination between configuration management, prompt management, and history processor
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from src.config.config_manager import ConfigManager
from src.processors.history_processor import HistoryProcessor
from src.services.system_prompt_manager import SystemPromptManager
from src.services.app_controller import AppController
from src.exceptions.system_prompt_exceptions import PromptValidationError, PromptNotFoundError


class TestSystemPromptIntegration:
    """系统提示词管理集成测试类 / System Prompt Management Integration Test Class"""
    
    @pytest.fixture
    def temp_workspace(self):
        """创建临时工作空间 / Create temporary workspace"""
        temp_dir = tempfile.mkdtemp()
        workspace = {
            'base_dir': Path(temp_dir),
            'config_file': Path(temp_dir) / 'config.yaml',
            'prompts_dir': Path(temp_dir) / 'system_prompts',
            'history_dir': Path(temp_dir) / 'history_references'
        }
        
        # 创建目录结构 / Create directory structure
        workspace['prompts_dir'].mkdir(parents=True)
        workspace['history_dir'].mkdir(parents=True)
        
        # 创建配置文件 / Create config file
        config_content = f"""
aws:
  auth_method: "profile"
  profile_name: "default"
  region: "us-east-1"

system_prompts:
  prompts_folder: "{workspace['prompts_dir']}"
  active_prompt: "default"

history_folder: "{workspace['history_dir']}"

app:
  title: "Test App"
  max_tokens: 4000
  temperature: 0.7
"""
        workspace['config_file'].write_text(config_content)
        
        yield workspace
        
        # 清理 / Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def config_manager(self, temp_workspace):
        """创建配置管理器 / Create config manager"""
        return ConfigManager(str(temp_workspace['config_file']))
    
    @pytest.fixture
    def history_processor(self, temp_workspace):
        """创建历史处理器 / Create history processor"""
        return HistoryProcessor(str(temp_workspace['history_dir']))
    
    @pytest.fixture
    def system_prompt_manager(self, config_manager, history_processor):
        """创建系统提示词管理器 / Create system prompt manager"""
        return SystemPromptManager(config_manager, history_processor)
    
    def test_config_and_prompt_manager_integration(self, config_manager, system_prompt_manager, temp_workspace):
        """测试配置管理与提示词管理的集成 / Test config management and prompt management integration"""
        # 验证配置正确加载 / Verify config loaded correctly
        app_config = config_manager.get_app_config()
        assert 'system_prompts' in app_config
        assert app_config['system_prompts']['active_prompt'] == 'default'
        
        # 验证提示词管理器使用了正确的路径 / Verify prompt manager uses correct paths
        assert str(temp_workspace['prompts_dir']) in system_prompt_manager.prompts_folder
        assert str(temp_workspace['history_dir']) in system_prompt_manager.history_base_folder
        
        # 验证默认提示词被创建 / Verify default prompt was created
        prompts = system_prompt_manager.list_prompts()
        assert len(prompts) >= 1
        assert any(p['name'] == 'default' for p in prompts)
    
    def test_prompt_creation_and_history_folder_integration(self, system_prompt_manager, temp_workspace):
        """测试提示词创建与历史文件夹的集成 / Test prompt creation and history folder integration"""
        # 创建新提示词 / Create new prompt
        success = system_prompt_manager.create_prompt("technical", "Technical analysis prompt")
        assert success is True
        
        # 验证提示词文件被创建 / Verify prompt file was created
        prompt_file = temp_workspace['prompts_dir'] / 'technical.md'
        assert prompt_file.exists()
        
        # 验证对应的历史文件夹被创建 / Verify corresponding history folder was created
        history_folder = temp_workspace['history_dir'] / 'technical'
        assert history_folder.exists()
        assert history_folder.is_dir()
        
        # 验证可以获取提示词内容 / Verify can get prompt content
        content = system_prompt_manager.get_prompt("technical")
        assert "Technical analysis prompt" in content
    
    def test_active_prompt_and_history_processor_integration(self, system_prompt_manager, history_processor, temp_workspace):
        """测试激活提示词与历史处理器的集成 / Test active prompt and history processor integration"""
        # 创建测试提示词和历史文件 / Create test prompt and history files
        system_prompt_manager.create_prompt("business", "Business case analysis")
        
        # 在对应的历史文件夹中创建测试文件 / Create test file in corresponding history folder
        business_history_dir = temp_workspace['history_dir'] / 'business'
        business_history_dir.mkdir(exist_ok=True)
        test_history_file = business_history_dir / 'test_case.txt'
        test_history_file.write_text("Test business case content")
        
        # 切换激活提示词 / Switch active prompt
        success = system_prompt_manager.set_active_prompt("business")
        assert success is True
        
        # 验证历史处理器的文件夹被更新 / Verify history processor folder was updated
        current_folder = history_processor.get_current_history_folder()
        assert 'business' in current_folder
        
        # 验证可以加载对应的历史文件 / Verify can load corresponding history files
        history_files = history_processor.load_history_files()
        assert len(history_files) >= 1
        assert any('test_case.txt' in f['name'] for f in history_files)
    
    def test_prompt_update_workflow(self, system_prompt_manager):
        """测试提示词更新工作流 / Test prompt update workflow"""
        # 创建提示词 / Create prompt
        system_prompt_manager.create_prompt("test_update", "Original content")
        
        # 更新提示词 / Update prompt
        success = system_prompt_manager.update_prompt("test_update", "Updated content")
        assert success is True
        
        # 验证内容被更新 / Verify content was updated
        content = system_prompt_manager.get_prompt("test_update")
        assert "Updated content" in content
        assert "Original content" not in content
    
    def test_prompt_deletion_workflow(self, system_prompt_manager):
        """测试提示词删除工作流 / Test prompt deletion workflow"""
        # 创建测试提示词 / Create test prompt
        system_prompt_manager.create_prompt("to_delete", "Content to delete")
        
        # 验证提示词存在 / Verify prompt exists
        content = system_prompt_manager.get_prompt("to_delete")
        assert content is not None
        
        # 删除提示词 / Delete prompt
        success = system_prompt_manager.delete_prompt("to_delete")
        assert success is True
        
        # 验证提示词不再存在 / Verify prompt no longer exists
        with pytest.raises(PromptNotFoundError):
            system_prompt_manager.get_prompt("to_delete")
    
    def test_active_prompt_fallback(self, system_prompt_manager):
        """测试激活提示词回退机制 / Test active prompt fallback mechanism"""
        # 创建测试提示词并设为激活 / Create test prompt and set as active
        system_prompt_manager.create_prompt("temp_active", "Temporary active prompt")
        system_prompt_manager.set_active_prompt("temp_active")
        
        # 验证激活提示词 / Verify active prompt
        active = system_prompt_manager.get_active_prompt()
        assert active['name'] == 'temp_active'
        
        # 删除激活的提示词 / Delete active prompt
        system_prompt_manager.delete_prompt("temp_active")
        
        # 验证回退到默认提示词 / Verify fallback to default prompt
        active = system_prompt_manager.get_active_prompt()
        assert active['name'] == 'default'
    
    def test_error_handling_integration(self, system_prompt_manager):
        """测试错误处理集成 / Test error handling integration"""
        # 测试创建重复提示词 / Test creating duplicate prompt
        system_prompt_manager.create_prompt("duplicate", "First content")
        
        # 第二次创建应该失败 / Second creation should fail
        success = system_prompt_manager.create_prompt("duplicate", "Second content")
        assert success is False
        
        # 测试无效名称 / Test invalid name
        with pytest.raises(PromptValidationError):
            system_prompt_manager.create_prompt("invalid<name>", "Content")
        
        # 测试获取不存在的提示词 / Test getting non-existent prompt
        with pytest.raises(PromptNotFoundError):
            system_prompt_manager.get_prompt("nonexistent")
    
    def test_list_prompts_with_metadata(self, system_prompt_manager, temp_workspace):
        """测试列出提示词及其元数据 / Test listing prompts with metadata"""
        # 创建多个提示词 / Create multiple prompts
        system_prompt_manager.create_prompt("prompt1", "Content 1")
        system_prompt_manager.create_prompt("prompt2", "Content 2")
        system_prompt_manager.set_active_prompt("prompt1")
        
        # 获取提示词列表 / Get prompt list
        prompts = system_prompt_manager.list_prompts()
        
        # 验证列表内容 / Verify list content
        assert len(prompts) >= 3  # default + prompt1 + prompt2
        
        # 验证元数据 / Verify metadata
        prompt1_info = next(p for p in prompts if p['name'] == 'prompt1')
        assert prompt1_info['is_active'] is True
        assert 'history_folder' in prompt1_info
        assert 'prompt1' in prompt1_info['history_folder']
        
        prompt2_info = next(p for p in prompts if p['name'] == 'prompt2')
        assert prompt2_info['is_active'] is False


class TestAppControllerIntegration:
    """应用控制器集成测试类 / App Controller Integration Test Class"""
    
    @pytest.fixture
    def mock_app_controller(self, temp_workspace):
        """创建模拟的应用控制器 / Create mock app controller"""
        with patch('src.services.app_controller.ConfigManager') as mock_config_class, \
             patch('src.services.app_controller.HistoryProcessor') as mock_history_class, \
             patch('src.services.app_controller.BedrockClient') as mock_bedrock_class, \
             patch('src.services.app_controller.ModelManager') as mock_model_class:
            
            # 配置ConfigManager mock / Configure ConfigManager mock
            mock_config = Mock()
            mock_config.load_config.return_value = None
            mock_config.validate_aws_credentials.return_value = True
            mock_config.get_history_folder.return_value = str(temp_workspace['history_dir'])
            mock_config.get_boto3_session.return_value = Mock()
            mock_config.config_data = {}
            mock_config.get_app_config.return_value = {
                'system_prompts': {
                    'prompts_folder': str(temp_workspace['prompts_dir']),
                    'active_prompt': 'default'
                },
                'history_folder': str(temp_workspace['history_dir']),
                'title': 'Test App',
                'max_tokens': 4000,
                'temperature': 0.7
            }
            mock_config_class.return_value = mock_config
            
            # 配置其他组件的mock / Configure other component mocks
            mock_history_class.return_value = Mock()
            mock_bedrock_class.return_value = Mock()
            mock_model_class.return_value = Mock()
            
            # 创建AppController实例 / Create AppController instance
            app_controller = AppController()
            
            yield app_controller
    
    def test_app_controller_prompt_management_integration(self, mock_app_controller):
        """测试应用控制器提示词管理集成 / Test app controller prompt management integration"""
        # 测试获取可用提示词 / Test getting available prompts
        prompts = mock_app_controller.get_available_prompts()
        assert isinstance(prompts, list)
        
        # 测试创建提示词 / Test creating prompt
        success = mock_app_controller.create_prompt("test_integration", "Integration test content")
        assert success is True
        
        # 测试获取激活提示词 / Test getting active prompt
        active = mock_app_controller.get_active_prompt()
        assert active is not None
        
        # 测试设置激活提示词 / Test setting active prompt
        success = mock_app_controller.set_active_prompt("test_integration")
        assert success is True
    
    def test_end_to_end_prompt_workflow(self, mock_app_controller):
        """测试端到端提示词工作流 / Test end-to-end prompt workflow"""
        # 1. 创建新提示词 / Create new prompt
        success = mock_app_controller.create_prompt("e2e_test", "End-to-end test prompt")
        assert success is True
        
        # 2. 设置为激活提示词 / Set as active prompt
        success = mock_app_controller.set_active_prompt("e2e_test")
        assert success is True
        
        # 3. 验证激活提示词 / Verify active prompt
        active = mock_app_controller.get_active_prompt()
        assert active['name'] == 'e2e_test'
        assert 'End-to-end test prompt' in active['content']
        
        # 4. 更新提示词内容 / Update prompt content
        success = mock_app_controller.update_prompt("e2e_test", "Updated e2e test prompt")
        assert success is True
        
        # 5. 验证更新后的内容 / Verify updated content
        active = mock_app_controller.get_active_prompt()
        assert 'Updated e2e test prompt' in active['content']
        
        # 6. 删除提示词 / Delete prompt
        success = mock_app_controller.delete_prompt("e2e_test")
        assert success is True
        
        # 7. 验证回退到默认提示词 / Verify fallback to default prompt
        active = mock_app_controller.get_active_prompt()
        assert active['name'] == 'default'