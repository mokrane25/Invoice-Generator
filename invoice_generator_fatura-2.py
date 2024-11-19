import json
import os
from PIL import Image, ImageDraw, ImageFont

def generate_invoice_from_json(json_file, template_path, output_folder="output_invoices", image_size=(600, 900)):
    # Charger le contenu du fichier JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Créer l'image blanche pour la facture
    img = Image.new("RGB", image_size, "white")
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except IOError:
        font = ImageFont.load_default()

    # Ajouter d'abord le logo si présent dans le JSON
    if "LOGO" in data and "bbox" in data["LOGO"]:
        try:
            # Charger le template original
            template = Image.open(template_path)
            
            # Récupérer les coordonnées du logo
            logo_bbox = data["LOGO"]["bbox"]
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
        except Exception as e:
            print(f"Erreur lors de l'ajout du logo: {e}")

    # Parcourir chaque élément du JSON pour le texte
    for key, content in data.items():
        if key != "LOGO" and isinstance(content, dict) and 'text' in content and 'bbox' in content:
            try:
                text = content['text']
                bbox = content['bbox']
                
                # Récupération des coordonnées
                x1, y1 = bbox[0]
                
                # Inversion de l'axe y pour la nouvelle image
                y1 = image_size[1] - y1
                
                # Dessiner le texte
                draw.text((x1, y1), text, fill="black", font=font)
            except Exception as e:
                print(f"Erreur lors de l'ajout du texte pour {key}: {e}")
    
    # Créer le dossier de sortie
    os.makedirs(output_folder, exist_ok=True)

    # Sauvegarder l'image
    output_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(json_file))[0]}.jpeg")
    img.save(output_path, "JPEG")
    print(f"Facture générée et enregistrée dans {output_path}")

# Dossier contenant les fichiers JSON
json_folder = "./FATURA"
template_path = "FATURA/preview.jpeg"
output_folder="output_invoices"
image_size = Image.open("FATURA/preview.jpeg").size  # (width, height)

# Générer une facture pour chaque fichier JSON
for json_file in os.listdir(json_folder):
    if json_file.endswith(".json"):
        generate_invoice_from_json(os.path.join(json_folder, json_file), template_path, output_folder, image_size)
        
        
        