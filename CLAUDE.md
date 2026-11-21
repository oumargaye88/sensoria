# Sensoria — site vitrine de parfums et huiles

Site statique d'une marque de parfums et de rituels. Il comporte :
- une page d'accueil (histoire, quiz, présentation des 4 gammes, sélection) ;
- une page par gamme (eaux de parfum, huiles précieuses, huiles à brûler, rituel hammam) ;
- 31 pages produit.

## En ligne

https://oumargaye88.github.io/sensoria/ (GitHub Pages, dépôt **public**)

## Technologies

- HTML, CSS (`style.css`) et JavaScript (`script.js`) statiques.
- Générateur Python 3 (`generate.py`), sans dépendance externe.
- **Seule source de données** : `data/products.json`. Les fichiers `index.html`, `collections/*.html` et `produits/*.html` sont **générés** à partir de lui.

## Commandes

| Action | Commande |
|---|---|
| Installer | rien à installer (Python 3 suffit) |
| Régénérer le site | `python3 generate.py`, après chaque modification de `data/products.json` |
| Lancer en local | `python3 -m http.server 8080`, puis ouvrir http://localhost:8080 |
| Tester | régénérer, puis vérifier les pages. Il n'y a pas de tests automatiques |

## Hébergement et déploiement

GitHub Pages, branche `main` : un `git push` publie le site.
Le dépôt est **public** : ne jamais y mettre de donnée privée.

## Services utilisés

Aucun.

## Variables d'environnement

Aucune. Voir `.env.example`.

## Règles

- Modifier `data/products.json` et le gabarit dans `generate.py`, jamais directement les pages générées.
