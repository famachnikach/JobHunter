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
    
    def test_upload_cv(self):
        """Test CV upload functionality with a test CV file"""
        # Create a test CV file if it doesn't exist
        test_cv_path = "/app/test_cv.txt"
        if not os.path.exists(test_cv_path):
            with open(test_cv_path, "w") as f:
                f.write("""John Doe
Software Developer
john.doe@example.com

SKILLS
Python, JavaScript, React, FastAPI, MongoDB, Docker, AWS

EXPERIENCE
Senior Software Developer at TechCorp (2020-2023)
- Developed and maintained web applications using React and Node.js
- Implemented CI/CD pipelines using GitHub Actions

Software Engineer at StartupXYZ (2018-2020)
- Built RESTful APIs using Python and FastAPI
- Worked with MongoDB and PostgreSQL databases

EDUCATION
Bachelor of Computer Science, University of Technology (2018)
""")
        
        # Convert text file to PDF-like bytes for testing
        with open(test_cv_path, "rb") as f:
            test_cv_content = f.read()
        
        # Create a mock PDF file for testing
        files = {
            'file': ('test_cv.pdf', test_cv_content, 'application/pdf')
        }
        
        success, response = self.run_test(
            "CV Upload",
            "POST",
            "upload-cv",
            200,
            files=files
        )
        
        if success and 'cv_id' in response:
            self.cv_id = response['cv_id']
            print(f"CV uploaded successfully with ID: {self.cv_id}")
            print(f"Skills extracted: {response.get('analysis', {}).get('skills', [])}")
            return True
        return False
    
    def test_search_jobs(self):
        """Test job search functionality"""
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
            if not self.job_id and response.get('jobs') and len(response['jobs']) > 0:
                self.job_id = response['jobs'][0]['id']
                print(f"Selected job ID: {self.job_id}")
            return True
        return False
    
    def test_apply_to_job(self):
        """Test applying to a job"""
        if not self.job_id:
            print("❌ No job ID available for application test")
            return False
        
        success, response = self.run_test(
            "Apply to Job",
            "POST",
            f"apply-job/{self.job_id}",
            200
        )
        
        if success and 'application_id' in response:
            self.application_id = response['application_id']
            print(f"Applied to job successfully with application ID: {self.application_id}")
            print(f"Cover letter generated with {len(response.get('cover_letter', ''))} characters")
            return True
        return False
    
    def test_get_applications(self):
        """Test retrieving applications"""
        success, response = self.run_test(
            "Get Applications",
            "GET",
            "applications",
            200
        )
        
        if success and 'applications' in response:
            print(f"Retrieved {len(response['applications'])} applications")
            return True
        return False
    
    def test_auto_apply(self):
        """Test auto-apply functionality"""
        success, response = self.run_test(
            "Auto Apply",
            "POST",
            "auto-apply?min_match_score=50&max_applications=3",
            200
        )
        
        if success:
            print(f"Auto-apply result: {response.get('message', 'No message')}")
            return True
        return False

def main():
    # Get the backend URL from frontend/.env
    backend_url = "https://c7b12ba2-6d55-4b37-8b6d-8bddb20c2307.preview.emergentagent.com"
    
    print(f"🚀 Testing LinkedIn Job Bot API at {backend_url}")
    
    # Setup tester
    tester = LinkedInJobBotTester(backend_url)
    
    # Test health check
    if not tester.test_health_check():
        print("❌ Health check failed, stopping tests")
        return 1
    
    # Test CV upload
    tester.test_upload_cv()
    
    # Test job search
    tester.test_search_jobs()
    
    # Test getting jobs
    tester.test_get_jobs()
    
    # Test applying to a job
    tester.test_apply_to_job()
    
    # Test getting applications
    tester.test_get_applications()
    
    # Test auto-apply
    tester.test_auto_apply()
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())