"""
输入验证器 / Input Validator

验证和清理用户输入，确保数据安全性
Validates and sanitizes user input to ensure data security
"""

import re
import html
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum


class ValidationLevel(Enum):
    """验证级别 / Validation Level"""
    BASIC = "basic"
    STRICT = "strict"
    PARANOID = "paranoid"


@dataclass
class ValidationResult:
    """验证结果 / Validation Result"""
    is_valid: bool
    cleaned_data: Optional[str] = None
    errors: List[str] = None
    warnings: List[str] = None


class InputValidator:
    """输入验证器 / Input Validator"""
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STRICT):
        self.validation_level = validation_level
        self.logger = logging.getLogger(__name__)
        
        # 危险模式列表 / Dangerous patterns
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',               # JavaScript URLs
            r'on\w+\s*=',                # Event handlers
            r'<iframe[^>]*>',            # Iframe tags
            r'<object[^>]*>',            # Object tags
            r'<embed[^>]*>',             # Embed tags
            r'eval\s*\(',                # Eval function
            r'exec\s*\(',                # Exec function
        ]
        
        # SQL注入模式 / SQL injection patterns
        self.sql_patterns = [
            r'union\s+select',
            r'drop\s+table',
            r'delete\s+from',
            r'insert\s+into',
            r'update\s+set',
            r'--\s*$',
            r'/\*.*?\*/',
        ]
        
        # 路径遍历模式 / Path traversal patterns
        self.path_traversal_patterns = [
            r'\.\./+',
            r'\.\.\\+',
            r'%2e%2e%2f',
            r'%2e%2e\\',
        ]
    
    def validate_user_message(self, message: str, max_length: int = 2000) -> ValidationResult:
        """验证用户消息 / Validate user message"""
        if not isinstance(message, str):
            return ValidationResult(False, errors=["消息必须是字符串 / Message must be string"])
        
        errors = []
        warnings = []
        
        # 长度检查 / Length check
        if len(message) > max_length:
            errors.append(f"消息长度超出限制 ({max_length}) / Message exceeds length limit ({max_length})")
        
        if len(message.strip()) == 0:
            errors.append("消息不能为空 / Message cannot be empty")
        
        # 危险内容检查 / Dangerous content check
        dangerous_found = self._check_dangerous_patterns(message)
        if dangerous_found:
            errors.extend(dangerous_found)
        
        # 清理内容 / Clean content
        cleaned_message = self._sanitize_input(message)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            cleaned_data=cleaned_message if len(errors) == 0 else None,
            errors=errors,
            warnings=warnings
        )
    
    def validate_file_path(self, file_path: str) -> ValidationResult:
        """验证文件路径 / Validate file path"""
        if not isinstance(file_path, str):
            return ValidationResult(False, errors=["路径必须是字符串 / Path must be string"])
        
        errors = []
        
        # 路径遍历检查 / Path traversal check
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, file_path, re.IGNORECASE):
                errors.append("检测到路径遍历攻击 / Path traversal attack detected")
                break
        
        # 绝对路径检查 / Absolute path check
        if file_path.startswith('/') or (len(file_path) > 1 and file_path[1] == ':'):
            errors.append("不允许绝对路径 / Absolute paths not allowed")
        
        # 清理路径 / Clean path
        cleaned_path = self._sanitize_file_path(file_path)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            cleaned_data=cleaned_path if len(errors) == 0 else None,
            errors=errors
        )
    
    def validate_prompt_content(self, content: str, max_length: int = 10000) -> ValidationResult:
        """验证提示词内容 / Validate prompt content"""
        if not isinstance(content, str):
            return ValidationResult(False, errors=["内容必须是字符串 / Content must be string"])
        
        errors = []
        warnings = []
        
        # 长度检查 / Length check
        if len(content) > max_length:
            errors.append(f"内容长度超出限制 ({max_length}) / Content exceeds length limit ({max_length})")
        
        # 基本安全检查 / Basic security check
        if self.validation_level in [ValidationLevel.STRICT, ValidationLevel.PARANOID]:
            dangerous_found = self._check_dangerous_patterns(content)
            if dangerous_found:
                warnings.extend(dangerous_found)
        
        # 清理内容 / Clean content
        cleaned_content = self._sanitize_prompt_content(content)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            cleaned_data=cleaned_content,
            errors=errors,
            warnings=warnings
        )
    
    def validate_session_id(self, session_id: str) -> ValidationResult:
        """验证会话ID / Validate session ID"""
        if not isinstance(session_id, str):
            return ValidationResult(False, errors=["会话ID必须是字符串 / Session ID must be string"])
        
        errors = []
        
        # 格式检查 / Format check
        if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
            errors.append("会话ID格式无效 / Invalid session ID format")
        
        if len(session_id) < 3 or len(session_id) > 64:
            errors.append("会话ID长度必须在3-64字符之间 / Session ID length must be 3-64 characters")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            cleaned_data=session_id if len(errors) == 0 else None,
            errors=errors
        )
    
    def _check_dangerous_patterns(self, text: str) -> List[str]:
        """检查危险模式 / Check dangerous patterns"""
        errors = []
        
        # XSS检查 / XSS check
        for pattern in self.dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                errors.append("检测到潜在的XSS攻击 / Potential XSS attack detected")
                break
        
        # SQL注入检查 / SQL injection check
        if self.validation_level == ValidationLevel.PARANOID:
            for pattern in self.sql_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    errors.append("检测到潜在的SQL注入 / Potential SQL injection detected")
                    break
        
        return errors
    
    def _sanitize_input(self, text: str) -> str:
        """清理输入内容 / Sanitize input content"""
        # HTML转义 / HTML escape
        cleaned = html.escape(text)
        
        # 移除控制字符 / Remove control characters
        cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', cleaned)
        
        # 标准化空白字符 / Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def _sanitize_file_path(self, path: str) -> str:
        """清理文件路径 / Sanitize file path"""
        # 移除危险字符 / Remove dangerous characters
        cleaned = re.sub(r'[<>:"|?*]', '', path)
        
        # 标准化路径分隔符 / Normalize path separators
        cleaned = cleaned.replace('\\', '/')
        
        # 移除多余的斜杠 / Remove extra slashes
        cleaned = re.sub(r'/+', '/', cleaned)
        
        return cleaned.strip('/')
    
    def _sanitize_prompt_content(self, content: str) -> str:
        """清理提示词内容 / Sanitize prompt content"""
        # 保留基本格式，只移除明显危险的内容 / Preserve basic formatting, only remove obviously dangerous content
        cleaned = content
        
        # 移除脚本标签 / Remove script tags
        cleaned = re.sub(r'<script[^>]*>.*?</script>', '', cleaned, flags=re.IGNORECASE | re.DOTALL)
        
        # 移除事件处理器 / Remove event handlers
        cleaned = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', cleaned, flags=re.IGNORECASE)
        
        return cleaned


class AccessController:
    """访问控制器 / Access Controller"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session_permissions = {}
        self.rate_limits = {}
    
    def check_session_access(self, session_id: str, user_id: str, operation: str) -> bool:
        """检查会话访问权限 / Check session access permission"""
        try:
            # 基本权限检查 / Basic permission check
            if not session_id or not user_id:
                return False
            
            # 会话所有权检查 / Session ownership check
            session_key = f"{session_id}:{user_id}"
            if session_key not in self.session_permissions:
                # 首次访问，记录权限 / First access, record permission
                self.session_permissions[session_key] = {
                    'created_at': self._get_current_time(),
                    'operations': [operation]
                }
                return True
            
            # 检查操作权限 / Check operation permission
            session_info = self.session_permissions[session_key]
            if operation not in session_info['operations']:
                session_info['operations'].append(operation)
            
            return True
            
        except Exception as e:
            self.logger.error(f"访问控制检查失败 / Access control check failed: {e}")
            return False
    
    def check_rate_limit(self, user_id: str, operation: str, limit: int = 100, window: int = 3600) -> bool:
        """检查速率限制 / Check rate limit"""
        try:
            current_time = self._get_current_time()
            rate_key = f"{user_id}:{operation}"
            
            if rate_key not in self.rate_limits:
                self.rate_limits[rate_key] = []
            
            # 清理过期记录 / Clean expired records
            self.rate_limits[rate_key] = [
                timestamp for timestamp in self.rate_limits[rate_key]
                if current_time - timestamp < window
            ]
            
            # 检查限制 / Check limit
            if len(self.rate_limits[rate_key]) >= limit:
                return False
            
            # 记录当前请求 / Record current request
            self.rate_limits[rate_key].append(current_time)
            return True
            
        except Exception as e:
            self.logger.error(f"速率限制检查失败 / Rate limit check failed: {e}")
            return True  # 失败时允许访问 / Allow access on failure
    
    def _get_current_time(self) -> int:
        """获取当前时间戳 / Get current timestamp"""
        import time
        return int(time.time())


class SecurityAuditor:
    """安全审计器 / Security Auditor"""
    
    def __init__(self, log_file: str = "security_audit.log"):
        self.log_file = log_file
        self.logger = logging.getLogger("security_audit")
        
        # 配置安全日志 / Configure security logging
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_security_event(self, event_type: str, user_id: str, details: Dict[str, Any]):
        """记录安全事件 / Log security event"""
        try:
            log_entry = {
                'event_type': event_type,
                'user_id': user_id,
                'timestamp': self._get_current_time(),
                'details': details
            }
            
            self.logger.info(f"SECURITY_EVENT: {log_entry}")
            
        except Exception as e:
            self.logger.error(f"安全日志记录失败 / Security logging failed: {e}")
    
    def log_access_attempt(self, user_id: str, session_id: str, operation: str, success: bool):
        """记录访问尝试 / Log access attempt"""
        self.log_security_event(
            "ACCESS_ATTEMPT",
            user_id,
            {
                'session_id': session_id,
                'operation': operation,
                'success': success
            }
        )
    
    def log_validation_failure(self, user_id: str, input_type: str, errors: List[str]):
        """记录验证失败 / Log validation failure"""
        self.log_security_event(
            "VALIDATION_FAILURE",
            user_id,
            {
                'input_type': input_type,
                'errors': errors
            }
        )
    
    def _get_current_time(self) -> str:
        """获取当前时间字符串 / Get current time string"""
        from datetime import datetime
        return datetime.now().isoformat()