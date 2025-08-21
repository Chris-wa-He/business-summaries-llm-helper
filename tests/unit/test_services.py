"""
服务模块单元测试 / Services Module Unit Tests

测试服务模块的各项功能
Test various functions of services module
"""

import pytest
from src.services.prompt_builder import PromptBuilder


class TestPromptBuilder:
    """PromptBuilder测试类 / PromptBuilder test class"""
    
    def setup_method(self):
        """测试方法设置 / Test method setup"""
        self.prompt_builder = PromptBuilder()
    
    def test_build_prompt_with_history(self):
        """测试构建包含历史信息的提示词 / Test building prompt with history"""
        case_input = "用户反映登录系统时出现认证失败的问题"
        history_reference = """
        ## 用户管理类别参考
        
        ### 文件: login_issues.txt
        用户登录系统时遇到认证失败的问题
        通常需要检查用户名和密码是否正确
        """
        system_prompt = "你是专业的案例总结助手"
        
        result = self.prompt_builder.build_prompt(case_input, history_reference, system_prompt)
        
        # 验证提示词包含所有必要部分 / Verify prompt contains all necessary parts
        assert "历史参考信息" in result or "Historical Reference Information" in result
        assert "需要总结的案例" in result or "Case to Summarize" in result
        assert "输出要求" in result or "Output Requirements" in result
        assert case_input in result
        assert "login_issues.txt" in result
    
    def test_build_prompt_without_history(self):
        """测试构建不包含历史信息的提示词 / Test building prompt without history"""
        case_input = "系统出现性能问题，响应时间过长"
        history_reference = ""
        system_prompt = "你是专业的案例总结助手"
        
        result = self.prompt_builder.build_prompt(case_input, history_reference, system_prompt)
        
        # 验证提示词包含案例和要求，但不包含历史信息 / Verify prompt contains case and requirements but no history
        assert "需要总结的案例" in result or "Case to Summarize" in result
        assert "输出要求" in result or "Output Requirements" in result
        assert case_input in result
        assert "历史参考信息" not in result and "Historical Reference Information" not in result
    
    def test_format_history_reference_normal(self):
        """测试格式化正常的历史参考信息 / Test formatting normal history reference"""
        history = """
        
        ## 类别1
        
        内容1
        
        
        内容2
        
        ## 类别2
        内容3
        
        
        """
        
        result = self.prompt_builder.format_history_reference(history)
        
        # 验证格式化结果 / Verify formatting result
        lines = result.split('\n')
        assert lines[0] == "## 类别1"
        assert lines[1] == ""
        assert lines[2] == "内容1"
        assert lines[3] == ""
        assert lines[4] == "内容2"
        
        # 验证没有多余的空行 / Verify no excessive empty lines
        assert not result.endswith('\n\n')
    
    def test_format_history_reference_empty(self):
        """测试格式化空的历史参考信息 / Test formatting empty history reference"""
        result = self.prompt_builder.format_history_reference("")
        assert result == ""
        
        result = self.prompt_builder.format_history_reference("   \n  \n  ")
        assert result == ""
    
    def test_format_history_reference_long_content(self):
        """测试格式化过长的历史参考信息 / Test formatting overly long history reference"""
        # 创建一个很长的历史信息 / Create very long history information
        long_content = "这是一个很长的内容。" * 2000  # 约30000字符 / About 30000 characters
        history = f"## 标题\n{long_content}"
        
        result = self.prompt_builder.format_history_reference(history)
        
        # 验证内容被截断 / Verify content is truncated
        assert len(result) < len(history)
        assert "标题" in result  # 标题应该被保留 / Title should be preserved
        assert "截断" in result or "truncated" in result  # 应该有截断提示 / Should have truncation notice
    
    def test_ensure_prompt_length_normal(self):
        """测试正常长度的提示词 / Test normal length prompt"""
        user_prompt = "这是一个正常长度的用户提示词"
        system_prompt = "这是系统提示词"
        
        result = self.prompt_builder._ensure_prompt_length(user_prompt, system_prompt)
        assert result == user_prompt
    
    def test_ensure_prompt_length_too_long(self):
        """测试过长的提示词 / Test overly long prompt"""
        # 创建一个超长的用户提示词 / Create overly long user prompt
        long_prompt = "这是一个很长的提示词。" * 3000  # 约45000字符 / About 45000 characters
        system_prompt = "系统提示词"
        
        result = self.prompt_builder._ensure_prompt_length(long_prompt, system_prompt)
        
        # 验证被截断 / Verify truncation
        assert len(result) < len(long_prompt)
        assert len(result) + len(system_prompt) <= self.prompt_builder.max_prompt_length
    
    def test_truncate_history_intelligently(self):
        """测试智能截断历史信息 / Test intelligent history truncation"""
        history = """
        # 重要标题
        这是重要信息
        
        ## 普通标题
        这是普通内容
        
        关键信息在这里
        
        """ + "普通内容。" * 1000  # 添加大量普通内容 / Add lots of regular content
        
        result = self.prompt_builder._truncate_history_intelligently(history)
        
        # 验证重要信息被保留 / Verify important information is preserved
        assert "重要标题" in result
        assert "重要信息" in result
        assert "关键信息" in result
        assert len(result) < len(history)
    
    def test_truncate_prompt_intelligently(self):
        """测试智能截断提示词 / Test intelligent prompt truncation"""
        prompt = """
        ## 历史参考信息
        一些历史信息
        
        ## 需要总结的案例
        这是需要总结的案例内容
        
        ## 输出要求
        请生成总结
        """ + "额外内容。" * 1000  # 添加大量额外内容 / Add lots of extra content
        
        max_length = 200
        result = self.prompt_builder._truncate_prompt_intelligently(prompt, max_length)
        
        # 验证关键部分被保留 / Verify key sections are preserved
        assert len(result) <= max_length + 100  # 允许一些缓冲 / Allow some buffer
        assert "需要总结的案例" in result or "Case to Summarize" in result
        assert "输出要求" in result or "Output Requirements" in result
    
    def test_create_system_message_format_with_prompt(self):
        """测试创建系统消息格式（有提示词）/ Test creating system message format with prompt"""
        system_prompt = "你是专业助手"
        result = self.prompt_builder.create_system_message_format(system_prompt)
        assert result == "你是专业助手"
    
    def test_create_system_message_format_empty_prompt(self):
        """测试创建系统消息格式（空提示词）/ Test creating system message format with empty prompt"""
        result = self.prompt_builder.create_system_message_format("")
        
        # 应该返回默认提示词 / Should return default prompt
        assert "专业的案例总结助手" in result
        assert "案例概述" in result
        assert "关键要点" in result
    
    def test_validate_prompt_components_valid(self):
        """测试验证有效的提示词组件 / Test validating valid prompt components"""
        case_input = "这是一个有效的案例输入内容"
        system_prompt = "这是系统提示词"
        
        result = self.prompt_builder.validate_prompt_components(case_input, system_prompt)
        assert result is True
    
    def test_validate_prompt_components_empty_case(self):
        """测试验证空案例输入 / Test validating empty case input"""
        case_input = ""
        system_prompt = "这是系统提示词"
        
        result = self.prompt_builder.validate_prompt_components(case_input, system_prompt)
        assert result is False
    
    def test_validate_prompt_components_short_case(self):
        """测试验证过短的案例输入 / Test validating short case input"""
        case_input = "短"  # 很短的输入 / Very short input
        system_prompt = "这是系统提示词"
        
        result = self.prompt_builder.validate_prompt_components(case_input, system_prompt)
        assert result is True  # 应该通过验证但有警告 / Should pass validation but with warning
    
    def test_validate_prompt_components_empty_system_prompt(self):
        """测试验证空系统提示词 / Test validating empty system prompt"""
        case_input = "这是有效的案例输入"
        system_prompt = ""
        
        result = self.prompt_builder.validate_prompt_components(case_input, system_prompt)
        assert result is True  # 应该通过验证但有警告 / Should pass validation but with warning
    
    def test_build_prompt_error_handling(self):
        """测试构建提示词的错误处理 / Test error handling in prompt building"""
        # 模拟异常情况 / Simulate exception scenario
        case_input = "正常案例输入"
        history_reference = None  # 可能导致错误的输入 / Input that might cause error
        system_prompt = "系统提示词"
        
        # 应该返回基础提示词而不是抛出异常 / Should return basic prompt instead of throwing exception
        result = self.prompt_builder.build_prompt(case_input, history_reference, system_prompt)
        
        assert "需要总结的案例" in result or "Case to Summarize" in result
        assert case_input in result
