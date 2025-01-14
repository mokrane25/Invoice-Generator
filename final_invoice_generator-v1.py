from final_table_generator import TableGenerator
import random, os, json


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
        
        
# def translate_data(text):
#     translator = GoogleTranslator(source='en', target='fr')
    
#     # Fonction pour convertir les prix en dollars en euros
#     def convert_currency(text):
#         import re
#         pattern = r'\$\s?(\d+(\.\d{1,2})?)'
#         matches = re.findall(pattern, text)
#         for match in matches:
#             dollar_amount = match[0]
#             euro_amount = float(dollar_amount) * 0.85  # Exemple de taux de conversion
#             text = text.replace(f"${dollar_amount}", f"{euro_amount:.2f} €")
#         return text
    
#     # Convertir les devises
#     text = convert_currency(text)
    
#     # Traduire le texte
#     translated_text = translator.translate(text)
#     return translated_text
    

def translate_data(text):
    translator = GoogleTranslator(source='en', target='fr')
    
    # Fonction pour convertir les prix en dollars en euros
    def convert_currency(text):
        import re
        # Pattern pour les prix en dollars avec le symbole $
        pattern_dollar = r'\$\s?(\d+(\.\d{1,2})?)'
        matches_dollar = re.findall(pattern_dollar, text)
        for match in matches_dollar:
            dollar_amount = match[0]
            euro_amount = float(dollar_amount) * 0.85  # Exemple de taux de conversion
            text = text.replace(f"${dollar_amount}", f"{euro_amount:.2f} €")
        
        # Pattern pour les prix en USD
        pattern_usd = r'(\d+(\.\d{1,2})?)\s?USD'
        matches_usd = re.findall(pattern_usd, text)
        for match in matches_usd:
            dollar_amount = match[0]
            euro_amount = float(dollar_amount) * 0.85  # Exemple de taux de conversion
            text = text.replace(f"{dollar_amount} USD", f"{euro_amount:.2f} €")
        
        # Pattern pour les prix en dollars avec le symbole $ à la fin
        pattern_dollar_end = r'(\d+(\.\d{1,2})?)\s?\$'
        matches_dollar_end = re.findall(pattern_dollar_end, text)
        for match in matches_dollar_end:
            dollar_amount = match[0]
            euro_amount = float(dollar_amount) * 0.85  # Exemple de taux de conversion
            text = text.replace(f"{dollar_amount} $", f"{euro_amount:.2f} €")
        
        return text
    
    # Convertir les devises
    text = convert_currency(text)
    
    # Traduire le texte
    translated_text = translator.translate(text)
    return translated_text
    
    

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
            text = translate_data(content['text'])
            bbox = content['bbox']
            
            # print(f"Texte original: {content['text']}, \nTexte traduit: {text}, \nBounding box: {bbox}")
            
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
    
    # Initialiser la classe TableGenerator
    height = max(table_bbox[0][1], table_bbox[1][1]) - min(table_bbox[0][1], table_bbox[1][1])
    width = max(table_bbox[0][0], table_bbox[1][0]) - min(table_bbox[0][0], table_bbox[1][0])
    
    table_generator = TableGenerator(height, width)
    
    # Générer les données du tableau
    # table_data = table_generator.generate_table_data()
    
    # Appeler la fonction pour dessiner le tableau sur l'image
    img = table_generator.draw_table_on_image(img, table_bbox)
    
    
    # Créer le dossier de sortie s'il n'existe pas
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Enregistrer l'image modifiée au format JPEG
    output_path = os.path.join(output_folder, output_file)
    img.save(output_path, "JPEG")
    print(f"Facture générée et enregistrée dans {output_path}")
    

    

    
    


# def main():
#     json_path = "FATURA_templates/template_fr.json"      # Dossier contenant les fichiers JSON 
#     # img_path = "FATURA/template.jpeg"
#     template_path = "FATURA_templates/preview.jpeg"      # pour extraire les données du tableau 
#     image_size = Image.open(template_path).size  # (width, height)

#     output_folder = "output_invoices"
#     output_file = "test_invoice.jpeg"
    

#     generate_invoice_from_json(json_path, template_path, output_folder, image_size, output_file)

def main():
    for k in range(1,11):
        for i in range(200):
            json_path = f"FATURA2/invoices_dataset_final/Annotations/Original_Format/Template{k}_Instance{i}.json"      # Dossier contenant les fichiers JSON 
            
            image_path = f"FATURA2/invoices_dataset_final/images/Template{k}_Instance{i}.jpg"      # pour extraire les données du tableau 
            image_size = Image.open(image_path).size

            output_folder = "generated_invoices"
            output_file = f"Template{k}_Invoice{i}.jpeg"

            generate_invoice_from_json(json_path, image_path, output_folder, image_size, output_file)
        
    
if __name__ == "__main__":
    main()





