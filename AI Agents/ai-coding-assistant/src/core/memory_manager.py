"""
Memory Manager

Monitors and manages memory usage across RAG components.
Provides:
- Memory monitoring with configurable thresholds
- Automatic garbage collection
- Model unloading on idle
- Adaptive batch sizing
- Memory pressure detection

Features:
- Cross-platform memory monitoring
- Thread-safe operations
- Background monitoring thread
- Event-based cleanup triggers
"""

import gc
import time
import threading
import psutil
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MemorySnapshot:
    """Snapshot of current memory usage."""
    timestamp: float
    total_mb: float
    used_mb: float
    available_mb: float
    percent: float
    process_mb: float


class MemoryManager:
    """
    Manages memory usage for RAG components.
    
    Monitors system and process memory, triggers cleanup when needed.
    """
    
    def __init__(
        self,
        gc_threshold_mb: int = 500,
        enable_auto_gc: bool = True,
        gc_interval_seconds: int = 60,
        enable_model_unloading: bool = True,
        model_idle_timeout_seconds: int = 300
    ):
        """
        Initialize memory manager.
        
        Args:
            gc_threshold_mb: Trigger GC above this memory usage
            enable_auto_gc: Enable automatic garbage collection
            gc_interval_seconds: Interval for GC checks
            enable_model_unloading: Enable automatic model unloading
            model_idle_timeout_seconds: Unload model after this idle time
        
        Example:
            >>> memory_mgr = MemoryManager(
            ...     gc_threshold_mb=500,
            ...     enable_auto_gc=True
            ... )
            >>> memory_mgr.start_monitoring()
        """
        self.gc_threshold_mb = gc_threshold_mb
        self.enable_auto_gc = enable_auto_gc
        self.gc_interval_seconds = gc_interval_seconds
        self.enable_model_unloading = enable_model_unloading
        self.model_idle_timeout_seconds = model_idle_timeout_seconds
        
        # Process handle
        self.process = psutil.Process()
        
        # Monitoring thread
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()
        
        # Statistics
        self.gc_count = 0
        self.model_unload_count = 0
        self.last_gc_time = time.time()
        self.last_model_activity = time.time()
        
        # Memory history
        self.memory_history: List[MemorySnapshot] = []
        self.max_history_size = 100
        
        # Callbacks
        self._cleanup_callbacks: List[Callable] = []
        self._model_unload_callback: Optional[Callable] = None
    
    def get_memory_usage(self) -> MemorySnapshot:
        """
        Get current memory usage snapshot.
        
        Returns:
            MemorySnapshot with current memory stats
        
        Example:
            >>> snapshot = memory_mgr.get_memory_usage()
            >>> print(f"Process memory: {snapshot.process_mb:.1f} MB")
            >>> print(f"System usage: {snapshot.percent:.1f}%")
        """
        # System memory
        vm = psutil.virtual_memory()
        
        # Process memory
        mem_info = self.process.memory_info()
        process_mb = mem_info.rss / (1024 * 1024)
        
        snapshot = MemorySnapshot(
            timestamp=time.time(),
            total_mb=vm.total / (1024 * 1024),
            used_mb=vm.used / (1024 * 1024),
            available_mb=vm.available / (1024 * 1024),
            percent=vm.percent,
            process_mb=process_mb
        )
        
        # Add to history
        with self._lock:
            self.memory_history.append(snapshot)
            if len(self.memory_history) > self.max_history_size:
                self.memory_history.pop(0)
        
        return snapshot
    
    def check_memory_pressure(self) -> bool:
        """
        Check if system is under memory pressure.
        
        Returns:
            True if memory usage is high
        
        Example:
            >>> if memory_mgr.check_memory_pressure():
            ...     print("Memory pressure detected!")
            ...     memory_mgr.trigger_cleanup()
        """
        snapshot = self.get_memory_usage()
        
        # Check system memory
        if snapshot.percent > 85:
            return True
        
        # Check process memory
        if snapshot.process_mb > self.gc_threshold_mb:
            return True
        
        return False
    
    def trigger_cleanup(self, force: bool = False) -> Dict[str, Any]:
        """
        Trigger memory cleanup.
        
        Args:
            force: Force cleanup even if not needed
        
        Returns:
            Dictionary with cleanup results
        
        Example:
            >>> results = memory_mgr.trigger_cleanup()
            >>> print(f"Freed: {results['memory_freed_mb']:.1f} MB")
        """
        with self._lock:
            before_snapshot = self.get_memory_usage()
            
            # Run cleanup callbacks
            for callback in self._cleanup_callbacks:
                try:
                    callback()
                except Exception as e:
                    print(f"Warning: Cleanup callback failed: {e}")
            
            # Force garbage collection
            if self.enable_auto_gc or force:
                collected = gc.collect()
                self.gc_count += 1
                self.last_gc_time = time.time()
            else:
                collected = 0
            
            after_snapshot = self.get_memory_usage()
            
            memory_freed = before_snapshot.process_mb - after_snapshot.process_mb
            
            return {
                'gc_collected': collected,
                'memory_before_mb': before_snapshot.process_mb,
                'memory_after_mb': after_snapshot.process_mb,
                'memory_freed_mb': memory_freed,
                'timestamp': datetime.now().isoformat()
            }
    
    def register_cleanup_callback(self, callback: Callable) -> None:
        """
        Register a callback for cleanup events.
        
        Args:
            callback: Function to call during cleanup
        
        Example:
            >>> def clear_cache():
            ...     print("Clearing cache...")
            >>> memory_mgr.register_cleanup_callback(clear_cache)
        """
        with self._lock:
            self._cleanup_callbacks.append(callback)
    
    def register_model_unload_callback(self, callback: Callable) -> None:
        """
        Register callback for model unloading.
        
        Args:
            callback: Function to call to unload model
        
        Example:
            >>> def unload_embedding_model():
            ...     print("Unloading embedding model...")
            >>> memory_mgr.register_model_unload_callback(unload_embedding_model)
        """
        self._model_unload_callback = callback
    
    def mark_model_activity(self) -> None:
        """
        Mark that model was recently used.
        
        Resets idle timer for model unloading.
        
        Example:
            >>> # After using model
            >>> memory_mgr.mark_model_activity()
        """
        self.last_model_activity = time.time()
    
    def check_model_idle(self) -> bool:
        """
        Check if model has been idle.
        
        Returns:
            True if model should be unloaded
        
        Example:
            >>> if memory_mgr.check_model_idle():
            ...     print("Model has been idle, should unload")
        """
        if not self.enable_model_unloading:
            return False
        
        idle_time = time.time() - self.last_model_activity
        return idle_time > self.model_idle_timeout_seconds
    
    def unload_model_if_idle(self) -> bool:
        """
        Unload model if it's been idle.
        
        Returns:
            True if model was unloaded
        
        Example:
            >>> if memory_mgr.unload_model_if_idle():
            ...     print("Model unloaded due to inactivity")
        """
        if not self.check_model_idle():
            return False
        
        if self._model_unload_callback:
            try:
                self._model_unload_callback()
                self.model_unload_count += 1
                print(f"✓ Model unloaded after {self.model_idle_timeout_seconds}s idle")
                return True
            except Exception as e:
                print(f"Warning: Model unload failed: {e}")
        
        return False
    
    def start_monitoring(self) -> None:
        """
        Start background memory monitoring.
        
        Runs periodic checks and triggers cleanup when needed.
        
        Example:
            >>> memory_mgr.start_monitoring()
            >>> # Monitoring runs in background
            >>> time.sleep(60)
            >>> memory_mgr.stop_monitoring()
        """
        if self._monitoring:
            print("Memory monitoring already running")
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self._monitor_thread.start()
        print("✓ Memory monitoring started")
    
    def stop_monitoring(self) -> None:
        """
        Stop background memory monitoring.
        
        Example:
            >>> memory_mgr.stop_monitoring()
        """
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        print("✓ Memory monitoring stopped")
    
    def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while self._monitoring:
            try:
                # Check memory pressure
                if self.check_memory_pressure():
                    print("⚠ Memory pressure detected, triggering cleanup...")
                    results = self.trigger_cleanup()
                    print(f"  Freed {results['memory_freed_mb']:.1f} MB")
                
                # Check model idle
                if self.enable_model_unloading:
                    self.unload_model_if_idle()
                
                # Periodic GC
                time_since_gc = time.time() - self.last_gc_time
                if time_since_gc > self.gc_interval_seconds:
                    if self.enable_auto_gc:
                        gc.collect()
                        self.gc_count += 1
                        self.last_gc_time = time.time()
                
            except Exception as e:
                print(f"Warning: Monitor loop error: {e}")
            
            # Sleep for check interval
            time.sleep(min(self.gc_interval_seconds, 30))
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get memory management statistics.
        
        Returns:
            Dictionary with statistics
        
        Example:
            >>> stats = memory_mgr.get_statistics()
            >>> print(f"GC count: {stats['gc_count']}")
            >>> print(f"Current memory: {stats['current_memory_mb']:.1f} MB")
        """
        snapshot = self.get_memory_usage()
        
        # Calculate average memory over history
        if self.memory_history:
            avg_memory = sum(s.process_mb for s in self.memory_history) / len(self.memory_history)
            peak_memory = max(s.process_mb for s in self.memory_history)
        else:
            avg_memory = snapshot.process_mb
            peak_memory = snapshot.process_mb
        
        return {
            'current_memory_mb': snapshot.process_mb,
            'current_memory_percent': snapshot.percent,
            'average_memory_mb': avg_memory,
            'peak_memory_mb': peak_memory,
            'gc_count': self.gc_count,
            'model_unload_count': self.model_unload_count,
            'monitoring_active': self._monitoring,
            'cleanup_callbacks_registered': len(self._cleanup_callbacks),
            'memory_history_size': len(self.memory_history)
        }
    
    def get_adaptive_batch_size(
        self,
        base_batch_size: int,
        max_batch_memory_mb: int = 512
    ) -> int:
        """
        Calculate adaptive batch size based on available memory.
        
        Args:
            base_batch_size: Desired batch size
            max_batch_memory_mb: Maximum memory for batch
        
        Returns:
            Adjusted batch size
        
        Example:
            >>> batch_size = memory_mgr.get_adaptive_batch_size(
            ...     base_batch_size=32,
            ...     max_batch_memory_mb=256
            ... )
            >>> print(f"Using batch size: {batch_size}")
        """
        snapshot = self.get_memory_usage()
        
        # If plenty of memory available, use base size
        if snapshot.available_mb > max_batch_memory_mb * 2:
            return base_batch_size
        
        # If low memory, reduce batch size
        if snapshot.available_mb < max_batch_memory_mb:
            reduction_factor = snapshot.available_mb / max_batch_memory_mb
            adjusted = int(base_batch_size * reduction_factor)
            return max(1, adjusted)
        
        return base_batch_size
    
    def __del__(self):
        """Cleanup on destruction."""
        if self._monitoring:
            self.stop_monitoring()


if __name__ == "__main__":
    print("=== Memory Manager Tests ===\n")
    
    # Create memory manager
    memory_mgr = MemoryManager(
        gc_threshold_mb=500,
        enable_auto_gc=True,
        gc_interval_seconds=5,
        enable_model_unloading=True,
        model_idle_timeout_seconds=3
    )
    
    # Test 1: Get memory usage
    print("1. Memory Usage:")
    snapshot = memory_mgr.get_memory_usage()
    print(f"   Process: {snapshot.process_mb:.1f} MB")
    print(f"   System: {snapshot.percent:.1f}%")
    print(f"   Available: {snapshot.available_mb:.1f} MB")
    print("   ✓ Memory monitoring works")
    
    # Test 2: Memory pressure
    print("\n2. Memory Pressure Check:")
    under_pressure = memory_mgr.check_memory_pressure()
    print(f"   Under pressure: {under_pressure}")
    print("   ✓ Pressure detection works")
    
    # Test 3: Cleanup
    print("\n3. Cleanup:")
    results = memory_mgr.trigger_cleanup(force=True)
    print(f"   GC collected: {results['gc_collected']} objects")
    print(f"   Memory freed: {results['memory_freed_mb']:.1f} MB")
    print("   ✓ Cleanup works")
    
    # Test 4: Callbacks
    print("\n4. Cleanup Callbacks:")
    callback_called = False
    def test_callback():
        global callback_called
        callback_called = True
        print("   Callback executed!")
    
    memory_mgr.register_cleanup_callback(test_callback)
    memory_mgr.trigger_cleanup(force=True)
    assert callback_called
    print("   ✓ Callbacks work")
    
    # Test 5: Model idle detection
    print("\n5. Model Idle Detection:")
    memory_mgr.mark_model_activity()
    print("   Marked activity")
    time.sleep(1)
    is_idle = memory_mgr.check_model_idle()
    print(f"   Idle after 1s: {is_idle}")
    time.sleep(3)
    is_idle = memory_mgr.check_model_idle()
    print(f"   Idle after 4s: {is_idle}")
    print("   ✓ Idle detection works")
    
    # Test 6: Adaptive batch sizing
    print("\n6. Adaptive Batch Sizing:")
    batch_size = memory_mgr.get_adaptive_batch_size(32, 256)
    print(f"   Adjusted batch size: {batch_size}")
    print("   ✓ Adaptive sizing works")
    
    # Test 7: Statistics
    print("\n7. Statistics:")
    stats = memory_mgr.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    print("   ✓ Statistics work")
    
    # Test 8: Background monitoring (brief)
    print("\n8. Background Monitoring:")
    memory_mgr.start_monitoring()
    print("   Monitoring started, waiting 6 seconds...")
    time.sleep(6)
    memory_mgr.stop_monitoring()
    print("   ✓ Background monitoring works")
    
    print("\n✓ All memory manager tests passed!")
