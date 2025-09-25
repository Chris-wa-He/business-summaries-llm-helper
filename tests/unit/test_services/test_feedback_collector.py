"""
反馈收集器单元测试 / Feedback Collector Unit Tests
"""

import pytest
from datetime import datetime

from src.services.feedback_collector import FeedbackCollector, UserFeedback


class TestFeedbackCollector:
    """反馈收集器测试类 / Feedback Collector Test Class"""
    
    def setup_method(self):
        """测试前设置 / Setup before each test"""
        self.collector = FeedbackCollector()
    
    def test_init(self):
        """测试初始化 / Test initialization"""
        assert self.collector.feedback_history == {}
    
    def test_collect_feedback(self):
        """测试收集反馈 / Test collect feedback"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        original_content = "Original content"
        modified_content = "Modified content"
        modification_request = "Make it more formal"
        satisfaction_score = 0.8
        modification_type = "style"
        
        feedback = self.collector.collect_feedback(
            user_id, prompt_name, original_content, modified_content,
            modification_request, satisfaction_score, modification_type
        )
        
        assert isinstance(feedback, UserFeedback)
        assert feedback.user_id == user_id
        assert feedback.prompt_name == prompt_name
        assert feedback.original_content == original_content
        assert feedback.modified_content == modified_content
        assert feedback.modification_request == modification_request
        assert feedback.satisfaction_score == satisfaction_score
        assert feedback.modification_type == modification_type
        assert feedback.timestamp is not None
        
        # Check feedback is stored
        assert user_id in self.collector.feedback_history
        assert prompt_name in self.collector.feedback_history[user_id]
        assert len(self.collector.feedback_history[user_id][prompt_name]) == 1
    
    def test_collect_multiple_feedbacks(self):
        """测试收集多个反馈 / Test collect multiple feedbacks"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        
        # Collect first feedback
        feedback1 = self.collector.collect_feedback(
            user_id, prompt_name, "content1", "modified1", "request1", 0.7, "type1"
        )
        
        # Collect second feedback
        feedback2 = self.collector.collect_feedback(
            user_id, prompt_name, "content2", "modified2", "request2", 0.9, "type2"
        )
        
        # Check both feedbacks are stored
        feedbacks = self.collector.feedback_history[user_id][prompt_name]
        assert len(feedbacks) == 2
        assert feedbacks[0] == feedback1
        assert feedbacks[1] == feedback2
    
    def test_get_user_feedback_history_empty(self):
        """测试获取空的用户反馈历史 / Test get empty user feedback history"""
        result = self.collector.get_user_feedback_history("nonexistent_user", "test_prompt")
        assert result == []
    
    def test_get_user_feedback_history_with_data(self):
        """测试获取包含数据的用户反馈历史 / Test get user feedback history with data"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        
        # Add some feedbacks
        feedback1 = self.collector.collect_feedback(
            user_id, prompt_name, "content1", "modified1", "request1", 0.7, "type1"
        )
        feedback2 = self.collector.collect_feedback(
            user_id, prompt_name, "content2", "modified2", "request2", 0.9, "type2"
        )
        
        result = self.collector.get_user_feedback_history(user_id, prompt_name)
        
        assert len(result) == 2
        assert result[0] == feedback1
        assert result[1] == feedback2
    
    def test_get_user_feedback_history_with_limit(self):
        """测试获取限制数量的用户反馈历史 / Test get user feedback history with limit"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        
        # Add 5 feedbacks
        for i in range(5):
            self.collector.collect_feedback(
                user_id, prompt_name, f"content{i}", f"modified{i}", 
                f"request{i}", 0.8, f"type{i}"
            )
        
        # Get last 3 feedbacks
        result = self.collector.get_user_feedback_history(user_id, prompt_name, limit=3)
        
        assert len(result) == 3
        assert result[0].modification_request == "request2"  # Last 3: 2, 3, 4
        assert result[1].modification_request == "request3"
        assert result[2].modification_request == "request4"
    
    def test_format_feedback_for_llm_empty(self):
        """测试格式化空反馈数据 / Test format empty feedback data for LLM"""
        result = self.collector.format_feedback_for_llm([])
        
        assert result['interaction_history'] == ''
        assert result['user_feedback'] == ''
        assert result['satisfaction_trends'] == []
    
    def test_format_feedback_for_llm_with_data(self):
        """测试格式化包含数据的反馈 / Test format feedback data with data for LLM"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        
        # Create some feedbacks
        feedbacks = []
        for i in range(3):
            feedback = self.collector.collect_feedback(
                user_id, prompt_name, f"content{i}", f"modified{i}",
                f"request{i}", 0.7 + i * 0.1, f"type{i}"
            )
            feedbacks.append(feedback)
        
        result = self.collector.format_feedback_for_llm(feedbacks)
        
        assert 'interaction_history' in result
        assert 'user_feedback' in result
        assert 'satisfaction_trends' in result
        
        # Check interaction history contains requests
        assert 'request0' in result['interaction_history']
        assert 'request1' in result['interaction_history']
        assert 'request2' in result['interaction_history']
        
        # Check satisfaction trends
        expected_trends = [0.7, 0.8, 0.9]
        actual_trends = result['satisfaction_trends']
        assert len(actual_trends) == len(expected_trends)
        for i, (actual, expected) in enumerate(zip(actual_trends, expected_trends)):
            assert abs(actual - expected) < 0.001, f"Index {i}: {actual} != {expected}"
        
        # Check user feedback summary contains statistics
        assert '总交互次数: 3' in result['user_feedback']
        assert '平均满意度: 0.80' in result['user_feedback']
    
    def test_analyze_modification_preferences(self):
        """测试分析修改类型偏好 / Test analyze modification preferences"""
        modification_types = {
            'style': [0.8, 0.9, 0.7],
            'content': [0.6, 0.8],
            'format': [0.9]
        }
        
        result = self.collector._analyze_modification_preferences(modification_types)
        
        assert 'style(0.80)' in result
        assert 'content(0.70)' in result
        assert 'format(0.90)' in result
    
    def test_analyze_satisfaction_trend_insufficient_data(self):
        """测试分析满意度趋势 - 数据不足 / Test analyze satisfaction trend - insufficient data"""
        feedbacks = [
            UserFeedback("user", "prompt", "orig", "mod", "req", 0.8, "type", "2024-01-01")
        ]
        
        result = self.collector._analyze_satisfaction_trend(feedbacks)
        assert result == "数据不足"
    
    def test_analyze_satisfaction_trend_rising(self):
        """测试分析满意度趋势 - 上升 / Test analyze satisfaction trend - rising"""
        feedbacks = []
        # Early feedbacks with lower scores
        for i in range(3):
            feedbacks.append(UserFeedback(
                "user", "prompt", "orig", "mod", "req", 0.5, "type", f"2024-01-0{i+1}"
            ))
        # Recent feedbacks with higher scores
        for i in range(3):
            feedbacks.append(UserFeedback(
                "user", "prompt", "orig", "mod", "req", 0.8, "type", f"2024-01-0{i+4}"
            ))
        
        result = self.collector._analyze_satisfaction_trend(feedbacks)
        assert result == "满意度上升"
    
    def test_analyze_satisfaction_trend_falling(self):
        """测试分析满意度趋势 - 下降 / Test analyze satisfaction trend - falling"""
        feedbacks = []
        # Early feedbacks with higher scores
        for i in range(3):
            feedbacks.append(UserFeedback(
                "user", "prompt", "orig", "mod", "req", 0.9, "type", f"2024-01-0{i+1}"
            ))
        # Recent feedbacks with lower scores
        for i in range(3):
            feedbacks.append(UserFeedback(
                "user", "prompt", "orig", "mod", "req", 0.5, "type", f"2024-01-0{i+4}"
            ))
        
        result = self.collector._analyze_satisfaction_trend(feedbacks)
        assert result == "满意度下降"
    
    def test_analyze_satisfaction_trend_stable(self):
        """测试分析满意度趋势 - 稳定 / Test analyze satisfaction trend - stable"""
        feedbacks = []
        # All feedbacks with similar scores
        for i in range(6):
            feedbacks.append(UserFeedback(
                "user", "prompt", "orig", "mod", "req", 0.75, "type", f"2024-01-0{i+1}"
            ))
        
        result = self.collector._analyze_satisfaction_trend(feedbacks)
        assert result == "满意度稳定"
    
    def test_should_trigger_learning_insufficient_data(self):
        """测试是否应该触发学习 - 数据不足 / Test should trigger learning - insufficient data"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        
        # Add only 2 feedbacks
        for i in range(2):
            self.collector.collect_feedback(
                user_id, prompt_name, f"content{i}", f"modified{i}",
                f"request{i}", 0.8, f"type{i}"
            )
        
        result = self.collector.should_trigger_learning(user_id, prompt_name)
        assert result is False
    
    def test_should_trigger_learning_low_satisfaction(self):
        """测试是否应该触发学习 - 低满意度 / Test should trigger learning - low satisfaction"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        
        # Add feedbacks with low satisfaction
        for i in range(5):
            self.collector.collect_feedback(
                user_id, prompt_name, f"content{i}", f"modified{i}",
                f"request{i}", 0.5, f"type{i}"  # Low satisfaction
            )
        
        result = self.collector.should_trigger_learning(user_id, prompt_name)
        assert result is True
    
    def test_should_trigger_learning_enough_interactions(self):
        """测试是否应该触发学习 - 足够的交互数据 / Test should trigger learning - enough interactions"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        
        # Add exactly 5 feedbacks (multiple of 5)
        for i in range(5):
            self.collector.collect_feedback(
                user_id, prompt_name, f"content{i}", f"modified{i}",
                f"request{i}", 0.8, f"type{i}"  # High satisfaction
            )
        
        result = self.collector.should_trigger_learning(user_id, prompt_name)
        assert result is True
    
    def test_should_trigger_learning_high_satisfaction_not_multiple(self):
        """测试是否应该触发学习 - 高满意度且非倍数 / Test should trigger learning - high satisfaction not multiple"""
        user_id = "test_user"
        prompt_name = "test_prompt"
        
        # Add 4 feedbacks with high satisfaction (not multiple of 5)
        for i in range(4):
            self.collector.collect_feedback(
                user_id, prompt_name, f"content{i}", f"modified{i}",
                f"request{i}", 0.9, f"type{i}"  # High satisfaction
            )
        
        result = self.collector.should_trigger_learning(user_id, prompt_name)
        assert result is False