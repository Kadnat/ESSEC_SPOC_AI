"""
JobMatchAI - Backend API
FastAPI application for CV analysis and job recommendations

Author: ESSEC AI Course Project
Date: November 1, 2025
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our services
from services.cv_parser import cv_parser
from services.semantic_matcher import semantic_matcher
from services.llm_service import llm_service
from services.job_fetcher import job_fetcher

# Initialize FastAPI app
app = FastAPI(
    title="JobMatchAI API",
    description="AI-powered CV analysis and job recommendation system",
    version="1.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Pydantic Models
# ============================================

class CVAnalysis(BaseModel):
    """Structured CV analysis results"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = []
    experience_years: Optional[int] = None
    education: List[str] = []
    languages: List[str] = []
    summary: str = ""

class JobRecommendation(BaseModel):
    """Job recommendation with match score"""
    job_id: str
    title: str
    description: str
    match_score: float
    required_skills: List[str]
    missing_skills: List[str]
    salary_range: Optional[str] = None
    education_level: Optional[str] = None
    # Optional fields to indicate fallback/alternative recommendations
    is_alternative: Optional[bool] = False
    alternative_reason: Optional[str] = None

class TrainingRecommendation(BaseModel):
    """Training/formation recommendation"""
    training_id: str
    title: str
    provider: str
    url: str
    duration: str
    skills_acquired: List[str]
    relevance_score: float

class RealJobOffer(BaseModel):
    """Real job offer from France Travail API"""
    id: str
    title: str
    company: str
    location: str
    contract_type: str
    description: str
    required_skills: List[str]
    experience_required: str
    salary: Optional[str] = None
    publication_date: str
    url: str
    rome_code: str
    source: str

class RecommendationResponse(BaseModel):
    """Complete response with analysis and recommendations"""
    cv_analysis: CVAnalysis
    job_recommendations: List[JobRecommendation]
    training_recommendations: List[TrainingRecommendation]
    ai_insights: str
    real_job_offers: List[RealJobOffer] = []  # New field for real offers

# ============================================
# API Endpoints
# ============================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "JobMatchAI API is running",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "models_loaded": False,  # TODO: Check if models are loaded
        "database_connected": True
    }

@app.post("/api/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    """
    Upload CV file (PDF or DOCX)
    Returns file metadata and confirmation
    """
    # Validate file type
    if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF and DOCX files are accepted."
        )
    
    # Validate file size (max 10MB)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 10MB limit."
        )
    
    return {
        "message": "CV uploaded successfully",
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents)
    }

@app.post("/api/analyze-cv", response_model=RecommendationResponse)
async def analyze_cv(file: UploadFile = File(...)):
    """
    Analyze CV and return comprehensive recommendations
    
    This endpoint:
    1. Parses the CV (PDF/DOCX)
    2. Extracts key information (skills, experience, education)
    3. Generates semantic embeddings
    4. Matches against job database
    5. Recommends relevant trainings
    6. Generates AI-powered insights
    """
    
    # Validate file type
    if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF and DOCX files are accepted."
        )
    
    # Read file content
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 10MB limit."
        )
    
    try:
        # Parse CV
        cv_data = cv_parser.parse_file(contents, file.content_type)
        
        # Get job recommendations using semantic matching
        job_recommendations = semantic_matcher.match_cv_with_jobs(cv_data, top_k=5)
        
        # Collect all missing skills
        all_missing_skills = []
        for job in job_recommendations:
            all_missing_skills.extend(job.get('missing_skills', []))
        # Remove duplicates
        unique_missing_skills = list(set(all_missing_skills))
        
        # Get training recommendations
        training_recommendations = semantic_matcher.recommend_trainings(
            cv_data,
            unique_missing_skills[:5],  # Top 5 missing skills
            top_k=3
        )
        
        # Generate AI insights using OpenAI GPT
        ai_insights = llm_service.generate_career_insights(
            cv_data,
            job_recommendations,
            unique_missing_skills
        )
        
        # Generate optimized job search keywords using GPT
        optimized_keywords = llm_service.generate_job_search_keywords(
            cv_data,
            job_recommendations
        )
        
        # Fetch real job offers from France Travail API
        # Extract ROME codes from recommended jobs
        top_rome_codes = [job.get('job_id', '') for job in job_recommendations[:3]]
        real_jobs = job_fetcher.get_jobs_for_cv(
            cv_data, 
            top_rome_codes, 
            job_recommendations,
            gpt_keywords=optimized_keywords
        )
        
        # Build response
        response = RecommendationResponse(
            cv_analysis=CVAnalysis(
                name=cv_data.get('name') or "Nom non détecté",
                email=cv_data.get('email'),
                phone=cv_data.get('phone'),
                skills=cv_data.get('skills', []),
                experience_years=cv_data.get('experience_years'),
                education=cv_data.get('education', []),
                languages=cv_data.get('languages', []),
                summary=cv_data.get('summary', "")
            ),
            job_recommendations=[
                JobRecommendation(**job) for job in job_recommendations
            ],
            training_recommendations=[
                TrainingRecommendation(**training) for training in training_recommendations
            ],
            ai_insights=ai_insights,
            real_job_offers=[
                RealJobOffer(**job) for job in real_jobs
            ]
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing CV: {str(e)}"
        )

@app.get("/api/jobs")
async def get_jobs():
    """Get all available jobs in database"""
    # TODO: Load from jobs database
    return {
        "total": 0,
        "jobs": []
    }

@app.get("/api/trainings")
async def get_trainings():
    """Get all available trainings"""
    # TODO: Load from trainings database
    return {
        "total": 0,
        "trainings": []
    }

# ============================================
# Main
# ============================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
