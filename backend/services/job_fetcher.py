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
            
            print(f"🔍 DEBUG - Input parameters:")
            print(f"   rome_codes: {rome_codes}")
            print(f"   keywords: {keywords}")
            print(f"   location: {location}")
            print(f"   experience: {experience}")
            
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
                print(f"🔍 DEBUG - Cleaned ROME codes: {cleaned}")
                if cleaned:
                    params['codeROME'] = ','.join(cleaned)
            
            # Add keywords filter (use only the FIRST keyword for better results)
            if keywords:
                # Take only the first keyword and clean it
                first_keyword = str(keywords[0]).strip()
                # Remove characters that may confuse the API
                first_keyword = first_keyword.replace(',', ' ').replace('/', ' ').replace('\\', ' ')
                # Collapse multiple spaces
                first_keyword = ' '.join(first_keyword.split())
                
                if first_keyword:
                    params['motsCles'] = first_keyword
                    print(f"🔍 DEBUG - Using keyword: '{first_keyword}'")
            
            # Add location filter
            if location:
                params['commune'] = location
            
            # Add experience filter
            if experience:
                params['experience'] = experience
            
            print(f"🔍 DEBUG - Final API params: {params}")
            
            # Make API request
            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json'
            }
            
            print(f"🔍 DEBUG - Making request to: {self.search_url}")
            
            response = requests.get(
                self.search_url,
                headers=headers,
                params=params,
                timeout=15
            )
            
            print(f"🔍 DEBUG - Response status code: {response.status_code}")
            print(f"🔍 DEBUG - Response headers: {dict(response.headers)}")
            
            response.raise_for_status()
            
            # Handle 204 No Content (no jobs found)
            if response.status_code == 204:
                print("ℹ️  No job offers found for the given criteria (HTTP 204)")
                print("🔍 DEBUG - Trying fallback: removing all filters except keywords")
                
                # Fallback 1: Try with just keywords (no ROME codes, no experience filter)
                if keywords:
                    fallback_params = {
                        'range': f'0-{min(max_results - 1, 149)}',
                        'sort': '1',
                    }
                    if 'motsCles' in params:
                        fallback_params['motsCles'] = params['motsCles']
                    
                    print(f"🔍 DEBUG - Fallback params: {fallback_params}")
                    fallback_response = requests.get(
                        self.search_url,
                        headers=headers,
                        params=fallback_params,
                        timeout=15
                    )
                    
                    if fallback_response.status_code == 200:
                        print(f"✅ Fallback search succeeded!")
                        response = fallback_response
                    else:
                        print(f"⚠️  Fallback also returned {fallback_response.status_code}")
                        return []
                else:
                    return []
            
            # Parse JSON response
            data = response.json()
            
            print(f"🔍 DEBUG - Response data keys: {data.keys() if data else 'None'}")
            if 'resultats' in data:
                print(f"🔍 DEBUG - Number of results: {len(data['resultats'])}")
            
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
            # Print response body when available for debugging
            try:
                if 'response' in locals() and response is not None:
                    print(f"⚠️  France Travail API response status: {response.status_code}")
                    print(f"⚠️  France Travail API response body: {response.text}")
            except Exception:
                pass

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
            
            # Extract and parse competences (skills)
            # France Travail API returns skills as list of dicts: [{'code': '...', 'libelle': '...', 'exigence': 'S'}]
            # We need to extract just the 'libelle' (skill name) as strings
            competences_raw = offer.get('competences', [])
            required_skills = []
            if isinstance(competences_raw, list):
                for comp in competences_raw:
                    if isinstance(comp, dict) and 'libelle' in comp:
                        required_skills.append(comp['libelle'])
                    elif isinstance(comp, str):
                        required_skills.append(comp)
            
            # Build job dictionary
            job = {
                'id': offer.get('id'),
                'title': offer.get('intitule', 'Sans titre'),
                'company': company_name,
                'location': location,
                'contract_type': type_contrat,
                'description': offer.get('description', ''),
                'required_skills': required_skills,
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
    
    def get_jobs_for_cv(
        self, 
        cv_data: Dict, 
        top_rome_codes: List[str], 
        recommended_jobs: List[Dict] = None,
        gpt_keywords: List[str] = None
    ) -> List[Dict]:
        """
        Fetch relevant job offers based on CV analysis and recommended ROME codes
        
        Args:
            cv_data: Parsed CV data with skills, experience, etc.
            top_rome_codes: List of recommended ROME codes from semantic matching
            recommended_jobs: List of recommended jobs from semantic matching (with titles)
            gpt_keywords: Optimized keywords generated by GPT for job search
            
        Returns:
            List of relevant job offers
        """
        # Priority 1: Use GPT-generated keywords if available
        job_titles = []
        if gpt_keywords:
            job_titles = gpt_keywords[:3]
            print(f"🤖 Using GPT-generated keywords: {job_titles}")
        # Priority 2: Extract and simplify job titles from recommendations
        elif recommended_jobs:
            for job in recommended_jobs[:3]:
                title = job.get('title', '')
                if title:
                    # Simplify title: take only the main part (before slash or gendered variants)
                    # Example: "Architecte d'intérieur / Décorateur / Décoratrice d'intérieur" -> "Architecte d'intérieur"
                    simplified = title.split('/')[0].strip()
                    # Remove gendered variants in parentheses
                    if '(' in simplified:
                        simplified = simplified.split('(')[0].strip()
                    job_titles.append(simplified)
            print(f"🔍 DEBUG - Simplified job titles: {job_titles}")
        # Priority 3: Fallback to skills if no job titles available
        else:
            job_titles = cv_data.get('skills', [])[:3]
            print(f"🔍 DEBUG - No job titles, using skills as fallback: {job_titles}")
        
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
        
        # Strategy: Try multiple searches with decreasing specificity
        # NOTE: Per request, try keywords-only FIRST (no ROME filtering)
        all_jobs = []

        # Try 1: Job title only (no ROME, no experience) - keywords-only test
        if job_titles:
            print(f"🔍 Try 1: Job title only (keywords-only, no ROME)")
            jobs = self.search_jobs(
                rome_codes=None,
                keywords=[job_titles[0]],
                max_results=20,
                experience=None
            )
            all_jobs.extend(jobs)

        # Try 2: If no results, try with ROME codes + first job title
        if not all_jobs and top_rome_codes and job_titles:
            print(f"🔍 Try 2: ROME codes + first job title")
            jobs = self.search_jobs(
                rome_codes=top_rome_codes[:3],
                keywords=[job_titles[0]],  # Only first title
                max_results=20,
                experience=experience_level
            )
            all_jobs.extend(jobs)

        # Try 3: If still no results, try with ROME codes only (no keywords)
        if not all_jobs and top_rome_codes:
            print(f"🔍 Try 3: ROME codes only (no keywords)")
            jobs = self.search_jobs(
                rome_codes=top_rome_codes[:3],
                keywords=None,
                max_results=20,
                experience=experience_level
            )
            all_jobs.extend(jobs)

        # Try 4: Last resort - broader keyword search with multiple titles
        if not all_jobs and len(job_titles) > 1:
            print(f"🔍 Try 4: Multiple job titles (no filters)")
            for title in job_titles[:2]:  # Try first 2 titles separately
                jobs = self.search_jobs(
                    rome_codes=None,
                    keywords=[title],
                    max_results=10,
                    experience=None
                )
                all_jobs.extend(jobs)
                if all_jobs:
                    break
        
        # Remove duplicates based on job ID
        seen_ids = set()
        unique_jobs = []
        for job in all_jobs:
            job_id = job.get('id')
            if job_id and job_id not in seen_ids:
                seen_ids.add(job_id)
                unique_jobs.append(job)
        
        print(f"✅ Total unique jobs found: {len(unique_jobs)}")
        return unique_jobs


# Singleton instance
job_fetcher = JobFetcher()
