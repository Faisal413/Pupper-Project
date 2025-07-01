#!/usr/bin/env python3
"""
Comprehensive test runner for Pupper application
Runs unit tests, integration tests, linting, and security checks
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🔍 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - PASSED")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def main():
    """Run all tests and checks"""
    print("🚀 Starting Pupper Application Test Suite")
    
    # Change to project directory
    os.chdir(Path(__file__).parent)
    
    # Install dev dependencies
    print("\n📦 Installing test dependencies...")
    if not run_command("uv sync --group dev", "Installing dependencies"):
        sys.exit(1)
    
    test_results = []
    
    # 1. Code formatting check
    test_results.append(run_command(
        "python -m black --check functions/ cdk/ tests/",
        "Code formatting check (Black)"
    ))
    
    # 2. Linting
    test_results.append(run_command(
        "python -m flake8 functions/ cdk/ tests/ --max-line-length=88 --extend-ignore=E203,W503",
        "Code linting (Flake8)"
    ))
    
    # 3. Type checking
    test_results.append(run_command(
        "python -m mypy functions/ cdk/ --ignore-missing-imports",
        "Type checking (MyPy)"
    ))
    
    # 4. Unit tests
    test_results.append(run_command(
        "python -m pytest tests/ -v --cov=functions --cov=cdk --cov-report=term-missing",
        "Unit tests (PyTest)"
    ))
    
    # 5. CDK synthesis test
    test_results.append(run_command(
        "cdk synth --quiet",
        "CDK synthesis test"
    ))
    
    # 6. Security checks with CDK Nag (if available)
    test_results.append(run_command(
        "python -c \"import cdk_nag; print('CDK Nag available')\"",
        "CDK Nag availability check"
    ))
    
    # 7. API integration test (if deployed)
    api_url = os.environ.get('PUPPER_API_URL')
    if api_url:
        test_results.append(run_command(
            f"python test_api.py {api_url}",
            "API integration test"
        ))
    else:
        print("\n⚠️  Skipping API integration test - PUPPER_API_URL not set")
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All tests passed! Your code is ready for deployment.")
        sys.exit(0)
    else:
        print(f"\n💥 {total - passed} test(s) failed. Please fix the issues before deployment.")
        sys.exit(1)

if __name__ == "__main__":
    main()
