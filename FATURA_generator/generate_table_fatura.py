from PIL import Image, ImageDraw, ImageFont
import os

def draw_table_on_image(template_path, table_bbox, table_data, output_folder="output_invoices"):
    """
    Trace un tableau sur une image template et le remplit avec les données, 
    puis enregistre l'image modifiée au format JPEG dans un dossier de sortie.
    
    Args:
        template_path (str): Chemin de l'image template (par ex., 'FATURA/preview.jpeg').
        table_bbox (list): Bounding box du tableau [[x1, y1], [x2, y2]].
        table_data (list): Données du tableau à remplir (liste de lignes, chaque ligne est une liste de colonnes).
        output_folder (str): Dossier de sortie pour enregistrer l'image modifiée. Par défaut, "output_invoices".
    """
    # Charger l'image template
    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)
    
    # Charger une police (par défaut Arial, peut être changé si indisponible)
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        font = ImageFont.load_default()
    
    # Coordonner de la bounding box
    (x1, y1), (x2, y2) = table_bbox
    
    y1, y2 = img.height - y1, img.height - y2
    x1, x2 = min(x1, x2), max(x1, x2)
    y1, y2 = min(y1, y2), max(y1, y2)
    
    width, height = x2 - x1, y2 - y1  # Largeur et hauteur du tableau (y inversé)
    
    
    # Nombre de colonnes et de lignes
    rows = len(table_data)
    cols = len(table_data[0])
    
    # Calcul des dimensions des cellules
    cell_width = width / cols
    cell_height = height / rows
    
    # Tracer les lignes horizontales et écrire les données
    for i, row in enumerate(table_data):
        for j, cell_text in enumerate(row):
            # Calculer les coordonnées de la cellule
            cell_x1 = x1 + j * cell_width
            cell_y1 = y1 - (i + 1) * cell_height  # Y inversé
            cell_x2 = cell_x1 + cell_width
            cell_y2 = cell_y1 + cell_height
            
            # Tracer le rectangle de la cellule
            draw.rectangle([cell_x1, cell_y1, cell_x2, cell_y2], outline="black", width=2)
            
            # Ajouter le texte dans la cellule
            text_bbox = draw.textbbox((0, 0), cell_text, font=font)
            text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

            text_x = cell_x1 + (cell_width - text_width) / 2
            text_y = cell_y1 + (cell_height - text_height) / 2
            draw.text((text_x, text_y), cell_text, fill="black", font=font)
    
    # Créer le dossier de sortie s'il n'existe pas
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Enregistrer l'image modifiée au format JPEG
    output_path = os.path.join(output_folder, "output_invoice.jpeg")
    img.save(output_path, "JPEG")
    print(f"Image enregistrée avec le tableau dessiné : {output_path}")


# Exemple d'utilisation
template_path = "output_invoices/template.jpeg"
output_folder = "output_invoices"

# Bounding box du tableau (extraite du JSON, convertie si nécessaire)
table_bbox = [[10.0, 328.88980000000004], [560.0, 220.8898]]

# Données du tableau (extraites manuellement du JSON)
table_data = [
    ["ITEMS", "QUANTITY", "PRICE"],
    ["Data score fire.", "6.00", "$57.80"],
    ["Determine half.", "2.00", "$24.70"],
    ["Model read.", "1.00", "$86.14"],
    ["Mother consider.", "1.00", "$81.84"],
    ["Tv focus.", "4.00", "$40.28"]
]

# Appeler la fonction
draw_table_on_image(template_path, table_bbox, table_data, output_folder)


