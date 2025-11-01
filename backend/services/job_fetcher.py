"""
Job Fetcher Service - France Travail API Integration
Fetch real job offers from France Travail (ex-Pôle Emploi)

API Documentation: https://francetravail.io/data/api/offres-emploi
Requires: FRANCE_TRAVAIL_CLIENT_ID and FRANCE_TRAVAIL_CLIENT_SECRET

Author: ESSEC AI Course Project
Date: November 1, 2025
"""

import os
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json

class JobFetcher:
    """Fetch real job offers from France Travail API"""
    
    def __init__(self):
        self.client_id = os.getenv('FRANCE_TRAVAIL_CLIENT_ID')
        self.client_secret = os.getenv('FRANCE_TRAVAIL_CLIENT_SECRET')
        
        # API endpoints
        self.auth_url = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire"
        self.search_url = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
        
        self.access_token = None
        self.token_expiry = None
        
        # Check if API credentials are configured
        if not self.client_id or not self.client_secret:
            print("⚠️  Warning: France Travail API credentials not configured.")
            print("   Set FRANCE_TRAVAIL_CLIENT_ID and FRANCE_TRAVAIL_CLIENT_SECRET in .env")
            print("   Register at: https://francetravail.io/inscription")
            self.api_available = False
        else:
            self.api_available = True
            print("✅ France Travail API credentials found")
    
    def _get_access_token(self) -> Optional[str]:
        """
        Get OAuth2 access token for France Travail API
        Token is cached and reused until expiry
        """
        # Return cached token if still valid
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.access_token
        
        try:
            # Request new token
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'api_offresdemploiv2 o2dsoffre'
            }
            
            response = requests.post(self.auth_url, headers=headers, data=data, timeout=10)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            
            # Set expiry time (typically 1499 seconds)
            expires_in = token_data.get('expires_in', 1499)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)  # 60s safety margin
            
            print(f"✅ France Travail API token obtained (expires in {expires_in}s)")
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to get France Travail API token: {e}")
            return None
    
    def search_jobs(
        self,
        rome_codes: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        location: Optional[str] = None,
        max_results: int = 20,
        experience: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for job offers on France Travail
        
        Args:
            rome_codes: List of ROME codes (e.g., ['M1805', 'M1806'])
            keywords: List of keywords to search for
            location: Location/city name (e.g., 'Paris', 'Lyon')
            max_results: Maximum number of results (default: 20, max: 150)
            experience: Experience level ('D' = Débutant, '1' = 1-2 ans, '2' = 2-5 ans, '3' = 5+ ans)
            
        Returns:
            List of job offers with details
        """
        if not self.api_available:
            return self._get_mock_jobs()
        
        # Get access token
        token = self._get_access_token()
        if not token:
            print("⚠️  Cannot fetch jobs: API token unavailable")
            return self._get_mock_jobs()
        
        try:
            # Build search parameters
            params = {
                'range': f'0-{min(max_results - 1, 149)}',  # API max is 150
                'sort': '1',  # Sort by date (most recent first)
            }
            
            # Add ROME codes filter (sanitize inputs: accept both 'M1805' and 'ROME_M1805')
            if rome_codes:
                cleaned = []
                for code in rome_codes[:5]:
                    if not code:
                        continue
                    c = str(code).upper().strip()
                    # Accept values like 'ROME_M1805' or 'M1805' -> normalize to 'M1805'
                    if c.startswith('ROME_'):
                        c = c.split('ROME_', 1)[1]
                    # Remove any accidental prefixes like 'ROME-' or whitespace
                    c = c.replace('ROME-', '')
                    c = c.strip()
                    if c:
                        cleaned.append(c)
                if cleaned:
                    params['codeROME'] = ','.join(cleaned)
            
            # Add keywords filter (sanitize to avoid reserved chars)
            if keywords:
                safe_keywords = []
                for kw in keywords[:5]:
                    if not kw:
                        continue
                    s = str(kw).strip()
                    # Remove characters that may confuse the API (commas, slashes)
                    s = s.replace(',', ' ').replace('/', ' ').replace('\\', ' ')
                    # Collapse multiple spaces
                    s = ' '.join(s.split())
                    if s:
                        safe_keywords.append(s)
                if safe_keywords:
                    params['motsCles'] = ' '.join(safe_keywords)
            
            # Add location filter
            if location:
                params['commune'] = location
            
            # Add experience filter
            if experience:
                params['experience'] = experience
            
            # Make API request
            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json'
            }
            
            response = requests.get(
                self.search_url,
                headers=headers,
                params=params,
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract job offers
            jobs = []
            if 'resultats' in data:
                for offer in data['resultats']:
                    job = self._parse_job_offer(offer)
                    if job:
                        jobs.append(job)
            
            print(f"✅ Found {len(jobs)} real job offers from France Travail")
            return jobs
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️  France Travail API error: {e}")
            return self._get_mock_jobs()
    
    def _parse_job_offer(self, offer: Dict) -> Optional[Dict]:
        """Parse a job offer from France Travail API response"""
        try:
            # Extract company info
            company = offer.get('entreprise', {})
            company_name = company.get('nom', 'Entreprise confidentielle')
            
            # Extract location
            lieu = offer.get('lieuTravail', {})
            location = lieu.get('libelle', 'Non spécifié')
            
            # Extract contract type
            type_contrat = offer.get('typeContrat', 'CDI')
            
            # Extract salary (if available)
            salaire = offer.get('salaire', {})
            salary_info = None
            if salaire and salaire.get('libelle'):
                salary_info = salaire.get('libelle')
            
            # Extract experience required
            experience = offer.get('experienceLibelle', 'Débutant accepté')
            
            # Build job dictionary
            job = {
                'id': offer.get('id'),
                'title': offer.get('intitule', 'Sans titre'),
                'company': company_name,
                'location': location,
                'contract_type': type_contrat,
                'description': offer.get('description', ''),
                'required_skills': offer.get('competences', []),
                'experience_required': experience,
                'salary': salary_info,
                'publication_date': offer.get('dateCreation', ''),
                'url': offer.get('origineOffre', {}).get('urlOrigine', ''),
                'rome_code': offer.get('romeCode', ''),
                'source': 'France Travail'
            }
            
            return job
            
        except Exception as e:
            print(f"⚠️  Error parsing job offer: {e}")
            return None
    
    def _get_mock_jobs(self) -> List[Dict]:
        """
        Return mock job offers when API is unavailable
        For development/demo purposes
        """
        return [
            {
                'id': 'MOCK001',
                'title': 'Développeur Full Stack',
                'company': 'TechCorp France',
                'location': 'Paris (75)',
                'contract_type': 'CDI',
                'description': 'Nous recherchons un développeur full stack pour rejoindre notre équipe...',
                'required_skills': ['React', 'Node.js', 'Python', 'SQL'],
                'experience_required': '2-5 ans',
                'salary': '40K-55K EUR/an',
                'publication_date': '2025-10-28',
                'url': 'https://francetravail.fr',
                'rome_code': 'M1805',
                'source': 'Mock Data (API non configurée)'
            },
            {
                'id': 'MOCK002',
                'title': 'Data Scientist',
                'company': 'AI Solutions',
                'location': 'Lyon (69)',
                'contract_type': 'CDI',
                'description': 'Rejoignez notre équipe data science pour développer des modèles ML...',
                'required_skills': ['Python', 'Machine Learning', 'TensorFlow', 'SQL'],
                'experience_required': '3+ ans',
                'salary': '45K-60K EUR/an',
                'publication_date': '2025-10-29',
                'url': 'https://francetravail.fr',
                'rome_code': 'M1805',
                'source': 'Mock Data (API non configurée)'
            }
        ]
    
    def get_jobs_for_cv(self, cv_data: Dict, top_rome_codes: List[str]) -> List[Dict]:
        """
        Fetch relevant job offers based on CV analysis and recommended ROME codes
        
        Args:
            cv_data: Parsed CV data with skills, experience, etc.
            top_rome_codes: List of recommended ROME codes from semantic matching
            
        Returns:
            List of relevant job offers
        """
        # Extract search parameters from CV
        skills = cv_data.get('skills', [])[:3]  # Top 3 skills as keywords
        experience_years = cv_data.get('experience_years', 0)
        
        # Map experience years to France Travail format
        experience_level = None
        if experience_years == 0:
            experience_level = 'D'  # Débutant
        elif experience_years <= 2:
            experience_level = '1'  # 1-2 ans
        elif experience_years <= 5:
            experience_level = '2'  # 2-5 ans
        else:
            experience_level = '3'  # 5+ ans
        
        # Search jobs with CV-based filters
        jobs = self.search_jobs(
            rome_codes=top_rome_codes[:3],  # Top 3 ROME matches
            keywords=skills,
            max_results=20,
            experience=experience_level
        )
        
        return jobs


# Singleton instance
job_fetcher = JobFetcher()
