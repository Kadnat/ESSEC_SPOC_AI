"""
Semantic Matching Service
Uses sentence-transformers to match CVs with jobs

Model: paraphrase-multilingual-mpnet-base-v2
"""

from typing import List, Dict, Tuple
import json
import os
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class SemanticMatcher:
    """Match CVs with jobs using semantic similarity"""
    
    def __init__(self):
        self.model = None
        self.jobs_data = []
        self.jobs_embeddings = None
        
        # Load jobs database
        self._load_jobs_database()
        
    def _load_jobs_database(self):
        """Load jobs from JSON file - Try complete ROME DB first, fallback to basic"""
        data_dir = Path(__file__).parent.parent / 'data'
        
        # Priority 1: Complete ROME database (1584 métiers)
        rome_complete_file = data_dir / 'jobs_rome_complete.json'
        jobs_file = data_dir / 'jobs.json'
        
        if rome_complete_file.exists():
            print(f"📚 Loading complete ROME database...")
            with open(rome_complete_file, 'r', encoding='utf-8') as f:
                rome_data = json.load(f)
                self.jobs_data = rome_data.get('jobs', [])
            print(f"✅ Loaded {len(self.jobs_data)} métiers from ROME v4.60")
        elif jobs_file.exists():
            print(f"📚 Loading basic jobs database...")
            with open(jobs_file, 'r', encoding='utf-8') as f:
                self.jobs_data = json.load(f)
            print(f"✅ Loaded {len(self.jobs_data)} jobs")
        else:
            print(f"❌ Warning: No jobs database found at {data_dir}")
            self.jobs_data = []
    
    def initialize_model(self):
        """Initialize the sentence transformer model"""
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers is not installed. "
                "Install it with: pip install sentence-transformers"
            )
        
        if self.model is None:
            print("Loading sentence-transformers model...")
            # Use multilingual model for French support
            self.model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
            print("Model loaded successfully!")
            
            # Pre-compute job embeddings
            self._compute_jobs_embeddings()
    
    def _compute_jobs_embeddings(self):
        """Pre-compute embeddings for all jobs"""
        if not self.jobs_data:
            return
        
        print("Computing job embeddings...")
        job_texts = []
        
        for job in self.jobs_data:
            # Combine title, description, and skills for richer embedding
            text = f"{job['title']}. {job['description']}. "
            text += f"Compétences: {', '.join(job['required_skills'])}"
            job_texts.append(text)
        
        self.jobs_embeddings = self.model.encode(job_texts)
        print(f"Computed embeddings for {len(job_texts)} jobs")
    
    def match_cv_with_jobs(
        self,
        cv_data: Dict,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Match a CV with jobs using semantic similarity
        
        Args:
            cv_data: Parsed CV data with skills, experience, etc.
            top_k: Number of top matches to return
            
        Returns:
            List of job recommendations with match scores
        """
        # Initialize model if not done
        if self.model is None:
            self.initialize_model()
        
        if not self.jobs_data:
            return []
        
        # Create CV text representation
        cv_text = self._create_cv_text(cv_data)
        
        # Compute CV embedding
        cv_embedding = self.model.encode([cv_text])
        
        # Calculate similarities
        similarities = cosine_similarity(cv_embedding, self.jobs_embeddings)[0]
        
        # Get top matches (by semantic similarity)
        top_indices = np.argsort(similarities)[::-1][:top_k]

        recommendations = []
        for idx in top_indices:
            job = self.jobs_data[idx].copy()
            match_score = float(similarities[idx])

            # Calculate missing skills
            cv_skills_lower = [s.lower() for s in cv_data.get('skills', [])]
            required_skills = job.get('required_skills', [])
            missing_skills = [
                skill for skill in required_skills
                if skill.lower() not in cv_skills_lower
            ]

            recommendations.append({
                'job_id': job.get('job_id', job.get('rome_code', job.get('id', ''))),
                'title': job.get('title', 'Intitulé non disponible'),
                'description': job.get('description', ''),
                'match_score': match_score,
                'required_skills': required_skills,
                'missing_skills': missing_skills,
                'salary_range': job.get('salary_range'),
                'education_level': job.get('education_level'),
                'is_alternative': False,
                'alternative_reason': None
            })

        # If we have no strong matches, broaden the scope and propose alternatives
        max_score = max([r['match_score'] for r in recommendations]) if recommendations else 0.0

        # Thresholds can be tuned; if top score is low or no recommendations, return alternatives
        if not recommendations or max_score < 0.25:
            # Build alternatives based on skills overlap and title keyword matches
            cv_skills_lower = [s.lower() for s in cv_data.get('skills', [])]

            alt_scores = []
            for job in self.jobs_data:
                req_skills = job.get('required_skills', [])
                if not req_skills:
                    continue

                # Count overlapping skills
                overlap = sum(1 for s in req_skills if any(s.lower() in cs or cs in s.lower() for cs in cv_skills_lower))
                # Normalize by number of required skills
                norm_overlap = overlap / max(1, len(req_skills))

                # Lightweight title match (tokens in common)
                title = job.get('title', '')
                title_tokens = {t.lower() for t in title.split()}
                cv_tokens = set()
                for s in cv_data.get('skills', []):
                    cv_tokens.update([t.lower() for t in s.split()])
                title_match = len(title_tokens & cv_tokens) / max(1, len(title_tokens)) if title_tokens else 0

                # Final alternative score: prefer skill overlap but include title match
                alt_score = 0.75 * norm_overlap + 0.25 * title_match

                if alt_score > 0:
                    alt_scores.append((alt_score, job))

            # Sort alternatives by score and return top_k
            alt_scores.sort(key=lambda x: x[0], reverse=True)

            alternatives = []
            for score, job in alt_scores[:top_k]:
                req_skills = job.get('required_skills', [])
                missing = [skill for skill in req_skills if skill.lower() not in cv_skills_lower]
                alternatives.append({
                    'job_id': job.get('job_id', job.get('rome_code', job.get('id', ''))),
                    'title': job.get('title', 'Intitulé non disponible'),
                    'description': job.get('description', ''),
                    'match_score': float(score),
                    'required_skills': req_skills,
                    'missing_skills': missing,
                    'salary_range': job.get('salary_range'),
                    'education_level': job.get('education_level'),
                    'is_alternative': True,
                    'alternative_reason': 'Compétences proches ou intitulé similaire'
                })

            # If we had some semantic recommendations (but weak), append alternatives after them
            if recommendations:
                # keep existing recommendations but mark as primary even if weak
                return recommendations + alternatives
            else:
                return alternatives

        return recommendations
    
    def _create_cv_text(self, cv_data: Dict) -> str:
        """Create a text representation of the CV for embedding"""
        parts = []
        
        # Add skills
        if cv_data.get('skills'):
            parts.append(f"Compétences: {', '.join(cv_data['skills'])}")
        
        # Add experience
        if cv_data.get('experience_years'):
            parts.append(f"{cv_data['experience_years']} ans d'expérience")
        
        # Add education
        if cv_data.get('education'):
            parts.append(f"Formation: {' '.join(cv_data['education'])}")
        
        # Add summary
        if cv_data.get('summary'):
            parts.append(cv_data['summary'])
        
        return '. '.join(parts)
    
    def recommend_trainings(
        self,
        cv_data: Dict,
        missing_skills: List[str],
        top_k: int = 3
    ) -> List[Dict]:
        """
        Recommend trainings based on missing skills
        
        Args:
            cv_data: Parsed CV data
            missing_skills: Skills that need to be developed
            top_k: Number of trainings to recommend
            
        Returns:
            List of training recommendations
        """
        # Load trainings database
        data_dir = Path(__file__).parent.parent / 'data'
        trainings_file = data_dir / 'formations.json'
        
        if not trainings_file.exists():
            return []
        
        with open(trainings_file, 'r', encoding='utf-8') as f:
            trainings_data = json.load(f)
        
        if not missing_skills:
            # If no missing skills, recommend based on current skills
            missing_skills = cv_data.get('skills', [])[:3]
        
        # Score trainings based on skill overlap
        scored_trainings = []
        missing_skills_lower = [s.lower() for s in missing_skills]
        
        for training in trainings_data:
            training_skills_lower = [s.lower() for s in training.get('skills_acquired', [])]
            
            # Count matching skills
            matches = sum(
                1 for skill in missing_skills_lower
                if any(skill in ts or ts in skill for ts in training_skills_lower)
            )
            
            if matches > 0:
                relevance_score = matches / len(missing_skills_lower)
                scored_trainings.append({
                    **training,
                    'relevance_score': relevance_score
                })
        
        # Sort by relevance and return top K
        scored_trainings.sort(key=lambda x: x['relevance_score'], reverse=True)
        return scored_trainings[:top_k]


# Singleton instance
semantic_matcher = SemanticMatcher()
