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
    
    def test_upload_cv(self, cv_path):
        """Test CV upload functionality"""
        try:
            with open(cv_path, 'rb') as f:
                files = {'file': ('test_cv.pdf', f, 'application/pdf')}
                success, response = self.run_test(
                    "CV Upload",
                    "POST",
                    "upload-cv",
                    200,
                    files=files
                )
                if success and 'cv_id' in response:
                    self.cv_id = response['cv_id']
                    print(f"CV ID: {self.cv_id}")
                    print(f"Skills detected: {response['analysis']['skills']}")
                return success
        except Exception as e:
            print(f"❌ Failed to upload CV: {str(e)}")
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
    
    def test_apply_to_job(self):
        """Test job application functionality"""
        if not self.job_id:
            print("❌ No job ID available for application test")
            return False
            
        success, response = self.run_test(
            "Job Application",
            "POST",
            f"apply-job/{self.job_id}",
            200,
            data={}
        )
        
        if success and 'application_id' in response:
            self.application_id = response['application_id']
            print(f"Application ID: {self.application_id}")
            print(f"Cover letter generated successfully")
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
    
    def create_sample_pdf(self):
        """Create a sample PDF for testing"""
        try:
            import fpdf
            
            pdf = fpdf.FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            pdf.cell(200, 10, txt="John Doe", ln=True, align='C')
            pdf.cell(200, 10, txt="Python Developer", ln=True, align='C')
            pdf.cell(200, 10, txt="john.doe@example.com | (123) 456-7890", ln=True, align='C')
            
            pdf.ln(10)
            pdf.cell(200, 10, txt="SKILLS", ln=True)
            pdf.cell(200, 10, txt="Python, JavaScript, React, FastAPI, MongoDB, SQL, Docker", ln=True)
            
            pdf.ln(10)
            pdf.cell(200, 10, txt="EXPERIENCE", ln=True)
            pdf.cell(200, 10, txt="Senior Python Developer - ABC Tech (2020-2023)", ln=True)
            pdf.cell(200, 10, txt="Full Stack Developer - XYZ Solutions (2018-2020)", ln=True)
            
            pdf.ln(10)
            pdf.cell(200, 10, txt="EDUCATION", ln=True)
            pdf.cell(200, 10, txt="Bachelor of Computer Science - University of Technology (2018)", ln=True)
            
            file_path = "/tmp/test_cv.pdf"
            pdf.output(file_path)
            print(f"✅ Created sample CV at {file_path}")
            return file_path
        except Exception as e:
            print(f"❌ Failed to create sample PDF: {str(e)}")
            return None

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
    
    # Create sample CV and test upload
    try:
        import fpdf
    except ImportError:
        print("Installing required packages...")
        os.system("pip install fpdf")
    
    cv_path = tester.create_sample_pdf()
    if not cv_path or not tester.test_upload_cv(cv_path):
        print("❌ CV upload failed, stopping tests")
        return 1
    
    # Test job search
    if not tester.test_search_jobs():
        print("❌ Job search failed, stopping tests")
        return 1
    
    # Test job application
    if not tester.test_apply_to_job():
        print("❌ Job application failed, stopping tests")
        return 1
    
    # Test getting applications
    tester.test_get_applications()
    
    # Test getting jobs
    tester.test_get_jobs()
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
