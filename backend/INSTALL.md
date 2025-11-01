# 🚀 Guide d'installation rapide - JobMatchAI Backend

## Installation Python

```bash
# 1. Créer l'environnement virtuel
python3 -m venv venv

# 2. Activer l'environnement
source venv/bin/activate  # macOS/Linux
# OU
venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install --upgrade pip
pip install fastapi uvicorn python-dotenv openai PyPDF2 python-docx

# Installation complète (avec ML)
pip install -r requirements.txt
```

## Installation rapide (sans ML pour test)

Si vous voulez tester rapidement SANS télécharger les modèles ML (2GB+):

```bash
pip install fastapi uvicorn python-dotenv openai PyPDF2 python-docx pydantic aiofiles
```

## Lancer le serveur

```bash
python main.py
```

Le backend sera accessible sur: **http://localhost:8001**

## Tester l'API

Ouvrir dans le navigateur:
- Documentation: http://localhost:8001/docs
- Health check: http://localhost:8001/api/health

## Configuration OpenAI

Le fichier `.env` contient déjà votre clé API OpenAI.

**Note**: Le modèle `gpt-4o-mini` sera utilisé pour générer les insights IA.

## Données disponibles

- ✅ 20 métiers dans `data/jobs.json`
- ✅ 12 formations dans `data/formations.json`  
- ✅ Données ROME/ONISEP dans `data/rome_onisep_data.json`

## Prochaines étapes

1. Uploader un CV depuis le frontend (http://localhost:5174)
2. Voir les recommandations avec insights GPT
3. Tester avec différents profils

## Troubleshooting

**Erreur: Module 'sentence_transformers' not found**
→ Normal si installation rapide. Le matching sémantique sera moins précis mais fonctionnel.

**Erreur: OpenAI API**
→ Vérifier que la clé API est valide dans `.env`

**Port 8001 déjà utilisé**
→ Changer le port dans `main.py` (ligne: `port=8001`)
