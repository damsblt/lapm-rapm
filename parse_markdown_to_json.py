#!/usr/bin/env python3
"""
Script pour parser les fichiers LAPM.md et RAPM.md et extraire tous les articles
pour créer un fichier JSON complet avec tous les articles.
"""

import re
import json

def parse_article_number(text):
    """Extrait le numéro d'article du texte"""
    # Patterns pour différents formats d'articles
    patterns = [
        r'Art\.\s*(\d+[A-Z]?)',  # Art. 1, Art. 10A
        r'Art\.\s*(\d+)\s*\(',   # Art. 1(3)
        r'##\s*\*\*Art\.\s*(\d+[A-Z]?)',  # ## **Art. 1**
        r'###\s*\*\*Art\.\s*(\d+[A-Z]?)', # ### **Art. 1**
        r'#\s*\*\*Art\.\s*(\d+[A-Z]?)',   # # **Art. 1**
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

def parse_article_title(text):
    """Extrait le titre de l'article"""
    # Cherche le titre après le numéro d'article
    patterns = [
        r'Art\.\s*\d+[A-Z]?\s*\([^)]*\)\s*\*\*(.*?)\*\*',  # Art. 1(3) **Titre**
        r'Art\.\s*\d+[A-Z]?\s*\*\*(.*?)\*\*',  # Art. 1 **Titre**
        r'Art\.\s*\d+[A-Z]?\s+(.*?)(?:\n|$)',  # Art. 1 Titre
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            title = match.group(1).strip()
            # Nettoie les balises markdown
            title = re.sub(r'\*\*', '', title)
            # Enlève les références entre parenthèses au début
            title = re.sub(r'^\([^)]*\)\s*', '', title)
            if title:
                return title
    
    return "Sans titre"

def extract_article_content(lines, start_idx):
    """Extrait le contenu d'un article jusqu'au prochain article"""
    content_lines = []
    i = start_idx
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Si on rencontre un nouvel article, on s'arrête
        if i > start_idx and re.match(r'^#+\s*\*\*Art\.', line):
            break
        
        # Si on rencontre un nouveau chapitre, on s'arrête
        if i > start_idx and re.match(r'^#+\s*\*\*Chapitre', line):
            break
        
        if line:
            content_lines.append(line)
        
        i += 1
    
    return '\n'.join(content_lines), i

def parse_lapm_markdown(content):
    """Parse le fichier LAPM.md"""
    articles = []
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Cherche les articles
        if re.search(r'Art\.\s*\d+', line, re.IGNORECASE):
            article_num = parse_article_number(line)
            
            if article_num:
                # Extrait le titre depuis la ligne actuelle
                # Format: ## **Art. 1**(3) **Définition**
                # Cherche le dernier **...** qui est le titre
                title_matches = list(re.finditer(r'\*\*(.*?)\*\*', line))
                if len(title_matches) >= 2:
                    # Le dernier **...** est généralement le titre
                    article_title = title_matches[-1].group(1).strip()
                else:
                    # Format alternatif: ## **Art. 1 Statut** (un seul **...**)
                    title_match = re.search(r'\*\*Art\.\s*\d+[A-Z]?\s+(.*?)\*\*', line)
                    if title_match:
                        article_title = title_match.group(1).strip()
                    else:
                        article_title = parse_article_title(line)
                
                # Nettoie le titre (enlève les références entre parenthèses au début)
                article_title = re.sub(r'^\([^)]*\)\s*', '', article_title)
                
                # Extrait le contenu
                content_text, next_idx = extract_article_content(lines, i)
                
                # Nettoie le contenu (enlève la ligne de titre)
                content_text = re.sub(r'^#+\s*\*\*Art\.\s*\d+[A-Z]?.*?\*\*', '', content_text, flags=re.MULTILINE)
                content_text = content_text.strip()
                
                # Divise en détails (paragraphes ou listes)
                details = []
                if content_text:
                    # Sépare par les alinéas numérotés ou les puces
                    parts = re.split(r'^-?\s*\d+\s+', content_text, flags=re.MULTILINE)
                    if len(parts) > 1:
                        details = [p.strip() for p in parts[1:] if p.strip()]
                    else:
                        # Sinon, sépare par les sauts de ligne doubles
                        parts = re.split(r'\n\n+', content_text)
                        details = [p.strip() for p in parts if p.strip()]
                    
                    # Si toujours vide, prend tout le contenu
                    if not details:
                        details = [content_text]
                
                articles.append({
                    "number": article_num,
                    "title": article_title,
                    "details": details if details else [content_text] if content_text else ["Aucun détail disponible"]
                })
                
                i = next_idx
                continue
        
        i += 1
    
    return articles

def parse_rapm_markdown(content):
    """Parse le fichier RAPM.md"""
    articles = []
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Cherche les articles
        if re.search(r'Art\.\s*\d+', line, re.IGNORECASE):
            article_num = parse_article_number(line)
            
            if article_num:
                # Extrait le titre depuis la ligne actuelle
                # Format: ## **Art. 1**(3) **Définition**
                # Cherche le dernier **...** qui est le titre
                title_matches = list(re.finditer(r'\*\*(.*?)\*\*', line))
                if len(title_matches) >= 2:
                    # Le dernier **...** est généralement le titre
                    article_title = title_matches[-1].group(1).strip()
                else:
                    # Format alternatif: ## **Art. 1 Statut** (un seul **...**)
                    title_match = re.search(r'\*\*Art\.\s*\d+[A-Z]?\s+(.*?)\*\*', line)
                    if title_match:
                        article_title = title_match.group(1).strip()
                    else:
                        article_title = parse_article_title(line)
                
                # Nettoie le titre (enlève les références entre parenthèses au début)
                article_title = re.sub(r'^\([^)]*\)\s*', '', article_title)
                
                # Extrait le contenu
                content_text, next_idx = extract_article_content(lines, i)
                
                # Nettoie le contenu (enlève la ligne de titre)
                content_text = re.sub(r'^#+\s*\*\*Art\.\s*\d+[A-Z]?.*?\*\*', '', content_text, flags=re.MULTILINE)
                content_text = content_text.strip()
                
                # Divise en détails
                details = []
                if content_text:
                    # Sépare par les alinéas numérotés ou les puces
                    parts = re.split(r'^-?\s*\d+\s+', content_text, flags=re.MULTILINE)
                    if len(parts) > 1:
                        details = [p.strip() for p in parts[1:] if p.strip()]
                    else:
                        # Sépare par les lettres (a), b), etc.)
                        parts = re.split(r'^-?\s*[a-z]\)\s+', content_text, flags=re.MULTILINE)
                        if len(parts) > 1:
                            details = [p.strip() for p in parts[1:] if p.strip()]
                        else:
                            # Sinon, sépare par les sauts de ligne doubles
                            parts = re.split(r'\n\n+', content_text)
                            details = [p.strip() for p in parts if p.strip()]
                    
                    # Si toujours vide, prend tout le contenu
                    if not details:
                        details = [content_text]
                
                articles.append({
                    "number": article_num,
                    "title": article_title,
                    "details": details if details else [content_text] if content_text else ["Aucun détail disponible"]
                })
                
                i = next_idx
                continue
        
        i += 1
    
    return articles

def main():
    # Lit les fichiers markdown
    with open('LAPM.md', 'r', encoding='utf-8') as f:
        lapm_content = f.read()
    
    with open('RAPM.md', 'r', encoding='utf-8') as f:
        rapm_content = f.read()
    
    # Parse les articles
    lapm_articles = parse_lapm_markdown(lapm_content)
    rapm_articles = parse_rapm_markdown(rapm_content)
    
    # Crée la structure JSON
    data = {
        "LAPM": {
            "title": "Loi sur les agents de la police municipale",
            "articles": lapm_articles
        },
        "RAPM": {
            "title": "Règlement sur les agents de la police municipale",
            "articles": rapm_articles
        }
    }
    
    # Écrit le fichier JSON
    with open('app/src/data-complete.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ {len(lapm_articles)} articles LAPM extraits")
    print(f"✓ {len(rapm_articles)} articles RAPM extraits")
    print("✓ Fichier app/src/data-complete.json créé")

if __name__ == '__main__':
    main()

