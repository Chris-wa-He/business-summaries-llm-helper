"""
版本存储测试 / Version Store Tests
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.storage.version_store import VersionStore
from src.models.refinement_models import ContentVersion, VersionDiff, ModificationType


class TestVersionStore:
    """版本存储测试类 / Version Store Test Class"""
    
    @pytest.fixture
    def temp_storage_path(self):
        """创建临时存储路径 / Create temporary storage path"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def version_store(self, temp_storage_path):
        """创建版本存储实例 / Create version store instance"""
        return VersionStore(temp_storage_path)
    
    @pytest.fixture
    def sample_version(self):
        """创建示例版本 / Create sample version"""
        return ContentVersion(
            id="version_001",
            session_id="session_001",
            content="版本内容",
            version_number=1,
            parent_version_id=None,
            modification_type=ModificationType.CONTENT_ADDITION.value,
            modification_description="添加内容",
            created_at=datetime.now(),
            is_milestone=False,
            metadata={"author": "test_user"}
        )
    
    def test_save_and_load_version(self, version_store, sample_version):
        """测试保存和加载版本 / Test save and load version"""
        # 保存版本
        assert version_store.save_version(sample_version) is True
        
        # 加载版本
        loaded_version = version_store.load_version(
            sample_version.session_id, 
            sample_version.id
        )
        assert loaded_version is not None
        assert loaded_version.id == sample_version.id
        assert loaded_version.session_id == sample_version.session_id
        assert loaded_version.content == sample_version.content
        assert loaded_version.version_number == sample_version.version_number
    
    def test_load_nonexistent_version(self, version_store):
        """测试加载不存在的版本 / Test load nonexistent version"""
        result = version_store.load_version("session_001", "nonexistent_version")
        assert result is None
    
    def test_delete_version(self, version_store, sample_version):
        """测试删除版本 / Test delete version"""
        # 先保存版本
        version_store.save_version(sample_version)
        
        # 删除版本
        assert version_store.delete_version(
            sample_version.session_id, 
            sample_version.id
        ) is True
        
        # 验证版本已被删除
        assert version_store.load_version(
            sample_version.session_id, 
            sample_version.id
        ) is None
        
        # 删除不存在的版本
        assert version_store.delete_version("session_001", "nonexistent") is False
    
    def test_list_versions(self, version_store):
        """测试列出版本 / Test list versions"""
        session_id = "test_session"
        
        # 创建多个版本
        versions = []
        for i in range(3):
            version = ContentVersion(
                id=f"version_{i}",
                session_id=session_id,
                content=f"内容 {i}",
                version_number=i + 1,
                parent_version_id=f"version_{i-1}" if i > 0 else None,
                modification_type=ModificationType.CONTENT_ADDITION.value,
                modification_description=f"修改 {i}",
                created_at=datetime.now(),
                is_milestone=i == 1,  # 第二个版本是里程碑
                metadata={}
            )
            versions.append(version)
            version_store.save_version(version)
        
        # 列出版本
        loaded_versions = version_store.list_versions(session_id)
        assert len(loaded_versions) == 3
        
        # 验证按版本号排序
        for i, version in enumerate(loaded_versions):
            assert version.version_number == i + 1
    
    def test_get_latest_version(self, version_store):
        """测试获取最新版本 / Test get latest version"""
        session_id = "test_session"
        
        # 创建多个版本
        for i in range(3):
            version = ContentVersion(
                id=f"version_{i}",
                session_id=session_id,
                content=f"内容 {i}",
                version_number=i + 1,
                parent_version_id=None,
                modification_type=ModificationType.CONTENT_ADDITION.value,
                modification_description=f"修改 {i}",
                created_at=datetime.now(),
                is_milestone=False,
                metadata={}
            )
            version_store.save_version(version)
        
        # 获取最新版本
        latest_version = version_store.get_latest_version(session_id)
        assert latest_version is not None
        assert latest_version.version_number == 3
        assert latest_version.id == "version_2"
    
    def test_cleanup_old_versions(self, version_store):
        """测试清理旧版本 / Test cleanup old versions"""
        session_id = "test_session"
        
        # 创建多个版本，包括里程碑版本
        for i in range(10):
            version = ContentVersion(
                id=f"version_{i}",
                session_id=session_id,
                content=f"内容 {i}",
                version_number=i + 1,
                parent_version_id=None,
                modification_type=ModificationType.CONTENT_ADDITION.value,
                modification_description=f"修改 {i}",
                created_at=datetime.now(),
                is_milestone=(i == 2 or i == 5),  # 第3和第6个版本是里程碑
                metadata={}
            )
            version_store.save_version(version)
        
        # 清理旧版本，保留5个
        cleaned_count = version_store.cleanup_old_versions(session_id, keep_count=5)
        
        # 验证清理结果
        remaining_versions = version_store.list_versions(session_id)
        
        # 应该保留里程碑版本和最新的5个常规版本
        milestone_count = len([v for v in remaining_versions if v.is_milestone])
        assert milestone_count == 2  # 两个里程碑版本应该被保留
        
        # 清理数量应该大于0
        assert cleaned_count > 0
    
    def test_save_and_load_version_diff(self, version_store):
        """测试保存和加载版本差异 / Test save and load version diff"""
        # 创建版本差异
        diff = VersionDiff(
            version1_id="version_1",
            version2_id="version_2",
            additions=["新增行1", "新增行2"],
            deletions=["删除行1"],
            modifications=[{"old": "旧内容", "new": "新内容"}],
            similarity_score=0.85
        )
        
        # 保存差异
        assert version_store.save_version_diff(diff) is True
        
        # 加载差异
        loaded_diff = version_store.load_version_diff("version_1", "version_2")
        assert loaded_diff is not None
        assert loaded_diff.version1_id == diff.version1_id
        assert loaded_diff.version2_id == diff.version2_id
        assert loaded_diff.additions == diff.additions
        assert loaded_diff.deletions == diff.deletions
        assert loaded_diff.similarity_score == diff.similarity_score
    
    def test_storage_directory_structure(self, version_store, sample_version):
        """测试存储目录结构 / Test storage directory structure"""
        # 保存版本
        version_store.save_version(sample_version)
        
        # 验证目录结构
        session_dir = version_store.storage_path / sample_version.session_id
        assert session_dir.exists()
        assert session_dir.is_dir()
        
        version_file = session_dir / f"{sample_version.id}.json"
        assert version_file.exists()
        assert version_file.is_file()
    
    def test_empty_session_versions(self, version_store):
        """测试空会话版本列表 / Test empty session versions"""
        # 不存在的会话应该返回空列表
        versions = version_store.list_versions("nonexistent_session")
        assert versions == []
        
        # 最新版本应该返回None
        latest = version_store.get_latest_version("nonexistent_session")
        assert latest is None