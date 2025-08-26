"""
系统提示词管理器单元测试 / System Prompt Manager Unit Tests
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock
from src.services.system_prompt_manager import SystemPromptManager


class TestSystemPromptManager:
    """系统提示词管理器测试类 / System Prompt Manager Test Class"""
    
    def setup_method(self):
        """测试前设置 / Setup before each test"""
        # 创建临时目录 / Create temporary directories
        self.temp_dir = tempfile.mkdtemp()
        self.prompts_folder = Path(self.temp_dir) / "prompts"
        self.history_folder = Path(self.temp_dir) / "history"
        
        # 创建模拟的配置管理器 / Create mock configuration manager
        self.mock_config_manager = Mock()
        self.mock_config_manager.get_app_config.return_value = {
            'system_prompts': {
                'prompts_folder': str(self.prompts_folder),
                'active_prompt': 'default'
            },
            'history_folder': str(self.history_folder)
        }
        
        # 创建模拟的历史处理器 / Create mock history processor
        self.mock_history_processor = Mock()
        self.mock_history_processor.set_history_folder = MagicMock()
        
        # 初始化管理器 / Initialize manager
        self.manager = SystemPromptManager(
            self.mock_config_manager,
            self.mock_history_processor
        )
    
    def teardown_method(self):
        """测试后清理 / Cleanup after each test"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_init_creates_default_prompt(self):
        """测试初始化时创建默认提示词 / Test default prompt creation during initialization"""
        # 验证默认提示词存在 / Verify default prompt exists
        default_content = self.manager.get_prompt('default')
        assert default_content is not None
        assert '专业的案例总结助手' in default_content
    
    def test_create_prompt_success(self):
        """测试成功创建提示词 / Test successful prompt creation"""
        name = "test_prompt"
        content = "这是一个测试提示词"
        
        result = self.manager.create_prompt(name, content)
        assert result is True
        
        # 验证提示词被创建 / Verify prompt was created
        loaded_content = self.manager.get_prompt(name)
        assert loaded_content == content
    
    def test_create_prompt_invalid_name(self):
        """测试使用无效名称创建提示词 / Test creating prompt with invalid name"""
        result = self.manager.create_prompt("", "content")
        assert result is False
        
        result = self.manager.create_prompt("test<>prompt", "content")
        assert result is False
    
    def test_create_prompt_already_exists(self):
        """测试创建已存在的提示词 / Test creating already existing prompt"""
        name = "test_prompt"
        content = "原始内容"
        
        # 先创建提示词 / Create prompt first
        assert self.manager.create_prompt(name, content)
        
        # 尝试再次创建相同名称的提示词 / Try to create prompt with same name again
        result = self.manager.create_prompt(name, "新内容")
        assert result is False
        
        # 验证内容没有改变 / Verify content hasn't changed
        loaded_content = self.manager.get_prompt(name)
        assert loaded_content == content
    
    def test_get_prompt_exists(self):
        """测试获取存在的提示词 / Test getting existing prompt"""
        name = "test_prompt"
        content = "测试内容"
        
        self.manager.create_prompt(name, content)
        result = self.manager.get_prompt(name)
        assert result == content
    
    def test_get_prompt_not_exists(self):
        """测试获取不存在的提示词 / Test getting non-existent prompt"""
        result = self.manager.get_prompt("nonexistent")
        assert result is None
    
    def test_update_prompt_success(self):
        """测试成功更新提示词 / Test successful prompt update"""
        name = "test_prompt"
        original_content = "原始内容"
        new_content = "更新后的内容"
        
        # 先创建提示词 / Create prompt first
        self.manager.create_prompt(name, original_content)
        
        # 更新提示词 / Update prompt
        result = self.manager.update_prompt(name, new_content)
        assert result is True
        
        # 验证内容已更新 / Verify content was updated
        loaded_content = self.manager.get_prompt(name)
        assert loaded_content == new_content
    
    def test_update_prompt_not_exists(self):
        """测试更新不存在的提示词 / Test updating non-existent prompt"""
        result = self.manager.update_prompt("nonexistent", "content")
        assert result is False
    
    def test_delete_prompt_success(self):
        """测试成功删除提示词 / Test successful prompt deletion"""
        name = "test_prompt"
        content = "测试内容"
        
        # 先创建提示词 / Create prompt first
        self.manager.create_prompt(name, content)
        assert self.manager.get_prompt(name) is not None
        
        # 删除提示词 / Delete prompt
        result = self.manager.delete_prompt(name)
        assert result is True
        
        # 验证提示词已删除 / Verify prompt was deleted
        assert self.manager.get_prompt(name) is None
    
    def test_delete_default_prompt_fails(self):
        """测试删除默认提示词失败 / Test deleting default prompt fails"""
        result = self.manager.delete_prompt("default")
        assert result is False
        
        # 验证默认提示词仍然存在 / Verify default prompt still exists
        assert self.manager.get_prompt("default") is not None
    
    def test_delete_active_prompt_switches_to_default(self):
        """测试删除激活提示词时切换到默认提示词 / Test switching to default when deleting active prompt"""
        name = "test_prompt"
        content = "测试内容"
        
        # 创建并设置为激活提示词 / Create and set as active prompt
        self.manager.create_prompt(name, content)
        self.manager.set_active_prompt(name)
        assert self.manager.active_prompt == name
        
        # 删除激活的提示词 / Delete active prompt
        result = self.manager.delete_prompt(name)
        assert result is True
        
        # 验证激活提示词切换到默认 / Verify active prompt switched to default
        assert self.manager.active_prompt == "default"
    
    def test_list_prompts(self):
        """测试列出提示词 / Test listing prompts"""
        # 初始状态应该只有默认提示词 / Initial state should only have default prompt
        prompts = self.manager.list_prompts()
        assert len(prompts) == 1
        assert prompts[0]['name'] == 'default'
        assert prompts[0]['is_active'] is True
        
        # 创建更多提示词 / Create more prompts
        self.manager.create_prompt("prompt1", "内容1")
        self.manager.create_prompt("prompt2", "内容2")
        
        # 验证列表 / Verify list
        prompts = self.manager.list_prompts()
        assert len(prompts) == 3
        
        prompt_names = [p['name'] for p in prompts]
        assert 'default' in prompt_names
        assert 'prompt1' in prompt_names
        assert 'prompt2' in prompt_names
    
    def test_set_active_prompt_success(self):
        """测试成功设置激活提示词 / Test successful active prompt setting"""
        name = "test_prompt"
        content = "测试内容"
        
        # 创建提示词 / Create prompt
        self.manager.create_prompt(name, content)
        
        # 设置为激活提示词 / Set as active prompt
        result = self.manager.set_active_prompt(name)
        assert result is True
        assert self.manager.active_prompt == name
        
        # 验证历史处理器的文件夹被切换 / Verify history processor folder was switched
        expected_folder = self.manager.get_prompt_history_folder(name)
        self.mock_history_processor.set_history_folder.assert_called_with(expected_folder)
    
    def test_set_active_prompt_not_exists(self):
        """测试设置不存在的激活提示词 / Test setting non-existent active prompt"""
        result = self.manager.set_active_prompt("nonexistent")
        assert result is False
        assert self.manager.active_prompt == "default"  # Should remain default
    
    def test_get_active_prompt(self):
        """测试获取激活提示词信息 / Test getting active prompt information"""
        # 默认情况 / Default case
        active_info = self.manager.get_active_prompt()
        assert active_info is not None
        assert active_info['name'] == 'default'
        assert '专业的案例总结助手' in active_info['content']
        
        # 切换到其他提示词 / Switch to other prompt
        name = "test_prompt"
        content = "测试内容"
        self.manager.create_prompt(name, content)
        self.manager.set_active_prompt(name)
        
        active_info = self.manager.get_active_prompt()
        assert active_info['name'] == name
        assert active_info['content'] == content
    
    def test_get_prompt_history_folder(self):
        """测试获取提示词历史文件夹路径 / Test getting prompt history folder path"""
        name = "test_prompt"
        folder_path = self.manager.get_prompt_history_folder(name)
        
        expected_path = str(Path(self.history_folder) / name)
        assert folder_path == expected_path
    
    def test_get_prompt_history_folder_with_special_chars(self):
        """测试包含特殊字符的提示词名称的历史文件夹路径 / Test history folder path for prompt names with special characters"""
        name = "test prompt with spaces"
        folder_path = self.manager.get_prompt_history_folder(name)
        
        # 应该被清理为合法的文件夹名称 / Should be sanitized to legal folder name
        expected_path = str(Path(self.history_folder) / "test_prompt_with_spaces")
        assert folder_path == expected_path
    
    def test_caching_mechanism(self):
        """测试缓存机制 / Test caching mechanism"""
        name = "cache_test_prompt"
        content = "缓存测试内容"
        
        # 创建提示词 / Create prompt
        assert self.manager.create_prompt(name, content)
        
        # 第一次读取 / First read
        result1 = self.manager.get_prompt(name)
        assert result1 == content
        
        # 验证缓存中有数据 / Verify cache has data
        assert name in self.manager._content_cache
        
        # 第二次读取应该从缓存获取 / Second read should be from cache
        result2 = self.manager.get_prompt(name)
        assert result2 == content
        assert result1 == result2
    
    def test_cache_invalidation_on_update(self):
        """测试更新时的缓存失效 / Test cache invalidation on update"""
        name = "update_cache_test"
        original_content = "原始内容"
        updated_content = "更新内容"
        
        # 创建并读取提示词 / Create and read prompt
        assert self.manager.create_prompt(name, original_content)
        assert self.manager.get_prompt(name) == original_content
        
        # 验证缓存中有数据 / Verify cache has data
        assert name in self.manager._content_cache
        
        # 更新提示词 / Update prompt
        assert self.manager.update_prompt(name, updated_content)
        
        # 验证缓存已清除该项 / Verify cache item was cleared
        assert name not in self.manager._content_cache
        
        # 读取更新后的内容 / Read updated content
        assert self.manager.get_prompt(name) == updated_content
    
    def test_cache_invalidation_on_delete(self):
        """测试删除时的缓存失效 / Test cache invalidation on delete"""
        name = "delete_cache_test"
        content = "删除测试内容"
        
        # 创建并读取提示词 / Create and read prompt
        assert self.manager.create_prompt(name, content)
        assert self.manager.get_prompt(name) == content
        
        # 验证缓存中有数据 / Verify cache has data
        assert name in self.manager._content_cache
        
        # 删除提示词 / Delete prompt
        assert self.manager.delete_prompt(name)
        
        # 验证缓存已清除该项 / Verify cache item was cleared
        assert name not in self.manager._content_cache
        
        # 验证提示词已删除 / Verify prompt was deleted
        assert self.manager.get_prompt(name) is None
    
    def test_list_prompts_caching(self):
        """测试列表缓存 / Test list caching"""
        # 第一次调用 / First call
        prompts1 = self.manager.list_prompts()
        
        # 验证列表缓存中有数据 / Verify list cache has data
        assert 'prompt_list' in self.manager._list_cache
        
        # 第二次调用应该从缓存获取 / Second call should be from cache
        prompts2 = self.manager.list_prompts()
        assert prompts1 == prompts2
        
        # 创建新提示词应该清除列表缓存 / Creating new prompt should clear list cache
        assert self.manager.create_prompt("new_prompt", "新内容")
        assert 'prompt_list' not in self.manager._list_cache