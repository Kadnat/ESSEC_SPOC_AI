# 🇫🇷 France Travail API Integration

## Vue d'ensemble

JobMatchAI intègre l'**API officielle France Travail** (ex-Pôle Emploi) pour afficher des **offres d'emploi réelles** en temps réel, matchées avec le profil du candidat.

## 🎯 Fonctionnalités

### 1. Matching Intelligent
Après analyse du CV, l'application :
- ✅ Identifie les métiers ROME correspondants
- ✅ Extrait les compétences clés du candidat
- ✅ Estime le niveau d'expérience
- ✅ Récupère 20 offres réelles ciblées

### 2. Filtres Appliqués
Les offres sont filtrées selon :
- **Codes ROME** : Top 3 métiers recommandés
- **Compétences** : Mots-clés issus du CV
- **Expérience** : Niveau adapté (débutant, 1-2 ans, 2-5 ans, 5+ ans)
- **Tri** : Par date (offres récentes en premier)

### 3. Données Affichées
Chaque offre contient :
- 📋 **Titre** et **description**
- 🏢 **Entreprise** (ou "Entreprise confidentielle")
- 📍 **Localisation** (ville + département)
- 📝 **Type de contrat** (CDI, CDD, alternance, etc.)
- 🎓 **Expérience requise**
- 💰 **Salaire** (si communiqué)
- 🔗 **Lien vers l'offre** sur France Travail
- 📅 **Date de publication**
- 🏷️ **Code ROME**

## 🔧 Configuration

### 1. Inscription à l'API

1. **Créer un compte développeur** :
   - Aller sur [https://francetravail.io/inscription](https://francetravail.io/inscription)
   - Choisir "Candidat" ou "Développeur"
   - Valider l'email

2. **Créer une application** :
   - Aller dans "Mes applications"
   - Cliquer "Nouvelle application"
   - Nom : `JobMatchAI`
   - Description : `Application d'analyse CV et recommandations`
   - Sélectionner l'API : **Offres d'emploi v2**
   - Valider

3. **Récupérer les credentials** :
   - Client ID : `PAR_jobmatchai_xxxxx`
   - Client Secret : `xxxxxxxxxxxxxx`

### 2. Configuration dans JobMatchAI

Éditer le fichier `backend/.env` :

```env
FRANCE_TRAVAIL_CLIENT_ID=PAR_jobmatchai_xxxxx
FRANCE_TRAVAIL_CLIENT_SECRET=xxxxxxxxxxxxxx
```

### 3. Redémarrer le backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8001
```

## 📊 Limites et Quotas

### API Gratuite
- ✅ **Quotas** : Généreux pour usage personnel/académique
- ✅ **Throttling** : 10 requêtes/seconde
- ✅ **Token** : Valide 1499 secondes (cache automatique)

### Données
- 🔄 **Mise à jour** : Quotidienne
- 📈 **Volume** : Plusieurs millions d'offres
- 🇫🇷 **Couverture** : France entière + DOM-TOM

## 🚀 Fonctionnement Technique

### Architecture

```
CV Upload
    ↓
Analyse GPT (extraction)
    ↓
Matching ROME (1584 métiers)
    ↓
Top 3 codes ROME extraits
    ↓
API France Travail
    ├─ OAuth2 Token (cached)
    ├─ Search with filters
    └─ Parse results
    ↓
Affichage 20 offres réelles
```

### Exemple de requête

```python
# Après analyse CV
rome_codes = ['M1805', 'M1806', 'M1810']  # Développeur, Admin sys, Data
skills = ['Python', 'React', 'SQL']
experience = '2'  # 2-5 ans

# Appel API
response = requests.get(
    'https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search',
    headers={'Authorization': f'Bearer {token}'},
    params={
        'codeROME': 'M1805,M1806,M1810',
        'motsCles': 'Python React SQL',
        'experience': '2',
        'range': '0-19',
        'sort': '1'
    }
)
```

### Fallback Mode

Si l'API n'est pas configurée :
- ⚠️ Message d'avertissement au démarrage
- 🎭 Affichage de 2 offres **mock** (démo)
- ✅ Application reste fonctionnelle

## 📖 Documentation Officielle

- **Portail** : [https://francetravail.io](https://francetravail.io)
- **API Offres** : [https://francetravail.io/data/api/offres-emploi](https://francetravail.io/data/api/offres-emploi)
- **Référentiel ROME** : [https://www.data.gouv.fr/fr/datasets/repertoire-operationnel-des-metiers-et-des-emplois-rome/](https://www.data.gouv.fr/fr/datasets/repertoire-operationnel-des-metiers-et-des-emplois-rome/)

## 🎓 Intégration avec ROME

### Synergie parfaite

1. **Base ROME** : 1584 métiers avec codes (M1805, etc.)
2. **Matching sémantique** : CV → Top 5 métiers ROME
3. **API France Travail** : Recherche par code ROME
4. **Résultat** : Offres **ultra-ciblées** pour le candidat

### Exemple de workflow

```
CV : "Développeur Python 3 ans, Django, React"
    ↓
Matching ROME :
    1. M1805 - Études et développement (95%)
    2. M1806 - Conseil et administration (78%)
    3. M1810 - Data Science (72%)
    ↓
API France Travail avec codes M1805, M1806, M1810
    ↓
20 offres réelles :
    - Développeur Full Stack Python/React - Paris - 45K€
    - Data Engineer Python - Lyon - 50K€
    - DevOps Engineer - Remote - 55K€
    - ...
```

## ✅ Avantages pour le Projet ESSEC

### 1. Valeur Ajoutée
- ✨ Passage de **recommandations théoriques** à **opportunités concrètes**
- 🎯 Données officielles et à jour (API gouvernementale)
- 🔗 Liens directs vers candidature

### 2. Démo Impactante
- 💡 "Votre CV analyse → Métiers recommandés → **25 offres réelles en 1 clic**"
- 📊 Statistiques impressionnantes dans la vidéo
- 🚀 Use case complet et concret

### 3. Reproductibilité
- 📦 API gratuite (inscription simple)
- 🔓 Open Data gouvernemental
- 📖 Documentation complète

### 4. Citations
- ✅ Source officielle France Travail
- ✅ License Open Data
- ✅ Intégration légale et éthique

## 🐛 Troubleshooting

### Erreur : "Token failed"
➡️ Vérifier Client ID et Secret dans `.env`

### Erreur : "No results"
➡️ Les codes ROME sont peut-être trop spécifiques
➡️ Essayer sans filtre d'expérience

### Offres en double
➡️ Normal, offres multi-publiées
➡️ Filtrage possible côté frontend

### API lente
➡️ Timeout configuré à 15s
➡️ Fallback automatique vers offres mock

## 📝 TODO Future

- [ ] Filtrage géographique (rayon autour localisation CV)
- [ ] Tri par pertinence (match skills)
- [ ] Cache des offres (éviter appels répétés)
- [ ] Pagination (afficher + de 20 offres)
- [ ] Statistiques (nombre offres par métier ROME)
- [ ] Export PDF avec offres incluses

---

**Développé pour le projet ESSEC AI Course**  
*Date : 1 novembre 2025*
