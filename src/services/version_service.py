"""
版本服务模块 / Version Service Module

管理内容版本的创建、存储和差异计算。
Manages content version creation, storage, and difference calculation.
"""

import logging
import difflib
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..models.refinement_models import ContentVersion, VersionDiff, ModificationType
from ..storage.version_store import VersionStore


logger = logging.getLogger(__name__)


class VersionService:
    """版本服务类 / Version Service Class"""
    
    def __init__(self):
        """初始化版本服务 / Initialize version service"""
        self.version_store = VersionStore()
        
        logger.info("版本服务初始化完成")
    
    def create_version(self, session_id: str, content: str, modification_type: str) -> str:
        """
        创建内容版本 / Create content version
        
        Args:
            session_id: 会话ID / Session ID
            content: 内容 / Content
            modification_type: 修改类型 / Modification type
            
        Returns:
            版本ID / Version ID
        """
        try:
            # 获取现有版本列表
            existing_versions = self.version_store.list_versions(session_id)
            
            # 计算新版本号
            version_number = len(existing_versions) + 1
            
            # 获取父版本ID
            parent_version_id = existing_versions[-1].id if existing_versions else None
            
            # 创建版本对象
            version = ContentVersion(
                id=f"ver_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{session_id[:8]}",
                session_id=session_id,
                content=content,
                version_number=version_number,
                parent_version_id=parent_version_id,
                modification_type=modification_type,
                modification_description=f"版本 {version_number}",
                created_at=datetime.now(),
                is_milestone=False,
                metadata={}
            )
            
            # 保存版本
            self.version_store.save_version(version)
            
            logger.info(f"创建版本成功: {version.id}")
            return version.id
            
        except Exception as e:
            logger.error(f"创建版本失败: {e}")
            raise
    
    def get_version_list(self, session_id: str) -> List[ContentVersion]:
        """
        获取版本列表 / Get version list
        
        Args:
            session_id: 会话ID / Session ID
            
        Returns:
            版本列表 / Version list
        """
        try:
            return self.version_store.list_versions(session_id)
            
        except Exception as e:
            logger.error(f"获取版本列表失败: {session_id}, 错误: {e}")
            return []
    
    def get_version_content(self, version_id: str) -> str:
        """
        获取版本内容 / Get version content
        
        Args:
            version_id: 版本ID / Version ID
            
        Returns:
            版本内容 / Version content
        """
        try:
            # 从版本ID中提取会话ID
            session_id = self._extract_session_id_from_version(version_id)
            if not session_id:
                raise ValueError("无法从版本ID中提取会话ID")
            
            version = self.version_store.load_version(session_id, version_id)
            if not version:
                raise ValueError(f"版本不存在: {version_id}")
            
            return version.content
            
        except Exception as e:
            logger.error(f"获取版本内容失败: {version_id}, 错误: {e}")
            raise
    
    def compare_versions(self, version_id1: str, version_id2: str) -> VersionDiff:
        """
        对比版本差异 / Compare version differences
        
        Args:
            version_id1: 版本1 ID / Version 1 ID
            version_id2: 版本2 ID / Version 2 ID
            
        Returns:
            版本差异 / Version difference
        """
        try:
            # 获取版本内容
            content1 = self.get_version_content(version_id1)
            content2 = self.get_version_content(version_id2)
            
            # 计算差异
            diff_result = self._calculate_diff(content1, content2)
            
            # 创建差异对象
            version_diff = VersionDiff(
                version1_id=version_id1,
                version2_id=version_id2,
                additions=diff_result['additions'],
                deletions=diff_result['deletions'],
                modifications=diff_result['modifications'],
                similarity_score=diff_result['similarity_score']
            )
            
            # 保存差异结果
            self.version_store.save_version_diff(version_diff)
            
            logger.info(f"版本对比完成: {version_id1} vs {version_id2}")
            return version_diff
            
        except Exception as e:
            logger.error(f"版本对比失败: {version_id1} vs {version_id2}, 错误: {e}")
            raise
    
    def revert_to_version(self, session_id: str, version_id: str) -> str:
        """
        回退到指定版本 / Revert to version
        
        Args:
            session_id: 会话ID / Session ID
            version_id: 版本ID / Version ID
            
        Returns:
            回退后的内容 / Reverted content
        """
        try:
            # 获取目标版本
            target_version = self.version_store.load_version(session_id, version_id)
            if not target_version:
                raise ValueError(f"版本不存在: {version_id}")
            
            # 创建回退版本
            revert_version_id = self.create_version(
                session_id=session_id,
                content=target_version.content,
                modification_type=ModificationType.STRUCTURAL.value
            )
            
            # 更新回退版本的描述
            revert_version = self.version_store.load_version(session_id, revert_version_id)
            if revert_version:
                revert_version.modification_description = f"回退到版本 {target_version.version_number}"
                revert_version.metadata = {"reverted_from": version_id}
                self.version_store.save_version(revert_version)
            
            logger.info(f"回退到版本成功: {session_id} -> {version_id}")
            return target_version.content
            
        except Exception as e:
            logger.error(f"回退到版本失败: {session_id} -> {version_id}, 错误: {e}")
            raise
    
    def create_milestone(self, version_id: str, description: str) -> bool:
        """
        创建里程碑版本 / Create milestone version
        
        Args:
            version_id: 版本ID / Version ID
            description: 里程碑描述 / Milestone description
            
        Returns:
            创建是否成功 / Whether creation was successful
        """
        try:
            # 从版本ID中提取会话ID
            session_id = self._extract_session_id_from_version(version_id)
            if not session_id:
                raise ValueError("无法从版本ID中提取会话ID")
            
            # 获取版本
            version = self.version_store.load_version(session_id, version_id)
            if not version:
                raise ValueError(f"版本不存在: {version_id}")
            
            # 标记为里程碑
            version.is_milestone = True
            version.modification_description = description
            version.metadata = version.metadata or {}
            version.metadata["milestone_created_at"] = datetime.now().isoformat()
            
            # 保存更新
            self.version_store.save_version(version)
            
            logger.info(f"创建里程碑成功: {version_id}")
            return True
            
        except Exception as e:
            logger.error(f"创建里程碑失败: {version_id}, 错误: {e}")
            return False
    
    def cleanup_old_versions(self, session_id: str, keep_count: int = 50) -> int:
        """
        清理旧版本 / Cleanup old versions
        
        Args:
            session_id: 会话ID / Session ID
            keep_count: 保留版本数量 / Number of versions to keep
            
        Returns:
            清理的版本数量 / Number of versions cleaned up
        """
        try:
            return self.version_store.cleanup_old_versions(session_id, keep_count)
            
        except Exception as e:
            logger.error(f"清理旧版本失败: {session_id}, 错误: {e}")
            return 0
    
    def get_version_statistics(self, session_id: str) -> Dict[str, Any]:
        """
        获取版本统计信息 / Get version statistics
        
        Args:
            session_id: 会话ID / Session ID
            
        Returns:
            统计信息 / Statistics information
        """
        try:
            versions = self.version_store.list_versions(session_id)
            
            if not versions:
                return {}
            
            milestone_count = sum(1 for v in versions if v.is_milestone)
            modification_types = {}
            
            for version in versions:
                mod_type = version.modification_type
                modification_types[mod_type] = modification_types.get(mod_type, 0) + 1
            
            return {
                "total_versions": len(versions),
                "milestone_versions": milestone_count,
                "latest_version": versions[-1].version_number,
                "first_created": versions[0].created_at.isoformat(),
                "last_modified": versions[-1].created_at.isoformat(),
                "modification_types": modification_types
            }
            
        except Exception as e:
            logger.error(f"获取版本统计失败: {session_id}, 错误: {e}")
            return {}
    
    def _calculate_diff(self, content1: str, content2: str) -> Dict[str, Any]:
        """
        计算内容差异 / Calculate content difference
        
        Args:
            content1: 内容1 / Content 1
            content2: 内容2 / Content 2
            
        Returns:
            差异结果 / Difference result
        """
        try:
            # 按行分割内容
            lines1 = content1.splitlines()
            lines2 = content2.splitlines()
            
            # 使用difflib计算差异
            differ = difflib.unified_diff(lines1, lines2, lineterm='')
            diff_lines = list(differ)
            
            # 分析差异
            additions = []
            deletions = []
            modifications = []
            
            for line in diff_lines:
                if line.startswith('+') and not line.startswith('+++'):
                    additions.append(line[1:])
                elif line.startswith('-') and not line.startswith('---'):
                    deletions.append(line[1:])
            
            # 计算相似度
            similarity_score = difflib.SequenceMatcher(None, content1, content2).ratio()
            
            # 识别修改（简化版本：删除+添加的组合）
            if len(deletions) > 0 and len(additions) > 0:
                for i, deletion in enumerate(deletions[:len(additions)]):
                    addition = additions[i] if i < len(additions) else ""
                    modifications.append({
                        "old": deletion,
                        "new": addition
                    })
            
            return {
                "additions": additions,
                "deletions": deletions,
                "modifications": modifications,
                "similarity_score": similarity_score
            }
            
        except Exception as e:
            logger.error(f"计算差异失败: {e}")
            return {
                "additions": [],
                "deletions": [],
                "modifications": [],
                "similarity_score": 0.0
            }
    
    def _extract_session_id_from_version(self, version_id: str) -> Optional[str]:
        """
        从版本ID中提取会话ID / Extract session ID from version ID
        
        Args:
            version_id: 版本ID / Version ID
            
        Returns:
            会话ID或None / Session ID or None
        """
        try:
            # 版本ID格式: ver_YYYYMMDD_HHMMSS_sessionid
            parts = version_id.split('_')
            if len(parts) >= 4:
                return parts[-1]  # 最后一部分是会话ID的前8位
            return None
            
        except Exception as e:
            logger.error(f"提取会话ID失败: {version_id}, 错误: {e}")
            return None