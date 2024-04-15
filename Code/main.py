from datetime import datetime
from Code.Products.maturity import Maturity 
from Code.Products.rate import Rate
from Code.Products.bond import FixedBond, ZcBond
from Code.Products.brownianMotion import BrownianMotion
from Code.Products.products import VanillaOption, KnockInOption, KnockOutOption, BinaryOption, Spread, OptionProducts, ButterflySpread, ReverseConvertible, CertificatOutperformance

from riskAnalysis import BondRisk, OptionRisk, OptionProductsRisk, SpreadRisk, ButterflySpreadRisk

########################################### TEST STRUCTURED PRODUCTS : #######################################

############################# CERTIFICAT OUTPERFORMANCE

# Call
call_co = VanillaOption("no dividend share", {"option_type":"call", "strike":100})
call_co_process = process.pricing(call_co)
print(f"Call (strike 100) : Prix = {round(call_co_process['price'], 2)}")

# Zero strike call
call_zs_co = VanillaOption("no dividend share", {"option_type":"call", "strike":0})
call_zs_co_process = process.pricing(call_zs_co)
print(f"Call (strike 0) : Prix = {round(call_zs_co_process['price'], 2)}")

# Certificat outperformance
co = CertificatOutperformance({"zero strike call": call_zs_co, "zero strike call price": call_zs_co_process["price"],
                               "call":call_co, "call price":call_co_process["price"]})
print(f"Certificat Outperformance price -> {co.price()}")

print("           ")

"""
    Résumé A faire : 
        - Ranger les fichiers dans des dossiers
        - Risques + Graphiques Options à barrières
        - Risques + Graphiques Options binaires  
        - Vérifier Produits structurés
        - Risques Produits structurés
    
"""