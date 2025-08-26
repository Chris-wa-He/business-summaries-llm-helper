"""
系统提示词UI组件单元测试 / System Prompt UI Components Unit Tests
"""

import pytest
from unittest.mock import Mock, patch
import gradio as gr

from src.ui.prompt_ui_components import PromptUIComponents


class TestPromptUIComponents:
    """系统提示词UI组件测试类 / System Prompt UI Components Test Class"""
    
    @pytest.fixture
    def mock_prompt_manager(self):
        """创建模拟的提示词管理器 / Create mock prompt manager"""
        manager = Mock()
        manager.list_prompts.return_value = [
            {'name': 'default', 'content': 'Default prompt content'},
            {'name': 'technical', 'content': 'Technical prompt content'}
        ]
        manager.get_active_prompt.return_value = {'name': 'default', 'content': 'Default prompt content'}
        manager.get_prompt.return_value = 'Default prompt content'
        manager.create_prompt.return_value = True
        manager.update_prompt.return_value = True
        manager.delete_prompt.return_value = True
        manager.set_active_prompt.return_value = True
        return manager
    
    @pytest.fixture
    def ui_components(self, mock_prompt_manager):
        """创建UI组件实例 / Create UI components instance"""
        return PromptUIComponents(mock_prompt_manager)
    
    def test_init(self, mock_prompt_manager):
        """测试初始化 / Test initialization"""
        ui_components = PromptUIComponents(mock_prompt_manager)
        assert ui_components.prompt_manager == mock_prompt_manager
        assert ui_components.logger is not None
    
    @patch('gradio.Dropdown')
    def test_create_prompt_selector(self, mock_dropdown, ui_components, mock_prompt_manager):
        """测试创建提示词选择器 / Test create prompt selector"""
        # 配置模拟返回值 / Configure mock return values
        mock_prompt_manager.list_prompts.return_value = [
            {'name': 'default', 'content': 'Default content'},
            {'name': 'technical', 'content': 'Technical content'}
        ]
        mock_prompt_manager.get_active_prompt.return_value = {'name': 'default', 'content': 'Default content'}
        
        # 调用方法 / Call method
        result = ui_components.create_prompt_selector()
        
        # 验证调用 / Verify calls
        mock_prompt_manager.list_prompts.assert_called_once()
        mock_prompt_manager.get_active_prompt.assert_called_once()
        mock_dropdown.assert_called_once()
        
        # 验证参数 / Verify parameters
        call_args = mock_dropdown.call_args
        assert call_args[1]['choices'] == ['default', 'technical']
        assert call_args[1]['value'] == 'default'
        assert call_args[1]['interactive'] is True
    
    @patch('gradio.Textbox')
    def test_create_prompt_editor(self, mock_textbox, ui_components, mock_prompt_manager):
        """测试创建提示词编辑器 / Test create prompt editor"""
        # 配置模拟返回值 / Configure mock return values
        mock_prompt_manager.get_active_prompt.return_value = {'name': 'default', 'content': 'Test content'}
        
        # 调用方法 / Call method
        result = ui_components.create_prompt_editor()
        
        # 验证调用 / Verify calls
        mock_prompt_manager.get_active_prompt.assert_called_once()
        mock_textbox.assert_called_once()
        
        # 验证参数 / Verify parameters
        call_args = mock_textbox.call_args
        assert call_args[1]['value'] == 'Test content'
        assert call_args[1]['interactive'] is True
    
    def test_handle_prompt_selection_success(self, ui_components, mock_prompt_manager):
        """测试成功处理提示词选择 / Test successful prompt selection handling"""
        # 配置模拟返回值 / Configure mock return values
        mock_prompt_manager.set_active_prompt.return_value = True
        mock_prompt_manager.get_prompt.return_value = 'Selected prompt content'
        
        # 调用方法 / Call method
        content, status = ui_components.handle_prompt_selection('technical')
        
        # 验证结果 / Verify results
        assert content == 'Selected prompt content'
        assert 'technical' in status
        assert '已切换到提示词' in status or 'Switched to prompt' in status
        
        # 验证调用 / Verify calls
        mock_prompt_manager.set_active_prompt.assert_called_once_with('technical')
        mock_prompt_manager.get_prompt.assert_called_once_with('technical')
    
    def test_handle_prompt_selection_empty_name(self, ui_components):
        """测试处理空提示词名称 / Test handling empty prompt name"""
        content, status = ui_components.handle_prompt_selection('')
        
        assert content == ''
        assert '请选择一个提示词' in status or 'Please select a prompt' in status
    
    def test_handle_prompt_selection_failure(self, ui_components, mock_prompt_manager):
        """测试处理提示词选择失败 / Test prompt selection failure handling"""
        # 配置模拟返回值 / Configure mock return values
        mock_prompt_manager.set_active_prompt.return_value = False
        
        # 调用方法 / Call method
        content, status = ui_components.handle_prompt_selection('nonexistent')
        
        # 验证结果 / Verify results
        assert content == ''
        assert '切换提示词失败' in status or 'Failed to switch prompt' in status
    
    @patch('gradio.Column')
    @patch('gradio.Dropdown')
    def test_handle_prompt_creation_success(self, mock_dropdown, mock_column, ui_components, mock_prompt_manager):
        """测试成功创建提示词 / Test successful prompt creation"""
        # 配置模拟返回值 / Configure mock return values
        mock_prompt_manager.create_prompt.return_value = True
        
        # 调用方法 / Call method
        status, dialog_state, selector = ui_components.handle_prompt_creation('new_prompt', 'New content')
        
        # 验证结果 / Verify results
        assert '成功创建提示词' in status or 'Successfully created prompt' in status
        assert 'new_prompt' in status
        
        # 验证调用 / Verify calls
        mock_prompt_manager.create_prompt.assert_called_once_with('new_prompt', 'New content')
        mock_column.assert_called_with(visible=False)
    
    def test_handle_prompt_creation_empty_name(self, ui_components):
        """测试创建提示词时名称为空 / Test prompt creation with empty name"""
        with patch('gradio.Column') as mock_column, patch('gradio.Dropdown') as mock_dropdown:
            status, dialog_state, selector = ui_components.handle_prompt_creation('', 'Some content')
            
            assert '提示词名称不能为空' in status or 'Prompt name cannot be empty' in status
            mock_column.assert_called_with(visible=True)
    
    def test_handle_prompt_creation_empty_content(self, ui_components):
        """测试创建提示词时内容为空 / Test prompt creation with empty content"""
        with patch('gradio.Column') as mock_column, patch('gradio.Dropdown') as mock_dropdown:
            status, dialog_state, selector = ui_components.handle_prompt_creation('test_name', '')
            
            assert '提示词内容不能为空' in status or 'Prompt content cannot be empty' in status
            mock_column.assert_called_with(visible=True)
    
    def test_handle_prompt_update_success(self, ui_components, mock_prompt_manager):
        """测试成功更新提示词 / Test successful prompt update"""
        # 配置模拟返回值 / Configure mock return values
        mock_prompt_manager.update_prompt.return_value = True
        
        # 调用方法 / Call method
        status = ui_components.handle_prompt_update('existing_prompt', 'Updated content')
        
        # 验证结果 / Verify results
        assert '成功更新提示词' in status or 'Successfully updated prompt' in status
        assert 'existing_prompt' in status
        
        # 验证调用 / Verify calls
        mock_prompt_manager.update_prompt.assert_called_once_with('existing_prompt', 'Updated content')
    
    def test_handle_prompt_update_no_name(self, ui_components):
        """测试更新提示词时没有名称 / Test prompt update with no name"""
        status = ui_components.handle_prompt_update('', 'Some content')
        
        assert '没有选中的提示词' in status or 'No prompt selected' in status
    
    def test_handle_prompt_update_empty_content(self, ui_components):
        """测试更新提示词时内容为空 / Test prompt update with empty content"""
        status = ui_components.handle_prompt_update('test_name', '')
        
        assert '提示词内容不能为空' in status or 'Prompt content cannot be empty' in status
    
    @patch('gradio.Dropdown')
    def test_handle_prompt_deletion_success(self, mock_dropdown, ui_components, mock_prompt_manager):
        """测试成功删除提示词 / Test successful prompt deletion"""
        # 配置模拟返回值 / Configure mock return values
        mock_prompt_manager.delete_prompt.return_value = True
        
        # 调用方法 / Call method
        status, selector = ui_components.handle_prompt_deletion('test_prompt')
        
        # 验证结果 / Verify results
        assert '成功删除提示词' in status or 'Successfully deleted prompt' in status
        assert 'test_prompt' in status
        
        # 验证调用 / Verify calls
        mock_prompt_manager.delete_prompt.assert_called_once_with('test_prompt')
    
    def test_handle_prompt_deletion_no_name(self, ui_components):
        """测试删除提示词时没有名称 / Test prompt deletion with no name"""
        with patch('gradio.Dropdown') as mock_dropdown:
            status, selector = ui_components.handle_prompt_deletion('')
            
            assert '没有选中的提示词' in status or 'No prompt selected' in status
    
    def test_handle_prompt_deletion_failure(self, ui_components, mock_prompt_manager):
        """测试删除提示词失败 / Test prompt deletion failure"""
        # 配置模拟返回值 / Configure mock return values
        mock_prompt_manager.delete_prompt.return_value = False
        
        with patch('gradio.Dropdown') as mock_dropdown:
            status, selector = ui_components.handle_prompt_deletion('test_prompt')
            
            assert '删除提示词失败' in status or 'Failed to delete prompt' in status
    
    def test_exception_handling_in_prompt_selection(self, ui_components, mock_prompt_manager):
        """测试提示词选择中的异常处理 / Test exception handling in prompt selection"""
        # 配置模拟抛出异常 / Configure mock to raise exception
        mock_prompt_manager.set_active_prompt.side_effect = Exception('Test error')
        
        # 调用方法 / Call method
        content, status = ui_components.handle_prompt_selection('test')
        
        # 验证结果 / Verify results
        assert content == ''
        assert 'Test error' in status
        assert '切换提示词时发生错误' in status or 'Error switching prompt' in status
    
    def test_exception_handling_in_prompt_creation(self, ui_components, mock_prompt_manager):
        """测试提示词创建中的异常处理 / Test exception handling in prompt creation"""
        # 配置模拟抛出异常 / Configure mock to raise exception
        mock_prompt_manager.create_prompt.side_effect = Exception('Creation error')
        
        with patch('gradio.Column') as mock_column, patch('gradio.Dropdown') as mock_dropdown:
            status, dialog_state, selector = ui_components.handle_prompt_creation('test', 'content')
            
            assert 'Creation error' in status
            assert '创建提示词时发生错误' in status or 'Error creating prompt' in status
            mock_column.assert_called_with(visible=True)
    
    def test_exception_handling_in_prompt_update(self, ui_components, mock_prompt_manager):
        """测试提示词更新中的异常处理 / Test exception handling in prompt update"""
        # 配置模拟抛出异常 / Configure mock to raise exception
        mock_prompt_manager.update_prompt.side_effect = Exception('Update error')
        
        # 调用方法 / Call method
        status = ui_components.handle_prompt_update('test', 'content')
        
        # 验证结果 / Verify results
        assert 'Update error' in status
        assert '更新提示词时发生错误' in status or 'Error updating prompt' in status
    
    def test_exception_handling_in_prompt_deletion(self, ui_components, mock_prompt_manager):
        """测试提示词删除中的异常处理 / Test exception handling in prompt deletion"""
        # 配置模拟抛出异常 / Configure mock to raise exception
        mock_prompt_manager.delete_prompt.side_effect = Exception('Deletion error')
        
        with patch('gradio.Dropdown') as mock_dropdown:
            status, selector = ui_components.handle_prompt_deletion('test')
            
            assert 'Deletion error' in status
            assert '删除提示词时发生错误' in status or 'Error deleting prompt' in status