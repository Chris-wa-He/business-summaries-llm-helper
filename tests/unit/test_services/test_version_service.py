"""
版本服务测试 / Version Service Tests
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.services.version_service import VersionService
from src.models.refinement_models import ContentVersion, ModificationType


class TestVersionService:
    """版本服务测试类 / Version Service Test Class"""
    
    @pytest.fixture
    def version_service(self):
        """创建版本服务实例 / Create version service instance"""
        with patch('src.services.version_service.VersionStore') as mock_store:
            service = VersionService()
            service.version_store = mock_store.return_value
            return service
    
    @pytest.fixture
    def sample_versions(self):
        """创建示例版本列表 / Create sample version list"""
        return [
            ContentVersion(
                id="ver_001",
                session_id="session_001",
                content="版本1内容",
                version_number=1,
                parent_version_id=None,
                modification_type=ModificationType.STRUCTURAL.value,
                modification_description="初始版本",
                created_at=datetime.now(),
                is_milestone=True,
                metadata={}
            ),
            ContentVersion(
                id="ver_002",
                session_id="session_001",
                content="版本2内容",
                version_number=2,
                parent_version_id="ver_001",
                modification_type=ModificationType.CONTENT_ADDITION.value,
                modification_description="添加内容",
                created_at=datetime.now(),
                is_milestone=False,
                metadata={}
            )
        ]
    
    def test_create_version(self, version_service, sample_versions):
        """测试创建版本 / Test create version"""
        # 模拟现有版本
        version_service.version_store.list_versions.return_value = sample_versions
        version_service.version_store.save_version.return_value = True
        
        session_id = "session_001"
        content = "新版本内容"
        modification_type = ModificationType.CONTENT_ADDITION.value
        
        version_id = version_service.create_version(session_id, content, modification_type)
        
        # 验证版本ID格式
        assert version_id.startswith("ver_")
        assert session_id[:8] in version_id
        
        # 验证保存被调用
        version_service.version_store.save_version.assert_called_once()
        
        # 验证版本号递增
        saved_version = version_service.version_store.save_version.call_args[0][0]
        assert saved_version.version_number == 3  # 应该是第3个版本
        assert saved_version.parent_version_id == "ver_002"  # 父版本应该是最后一个
    
    def test_create_first_version(self, version_service):
        """测试创建第一个版本 / Test create first version"""
        # 模拟没有现有版本
        version_service.version_store.list_versions.return_value = []
        version_service.version_store.save_version.return_value = True
        
        session_id = "session_new"
        content = "第一个版本"
        modification_type = ModificationType.STRUCTURAL.value
        
        version_id = version_service.create_version(session_id, content, modification_type)
        
        # 验证版本创建
        assert version_id is not None
        
        # 验证版本属性
        saved_version = version_service.version_store.save_version.call_args[0][0]
        assert saved_version.version_number == 1
        assert saved_version.parent_version_id is None
    
    def test_get_version_list(self, version_service, sample_versions):
        """测试获取版本列表 / Test get version list"""
        version_service.version_store.list_versions.return_value = sample_versions
        
        session_id = "session_001"
        versions = version_service.get_version_list(session_id)
        
        assert len(versions) == 2
        assert versions[0].version_number == 1
        assert versions[1].version_number == 2
        
        version_service.version_store.list_versions.assert_called_once_with(session_id)
    
    def test_get_version_content(self, version_service, sample_versions):
        """测试获取版本内容 / Test get version content"""
        version_service.version_store.load_version.return_value = sample_versions[0]
        
        # 模拟从版本ID提取会话ID
        with patch.object(version_service, '_extract_session_id_from_version') as mock_extract:
            mock_extract.return_value = "session_001"
            
            content = version_service.get_version_content("ver_001")
            
            assert content == "版本1内容"
            version_service.version_store.load_version.assert_called_once_with("session_001", "ver_001")
    
    def test_get_version_content_not_found(self, version_service):
        """测试获取不存在版本的内容 / Test get content for non-existent version"""
        version_service.version_store.load_version.return_value = None
        
        with patch.object(version_service, '_extract_session_id_from_version') as mock_extract:
            mock_extract.return_value = "session_001"
            
            with pytest.raises(ValueError, match="版本不存在"):
                version_service.get_version_content("ver_nonexistent")
    
    def test_compare_versions(self, version_service):
        """测试版本对比 / Test compare versions"""
        # 模拟获取版本内容
        with patch.object(version_service, 'get_version_content') as mock_get_content:
            mock_get_content.side_effect = ["内容A\n第二行", "内容B\n第二行\n第三行"]
            
            version_service.version_store.save_version_diff.return_value = True
            
            diff = version_service.compare_versions("ver_001", "ver_002")
            
            # 验证差异对象
            assert diff.version1_id == "ver_001"
            assert diff.version2_id == "ver_002"
            assert isinstance(diff.additions, list)
            assert isinstance(diff.deletions, list)
            assert 0.0 <= diff.similarity_score <= 1.0
            
            # 验证保存差异被调用
            version_service.version_store.save_version_diff.assert_called_once()
    
    def test_revert_to_version(self, version_service, sample_versions):
        """测试回退到版本 / Test revert to version"""
        target_version = sample_versions[0]
        version_service.version_store.load_version.return_value = target_version
        version_service.version_store.list_versions.return_value = sample_versions
        version_service.version_store.save_version.return_value = True
        
        session_id = "session_001"
        version_id = "ver_001"
        
        content = version_service.revert_to_version(session_id, version_id)
        
        # 验证返回的内容
        assert content == target_version.content
        
        # 验证创建了新版本（回退版本）
        assert version_service.version_store.save_version.call_count >= 1
    
    def test_create_milestone(self, version_service, sample_versions):
        """测试创建里程碑 / Test create milestone"""
        version = sample_versions[1]  # 非里程碑版本
        version_service.version_store.load_version.return_value = version
        version_service.version_store.save_version.return_value = True
        
        with patch.object(version_service, '_extract_session_id_from_version') as mock_extract:
            mock_extract.return_value = "session_001"
            
            result = version_service.create_milestone("ver_002", "重要里程碑")
            
            assert result is True
            
            # 验证版本被更新为里程碑
            version_service.version_store.save_version.assert_called_once()
            saved_version = version_service.version_store.save_version.call_args[0][0]
            assert saved_version.is_milestone is True
            assert saved_version.modification_description == "重要里程碑"
    
    def test_cleanup_old_versions(self, version_service):
        """测试清理旧版本 / Test cleanup old versions"""
        version_service.version_store.cleanup_old_versions.return_value = 5
        
        session_id = "session_001"
        cleaned_count = version_service.cleanup_old_versions(session_id, keep_count=10)
        
        assert cleaned_count == 5
        version_service.version_store.cleanup_old_versions.assert_called_once_with(session_id, 10)
    
    def test_get_version_statistics(self, version_service, sample_versions):
        """测试获取版本统计 / Test get version statistics"""
        version_service.version_store.list_versions.return_value = sample_versions
        
        session_id = "session_001"
        stats = version_service.get_version_statistics(session_id)
        
        # 验证统计信息
        assert stats["total_versions"] == 2
        assert stats["milestone_versions"] == 1  # 只有第一个版本是里程碑
        assert stats["latest_version"] == 2
        assert "first_created" in stats
        assert "last_modified" in stats
        assert "modification_types" in stats
        
        # 验证修改类型统计
        mod_types = stats["modification_types"]
        assert ModificationType.STRUCTURAL.value in mod_types
        assert ModificationType.CONTENT_ADDITION.value in mod_types
    
    def test_get_version_statistics_empty(self, version_service):
        """测试获取空版本列表的统计 / Test get statistics for empty version list"""
        version_service.version_store.list_versions.return_value = []
        
        stats = version_service.get_version_statistics("session_empty")
        
        assert stats == {}
    
    def test_calculate_diff(self, version_service):
        """测试计算差异 / Test calculate diff"""
        content1 = "第一行\n第二行\n第三行"
        content2 = "第一行\n修改的第二行\n第三行\n新增行"
        
        diff_result = version_service._calculate_diff(content1, content2)
        
        # 验证差异结果结构
        assert "additions" in diff_result
        assert "deletions" in diff_result
        assert "modifications" in diff_result
        assert "similarity_score" in diff_result
        
        # 验证相似度分数
        assert 0.0 <= diff_result["similarity_score"] <= 1.0
        
        # 验证有变化被检测到
        assert len(diff_result["additions"]) > 0 or len(diff_result["deletions"]) > 0
    
    def test_extract_session_id_from_version(self, version_service):
        """测试从版本ID提取会话ID / Test extract session ID from version ID"""
        version_id = "ver_20231201_143000_sess001"
        
        session_id = version_service._extract_session_id_from_version(version_id)
        
        assert session_id == "sess001"
    
    def test_extract_session_id_invalid_format(self, version_service):
        """测试无效格式的版本ID / Test invalid format version ID"""
        version_id = "invalid_format"
        
        session_id = version_service._extract_session_id_from_version(version_id)
        
        assert session_id is None
    
    def test_error_handling(self, version_service):
        """测试错误处理 / Test error handling"""
        # 模拟存储错误
        version_service.version_store.list_versions.side_effect = Exception("存储错误")
        
        # 获取版本列表应该返回空列表而不是抛出异常
        versions = version_service.get_version_list("session_001")
        assert versions == []
        
        # 获取统计信息应该返回空字典
        stats = version_service.get_version_statistics("session_001")
        assert stats == {}