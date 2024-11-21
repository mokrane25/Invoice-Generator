from deep_translator import GoogleTranslator

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
    
    return table_data_fr

# Exemple de table_data
table_data = [
    ["ITEMS", "QUANTITY", "PRICE"],
    ["Data score fire.", "6.00", "$57.80"],
    ["Determine half.", "2.00", "$24.70"],
    ["Model read.", "1.00", "$86.14"],
    ["Mother consider.", "1.00", "$81.84"],
    ["Tv focus.", "4.00", "$40.28"]
]

# Traduire les données du tableau en français
table_data_fr = translate_table_data(table_data)

print("Données du tableau en français:", table_data_fr)