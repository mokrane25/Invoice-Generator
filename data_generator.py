from faker import Faker
import json
import os
import random
from pathlib import Path
import cairosvg

class GenerateurDonnees:
    def __init__(self, dossier_base, locale='fr_FR'):
        """
        Initialise le générateur de données avec Faker en français
        """
        self.fake = Faker(locale)
        self.dossier_base = Path(dossier_base)
        
        # Créer les dossiers nécessaires
        for dossier in ['fournisseurs', 'clients', 'articles', 'logos']:
            (self.dossier_base / dossier).mkdir(parents=True, exist_ok=True)

    def generer_entreprise(self):
        """
        Génère des données d'entreprise réalistes
        """
        return {
            "nom": self.fake.company(),
            "adresse": self.fake.street_address(),
            "code_postal": self.fake.postcode(),
            "ville": self.fake.city(),
            "telephone": self.fake.phone_number(),
            "email": self.fake.company_email(),
            "siret": self.fake.siret(),
            "tva_num": f"FR{self.fake.random_number(digits=11)}",
        }

    def generer_fournisseurs(self, nombre=10):
        """
        Génère et sauvegarde des données de fournisseurs
        """
        for i in range(nombre):
            fournisseur = self.generer_entreprise()
            fichier = self.dossier_base / 'fournisseurs' / f'fournisseur_{i+1}.json'
            with open(fichier, 'w', encoding='utf-8') as f:
                json.dump(fournisseur, f, ensure_ascii=False, indent=2)

    def generer_clients(self, nombre=20):
        """
        Génère et sauvegarde des données de clients
        """
        for i in range(nombre):
            client = self.generer_entreprise()
            fichier = self.dossier_base / 'clients' / f'client_{i+1}.json'
            with open(fichier, 'w', encoding='utf-8') as f:
                json.dump(client, f, ensure_ascii=False, indent=2)

    def generer_articles(self, nombre_listes=5, articles_par_liste=10):
        """
        Génère et sauvegarde des listes d'articles
        """
        categories = [
            "Matériel informatique", "Fournitures de bureau",
            "Mobilier", "Services consulting", "Licences logicielles"
        ]
        
        produits_par_categorie = {
            "Matériel informatique": [
                "Ordinateur portable", "Écran LCD", "Clavier sans fil",
                "Souris ergonomique", "Dock station", "Webcam HD",
                "Disque SSD", "RAM DDR4", "Carte graphique", "Processeur"
            ],
            "Fournitures de bureau": [
                "Papier A4", "Stylos", "Classeurs", "Post-it",
                "Agrafeuses", "Marqueurs", "Enveloppes", "Cahiers",
                "Chemises cartonnées", "Trombones"
            ],
            "Mobilier": [
                "Bureau ergonomique", "Chaise de bureau", "Armoire",
                "Lampe de bureau", "Table de réunion", "Caisson",
                "Support écran", "Repose-pieds", "Tableau blanc", "Étagère"
            ],
            "Services consulting": [
                "Formation", "Audit", "Développement sur mesure",
                "Maintenance", "Support technique", "Conseil stratégique",
                "Gestion de projet", "Analyse des données", "Migration système",
                "Sécurité informatique"
            ],
            "Licences logicielles": [
                "Suite bureautique", "Antivirus", "Logiciel de CAO",
                "Système d'exploitation", "Base de données", "CRM",
                "Logiciel de comptabilité", "Outil de collaboration",
                "Logiciel de monitoring", "Solution cloud"
            ]
        }

        for i in range(nombre_listes):
            categorie = random.choice(categories)
            articles = []
            
            for _ in range(articles_par_liste):
                nom_produit = random.choice(produits_par_categorie[categorie])
                article = {
                    "description": f"{nom_produit} - {self.fake.catch_phrase()}",
                    "reference": self.fake.ean13(),
                    "categorie": categorie,
                    "prix": round(random.uniform(10, 2000), 2),
                    "unite": random.choice(["pièce", "lot", "jour", "mois", "licence"]),
                }
                articles.append(article)

            fichier = self.dossier_base / 'articles' / f'liste_articles_{i+1}.json'
            with open(fichier, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)



    def generer_logos_exemple(self, nombre=5):
        """
        Génère des logos PNG plus élaborés
        """
        formes = ['circle', 'square', 'triangle']
        
        for i in range(nombre):
            # Génère une couleur aléatoire
            couleur = f'#{random.randint(0, 0xFFFFFF):06x}'
            couleur_secondaire = f'#{random.randint(0, 0xFFFFFF):06x}'
            forme = random.choice(formes)
            
            # Création du SVG avec des éléments plus sophistiqués
            logo_svg = f'''<?xml version="1.0" encoding="UTF-8"?>
            <svg width="200" height="100" xmlns="http://www.w3.org/2000/svg">
                <!-- Fond avec gradient -->
                <defs>
                    <linearGradient id="grad{i}" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:{couleur};stop-opacity:0.1"/>
                        <stop offset="100%" style="stop-color:{couleur_secondaire};stop-opacity:0.1"/>
                    </linearGradient>
                </defs>
                <rect width="200" height="100" fill="url(#grad{i})"/>
                
                <!-- Forme principale -->
                {self._generer_forme(forme, couleur)}
                
                <!-- Texte stylisé -->
                <text x="100" y="60" 
                    font-family="Arial" 
                    font-size="20" 
                    font-weight="bold"
                    fill="{couleur}"
                    text-anchor="middle">
                    Logo {i+1}
                </text>
                
                <!-- Élément décoratif -->
                <path d="M160 20 Q180 20 180 40" 
                    stroke="{couleur_secondaire}" 
                    fill="none" 
                    stroke-width="2"/>
            </svg>'''
            
            fichier_svg = self.dossier_base / 'logos' / f'logo_{i+1}.svg'
            fichier_png = self.dossier_base / 'logos' / f'logo_{i+1}.png'

            # Écriture du fichier SVG temporaire
            with open(fichier_svg, 'w', encoding='utf-8') as f:
                f.write(logo_svg)

            # Conversion du fichier SVG en PNG
            cairosvg.svg2png(url=str(fichier_svg), write_to=str(fichier_png))

            # Suppression du fichier SVG après conversion
            fichier_svg.unlink()

    def _generer_forme(self, forme, couleur):
        """Génère le code SVG pour différentes formes"""
        if forme == 'circle':
            return f'<circle cx="50" cy="50" r="30" fill="{couleur}" opacity="0.8"/>'
        elif forme == 'square':
            return f'<rect x="20" y="20" width="60" height="60" fill="{couleur}" opacity="0.8"/>'
        else:  # triangle
            return f'<polygon points="50,20 20,70 80,70" fill="{couleur}" opacity="0.8"/>'

        
    

# Exemple d'utilisation
if __name__ == "__main__":
    generateur = GenerateurDonnees("donnees_test_factures")
    
    # Générer toutes les données
    generateur.generer_fournisseurs(10)  # 10 fournisseurs
    generateur.generer_clients(20)       # 20 clients
    generateur.generer_articles(5)       # 5 listes d'articles
    generateur.generer_logos_exemple()   # 5 logos exemple

    print("Données de test générées avec succès !")
    
    
    
    
    
    
    