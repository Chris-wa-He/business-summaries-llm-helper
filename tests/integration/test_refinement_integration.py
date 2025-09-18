"""
优化控制器集成测试 / Refinement Controller Integration Tests
"""

import pytest
import tempfile
import shutil
from unittest.mock import Mock, patch

from src.services.refinement_controller import RefinementController
from src.services.app_controller import AppController


class TestRefinementIntegration:
    """优化控制器集成测试类 / Refinement Controller Integration Test Class"""
    
    @pytest.fixture
    def temp_storage_path(self):
        """创建临时存储路径 / Create temporary storage path"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_app_controller(self):
        """创建模拟应用控制器 / Create mock app controller"""
        mock_controller = Mock(spec=AppController)
        mock_controller.get_initialization_status.return_value = (True, "系统已初始化")
        return mock_controller
    
    def test_refinement_controller_initialization(self, mock_app_controller, temp_storage_path):
        """测试优化控制器初始化 / Test refinement controller initialization"""
        with patch('src.services.refinement_controller.ConversationStore'), \
             patch('src.services.refinement_controller.VersionStore'):
            
            controller = RefinementController(mock_app_controller)
            
            # 验证控制器初始化
            assert controller.app_controller is mock_app_controller
            assert controller.conversation_store is not None
            assert controller.version_store is not None
            assert isinstance(controller.active_sessions, dict)
            assert len(controller.active_sessions) == 0
    
    def test_complete_refinement_workflow(self, mock_app_controller, temp_storage_path):
        """测试完整的优化工作流 / Test complete refinement workflow"""
        with patch('src.services.refinement_controller.ConversationStore') as mock_conv_store, \
             patch('src.services.refinement_controller.VersionStore') as mock_ver_store:
            
            # 配置mock
            mock_conv_store.return_value.save_session.return_value = True
            mock_ver_store.return_value.save_version.return_value = True
            mock_ver_store.return_value.list_versions.return_value = []
            
            controller = RefinementController(mock_app_controller)
            
            # 1. 启动会话
            session_id = controller.start_refinement_session("初始内容", "test_user")
            assert session_id is not None
            
            # 2. 处理用户消息
            result = controller.process_user_message("请添加更多细节", session_id)
            assert result["success"] is True
            
            # 3. 应用修改
            modification = {"type": "content_addition", "description": "添加细节"}
            modified_content = controller.apply_modification(modification, session_id)
            assert modified_content is not None
            
            # 4. 获取版本历史
            history = controller.get_version_history(session_id)
            assert isinstance(history, list)
            
            # 5. 获取会话状态
            status = controller.get_session_status(session_id)
            assert status["exists"] is True
    
    def test_error_handling_integration(self, mock_app_controller):
        """测试错误处理集成 / Test error handling integration"""
        with patch('src.services.refinement_controller.ConversationStore') as mock_conv_store, \
             patch('src.services.refinement_controller.VersionStore') as mock_ver_store:
            
            # 配置mock抛出异常
            mock_conv_store.return_value.save_session.side_effect = Exception("存储错误")
            
            controller = RefinementController(mock_app_controller)
            
            # 验证异常处理
            with pytest.raises(Exception):
                controller.start_refinement_session("测试内容", "test_user")
    
    def test_app_controller_integration(self, mock_app_controller):
        """测试与应用控制器的集成 / Test integration with app controller"""
        with patch('src.services.refinement_controller.ConversationStore'), \
             patch('src.services.refinement_controller.VersionStore'):
            
            controller = RefinementController(mock_app_controller)
            
            # 验证可以访问应用控制器的方法
            status = controller.app_controller.get_initialization_status()
            assert status[0] is True
            assert "系统已初始化" in status[1]