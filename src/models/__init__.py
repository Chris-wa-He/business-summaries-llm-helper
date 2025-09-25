"""
数据模型模块 / Data Models Module

提供交互式内容优化功能的核心数据模型
Provides core data models for interactive content refinement functionality
"""

from .refinement_models import (
    ConversationMessage,
    ConversationSession,
    ContentVersion,
    ModificationPlan,
    ModificationType,
    ImpactLevel,
    VersionDiff,
    UserPreferenceProfile
)

__all__ = [
    "ConversationMessage",
    "ConversationSession", 
    "ContentVersion",
    "ModificationPlan",
    "ModificationType",
    "ImpactLevel",
    "VersionDiff",
    "UserPreferenceProfile"
]