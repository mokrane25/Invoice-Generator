from data_generator import GenerateurDonnees
from invoice_generator import FactureGenerator


# D'abord, générer les données de test
gen_donnees = GenerateurDonnees("donnees_test_factures")
gen_donnees.generer_fournisseurs()
gen_donnees.generer_clients()
gen_donnees.generer_articles()
gen_donnees.generer_logos_exemple()

# Ensuite, générer les factures
generateur = FactureGenerator("donnees_test_factures")

# Générer une seule facture
# generateur.creer_facture_pdf("ma_facture.pdf")

# Ou générer plusieurs factures
generateur.generer_lot_factures(5, "mes_factures")


