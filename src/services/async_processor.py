"""
异步任务处理器 / Async Task Processor

提供异步任务处理能力，提高并发处理性能
Provides async task processing capabilities to improve concurrent processing performance
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class TaskStatus(Enum):
    """任务状态枚举 / Task Status Enum"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AsyncTask:
    """异步任务数据类 / Async Task Data Class"""
    id: str
    task_type: str
    payload: Dict[str, Any]
    status: TaskStatus
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None


class AsyncProcessor:
    """异步任务处理器 / Async Task Processor"""
    
    def __init__(self, max_workers: int = 5):
        """
        初始化异步处理器 / Initialize async processor
        
        Args:
            max_workers: 最大工作线程数 / Maximum number of workers
        """
        self.max_workers = max_workers
        self.task_queue = asyncio.Queue()
        self.active_tasks = {}
        self.completed_tasks = {}
        self.workers = []
        self.is_running = False
        self.logger = logging.getLogger(__name__)
        
        # 任务处理器映射 / Task processor mapping
        self.task_processors = {
            'refinement': self._process_refinement_task,
            'export': self._process_export_task,
            'import': self._process_import_task
        }
    
    async def start(self):
        """启动异步处理器 / Start async processor"""
        if self.is_running:
            return
        
        self.is_running = True
        self.logger.info(f"启动异步处理器，工作线程数: {self.max_workers} / Starting async processor with {self.max_workers} workers")
        
        # 启动工作线程 / Start worker threads
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker_loop(f"worker-{i}"))
            self.workers.append(worker)
    
    async def stop(self):
        """停止异步处理器 / Stop async processor"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.logger.info("停止异步处理器 / Stopping async processor")
        
        # 等待所有任务完成 / Wait for all tasks to complete
        await self.task_queue.join()
        
        # 取消工作线程 / Cancel worker threads
        for worker in self.workers:
            worker.cancel()
        
        self.workers.clear()
    
    async def submit_task(self, task_type: str, payload: Dict[str, Any]) -> str:
        """
        提交异步任务 / Submit async task
        
        Args:
            task_type: 任务类型 / Task type
            payload: 任务数据 / Task payload
            
        Returns:
            任务ID / Task ID
        """
        task_id = f"{task_type}_{int(time.time() * 1000)}"
        
        task = AsyncTask(
            id=task_id,
            task_type=task_type,
            payload=payload,
            status=TaskStatus.PENDING,
            created_at=time.time()
        )
        
        self.active_tasks[task_id] = task
        await self.task_queue.put(task)
        
        self.logger.info(f"提交异步任务: {task_id} / Submitted async task: {task_id}")
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[AsyncTask]:
        """
        获取任务状态 / Get task status
        
        Args:
            task_id: 任务ID / Task ID
            
        Returns:
            任务信息 / Task information
        """
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        elif task_id in self.completed_tasks:
            return self.completed_tasks[task_id]
        else:
            return None
    
    async def _worker_loop(self, worker_id: str):
        """
        工作线程循环 / Worker loop
        
        Args:
            worker_id: 工作线程ID / Worker ID
        """
        self.logger.info(f"启动工作线程: {worker_id} / Starting worker: {worker_id}")
        
        while self.is_running:
            try:
                # 获取任务 / Get task
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                
                # 处理任务 / Process task
                await self._process_task(task, worker_id)
                
                # 标记任务完成 / Mark task as done
                self.task_queue.task_done()
                
            except asyncio.TimeoutError:
                # 超时继续循环 / Continue loop on timeout
                continue
            except Exception as e:
                self.logger.error(f"工作线程 {worker_id} 错误: {e} / Worker {worker_id} error: {e}")
    
    async def _process_task(self, task: AsyncTask, worker_id: str):
        """
        处理单个任务 / Process single task
        
        Args:
            task: 任务对象 / Task object
            worker_id: 工作线程ID / Worker ID
        """
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        
        self.logger.info(f"工作线程 {worker_id} 开始处理任务: {task.id} / Worker {worker_id} started processing task: {task.id}")
        
        try:
            # 根据任务类型选择处理器 / Select processor based on task type
            if task.task_type in self.task_processors:
                processor = self.task_processors[task.task_type]
                result = await processor(task.payload)
                
                task.result = result
                task.status = TaskStatus.COMPLETED
                task.completed_at = time.time()
                
                self.logger.info(f"任务 {task.id} 处理完成 / Task {task.id} completed")
            else:
                raise ValueError(f"未知任务类型: {task.task_type} / Unknown task type: {task.task_type}")
                
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = time.time()
            
            self.logger.error(f"任务 {task.id} 处理失败: {e} / Task {task.id} failed: {e}")
        
        finally:
            # 移动任务到完成列表 / Move task to completed list
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]
            self.completed_tasks[task.id] = task
    
    async def _process_refinement_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理优化任务 / Process refinement task"""
        # 模拟异步处理
        await asyncio.sleep(0.1)
        return {
            'success': True,
            'message': '优化任务处理完成 / Refinement task completed'
        }
    
    async def _process_export_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理导出任务 / Process export task"""
        # 模拟异步处理
        await asyncio.sleep(0.1)
        return {
            'success': True,
            'filename': f"export_{int(time.time())}.json"
        }
    
    async def _process_import_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """处理导入任务 / Process import task"""
        # 模拟异步处理
        await asyncio.sleep(0.1)
        return {
            'success': True,
            'imported_count': payload.get('item_count', 0)
        }


class CacheManager:
    """缓存管理器 / Cache Manager"""
    
    def __init__(self, default_ttl: int = 3600):
        """
        初始化缓存管理器 / Initialize cache manager
        
        Args:
            default_ttl: 默认缓存过期时间（秒）/ Default cache TTL in seconds
        """
        self.default_ttl = default_ttl
        self.cache = {}
        self.logger = logging.getLogger(__name__)
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值 / Get cached value
        
        Args:
            key: 缓存键 / Cache key
            
        Returns:
            缓存值或None / Cached value or None
        """
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # 检查是否过期 / Check if expired
        if time.time() > entry['expires_at']:
            del self.cache[key]
            return None
        
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        设置缓存值 / Set cached value
        
        Args:
            key: 缓存键 / Cache key
            value: 缓存值 / Cache value
            ttl: 过期时间（秒）/ TTL in seconds
        """
        if ttl is None:
            ttl = self.default_ttl
        
        self.cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl,
            'created_at': time.time()
        }
        
        self.logger.debug(f"设置缓存: {key} (TTL: {ttl}s) / Set cache: {key} (TTL: {ttl}s)")
    
    def delete(self, key: str):
        """删除缓存 / Delete cache"""
        if key in self.cache:
            del self.cache[key]
            self.logger.debug(f"删除缓存: {key} / Deleted cache: {key}")
    
    def clear(self):
        """清空所有缓存 / Clear all cache"""
        self.cache.clear()
        self.logger.info("清空所有缓存 / Cleared all cache")
    
    def cleanup_expired(self):
        """清理过期缓存 / Cleanup expired cache"""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self.cache.items():
            if current_time > entry['expires_at']:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self.logger.info(f"清理了 {len(expired_keys)} 个过期缓存 / Cleaned up {len(expired_keys)} expired cache entries")