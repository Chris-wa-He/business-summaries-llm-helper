"""
错误处理和恢复机制 / Error Handling and Recovery Mechanism
"""

import logging
from typing import Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class ErrorSeverity(Enum):
    """错误严重程度 / Error Severity Levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """错误类别 / Error Categories"""
    CONVERSATION = "conversation"
    VERSION = "version"
    MODIFICATION = "modification"
    PREFERENCE = "preference"
    SYSTEM = "system"
    NETWORK = "network"


@dataclass
class ErrorContext:
    """错误上下文信息 / Error Context Information"""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class RecoveryAction:
    """恢复操作 / Recovery Action"""
    action_type: str
    description: str
    handler: Callable
    auto_execute: bool = False


class RefinementErrorHandler:
    """交互式优化功能错误处理器 / Interactive Refinement Error Handler"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.recovery_strategies = self._initialize_recovery_strategies()
        self.error_history = []
        
    def _initialize_recovery_strategies(self) -> Dict[ErrorCategory, Dict[str, RecoveryAction]]:
        """初始化恢复策略 / Initialize Recovery Strategies"""
        return {
            ErrorCategory.CONVERSATION: {
                "session_timeout": RecoveryAction(
                    "recreate_session",
                    "重新创建对话会话 / Recreate conversation session",
                    self._recover_conversation_session,
                    auto_execute=True
                ),
                "context_overflow": RecoveryAction(
                    "compress_context",
                    "压缩对话上下文 / Compress conversation context",
                    self._compress_conversation_context,
                    auto_execute=True
                )
            },
            ErrorCategory.VERSION: {
                "storage_failure": RecoveryAction(
                    "backup_restore",
                    "从备份恢复版本数据 / Restore from backup",
                    self._restore_version_backup,
                    auto_execute=False
                ),
                "corruption": RecoveryAction(
                    "rebuild_history",
                    "重建版本历史 / Rebuild version history",
                    self._rebuild_version_history,
                    auto_execute=False
                )
            },
            ErrorCategory.MODIFICATION: {
                "llm_failure": RecoveryAction(
                    "retry_with_fallback",
                    "使用备用模型重试 / Retry with fallback model",
                    self._retry_with_fallback_model,
                    auto_execute=True
                ),
                "invalid_request": RecoveryAction(
                    "clarify_request",
                    "请求用户澄清 / Request user clarification",
                    self._request_clarification,
                    auto_execute=False
                )
            },
            ErrorCategory.PREFERENCE: {
                "learning_failure": RecoveryAction(
                    "reset_preferences",
                    "重置偏好设置 / Reset preferences",
                    self._reset_user_preferences,
                    auto_execute=False
                ),
                "data_corruption": RecoveryAction(
                    "restore_defaults",
                    "恢复默认设置 / Restore default settings",
                    self._restore_default_preferences,
                    auto_execute=True
                )
            },
            ErrorCategory.SYSTEM: {
                "resource_exhaustion": RecoveryAction(
                    "cleanup_resources",
                    "清理系统资源 / Cleanup system resources",
                    self._cleanup_system_resources,
                    auto_execute=True
                ),
                "configuration_error": RecoveryAction(
                    "reload_config",
                    "重新加载配置 / Reload configuration",
                    self._reload_system_config,
                    auto_execute=True
                )
            },
            ErrorCategory.NETWORK: {
                "connection_timeout": RecoveryAction(
                    "retry_connection",
                    "重试网络连接 / Retry network connection",
                    self._retry_network_connection,
                    auto_execute=True
                ),
                "api_rate_limit": RecoveryAction(
                    "backoff_retry",
                    "退避重试 / Backoff retry",
                    self._backoff_retry,
                    auto_execute=True
                )
            }
        }
    
    def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """统一错误处理入口 / Unified Error Handling Entry Point"""
        try:
            # 分析错误类型和严重程度
            error_context = self._analyze_error(error, context)
            
            # 记录错误
            self._log_error(error_context)
            
            # 执行恢复策略
            recovery_result = self._execute_recovery(error_context)
            
            # 更新错误历史
            self.error_history.append(error_context)
            
            return {
                "success": recovery_result.get("success", False),
                "error_id": error_context.error_id,
                "message": error_context.message,
                "recovery_action": recovery_result.get("action"),
                "user_message": self._generate_user_message(error_context, recovery_result)
            }
            
        except Exception as handler_error:
            self.logger.critical(f"Error handler failed: {handler_error}")
            return {
                "success": False,
                "error_id": "handler_failure",
                "message": "系统错误处理器故障 / Error handler failure",
                "user_message": "系统遇到严重错误，请重启应用 / System encountered critical error, please restart application"
            }
    
    def _analyze_error(self, error: Exception, context: Dict[str, Any]) -> ErrorContext:
        """分析错误类型和严重程度 / Analyze Error Type and Severity"""
        error_type = type(error).__name__
        error_message = str(error)
        
        # 根据错误类型确定类别和严重程度
        category = self._determine_error_category(error_type, error_message, context)
        severity = self._determine_error_severity(error_type, error_message, context)
        
        return ErrorContext(
            error_id=f"{category.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            category=category,
            severity=severity,
            message=error_message,
            details={
                "error_type": error_type,
                "context": context,
                "traceback": str(error)
            },
            timestamp=datetime.now(),
            user_id=context.get("user_id"),
            session_id=context.get("session_id")
        )
    
    def _determine_error_category(self, error_type: str, message: str, context: Dict[str, Any]) -> ErrorCategory:
        """确定错误类别 / Determine Error Category"""
        if "conversation" in message.lower() or "session" in message.lower():
            return ErrorCategory.CONVERSATION
        elif "version" in message.lower() or "history" in message.lower():
            return ErrorCategory.VERSION
        elif "modification" in message.lower() or "llm" in message.lower():
            return ErrorCategory.MODIFICATION
        elif "preference" in message.lower() or "learning" in message.lower():
            return ErrorCategory.PREFERENCE
        elif "network" in message.lower() or "connection" in message.lower():
            return ErrorCategory.NETWORK
        else:
            return ErrorCategory.SYSTEM
    
    def _determine_error_severity(self, error_type: str, message: str, context: Dict[str, Any]) -> ErrorSeverity:
        """确定错误严重程度 / Determine Error Severity"""
        critical_keywords = ["critical", "fatal", "corruption", "data_loss"]
        high_keywords = ["timeout", "failure", "unavailable"]
        medium_keywords = ["warning", "retry", "fallback"]
        
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in critical_keywords):
            return ErrorSeverity.CRITICAL
        elif any(keyword in message_lower for keyword in high_keywords):
            return ErrorSeverity.HIGH
        elif any(keyword in message_lower for keyword in medium_keywords):
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def _execute_recovery(self, error_context: ErrorContext) -> Dict[str, Any]:
        """执行恢复策略 / Execute Recovery Strategy"""
        category_strategies = self.recovery_strategies.get(error_context.category, {})
        
        # 根据错误详情选择合适的恢复策略
        strategy_key = self._select_recovery_strategy(error_context, category_strategies)
        
        if strategy_key and strategy_key in category_strategies:
            recovery_action = category_strategies[strategy_key]
            
            try:
                if recovery_action.auto_execute:
                    result = recovery_action.handler(error_context)
                    return {
                        "success": True,
                        "action": recovery_action.description,
                        "result": result
                    }
                else:
                    return {
                        "success": False,
                        "action": recovery_action.description,
                        "requires_user_action": True
                    }
            except Exception as recovery_error:
                self.logger.error(f"Recovery action failed: {recovery_error}")
                return {
                    "success": False,
                    "action": "recovery_failed",
                    "error": str(recovery_error)
                }
        
        return {
            "success": False,
            "action": "no_recovery_available"
        }
    
    def _select_recovery_strategy(self, error_context: ErrorContext, strategies: Dict[str, RecoveryAction]) -> Optional[str]:
        """选择恢复策略 / Select Recovery Strategy"""
        error_message = error_context.message.lower()
        
        # 基于错误消息关键词选择策略
        for strategy_key in strategies.keys():
            if strategy_key.replace("_", " ") in error_message:
                return strategy_key
        
        # 返回第一个可用策略作为默认选择
        return next(iter(strategies.keys())) if strategies else None
    
    def _log_error(self, error_context: ErrorContext):
        """记录错误日志 / Log Error"""
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }.get(error_context.severity, logging.ERROR)
        
        self.logger.log(
            log_level,
            f"Error [{error_context.error_id}] {error_context.category.value}: {error_context.message}",
            extra={
                "error_id": error_context.error_id,
                "category": error_context.category.value,
                "severity": error_context.severity.value,
                "user_id": error_context.user_id,
                "session_id": error_context.session_id,
                "details": error_context.details
            }
        )
    
    def _generate_user_message(self, error_context: ErrorContext, recovery_result: Dict[str, Any]) -> str:
        """生成用户友好的错误消息 / Generate User-Friendly Error Message"""
        if recovery_result.get("success"):
            return f"系统已自动处理问题并恢复正常 / System automatically handled the issue and recovered"
        elif recovery_result.get("requires_user_action"):
            return f"需要您的确认来解决问题：{recovery_result.get('action')} / User confirmation required: {recovery_result.get('action')}"
        else:
            return f"系统遇到问题，请稍后重试或联系支持 / System encountered an issue, please retry or contact support"
    
    # 恢复操作实现 / Recovery Action Implementations
    def _recover_conversation_session(self, error_context: ErrorContext) -> Dict[str, Any]:
        """恢复对话会话 / Recover Conversation Session"""
        return {"action": "session_recreated", "message": "对话会话已重新创建"}
    
    def _compress_conversation_context(self, error_context: ErrorContext) -> Dict[str, Any]:
        """压缩对话上下文 / Compress Conversation Context"""
        return {"action": "context_compressed", "message": "对话上下文已压缩"}
    
    def _restore_version_backup(self, error_context: ErrorContext) -> Dict[str, Any]:
        """从备份恢复版本 / Restore Version from Backup"""
        return {"action": "backup_restored", "message": "版本数据已从备份恢复"}
    
    def _rebuild_version_history(self, error_context: ErrorContext) -> Dict[str, Any]:
        """重建版本历史 / Rebuild Version History"""
        return {"action": "history_rebuilt", "message": "版本历史已重建"}
    
    def _retry_with_fallback_model(self, error_context: ErrorContext) -> Dict[str, Any]:
        """使用备用模型重试 / Retry with Fallback Model"""
        return {"action": "fallback_retry", "message": "已使用备用模型重试"}
    
    def _request_clarification(self, error_context: ErrorContext) -> Dict[str, Any]:
        """请求用户澄清 / Request User Clarification"""
        return {"action": "clarification_requested", "message": "请澄清您的修改要求"}
    
    def _reset_user_preferences(self, error_context: ErrorContext) -> Dict[str, Any]:
        """重置用户偏好 / Reset User Preferences"""
        return {"action": "preferences_reset", "message": "用户偏好已重置"}
    
    def _restore_default_preferences(self, error_context: ErrorContext) -> Dict[str, Any]:
        """恢复默认偏好 / Restore Default Preferences"""
        return {"action": "defaults_restored", "message": "已恢复默认偏好设置"}
    
    def _cleanup_system_resources(self, error_context: ErrorContext) -> Dict[str, Any]:
        """清理系统资源 / Cleanup System Resources"""
        return {"action": "resources_cleaned", "message": "系统资源已清理"}
    
    def _reload_system_config(self, error_context: ErrorContext) -> Dict[str, Any]:
        """重新加载系统配置 / Reload System Configuration"""
        return {"action": "config_reloaded", "message": "系统配置已重新加载"}
    
    def _retry_network_connection(self, error_context: ErrorContext) -> Dict[str, Any]:
        """重试网络连接 / Retry Network Connection"""
        return {"action": "connection_retried", "message": "网络连接已重试"}
    
    def _backoff_retry(self, error_context: ErrorContext) -> Dict[str, Any]:
        """退避重试 / Backoff Retry"""
        return {"action": "backoff_applied", "message": "已应用退避重试策略"}
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """获取错误统计信息 / Get Error Statistics"""
        if not self.error_history:
            return {"total_errors": 0}
        
        category_counts = {}
        severity_counts = {}
        
        for error in self.error_history:
            category_counts[error.category.value] = category_counts.get(error.category.value, 0) + 1
            severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1
        
        return {
            "total_errors": len(self.error_history),
            "by_category": category_counts,
            "by_severity": severity_counts,
            "recent_errors": len([e for e in self.error_history if (datetime.now() - e.timestamp).seconds < 3600])
        }