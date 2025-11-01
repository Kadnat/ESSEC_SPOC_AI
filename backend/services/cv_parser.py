"""
CV Parser Service with GPT Enhancement
Extract and structure information from PDF and DOCX files

Strategy:
1. Extract raw text from PDF/DOCX
2. Send to GPT for intelligent parsing and structuring
3. Return clean, structured CV data

Uses:
- PyPDF2 for PDF extraction
- python-docx for DOCX extraction
- OpenAI GPT-4o-mini for intelligent text structuring
"""

import re
import os
import json
from typing import Dict, List, Optional
import io
from openai import OpenAI

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import docx
except ImportError:
    docx = None


class CVParser:
    """Parse CV files and extract structured information using GPT"""
    
    def __init__(self):
        # Initialize OpenAI client
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            self.gpt_available = True
        else:
            print("⚠️  Warning: OPENAI_API_KEY not found. CV parsing will use basic regex.")
            self.client = None
            self.gpt_available = False
        
        # Fallback patterns (si GPT non disponible)
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(\+33|0)[1-9](\s?\d{2}){4}'
        
        # Fallback skill keywords for regex-based extraction
        self.tech_skills = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
            'node.js', 'nodejs', 'express', 'django', 'flask', 'fastapi',
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'machine learning', 'deep learning', 'tensorflow', 'pytorch',
            'git', 'ci/cd', 'agile', 'scrum',
            'html', 'css', 'tailwind', 'bootstrap',
            'rest api', 'graphql', 'microservices'
        ]
        
    def parse_file(self, file_content: bytes, content_type: str) -> Dict:
        """
        Parse CV file and extract information using GPT
        
        Args:
            file_content: Binary content of the file
            content_type: MIME type of the file
            
        Returns:
            Dictionary with extracted CV information
        """
        # Step 1: Extract raw text based on file type
        if 'pdf' in content_type.lower():
            text = self._extract_text_from_pdf(file_content)
        elif 'word' in content_type.lower() or 'docx' in content_type.lower():
            text = self._extract_text_from_docx(file_content)
        else:
            raise ValueError(f"Unsupported file type: {content_type}")
        
        # Step 2: Use GPT to structure the text (if available)
        if self.gpt_available and text.strip():
            try:
                cv_data = self._parse_with_gpt(text)
                cv_data['raw_text'] = text  # Keep original text
                return cv_data
            except Exception as e:
                print(f"⚠️  GPT parsing failed: {e}. Falling back to regex.")
                # Fallback to regex if GPT fails
                return self._parse_with_regex(text)
        else:
            # Fallback to regex parsing
            return self._parse_with_regex(text)
    
    def _extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        if PyPDF2 is None:
            raise ImportError("PyPDF2 is not installed. Install it with: pip install PyPDF2")
        
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            raise ValueError(f"Error extracting text from PDF: {str(e)}")
    
    def _extract_text_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX file"""
        if docx is None:
            raise ImportError("python-docx is not installed. Install it with: pip install python-docx")
        
        try:
            docx_file = io.BytesIO(file_content)
            doc = docx.Document(docx_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            raise ValueError(f"Error extracting text from DOCX: {str(e)}")
    
    def _parse_with_gpt(self, text: str) -> Dict:
        """
        Use GPT to intelligently parse and structure CV text
        
        Args:
            text: Raw CV text
            
        Returns:
            Structured CV data dictionary
        """
        prompt = f"""Tu es un expert en analyse de CV. Extrais les informations suivantes du CV ci-dessous et retourne-les au format JSON strict.

Structure JSON attendue :
{{
    "name": "Prénom NOM du candidat",
    "email": "email@example.com",
    "phone": "numéro de téléphone",
    "skills": ["compétence1", "compétence2", "compétence3"],
    "experience_years": nombre d'années d'expérience (nombre entier),
    "education": ["Diplôme 1", "Diplôme 2"],
    "languages": ["langue1", "langue2"],
    "summary": "Résumé du profil en 2-3 phrases"
}}

Instructions :
- Si une information est absente, utilise null ou [] selon le type
- Pour experience_years, estime à partir des dates d'expériences mentionnées
- Pour skills, liste les compétences techniques et soft skills importantes
- Pour education, liste les diplômes obtenus (TABLEAU de strings)
- Pour languages, liste les langues avec leur niveau si mentionné
- Pour summary, résume le profil professionnel en 2-3 phrases maximum

CV à analyser :
---
{text[:4000]}
---

Réponds UNIQUEMENT avec le JSON, sans texte avant ou après."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Tu es un assistant qui extrait des données structurées de CV. Tu réponds UNIQUEMENT en JSON valide."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Low temperature for consistent extraction
                max_tokens=1000
            )
            
            # Parse JSON response
            json_str = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if json_str.startswith('```'):
                json_str = json_str.split('```')[1]
                if json_str.startswith('json'):
                    json_str = json_str[4:]
                json_str = json_str.strip()
            
            cv_data = json.loads(json_str)
            
            # Ensure all expected fields exist with correct types
            cv_data.setdefault('name', None)
            cv_data.setdefault('email', None)
            cv_data.setdefault('phone', None)
            cv_data.setdefault('skills', [])
            cv_data.setdefault('experience_years', 0)
            cv_data.setdefault('languages', [])
            cv_data.setdefault('summary', None)
            
            # Ensure education is always a list
            education = cv_data.get('education')
            if education is None:
                cv_data['education'] = []
            elif isinstance(education, str):
                # Convert string to list
                cv_data['education'] = [education] if education.strip() else []
            elif not isinstance(education, list):
                cv_data['education'] = []
            
            print(f"✅ GPT successfully parsed CV: {cv_data.get('name', 'Unknown')}")
            return cv_data
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Failed to parse GPT JSON response: {e}")
            raise
        except Exception as e:
            print(f"⚠️  GPT API error: {e}")
            raise
    
    def _parse_with_regex(self, text: str) -> Dict:
        """
        Fallback: Parse CV using regex patterns (basic extraction)
        
        Args:
            text: Raw CV text
            
        Returns:
            Structured CV data dictionary
        """
        print("⚠️  Using fallback regex parsing (GPT unavailable)")
        cv_data = {
            'name': self._extract_name(text),
            'email': self._extract_email(text),
            'phone': self._extract_phone(text),
            'skills': self._extract_skills(text),
            'experience_years': self._estimate_experience_years(text),
            'education': self._extract_education(text),
            'languages': self._extract_languages(text),
            'summary': self._generate_summary(text)
        }
        return cv_data
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text"""
        match = re.search(self.email_pattern, text)
        return match.group(0) if match else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text"""
        match = re.search(self.phone_pattern, text)
        return match.group(0) if match else None
    
    def _extract_name(self, text: str) -> Optional[str]:
        """
        Extract name from CV (usually first line)
        This is a simple heuristic - can be improved with NER
        """
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            # Name is usually short and contains only letters
            if line and len(line.split()) <= 4 and re.match(r'^[A-Za-zÀ-ÿ\s\-]+$', line):
                return line
        return None
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from text"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.tech_skills:
            if skill.lower() in text_lower:
                # Capitalize properly
                found_skills.append(skill.title() if ' ' not in skill else skill)
        
        # Remove duplicates and sort
        return sorted(list(set(found_skills)))
    
    def _estimate_experience_years(self, text: str) -> Optional[int]:
        """
        Estimate years of experience
        Look for patterns like "5 ans d'expérience", "2 years of experience"
        """
        patterns = [
            r'(\d+)\s*(ans?|years?)\s*(d.expérience|of experience)',
            r'(expérience|experience)\s*:\s*(\d+)\s*(ans?|years?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                # Extract the number from any group
                for group in match.groups():
                    if group and group.isdigit():
                        return int(group)
        
        return None
    
    def _extract_education(self, text: str) -> List[str]:
        """Extract education/diplomas"""
        education_keywords = [
            'master', 'licence', 'bachelor', 'doctorat', 'phd',
            'bts', 'dut', 'bac+', 'ingénieur', 'mba'
        ]
        
        education = []
        lines = text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            for keyword in education_keywords:
                if keyword in line_lower and len(line.strip()) < 100:
                    education.append(line.strip())
                    break
        
        return education[:3]  # Return max 3 entries
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extract spoken languages"""
        language_keywords = {
            'français': 'Français',
            'french': 'Français',
            'anglais': 'Anglais',
            'english': 'Anglais',
            'espagnol': 'Espagnol',
            'spanish': 'Espagnol',
            'allemand': 'Allemand',
            'german': 'Allemand',
            'italien': 'Italien',
            'italian': 'Italien',
            'chinois': 'Chinois',
            'chinese': 'Chinois',
            'arabe': 'Arabe',
            'arabic': 'Arabe'
        }
        
        text_lower = text.lower()
        languages = []
        
        for keyword, language in language_keywords.items():
            if keyword in text_lower and language not in languages:
                languages.append(language)
        
        return languages
    
    def _generate_summary(self, text: str) -> str:
        """
        Generate a brief summary of the CV
        For now, extract first meaningful paragraph
        """
        lines = text.split('\n')
        
        # Skip empty lines and very short lines
        for line in lines:
            line = line.strip()
            if len(line) > 50 and not re.match(r'^[A-Z\s]+$', line):
                # Found a substantial paragraph
                return line[:200] + '...' if len(line) > 200 else line
        
        return "Professionnel expérimenté"


# Singleton instance
cv_parser = CVParser()
