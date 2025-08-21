"""
历史信息处理器 / History Information Processor

负责读取、处理和整合历史参考文件
Responsible for reading, processing and integrating historical reference files
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Optional, Set
import re


class HistoryProcessingError(Exception):
    """历史信息处理错误 / History processing error"""
    pass


class HistoryProcessor:
    """历史信息处理器 / History Information Processor"""
    
    def __init__(self, history_folder: str):
        """
        初始化历史信息处理器 / Initialize history processor
        
        Args:
            history_folder: 历史参考文件夹路径 / History reference folder path
        """
        self.history_folder = Path(history_folder)
        self.logger = logging.getLogger(__name__)
        self.supported_extensions = {'.txt', '.md', '.markdown'}
        
    def load_history_files(self) -> List[Dict[str, str]]:
        """
        加载历史参考文件 / Load history reference files
        
        Returns:
            历史文件信息列表 / List of history file information
            
        Raises:
            HistoryProcessingError: 文件读取失败 / File reading failed
        """
        history_files = []
        
        try:
            if not self.history_folder.exists():
                self.logger.warning(f"历史参考文件夹不存在: {self.history_folder} / History folder not found: {self.history_folder}")
                return history_files
            
            # 递归读取所有支持的文件 / Recursively read all supported files
            for file_path in self._get_supported_files():
                try:
                    content = self._read_file_content(file_path)
                    if content.strip():  # 只添加非空文件 / Only add non-empty files
                        history_files.append({
                            'path': str(file_path),
                            'name': file_path.name,
                            'content': content,
                            'category': self._get_file_category(file_path)
                        })
                        self.logger.debug(f"成功读取历史文件: {file_path} / Successfully read history file: {file_path}")
                except Exception as e:
                    self.logger.error(f"读取文件失败 {file_path}: {e} / Failed to read file {file_path}: {e}")
                    continue
            
            self.logger.info(f"成功加载 {len(history_files)} 个历史文件 / Successfully loaded {len(history_files)} history files")
            return history_files
            
        except Exception as e:
            raise HistoryProcessingError(f"加载历史文件失败: {e} / Failed to load history files: {e}")
    
    def process_history_content(self, files: List[Dict[str, str]]) -> str:
        """
        处理历史内容为参考信息 / Process history content as reference information
        
        Args:
            files: 历史文件信息列表 / List of history file information
            
        Returns:
            格式化的历史参考信息 / Formatted history reference information
        """
        if not files:
            return "暂无历史参考信息 / No historical reference information available"
        
        # 按类别组织文件 / Organize files by category
        categorized_files = self._categorize_files(files)
        
        reference_sections = []
        
        for category, category_files in categorized_files.items():
            if not category_files:
                continue
                
            section_content = [f"\n## {category}类别参考 / {category} Category Reference\n"]
            
            for file_info in category_files:
                # 添加文件标题和内容 / Add file title and content
                section_content.append(f"### 文件: {file_info['name']} / File: {file_info['name']}")
                section_content.append(self._format_file_content(file_info['content']))
                section_content.append("")  # 空行分隔 / Empty line separator
            
            reference_sections.append("\n".join(section_content))
        
        return "\n".join(reference_sections)
    
    def filter_relevant_history(self, case_input: str, history: str) -> str:
        """
        筛选相关历史信息 / Filter relevant history information
        
        Args:
            case_input: 案例输入内容 / Case input content
            history: 完整历史参考信息 / Complete history reference information
            
        Returns:
            筛选后的相关历史信息 / Filtered relevant history information
        """
        if not case_input.strip() or not history.strip():
            return history
        
        # 提取案例输入中的关键词 / Extract keywords from case input
        keywords = self._extract_keywords(case_input)
        
        if not keywords:
            return history
        
        # 按段落分割历史信息 / Split history by paragraphs
        history_sections = self._split_history_sections(history)
        
        # 计算每个段落的相关性得分 / Calculate relevance score for each paragraph
        relevant_sections = []
        for section in history_sections:
            relevance_score = self._calculate_relevance_score(section, keywords)
            if relevance_score > 0:  # 有任何关键词匹配就保留 / Keep if any keywords match
                relevant_sections.append((section, relevance_score))
        
        if not relevant_sections:
            # 如果没有相关内容，返回原始历史信息的摘要 / If no relevant content, return summary of original history
            return self._create_history_summary(history)
        
        # 按相关性得分排序并返回 / Sort by relevance score and return
        relevant_sections.sort(key=lambda x: x[1], reverse=True)
        
        filtered_content = []
        filtered_content.append("## 相关历史参考信息 / Relevant Historical Reference Information\n")
        
        for section, score in relevant_sections[:5]:  # 最多返回5个最相关的段落 / Return at most 5 most relevant paragraphs
            filtered_content.append(section)
            filtered_content.append("")  # 空行分隔 / Empty line separator
        
        return "\n".join(filtered_content)
    
    def _get_supported_files(self) -> List[Path]:
        """获取所有支持的文件 / Get all supported files"""
        supported_files = []
        
        for root, dirs, files in os.walk(self.history_folder):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in self.supported_extensions:
                    supported_files.append(file_path)
        
        return supported_files
    
    def _read_file_content(self, file_path: Path) -> str:
        """读取文件内容 / Read file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # 尝试其他编码 / Try other encodings
            for encoding in ['gbk', 'gb2312', 'latin1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            raise HistoryProcessingError(f"无法解码文件: {file_path} / Cannot decode file: {file_path}")
    
    def _get_file_category(self, file_path: Path) -> str:
        """获取文件类别 / Get file category"""
        # 基于文件路径确定类别 / Determine category based on file path
        relative_path = file_path.relative_to(self.history_folder)
        
        if len(relative_path.parts) > 1:
            return relative_path.parts[0]  # 使用第一级目录作为类别 / Use first level directory as category
        else:
            return "通用"  # 默认类别 / Default category
    
    def _categorize_files(self, files: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
        """按类别组织文件 / Organize files by category"""
        categorized = {}
        
        for file_info in files:
            category = file_info['category']
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(file_info)
        
        return categorized
    
    def _format_file_content(self, content: str) -> str:
        """格式化文件内容 / Format file content"""
        # 清理多余的空行 / Clean excessive empty lines
        lines = content.split('\n')
        formatted_lines = []
        
        prev_empty = False
        started = False  # 标记是否已经开始添加内容 / Mark if content has started
        
        for line in lines:
            line = line.strip()
            if not line:
                if started and not prev_empty:  # 只有在开始添加内容后才添加空行 / Only add empty lines after content starts
                    formatted_lines.append('')
                prev_empty = True
            else:
                formatted_lines.append(line)
                prev_empty = False
                started = True
        
        # 移除末尾的空行 / Remove trailing empty lines
        while formatted_lines and formatted_lines[-1] == '':
            formatted_lines.pop()
        
        return '\n'.join(formatted_lines)
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """提取关键词 / Extract keywords"""
        # 简单的关键词提取：提取2-4个字符的中文词汇和英文单词 / Simple keyword extraction
        import re
        
        # 提取中文词汇（2-4个字符）/ Extract Chinese words (2-4 characters)
        chinese_words = []
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        chinese_text = ''.join(chinese_chars)
        
        # 生成2-4字的中文词汇组合 / Generate 2-4 character Chinese word combinations
        for i in range(len(chinese_text)):
            for length in [2, 3, 4]:
                if i + length <= len(chinese_text):
                    word = chinese_text[i:i+length]
                    chinese_words.append(word)
        
        # 提取英文单词 / Extract English words
        english_words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
        
        all_words = chinese_words + english_words
        
        # 过滤常见停用词 / Filter common stop words
        stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '时', '需要',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
        }
        
        keywords = {word for word in all_words if word not in stop_words and len(word) >= 2}
        return keywords
    
    def _split_history_sections(self, history: str) -> List[str]:
        """分割历史信息为段落 / Split history into sections"""
        # 按标题和空行分割 / Split by headers and empty lines
        sections = []
        current_section = []
        
        lines = history.split('\n')
        for line in lines:
            line = line.strip()
            
            # 检查是否是标题行 / Check if it's a header line
            if line.startswith('#') or (line and not current_section):
                if current_section:
                    sections.append('\n'.join(current_section))
                    current_section = []
                current_section.append(line)
            elif line:
                current_section.append(line)
            elif current_section:
                # 遇到空行且当前段落不为空，结束当前段落 / End current section on empty line
                sections.append('\n'.join(current_section))
                current_section = []
        
        # 添加最后一个段落 / Add the last section
        if current_section:
            sections.append('\n'.join(current_section))
        
        return [section for section in sections if section.strip()]
    
    def _calculate_relevance_score(self, section: str, keywords: Set[str]) -> int:
        """计算段落相关性得分 / Calculate section relevance score"""
        section_lower = section.lower()
        score = 0
        
        for keyword in keywords:
            # 计算关键词在段落中出现的次数 / Count keyword occurrences in section
            count = section_lower.count(keyword.lower())
            score += count
        
        return score
    
    def _create_history_summary(self, history: str) -> str:
        """创建历史信息摘要 / Create history summary"""
        lines = history.split('\n')
        summary_lines = []
        
        # 提取标题和前几行内容作为摘要 / Extract headers and first few lines as summary
        for line in lines[:20]:  # 只取前20行 / Only take first 20 lines
            line = line.strip()
            if line.startswith('#') or len(line) > 10:  # 标题或较长的内容行 / Headers or longer content lines
                summary_lines.append(line)
        
        if summary_lines:
            return "## 历史参考信息摘要 / Historical Reference Summary\n\n" + '\n'.join(summary_lines[:10])
        else:
            return "## 历史参考信息 / Historical Reference Information\n\n" + history[:500] + "..."
