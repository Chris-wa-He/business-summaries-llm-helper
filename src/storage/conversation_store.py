"""
对话存储模块 / Conversation Storage Module

提供对话会话和消息的持久化存储功能。
Provides persistent storage functionality for conversation sessions and messages.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from ..models.refinement_models import ConversationSession, ConversationMessage


logger = logging.getLogger(__name__)


class ConversationStore:
    """对话存储类 / Conversation Storage Class"""
    
    def __init__(self, storage_path: str = "./data/conversations"):
        """
        初始化对话存储 / Initialize conversation storage
        
        Args:
            storage_path: 存储路径 / Storage path
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
    def save_session(self, session: ConversationSession) -> bool:
        """
        保存对话会话 / Save conversation session
        
        Args:
            session: 对话会话对象 / Conversation session object
            
        Returns:
            保存是否成功 / Whether save was successful
        """
        try:
            session_file = self.storage_path / f"{session.id}.json"
            session_data = session.to_dict()
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"保存对话会话成功: {session.id}")
            return True
            
        except Exception as e:
            logger.error(f"保存对话会话失败: {session.id}, 错误: {e}")
            return False
    
    def load_session(self, session_id: str) -> Optional[ConversationSession]:
        """
        加载对话会话 / Load conversation session
        
        Args:
            session_id: 会话ID / Session ID
            
        Returns:
            对话会话对象或None / Conversation session object or None
        """
        try:
            session_file = self.storage_path / f"{session_id}.json"
            
            if not session_file.exists():
                logger.warning(f"对话会话文件不存在: {session_id}")
                return None
            
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            session = ConversationSession.from_dict(session_data)
            logger.info(f"加载对话会话成功: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"加载对话会话失败: {session_id}, 错误: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除对话会话 / Delete conversation session
        
        Args:
            session_id: 会话ID / Session ID
            
        Returns:
            删除是否成功 / Whether deletion was successful
        """
        try:
            session_file = self.storage_path / f"{session_id}.json"
            
            if session_file.exists():
                session_file.unlink()
                logger.info(f"删除对话会话成功: {session_id}")
                return True
            else:
                logger.warning(f"对话会话文件不存在: {session_id}")
                return False
                
        except Exception as e:
            logger.error(f"删除对话会话失败: {session_id}, 错误: {e}")
            return False
    
    def list_sessions(self, user_id: Optional[str] = None) -> List[str]:
        """
        列出对话会话 / List conversation sessions
        
        Args:
            user_id: 用户ID，如果提供则只返回该用户的会话 / User ID, if provided only return sessions for this user
            
        Returns:
            会话ID列表 / List of session IDs
        """
        try:
            session_ids = []
            
            for session_file in self.storage_path.glob("*.json"):
                session_id = session_file.stem
                
                # 如果指定了用户ID，需要检查会话是否属于该用户
                if user_id:
                    session = self.load_session(session_id)
                    if session and session.user_id == user_id:
                        session_ids.append(session_id)
                else:
                    session_ids.append(session_id)
            
            return session_ids
            
        except Exception as e:
            logger.error(f"列出对话会话失败, 错误: {e}")
            return []
    
    def cleanup_old_sessions(self, days: int = 30) -> int:
        """
        清理旧的对话会话 / Cleanup old conversation sessions
        
        Args:
            days: 保留天数 / Days to keep
            
        Returns:
            清理的会话数量 / Number of sessions cleaned up
        """
        try:
            cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
            cleaned_count = 0
            
            for session_file in self.storage_path.glob("*.json"):
                if session_file.stat().st_mtime < cutoff_time:
                    session_file.unlink()
                    cleaned_count += 1
                    logger.info(f"清理旧会话: {session_file.stem}")
            
            logger.info(f"清理完成，共清理 {cleaned_count} 个旧会话")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"清理旧会话失败, 错误: {e}")
            return 0