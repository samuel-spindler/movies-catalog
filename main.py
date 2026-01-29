import tkinter as tk
from tkinter import *
from tkinter import messagebox, simpledialog, filedialog, ttk
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import subprocess
import json

# ========== CONFIGURATION DES CHEMINS ==========
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def get_json_path(filename):
    """Retourne le chemin vers les fichiers JSON dans Fichiers_json/"""
    return os.path.join(PROJECT_ROOT, "Fichiers_json", filename)

def get_project_path(filename):
    """Retourne le chemin vers les fichiers à la racine du projet"""
    return os.path.join(PROJECT_ROOT, filename)

# ========== FIN CONFIGURATION DES CHEMINS ==========

# Fonctions d'import du catalogue
def importer_catalogue(fichier): 
    """Importe un fichier JSON contenant un catalogue de films."""
    try:
        with open(fichier, 'r', encoding='utf-8') as f: # Ouvrir le fichier en mode lecture
            return json.load(f) # Charger le contenu du fichier JSON
    except (FileNotFoundError, json.JSONDecodeError):
        return [] # Retourner une liste vide si le fichier n'existe pas ou est invalide

# Fonctions d'export du catalogue
def exporter_catalogue(fichier, catalogue): 
    """Exporte le catalogue de films dans un fichier JSON."""
    with open(fichier, 'w', encoding='utf-8') as f: # Ouvrir le fichier en mode écriture
        json.dump(catalogue, f, ensure_ascii=False, indent=4) # Écrire le contenu du catalogue dans le fichier JSON

# Fonctions de chargement des ventes
def charger_ventes(fichier=None):
    """Charge l'historique des ventes depuis Fichiers_json/ventes.json."""
    if fichier is None:
        fichier = get_json_path('ventes.json')
    if not os.path.exists(fichier): # Vérifier si le fichier existe
        with open(fichier, 'w', encoding='utf-8') as f: # Créer le fichier s'il n'existe pas
            json.dump([], f, ensure_ascii=False, indent=4) # Écrire une liste vide dans le fichier JSON
    with open(fichier, 'r', encoding='utf-8') as f: # Ouvrir le fichier en mode lecture
        try:
            return json.load(f) # Charger le contenu du fichier JSON
        except json.JSONDecodeError:
            return [] # Retourner une liste vide si le fichier est vide ou invalide

# Sauvegarde des ventes
def sauvegarder_ventes(ventes, fichier=None): 
    """Sauvegarde l'historique des ventes dans Fichiers_json/ventes.json."""
    if fichier is None:
        fichier = get_json_path('ventes.json')
    with open(fichier, 'w', encoding='utf-8') as f: # Ouvrir le fichier en mode écriture
        json.dump(ventes, f, ensure_ascii=False, indent=4) # Écrire le contenu des ventes dans le fichier JSON

# Fonctions de chargement des utilisateurs
def charger_utilisateurs(fichier=None):
    """Charge la liste des utilisateurs depuis Fichiers_json/ListeUtilisateurs.json."""
    if fichier is None:
        fichier = get_json_path('ListeUtilisateurs.json')
    if not os.path.exists(fichier): # Vérifier si le fichier existe
        with open(fichier, 'w', encoding='utf-8') as f: # Créer le fichier s'il n'existe pas
            json.dump([], f, ensure_ascii=False, indent=4) # Écrire une liste vide dans le fichier JSON
    with open(fichier, 'r', encoding='utf-8') as f: # Ouvrir le fichier en mode lecture
        try:
            return json.load(f) # Charger le contenu du fichier JSON
        except json.JSONDecodeError:
            return []  # Retourner une liste vide si le fichier est vide ou invalide

# Sauvegarde des utilisateurs
def sauvegarder_utilisateurs(utilisateurs, fichier=None): 
    """Sauvegarde la liste des utilisateurs dans Fichiers_json/ListeUtilisateurs.json."""
    if fichier is None:
        fichier = get_json_path('ListeUtilisateurs.json')
    with open(fichier, 'w', encoding='utf-8') as f: # Ouvrir le fichier en mode écriture
        json.dump(utilisateurs, f, ensure_ascii=False, indent=4) # Écrire le contenu des utilisateurs dans le fichier JSON

# Ajouter une note à un film pour un utilisateur
def ajouter_note_utilisateur(username, film, note, fichier=None): 
    """Ajoute une note à un film pour un utilisateur dans le fichier ListeUtilisateurs.json."""
    if fichier is None:
        fichier = get_json_path('ListeUtilisateurs.json')
    liste_utilisateurs = charger_utilisateurs(fichier) # Charger la liste des utilisateurs
    utilisateur_existant = next((u for u in liste_utilisateurs if u['username'] == username), None) # Rechercher l'utilisateur par son nom

    if utilisateur_existant: # Si l'utilisateur existe 
        utilisateur_existant['notes'][film] = note # Ajouter la note pour le film
    else: # Si l'utilisateur n'existe pas
        new_id = (max((u['user_id'] for u in liste_utilisateurs), default=0) + 1) # Générer un nouvel identifiant
        nouveau_utilisateur = {
            'user_id': new_id,
            'username': username,
            'notes': {film: note}
        }
        liste_utilisateurs.append(nouveau_utilisateur) # Ajouter le nouvel utilisateur à la liste

    sauvegarder_utilisateurs(liste_utilisateurs, fichier) # Sauvegarder la liste des utilisateurs dans le fichier


# Classe principale de l'application
class FilmCatalogueApp:
    """Application de gestion de catalogue de films avec interface graphique."""
    def __init__(self, root, catalogue): # Constructeur de la classe
        self.root = root # Fenêtre principale de l'application
        self.root.title("Catalogue de Films") # Titre de la fenêtre
        self.root.geometry("1000x700") # Dimensions de la fenêtre
        self.root.configure(bg="#E8F4FF") # Couleur de fond

        self.catalogue = catalogue # Catalogue de films
        self.user = None # Utilisateur connecté
        self.user_id = None # Identifiant de l'utilisateur connecté
        self.user_notes = {} # Notes attribuées par l'utilisateur connecté
        self.ventes = charger_ventes()  # Charger l'historique des ventes

        # Configuration de police
        self.default_font = ("Arial", 12)  # Police par défaut

        # Barre de menu
        self.menu_bar = tk.Menu(self.root) # Créer une barre de menu
        self.root.config(menu=self.menu_bar) # Ajouter la barre de menu à la fenêtre

        # Menu Fichier
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0) # Créer un menu déroulant
        self.file_menu.add_command(label="Importer Catalogue", command=self.importer_catalogue_interface) # Ajouter une option au menu
        self.file_menu.add_command(label="Exporter Catalogue", command=self.exporter_catalogue_interface) # Ajouter une option au menu
        self.file_menu.add_separator() # Ajouter un séparateur
        self.file_menu.add_command(label="Quitter", command=self.root.quit) # Ajouter une option au menu
        self.menu_bar.add_cascade(label="Fichier", menu=self.file_menu) # Ajouter le menu à la barre de menu

        # Menu Edition
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0) # Créer un menu déroulant
        self.edit_menu.add_command(label="Ajouter un film", command=self.ajouter_film) # Ajouter une option au menu
        self.menu_bar.add_cascade(label="Édition", menu=self.edit_menu) # Ajouter le menu à la barre de menu

        # Menu Utilisateur
        self.user_menu = tk.Menu(self.menu_bar, tearoff=0) # Créer un menu déroulant
        self.user_menu.add_command(label="Changer d'utilisateur", command=self.deconnecter_utilisateur) # Ajouter une option au menu
        self.menu_bar.add_cascade(label="Utilisateur", menu=self.user_menu) # Ajouter le menu à la barre de menu

        # Menu Statistiques
        self.stats_menu = tk.Menu(self.menu_bar, tearoff=0) # Créer un menu déroulant
        self.stats_menu.add_command(label="Afficher les statistiques", command=self.afficher_statistiques) # Ajouter une option au menu
        self.menu_bar.add_cascade(label="Statistiques", menu=self.stats_menu) # Ajouter le menu à la barre de menu

        # Menu Ventes
        self.sales_menu = tk.Menu(self.root, tearoff=0) # Créer un menu déroulant
        self.sales_menu.add_command(label="Enregistrer une vente", command=self.ajouter_vente_interface) # Ajouter une option au menu
        self.sales_menu.add_command(label="Historique des ventes", command=self.afficher_historiques_ventes) # Ajouter une option au menu
        self.sales_menu.add_command(label="Analyse des ventes", command=self.afficher_analyse_ventes) # Ajouter une option au menu
        self.menu_bar.add_cascade(label="Ventes", menu=self.sales_menu) # Ajouter le menu à la barre de menu


        # Frame de connexion utilisateur
        self.login_frame = tk.Frame(self.root, bg="#E8F4FF") # Créer un cadre pour le formulaire de connexion
        self.login_frame.pack(pady=20) # Afficher le cadre

        tk.Label(self.login_frame, text="Nom d'utilisateur :", bg="#E8F4FF", font=self.default_font).grid(row=0, column=0, padx=5) # Ajouter un label
        self.username_entry = tk.Entry(self.login_frame, font=self.default_font, width=20) # Ajouter un champ de saisie
        self.username_entry.grid(row=0, column=1, padx=5) # Afficher le champ de saisie
        connect_btn = tk.Button(self.login_frame, text="Se connecter / Créer compte", command=self.connect_user, bg="#007ACC", fg="white", font=self.default_font)
        connect_btn.grid(row=0, column=2, padx=5) # Ajouter un bouton pour se connecter


        # Cadre des filtres et tri - caché avant connexion
        self.filters_frame = tk.Frame(self.root, bg="#E8F4FF") # Créer un cadre pour les filtres et le tri
        self.genre_filter = tk.StringVar() # Variable pour le filtre de genre
        self.year_filter = tk.StringVar() # Variable pour le filtre d'année
        self.min_rating_filter = tk.StringVar() # Variable pour le filtre de cote
        self.sort_option = tk.StringVar(value="titre") # Variable pour le tri

        # Logo
        logo_path = get_project_path("logo.png")
        if os.path.exists(logo_path):
            self.logo = tk.PhotoImage(file=logo_path)
            self.logo_reduit = self.logo.subsample(8, 8)
            self.logo_label = tk.Label(self.filters_frame, image=self.logo_reduit, bg="#E8F4FF").grid(row=0, column=4, padx=5)
        else:
            print(f"Logo non trouvé: {logo_path}")


        # Ligne de filtres
        tk.Label(self.filters_frame, text="Filtres :", bg="#E8F4FF", font=("Arial", 14, "bold")).grid(row=1, column=0, padx=5, sticky="e") # Ajouter un label
        tk.Label(self.filters_frame, text="Genre :", bg="#E8F4FF", font=self.default_font).grid(row=1, column=1, padx=5, sticky="e") # Ajouter un label
        tk.Entry(self.filters_frame, textvariable=self.genre_filter, font=self.default_font, width=15).grid(row=1, column=2, padx=5, sticky="w") # Ajouter un champ de saisie

        tk.Label(self.filters_frame, text="Année :", bg="#E8F4FF", font=self.default_font).grid(row=1, column=3, padx=5, sticky="e") # Ajouter un label
        tk.Entry(self.filters_frame, textvariable=self.year_filter, font=self.default_font, width=10).grid(row=1, column=4, padx=5, sticky="w") # Ajouter un champ de saisie
        tk.Label(self.filters_frame, text="Note Min. :", bg="#E8F4FF", font=self.default_font).grid(row=1, column=5, padx=5, sticky="e") # Ajouter un label
        tk.Entry(self.filters_frame, textvariable=self.min_rating_filter, font=self.default_font, width=10).grid(row=1, column=6, padx=5, sticky="w") # Ajouter un champ de saisie
        tk.Button(self.filters_frame, text="Appliquer Filtres", command=self.apply_filters, bg="#007ACC", fg="white", font=self.default_font).grid(row=1, column=7, padx=10) # Ajouter un bouton pour appliquer les filtres


        # Ligne de tri
        tk.Label(self.filters_frame, text="Tri :", bg="#E8F4FF", font=("Arial", 14, "bold")).grid(row=3, column=0, padx=5, sticky="e") # Ajouter un label
        tk.Label(self.filters_frame, text="Trier par :", bg="#E8F4FF", font=self.default_font).grid(row=3, column=3, padx=5, sticky="e") # Ajouter un label
        ttk.OptionMenu(self.filters_frame, self.sort_option, "titre", "titre", "annee", "cote").grid(row=3, column=4, padx=5, sticky="w") # Ajouter un menu déroulant pour le tri
        tk.Button(self.filters_frame, text="Appliquer Tri", command=self.sort_films, bg="#007ACC", fg="white", font=self.default_font).grid(row=3, column=6, padx=10) # Ajouter un bouton pour appliquer le tri

        # Séparateur horizontal
        separator = ttk.Separator(self.filters_frame, orient='horizontal') # Ajouter un séparateur horizontal
        separator.grid(row=4, column=0, columnspan=8, pady=10, sticky="ew") # Afficher le séparateur

        # Section d'affichage des films
        self.scroll_frame = tk.Frame(self.root, bg="#E8F4FF") # Créer un cadre pour afficher les films
        
        # Canvas pour les films
        self.canvas = tk.Canvas(self.scroll_frame, bg="#E8F4FF", highlightthickness=0) # Créer un canvas pour afficher les films
        self.canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5) # Afficher le canvas

        # Barre de défilement
        self.scrollbar = ttk.Scrollbar(self.scroll_frame, orient="vertical", command=self.canvas.yview) # Créer une barre de défilement
        self.scrollbar.pack(side="right", fill="y") # Afficher la barre de défilement
        self.canvas.configure(yscrollcommand=self.scrollbar.set) # Configurer la barre de défilement

        # Cadre intérieur pour les films
        self.films_frame = tk.Frame(self.canvas, bg="#E8F4FF") # Créer un cadre pour afficher les films
        self.canvas.create_window((0, 0), window=self.films_frame, anchor="nw") # Ajouter le cadre au canvas

        self.films_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))) # Ajuster la zone de défilement

        ## Button pour recommandation
        btn_reco = tk.Button(self.filters_frame, text="Recommandation", bg="#007ACC", fg="white", font=("Arial", 12), command=self.lancer_recommandation) # Ajouter un bouton pour lancer la recommandation
        btn_reco.grid(row=0, column=7, padx=5) # Afficher le bouton

## Méthode des connexions et déconnexions des utilisateurs ##
    def connect_user(self):
        """Connexion de l'utilisateur ou création d'un compte si inexistant"""
        self.user = self.username_entry.get().strip() # Récupérer le nom d'utilisateur
        if not self.user: # Vérifier si le nom d'utilisateur est vide
            messagebox.showerror("Erreur", "Veuillez entrer un nom d'utilisateur.") # Afficher un message d'erreur
            return

        utilisateurs = charger_utilisateurs() # Charger la liste des utilisateurs
        utilisateur_existant = next((u for u in utilisateurs if u['username'] == self.user), None) # Rechercher l'utilisateur par son nom

        if not utilisateur_existant:
            # L'utilisateur n'existe pas, on propose de le créer
            reponse = messagebox.askyesno("Nouvel Utilisateur", f"L'utilisateur '{self.user}' n'existe pas. Voulez-vous le créer ?")
            if reponse:  # Si l'utilisateur veut créer un compte
                new_id = (max((u['user_id'] for u in utilisateurs), default=0) + 1) # Générer un nouvel identifiant
                nouveau_utilisateur = { 
                    'user_id': new_id,
                    'username': self.user,
                    'notes': {}
                }
                utilisateurs.append(nouveau_utilisateur) # Ajouter le nouvel utilisateur à la liste
                sauvegarder_utilisateurs(utilisateurs) # Sauvegarder la liste des utilisateurs dans le fichier
                self.user_id = new_id # Affecter l'identifiant de l'utilisateur
                self.user_notes = {} # Initialiser les notes de l'utilisateur
            else:
                return # Si l'utilisateur ne veut pas créer un compte, on ne fait rien
        else:
            self.user_id = utilisateur_existant['user_id'] # Affecter l'identifiant de l'utilisateur
            self.user_notes = utilisateur_existant['notes'] # Récupérer les notes de l'utilisateur

        self.login_frame.pack_forget() # Masquer le cadre de connexion
        self.filters_frame.pack(pady=10, padx=10, fill="x") # Afficher le cadre de filtres et tri
        self.scroll_frame.pack(expand=True, fill="both") # Afficher le cadre d'affichage des films
        self.display_films(self.catalogue) # Afficher les films dans l'interface


    def deconnecter_utilisateur(self):
        """Permettre de se déconnecter et changer d'utilisateur sans fermer l'application."""
        # Réinitialiser les infos utilisateur
        self.user = None 
        self.user_id = None
        self.user_notes = {}

        # Masquer les cadres de navigation et d'affichage des films
        self.filters_frame.pack_forget() # Masquer le cadre de filtres et tri
        self.scroll_frame.pack_forget() # Masquer le cadre d'affichage des films

        # Ré-afficher le cadre de connexion
        self.login_frame.pack(pady=20)

        # Effacer le champ nom d'utilisateur
        self.username_entry.delete(0, tk.END)

## Méthode de gestion catalogue de films ##
    def display_films(self, films):
        """Afficher les films dans le cadre avec des options de notation"""
        for widget in self.films_frame.winfo_children(): # Parcourir les widgets  du cadre
            widget.destroy() # Supprimer le widget

        columns = 4 # Nombre de colonnes
        row = 0 # Ligne de départ
        col = 0 # Colonne de départ

        for film in films: 
            frame = tk.Frame(self.films_frame, bg="white", bd=2, relief="groove", width=220, height=250) # Créer un cadre pour chaque film
            frame.grid(row=row, column=col, padx=10, pady=10) # Afficher le cadre
            frame.pack_propagate(False) # Empêcher le cadre de changer de taille

            title_label = tk.Label(frame, text=film["titre"], font=("Arial", 12, "bold"), bg="white", wraplength=200) # Ajouter un label pour le titre du film
            title_label.pack(pady=5) # Afficher le label

            info_frame = tk.Frame(frame, bg="white") # Créer un cadre pour les informations du film
            info_frame.pack(pady=5) # Afficher le cadre

            tk.Label(info_frame, text=f"Genre : {film['genre']}", font=self.default_font, bg="white", anchor="w").pack(anchor="w") # Ajouter un label pour le genre
            tk.Label(info_frame, text=f"Année : {film['annee']}", font=self.default_font, bg="white", anchor="w").pack(anchor="w") # Ajouter un label pour l'année
            tk.Label(info_frame, text=f"Cote : {film['cote']}", font=self.default_font, bg="white", anchor="w").pack(anchor="w") # Ajouter un label pour la cote
            tk.Label(info_frame, text=f"Stock : {film['stock']}", font=("Arial", 10, "italic"), bg="white", anchor="w").pack(anchor="w") # Ajouter un label pour le stock
            tk.Label(info_frame, text=f"Prix : {film['prix_unitaire']} €", font=("Arial", 10, "italic"), bg="white", anchor="w").pack(anchor="w") # Ajouter un label pour le prix

            user_rating = self.user_notes.get(film["titre"], "Pas noté") # Récupérer la note de l'utilisateur pour ce film
            rating_label = tk.Label(frame, text=f"Votre note : {user_rating}", font=("Arial", 12, "italic"), bg="white") # Ajouter un label pour la note
            rating_label.pack(pady=5) # Afficher le label

            note_btn = tk.Button(frame, text="Attribuer note", command=lambda f=film, l=rating_label: self.rate_film(f, l), bg="#007ACC", fg="white", font=self.default_font) # Ajouter un bouton pour noter le film
            note_btn.pack(pady=5) # Afficher le bouton

            col += 1 # Passer à la colonne suivante
            if col >= columns:  # Si on atteint le nombre de colonnes
                col = 0  # Revenir à la première colonne
                row += 1 # Passer à la ligne suivante

    def ajouter_film(self):
        """Ouvre une fenêtre pour ajouter un film au catalogue"""
        add_film_window = tk.Toplevel(self.root) # Créer une nouvelle fenêtre
        add_film_window.title("Ajouter un Film") # Définir le titre de la fenêtre
        add_film_window.geometry("500x600") # Définir les dimensions de la fenêtre
        add_film_window.configure(bg="#E8F4FF") # Définir la couleur de fond

        form_font = ("Arial", 12) # Police du formulaire

        tk.Label(add_film_window, text="Titre du film :", font=form_font, bg="#E8F4FF").pack(pady=10) # Ajouter un label
        titre_entry = tk.Entry(add_film_window, font=("Arial", 14), width=40)
        titre_entry.pack(pady=5) # Ajouter un champ de saisie

        tk.Label(add_film_window, text="Genre du film :", font=form_font, bg="#E8F4FF").pack(pady=10) # Ajouter un label
        genre_entry = tk.Entry(add_film_window, font=("Arial", 14), width=40) # Créer un champ de saisie
        genre_entry.pack(pady=5) # Ajouter un champ de saisie

        tk.Label(add_film_window, text="Année du film :", font=form_font, bg="#E8F4FF").pack(pady=10) # Ajouter un label
        annee_entry = tk.Entry(add_film_window, font=("Arial", 14), width=40)
        annee_entry.pack(pady=5) # Ajouter un champ de saisie

        tk.Label(add_film_window, text="Cote du film (0-10) :", font=form_font, bg="#E8F4FF").pack(pady=10) # Ajouter un label
        cote_entry = tk.Entry(add_film_window, font=("Arial", 14), width=40) # Créer un champ de saisie
        cote_entry.pack(pady=5) # Ajouter un champ de saisie

        tk.Label(add_film_window, text="Quantité en stock :", font=form_font, bg="#E8F4FF").pack(pady=10) # Ajouter un label
        stock_entry = tk.Entry(add_film_window, font=("Arial", 14), width=40) # Créer un champ de saisie
        stock_entry.pack(pady=5) # Ajouter un champ de saisie

        tk.Label(add_film_window, text="Prix unitaire (€) :", font=form_font, bg="#E8F4FF").pack(pady=10) # Ajouter un label
        prix_entry = tk.Entry(add_film_window, font=("Arial", 14), width=40) # Créer un champ de saisie
        prix_entry.pack(pady=5) # Ajouter un champ de saisie

        def submit():
            """Fonction pour soumettre le formulaire et ajouter le film au catalogue"""
            titre = titre_entry.get().strip() # Récupérer le titre du film
            genre = genre_entry.get().strip() # Récupérer le genre du film
            annee_str = annee_entry.get().strip() # Récupérer l'année du film
            cote_str = cote_entry.get().strip() # Récupérer la cote du film
            stock_str = stock_entry.get().strip() # Récupérer la quantité en stock
            prix_str = prix_entry.get().strip() # Récupérer le prix unitaire

            if not titre or not genre or not annee_str or not cote_str or not stock_str or not prix_str: # Vérifier si les champs sont vides
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs.") # Afficher un message d'erreur
                return # Arrêter la fonction

            try: # Essayer de convertir l'année, la cote, la quantité et le prix en entier et float
                annee = int(annee_str)
                cote = float(cote_str)
                stock = int(stock_str)
                prix = float(prix_str)
            except ValueError: # Gérer l'erreur si la conversion échoue
                messagebox.showerror("Erreur", "L'année, la quantité doivent être des entiers et la cote, le prix doivent être des nombres.") # Afficher un message d'erreur
                return # Arrêter la fonction

            self.catalogue.append({"titre": titre, "genre": genre, "annee": annee, "cote": cote, "notes": {}, "stock": stock, "prix_unitaire": prix}) # Ajouter le film au catalogue
            exporter_catalogue(get_json_path("catalogue_films.json"), self.catalogue) # Sauvegarder le catalogue dans le fichier JSON
            self.display_films(self.catalogue) # Afficher les films dans l'interface
            add_film_window.destroy() # Fermer la fenêtre

        tk.Button(add_film_window, text="Ajouter le film", command=submit, bg="#007ACC", fg="white", font=("Arial", 14)).pack(pady=20) # Ajouter un bouton pour soumettre le formulaire

    
    def rate_film(self, film, label):
        """Permet à l'utilisateur de noter un film et met à jour la cote du film."""
        note = simpledialog.askfloat("Noter le film", f"Attribuez une note à '{film['titre']}' (0-10) :") # Demander à l'utilisateur de saisir une note
        if note is not None: # Vérifier que l'utilisateur a saisi une note
            if 0 <= note <= 10: # Vérifier si la note est entre 0 et 10
                # Rechercher le film dans self.catalogue
                for f in self.catalogue: 
                    if f["titre"] == film["titre"]: 
                        # S'assurer que le champ "notes" existe
                        if "notes" not in f: # Si le champ "notes" n'existe pas
                            f["notes"] = {} # Créer un champ "notes" vide

                        # Mettre à jour la note de l'utilisateur pour ce film
                        f["notes"][self.user] = note 
            
                        # Recalculer la cote comme la moyenne des notes
                        if f["notes"]:
                            f["cote"] = sum(f["notes"].values()) / len(f["notes"])
                        else:
                            f["cote"] = 0.0 # Si aucun utilisateur n'a noté le film, la cote est 0

                        # Sauvegarder les modifications dans le fichier JSON du catalogue
                        exporter_catalogue(get_json_path("catalogue_films.json"), self.catalogue)
                        break # Sortir de la boucle

                
                # Mettre à jour le label dans l'interface
                self.user_notes[film["titre"]] = note # Mettre à jour la note de l'utilisateur
                label.config(text=f"Votre note : {note}") # Mettre à jour le label

                # Mettre à jour l'affichage
                self.display_films(self.catalogue)

                # Mettre à jour le fichier ListeUtilisateurs.json si nécessaire
                ajouter_note_utilisateur(self.user, film["titre"], note)

            else: # Si la note n'est pas entre 0 et 10
                messagebox.showerror("Erreur", "La note doit être entre 0 et 10.") # Afficher un message d'erreur


    def apply_filters(self):
        """Appliquer les filtres de genre, année et cote sur le catalogue de films."""
        genre = self.genre_filter.get().strip().lower() # Récupérer le genre
        year = self.year_filter.get().strip() # Récupérer l'année
        min_rating = self.min_rating_filter.get().strip() # Récupérer la cote minimale

        filtered = self.catalogue # Copie du catalogue
        if genre: # Filtrer par genre
            filtered = [film for film in filtered if film["genre"].lower() == genre] 
        if year: # Filtrer par année
            try:
                y = int(year) # Convertir l'année en entier
                filtered = [film for film in filtered if film["annee"] == y] 
            except ValueError:
                messagebox.showerror("Erreur", "L'année doit être un entier.") # Afficher un message d'erreur
                return 
        if min_rating: # Filtrer par cote minimale
            try:
                mr = float(min_rating) # Convertir la cote minimale en float
                filtered = [film for film in filtered if film["cote"] >= mr]
            except ValueError:
                messagebox.showerror("Erreur", "La cote min. doit être un nombre.") # Afficher un message d'erreur
                return

        self.display_films(filtered) # Afficher les films filtrés dans l'interface

    def sort_films(self):
        """Trier les films du catalogue par titre, année ou cote."""
        sort_by = self.sort_option.get() # Récupérer l'option de tri
        if sort_by == "titre": # Trier par titre
            self.catalogue.sort(key=lambda x: x["titre"].lower())
        elif sort_by == "annee": # Trier par année
            self.catalogue.sort(key=lambda x: x["annee"])
        elif sort_by == "cote": # Trier par cote
            self.catalogue.sort(key=lambda x: x["cote"], reverse=True)
        self.display_films(self.catalogue) # Afficher les films triés dans l'interface

    def importer_catalogue_interface(self):
        """Ouvre une fenêtre pour importer un fichier JSON contenant un catalogue de films."""
        fichier = filedialog.askopenfilename(title="Sélectionnez un fichier catalogue",
                                             filetypes=[("Fichiers JSON", "*.json")]) # Ouvrir une boîte de dialogue pour sélectionner un fichier
        if fichier: # Si un fichier est sélectionné
            new_catalogue = importer_catalogue(fichier) # Importer le catalogue
            if new_catalogue: # Si le catalogue est importé avec succès
                self.catalogue = new_catalogue # Mettre à jour le catalogue
                self.display_films(self.catalogue) # Afficher les films dans l'interface
                for film in self.catalogue: # Parcourir les films du catalogue
                    if "notes" not in film: # S'assurer que le champ "notes" existe
                        film["notes"] = {} # Créer un champ "notes" vide
                messagebox.showinfo("Importation", "Catalogue importé avec succès!") # Afficher un message de confirmation
            else:
                messagebox.showerror("Erreur", "Impossible d'importer le catalogue.") # Afficher un message d'erreur
            

    def exporter_catalogue_interface(self):
        """Ouvre une fenêtre pour exporter le catalogue de films au format JSON."""
        fichier = filedialog.asksaveasfilename(defaultextension=".json",
                                               filetypes=[("Fichiers JSON", "*.json")]) # Ouvrir une boîte de dialogue pour enregistrer le fichier
        if fichier: # Si un fichier est sélectionné
            exporter_catalogue(fichier, self.catalogue) # Exporter le catalogue
            messagebox.showinfo("Exportation", "Catalogue exporté avec succès!") # Afficher un message de confirmation



## Méthodes de calcul des statistiques ##

    def films_mieux_notes_par_genre(self):
        """Retourne un dict {genre: (titre_film, cote)} du meilleur film par genre"""
        meilleur_par_genre = {} # Initialiser un dictionnaire vide
        for film in self.catalogue: # Parcourir les films du catalogue
            genre = film["genre"] # Récupérer le genre du film
            # S'assurer que la cote est correctement calculée
            cote = film["cote"] 
            if genre not in meilleur_par_genre or cote > meilleur_par_genre[genre][1]: # Si le genre n'est pas dans le dictionnaire ou si la cote est supérieure
                meilleur_par_genre[genre] = (film["titre"], cote) # Mettre à jour le meilleur film par genre
        return meilleur_par_genre # Retourner le dictionnaire

    def nombre_films_par_annee(self): 
        """Retourne un dict {annee: nombre_de_films}"""
        count = {} # Initialiser un dictionnaire vide 
        for film in self.catalogue: # Parcourir les films du catalogue
            annee = film["annee"]  # Récupérer l'année du film
            count[annee] = count.get(annee, 0) + 1 # Mettre à jour le nombre de films par année
        return count # Retourner le dictionnaire

    def nombre_total_films(self):
        """Retourne le nombre total de films"""
        return len(self.catalogue) # Retourner le nombre de films dans le catalogue

    def afficher_statistiques(self):
        """Affiche une fenêtre avec les statistiques calculées dans une interface plus conviviale, avec une scrollbar."""
        # Calculer les stats
        meilleurs_films = self.films_mieux_notes_par_genre() # Meilleurs films par genre
        nb_par_annee = self.nombre_films_par_annee() # Nombre de films par année
        total = self.nombre_total_films() # Nombre total de films

        # Créer une fenêtre Toplevel pour afficher les stats
        stats_window = tk.Toplevel(self.root) # Créer une nouvelle fenêtre
        stats_window.title("Statistiques") # Définir le titre de la fenêtre
        stats_window.geometry("600x400") # Définir les dimensions de la fenêtre
        stats_window.configure(bg="#E8F4FF") # Définir la couleur de fond

        # Police
        title_font = ("Arial", 16, "bold") # Police pour le titre
        subtitle_font = ("Arial", 14, "bold") # Police pour les sous-titres
        normal_font = ("Arial", 12) # Police normale

        # Cadre principal pour le canvas et scrollbar
        container = tk.Frame(stats_window, bg="#E8F4FF") 
        container.pack(expand=True, fill="both") 

        # Création du canvas
        canvas = tk.Canvas(container, bg="#E8F4FF", highlightthickness=0) # Créer un canvas pour afficher les statistiques
        canvas.pack(side="left", fill="both", expand=True) # Afficher le canvas

        # Barre de défilement
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview) # Créer une barre de défilement
        scrollbar.pack(side="right", fill="y") # Afficher la barre de défilement

        # Cadre intérieur qui va contenir tous les labels
        stats_frame = tk.Frame(canvas, bg="#E8F4FF")
        canvas.create_window((0,0), window=stats_frame, anchor="nw")

        # Fonction pour ajuster la zone de défilement
        def on_frame_configure(event):
            """Ajuste la zone de défilement en fonction de la taille du cadre intérieur"""
            canvas.configure(scrollregion=canvas.bbox("all")) # Ajuster la zone de défilement

        stats_frame.bind("<Configure>", on_frame_configure) # Appeler la fonction on_frame_configure quand le cadre est modifié
        canvas.configure(yscrollcommand=scrollbar.set) # Configurer la barre de défilement

        # Titre
        titre_label = tk.Label(stats_frame, text="=== Statistiques du Catalogue ===", font=title_font, bg="#E8F4FF") # Ajouter un label pour le titre
        titre_label.pack(pady=10) # Afficher le label

        # Frame pour la section "Meilleurs films par genre"
        meilleurs_frame = tk.Frame(stats_frame, bg="#E8F4FF")
        meilleurs_frame.pack(fill="x", pady=10)

        subtitle_meilleurs = tk.Label(meilleurs_frame, text="Meilleurs films par genre:", font=subtitle_font, bg="#E8F4FF") # Ajouter un label pour le sous-titre
        subtitle_meilleurs.pack(anchor="w") # Afficher le label

        for genre, (titre, cote) in meilleurs_films.items(): # Parcourir les meilleurs films par genre
            line = f"Genre: {genre}, Film: {titre}, Cote moyenne: {cote:.1f}"
            tk.Label(meilleurs_frame, text=line, font=normal_font, bg="#E8F4FF").pack(anchor="w", padx=20) # Ajouter un label pour chaque ligne

        # Séparateur
        ttk.Separator(stats_frame, orient="horizontal").pack(fill="x", pady=10)

        # Frame pour la section "Nombre de films par année"
        annee_frame = tk.Frame(stats_frame, bg="#E8F4FF") # Créer un cadre pour afficher le nombre de films par année
        annee_frame.pack(fill="x", pady=10) # Afficher le cadre

        subtitle_annee = tk.Label(annee_frame, text="Nombre de films par année:", font=subtitle_font, bg="#E8F4FF") # Ajouter un label pour le sous-titre
        subtitle_annee.pack(anchor="w") # Afficher le label

        for annee, count in sorted(nb_par_annee.items()): # Parcourir le nombre de films par année
            line = f"Année {annee}: {count} film(s)"
            tk.Label(annee_frame, text=line, font=normal_font, bg="#E8F4FF").pack(anchor="w", padx=20) # Ajouter un label pour chaque ligne

        # Séparateur
        ttk.Separator(stats_frame, orient="horizontal").pack(fill="x", pady=10)

        # Frame pour le nombre total de films
        total_frame = tk.Frame(stats_frame, bg="#E8F4FF")
        total_frame.pack(fill="x", pady=10)

        subtitle_total = tk.Label(total_frame, text="Nombre total de films:", font=subtitle_font, bg="#E8F4FF") # Ajouter un label pour le sous-titre
        subtitle_total.pack(anchor="w") # Afficher le label

        tk.Label(total_frame, text=f"{total}", font=("Arial", 12, "bold"), bg="#E8F4FF").pack(anchor="w", padx=20, pady=5) # Afficher le nombre total de films 



 ## Méthodes de gestion des ventes ##
    # --------------------------------------------------------------------
    # 1) AJOUTER UNE VENTE
    # --------------------------------------------------------------------
    def ajouter_vente_interface(self):
        """Ouvre une fenêtre permettant de sélectionner un film, d’indiquer la quantité,
        et d’enregistrer une vente en mettant à jour le stock et le fichier ventes.json."""

        # Vérifier si un utilisateur est connecté
        if not self.user: 
            messagebox.showerror("Erreur", "Aucun utilisateur connecté. Connectez-vous d'abord.") # Afficher un message d'erreur
            return

        vente_window = tk.Toplevel(self.root) # Créer une nouvelle fenêtre
        vente_window.title("Enregistrer une vente") # Définir le titre de la fenêtre
        vente_window.geometry("400x300") # Définir les dimensions de la fenêtre
        vente_window.configure(bg="#E8F4FF") # Définir la couleur de fond

        font_default = ("Arial", 12) # Police par défaut

        # Liste des titres de films disposant d'un stock > 0
        films_dispo = [f["titre"] for f in self.catalogue if f.get("stock", 0) > 0]

        tk.Label(vente_window, text="Sélectionnez un film :", font=font_default, bg="#E8F4FF").pack(pady=5) # Ajouter un label
        film_var = tk.StringVar() # Variable pour stocker le film sélectionné
        film_combo = ttk.Combobox(vente_window, textvariable=film_var, values=films_dispo, state='readonly') # Ajouter une combobox pour sélectionner un film
        film_combo.pack(pady=5) # Afficher la combobox

        # Quand on choisit un film dans la combobox, on pré-remplit le prix unitaire
        prix_var = tk.DoubleVar(value=0.0) # Variable pour stocker le prix unitaire

        def on_film_selected(event):
            """Fonction appelée lorsqu'un film est sélectionné dans la combobox"""
            titre_choisi = film_var.get() # Récupérer le titre du film choisi
            # Trouver le film dans self.catalogue
            for film in self.catalogue: # Parcourir les films du catalogue
                if film["titre"] == titre_choisi: # Si le titre du film correspond
                    prix_var.set(film.get("prix_unitaire", 0.0)) # Pré-remplir le prix unitaire
                    break # Sortir de la boucle

        film_combo.bind("<<ComboboxSelected>>", on_film_selected) # Appeler la fonction on_film_selected lorsqu'un film est sélectionné

        tk.Label(vente_window, text="Prix unitaire :", font=font_default, bg="#E8F4FF").pack(pady=5) # Ajouter un label
        prix_entry = tk.Entry(vente_window, textvariable=prix_var, font=font_default, state='readonly') # Ajouter un champ de saisie pour le prix unitaire
        prix_entry.pack(pady=5) # Afficher le champ de saisie

        tk.Label(vente_window, text="Quantité :", font=font_default, bg="#E8F4FF").pack(pady=5) # Ajouter un label
        quantite_entry = tk.Entry(vente_window, font=font_default) # Ajouter un champ de saisie pour la quantité
        quantite_entry.pack(pady=5) # Afficher le champ de saisie
        

        def valider_vente():
            """Fonction pour valider la vente et mettre à jour le stock et le fichier ventes.json"""
            titre_choisi = film_var.get() # Récupérer le titre du film choisi
            if not titre_choisi: 
                messagebox.showerror("Erreur", "Veuillez sélectionner un film.") # Afficher un message d'erreur
                return # Arrêter la fonction
            try:
                quantite_vendue = int(quantite_entry.get()) # Récupérer la quantité vendue
            except ValueError:
                messagebox.showerror("Erreur", "Veuillez saisir une quantité valide.") # Afficher un message d'erreur
                return # Arrêter la fonction

            # Récupérer le film dans self.catalogue
            film_selectionne = None # Initialiser le film sélectionné à None
            for film in self.catalogue: # Parcourir les films du catalogue
                if film["titre"] == titre_choisi: # Si le titre du film correspond
                    film_selectionne = film # Mettre à jour le film sélectionné
                    break # Sortir de la boucle

            if film_selectionne is None: # Si le film n'est pas trouvé
                messagebox.showerror("Erreur", "Film introuvable dans le catalogue.") # Afficher un message d'erreur
                return

            stock_actuel = film_selectionne.get("stock", 0) # Récupérer le stock actuel
            if quantite_vendue <= 0:  # Vérifier si la quantité est supérieure à 0
                messagebox.showerror("Erreur", "La quantité doit être supérieure à 0.") 
                return
            if quantite_vendue > stock_actuel: # Vérifier si la quantité est inférieure au stock
                messagebox.showerror("Erreur", f"Stock insuffisant. Stock actuel: {stock_actuel}")
                return

            # Mettre à jour le stock
            film_selectionne["stock"] = stock_actuel - quantite_vendue

            # Calculer le revenu total
            prix_uni = film_selectionne.get("prix_unitaire", 0.0)
            revenu_total = quantite_vendue * prix_uni

            # Créer l'entrée de vente
            nouvelle_vente = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "film": titre_choisi,
                "vendeur": self.user,  # utilisateur courant
                "quantite": quantite_vendue,
                "prix_unitaire": prix_uni,
                "revenu_total": revenu_total
            }
            self.ventes.append(nouvelle_vente) # Ajouter la vente à la liste des ventes
            sauvegarder_ventes(self.ventes)  # mise à jour ventes.json

            # Sauvegarder le catalogue mis à jour (stock modifié)
            exporter_catalogue(get_json_path("catalogue_films.json"), self.catalogue)

            messagebox.showinfo("Succès", "Vente enregistrée avec succès.")
            vente_window.destroy() # Fermer la fenêtre

            self.display_films(self.catalogue) # Mettre à jour l'affichage des films

        tk.Button(vente_window, text="Valider la vente", bg="#007ACC", fg="white", font=font_default, command=valider_vente).pack(pady=15) # Ajouter un bouton pour valider la vente


    # --------------------------------------------------------------------
    # 2) HISTORIQUE DES VENTES
    # --------------------------------------------------------------------
    def afficher_historiques_ventes(self):
        """Ouvre une nouvelle fenêtre avec un tableau (Treeview) résumant toutes les ventes passées :
           titre du film, date, utilisateur, quantité, prix unitaire ou total.
        """
        hist_window = tk.Toplevel(self.root) # Créer une nouvelle fenêtre
        hist_window.title("Historique des ventes") # Définir le titre de la fenêtre
        hist_window.geometry("700x400") # Définir les dimensions de la fenêtre
        hist_window.configure(bg="#E8F4FF") # Définir la couleur de fond

        cols = ("date", "film", "vendeur", "quantite", "prix_unitaire", "revenu_total") # Colonnes du tableau
        tree = ttk.Treeview(hist_window, columns=cols, show='headings') # Créer un Treeview pour afficher les ventes
        tree.pack(expand=True, fill="both", padx=10, pady=10) # Afficher le Treeview

        # Configuration des en-têtes
        tree.heading("date", text="Date")
        tree.heading("film", text="Film")
        tree.heading("vendeur", text="Vendeur")
        tree.heading("quantite", text="Quantité")
        tree.heading("prix_unitaire", text="Prix Uni.")
        tree.heading("revenu_total", text="Revenu")

        # Ajuster la largeur des colonnes
        for c in cols: # Parcourir les colonnes
            tree.column(c, stretch=True, width=100) # Ajuster la largeur des colonnes

        # Insérer les lignes (les ventes)
        for v in self.ventes: # Parcourir les ventes
            tree.insert("", tk.END, values=( 
                v.get("date", ""),
                v.get("film", ""),
                v.get("vendeur", ""),
                v.get("quantite", ""),
                v.get("prix_unitaire", ""),
                v.get("revenu_total", "")
            )) # Insérer une ligne dans le tableau

    # --------------------------------------------------------------------
    # 3) ANALYSE DES VENTES (TABLEAU DE BORD + GRAPHIQUES)
    # --------------------------------------------------------------------
    def afficher_analyse_ventes(self):
        """Ouvre une fenêtre avec un tableau de bord des ventes, des graphiques et des statistiques."""
        # Créer la fenêtre Toplevel
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("Analyse des ventes")
        analysis_window.geometry("900x600")
        analysis_window.configure(bg="#E8F4FF")

        #container 
        container = tk.Frame(analysis_window, bg="#E8F4FF")
        container.pack(expand=True, fill="both")

        # Canvas
        canvas = tk.Canvas(container, bg="#E8F4FF", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        # Barre de défilement verticale
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Frame 
        analysis_frame = tk.Frame(canvas, bg="#E8F4FF") # Créer un cadre pour afficher l'analyse des ventes
        canvas.create_window((0, 0), window=analysis_frame, anchor="nw") # Créer une fenêtre dans le canvas

        # Fonction pour ajuster la région de défilement
        def on_frame_configure(event):
            """Ajuste la zone de défilement en fonction de la taille du cadre intérieur"""
            canvas.configure(scrollregion=canvas.bbox("all")) # Ajuster la zone de défilement

        analysis_frame.bind("<Configure>", on_frame_configure) # Appeler la fonction on_frame_configure quand le cadre est modifié

        # 2) statistiques
        total_revenu = 0.0
        ventes_par_jour = {}         # date (YYYY-MM-DD) -> revenu du jour
        genres_vendus = {}           # genre -> quantité totale vendue
        ventes_par_utilisateur = {}  # username -> quantité totale vendue
        nombre_ventes = len(self.ventes) 
        total_films_vendus = 0

        for vente in self.ventes:
            # Revenu total
            total_revenu += vente["revenu_total"] 

            # Grouper par jour (extrait la partie "YYYY-MM-DD" de "YYYY-MM-DD HH:MM:SS")
            date_str = vente["date"].split(" ")[0] # Extraire la date
            ventes_par_jour[date_str] = ventes_par_jour.get(date_str, 0.0) + vente["revenu_total"] # Ajouter le revenu du jour

            # Récupérer le genre du film en cherchant dans le catalogue
            film_titre = vente["film"] # Récupérer le titre du film
            quantite = vente["quantite"] # Récupérer la quantité vendue
            total_films_vendus += quantite # Ajouter la quantité vendue au total

            # Identifier le genre
            for film in self.catalogue: # Parcourir les films du catalogue
                if film["titre"] == film_titre: # Si le titre du film correspond
                    genre = film.get("genre", "Inconnu") # Récupérer le genre du film
                    genres_vendus[genre] = genres_vendus.get(genre, 0) + quantite # Ajouter la quantité vendue par genre
                    break # Sortir de la boucle

            # Comptabiliser les ventes par utilisateur
            vendeur = vente.get("vendeur", "Inconnu") # Récupérer le vendeur
            ventes_par_utilisateur[vendeur] = ventes_par_utilisateur.get(vendeur, 0) + quantite # Ajouter la quantité vendue par utilisateur

        # Afficher un tableau de bord textuel
        font_title = ("Arial", 16, "bold") # Police pour le titre
        font_default = ("Arial", 12) # Police par défaut

        board_frame = tk.Frame(analysis_frame, bg="#E8F4FF") # Créer un cadre pour afficher le tableau de bord
        board_frame.pack(fill="x", pady=10) # Afficher le cadre

        tk.Label(board_frame, text="Tableau de bord des ventes", font=font_title, bg="#E8F4FF").pack(pady=5) # Ajouter un label pour le titre

        tk.Label(board_frame, text=f"Revenu total : {total_revenu:.2f} €", bg="#E8F4FF", font=font_default).pack(anchor="w", padx=20) # Ajouter un label pour le revenu total
        tk.Label(board_frame, text=f"Nombre total de ventes : {nombre_ventes}", bg="#E8F4FF", font=font_default).pack(anchor="w", padx=20) # Ajouter un label pour le nombre total de ventes
        tk.Label(board_frame, text=f"Nombre total de films vendus : {total_films_vendus}", bg="#E8F4FF", font=font_default).pack(anchor="w", padx=20) # Ajouter un label pour le nombre total de films vendus

        # Créer les figures matplotlib 
        fig1 = plt.Figure(figsize=(9, 6), dpi=100) # Créer une figure pour les graphiques

        # Subplot 1 : Revenu par jour (line chart)
        ax1 = fig1.add_subplot(1,2,1)  # 2 lignes, 2 colonnes, 1ère position
        sorted_dates = sorted(ventes_par_jour.keys()) # Trier les dates
        x_dates = sorted_dates # Dates en abscisse
        y_revenus = [ventes_par_jour[d] for d in x_dates] # Revenus en ordonnée

        ax1.plot(x_dates, y_revenus, marker='o', color='blue') # Tracer le graphique
        ax1.set_title("Revenu par jour") # Ajouter un titre
        ax1.set_xlabel("Date") # Ajouter une étiquette pour l'axe des x
        ax1.set_ylabel("Revenu (€)") # Ajouter une étiquette pour l'axe des y
        ax1.tick_params(axis='x', rotation=45) # Faire pivoter les dates

        # Subplot 2 : Ventes par genre (bar chart)
        ax2 = fig1.add_subplot(1,2,2)  # 1 lignes, 2 colonnes, 2ème position
        genres = list(genres_vendus.keys()) # Genres
        q_genres = [genres_vendus[g] for g in genres] # Quantités vendues

        ax2.bar(genres, q_genres, color='green') # Tracer le graphique
        ax2.set_title("Quantité vendue par genre") # Ajouter un titre
        ax2.set_xlabel("Genre") # Ajouter une étiquette pour l'axe des x
        ax2.set_ylabel("Quantité") # Ajouter une étiquette pour l'axe des y
        ax2.tick_params(axis='x', rotation=45) # Faire pivoter les genres

        # figure 2 : Ventes par utilisateur
        fig2 = plt.Figure(figsize=(9, 6), dpi=100) # Créer une nouvelle figure
        ax3 = fig2.add_subplot(1,1,1)  # 1 ligne, 1 colonne, 1ère position
        users = list(ventes_par_utilisateur.keys()) # Utilisateurs
        q_users = [ventes_par_utilisateur[u] for u in users] # Quantités vendues

        ax3.bar(users, q_users, color='orange') # Tracer le graphique
        ax3.set_title("Quantité vendue par utilisateur") # Ajouter un titre
        ax3.set_xlabel("Utilisateur")   # Ajouter une étiquette pour l'axe des x
        ax3.set_ylabel("Quantité") # Ajouter une étiquette pour l'axe des y
        ax3.tick_params(axis='x', rotation=45) # Faire pivoter les utilisateurs

        fig1.tight_layout() # Ajuster la disposition des graphiques
        fig2.tight_layout() # Ajuster la disposition des graphiques

        # figure 3 : Stock de films
        fig3 = plt.Figure(figsize=(9, 6), dpi=100) # Créer une nouvelle figure
        ax4 = fig3.add_subplot(1,1,1)  # 1 ligne, 1 colonne, 1ère position
        films_titres = [film["titre"] for film in self.catalogue] # Titres des films
        films_stock  = [film["stock"] for film in self.catalogue] # Stock des films
        ax4.bar(films_titres, films_stock, color='purple') # Tracer le graphique
        ax4.set_title("Stock disponible par film") # Ajouter un titre
        ax4.set_xlabel("Film") # Ajouter une étiquette pour l'axe des x
        ax4.set_ylabel("Stock") # Ajouter une étiquette pour l'axe des y
        ax4.tick_params(axis='x', rotation=90) # Faire pivoter les titres des films

        fig1.tight_layout() # Ajuster la disposition des graphiques
        fig2.tight_layout() # Ajuster la disposition des graphiques
        fig3.tight_layout() # Ajuster la disposition des graphiques

        # 5) Intégrer la figure dans Tkinter
        canvas_fig = FigureCanvasTkAgg(fig1, master=analysis_frame) # Créer un canvas pour afficher la figure
        canvas_fig.draw() # Afficher la figure
        canvas_fig.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10) # Afficher le canvas

        canvas_fig = FigureCanvasTkAgg(fig2, master=analysis_frame) 
        canvas_fig.draw()
        canvas_fig.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)

        canvas_fig = FigureCanvasTkAgg(fig3, master=analysis_frame)
        canvas_fig.draw()
        canvas_fig.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)
 
    def lancer_recommandation(self): 
        """Lancer le programme de recommandation externe et afficher les recommandations."""   
        user_cible = self.user # Utilisateur cible

        # Ecrire dans un fichier JSON
        import json 
        with open(get_json_path("target_user.json"),"w",encoding="utf-8") as f: # Ouvrir le fichier en écriture
            json.dump({"target": user_cible}, f) # Ecrire le nom de l'utilisateur cible

        exe_path = get_project_path("recommandation.exe")
        result = subprocess.run([exe_path], capture_output=True, text=True) # Lancer le programme de recommandation
        if result.returncode != 0: # Si le programme a retourné une erreur
            messagebox.showerror("Erreur", f"Échec : {result.stderr}") # Afficher un message d'erreur
            return  # Sortir de la fonction
        
        # Lire recommendations.json
        try:
            with open(get_json_path("recommendations.json"),"r",encoding="utf-8") as f: # Ouvrir le fichier en lecture
                data = json.load(f) # Charger les données
        except (FileNotFoundError, json.JSONDecodeError) as e:
            messagebox.showerror("Erreur", "Impossible de lire recommendations.json") # Afficher un message d'erreur
            return # Sortir de la fonction

        recs = data.get("recommendations", []) # Récupérer les recommandations
        if not recs: # Si aucune recommandation n'est disponible
            messagebox.showinfo("Recommandation", "Aucune recommandation disponible.") # Afficher un message d'information
            return # Sortir de la fonction

        txt = f"Recommandations pour {data.get('target')}:\n\n" # Texte des recommandations
        for rec in recs: # Parcourir les recommandations
            txt += f" - {rec['titre']}\n" # Ajouter le titre du film à la liste
        messagebox.showinfo("Recommandation", txt) # Afficher les recommandations dans une boîte de dialogue


## MAIN ##
def main():
    fichier_catalogue = get_json_path("catalogue_films.json") # Fichier JSON contenant le catalogue de films
    catalogue = importer_catalogue(fichier_catalogue) # Importer le catalogue de films

    root = tk.Tk() # Créer une fenêtre principale
    app = FilmCatalogueApp(root, catalogue) # Créer une instance de l'application
    root.mainloop() # Lancer la boucle principale

if __name__ == "__main__": # Si le script est exécuté en tant que programme principal
    main() # Appeler la fonction main() pour lancer l'application
