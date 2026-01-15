"""
Module 5 Authentication & RBAC Testing Script
Tests all user roles and access permissions
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_header(text):
    print(f"\n{'='*70}")
    print(f"{text.center(70)}")
    print(f"{'='*70}")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

print_header("MODULE 5: AUTHENTICATION & RBAC TESTING")
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Test users - CORRECTED usernames
users = [
    {"username": "finance_user", "password": "finance123", "role": "Finance"},
    {"username": "marketing_user", "password": "marketing123", "role": "Marketing"},
    {"username": "hr_user", "password": "hr123", "role": "HR"},
    {"username": "engineering_user", "password": "engineering123", "role": "Engineering"},
    {"username": "employee_user", "password": "employee123", "role": "Employees"},
    {"username": "clevel_user", "password": "clevel123", "role": "C-Level"},
]

# Check if server is running
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    if response.status_code == 200:
        print_success("Server is running at http://localhost:8000")
    else:
        print_error("Server returned unexpected status")
        exit(1)
except Exception as e:
    print_error("Cannot connect to server. Make sure it's running!")
    print_error(f"Error: {str(e)}")
    exit(1)

print()

# Test each user
total_tests = 0
passed_tests = 0

for user in users:
    print_header(f"Testing: {user['username']} ({user['role']})")
    
    # Test 1: Login
    total_tests += 1
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": user["username"], "password": user["password"]},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            print_success(f"Login successful")
            print(f"   Role: {data['role']}")
            print(f"   Token: {token[:40]}...")
            passed_tests += 1
            
            # Test accessing different endpoints
            headers = {"Authorization": f"Bearer {token}"}
            
            # Define expected access for each role
            access_matrix = {
                "Finance": {
                    "/api/finance/reports": 200,
                    "/api/marketing/campaigns": 403,
                    "/api/hr/employees": 403,
                    "/api/query": 200,
                },
                "Marketing": {
                    "/api/finance/reports": 403,
                    "/api/marketing/campaigns": 200,
                    "/api/hr/employees": 403,
                    "/api/query": 200,
                },
                "HR": {
                    "/api/finance/reports": 403,
                    "/api/marketing/campaigns": 403,
                    "/api/hr/employees": 200,
                    "/api/query": 200,
                },
                "Engineering": {
                    "/api/finance/reports": 403,
                    "/api/marketing/campaigns": 403,
                    "/api/hr/employees": 403,
                    "/api/query": 200,
                },
                "Employees": {
                    "/api/finance/reports": 403,
                    "/api/marketing/campaigns": 403,
                    "/api/hr/employees": 403,
                    "/api/query": 200,
                },
                "C-Level": {
                    "/api/finance/reports": 200,
                    "/api/marketing/campaigns": 200,
                    "/api/hr/employees": 200,
                    "/api/query": 200,
                    "/api/audit/logs": 200,
                },
            }
            
            expected = access_matrix.get(user['role'], {})
            
            print("\n   Testing endpoint access:")
            for endpoint, expected_status in expected.items():
                total_tests += 1
                try:
                    resp = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
                    
                    if resp.status_code == expected_status:
                        if resp.status_code == 200:
                            print(f"   ✅ {endpoint} - Accessible (200)")
                        else:
                            print(f"   ✅ {endpoint} - Correctly blocked (403)")
                        passed_tests += 1
                    else:
                        print(f"   ❌ {endpoint} - Got {resp.status_code}, expected {expected_status}")
                except Exception as e:
                    print(f"   ❌ {endpoint} - Error: {str(e)}")
            
            # Test POST /api/query
            total_tests += 1
            try:
                resp = requests.post(
                    f"{BASE_URL}/api/query",
                    headers=headers,
                    json={"query": "Test query from automated script"},
                    timeout=10
                )
                if resp.status_code == 200:
                    print(f"   ✅ POST /api/query - Works correctly")
                    passed_tests += 1
                else:
                    print(f"   ❌ POST /api/query - Failed ({resp.status_code})")
            except Exception as e:
                print(f"   ❌ POST /api/query - Error: {str(e)}")
                
        else:
            print_error(f"Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print_error(f"Login error: {str(e)}")

# Test invalid credentials
print_header("Testing Invalid Credentials")
total_tests += 1
try:
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "invalid_user", "password": "wrong_password"},
        timeout=10
    )
    
    if response.status_code == 401:
        print_success("Invalid credentials correctly rejected (401)")
        passed_tests += 1
    else:
        print_error(f"Invalid credentials not rejected properly ({response.status_code})")
except Exception as e:
    print_error(f"Error: {str(e)}")

# Test unauthenticated access
print_header("Testing Unauthenticated Access")
total_tests += 1
try:
    response = requests.get(f"{BASE_URL}/api/finance/reports", timeout=10)
    
    if response.status_code == 401:
        print_success("Unauthenticated access blocked (401)")
        passed_tests += 1
    else:
        print_error(f"Unauthenticated access not blocked ({response.status_code})")
except Exception as e:
    print_error(f"Error: {str(e)}")

# Final summary
print_header("TEST SUMMARY")
print(f"Total Tests: {total_tests}")
print(f"Passed: {passed_tests}")
print(f"Failed: {total_tests - passed_tests}")
print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

if passed_tests == total_tests:
    print("\n" + "="*70)
    print_success("ALL TESTS PASSED! MODULE 5 COMPLETE!")
    print("="*70)
    print("\n✨ Ready to proceed to Module 6: RAG Pipeline & LLM Integration")
else:
    print("\n" + "="*70)
    print_warning(f"Some tests failed. Please review the errors above.")
    print("="*70)

print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")