"""
应用状态恢复测试 / Application State Recovery Tests

测试应用重启后的状态恢复功能。
Tests application state recovery functionality after restart.
"""

import pytest
from .test_base import E2ETestBase


class TestStateRecovery(E2ETestBase):
    """状态恢复测试类 / State Recovery Test Class"""
    
    def test_prompt_persistence_across_restarts(self):
        """测试提示词在重启后的持久化 / Test prompt persistence across restarts"""
        # 第一次启动 - 创建提示词 / First startup - create prompts
        manager1 = self.create_system_prompt_manager()
        
        # 创建多个提示词 / Create multiple prompts
        prompts_data = [
            ("technical", "技术分析专家提示词"),
            ("business", "商业分析专家提示词"),
            ("customer_service", "客服专家提示词")
        ]
        
        for name, content in prompts_data:
            success = manager1.create_prompt(name, content)
            assert success is True
        
        # 设置激活提示词 / Set active prompt
        success = manager1.set_active_prompt("business")
        assert success is True
        
        # 模拟应用重启 - 创建新的管理器实例 / Simulate restart - create new manager instance
        manager2 = self.create_system_prompt_manager()
        
        # 验证所有提示词都存在 / Verify all prompts exist
        prompts = manager2.list_prompts()
        prompt_names = [p['name'] for p in prompts]
        
        assert 'default' in prompt_names
        for name, _ in prompts_data:
            assert name in prompt_names
        
        # 验证提示词内容 / Verify prompt content
        for name, expected_content in prompts_data:
            content = manager2.get_prompt(name)
            assert content == expected_content
        
        # 验证激活提示词状态 / Verify active prompt state
        # 注意：当前实现中激活提示词状态不会持久化，重启后会回到默认状态
        # Note: In current implementation, active prompt state is not persisted, returns to default after restart
        active_prompt = manager2.get_active_prompt()
        assert active_prompt['name'] == 'default'  # 重启后应该回到默认状态 / Should return to default after restart
    
    def test_cache_reset_after_restart(self):
        """测试重启后缓存重置 / Test cache reset after restart"""
        # 第一次启动 / First startup
        manager1 = self.create_system_prompt_manager()
        
        # 创建提示词并读取（填充缓存）/ Create prompt and read (populate cache)
        prompt_name = "cache_test"
        prompt_content = "缓存测试内容"
        
        success = manager1.create_prompt(prompt_name, prompt_content)
        assert success is True
        
        content = manager1.get_prompt(prompt_name)
        assert content == prompt_content
        
        # 调用list_prompts来填充列表缓存 / Call list_prompts to populate list cache
        prompts = manager1.list_prompts()
        
        # 验证缓存中有数据 / Verify cache has data
        assert prompt_name in manager1._content_cache
        assert 'prompt_list' in manager1._list_cache
        
        # 模拟重启 / Simulate restart
        manager2 = self.create_system_prompt_manager()
        
        # 验证新实例的缓存是空的 / Verify new instance has empty cache
        assert len(manager2._content_cache) == 0
        assert len(manager2._list_cache) == 0
        
        # 但数据仍然可以正确读取 / But data can still be read correctly
        content = manager2.get_prompt(prompt_name)
        assert content == prompt_content
    
    def test_history_folder_association_persistence(self):
        """测试历史文件夹关联的持久化 / Test history folder association persistence"""
        # 第一次启动 / First startup
        manager1 = self.create_system_prompt_manager()
        
        # 创建提示词 / Create prompt
        prompt_name = "folder_test"
        prompt_content = "文件夹测试内容"
        
        success = manager1.create_prompt(prompt_name, prompt_content)
        assert success is True
        
        # 获取历史文件夹路径 / Get history folder path
        folder_path1 = manager1.get_prompt_history_folder(prompt_name)
        
        # 模拟重启 / Simulate restart
        manager2 = self.create_system_prompt_manager()
        
        # 验证历史文件夹路径一致 / Verify history folder path consistency
        folder_path2 = manager2.get_prompt_history_folder(prompt_name)
        assert folder_path1 == folder_path2
        
        # 验证路径格式正确 / Verify path format is correct
        expected_path = str(self.history_dir / prompt_name)
        assert folder_path2 == expected_path
    
    def test_configuration_consistency(self):
        """测试配置一致性 / Test configuration consistency"""
        # 第一次启动 / First startup
        manager1 = self.create_system_prompt_manager()
        
        # 获取配置信息 / Get configuration info
        config1 = manager1.config_manager.get_app_config()
        
        # 模拟重启 / Simulate restart
        manager2 = self.create_system_prompt_manager()
        
        # 验证配置一致 / Verify configuration consistency
        config2 = manager2.config_manager.get_app_config()
        
        assert config1['system_prompts']['prompts_folder'] == config2['system_prompts']['prompts_folder']
        assert config1['history_folder'] == config2['history_folder']
