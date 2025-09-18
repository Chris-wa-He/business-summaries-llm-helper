"""
交互式内容优化数据模型测试 / Interactive Content Refinement Data Models Tests
"""

import pytest
from datetime import datetime
from src.models.refinement_models import (
    ConversationMessage,
    ConversationSession,
    ContentVersion,
    ModificationPlan,
    ModificationType,
    ImpactLevel,
    VersionDiff,
    UserPreferenceProfile
)


class TestConversationMessage:
    """对话消息模型测试 / Conversation Message Model Tests"""

    def test_create_message_with_defaults(self):
        """测试使用默认值创建消息 / Test creating message with defaults"""
        message = ConversationMessage(
            session_id="test_session",
            sender="user",
            content="测试消息"
        )
        
        assert message.session_id == "test_session"
        assert message.sender == "user"
        assert message.content == "测试消息"
        assert message.message_type == "text"
        assert isinstance(message.timestamp, datetime)
        assert len(message.id) > 0

    def test_message_validation_success(self):
        """测试消息验证成功 / Test message validation success"""
        message = ConversationMessage(
            session_id="test_session",
            sender="user",
            content="测试消息",
            message_type="text"
        )
        
        assert message.validate() is True

    def test_message_validation_failure(self):
        """测试消息验证失败 / Test message validation failure"""
        # 空内容
        message = ConversationMessage(
            session_id="test_session",
            sender="user",
            content=""
        )
        assert message.validate() is False
        
        # 无效发送者
        message = ConversationMessage(
            session_id="test_session",
            sender="invalid",
            content="测试消息"
        )
        assert message.validate() is False

    def test_message_serialization(self):
        """测试消息序列化 / Test message serialization"""
        message = ConversationMessage(
            session_id="test_session",
            sender="user",
            content="测试消息"
        )
        
        # 转换为字典
        data = message.to_dict()
        assert isinstance(data, dict)
        assert data["session_id"] == "test_session"
        assert data["sender"] == "user"
        assert data["content"] == "测试消息"
        
        # 从字典恢复
        restored_message = ConversationMessage.from_dict(data)
        assert restored_message.session_id == message.session_id
        assert restored_message.sender == message.sender
        assert restored_message.content == message.content


class TestConversationSession:
    """对话会话模型测试 / Conversation Session Model Tests"""

    def test_create_session_with_defaults(self):
        """测试使用默认值创建会话 / Test creating session with defaults"""
        session = ConversationSession(
            user_id="test_user",
            initial_content="初始内容"
        )
        
        assert session.user_id == "test_user"
        assert session.initial_content == "初始内容"
        assert session.status == "active"
        assert isinstance(session.created_at, datetime)
        assert len(session.id) > 0

    def test_session_validation_success(self):
        """测试会话验证成功 / Test session validation success"""
        session = ConversationSession(
            user_id="test_user",
            initial_content="初始内容",
            status="active"
        )
        
        assert session.validate() is True

    def test_session_validation_failure(self):
        """测试会话验证失败 / Test session validation failure"""
        # 空用户ID
        session = ConversationSession(
            user_id="",
            initial_content="初始内容"
        )
        assert session.validate() is False
        
        # 无效状态
        session = ConversationSession(
            user_id="test_user",
            initial_content="初始内容",
            status="invalid"
        )
        assert session.validate() is False


class TestContentVersion:
    """内容版本模型测试 / Content Version Model Tests"""

    def test_create_version_with_defaults(self):
        """测试使用默认值创建版本 / Test creating version with defaults"""
        version = ContentVersion(
            session_id="test_session",
            content="版本内容"
        )
        
        assert version.session_id == "test_session"
        assert version.content == "版本内容"
        assert version.version_number == 1
        assert version.modification_type == ModificationType.CONTENT_ADDITION.value
        assert isinstance(version.created_at, datetime)

    def test_version_validation_success(self):
        """测试版本验证成功 / Test version validation success"""
        version = ContentVersion(
            session_id="test_session",
            content="版本内容",
            version_number=2,
            modification_type=ModificationType.STYLE_ADJUSTMENT.value
        )
        
        assert version.validate() is True

    def test_version_validation_failure(self):
        """测试版本验证失败 / Test version validation failure"""
        # 版本号为0
        version = ContentVersion(
            session_id="test_session",
            content="版本内容",
            version_number=0
        )
        assert version.validate() is False
        
        # 无效修改类型
        version = ContentVersion(
            session_id="test_session",
            content="版本内容",
            modification_type="invalid_type"
        )
        assert version.validate() is False


class TestModificationPlan:
    """修改计划模型测试 / Modification Plan Model Tests"""

    def test_create_plan_with_defaults(self):
        """测试使用默认值创建修改计划 / Test creating plan with defaults"""
        plan = ModificationPlan(
            request="请添加更多细节"
        )
        
        assert plan.request == "请添加更多细节"
        assert plan.modification_type == ModificationType.CONTENT_ADDITION
        assert plan.estimated_impact == ImpactLevel.MEDIUM
        assert plan.confidence_score == 0.0

    def test_plan_validation_success(self):
        """测试修改计划验证成功 / Test plan validation success"""
        plan = ModificationPlan(
            request="请添加更多细节",
            modification_type=ModificationType.CONTENT_ADDITION,
            confidence_score=0.8
        )
        
        assert plan.validate() is True

    def test_plan_validation_failure(self):
        """测试修改计划验证失败 / Test plan validation failure"""
        # 置信度超出范围
        plan = ModificationPlan(
            request="请添加更多细节",
            confidence_score=1.5
        )
        assert plan.validate() is False


class TestVersionDiff:
    """版本差异模型测试 / Version Diff Model Tests"""

    def test_create_diff_with_defaults(self):
        """测试使用默认值创建版本差异 / Test creating diff with defaults"""
        diff = VersionDiff(
            version1_id="v1",
            version2_id="v2"
        )
        
        assert diff.version1_id == "v1"
        assert diff.version2_id == "v2"
        assert diff.similarity_score == 0.0
        assert len(diff.additions) == 0

    def test_diff_validation_success(self):
        """测试版本差异验证成功 / Test diff validation success"""
        diff = VersionDiff(
            version1_id="v1",
            version2_id="v2",
            similarity_score=0.85
        )
        
        assert diff.validate() is True

    def test_diff_validation_failure(self):
        """测试版本差异验证失败 / Test diff validation failure"""
        # 相似度超出范围
        diff = VersionDiff(
            version1_id="v1",
            version2_id="v2",
            similarity_score=1.5
        )
        assert diff.validate() is False


class TestUserPreferenceProfile:
    """用户偏好档案模型测试 / User Preference Profile Model Tests"""

    def test_create_profile_with_defaults(self):
        """测试使用默认值创建偏好档案 / Test creating profile with defaults"""
        profile = UserPreferenceProfile(
            user_id="test_user",
            prompt_name="default"
        )
        
        assert profile.user_id == "test_user"
        assert profile.prompt_name == "default"
        assert isinstance(profile.modification_preferences, dict)
        assert isinstance(profile.created_at, datetime)

    def test_profile_validation_success(self):
        """测试偏好档案验证成功 / Test profile validation success"""
        profile = UserPreferenceProfile(
            user_id="test_user",
            prompt_name="default",
            modification_preferences={"structural": 0.8},
            style_preferences={"formality": "professional"}
        )
        
        assert profile.validate() is True

    def test_profile_validation_failure(self):
        """测试偏好档案验证失败 / Test profile validation failure"""
        # 空用户ID
        profile = UserPreferenceProfile(
            user_id="",
            prompt_name="default"
        )
        assert profile.validate() is False

    def test_profile_serialization(self):
        """测试偏好档案序列化 / Test profile serialization"""
        profile = UserPreferenceProfile(
            user_id="test_user",
            prompt_name="default",
            modification_preferences={"structural": 0.8}
        )
        
        # 转换为字典
        data = profile.to_dict()
        assert isinstance(data, dict)
        assert data["user_id"] == "test_user"
        assert data["modification_preferences"]["structural"] == 0.8
        
        # 从字典恢复
        restored_profile = UserPreferenceProfile.from_dict(data)
        assert restored_profile.user_id == profile.user_id
        assert restored_profile.modification_preferences == profile.modification_preferences


class TestEnumTypes:
    """枚举类型测试 / Enum Types Tests"""

    def test_modification_type_enum(self):
        """测试修改类型枚举 / Test modification type enum"""
        assert ModificationType.STRUCTURAL.value == "structural"
        assert ModificationType.CONTENT_ADDITION.value == "content_addition"
        assert ModificationType.STYLE_ADJUSTMENT.value == "style_adjustment"

    def test_impact_level_enum(self):
        """测试影响级别枚举 / Test impact level enum"""
        assert ImpactLevel.LOW.value == "low"
        assert ImpactLevel.MEDIUM.value == "medium"
        assert ImpactLevel.HIGH.value == "high"
        assert ImpactLevel.CRITICAL.value == "critical"