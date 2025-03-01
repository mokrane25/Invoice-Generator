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
            ['qte', 'Description', 'prix unitaire', 'total'],
            ['description', 'qte', 'prix net', 'prix coutant', 'TVA(%)']
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
    
    def generate_table_data(self):
        min_height = 20
        max_lignes = max(3, self.height // min_height)
        nombre_lignes = random.randint(2, max_lignes)

        data = []
        data.append(self.en_tetes)
        
        for _ in range(nombre_lignes):
            row = self._generate_random_row()
            data.append(row)

        return data
    
    def draw_table_on_image(self, img, table_bbox, table_data=None, output_folder="output_invoices", font_size=12, border_width=2):
        if table_data is None:
            table_data = self.generate_table_data()
        
        var_1 = random.randint(1, 5)
        if var_1 < 3:
            en_tetes_majuscules = [header.upper() for header in self.en_tetes]
            self.en_tetes = en_tetes_majuscules

        if not table_data or not table_data[0]:
            raise ValueError("Les données du tableau ne peuvent pas être vides")
        
        cols = len(table_data[0])
        if not all(len(row) == cols for row in table_data):
            raise ValueError("Toutes les lignes doivent avoir le même nombre de colonnes")
        
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("fonts/DejaVuSans.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
        
        (x1, y1), (x2, y2) = table_bbox
        
        y1, y2 = img.height - y1, img.height - y2
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        width, height = x2 - x1, y2 - y1
        
        rows = len(table_data)
        cols = len(table_data[0])
        
        cell_width = width / cols
        cell_height = height / rows
        
        for i, row in enumerate(table_data):
            for j, cell_text in enumerate(row):
                cell_x1 = x1 + j * cell_width
                cell_y1 = y1 + i * cell_height
                cell_x2 = cell_x1 + cell_width
                cell_y2 = cell_y1 + cell_height
                
                draw.rectangle([cell_x1, cell_y1, cell_x2, cell_y2], outline="black", width=border_width)
                
                cell_text = str(cell_text)
                
                text_bbox = draw.textbbox((0, 0), cell_text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                text_x = cell_x1 + (cell_width - text_width) / 2
                text_y = cell_y1 + (cell_height - text_height) / 2
                
                draw.text((text_x, text_y), cell_text, fill="black", font=font)
        
        print("Le tableau a été généré avec succès")
        return img, table_data