"""
备份管理器单元测试 / Backup Manager Unit Tests
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path

from src.services.backup_manager import BackupManager


class TestBackupManager:
    """备份管理器测试类 / Backup Manager Test Class"""
    
    def setup_method(self):
        """测试前设置 / Setup before each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.backup_manager = BackupManager(self.temp_dir)
        
        # 创建测试数据
        self.test_data_dir = Path(tempfile.mkdtemp())
        self.create_test_data()
        
    def teardown_method(self):
        """测试后清理 / Cleanup after each test"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        shutil.rmtree(self.test_data_dir, ignore_errors=True)
    
    def create_test_data(self):
        """创建测试数据 / Create test data"""
        # 创建测试文件
        test_file = self.test_data_dir / "test_file.txt"
        test_file.write_text("Test content")
        
        # 创建测试目录
        test_dir = self.test_data_dir / "test_dir"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("File 1 content")
        (test_dir / "file2.txt").write_text("File 2 content")
    
    def test_init(self):
        """测试初始化 / Test initialization"""
        assert self.backup_manager.backup_base_path.exists()
        assert self.backup_manager.backup_base_path.is_dir()
    
    def test_create_backup_success(self):
        """测试成功创建备份 / Test successful backup creation"""
        user_id = "test_user"
        data_sources = {
            "test_file": str(self.test_data_dir / "test_file.txt"),
            "test_dir": str(self.test_data_dir / "test_dir")
        }
        
        result = self.backup_manager.create_backup(user_id, data_sources)
        
        assert result['success'] is True
        assert 'backup_name' in result
        assert result['backup_name'].startswith(f"backup_{user_id}_")
        assert Path(result['backup_path']).exists()
        
        # 验证备份内容
        backup_path = Path(result['backup_path'])
        assert (backup_path / "test_file" / "test_file.txt").exists()
        assert (backup_path / "test_dir" / "test_dir").exists()
        assert (backup_path / "backup_metadata.json").exists()
    
    def test_create_backup_nonexistent_source(self):
        """测试备份不存在的源 / Test backup with nonexistent source"""
        user_id = "test_user"
        data_sources = {
            "nonexistent": "/path/that/does/not/exist"
        }
        
        result = self.backup_manager.create_backup(user_id, data_sources)
        
        assert result['success'] is True  # 备份操作本身成功
        assert result['metadata']['data_sources']['nonexistent']['success'] is False
    
    def test_list_backups_empty(self):
        """测试列出空备份列表 / Test list empty backups"""
        result = self.backup_manager.list_backups()
        assert result == []
    
    def test_list_backups_with_data(self):
        """测试列出包含数据的备份 / Test list backups with data"""
        user_id = "test_user"
        data_sources = {"test_file": str(self.test_data_dir / "test_file.txt")}
        
        # 创建备份
        backup_result = self.backup_manager.create_backup(user_id, data_sources)
        assert backup_result['success'] is True
        
        # 列出备份
        backups = self.backup_manager.list_backups()
        
        assert len(backups) == 1
        assert backups[0]['user_id'] == user_id
        assert backups[0]['backup_name'] == backup_result['backup_name']
        assert 'created_at' in backups[0]
        assert 'total_size' in backups[0]
    
    def test_list_backups_filtered_by_user(self):
        """测试按用户过滤备份列表 / Test list backups filtered by user"""
        data_sources = {"test_file": str(self.test_data_dir / "test_file.txt")}
        
        # 创建不同用户的备份
        self.backup_manager.create_backup("user1", data_sources)
        self.backup_manager.create_backup("user2", data_sources)
        
        # 测试过滤
        user1_backups = self.backup_manager.list_backups("user1")
        user2_backups = self.backup_manager.list_backups("user2")
        all_backups = self.backup_manager.list_backups()
        
        assert len(user1_backups) == 1
        assert len(user2_backups) == 1
        assert len(all_backups) == 2
        assert user1_backups[0]['user_id'] == "user1"
        assert user2_backups[0]['user_id'] == "user2"
    
    def test_restore_backup_success(self):
        """测试成功恢复备份 / Test successful backup restore"""
        user_id = "test_user"
        data_sources = {"test_file": str(self.test_data_dir / "test_file.txt")}
        
        # 创建备份
        backup_result = self.backup_manager.create_backup(user_id, data_sources)
        assert backup_result['success'] is True
        
        # 准备恢复目标
        restore_dir = Path(tempfile.mkdtemp())
        restore_targets = {"test_file": str(restore_dir / "restored_file.txt")}
        
        try:
            # 恢复备份
            restore_result = self.backup_manager.restore_backup(
                backup_result['backup_name'], restore_targets
            )
            
            assert restore_result['success'] is True
            assert restore_result['successful_restores'] == 1
            assert restore_result['total_restores'] == 1
            
            # 验证恢复的文件
            restored_file = restore_dir / "restored_file.txt"
            assert restored_file.exists()
            assert restored_file.read_text() == "Test content"
            
        finally:
            shutil.rmtree(restore_dir, ignore_errors=True)
    
    def test_restore_backup_not_found(self):
        """测试恢复不存在的备份 / Test restore nonexistent backup"""
        restore_targets = {"test": "/some/path"}
        
        result = self.backup_manager.restore_backup("nonexistent_backup", restore_targets)
        
        assert result['success'] is False
        assert 'not found' in result['error']
    
    def test_delete_backup_success(self):
        """测试成功删除备份 / Test successful backup deletion"""
        user_id = "test_user"
        data_sources = {"test_file": str(self.test_data_dir / "test_file.txt")}
        
        # 创建备份
        backup_result = self.backup_manager.create_backup(user_id, data_sources)
        backup_name = backup_result['backup_name']
        backup_path = Path(backup_result['backup_path'])
        
        # 验证备份存在
        assert backup_path.exists()
        
        # 删除备份
        delete_result = self.backup_manager.delete_backup(backup_name)
        
        assert delete_result is True
        assert not backup_path.exists()
    
    def test_delete_backup_not_found(self):
        """测试删除不存在的备份 / Test delete nonexistent backup"""
        result = self.backup_manager.delete_backup("nonexistent_backup")
        assert result is False
    
    def test_cleanup_old_backups_no_cleanup_needed(self):
        """测试不需要清理的情况 / Test cleanup when no cleanup needed"""
        user_id = "test_user"
        data_sources = {"test_file": str(self.test_data_dir / "test_file.txt")}
        
        # 创建少量备份
        self.backup_manager.create_backup(user_id, data_sources)
        self.backup_manager.create_backup(user_id, data_sources)
        
        # 清理（保留5个）
        result = self.backup_manager.cleanup_old_backups(user_id, keep_count=5)
        
        assert result['success'] is True
        assert result['deleted_count'] == 0
        assert result['kept_count'] == 2
        assert 'No cleanup needed' in result['message']
    
    def test_cleanup_old_backups_with_cleanup(self):
        """测试需要清理的情况 / Test cleanup when cleanup needed"""
        user_id = "test_user"
        data_sources = {"test_file": str(self.test_data_dir / "test_file.txt")}
        
        # 创建多个备份
        backup_names = []
        for i in range(7):
            result = self.backup_manager.create_backup(user_id, data_sources)
            backup_names.append(result['backup_name'])
        
        # 清理（保留3个）
        cleanup_result = self.backup_manager.cleanup_old_backups(user_id, keep_count=3)
        
        assert cleanup_result['success'] is True
        assert cleanup_result['deleted_count'] == 4
        assert cleanup_result['kept_count'] == 3
        
        # 验证剩余备份数量
        remaining_backups = self.backup_manager.list_backups(user_id)
        assert len(remaining_backups) == 3
    
    def test_backup_data_source_file(self):
        """测试备份单个文件 / Test backup single file"""
        test_file = self.test_data_dir / "test_file.txt"
        backup_path = Path(self.temp_dir) / "backup_test"
        
        result = self.backup_manager._backup_data_source(str(test_file), backup_path)
        
        assert result['success'] is True
        assert result['size'] > 0
        assert (backup_path / "test_file.txt").exists()
    
    def test_backup_data_source_directory(self):
        """测试备份目录 / Test backup directory"""
        test_dir = self.test_data_dir / "test_dir"
        backup_path = Path(self.temp_dir) / "backup_test"
        
        result = self.backup_manager._backup_data_source(str(test_dir), backup_path)
        
        assert result['success'] is True
        assert result['size'] > 0
        assert (backup_path / "test_dir").exists()
        assert (backup_path / "test_dir" / "file1.txt").exists()
    
    def test_backup_data_source_nonexistent(self):
        """测试备份不存在的源 / Test backup nonexistent source"""
        backup_path = Path(self.temp_dir) / "backup_test"
        
        result = self.backup_manager._backup_data_source("/nonexistent/path", backup_path)
        
        assert result['success'] is False
        assert 'does not exist' in result['error']
        assert result['size'] == 0
    
    def test_restore_data_source_file(self):
        """测试恢复单个文件 / Test restore single file"""
        # 先创建备份
        test_file = self.test_data_dir / "test_file.txt"
        backup_path = Path(self.temp_dir) / "backup_test"
        self.backup_manager._backup_data_source(str(test_file), backup_path)
        
        # 恢复到新位置
        restore_target = Path(self.temp_dir) / "restored_file.txt"
        backup_file = backup_path / "test_file.txt"
        
        result = self.backup_manager._restore_data_source(backup_file, str(restore_target))
        
        assert result['success'] is True
        assert restore_target.exists()
        assert restore_target.read_text() == "Test content"
    
    def test_restore_data_source_directory(self):
        """测试恢复目录 / Test restore directory"""
        # 先创建备份
        test_dir = self.test_data_dir / "test_dir"
        backup_path = Path(self.temp_dir) / "backup_test"
        self.backup_manager._backup_data_source(str(test_dir), backup_path)
        
        # 恢复到新位置
        restore_target = Path(self.temp_dir) / "restored_dir"
        backup_dir = backup_path / "test_dir"
        
        result = self.backup_manager._restore_data_source(backup_dir, str(restore_target))
        
        assert result['success'] is True
        assert restore_target.exists()
        assert (restore_target / "file1.txt").exists()
        assert (restore_target / "file2.txt").exists()
    
    def test_restore_data_source_nonexistent(self):
        """测试恢复不存在的备份 / Test restore nonexistent backup"""
        nonexistent_backup = Path(self.temp_dir) / "nonexistent"
        restore_target = Path(self.temp_dir) / "target"
        
        result = self.backup_manager._restore_data_source(nonexistent_backup, str(restore_target))
        
        assert result['success'] is False
        assert 'does not exist' in result['error']