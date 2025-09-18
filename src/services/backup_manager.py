"""
数据备份管理器 / Data Backup Manager

该模块负责用户数据的备份和恢复功能。
This module handles backup and restore functionality for user data.
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class BackupManager:
    """数据备份管理器 / Data Backup Manager"""
    
    def __init__(self, backup_base_path: str = "./backups"):
        """
        初始化备份管理器
        Initialize backup manager
        
        Args:
            backup_base_path: 备份基础路径 / Base backup path
        """
        self.backup_base_path = Path(backup_base_path)
        self.backup_base_path.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, user_id: str, data_sources: Dict[str, str]) -> Dict[str, Any]:
        """
        创建用户数据备份 / Create user data backup
        
        Args:
            user_id: 用户ID / User ID
            data_sources: 数据源路径映射 / Data source path mapping
                         格式: {"prompts": "/path/to/prompts", "preferences": "/path/to/prefs"}
            
        Returns:
            Dict: 备份结果 / Backup result
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # 包含毫秒，去掉最后3位
            backup_name = f"backup_{user_id}_{timestamp}"
            backup_dir = self.backup_base_path / backup_name
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            backup_info = {
                'user_id': user_id,
                'timestamp': timestamp,
                'backup_name': backup_name,
                'created_at': datetime.now().isoformat(),
                'data_sources': {},
                'total_size': 0
            }
            
            # 备份各个数据源
            for source_name, source_path in data_sources.items():
                source_backup_result = self._backup_data_source(
                    source_path, backup_dir / source_name
                )
                backup_info['data_sources'][source_name] = source_backup_result
                backup_info['total_size'] += source_backup_result.get('size', 0)
            
            # 保存备份元数据
            metadata_file = backup_dir / 'backup_metadata.json'
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, ensure_ascii=False, indent=2)
            
            logging.info(f"Created backup {backup_name} for user {user_id}")
            return {
                'success': True,
                'backup_name': backup_name,
                'backup_path': str(backup_dir),
                'metadata': backup_info
            }
            
        except Exception as e:
            logging.error(f"Failed to create backup for {user_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_backups(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        列出备份 / List backups
        
        Args:
            user_id: 用户ID，None表示列出所有用户的备份 / User ID, None for all users
            
        Returns:
            List[Dict]: 备份列表 / Backup list
        """
        backups = []
        
        try:
            pattern = f"backup_{user_id}_*" if user_id else "backup_*"
            
            for backup_dir in self.backup_base_path.glob(pattern):
                if backup_dir.is_dir():
                    metadata_file = backup_dir / 'backup_metadata.json'
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                            
                            backup_info = {
                                'backup_name': metadata.get('backup_name'),
                                'user_id': metadata.get('user_id'),
                                'created_at': metadata.get('created_at'),
                                'total_size': metadata.get('total_size', 0),
                                'data_sources': list(metadata.get('data_sources', {}).keys()),
                                'backup_path': str(backup_dir)
                            }
                            backups.append(backup_info)
                            
                        except Exception as e:
                            logging.warning(f"Failed to read backup metadata {metadata_file}: {e}")
            
            # 按创建时间排序
            backups.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
        except Exception as e:
            logging.error(f"Failed to list backups: {e}")
        
        return backups
    
    def restore_backup(self, backup_name: str, restore_targets: Dict[str, str]) -> Dict[str, Any]:
        """
        恢复备份 / Restore backup
        
        Args:
            backup_name: 备份名称 / Backup name
            restore_targets: 恢复目标路径映射 / Restore target path mapping
                           格式: {"prompts": "/path/to/restore/prompts"}
            
        Returns:
            Dict: 恢复结果 / Restore result
        """
        try:
            backup_dir = self.backup_base_path / backup_name
            if not backup_dir.exists():
                return {
                    'success': False,
                    'error': f'Backup {backup_name} not found'
                }
            
            # 读取备份元数据
            metadata_file = backup_dir / 'backup_metadata.json'
            if not metadata_file.exists():
                return {
                    'success': False,
                    'error': 'Backup metadata not found'
                }
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            restore_results = {}
            
            # 恢复各个数据源
            for source_name, target_path in restore_targets.items():
                source_backup_path = backup_dir / source_name
                if source_backup_path.exists():
                    restore_result = self._restore_data_source(
                        source_backup_path, target_path
                    )
                    restore_results[source_name] = restore_result
                else:
                    restore_results[source_name] = {
                        'success': False,
                        'error': f'Source {source_name} not found in backup'
                    }
            
            # 统计恢复结果
            successful_restores = sum(1 for r in restore_results.values() if r.get('success'))
            total_restores = len(restore_results)
            
            logging.info(f"Restored backup {backup_name}: {successful_restores}/{total_restores} successful")
            
            return {
                'success': successful_restores > 0,
                'backup_name': backup_name,
                'restore_results': restore_results,
                'successful_restores': successful_restores,
                'total_restores': total_restores,
                'metadata': metadata
            }
            
        except Exception as e:
            logging.error(f"Failed to restore backup {backup_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_backup(self, backup_name: str) -> bool:
        """
        删除备份 / Delete backup
        
        Args:
            backup_name: 备份名称 / Backup name
            
        Returns:
            bool: 删除是否成功 / Whether deletion was successful
        """
        try:
            backup_dir = self.backup_base_path / backup_name
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
                logging.info(f"Deleted backup {backup_name}")
                return True
            else:
                logging.warning(f"Backup {backup_name} not found")
                return False
                
        except Exception as e:
            logging.error(f"Failed to delete backup {backup_name}: {e}")
            return False
    
    def cleanup_old_backups(self, user_id: str, keep_count: int = 5) -> Dict[str, Any]:
        """
        清理旧备份 / Cleanup old backups
        
        Args:
            user_id: 用户ID / User ID
            keep_count: 保留备份数量 / Number of backups to keep
            
        Returns:
            Dict: 清理结果 / Cleanup result
        """
        try:
            user_backups = self.list_backups(user_id)
            
            if len(user_backups) <= keep_count:
                return {
                    'success': True,
                    'deleted_count': 0,
                    'kept_count': len(user_backups),
                    'message': 'No cleanup needed'
                }
            
            # 删除多余的备份
            backups_to_delete = user_backups[keep_count:]
            deleted_count = 0
            
            for backup in backups_to_delete:
                if self.delete_backup(backup['backup_name']):
                    deleted_count += 1
            
            # 计算实际保留的备份数量
            actual_kept_count = len(user_backups) - deleted_count
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'kept_count': actual_kept_count,
                'message': f'Cleaned up {deleted_count} old backups'
            }
            
        except Exception as e:
            logging.error(f"Failed to cleanup backups for {user_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _backup_data_source(self, source_path: str, backup_path: Path) -> Dict[str, Any]:
        """备份数据源 / Backup data source"""
        try:
            source = Path(source_path)
            
            if not source.exists():
                return {
                    'success': False,
                    'error': f'Source path {source_path} does not exist',
                    'size': 0
                }
            
            backup_path.mkdir(parents=True, exist_ok=True)
            
            if source.is_file():
                # 备份单个文件 - 直接复制到备份目录
                target_file = backup_path / source.name
                shutil.copy2(source, target_file)
                size = source.stat().st_size
            else:
                # 备份目录
                shutil.copytree(source, backup_path / source.name, dirs_exist_ok=True)
                size = sum(f.stat().st_size for f in source.rglob('*') if f.is_file())
            
            return {
                'success': True,
                'source_path': source_path,
                'backup_path': str(backup_path),
                'size': size
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'size': 0
            }
    
    def _restore_data_source(self, backup_path: Path, target_path: str) -> Dict[str, Any]:
        """恢复数据源 / Restore data source"""
        try:
            target = Path(target_path)
            
            if not backup_path.exists():
                return {
                    'success': False,
                    'error': f'Backup path {backup_path} does not exist'
                }
            
            # 确保目标目录存在
            target.parent.mkdir(parents=True, exist_ok=True)
            
            # 判断备份类型并恢复
            if backup_path.is_dir():
                # 如果备份路径是目录，查找其中的文件
                backup_files = list(backup_path.glob('*'))
                if len(backup_files) == 1 and backup_files[0].is_file():
                    # 单个文件备份
                    shutil.copy2(backup_files[0], target)
                else:
                    # 目录备份
                    if target.exists():
                        shutil.rmtree(target)
                    shutil.copytree(backup_path, target)
            else:
                # 直接文件备份
                shutil.copy2(backup_path, target)
            
            return {
                'success': True,
                'backup_path': str(backup_path),
                'target_path': target_path
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }