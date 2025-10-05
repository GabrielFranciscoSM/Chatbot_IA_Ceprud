#!/usr/bin/env python3
"""
Phase 4 Implementation Test Script

Tests the frontend LTI integration components.
"""

import os
import sys
from pathlib import Path

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_status(status: bool, message: str):
    """Print status with color"""
    icon = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
    print(f"  {icon} {message}")

def test_file_exists(filepath: str, description: str) -> bool:
    """Test if a file exists"""
    exists = os.path.exists(filepath)
    print_status(exists, f"{description}: {filepath}")
    return exists

def test_file_contains(filepath: str, search_text: str, description: str) -> bool:
    """Test if a file contains specific text"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            found = search_text in content
            print_status(found, description)
            return found
    except Exception as e:
        print_status(False, f"{description} (Error: {e})")
        return False

def main():
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Phase 4 Frontend LTI Integration - Implementation Test{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    frontend_dir = Path(__file__).parent.parent / "frontend" / "src"
    app_dir = Path(__file__).parent.parent / "app"
    
    results = []
    
    # Test 1: New Files Created
    print(f"\n{YELLOW}TEST 1: New Files Created{RESET}")
    results.append(test_file_exists(
        str(frontend_dir / "types" / "session.ts"),
        "Session types"
    ))
    results.append(test_file_exists(
        str(frontend_dir / "contexts" / "SessionContext.tsx"),
        "SessionContext provider"
    ))
    results.append(test_file_exists(
        str(frontend_dir / "hooks" / "useSession.ts"),
        "useSession hook"
    ))
    results.append(test_file_exists(
        str(frontend_dir / "styles" / "lti.css"),
        "LTI styles"
    ))
    
    # Test 2: Frontend Modifications
    print(f"\n{YELLOW}TEST 2: Frontend Modifications{RESET}")
    results.append(test_file_contains(
        str(frontend_dir / "main.tsx"),
        "SessionProvider",
        "main.tsx imports SessionProvider"
    ))
    results.append(test_file_contains(
        str(frontend_dir / "main.tsx"),
        "import './styles/lti.css'",
        "main.tsx imports LTI styles"
    ))
    results.append(test_file_contains(
        str(frontend_dir / "App.tsx"),
        "useSession",
        "App.tsx uses useSession hook"
    ))
    results.append(test_file_contains(
        str(frontend_dir / "App.tsx"),
        "session.isLTI",
        "App.tsx checks for LTI mode"
    ))
    results.append(test_file_contains(
        str(frontend_dir / "App.tsx"),
        "lti-mode",
        "App.tsx applies LTI mode class"
    ))
    results.append(test_file_contains(
        str(frontend_dir / "App.tsx"),
        "context-banner",
        "App.tsx renders context banner"
    ))
    
    # Test 3: API Client Updates
    print(f"\n{YELLOW}TEST 3: API Client Updates{RESET}")
    results.append(test_file_contains(
        str(frontend_dir / "api.ts"),
        "X-Session-Token",
        "api.ts adds session token header"
    ))
    results.append(test_file_contains(
        str(frontend_dir / "api.ts"),
        "validateSession",
        "api.ts has validateSession method"
    ))
    results.append(test_file_contains(
        str(frontend_dir / "api.ts"),
        "localStorage.getItem('session_token')",
        "api.ts reads session token from localStorage"
    ))
    
    # Test 4: Backend Session Validation
    print(f"\n{YELLOW}TEST 4: Backend Session Validation{RESET}")
    results.append(test_file_contains(
        str(app_dir / "api_router.py"),
        "/session/validate",
        "api_router.py has session validation endpoint"
    ))
    results.append(test_file_contains(
        str(app_dir / "api_router.py"),
        "X-Session-Token",
        "api_router.py accepts session token header"
    ))
    results.append(test_file_contains(
        str(app_dir / "api_router.py"),
        "LTISessionService",
        "api_router.py uses LTISessionService"
    ))
    results.append(test_file_contains(
        str(app_dir / "app.py"),
        "expose_headers",
        "app.py exposes custom headers in CORS"
    ))
    
    # Test 5: SessionContext Features
    print(f"\n{YELLOW}TEST 5: SessionContext Features{RESET}")
    session_context_path = str(frontend_dir / "contexts" / "SessionContext.tsx")
    results.append(test_file_contains(
        session_context_path,
        "parseURLParameters",
        "SessionContext parses URL parameters"
    ))
    results.append(test_file_contains(
        session_context_path,
        "validateSession",
        "SessionContext validates session"
    ))
    results.append(test_file_contains(
        session_context_path,
        "localStorage.setItem('session_token'",
        "SessionContext stores token in localStorage"
    ))
    results.append(test_file_contains(
        session_context_path,
        "chatApi.validateSession",
        "SessionContext calls API validation"
    ))
    
    # Test 6: LTI Styles
    print(f"\n{YELLOW}TEST 6: LTI Styles{RESET}")
    lti_css_path = str(frontend_dir / "styles" / "lti.css")
    results.append(test_file_contains(
        lti_css_path,
        ".lti-mode",
        "LTI mode base class defined"
    ))
    results.append(test_file_contains(
        lti_css_path,
        ".context-banner",
        "Context banner styles defined"
    ))
    results.append(test_file_contains(
        lti_css_path,
        ".lti-loading",
        "Loading state styles defined"
    ))
    results.append(test_file_contains(
        lti_css_path,
        ".lti-error",
        "Error state styles defined"
    ))
    
    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"\n{YELLOW}RESULTS:{RESET}")
    print(f"  Total Tests: {total}")
    print(f"  {GREEN}Passed: {passed}{RESET}")
    print(f"  {RED}Failed: {failed}{RESET}")
    print(f"  Success Rate: {(passed/total*100):.1f}%")
    
    if passed == total:
        print(f"\n{GREEN}✓ ALL TESTS PASSED! Phase 4 implementation complete.{RESET}")
        print(f"\n{YELLOW}Next Steps:{RESET}")
        print(f"  1. Build and test frontend: cd frontend && npm run build")
        print(f"  2. Start backend: cd app && python -m uvicorn app:app --reload")
        print(f"  3. Test locally with: http://localhost:5173/?session_token=TEST&lti=true&subject=test")
        print(f"  4. Register in Moodle Cloud and test real LTI launch")
        return 0
    else:
        print(f"\n{RED}✗ Some tests failed. Please review the implementation.{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
