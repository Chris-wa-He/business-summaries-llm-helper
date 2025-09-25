"""
基础端到端测试 / Basic End-to-End Tests
"""

import pytest
from unittest.mock import Mock

from src.utils.input_validator import InputValidator
from src.services.error_handler import RefinementErrorHandler
from src.services.conversation_service import ConversationService
from src.services.version_service import VersionService


class TestBasicE2E:
    """基础端到端测试 / Basic End-to-End Tests"""
    
    def test_input_validation_workflow(self):
        """测试输入验证工作流 / Test input validation workflow"""
        validator = InputValidator()
        
        # 正常输入 / Normal input
        normal_input = "请帮我优化这个案例总结"
        result = validator.validate_user_message(normal_input)
        assert result.is_valid
        assert result.cleaned_data == normal_input
        
        # 恶意输入 / Malicious input
        malicious_input = "<script>alert('xss')</script>"
        result = validator.validate_user_message(malicious_input)
        assert not result.is_valid
        assert result.errors is not None
    
    def test_error_handling_workflow(self):
        """测试错误处理工作流 / Test error handling workflow"""
        error_handler = RefinementErrorHandler()
        
        # 模拟错误 / Mock error
        test_error = Exception("测试错误")
        context = {"user_id": "test_user", "session_id": "test_session"}
        
        result = error_handler.handle_error(test_error, context)
        
        assert "error_id" in result
        assert "message" in result
        assert "user_message" in result
        assert isinstance(result["success"], bool)
    
    def test_conversation_service_workflow(self):
        """测试对话服务工作流 / Test conversation service workflow"""
        conversation_service = ConversationService()
        
        # 创建会话 / Create session
        session_id = conversation_service.create_session("test_user", "初始内容")
        assert session_id is not None
        
        # 获取对话历史 / Get conversation history
        history = conversation_service.get_conversation_history(session_id)
        assert isinstance(history, list)
    
    def test_version_service_workflow(self):
        """测试版本服务工作流 / Test version service workflow"""
        version_service = VersionService()
        
        # 创建版本 / Create version
        version_id = version_service.create_version(
            "test_session", "测试内容", "initial"
        )
        assert version_id is not None
        
        # 获取版本列表 / Get version list
        versions = version_service.get_version_list("test_session")
        assert isinstance(versions, list)
    
    def test_security_validation_integration(self):
        """测试安全验证集成 / Test security validation integration"""
        validator = InputValidator()
        
        # 测试各种安全威胁 / Test various security threats
        test_cases = [
            {
                'input': '正常消息',
                'expected': True
            },
            {
                'input': '<script>alert("xss")</script>',
                'expected': False
            },
            {
                'input': 'a' * 3000,  # 超长输入
                'expected': False
            }
        ]
        
        for case in test_cases:
            if len(case['input']) > 2000:
                result = validator.validate_user_message(case['input'], max_length=2000)
            else:
                result = validator.validate_user_message(case['input'])
            
            assert result.is_valid == case['expected']
    
    def test_component_integration(self):
        """测试组件集成 / Test component integration"""
        # 验证所有核心组件都能正常实例化
        # Verify all core components can be instantiated normally
        
        validator = InputValidator()
        error_handler = RefinementErrorHandler()
        conversation_service = ConversationService()
        version_service = VersionService()
        
        # 验证组件接口 / Verify component interfaces
        assert hasattr(validator, 'validate_user_message')
        assert hasattr(error_handler, 'handle_error')
        assert hasattr(conversation_service, 'create_session')
        assert hasattr(version_service, 'create_version')
    
    def test_data_flow_integration(self):
        """测试数据流集成 / Test data flow integration"""
        # 模拟完整的数据处理流程
        # Mock complete data processing flow
        
        # 1. 输入验证 / Input validation
        validator = InputValidator()
        user_input = "请添加技术细节"
        validation_result = validator.validate_user_message(user_input)
        assert validation_result.is_valid
        
        # 2. 会话管理 / Session management
        conversation_service = ConversationService()
        session_id = conversation_service.create_session("test_user", "初始内容")
        assert session_id is not None
        
        # 3. 版本管理 / Version management
        version_service = VersionService()
        version_id = version_service.create_version(session_id, "修改后内容", "modification")
        assert version_id is not None
        
        # 4. 错误处理 / Error handling
        error_handler = RefinementErrorHandler()
        stats = error_handler.get_error_statistics()
        assert "total_errors" in stats


class TestSystemStability:
    """系统稳定性测试 / System Stability Tests"""
    
    def test_repeated_operations(self):
        """测试重复操作稳定性 / Test repeated operations stability"""
        validator = InputValidator()
        
        # 重复验证操作 / Repeated validation operations
        for i in range(10):
            result = validator.validate_user_message(f"测试消息 {i}")
            assert result.is_valid
    
    def test_error_recovery(self):
        """测试错误恢复 / Test error recovery"""
        error_handler = RefinementErrorHandler()
        
        # 处理多个错误 / Handle multiple errors
        for i in range(5):
            test_error = Exception(f"测试错误 {i}")
            result = error_handler.handle_error(test_error, {"test": i})
            assert "error_id" in result
        
        # 验证错误统计 / Verify error statistics
        stats = error_handler.get_error_statistics()
        assert stats["total_errors"] == 5
    
    def test_resource_cleanup(self):
        """测试资源清理 / Test resource cleanup"""
        # 创建多个服务实例 / Create multiple service instances
        services = []
        for i in range(5):
            conversation_service = ConversationService()
            version_service = VersionService()
            services.append((conversation_service, version_service))
        
        # 验证实例创建成功 / Verify instances created successfully
        assert len(services) == 5
        
        # 清理资源 / Cleanup resources
        del services


@pytest.mark.integration
class TestRealWorldScenarios:
    """真实世界场景测试 / Real World Scenario Tests"""
    
    def test_typical_user_interaction(self):
        """测试典型用户交互 / Test typical user interaction"""
        # 模拟用户的典型使用流程
        # Mock typical user workflow
        
        validator = InputValidator()
        conversation_service = ConversationService()
        version_service = VersionService()
        
        # 1. 用户输入验证 / User input validation
        user_messages = [
            "请添加风险评估部分",
            "详细说明技术实现",
            "调整语言风格"
        ]
        
        for message in user_messages:
            result = validator.validate_user_message(message)
            assert result.is_valid
        
        # 2. 会话管理 / Session management
        session_id = conversation_service.create_session("typical_user", "初始内容")
        assert session_id is not None
        
        # 3. 版本创建 / Version creation
        for i, message in enumerate(user_messages):
            version_id = version_service.create_version(
                session_id, f"修改后内容 {i+1}", "modification"
            )
            assert version_id is not None
    
    def test_edge_case_handling(self):
        """测试边界情况处理 / Test edge case handling"""
        validator = InputValidator()
        
        # 边界情况测试 / Edge case tests
        edge_cases = [
            "",  # 空输入
            " ",  # 空白输入
            "a",  # 单字符
            "测试" * 1000,  # 长输入
        ]
        
        for case in edge_cases:
            if len(case) > 2000:
                result = validator.validate_user_message(case, max_length=2000)
            else:
                result = validator.validate_user_message(case)
            
            # 验证处理结果 / Verify handling result
            assert isinstance(result.is_valid, bool)
            if result.errors:
                assert isinstance(result.errors, list)
    
    def test_multilingual_support(self):
        """测试多语言支持 / Test multilingual support"""
        validator = InputValidator()
        
        # 多语言输入测试 / Multilingual input tests
        multilingual_inputs = [
            "请添加技术细节",  # 中文
            "Please add technical details",  # 英文
            "技術詳細を追加してください",  # 日文
            "Veuillez ajouter des détails techniques",  # 法文
        ]
        
        for input_text in multilingual_inputs:
            result = validator.validate_user_message(input_text)
            assert result.is_valid
            assert result.cleaned_data is not None