# JobMatch AI - User Guide

**Version:** 1.0  
**Last Updated:** November 1, 2025  
**Target Audience:** End users, developers, evaluators

---

## Table of Contents

1. [Quick Start](#1-quick-start)
2. [System Requirements](#2-system-requirements)
3. [Installation Guide](#3-installation-guide)
4. [Using the Application](#4-using-the-application)
5. [Understanding Results](#5-understanding-results)
6. [Troubleshooting](#6-troubleshooting)
7. [API Configuration](#7-api-configuration)
8. [Development Guide](#8-development-guide)

---

## 1. Quick Start

### For End Users

1. Open your web browser
2. Navigate to the application URL (e.g., http://localhost:5173 for local development)
3. Upload your CV (PDF or DOCX format, max 10MB)
4. Wait 4-7 seconds for analysis
5. Review your personalized results:
   - CV analysis and extracted skills
   - Top 5 recommended jobs with match scores
   - Real job offers from France Travail
   - Recommended training courses
   - AI-generated career insights

### For Developers

```bash
# Clone repository
git clone <repository-url>
cd job-match-ai

# Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys

# Setup frontend
cd ../
npm install

# Run application
# Terminal 1: Backend
cd backend && python main.py

# Terminal 2: Frontend
npm run dev
```

---

## 2. System Requirements

### End Users
- **Browser:** Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Internet:** Stable connection (minimum 2 Mbps)
- **CV Format:** PDF or DOCX, max 10MB
- **Screen Resolution:** Minimum 1024x768 (desktop), 375x667 (mobile)

### Developers

**Required:**
- Python 3.11 or higher
- Node.js 18.0 or higher
- npm 9.0 or higher
- Git 2.30 or higher

**Recommended:**
- 8GB RAM (for running both frontend and backend)
- 2GB free disk space
- macOS, Linux, or Windows with WSL2

**API Keys:**
- OpenAI API key (GPT-4o-mini access required)
- France Travail API credentials (free registration)

---

## 3. Installation Guide

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd job-match-ai
```

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create `backend/.env` file:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4o-mini

# France Travail API Configuration
FRANCE_TRAVAIL_CLIENT_ID=your-client-id-here
FRANCE_TRAVAIL_CLIENT_SECRET=your-client-secret-here
```

**How to get API keys:**

**OpenAI API Key:**
1. Go to https://platform.openai.com/signup
2. Create an account or sign in
3. Navigate to API Keys section
4. Click "Create new secret key"
5. Copy the key (starts with `sk-proj-`)
6. Add billing information (pay-as-you-go)

**France Travail API Credentials:**
1. Go to https://francetravail.io/inscription
2. Register for a developer account
3. Validate your email
4. Create a new application
5. Request access to "Offres d'emploi v2" API
6. Copy Client ID and Client Secret from application settings

### Step 4: Verify Data Files

Ensure these files exist:
```
backend/data/
  ├── jobs_rome_complete.json  (1,584 French job roles)
  └── formations.json           (Training courses database)
```

These files are included in the repository.

### Step 5: Frontend Setup

```bash
cd ..  # Return to project root
npm install
```

### Step 6: Start Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```

Expected output:
```
📚 Loading complete ROME database...
✅ Loaded 1584 métiers from ROME v4.60
✅ France Travail API credentials found
INFO: Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

Expected output:
```
VITE v7.1.12 ready in 170 ms
➜ Local:   http://localhost:5173/
➜ Network: use --host to expose
```

### Step 7: Access Application

Open your browser to: http://localhost:5173

---

## 4. Using the Application

### 4.1 Uploading a CV

1. **Click or drag-and-drop** your CV file into the upload area
2. **Supported formats:** PDF (.pdf) or Microsoft Word (.docx)
3. **File size limit:** 10MB maximum
4. **Language:** French CVs recommended (multilingual support available)

**Tips for best results:**
- Use a well-structured CV with clear sections (Experience, Education, Skills)
- Include specific technical and soft skills
- List years of experience
- Mention degrees and certifications
- Avoid overly creative layouts (plain text works best)

### 4.2 Analysis Process

Once uploaded, the system performs:

1. **Document parsing** (1-2 seconds)
   - Extract text from PDF or DOCX
   - Handle French character encoding

2. **AI extraction** (1-2 seconds)
   - GPT-4o-mini extracts structured information
   - Identifies name, contact info, skills, experience, education

3. **Semantic matching** (1-2 seconds)
   - Compares CV to 1,584 French job roles
   - Calculates match scores using AI embeddings

4. **Job search** (1-2 seconds)
   - Generates optimized keywords with GPT
   - Queries France Travail API for real job offers

5. **Recommendations** (1 second)
   - Identifies skill gaps
   - Suggests relevant training courses
   - Generates personalized career insights

**Total time:** 4-7 seconds

### 4.3 Navigating Results

Results are displayed in tabs:

**1. Métiers Recommandés (Recommended Jobs)**
- Top 5 job roles that match your profile
- Match score percentage (color-coded)
- Job description and required skills
- Missing skills highlighted
- Click to see full details

**2. Offres Réelles (Real Job Offers)**
- Live job postings from France Travail
- Company name, location, contract type
- Job description and required skills
- Salary information (when available)
- Publication date
- Direct link to apply

**3. Formations (Training Courses)**
- Recommended courses to develop missing skills
- Course duration and level
- Skills acquired
- Relevance score
- Online/in-person delivery method

### 4.4 Understanding Match Scores

Match scores indicate compatibility between your profile and a job role:

- **70-100% (High Match - Green):** Excellent fit, apply now
- **50-69% (Medium Match - Yellow):** Good fit with some skill gaps
- **Below 50% (Low Match - Orange):** Consider training first

Match scores are calculated using:
- Semantic similarity between your CV and job description (60%)
- Skills overlap (30%)
- Education and experience level (10%)

### 4.5 Acting on Results

**For Job Offers:**
1. Review match score and job description
2. Click "Voir l'offre" button
3. Redirected to France Travail official job posting
4. Apply directly through France Travail platform

**For Training Courses:**
1. Identify priority skills to develop
2. Note recommended courses
3. Search for courses on:
   - France Travail training portal
   - LinkedIn Learning
   - Coursera / Udemy
   - Local training centers

**For Career Insights:**
- Read AI-generated personalized advice
- Focus on suggested priority skills
- Follow actionable recommendations
- Consider suggested career paths

---

## 5. Understanding Results

### 5.1 CV Analysis Section

**Profile Card:**
```
Name: [Extracted name]
Email: [Extracted email]
Phone: [Extracted phone]
Experience: [X years]
```

**Skills Grid:**
- All extracted technical and soft skills
- Color-coded pills for easy scanning
- Click to search related job offers

**Education:**
- Degrees and certifications
- Institutions and years (when available)

**Languages:**
- Spoken/written languages
- Proficiency levels (when specified)

### 5.2 Job Recommendations

Each recommendation includes:

**Match Score Badge:**
- Percentage match (e.g., 87%)
- Color indicator (green/yellow/orange)
- Position in ranking (1-5)

**Job Details:**
- ROME code (e.g., M1805)
- Job title in French
- Comprehensive description
- Required skills list
- Missing skills (highlighted in red)
- Typical salary range
- Education level required

**Alternative Recommendations:**
- Marked with "Alternative" badge
- Explanation: "Compétences proches ou intitulé similaire"
- Consider these if primary matches don't fit

### 5.3 Real Job Offers

Each offer includes:

**Header:**
- Job title
- Company name (or "Entreprise confidentielle")
- Location (city and department code)

**Details:**
- Contract type (CDI, CDD, Interim, etc.)
- Experience required (Débutant accepté, 1-2 ans, 2-5 ans, 5+ ans)
- Salary (when disclosed)
- Publication date

**Description:**
- Full job description from employer
- Required skills
- Company information (when available)

**Actions:**
- "Voir l'offre" button links to France Travail
- Save or share offer (if logged in)

### 5.4 Training Recommendations

Each training includes:

**Training Info:**
- Course title
- Provider/platform
- Duration (hours or weeks)
- Level (Débutant, Intermédiaire, Avancé)

**Relevance:**
- Percentage match to missing skills
- Skills you will acquire
- Why this training is recommended

**Delivery:**
- Online, in-person, or hybrid
- Self-paced or scheduled
- Certification available

### 5.5 AI Career Insights

Personalized text analysis including:

1. **Strengths Summary:**
   - Your key assets
   - Competitive advantages
   - Areas of expertise

2. **Career Opportunities:**
   - Best-fit roles
   - Industries to explore
   - Growth potential

3. **Skill Development Priorities:**
   - Most valuable skills to learn
   - Why they matter
   - Expected impact

4. **Actionable Advice:**
   - Immediate next steps
   - Medium-term goals
   - Long-term career path

---

## 6. Troubleshooting

### 6.1 Upload Issues

**Problem:** "Format invalide. Veuillez télécharger un fichier PDF ou DOCX."

**Solutions:**
- Ensure file extension is .pdf or .docx
- Try saving your CV in a different format
- Reduce file size if over 10MB (compress PDF)
- Avoid password-protected documents

**Problem:** "Fichier trop volumineux. Maximum 10MB."

**Solutions:**
- Compress PDF using Adobe Acrobat or online tools
- Remove images or reduce image resolution
- Use DOCX instead of PDF (smaller file size)
- Remove unnecessary pages

**Problem:** Upload button not responding

**Solutions:**
- Check internet connection
- Refresh browser page
- Clear browser cache
- Try different browser (Chrome recommended)
- Disable browser extensions (ad blockers)

### 6.2 Analysis Errors

**Problem:** "Erreur lors de l'analyse du CV."

**Common causes:**
- Backend server not running
- API keys not configured
- Network timeout
- Invalid CV format (scanned image PDF)

**Solutions:**
- Verify backend is running (check Terminal 1)
- Check .env file has valid API keys
- Wait and retry (may be temporary API issue)
- Use text-based PDF (not scanned images)

**Problem:** "Nom non détecté" or missing information

**Causes:**
- CV format not recognized by AI
- Information formatted unusually
- Scanned document without OCR

**Solutions:**
- Ensure CV has clear section headers
- Put name at top of document
- Use standard CV format
- Convert scanned PDF to text

### 6.3 No Job Offers Found

**Problem:** Real job offers section is empty

**Possible reasons:**
- No matching jobs available currently
- Search keywords too specific
- France Travail API temporarily unavailable
- Rate limit reached

**Solutions:**
- Broaden your skills (add more keywords)
- Try again later (new jobs posted daily)
- Check France Travail directly: https://candidat.francetravail.fr
- Contact support if persistent

### 6.4 Performance Issues

**Problem:** Analysis takes longer than 7 seconds

**Causes:**
- Slow internet connection
- High server load
- API rate limits
- Large CV file size

**Solutions:**
- Check internet speed (minimum 2 Mbps)
- Retry during off-peak hours
- Reduce CV file size
- Wait for current analysis to complete

**Problem:** Browser freezes or crashes

**Solutions:**
- Close other browser tabs
- Update browser to latest version
- Clear browser cache and cookies
- Try incognito/private mode
- Ensure 4GB+ available RAM

### 6.5 Display Issues

**Problem:** Results not displaying correctly

**Solutions:**
- Refresh page (Ctrl+R or Cmd+R)
- Try different browser
- Disable browser extensions
- Check browser console for errors (F12)

**Problem:** Layout looks broken or compressed

**Solutions:**
- Zoom browser to 100% (Ctrl+0 or Cmd+0)
- Resize browser window
- Try full-screen mode (F11)
- Use minimum 1024x768 resolution

---

## 7. API Configuration

### 7.1 OpenAI API Setup

**Step 1: Create Account**
1. Visit https://platform.openai.com/signup
2. Sign up with email or Google/Microsoft account
3. Verify your email address

**Step 2: Add Billing**
1. Go to Settings > Billing
2. Add payment method (credit card required)
3. Set usage limits (recommended: $10/month for testing)
4. Monitor usage: https://platform.openai.com/usage

**Step 3: Generate API Key**
1. Navigate to API Keys section
2. Click "Create new secret key"
3. Name: "JobMatch AI Backend"
4. Copy key immediately (cannot view again)
5. Add to backend/.env as OPENAI_API_KEY

**Step 4: Verify Access**
```bash
# Test API key (from backend folder)
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Pricing:**
- GPT-4o-mini: $0.150 per 1M input tokens, $0.600 per 1M output tokens
- Average CV analysis cost: $0.02
- Budget for testing: $10 (500 analyses)

### 7.2 France Travail API Setup

**Step 1: Register**
1. Visit https://francetravail.io/inscription
2. Fill registration form
3. Verify email
4. Activate account

**Step 2: Create Application**
1. Login to developer portal
2. Click "Créer une application"
3. Name: "JobMatch AI"
4. Description: "AI-powered career matching platform"
5. Environment: Development (for testing)

**Step 3: Request API Access**
1. Select "Offres d'emploi v2" API
2. Justify usage: "Educational project for ESSEC AI course"
3. Wait for approval (usually instant for educational use)

**Step 4: Get Credentials**
1. Navigate to application settings
2. Copy Client ID
3. Copy Client Secret (keep secure)
4. Add to backend/.env:
```
FRANCE_TRAVAIL_CLIENT_ID=your_client_id
FRANCE_TRAVAIL_CLIENT_SECRET=your_secret
```

**Step 5: Test Connection**
```bash
# Test OAuth token (from backend folder)
python -c "
from services.job_fetcher import JobFetcher
fetcher = JobFetcher()
token = fetcher._get_access_token()
print('Token obtained!' if token else 'Failed')
"
```

**Rate Limits:**
- 10 requests per second per Client ID
- 100 requests per second default limit
- Monitor headers: X-Ratelimit-Remaining-Clientidlimiter

**Costs:**
- Free for educational and non-commercial use
- Commercial use requires contacting France Travail

---

## 8. Development Guide

### 8.1 Project Structure

```
job-match-ai/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables (not in git)
│   ├── data/
│   │   ├── jobs_rome_complete.json    # 1,584 French job roles
│   │   └── formations.json            # Training courses database
│   └── services/
│       ├── cv_parser.py        # CV extraction (GPT + Regex)
│       ├── semantic_matcher.py # Job matching (Transformers)
│       ├── job_fetcher.py      # France Travail API client
│       └── llm_service.py      # OpenAI GPT wrapper
├── src/
│   ├── App.jsx                 # Main React component
│   ├── App.css                 # Component styles
│   ├── services/
│   │   └── api.js              # Backend API client (Axios)
│   └── assets/                 # Images and static files
├── public/                     # Public assets
├── package.json                # Node.js dependencies
├── vite.config.js              # Vite build configuration
├── PROJECT_REPORT.md           # Comprehensive project report
├── USER_GUIDE.md               # This file
└── README.md                   # Quick start guide
```

### 8.2 Adding New Features

**Example: Add Location Filter**

**Step 1: Update Backend**

Edit `backend/services/job_fetcher.py`:
```python
def search_jobs(
    self,
    rome_codes: Optional[List[str]] = None,
    keywords: Optional[List[str]] = None,
    location: Optional[str] = None,  # Add parameter
    max_results: int = 20,
    experience: Optional[str] = None
) -> List[Dict]:
    # ...
    if location:
        params['commune'] = location  # Already implemented
    # ...
```

Edit `backend/main.py`:
```python
@app.post("/api/analyze-cv")
async def analyze_cv(
    file: UploadFile = File(...),
    location: Optional[str] = None  # Add query parameter
):
    # ...
    real_jobs = job_fetcher.get_jobs_for_cv(
        cv_data, 
        top_rome_codes, 
        job_recommendations,
        gpt_keywords,
        location=location  # Pass location
    )
    # ...
```

**Step 2: Update Frontend**

Edit `src/App.jsx`:
```jsx
function App() {
  const [location, setLocation] = useState('')
  
  const handleAnalyze = async () => {
    const formData = new FormData()
    formData.append('file', file)
    
    // Add location as query parameter
    const url = location 
      ? `/api/analyze-cv?location=${encodeURIComponent(location)}`
      : '/api/analyze-cv'
    
    const response = await axios.post(url, formData)
    // ...
  }
  
  return (
    <>
      {/* Add location input */}
      <input
        type="text"
        placeholder="Ville (optionnel)"
        value={location}
        onChange={(e) => setLocation(e.target.value)}
      />
      {/* ... */}
    </>
  )
}
```

**Step 3: Test**
```bash
# Upload CV with location parameter
curl -X POST http://localhost:8001/api/analyze-cv \
  -F "file=@test_cv.pdf" \
  -F "location=Paris"
```

### 8.3 Running Tests

**Backend Unit Tests:**
```bash
cd backend
pytest tests/
```

**Frontend Component Tests:**
```bash
npm test
```

**Integration Tests:**
```bash
# Start backend and frontend
# Then run:
npm run test:e2e
```

### 8.4 Debugging

**Backend Debugging:**

Enable verbose logging in `backend/main.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

View logs:
```bash
# Backend logs in Terminal 1
# Look for:
# - 🔍 DEBUG messages (API parameters)
# - ⚠️ Warning messages (fallbacks)
# - ❌ Error messages (failures)
```

**Frontend Debugging:**

Open browser console (F12) and check:
```javascript
// Network tab: Monitor API calls
// Console tab: Check for errors
// React DevTools: Inspect component state
```

### 8.5 Building for Production

**Backend:**
```bash
cd backend
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

**Frontend:**
```bash
npm run build
# Output in dist/ folder
# Deploy to: Vercel, Netlify, AWS S3, etc.
```

### 8.6 Environment Variables Reference

**Backend (.env):**
```bash
# Required
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
FRANCE_TRAVAIL_CLIENT_ID=...
FRANCE_TRAVAIL_CLIENT_SECRET=...

# Optional (with defaults)
BACKEND_PORT=8001
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
LOG_LEVEL=INFO
```

**Frontend (.env):**
```bash
VITE_API_URL=http://localhost:8001
VITE_APP_NAME=JobMatch AI
```

---

## Support and Contact

For technical issues, questions, or feedback:

- **GitHub Issues:** [Repository URL]/issues
- **Email:** [Your contact email]
- **Documentation:** See PROJECT_REPORT.md for technical details

---

**Last Updated:** November 1, 2025  
**Version:** 1.0  
**License:** MIT (Educational Use)
