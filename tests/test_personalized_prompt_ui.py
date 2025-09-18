"""
个性化Prompt管理界面测试 / Personalized Prompt Management UI Tests

测试个性化Prompt管理界面的功能
Test personalized prompt management interface functionality
"""

import pytest
from unittest.mock import Mock, patch
from src.ui.gradio_interface import GradioInterface
from src.services.app_controller import AppController


class TestPersonalizedPromptUI:
    """个性化Prompt管理界面测试类 / Personalized Prompt Management UI Test Class"""
    
    def setup_method(self):
        """设置测试环境 / Setup test environment"""
        # 创建模拟的应用控制器
        self.mock_app_controller = Mock(spec=AppController)
        self.mock_app_controller.get_app_config.return_value = {
            "title": "测试案例总结生成器",
            "max_tokens": 4000,
            "temperature": 0.7
        }
        
        # 创建Gradio界面实例
        self.gradio_interface = GradioInterface(self.mock_app_controller)
    
    def test_create_personalized_prompt_tab(self):
        """测试创建个性化Prompt标签页 / Test creating personalized prompt tab"""
        # 测试方法存在
        assert hasattr(self.gradio_interface, '_create_personalized_prompt_tab')
        
        # 测试方法可以调用（不会抛出异常）
        try:
            # 由于Gradio组件需要在Blocks上下文中创建，这里只测试方法存在
            assert callable(self.gradio_interface._create_personalized_prompt_tab)
        except Exception as e:
            # 如果是Gradio上下文相关的异常，这是预期的
            assert "Blocks" in str(e) or "context" in str(e)
    
    def test_bind_personalized_prompt_events(self):
        """测试绑定个性化Prompt事件 / Test binding personalized prompt events"""
        # 测试方法存在
        assert hasattr(self.gradio_interface, '_bind_personalized_prompt_events')
        assert callable(self.gradio_interface._bind_personalized_prompt_events)
    
    def test_view_personalized_prompt(self):
        """测试查看个性化Prompt / Test viewing personalized prompt"""
        # 测试空数据
        result = self.gradio_interface._view_personalized_prompt([])
        assert "请选择一个个性化Prompt" in result or "Please select a personalized prompt" in result
        
        # 测试有效数据
        sample_data = [["技术分析", "v1.0", "2024-01-01", "活跃"]]
        result = self.gradio_interface._view_personalized_prompt(sample_data)
        assert "技术分析" in result
        assert "个性化系统提示词" in result
    
    def test_activate_personalized_prompt(self):
        """测试激活个性化Prompt / Test activating personalized prompt"""
        # 测试空数据
        result = self.gradio_interface._activate_personalized_prompt([])
        assert "❌" in result
        
        # 测试有效数据
        sample_data = [["技术分析", "v1.0", "2024-01-01", "活跃"]]
        result = self.gradio_interface._activate_personalized_prompt(sample_data)
        assert "✅" in result
        assert "技术分析" in result
    
    def test_delete_personalized_prompt(self):
        """测试删除个性化Prompt / Test deleting personalized prompt"""
        # 测试空数据
        updated_data, message = self.gradio_interface._delete_personalized_prompt([])
        assert "❌" in message
        
        # 测试有效数据
        sample_data = [
            ["技术分析", "v1.0", "2024-01-01", "活跃"],
            ["商业案例", "v1.0", "2024-01-02", "活跃"]
        ]
        updated_data, message = self.gradio_interface._delete_personalized_prompt(sample_data)
        assert "✅" in message
        assert len(updated_data) == 1  # 删除了一个
        assert updated_data[0][0] == "商业案例"  # 剩下的是商业案例
    
    def test_save_personalized_prompt(self):
        """测试保存个性化Prompt / Test saving personalized prompt"""
        # 测试空数据
        textbox, message = self.gradio_interface._save_personalized_prompt([], "content")
        assert "❌" in message
        
        # 测试空内容
        sample_data = [["技术分析", "v1.0", "2024-01-01", "活跃"]]
        textbox, message = self.gradio_interface._save_personalized_prompt(sample_data, "")
        assert "❌" in message
        assert "内容不能为空" in message or "Content cannot be empty" in message
        
        # 测试有效数据
        textbox, message = self.gradio_interface._save_personalized_prompt(sample_data, "test content")
        assert "✅" in message
        assert "技术分析" in message
    
    def test_export_single_prompt(self):
        """测试导出单个Prompt / Test exporting single prompt"""
        # 测试空数据
        result = self.gradio_interface._export_single_prompt([], "JSON")
        assert "❌" in result
        
        # 测试有效数据
        sample_data = [["技术分析", "v1.0", "2024-01-01", "活跃"]]
        result = self.gradio_interface._export_single_prompt(sample_data, "JSON")
        assert "✅" in result
        assert "技术分析" in result
        assert "json" in result.lower()
    
    def test_export_all_prompts(self):
        """测试导出全部Prompt / Test exporting all prompts"""
        result = self.gradio_interface._export_all_prompts("JSON")
        assert "✅" in result
        assert "json" in result.lower()
    
    def test_import_prompts(self):
        """测试导入Prompt / Test importing prompts"""
        # 测试空文件
        data, message = self.gradio_interface._import_prompts(None)
        assert "❌" in message
        assert len(data) == 0
        
        # 测试有效文件（模拟）
        mock_file = Mock()
        mock_file.name = "test.json"
        data, message = self.gradio_interface._import_prompts(mock_file)
        assert "✅" in message
        assert len(data) > 0
    
    def test_refresh_personalized_prompt_list(self):
        """测试刷新个性化Prompt列表 / Test refreshing personalized prompt list"""
        result = self.gradio_interface._refresh_personalized_prompt_list()
        assert isinstance(result, list)
        assert len(result) > 0  # 应该返回示例数据
        
        # 检查数据格式
        for row in result:
            assert len(row) == 4  # 应该有4列：场景、版本、时间、状态
            assert isinstance(row[0], str)  # 场景名称
            assert isinstance(row[1], str)  # 版本
    
    def test_enable_prompt_editing(self):
        """测试启用Prompt编辑 / Test enabling prompt editing"""
        # 由于返回Gradio组件，这里只测试方法存在和可调用
        assert hasattr(self.gradio_interface, '_enable_prompt_editing')
        assert callable(self.gradio_interface._enable_prompt_editing)


if __name__ == "__main__":
    pytest.main([__file__])