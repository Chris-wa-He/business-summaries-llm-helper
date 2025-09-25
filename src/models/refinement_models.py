"""
交互式内容优化数据模型 / Interactive Content Refinement Data Models

定义交互式内容优化功能的核心数据结构
Defines core data structures for interactive content refinement functionality
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import json
import uuid


class ModificationType(Enum):
    """修改类型枚举 / Modification Type Enumeration"""
    STRUCTURAL = "structural"
    CONTENT_ADDITION = "content_addition"
    CONTENT_REMOVAL = "content_removal"
    STYLE_ADJUSTMENT = "style_adjustment"
    FORMAT_MODIFICATION = "format_modification"
    LANGUAGE_OPTIMIZATION = "language_optimization"


class ImpactLevel(Enum):
    """影响级别枚举 / Impact Level Enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ConversationMessage:
    """对话消息模型 / Conversation Message Model"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    sender: str = ""  # 'user' or 'ai'
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    message_type: str = "text"  # 'text', 'modification_request', 'system'
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式 / Convert to dictionary format"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "sender": self.sender,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "message_type": self.message_type,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationMessage":
        """从字典创建实例 / Create instance from dictionary"""
        data = data.copy()
        if "timestamp" in data and isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)

    def validate(self) -> bool:
        """验证消息数据 / Validate message data"""
        return (
            bool(self.id) and
            bool(self.session_id) and
            self.sender in ["user", "ai"] and
            bool(self.content.strip()) and
            self.message_type in ["text", "modification_request", "system"]
        )


@dataclass
class ConversationSession:
    """对话会话模型 / Conversation Session Model"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    initial_content: str = ""
    current_content: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    status: str = "active"  # 'active', 'paused', 'completed'
    context_summary: str = ""
    preferences: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式 / Convert to dictionary format"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "initial_content": self.initial_content,
            "current_content": self.current_content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status,
            "context_summary": self.context_summary,
            "preferences": self.preferences
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationSession":
        """从字典创建实例 / Create instance from dictionary"""
        data = data.copy()
        for field_name in ["created_at", "updated_at"]:
            if field_name in data and isinstance(data[field_name], str):
                data[field_name] = datetime.fromisoformat(data[field_name])
        return cls(**data)

    def validate(self) -> bool:
        """验证会话数据 / Validate session data"""
        return (
            bool(self.id) and
            bool(self.user_id) and
            bool(self.initial_content.strip()) and
            self.status in ["active", "paused", "completed"]
        )


@dataclass
class ContentVersion:
    """内容版本模型 / Content Version Model"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    content: str = ""
    version_number: int = 1
    parent_version_id: Optional[str] = None
    modification_type: str = ModificationType.CONTENT_ADDITION.value
    modification_description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    is_milestone: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式 / Convert to dictionary format"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "content": self.content,
            "version_number": self.version_number,
            "parent_version_id": self.parent_version_id,
            "modification_type": self.modification_type,
            "modification_description": self.modification_description,
            "created_at": self.created_at.isoformat(),
            "is_milestone": self.is_milestone,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContentVersion":
        """从字典创建实例 / Create instance from dictionary"""
        data = data.copy()
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)

    def validate(self) -> bool:
        """验证版本数据 / Validate version data"""
        return (
            bool(self.id) and
            bool(self.session_id) and
            bool(self.content.strip()) and
            self.version_number > 0 and
            self.modification_type in [t.value for t in ModificationType]
        )


@dataclass
class ModificationPlan:
    """修改计划模型 / Modification Plan Model"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request: str = ""
    modification_type: ModificationType = ModificationType.CONTENT_ADDITION
    target_sections: List[str] = field(default_factory=list)
    instructions: List[str] = field(default_factory=list)
    estimated_impact: ImpactLevel = ImpactLevel.MEDIUM
    confidence_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式 / Convert to dictionary format"""
        return {
            "id": self.id,
            "request": self.request,
            "modification_type": self.modification_type.value,
            "target_sections": self.target_sections,
            "instructions": self.instructions,
            "estimated_impact": self.estimated_impact.value,
            "confidence_score": self.confidence_score
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModificationPlan":
        """从字典创建实例 / Create instance from dictionary"""
        data = data.copy()
        if "modification_type" in data and isinstance(data["modification_type"], str):
            data["modification_type"] = ModificationType(data["modification_type"])
        if "estimated_impact" in data and isinstance(data["estimated_impact"], str):
            data["estimated_impact"] = ImpactLevel(data["estimated_impact"])
        return cls(**data)

    def validate(self) -> bool:
        """验证修改计划数据 / Validate modification plan data"""
        return (
            bool(self.id) and
            bool(self.request.strip()) and
            isinstance(self.modification_type, ModificationType) and
            isinstance(self.estimated_impact, ImpactLevel) and
            0.0 <= self.confidence_score <= 1.0
        )


@dataclass
class VersionDiff:
    """版本差异模型 / Version Diff Model"""
    version1_id: str = ""
    version2_id: str = ""
    additions: List[str] = field(default_factory=list)
    deletions: List[str] = field(default_factory=list)
    modifications: List[Dict[str, str]] = field(default_factory=list)
    similarity_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式 / Convert to dictionary format"""
        return {
            "version1_id": self.version1_id,
            "version2_id": self.version2_id,
            "additions": self.additions,
            "deletions": self.deletions,
            "modifications": self.modifications,
            "similarity_score": self.similarity_score
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VersionDiff":
        """从字典创建实例 / Create instance from dictionary"""
        return cls(**data)

    def validate(self) -> bool:
        """验证版本差异数据 / Validate version diff data"""
        return (
            bool(self.version1_id) and
            bool(self.version2_id) and
            0.0 <= self.similarity_score <= 1.0
        )


@dataclass
class UserPreferenceProfile:
    """用户偏好档案 / User Preference Profile"""
    user_id: str = ""
    prompt_name: str = ""
    modification_preferences: Dict[str, float] = field(default_factory=dict)
    style_preferences: Dict[str, Any] = field(default_factory=dict)
    interaction_patterns: Dict[str, Any] = field(default_factory=dict)
    content_structure_preferences: Dict[str, Any] = field(default_factory=dict)
    success_history: List[Dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式 / Convert to dictionary format"""
        return {
            "user_id": self.user_id,
            "prompt_name": self.prompt_name,
            "modification_preferences": self.modification_preferences,
            "style_preferences": self.style_preferences,
            "interaction_patterns": self.interaction_patterns,
            "content_structure_preferences": self.content_structure_preferences,
            "success_history": self.success_history,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserPreferenceProfile":
        """从字典创建实例 / Create instance from dictionary"""
        data = data.copy()
        for field_name in ["created_at", "updated_at"]:
            if field_name in data and isinstance(data[field_name], str):
                data[field_name] = datetime.fromisoformat(data[field_name])
        return cls(**data)

    def validate(self) -> bool:
        """验证用户偏好数据 / Validate user preference data"""
        return (
            bool(self.user_id) and
            bool(self.prompt_name) and
            isinstance(self.modification_preferences, dict) and
            isinstance(self.style_preferences, dict)
        )