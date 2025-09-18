"""
应用监控指标收集器 / Application Metrics Collector
"""

import time
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import os

logger = logging.getLogger(__name__)


@dataclass
class MetricData:
    """指标数据结构 / Metric data structure"""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """应用指标收集器 / Application metrics collector"""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.metrics: Dict[str, MetricData] = {}
        self.counters: Dict[str, int] = {}
        self.timers: Dict[str, float] = {}
        self.start_time = time.time()
        
    def increment_counter(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """增加计数器 / Increment counter"""
        if not self.enabled:
            return
            
        self.counters[name] = self.counters.get(name, 0) + value
        self.metrics[name] = MetricData(
            name=name,
            value=self.counters[name],
            timestamp=datetime.now(),
            tags=tags or {}
        )
        
    def record_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """记录仪表盘指标 / Record gauge metric"""
        if not self.enabled:
            return
            
        self.metrics[name] = MetricData(
            name=name,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {}
        )
        
    def start_timer(self, name: str):
        """开始计时器 / Start timer"""
        if not self.enabled:
            return
            
        self.timers[name] = time.time()
        
    def end_timer(self, name: str, tags: Optional[Dict[str, str]] = None):
        """结束计时器 / End timer"""
        if not self.enabled or name not in self.timers:
            return
            
        duration = time.time() - self.timers[name]
        self.record_gauge(f"{name}_duration", duration, tags)
        del self.timers[name]
        
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要 / Get metrics summary"""
        if not self.enabled:
            return {}
            
        uptime = time.time() - self.start_time
        
        return {
            "uptime_seconds": uptime,
            "total_metrics": len(self.metrics),
            "counters": dict(self.counters),
            "recent_metrics": {
                name: {
                    "value": metric.value,
                    "timestamp": metric.timestamp.isoformat(),
                    "tags": metric.tags
                }
                for name, metric in list(self.metrics.items())[-10:]
            }
        }
        
    def export_metrics(self, format_type: str = "json") -> str:
        """导出指标数据 / Export metrics data"""
        if not self.enabled:
            return "{}" if format_type == "json" else ""
            
        summary = self.get_metrics_summary()
        
        if format_type == "json":
            return json.dumps(summary, indent=2, ensure_ascii=False)
        elif format_type == "prometheus":
            # 简单的Prometheus格式 / Simple Prometheus format
            lines = []
            for name, value in self.counters.items():
                lines.append(f"# TYPE {name} counter")
                lines.append(f"{name} {value}")
            return "\n".join(lines)
        else:
            return str(summary)


# 全局指标收集器实例 / Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """获取全局指标收集器 / Get global metrics collector"""
    global _metrics_collector
    if _metrics_collector is None:
        enabled = os.getenv("ENABLE_METRICS", "true").lower() == "true"
        _metrics_collector = MetricsCollector(enabled=enabled)
    return _metrics_collector


def record_request_metric(endpoint: str, method: str, status_code: int, duration: float):
    """记录请求指标 / Record request metric"""
    collector = get_metrics_collector()
    
    # 记录请求计数 / Record request count
    collector.increment_counter(
        "http_requests_total",
        tags={"endpoint": endpoint, "method": method, "status": str(status_code)}
    )
    
    # 记录响应时间 / Record response time
    collector.record_gauge(
        "http_request_duration_seconds",
        duration,
        tags={"endpoint": endpoint, "method": method}
    )
    
    # 记录错误率 / Record error rate
    if status_code >= 400:
        collector.increment_counter(
            "http_errors_total",
            tags={"endpoint": endpoint, "status": str(status_code)}
        )


def record_ai_model_metric(model_id: str, tokens_used: int, duration: float, success: bool):
    """记录AI模型调用指标 / Record AI model call metric"""
    collector = get_metrics_collector()
    
    # 记录模型调用次数 / Record model call count
    collector.increment_counter(
        "ai_model_calls_total",
        tags={"model": model_id, "success": str(success)}
    )
    
    # 记录token使用量 / Record token usage
    collector.record_gauge(
        "ai_model_tokens_used",
        tokens_used,
        tags={"model": model_id}
    )
    
    # 记录调用时间 / Record call duration
    collector.record_gauge(
        "ai_model_call_duration_seconds",
        duration,
        tags={"model": model_id}
    )


def record_refinement_metric(operation: str, success: bool, duration: float):
    """记录内容优化指标 / Record content refinement metric"""
    collector = get_metrics_collector()
    
    # 记录优化操作次数 / Record refinement operation count
    collector.increment_counter(
        "refinement_operations_total",
        tags={"operation": operation, "success": str(success)}
    )
    
    # 记录操作时间 / Record operation duration
    collector.record_gauge(
        "refinement_operation_duration_seconds",
        duration,
        tags={"operation": operation}
    )


def record_system_metric(metric_name: str, value: float):
    """记录系统指标 / Record system metric"""
    collector = get_metrics_collector()
    collector.record_gauge(metric_name, value)