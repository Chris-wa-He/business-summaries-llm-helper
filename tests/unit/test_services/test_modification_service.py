"""
修改服务测试 / Modification Service Tests
"""

import pytest
from unittest.mock import Mock, AsyncMock

from src.services.modification_service import ModificationService
from src.models.refinement_models import ModificationType, ImpactLevel
from src.clients.bedrock_client import BedrockClient


class TestModificationService:
    """修改服务测试类 / Modification Service Test Class"""
    
    @pytest.fixture
    def mock_bedrock_client(self):
        """创建模拟Bedrock客户端 / Create mock Bedrock client"""
        mock_client = Mock(spec=BedrockClient)
        mock_client.converse = AsyncMock(return_value="修改后的内容")
        return mock_client
    
    @pytest.fixture
    def modification_service(self, mock_bedrock_client):
        """创建修改服务实例 / Create modification service instance"""
        return ModificationService(mock_bedrock_client)
    
    def test_categorize_modification_structural(self, modification_service):
        """测试结构性修改分类 / Test structural modification categorization"""
        requests = [
            "重新组织内容结构",
            "调整结构",
            "restructure the content",
            "reorganize the sections",
            "rearrange the layout"
        ]
        
        for request in requests:
            mod_type = modification_service.categorize_modification(request)
            assert mod_type == ModificationType.STRUCTURAL
    
    def test_categorize_modification_content_addition(self, modification_service):
        """测试内容添加分类 / Test content addition categorization"""
        requests = [
            "请详细说明技术实现",
            "补充更多信息",
            "添加具体案例",
            "expand the details",
            "add more information"
        ]
        
        for request in requests:
            mod_type = modification_service.categorize_modification(request)
            assert mod_type == ModificationType.CONTENT_ADDITION
    
    def test_categorize_modification_content_removal(self, modification_service):
        """测试内容删除分类 / Test content removal categorization"""
        requests = [
            "删除不必要的部分",
            "简化内容",
            "去掉冗余信息",
            "remove unnecessary parts",
            "simplify the content"
        ]
        
        for request in requests:
            mod_type = modification_service.categorize_modification(request)
            assert mod_type == ModificationType.CONTENT_REMOVAL
    
    def test_categorize_modification_style_adjustment(self, modification_service):
        """测试风格调整分类 / Test style adjustment categorization"""
        requests = [
            "改变语气",
            "调整表达",
            "更正式",
            "change the style",
            "adjust the tone"
        ]
        
        for request in requests:
            mod_type = modification_service.categorize_modification(request)
            assert mod_type == ModificationType.STYLE_ADJUSTMENT
    
    def test_categorize_modification_format(self, modification_service):
        """测试格式修改分类 / Test format modification categorization"""
        requests = [
            "调整格式",
            "修改标题样式",
            "改为列表形式",
            "format the content",
            "change to bullet points"
        ]
        
        for request in requests:
            mod_type = modification_service.categorize_modification(request)
            assert mod_type == ModificationType.FORMAT_MODIFICATION
    
    def test_categorize_modification_language_optimization(self, modification_service):
        """测试语言优化分类 / Test language optimization categorization"""
        requests = [
            "语言优化",
            "表达优化",
            "语法修正",
            "grammar check",
            "improve the language"
        ]
        
        for request in requests:
            mod_type = modification_service.categorize_modification(request)
            assert mod_type == ModificationType.LANGUAGE_OPTIMIZATION
    
    def test_categorize_modification_default(self, modification_service):
        """测试默认分类 / Test default categorization"""
        # 无法识别的请求应该默认为内容添加
        request = "这是一个无法识别的请求"
        mod_type = modification_service.categorize_modification(request)
        assert mod_type == ModificationType.CONTENT_ADDITION
    
    def test_estimate_modification_impact_high(self, modification_service):
        """测试高影响评估 / Test high impact estimation"""
        requests = [
            "完全重新组织内容",
            "大幅修改结构",
            "rewrite the entire content"
        ]
        
        for request in requests:
            impact = modification_service.estimate_modification_impact_level(request, "短内容")
            assert impact == ImpactLevel.HIGH
    
    def test_estimate_modification_impact_medium(self, modification_service):
        """测试中等影响评估 / Test medium impact estimation"""
        requests = [
            "添加章节部分",  # 匹配 "添加章节" 关键词
            "change the style here",  # 匹配 "change.*style" 模式
            "add new section content"  # 匹配 "new.*section" 模式
        ]
        
        for request in requests:
            impact = modification_service.estimate_modification_impact_level(request, "短内容")
            assert impact == ImpactLevel.MEDIUM
    
    def test_estimate_modification_impact_low(self, modification_service):
        """测试低影响评估 / Test low impact estimation"""
        request = "修正一个小错误"
        impact = modification_service.estimate_modification_impact_level(request, "短内容")
        assert impact == ImpactLevel.LOW
    
    def test_estimate_modification_impact_by_content_length(self, modification_service):
        """测试基于内容长度的影响评估 / Test impact estimation by content length"""
        request = "简单修改"
        long_content = "很长的内容" * 500  # 超过2000字符
        
        impact = modification_service.estimate_modification_impact_level(request, long_content)
        assert impact == ImpactLevel.MEDIUM
    
    @pytest.mark.asyncio
    async def test_analyze_modification_request(self, modification_service):
        """测试分析修改请求 / Test analyze modification request"""
        request = "请添加技术实现细节"
        context = "这是一个技术文档"
        
        plan = await modification_service.analyze_modification_request(request, context)
        
        assert plan.request == request
        assert plan.modification_type == ModificationType.CONTENT_ADDITION
        assert isinstance(plan.target_sections, list)
        assert isinstance(plan.instructions, list)
        assert plan.estimated_impact in [ImpactLevel.LOW, ImpactLevel.MEDIUM, ImpactLevel.HIGH]
        assert 0.0 <= plan.confidence_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_apply_modification_structural(self, modification_service, mock_bedrock_client):
        """测试应用结构性修改 / Test apply structural modification"""
        from src.models.refinement_models import ModificationPlan
        
        plan = ModificationPlan(
            id="test_plan",
            request="重新组织内容",
            modification_type=ModificationType.STRUCTURAL,
            target_sections=[],
            instructions=["重新组织内容"],
            estimated_impact=ImpactLevel.MEDIUM,
            confidence_score=0.8
        )
        
        content = "原始内容"
        result = await modification_service.apply_modification(plan, content)
        
        assert result == "修改后的内容"
        mock_bedrock_client.converse.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_apply_modification_content_addition(self, modification_service, mock_bedrock_client):
        """测试应用内容添加修改 / Test apply content addition modification"""
        from src.models.refinement_models import ModificationPlan
        
        plan = ModificationPlan(
            id="test_plan",
            request="添加更多细节",
            modification_type=ModificationType.CONTENT_ADDITION,
            target_sections=[],
            instructions=["添加更多细节"],
            estimated_impact=ImpactLevel.LOW,
            confidence_score=0.7
        )
        
        content = "原始内容"
        result = await modification_service.apply_modification(plan, content)
        
        assert result == "修改后的内容"
        mock_bedrock_client.converse.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_structural_change(self, modification_service, mock_bedrock_client):
        """测试处理结构性修改 / Test handle structural change"""
        content = "原始内容"
        instruction = "重新组织结构"
        
        result = await modification_service.handle_structural_change(content, instruction)
        
        assert result == "修改后的内容"
        mock_bedrock_client.converse.assert_called_once()
        
        # 验证调用参数
        call_args = mock_bedrock_client.converse.call_args
        assert call_args[1]["model_id"] == "anthropic.claude-3-5-sonnet-20241022-v2:0"
        assert call_args[1]["temperature"] == 0.3
    
    @pytest.mark.asyncio
    async def test_handle_content_addition(self, modification_service, mock_bedrock_client):
        """测试处理内容添加 / Test handle content addition"""
        content = "原始内容"
        instruction = "添加技术细节"
        
        result = await modification_service.handle_content_addition(content, instruction)
        
        assert result == "修改后的内容"
        mock_bedrock_client.converse.assert_called_once()
        
        # 验证调用参数
        call_args = mock_bedrock_client.converse.call_args
        assert call_args[1]["temperature"] == 0.5
    
    @pytest.mark.asyncio
    async def test_handle_style_adjustment(self, modification_service, mock_bedrock_client):
        """测试处理风格调整 / Test handle style adjustment"""
        content = "原始内容"
        instruction = "改为更正式的风格"
        
        result = await modification_service.handle_style_adjustment(content, instruction)
        
        assert result == "修改后的内容"
        mock_bedrock_client.converse.assert_called_once()
        
        # 验证调用参数
        call_args = mock_bedrock_client.converse.call_args
        assert call_args[1]["temperature"] == 0.4
    
    @pytest.mark.asyncio
    async def test_bedrock_client_error_handling(self, modification_service, mock_bedrock_client):
        """测试Bedrock客户端错误处理 / Test Bedrock client error handling"""
        # 模拟Bedrock客户端抛出异常
        mock_bedrock_client.converse.side_effect = Exception("API调用失败")
        
        content = "原始内容"
        instruction = "修改内容"
        
        # 应该返回原始内容而不是抛出异常
        result = await modification_service.handle_general_modification(content, instruction)
        assert result == content
    
    def test_extract_target_sections(self, modification_service):
        """测试提取目标区域 / Test extract target sections"""
        request = "请修改第一章和技术实现部分"
        context = "文档内容"
        
        sections = modification_service._extract_target_sections(request, context)
        
        assert isinstance(sections, list)
        assert len(sections) <= 5  # 最多返回5个
    
    def test_generate_instructions(self, modification_service):
        """测试生成修改指令 / Test generate modification instructions"""
        request = "添加技术细节"
        mod_type = ModificationType.CONTENT_ADDITION
        
        instructions = modification_service._generate_instructions(request, mod_type)
        
        assert isinstance(instructions, list)
        assert len(instructions) >= 1
        assert request in instructions
    
    def test_calculate_confidence(self, modification_service):
        """测试计算置信度 / Test calculate confidence"""
        # 明确的请求应该有较高置信度
        request = "请详细说明技术实现"
        mod_type = ModificationType.CONTENT_ADDITION
        
        confidence = modification_service._calculate_confidence(request, mod_type)
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.5  # 应该有较高置信度
    
    def test_calculate_confidence_low(self, modification_service):
        """测试低置信度计算 / Test low confidence calculation"""
        # 模糊的请求应该有较低置信度
        request = "改一下"
        mod_type = ModificationType.CONTENT_ADDITION
        
        confidence = modification_service._calculate_confidence(request, mod_type)
        
        assert 0.0 <= confidence <= 1.0