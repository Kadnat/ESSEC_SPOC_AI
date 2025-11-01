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
                        "content": """Tu es un conseiller en orientation professionnelle expert. 
                        Ton rôle est d'analyser le profil d'un candidat et de lui fournir des conseils 
                        personnalisés pour sa carrière. Sois concis, encourageant et constructif. 
                        Réponds toujours en français."""
                    },
                    {
                        "role": "user",
                        "content": f"""Analyse ce profil professionnel et fournis des insights personnalisés :

{context}

Fournis une analyse en 3-4 phrases qui :
1. Résume les points forts du profil
2. Identifie les opportunités de carrière les plus pertinentes
3. Recommande les compétences prioritaires à développer
4. Donne un conseil actionnable pour la suite

Ton analyse doit être encourageante, précise et en français."""
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
        lines.append("PROFIL DU CANDIDAT:")
        if cv_data.get('name'):
            lines.append(f"- Nom: {cv_data['name']}")
        
        if cv_data.get('experience_years'):
            lines.append(f"- Expérience: {cv_data['experience_years']} ans")
        
        if cv_data.get('skills'):
            skills_str = ', '.join(cv_data['skills'][:10])
            lines.append(f"- Compétences: {skills_str}")
        
        if cv_data.get('education'):
            edu_str = ', '.join(cv_data['education'][:2])
            lines.append(f"- Formation: {edu_str}")
        
        # Job recommendations
        lines.append("\nMÉTIERS RECOMMANDÉS (par ordre de compatibilité):")
        for i, job in enumerate(job_recommendations[:3], 1):
            match_pct = int(job.get('match_score', 0) * 100)
            lines.append(f"{i}. {job['title']} ({match_pct}% de compatibilité)")
        
        # Missing skills
        if missing_skills:
            top_missing = missing_skills[:5]
            lines.append(f"\nCOMPÉTENCES À DÉVELOPPER: {', '.join(top_missing)}")
        
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
            insights.append(f"Excellent ! Vous possédez {num_skills} compétences techniques identifiées.")
        elif num_skills > 5:
            insights.append(f"Vous avez {num_skills} compétences techniques dans votre profil.")
        else:
            insights.append("Pensez à enrichir votre CV avec plus de compétences techniques spécifiques.")
        
        # Analyze experience
        exp_years = cv_data.get('experience_years')
        if exp_years:
            if exp_years >= 5:
                insights.append(f"Avec {exp_years} ans d'expérience, vous êtes un profil senior recherché.")
            elif exp_years >= 2:
                insights.append(f"Vos {exp_years} ans d'expérience vous positionnent comme profil confirmé.")
            else:
                insights.append(f"Vous êtes en début de carrière ({exp_years} an{'s' if exp_years > 1 else ''}) avec un beau potentiel d'évolution.")
        
        # Analyze job matches
        if job_recommendations:
            best_match = job_recommendations[0]
            match_pct = int(best_match.get('match_score', 0) * 100)
            insights.append(f"Votre meilleur match est '{best_match['title']}' avec {match_pct}% de compatibilité.")
        
        # Recommend skill development
        if missing_skills:
            top_missing = missing_skills[:3]
            insights.append(f"Pour élargir vos opportunités, développez : {', '.join(top_missing)}.")
        
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
                        "content": "Tu es un expert en ressources humaines. Enrichis les descriptions de poste de manière concise et professionnelle."
                    },
                    {
                        "role": "user",
                        "content": f"Enrichis cette description de poste en 2 phrases maximum :\n\nTitre : {job_title}\nDescription : {base_description}"
                    }
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error enhancing job description: {e}")
            return base_description


# Singleton instance
llm_service = LLMService()
