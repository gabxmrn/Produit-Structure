from datetime import datetime
from maturity import Maturity 
from rate import Rate
from bond import FixedBond, ZcBond
from brownianMotion import BrownianMotion
from products import VanillaOption, KnockInOption, KnockOutOption, Spread

from riskAnalysis import BondRisk, OptionRisk


########################################### TEST MATURITY & RATE : ###########################################

# # maturity = Maturity(maturity_in_years=4.5, day_count_convention="ACT/365")
# maturity = Maturity(begin_date=datetime(2024, 3, 7), end_date=datetime(2025, 3, 7), day_count_convention="ACT/360")
# print(f"Maturité (en année) = {round(maturity.maturity(), 2)}")

# # rate = Rate(rate=0.03, rate_type="continuous")
# curve = {Maturity(1.0/365.0):0.0075,
#         Maturity(1.0/12.0):0.01,
#         Maturity(3.0/12.0):0.015,
#         Maturity(6.0/12.0):0.0175,
#         Maturity(1.0):0.02,
#         Maturity(5.0):0.03}
# rate = Rate(rate_type="compounded", rate_curve=curve, interpol_type="linear")
# print(f"Taux = {round(rate.rate(maturity), 2)}")

# print("           ")


# ################################################ TEST BONDS : ################################################

# #### Zero Coupon  Bond : 
# zc_bond = ZcBond(rate=rate, maturity=maturity, nominal=100)
# print(f"Prix zero coupon bond = {round(zc_bond.price(), 2)}")

# #### Fixed Bond : 
# fixed_bond = FixedBond(coupon_rate=0.1, maturity=maturity, nominal=100, nb_coupon=22, rate=rate)
# print(f"Prix de l'obligation à taux fixe = {round(fixed_bond.price(), 2)}")
# print(f"YTM de l'obligation à taux fixe = {round(fixed_bond.ytm(), 2)}")
# bond_risk = BondRisk(bond=fixed_bond)
# print(f"Duration de l'obligation à taux fixe = {round(bond_risk.duration(), 2)}")
# print(f"Convexité de l'obligation à taux fixe = {round(bond_risk.convexity(), 2)}")

# print("           ")

########################################### TEST VANILLA OPTIONS : ###########################################

#### Test normal Call/Put : 

# process = BrownianMotion({
#     "nb_simulations":1000,
#     "nb_steps":1000,
#     "spot":100,
#     "rates":Rate(0.03, rate_type="compounded"),
#     "volatility":0.2,
#     "maturity":Maturity(0.5)
# })

# call_product = VanillaOption("no dividend share", {"option_type":"call", "strike":102})
# call_process = process.pricing(call_product) 
# call_greeks = OptionRisk(call_product, process)

# put_product = VanillaOption("non capitalized index", {"option_type":"put", "strike":102})
# put_process = process.pricing(put_product)
# put_greeks = OptionRisk(put_product, process)

# print(f"Call : Prix = {round(call_process['price'], 2)}, proba d'exercice = {round(call_process['proba'], 2)}, Payoff = {call_product.payoff(call_process['price'])}")
# print(f"Greeks -> {call_greeks.greeks()}")
# print(f"Put : Prix = {round(put_process['price'])}, proba d'exercice = {round(put_process['proba'])}, Payoff = {put_product.payoff(put_process['price'])}")
# print(f"Greeks -> {put_greeks.greeks()}")

# print("           ")

# # Test Share + FX Options : 

# process_share = BrownianMotion({
#     "nb_simulations":1000,
#     "nb_steps":50,
#     "spot":100,
#     "rates":Rate(0.03, rate_type="continuous"),
#     "volatility":0.2,
#     "maturity":Maturity(0.5), 
#     "dividend":0.02})
# call_share = VanillaOption("dividend share", {"option_type":"call", "strike":102})
# call_process_share = process_share.pricing(call_share) 
# greeks_share = OptionRisk(call_share, process_share)
# print(f"Share Call : Prix = {round(call_process_share['price'], 2)}, proba d'exercice = {round(call_process_share['proba'], 2)}, Payoff = {round(call_share.payoff(call_process_share['price']), 2)}")
# print(f"Greeks -> {greeks_share.greeks()}")

# process_fx = BrownianMotion({
#     "nb_simulations":1000,
#     "nb_steps":1000,
#     "spot":100,
#     "rates":Rate(0.03, rate_type="continuous"),
#     "volatility":0.2,
#     "maturity":Maturity(0.5), 
#     "forward_rate":0.2})
# put_fx = VanillaOption("forex rate", {"option_type":"put", "strike":102, "domestic_rate":0.1, "maturity":Maturity(0.5)})
# put_process_fx = process_fx.pricing(put_fx) 
# greeks_fx = OptionRisk(put_fx, process_fx)
# print(f"Forex Put : Prix = {round(put_process_fx['price'], 2)}, proba d'exercice = {round(put_process_fx['proba'], 2)}, Payoff = {round(put_fx.payoff(put_process_fx['price']), 2)}")
# print(f"Greeks -> {greeks_fx.greeks()}")

# print("           ")


########################################### TEST OPTION STRATEGY : ###########################################
process = BrownianMotion({
    "nb_simulations":1000,
    "nb_steps":1000,
    "spot":100,
    "rates":Rate(0.03, rate_type="compounded"),
    "volatility":0.2,
    "maturity":Maturity(0.5)
})

############################# CALL SPREAD

# Call vendu (short)
short_call = VanillaOption("no dividend share", {"option_type":"call", "strike":105})
short_process = process.pricing(short_call)
print(f"Call short (strike 105) : Prix = {round(short_process['price'], 2)}")

# Call acheté (long)
long_call = VanillaOption("no dividend share", {"option_type":"call", "strike":95})
long_process = process.pricing(long_call)
print(f"Call long (strike 95) : Prix = {round(long_process['price'], 2)}")

call_spread = Spread("call spread",
                     {"long leg": long_call, "long leg price":long_process['price'], "short leg": short_call, "short leg price": short_process['price']})
print(f"Prix du call spread : {round(call_spread.price(),2)}")

############################# PUT SPREAD

# Put vendu (short)
short_put = VanillaOption("no dividend share", {"option_type":"put", "strike":95})
short_process2 = process.pricing(short_put)
print(f"Put short (strike 95) : Prix = {round(short_process2['price'], 2)}")

# Put acheté (long)
long_put = VanillaOption("no dividend share", {"option_type":"put", "strike":105})
long_process2 = process.pricing(long_put)
print(f"Put long (strike 105) : Prix = {round(long_process2['price'], 2)}")

put_spread = Spread("put spread",
                     {"long leg": long_put, "long leg price":long_process2['price'], "short leg": short_put, "short leg price": short_process2['price']})
print(f"Prix du put spread : {round(put_spread.price(),2)}")

########################################### TEST BARRIER OPTIONS : ###########################################

# # Test Knock Out Option (KO) : 
# barrier_KO = KnockOutOption({"barrier":120, "strike":100})
# KO_option = process.pricing(barrier_KO, monte_carlo=True)
# print(f"KO Option : Prix = {round(KO_option['price'], 2)}, proba d'exercice = {round(KO_option['proba'], 2)}")

# # Test Knock In Option (KI) : 
# barrier_KI= KnockInOption({"barrier":120, "strike":100})
# KI_option = process.pricing(barrier_KI, monte_carlo=True)
# print(f"KI Option : Prix = {round(KI_option['price'], 2)}, proba d'exercice = {round(KI_option['proba'], 2)}")


"""
    Résumé : 
        - maturity : OK
        - rate : OK
        
            ### Obligations : ###
        - zcBond : OK
        - bond : OK
        - optim : OK
        - risk : OK
        
            ### Options Vanilles : ###
        - brownianMotion : OK
        - products : OK
        - risk : OK
        
            ### Options à barrières : ###
        - brownianMotion : OK
        - products : OK
        - risk : ??? je sais pas si on peut en faire

            ### Produits à stratégie optionnelle : ###
        - call spread : ok
        - put spread : ok
        - straddle
        - strangle
        - butterfly
        - strap
        - strip

    Problème : run time error sur le discount factor "compounded"
    
"""