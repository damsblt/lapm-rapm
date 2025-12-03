#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script final pour extraire le texte exact des PDFs
"""

import PyPDF2
import json
import re

def extract_all_pages(pdf_path):
    """Extrait tout le texte du PDF"""
    full_text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                full_text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Erreur: {e}")
        return None
    return full_text

def find_article_section(text, article_number):
    """Trouve la section d'un article dans le texte complet"""
    # Patterns pour trouver l'article (avec ou sans espace, avec alinéas)
    patterns = [
        rf'Art\.?\s*{re.escape(article_number)}\s*[,\s]',
        rf'Art\.?\s*{re.escape(article_number)}\s*$',
        rf'Art\.?\s*{re.escape(article_number)}\s*al\.',
    ]
    
    for pattern in patterns:
        matches = list(re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE))
        if matches:
            # Prendre le premier match
            match = matches[0]
            start = match.start()
            
            # Chercher le prochain article (mais pas le même avec un alinéa différent)
            next_pattern = rf'Art\.?\s*\d+[A-Z]?\s*[,\s]'
            remaining = text[start + 50:]
            next_match = re.search(next_pattern, remaining, re.IGNORECASE)
            
            if next_match:
                # Vérifier que ce n'est pas le même article avec un alinéa
                next_art = re.search(r'Art\.?\s*(\d+[A-Z]?)', remaining[next_match.start():next_match.start()+20], re.IGNORECASE)
                if next_art and next_art.group(1) == article_number:
                    # C'est le même article, continuer
                    end = start + 50 + next_match.start() + 2000
                else:
                    end = start + 50 + next_match.start()
            else:
                end = min(start + 3000, len(text))
            
            section = text[start:end]
            return section
    
    return None

def extract_bullet_points(text):
    """Extrait les bullet points du texte"""
    details = []
    
    # Nettoyer
    text = re.sub(r'\s+', ' ', text)
    
    # Patterns pour bullet points
    patterns = [
        r'[•○▪]\s*([^•○▪]{20,400}?)(?=\s*[•○▪]|\s*Art\.|$)',
        r'-\s+([^-]{20,400}?)(?=\s*-|\s*Art\.|$)',
        r'\d+[\.\)]\s+([^\d]{20,400}?)(?=\s*\d+[\.\)]|\s*Art\.|$)',
        r'[a-z]\)\s+([^a-z\)]{20,400}?)(?=\s*[a-z]\)|\s*Art\.|$)',
        r'[A-Z]\)\s+([^A-Z\)]{20,400}?)(?=\s*[A-Z]\)|\s*Art\.|$)',
    ]
    
    found = set()
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
        for match in matches:
            detail = match.group(1).strip()
            detail = re.sub(r'\s+', ' ', detail)
            # Enlever caractères de contrôle mais garder la ponctuation
            detail = re.sub(r'[^\w\s\.,;:!?\-\(\)\'\"]', '', detail)
            if len(detail) > 20 and detail not in found:
                found.add(detail)
                details.append(detail)
    
    # Si pas de bullet points, extraire les phrases
    if not details:
        # Chercher les phrases qui commencent par des mots-clés importants
        sentences = re.split(r'[\.!?]\s+', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if (len(sentence) > 25 and 
                'Art.' not in sentence and 
                'Article' not in sentence and
                'PAGE' not in sentence and
                sentence not in found):
                sentence = re.sub(r'\s+', ' ', sentence)
                found.add(sentence)
                details.append(sentence)
    
    return details[:30]

def extract_title(text, article_number):
    """Extrait le titre de l'article"""
    # Chercher après "Art. X" jusqu'à la première phrase complète ou bullet point
    pattern = rf'Art\.?\s*{re.escape(article_number)}\s*([^•○▪\n]{10,150}?)(?=[•○▪\n]|Art\.)'
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    
    if match:
        title = match.group(1).strip()
        title = re.sub(r'\s+', ' ', title)
        # Enlever caractères spéciaux mais garder les lettres, chiffres, espaces, tirets
        title = re.sub(r'[^\w\s\-\(\)]', '', title)
        if len(title) > 5:
            return title[:200]
    
    return None

def process_pdfs():
    """Traite les PDFs"""
    # Charger la structure existante
    with open('app/src/data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("Extraction du texte des PDFs...")
    lapm_text = extract_all_pages("LAPM_cours_2025.pdf")
    rapm_text = extract_all_pages("RAPM_cours_2025.pdf")
    
    # Traiter LAPM
    if lapm_text:
        print("\n=== Traitement LAPM ===")
        for article in data["LAPM"]["articles"]:
            article_num = article["number"]
            print(f"  Art. {article_num}...", end=" ")
            
            section = find_article_section(lapm_text, article_num)
            if section:
                # Extraire titre
                title = extract_title(section, article_num)
                if title:
                    article["title"] = title
                
                # Extraire détails
                details = extract_bullet_points(section)
                if details:
                    article["details"] = details
                    print(f"✓ {len(details)} détails")
                else:
                    print("⚠ Pas de détails")
            else:
                print("⚠ Non trouvé")
    
    # Traiter RAPM
    if rapm_text:
        print("\n=== Traitement RAPM ===")
        for article in data["RAPM"]["articles"]:
            article_num = article["number"]
            print(f"  Art. {article_num}...", end=" ")
            
            section = find_article_section(rapm_text, article_num)
            if section:
                # Extraire titre
                title = extract_title(section, article_num)
                if title:
                    article["title"] = title
                
                # Extraire détails
                details = extract_bullet_points(section)
                if details:
                    article["details"] = details
                    print(f"✓ {len(details)} détails")
                else:
                    print("⚠ Pas de détails")
            else:
                print("⚠ Non trouvé")
    
    # Sauvegarder
    with open('app/src/data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("\n✓ Données mises à jour")

if __name__ == "__main__":
    process_pdfs()


