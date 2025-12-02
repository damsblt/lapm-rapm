#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour extraire le texte exact des PDFs en utilisant les articles identifiés
"""

import PyPDF2
import json
import re

def extract_all_text_from_pdf(pdf_path):
    """Extrait tout le texte d'un PDF"""
    pages_text = []
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                pages_text.append((page_num + 1, text))
    except Exception as e:
        print(f"Erreur: {e}")
        return []
    return pages_text

def find_article_in_pages(pages_text, article_number, title_hint):
    """Trouve le contenu d'un article dans les pages"""
    article_number_clean = article_number.replace('A', 'A').replace('a', 'a')
    
    # Patterns pour trouver l'article
    patterns = [
        rf'Art\.\s*{re.escape(article_number_clean)}\s',
        rf'Art\s*{re.escape(article_number_clean)}\s',
        rf'Article\s*{re.escape(article_number_clean)}\s',
    ]
    
    for page_num, page_text in pages_text:
        for pattern in patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                # Extraire le contexte autour de l'article
                start = max(0, match.start() - 50)
                # Chercher jusqu'à la fin de la page ou jusqu'au prochain article
                remaining_text = page_text[match.start():]
                
                # Chercher le prochain article
                next_article = re.search(r'Art\.\s*\d+[A-Z]?', remaining_text[200:], re.IGNORECASE)
                if next_article:
                    end = match.start() + 200 + next_article.start()
                    article_text = page_text[match.start():end]
                else:
                    # Prendre jusqu'à la fin de la page ou 3000 caractères
                    article_text = page_text[match.start():match.start() + 3000]
                
                return page_num, article_text
    
    return None, None

def extract_details_from_text(text):
    """Extrait les détails (bullet points) du texte"""
    details = []
    
    # Nettoyer le texte
    text = re.sub(r'--- PAGE \d+ ---', '', text)
    text = re.sub(r'\s+', ' ', text)
    
    # Chercher les bullet points avec différents formats
    bullet_patterns = [
        r'[•○▪]\s*([^•○▪\n]{15,400})',
        r'-\s+([^-\n]{15,400})',
        r'\d+[\.\)]\s+([^\d\n]{15,400})',
        r'[a-z]\)\s+([^a-z\)\n]{15,400})',
        r'[A-Z]\)\s+([^A-Z\)\n]{15,400})',
    ]
    
    found_texts = set()
    
    for pattern in bullet_patterns:
        matches = re.finditer(pattern, text, re.MULTILINE)
        for match in matches:
            detail = match.group(1).strip()
            # Nettoyer
            detail = re.sub(r'\s+', ' ', detail)
            # Enlever les caractères de contrôle
            detail = re.sub(r'[^\w\s\.,;:!?\-\(\)\'\"]', '', detail)
            if len(detail) > 15 and detail not in found_texts:
                found_texts.add(detail)
                details.append(detail)
    
    # Si pas de bullet points, extraire les phrases complètes
    if not details:
        # Diviser en phrases
        sentences = re.split(r'[\.!?]\s+', text)
        for sentence in sentences:
            sentence = sentence.strip()
            # Ignorer les très courtes et celles avec "Art."
            if (len(sentence) > 20 and 
                'Art.' not in sentence and 
                'Article' not in sentence and
                'PAGE' not in sentence and
                sentence not in found_texts):
                sentence = re.sub(r'\s+', ' ', sentence)
                found_texts.add(sentence)
                details.append(sentence)
    
    return details[:25]  # Limiter à 25 détails

def extract_title_from_text(text, article_number):
    """Extrait le titre de l'article"""
    # Chercher après "Art. X" ou "Article X"
    patterns = [
        rf'Art\.\s*{re.escape(article_number)}\s+([^\n]{10,150})',
        rf'Art\s*{re.escape(article_number)}\s+([^\n]{10,150})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            # Nettoyer
            title = re.sub(r'\s+', ' ', title)
            title = re.sub(r'[^\w\s\-\(\)]', '', title)
            if len(title) > 5:
                return title[:200]
    
    return None

def process_pdfs():
    """Traite les PDFs et met à jour le JSON avec le texte exact"""
    # Charger la structure existante
    with open('app/src/data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("Extraction du texte des PDFs...")
    lapm_pages = extract_all_text_from_pdf("LAPM_cours_2025.pdf")
    rapm_pages = extract_all_text_from_pdf("RAPM_cours_2025.pdf")
    
    print(f"LAPM: {len(lapm_pages)} pages")
    print(f"RAPM: {len(rapm_pages)} pages")
    
    # Traiter LAPM
    if lapm_pages:
        print("\n=== Traitement LAPM ===")
        for article in data["LAPM"]["articles"]:
            article_num = article["number"]
            print(f"  Art. {article_num}...", end=" ")
            page_num, article_text = find_article_in_pages(lapm_pages, article_num, article["title"])
            
            if article_text:
                # Extraire le titre
                title = extract_title_from_text(article_text, article_num)
                if title:
                    article["title"] = title
                
                # Extraire les détails
                details = extract_details_from_text(article_text)
                if details:
                    article["details"] = details
                    print(f"✓ {len(details)} détails trouvés (page {page_num})")
                else:
                    print("⚠ Pas de détails trouvés")
            else:
                print("⚠ Article non trouvé dans le PDF")
    
    # Traiter RAPM
    if rapm_pages:
        print("\n=== Traitement RAPM ===")
        for article in data["RAPM"]["articles"]:
            article_num = article["number"]
            print(f"  Art. {article_num}...", end=" ")
            page_num, article_text = find_article_in_pages(rapm_pages, article_num, article["title"])
            
            if article_text:
                # Extraire le titre
                title = extract_title_from_text(article_text, article_num)
                if title:
                    article["title"] = title
                
                # Extraire les détails
                details = extract_details_from_text(article_text)
                if details:
                    article["details"] = details
                    print(f"✓ {len(details)} détails trouvés (page {page_num})")
                else:
                    print("⚠ Pas de détails trouvés")
            else:
                print("⚠ Article non trouvé dans le PDF")
    
    # Sauvegarder
    with open('app/src/data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("\n✓ Données mises à jour dans app/src/data.json")

if __name__ == "__main__":
    process_pdfs()

