"""
系统提示词异常处理测试 / System Prompt Exception Handling Tests
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from src.exceptions.system_prompt_exceptions import (
    SystemPromptError, PromptNotFoundError, PromptValidationError, 
    PromptStorageError, HistoryFolderError
)
from src.services.system_prompt_service import SystemPromptService


class TestSystemPromptExceptions:
    """系统提示词异常测试类 / System Prompt Exceptions Test Class"""
    
    def test_exception_hierarchy(self):
        """测试异常继承层次 / Test exception hierarchy"""
        # 测试所有异常都继承自SystemPromptError / Test all exceptions inherit from SystemPromptError
        assert issubclass(PromptNotFoundError, SystemPromptError)
        assert issubclass(PromptValidationError, SystemPromptError)
        assert issubclass(PromptStorageError, SystemPromptError)
        assert issubclass(HistoryFolderError, SystemPromptError)
        
        # 测试SystemPromptError继承自Exception / Test SystemPromptError inherits from Exception
        assert issubclass(SystemPromptError, Exception)
    
    def test_exception_messages(self):
        """测试异常消息 / Test exception messages"""
        # 测试各种异常的消息传递 / Test message passing for various exceptions
        message = "Test error message"
        
        error = PromptNotFoundError(message)
        assert str(error) == message
        
        error = PromptValidationError(message)
        assert str(error) == message
        
        error = PromptStorageError(message)
        assert str(error) == message
        
        error = HistoryFolderError(message)
        assert str(error) == message


class TestSystemPromptServiceExceptions:
    """系统提示词服务异常测试类 / System Prompt Service Exceptions Test Class"""
    
    @pytest.fixture
    def temp_service(self, tmp_path):
        """创建临时服务实例 / Create temporary service instance"""
        prompts_folder = tmp_path / "prompts"
        history_folder = tmp_path / "history"
        return SystemPromptService(str(prompts_folder), str(history_folder))
    
    def test_validate_prompt_name_empty(self, temp_service):
        """测试空提示词名称验证 / Test empty prompt name validation"""
        with pytest.raises(PromptValidationError) as exc_info:
            temp_service.validate_prompt_name("")
        
        assert "提示词名称不能为空" in str(exc_info.value) or "Prompt name cannot be empty" in str(exc_info.value)
    
    def test_validate_prompt_name_too_long(self, temp_service):
        """测试过长提示词名称验证 / Test too long prompt name validation"""
        long_name = "a" * 101  # 超过100字符限制 / Exceed 100 character limit
        
        with pytest.raises(PromptValidationError) as exc_info:
            temp_service.validate_prompt_name(long_name)
        
        assert "提示词名称过长" in str(exc_info.value) or "Prompt name too long" in str(exc_info.value)
    
    def test_validate_prompt_name_illegal_characters(self, temp_service):
        """测试非法字符提示词名称验证 / Test illegal characters prompt name validation"""
        illegal_name = "test<name>"
        
        with pytest.raises(PromptValidationError) as exc_info:
            temp_service.validate_prompt_name(illegal_name)
        
        assert "非法字符" in str(exc_info.value) or "illegal characters" in str(exc_info.value)
    
    def test_save_prompt_file_empty_content(self, temp_service):
        """测试保存空内容提示词 / Test save prompt with empty content"""
        with pytest.raises(PromptValidationError) as exc_info:
            temp_service.save_prompt_file("test", "")
        
        assert "提示词内容不能为空" in str(exc_info.value) or "Prompt content cannot be empty" in str(exc_info.value)
    
    def test_load_prompt_file_not_found(self, temp_service):
        """测试加载不存在的提示词文件 / Test load non-existent prompt file"""
        with pytest.raises(PromptNotFoundError) as exc_info:
            temp_service.load_prompt_file("nonexistent")
        
        assert "提示词文件不存在" in str(exc_info.value) or "Prompt file not found" in str(exc_info.value)
    
    def test_save_and_load_prompt_success(self, temp_service):
        """测试成功保存和加载提示词 / Test successful save and load prompt"""
        # 这应该成功，不抛出异常 / This should succeed without throwing exceptions
        success = temp_service.save_prompt_file("test_prompt", "Test content")
        assert success is True
        
        content = temp_service.load_prompt_file("test_prompt")
        assert "Test content" in content
    
    @patch('builtins.open')
    def test_save_prompt_file_storage_error(self, mock_open, temp_service):
        """测试保存提示词文件存储错误 / Test save prompt file storage error"""
        # 配置mock抛出IO异常 / Configure mock to raise IO exception
        mock_open.side_effect = IOError("Permission denied")
        
        with pytest.raises(PromptStorageError) as exc_info:
            temp_service.save_prompt_file("test", "content")
        
        assert "保存提示词文件失败" in str(exc_info.value) or "Failed to save prompt file" in str(exc_info.value)
    
    def test_load_prompt_file_storage_error(self, temp_service):
        """测试加载提示词文件存储错误 / Test load prompt file storage error"""
        # 先创建文件 / First create the file
        temp_service.save_prompt_file("test", "content")
        
        # 然后使用patch模拟文件读取错误 / Then use patch to simulate file read error
        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', side_effect=IOError("Read error")):
            
            with pytest.raises(PromptStorageError) as exc_info:
                temp_service.load_prompt_file("test")
            
            assert "加载提示词文件失败" in str(exc_info.value) or "Failed to load prompt file" in str(exc_info.value)