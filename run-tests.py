#!/usr/bin/env python3
"""
Cross-platform test runner for master-dashboard-template
Works on Windows, macOS, and Linux
"""

import sys
import subprocess
import os
from pathlib import Path


# ANSI color codes (work on most terminals, including Windows 10+)
class Colors:
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'  # No Color
    
    @staticmethod
    def disable():
        """Disable colors on Windows if needed."""
        if os.name == 'nt' and not os.environ.get('TERM'):
            Colors.GREEN = ''
            Colors.BLUE = ''
            Colors.YELLOW = ''
            Colors.RED = ''
            Colors.NC = ''


def print_header():
    """Print test suite header."""
    print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.BLUE}║                                                            ║{Colors.NC}")
    print(f"{Colors.BLUE}║          MASTER DASHBOARD TEMPLATE - TEST SUITE            ║{Colors.NC}")
    print(f"{Colors.BLUE}║                                                            ║{Colors.NC}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════════╝{Colors.NC}")
    print()


def check_directory():
    """Check if we're in the correct directory."""
    if not Path('backend/main.py').exists():
        print(f"{Colors.RED}Error: Please run this script from the master-dashboard-template directory{Colors.NC}")
        sys.exit(1)


def ensure_pytest_installed():
    """Ensure pytest is installed."""
    try:
        import pytest
    except ImportError:
        print(f"{Colors.YELLOW}Installing test dependencies...{Colors.NC}")
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 
            '-r', 'tests/requirements-test.txt'
        ])


def run_pytest(args):
    """Run pytest with given arguments."""
    cmd = [sys.executable, '-m', 'pytest'] + args
    return subprocess.call(cmd)


def print_results(exit_code):
    """Print test results."""
    print()
    
    if exit_code == 0:
        print(f"{Colors.GREEN}╔════════════════════════════════════════════════════════════╗{Colors.NC}")
        print(f"{Colors.GREEN}║                  ALL TESTS PASSED! ✓                       ║{Colors.NC}")
        print(f"{Colors.GREEN}╚════════════════════════════════════════════════════════════╝{Colors.NC}")
    else:
        print(f"{Colors.RED}╔════════════════════════════════════════════════════════════╗{Colors.NC}")
        print(f"{Colors.RED}║                  SOME TESTS FAILED ✗                       ║{Colors.NC}")
        print(f"{Colors.RED}╚════════════════════════════════════════════════════════════╝{Colors.NC}")


def print_usage():
    """Print usage information."""
    print()
    print("Test categories:")
    print("  python run-tests.py unit         # Fast unit tests only")
    print("  python run-tests.py integration  # Integration tests only")
    print("  python run-tests.py api          # API endpoint tests only")
    print("  python run-tests.py fast         # Unit + API tests")
    print("  python run-tests.py coverage     # All tests with coverage")
    print("  python run-tests.py all          # All tests (default)")


def main():
    """Main test runner."""
    # Enable colors on Windows 10+
    if os.name == 'nt':
        os.system('')  # Enable ANSI codes on Windows
    
    Colors.disable() if os.name == 'nt' and not os.environ.get('TERM') else None
    
    print_header()
    
    # Check we're in the right place
    check_directory()
    
    # Ensure pytest is installed
    ensure_pytest_installed()
    
    # Get test type from command line
    test_type = sys.argv[1] if len(sys.argv) > 1 else 'all'
    
    print(f"{Colors.BLUE}Running tests...{Colors.NC}")
    print()
    
    # Build pytest arguments based on test type
    pytest_args = ['tests/', '-v']
    
    if test_type == 'unit':
        print(f"{Colors.BLUE}Running unit tests only...{Colors.NC}")
        pytest_args.extend(['-m', 'unit'])
    
    elif test_type == 'integration':
        print(f"{Colors.BLUE}Running integration tests only...{Colors.NC}")
        pytest_args.extend(['-m', 'integration'])
    
    elif test_type == 'api':
        print(f"{Colors.BLUE}Running API tests only...{Colors.NC}")
        pytest_args.extend(['-m', 'api'])
    
    elif test_type == 'fast':
        print(f"{Colors.BLUE}Running fast tests only (unit + api)...{Colors.NC}")
        pytest_args.extend(['-m', 'unit or api'])
    
    elif test_type == 'coverage':
        print(f"{Colors.BLUE}Running all tests with coverage report...{Colors.NC}")
        pytest_args.extend(['--cov', '--cov-report=term-missing', '--cov-report=html'])
    
    elif test_type == 'all' or test_type == '':
        print(f"{Colors.BLUE}Running all tests...{Colors.NC}")
    
    else:
        print(f"{Colors.RED}Unknown test type: {test_type}{Colors.NC}")
        print_usage()
        sys.exit(1)
    
    # Run pytest
    exit_code = run_pytest(pytest_args)
    
    # Print results
    print_results(exit_code)
    print_usage()
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()