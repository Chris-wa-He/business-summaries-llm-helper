"""
个性化偏好学习引擎 / Personalized Preference Learning Engine

实现基于用户交互历史的偏好学习和智能建议生成。
Implements preference learning and intelligent suggestion generation based on user interaction history.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

from ..models.refinement_models import UserPreferenceProfile
from .preference_storage import PreferenceStorage

logger = logging.getLogger(__name__)


@dataclass
class ProactiveSuggestion:
    """主动建议数据模型 / Proactive Suggestion Data Model"""
    id: str
    content: str
    category: str  # 'style', 'structure', 'content', 'format'
    confidence: float
    reasoning: str
    applicable_context: str


class PreferenceLearningEngine:
    """偏好学习引擎 - 支持系统提示词级别的个性化学习"""
    
    def __init__(self):
        # 为每个系统提示词维护独立的偏好模型
        self.prompt_preferences = {}  # {prompt_name: {user_id: UserPreferenceProfile}}
        self.learning_rate = 0.1
        self.preference_decay_rate = 0.95  # 偏好衰减率，避免过度拟合
        
        # 初始化持久化存储
        self.storage = PreferenceStorage()
        
        logger.info("偏好学习引擎初始化完成")
        
    def get_user_preference_profile(self, user_id: str, prompt_name: str) -> UserPreferenceProfile:
        """获取用户在特定系统提示词下的偏好档案"""
        if prompt_name not in self.prompt_preferences:
            self.prompt_preferences[prompt_name] = {}
            
        if user_id not in self.prompt_preferences[prompt_name]:
            # 尝试从存储加载
            stored_data = self.storage.load_user_preferences(user_id, prompt_name)
            
            if stored_data:
                # 从存储数据恢复偏好档案
                profile = self._restore_profile_from_storage(stored_data)
                self.prompt_preferences[prompt_name][user_id] = profile
                logger.info(f"从存储恢复偏好档案: {user_id}/{prompt_name}")
            else:
                # 创建新的偏好档案
                profile = UserPreferenceProfile(
                    user_id=user_id,
                    prompt_name=prompt_name,
                    modification_preferences=self.initialize_modification_preferences(),
                    style_preferences=self.initialize_style_preferences(),
                    interaction_patterns=self.initialize_interaction_patterns(),
                    content_structure_preferences=self.initialize_structure_preferences(),
                    success_history=[],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                self.prompt_preferences[prompt_name][user_id] = profile
                # 保存到存储
                self._save_profile_to_storage(profile)
        
        return self.prompt_preferences[prompt_name][user_id]
    
    def initialize_modification_preferences(self) -> Dict[str, float]:
        """初始化修改类型偏好"""
        return {
            'structural': 0.5,
            'content_addition': 0.5,
            'content_removal': 0.5,
            'style_adjustment': 0.5,
            'format_modification': 0.5,
            'language_optimization': 0.5
        }
    
    def initialize_style_preferences(self) -> Dict[str, Any]:
        """初始化语言风格偏好"""
        return {
            'formality': 'balanced',  # formal/informal/balanced
            'detail_preference': 'moderate',  # detailed/concise/moderate
            'technical_depth': 'appropriate',  # deep/surface/appropriate
            'tone': 'professional',  # professional/friendly/authoritative
            'sentence_length': 'mixed'  # short/long/mixed
        }
    
    def initialize_interaction_patterns(self) -> Dict[str, Any]:
        """初始化交互模式偏好"""
        return {
            'preferred_modification_size': 'medium',  # small/medium/large
            'feedback_frequency': 'periodic',  # immediate/periodic/final
            'guidance_level': 'moderate'  # minimal/moderate/detailed
        }
    
    def initialize_structure_preferences(self) -> Dict[str, Any]:
        """初始化内容结构偏好"""
        return {
            'preferred_sections': ['概述', '分析', '结论', '建议'],
            'section_order': ['概述', '分析', '结论', '建议'],
            'paragraph_length': 'medium',
            'bullet_point_style': 'standard'
        }
    
    def update_preferences_from_interaction(self, user_id: str, prompt_name: str, 
                                          interaction_data: Dict) -> None:
        """从用户交互中更新偏好"""
        profile = self.get_user_preference_profile(user_id, prompt_name)
        
        # 1. 更新修改类型偏好
        if 'modification_type' in interaction_data:
            mod_type = interaction_data['modification_type']
            success_score = interaction_data.get('user_satisfaction', 0.5)
            
            current_weight = profile.modification_preferences.get(mod_type, 0.5)
            new_weight = current_weight + self.learning_rate * (success_score - current_weight)
            profile.modification_preferences[mod_type] = new_weight
        
        # 2. 更新语言风格偏好
        if 'style_feedback' in interaction_data:
            style_data = interaction_data['style_feedback']
            for style_aspect, preference in style_data.items():
                profile.style_preferences[style_aspect] = preference
        
        # 3. 更新交互模式偏好
        if 'interaction_pattern' in interaction_data:
            pattern = interaction_data['interaction_pattern']
            profile.interaction_patterns[pattern['type']] = pattern['effectiveness']
        
        # 4. 记录成功历史
        if interaction_data.get('success', False):
            profile.success_history.append({
                'timestamp': datetime.now(),
                'modification_type': interaction_data.get('modification_type'),
                'satisfaction_score': interaction_data.get('user_satisfaction', 0.5),
                'content_length_before': interaction_data.get('content_length_before'),
                'content_length_after': interaction_data.get('content_length_after'),
                'modification_complexity': interaction_data.get('complexity_score', 0.5)
            })
        
        # 5. 应用偏好衰减，避免过度拟合
        self.apply_preference_decay(profile)
        
        profile.updated_at = datetime.now()
        
        # 保存到持久化存储
        self._save_profile_to_storage(profile)
        
        logger.info(f"更新用户偏好: {user_id}/{prompt_name}")
    
    def apply_preference_decay(self, profile: UserPreferenceProfile) -> None:
        """应用偏好衰减"""
        for mod_type in profile.modification_preferences:
            current_value = profile.modification_preferences[mod_type]
            # 向中性值0.5衰减
            profile.modification_preferences[mod_type] = (
                current_value * self.preference_decay_rate + 
                0.5 * (1 - self.preference_decay_rate)
            )
    
    def generate_personalized_guidance(self, user_id: str, prompt_name: str, 
                                     current_content: str, context: str) -> Dict[str, Any]:
        """为后续生成提供个性化指引"""
        profile = self.get_user_preference_profile(user_id, prompt_name)
        
        guidance = {
            'preferred_modification_types': self.get_top_preferred_modifications(profile),
            'style_guidance': self.generate_style_guidance(profile, current_content),
            'structure_suggestions': self.generate_structure_suggestions(profile, current_content),
            'interaction_recommendations': self.generate_interaction_recommendations(profile),
            'proactive_suggestions': self.generate_proactive_suggestions(profile, current_content, context)
        }
        
        return guidance
    
    def get_top_preferred_modifications(self, profile: UserPreferenceProfile) -> List[Dict]:
        """获取用户最偏好的修改类型"""
        sorted_prefs = sorted(
            profile.modification_preferences.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [
            {
                'type': mod_type,
                'weight': weight,
                'description': self.get_modification_description(mod_type)
            }
            for mod_type, weight in sorted_prefs[:3] if weight > 0.6
        ]
    
    def get_modification_description(self, mod_type: str) -> str:
        """获取修改类型描述"""
        descriptions = {
            'structural': '结构调整 - 重新组织内容结构',
            'content_addition': '内容补充 - 添加更多详细信息',
            'content_removal': '内容精简 - 删除冗余信息',
            'style_adjustment': '风格调整 - 改变语言表达风格',
            'format_modification': '格式修改 - 调整文档格式',
            'language_optimization': '语言优化 - 提升表达质量'
        }
        return descriptions.get(mod_type, '未知修改类型')
    
    def generate_style_guidance(self, profile: UserPreferenceProfile, content: str) -> Dict[str, Any]:
        """生成语言风格指引"""
        style_prefs = profile.style_preferences
        
        guidance = {
            'formality_level': style_prefs.get('formality', 'balanced'),
            'detail_level': style_prefs.get('detail_preference', 'moderate'),
            'technical_depth': style_prefs.get('technical_depth', 'appropriate'),
            'tone': style_prefs.get('tone', 'professional'),
            'preferred_sentence_length': style_prefs.get('sentence_length', 'mixed')
        }
        
        # 基于当前内容分析，提供具体建议
        current_style = self.analyze_current_style(content)
        guidance['adjustment_suggestions'] = self.compare_styles(current_style, style_prefs)
        
        return guidance
    
    def analyze_current_style(self, content: str) -> Dict[str, Any]:
        """分析当前内容的风格特征"""
        # 简化的风格分析
        sentences = content.split('。')
        avg_sentence_length = sum(len(s) for s in sentences) / max(len(sentences), 1)
        
        return {
            'avg_sentence_length': avg_sentence_length,
            'formality_score': 0.5,  # 简化实现
            'technical_density': 0.5
        }
    
    def compare_styles(self, current_style: Dict, preferred_style: Dict) -> List[str]:
        """对比当前风格与偏好风格，生成调整建议"""
        suggestions = []
        
        # 句子长度建议
        if current_style['avg_sentence_length'] > 50 and preferred_style.get('sentence_length') == 'short':
            suggestions.append("建议使用更短的句子以提高可读性")
        elif current_style['avg_sentence_length'] < 20 and preferred_style.get('sentence_length') == 'long':
            suggestions.append("可以使用更复杂的句式来丰富表达")
        
        return suggestions
    
    def generate_structure_suggestions(self, profile: UserPreferenceProfile, 
                                     current_content: str) -> List[str]:
        """生成结构建议"""
        suggestions = []
        preferred_sections = profile.content_structure_preferences.get('preferred_sections', [])
        
        # 检查是否包含偏好的章节
        for section in preferred_sections:
            if section not in current_content:
                suggestions.append(f"建议添加'{section}'部分")
        
        return suggestions
    
    def generate_interaction_recommendations(self, profile: UserPreferenceProfile) -> Dict[str, str]:
        """生成交互建议"""
        patterns = profile.interaction_patterns
        
        return {
            'modification_size': f"建议使用{patterns.get('preferred_modification_size', 'medium')}规模的修改",
            'feedback_timing': f"推荐{patterns.get('feedback_frequency', 'periodic')}反馈频率",
            'guidance_level': f"提供{patterns.get('guidance_level', 'moderate')}级别的指导"
        }
    
    def generate_proactive_suggestions(self, profile: UserPreferenceProfile, 
                                     current_content: str, context: str) -> List[ProactiveSuggestion]:
        """生成主动建议"""
        suggestions = []
        
        logger.info(f"开始生成主动建议，内容长度: {len(current_content)}, 用户: {profile.user_id}")
        
        # 基于历史成功模式生成建议
        successful_patterns = self.analyze_success_patterns(profile.success_history)
        logger.info(f"分析到 {len(successful_patterns)} 个成功模式")
        
        for pattern in successful_patterns:
            if self.is_pattern_applicable(pattern, current_content, context):
                suggestion = self.generate_suggestion_from_pattern(pattern, current_content)
                if suggestion:
                    suggestions.append(suggestion)
        
        # 基于系统提示词特性生成建议
        prompt_specific_suggestions = self.generate_prompt_specific_suggestions(
            profile.prompt_name, current_content, profile
        )
        logger.info(f"生成了 {len(prompt_specific_suggestions)} 个提示词特定建议")
        suggestions.extend(prompt_specific_suggestions)
        
        # 如果没有任何建议，生成基础建议
        if not suggestions:
            logger.info("没有生成任何建议，添加基础建议")
            suggestions.extend(self.generate_basic_suggestions(current_content))
        
        logger.info(f"总共生成 {len(suggestions)} 个建议")
        return suggestions[:5]  # 最多返回5个主动建议
    
    def analyze_success_patterns(self, success_history: List[Dict]) -> List[Dict]:
        """分析成功模式"""
        if not success_history:
            return []
        
        # 简化的模式分析
        patterns = []
        
        # 分析高满意度的修改类型
        high_satisfaction_mods = [
            h for h in success_history 
            if h.get('satisfaction_score', 0) > 0.7
        ]
        
        if high_satisfaction_mods:
            common_types = {}
            for mod in high_satisfaction_mods:
                mod_type = mod.get('modification_type')
                if mod_type:
                    common_types[mod_type] = common_types.get(mod_type, 0) + 1
            
            # 找出最常见的成功修改类型
            if common_types:
                most_common = max(common_types.items(), key=lambda x: x[1])
                patterns.append({
                    'type': 'successful_modification',
                    'modification_type': most_common[0],
                    'frequency': most_common[1],
                    'confidence': min(most_common[1] / len(success_history), 1.0)
                })
        
        return patterns
    
    def is_pattern_applicable(self, pattern: Dict, current_content: str, context: str) -> bool:
        """判断模式是否适用于当前内容"""
        # 简化的适用性判断
        if pattern['type'] == 'successful_modification':
            # 如果内容长度合适且置信度足够，则适用
            return len(current_content) > 10 and pattern['confidence'] > 0.1
        
        return False
    
    def generate_suggestion_from_pattern(self, pattern: Dict, current_content: str) -> Optional[ProactiveSuggestion]:
        """从模式生成建议"""
        if pattern['type'] == 'successful_modification':
            mod_type = pattern['modification_type']
            
            suggestion_templates = {
                'content_addition': "基于您的偏好，建议添加更多详细信息来丰富内容",
                'style_adjustment': "根据您的历史偏好，建议调整语言风格使其更符合您的要求",
                'structural': "建议重新组织内容结构以提高逻辑性",
                'format_modification': "建议调整格式以提高可读性"
            }
            
            if mod_type in suggestion_templates:
                return ProactiveSuggestion(
                    id=f"pattern_{mod_type}_{datetime.now().timestamp()}",
                    content=suggestion_templates[mod_type],
                    category=mod_type,
                    confidence=pattern['confidence'],
                    reasoning=f"基于您{pattern['frequency']}次成功的{mod_type}修改经验",
                    applicable_context="通用"
                )
        
        return None
    
    def generate_prompt_specific_suggestions(self, prompt_name: str, current_content: str, 
                                           profile: UserPreferenceProfile) -> List[ProactiveSuggestion]:
        """基于系统提示词特性生成建议"""
        suggestions = []
        
        logger.info(f"为提示词 '{prompt_name}' 生成特定建议，内容长度: {len(current_content)}")
        
        # 根据不同的提示词类型生成特定建议
        if "技术" in prompt_name or "technical" in prompt_name.lower():
            suggestions.append(ProactiveSuggestion(
                id=f"tech_{datetime.now().timestamp()}",
                content="建议添加技术细节和实现方案",
                category="content_addition",
                confidence=0.8,
                reasoning="技术类提示词通常需要详细的技术说明",
                applicable_context="技术文档"
            ))
        
        if "业务" in prompt_name or "business" in prompt_name.lower():
            suggestions.append(ProactiveSuggestion(
                id=f"business_{datetime.now().timestamp()}",
                content="建议添加业务影响分析和ROI评估",
                category="content_addition",
                confidence=0.7,
                reasoning="业务类提示词通常需要商业价值分析",
                applicable_context="业务文档"
            ))
        
        # 基于内容长度的通用建议（降低阈值）
        if len(current_content) < 500:  # 从300改为500
            suggestions.append(ProactiveSuggestion(
                id=f"general_detail_{datetime.now().timestamp()}",
                content="建议添加更多具体细节和案例说明",
                category="content_addition",
                confidence=0.6,
                reasoning="内容相对较短，可以通过添加细节来丰富内容",
                applicable_context="通用"
            ))
        
        if len(current_content) > 1500:  # 添加长内容建议
            suggestions.append(ProactiveSuggestion(
                id=f"general_simplify_{datetime.now().timestamp()}",
                content="建议精简内容，突出重点信息",
                category="content_removal",
                confidence=0.6,
                reasoning="内容较长，可以通过精简来提高可读性",
                applicable_context="通用"
            ))
        
        # 检查是否包含总结关键词（放宽条件）
        content_lower = current_content.lower()
        if any(keyword in content_lower for keyword in ["总结", "summary", "概述", "结论"]):
            suggestions.append(ProactiveSuggestion(
                id=f"structure_{datetime.now().timestamp()}",
                content="建议优化总结结构，突出关键要点",
                category="structural",
                confidence=0.7,
                reasoning="总结类内容需要清晰的结构和重点突出",
                applicable_context="总结文档"
            ))
        
        logger.info(f"生成了 {len(suggestions)} 个提示词特定建议")
        return suggestions
    
    def generate_basic_suggestions(self, current_content: str) -> List[ProactiveSuggestion]:
        """生成基础建议（当没有其他建议时使用）"""
        suggestions = []
        content_length = len(current_content)
        
        logger.info(f"生成基础建议，内容长度: {content_length}")
        
        # 基于内容长度的基础建议
        if content_length < 200:
            suggestions.append(ProactiveSuggestion(
                id=f"basic_expand_{datetime.now().timestamp()}",
                content="建议扩展内容，添加更多详细信息",
                category="content_addition",
                confidence=0.8,
                reasoning="内容较短，需要添加更多细节",
                applicable_context="通用"
            ))
        
        # 通用的结构优化建议
        suggestions.append(ProactiveSuggestion(
            id=f"basic_structure_{datetime.now().timestamp()}",
            content="建议优化内容结构，增强逻辑性",
            category="structural",
            confidence=0.6,
            reasoning="良好的结构有助于提高内容的可读性",
            applicable_context="通用"
        ))
        
        # 通用的风格调整建议
        suggestions.append(ProactiveSuggestion(
            id=f"basic_style_{datetime.now().timestamp()}",
            content="建议调整语言风格，使其更加专业",
            category="style_adjustment",
            confidence=0.5,
            reasoning="专业的语言风格有助于提升内容质量",
            applicable_context="通用"
        ))
        
        logger.info(f"生成了 {len(suggestions)} 个基础建议")
        return suggestions
    
    def cross_prompt_learning(self, user_id: str) -> None:
        """跨系统提示词的偏好学习"""
        user_profiles = []
        
        # 收集用户在所有系统提示词下的偏好档案
        for prompt_name, prompt_users in self.prompt_preferences.items():
            if user_id in prompt_users:
                user_profiles.append(prompt_users[user_id])
        
        if len(user_profiles) < 2:
            return  # 需要至少2个档案才能进行跨提示词学习
        
        # 识别通用偏好模式
        common_patterns = self.identify_common_patterns(user_profiles)
        
        # 将通用模式应用到偏好较少的档案中
        for profile in user_profiles:
            if len(profile.success_history) < 5:  # 经验较少的档案
                self.apply_common_patterns(profile, common_patterns)
                
        logger.info(f"完成用户{user_id}的跨提示词学习")
    
    def identify_common_patterns(self, profiles: List[UserPreferenceProfile]) -> Dict[str, Any]:
        """识别通用偏好模式"""
        common_patterns = {
            'modification_preferences': {},
            'style_preferences': {},
            'interaction_patterns': {}
        }
        
        # 计算修改偏好的平均值
        for mod_type in ['structural', 'content_addition', 'content_removal', 
                        'style_adjustment', 'format_modification', 'language_optimization']:
            values = [p.modification_preferences.get(mod_type, 0.5) for p in profiles]
            common_patterns['modification_preferences'][mod_type] = sum(values) / len(values)
        
        return common_patterns
    
    def apply_common_patterns(self, profile: UserPreferenceProfile, common_patterns: Dict) -> None:
        """将通用模式应用到偏好档案"""
        # 对经验较少的档案，使用通用模式进行初始化
        for mod_type, common_value in common_patterns['modification_preferences'].items():
            current_value = profile.modification_preferences.get(mod_type, 0.5)
            # 加权平均：70%通用模式 + 30%个人偏好
            profile.modification_preferences[mod_type] = common_value * 0.7 + current_value * 0.3
    
    def generate_learning_insights(self, user_id: str, prompt_name: str) -> Dict[str, Any]:
        """生成学习洞察报告"""
        profile = self.get_user_preference_profile(user_id, prompt_name)
        
        insights = {
            'preference_summary': {
                'dominant_modification_types': self.get_top_preferred_modifications(profile),
                'style_profile': profile.style_preferences,
                'interaction_efficiency': self.calculate_interaction_efficiency(profile)
            },
            'learning_progress': {
                'total_interactions': len(profile.success_history),
                'success_rate': self.calculate_success_rate(profile),
                'preference_stability': self.calculate_preference_stability(profile)
            },
            'recommendations': {
                'optimization_suggestions': self.generate_optimization_suggestions(profile),
                'learning_opportunities': self.identify_learning_opportunities(profile)
            }
        }
        
        return insights
    
    def calculate_interaction_efficiency(self, profile: UserPreferenceProfile) -> float:
        """计算交互效率"""
        if not profile.success_history:
            return 0.0
        
        recent_history = profile.success_history[-10:]  # 最近10次交互
        avg_satisfaction = sum(h.get('satisfaction_score', 0) for h in recent_history) / len(recent_history)
        return avg_satisfaction
    
    def calculate_success_rate(self, profile: UserPreferenceProfile) -> float:
        """计算成功率"""
        if not profile.success_history:
            return 0.0
        
        successful_interactions = sum(1 for h in profile.success_history if h.get('satisfaction_score', 0) > 0.6)
        return successful_interactions / len(profile.success_history)
    
    def calculate_preference_stability(self, profile: UserPreferenceProfile) -> float:
        """计算偏好稳定性"""
        # 简化实现：基于成功历史的长度和一致性
        if len(profile.success_history) < 3:
            return 0.3  # 数据不足，稳定性较低
        
        # 检查最近的偏好是否一致
        recent_mods = [h.get('modification_type') for h in profile.success_history[-5:]]
        unique_mods = set(recent_mods)
        
        # 如果最近的修改类型比较集中，说明偏好稳定
        stability = 1.0 - (len(unique_mods) / len(recent_mods))
        return min(stability, 1.0)
    
    def generate_optimization_suggestions(self, profile: UserPreferenceProfile) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        # 基于成功率提供建议
        success_rate = self.calculate_success_rate(profile)
        if success_rate < 0.6:
            suggestions.append("建议尝试更明确的修改指令以提高成功率")
        
        # 基于交互效率提供建议
        efficiency = self.calculate_interaction_efficiency(profile)
        if efficiency < 0.7:
            suggestions.append("建议提供更具体的反馈以改善交互效果")
        
        return suggestions
    
    def identify_learning_opportunities(self, profile: UserPreferenceProfile) -> List[str]:
        """识别学习机会"""
        opportunities = []
        
        # 检查是否有未充分探索的修改类型
        for mod_type, weight in profile.modification_preferences.items():
            if abs(weight - 0.5) < 0.1:  # 接近中性值，说明缺乏经验
                opportunities.append(f"可以尝试更多{self.get_modification_description(mod_type)}")
        
        return opportunities
    
    def _save_profile_to_storage(self, profile: UserPreferenceProfile) -> None:
        """保存偏好档案到存储"""
        try:
            # 转换为可序列化的字典
            profile_data = asdict(profile)
            
            # 处理日期时间字段
            profile_data['created_at'] = profile.created_at.isoformat() if profile.created_at else None
            profile_data['updated_at'] = profile.updated_at.isoformat() if profile.updated_at else None
            
            # 保存到存储
            self.storage.save_user_preferences(
                user_id=profile.user_id,
                prompt_name=profile.prompt_name,
                preference_data=profile_data
            )
        except Exception as e:
            logger.error(f"保存偏好档案失败: {e}")
    
    def _restore_profile_from_storage(self, stored_data: Dict) -> UserPreferenceProfile:
        """从存储数据恢复偏好档案"""
        try:
            # 处理日期时间字段
            created_at = datetime.fromisoformat(stored_data['created_at']) if stored_data.get('created_at') else datetime.now()
            updated_at = datetime.fromisoformat(stored_data['updated_at']) if stored_data.get('updated_at') else datetime.now()
            
            return UserPreferenceProfile(
                user_id=stored_data['user_id'],
                prompt_name=stored_data['prompt_name'],
                modification_preferences=stored_data.get('modification_preferences', self.initialize_modification_preferences()),
                style_preferences=stored_data.get('style_preferences', self.initialize_style_preferences()),
                interaction_patterns=stored_data.get('interaction_patterns', self.initialize_interaction_patterns()),
                content_structure_preferences=stored_data.get('content_structure_preferences', self.initialize_structure_preferences()),
                success_history=stored_data.get('success_history', []),
                created_at=created_at,
                updated_at=updated_at
            )
        except Exception as e:
            logger.error(f"恢复偏好档案失败: {e}")
            # 返回默认档案
            return UserPreferenceProfile(
                user_id=stored_data.get('user_id', 'unknown'),
                prompt_name=stored_data.get('prompt_name', 'default'),
                modification_preferences=self.initialize_modification_preferences(),
                style_preferences=self.initialize_style_preferences(),
                interaction_patterns=self.initialize_interaction_patterns(),
                content_structure_preferences=self.initialize_structure_preferences(),
                success_history=[],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
