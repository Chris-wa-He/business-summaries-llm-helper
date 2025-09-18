"""
对话存储测试 / Conversation Store Tests
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.storage.conversation_store import ConversationStore
from src.models.refinement_models import ConversationSession, ConversationMessage


class TestConversationStore:
    """对话存储测试类 / Conversation Store Test Class"""
    
    @pytest.fixture
    def temp_storage_path(self):
        """创建临时存储路径 / Create temporary storage path"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def conversation_store(self, temp_storage_path):
        """创建对话存储实例 / Create conversation store instance"""
        return ConversationStore(temp_storage_path)
    
    @pytest.fixture
    def sample_session(self):
        """创建示例会话 / Create sample session"""
        return ConversationSession(
            id="test_session_001",
            user_id="test_user",
            initial_content="初始内容",
            current_content="当前内容",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status="active",
            context_summary="上下文摘要",
            preferences={"style": "formal"}
        )
    
    def test_save_and_load_session(self, conversation_store, sample_session):
        """测试保存和加载会话 / Test save and load session"""
        # 保存会话
        assert conversation_store.save_session(sample_session) is True
        
        # 加载会话
        loaded_session = conversation_store.load_session(sample_session.id)
        assert loaded_session is not None
        assert loaded_session.id == sample_session.id
        assert loaded_session.user_id == sample_session.user_id
        assert loaded_session.initial_content == sample_session.initial_content
        assert loaded_session.status == sample_session.status
    
    def test_load_nonexistent_session(self, conversation_store):
        """测试加载不存在的会话 / Test load nonexistent session"""
        result = conversation_store.load_session("nonexistent_session")
        assert result is None
    
    def test_delete_session(self, conversation_store, sample_session):
        """测试删除会话 / Test delete session"""
        # 先保存会话
        conversation_store.save_session(sample_session)
        
        # 删除会话
        assert conversation_store.delete_session(sample_session.id) is True
        
        # 验证会话已被删除
        assert conversation_store.load_session(sample_session.id) is None
        
        # 删除不存在的会话
        assert conversation_store.delete_session("nonexistent") is False
    
    def test_list_sessions(self, conversation_store):
        """测试列出会话 / Test list sessions"""
        # 创建多个会话
        sessions = []
        for i in range(3):
            session = ConversationSession(
                id=f"session_{i}",
                user_id=f"user_{i % 2}",  # 两个用户
                initial_content=f"内容 {i}",
                current_content=f"内容 {i}",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                status="active",
                context_summary="",
                preferences={}
            )
            sessions.append(session)
            conversation_store.save_session(session)
        
        # 列出所有会话
        all_sessions = conversation_store.list_sessions()
        assert len(all_sessions) == 3
        
        # 列出特定用户的会话
        user_0_sessions = conversation_store.list_sessions("user_0")
        assert len(user_0_sessions) == 2  # session_0 和 session_2
        
        user_1_sessions = conversation_store.list_sessions("user_1")
        assert len(user_1_sessions) == 1  # session_1
    
    def test_cleanup_old_sessions(self, conversation_store, temp_storage_path):
        """测试清理旧会话 / Test cleanup old sessions"""
        # 创建一个会话文件
        session_file = Path(temp_storage_path) / "old_session.json"
        session_file.write_text('{"id": "old_session"}')
        
        # 修改文件时间为很久以前
        import os
        import time
        old_time = time.time() - (40 * 24 * 3600)  # 40天前
        os.utime(session_file, (old_time, old_time))
        
        # 清理旧会话（保留30天）
        cleaned_count = conversation_store.cleanup_old_sessions(30)
        assert cleaned_count == 1
        assert not session_file.exists()
    
    def test_storage_directory_creation(self, temp_storage_path):
        """测试存储目录创建 / Test storage directory creation"""
        storage_path = Path(temp_storage_path) / "new_conversations"
        assert not storage_path.exists()
        
        # 创建存储实例应该自动创建目录
        ConversationStore(str(storage_path))
        assert storage_path.exists()
        assert storage_path.is_dir()
    
    def test_invalid_session_data_handling(self, conversation_store, temp_storage_path):
        """测试无效会话数据处理 / Test invalid session data handling"""
        # 创建无效的JSON文件
        invalid_file = Path(temp_storage_path) / "invalid_session.json"
        invalid_file.write_text("invalid json content")
        
        # 尝试加载应该返回None
        result = conversation_store.load_session("invalid_session")
        assert result is None