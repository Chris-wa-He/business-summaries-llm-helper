"""
优化控制器测试 / Refinement Controller Tests
"""

import pytest
import tempfile
import shutil
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.services.refinement_controller import RefinementController
from src.services.app_controller import AppController
from src.models.refinement_models import ModificationType


class TestRefinementController:
    """优化控制器测试类 / Refinement Controller Test Class"""
    
    @pytest.fixture
    def temp_storage_path(self):
        """创建临时存储路径 / Create temporary storage path"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_app_controller(self):
        """创建模拟应用控制器 / Create mock app controller"""
        return Mock(spec=AppController)
    
    @pytest.fixture
    def refinement_controller(self, mock_app_controller, temp_storage_path):
        """创建优化控制器实例 / Create refinement controller instance"""
        with patch('src.services.refinement_controller.ConversationStore') as mock_conv_store, \
             patch('src.services.refinement_controller.VersionStore') as mock_ver_store:
            
            # 配置mock存储
            mock_conv_store.return_value.save_session.return_value = True
            mock_ver_store.return_value.save_version.return_value = True
            mock_ver_store.return_value.list_versions.return_value = []
            
            controller = RefinementController(mock_app_controller)
            return controller
    
    def test_start_refinement_session(self, refinement_controller):
        """测试启动优化会话 / Test start refinement session"""
        initial_content = "这是初始内容"
        user_id = "test_user"
        
        session_id = refinement_controller.start_refinement_session(initial_content, user_id)
        
        # 验证会话ID格式
        assert session_id.startswith("session_")
        assert len(session_id) == 16  # "session_" + 8位hex
        
        # 验证会话已保存到内存
        assert session_id in refinement_controller.active_sessions
        
        session = refinement_controller.active_sessions[session_id]
        assert session.user_id == user_id
        assert session.initial_content == initial_content
        assert session.current_content == initial_content
        assert session.status == "active"
    
    def test_process_user_message(self, refinement_controller):
        """测试处理用户消息 / Test process user message"""
        # 先创建会话
        session_id = refinement_controller.start_refinement_session("初始内容", "test_user")
        
        # 处理用户消息
        message = "请添加更多细节"
        result = refinement_controller.process_user_message(message, session_id)
        
        # 验证处理结果
        assert result["success"] is True
        assert "response" in result
        assert "modified_content" in result
        assert message in result["response"]
    
    def test_process_user_message_invalid_session(self, refinement_controller):
        """测试处理无效会话的用户消息 / Test process user message with invalid session"""
        # 确保存储返回None表示会话不存在
        refinement_controller.conversation_store.load_session.return_value = None
        
        result = refinement_controller.process_user_message("测试消息", "invalid_session")
        
        assert result["success"] is False
        assert "error" in result
        assert "会话不存在" in result["error"]
    
    def test_apply_modification(self, refinement_controller):
        """测试应用修改 / Test apply modification"""
        # 先创建会话
        session_id = refinement_controller.start_refinement_session("初始内容", "test_user")
        
        # 应用修改
        modification = {
            "type": ModificationType.CONTENT_ADDITION.value,
            "description": "添加详细信息"
        }
        
        modified_content = refinement_controller.apply_modification(modification, session_id)
        
        # 验证修改结果
        assert modified_content is not None
        assert isinstance(modified_content, str)
    
    def test_get_version_history(self, refinement_controller):
        """测试获取版本历史 / Test get version history"""
        # 先创建会话
        session_id = refinement_controller.start_refinement_session("初始内容", "test_user")
        
        # 获取版本历史
        history = refinement_controller.get_version_history(session_id)
        
        # 验证历史记录格式
        assert isinstance(history, list)
        # 由于mock返回空列表，这里验证不会出错
    
    def test_revert_to_version(self, refinement_controller):
        """测试回退到版本 / Test revert to version"""
        # 先创建会话
        session_id = refinement_controller.start_refinement_session("初始内容", "test_user")
        
        # 模拟版本存在
        from src.models.refinement_models import ContentVersion
        mock_version = ContentVersion(
            id="version_001",
            session_id=session_id,
            content="版本内容",
            version_number=1,
            parent_version_id=None,
            modification_type=ModificationType.STRUCTURAL.value,
            modification_description="测试版本",
            created_at=datetime.now(),
            is_milestone=False,
            metadata={}
        )
        
        refinement_controller.version_store.load_version.return_value = mock_version
        
        # 回退到版本
        reverted_content = refinement_controller.revert_to_version(session_id, "version_001")
        
        # 验证回退结果
        assert reverted_content == "版本内容"
        
        # 验证会话内容已更新
        session = refinement_controller.active_sessions[session_id]
        assert session.current_content == "版本内容"
    
    def test_revert_to_nonexistent_version(self, refinement_controller):
        """测试回退到不存在的版本 / Test revert to nonexistent version"""
        # 先创建会话
        session_id = refinement_controller.start_refinement_session("初始内容", "test_user")
        
        # 模拟版本不存在
        refinement_controller.version_store.load_version.return_value = None
        
        # 尝试回退应该抛出异常
        with pytest.raises(ValueError, match="版本不存在"):
            refinement_controller.revert_to_version(session_id, "nonexistent_version")
    
    def test_get_session_status(self, refinement_controller):
        """测试获取会话状态 / Test get session status"""
        # 先创建会话
        session_id = refinement_controller.start_refinement_session("初始内容", "test_user")
        
        # 获取会话状态
        status = refinement_controller.get_session_status(session_id)
        
        # 验证状态信息
        assert status["exists"] is True
        assert status["status"] == "active"
        assert "created_at" in status
        assert "updated_at" in status
        assert "version_count" in status
        assert "current_version" in status
    
    def test_get_nonexistent_session_status(self, refinement_controller):
        """测试获取不存在会话的状态 / Test get nonexistent session status"""
        # 确保存储返回None表示会话不存在
        refinement_controller.conversation_store.load_session.return_value = None
        
        status = refinement_controller.get_session_status("nonexistent_session")
        
        assert status["exists"] is False
    
    def test_cleanup_inactive_sessions(self, refinement_controller):
        """测试清理不活跃会话 / Test cleanup inactive sessions"""
        # 创建一个会话
        session_id = refinement_controller.start_refinement_session("初始内容", "test_user")
        
        # 修改会话时间为很久以前
        session = refinement_controller.active_sessions[session_id]
        session.updated_at = datetime.now() - timedelta(hours=25)
        
        # 清理不活跃会话（24小时）
        cleaned_count = refinement_controller.cleanup_inactive_sessions(24)
        
        # 验证清理结果
        assert cleaned_count == 1
        assert session_id not in refinement_controller.active_sessions
    
    def test_get_session_from_storage(self, refinement_controller):
        """测试从存储中获取会话 / Test get session from storage"""
        from src.models.refinement_models import ConversationSession
        
        # 模拟从存储加载会话
        mock_session = ConversationSession(
            id="stored_session",
            user_id="test_user",
            initial_content="存储的内容",
            current_content="存储的内容",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status="active",
            context_summary="",
            preferences={}
        )
        
        refinement_controller.conversation_store.load_session.return_value = mock_session
        
        # 获取会话（不在内存中）
        session = refinement_controller._get_session("stored_session")
        
        # 验证会话已加载到内存
        assert session is not None
        assert session.id == "stored_session"
        assert "stored_session" in refinement_controller.active_sessions