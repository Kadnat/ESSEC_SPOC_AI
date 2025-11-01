"""
Parser XML complet des fiches métiers ROME (France Travail)
Source: Fichier officiel unix_fiche_emploi_metier_v460_iso8859-15.xml

Ce script extrait TOUTES les fiches métiers du ROME (~532 métiers) 
et les transforme en format JSON pour JobMatchAI.

Auteur: JobMatchAI Team
Date: 2025-11-01
"""

import xml.etree.ElementTree as ET
import json
from pathlib import Path
from collections import defaultdict

# Configuration
DATA_DIR = Path(__file__).parent.parent / "data"
XML_FILE = DATA_DIR / "unix_fiche_emploi_metier_v460_iso8859-15.xml"
OUTPUT_FILE = DATA_DIR / "jobs_rome_complete.json"

# Catégories tech/digital prioritaires pour filtrage rapide
TECH_CATEGORIES = {
    'M': 'Support à l\'entreprise',  # Informatique, gestion, commerce
    'H': 'Industrie',  # Ingénierie, R&D
    'K': 'Services à la personne et à la collectivité',  # Formation
    'E': 'Communication, média et multimédia'
}


def parse_rome_xml(xml_file, filter_tech_only=False):
    """
    Parse le fichier XML ROME et extrait toutes les fiches métiers
    
    Args:
        xml_file: Chemin vers le fichier XML
        filter_tech_only: Si True, ne garde que les métiers tech/digital (M, H, K, E)
    
    Returns:
        Liste de dictionnaires avec les données métiers
    """
    print(f"📖 Parsing du fichier XML: {xml_file.name}")
    print(f"🔍 Filtrage tech: {'Oui' if filter_tech_only else 'Non'}\n")
    
    # Parser le XML
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    jobs = []
    skipped = 0
    
    # Parcourir toutes les fiches
    for fiche in root.findall('fiche_metier'):
        # Extraction des données de base
        code_rome = fiche.find('rome/code_rome').text if fiche.find('rome/code_rome') is not None else None
        
        if not code_rome:
            skipped += 1
            continue
        
        # Filtrer par catégorie si demandé
        if filter_tech_only:
            category = code_rome[0]  # Premier caractère (M, H, K, etc.)
            if category not in TECH_CATEGORIES:
                skipped += 1
                continue
        
        # Titre principal
        intitule = fiche.find('rome/intitule')
        title = intitule.text if intitule is not None else f"Métier {code_rome}"
        
        # Définition
        definition_elem = fiche.find('definition')
        definition = definition_elem.text if definition_elem is not None else ""
        
        # Conditions d'accès
        acces_elem = fiche.find('acces_metier')
        acces = acces_elem.text if acces_elem is not None else ""
        
        # Appellations (variantes du titre)
        appellations = []
        appellations_elem = fiche.find('appellations')
        if appellations_elem is not None:
            for appellation in appellations_elem.findall('appellation'):
                libelle = appellation.find('libelle')
                if libelle is not None and libelle.text:
                    appellations.append(libelle.text)
        
        # Compétences (savoir-faire)
        skills = []
        competences_elem = fiche.find('competences/savoir_faire/enjeux')
        if competences_elem is not None:
            for enjeu in competences_elem.findall('enjeu'):
                items = enjeu.find('items')
                if items is not None:
                    for item in items.findall('item'):
                        libelle = item.find('libelle')
                        coeur_metier = item.find('coeur_metier')
                        
                        if libelle is not None and libelle.text:
                            skill = {
                                'skill': libelle.text,
                                'core': coeur_metier.text == 'Principale' if coeur_metier is not None else False
                            }
                            skills.append(skill)
        
        # Séparer compétences principales et secondaires
        required_skills = [s['skill'] for s in skills if s['core']][:15]  # Max 15
        optional_skills = [s['skill'] for s in skills if not s['core']][:10]  # Max 10
        
        # Construction de l'objet métier
        job = {
            'job_id': f'ROME_{code_rome}',
            'code_rome': code_rome,
            'title': title,
            'category': TECH_CATEGORIES.get(code_rome[0], 'Autre') if filter_tech_only else 'Divers',
            'description': definition[:500] if definition else f"Fiche métier {title}",
            'required_skills': required_skills,
            'optional_skills': optional_skills,
            'appellations': appellations[:8],  # Max 8 variantes
            'access_conditions': acces[:300] if acces else "",
            'remote_friendly': 'informatique' in title.lower() or 'digital' in title.lower() or 'data' in title.lower(),
            'education_level': 'Variable',
            'salary_range': 'Variable'
        }
        
        jobs.append(job)
        
        # Afficher progression tous les 50 métiers
        if len(jobs) % 50 == 0:
            print(f"   ⏳ {len(jobs)} métiers extraits...")
    
    print(f"\n✅ Extraction terminée:")
    print(f"   📊 Métiers extraits: {len(jobs)}")
    print(f"   ⏭️  Métiers ignorés: {skipped}")
    
    return jobs


def save_to_json(jobs, output_file):
    """Sauvegarde les métiers en JSON"""
    output_data = {
        'metadata': {
            'source': 'Répertoire Opérationnel des Métiers et des Emplois (ROME)',
            'version': 'v4.60',
            'provider': 'France Travail (Pôle Emploi)',
            'url': 'https://www.data.gouv.fr/fr/datasets/repertoire-operationnel-des-metiers-et-des-emplois-rome/',
            'license': 'Open Data - Licence Ouverte v2.0',
            'date_extraction': '2025-11-01',
            'total_jobs': len(jobs),
            'attribution': 'Données officielles France Travail - ROME v4.60',
            'xml_source': 'unix_fiche_emploi_metier_v460_iso8859-15.xml'
        },
        'jobs': jobs
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 Fichier créé: {output_file}")
    print(f"📦 Taille: {output_file.stat().st_size / 1024:.1f} KB")


def analyze_categories(jobs):
    """Analyse la répartition par catégories"""
    categories = defaultdict(int)
    for job in jobs:
        cat = job['code_rome'][0]
        categories[cat] += 1
    
    print("\n📊 Répartition par catégories:")
    for cat, count in sorted(categories.items()):
        cat_name = TECH_CATEGORIES.get(cat, 'Autre')
        print(f"   {cat} - {cat_name}: {count} métiers")


def main():
    """Fonction principale"""
    print("=" * 70)
    print("🚀 EXTRACTION COMPLÈTE DES FICHES MÉTIERS ROME")
    print("=" * 70)
    print()
    
    # Choix: Tous les métiers OU seulement tech
    print("Options d'extraction:")
    print("1. TOUS les métiers (~532 fiches)")
    print("2. Seulement métiers TECH/DIGITAL (M, H, K, E) (~200 fiches)")
    print()
    
    # Pour JobMatchAI, on recommande l'option 2 (tech only)
    choice = input("Choisir [1/2] (défaut: 2): ").strip() or "2"
    
    filter_tech = choice == "2"
    
    # Parser le XML
    jobs = parse_rome_xml(XML_FILE, filter_tech_only=filter_tech)
    
    if not jobs:
        print("❌ Aucun métier extrait!")
        return
    
    # Analyser les catégories
    analyze_categories(jobs)
    
    # Sauvegarder
    save_to_json(jobs, OUTPUT_FILE)
    
    # Afficher quelques exemples
    print("\n📄 Exemples de métiers extraits:")
    for job in jobs[:3]:
        print(f"\n   • {job['title']} ({job['code_rome']})")
        print(f"     Compétences: {', '.join(job['required_skills'][:3])}...")
        print(f"     Variantes: {len(job['appellations'])} appellations")
    
    print("\n" + "=" * 70)
    print("✅ TERMINÉ! Base de données JobMatchAI prête.")
    print("=" * 70)


if __name__ == "__main__":
    main()
