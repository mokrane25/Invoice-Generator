import os
import json
from PIL import Image, ImageDraw, ImageFont
import pytesseract
import re

def extract_table_bbox_from_json(json_path):
    """
    Extrait la bounding box du tableau à partir d'un fichier JSON.
    
    Args:
        json_path (str): Chemin du fichier JSON.
    
    Returns:
        list: Bounding box du tableau [[x1, y1], [x2, y2]].
    """
    with open(json_path, 'r') as file:
        data = json.load(file)
    
    # Assurez-vous que la structure JSON correspond
    table_bbox = data["TABLE"][0][0]["bbox"]
    return table_bbox

def extract_table_data_from_image(image_path, table_bbox):
    """
    Extrait les données du tableau à partir d'une image en utilisant l'OCR.
    
    Args:
        image_path (str): Chemin de l'image.
        table_bbox (list): Bounding box du tableau [[x1, y1], [x2, y2]].
    
    Returns:
        list: Données du tableau (liste de listes, chaque liste est une ligne).
    """
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    
    # Extraire la région de la bounding box
    x1, y1 = table_bbox[0]
    x2, y2 = table_bbox[1]
    
    y1, y2 = img.height - y1, img.height - y2
    x1, x2 = min(x1, x2), max(x1, x2)
    y1, y2 = min(y1, y2), max(y1, y2)
    
    table_region = img.crop((x1, y1, x2, y2))  # Inverser y1 et y2 pour correspondre à l'axe y de l'image
    
    # Utiliser pytesseract pour extraire le texte de la région du tableau
    table_text = pytesseract.image_to_string(table_region)
    
    # Parse le texte pour récupérer les données du tableau
    lines = table_text.split("\n")
    table_data = []
    for line in lines:
        if line.strip():
            columns = line.split()
            if len(columns) > 3:
                item_name = ' '.join(columns[:-2])
                quantity = columns[-2]
                price = columns[-1]
                table_data.append([item_name, quantity, price])
            else:
                table_data.append(columns)
    
    return table_data

# Exemple d'utilisation
template_path = "FATURA/preview.jpeg"
json_path = "FATURA/template.json"

# Extraire la bounding box du tableau à partir du JSON
table_bbox = extract_table_bbox_from_json(json_path)

# Extraire les données du tableau à partir de l'image
table_data = extract_table_data_from_image(template_path, table_bbox)

print("Bounding Box du tableau:", table_bbox)
print("Données du tableau:", table_data)

