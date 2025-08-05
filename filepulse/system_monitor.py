"""
System monitoring functionality for FilePulseApp.

This module provides system resource monitoring capabilities.
"""

import psutil
import time
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
import logging


@dataclass
class SystemMetrics:
    """System performance metrics."""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used: int
    memory_total: int
    disk_io_read: int
    disk_io_write: int
    network_sent: int
    network_recv: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp,
            'cpu_percent': self.cpu_percent,
            'memory_percent': self.memory_percent,
            'memory_used': self.memory_used,
            'memory_total': self.memory_total,
            'disk_io_read': self.disk_io_read,
            'disk_io_write': self.disk_io_write,
            'network_sent': self.network_sent,
            'network_recv': self.network_recv
        }


class SystemMonitor:
    """System resource monitor."""
    
    def __init__(self, update_interval: float = 1.0):
        """Initialize system monitor.
        
        Args:
            update_interval: Update interval in seconds
        """
        self.update_interval = update_interval
        self.running = False
        self.thread = None
        self.callbacks = []
        self.metrics_history = []
        self.max_history = 1000
        
        # Initialize baseline values for counters
        self.last_disk_io = None
        self.last_network_io = None
        
        self.logger = logging.getLogger(__name__)
    
    def add_callback(self, callback: Callable[[SystemMetrics], None]) -> None:
        """Add callback for system metrics updates.
        
        Args:
            callback: Function to call with new metrics
        """
        if callback not in self.callbacks:
            self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[SystemMetrics], None]) -> None:
        """Remove callback.
        
        Args:
            callback: Callback to remove
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def start_monitoring(self) -> bool:
        """Start system monitoring.
        
        Returns:
            True if monitoring started successfully
        """
        if self.running:
            return True
        
        try:
            # Initialize baseline values
            self._initialize_counters()
            
            self.running = True
            self.thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.thread.start()
            
            self.logger.info("System monitoring started")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start system monitoring: {e}")
            return False
    
    def stop_monitoring(self) -> None:
        """Stop system monitoring."""
        if not self.running:
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        
        self.logger.info("System monitoring stopped")
    
    def _initialize_counters(self) -> None:
        """Initialize counter baselines."""
        try:
            self.last_disk_io = psutil.disk_io_counters()
            self.last_network_io = psutil.net_io_counters()
        except Exception as e:
            self.logger.warning(f"Failed to initialize counters: {e}")
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self.running:
            try:
                metrics = self._collect_metrics()
                if metrics:
                    # Add to history
                    self.metrics_history.append(metrics)
                    if len(self.metrics_history) > self.max_history:
                        self.metrics_history.pop(0)
                    
                    # Notify callbacks
                    for callback in self.callbacks:
                        try:
                            callback(metrics)
                        except Exception as e:
                            self.logger.error(f"Error in metrics callback: {e}")
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
            
            time.sleep(self.update_interval)
    
    def _collect_metrics(self) -> Optional[SystemMetrics]:
        """Collect current system metrics.
        
        Returns:
            SystemMetrics object or None if error
        """
        try:
            timestamp = time.time()
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used
            memory_total = memory.total
            
            # Disk I/O
            disk_io_read = 0
            disk_io_write = 0
            try:
                current_disk_io = psutil.disk_io_counters()
                if current_disk_io and self.last_disk_io:
                    disk_io_read = current_disk_io.read_bytes - self.last_disk_io.read_bytes
                    disk_io_write = current_disk_io.write_bytes - self.last_disk_io.write_bytes
                self.last_disk_io = current_disk_io
            except Exception:
                pass
            
            # Network I/O
            network_sent = 0
            network_recv = 0
            try:
                current_network_io = psutil.net_io_counters()
                if current_network_io and self.last_network_io:
                    network_sent = current_network_io.bytes_sent - self.last_network_io.bytes_sent
                    network_recv = current_network_io.bytes_recv - self.last_network_io.bytes_recv
                self.last_network_io = current_network_io
            except Exception:
                pass
            
            return SystemMetrics(
                timestamp=timestamp,
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used=memory_used,
                memory_total=memory_total,
                disk_io_read=max(0, disk_io_read),  # Ensure non-negative
                disk_io_write=max(0, disk_io_write),
                network_sent=max(0, network_sent),
                network_recv=max(0, network_recv)
            )
            
        except Exception as e:
            self.logger.error(f"Failed to collect metrics: {e}")
            return None
    
    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """Get current system metrics immediately.
        
        Returns:
            SystemMetrics object or None if error
        """
        return self._collect_metrics()
    
    def get_metrics_history(self, count: Optional[int] = None) -> List[SystemMetrics]:
        """Get metrics history.
        
        Args:
            count: Number of recent metrics to return (None for all)
            
        Returns:
            List of SystemMetrics
        """
        if count is None:
            return self.metrics_history.copy()
        return self.metrics_history[-count:] if self.metrics_history else []
    
    def get_average_metrics(self, duration_seconds: Optional[float] = None) -> Optional[Dict[str, float]]:
        """Get average metrics over specified duration.
        
        Args:
            duration_seconds: Duration to average over (None for all history)
            
        Returns:
            Dictionary with average values or None if no data
        """
        if not self.metrics_history:
            return None
        
        # Filter by duration if specified
        if duration_seconds is not None:
            cutoff_time = time.time() - duration_seconds
            relevant_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        else:
            relevant_metrics = self.metrics_history
        
        if not relevant_metrics:
            return None
        
        # Calculate averages
        count = len(relevant_metrics)
        return {
            'cpu_percent': sum(m.cpu_percent for m in relevant_metrics) / count,
            'memory_percent': sum(m.memory_percent for m in relevant_metrics) / count,
            'disk_io_read_per_sec': sum(m.disk_io_read for m in relevant_metrics) / (count * self.update_interval),
            'disk_io_write_per_sec': sum(m.disk_io_write for m in relevant_metrics) / (count * self.update_interval),
            'network_sent_per_sec': sum(m.network_sent for m in relevant_metrics) / (count * self.update_interval),
            'network_recv_per_sec': sum(m.network_recv for m in relevant_metrics) / (count * self.update_interval)
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get static system information.
        
        Returns:
            Dictionary with system information
        """
        try:
            # CPU info
            cpu_info = {
                'physical_cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True),
                'max_frequency': getattr(psutil.cpu_freq(), 'max', 0) if psutil.cpu_freq() else 0,
                'current_frequency': getattr(psutil.cpu_freq(), 'current', 0) if psutil.cpu_freq() else 0
            }
            
            # Memory info
            memory = psutil.virtual_memory()
            memory_info = {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free,
                'percent': memory.percent
            }
            
            # Swap info
            swap = psutil.swap_memory()
            swap_info = {
                'total': swap.total,
                'used': swap.used,
                'free': swap.free,
                'percent': swap.percent
            }
            
            # Disk info
            disk_partitions = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_partitions.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': (usage.used / usage.total) * 100 if usage.total > 0 else 0
                    })
                except (PermissionError, FileNotFoundError):
                    continue
            
            # Network interfaces
            network_interfaces = []
            for interface, addrs in psutil.net_if_addrs().items():
                interface_info = {'name': interface, 'addresses': []}
                for addr in addrs:
                    interface_info['addresses'].append({
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': getattr(addr, 'netmask', None),
                        'broadcast': getattr(addr, 'broadcast', None)
                    })
                network_interfaces.append(interface_info)
            
            return {
                'cpu': cpu_info,
                'memory': memory_info,
                'swap': swap_info,
                'disk_partitions': disk_partitions,
                'network_interfaces': network_interfaces,
                'boot_time': psutil.boot_time()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system info: {e}")
            return {}
    
    def is_monitoring(self) -> bool:
        """Check if monitoring is active.
        
        Returns:
            True if monitoring is running
        """
        return self.running
    
    def clear_history(self) -> None:
        """Clear metrics history."""
        self.metrics_history.clear()
        self.logger.debug("Metrics history cleared")


def get_system_resources() -> Dict[str, Any]:
    """Get current system resource usage.
    
    Returns:
        Dictionary with current resource usage
    """
    try:
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory()._asdict(),
            'disk_usage': {p.mountpoint: psutil.disk_usage(p.mountpoint)._asdict() 
                          for p in psutil.disk_partitions() 
                          if not p.mountpoint.startswith('/sys') and not p.mountpoint.startswith('/proc')},
            'disk_io': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
            'network_io': psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
        }
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to get system resources: {e}")
        return {}
