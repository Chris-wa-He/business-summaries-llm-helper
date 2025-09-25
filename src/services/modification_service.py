"""
修改服务模块 / Modification Service Module

处理各种类型的内容修改和意图识别。
Handles various types of content modifications and intent recognition.
"""

import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..models.refinement_models import ModificationPlan, ModificationType, ImpactLevel
from ..clients.bedrock_client import BedrockClient


logger = logging.getLogger(__name__)


class ModificationService:
    """修改服务类 / Modification Service Class"""
    
    def __init__(self, bedrock_client: BedrockClient):
        """
        初始化修改服务 / Initialize modification service
        
        Args:
            bedrock_client: Bedrock客户端实例 / Bedrock client instance
        """
        self.bedrock_client = bedrock_client
        self.intent_patterns = self._initialize_intent_patterns()
        
        logger.info("修改服务初始化完成")
    
    def _initialize_intent_patterns(self) -> Dict[ModificationType, List[str]]:
        """
        初始化意图识别模式 / Initialize intent recognition patterns
        
        Returns:
            意图模式字典 / Intent patterns dictionary
        """
        return {
            ModificationType.STRUCTURAL: [
                r"添加.*部分", r"增加.*章节", r"重新组织", r"调整结构", r"重新排列",
                r"add.*section", r"restructure", r"reorganize", r"rearrange", r"new.*section"
            ],
            ModificationType.CONTENT_ADDITION: [
                r"详细说明", r"补充.*信息", r"添加.*内容", r"扩展", r"更多细节",
                r"add.*detail", r"expand", r"elaborate", r"include.*more", r"more.*information"
            ],
            ModificationType.CONTENT_REMOVAL: [
                r"删除", r"移除", r"去掉", r"简化", r"精简",
                r"remove", r"delete", r"simplify", r"reduce"
            ],
            ModificationType.STYLE_ADJUSTMENT: [
                r"更.*风格", r"改变语气", r"调整表达", r"更正式", r"更通俗",
                r"change.*style", r"adjust.*tone", r"more.*formal", r"more.*casual", r"language.*style"
            ],
            ModificationType.FORMAT_MODIFICATION: [
                r"格式", r"排版", r"布局", r"标题", r"列表",
                r"format", r"layout", r"heading", r"bullet", r"numbering"
            ],
            ModificationType.LANGUAGE_OPTIMIZATION: [
                r"语言优化", r"表达优化", r"用词", r"语法", r"流畅",
                r"language.*improve", r"grammar", r"fluency", r"wording", r"improve.*language"
            ]
        }
    
    def analyze_modification_request(self, request: str, context: str) -> ModificationPlan:
        """
        分析修改请求 / Analyze modification request
        
        Args:
            request: 修改请求 / Modification request
            context: 上下文信息 / Context information
            
        Returns:
            修改计划 / Modification plan
        """
        try:
            # 1. 分类修改类型
            modification_type = self.categorize_modification(request)
            
            # 2. 提取目标区域
            target_sections = self._extract_target_sections(request, context)
            
            # 3. 生成修改指令
            instructions = self._generate_instructions(request, modification_type)
            
            # 4. 评估影响程度
            impact_level = self.estimate_modification_impact_level(request, context)
            
            # 5. 计算置信度
            confidence_score = self._calculate_confidence(request, modification_type)
            
            plan = ModificationPlan(
                id=f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                request=request,
                modification_type=modification_type,
                target_sections=target_sections,
                instructions=instructions,
                estimated_impact=impact_level,
                confidence_score=confidence_score
            )
            
            logger.info(f"分析修改请求完成: {modification_type.value}")
            return plan
            
        except Exception as e:
            logger.error(f"分析修改请求失败: {e}")
            raise
    
    def apply_modification(self, plan: ModificationPlan, content: str) -> str:
        """
        应用修改 / Apply modification
        
        Args:
            plan: 修改计划 / Modification plan
            content: 原始内容 / Original content
            
        Returns:
            修改后的内容 / Modified content
        """
        try:
            # 根据修改类型选择处理方法
            if plan.modification_type == ModificationType.STRUCTURAL:
                return self.handle_structural_change(content, plan.request)
            elif plan.modification_type == ModificationType.CONTENT_ADDITION:
                return self.handle_content_addition(content, plan.request)
            elif plan.modification_type == ModificationType.CONTENT_REMOVAL:
                return self.handle_content_removal(content, plan.request)
            elif plan.modification_type == ModificationType.STYLE_ADJUSTMENT:
                return self.handle_style_adjustment(content, plan.request)
            elif plan.modification_type == ModificationType.FORMAT_MODIFICATION:
                return self.handle_format_modification(content, plan.request)
            elif plan.modification_type == ModificationType.LANGUAGE_OPTIMIZATION:
                return self.handle_language_optimization(content, plan.request)
            else:
                # 默认处理
                return self.handle_general_modification(content, plan.request)
                
        except Exception as e:
            logger.error(f"应用修改失败: {e}")
            raise
    
    def categorize_modification(self, request: str) -> ModificationType:
        """
        分类修改类型 / Categorize modification type
        
        Args:
            request: 修改请求 / Modification request
            
        Returns:
            修改类型 / Modification type
        """
        try:
            request_lower = request.lower()
            
            # 按优先级检查模式匹配
            for mod_type, patterns in self.intent_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, request_lower):
                        logger.info(f"识别修改类型: {mod_type.value}")
                        return mod_type
            
            # 默认为内容添加
            logger.info("使用默认修改类型: CONTENT_ADDITION")
            return ModificationType.CONTENT_ADDITION
            
        except Exception as e:
            logger.error(f"分类修改类型失败: {e}")
            return ModificationType.CONTENT_ADDITION
    
    def estimate_modification_impact_level(self, request: str, context: str) -> ImpactLevel:
        """
        评估修改影响程度 / Estimate modification impact level
        
        Args:
            request: 修改请求 / Modification request
            context: 上下文信息 / Context information
            
        Returns:
            影响级别 / Impact level
        """
        try:
            # 基于关键词判断影响程度
            high_impact_keywords = ["重新组织", "完全重写", "大幅修改", "restructure", "rewrite", "completely"]
            medium_impact_keywords = ["添加章节", "调整风格", "修改格式", "add.*section", "change.*style", "new.*section"]
            
            request_lower = request.lower()
            
            for keyword in high_impact_keywords:
                if keyword in request_lower:
                    return ImpactLevel.HIGH
            
            for keyword in medium_impact_keywords:
                if re.search(keyword, request_lower):
                    return ImpactLevel.MEDIUM
            
            # 基于内容长度判断
            if len(context) > 2000:
                return ImpactLevel.MEDIUM
            
            return ImpactLevel.LOW
            
        except Exception as e:
            logger.error(f"评估修改影响失败: {e}")
            return ImpactLevel.LOW
    
    def handle_structural_change(self, content: str, instruction: str) -> str:
        """
        处理结构性修改 / Handle structural change
        
        Args:
            content: 原始内容 / Original content
            instruction: 修改指令 / Modification instruction
            
        Returns:
            修改后的内容 / Modified content
        """
        try:
            prompt = f"""请根据以下指令对内容进行结构性调整：

指令：{instruction}

原始内容：
{content}

请保持内容的核心信息不变，只调整结构和组织方式。"""

            messages = self.bedrock_client.format_messages(prompt)
            response = self.bedrock_client.converse(
                model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
                messages=messages,
                max_tokens=4000,
                temperature=0.3
            )
            
            return response
            
        except Exception as e:
            logger.error(f"处理结构性修改失败: {e}")
            return content
    
    def handle_content_addition(self, content: str, instruction: str) -> str:
        """
        处理内容添加 / Handle content addition
        
        Args:
            content: 原始内容 / Original content
            instruction: 修改指令 / Modification instruction
            
        Returns:
            修改后的内容 / Modified content
        """
        try:
            prompt = f"""请根据以下指令为内容添加相关信息：

指令：{instruction}

原始内容：
{content}

请在适当的位置添加相关内容，保持整体逻辑连贯。"""

            messages = self.bedrock_client.format_messages(prompt)
            response = self.bedrock_client.converse(
                model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
                messages=messages,
                max_tokens=4000,
                temperature=0.5
            )
            
            return response
            
        except Exception as e:
            logger.error(f"处理内容添加失败: {e}")
            return content
    
    def handle_content_removal(self, content: str, instruction: str) -> str:
        """
        处理内容删除 / Handle content removal
        
        Args:
            content: 原始内容 / Original content
            instruction: 修改指令 / Modification instruction
            
        Returns:
            修改后的内容 / Modified content
        """
        try:
            prompt = f"""请根据以下指令精简内容：

指令：{instruction}

原始内容：
{content}

请移除不必要的内容，保持核心信息完整。"""

            messages = self.bedrock_client.format_messages(prompt)
            response = self.bedrock_client.converse(
                model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
                messages=messages,
                max_tokens=4000,
                temperature=0.3
            )
            
            return response
            
        except Exception as e:
            logger.error(f"处理内容删除失败: {e}")
            return content
    
    def handle_style_adjustment(self, content: str, instruction: str) -> str:
        """
        处理风格调整 / Handle style adjustment
        
        Args:
            content: 原始内容 / Original content
            instruction: 修改指令 / Modification instruction
            
        Returns:
            修改后的内容 / Modified content
        """
        try:
            prompt = f"""请根据以下指令调整内容的语言风格：

指令：{instruction}

原始内容：
{content}

请调整表达方式和语言风格，保持内容信息不变。"""

            messages = self.bedrock_client.format_messages(prompt)
            response = self.bedrock_client.converse(
                model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
                messages=messages,
                max_tokens=4000,
                temperature=0.4
            )
            
            return response
            
        except Exception as e:
            logger.error(f"处理风格调整失败: {e}")
            return content
    
    def handle_format_modification(self, content: str, instruction: str) -> str:
        """
        处理格式修改 / Handle format modification
        
        Args:
            content: 原始内容 / Original content
            instruction: 修改指令 / Modification instruction
            
        Returns:
            修改后的内容 / Modified content
        """
        try:
            prompt = f"""请根据以下指令调整内容的格式：

指令：{instruction}

原始内容：
{content}

请调整格式、标题、列表等，保持内容信息不变。"""

            messages = self.bedrock_client.format_messages(prompt)
            response = self.bedrock_client.converse(
                model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
                messages=messages,
                max_tokens=4000,
                temperature=0.2
            )
            
            return response
            
        except Exception as e:
            logger.error(f"处理格式修改失败: {e}")
            return content
    
    def handle_language_optimization(self, content: str, instruction: str) -> str:
        """
        处理语言优化 / Handle language optimization
        
        Args:
            content: 原始内容 / Original content
            instruction: 修改指令 / Modification instruction
            
        Returns:
            修改后的内容 / Modified content
        """
        try:
            prompt = f"""请根据以下指令优化内容的语言表达：

指令：{instruction}

原始内容：
{content}

请优化语言表达、语法和流畅度，保持内容含义不变。"""

            messages = self.bedrock_client.format_messages(prompt)
            response = self.bedrock_client.converse(
                model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
                messages=messages,
                max_tokens=4000,
                temperature=0.3
            )
            
            return response
            
        except Exception as e:
            logger.error(f"处理语言优化失败: {e}")
            return content
    
    def handle_general_modification(self, content: str, instruction: str) -> str:
        """
        处理通用修改 / Handle general modification
        
        Args:
            content: 原始内容 / Original content
            instruction: 修改指令 / Modification instruction
            
        Returns:
            修改后的内容 / Modified content
        """
        try:
            prompt = f"""请根据以下指令修改内容：

指令：{instruction}

原始内容：
{content}

请按照指令要求进行修改，保持内容的专业性和准确性。"""

            messages = self.bedrock_client.format_messages(prompt)
            response = self.bedrock_client.converse(
                model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
                messages=messages,
                max_tokens=4000,
                temperature=0.4
            )
            
            return response
            
        except Exception as e:
            logger.error(f"处理通用修改失败: {e}")
            return content
    
    def _extract_target_sections(self, request: str, context: str) -> List[str]:
        """
        提取目标区域 / Extract target sections
        
        Args:
            request: 修改请求 / Modification request
            context: 上下文信息 / Context information
            
        Returns:
            目标区域列表 / List of target sections
        """
        try:
            sections = []
            
            # 查找明确提到的章节
            section_patterns = [
                r"第.*章", r"第.*节", r".*部分", r".*section", r"chapter.*"
            ]
            
            for pattern in section_patterns:
                matches = re.findall(pattern, request, re.IGNORECASE)
                sections.extend(matches)
            
            return sections[:5]  # 最多返回5个目标区域
            
        except Exception as e:
            logger.error(f"提取目标区域失败: {e}")
            return []
    
    def _generate_instructions(self, request: str, modification_type: ModificationType) -> List[str]:
        """
        生成修改指令 / Generate modification instructions
        
        Args:
            request: 修改请求 / Modification request
            modification_type: 修改类型 / Modification type
            
        Returns:
            指令列表 / List of instructions
        """
        try:
            instructions = [request]  # 基础指令就是原始请求
            
            # 根据修改类型添加具体指导
            if modification_type == ModificationType.STRUCTURAL:
                instructions.append("保持内容完整性，只调整结构")
            elif modification_type == ModificationType.CONTENT_ADDITION:
                instructions.append("在适当位置添加相关内容")
            elif modification_type == ModificationType.STYLE_ADJUSTMENT:
                instructions.append("调整语言风格，保持信息准确")
            
            return instructions
            
        except Exception as e:
            logger.error(f"生成修改指令失败: {e}")
            return [request]
    
    def _calculate_confidence(self, request: str, modification_type: ModificationType) -> float:
        """
        计算置信度 / Calculate confidence score
        
        Args:
            request: 修改请求 / Modification request
            modification_type: 修改类型 / Modification type
            
        Returns:
            置信度分数 / Confidence score
        """
        try:
            # 基于模式匹配的置信度
            patterns = self.intent_patterns.get(modification_type, [])
            request_lower = request.lower()
            
            match_count = sum(1 for pattern in patterns if re.search(pattern, request_lower))
            
            if match_count > 0:
                base_confidence = min(0.9, 0.6 + (match_count * 0.1))
            else:
                base_confidence = 0.5
            
            # 基于请求长度和清晰度调整
            if len(request) > 10 and len(request) < 200:
                base_confidence += 0.1
            
            return min(1.0, base_confidence)
            
        except Exception as e:
            logger.error(f"计算置信度失败: {e}")
            return 0.5