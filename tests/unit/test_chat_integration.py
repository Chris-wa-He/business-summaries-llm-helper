"""
聊天交互集成测试 / Chat Integration Tests

测试聊天交互界面的基本功能
Test basic functionality of chat interaction interface
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.ui.gradio_interface import GradioInterface
from src.services.app_controller import AppController


class TestChatIntegration(unittest.TestCase):
    """聊天交互集成测试类 / Chat Integration Test Class"""

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

    def test_chat_interface_initialization(self):
        """测试聊天界面初始化 / Test chat interface initialization"""
        # 验证聊天相关属性已初始化
        self.assertIsNotNone(self.interface.refinement_controller)
        self.assertEqual(self.interface.current_session_id, None)
        self.assertEqual(self.interface.current_content, "")

    def test_handle_user_message_no_session(self):
        """测试无会话时处理用户消息 / Test handling user message without session"""
        # 测试没有会话时的消息处理
        result = self.interface._handle_user_message("测试消息")
        
        # 验证返回格式
        self.assertEqual(len(result), 5)
        chat_history, cleared_input, content, version_info, content_stats = result
        
        # 验证错误提示
        self.assertEqual(len(chat_history), 1)
        self.assertIn("请先生成案例总结", chat_history[0][1])
        self.assertEqual(cleared_input, "")

    def test_handle_user_message_empty(self):
        """测试处理空消息 / Test handling empty message"""
        result = self.interface._handle_user_message("")
        
        # 验证返回空的聊天历史
        chat_history, cleared_input, content, version_info, content_stats = result
        self.assertEqual(chat_history, [])
        self.assertEqual(cleared_input, "")

    @patch('src.ui.gradio_interface.RefinementController')
    def test_handle_user_message_with_session(self, mock_refinement_controller_class):
        """测试有会话时处理用户消息 / Test handling user message with session"""
        # 设置模拟的优化控制器
        mock_controller = Mock()
        mock_controller.process_user_message.return_value = {
            'success': True,
            'response': 'AI响应',
            'modified_content': '修改后的内容'
        }
        mock_refinement_controller_class.return_value = mock_controller
        
        # 重新创建界面实例
        with patch('src.ui.gradio_interface.PromptUIComponents'):
            interface = GradioInterface(self.mock_app_controller)
            interface.current_session_id = "test_session"
            interface.refinement_controller = mock_controller
        
        # 测试消息处理
        result = interface._handle_user_message("测试消息")
        
        # 验证结果
        chat_history, cleared_input, content, version_info, content_stats = result
        self.assertEqual(len(chat_history), 1)
        self.assertEqual(chat_history[0][0], "测试消息")
        self.assertEqual(chat_history[0][1], "AI响应")
        self.assertEqual(cleared_input, "")
        self.assertEqual(content, "修改后的内容")

    def test_clear_chat_history(self):
        """测试清空聊天历史 / Test clearing chat history"""
        result = self.interface._clear_chat_history()
        self.assertEqual(result, [])

    def test_get_version_info_no_session(self):
        """测试无会话时获取版本信息 / Test getting version info without session"""
        result = self.interface._get_version_info()
        self.assertIn("初始版本", result)
        self.assertIn("Initial", result)

    def test_get_content_stats_empty(self):
        """测试空内容统计 / Test empty content statistics"""
        result = self.interface._get_content_stats()
        self.assertIn("字数: 0", result)
        self.assertIn("Words: 0", result)

    def test_get_content_stats_with_content(self):
        """测试有内容时的统计 / Test content statistics with content"""
        self.interface.current_content = "测试内容\n第二段"
        result = self.interface._get_content_stats()
        
        # 验证字数和段落数统计
        self.assertIn("字数: 8", result)  # "测试内容\n第二段" = 8个字符
        self.assertIn("段落: 2", result)  # 两个段落

    @patch('src.ui.gradio_interface.RefinementController')
    def test_undo_last_modification_success(self, mock_refinement_controller_class):
        """测试成功撤销修改 / Test successful undo modification"""
        # 设置模拟的优化控制器
        mock_controller = Mock()
        mock_controller.undo_last_modification.return_value = {
            'success': True,
            'content': '撤销后的内容'
        }
        mock_refinement_controller_class.return_value = mock_controller
        
        # 重新创建界面实例
        with patch('src.ui.gradio_interface.PromptUIComponents'):
            interface = GradioInterface(self.mock_app_controller)
            interface.current_session_id = "test_session"
            interface.refinement_controller = mock_controller
        
        # 测试撤销操作
        result = interface._undo_last_modification()
        
        # 验证结果
        content, version_info, content_stats, chat_history = result
        self.assertEqual(content, "撤销后的内容")
        self.assertEqual(len(chat_history), 1)
        self.assertIn("已撤销", chat_history[0][1])

    def test_generate_summary_starts_session(self):
        """测试生成总结启动会话 / Test summary generation starts session"""
        # 设置模拟返回值
        self.mock_app_controller.process_case_summary.return_value = "生成的总结"
        
        # 模拟优化控制器
        mock_controller = Mock()
        mock_controller.start_refinement_session.return_value = "new_session_id"
        self.interface.refinement_controller = mock_controller
        
        # 测试生成总结
        result = self.interface._generate_summary("测试案例", "test_model", "测试提示词")
        
        # 验证会话已启动
        self.assertEqual(self.interface.current_session_id, "new_session_id")
        self.assertEqual(self.interface.current_content, "生成的总结")
        
        # 验证返回结果
        summary, status = result
        self.assertEqual(summary, "生成的总结")
        self.assertIn("成功", status)


if __name__ == '__main__':
    unittest.main()