# Application de Révision LAPM / RAPM

Application React pour réviser la Loi sur les agents de la police municipale (LAPM) et le Règlement sur les agents de la police municipale (RAPM) avec un système de flashcards.

## Fonctionnalités

- **Deux volets** : Navigation entre LAPM et RAPM
- **Système de flashcards** : 
  - Recto : Numéro d'article et titre
  - Verso : Détails en bullet points
- **Navigation** : Boutons pour passer d'un article à l'autre
- **Design moderne** : Interface utilisateur élégante et responsive

## Installation

```bash
npm install
```

## Développement

```bash
npm run dev
```

L'application sera accessible sur `http://localhost:5173`

## Build

```bash
npm run build
```

## Déploiement sur GitHub Pages

1. Assurez-vous que votre repository GitHub s'appelle `LAPM-RAPM` (ou modifiez le `base` dans `vite.config.js`)

2. Déployez l'application :
```bash
npm run deploy
```

3. Dans les paramètres de votre repository GitHub, allez dans "Pages" et configurez la source sur la branche `gh-pages`.

4. Votre application sera accessible à l'adresse : `https://[votre-username].github.io/LAPM-RAPM/`

## Structure des données

Les données sont stockées dans `src/data.json` avec la structure suivante :

```json
{
  "LAPM": {
    "title": "Loi sur les agents de la police municipale",
    "articles": [
      {
        "number": "1",
        "title": "Définition",
        "details": ["...", "..."]
      }
    ]
  },
  "RAPM": {
    "title": "Règlement sur les agents de la police municipale",
    "articles": [...]
  }
}
```

## Technologies utilisées

- React 19
- Vite
- CSS3 (animations et transitions)
