"""
版本存储模块 / Version Storage Module

提供内容版本的持久化存储功能。
Provides persistent storage functionality for content versions.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from ..models.refinement_models import ContentVersion, VersionDiff


logger = logging.getLogger(__name__)


class VersionStore:
    """版本存储类 / Version Storage Class"""
    
    def __init__(self, storage_path: str = "./data/versions"):
        """
        初始化版本存储 / Initialize version storage
        
        Args:
            storage_path: 存储路径 / Storage path
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
    def save_version(self, version: ContentVersion) -> bool:
        """
        保存内容版本 / Save content version
        
        Args:
            version: 内容版本对象 / Content version object
            
        Returns:
            保存是否成功 / Whether save was successful
        """
        try:
            # 按会话ID创建子目录
            session_dir = self.storage_path / version.session_id
            session_dir.mkdir(exist_ok=True)
            
            version_file = session_dir / f"{version.id}.json"
            version_data = version.to_dict()
            
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(version_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"保存内容版本成功: {version.id}")
            return True
            
        except Exception as e:
            logger.error(f"保存内容版本失败: {version.id}, 错误: {e}")
            return False
    
    def load_version(self, session_id: str, version_id: str) -> Optional[ContentVersion]:
        """
        加载内容版本 / Load content version
        
        Args:
            session_id: 会话ID / Session ID
            version_id: 版本ID / Version ID
            
        Returns:
            内容版本对象或None / Content version object or None
        """
        try:
            version_file = self.storage_path / session_id / f"{version_id}.json"
            
            if not version_file.exists():
                logger.warning(f"内容版本文件不存在: {version_id}")
                return None
            
            with open(version_file, 'r', encoding='utf-8') as f:
                version_data = json.load(f)
            
            version = ContentVersion.from_dict(version_data)
            logger.info(f"加载内容版本成功: {version_id}")
            return version
            
        except Exception as e:
            logger.error(f"加载内容版本失败: {version_id}, 错误: {e}")
            return None
    
    def delete_version(self, session_id: str, version_id: str) -> bool:
        """
        删除内容版本 / Delete content version
        
        Args:
            session_id: 会话ID / Session ID
            version_id: 版本ID / Version ID
            
        Returns:
            删除是否成功 / Whether deletion was successful
        """
        try:
            version_file = self.storage_path / session_id / f"{version_id}.json"
            
            if version_file.exists():
                version_file.unlink()
                logger.info(f"删除内容版本成功: {version_id}")
                return True
            else:
                logger.warning(f"内容版本文件不存在: {version_id}")
                return False
                
        except Exception as e:
            logger.error(f"删除内容版本失败: {version_id}, 错误: {e}")
            return False
    
    def list_versions(self, session_id: str) -> List[ContentVersion]:
        """
        列出会话的所有版本 / List all versions for a session
        
        Args:
            session_id: 会话ID / Session ID
            
        Returns:
            版本列表 / List of versions
        """
        try:
            session_dir = self.storage_path / session_id
            
            if not session_dir.exists():
                return []
            
            versions = []
            for version_file in session_dir.glob("*.json"):
                version_id = version_file.stem
                version = self.load_version(session_id, version_id)
                if version:
                    versions.append(version)
            
            # 按版本号排序
            versions.sort(key=lambda v: v.version_number)
            return versions
            
        except Exception as e:
            logger.error(f"列出版本失败: {session_id}, 错误: {e}")
            return []
    
    def get_latest_version(self, session_id: str) -> Optional[ContentVersion]:
        """
        获取最新版本 / Get latest version
        
        Args:
            session_id: 会话ID / Session ID
            
        Returns:
            最新版本或None / Latest version or None
        """
        versions = self.list_versions(session_id)
        return versions[-1] if versions else None
    
    def cleanup_old_versions(self, session_id: str, keep_count: int = 50) -> int:
        """
        清理旧版本，保留指定数量的最新版本 / Cleanup old versions, keep specified number of latest versions
        
        Args:
            session_id: 会话ID / Session ID
            keep_count: 保留版本数量 / Number of versions to keep
            
        Returns:
            清理的版本数量 / Number of versions cleaned up
        """
        try:
            versions = self.list_versions(session_id)
            
            if len(versions) <= keep_count:
                return 0
            
            # 保留里程碑版本和最新的版本
            versions_to_delete = []
            milestone_versions = [v for v in versions if v.is_milestone]
            regular_versions = [v for v in versions if not v.is_milestone]
            
            # 如果常规版本超过保留数量，删除最旧的
            if len(regular_versions) > keep_count:
                versions_to_delete = regular_versions[:-keep_count]
            
            cleaned_count = 0
            for version in versions_to_delete:
                if self.delete_version(session_id, version.id):
                    cleaned_count += 1
            
            logger.info(f"清理完成，会话 {session_id} 清理了 {cleaned_count} 个旧版本")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"清理旧版本失败: {session_id}, 错误: {e}")
            return 0
    
    def save_version_diff(self, diff: VersionDiff) -> bool:
        """
        保存版本差异 / Save version diff
        
        Args:
            diff: 版本差异对象 / Version diff object
            
        Returns:
            保存是否成功 / Whether save was successful
        """
        try:
            diff_dir = self.storage_path / "diffs"
            diff_dir.mkdir(exist_ok=True)
            
            diff_file = diff_dir / f"{diff.version1_id}_{diff.version2_id}.json"
            diff_data = diff.to_dict()
            
            with open(diff_file, 'w', encoding='utf-8') as f:
                json.dump(diff_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"保存版本差异成功: {diff.version1_id} -> {diff.version2_id}")
            return True
            
        except Exception as e:
            logger.error(f"保存版本差异失败: {diff.version1_id} -> {diff.version2_id}, 错误: {e}")
            return False
    
    def load_version_diff(self, version1_id: str, version2_id: str) -> Optional[VersionDiff]:
        """
        加载版本差异 / Load version diff
        
        Args:
            version1_id: 版本1 ID / Version 1 ID
            version2_id: 版本2 ID / Version 2 ID
            
        Returns:
            版本差异对象或None / Version diff object or None
        """
        try:
            diff_file = self.storage_path / "diffs" / f"{version1_id}_{version2_id}.json"
            
            if not diff_file.exists():
                return None
            
            with open(diff_file, 'r', encoding='utf-8') as f:
                diff_data = json.load(f)
            
            diff = VersionDiff.from_dict(diff_data)
            return diff
            
        except Exception as e:
            logger.error(f"加载版本差异失败: {version1_id} -> {version2_id}, 错误: {e}")
            return None