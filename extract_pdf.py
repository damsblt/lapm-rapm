#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour extraire le contenu des PDFs LAPM et RAPM et le structurer en JSON
"""

import PyPDF2
import json
import re
import sys

def extract_text_from_pdf(pdf_path):
    """Extrait le texte d'un PDF"""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Erreur lors de l'extraction du PDF {pdf_path}: {e}")
        return None
    return text

def find_articles_in_text(text, law_type):
    """Trouve les articles dans le texte extrait"""
    articles = []
    
    # Pattern pour trouver les articles (Art. X ou Article X)
    # On cherche aussi les numéros d'articles dans les titres de slides
    article_pattern = r'(?:Art\.|Article)\s*(\d+[A-Z]?)\s*(.*?)(?=(?:Art\.|Article)\s*\d+[A-Z]?|$)'
    
    matches = re.finditer(article_pattern, text, re.IGNORECASE | re.DOTALL)
    
    for match in matches:
        article_num = match.group(1).strip()
        content = match.group(2).strip()
        
        # Extraire le titre (première ligne ou phrase)
        lines = content.split('\n')
        title = ""
        details = []
        
        # Chercher le titre (généralement la première ligne significative)
        for i, line in enumerate(lines[:5]):  # Regarder les 5 premières lignes
            line = line.strip()
            if line and len(line) > 10 and len(line) < 200:
                title = line
                # Le reste du contenu après le titre
                remaining = '\n'.join(lines[i+1:])
                break
        
        if not title:
            # Si pas de titre trouvé, prendre la première phrase
            first_sentence = content.split('.')[0] if '.' in content else content[:100]
            title = first_sentence.strip()
            remaining = content[len(title):]
        
        # Nettoyer et structurer les détails
        remaining = remaining.strip()
        if remaining:
            # Diviser en bullet points si possible
            detail_lines = [line.strip() for line in remaining.split('\n') if line.strip()]
            details = detail_lines[:20]  # Limiter à 20 lignes
        
        if article_num:
            articles.append({
                "number": article_num,
                "title": title,
                "details": details if details else [remaining[:500]]  # Limiter la longueur
            })
    
    return articles

def process_pdfs():
    """Traite les deux PDFs et crée la structure JSON"""
    lapm_text = extract_text_from_pdf("LAPM_cours_2025.pdf")
    rapm_text = extract_text_from_pdf("RAPM_cours_2025.pdf")
    
    data = {
        "LAPM": {
            "title": "Loi sur les agents de la police municipale",
            "articles": []
        },
        "RAPM": {
            "title": "Règlement sur les agents de la police municipale",
            "articles": []
        }
    }
    
    if lapm_text:
        print("Extraction LAPM...")
        data["LAPM"]["articles"] = find_articles_in_text(lapm_text, "LAPM")
        print(f"Trouvé {len(data['LAPM']['articles'])} articles dans LAPM")
    
    if rapm_text:
        print("Extraction RAPM...")
        data["RAPM"]["articles"] = find_articles_in_text(rapm_text, "RAPM")
        print(f"Trouvé {len(data['RAPM']['articles'])} articles dans RAPM")
    
    # Sauvegarder en JSON
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\nDonnées sauvegardées dans data.json")
    print(f"Total articles LAPM: {len(data['LAPM']['articles'])}")
    print(f"Total articles RAPM: {len(data['RAPM']['articles'])}")
    
    # Afficher un aperçu
    if data["LAPM"]["articles"]:
        print("\nAperçu LAPM:")
        for art in data["LAPM"]["articles"][:3]:
            print(f"  Art. {art['number']}: {art['title'][:50]}...")
    
    if data["RAPM"]["articles"]:
        print("\nAperçu RAPM:")
        for art in data["RAPM"]["articles"][:3]:
            print(f"  Art. {art['number']}: {art['title'][:50]}...")

if __name__ == "__main__":
    process_pdfs()

