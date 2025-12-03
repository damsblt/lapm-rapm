#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour extraire le texte exact des PDFs pour les articles identifiés
"""

import PyPDF2
import json
import re

def extract_text_from_pdf(pdf_path):
    """Extrait le texte d'un PDF"""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text += f"\n--- PAGE {page_num + 1} ---\n{page_text}\n"
    except Exception as e:
        print(f"Erreur lors de l'extraction du PDF {pdf_path}: {e}")
        return None
    return text

def find_article_content(text, article_number, title_hint):
    """Trouve le contenu exact d'un article dans le texte"""
    # Chercher l'article par son numéro
    patterns = [
        rf'Art\.\s*{re.escape(article_number)}\s*',
        rf'Article\s*{re.escape(article_number)}\s*',
        rf'Art\s*{re.escape(article_number)}\s*',
    ]
    
    article_content = None
    start_pos = None
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            start_pos = match.start()
            # Chercher le prochain article ou la fin
            next_article = re.search(r'Art\.\s*\d+[A-Z]?', text[start_pos + 100:], re.IGNORECASE)
            if next_article:
                end_pos = start_pos + 100 + next_article.start()
            else:
                end_pos = min(start_pos + 5000, len(text))  # Limiter à 5000 caractères
            
            article_content = text[start_pos:end_pos]
            break
    
    if not article_content:
        return None, None
    
    # Extraire le titre (chercher après "Art. X" ou "Article X")
    title_match = re.search(r'Art\.?\s*\d+[A-Z]?\s*([^\n]{10,200})', article_content, re.IGNORECASE)
    if title_match:
        potential_title = title_match.group(1).strip()
        # Nettoyer le titre
        title = re.sub(r'[^\w\s\-\(\)]', '', potential_title)
        title = re.sub(r'\s+', ' ', title).strip()
        if len(title) > 5:
            extracted_title = title[:200]
        else:
            extracted_title = title_hint
    else:
        extracted_title = title_hint
    
    # Extraire les détails (bullet points et paragraphes)
    details = []
    
    # Chercher les bullet points (•, -, ○, ▪, ou numérotés)
    bullet_patterns = [
        r'[•○▪]\s*([^\n]{10,500})',
        r'-\s*([^\n]{10,500})',
        r'\d+[\.\)]\s*([^\n]{10,500})',
        r'[a-z]\)\s*([^\n]{10,500})',
    ]
    
    for pattern in bullet_patterns:
        matches = re.finditer(pattern, article_content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            detail = match.group(1).strip()
            # Nettoyer
            detail = re.sub(r'\s+', ' ', detail)
            if len(detail) > 10 and detail not in details:
                details.append(detail)
    
    # Si pas de bullet points trouvés, extraire les phrases
    if not details:
        sentences = re.split(r'[\.!?]\s+', article_content)
        for sentence in sentences:
            sentence = sentence.strip()
            # Ignorer les très courtes phrases et celles qui contiennent "Art."
            if len(sentence) > 20 and 'Art.' not in sentence and 'Article' not in sentence:
                sentence = re.sub(r'\s+', ' ', sentence)
                if sentence not in details:
                    details.append(sentence)
    
    return extracted_title, details[:30]  # Limiter à 30 détails

def process_pdfs_with_exact_text():
    """Traite les PDFs et extrait le texte exact pour les articles identifiés"""
    # Charger la structure existante
    with open('app/src/data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("Extraction du texte des PDFs...")
    lapm_text = extract_text_from_pdf("LAPM_cours_2025.pdf")
    rapm_text = extract_text_from_pdf("RAPM_cours_2025.pdf")
    
    # Traiter LAPM
    if lapm_text:
        print("\nTraitement LAPM...")
        for article in data["LAPM"]["articles"]:
            article_num = article["number"]
            title_hint = article["title"]
            print(f"  Extraction Art. {article_num}...")
            title, details = find_article_content(lapm_text, article_num, title_hint)
            if title:
                article["title"] = title
            if details:
                article["details"] = details
                print(f"    Trouvé {len(details)} détails")
    
    # Traiter RAPM
    if rapm_text:
        print("\nTraitement RAPM...")
        for article in data["RAPM"]["articles"]:
            article_num = article["number"]
            title_hint = article["title"]
            print(f"  Extraction Art. {article_num}...")
            title, details = find_article_content(rapm_text, article_num, title_hint)
            if title:
                article["title"] = title
            if details:
                article["details"] = details
                print(f"    Trouvé {len(details)} détails")
    
    # Sauvegarder
    with open('app/src/data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("\n✓ Données mises à jour dans app/src/data.json")

if __name__ == "__main__":
    process_pdfs_with_exact_text()


