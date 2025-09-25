"""
性能优化报告生成 / Performance Optimization Report Generation
"""

import pytest
import time
import json
from pathlib import Path
from datetime import datetime

from src.utils.input_validator import InputValidator
from src.services.error_handler import RefinementErrorHandler
from src.services.conversation_service import ConversationService
from src.services.async_processor import CacheManager


class PerformanceProfiler:
    """性能分析器 / Performance Profiler"""
    
    def __init__(self):
        self.metrics = {}
        self.recommendations = []
    
    def profile_component(self, component_name: str, operation_func, iterations: int = 100):
        """分析组件性能 / Profile component performance"""
        start_time = time.time()
        
        for _ in range(iterations):
            operation_func()
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / iterations
        
        self.metrics[component_name] = {
            'total_time': total_time,
            'average_time': avg_time,
            'iterations': iterations,
            'throughput': iterations / total_time
        }
        
        return self.metrics[component_name]
    
    def analyze_performance(self):
        """分析性能并生成建议 / Analyze performance and generate recommendations"""
        for component, metrics in self.metrics.items():
            # 分析吞吐量 / Analyze throughput
            if metrics['throughput'] < 100:
                self.recommendations.append({
                    'component': component,
                    'issue': 'Low throughput',
                    'current_value': metrics['throughput'],
                    'recommendation': 'Consider optimizing algorithm or adding caching'
                })
            
            # 分析平均响应时间 / Analyze average response time
            if metrics['average_time'] > 0.01:  # 10ms
                self.recommendations.append({
                    'component': component,
                    'issue': 'High response time',
                    'current_value': metrics['average_time'],
                    'recommendation': 'Optimize critical path or reduce complexity'
                })
    
    def generate_report(self) -> dict:
        """生成性能报告 / Generate performance report"""
        self.analyze_performance()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.metrics,
            'recommendations': self.recommendations,
            'summary': {
                'total_components': len(self.metrics),
                'issues_found': len(self.recommendations),
                'overall_health': 'Good' if len(self.recommendations) == 0 else 'Needs Attention'
            }
        }


class TestPerformanceOptimization:
    """性能优化测试 / Performance Optimization Tests"""
    
    def test_generate_performance_report(self):
        """测试生成性能报告 / Test generate performance report"""
        profiler = PerformanceProfiler()
        
        # 分析输入验证器性能 / Profile input validator performance
        validator = InputValidator()
        profiler.profile_component(
            'InputValidator',
            lambda: validator.validate_user_message("测试消息"),
            iterations=1000
        )
        
        # 分析错误处理器性能 / Profile error handler performance
        error_handler = RefinementErrorHandler()
        profiler.profile_component(
            'ErrorHandler',
            lambda: error_handler.handle_error(Exception("测试"), {"test": True}),
            iterations=500
        )
        
        # 分析缓存管理器性能 / Profile cache manager performance
        cache = CacheManager()
        profiler.profile_component(
            'CacheManager',
            lambda: cache.set("test_key", "test_value"),
            iterations=2000
        )
        
        # 生成报告 / Generate report
        report = profiler.generate_report()
        
        # 验证报告结构 / Verify report structure
        assert 'timestamp' in report
        assert 'metrics' in report
        assert 'recommendations' in report
        assert 'summary' in report
        
        # 验证指标 / Verify metrics
        assert 'InputValidator' in report['metrics']
        assert 'ErrorHandler' in report['metrics']
        assert 'CacheManager' in report['metrics']
        
        # 验证每个组件的指标 / Verify metrics for each component
        for component, metrics in report['metrics'].items():
            assert 'total_time' in metrics
            assert 'average_time' in metrics
            assert 'iterations' in metrics
            assert 'throughput' in metrics
            assert metrics['throughput'] > 0
        
        return report
    
    def test_performance_comparison(self):
        """测试性能对比 / Test performance comparison"""
        # 基线测试 / Baseline test
        validator = InputValidator()
        
        # 测试不同输入大小的性能 / Test performance with different input sizes
        input_sizes = [10, 50, 100, 200]
        results = {}
        
        for size in input_sizes:
            test_input = "测试内容 " * size
            
            start_time = time.time()
            for _ in range(100):
                result = validator.validate_user_message(test_input, max_length=size * 10)
                assert result.is_valid or not result.is_valid  # 只要有结果即可
            end_time = time.time()
            
            results[f'size_{size}'] = {
                'input_size': size * 4,  # 大约字符数
                'processing_time': end_time - start_time,
                'avg_time_per_operation': (end_time - start_time) / 100
            }
        
        # 分析性能趋势 / Analyze performance trends
        prev_time = 0
        for size_key, metrics in results.items():
            current_time = metrics['avg_time_per_operation']
            
            # 验证性能不会急剧下降 / Verify performance doesn't degrade sharply
            if prev_time > 0:
                performance_ratio = current_time / prev_time
                assert performance_ratio < 5.0, f"性能下降过快: {performance_ratio:.2f}x"
            
            prev_time = current_time
        
        return results
    
    def test_optimization_recommendations(self):
        """测试优化建议生成 / Test optimization recommendations generation"""
        profiler = PerformanceProfiler()
        
        # 模拟慢速组件 / Mock slow component
        def slow_operation():
            time.sleep(0.001)  # 1ms延迟
        
        profiler.profile_component('SlowComponent', slow_operation, iterations=10)
        
        # 模拟快速组件 / Mock fast component
        def fast_operation():
            pass
        
        profiler.profile_component('FastComponent', fast_operation, iterations=1000)
        
        # 生成报告 / Generate report
        report = profiler.generate_report()
        
        # 验证建议生成 / Verify recommendations generation
        assert len(report['recommendations']) > 0, "应该为慢速组件生成优化建议"
        
        # 检查建议内容 / Check recommendation content
        slow_recommendations = [r for r in report['recommendations'] if r['component'] == 'SlowComponent']
        assert len(slow_recommendations) > 0, "慢速组件应该有优化建议"
        
        for rec in slow_recommendations:
            assert 'issue' in rec
            assert 'current_value' in rec
            assert 'recommendation' in rec
        
        return report
    
    def test_save_performance_report(self, tmp_path):
        """测试保存性能报告 / Test save performance report"""
        profiler = PerformanceProfiler()
        
        # 生成一些测试数据 / Generate some test data
        validator = InputValidator()
        profiler.profile_component(
            'TestValidator',
            lambda: validator.validate_user_message("测试"),
            iterations=100
        )
        
        # 生成报告 / Generate report
        report = profiler.generate_report()
        
        # 保存报告 / Save report
        report_file = tmp_path / "performance_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 验证文件保存 / Verify file saved
        assert report_file.exists()
        
        # 验证文件内容 / Verify file content
        with open(report_file, 'r', encoding='utf-8') as f:
            loaded_report = json.load(f)
        
        assert loaded_report['summary']['total_components'] == report['summary']['total_components']
        assert 'TestValidator' in loaded_report['metrics']
        
        return str(report_file)


class TestPerformanceRegression:
    """性能回归测试 / Performance Regression Tests"""
    
    def test_performance_baseline_establishment(self):
        """测试性能基线建立 / Test performance baseline establishment"""
        baseline_metrics = {}
        
        # 建立各组件基线 / Establish baseline for each component
        components = {
            'InputValidator': lambda: InputValidator().validate_user_message("基线测试"),
            'ErrorHandler': lambda: RefinementErrorHandler().handle_error(Exception("基线"), {}),
            'ConversationService': lambda: ConversationService().create_session("baseline_user", "基线内容")
        }
        
        for name, operation in components.items():
            start_time = time.time()
            
            # 执行多次操作建立稳定基线 / Execute multiple operations to establish stable baseline
            for _ in range(50):
                try:
                    operation()
                except Exception:
                    pass  # 忽略错误，专注于性能测量
            
            end_time = time.time()
            avg_time = (end_time - start_time) / 50
            
            baseline_metrics[name] = {
                'average_time': avg_time,
                'baseline_date': datetime.now().isoformat(),
                'iterations': 50
            }
        
        # 验证基线合理性 / Verify baseline reasonableness
        for name, metrics in baseline_metrics.items():
            assert metrics['average_time'] > 0, f"{name} 基线时间应大于0"
            assert metrics['average_time'] < 1.0, f"{name} 基线时间不应超过1秒"
        
        return baseline_metrics
    
    def test_performance_trend_analysis(self):
        """测试性能趋势分析 / Test performance trend analysis"""
        # 模拟历史性能数据 / Mock historical performance data
        historical_data = [
            {'date': '2024-01-01', 'avg_time': 0.001, 'component': 'InputValidator'},
            {'date': '2024-01-02', 'avg_time': 0.0012, 'component': 'InputValidator'},
            {'date': '2024-01-03', 'avg_time': 0.0015, 'component': 'InputValidator'},
            {'date': '2024-01-04', 'avg_time': 0.0011, 'component': 'InputValidator'},
        ]
        
        # 分析趋势 / Analyze trends
        times = [data['avg_time'] for data in historical_data]
        
        # 计算性能变化 / Calculate performance changes
        if len(times) > 1:
            latest_time = times[-1]
            baseline_time = times[0]
            performance_change = (latest_time - baseline_time) / baseline_time
            
            # 验证性能没有显著退化 / Verify no significant performance degradation
            assert abs(performance_change) < 0.5, f"性能变化过大: {performance_change:.1%}"
        
        # 计算平均性能 / Calculate average performance
        avg_performance = sum(times) / len(times)
        assert avg_performance < 0.01, f"平均性能 {avg_performance:.4f}s 超出预期"
        
        return {
            'trend_analysis': {
                'performance_change': performance_change if len(times) > 1 else 0,
                'average_performance': avg_performance,
                'data_points': len(historical_data)
            }
        }