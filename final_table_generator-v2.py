import matplotlib.pyplot as plt
import random
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from PIL import Image, ImageTk, ImageDraw 

import numpy as np
import os
import matplotlib.pyplot as plt

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
            file_path = f'INVOICE_DATA/table_data/{file_key}.txt'
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = file.readlines()
                row.append(random.choice(data).strip())
            else:
                row.append(f'Cellule {header}')
        return row
    
    
    
    def generate(self, img, table_bbox):
        # Calcul dynamique du nombre de lignes et de la taille de police
        # Ajuster dynamiquement la taille en fonction de la hauteur réelle du canvas
        min_row_height = 10  # Hauteur minimale par ligne
        max_rows = max(3, self.height // min_row_height)
        nombre_lignes = random.randint(2, min(6, max_rows))
        
        # Génération des données du tableau
        data = []
        for _ in range(nombre_lignes):
            row = self._generate_random_row()
            data.append(row)
            
            
# Convertir les en-têtes en majuscules
        var_1 = random.randint(1, 5)
        if var_1 < 3:
            en_tetes_majuscules = [header.upper() for header in self.en_tetes]
            self.en_tetes = en_tetes_majuscules
        

            
        
        # Création de la figure matplotlib
        plt.close('all')  # Fermer toutes les figures précédentes
        fig, ax = plt.subplots(figsize=(self.width/100, self.height/100), dpi=100)
        ax.axis('tight')
        ax.axis('off')

        # Ajustement dynamique de la taille de police
        font_size = min(7, max(8, int(self.height / (nombre_lignes * 3))))

        # Création du tableau avec une échelle adaptative
        table = ax.table(
            cellText=data, 
            colLabels=self.en_tetes, 
            loc='center', 
            cellLoc='center'
        )

        # Style du tableau
        table.auto_set_font_size(False)
        table.set_fontsize(font_size)
          

# Convertir les en-têtes en majuscules
        var_2 = random.randint(1, 5)
        if var_2 < 3 : 
            # Mettre les en-têtes en gras
            for (i, j), cell in table.get_celld().items():
                if i == 0:  # Ligne des en-têtes
                    cell.set_text_props(weight='bold')
        
                    
# changer les couleurs des lignes du tracé du tableau (blanc ou noir)
        var_3 = random.randint(1, 4)
        if var_3 == 1:
            for i, key in enumerate(table.get_celld().keys()):
                cell = table.get_celld()[key]
                cell.set_edgecolor('white')  # Lignes blanches


        # Ajustement dynamique de l'échelle verticale
        vertical_scale = min(2.0, max(1.2, self.height / (nombre_lignes * 50)))
        table.scale(1, vertical_scale)

        plt.tight_layout(pad=0.1)

        # Convertir la figure matplotlib en image PIL
        canvas_agg = FigureCanvas(fig)
        canvas_agg.draw()

        # Convertir le buffer RGBA en numpy array
        buf = np.frombuffer(canvas_agg.buffer_rgba(), dtype=np.uint8)
        width, height = canvas_agg.get_width_height()
        


        # Convertir en image RGBA
        table_img = Image.fromarray(buf.reshape(height, width, 4))

        # Dessiner l'image du tableau sur l'image principale
        draw = ImageDraw.Draw(img)
        img.paste(table_img, (int(table_bbox[0][0]), int(table_bbox[0][1])))

        plt.close(fig)  # Fermer proprement la figure

        return img

    