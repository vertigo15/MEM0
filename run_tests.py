#!/usr/bin/env python3
"""Test runner script for mem0 API tests."""

import sys
import subprocess
import argparse
import time
import requests
from pathlib import Path


def check_api_health(base_url="http://localhost:8000", timeout=30):
    """Check if the API is healthy and ready for testing."""
    print(f"Checking API health at {base_url}/health...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ API is healthy: {health_data['status']}")
                print(f"   Database: {health_data['database']}")
                print(f"   LLM Provider: {health_data['llm_provider']}")
                print(f"   Storage Provider: {health_data['storage_provider']}")
                return True
        except requests.exceptions.RequestException as e:
            pass
        
        print("⏳ Waiting for API to be ready...")
        time.sleep(2)
    
    print("❌ API is not responding after {timeout} seconds")
    return False


def install_test_dependencies():
    """Install test dependencies if they're not already installed."""
    print("Installing test dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "test-requirements.txt"
        ], check=True, cwd=Path(__file__).parent)
        print("✅ Test dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install test dependencies: {e}")
        return False


def run_tests(test_type="all", verbose=False, coverage=False):
    """Run the specified test suite."""
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    
    # Select test type
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "slow":
        cmd.extend(["-m", "slow"])
    elif test_type == "fast":
        cmd.extend(["-m", "not slow"])
    elif test_type == "all":
        pass  # Run all tests
    else:
        cmd.append(f"tests/test_{test_type}.py")
    
    print(f"Running tests: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run mem0 API tests")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "slow", "fast", "health", "memory_api", "error_handling"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Run tests in verbose mode"
    )
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Skip installation of test dependencies"
    )
    parser.add_argument(
        "--skip-health-check",
        action="store_true", 
        help="Skip API health check"
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="Base URL for the API (default: http://localhost:8000)"
    )
    
    args = parser.parse_args()
    
    print("🚀 Mem0 API Test Runner")
    print("=" * 50)
    
    # Install dependencies
    if not args.skip_install:
        if not install_test_dependencies():
            sys.exit(1)
        print()
    
    # Check API health
    if not args.skip_health_check:
        if not check_api_health(args.api_url):
            print("💡 Make sure the API is running with: docker-compose up -d")
            sys.exit(1)
        print()
    
    # Run tests
    print(f"Running {args.type} tests...")
    success = run_tests(
        test_type=args.type,
        verbose=args.verbose,
        coverage=args.coverage
    )
    
    if success:
        print("\n✅ All tests passed!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()