from datetime import datetime

from maturity import Maturity 
from rate import Rate
from bond import FixedBond, ZcBond
from brownianMotion import BrownianMotion
from products import VanillaOption, KnockInOption, KnockOutOption

from riskAnalysis import BondRisk, OptionRisk


#### Test Maturity : 
# maturity = Maturity(maturity_in_years=4.5, day_count_convention="ACT/365")
maturity = Maturity(begin_date=datetime(2024, 3, 7), end_date=datetime(2025, 3, 7), day_count_convention="ACT/360")
print(f"Maturité (en année) = {maturity.maturity()}")

#### Test Rate : 
# rate = Rate(rate=0.03, rate_type="continuous")
curve = {Maturity(1.0/365.0):0.0075,
        Maturity(1.0/12.0):0.01,
        Maturity(3.0/12.0):0.015,
        Maturity(6.0/12.0):0.0175,
        Maturity(1.0):0.02,
        Maturity(5.0):0.03}
rate = Rate(rate_type="compounded", rate_curve=curve, interpol_type="linear")
print(f"Taux = {rate.rate(maturity)}")

print("           ")

#### Test zcBond : 
zc_bond = ZcBond(rate=rate, maturity=maturity, nominal=100)
print(f"Prix zero coupon = {zc_bond.price()}")
# PS : on a le même résultat que le prof avec r = 0.03 :)

#### Test Bond : 
fixed_bond = FixedBond(coupon_rate=0.1, maturity=maturity, nominal=100, nb_coupon=22, rate=rate)
print(f"Prix de l'obligation à taux fixe = {fixed_bond.price()}")
print(f"YTM de l'obligation à taux fixe = {fixed_bond.ytm()}")
bond_risk = BondRisk(bond=fixed_bond)
print(f"Duration de l'obligation à taux fixe = {bond_risk.duration()}")
print(f"Convexité de l'obligation à taux fixe = {bond_risk.convexite()}")

print("           ")

#### Test Options Vanilles : 

process = BrownianMotion({
    "nb_simulations":1000,
    "nb_steps":1000,
    "spot":100,
    "rates":Rate(0.03, rate_type="continuous"),
    "volatility":0.2,
    "maturity":Maturity(0.5)
})
call_product = VanillaOption({"option_type":"call", "strike":102})
put_product = VanillaOption({"option_type":"put", "strike":102})
call = process.pricing(call_product) 
put = process.pricing(put_product)
print(f"Call : Prix = {call['price']}, proba d'exercice = {call['proba']}, Payoff = {call_product.payoff(call['price'])}")
print(f"Put : Prix = {put['price']}, proba d'exercice = {put['proba']}, Payoff = {put_product.payoff(put['price'])}")
greeks_call = OptionRisk(call_product, process)
print(f"Call -> Delta = {greeks_call.delta()}, Gamma = {greeks_call.gamma()}, Vega = {greeks_call.vega()}, theta = {greeks_call.theta()}, rho = {greeks_call.rho()}")
greeks_put = OptionRisk(put_product, process)
print(f"Put -> Delta = {greeks_put.delta()}, Gamma = {greeks_put.gamma()}, Vega = {greeks_put.vega()}, theta = {greeks_put.theta()}, rho = {greeks_put.rho()}")

print("           ")

process_share = BrownianMotion({
    "nb_simulations":1000,
    "nb_steps":50,
    "spot":100,
    "rates":Rate(0.03, rate_type="continuous"),
    "volatility":0.2,
    "maturity":Maturity(0.5),
}, {"dividend":0.01})
call_share = VanillaOption({"option_type":"call", "strike":102})
call_2 = process_share.pricing(call_share) 
print(f"Call sur action : Prix = {call_2['price']}, proba d'exercice = {call_2['proba']}, Payoff = {call_share.payoff(call['price'])}")
greeks_share = OptionRisk(call_share, process_share)
print(f"Delta = {greeks_share.delta()}, Gamma = {greeks_share.gamma()}, Vega = {greeks_share.vega()}, theta = {greeks_share.theta()}, rho = {greeks_share.rho()}")
process_fx = BrownianMotion({
    "nb_simulations":1000,
    "nb_steps":1000,
    "spot":100,
    "rates":Rate(0.03, rate_type="continuous"),
    "volatility":0.2,
    "maturity":Maturity(0.5),
}, {"forward_rate":0.2, 
    "domestic_rate":0.1})
put_fx = VanillaOption({"option_type":"put", "strike":102})
put_2 = process_fx.pricing(put_fx) 
print(f"Put sur Forex : Prix = {put_2['price']}, proba d'exercice = {put_2['proba']}, Payoff = {put_fx.payoff(call['price'])}")
greeks_fx = OptionRisk(put_fx, process_fx)
print(f"Delta = {greeks_fx.delta()}, Gamma = {greeks_fx.gamma()}, Vega = {greeks_fx.vega()}, theta = {greeks_fx.theta()}, rho = {greeks_fx.rho()}")

print("           ")

# Option sur taux de change :
barrierKO= KnockOutOption({"barrier":120, "strike":100})
KO_option = process.pricing(barrierKO, monte_carlo=True)
print(f"KO Option : Prix = {KO_option['price']}, proba d'exercice = {KO_option['proba']}")
barrierKI= KnockInOption({"barrier":120, "strike":100})
KI_option = process.pricing(barrierKI, monte_carlo=True)
print(f"KI Option : Prix = {KI_option['price']}, proba d'exercice = {KI_option['proba']}")



"""
    Résumé : 
        - maturity : OK
        - rate : OK
        
            ### Obligations : ###
        - zcBond : OK
        - bond : OK
        - optim : OK
        
            ### Options : ###
        - brownianMotion : OK
        - products : fonctionne mais pas complet 
        
        
    Caro : 
    - j'ai tenter de rajouter la duration + convexité mais vraiment pas sure de la formule (et des résultats) ??
    - on a une erreur quand maturité trop longue (problème de discount factor)
    - option sur action et tx de change fait (d'après le cours), pour les indices je sais pas encore quoi changer 
    la méthode est pas forcément optimale (et le code pas encore commenté), dites moi si vous voyez des améliorations à faire :) 
    - A verifier : formule prix (pas le meme que sur pricer google...) + spot avec dividende et fx !!
    + commenter les nouveaux codes 
    
"""