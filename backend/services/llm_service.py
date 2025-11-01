"""
LLM Service for generating personalized insights
Uses OpenAI GPT-4o-mini for recommendations
"""

import os
from typing import Dict, List
from openai import OpenAI

class LLMService:
    """Generate AI-powered insights using OpenAI"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-5-nano')
        
        if not self.api_key:
            print("Warning: OPENAI_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
    
    def generate_career_insights(
        self,
        cv_data: Dict,
        job_recommendations: List[Dict],
        missing_skills: List[str]
    ) -> str:
        """
        Generate personalized career insights using GPT
        
        Args:
            cv_data: Parsed CV data
            job_recommendations: List of recommended jobs
            missing_skills: Skills that need development
            
        Returns:
            AI-generated career insights in French
        """
        if not self.client:
            return self._generate_fallback_insights(cv_data, job_recommendations, missing_skills)
        
        # Prepare context for GPT
        context = self._prepare_context(cv_data, job_recommendations, missing_skills)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert career counselor. 
                        Your role is to analyze a candidate's profile and provide personalized 
                        career advice. Be concise, encouraging, and constructive. 
                        Always respond in English."""
                    },
                    {
                        "role": "user",
                        "content": f"""Analyze this professional profile and provide personalized insights:

{context}

Provide an analysis in 3-4 sentences that:
1. Summarizes the profile's key strengths
2. Identifies the most relevant career opportunities
3. Recommends priority skills to develop
4. Gives actionable advice for next steps

Your analysis should be encouraging, precise, and in English."""
                    }
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            insights = response.choices[0].message.content.strip()
            return insights
            
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return self._generate_fallback_insights(cv_data, job_recommendations, missing_skills)
    
    def _prepare_context(
        self,
        cv_data: Dict,
        job_recommendations: List[Dict],
        missing_skills: List[str]
    ) -> str:
        """Prepare context string for GPT"""
        lines = []
        
        # Profile summary
        lines.append("CANDIDATE PROFILE:")
        if cv_data.get('name'):
            lines.append(f"- Name: {cv_data['name']}")
        
        if cv_data.get('experience_years'):
            lines.append(f"- Experience: {cv_data['experience_years']} years")
        
        if cv_data.get('skills'):
            skills_str = ', '.join(cv_data['skills'][:10])
            lines.append(f"- Skills: {skills_str}")
        
        if cv_data.get('education'):
            edu_str = ', '.join(cv_data['education'][:2])
            lines.append(f"- Education: {edu_str}")
        
        # Job recommendations
        lines.append("\nRECOMMENDED JOBS (by compatibility):")
        for i, job in enumerate(job_recommendations[:3], 1):
            match_pct = int(job.get('match_score', 0) * 100)
            lines.append(f"{i}. {job['title']} ({match_pct}% match)")
        
        # Missing skills
        if missing_skills:
            top_missing = missing_skills[:5]
            lines.append(f"\nSKILLS TO DEVELOP: {', '.join(top_missing)}")
        
        return '\n'.join(lines)
    
    def _generate_fallback_insights(
        self,
        cv_data: Dict,
        job_recommendations: List[Dict],
        missing_skills: List[str]
    ) -> str:
        """Generate basic insights without LLM (fallback)"""
        insights = []
        
        # Analyze skills
        num_skills = len(cv_data.get('skills', []))
        if num_skills > 10:
            insights.append(f"Excellent! You have {num_skills} identified technical skills.")
        elif num_skills > 5:
            insights.append(f"You have {num_skills} technical skills in your profile.")
        else:
            insights.append("Consider enriching your CV with more specific technical skills.")
        
        # Analyze experience
        exp_years = cv_data.get('experience_years')
        if exp_years:
            if exp_years >= 5:
                insights.append(f"With {exp_years} years of experience, you are a sought-after senior profile.")
            elif exp_years >= 2:
                insights.append(f"Your {exp_years} years of experience position you as an experienced profile.")
            else:
                insights.append(f"You are early in your career ({exp_years} year{'s' if exp_years > 1 else ''}) with great growth potential.")
        
        # Analyze job matches
        if job_recommendations:
            best_match = job_recommendations[0]
            match_pct = int(best_match.get('match_score', 0) * 100)
            insights.append(f"Your best match is '{best_match['title']}' with {match_pct}% compatibility.")
        
        # Recommend skill development
        if missing_skills:
            top_missing = missing_skills[:3]
            insights.append(f"To expand your opportunities, develop: {', '.join(top_missing)}.")
        
        return " ".join(insights)
    
    def enhance_job_description(self, job_title: str, base_description: str) -> str:
        """
        Enhance job description with more details using GPT
        
        Args:
            job_title: Title of the job
            base_description: Basic description
            
        Returns:
            Enhanced description
        """
        if not self.client:
            return base_description
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an HR expert. Enrich job descriptions concisely and professionally in English."
                    },
                    {
                        "role": "user",
                        "content": f"Enrich this job description in maximum 2 sentences:\n\nTitle: {job_title}\nDescription: {base_description}"
                    }
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error enhancing job description: {e}")
            return base_description
    
    def generate_job_search_keywords(
        self,
        cv_data: Dict,
        job_recommendations: List[Dict]
    ) -> List[str]:
        """
        Generate optimized keywords for job search using GPT
        
        Args:
            cv_data: Parsed CV data with skills and experience
            job_recommendations: List of recommended jobs from semantic matching
            
        Returns:
            List of 3-5 optimized search keywords for France Travail API
        """
        if not self.client:
            # Fallback: use simplified job titles
            return [job.get('title', '').split('/')[0].strip() for job in job_recommendations[:3] if job.get('title')]
        
        try:
            # Prepare context for GPT
            skills = ', '.join(cv_data.get('skills', [])[:10])
            job_titles = [job.get('title', '') for job in job_recommendations[:5] if job.get('title')]
            exp_years = cv_data.get('experience_years', 0)
            
            context = f"""PROFIL:
- Compétences: {skills}
- Expérience: {exp_years} ans
- Métiers recommandés: {', '.join(job_titles)}"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """Tu es un expert en recherche d'emploi. Ton rôle est de générer des mots-clés 
                        optimisés pour rechercher des offres d'emploi sur France Travail. Les mots-clés doivent être :
                        - Courts et précis (2-4 mots maximum)
                        - Des intitulés de poste courants en France
                        - Sans variantes genrées multiples (choisir la forme la plus courante)
                        - Adaptés au profil du candidat
                        
                        Réponds UNIQUEMENT avec une liste de 3-5 mots-clés séparés par des virgules, sans numérotation ni explication."""
                    },
                    {
                        "role": "user",
                        "content": f"""Génère 3-5 mots-clés optimisés pour rechercher des offres d'emploi correspondant à ce profil :

{context}

Réponds uniquement avec les mots-clés séparés par des virgules."""
                    }
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            keywords_text = response.choices[0].message.content.strip()
            # Parse comma-separated keywords
            keywords = [k.strip() for k in keywords_text.split(',') if k.strip()]
            
            print(f"🤖 GPT generated keywords: {keywords}")
            return keywords[:5]  # Max 5 keywords
            
        except Exception as e:
            print(f"⚠️  Error generating keywords with GPT: {e}")
            # Fallback: use simplified job titles
            return [job.get('title', '').split('/')[0].strip() for job in job_recommendations[:3] if job.get('title')]


# Singleton instance
llm_service = LLMService()
