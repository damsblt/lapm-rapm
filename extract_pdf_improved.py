#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script amélioré pour extraire le contenu des PDFs LAPM et RAPM
"""

import PyPDF2
import json
import re
from collections import defaultdict

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

def clean_text(text):
    """Nettoie le texte extrait"""
    # Supprimer les caractères de contrôle
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    # Normaliser les espaces
    text = re.sub(r'\s+', ' ', text)
    # Supprimer les marqueurs de page
    text = re.sub(r'--- PAGE \d+ ---', '', text)
    return text.strip()

def find_articles_improved(text, law_type):
    """Trouve les articles dans le texte avec une meilleure détection"""
    articles_dict = defaultdict(list)
    
    # Patterns pour détecter les articles
    # Chercher "Art. X" ou "Article X" suivi d'un titre
    patterns = [
        r'Art\.\s*(\d+[A-Z]?)\s*([^\n]{10,200})',  # Art. X suivi d'un titre
        r'Article\s*(\d+[A-Z]?)\s*([^\n]{10,200})',  # Article X suivi d'un titre
        r'Art\.\s*(\d+[A-Z]?)\s*\n\s*([^\n]{10,200})',  # Art. X sur une ligne, titre sur la suivante
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            article_num = match.group(1).strip()
            potential_title = match.group(2).strip()
            
            # Nettoyer le titre
            title = re.sub(r'[^\w\s\-\(\)]', '', potential_title)
            title = re.sub(r'\s+', ' ', title).strip()
            
            if len(title) > 5 and len(title) < 200:
                # Trouver le contenu après le titre
                start_pos = match.end()
                # Chercher jusqu'au prochain article ou jusqu'à la fin
                next_article = re.search(r'Art\.\s*\d+[A-Z]?', text[start_pos:start_pos+2000], re.IGNORECASE)
                end_pos = start_pos + (next_article.start() if next_article else 2000)
                
                content = text[start_pos:end_pos].strip()
                
                # Extraire les bullet points
                details = []
                # Chercher les lignes qui commencent par des puces ou des tirets
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and (line.startswith('•') or line.startswith('-') or 
                                line.startswith('○') or line.startswith('▪') or
                                re.match(r'^\d+[\.\)]', line) or
                                line.startswith('a)') or line.startswith('b)')):
                        # Nettoyer la ligne
                        cleaned = re.sub(r'^[•\-○▪\d\.\)\s]+', '', line)
                        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                        if cleaned and len(cleaned) > 10:
                            details.append(cleaned)
                    elif line and len(line) > 20 and len(line) < 500:
                        # Ligne de texte normale
                        cleaned = re.sub(r'\s+', ' ', line).strip()
                        if cleaned:
                            details.append(cleaned)
                
                # Si pas de détails structurés, prendre le texte brut (limité)
                if not details:
                    cleaned_content = re.sub(r'\s+', ' ', content[:500]).strip()
                    if cleaned_content:
                        details = [cleaned_content]
                
                articles_dict[article_num].append({
                    "title": title,
                    "details": details[:15]  # Limiter à 15 détails
                })
    
    # Convertir en liste d'articles
    articles = []
    for article_num, variants in articles_dict.items():
        # Si plusieurs variantes pour le même article, prendre la plus complète
        best_variant = max(variants, key=lambda x: len(x['details']))
        articles.append({
            "number": article_num,
            "title": best_variant["title"],
            "details": best_variant["details"]
        })
    
    # Trier par numéro d'article
    def sort_key(art):
        num = art["number"]
        # Extraire le numéro et la lettre
        match = re.match(r'(\d+)([A-Z]?)', num)
        if match:
            return (int(match.group(1)), match.group(2) or '')
        return (999, '')
    
    articles.sort(key=sort_key)
    return articles

def process_pdfs():
    """Traite les deux PDFs et crée la structure JSON"""
    print("Extraction du texte des PDFs...")
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
        print("Traitement LAPM...")
        lapm_text = clean_text(lapm_text)
        data["LAPM"]["articles"] = find_articles_improved(lapm_text, "LAPM")
        print(f"Trouvé {len(data['LAPM']['articles'])} articles dans LAPM")
    
    if rapm_text:
        print("Traitement RAPM...")
        rapm_text = clean_text(rapm_text)
        data["RAPM"]["articles"] = find_articles_improved(rapm_text, "RAPM")
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
        for art in data["LAPM"]["articles"][:5]:
            print(f"  Art. {art['number']}: {art['title'][:60]}...")
            print(f"    Détails: {len(art['details'])} points")
    
    if data["RAPM"]["articles"]:
        print("\nAperçu RAPM:")
        for art in data["RAPM"]["articles"][:5]:
            print(f"  Art. {art['number']}: {art['title'][:60]}...")
            print(f"    Détails: {len(art['details'])} points")

if __name__ == "__main__":
    process_pdfs()

