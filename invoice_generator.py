from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import cm
import os
import random
from datetime import datetime, timedelta
import json
from pathlib import Path

class FactureGenerator:
    def __init__(self, dossier_base):
        """
        Initialise le générateur de factures
        
        Args:
            dossier_base (str): Chemin vers le dossier contenant les données
        """
        self.dossier_base = Path(dossier_base)
        
    def charger_element_aleatoire(self, sous_dossier):
        """
        Charge un élément aléatoire depuis un sous-dossier spécifié
        
        Args:
            sous_dossier (str): Nom du sous-dossier ('fournisseurs', 'clients', etc.)
        """
        chemin = self.dossier_base / sous_dossier
        if not chemin.exists():
            raise Exception(f"Le dossier {sous_dossier} n'existe pas")
            
        fichiers = list(chemin.glob('*.json'))
        if not fichiers:
            raise Exception(f"Le dossier {sous_dossier} est vide")
            
        fichier_choisi = random.choice(fichiers)
        with open(fichier_choisi, 'r', encoding='utf-8') as f:
            return json.load(f)


    def charger_logo_aleatoire(self):
        """Charge un logo PNG aléatoire"""
        logos_dir = self.dossier_base / 'logos'
        logos = list(logos_dir.glob('*.png'))  # Changez ici pour charger des PNG
        if not logos:
            raise Exception("Aucun logo trouvé")
        return random.choice(logos)


    def generer_numero_facture(self):
        """Génère un numéro de facture unique"""
        return f"FACT-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

    def creer_facture_pdf(self, nom_fichier):
        """
        Crée une facture PDF avec les éléments aléatoires
        
        Args:
            nom_fichier (str): Nom du fichier PDF à créer
        """
        # Charger les données
        fournisseur = self.charger_element_aleatoire('fournisseurs')
        client = self.charger_element_aleatoire('clients')
        liste_articles = self.charger_element_aleatoire('articles')
        
        # Sélectionner un sous-ensemble aléatoire d'articles
        articles = random.sample(liste_articles, k=random.randint(1, 5))
        
        # Créer le PDF
        c = canvas.Canvas(nom_fichier, pagesize=A4)
        largeur, hauteur = A4

        # Ajouter le logo
        logo_path = self.charger_logo_aleatoire()
        c.drawImage(str(logo_path), 50, hauteur - 150, width=200, height=100)

        # Informations fournisseur
        c.setFont("Helvetica-Bold", 12)
        y = hauteur - 200
        c.drawString(50, y, "Fournisseur:")
        c.setFont("Helvetica", 10)
        y -= 15
        c.drawString(50, y, fournisseur['nom'])
        y -= 15
        c.drawString(50, y, fournisseur['adresse'])
        y -= 15
        c.drawString(50, y, f"{fournisseur['code_postal']} {fournisseur['ville']}")
        y -= 15
        c.drawString(50, y, f"Tél: {fournisseur['telephone']}")
        y -= 15
        c.drawString(50, y, f"SIRET: {fournisseur['siret']}")
        y -= 15
        c.drawString(50, y, f"N° TVA: {fournisseur['tva_num']}")

        # Informations client
        c.setFont("Helvetica-Bold", 12)
        y = hauteur - 200
        c.drawString(300, y, "Client:")
        c.setFont("Helvetica", 10)
        y -= 15
        c.drawString(300, y, client['nom'])
        y -= 15
        c.drawString(300, y, client['adresse'])
        y -= 15
        c.drawString(300, y, f"{client['code_postal']} {client['ville']}")
        y -= 15
        c.drawString(300, y, f"Tél: {client['telephone']}")
        y -= 15
        c.drawString(300, y, f"Email: {client['email']}")

        # Numéro de facture et date
        numero_facture = self.generer_numero_facture()
        date_facture = datetime.now().strftime("%d/%m/%Y")
        date_echeance = (datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y")
        
        y = hauteur - 350
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, f"Facture N° {numero_facture}")
        c.setFont("Helvetica", 10)
        c.drawString(50, y - 20, f"Date d'émission: {date_facture}")
        c.drawString(50, y - 35, f"Date d'échéance: {date_echeance}")

        # Tableau des articles
        data = [['Description', 'Référence', 'Quantité', 'Prix unitaire HT', 'Total HT']]
        total_ht = 0
        
        for article in articles:
            quantite = random.randint(1, 10)
            prix_unitaire = article['prix']
            total_ligne = quantite * prix_unitaire
            total_ht += total_ligne
            data.append([
                article['description'][:40],  # Limite la longueur de la description
                article['reference'],
                str(quantite),
                f"{prix_unitaire:.2f} €",
                f"{total_ligne:.2f} €"
            ])

        # Calculs des totaux
        tva = total_ht * 0.20
        total_ttc = total_ht + tva

        # Ajouter les totaux au tableau
        data.extend([
            ['', '', '', 'Total HT', f"{total_ht:.2f} €"],
            ['', '', '', 'TVA (20%)', f"{tva:.2f} €"],
            ['', '', '', 'Total TTC', f"{total_ttc:.2f} €"]
        ])

        # Créer et dessiner le tableau
        table = Table(data, colWidths=[8*cm, 3*cm, 2*cm, 3*cm, 3*cm])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Alignement à gauche pour les descriptions
            ('ALIGN', (-2, -3), (-1, -1), 'RIGHT'),  # Alignement à droite pour les totaux
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONT', (0, -3), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        table.wrapOn(c, largeur - 100, 500)
        table.drawOn(c, 50, y - 350)

        # Pied de page
        c.setFont("Helvetica", 8)
        c.drawString(50, 50, f"Conditions de paiement : règlement à 30 jours - Date d'échéance : {date_echeance}")
        c.drawString(50, 35, "En cas de retard de paiement, une pénalité de 3 fois le taux d'intérêt légal sera appliquée")
        c.drawString(50, 20, f"Facture générée automatiquement le {datetime.now().strftime('%d/%m/%Y à %H:%M')}")

        c.save()
        return nom_fichier

    def generer_lot_factures(self, nombre, dossier_sortie="factures"):
        """
        Génère plusieurs factures
        
        Args:
            nombre (int): Nombre de factures à générer
            dossier_sortie (str): Dossier où sauvegarder les factures
        """
        dossier_sortie = Path(dossier_sortie)
        dossier_sortie.mkdir(parents=True, exist_ok=True)
        
        factures_generees = []
        for i in range(nombre):
            nom_fichier = dossier_sortie / f"facture_{i+1}.pdf"
            self.creer_facture_pdf(str(nom_fichier))
            factures_generees.append(nom_fichier)
            
        return factures_generees

# Exemple d'utilisation
if __name__ == "__main__":
    # Supposons que les données ont été générées dans le dossier "donnees_test_factures"
    generateur = FactureGenerator("./donnees_test_factures")
    
    # Générer une seule facture
    generateur.creer_facture_pdf("facture_test.pdf")
    
    # Ou générer un lot de factures
    #factures = generateur.generer_lot_factures(5, "factures_generees")
    #print(f"Factures générées : {factures}")
    
    
    
    