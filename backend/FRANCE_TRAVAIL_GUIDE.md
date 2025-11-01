# 📥 Guide : Téléchargement des fiches métiers France Travail (PDF)

## 🎯 Objectif
Télécharger les fiches métiers officielles ROME depuis l'API France Travail pour enrichir notre base de données JobMatchAI.

---

## 🔗 Sources officielles

### 1. API France Travail (Nécessite clé API)
```
https://api.francetravail.fr/api-nomenclatureemploi/v1/open-data/pdf
```

**⚠️ Problème** : Les URLs directes (ex: `ROME_M1805.pdf`) retournent 404.

### 2. Data.gouv.fr (Données CSV, pas PDF)
```
https://www.data.gouv.fr/fr/datasets/repertoire-operationnel-des-metiers-et-des-emplois-rome/
```

**Contenu disponible** :
- `unix_referentiel_appellation_v346_utf8.csv` : Tous les titres de métiers
- `unix_referentiel_competence_v346_utf8.csv` : Compétences par métier
- `unix_liens_rome_referentiels_v346_utf8.csv` : Liens entre métiers

---

## 🛠️ Solutions alternatives

### Option A : Télécharger les CSV et parser

```bash
# Télécharger les fichiers CSV depuis data.gouv.fr
cd backend/data

# Référentiel des appellations (titres de métiers)
curl -o rome_appellations.csv "https://www.data.gouv.fr/fr/datasets/r/85abf7bc-0ae2-4684-88f4-6c3a7f7d0462"

# Référentiel des compétences
curl -o rome_competences.csv "https://www.data.gouv.fr/fr/datasets/r/...id-competences..."
```

Puis parser avec Pandas :
```python
import pandas as pd

# Charger les métiers
df_jobs = pd.read_csv('rome_appellations.csv', sep='|')
# Colonnes: code_rome, libelle_appellation, etc.

# Filtrer les métiers tech
tech_codes = ['M1805', 'M1806', 'M1810', ...]
tech_jobs = df_jobs[df_jobs['code_rome'].isin(tech_codes)]
```

### Option B : Scraper le site France Travail

⚠️ **Légal** : Vérifier les CGU avant de scraper.

```python
import requests
from bs4 import BeautifulSoup

def scrape_rome_fiche(code_rome):
    url = f"https://candidat.francetravail.fr/metierscope/fiche-metier/{code_rome}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extraire les sections
    titre = soup.find('h1').text
    description = soup.find('div', class_='description').text
    competences = soup.find_all('li', class_='competence')
    
    return {
        'code_rome': code_rome,
        'titre': titre,
        'description': description,
        'competences': [c.text for c in competences]
    }
```

### Option C : Utiliser l'API France Travail (Inscription requise)

1. **Créer un compte développeur** :
   https://francetravail.io/

2. **S'inscrire à l'API Nomenclature Emploi** :
   https://francetravail.io/produits/api-nomenclature-emploi

3. **Obtenir une clé API** (gratuit pour usage académique)

4. **Appeler l'API** :
```python
import requests

headers = {
    'Authorization': 'Bearer YOUR_API_KEY_HERE'
}

def get_rome_fiche(code_rome):
    url = f"https://api.francetravail.fr/partenaire/nomenclaturerome/v1/metier/{code_rome}"
    response = requests.get(url, headers=headers)
    return response.json()

# Exemple
fiche = get_rome_fiche('M1805')
print(fiche['appellations'])
print(fiche['competences'])
```

### Option D : Utilisation manuelle (Pour projet MVP)

✅ **Recommandé pour JobMatchAI** (projet étudiant, délai court)

1. Visiter : https://candidat.francetravail.fr/metierscope/

2. Chercher manuellement les métiers tech :
   - M1805 : Développement informatique
   - M1808 : Data Science
   - etc.

3. Copier-coller les informations dans notre base structurée

4. **Déjà fait !** ✅ Voir `backend/data/jobs_francetravail.json`

---

## ✅ Ce qui est déjà implémenté

### Fichier créé : `jobs_francetravail.json`

```json
{
  "metadata": {
    "source": "Répertoire ROME - France Travail",
    "total_jobs": 10,
    "license": "Open Data - Licence Ouverte v2.0",
    "url": "https://www.data.gouv.fr/fr/datasets/repertoire-operationnel-des-metiers-et-des-emplois-rome/"
  },
  "jobs": [
    {
      "code_rome": "M1805",
      "title": "Études et développement informatique",
      "required_skills": ["Python", "JavaScript", "Java", ...],
      "activities": ["Analyser les besoins", ...],
      ...
    }
  ]
}
```

### Métiers inclus (10)
1. M1805 - Développement informatique
2. M1806 - Conseil MOA
3. M1810 - DevOps/SRE
4. M1803 - DSI/CTO
5. M1802 - Expert cybersécurité
6. M1704 - Product Manager
7. M1808 - Data Scientist
8. E1104 - Développeur Front-end
9. M1701 - Administrateur BDD
10. K2111 - Formateur IT

---

## 📊 Pour aller plus loin (Après MVP)

### Enrichir la base avec les 500+ métiers ROME

```python
# Script à développer
import pandas as pd

# Télécharger depuis data.gouv.fr
df_rome = pd.read_csv('rome_appellations.csv', sep='|')

# Transformer en format JobMatchAI
for _, row in df_rome.iterrows():
    job = {
        'job_id': f"FT_{row['code_rome']}",
        'code_rome': row['code_rome'],
        'title': row['libelle_appellation'],
        # ... mapper les autres champs
    }
    jobs.append(job)

# Sauvegarder
with open('jobs_complete.json', 'w') as f:
    json.dump(jobs, f, ensure_ascii=False)
```

### Intégrer l'API en temps réel

```python
# Dans semantic_matcher.py
import requests

def get_latest_rome_jobs():
    """Récupère les métiers ROME depuis l'API France Travail"""
    headers = {'Authorization': f'Bearer {API_KEY}'}
    response = requests.get(FRANCE_TRAVAIL_API_URL, headers=headers)
    return response.json()

# Mise à jour automatique chaque semaine
jobs = get_latest_rome_jobs()
save_to_database(jobs)
```

---

## 📝 Citations à inclure dans le rapport

```markdown
### Sources de données

**Répertoire ROME (Répertoire Opérationnel des Métiers et Emplois)**
- Fournisseur : France Travail (Pôle Emploi)
- URL : https://www.data.gouv.fr/fr/datasets/repertoire-operationnel-des-metiers-et-des-emplois-rome/
- License : Open Data - Licence Ouverte v2.0
- Date d'extraction : 2025-11-01
- Nombre de métiers : 10 (sample) / 500+ (complet)
- Format : JSON structuré depuis données ROME v3

**API France Travail**
- Documentation : https://francetravail.io/
- Endpoint : /api-nomenclatureemploi/v1/
- Authentification : OAuth2 (non utilisé dans MVP)
```

---

## 🚀 Prochaines étapes (Post-projet)

1. ✅ **Immédiat** : Utiliser les 10 métiers manuels (FAIT)
2. 📥 **Court terme** : Télécharger les CSV data.gouv.fr et parser
3. 🔑 **Moyen terme** : S'inscrire à l'API France Travail
4. 🤖 **Long terme** : Intégration API en temps réel + cache

---

## ❓ FAQ

**Q: Pourquoi les PDFs ne sont pas accessibles directement ?**
A: L'API nécessite une authentification et les URLs ont changé depuis 2024.

**Q: Faut-il absolument les PDFs ?**
A: Non ! Les CSV sur data.gouv.fr contiennent toutes les infos nécessaires.

**Q: C'est légal d'utiliser ces données ?**
A: Oui, license Open Data. Il faut juste citer la source (fait ✅).

**Q: Combien de métiers dans la base complète ?**
A: ~500 fiches ROME officielles + variantes (appellations).

---

📅 **Dernière mise à jour** : 2025-11-01
👤 **Contact** : Nathanael Blavo - JobMatchAI Team
