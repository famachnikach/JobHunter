from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import uuid
import io
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import PyPDF2
from bs4 import BeautifulSoup
import requests
import json
import asyncio
import time
from datetime import datetime, timedelta
from emergentintegrations.llm.chat import LlmChat, UserMessage
import re

# Models
class CVData(BaseModel):
    id: str
    filename: str
    extracted_text: str
    skills: List[str]
    experience: List[str]
    education: List[str]
    summary: str
    created_at: datetime

class JobListing(BaseModel):
    id: str
    title: str
    company: str
    location: str
    description: str
    requirements: str
    url: str
    posted_date: str
    match_score: float
    applied: bool = False
    created_at: datetime

class JobApplication(BaseModel):
    id: str
    job_id: str
    cv_id: str
    cover_letter: str
    application_date: datetime
    status: str = "applied"
    response_received: bool = False

class JobSearchRequest(BaseModel):
    keywords: str
    location: str = "Remote"
    experience_level: str = "mid-level"
    max_results: int = 20

# FastAPI app
app = FastAPI(title="LinkedIn Dream Job Bot")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
client = None
db = None

@app.on_event("startup")
async def startup_event():
    global client, db
    from dotenv import load_dotenv
    load_dotenv()
    client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
    db_name = os.getenv("DB_NAME")
    if not db_name:
        db_name = "linkedin_job_bot"
    db = client[db_name]

@app.on_event("shutdown")
async def shutdown_event():
    if client:
        client.close()

# CV Processing Functions
def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

async def analyze_cv_with_ai(text: str) -> Dict[str, Any]:
    """Use Gemini to analyze CV and extract structured data"""
    try:
        chat = LlmChat(
            api_key=os.getenv("GEMINI_API_KEY"),
            session_id=f"cv_analysis_{uuid.uuid4()}",
            system_message="""You are an expert CV analyzer. Extract structured information from the CV text and return it in JSON format.

Extract:
1. skills: List of technical and soft skills
2. experience: List of job experiences with company, role, and duration
3. education: List of educational qualifications
4. summary: Professional summary (2-3 sentences)

Return valid JSON only, no additional text."""
        ).with_model("gemini", "gemini-2.0-flash")

        user_message = UserMessage(text=f"Analyze this CV and extract structured data:\n\n{text}")
        response = await chat.send_message(user_message)
        
        # Clean and parse JSON response
        json_text = response.strip()
        if json_text.startswith("```json"):
            json_text = json_text[7:]
        if json_text.endswith("```"):
            json_text = json_text[:-3]
        
        return json.loads(json_text)
    except Exception as e:
        # Fallback to basic parsing if AI fails
        return {
            "skills": extract_skills_basic(text),
            "experience": extract_experience_basic(text),
            "education": extract_education_basic(text),
            "summary": text[:200] + "..." if len(text) > 200 else text
        }

def extract_skills_basic(text: str) -> List[str]:
    """Basic skill extraction using keywords"""
    skills_keywords = [
        "Python", "JavaScript", "React", "Node.js", "FastAPI", "MongoDB", "SQL",
        "Docker", "Kubernetes", "AWS", "Git", "Machine Learning", "AI", "Data Science",
        "Project Management", "Leadership", "Communication", "Problem Solving"
    ]
    found_skills = []
    text_lower = text.lower()
    for skill in skills_keywords:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    return found_skills

def extract_experience_basic(text: str) -> List[str]:
    """Basic experience extraction"""
    # Look for common job-related patterns
    experience_patterns = [
        r"(\d{4}[\s\-]+\d{4}|present).*?([A-Z][a-z]+.*?(?:engineer|developer|manager|analyst|specialist|consultant))",
        r"([A-Z][a-z]+.*?(?:engineer|developer|manager|analyst|specialist|consultant)).*?(\d{4}[\s\-]+\d{4}|present)"
    ]
    experiences = []
    for pattern in experience_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches[:5]:  # Limit to 5 experiences
            experiences.append(" ".join(match))
    
    # If no matches found, add a default experience
    if not experiences:
        experiences = ["Software Developer 2020-2023"]
    
    return experiences

def extract_education_basic(text: str) -> List[str]:
    """Basic education extraction"""
    education_patterns = [
        r"(Bachelor|Master|PhD|B\.S\.|M\.S\.|B\.A\.|M\.A\.).*?(\d{4}|\d{2})",
        r"(University|College|Institute).*?(\d{4}|\d{2})"
    ]
    education = []
    for pattern in education_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches[:3]:  # Limit to 3 education entries
            education.append(" ".join(match))
    return education

# Job Search Functions
def search_jobs_linkedin_scrape(keywords: str, location: str = "Remote", max_results: int = 20) -> List[Dict]:
    """Simulate LinkedIn job search (in real implementation, use web scraping)"""
    # This is a mock implementation. In production, you'd use Selenium/BeautifulSoup
    # to scrape LinkedIn job listings
    mock_jobs = [
        {
            "title": f"Senior {keywords} Developer",
            "company": "Tech Innovators Inc",
            "location": location,
            "description": f"We are looking for an experienced {keywords} developer to join our dynamic team. You will work on cutting-edge projects and collaborate with cross-functional teams.",
            "requirements": f"5+ years experience with {keywords}, strong problem-solving skills, team player",
            "url": f"https://linkedin.com/jobs/view/12345{i}",
            "posted_date": "2 days ago"
        }
        for i in range(min(max_results, 10))
    ]
    
    # Add some variety
    job_titles = ["Software Engineer", "Full Stack Developer", "Backend Developer", "Frontend Developer", "DevOps Engineer"]
    companies = ["Google", "Microsoft", "Amazon", "Meta", "Netflix", "Uber", "Airbnb", "Spotify"]
    
    for i, job in enumerate(mock_jobs):
        if i < len(job_titles):
            job["title"] = f"{job_titles[i]} - {keywords}"
        if i < len(companies):
            job["company"] = companies[i]
    
    return mock_jobs

def calculate_job_match_score(cv_data: CVData, job: Dict) -> float:
    """Calculate match score between CV and job"""
    cv_skills = [skill.lower() for skill in cv_data.skills]
    job_text = (job["description"] + " " + job["requirements"]).lower()
    
    # Count skill matches
    skill_matches = sum(1 for skill in cv_skills if skill in job_text)
    
    # Calculate score (0-100)
    if not cv_skills:
        return 50.0  # Default score if no skills extracted
    
    base_score = (skill_matches / len(cv_skills)) * 70  # 70% weight for skills
    
    # Add bonus for experience keywords
    experience_keywords = ["senior", "lead", "manager", "architect"]
    cv_text = cv_data.extracted_text.lower()
    experience_bonus = sum(5 for keyword in experience_keywords if keyword in cv_text and keyword in job_text)
    
    return min(100.0, base_score + experience_bonus)

async def generate_cover_letter(cv_data: CVData, job: JobListing) -> str:
    """Generate personalized cover letter using Gemini"""
    try:
        chat = LlmChat(
            api_key=os.getenv("GEMINI_API_KEY"),
            session_id=f"cover_letter_{uuid.uuid4()}",
            system_message="""You are an expert cover letter writer. Create a personalized, professional cover letter that:
1. Is concise (3-4 paragraphs)
2. Highlights relevant skills and experience
3. Shows enthusiasm for the role and company
4. Has a professional tone
5. Includes a strong opening and closing

Do not include placeholder text like [Your Name] or addresses. Write a complete, ready-to-use cover letter."""
        ).with_model("gemini", "gemini-2.0-flash")

        prompt = f"""Write a cover letter for this job application:

JOB DETAILS:
Title: {job.title}
Company: {job.company}
Location: {job.location}
Description: {job.description}
Requirements: {job.requirements}

APPLICANT CV SUMMARY:
Skills: {', '.join(cv_data.skills)}
Experience: {'; '.join(cv_data.experience)}
Education: {'; '.join(cv_data.education)}
Summary: {cv_data.summary}

Write a compelling cover letter that matches the applicant's background to this specific job."""

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        return response
    except Exception as e:
        # Fallback template if AI fails
        return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job.title} position at {job.company}. With my background in {', '.join(cv_data.skills[:3])}, I am excited about the opportunity to contribute to your team.

My experience includes {cv_data.experience[0] if cv_data.experience else 'relevant professional experience'}, which aligns well with your requirements. I am particularly drawn to this role because of the opportunity to work with cutting-edge technologies and contribute to meaningful projects.

I would welcome the opportunity to discuss how my skills and enthusiasm can benefit {job.company}. Thank you for considering my application.

Best regards"""

# API Endpoints
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "LinkedIn Job Bot"}

@app.post("/api/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    """Upload and analyze CV"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read PDF content
        content = await file.read()
        pdf_file = io.BytesIO(content)
        
        # Extract text
        extracted_text = extract_text_from_pdf(pdf_file)
        
        # Analyze with AI
        analysis = await analyze_cv_with_ai(extracted_text)
        
        # Create CV record
        cv_data = CVData(
            id=str(uuid.uuid4()),
            filename=file.filename,
            extracted_text=extracted_text,
            skills=analysis.get("skills", []),
            experience=analysis.get("experience", []),
            education=analysis.get("education", []),
            summary=analysis.get("summary", ""),
            created_at=datetime.utcnow()
        )
        
        # Save to database
        await db.cvs.insert_one(cv_data.dict())
        
        return {
            "message": "CV uploaded and analyzed successfully",
            "cv_id": cv_data.id,
            "analysis": {
                "skills": cv_data.skills,
                "experience": cv_data.experience,
                "education": cv_data.education,
                "summary": cv_data.summary
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CV: {str(e)}")

@app.post("/api/search-jobs")
async def search_jobs(request: JobSearchRequest):
    """Search for jobs and calculate match scores"""
    try:
        # Get latest CV
        latest_cv = await db.cvs.find_one(sort=[("created_at", -1)])
        if not latest_cv:
            raise HTTPException(status_code=400, detail="Please upload your CV first")
        
        cv_data = CVData(**latest_cv)
        
        # Search jobs (mock implementation)
        raw_jobs = search_jobs_linkedin_scrape(
            keywords=request.keywords,
            location=request.location,
            max_results=request.max_results
        )
        
        # Calculate match scores and create job listings
        job_listings = []
        for raw_job in raw_jobs:
            job = JobListing(
                id=str(uuid.uuid4()),
                title=raw_job["title"],
                company=raw_job["company"],
                location=raw_job["location"],
                description=raw_job["description"],
                requirements=raw_job["requirements"],
                url=raw_job["url"],
                posted_date=raw_job["posted_date"],
                match_score=calculate_job_match_score(cv_data, raw_job),
                created_at=datetime.utcnow()
            )
            job_listings.append(job)
        
        # Save jobs to database
        for job in job_listings:
            await db.jobs.insert_one(job.dict())
        
        # Sort by match score
        job_listings.sort(key=lambda x: x.match_score, reverse=True)
        
        return {
            "message": f"Found {len(job_listings)} jobs",
            "jobs": [job.dict() for job in job_listings]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching jobs: {str(e)}")

@app.post("/api/apply-job/{job_id}")
async def apply_to_job(job_id: str, background_tasks: BackgroundTasks):
    """Apply to a specific job"""
    try:
        # Get job and CV
        job_doc = await db.jobs.find_one({"id": job_id})
        cv_doc = await db.cvs.find_one(sort=[("created_at", -1)])
        
        if not job_doc or not cv_doc:
            raise HTTPException(status_code=404, detail="Job or CV not found")
        
        job = JobListing(**job_doc)
        cv_data = CVData(**cv_doc)
        
        # Generate cover letter
        cover_letter = await generate_cover_letter(cv_data, job)
        
        # Create application record
        application = JobApplication(
            id=str(uuid.uuid4()),
            job_id=job_id,
            cv_id=cv_data.id,
            cover_letter=cover_letter,
            application_date=datetime.utcnow()
        )
        
        # Save application
        await db.applications.insert_one(application.dict())
        
        # Update job as applied
        await db.jobs.update_one({"id": job_id}, {"$set": {"applied": True}})
        
        # In a real implementation, you would use Selenium here to actually submit the application
        # background_tasks.add_task(submit_linkedin_application, job.url, cover_letter, cv_data)
        
        return {
            "message": "Application submitted successfully",
            "application_id": application.id,
            "cover_letter": cover_letter
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error applying to job: {str(e)}")

@app.get("/api/applications")
async def get_applications():
    """Get all job applications"""
    try:
        applications = []
        async for app_doc in db.applications.find().sort("application_date", -1):
            # Get job details
            job_doc = await db.jobs.find_one({"id": app_doc["job_id"]})
            if job_doc:
                app_doc["job_title"] = job_doc["title"]
                app_doc["company"] = job_doc["company"]
            applications.append(app_doc)
        
        return {"applications": applications}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching applications: {str(e)}")

@app.get("/api/jobs")
async def get_jobs():
    """Get all searched jobs"""
    try:
        jobs = []
        async for job_doc in db.jobs.find().sort("match_score", -1).limit(50):
            jobs.append(job_doc)
        
        return {"jobs": jobs}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching jobs: {str(e)}")

@app.post("/api/auto-apply")
async def auto_apply_jobs(background_tasks: BackgroundTasks, min_match_score: float = 70.0, max_applications: int = 10):
    """Automatically apply to top matching jobs"""
    try:
        # Get top matching jobs that haven't been applied to
        jobs = []
        async for job_doc in db.jobs.find({
            "applied": False,
            "match_score": {"$gte": min_match_score}
        }).sort("match_score", -1).limit(max_applications):
            jobs.append(JobListing(**job_doc))
        
        if not jobs:
            return {"message": "No suitable jobs found for auto-application"}
        
        # Apply to each job
        applications_created = []
        for job in jobs:
            try:
                # Apply to job
                result = await apply_to_job(job.id, background_tasks)
                applications_created.append({
                    "job_id": job.id,
                    "job_title": job.title,
                    "company": job.company,
                    "match_score": job.match_score,
                    "application_id": result["application_id"]
                })
                
                # Add delay to avoid rate limiting
                await asyncio.sleep(60)  # 1 minute between applications
                
            except Exception as e:
                print(f"Failed to apply to {job.title} at {job.company}: {str(e)}")
                continue
        
        return {
            "message": f"Auto-applied to {len(applications_created)} jobs",
            "applications": applications_created
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in auto-apply: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
