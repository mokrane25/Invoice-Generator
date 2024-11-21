import json
import os
from PIL import Image, ImageDraw, ImageFont

# Fonction pour générer une facture à partir d'un fichier JSON et sauvegarder en JPEG
def generate_invoice_from_json(json_file, template_path,  output_folder="output_invoices", image_size=(600, 900)):
    # Charger le contenu du fichier JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Créer l'image blanche pour la facture
    img = Image.new("RGB", image_size, "white")
    draw = ImageDraw.Draw(img)
    
    # Font par défaut pour le texte (définir un chemin vers une police si nécessaire)
    try:
        font = ImageFont.truetype("arial.ttf", 12)  # Utiliser une police TTF
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
    
    
    # Créer le dossier de sortie s'il n'existe pas
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Enregistrer l'image JPEG
    output_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(json_file))[0]}.jpeg")
    img.save(output_path, "JPEG")
    print(f"Facture générée et enregistrée dans {output_path}")



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
        
    
    
    
    
# Dossier contenant les fichiers JSON
json_folder = "./FATURA"
json_file = "FATURA/template.json"
template_path = "FATURA/preview.jpeg"
output_folder="output_invoices"
image_size = Image.open("FATURA/preview.jpeg").size  # (width, height)


# Générer une facture pour chaque fichier JSON dans le dossier
generate_invoice_from_json(json_file, template_path, output_folder, image_size)



