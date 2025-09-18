"""
优化控制器模块 / Refinement Controller Module

提供交互式内容优化功能的核心控制器。
Provides core controller for interactive content refinement functionality.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class RefinementController:
    """交互式内容优化控制器 / Interactive content refinement controller"""
    
    def __init__(self, app_controller):
        """
        初始化优化控制器 / Initialize refinement controller
        
        Args:
            app_controller: 应用控制器实例 / Application controller instance
        """
        self.app_controller = app_controller
        self.active_sessions: Dict[str, Dict] = {}
        
        logger.info("RefinementController initialized")
    
    def start_refinement_session(self, initial_content: str, user_id: str, original_context: Optional[str] = None) -> str:
        """
        启动优化会话 / Start refinement session
        
        Args:
            initial_content: 初始内容 / Initial content
            user_id: 用户ID / User ID
            original_context: 原始上下文（生成总结时的原始输入） / Original context (original input when generating summary)
            
        Returns:
            会话ID / Session ID
        """
        try:
            session_id = str(uuid.uuid4())
            
            # 创建简化的会话对象 / Create simplified session object
            session = {
                "id": session_id,
                "user_id": user_id,
                "initial_content": initial_content,
                "current_content": initial_content,
                "original_context": original_context,  # 保存原始上下文
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "status": "active",
                "messages": []
            }
            
            # 保存到内存 / Save to memory
            self.active_sessions[session_id] = session
            
            logger.info(f"Started refinement session: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to start refinement session: {e}")
            raise
    
    def process_user_message(self, message: str, session_id: str, model_id: Optional[str] = None) -> Dict[str, Any]:
        """
        处理用户消息 / Process user message
        
        Args:
            message: 用户消息 / User message
            session_id: 会话ID / Session ID
            model_id: 模型ID / Model ID (optional)
            
        Returns:
            处理结果 / Processing result
        """
        try:
            # 获取会话 / Get session
            session = self.active_sessions.get(session_id)
            if not session:
                raise ValueError(f"Session not found: {session_id}")
            
            # 获取当前激活的system prompt / Get current active system prompt
            active_prompt_info = self.app_controller.get_active_prompt()
            system_prompt = active_prompt_info.get('content') if active_prompt_info else None
            
            # 构建优化message，保持"生成案例总结"的message结构 / Build optimization message maintaining "generate case summary" message structure
            # 在原始案例输入基础上添加已生成内容和用户优化要求 / Add generated content and user optimization requirements to original case input
            original_case = session.get('original_context') or ''
            current_summary = session.get('current_content') or ''
            
            # 构建完整的案例输入，包含原始案例、已生成总结和优化要求 / Build complete case input with original case, generated summary and optimization requirements
            enhanced_case_input = f"""需要总结的案例：
{original_case}

已生成的总结内容：
{current_summary}

用户的优化要求：
{message}

请根据用户的要求对已生成的总结内容进行优化和修改，保持内容的专业性和结构化。直接返回修改后的完整内容。"""
            
            # 使用默认模型如果没有指定 / Use default model if not specified
            if not model_id:
                model_id = self.app_controller.get_default_model()
            
            # 调用AI模型进行内容修改，使用相同的process_case_summary方法 / Call AI model for content modification using same process_case_summary method
            try:
                modified_content = self.app_controller.process_case_summary(
                    case_input=enhanced_case_input,
                    model_id=model_id,
                    custom_system_prompt=system_prompt  # 使用界面选定的system prompt
                )
                
                # 更新会话内容 / Update session content
                session["current_content"] = modified_content
                
                ai_response = f"已根据您的要求优化内容：{message}"
                
            except Exception as e:
                logger.error(f"AI model call failed: {e}")
                ai_response = f"抱歉，处理您的修改请求时出现错误：{str(e)}"
                modified_content = session["current_content"]  # 保持原内容不变
            
            # 保存消息到会话 / Save message to session
            session["messages"].append({
                "user": message,
                "ai": ai_response,
                "timestamp": datetime.now()
            })
            
            # 更新会话 / Update session
            session["updated_at"] = datetime.now()
            
            return {
                "success": True,
                "response": ai_response,
                "modified_content": session["current_content"],
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Failed to process user message: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    def get_version_history(self, session_id: str) -> List[Dict]:
        """
        获取版本历史 / Get version history
        
        Args:
            session_id: 会话ID / Session ID
            
        Returns:
            版本历史列表 / Version history list
        """
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return []
            
            # 返回简化的版本历史 / Return simplified version history
            return [
                {
                    "id": "v1",
                    "version_number": 1,
                    "modification_type": "initial",
                    "description": "Initial content",
                    "created_at": session["created_at"].isoformat(),
                    "is_milestone": True
                }
            ]
        except Exception as e:
            logger.error(f"Failed to get version history: {e}")
            return []
    
    def revert_to_version(self, session_id: str, version_id: str) -> str:
        """
        回退到指定版本 / Revert to specified version
        
        Args:
            session_id: 会话ID / Session ID
            version_id: 版本ID / Version ID
            
        Returns:
            回退后的内容 / Content after revert
        """
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                raise ValueError(f"Session not found: {session_id}")
            
            # 简化处理，回退到初始内容 / Simplified handling, revert to initial content
            session["current_content"] = session["initial_content"]
            session["updated_at"] = datetime.now()
            
            logger.info(f"Reverted session {session_id} to version {version_id}")
            return session["current_content"]
            
        except Exception as e:
            logger.error(f"Failed to revert to version: {e}")
            raise