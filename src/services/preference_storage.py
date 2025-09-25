"""
偏好持久化存储 / Preference Persistent Storage
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PreferenceStorage:
    """偏好存储管理器"""
    
    def __init__(self, storage_path: str = "./user_preferences"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"偏好存储初始化: {self.storage_path}")
    
    def save_user_preferences(self, user_id: str, prompt_name: str, preference_data: Dict) -> bool:
        """保存用户偏好"""
        try:
            user_dir = self.storage_path / user_id
            user_dir.mkdir(exist_ok=True)
            
            file_path = user_dir / f"{prompt_name}.json"
            
            # 添加保存时间戳
            save_data = {
                "saved_at": datetime.now().isoformat(),
                "user_id": user_id,
                "prompt_name": prompt_name,
                **preference_data
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"保存偏好成功: {user_id}/{prompt_name}")
            return True
            
        except Exception as e:
            logger.error(f"保存偏好失败: {e}")
            return False
    
    def load_user_preferences(self, user_id: str, prompt_name: str) -> Optional[Dict]:
        """加载用户偏好"""
        try:
            file_path = self.storage_path / user_id / f"{prompt_name}.json"
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"加载偏好成功: {user_id}/{prompt_name}")
            return data
            
        except Exception as e:
            logger.error(f"加载偏好失败: {e}")
            return None
    
    def list_user_prompts(self, user_id: str) -> list:
        """列出用户的所有提示词偏好"""
        try:
            user_dir = self.storage_path / user_id
            if not user_dir.exists():
                return []
            
            prompts = []
            for file_path in user_dir.glob("*.json"):
                prompt_name = file_path.stem
                prompts.append(prompt_name)
            
            return prompts
            
        except Exception as e:
            logger.error(f"列出用户提示词失败: {e}")
            return []