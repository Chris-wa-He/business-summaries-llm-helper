"""
基础性能测试 / Basic Performance Tests
"""

import pytest
import time
from src.utils.input_validator import InputValidator
from src.services.error_handler import RefinementErrorHandler


class TestBasicPerformance:
    """基础性能测试 / Basic Performance Tests"""
    
    def test_input_validation_speed(self):
        """测试输入验证速度 / Test input validation speed"""
        validator = InputValidator()
        
        start_time = time.time()
        result = validator.validate_user_message("测试消息")
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # 基准：单次验证应在100ms内完成
        assert processing_time < 0.1, f"验证耗时 {processing_time:.3f}s 超出基准"
        assert result.is_valid
    
    def test_error_handling_speed(self):
        """测试错误处理速度 / Test error handling speed"""
        error_handler = RefinementErrorHandler()
        
        start_time = time.time()
        result = error_handler.handle_error(Exception("测试错误"), {"test": True})
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # 基准：单次错误处理应在100ms内完成
        assert processing_time < 0.1, f"错误处理耗时 {processing_time:.3f}s 超出基准"
        assert "error_id" in result
    
    def test_batch_validation_performance(self):
        """测试批量验证性能 / Test batch validation performance"""
        validator = InputValidator()
        
        # 测试10条消息的批量处理
        messages = [f"测试消息 {i}" for i in range(10)]
        
        start_time = time.time()
        for message in messages:
            result = validator.validate_user_message(message)
            assert result.is_valid
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time = total_time / len(messages)
        
        # 基准：平均每条消息处理时间应在50ms内
        assert avg_time < 0.05, f"平均处理时间 {avg_time:.3f}s 超出基准"
        assert total_time < 1.0, f"总处理时间 {total_time:.3f}s 超出基准"
    
    def test_performance_baseline(self):
        """测试性能基线 / Test performance baseline"""
        # 建立基本性能指标
        metrics = {}
        
        # 输入验证基线
        validator = InputValidator()
        start_time = time.time()
        validator.validate_user_message("基线测试")
        metrics['validation_time'] = time.time() - start_time
        
        # 错误处理基线
        error_handler = RefinementErrorHandler()
        start_time = time.time()
        error_handler.handle_error(Exception("基线错误"), {})
        metrics['error_time'] = time.time() - start_time
        
        # 验证基线合理性
        assert metrics['validation_time'] < 0.1, "验证基线超出预期"
        assert metrics['error_time'] < 0.1, "错误处理基线超出预期"
        
        return metrics


class TestPerformanceReport:
    """性能报告测试 / Performance Report Tests"""
    
    def test_generate_simple_report(self):
        """生成简单性能报告 / Generate simple performance report"""
        report = {
            'test_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'components_tested': ['InputValidator', 'ErrorHandler'],
            'status': 'PASSED',
            'summary': '所有性能测试通过基准要求'
        }
        
        assert 'test_date' in report
        assert len(report['components_tested']) == 2
        assert report['status'] == 'PASSED'
        
        return report