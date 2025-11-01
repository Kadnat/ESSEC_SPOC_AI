# JobMatchAI 🚀

**JobMatchAI** est une application d'intelligence artificielle qui analyse votre CV et recommande les métiers et formations les plus adaptés à votre profil.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![React](https://img.shields.io/badge/react-19.1-61dafb)

## 📋 Table des matières

- [Aperçu](#aperçu)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Technologies utilisées](#technologies-utilisées)
- [Datasets](#datasets)
- [Modèles IA](#modèles-ia)
- [Prompts IA utilisés](#prompts-ia-utilisés)
- [Contributeurs](#contributeurs)
- [Licence](#licence)

## 🎯 Aperçu

JobMatchAI résout un problème majeur du marché de l'emploi : **le gap entre les compétences des candidats et les opportunités disponibles**. 

Notre solution utilise:
- 🧠 **Matching sémantique** pour comparer votre profil avec des milliers de métiers
- 💬 **LLM (Large Language Models)** pour générer des recommandations personnalisées
- 📊 **Analyse de compétences** pour identifier vos forces et axes d'amélioration
- 🎓 **Suggestions de formations** adaptées à vos objectifs de carrière

## ✨ Fonctionnalités

✅ **Upload de CV** (PDF, DOCX)  
✅ **Extraction automatique** des compétences, expériences, formations  
✅ **Analyse sémantique** avec embeddings (Hugging Face)  
✅ **Recommandations de métiers** avec score de compatibilité  
✅ **Suggestions de formations** personnalisées  
✅ **Insights IA** générés par LLM  
✅ **Interface moderne et responsive**  
✅ **Export des résultats en PDF**  

## 🏗️ Architecture

```
Frontend (React + Vite + Tailwind)
         ↓ HTTP/REST
Backend (FastAPI + Python)
         ↓
AI Models (Hugging Face)
  - sentence-transformers (matching sémantique)
  - Mistral-7B (recommandations LLM)
  - BERT-NER (extraction d'entités)
```

Voir [ARCHITECTURE.md](./ARCHITECTURE.md) pour plus de détails.

## 🚀 Installation

### Prérequis

- **Node.js** 18+ et npm
- **Python** 3.10+
- **Git**

### 1️⃣ Cloner le repository

```bash
git clone https://github.com/votre-username/job-match-ai.git
cd job-match-ai
```

### 2️⃣ Installation Frontend (React)

```bash
# Installer les dépendances
npm install

# Lancer le serveur de développement
npm run dev
```

L'application sera accessible sur `http://localhost:5173`

### 3️⃣ Installation Backend (Python)

```bash
# Aller dans le dossier backend
cd backend

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur macOS/Linux:
source venv/bin/activate
# Sur Windows:
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur FastAPI
python main.py
```

L'API sera accessible sur `http://localhost:8000`

### 4️⃣ Configuration

Créer un fichier `.env` dans le dossier `backend`:

```env
# Hugging Face API Token (optionnel, pour certains modèles)
HF_API_TOKEN=your_token_here

# Mistral AI API Key (si vous utilisez Mistral API)
MISTRAL_API_KEY=your_key_here
```

## 📖 Utilisation

### Via l'interface web

1. **Ouvrir l'application** : `http://localhost:5173`
2. **Télécharger votre CV** (PDF ou DOCX)
3. **Cliquer sur "Analyser mon CV"**
4. **Consulter les résultats** :
   - Compétences extraites
   - Métiers recommandés avec score de compatibilité
   - Formations suggérées
   - Insights IA personnalisés

### Via l'API

```bash
# Upload d'un CV
curl -X POST http://localhost:8000/api/upload-cv \
  -F "file=@/path/to/cv.pdf"

# Analyse complète
curl -X POST http://localhost:8000/api/analyze-cv \
  -F "file=@/path/to/cv.pdf"
```

Voir la documentation interactive de l'API : `http://localhost:8000/docs`

## 🛠️ Technologies utilisées

### Frontend
- **React 19** - Framework UI
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Recharts** - Visualisations

### Backend
- **FastAPI** - Framework API
- **Uvicorn** - ASGI server
- **Pydantic** - Validation de données

### IA/ML
- **Hugging Face Transformers** - Modèles NLP
- **sentence-transformers** - Embeddings sémantiques
- **PyTorch** - Framework ML
- **spaCy** - NLP processing

### Parsing CV
- **PyPDF2** - Extraction PDF
- **python-docx** - Extraction DOCX
- **pdfplumber** - Parsing PDF avancé

## 📊 Datasets

### Sources utilisées

| Dataset | Source | Description | Licence |
|---------|--------|-------------|---------|
| **ROME** | [Pôle Emploi](https://www.pole-emploi.fr/employeur/vos-recrutements/le-rome-et-les-fiches-metiers.html) | Référentiel métiers français | Open License |
| **Job Skills** | [Kaggle](https://www.kaggle.com/) | Compétences par métier | CC BY 4.0 |
| **Formations MOOC** | Données publiques | OpenClassrooms, Coursera, etc. | - |

### Préparation des données

Les datasets sont nettoyés et structurés dans `backend/data/`:
- `jobs.json` - Base de métiers avec embeddings
- `formations.json` - Catalogue de formations
- `skills_taxonomy.json` - Taxonomie des compétences

## 🤖 Modèles IA

### 1. Matching Sémantique
**Modèle** : `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`  
**Source** : [Hugging Face](https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2)  
**Usage** : Créer des embeddings pour CVs et descriptions de métiers  
**Licence** : Apache 2.0

### 2. LLM pour Recommandations
**Modèle** : `mistralai/Mistral-7B-Instruct-v0.2`  
**Source** : [Hugging Face](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2)  
**Usage** : Générer des insights et recommandations personnalisées  
**Licence** : Apache 2.0

### 3. Named Entity Recognition
**Modèle** : `dslim/bert-base-NER`  
**Source** : [Hugging Face](https://huggingface.co/dslim/bert-base-NER)  
**Usage** : Extraire compétences, entreprises, formations du CV  
**Licence** : MIT

## 💡 Prompts IA utilisés

### Prompt ChatGPT pour architecture
```
Je développe une application d'aide à l'emploi avec React et Python.
L'application doit analyser des CVs et recommander des métiers compatibles.
Propose-moi une architecture technique avec FastAPI, Hugging Face, 
et sentence-transformers pour le matching sémantique.
```

### Prompt GitHub Copilot pour parsing CV
```python
# Parse CV PDF and extract:
# - Name, email, phone
# - Skills list
# - Work experience (company, role, duration)
# - Education (degree, school, year)
# - Languages spoken
def parse_cv_pdf(file_path: str) -> CVAnalysis:
```

### Prompt pour génération de recommandations (LLM)
```
Analyse le profil suivant et génère des recommandations de carrière :
- Compétences : {skills}
- Expérience : {experience_years} ans
- Formation : {education}

Format attendu :
1. Analyse du profil (forces/faiblesses)
2. Top 3 métiers recommandés avec justification
3. Compétences manquantes à développer
4. Conseils de carrière personnalisés
```

Voir [AI_PROMPTS.md](./docs/AI_PROMPTS.md) pour la liste complète.

## 👥 Contributeurs

**Projet ESSEC AI Course 2025**

- Votre Nom - Lead Developer
- Membre 2 - Backend & IA
- Membre 3 - Frontend & UX
- Membre 4 - Data & Testing

## 📄 Licence

MIT License - voir [LICENSE](./LICENSE)

## 🙏 Crédits

Voir [CREDITS.md](./CREDITS.md) pour la liste complète des ressources utilisées.

## 📞 Contact

Pour toute question : jobmatchai@essec.edu

---

**⭐ Si ce projet vous plaît, n'hésitez pas à le star !**

Made with ❤️ by ESSEC AI Team
