"""
用户界面响应性测试 / User Interface Responsiveness Tests

测试UI组件的响应性和用户体验。
Tests UI component responsiveness and user experience.
"""

import pytest
from unittest.mock import Mock, patch
from .test_base import E2ETestBase
from src.ui.prompt_ui_components import PromptUIComponents


class TestUIResponsiveness(E2ETestBase):
    """UI响应性测试类 / UI Responsiveness Test Class"""
    
    def setup_method(self):
        """设置测试环境 / Setup test environment"""
        super().setup_method()
        self.manager = self.create_system_prompt_manager()
        self.ui_components = PromptUIComponents(self.manager)
    
    def test_prompt_selector_creation(self):
        """测试提示词选择器创建 / Test prompt selector creation"""
        # 创建一些测试提示词 / Create some test prompts
        test_prompts = [
            ("technical", "技术分析"),
            ("business", "商业分析"),
            ("customer", "客户服务")
        ]
        
        for name, content in test_prompts:
            self.manager.create_prompt(name, content)
        
        # 创建选择器 / Create selector
        selector = self.ui_components.create_prompt_selector()
        
        # 验证选择器不为空 / Verify selector is not None
        assert selector is not None
        
        # 验证选择器有正确的配置 / Verify selector has correct configuration
        assert hasattr(selector, 'label')
        assert hasattr(selector, 'choices')
    
    def test_prompt_editor_creation(self):
        """测试提示词编辑器创建 / Test prompt editor creation"""
        editor = self.ui_components.create_prompt_editor()
        
        # 验证编辑器不为空 / Verify editor is not None
        assert editor is not None
        
        # 验证编辑器有正确的配置 / Verify editor has correct configuration
        assert hasattr(editor, 'label')
        assert hasattr(editor, 'lines')
    
    def test_management_panel_creation(self):
        """测试管理面板创建 / Test management panel creation"""
        panel = self.ui_components.create_prompt_management_panel()
        
        # 验证面板不为空 / Verify panel is not None
        assert panel is not None
    
    def test_new_prompt_dialog_creation(self):
        """测试新建提示词对话框创建 / Test new prompt dialog creation"""
        dialog = self.ui_components.create_new_prompt_dialog()
        
        # 验证对话框不为空 / Verify dialog is not None
        assert dialog is not None
    
    def test_prompt_selection_handling(self):
        """测试提示词选择处理 / Test prompt selection handling"""
        # 创建测试提示词 / Create test prompt
        prompt_name = "test_selection"
        prompt_content = "测试选择内容"
        self.manager.create_prompt(prompt_name, prompt_content)
        
        # 测试选择处理 / Test selection handling
        result = self.ui_components.handle_prompt_selection(prompt_name)
        
        # 验证返回结果 / Verify return result
        assert isinstance(result, tuple)
        assert len(result) == 2
        content, message = result
        assert content == prompt_content
        assert "切换" in message or "Switched" in message
    
    def test_prompt_creation_handling(self):
        """测试提示词创建处理 / Test prompt creation handling"""
        prompt_name = "ui_test_create"
        prompt_content = "UI测试创建内容"
        
        # 测试创建处理 / Test creation handling
        result = self.ui_components.handle_prompt_creation(prompt_name, prompt_content)
        
        # 验证返回结果 / Verify return result
        assert isinstance(result, tuple)
        message = result[0] if isinstance(result[0], str) else str(result[0])
        assert "成功" in message or "Success" in message
        
        # 验证提示词确实被创建 / Verify prompt was actually created
        content = self.manager.get_prompt(prompt_name)
        assert content == prompt_content
    
    def test_prompt_update_handling(self):
        """测试提示词更新处理 / Test prompt update handling"""
        # 先创建提示词 / First create prompt
        prompt_name = "ui_test_update"
        original_content = "原始内容"
        self.manager.create_prompt(prompt_name, original_content)
        
        # 测试更新处理 / Test update handling
        updated_content = "更新后的内容"
        result = self.ui_components.handle_prompt_update(prompt_name, updated_content)
        
        # 验证返回结果 / Verify return result
        assert isinstance(result, str)
        assert "成功" in result or "Success" in result
        
        # 验证提示词确实被更新 / Verify prompt was actually updated
        content = self.manager.get_prompt(prompt_name)
        assert content == updated_content
    
    def test_prompt_deletion_handling(self):
        """测试提示词删除处理 / Test prompt deletion handling"""
        # 先创建提示词 / First create prompt
        prompt_name = "ui_test_delete"
        prompt_content = "待删除内容"
        self.manager.create_prompt(prompt_name, prompt_content)
        
        # 测试删除处理 / Test deletion handling
        result = self.ui_components.handle_prompt_deletion(prompt_name)
        
        # 验证返回结果 / Verify return result
        assert isinstance(result, tuple)
        message = result[0] if isinstance(result[0], str) else str(result[0])
        assert "成功" in message or "Success" in message
        
        # 验证提示词确实被删除 / Verify prompt was actually deleted
        content = self.manager.get_prompt(prompt_name)
        assert content is None
    
    def test_error_handling_in_ui(self):
        """测试UI中的错误处理 / Test error handling in UI"""
        # 测试选择不存在的提示词 / Test selecting non-existent prompt
        result = self.ui_components.handle_prompt_selection("nonexistent")
        content, message = result
        assert content == ""
        assert "失败" in message or "Failed" in message
        
        # 测试创建无效名称的提示词 / Test creating prompt with invalid name
        result = self.ui_components.handle_prompt_creation("../invalid", "内容")
        message = result[0] if isinstance(result, tuple) else result
        assert "失败" in message or "Failed" in message or "错误" in message or "Error" in message
        
        # 测试更新不存在的提示词 / Test updating non-existent prompt
        result = self.ui_components.handle_prompt_update("nonexistent", "内容")
        assert "失败" in result or "Failed" in result or "错误" in result or "Error" in result
        
        # 测试删除默认提示词 / Test deleting default prompt
        result = self.ui_components.handle_prompt_deletion("default")
        message = result[0] if isinstance(result, tuple) else result
        assert "失败" in message or "Failed" in message or "错误" in message or "Error" in message
    
    def test_bilingual_messages(self):
        """测试双语消息 / Test bilingual messages"""
        # 创建提示词并测试成功消息 / Create prompt and test success message
        result = self.ui_components.handle_prompt_creation("bilingual_test", "测试内容")
        
        # 验证消息包含中英文 / Verify message contains both Chinese and English
        message = result[0] if isinstance(result, tuple) else result
        assert "成功" in message and "Success" in message
