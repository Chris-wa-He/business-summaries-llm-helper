"""
增强系统提示词管理器单元测试 / Enhanced System Prompt Manager Unit Tests
"""

import pytest
import tempfile
import shutil
from unittest.mock import Mock, AsyncMock, patch

from src.services.enhanced_system_prompt_manager import EnhancedSystemPromptManager


class TestEnhancedSystemPromptManager:
    """增强系统提示词管理器测试类 / Enhanced System Prompt Manager Test Class"""
    
    def setup_method(self):
        """测试前设置 / Setup before each test"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock dependencies with proper configuration
        self.mock_config_manager = Mock()
        self.mock_config_manager.get_app_config.return_value = {
            'system_prompts': {
                'prompts_folder': self.temp_dir,
                'active_prompt': 'default'
            }
        }
        
        self.mock_history_processor = Mock()
        self.mock_bedrock_client = Mock()
        
        # Patch the SystemPromptManager to avoid real initialization
        with patch('src.services.enhanced_system_prompt_manager.SystemPromptManager') as mock_base_manager:
            with patch('src.services.enhanced_system_prompt_manager.PersonalizedPromptManager') as mock_personalized_manager:
                with patch('src.services.enhanced_system_prompt_manager.LLMBasedPreferenceLearning') as mock_llm_learning:
                    self.manager = EnhancedSystemPromptManager(
                        self.mock_config_manager,
                        self.mock_history_processor,
                        self.mock_bedrock_client
                    )
                    
                    # Store mocked instances for testing
                    self.manager.base_manager = mock_base_manager.return_value
                    self.manager.personalized_manager = mock_personalized_manager.return_value
                    self.manager.llm_learning = mock_llm_learning.return_value
        
    def teardown_method(self):
        """测试后清理 / Cleanup after each test"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """测试初始化 / Test initialization"""
        assert self.manager.base_manager is not None
        assert self.manager.personalized_manager is not None
        assert self.manager.llm_learning is not None
    
    def test_get_effective_prompt_personalized_exists(self):
        """测试获取有效提示词 - 个性化版本存在 / Test get effective prompt - personalized version exists"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        personalized_content = "Personalized prompt content"
        
        # Mock personalized prompt exists
        self.manager.personalized_manager.load_personalized_prompt = Mock(
            return_value=personalized_content
        )
        
        result = self.manager.get_effective_prompt(user_id, prompt_name)
        
        assert result == personalized_content
        self.manager.personalized_manager.load_personalized_prompt.assert_called_once_with(
            user_id, prompt_name
        )
    
    def test_get_effective_prompt_fallback_to_base(self):
        """测试获取有效提示词 - 回退到基础提示词 / Test get effective prompt - fallback to base"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        base_content = "Base prompt content"
        
        # Mock no personalized prompt, but base exists
        self.manager.personalized_manager.load_personalized_prompt = Mock(return_value=None)
        self.manager.base_manager.get_prompt = Mock(return_value=base_content)
        
        result = self.manager.get_effective_prompt(user_id, prompt_name)
        
        assert result == base_content
        self.manager.base_manager.get_prompt.assert_called_once_with(prompt_name)
    
    def test_get_effective_prompt_fallback_to_default(self):
        """测试获取有效提示词 - 回退到默认提示词 / Test get effective prompt - fallback to default"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        default_content = "Default prompt content"
        
        # Mock no personalized and no base prompt
        self.manager.personalized_manager.load_personalized_prompt = Mock(return_value=None)
        self.manager.base_manager.get_prompt = Mock(return_value=None)
        self.manager.base_manager.get_active_prompt = Mock(
            return_value={'content': default_content}
        )
        
        result = self.manager.get_effective_prompt(user_id, prompt_name)
        
        assert result == default_content
    
    def test_get_effective_prompt_error_handling(self):
        """测试获取有效提示词 - 错误处理 / Test get effective prompt - error handling"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        fallback_content = "Fallback content"
        
        # Mock exception in personalized manager
        self.manager.personalized_manager.load_personalized_prompt = Mock(
            side_effect=Exception("Test error")
        )
        self.manager.base_manager.get_prompt = Mock(return_value=fallback_content)
        
        result = self.manager.get_effective_prompt(user_id, prompt_name)
        
        assert result == fallback_content
    
    @pytest.mark.asyncio
    async def test_update_preference_from_feedback_success(self):
        """测试从反馈更新偏好 - 成功 / Test update preference from feedback - success"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        feedback_data = {"satisfaction": 0.8, "modification_type": "style"}
        
        # Mock successful LLM learning
        self.manager.llm_learning.analyze_and_update_preference = AsyncMock(
            return_value={'success': True}
        )
        
        result = await self.manager.update_preference_from_feedback(
            user_id, prompt_name, feedback_data
        )
        
        assert result is True
        self.manager.llm_learning.analyze_and_update_preference.assert_called_once_with(
            user_id, prompt_name, feedback_data
        )
    
    @pytest.mark.asyncio
    async def test_update_preference_from_feedback_failure(self):
        """测试从反馈更新偏好 - 失败 / Test update preference from feedback - failure"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        feedback_data = {"satisfaction": 0.8}
        
        # Mock failed LLM learning
        self.manager.llm_learning.analyze_and_update_preference = AsyncMock(
            return_value={'success': False, 'error': 'Test error'}
        )
        
        result = await self.manager.update_preference_from_feedback(
            user_id, prompt_name, feedback_data
        )
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_update_preference_from_feedback_exception(self):
        """测试从反馈更新偏好 - 异常处理 / Test update preference from feedback - exception handling"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        feedback_data = {"satisfaction": 0.8}
        
        # Mock exception in LLM learning
        self.manager.llm_learning.analyze_and_update_preference = AsyncMock(
            side_effect=Exception("Test error")
        )
        
        result = await self.manager.update_preference_from_feedback(
            user_id, prompt_name, feedback_data
        )
        
        assert result is False
    
    def test_get_user_prompt_versions(self):
        """测试获取用户prompt版本 / Test get user prompt versions"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        versions = [{"version": "v1", "created_at": "2024-01-01"}]
        
        self.manager.personalized_manager.get_prompt_versions = Mock(return_value=versions)
        
        result = self.manager.get_user_prompt_versions(user_id, prompt_name)
        
        assert result == versions
        self.manager.personalized_manager.get_prompt_versions.assert_called_once_with(
            user_id, prompt_name
        )
    
    def test_activate_user_prompt_version(self):
        """测试激活用户prompt版本 / Test activate user prompt version"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        version = "v1"
        
        self.manager.personalized_manager.activate_prompt_version = Mock(return_value=True)
        
        result = self.manager.activate_user_prompt_version(user_id, prompt_name, version)
        
        assert result is True
        self.manager.personalized_manager.activate_prompt_version.assert_called_once_with(
            user_id, prompt_name, version
        )
    
    def test_has_personalized_prompt_true(self):
        """测试检查个性化prompt存在 / Test check personalized prompt exists"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        
        self.manager.personalized_manager.get_prompt_versions = Mock(
            return_value=[{"version": "v1"}]
        )
        
        result = self.manager.has_personalized_prompt(user_id, prompt_name)
        
        assert result is True
    
    def test_has_personalized_prompt_false(self):
        """测试检查个性化prompt不存在 / Test check personalized prompt does not exist"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        
        self.manager.personalized_manager.get_prompt_versions = Mock(return_value=[])
        
        result = self.manager.has_personalized_prompt(user_id, prompt_name)
        
        assert result is False
    
    def test_has_personalized_prompt_exception(self):
        """测试检查个性化prompt异常处理 / Test check personalized prompt exception handling"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        
        self.manager.personalized_manager.get_prompt_versions = Mock(
            side_effect=Exception("Test error")
        )
        
        result = self.manager.has_personalized_prompt(user_id, prompt_name)
        
        assert result is False
    
    def test_delegate_methods(self):
        """测试代理方法 / Test delegate methods"""
        # Test create_prompt
        self.manager.base_manager.create_prompt = Mock(return_value=True)
        result = self.manager.create_prompt("test", "content")
        assert result is True
        
        # Test get_prompt
        self.manager.base_manager.get_prompt = Mock(return_value="content")
        result = self.manager.get_prompt("test")
        assert result == "content"
        
        # Test update_prompt
        self.manager.base_manager.update_prompt = Mock(return_value=True)
        result = self.manager.update_prompt("test", "new_content")
        assert result is True
        
        # Test delete_prompt
        self.manager.base_manager.delete_prompt = Mock(return_value=True)
        result = self.manager.delete_prompt("test")
        assert result is True
        
        # Test list_prompts
        self.manager.base_manager.list_prompts = Mock(return_value=["prompt1", "prompt2"])
        result = self.manager.list_prompts()
        assert result == ["prompt1", "prompt2"]
        
        # Test set_active_prompt
        self.manager.base_manager.set_active_prompt = Mock(return_value=True)
        result = self.manager.set_active_prompt("test")
        assert result is True
        
        # Test get_active_prompt
        self.manager.base_manager.get_active_prompt = Mock(
            return_value={"name": "test", "content": "content"}
        )
        result = self.manager.get_active_prompt()
        assert result == {"name": "test", "content": "content"}
        
        # Test get_prompt_history_folder
        self.manager.base_manager.get_prompt_history_folder = Mock(return_value="/path/to/folder")
        result = self.manager.get_prompt_history_folder("test")
        assert result == "/path/to/folder"