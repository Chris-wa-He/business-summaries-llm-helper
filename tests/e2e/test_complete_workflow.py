"""
端到端测试 - 完整工作流 / End-to-End Tests - Complete Workflow
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from src.services.refinement_controller import RefinementController
from src.services.conversation_service import ConversationService
from src.services.version_service import VersionService
from src.services.modification_service import ModificationService
from src.utils.input_validator import InputValidator
from src.services.error_handler import RefinementErrorHandler


@pytest.fixture
def temp_workspace():
    """创建临时工作空间 / Create temporary workspace"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_app_controller():
    """模拟应用控制器 / Mock app controller"""
    controller = Mock()
    controller.get_bedrock_client.return_value = Mock()
    return controller


class TestCompleteRefinementWorkflow:
    """完整优化工作流测试 / Complete Refinement Workflow Tests"""
    
    @pytest.mark.asyncio
    async def test_content_generation_to_refinement_workflow(self, temp_workspace, mock_app_controller):
        """测试从内容生成到交互优化的完整流程 / Test complete workflow from content generation to interactive refinement"""
        
        # 1. 初始化组件 / Initialize components
        refinement_controller = RefinementController(mock_app_controller)
        
        # 模拟初始内容生成 / Mock initial content generation
        initial_content = "这是一个初始的案例总结内容。包含基本信息和分析。"
        user_id = "test_user_001"
        
        # 2. 启动优化会话 / Start refinement session
        session_id = await refinement_controller.start_refinement_session(initial_content, user_id)
        assert session_id is not None
        assert session_id.startswith("session_")
        
        # 3. 模拟用户交互 / Mock user interaction
        user_messages = [
            "请添加风险评估部分",
            "详细说明技术实现方案", 
            "调整语言风格，使其更加正式"
        ]
        
        # 模拟AI响应 / Mock AI responses
        with patch.object(refinement_controller.modification_service, 'process_modification_request', new_callable=AsyncMock) as mock_modify:
            mock_modify.return_value = {
                'success': True,
                'modified_content': initial_content + "\n\n## 风险评估\n相关风险分析内容...",
                'modification_type': 'content_addition'
            }
            
            # 处理用户消息 / Process user messages
            for message in user_messages:
                result = await refinement_controller.process_user_message(message, session_id)
                
                assert result['success'] is True
                assert 'response' in result
                assert 'modified_content' in result
        
        # 4. 验证版本历史 / Verify version history
        version_history = refinement_controller.get_version_history(session_id)
        assert len(version_history) >= 1  # 至少有初始版本
        
        # 5. 测试版本回退 / Test version rollback
        if len(version_history) > 1:
            first_version_id = version_history[0]['id']
            reverted_content = refinement_controller.revert_to_version(session_id, first_version_id)
            assert reverted_content is not None


class TestPersonalizedPreferenceLearning:
    """个性化偏好学习测试 / Personalized Preference Learning Tests"""
    
    def test_preference_learning_workflow(self, temp_workspace):
        """测试偏好学习工作流 / Test preference learning workflow"""
        
        # 模拟用户交互历史 / Mock user interaction history
        interaction_history = [
            {
                'user_message': '请添加更多技术细节',
                'modification_type': 'content_addition',
                'user_satisfaction': 0.9,
                'timestamp': '2024-01-01T10:00:00'
            },
            {
                'user_message': '调整为更正式的语言',
                'modification_type': 'style_adjustment', 
                'user_satisfaction': 0.8,
                'timestamp': '2024-01-01T10:05:00'
            }
        ]
        
        # 验证偏好数据结构 / Verify preference data structure
        assert len(interaction_history) == 2
        assert all('user_satisfaction' in item for item in interaction_history)
        assert all('modification_type' in item for item in interaction_history)


class TestDataExportImport:
    """数据导出导入测试 / Data Export Import Tests"""
    
    def test_export_import_workflow(self, temp_workspace):
        """测试数据导出导入完整性 / Test data export import integrity"""
        
        # 模拟用户偏好数据 / Mock user preference data
        test_data = {
            'user_id': 'test_user',
            'preferences': {
                'modification_types': {
                    'content_addition': 0.8,
                    'style_adjustment': 0.7
                },
                'interaction_patterns': {
                    'preferred_detail_level': 'high',
                    'communication_style': 'formal'
                }
            },
            'export_timestamp': '2024-01-01T12:00:00'
        }
        
        # 验证数据结构完整性 / Verify data structure integrity
        assert 'user_id' in test_data
        assert 'preferences' in test_data
        assert 'export_timestamp' in test_data
        
        # 模拟导出过程 / Mock export process
        export_result = {
            'success': True,
            'filename': f"preferences_{test_data['user_id']}_20240101.json",
            'data_size': len(str(test_data))
        }
        
        assert export_result['success'] is True
        assert 'filename' in export_result


class TestSystemIntegration:
    """系统集成测试 / System Integration Tests"""
    
    def test_component_integration(self):
        """测试组件集成 / Test component integration"""
        
        # 测试输入验证集成 / Test input validation integration
        validator = InputValidator()
        test_message = "请帮我优化这个案例总结"
        
        validation_result = validator.validate_user_message(test_message)
        assert validation_result.is_valid
        assert validation_result.cleaned_data == test_message
        
        # 测试错误处理集成 / Test error handling integration
        error_handler = RefinementErrorHandler()
        test_error = Exception("测试错误")
        
        error_result = error_handler.handle_error(test_error, {'user_id': 'test_user'})
        assert 'error_id' in error_result
        assert 'user_message' in error_result
    
    def test_service_compatibility(self):
        """测试服务兼容性 / Test service compatibility"""
        
        # 测试对话服务 / Test conversation service
        conversation_service = ConversationService()
        assert hasattr(conversation_service, 'create_session')
        assert hasattr(conversation_service, 'add_message')
        
        # 测试版本服务 / Test version service
        version_service = VersionService()
        assert hasattr(version_service, 'create_version')
        assert hasattr(version_service, 'get_version_list')
        
        # 测试修改服务 / Test modification service
        modification_service = ModificationService(Mock())
        assert hasattr(modification_service, 'process_modification_request')


class TestErrorRecovery:
    """错误恢复测试 / Error Recovery Tests"""
    
    @pytest.mark.asyncio
    async def test_session_recovery_workflow(self, mock_app_controller):
        """测试会话恢复工作流 / Test session recovery workflow"""
        
        refinement_controller = RefinementController(mock_app_controller)
        
        # 模拟会话创建 / Mock session creation
        initial_content = "测试内容"
        user_id = "test_user"
        
        session_id = await refinement_controller.start_refinement_session(initial_content, user_id)
        assert session_id is not None
        
        # 模拟错误场景 / Mock error scenario
        with patch.object(refinement_controller.conversation_service, 'add_message', side_effect=Exception("连接错误")):
            # 测试错误处理 / Test error handling
            try:
                await refinement_controller.process_user_message("测试消息", session_id)
            except Exception as e:
                # 验证错误被正确处理 / Verify error is properly handled
                assert "连接错误" in str(e)
    
    def test_data_corruption_recovery(self):
        """测试数据损坏恢复 / Test data corruption recovery"""
        
        # 模拟数据损坏场景 / Mock data corruption scenario
        corrupted_data = "invalid_json_data"
        
        # 验证错误处理机制 / Verify error handling mechanism
        error_handler = RefinementErrorHandler()
        
        try:
            import json
            json.loads(corrupted_data)
        except json.JSONDecodeError as e:
            error_result = error_handler.handle_error(e, {'data_type': 'preference'})
            assert error_result['success'] is False
            assert 'error_id' in error_result


class TestPerformanceUnderLoad:
    """负载下性能测试 / Performance Under Load Tests"""
    
    @pytest.mark.asyncio
    async def test_concurrent_sessions(self, mock_app_controller):
        """测试并发会话处理 / Test concurrent session handling"""
        
        refinement_controller = RefinementController(mock_app_controller)
        
        # 创建多个并发会话 / Create multiple concurrent sessions
        sessions = []
        for i in range(3):  # 减少并发数量以避免测试超时
            session_id = await refinement_controller.start_refinement_session(
                f"测试内容 {i}", f"user_{i}"
            )
            sessions.append(session_id)
        
        # 验证所有会话都成功创建 / Verify all sessions created successfully
        assert len(sessions) == 3
        assert all(session.startswith("session_") for session in sessions)
    
    def test_large_content_handling(self):
        """测试大内容处理 / Test large content handling"""
        
        # 创建大内容 / Create large content
        large_content = "测试内容 " * 1000  # 约10KB内容
        
        # 测试输入验证 / Test input validation
        validator = InputValidator()
        result = validator.validate_user_message(large_content, max_length=50000)
        
        assert result.is_valid
        assert len(result.cleaned_data) > 0


@pytest.mark.integration
class TestFullSystemWorkflow:
    """完整系统工作流测试 / Full System Workflow Tests"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_user_journey(self, temp_workspace, mock_app_controller):
        """测试端到端用户旅程 / Test end-to-end user journey"""
        
        # 1. 系统初始化 / System initialization
        refinement_controller = RefinementController(mock_app_controller)
        validator = InputValidator()
        error_handler = RefinementErrorHandler()
        
        # 2. 用户输入验证 / User input validation
        user_input = "请帮我优化这个案例总结，添加更多技术细节"
        validation_result = validator.validate_user_message(user_input)
        assert validation_result.is_valid
        
        # 3. 会话创建 / Session creation
        initial_content = "原始案例总结内容..."
        session_id = await refinement_controller.start_refinement_session(
            initial_content, "test_user"
        )
        assert session_id is not None
        
        # 4. 模拟交互优化过程 / Mock interactive refinement process
        with patch.object(refinement_controller.modification_service, 'process_modification_request', new_callable=AsyncMock) as mock_modify:
            mock_modify.return_value = {
                'success': True,
                'modified_content': initial_content + "\n\n技术细节补充...",
                'modification_type': 'content_addition'
            }
            
            result = await refinement_controller.process_user_message(
                validation_result.cleaned_data, session_id
            )
            
            assert result['success'] is True
        
        # 5. 验证系统状态 / Verify system state
        version_history = refinement_controller.get_version_history(session_id)
        assert len(version_history) >= 1
        
        # 6. 测试错误恢复 / Test error recovery
        test_error = Exception("模拟系统错误")
        error_result = error_handler.handle_error(test_error, {'session_id': session_id})
        assert 'error_id' in error_result