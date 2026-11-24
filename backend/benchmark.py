"""Contextual Query Engine CLI Benchmark Runner.

Run directly via:
    python benchmark.py
or:
    python -m src.benchmark
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.benchmark import print_benchmark_report, run_benchmark

if __name__ == "__main__":
    result = run_benchmark()
    print_benchmark_report(result)
