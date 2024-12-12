from deep_translator import GoogleTranslator

def translate_data(text):
    translator = GoogleTranslator(source='en', target='fr')
    
    # Fonction pour convertir les prix en dollars en euros
    def convert_currency(text):
        import re
        # Pattern pour les prix en dollars avec le symbole $ au début
        pattern_dollar = r'\$\s*(\d+(\.\d{1,2})?)'
        matches_dollar = re.findall(pattern_dollar, text)
        for match in matches_dollar:
            dollar_amount = match[0]
            euro_amount = float(dollar_amount) * 0.85  # Exemple de taux de conversion
            text = text.replace(f"${dollar_amount}", f"{euro_amount:.2f} €")
        
        # Pattern pour les prix en USD
        pattern_usd = r'(\d+(\.\d{1,2})?)\s*USD'
        matches_usd = re.findall(pattern_usd, text)
        for match in matches_usd:
            dollar_amount = match[0]
            euro_amount = float(dollar_amount) * 0.85  # Exemple de taux de conversion
            text = text.replace(f"{dollar_amount} USD", f"{euro_amount:.2f} €")
        
        # Pattern pour les prix en dollars avec le symbole $ à la fin
        pattern_dollar_end = r'(\d+(\.\d{1,2})?)\s*\$'
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

# Exemple d'utilisation
text1 = "The total amount is $100 or 100 USD. Thank you for your purchase."
translated_text1 = translate_data(text1)
print(translated_text1)

text2 = "The total amount is 100 USD. Thank you for your purchase."
translated_text2 = translate_data(text2)
print(translated_text2)

text3 = "SUB_TOTAL : 445.25  $"
translated_text3 = translate_data(text3)
print(translated_text3)