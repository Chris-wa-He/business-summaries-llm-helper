"""
个性化Prompt文件管理器 / Personalized Prompt File Manager

该模块负责管理个性化prompt文件的生成、存储和版本控制。
This module manages the generation, storage, and version control of personalized prompt files.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class PersonalizedPromptInfo:
    """个性化Prompt信息 / Personalized Prompt Information"""
    file_path: str
    file_name: str
    version: str
    content: str
    created_at: str
    prompt_name: str
    user_id: str


class PersonalizedPromptManager:
    """个性化Prompt文件管理器 / Personalized Prompt File Manager"""
    
    def __init__(self, base_path: str = "./personalized_prompts"):
        """
        初始化个性化Prompt管理器
        Initialize personalized prompt manager
        
        Args:
            base_path: 个性化prompt存储基础路径 / Base path for personalized prompt storage
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.active_prompts = {}  # {user_id: {prompt_name: file_path}}
        
    def create_personalized_prompt_file(self, user_id: str, prompt_name: str, 
                                      preference_analysis: Dict) -> PersonalizedPromptInfo:
        """
        创建个性化prompt文件 / Create personalized prompt file
        
        Args:
            user_id: 用户ID / User ID
            prompt_name: 提示词名称 / Prompt name
            preference_analysis: 偏好分析结果 / Preference analysis result
            
        Returns:
            PersonalizedPromptInfo: 创建的prompt文件信息 / Created prompt file information
        """
        try:
            # 生成文件路径和版本 - 使用双下划线作为分隔符
            import time
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # 包含毫秒确保唯一性
            file_name = f"{user_id}__{prompt_name}__v{timestamp}.md"
            user_dir = self.base_path / user_id
            user_dir.mkdir(parents=True, exist_ok=True)
            file_path = user_dir / file_name
            
            # 构建文件内容
            file_content = self._build_prompt_file_content(
                user_id, prompt_name, timestamp, preference_analysis
            )
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            # 更新当前激活的个性化prompt
            self._update_active_prompt(user_id, prompt_name, str(file_path))
            
            prompt_info = PersonalizedPromptInfo(
                file_path=str(file_path),
                file_name=file_name,
                version=timestamp,
                content=file_content,
                created_at=datetime.now().isoformat(),
                prompt_name=prompt_name,
                user_id=user_id
            )
            
            logging.info(f"Created personalized prompt file: {file_path}")
            return prompt_info
            
        except Exception as e:
            logging.error(f"Failed to create personalized prompt file: {e}")
            raise
    
    def load_personalized_prompt(self, user_id: str, prompt_name: str) -> Optional[str]:
        """
        加载用户的个性化prompt / Load user's personalized prompt
        
        Args:
            user_id: 用户ID / User ID
            prompt_name: 提示词名称 / Prompt name
            
        Returns:
            Optional[str]: 个性化prompt内容 / Personalized prompt content
        """
        try:
            # 获取当前激活的个性化prompt文件
            active_file = self._get_active_prompt_file(user_id, prompt_name)
            
            if not active_file or not Path(active_file).exists():
                return None
            
            # 读取文件内容
            with open(active_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取个性化提示词部分
            personalized_prompt = self._extract_prompt_content(content)
            return personalized_prompt
            
        except Exception as e:
            logging.error(f"Failed to load personalized prompt for {user_id}/{prompt_name}: {e}")
            return None
    
    def get_prompt_versions(self, user_id: str, prompt_name: str) -> List[Dict[str, Any]]:
        """
        获取个性化prompt的版本列表 / Get personalized prompt version list
        
        Args:
            user_id: 用户ID / User ID
            prompt_name: 提示词名称 / Prompt name
            
        Returns:
            List[Dict]: 版本信息列表 / Version information list
        """
        user_dir = self.base_path / user_id
        if not user_dir.exists():
            return []
        
        versions = []
        pattern = f"{user_id}__{prompt_name}__v*.md"
        
        for file_path in user_dir.glob(pattern):
            version_info = self._parse_prompt_file_info(file_path)
            if version_info:
                versions.append(version_info)
        
        # 按版本时间排序
        versions.sort(key=lambda x: x['version'], reverse=True)
        return versions
    
    def activate_prompt_version(self, user_id: str, prompt_name: str, version: str) -> bool:
        """
        激活特定版本的prompt / Activate specific version of prompt
        
        Args:
            user_id: 用户ID / User ID
            prompt_name: 提示词名称 / Prompt name
            version: 版本号 / Version number
            
        Returns:
            bool: 激活是否成功 / Whether activation was successful
        """
        try:
            user_dir = self.base_path / user_id
            file_name = f"{user_id}__{prompt_name}__v{version}.md"
            file_path = user_dir / file_name
            
            if file_path.exists():
                self._update_active_prompt(user_id, prompt_name, str(file_path))
                logging.info(f"Activated prompt version {version} for {user_id}/{prompt_name}")
                return True
            else:
                logging.warning(f"Prompt version file not found: {file_path}")
                return False
                
        except Exception as e:
            logging.error(f"Failed to activate prompt version: {e}")
            return False
    
    def delete_prompt_version(self, user_id: str, prompt_name: str, version: str) -> bool:
        """
        删除特定版本的prompt / Delete specific version of prompt
        
        Args:
            user_id: 用户ID / User ID
            prompt_name: 提示词名称 / Prompt name
            version: 版本号 / Version number
            
        Returns:
            bool: 删除是否成功 / Whether deletion was successful
        """
        try:
            user_dir = self.base_path / user_id
            file_name = f"{user_id}__{prompt_name}__v{version}.md"
            file_path = user_dir / file_name
            
            if file_path.exists():
                file_path.unlink()
                logging.info(f"Deleted prompt version {version} for {user_id}/{prompt_name}")
                return True
            else:
                logging.warning(f"Prompt version file not found: {file_path}")
                return False
                
        except Exception as e:
            logging.error(f"Failed to delete prompt version: {e}")
            return False
    
    def _build_prompt_file_content(self, user_id: str, prompt_name: str, 
                                 timestamp: str, preference_analysis: Dict) -> str:
        """构建prompt文件内容 / Build prompt file content"""
        return f"""# 个性化系统提示词 / Personalized System Prompt

## 基本信息 / Basic Information
- **用户ID**: {user_id}
- **场景**: {prompt_name}
- **版本**: {timestamp}
- **创建时间**: {datetime.now().isoformat()}

## 偏好分析 / Preference Analysis
{preference_analysis.get('analysis', '')}

## 个性化提示词 / Personalized Prompt
{preference_analysis.get('personalized_prompt', '')}

## 使用说明 / Usage Instructions
此提示词基于用户的历史交互和反馈自动生成，会随着用户使用不断优化。
This prompt is automatically generated based on user's historical interactions and feedback, and will be continuously optimized with usage.
"""
    
    def _extract_prompt_content(self, file_content: str) -> str:
        """从文件内容中提取个性化提示词 / Extract personalized prompt from file content"""
        lines = file_content.split('\n')
        in_prompt_section = False
        prompt_lines = []
        
        for line in lines:
            if line.startswith('## 个性化提示词 / Personalized Prompt'):
                in_prompt_section = True
                continue
            elif line.startswith('## ') and in_prompt_section:
                break
            elif in_prompt_section and line.strip():
                prompt_lines.append(line)
        
        return '\n'.join(prompt_lines).strip()
    
    def _parse_prompt_file_info(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """解析prompt文件信息 / Parse prompt file information"""
        try:
            # 从文件名解析信息 - 格式: {user_id}__{prompt_name}__v{timestamp}.md
            file_name = file_path.stem
            
            # 找到最后一个'__v'的位置，这是版本号的开始
            version_marker = '__v'
            version_start = file_name.rfind(version_marker)
            
            if version_start == -1:
                return None
            
            # 分离文件名和版本号
            name_part = file_name[:version_start]
            version_part = file_name[version_start + 3:]  # 移除'__v'
            
            # 从名称部分分离 user_id 和 prompt_name
            if '__' not in name_part:
                return None
            
            user_id, prompt_name = name_part.split('__', 1)
            
            return {
                'user_id': user_id,
                'prompt_name': prompt_name,
                'version': version_part,
                'file_path': str(file_path),
                'file_name': file_path.name,
                'created_at': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
        except Exception as e:
            logging.error(f"Failed to parse prompt file info: {e}")
        
        return None
    
    def _get_active_prompt_file(self, user_id: str, prompt_name: str) -> Optional[str]:
        """获取当前激活的prompt文件路径 / Get current active prompt file path"""
        return self.active_prompts.get(user_id, {}).get(prompt_name)
    
    def _update_active_prompt(self, user_id: str, prompt_name: str, file_path: str):
        """更新当前激活的prompt / Update current active prompt"""
        if user_id not in self.active_prompts:
            self.active_prompts[user_id] = {}
        self.active_prompts[user_id][prompt_name] = file_path