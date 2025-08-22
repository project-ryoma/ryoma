#!/usr/bin/env python3
"""
Performance and stress tests for the InjectedStore system and SQL tools.
Tests system performance under load, memory usage, latency, and throughput scenarios.
"""

import asyncio
import gc
import statistics
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Tuple
from unittest.mock import MagicMock, Mock

import psutil
import pytest
from langgraph.store.memory import InMemoryStore
from ryoma_ai.agent.base import BaseAgent
from ryoma_ai.agent.workflow import WorkflowAgent
from ryoma_ai.datasource.sql import SqlDataSource
from ryoma_ai.tool.sql_tool import (
    Column,
    CreateTableTool,
    QueryPlanTool,
    SchemaAnalysisTool,
    SqlQueryTool,
    get_datasource_from_store,
)


class PerformanceMockDataSource:
    """High-performance mock datasource for stress testing."""

    def __init__(self, response_delay: float = 0.001):
        self.response_delay = response_delay
        self.query_count = 0
        self.total_response_time = 0.0
        self.lock = threading.Lock()

    def query(self, sql: str):
        start_time = time.time()
        time.sleep(self.response_delay)  # Simulate query execution time

        with self.lock:
            self.query_count += 1
            self.total_response_time += time.time() - start_time

        return f"Query {self.query_count}: {sql[:50]}..."

    def get_catalog(self):
        time.sleep(self.response_delay * 0.5)  # Faster than query
        mock_catalog = Mock()
        mock_catalog.catalog_name = "performance_catalog"
        mock_catalog.schemas = []
        return mock_catalog

    def get_query_plan(self, query: str):
        time.sleep(self.response_delay * 0.8)
        return f"Execution plan for: {query[:30]}..."

    def get_query_profile(self, query: str):
        time.sleep(self.response_delay * 1.2)
        return f"Performance profile for: {query[:30]}..."

    @property
    def average_response_time(self):
        with self.lock:
            if self.query_count == 0:
                return 0
            return self.total_response_time / self.query_count


class TestPerformanceBenchmarks:
    """Performance benchmarks for core functionality."""

    def test_store_operation_performance(self):
        """Benchmark store put/get operations."""
        store = InMemoryStore()
        datasource = PerformanceMockDataSource(response_delay=0.0001)

        # Benchmark put operations
        put_times = []
        for i in range(1000):
            start_time = time.time()
            store.put(("datasource",), f"namespace_{i}", datasource)
            put_times.append(time.time() - start_time)

        # Benchmark get operations
        get_times = []
        for i in range(1000):
            start_time = time.time()
            result = store.get(("datasource",), f"namespace_{i % 100}")  # Access subset
            get_times.append(time.time() - start_time)
            assert result is not None

        # Performance assertions
        avg_put_time = statistics.mean(put_times)
        avg_get_time = statistics.mean(get_times)

        print(f"Average put time: {avg_put_time:.6f}s")
        print(f"Average get time: {avg_get_time:.6f}s")

        # Performance thresholds (adjust based on system capabilities)
        assert avg_put_time < 0.001  # Less than 1ms per put
        assert avg_get_time < 0.001  # Less than 1ms per get

        # Check for performance consistency
        put_stddev = statistics.stdev(put_times)
        get_stddev = statistics.stdev(get_times)

        assert put_stddev < avg_put_time * 2  # Standard deviation should be reasonable
        assert get_stddev < avg_get_time * 2

    def test_tool_execution_performance(self):
        """Benchmark SQL tool execution performance."""
        store = InMemoryStore()
        fast_datasource = PerformanceMockDataSource(response_delay=0.0001)
        store.put(("datasource",), "main", fast_datasource)

        tool = SqlQueryTool()

        # Benchmark tool execution
        execution_times = []
        for i in range(500):
            start_time = time.time()
            result = tool._run(query=f"SELECT {i} FROM test_table", store=store)
            execution_times.append(time.time() - start_time)

            assert isinstance(result, tuple)
            assert len(result) == 2

        # Performance analysis
        avg_execution_time = statistics.mean(execution_times)
        median_execution_time = statistics.median(execution_times)
        p95_execution_time = sorted(execution_times)[int(0.95 * len(execution_times))]

        print(f"Average execution time: {avg_execution_time:.6f}s")
        print(f"Median execution time: {median_execution_time:.6f}s")
        print(f"95th percentile execution time: {p95_execution_time:.6f}s")

        # Performance thresholds
        assert avg_execution_time < 0.01  # Less than 10ms average
        assert p95_execution_time < 0.02  # Less than 20ms for 95% of requests

        # Verify datasource was used efficiently
        assert fast_datasource.query_count == 500

    def test_helper_function_performance(self):
        """Benchmark get_datasource_from_store helper function."""
        store = InMemoryStore()
        datasource = PerformanceMockDataSource(response_delay=0)
        store.put(("datasource",), "main", datasource)

        # Benchmark helper function
        retrieval_times = []
        for i in range(10000):  # Many iterations for micro-benchmark
            start_time = time.time()
            result = get_datasource_from_store(store)
            retrieval_times.append(time.time() - start_time)

            assert result is datasource

        avg_retrieval_time = statistics.mean(retrieval_times)
        print(f"Average helper function time: {avg_retrieval_time:.9f}s")

        # Should be very fast as it's just a store lookup
        assert avg_retrieval_time < 0.0001  # Less than 0.1ms


class TestThroughputAndConcurrency:
    """Test system throughput under concurrent load."""

    def test_concurrent_tool_execution_throughput(self):
        """Test throughput with multiple concurrent tool executions."""
        store = InMemoryStore()
        datasource = PerformanceMockDataSource(response_delay=0.001)
        store.put(("datasource",), "main", datasource)

        def worker_task(task_id: int, num_operations: int) -> List[float]:
            tool = SqlQueryTool()
            execution_times = []

            for i in range(num_operations):
                start_time = time.time()
                result = tool._run(query=f"SELECT {task_id}_{i}", store=store)
                execution_times.append(time.time() - start_time)

                assert isinstance(result, tuple)

            return execution_times

        # Test with different concurrency levels
        concurrency_levels = [1, 2, 4, 8, 16]
        results = {}

        for num_threads in concurrency_levels:
            start_time = time.time()

            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = [
                    executor.submit(worker_task, i, 50)  # 50 operations per thread
                    for i in range(num_threads)
                ]

                all_times = []
                for future in as_completed(futures):
                    all_times.extend(future.result())

            total_time = time.time() - start_time
            total_operations = num_threads * 50
            throughput = total_operations / total_time

            results[num_threads] = {
                "throughput": throughput,
                "total_time": total_time,
                "avg_latency": statistics.mean(all_times),
                "operations": total_operations,
            }

            print(
                f"Concurrency {num_threads}: {throughput:.1f} ops/sec, "
                f"avg latency: {statistics.mean(all_times):.4f}s"
            )

        # Verify that concurrency improves throughput (up to a point)
        assert results[2]["throughput"] > results[1]["throughput"]
        assert results[4]["throughput"] > results[2]["throughput"]

        # Verify all operations completed successfully
        expected_total_queries = sum(level * 50 for level in concurrency_levels)
        assert (
            datasource.query_count >= expected_total_queries * 0.9
        )  # Allow some tolerance

    def test_store_concurrent_access_performance(self):
        """Test store performance under concurrent access."""
        store = InMemoryStore()

        # Pre-populate store with datasources
        datasources = []
        for i in range(100):
            ds = PerformanceMockDataSource(response_delay=0.0001)
            store.put(("datasource",), f"ds_{i}", ds)
            datasources.append(ds)

        def concurrent_access_worker(
            worker_id: int, num_accesses: int
        ) -> Dict[str, float]:
            access_times = []
            retrieval_times = []

            for i in range(num_accesses):
                # Access random datasource
                ds_id = (worker_id * num_accesses + i) % 100

                start_time = time.time()
                result = store.get(("datasource",), f"ds_{ds_id}")
                access_time = time.time() - start_time
                access_times.append(access_time)

                assert result is not None

                # Use helper function
                temp_store = InMemoryStore()
                temp_store.put(("datasource",), "main", result.value)

                start_time = time.time()
                retrieved_ds = get_datasource_from_store(temp_store)
                retrieval_time = time.time() - start_time
                retrieval_times.append(retrieval_time)

                assert retrieved_ds is result.value

            return {
                "avg_access_time": statistics.mean(access_times),
                "avg_retrieval_time": statistics.mean(retrieval_times),
                "total_accesses": num_accesses,
            }

        # Run concurrent access test
        num_workers = 8
        accesses_per_worker = 100

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [
                executor.submit(concurrent_access_worker, i, accesses_per_worker)
                for i in range(num_workers)
            ]

            worker_results = [future.result() for future in as_completed(futures)]

        total_time = time.time() - start_time
        total_accesses = num_workers * accesses_per_worker
        access_throughput = total_accesses / total_time

        print(f"Concurrent store access: {access_throughput:.1f} accesses/sec")

        # Performance verification
        assert access_throughput > 1000  # Should handle >1000 accesses per second

        avg_access_times = [r["avg_access_time"] for r in worker_results]
        overall_avg_access = statistics.mean(avg_access_times)
        assert overall_avg_access < 0.001  # Less than 1ms average access time

    def test_workflow_agent_performance(self):
        """Test WorkflowAgent performance under load."""
        from langchain_core.language_models.chat_models import BaseChatModel
        from langchain_core.messages import AIMessage
        from ryoma_ai.agent.workflow import ToolMode, WorkflowAgent

        class FastMockModel(BaseChatModel):
            def __init__(self):
                super().__init__()
                self.call_count = 0

            def _generate(self, messages, stop=None, **kwargs):
                self.call_count += 1
                mock_generation = Mock()
                mock_generation.message = AIMessage(
                    content=f"Response {self.call_count}"
                )
                mock_result = Mock()
                mock_result.generations = [[mock_generation]]
                return mock_result

            def _llm_type(self):
                return "fast_mock_model"

            @property
            def _identifying_params(self):
                return {"model": "fast_mock"}

        # Create workflow agent with performance datasource
        datasource = PerformanceMockDataSource(response_delay=0.001)
        tools = [SqlQueryTool(), QueryPlanTool(), SchemaAnalysisTool()]

        agent = WorkflowAgent(tools=tools, model=FastMockModel(), datasource=datasource)

        # Benchmark workflow execution
        execution_times = []
        for i in range(20):  # Fewer iterations due to workflow complexity
            start_time = time.time()
            result = agent.invoke(f"Execute query {i}", display=False)
            execution_times.append(time.time() - start_time)

            assert result is not None

        avg_workflow_time = statistics.mean(execution_times)
        print(f"Average workflow execution time: {avg_workflow_time:.4f}s")

        # Workflow should complete reasonably quickly
        assert avg_workflow_time < 1.0  # Less than 1 second per workflow


class TestMemoryUsageAndLeaks:
    """Test memory usage patterns and detect potential leaks."""

    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024

    def test_store_memory_usage_scaling(self):
        """Test how store memory usage scales with data."""
        initial_memory = self.get_memory_usage()
        store = InMemoryStore()

        memory_measurements = [initial_memory]
        object_counts = [0]

        # Add datasources in batches and measure memory
        batch_size = 100
        num_batches = 10

        for batch in range(num_batches):
            # Add batch of datasources
            for i in range(batch_size):
                ds = PerformanceMockDataSource(response_delay=0)
                ds.large_data = "x" * 1000  # 1KB per datasource
                store.put(("datasource",), f"batch_{batch}_ds_{i}", ds)

            # Force garbage collection and measure
            gc.collect()
            memory_usage = self.get_memory_usage()
            memory_measurements.append(memory_usage)
            object_counts.append((batch + 1) * batch_size)

        # Analyze memory scaling
        memory_growth = memory_measurements[-1] - memory_measurements[0]
        objects_created = object_counts[-1]

        print(f"Memory growth: {memory_growth:.1f} MB for {objects_created} objects")
        print(f"Memory per object: {memory_growth / objects_created * 1024:.1f} KB")

        # Memory growth should be reasonable
        assert memory_growth < 100  # Less than 100MB for 1000 objects

        # Memory scaling should be roughly linear
        mid_point = len(memory_measurements) // 2
        first_half_growth = memory_measurements[mid_point] - memory_measurements[0]
        second_half_growth = memory_measurements[-1] - memory_measurements[mid_point]

        # Second half shouldn't grow much more than first half (indicating linear scaling)
        assert second_half_growth < first_half_growth * 2

    def test_tool_execution_memory_stability(self):
        """Test that repeated tool execution doesn't leak memory."""
        initial_memory = self.get_memory_usage()

        store = InMemoryStore()
        datasource = PerformanceMockDataSource(response_delay=0.0001)
        store.put(("datasource",), "main", datasource)

        tool = SqlQueryTool()

        # Execute many operations
        num_operations = 1000
        memory_samples = []

        for i in range(num_operations):
            result = tool._run(query=f"SELECT {i}", store=store)
            assert isinstance(result, tuple)

            # Sample memory usage periodically
            if i % 100 == 0:
                gc.collect()
                memory_samples.append(self.get_memory_usage())

        final_memory = self.get_memory_usage()
        memory_growth = final_memory - initial_memory

        print(
            f"Memory growth after {num_operations} operations: {memory_growth:.1f} MB"
        )

        # Memory growth should be minimal (no major leaks)
        assert memory_growth < 50  # Less than 50MB growth

        # Memory should be relatively stable (not continuously growing)
        if len(memory_samples) > 2:
            early_memory = statistics.mean(memory_samples[:3])
            late_memory = statistics.mean(memory_samples[-3:])
            stability_ratio = late_memory / early_memory

            assert stability_ratio < 1.5  # Memory shouldn't grow more than 50%

    def test_concurrent_execution_memory_efficiency(self):
        """Test memory efficiency under concurrent execution."""
        initial_memory = self.get_memory_usage()

        store = InMemoryStore()
        datasource = PerformanceMockDataSource(response_delay=0.001)
        store.put(("datasource",), "main", datasource)

        def memory_intensive_worker(worker_id: int, num_ops: int):
            tool = SqlQueryTool()
            results = []

            for i in range(num_ops):
                result = tool._run(query=f"SELECT {worker_id}_{i}", store=store)
                # Keep results in memory temporarily to test memory pressure
                results.append(result)

            return len(results)

        # Run concurrent memory-intensive tasks
        num_threads = 4
        ops_per_thread = 100

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(memory_intensive_worker, i, ops_per_thread)
                for i in range(num_threads)
            ]

            completed_ops = [future.result() for future in as_completed(futures)]

        final_memory = self.get_memory_usage()
        memory_growth = final_memory - initial_memory

        print(
            f"Memory growth with {num_threads} concurrent threads: {memory_growth:.1f} MB"
        )

        # Verify all operations completed
        assert sum(completed_ops) == num_threads * ops_per_thread

        # Memory growth should be reasonable for concurrent execution
        assert memory_growth < 100  # Less than 100MB for concurrent test


class TestLatencyAndResponseTime:
    """Test latency characteristics and response time distribution."""

    def test_latency_distribution(self):
        """Test latency distribution characteristics."""
        store = InMemoryStore()

        # Test with different response delays
        delay_scenarios = [0.001, 0.005, 0.01, 0.02]

        for delay in delay_scenarios:
            datasource = PerformanceMockDataSource(response_delay=delay)
            store.put(("datasource",), "main", datasource)

            tool = SqlQueryTool()
            latencies = []

            # Collect latency samples
            for i in range(100):
                start_time = time.time()
                result = tool._run(query=f"SELECT {i}", store=store)
                latency = time.time() - start_time
                latencies.append(latency)

                assert isinstance(result, tuple)

            # Analyze latency distribution
            avg_latency = statistics.mean(latencies)
            median_latency = statistics.median(latencies)
            p99_latency = sorted(latencies)[99]  # 99th percentile
            latency_stddev = statistics.stdev(latencies)

            print(
                f"Delay {delay:.3f}s - Avg: {avg_latency:.4f}s, "
                f"Median: {median_latency:.4f}s, P99: {p99_latency:.4f}s, "
                f"StdDev: {latency_stddev:.4f}s"
            )

            # Latency should correlate with datasource delay
            assert avg_latency >= delay * 0.8  # Allow some tolerance
            assert avg_latency <= delay * 3.0  # But not too much overhead

            # P99 latency should be reasonable
            assert p99_latency <= delay * 5.0

    def test_cold_start_vs_warm_performance(self):
        """Test performance difference between cold start and warm execution."""
        store = InMemoryStore()
        datasource = PerformanceMockDataSource(response_delay=0.001)
        store.put(("datasource",), "main", datasource)

        tool = SqlQueryTool()

        # Cold start - first execution
        start_time = time.time()
        result = tool._run(query="SELECT cold_start", store=store)
        cold_start_time = time.time() - start_time

        assert isinstance(result, tuple)

        # Warm executions
        warm_times = []
        for i in range(50):
            start_time = time.time()
            result = tool._run(query=f"SELECT warm_{i}", store=store)
            warm_times.append(time.time() - start_time)
            assert isinstance(result, tuple)

        avg_warm_time = statistics.mean(warm_times)

        print(f"Cold start time: {cold_start_time:.6f}s")
        print(f"Average warm time: {avg_warm_time:.6f}s")
        print(f"Cold start overhead: {(cold_start_time - avg_warm_time) * 1000:.2f}ms")

        # Cold start might be slower, but not excessively
        assert cold_start_time <= avg_warm_time * 10  # At most 10x slower

        # Warm execution should be consistent
        warm_stddev = statistics.stdev(warm_times)
        assert warm_stddev < avg_warm_time * 0.5  # Low variance in warm execution


if __name__ == "__main__":
    # Add performance markers for pytest-benchmark if available
    try:
        import pytest_benchmark

        print("pytest-benchmark is available for advanced performance testing")
    except ImportError:
        print("pytest-benchmark not available, using basic timing")

    pytest.main([__file__, "-v", "-s"])  # -s to show print statements
