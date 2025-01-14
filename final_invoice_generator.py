from final_table_generator import TableGenerator
import random, os, json
from PIL import Image, ImageDraw, ImageFont
import pytesseract
from deep_translator import GoogleTranslator

# Fonction pour découper et coller le logo
def add_logo_to_invoice(template_path, logo_bbox, img, image_size):
    template = Image.open(template_path)
    x1, y1 = logo_bbox[0]
    x2, y2 = logo_bbox[1]
    y1, y2 = template.height - y1, template.height - y2
    x1, x2 = min(x1, x2), max(x1, x2)
    y1, y2 = min(y1, y2), max(y1, y2)
    logo = template.crop((x1, y1, x2, y2))
    new_y1 = image_size[1] - (template.height - y1)
    img.paste(logo, (int(x1), int(new_y1)))
    print(f"Logo ajouté à la position ({x1}, {new_y1})")

def extract_table_bbox_from_json(json_path):
    with open(json_path, 'r') as file:
        data = json.load(file)
    table_bbox = data["TABLE"][0][0]["bbox"]
    return table_bbox

def translate_data(text):
    translator = GoogleTranslator(source='en', target='fr')
    def convert_currency(text):
        import re
        pattern_dollar = r'\$\s?(\d+(\.\d{1,2})?)'
        matches_dollar = re.findall(pattern_dollar, text)
        for match in matches_dollar:
            dollar_amount = match[0]
            euro_amount = float(dollar_amount) * 0.85
            text = text.replace(f"${dollar_amount}", f"{euro_amount:.2f} €")
        pattern_usd = r'(\d+(\.\d{1,2})?)\s?USD'
        matches_usd = re.findall(pattern_usd, text)
        for match in matches_usd:
            dollar_amount = match[0]
            euro_amount = float(dollar_amount) * 0.85
            text = text.replace(f"{dollar_amount} USD", f"{euro_amount:.2f} €")
        pattern_dollar_end = r'(\d+(\.\d{1,2})?)\s?\$'
        matches_dollar_end = re.findall(pattern_dollar_end, text)
        for match in matches_dollar_end:
            dollar_amount = match[0]
            euro_amount = float(dollar_amount) * 0.85
            text = text.replace(f"{dollar_amount} $", f"{euro_amount:.2f} €")
        return text
    text = convert_currency(text)
    translated_text = translator.translate(text)
    return translated_text

def generate_invoice_from_json(json_file, template_path, output_folder="output_invoices", image_size=(600, 900), output_file="output_invoice.jpeg", annotations_folder="generated_annotations"):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    img = Image.new("RGB", image_size, "white")
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("fonts/DejaVuSans.ttf", 12)
    except IOError:
        font = ImageFont.load_default()

    annotations = {}

    for key, content in data.items():
        if 'text' in content and 'bbox' in content:
            text = translate_data(content['text'])
            bbox = content['bbox']
            x1, y1 = bbox[0]
            x2, y2 = bbox[1]
            y1, y2 = image_size[1] - y1, image_size[1] - y2
            position = (x1, min(y1, y2))
            draw.text(position, text, fill="black", font=font)
            annotations[key] = {"bbox": [x1, y1, x2, y2], "text": text}

    if "LOGO" in data and "bbox" in data["LOGO"]:
        try:
            add_logo_to_invoice(template_path, data["LOGO"]["bbox"], img, image_size)
            annotations["LOGO"] = {"bbox": data["LOGO"]["bbox"], "text": "LOGO"}
        except Exception as e:
            print(f"Erreur lors de l'ajout du logo: {e}")

    table_bbox = extract_table_bbox_from_json(json_file)
    height = max(table_bbox[0][1], table_bbox[1][1]) - min(table_bbox[0][1], table_bbox[1][1])
    width = max(table_bbox[0][0], table_bbox[1][0]) - min(table_bbox[0][0], table_bbox[1][0])
    table_generator = TableGenerator(height, width)
    img, table_data = table_generator.draw_table_on_image(img, table_bbox)
    annotations["TABLE"] = {"bbox": table_bbox, "text": table_data}

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    output_path = os.path.join(output_folder, output_file)
    img.save(output_path, "JPEG")
    print(f"Facture générée et enregistrée dans {output_path}")

    if not os.path.exists(annotations_folder):
        os.makedirs(annotations_folder)
    
    annotations_path = os.path.join(annotations_folder, output_file.replace(".jpeg", ".json"))
    with open(annotations_path, 'w', encoding='utf-8') as f:
        json.dump(annotations, f, ensure_ascii=False, indent=4)
    print(f"Annotations générées et enregistrées dans {annotations_path}")

def main():
    for k in range(13, 51):
        for i in range(200):
            json_path = f"FATURA2/invoices_dataset_final/Annotations/Original_Format/Template{k}_Instance{i}.json"
            image_path = f"FATURA2/invoices_dataset_final/images/Template{k}_Instance{i}.jpg"
            image_size = Image.open(image_path).size
            output_folder = "generated_invoices"
            output_file = f"Template{k}_Invoice{i}.jpeg"
            annotations_folder = "generated_annotations"
            generate_invoice_from_json(json_path, image_path, output_folder, image_size, output_file, annotations_folder)

if __name__ == "__main__":
    main()
    