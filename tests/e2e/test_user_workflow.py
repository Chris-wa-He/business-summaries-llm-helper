"""
用户工作流端到端测试 / User Workflow End-to-End Tests

测试完整的用户工作流程，包括提示词管理、历史文件处理等。
Tests complete user workflows including prompt management, history file processing, etc.
"""

import pytest
from .test_base import E2ETestBase


class TestUserWorkflow(E2ETestBase):
    """用户工作流测试类 / User Workflow Test Class"""
    
    def test_complete_prompt_management_workflow(self):
        """测试完整的提示词管理工作流 / Test complete prompt management workflow"""
        manager = self.create_system_prompt_manager()
        
        # 1. 验证默认提示词存在 / Verify default prompt exists
        prompts = manager.list_prompts()
        assert len(prompts) >= 1
        default_prompt = next((p for p in prompts if p['name'] == 'default'), None)
        assert default_prompt is not None
        assert default_prompt['is_active'] is True
        
        # 2. 创建新提示词 / Create new prompt
        new_prompt_name = "technical_analysis"
        new_prompt_content = "你是一个技术分析专家，专门分析技术问题和解决方案。"
        
        success = manager.create_prompt(new_prompt_name, new_prompt_content)
        assert success is True
        
        # 3. 验证新提示词已创建 / Verify new prompt was created
        content = manager.get_prompt(new_prompt_name)
        assert content == new_prompt_content
        
        # 4. 切换到新提示词 / Switch to new prompt
        success = manager.set_active_prompt(new_prompt_name)
        assert success is True
        
        active_prompt = manager.get_active_prompt()
        assert active_prompt['name'] == new_prompt_name
        assert active_prompt['content'] == new_prompt_content
        
        # 5. 更新提示词内容 / Update prompt content
        updated_content = "你是一个高级技术分析专家，专门分析复杂的技术问题。"
        success = manager.update_prompt(new_prompt_name, updated_content)
        assert success is True
        
        # 6. 验证更新成功 / Verify update success
        content = manager.get_prompt(new_prompt_name)
        assert content == updated_content
        
        # 7. 列出所有提示词 / List all prompts
        prompts = manager.list_prompts()
        assert len(prompts) >= 2
        prompt_names = [p['name'] for p in prompts]
        assert 'default' in prompt_names
        assert new_prompt_name in prompt_names
        
        # 8. 删除提示词 / Delete prompt
        success = manager.delete_prompt(new_prompt_name)
        assert success is True
        
        # 9. 验证删除成功且切换回默认提示词 / Verify deletion and switch to default
        content = manager.get_prompt(new_prompt_name)
        assert content is None
        
        active_prompt = manager.get_active_prompt()
        assert active_prompt['name'] == 'default'
    
    def test_prompt_history_folder_integration(self):
        """测试提示词与历史文件夹的集成 / Test prompt and history folder integration"""
        manager = self.create_system_prompt_manager()
        
        # 1. 创建提示词 / Create prompt
        prompt_name = "business_analysis"
        prompt_content = "你是一个商业分析师。"
        
        success = manager.create_prompt(prompt_name, prompt_content)
        assert success is True
        
        # 2. 验证历史文件夹路径 / Verify history folder path
        history_folder = manager.get_prompt_history_folder(prompt_name)
        expected_path = str(self.history_dir / prompt_name)
        assert history_folder == expected_path
        
        # 3. 切换提示词应该调用历史处理器 / Switching prompt should call history processor
        success = manager.set_active_prompt(prompt_name)
        assert success is True
        
        # 验证历史处理器被调用 / Verify history processor was called
        manager.history_processor.set_history_folder.assert_called_with(history_folder)
    
    def test_caching_across_operations(self):
        """测试跨操作的缓存行为 / Test caching behavior across operations"""
        manager = self.create_system_prompt_manager()
        
        # 1. 创建提示词 / Create prompt
        prompt_name = "cache_test"
        prompt_content = "缓存测试内容"
        
        success = manager.create_prompt(prompt_name, prompt_content)
        assert success is True
        
        # 2. 第一次读取 / First read
        content1 = manager.get_prompt(prompt_name)
        assert content1 == prompt_content
        
        # 3. 第二次读取应该使用缓存 / Second read should use cache
        content2 = manager.get_prompt(prompt_name)
        assert content2 == content1
        
        # 4. 更新后缓存应该失效 / Cache should be invalidated after update
        new_content = "更新后的内容"
        success = manager.update_prompt(prompt_name, new_content)
        assert success is True
        
        # 5. 读取应该返回新内容 / Read should return new content
        content3 = manager.get_prompt(prompt_name)
        assert content3 == new_content
        assert content3 != content1
    
    def test_error_handling_workflow(self):
        """测试错误处理工作流 / Test error handling workflow"""
        manager = self.create_system_prompt_manager()
        
        # 1. 尝试创建无效名称的提示词 / Try to create prompt with invalid name
        success = manager.create_prompt("../invalid", "内容")
        assert success is False
        
        # 2. 尝试创建空内容的提示词 / Try to create prompt with empty content
        success = manager.create_prompt("valid_name", "")
        assert success is False
        
        # 3. 尝试获取不存在的提示词 / Try to get non-existent prompt
        content = manager.get_prompt("nonexistent")
        assert content is None
        
        # 4. 尝试更新不存在的提示词 / Try to update non-existent prompt
        success = manager.update_prompt("nonexistent", "内容")
        assert success is False
        
        # 5. 尝试删除默认提示词 / Try to delete default prompt
        success = manager.delete_prompt("default")
        assert success is False
        
        # 6. 尝试设置不存在的激活提示词 / Try to set non-existent active prompt
        success = manager.set_active_prompt("nonexistent")
        assert success is False
