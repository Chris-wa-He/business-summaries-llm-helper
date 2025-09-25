"""
用户反馈收集器 / User Feedback Collector

该模块负责收集和格式化用户反馈数据，用于个性化学习。
This module handles collection and formatting of user feedback data for personalized learning.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class UserFeedback:
    """用户反馈数据模型 / User Feedback Data Model"""
    user_id: str
    prompt_name: str
    original_content: str
    modified_content: str
    modification_request: str
    satisfaction_score: float  # 0.0 - 1.0
    modification_type: str
    timestamp: str


class FeedbackCollector:
    """用户反馈收集器 / User Feedback Collector"""
    
    def __init__(self):
        """初始化反馈收集器 / Initialize feedback collector"""
        self.feedback_history = {}  # {user_id: {prompt_name: [feedbacks]}}
    
    def collect_feedback(self, user_id: str, prompt_name: str, 
                        original_content: str, modified_content: str,
                        modification_request: str, satisfaction_score: float,
                        modification_type: str = "general") -> UserFeedback:
        """
        收集用户反馈 / Collect user feedback
        
        Args:
            user_id: 用户ID / User ID
            prompt_name: 提示词名称 / Prompt name
            original_content: 原始内容 / Original content
            modified_content: 修改后内容 / Modified content
            modification_request: 修改请求 / Modification request
            satisfaction_score: 满意度评分 / Satisfaction score
            modification_type: 修改类型 / Modification type
            
        Returns:
            UserFeedback: 反馈数据对象 / Feedback data object
        """
        feedback = UserFeedback(
            user_id=user_id,
            prompt_name=prompt_name,
            original_content=original_content,
            modified_content=modified_content,
            modification_request=modification_request,
            satisfaction_score=satisfaction_score,
            modification_type=modification_type,
            timestamp=datetime.now().isoformat()
        )
        
        # 存储反馈历史
        if user_id not in self.feedback_history:
            self.feedback_history[user_id] = {}
        if prompt_name not in self.feedback_history[user_id]:
            self.feedback_history[user_id][prompt_name] = []
        
        self.feedback_history[user_id][prompt_name].append(feedback)
        
        logging.info(f"Collected feedback from {user_id} for {prompt_name}")
        return feedback
    
    def get_user_feedback_history(self, user_id: str, prompt_name: str, 
                                 limit: int = 10) -> List[UserFeedback]:
        """
        获取用户反馈历史 / Get user feedback history
        
        Args:
            user_id: 用户ID / User ID
            prompt_name: 提示词名称 / Prompt name
            limit: 返回数量限制 / Return count limit
            
        Returns:
            List[UserFeedback]: 反馈历史列表 / Feedback history list
        """
        if user_id not in self.feedback_history:
            return []
        if prompt_name not in self.feedback_history[user_id]:
            return []
        
        feedbacks = self.feedback_history[user_id][prompt_name]
        return feedbacks[-limit:] if limit > 0 else feedbacks
    
    def format_feedback_for_llm(self, feedbacks: List[UserFeedback]) -> Dict[str, Any]:
        """
        格式化反馈数据供LLM分析 / Format feedback data for LLM analysis
        
        Args:
            feedbacks: 反馈列表 / Feedback list
            
        Returns:
            Dict: 格式化的反馈数据 / Formatted feedback data
        """
        if not feedbacks:
            return {
                'interaction_history': '',
                'user_feedback': '',
                'satisfaction_trends': []
            }
        
        # 构建交互历史
        interaction_history = []
        for feedback in feedbacks:
            interaction_history.append(f"""
修改请求: {feedback.modification_request}
修改类型: {feedback.modification_type}
满意度: {feedback.satisfaction_score}/1.0
时间: {feedback.timestamp}
""")
        
        # 构建用户反馈总结
        avg_satisfaction = sum(f.satisfaction_score for f in feedbacks) / len(feedbacks)
        modification_types = {}
        for feedback in feedbacks:
            mod_type = feedback.modification_type
            if mod_type not in modification_types:
                modification_types[mod_type] = []
            modification_types[mod_type].append(feedback.satisfaction_score)
        
        user_feedback_summary = f"""
总交互次数: {len(feedbacks)}
平均满意度: {avg_satisfaction:.2f}
修改类型偏好: {self._analyze_modification_preferences(modification_types)}
最近趋势: {self._analyze_satisfaction_trend(feedbacks)}
"""
        
        return {
            'interaction_history': '\n'.join(interaction_history),
            'user_feedback': user_feedback_summary,
            'satisfaction_trends': [f.satisfaction_score for f in feedbacks]
        }
    
    def _analyze_modification_preferences(self, modification_types: Dict[str, List[float]]) -> str:
        """分析修改类型偏好 / Analyze modification type preferences"""
        preferences = []
        for mod_type, scores in modification_types.items():
            avg_score = sum(scores) / len(scores)
            preferences.append(f"{mod_type}({avg_score:.2f})")
        return ', '.join(preferences)
    
    def _analyze_satisfaction_trend(self, feedbacks: List[UserFeedback]) -> str:
        """分析满意度趋势 / Analyze satisfaction trend"""
        if len(feedbacks) < 2:
            return "数据不足"
        
        recent_scores = [f.satisfaction_score for f in feedbacks[-3:]]
        early_scores = [f.satisfaction_score for f in feedbacks[:3]]
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        early_avg = sum(early_scores) / len(early_scores)
        
        if recent_avg > early_avg + 0.1:
            return "满意度上升"
        elif recent_avg < early_avg - 0.1:
            return "满意度下降"
        else:
            return "满意度稳定"
    
    def should_trigger_learning(self, user_id: str, prompt_name: str) -> bool:
        """
        判断是否应该触发学习更新 / Determine if learning update should be triggered
        
        Args:
            user_id: 用户ID / User ID
            prompt_name: 提示词名称 / Prompt name
            
        Returns:
            bool: 是否应该触发学习 / Whether learning should be triggered
        """
        feedbacks = self.get_user_feedback_history(user_id, prompt_name)
        
        if len(feedbacks) < 3:
            return False
        
        # 检查最近的反馈是否有足够的数据进行学习
        recent_feedbacks = feedbacks[-5:]
        avg_satisfaction = sum(f.satisfaction_score for f in recent_feedbacks) / len(recent_feedbacks)
        
        # 如果满意度较低或者有足够的交互数据，触发学习
        return avg_satisfaction < 0.7 or len(feedbacks) % 5 == 0