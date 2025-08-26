"""
系统提示词服务安全测试 / System Prompt Service Security Tests

测试SystemPromptService的输入验证和安全检查功能。
Tests input validation and security check functionality of SystemPromptService.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open
from src.services.system_prompt_service import SystemPromptService
from src.exceptions.system_prompt_exceptions import (
    PromptValidationError, PromptStorageError
)


class TestSystemPromptServiceSecurity:
    """系统提示词服务安全测试类 / System Prompt Service Security Test Class"""
    
    def setup_method(self):
        """设置测试环境 / Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.prompts_folder = Path(self.temp_dir) / "prompts"
        self.history_folder = Path(self.temp_dir) / "history"
        
        self.prompts_folder.mkdir(parents=True, exist_ok=True)
        self.history_folder.mkdir(parents=True, exist_ok=True)
        
        self.service = SystemPromptService(
            str(self.prompts_folder),
            str(self.history_folder)
        )
    
    def teardown_method(self):
        """清理测试环境 / Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validate_prompt_name_empty(self):
        """测试空提示词名称验证 / Test empty prompt name validation"""
        with pytest.raises(PromptValidationError, match="提示词名称不能为空"):
            self.service.validate_prompt_name("")
        
        with pytest.raises(PromptValidationError, match="提示词名称不能为空"):
            self.service.validate_prompt_name("   ")
        
        with pytest.raises(PromptValidationError, match="提示词名称不能为空"):
            self.service.validate_prompt_name(None)
    
    def test_validate_prompt_name_too_long(self):
        """测试过长提示词名称验证 / Test too long prompt name validation"""
        long_name = "a" * 101
        with pytest.raises(PromptValidationError, match="提示词名称过长"):
            self.service.validate_prompt_name(long_name)
    
    def test_validate_prompt_name_path_traversal(self):
        """测试路径遍历攻击防护 / Test path traversal attack protection"""
        dangerous_names = [
            "../test",
            "test/../other",
            "..\\test",
            "test\\..\\other",
            "/etc/passwd",
            "C:\\Windows\\System32"
        ]
        
        for name in dangerous_names:
            with pytest.raises(PromptValidationError, match="不能包含路径分隔符"):
                self.service.validate_prompt_name(name)
    
    def test_validate_prompt_name_illegal_characters(self):
        """测试非法字符验证 / Test illegal characters validation"""
        illegal_names = [
            "test<name>",
            "test:name",
            'test"name',
            "test|name",
            "test?name",
            "test*name",
            "test\x00name",  # null character
            "test\x1fname"   # control character
        ]
        
        for name in illegal_names:
            with pytest.raises(PromptValidationError, match="包含非法字符"):
                self.service.validate_prompt_name(name)
    
    def test_validate_prompt_name_reserved_names(self):
        """测试系统保留名称验证 / Test system reserved names validation"""
        reserved_names = ["CON", "PRN", "AUX", "NUL", "COM1", "LPT1"]
        
        for name in reserved_names:
            with pytest.raises(PromptValidationError, match="不能使用系统保留名称"):
                self.service.validate_prompt_name(name)
            
            # 测试小写版本 / Test lowercase version
            with pytest.raises(PromptValidationError, match="不能使用系统保留名称"):
                self.service.validate_prompt_name(name.lower())
    
    def test_validate_prompt_name_valid(self):
        """测试有效提示词名称 / Test valid prompt names"""
        valid_names = [
            "test_prompt",
            "测试提示词",
            "prompt-123",
            "My Prompt",
            "prompt_with_underscores"
        ]
        
        for name in valid_names:
            assert self.service.validate_prompt_name(name) is True
    
    def test_validate_prompt_content_empty(self):
        """测试空内容验证 / Test empty content validation"""
        with pytest.raises(PromptValidationError, match="提示词内容不能为空"):
            self.service.validate_prompt_content("")
        
        with pytest.raises(PromptValidationError, match="提示词内容不能为空"):
            self.service.validate_prompt_content("   ")
        
        with pytest.raises(PromptValidationError, match="提示词内容不能为空"):
            self.service.validate_prompt_content(None)
    
    def test_validate_prompt_content_too_long(self):
        """测试过长内容验证 / Test too long content validation"""
        long_content = "a" * 50001
        with pytest.raises(PromptValidationError, match="提示词内容过长"):
            self.service.validate_prompt_content(long_content)
    
    def test_validate_prompt_content_control_characters(self):
        """测试控制字符验证 / Test control characters validation"""
        content_with_control_chars = [
            "test\x00content",  # null
            "test\x01content",  # start of heading
            "test\x1fcontent",  # unit separator
            "test\x7fcontent"   # delete
        ]
        
        for content in content_with_control_chars:
            with pytest.raises(PromptValidationError, match="包含非法控制字符"):
                self.service.validate_prompt_content(content)
    
    def test_validate_prompt_content_valid(self):
        """测试有效内容 / Test valid content"""
        valid_contents = [
            "This is a valid prompt content.",
            "这是一个有效的提示词内容。",
            "Content with\nnewlines\tand tabs.",
            "Content with émojis 🎉 and special chars: @#$%^&*()"
        ]
        
        for content in valid_contents:
            assert self.service.validate_prompt_content(content) is True
    
    def test_validate_file_path_security_outside_base(self):
        """测试文件路径安全检查 - 超出基础目录 / Test file path security - outside base directory"""
        dangerous_path = Path("/etc/passwd")
        with pytest.raises(PromptStorageError, match="文件路径超出允许范围"):
            self.service.validate_file_path_security(dangerous_path)
    
    def test_validate_file_path_security_valid(self):
        """测试有效文件路径 / Test valid file path"""
        valid_path = self.prompts_folder / "test_prompt.md"
        assert self.service.validate_file_path_security(valid_path) is True
    
    @patch('os.access')
    def test_check_file_permissions_write_no_permission(self, mock_access):
        """测试写权限检查 - 无权限 / Test write permission check - no permission"""
        mock_access.return_value = False
        
        test_path = self.prompts_folder / "test.md"
        with pytest.raises(PromptStorageError, match="目录写入权限不足"):
            self.service.check_file_permissions(test_path, 'write')
    
    @patch('os.access')
    def test_check_file_permissions_read_no_permission(self, mock_access):
        """测试读权限检查 - 无权限 / Test read permission check - no permission"""
        # 创建测试文件 / Create test file
        test_path = self.prompts_folder / "test.md"
        test_path.write_text("test content")
        
        mock_access.return_value = False
        
        with pytest.raises(PromptStorageError, match="文件读取权限不足"):
            self.service.check_file_permissions(test_path, 'read')
    
    def test_check_file_permissions_valid(self):
        """测试有效权限检查 / Test valid permission check"""
        test_path = self.prompts_folder / "test.md"
        
        # 测试写权限 / Test write permission
        assert self.service.check_file_permissions(test_path, 'write') is True
        
        # 创建文件后测试读权限 / Test read permission after creating file
        test_path.write_text("test content")
        assert self.service.check_file_permissions(test_path, 'read') is True
    
    def test_save_prompt_file_with_security_checks(self):
        """测试保存文件时的安全检查 / Test security checks when saving file"""
        # 测试有效保存 / Test valid save
        assert self.service.save_prompt_file("valid_name", "Valid content") is True
        
        # 测试无效名称 / Test invalid name
        with pytest.raises(PromptValidationError):
            self.service.save_prompt_file("../invalid", "Content")
        
        # 测试无效内容 / Test invalid content
        with pytest.raises(PromptValidationError):
            self.service.save_prompt_file("valid_name", "")
    
    def test_load_prompt_file_with_security_checks(self):
        """测试加载文件时的安全检查 / Test security checks when loading file"""
        # 先创建一个有效文件 / First create a valid file
        self.service.save_prompt_file("test_prompt", "Test content")
        
        # 测试有效加载 / Test valid load
        content = self.service.load_prompt_file("test_prompt")
        assert "Test content" in content
        
        # 测试加载不存在的文件 / Test loading non-existent file
        from src.exceptions.system_prompt_exceptions import PromptNotFoundError
        with pytest.raises(PromptNotFoundError):
            self.service.load_prompt_file("nonexistent")
