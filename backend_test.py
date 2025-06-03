import requests
import os
import sys
import time
import json
from datetime import datetime

class LinkedInJobBotTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.cv_id = None
        self.job_id = None
        self.application_id = None
        
    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'} if not files else {}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files)
                else:
                    response = requests.post(url, json=data, headers=headers)
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.text}")
                    return False, response.json()
                except:
                    return False, {}
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}
    
    def test_health_check(self):
        """Test the health check endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "health",
            200
        )
        return success
    
    def test_search_jobs(self):
        """Test job search functionality without CV upload"""
        data = {
            "keywords": "Python Developer",
            "location": "Remote",
            "experience_level": "mid-level",
            "max_results": 10
        }
        
        success, response = self.run_test(
            "Job Search",
            "POST",
            "search-jobs",
            200,
            data=data
        )
        
        if success and 'jobs' in response and len(response['jobs']) > 0:
            self.job_id = response['jobs'][0]['id']
            print(f"Found {len(response['jobs'])} jobs")
            print(f"First job ID: {self.job_id}")
            return True
        return False
    
    def test_get_jobs(self):
        """Test retrieving jobs"""
        success, response = self.run_test(
            "Get Jobs",
            "GET",
            "jobs",
            200
        )
        
        if success and 'jobs' in response:
            print(f"Retrieved {len(response['jobs'])} jobs")
            return True
        return False

def main():
    # Get the backend URL from environment or use the one from frontend/.env
    backend_url = "https://c7b12ba2-6d55-4b37-8b6d-8bddb20c2307.preview.emergentagent.com"
    
    print(f"🚀 Testing LinkedIn Job Bot API at {backend_url}")
    
    # Setup tester
    tester = LinkedInJobBotTester(backend_url)
    
    # Test health check
    if not tester.test_health_check():
        print("❌ Health check failed, stopping tests")
        return 1
    
    # Test job search (this might fail if CV upload is required)
    tester.test_search_jobs()
    
    # Test getting jobs
    tester.test_get_jobs()
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())