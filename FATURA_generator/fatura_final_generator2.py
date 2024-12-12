import json
import os
from PIL import Image, ImageDraw, ImageFont
import pytesseract
from deep_translator import GoogleTranslator



# Fonction pour découper et coller le logo
def add_logo_to_invoice(template_path, logo_bbox, img, image_size):
    # Charger le template original
    template = Image.open(template_path)
    
    # Récupérer les coordonnées du logo
    x1, y1 = logo_bbox[0]
    x2, y2 = logo_bbox[1]
    
    # Inverser les coordonnées y par rapport à la hauteur du template original
    y1, y2 = template.height - y1, template.height - y2
    
    # S'assurer que les coordonnées sont dans le bon ordre (min à max)
    x1, x2 = min(x1, x2), max(x1, x2)
    y1, y2 = min(y1, y2), max(y1, y2)
    
    # Découper le logo
    logo = template.crop((x1, y1, x2, y2))
    
    # Calculer la position dans la nouvelle image
    new_y1 = image_size[1] - (template.height - y1)
    
    # Coller le logo sur la nouvelle image
    img.paste(logo, (int(x1), int(new_y1)))
    print(f"Logo ajouté à la position ({x1}, {new_y1})")
        
    
    
    


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

def translate_table_data(table_data, src_lang='en', dest_lang='fr'):
    """
    Traduit les données du tableau de l'anglais en français et remplace les signes de dollar par des signes d'euro.
    
    Args:
        table_data (list): Données du tableau (liste de listes, chaque liste est une ligne).
        src_lang (str): Langue source (par défaut 'en' pour anglais).
        dest_lang (str): Langue cible (par défaut 'fr' pour français).
    
    Returns:
        list: Données du tableau traduites en français.
    """
    translator = GoogleTranslator(source=src_lang, target=dest_lang)
    table_data_fr = []
    
    for row in table_data:
        translated_row = []
        for cell in row:
            # Remplacer le signe $ par € et déplacer le symbole après le montant
            if '$' in cell:
                amount = cell.replace('$', '').strip()
                translated_cell = f"{amount} €"
            else:
                translated_cell = translator.translate(cell)
            translated_row.append(translated_cell)
        table_data_fr.append(translated_row)
    
        # Inverser l'ordre des listes
    table_data_fr.reverse()
    return table_data_fr


def draw_table_on_image(img, table_bbox, table_data, output_folder="output_invoices"):
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
    # img = Image.open(template_path)
    draw = ImageDraw.Draw(img)
    
    # Charger une police (par défaut Arial, peut être changé si indisponible)
    try:
        # font = ImageFont.truetype("arial.ttf", 16)
        font = ImageFont.truetype("fonts/DejaVuSans.ttf", 12)
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
    
    print("Le tableau a été dessiné ")




# Fonction pour générer une facture à partir d'un fichier JSON et sauvegarder en JPEG
def generate_invoice_from_json(json_file, template_path,  output_folder="output_invoices", image_size=(600, 900), output_file="output_invoice.jpeg"):
    # Charger le contenu du fichier JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Créer l'image blanche pour la facture
    img = Image.new("RGB", image_size, "white")
    draw = ImageDraw.Draw(img)
    
    # Font par défaut pour le texte (définir un chemin vers une police si nécessaire)
    try:
        # font = ImageFont.truetype("arial.ttf", 12)  # Utiliser une police TTF
        font = ImageFont.truetype("fonts/DejaVuSans.ttf", 12)  # Utiliser une police TTF
    except IOError:
        font = ImageFont.load_default()  # Police par défaut si Arial non disponible

    # Parcourir chaque élément du JSON
    for key, content in data.items():
        if 'text' in content and 'bbox' in content:
            text = content['text']
            bbox = content['bbox']
            
            print(f"Texte: {text}, Bounding box: {bbox}")
            
            # Récupération des coordonnées de la bounding box et inversion de l'axe y
            x1, y1 = bbox[0]
            x2, y2 = bbox[1]
            y1, y2 = image_size[1] - y1, image_size[1] - y2  # Inversion de l'axe y
            
            # Définir la position de texte dans la bounding box
            position = (x1, min(y1, y2))
            
            # Dessiner le texte dans l'image
            draw.text(position, text, fill="black", font=font)
    
    
    
    # Ajouter le logo si présent dans le JSON
    if "LOGO" in data and "bbox" in data["LOGO"]:
        try :
            add_logo_to_invoice(template_path, data["LOGO"]["bbox"], img, image_size)    
        except Exception as e:
            print(f"Erreur lors de l'ajout du logo: {e}")
    
    
    # Extraire la bounding box du tableau à partir du JSON
    table_bbox = extract_table_bbox_from_json(json_file)
    # Extraire les données du tableau à partir de l'image
    table_data = extract_table_data_from_image(template_path, table_bbox)
    # Traduire les données du tableau en français
    table_data_fr = translate_table_data(table_data)

    # Appeler la fonction pour dessiner le tableau sur l'image
    draw_table_on_image(img, table_bbox, table_data_fr, output_folder)
    
    
    # Créer le dossier de sortie s'il n'existe pas
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Enregistrer l'image modifiée au format JPEG
    output_path = os.path.join(output_folder, output_file)
    img.save(output_path, "JPEG")
    print(f"Facture générée et enregistrée dans {output_path}")
    

    

    
    

def main():
    json_path = "FATURA_templates/template_fr.json"      # Dossier contenant les fichiers JSON 
    # img_path = "FATURA/template.jpeg"
    template_path = "FATURA_templates/preview.jpeg"      # pour extraire les données du tableau 
    image_size = Image.open(template_path).size  # (width, height)

    output_folder = "output_invoices"
    

    generate_invoice_from_json(json_path, template_path, output_folder, image_size)


def main():
    for i in range(10):
        json_path = f"FATURA2/invoices_dataset_final/Annotations/Original_Format/Template1_Instance{i}.json"      # Dossier contenant les fichiers JSON 
        
        template_path = f"FATURA2/invoices_dataset_final/images/Template1_Instance{i}.jpg"      # pour extraire les données du tableau 
        image_size = Image.open(template_path).size

        output_folder = "output_invoices"
        output_file = f"output_invoice{i}.jpeg"

        generate_invoice_from_json(json_path, template_path, output_folder, image_size, output_file)
    
    
if __name__ == "__main__":
    main()

