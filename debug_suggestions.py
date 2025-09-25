#!/usr/bin/env python3
"""
调试智能建议功能 / Debug Smart Suggestions Feature
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# 直接测试默认建议生成逻辑
def test_default_suggestions():
    """测试默认建议生成"""
    
    # 模拟会话数据
    session_short = {
        "current_content": "这是一个很短的内容",  # 少于500字符
        "user_id": "test_user"
    }
    
    session_long = {
        "current_content": "这是一个很长的内容" * 100,  # 超过2000字符
        "user_id": "test_user"
    }
    
    session_medium = {
        "current_content": "这是一个中等长度的内容，用于测试智能建议功能。" * 20,  # 中等长度
        "user_id": "test_user"
    }
    
    def generate_default_suggestions(session):
        """生成默认建议（复制自RefinementController）"""
        current_content = session.get("current_content", "")
        content_length = len(current_content)
        
        suggestions = []
        
        # 基于内容长度的建议
        if content_length < 500:
            suggestions.append({
                "id": "default_add_detail",
                "content": "建议添加更多详细信息和具体案例",
                "category": "content_addition",
                "confidence": 0.7,
                "reasoning": "当前内容较短，可以通过添加细节来丰富内容"
            })
        
        if content_length > 2000:
            suggestions.append({
                "id": "default_simplify",
                "content": "建议精简内容，突出重点信息",
                "category": "content_removal",
                "confidence": 0.6,
                "reasoning": "当前内容较长，可以通过精简来提高可读性"
            })
        
        # 通用建议
        suggestions.extend([
            {
                "id": "default_structure",
                "content": "建议优化内容结构，增强逻辑性",
                "category": "structural",
                "confidence": 0.5,
                "reasoning": "良好的结构有助于提高内容的可读性"
            },
            {
                "id": "default_style",
                "content": "建议调整语言风格，使其更加专业",
                "category": "style_adjustment",
                "confidence": 0.5,
                "reasoning": "专业的语言风格有助于提升内容质量"
            }
        ])
        
        return suggestions[:3]  # 返回最多3个默认建议
    
    # 测试不同长度的内容
    print("=== 测试短内容 ===")
    short_suggestions = generate_default_suggestions(session_short)
    print(f"短内容长度: {len(session_short['current_content'])}")
    print(f"建议数量: {len(short_suggestions)}")
    for i, suggestion in enumerate(short_suggestions, 1):
        print(f"建议 {i}: {suggestion['content']}")
        print(f"  类别: {suggestion['category']}")
        print(f"  置信度: {suggestion['confidence']}")
        print(f"  推理: {suggestion['reasoning']}")
        print()
    
    print("=== 测试长内容 ===")
    long_suggestions = generate_default_suggestions(session_long)
    print(f"长内容长度: {len(session_long['current_content'])}")
    print(f"建议数量: {len(long_suggestions)}")
    for i, suggestion in enumerate(long_suggestions, 1):
        print(f"建议 {i}: {suggestion['content']}")
        print(f"  类别: {suggestion['category']}")
        print(f"  置信度: {suggestion['confidence']}")
        print(f"  推理: {suggestion['reasoning']}")
        print()
    
    print("=== 测试中等内容 ===")
    medium_suggestions = generate_default_suggestions(session_medium)
    print(f"中等内容长度: {len(session_medium['current_content'])}")
    print(f"建议数量: {len(medium_suggestions)}")
    for i, suggestion in enumerate(medium_suggestions, 1):
        print(f"建议 {i}: {suggestion['content']}")
        print(f"  类别: {suggestion['category']}")
        print(f"  置信度: {suggestion['confidence']}")
        print(f"  推理: {suggestion['reasoning']}")
        print()

if __name__ == "__main__":
    test_default_suggestions()