"""
个性化Prompt导出导入管理器 / Personalized Prompt Export/Import Manager

该模块负责个性化prompt文件的导出导入功能。
This module handles export/import functionality for personalized prompt files.
"""

import json
import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class PromptExportImportManager:
    """个性化Prompt导出导入管理器 / Personalized Prompt Export/Import Manager"""
    
    def __init__(self, personalized_prompt_manager):
        """
        初始化导出导入管理器
        Initialize export/import manager
        
        Args:
            personalized_prompt_manager: 个性化prompt管理器实例 / Personalized prompt manager instance
        """
        self.prompt_manager = personalized_prompt_manager
        self.export_formats = ['json', 'yaml']
    
    def export_user_prompts(self, user_id: str, export_config: Dict) -> Dict[str, Any]:
        """
        导出用户的个性化prompt数据 / Export user's personalized prompt data
        
        Args:
            user_id: 用户ID / User ID
            export_config: 导出配置 / Export configuration
            
        Returns:
            Dict: 导出结果 / Export result
        """
        try:
            export_format = export_config.get('format', 'json')
            include_history = export_config.get('include_history', True)
            prompts_filter = export_config.get('prompts', None)
            
            # 收集用户数据
            user_data = self._collect_user_data(user_id, prompts_filter, include_history)
            
            if not user_data['prompts']:
                return {
                    'success': False,
                    'error': 'No personalized prompts found for user'
                }
            
            # 添加导出元数据
            export_metadata = {
                'export_timestamp': datetime.now().isoformat(),
                'export_version': '1.0',
                'user_id': user_id,
                'export_config': export_config,
                'data_integrity_hash': self._calculate_data_hash(user_data)
            }
            
            # 格式化导出数据
            export_package = {
                'metadata': export_metadata,
                'user_profile': user_data['profile'],
                'prompt_preferences': user_data['prompts']
            }
            
            # 转换为指定格式
            formatted_data = self._format_export_data(export_package, export_format)
            
            # 生成导出文件名
            export_filename = f"personalized_prompts_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_format}"
            
            return {
                'success': True,
                'filename': export_filename,
                'data': formatted_data,
                'metadata': export_metadata
            }
            
        except Exception as e:
            logging.error(f"Failed to export prompts for {user_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def import_user_prompts(self, import_data: Dict, import_config: Dict) -> Dict[str, Any]:
        """
        导入用户的个性化prompt数据 / Import user's personalized prompt data
        
        Args:
            import_data: 导入数据 / Import data
            import_config: 导入配置 / Import configuration
            
        Returns:
            Dict: 导入结果 / Import result
        """
        try:
            merge_strategy = import_config.get('merge_strategy', 'replace')
            validate_integrity = import_config.get('validate_integrity', True)
            backup_existing = import_config.get('backup_existing', True)
            
            # 验证导入数据格式
            validation_result = self._validate_import_data(import_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': f"Invalid import data: {validation_result['errors']}"
                }
            
            # 验证数据完整性
            if validate_integrity:
                integrity_check = self._verify_data_integrity(import_data)
                if not integrity_check['valid']:
                    return {
                        'success': False,
                        'error': f"Data integrity check failed: {integrity_check['error']}"
                    }
            
            user_id = import_data['metadata']['user_id']
            
            # 备份现有数据（如果需要）
            if backup_existing:
                backup_result = self._backup_existing_prompts(user_id)
                if not backup_result['success']:
                    logging.warning(f"Failed to backup existing prompts: {backup_result['error']}")
            
            # 处理导入策略
            import_results = []
            
            for prompt_name, prompt_data in import_data['prompt_preferences'].items():
                result = self._import_prompt_data(
                    user_id, prompt_name, prompt_data, merge_strategy
                )
                import_results.append(result)
            
            # 统计导入结果
            successful_imports = sum(1 for r in import_results if r['success'])
            total_imports = len(import_results)
            
            return {
                'success': successful_imports > 0,
                'total_items': total_imports,
                'successful_items': successful_imports,
                'failed_items': total_imports - successful_imports,
                'details': import_results,
                'import_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Failed to import prompts: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _collect_user_data(self, user_id: str, prompts_filter: Optional[List[str]], 
                          include_history: bool) -> Dict[str, Any]:
        """收集用户数据 / Collect user data"""
        user_dir = self.prompt_manager.base_path / user_id
        user_data = {
            'profile': {
                'user_id': user_id,
                'created_at': datetime.now().isoformat(),
                'total_prompts': 0
            },
            'prompts': {}
        }
        
        if not user_dir.exists():
            return user_data
        
        # 收集所有prompt文件
        for prompt_file in user_dir.glob("*.md"):
            prompt_info = self.prompt_manager._parse_prompt_file_info(prompt_file)
            if not prompt_info:
                continue
                
            prompt_name = prompt_info['prompt_name']
            
            # 应用过滤器
            if prompts_filter and prompt_name not in prompts_filter:
                continue
            
            if prompt_name not in user_data['prompts']:
                user_data['prompts'][prompt_name] = []
            
            # 读取文件内容
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                user_data['prompts'][prompt_name].append({
                    'version': prompt_info['version'],
                    'file_name': prompt_file.name,
                    'content': content,
                    'created_at': prompt_info['created_at']
                })
            except Exception as e:
                logging.error(f"Failed to read prompt file {prompt_file}: {e}")
        
        user_data['profile']['total_prompts'] = len(user_data['prompts'])
        return user_data
    
    def _format_export_data(self, export_package: Dict, export_format: str) -> str:
        """格式化导出数据 / Format export data"""
        if export_format == 'json':
            return json.dumps(export_package, ensure_ascii=False, indent=2)
        elif export_format == 'yaml':
            return yaml.dump(export_package, allow_unicode=True, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
    
    def _validate_import_data(self, import_data: Dict) -> Dict[str, Any]:
        """验证导入数据格式 / Validate import data format"""
        errors = []
        
        # 检查必要字段
        required_fields = ['metadata', 'user_profile', 'prompt_preferences']
        for field in required_fields:
            if field not in import_data:
                errors.append(f"Missing required field: {field}")
        
        # 检查元数据
        if 'metadata' in import_data:
            metadata = import_data['metadata']
            if 'user_id' not in metadata:
                errors.append("Missing user_id in metadata")
            if 'export_version' not in metadata:
                errors.append("Missing export_version in metadata")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _verify_data_integrity(self, import_data: Dict) -> Dict[str, Any]:
        """验证数据完整性 / Verify data integrity"""
        try:
            # 简单的完整性检查
            metadata = import_data.get('metadata', {})
            expected_hash = metadata.get('data_integrity_hash')
            
            if not expected_hash:
                return {'valid': True}  # 如果没有hash，跳过验证
            
            # 重新计算hash
            user_data = {
                'profile': import_data.get('user_profile', {}),
                'prompts': import_data.get('prompt_preferences', {})
            }
            actual_hash = self._calculate_data_hash(user_data)
            
            return {
                'valid': expected_hash == actual_hash,
                'error': 'Data integrity hash mismatch' if expected_hash != actual_hash else None
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f"Integrity verification failed: {e}"
            }
    
    def _calculate_data_hash(self, data: Dict) -> str:
        """计算数据hash / Calculate data hash"""
        import hashlib
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(data_str.encode('utf-8')).hexdigest()
    
    def _backup_existing_prompts(self, user_id: str) -> Dict[str, Any]:
        """备份现有prompt / Backup existing prompts"""
        try:
            backup_config = {
                'format': 'json',
                'include_history': True
            }
            
            backup_result = self.export_user_prompts(user_id, backup_config)
            
            if backup_result['success']:
                # 保存备份文件
                backup_dir = self.prompt_manager.base_path / user_id / 'backups'
                backup_dir.mkdir(exist_ok=True)
                
                backup_file = backup_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(backup_result['data'])
                
                return {'success': True, 'backup_file': str(backup_file)}
            else:
                return backup_result
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _import_prompt_data(self, user_id: str, prompt_name: str, 
                          prompt_data: List[Dict], merge_strategy: str) -> Dict[str, Any]:
        """导入prompt数据 / Import prompt data"""
        try:
            imported_count = 0
            
            for version_data in prompt_data:
                # 重新生成文件名以避免冲突
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # 包含毫秒
                new_filename = f"{user_id}_{prompt_name}_imported_{timestamp}.md"
                
                user_dir = self.prompt_manager.base_path / user_id
                user_dir.mkdir(parents=True, exist_ok=True)
                file_path = user_dir / new_filename
                
                # 写入文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(version_data['content'])
                
                imported_count += 1
            
            return {
                'success': True,
                'prompt_name': prompt_name,
                'imported_count': imported_count
            }
            
        except Exception as e:
            return {
                'success': False,
                'prompt_name': prompt_name,
                'error': str(e)
            }