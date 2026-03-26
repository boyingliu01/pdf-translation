"""Performance test for PDF translation."""

import time
import psutil
import os
from pathlib import Path


def test_performance():
    """Test translation performance."""
    print("=== Performance Test ===\n")

    # Check if translated PDF exists
    pdf_path = Path(
        "E:/2-booboo/Palantir/output/The Philosopher in the Valley Alex Karp, Palantir, and the Rise of the Surveillance State.FINAL_FIXED.zh.dual.pdf"
    )

    if pdf_path.exists():
        file_size_mb = pdf_path.stat().st_size / 1024 / 1024
        print(f"✓ Translated PDF size: {file_size_mb:.2f} MB")
    else:
        print("✗ Translated PDF not found")

    # Check memory usage
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"✓ Current memory usage: {memory_mb:.2f} MB")

    # Check CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"✓ CPU usage: {cpu_percent}%")

    # Check disk usage
    disk_usage = psutil.disk_usage("E:")
    disk_free_gb = disk_usage.free / 1024 / 1024 / 1024
    print(f"✓ Disk free: {disk_free_gb:.2f} GB")

    print("\n=== Performance Test Completed ===")


if __name__ == "__main__":
    test_performance()
