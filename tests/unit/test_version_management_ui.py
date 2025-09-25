"""
版本管理界面测试 / Version Management UI Tests

测试版本管理界面的基本功能
Test basic functionality of version management interface
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.ui.gradio_interface import GradioInterface
from src.services.app_controller import AppController


class TestVersionManagementUI(unittest.TestCase):
    """版本管理界面测试类 / Version Management UI Test Class"""

    def setUp(self):
        """设置测试环境 / Set up test environment"""
        # 创建模拟的应用控制器
        self.mock_app_controller = Mock(spec=AppController)
        self.mock_app_controller.get_app_config.return_value = {
            "title": "Test Case Summary Generator"
        }
        
        # 创建Gradio界面实例
        with patch('src.ui.gradio_interface.PromptUIComponents'):
            with patch('src.ui.gradio_interface.RefinementController'):
                self.interface = GradioInterface(self.mock_app_controller)

    def test_refresh_version_history_no_session(self):
        """测试无会话时刷新版本历史 / Test refresh version history without session"""
        result = self.interface._refresh_version_history()
        self.assertEqual(result, [])

    @patch('src.ui.gradio_interface.RefinementController')
    def test_refresh_version_history_with_session(self, mock_refinement_controller_class):
        """测试有会话时刷新版本历史 / Test refresh version history with session"""
        # 设置模拟的优化控制器
        mock_controller = Mock()
        mock_controller.get_version_history.return_value = [
            {
                'version_number': 1,
                'created_at': '2023-01-01T10:00:00',
                'modification_type': 'initial',
                'description': '初始版本'
            },
            {
                'version_number': 2,
                'created_at': '2023-01-01T10:05:00',
                'modification_type': 'content_addition',
                'description': '添加细节'
            }
        ]
        mock_refinement_controller_class.return_value = mock_controller
        
        # 重新创建界面实例
        with patch('src.ui.gradio_interface.PromptUIComponents'):
            interface = GradioInterface(self.mock_app_controller)
            interface.current_session_id = "test_session"
            interface.refinement_controller = mock_controller
        
        # 测试刷新版本历史
        result = interface._refresh_version_history()
        
        # 验证结果
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ['v1', '2023-01-01T10:00:00', 'initial', '初始版本'])
        self.assertEqual(result[1], ['v2', '2023-01-01T10:05:00', 'content_addition', '添加细节'])

    def test_view_selected_version_no_data(self):
        """测试查看版本时无数据 / Test view version with no data"""
        result = self.interface._view_selected_version([])
        self.assertIn("请选择一个版本", result.value)

    def test_view_selected_version_with_data(self):
        """测试查看版本时有数据 / Test view version with data"""
        version_data = [['v1', '2023-01-01T10:00:00', 'initial', '初始版本']]
        result = self.interface._view_selected_version(version_data)
        
        # 验证返回的HTML包含版本信息
        self.assertIn("v1", result.value)
        self.assertIn("2023-01-01T10:00:00", result.value)
        self.assertIn("initial", result.value)
        self.assertIn("初始版本", result.value)

    def test_compare_versions_insufficient_data(self):
        """测试对比版本时数据不足 / Test compare versions with insufficient data"""
        result = self.interface._compare_versions([])
        self.assertIn("请选择至少两个版本", result.value)
        
        result = self.interface._compare_versions([['v1', '2023-01-01T10:00:00', 'initial', '初始版本']])
        self.assertIn("请选择至少两个版本", result.value)

    def test_compare_versions_with_data(self):
        """测试对比版本时有足够数据 / Test compare versions with sufficient data"""
        version_data = [
            ['v1', '2023-01-01T10:00:00', 'initial', '初始版本'],
            ['v2', '2023-01-01T10:05:00', 'content_addition', '添加细节']
        ]
        result = self.interface._compare_versions(version_data)
        
        # 验证返回的HTML包含对比信息
        self.assertIn("版本 A: v1", result.value)
        self.assertIn("版本 B: v2", result.value)
        self.assertIn("版本对比", result.value)

    def test_revert_to_version_no_data(self):
        """测试回退版本时无数据 / Test revert version with no data"""
        content, version_info, content_stats, result_html = self.interface._revert_to_version([])
        self.assertIn("请选择一个版本", result_html.value)

    def test_revert_to_version_no_session(self):
        """测试回退版本时无会话 / Test revert version with no session"""
        version_data = [['v1', '2023-01-01T10:00:00', 'initial', '初始版本']]
        content, version_info, content_stats, result_html = self.interface._revert_to_version(version_data)
        self.assertIn("没有活跃的会话", result_html.value)

    @patch('src.ui.gradio_interface.RefinementController')
    def test_revert_to_version_success(self, mock_refinement_controller_class):
        """测试成功回退版本 / Test successful version revert"""
        # 设置模拟的优化控制器
        mock_controller = Mock()
        mock_controller.undo_last_modification.return_value = {
            'success': True,
            'content': '回退后的内容'
        }
        mock_refinement_controller_class.return_value = mock_controller
        
        # 重新创建界面实例
        with patch('src.ui.gradio_interface.PromptUIComponents'):
            interface = GradioInterface(self.mock_app_controller)
            interface.current_session_id = "test_session"
            interface.refinement_controller = mock_controller
        
        # 测试回退版本
        version_data = [['v2', '2023-01-01T10:05:00', 'content_addition', '添加细节']]
        content, version_info, content_stats, result_html = interface._revert_to_version(version_data)
        
        # 验证结果
        self.assertEqual(content, "回退后的内容")
        self.assertIn("成功回退", result_html.value)

    def test_create_milestone_no_data(self):
        """测试创建里程碑时无数据 / Test create milestone with no data"""
        result = self.interface._create_milestone([])
        self.assertIn("请选择一个版本创建里程碑", result.value)

    def test_create_milestone_with_data(self):
        """测试创建里程碑时有数据 / Test create milestone with data"""
        version_data = [['v1', '2023-01-01T10:00:00', 'initial', '初始版本']]
        result = self.interface._create_milestone(version_data)
        
        # 验证返回的HTML包含里程碑创建成功信息
        self.assertIn("已为 v1 创建里程碑", result.value)
        self.assertIn("总版本数: 1", result.value)
        self.assertIn("里程碑: 1", result.value)

    def test_version_management_components_exist(self):
        """测试版本管理组件是否存在 / Test version management components exist"""
        # 简化测试，只验证方法是否存在
        interface = self.interface
        
        # 验证版本管理相关的方法是否存在
        self.assertTrue(hasattr(interface, '_create_version_management_section'))
        self.assertTrue(hasattr(interface, '_refresh_version_history'))
        self.assertTrue(hasattr(interface, '_view_selected_version'))
        self.assertTrue(hasattr(interface, '_compare_versions'))
        self.assertTrue(hasattr(interface, '_revert_to_version'))
        self.assertTrue(hasattr(interface, '_create_milestone'))
        self.assertTrue(hasattr(interface, '_bind_version_events'))


if __name__ == '__main__':
    unittest.main()