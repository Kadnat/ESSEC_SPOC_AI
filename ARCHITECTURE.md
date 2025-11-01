# 🏗️ JobMatchAI - Architecture Technique

## 📊 Vue d'ensemble

**JobMatchAI** est une application d'aide à l'emploi qui utilise l'IA pour analyser des CVs et recommander des métiers ou formations compatibles.

## 🎯 Stack Technique

### Frontend
- **Framework**: React 19 + Vite
- **Styling**: Tailwind CSS
- **État**: React Hooks (useState, useContext)
- **HTTP Client**: Axios
- **Upload**: react-dropzone
- **Visualisations**: Recharts ou Chart.js
- **Export PDF**: jsPDF ou react-pdf

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **CORS**: fastapi-cors
- **Upload**: python-multipart
- **Parsing CV**: 
  - PyPDF2 / pdfplumber (PDF)
  - python-docx (DOCX)
  - pytesseract (OCR si nécessaire)

### Intelligence Artificielle

#### 1. Matching Sémantique
- **Modèle**: `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`
- **Source**: Hugging Face
- **Usage**: Créer embeddings des CVs et descriptions de métiers
- **Similarité**: Cosine similarity

#### 2. LLM pour Recommandations
Options:
- **Option A**: Hugging Face Inference API (Mistral-7B)
- **Option B**: API Mistral AI
- **Option C**: Modèle local (LLaMA, Mistral)

#### 3. Named Entity Recognition (NER)
- **Modèle**: `dslim/bert-base-NER-uncased` ou équivalent français
- **Usage**: Extraire compétences, expériences, formations

## 🗄️ Données

### Sources de Données
1. **Référentiel ROME** (Pôle Emploi)
   - ~500 fiches métiers
   - Compétences associées
   - Niveau d'études requis

2. **Dataset Kaggle**
   - Job descriptions
   - Skills database

3. **Base de Formations**
   - MOOC (Coursera, OpenClassrooms, FUN)
   - Certifications professionnelles

### Structure des Données

```json
{
  "jobs": [
    {
      "id": "M1805",
      "title": "Développeur Full Stack",
      "description": "Concevoir et développer des applications web...",
      "skills": ["JavaScript", "React", "Node.js", "SQL"],
      "education_level": "Bac+3",
      "experience_required": "2-5 ans",
      "salary_range": "35-50k€",
      "embedding": [0.123, -0.456, ...]
    }
  ],
  "formations": [
    {
      "id": "F001",
      "title": "Formation React Avancé",
      "provider": "OpenClassrooms",
      "url": "https://...",
      "duration": "40h",
      "skills_acquired": ["React", "Redux", "Testing"]
    }
  ]
}
```

## 🔄 Architecture Système

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Upload CV   │  │  Dashboard   │  │  Results     │      │
│  │  Component   │  │  Component   │  │  Component   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/REST API
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    BACKEND API (FastAPI)                     │
│                                                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │             Endpoints                               │     │
│  │  • POST /api/upload-cv                             │     │
│  │  • POST /api/analyze-cv                            │     │
│  │  • GET  /api/recommend-jobs                        │     │
│  │  • GET  /api/recommend-trainings                   │     │
│  └────────────────────────────────────────────────────┘     │
│                            │                                  │
│  ┌────────────────────────▼────────────────────────────┐    │
│  │           Services Layer                             │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐│    │
│  │  │ CV Parser    │  │ Semantic     │  │ LLM       ││    │
│  │  │ Service      │  │ Matcher      │  │ Service   ││    │
│  │  └──────────────┘  └──────────────┘  └───────────┘│    │
│  └─────────────────────────────────────────────────────┘    │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                  AI Models (Hugging Face)                    │
│                                                               │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │ sentence-transformers │  │ Mistral-7B-Instruct │        │
│  │ (Embeddings)          │  │ (Recommendations)   │        │
│  └──────────────────────┘  └──────────────────────┘        │
└───────────────────────────────────────────────────────────────┘
```

## 📁 Structure du Projet

```
job-match-ai/
├── frontend/                  # Application React
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadCV.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── JobCard.jsx
│   │   │   ├── TrainingCard.jsx
│   │   │   └── ResultsView.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
│
├── backend/                   # API FastAPI
│   ├── app/
│   │   ├── main.py           # Point d'entrée FastAPI
│   │   ├── routers/
│   │   │   ├── cv_upload.py
│   │   │   └── recommendations.py
│   │   ├── services/
│   │   │   ├── cv_parser.py
│   │   │   ├── semantic_matcher.py
│   │   │   └── llm_service.py
│   │   ├── models/
│   │   │   └── schemas.py
│   │   └── utils/
│   │       └── embeddings.py
│   ├── data/
│   │   ├── jobs.json
│   │   └── formations.json
│   ├── requirements.txt
│   └── Dockerfile
│
├── data/                      # Datasets
│   ├── rome_referentiel.csv
│   ├── jobs_database.json
│   └── formations_database.json
│
├── docs/                      # Documentation
│   ├── ARCHITECTURE.md
│   ├── USER_GUIDE.md
│   └── AI_PROMPTS.md
│
├── CREDITS.md                 # Citations
└── README.md
```

## 🔐 Sécurité et Performance

### Sécurité
- Validation des fichiers uploadés (type, taille)
- Limitation du taux de requêtes (rate limiting)
- Sanitisation des inputs
- HTTPS en production

### Performance
- Cache des embeddings calculés
- Utilisation de GPU si disponible
- Pagination des résultats
- Compression des réponses API

## 🚀 Déploiement

### Option 1: Déploiement Séparé
- **Frontend**: Vercel ou Netlify
- **Backend**: Render, Railway, ou Hugging Face Spaces

### Option 2: Tout-en-un
- **Streamlit** ou **Gradio** sur Hugging Face Spaces

## 📈 Métriques de Succès

1. **Précision du matching**: >80% de recommandations pertinentes
2. **Temps de réponse**: <5 secondes pour l'analyse complète
3. **Taux de conversion**: Utilisateurs téléchargeant les recommandations
4. **Satisfaction utilisateur**: Feedback positif >4/5

## 🔄 Pipeline de Traitement

```
1. Upload CV (PDF/DOCX)
   ↓
2. Extraction de texte (PyPDF2/python-docx)
   ↓
3. Parsing et structuration (NER)
   ↓
4. Création d'embeddings (sentence-transformers)
   ↓
5. Matching sémantique avec base métiers (cosine similarity)
   ↓
6. Génération de recommandations personnalisées (LLM)
   ↓
7. Suggestion de formations complémentaires
   ↓
8. Présentation des résultats (Frontend)
```

## 🛠️ Technologies Clés

| Catégorie | Technologie | Source | Licence |
|-----------|------------|--------|---------|
| Frontend | React 19 | npm | MIT |
| UI | Tailwind CSS | npm | MIT |
| Backend | FastAPI | PyPI | MIT |
| Embeddings | sentence-transformers | Hugging Face | Apache 2.0 |
| LLM | Mistral-7B | Hugging Face | Apache 2.0 |
| NER | bert-base-NER | Hugging Face | MIT |
| Data | ROME Pôle Emploi | data.gouv.fr | Open License |

## 📚 Références

- [Hugging Face Transformers](https://huggingface.co/docs/transformers)
- [Sentence Transformers](https://www.sbert.net/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [ROME Pôle Emploi](https://www.pole-emploi.fr/employeur/vos-recrutements/le-rome-et-les-fiches-metiers.html)

---

*Document créé le: 1er novembre 2025*
*Dernière mise à jour: 1er novembre 2025*
