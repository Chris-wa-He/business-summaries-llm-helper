"""
安全性测试 / Security Tests
"""

import pytest
import tempfile
import os
from src.utils.input_validator import (
    InputValidator, AccessController, SecurityAuditor,
    ValidationLevel, ValidationResult
)


class TestInputValidator:
    """输入验证器测试 / Input Validator Tests"""
    
    @pytest.fixture
    def validator(self):
        return InputValidator(ValidationLevel.STRICT)
    
    def test_validate_user_message_success(self, validator):
        """测试用户消息验证成功 / Test user message validation success"""
        result = validator.validate_user_message("这是一个正常的消息")
        assert result.is_valid
        assert result.cleaned_data == "这是一个正常的消息"
        assert not result.errors
    
    def test_validate_user_message_xss_attack(self, validator):
        """测试XSS攻击检测 / Test XSS attack detection"""
        malicious_input = "<script>alert('xss')</script>"
        result = validator.validate_user_message(malicious_input)
        assert not result.is_valid
        assert "XSS" in str(result.errors)
    
    def test_validate_user_message_length_limit(self, validator):
        """测试消息长度限制 / Test message length limit"""
        long_message = "a" * 2001
        result = validator.validate_user_message(long_message, max_length=2000)
        assert not result.is_valid
        assert "长度超出限制" in str(result.errors) or "exceeds length limit" in str(result.errors)
    
    def test_validate_file_path_success(self, validator):
        """测试文件路径验证成功 / Test file path validation success"""
        result = validator.validate_file_path("folder/file.txt")
        assert result.is_valid
        assert result.cleaned_data == "folder/file.txt"
    
    def test_validate_file_path_traversal_attack(self, validator):
        """测试路径遍历攻击检测 / Test path traversal attack detection"""
        malicious_path = "../../../etc/passwd"
        result = validator.validate_file_path(malicious_path)
        assert not result.is_valid
        assert "路径遍历" in str(result.errors) or "traversal" in str(result.errors)
    
    def test_validate_prompt_content(self, validator):
        """测试提示词内容验证 / Test prompt content validation"""
        content = "你是一个专业的助手，请帮助用户解决问题。"
        result = validator.validate_prompt_content(content)
        assert result.is_valid
        assert result.cleaned_data == content
    
    def test_validate_session_id_success(self, validator):
        """测试会话ID验证成功 / Test session ID validation success"""
        result = validator.validate_session_id("session_123")
        assert result.is_valid
        assert result.cleaned_data == "session_123"
    
    def test_validate_session_id_invalid_format(self, validator):
        """测试会话ID格式无效 / Test invalid session ID format"""
        result = validator.validate_session_id("session@123!")
        assert not result.is_valid
        assert "格式无效" in str(result.errors) or "Invalid" in str(result.errors)


class TestAccessController:
    """访问控制器测试 / Access Controller Tests"""
    
    @pytest.fixture
    def access_controller(self):
        return AccessController()
    
    def test_check_session_access_success(self, access_controller):
        """测试会话访问检查成功 / Test session access check success"""
        result = access_controller.check_session_access("session_1", "user_1", "read")
        assert result is True
    
    def test_check_session_access_invalid_params(self, access_controller):
        """测试会话访问检查无效参数 / Test session access check invalid params"""
        result = access_controller.check_session_access("", "user_1", "read")
        assert result is False
        
        result = access_controller.check_session_access("session_1", "", "read")
        assert result is False
    
    def test_check_rate_limit_success(self, access_controller):
        """测试速率限制检查成功 / Test rate limit check success"""
        result = access_controller.check_rate_limit("user_1", "message", limit=5, window=60)
        assert result is True
    
    def test_check_rate_limit_exceeded(self, access_controller):
        """测试速率限制超出 / Test rate limit exceeded"""
        # 快速发送多个请求 / Send multiple requests quickly
        for i in range(3):
            access_controller.check_rate_limit("user_1", "message", limit=2, window=60)
        
        # 第4个请求应该被限制 / 4th request should be limited
        result = access_controller.check_rate_limit("user_1", "message", limit=2, window=60)
        assert result is False


class TestSecurityAuditor:
    """安全审计器测试 / Security Auditor Tests"""
    
    @pytest.fixture
    def security_auditor(self):
        # 使用临时文件 / Use temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        auditor = SecurityAuditor(temp_file.name)
        yield auditor
        # 清理临时文件 / Cleanup temporary file
        os.unlink(temp_file.name)
    
    def test_log_security_event(self, security_auditor):
        """测试安全事件记录 / Test security event logging"""
        security_auditor.log_security_event(
            "TEST_EVENT",
            "user_1",
            {"action": "test", "result": "success"}
        )
        
        # 验证日志文件存在 / Verify log file exists
        assert os.path.exists(security_auditor.log_file)
    
    def test_log_access_attempt(self, security_auditor):
        """测试访问尝试记录 / Test access attempt logging"""
        security_auditor.log_access_attempt("user_1", "session_1", "read", True)
        
        # 验证日志文件存在 / Verify log file exists
        assert os.path.exists(security_auditor.log_file)
    
    def test_log_validation_failure(self, security_auditor):
        """测试验证失败记录 / Test validation failure logging"""
        security_auditor.log_validation_failure(
            "user_1",
            "message",
            ["XSS attack detected"]
        )
        
        # 验证日志文件存在 / Verify log file exists
        assert os.path.exists(security_auditor.log_file)


class TestSecurityIntegration:
    """安全性集成测试 / Security Integration Tests"""
    
    def test_complete_security_workflow(self):
        """测试完整安全工作流 / Test complete security workflow"""
        validator = InputValidator(ValidationLevel.STRICT)
        access_controller = AccessController()
        
        # 1. 验证输入 / Validate input
        message = "请帮我分析这个案例"
        validation_result = validator.validate_user_message(message)
        assert validation_result.is_valid
        
        # 2. 检查访问权限 / Check access permission
        access_granted = access_controller.check_session_access("session_1", "user_1", "message")
        assert access_granted
        
        # 3. 检查速率限制 / Check rate limit
        rate_ok = access_controller.check_rate_limit("user_1", "message", limit=10, window=60)
        assert rate_ok
    
    def test_security_failure_workflow(self):
        """测试安全失败工作流 / Test security failure workflow"""
        validator = InputValidator(ValidationLevel.STRICT)
        
        # 恶意输入测试 / Malicious input test
        malicious_input = "<script>alert('hack')</script>"
        validation_result = validator.validate_user_message(malicious_input)
        assert not validation_result.is_valid
        
        # 路径遍历测试 / Path traversal test
        malicious_path = "../../etc/passwd"
        path_result = validator.validate_file_path(malicious_path)
        assert not path_result.is_valid