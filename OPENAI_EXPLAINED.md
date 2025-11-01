# 🤖 Architecture IA de JobMatchAI - Explication détaillée

## 📊 Vue d'ensemble du pipeline

JobMatchAI utilise **3 couches d'intelligence artificielle** qui travaillent ensemble :

```
CV Upload
   ↓
[1] CV Parser (Regex + NLP)
   ↓
[2] Semantic Matcher (sentence-transformers)
   ↓
[3] LLM OpenAI GPT-4o-mini
   ↓
Recommandations personnalisées
```

---

## 1️⃣ CV Parser - Extraction de données

### 🎯 Rôle
Extraire les informations structurées d'un CV (PDF/DOCX)

### 🔧 Technologie
- **PyPDF2** / **python-docx** : Extraction du texte brut
- **Regex** : Patterns pour email, téléphone, compétences

### 📤 Output
```json
{
  "name": "Jean Dupont",
  "email": "jean.dupont@email.com",
  "phone": "+33 6 12 34 56 78",
  "skills": ["Python", "JavaScript", "React", "SQL"],
  "raw_text": "Développeur Full-Stack avec 3 ans d'expérience..."
}
```

### ⚠️ Limitation
Extraction basique, pas de compréhension sémantique.

---

## 2️⃣ Semantic Matcher - Matching CV/Métiers

### 🎯 Rôle
**Calculer la similarité sémantique** entre le CV et les métiers disponibles.

### 🔧 Technologie
**Sentence-Transformers** (Hugging Face)
- Modèle : `paraphrase-multilingual-mpnet-base-v2`
- Support multilingue (français inclus)
- Embedding : 768 dimensions

### 📐 Comment ça marche ?

1. **Création des embeddings (vecteurs)**
   ```python
   # CV devient un vecteur de 768 nombres
   cv_embedding = model.encode("Développeur Python avec expérience en ML")
   # [0.23, -0.45, 0.78, ..., 0.12]  # 768 dimensions
   
   # Chaque métier aussi
   job_embedding = model.encode("Data Scientist - Python, ML, Stats")
   # [0.25, -0.42, 0.80, ..., 0.15]
   ```

2. **Calcul de similarité cosine**
   ```python
   similarity = cosine_similarity(cv_embedding, job_embedding)
   # Result: 0.85 = 85% de match
   ```

3. **Détection des compétences manquantes**
   ```python
   missing_skills = job.required_skills - cv.skills
   # ["Machine Learning", "Statistiques"]
   ```

### 📤 Output
```json
{
  "job_recommendations": [
    {
      "job_id": "FT_M1808",
      "title": "Data Scientist",
      "match_score": 0.85,
      "missing_skills": ["Machine Learning", "Statistiques", "Pandas"]
    },
    {
      "job_id": "FT_M1805",
      "title": "Développeur Full-Stack",
      "match_score": 0.92,
      "missing_skills": ["Docker", "Kubernetes"]
    }
  ]
}
```

### ✅ Avantages
- **Compréhension sémantique** : "développeur" match avec "ingénieur logiciel"
- **Multilingue** : Fonctionne en français
- **Rapide** : Calcul en quelques millisecondes
- **Open-source** : Hugging Face, pas de coût API

### ⚠️ Limitation
- Donne des scores numériques, **PAS d'explications en langage naturel**
- Ne génère pas de conseils personnalisés

---

## 3️⃣ OpenAI GPT-4o-mini - Génération d'insights

### 🎯 Rôle Principal
**Transformer les données techniques en conseils humains et personnalisés.**

C'est le **conseiller en orientation virtuel** qui :
- Analyse le profil du candidat
- Explique POURQUOI tel métier correspond
- Donne des conseils concrets pour progresser
- Recommande des formations adaptées

### 🔧 Technologie
- **Modèle** : GPT-4o-mini (OpenAI)
- **API** : OpenAI REST API
- **Coût** : ~0.15$ pour 1M tokens d'input (très économique)

### 💡 Pourquoi GPT-4o-mini et pas un autre LLM ?

| Critère | GPT-4o-mini | GPT-4 | Mistral | LLaMA |
|---------|-------------|-------|---------|-------|
| **Qualité français** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Coût** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Vitesse** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Facilité setup** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |

**Choix** : GPT-4o-mini offre le **meilleur rapport qualité/prix/vitesse** pour un projet étudiant.

### 📝 Le prompt système

```python
SYSTEM_PROMPT = """
Tu es un conseiller en orientation professionnelle expert.

Ton rôle :
1. Analyser le profil du candidat
2. Expliquer pourquoi les métiers recommandés correspondent
3. Identifier les compétences à développer
4. Suggérer un plan d'action concret
5. Encourager et motiver le candidat

Ton style :
- Bienveillant et encourageant
- Concret et actionnable
- En français professionnel
- Structuré (avec émojis si approprié)
"""
```

### 🔄 Workflow GPT

```python
# 1. Préparer le contexte
context = f"""
Profil candidat:
- Compétences: {cv.skills}
- Expérience: {cv.experience}

Métiers recommandés:
- {job1.title} (92% match, manque: Docker, K8s)
- {job2.title} (85% match, manque: ML, Stats)
"""

# 2. Appeler GPT
response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": context}
    ],
    temperature=0.7  # Créativité modérée
)

# 3. Récupérer les insights
insights = response.choices[0].message.content
```

### 📤 Output GPT (Exemple)

```markdown
## 🎯 Votre Profil

Bonjour ! Votre profil de développeur Python avec une expertise en React 
est très recherché sur le marché. Vos compétences sont un excellent 
tremplin vers plusieurs métiers tech.

## 💼 Métiers Recommandés

### 1. Développeur Full-Stack (92% de correspondance) ⭐
**Pourquoi ce métier vous correspond :**
- Vous maîtrisez déjà Python et React, les deux piliers du développement 
  full-stack moderne
- Votre expérience en API REST est un atout majeur
- Le travail en Agile que vous pratiquez est standard dans ce métier

**Compétences à acquérir :**
- **Docker** : Conteneurisation d'applications (2-3 semaines)
- **Kubernetes** : Orchestration de containers (1-2 mois)

**Plan d'action :**
1. Suivez le cours "Docker Mastery" sur Udemy (10h)
2. Pratiquez avec des projets perso sur GitHub
3. Certifiez-vous : Docker Certified Associate

---

### 2. Data Scientist (85% de correspondance) 🔬
**Pourquoi ce métier vous correspond :**
- Python est LE langage de la data science
- Votre logique de développeur facilite l'apprentissage du ML
- Les opportunités sont nombreuses et bien rémunérées

**Compétences à acquérir :**
- **Machine Learning** : Scikit-learn, TensorFlow (3-4 mois)
- **Statistiques** : Bases mathématiques (2-3 mois)
- **Pandas/NumPy** : Manipulation de données (1 mois)

**Plan d'action :**
1. "Machine Learning A-Z" sur Udemy
2. Projets Kaggle pour pratiquer
3. Certification Google Data Analytics

## 📚 Formations Recommandées

1. **Docker pour les développeurs** - Udemy
   - Durée : 12h | Prix : 19.99€
   - [Lien vers la formation]

2. **Machine Learning avec Python** - OpenClassrooms
   - Durée : 3 mois | Certificat : Oui
   - [Lien vers la formation]

## 🚀 Conclusion

Vous avez déjà 92% des compétences pour devenir développeur full-stack ! 
Avec quelques semaines de formation Docker/K8s, vous serez opérationnel. 

Pour la data science, c'est une belle reconversion possible en 6 mois 
d'apprentissage structuré. 

Je vous recommande de commencer par le full-stack (plus rapide) puis 
d'évoluer vers la data si ça vous passionne. 🎓
```

### ✅ Valeur ajoutée d'OpenAI

Sans GPT, l'utilisateur verrait :
```
Job: Développeur Full-Stack
Match: 92%
Missing: Docker, Kubernetes
```

Avec GPT, il reçoit :
- ✅ Une **explication personnalisée**
- ✅ Un **plan d'action concret**
- ✅ Des **formations recommandées**
- ✅ De la **motivation et encouragement**
- ✅ Une **priorisation** des apprentissages

C'est comme avoir un **vrai conseiller d'orientation** disponible 24/7 !

---

## 🆚 Comparaison : Avec vs Sans OpenAI

### Sans OpenAI (Juste Semantic Matcher)
```json
{
  "job": "Data Scientist",
  "score": 0.85,
  "missing": ["ML", "Stats", "Pandas"]
}
```
→ **Froid, technique, peu actionnable**

### Avec OpenAI
```markdown
Votre profil Python est parfait pour la data science ! 
Voici comment y arriver en 6 mois :
1. Apprenez ML avec le cours X
2. Pratiquez sur Kaggle
3. Certifiez-vous
```
→ **Humain, motivant, actionnable**

---

## 💰 Coûts OpenAI (Estimations)

| Usage | Tokens | Coût |
|-------|--------|------|
| 1 analyse CV | ~2000 tokens | 0.0003$ |
| 100 analyses | 200k tokens | 0.03$ |
| 1000 analyses | 2M tokens | 0.30$ |

**Verdict** : Quasi-gratuit pour un projet étudiant !

---

## 📊 Sources de données - France Travail

### Base de données ROME (Répertoire Opérationnel des Métiers et Emplois)

**Source officielle** : France Travail (ex-Pôle Emploi)

#### 🔗 Liens
- **Data.gouv.fr** : https://www.data.gouv.fr/fr/datasets/repertoire-operationnel-des-metiers-et-des-emplois-rome/
- **API France Travail** : https://api.francetravail.fr/api-nomenclatureemploi/v1/open-data/pdf
- **License** : Open Data - Licence Ouverte v2.0

#### 📄 Contenu
- **500+ fiches métiers** officielles
- **Codes ROME** : M1805 (Développement info), M1808 (Data), etc.
- **Structure** :
  - Définition du métier
  - Compétences requises
  - Conditions d'accès
  - Appellations (variantes du titre)
  - Activités principales

#### ✅ Pourquoi utiliser France Travail ?
1. **Données officielles** : Reconnues par l'État français
2. **Mise à jour régulière** : Suivi du marché de l'emploi
3. **Crédibilité** : Citation légitime pour projet académique
4. **Open Data** : Gratuit et réutilisable

#### 📥 Notre extraction
```bash
backend/data/jobs_francetravail.json
```
- **10 métiers tech/data** extraits
- **Format structuré** pour JobMatchAI
- **Attribution complète** : Source, license, date

---

## 🎓 Résumé pour le rapport académique

### Architecture IA en 3 couches :

1. **CV Parser** (PyPDF2 + Regex)
   → Extraction de données brutes

2. **Semantic Matcher** (Sentence-Transformers, Hugging Face)
   → Calcul de similarité sémantique (scores quantitatifs)
   → **Open-source, gratuit, rapide**

3. **LLM OpenAI GPT-4o-mini**
   → Génération d'insights personnalisés (conseils qualitatifs)
   → **Valeur ajoutée : humanisation des recommandations**

### Sources de données :
- **France Travail** : Base ROME (métiers officiels)
- **Formations** : Udemy, OpenClassrooms, Coursera, DataCamp

### Citations :
- Sentence-Transformers : Reimers & Gurevych (2019)
- OpenAI GPT : Brown et al. (2020)
- Données ROME : France Travail - data.gouv.fr

---

## ❓ FAQ

**Q: Pourquoi ne pas utiliser seulement sentence-transformers ?**
A: Il donne des scores (85%), pas des conseils humains. OpenAI humanise l'expérience.

**Q: Pourquoi ne pas utiliser seulement GPT ?**
A: GPT seul est lent et coûteux pour matcher 500 métiers. Sentence-transformers fait le tri rapide.

**Q: Et si on n'a pas de budget OpenAI ?**
A: Alternatives gratuites : Mistral API, Hugging Face Inference API, ou modèles locaux (LLaMA).

**Q: Les données France Travail sont-elles à jour ?**
A: ROME v3 (2023), mises à jour régulières. Pour un projet temps réel, utiliser l'API officielle.

---

📝 **Document créé pour** : JobMatchAI - Projet ESSEC AI Course
📅 **Date** : 2025-11-01
👤 **Auteur** : Nathanael Blavo
