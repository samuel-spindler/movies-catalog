# Gestion de Catalogue de Films

Ce projet est une application permettant de gérer un catalogue de films avec système de recommandation en utilisant **Python** pour l'interface graphique et **C** pour l'algorithme de recommandation.

---

## Équipe du projet

Ce projet a été réalisé en équipe dans le cadre de l'UE NF06 en deuxième année de classe préparatoire à la formation d'ingénieur.
- **Samuel SPINDLER**
- **Clémence BUTTAZZONI**

---

## Fonctionnalités

- **Gestion du catalogue** : ajouter, modifier, filtrer et trier les films
- **Notation** : les utilisateurs notent les films, calcul automatique de la cote moyenne
- **Gestion des ventes** : enregistrement des ventes avec suivi du stock
- **Graphiques** : analyse des ventes (revenu par jour, par genre, par vendeur)
- **Recommandations** : système intelligent basé sur la similarité de Jaccard pour suggérer des films
- **Multi-utilisateurs** : création de comptes et mémorisation des utilisateurs

---

##  Prérequis

- Python 3.8+
- gcc (pour compiler la partie C)
- Bibliothèque Tkinter
- Bibliothèque Matplotlib

##  Installation et Utilisation


### Étape 1 : Installer les bibliothèques Python

```bash
pip install matplotlib
pip install tkinter
```

### Étape 2 : Compiler le programme C

```bash
gcc -o recommandation recommandation.c cjson/cJSON.c -I cjson
```

pour crée l'exécutable `recommandation.exe` utilisé par le système de recommandation python.

### Étape 3 : Lancer l'application

```bash
python main.py
```

L'interface graphique s'ouvre automatiquement.

##  Structure du projet

```
.
├── main.py                         # Application principale (Python)
├── recommandation.c                # Algorithme de recommandation (C)
├── recommandation.exe              # Exécutable compilé
├── logo.png                        # Logo de l'application
├── README.md
│
├── cjson/                          # Bibliothèque JSON pour C
│   ├── cJSON.c
│   └── cJSON.h
│
└── Fichiers_json/                  # Données persistantes
    ├── catalogue_films.json        # Liste des films
    ├── ListeUtilisateurs.json      # Profils utilisateurs et notes
    ├── ventes.json                 # Historique des ventes
    ├── target_user.json            # Utilisateur cible (pour recommandation)
    └── recommendations.json        # Résultats de la recommandation
```

---

##  Options pour l'utilisateur

1. **Authentification**
   - Créer un compte ou se connecter
   - Chaque utilisateur a un historique de notes persistant

2. **Parcourir le catalogue**
   - Visualiser tous les films disponibles
   - Voir : titre, genre, année, cote actuelle, stock, prix

3. **Noter les films**
   - Attribuer une note entre 0 et 10
   - La cote moyenne du film se met à jour automatiquement
   - L'historique des notes est sauvegardé

4. **Filtrer et trier**
   - Rechercher par genre, année ou note minimale
   - Trier par titre, année ou cote
   - Affichage dynamique instantané

5. **Gestion des ventes**
   - Enregistrer une vente
   - Le stock se décrémente automatiquement
   - Chaque vente est datée et attribuée au vendeur

6. **Analyser et visualiser**
   - Consulter les statistiques globales (meilleur film par genre, etc.)
   - Voir les graphiques des ventes (revenu, par genre, par vendeur)
   - Suivre le stock disponible

7. **Obtenir des recommandations**
   - Cliquer sur "Recommandation"
   - L'algorithme analyse les utilisateurs similaires
   - Recevoir des suggestions de films à découvrir

## Système de recommandation

L'algorithme utilise la **similarité de Jaccard** pour identifier les utilisateurs avec des goûts similaires et leur recommander des films :

```
Similarité(A, B) = |Films notés par A ∩ Films notés par B| / |Films notés par A ∪ Films notés par B|
```

### Fonctionnement

1. Identifie l'utilisateur cible
2. Calcule la similarité avec tous les autres utilisateurs
3. Trouve l'utilisateur le plus similaire
4. Extrait les films notés par cet utilisateur similaire
5. Recommande ceux que l'utilisateur cible n'a pas encore vus

**Exemple** :
- Utilisateur A a noté : Inception (8.5), Avatar (7), Titanic (6)
- Utilisateur B a noté : Avatar (7.5), The Matrix (9), Inception (8)
- Similarité = 2/4 = 0.5
- Recommandation pour A : The Matrix




