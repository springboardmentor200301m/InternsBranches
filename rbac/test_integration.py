"""
Module 8: Comprehensive Integration Testing
Tests complete workflow for all user roles
"""

import requests
import time
from datetime import datetime
from typing import Dict, List

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_info(text: str):
    print(f"{Colors.YELLOW}ℹ️  {text}{Colors.RESET}")

class IntegrationTester:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []
    
    def test_api_health(self) -> bool:
        """Test if API is running"""
        print_header("Testing API Health")
        self.total_tests += 1
        
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print_success("API is running")
                print_info(f"Status: {data.get('status')}")
                print_info(f"RAG Status: {data.get('rag_status')}")
                self.passed_tests += 1
                self.test_results.append({"test": "API Health", "status": "PASS"})
                return True
            else:
                print_error(f"API returned status {response.status_code}")
                self.failed_tests += 1
                self.test_results.append({"test": "API Health", "status": "FAIL"})
                return False
        except Exception as e:
            print_error(f"Cannot connect to API: {e}")
            self.failed_tests += 1
            self.test_results.append({"test": "API Health", "status": "FAIL"})
            return False
    
    def test_complete_workflow(self, username: str, password: str, role: str):
        """Test complete workflow for a specific user"""
        print_header(f"Testing Complete Workflow: {role}")
        
        # Test 1: Login
        print_info(f"Test 1: Login as {username}")
        self.total_tests += 1
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"username": username, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data['access_token']
                print_success(f"Login successful - Role: {data['role']}")
                self.passed_tests += 1
                self.test_results.append({"test": f"{role} Login", "status": "PASS"})
            else:
                print_error(f"Login failed: {response.status_code}")
                self.failed_tests += 1
                self.test_results.append({"test": f"{role} Login", "status": "FAIL"})
                return
        except Exception as e:
            print_error(f"Login error: {e}")
            self.failed_tests += 1
            self.test_results.append({"test": f"{role} Login", "status": "FAIL"})
            return
        
        # Test 2: Get user info
        print_info("Test 2: Get user information")
        self.total_tests += 1
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"User info retrieved - {data['username']} ({data['role']})")
                self.passed_tests += 1
                self.test_results.append({"test": f"{role} User Info", "status": "PASS"})
            else:
                print_error(f"Failed to get user info: {response.status_code}")
                self.failed_tests += 1
                self.test_results.append({"test": f"{role} User Info", "status": "FAIL"})
        except Exception as e:
            print_error(f"User info error: {e}")
            self.failed_tests += 1
            self.test_results.append({"test": f"{role} User Info", "status": "FAIL"})
        
        # Test 3: Query with RAG
        print_info("Test 3: RAG-powered query")
        self.total_tests += 1
        
        query_map = {
            "Finance": "What are the Q3 financial results?",
            "Marketing": "What marketing campaigns are running?",
            "HR": "What are the employee benefits?",
            "Engineering": "What is our system architecture?",
            "Employees": "What is the work from home policy?",
            "C-Level": "Give me an overview of company performance"
        }
        
        query = query_map.get(role, "What information is available?")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/api/query",
                json={"query": query},
                headers=headers,
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                response_time = (end_time - start_time) * 1000
                print_success(f"Query successful - Response time: {response_time:.0f}ms")
                print_info(f"Response length: {len(data['response'])} characters")
                print_info(f"Sources used: {len(data.get('sources', []))}")
                print_info(f"Context used: {data.get('context_used', False)}")
                
                if response_time < 3000:
                    print_success("Performance: Response time under 3 seconds ✅")
                else:
                    print_error("Performance: Response time exceeded 3 seconds")
                
                self.passed_tests += 1
                self.test_results.append({"test": f"{role} RAG Query", "status": "PASS"})
            else:
                print_error(f"Query failed: {response.status_code}")
                self.failed_tests += 1
                self.test_results.append({"test": f"{role} RAG Query", "status": "FAIL"})
        except Exception as e:
            print_error(f"Query error: {e}")
            self.failed_tests += 1
            self.test_results.append({"test": f"{role} RAG Query", "status": "FAIL"})
        
        # Test 4: Role-based access control
        print_info("Test 4: Testing role-based access control")
        
        # Test accessing endpoints user should NOT have access to
        forbidden_tests = {
            "Finance": ["/api/marketing/campaigns", "/api/hr/employees"],
            "Marketing": ["/api/finance/reports", "/api/hr/employees"],
            "HR": ["/api/finance/reports", "/api/marketing/campaigns"],
            "Engineering": ["/api/finance/reports", "/api/hr/employees"],
            "Employees": ["/api/finance/reports", "/api/marketing/campaigns", "/api/hr/employees"],
        }
        
        if role in forbidden_tests:
            for endpoint in forbidden_tests[role]:
                self.total_tests += 1
                try:
                    response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
                    
                    if response.status_code == 403:
                        print_success(f"Access correctly denied to {endpoint}")
                        self.passed_tests += 1
                        self.test_results.append({"test": f"{role} Access Control {endpoint}", "status": "PASS"})
                    else:
                        print_error(f"Access control failed for {endpoint} - got {response.status_code}")
                        self.failed_tests += 1
                        self.test_results.append({"test": f"{role} Access Control {endpoint}", "status": "FAIL"})
                except Exception as e:
                    print_error(f"Access control test error: {e}")
                    self.failed_tests += 1
                    self.test_results.append({"test": f"{role} Access Control {endpoint}", "status": "FAIL"})
        
        print()
    
    def test_security_features(self):
        """Test security-related features"""
        print_header("Testing Security Features")
        
        # Test 1: Invalid credentials
        print_info("Test 1: Invalid credentials rejection")
        self.total_tests += 1
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"username": "invalid_user", "password": "wrong_password"},
                timeout=10
            )
            
            if response.status_code == 401:
                print_success("Invalid credentials correctly rejected")
                self.passed_tests += 1
                self.test_results.append({"test": "Invalid Credentials", "status": "PASS"})
            else:
                print_error(f"Security issue: Invalid credentials accepted")
                self.failed_tests += 1
                self.test_results.append({"test": "Invalid Credentials", "status": "FAIL"})
        except Exception as e:
            print_error(f"Error testing invalid credentials: {e}")
            self.failed_tests += 1
            self.test_results.append({"test": "Invalid Credentials", "status": "FAIL"})
        
        # Test 2: Unauthenticated access
        print_info("Test 2: Unauthenticated access blocking")
        self.total_tests += 1
        
        try:
            response = requests.get(f"{BASE_URL}/api/finance/reports", timeout=10)
            
            if response.status_code == 401:
                print_success("Unauthenticated access correctly blocked")
                self.passed_tests += 1
                self.test_results.append({"test": "Unauthenticated Access", "status": "PASS"})
            else:
                print_error(f"Security issue: Unauthenticated access allowed")
                self.failed_tests += 1
                self.test_results.append({"test": "Unauthenticated Access", "status": "FAIL"})
        except Exception as e:
            print_error(f"Error testing unauthenticated access: {e}")
            self.failed_tests += 1
            self.test_results.append({"test": "Unauthenticated Access", "status": "FAIL"})
        
        # Test 3: Invalid token
        print_info("Test 3: Invalid token rejection")
        self.total_tests += 1
        
        try:
            headers = {"Authorization": "Bearer invalid_token_12345"}
            response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers, timeout=10)
            
            if response.status_code == 401:
                print_success("Invalid token correctly rejected")
                self.passed_tests += 1
                self.test_results.append({"test": "Invalid Token", "status": "PASS"})
            else:
                print_error(f"Security issue: Invalid token accepted")
                self.failed_tests += 1
                self.test_results.append({"test": "Invalid Token", "status": "FAIL"})
        except Exception as e:
            print_error(f"Error testing invalid token: {e}")
            self.failed_tests += 1
            self.test_results.append({"test": "Invalid Token", "status": "FAIL"})
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print_header("TEST REPORT")
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {Colors.GREEN}{self.passed_tests}{Colors.RESET}")
        print(f"Failed: {Colors.RED}{self.failed_tests}{Colors.RESET}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        print(f"\n{Colors.BOLD}Detailed Results:{Colors.RESET}")
        print("-" * 70)
        
        for result in self.test_results:
            status_color = Colors.GREEN if result['status'] == 'PASS' else Colors.RED
            print(f"{result['test']:50} {status_color}{result['status']}{Colors.RESET}")
        
        print("=" * 70)
        
        if self.failed_tests == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! SYSTEM READY FOR DEPLOYMENT!{Colors.RESET}")
        else:
            print(f"\n{Colors.YELLOW}⚠️  Some tests failed. Please review errors above.{Colors.RESET}")
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"test_report_{timestamp}.txt", "w") as f:
            f.write("="*70 + "\n")
            f.write("INTEGRATION TEST REPORT\n")
            f.write("="*70 + "\n\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Tests: {self.total_tests}\n")
            f.write(f"Passed: {self.passed_tests}\n")
            f.write(f"Failed: {self.failed_tests}\n")
            f.write(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%\n\n")
            f.write("Detailed Results:\n")
            f.write("-"*70 + "\n")
            for result in self.test_results:
                f.write(f"{result['test']:50} {result['status']}\n")
        
        print(f"\n📄 Report saved to: test_report_{timestamp}.txt")

def main():
    print(f"\n{Colors.BOLD}Module 8: Comprehensive Integration Testing{Colors.RESET}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    tester = IntegrationTester()
    
    # Test 1: API Health
    if not tester.test_api_health():
        print_error("API is not running. Please start the server first.")
        print_info("Run: python main.py")
        return
    
    # Test 2: Complete workflows for each role
    test_users = [
        ("finance_user", "finance123", "Finance"),
        ("marketing_user", "marketing123", "Marketing"),
        ("hr_user", "hr123", "HR"),
        ("employee_user", "employee123", "Employees"),
    ]
    
    for username, password, role in test_users:
        tester.test_complete_workflow(username, password, role)
    
    # Test 3: Security features
    tester.test_security_features()
    
    # Generate final report
    tester.generate_report()
    
    print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()