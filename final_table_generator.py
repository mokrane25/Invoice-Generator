import random
import os
from PIL import Image, ImageDraw, ImageFont

class TableGenerator:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.en_tetes = self._select_random_headers()
        self.synonymes = {
            'produit': ['produit', 'description', 'article', 'code article'],
            'quantite': ['quantité', 'qte', 'Quantité commandée', 'Quantité livrée'],
            'prix': ['prix', 'prix unitaire', 'prix net', 'prix coutant'],
            'total': ['total', 'montant'],
            'tax': ['tax', 'TVA(%)', 'tva'],
            'ID': ['ID', 'No', 'Référence']
        }
    
    def _select_random_headers(self):
        headers = [
            ['produit', 'quantité', 'prix'],
            ['produit', 'prix', 'quantité', 'total'],
            ['produit', 'quantité', 'prix', 'tax', 'total'],
            ['qte', 'ID', 'Description', 'prix unitaire', 'total'],
            ['No', 'description', 'qte', 'prix net', 'prix coutant', 'TVA(%)']
        ]
        return random.choice(headers)
    
    def _get_file_for_header(self, header):
        for key, synonyms in self.synonymes.items():
            for synonym in synonyms:
                if header.lower() in synonym.lower():
                    return key
        return header.lower()
    
    def _generate_random_row(self):
        row = []
        for header in self.en_tetes:
            file_key = self._get_file_for_header(header)
            file_path = f'INVOICE_DATA/{file_key}.txt'
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    data = file.readlines()
                row.append(random.choice(data).strip())
            else:
                row.append(f'Cellule {header}')
        return row
    
    def generate_table_data(self):
        min_height = 20
        max_lignes = max(3, self.height // min_height)
        nombre_lignes = random.randint(2, max_lignes)

        data = []
        # Ajouter l'en-tête comme première ligne
        data.append(self.en_tetes)
        
        # Générer des lignes de données
        for _ in range(nombre_lignes):
            row = self._generate_random_row()
            data.append(row)

        # data.reverse()
        return data
    
    
    def draw_table_on_image(self, img, table_bbox, table_data=None, output_folder="output_invoices", font_size=12, border_width=2):
        """
        Trace un tableau dynamique sur une image template avec des dimensions flexibles.
        
        Args:
            img (Image): Image PIL sur laquelle tracer le tableau.
            table_bbox (list): Bounding box du tableau [[x1, y1], [x2, y2]].
            table_data (list, optional): Données du tableau à remplir. Si None, génère des données aléatoires.
            output_folder (str, optional): Dossier de sortie. Défaut: "output_invoices".
            font_size (int, optional): Taille de police. Défaut: 12.
            border_width (int, optional): Épaisseur des bordures. Défaut: 2.
        
        Returns:
            Image: Image avec le tableau ajouté.
        """
        # Si aucune donnée n'est fournie, générer des données aléatoires
        if table_data is None:
            table_data = self.generate_table_data()
        
# Convertir les en-têtes en majuscules
        var_1 = random.randint(1, 5)
        if var_1 < 3:
            en_tetes_majuscules = [header.upper() for header in self.en_tetes]
            self.en_tetes = en_tetes_majuscules
# Convertir les en-têtes en majuscules
        # var_2 = random.randint(1, 5)
        # if var_2 < 3 : 
        #     # Mettre les en-têtes en gras
        #     for (i, j), cell in table.get_celld().items():
        #         if i == 0:  # Ligne des en-têtes
        #             cell.set_text_props(weight='bold')     
# changer les couleurs des lignes du tracé du tableau (blanc ou noir)
        # var_3 = random.randint(1, 4)
        # if var_3 == 1:
        #     for i, key in enumerate(table.get_celld().keys()):
        #         cell = table.get_celld()[key]
        #         cell.set_edgecolor('white')  # Lignes blanches


        # Validation des données
        if not table_data or not table_data[0]:
            raise ValueError("Les données du tableau ne peuvent pas être vides")
        
        # Vérifier que toutes les lignes ont le même n ombre de colonnes
        cols = len(table_data[0])
        if not all(len(row) == cols for row in table_data):
            raise ValueError("Toutes les lignes doivent avoir le même nombre de colonnes")
        
        # Préparation du dessin
        draw = ImageDraw.Draw(img)
        
        # Gestion de la police
        try:
            font = ImageFont.truetype("fonts/DejaVuSans.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
        
        # Coordonnées de la bounding box
        (x1, y1), (x2, y2) = table_bbox
        
        # Calcul des coordonnées en tenant compte de l'axe Y inversé
        y1, y2 = img.height - y1, img.height - y2
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        # Dimensions du tableau
        width, height = x2 - x1, y2 - y1
        
        # Nombre de lignes et de colonnes
        rows = len(table_data)
        cols = len(table_data[0])
        
        # Calcul des dimensions des cellules
        cell_width = width / cols
        cell_height = height / rows
        
        # Tracer les cellules et ajouter le texte
        for i, row in enumerate(table_data):
            for j, cell_text in enumerate(row):
                # Calculer les coordonnées de la cellule (Y inversé pour PIL)
                cell_x1 = x1 + j * cell_width
                cell_y1 = y1 + i * cell_height  # Inversion supprimée ici, car y1 est déjà ajusté
                cell_x2 = cell_x1 + cell_width
                cell_y2 = cell_y1 + cell_height
                
                # Tracer le rectangle de la cellule
                draw.rectangle([cell_x1, cell_y1, cell_x2, cell_y2],
                            outline="black",
                            width=border_width)
                
                # Convertir le contenu de la cellule en chaîne
                cell_text = str(cell_text)
                
                # Calculer la position du texte
                text_bbox = draw.textbbox((0, 0), cell_text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                # Centrer le texte dans la cellule
                text_x = cell_x1 + (cell_width - text_width) / 2
                text_y = cell_y1 + (cell_height - text_height) / 2
                
                # Ajouter le texte
                draw.text((text_x, text_y), cell_text, fill="black", font=font)
        
        print("Le tableau a été généré avec succès")
        return img

    
    